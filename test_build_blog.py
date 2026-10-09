"""Regression checks for intact, cache-versioned static blog triptychs."""
import contextlib
import hashlib
import importlib.util
import io
import json
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("build_blog", Path(__file__).with_name("build-blog.py"))
blog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(blog)


class Elements(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.tags = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def all(self, name):
        return [attrs for tag, attrs in self.tags if tag == name]


class TriptychTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="t27-blog-cover-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.art = self.root / "og-art"
        self.art.mkdir()
        self.addCleanup(patch.stopall)
        patch.object(blog, "ROOT", self.root, create=True).start()
        self.post = {
            "slug": "three-panels", "title": 'A "measured" result',
            "summary": "Measured, not assumed.", "date": "2026-09-07",
            "readingMinutes": 3, "tags": ["verification"],
            "body": [{"kind": "p", "text": "The full article remains here."}],
            "ru": {"title": "Проверенный результат", "summary": "Измерено, не предположено.",
                   "body": [{"kind": "p", "text": "Полный текст статьи."}]},
        }
        self.bytes = b"test cover revision one"
        (self.art / "three-panels.jpg").write_bytes(self.bytes)
        self.digest = hashlib.sha256(self.bytes).hexdigest()[:12]
        self.panels = [
            {"heading": "THE OBSERVATION", "caption": "A measured result."},
            {"heading": "THE EVIDENCE", "caption": "An independent check."},
            {"heading": "THE LIMIT", "caption": "Not a hardware claim."},
        ]

    def write_captions(self, value):
        (self.art / "captions.json").write_text(json.dumps(value), encoding="utf-8")

    def test_articles_in_both_languages_show_intact_versioned_cover(self):
        for lang in ("en", "ru"):
            with self.subTest(lang=lang):
                page = blog.post_page(self.post, lang)
                image = Elements(page).all("img")[0]
                self.assertEqual(image["src"], f"/og-art/three-panels.jpg?v={self.digest}")
                self.assertEqual((image["width"], image["height"]), ("1200", "630"))
                self.assertEqual(image["loading"], "eager")
                self.assertEqual(image["decoding"], "async")
                self.assertIn(blog.localise(self.post, lang)["title"], image["alt"])
                self.assertIn('class="blog-cover"', page)
                self.assertIn('target="_blank"', page)
                full_size_links = [a for a in Elements(page).all("a") if a.get("target") == "_blank"]
                self.assertTrue(all(blog.localise(self.post, lang)["title"] in a["aria-label"] for a in full_size_links))
                self.assertIn(blog.localise(self.post, lang)["body"][0]["text"], page)

    def test_both_indexes_use_lazy_whole_covers_and_local_article_links(self):
        for lang in ("en", "ru"):
            with self.subTest(lang=lang):
                page = blog.index_page([self.post], lang)
                image = Elements(page).all("img")[0]
                self.assertEqual(image["src"], f"/og-art/three-panels.jpg?v={self.digest}")
                self.assertEqual(image["loading"], "lazy")
                self.assertIn(f'href="{blog.base(lang)}/three-panels/"', page)

    def test_asset_change_changes_url_without_changing_public_article_url(self):
        old = Elements(blog.post_page(self.post)).all("img")[0]["src"]
        (self.art / "three-panels.jpg").write_bytes(b"test cover revision two")
        page = blog.post_page(self.post)
        new = Elements(page).all("img")[0]["src"]
        self.assertNotEqual(old, new)
        self.assertIn('rel="canonical" href="https://t27.ai/blog/three-panels/"', page)

    def test_missing_art_has_no_broken_preview_or_title_card_substitution(self):
        (self.art / "three-panels.jpg").unlink()
        for render in (blog.post_page, lambda p, lang: blog.index_page([p], lang)):
            for lang in ("en", "ru"):
                with self.subTest(render=render, lang=lang):
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr):
                        page = render(self.post, lang)
                    self.assertFalse(Elements(page).all("img"))
                    self.assertIn("missing triptych", stderr.getvalue())
                    self.assertIn("og-art/three-panels.jpg", stderr.getvalue())
                    self.assertIn(blog.localise(self.post, lang)["title"].split()[0], page)

    def test_missing_art_falls_back_to_the_card_the_app_shows(self):
        # BlogCover.tsx shows og-blog-<slug>[-ru].png for every post; a shared
        # static link must not be the only place a post has no picture.
        (self.art / "three-panels.jpg").unlink()
        (self.root / "og-blog-three-panels.png").write_bytes(b"en card")
        (self.root / "og-blog-three-panels-ru.png").write_bytes(b"ru card")
        self.write_captions({"three-panels": {"en": self.panels}})
        for lang, name in (("en", "og-blog-three-panels.png"), ("ru", "og-blog-three-panels-ru.png")):
            with self.subTest(lang=lang):
                with contextlib.redirect_stderr(io.StringIO()):
                    page = blog.post_page(self.post, lang)
                image = Elements(page).all("img")[0]
                self.assertTrue(image["src"].startswith(f"/{name}?v="))
                # The card is text, not the engraving: never call it a triptych.
                ui, cover = blog.UI[lang], page[page.index('<figure class="blog-cover">'):]
                self.assertTrue(image["alt"].startswith(ui["cardAlt"]))
                for claim in (ui["coverAlt"], ui["coverFull"], "cover-panels", self.panels[0]["heading"]):
                    self.assertNotIn(claim, cover)
                self.assertIn(ui["cardFull"], cover)

    def test_three_panel_transcription_is_visible_with_explicit_english_fallback(self):
        self.write_captions({"three-panels": {"en": self.panels}})
        for render in (blog.post_page, lambda p, lang: blog.index_page([p], lang)):
            page = render(self.post, "ru")
            self.assertIn("Подписи на изображении — на английском", page)
            self.assertIn('class="cover-panels" lang="en"', page)
            self.assertNotIn("<details", page)
            for panel in self.panels:
                self.assertIn(panel["heading"], page)
                self.assertIn(panel["caption"], page)

    def test_russian_transcription_is_used_when_provided(self):
        ru = [{"heading": f"ПАНЕЛЬ {n}", "caption": f"Вывод {n}."} for n in (1, 2, 3)]
        self.write_captions({"three-panels": {"en": self.panels, "ru": ru}})
        page = blog.post_page(self.post, "ru")
        self.assertIn('class="cover-panels" lang="ru"', page)
        self.assertNotIn("Подписи на изображении — на английском", page)
        self.assertIn("Вывод 3.", page)

    def test_invalid_panel_metadata_fails_instead_of_silently_dropping_a_panel(self):
        self.write_captions({"three-panels": {"en": self.panels[:2]}})
        with self.assertRaisesRegex(SystemExit, "exactly three"):
            blog.post_page(self.post)

    def test_caption_text_is_html_escaped(self):
        self.panels[0] = {"heading": "<THE & OBSERVATION>", "caption": 'A "quoted" result.'}
        self.write_captions({"three-panels": {"en": self.panels}})
        page = blog.post_page(self.post)
        self.assertIn("&lt;THE &amp; OBSERVATION&gt;", page)
        self.assertNotIn("<THE & OBSERVATION>", page)

    def test_cover_css_preserves_ratio_on_mobile_and_does_not_crop(self):
        self.assertIn(".blog-cover img{", blog.CSS)
        self.assertIn("height:auto", blog.CSS)
        self.assertIn("object-fit:contain", blog.CSS)
        self.assertNotIn("object-fit:cover", blog.CSS)
        self.assertIn("@media(max-width:600px)", blog.CSS)


class TerminalBlockTests(unittest.TestCase):
    """trinity#1273 added a `terminal` block; until build-blog knew it, every
    publish from 2026-10-03 14:04 UTC stopped on `unknown block kind`."""

    block = {"kind": "terminal", "src": "term/devkit-flow/session.cast",
             "share": "https://t27.ai/term/devkit-flow/",
             "title": "tri devkit <flow>", "caption": "The run: `tri devkit flow --build`."}

    def test_links_the_recording_page_in_the_reader_language(self):
        en = blog.block_html(self.block)
        ru = blog.block_html(self.block, "ru")
        self.assertIn('<a href="https://t27.ai/term/devkit-flow/">Open the recording on its own page.</a>', en)
        self.assertIn("Открыть запись на отдельной странице.", ru)
        self.assertIn("<code>tri devkit flow --build</code>", en)
        self.assertIn("tri devkit &lt;flow&gt;", en)

    def test_the_static_page_mounts_the_apps_player(self):
        html = blog.block_html(self.block)
        cast = [a for a in Elements(html).all("div") if a.get("class") == "t27-cast"]
        self.assertEqual(cast[0]["data-src"], "/term/devkit-flow/session.cast")
        self.assertEqual(cast[0]["data-share"], "https://t27.ai/term/devkit-flow/")
        page = blog.shell(url="u", title="t", desc="d", og="o.png", body=html)
        self.assertIn("import { mount } from '/term/player.js'", page)
        self.assertNotIn("/term/player.js", blog.shell(url="u", title="t", desc="d", og="o.png", body="<p>x</p>"))

    def test_without_a_share_page_there_is_no_dead_link(self):
        block = {k: v for k, v in self.block.items() if k != "share"}
        self.assertNotIn("<a ", blog.block_html(block))

    def test_an_unknown_kind_still_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "unknown block kind"):
            blog.block_html({"kind": "video"})


if __name__ == "__main__":
    unittest.main()
