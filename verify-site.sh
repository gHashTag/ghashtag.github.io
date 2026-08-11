#!/usr/bin/env bash
# Check that what is committed here is what t27.ai actually serves.
#
# Written because three separate checks returned a confident green on something
# broken: a build script that skips the typechecker, an asset-hash pattern that
# missed the underscore in Vite hashes and so compared an empty string against
# an empty string, and a redirect stub that looked right in a browser while
# every crawler received the homepage.
#
# Every check here fails loudly on an empty value rather than treating it as a
# pass. That is the whole point.
#
#   ./verify-site.sh          check the live site
#   ./verify-site.sh --local  check only what is on disk (no network)

set -uo pipefail
cd "$(dirname "$0")"

SITE="https://t27.ai"
PAGES="gft verification proof ip course cases about"
fails=0

red()  { printf '  \033[31m✗\033[0m %s\n' "$1"; fails=$((fails + 1)); }
green(){ printf '  \033[32m✓\033[0m %s\n' "$1"; }

echo
echo "── on disk ──"

# The domain lives or dies by this file; a deploy that drops it takes the site
# off its own name.
# A feed that quietly loses an entry is invisible: the reader simply never
# learns the post exists, and nothing on either side reports it. So the entry
# count is compared against the posts the generator actually wrote.
for lang_root in blog ru/blog; do
  feed="$lang_root/feed.xml"
  if [ ! -f "$feed" ]; then
    red "$feed is missing — run build-blog.py"
  else
    entries=$(grep -o '<entry>' "$feed" | wc -l | tr -d ' ')
    posts=$(find "$lang_root" -mindepth 2 -name index.html | wc -l | tr -d ' ')
    if [ "$entries" = "$posts" ] && [ "$entries" != "0" ]; then
      green "$feed lists all $posts post(s)"
    else
      red "$feed has $entries entries for $posts post pages"
    fi
  fi
done

if [ "$(cat CNAME 2>/dev/null)" = "t27.ai" ]; then
  green "CNAME is t27.ai"
else
  red "CNAME missing or wrong: '$(cat CNAME 2>/dev/null)'"
fi

LOCAL_JS=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' index.html 2>/dev/null | head -1)
if [ -n "$LOCAL_JS" ]; then
  green "index.html references $LOCAL_JS"
else
  red "no bundle reference found in index.html — the pattern or the file is wrong"
fi

missing=0
for f in $(grep -o 'assets/[A-Za-z0-9._-]*' index.html 2>/dev/null | sort -u); do
  [ -f "$f" ] || { red "index.html references a missing file: $f"; missing=1; }
done
[ "$missing" = 0 ] && green "every referenced asset exists on disk"

# A landing page that redirects into a fragment URL cannot be indexed: the
# crawler discards the fragment and files the page under the homepage.
for p in $PAGES; do
  f="$p/index.html"
  if [ ! -f "$f" ]; then
    red "$p/ is missing"
    continue
  fi
  words=$(sed -e 's/<[^>]*>/ /g' "$f" | wc -w | tr -d ' ')
  if grep -q 'location.replace\|http-equiv="refresh"' "$f"; then
    red "$p/ still auto-redirects — it will not be indexed"
  elif [ "$words" -lt 150 ]; then
    red "$p/ has only $words words — too thin to index"
  else
    green "$p/ is a real page ($words words)"
  fi
  for tag in 'og:title' 'og:description' 'og:image' 'rel="canonical"'; do
    grep -q "$tag" "$f" || red "$p/ is missing $tag"
  done

  # The tag being present is not the same as the image existing. That was only
  # checked against the live site, so a page could point at a file that was
  # never created and the on-disk gate stayed green -- which is how /about/ once
  # shipped referencing an og-about.svg that did not exist.
  # SVG is refused outright: no social platform renders it, so an SVG card is
  # indistinguishable from having no card at all.
  ogsrc=$(grep -o 'property="og:image" content="[^"]*"' "$f" | head -1 | sed 's/.*content="//;s/"$//')
  ogfile="${ogsrc#$SITE/}"
  if [ -z "$ogsrc" ]; then
    red "$p/ has no og:image content"
  elif [ ! -f "$ogfile" ]; then
    red "$p/ points at $ogfile, which is not on disk"
  elif [ "${ogfile##*.}" = "svg" ]; then
    red "$p/ uses an SVG og:image — no social platform renders it"
  else
    green "$p/ og:image $ogfile is on disk"
  fi
done

# /ru/ answered 404 while /ru/gft/ and friends worked, so trimming a URL to its
# parent landed on an error page and Russian search had no front door at all.
if [ ! -f ru/index.html ]; then
  red "ru/index.html is missing — /ru/ is the Russian entry point"
else
  rw=$(sed -e 's/<[^>]*>/ /g' ru/index.html | wc -w | tr -d ' ')
  [ "$rw" -ge 200 ] && green "ru/ is a real page ($rw words)" \
    || red "ru/ is $rw words — too thin to be an entry point"
  grep -q '<html lang="ru"' ru/index.html || red "ru/ does not declare lang=\"ru\""
  grep -q "rel=\"canonical\" href=\"$SITE/ru/\"" ru/index.html \
    || red "ru/ canonical is not $SITE/ru/"
  # An empty slug used to leave href="//", which a browser reads as
  # protocol-relative and follows to a different host.
  grep -q 'href="//"' ru/index.html && red "ru/ contains a protocol-relative href=\"//\""
  grep -qE '/ru//|og--ru' ru/index.html && red "ru/ contains a doubled-slash path"
  [ -f og-home-ru.png ] && green "ru/ og:image og-home-ru.png is on disk" \
    || red "ru/ og:image og-home-ru.png is missing"
  grep -q "<loc>$SITE/ru/</loc>" sitemap.xml 2>/dev/null || red "sitemap.xml does not list /ru/"
  # The other half of the pair lives in the SPA's index.html, which is generated
  # in trinity — so it is the half that silently goes missing on a rebuild.
  grep -q "hreflang=\"ru\" href=\"$SITE/ru/\"" index.html \
    && green "the homepage declares its Russian alternate" \
    || red "index.html does not point at /ru/ — rebuild from trinity, the source carries it"
  grep -q "hreflang=\"en\" href=\"$SITE/\"" ru/index.html \
    || red "ru/ does not point back at the English homepage"
fi

# Russian landings are separate URLs, so each needs its own body, its own card
# and a reciprocal hreflang — a one-way alternate is filed as duplicate content.
for p in $PAGES; do
  rf="ru/$p/index.html"
  if [ ! -f "$rf" ]; then
    red "ru/$p/ is missing — landing-ru.json holds the copy"
    continue
  fi
  rw=$(sed -e 's/<[^>]*>/ /g' "$rf" | wc -w | tr -d ' ')
  if [ "$rw" -lt 200 ]; then
    red "ru/$p/ is $rw words — the Russian copy is not in the HTML"
  else
    green "ru/$p/ is a real page ($rw words)"
  fi
  grep -q '<html lang="ru"' "$rf" || red "ru/$p/ does not declare lang=\"ru\""
  grep -q "hreflang=\"ru\" href=\"$SITE/ru/$p/\"" "$p/index.html" \
    || red "$p/ does not point at its Russian version"
  grep -q "hreflang=\"en\" href=\"$SITE/$p/\"" "$rf" \
    || red "ru/$p/ does not point back at the English version"
  # Structured data on the landings, both languages. Only the homepage had any.
  for g in "$p/index.html" "$rf"; do
    grep -q 'application/ld+json' "$g" || red "$g carries no JSON-LD"
  done
  [ -f "og-$p-ru.png" ] && green "ru/$p/ og:image og-$p-ru.png is on disk" \
    || red "ru/$p/ og:image og-$p-ru.png is missing"
  grep -q "<loc>$SITE/ru/$p/</loc>" sitemap.xml 2>/dev/null \
    || red "sitemap.xml does not list /ru/$p/"
done

# The blog ships as static pages because /blog answered 404 with the SPA shim and
# no article was in the sitemap. Derived from disk, not from a list here, so a
# new post is covered the moment it is generated. Its preview cards are named
# og-blog-<slug>.png, which is why this cannot reuse the $PAGES loops above.
BLOG=$(ls -d blog/*/ 2>/dev/null | sed 's|/$||')
if [ -z "$BLOG" ]; then
  red "blog/ holds no post directories — run build-blog.py"
else
  for d in $BLOG; do
    slug=$(basename "$d")
    f="$d/index.html"
    if [ ! -f "$f" ]; then red "$d/ has no index.html"; continue; fi
    words=$(sed -e 's/<[^>]*>/ /g' "$f" | wc -w | tr -d ' ')
    # A stub that links into the app ranks for nothing; the article itself has
    # to be in the HTML. 400 words is well below the shortest real post.
    if [ "$words" -lt 400 ]; then
      red "blog/$slug is $words words — the article body is not in the HTML"
    else
      green "blog/$slug carries the article ($words words)"
    fi
    grep -q 'rel="canonical"' "$f" || red "blog/$slug has no canonical link"
    # Structured data: only the homepage had any, and a post is where it pays.
    if grep -q 'application/ld+json' "$f"; then
      python3 - "$f" <<'PYCHK' || red "blog/$slug has JSON-LD that does not parse"
import json, re, sys
h = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
d = json.loads(m.group(1))
assert d.get("@type") == "BlogPosting" and d.get("datePublished") and d.get("headline")
PYCHK
      green "blog/$slug JSON-LD parses as a dated BlogPosting"
    else
      red "blog/$slug carries no JSON-LD"
    fi
    img="og-blog-$slug.png"
    [ -f "$img" ] && green "blog/$slug og:image $img is on disk" || red "blog/$slug og:image $img is missing"
    grep -q "<loc>$SITE/blog/$slug/</loc>" sitemap.xml 2>/dev/null \
      || red "sitemap.xml does not list /blog/$slug/"

    # The Russian version is a separate URL, so it needs its own body, its own
    # card and a reciprocal hreflang — a one-way alternate is filed as duplicate
    # content and the translation earns nothing.
    rf="ru/blog/$slug/index.html"
    if [ ! -f "$rf" ]; then
      red "ru/blog/$slug is missing — the Russian text exists in the data"
    else
      rw=$(sed -e 's/<[^>]*>/ /g' "$rf" | wc -w | tr -d ' ')
      if [ "$rw" -lt 400 ]; then
        red "ru/blog/$slug is $rw words — the Russian body is not in the HTML"
      else
        green "ru/blog/$slug carries the article ($rw words)"
      fi
      grep -q '<html lang="ru"' "$rf" || red "ru/blog/$slug does not declare lang=\"ru\""
      grep -q "hreflang=\"ru\" href=\"$SITE/ru/blog/$slug/\"" "$f" \
        || red "blog/$slug does not point at its Russian version"
      grep -q "hreflang=\"en\" href=\"$SITE/blog/$slug/\"" "$rf" \
        || red "ru/blog/$slug does not point back at the English version"
      rimg="og-blog-$slug-ru.png"
      [ -f "$rimg" ] && green "ru/blog/$slug og:image $rimg is on disk" \
        || red "ru/blog/$slug og:image $rimg is missing"
      grep -q "<loc>$SITE/ru/blog/$slug/</loc>" sitemap.xml 2>/dev/null \
        || red "sitemap.xml does not list /ru/blog/$slug/"
    fi
  done
  grep -q "<loc>$SITE/blog/</loc>" sitemap.xml 2>/dev/null \
    || red "sitemap.xml does not list the blog index"

  # blog/ is generated from a snapshot of trinity's posts.ts, so adding a post
  # upstream and republishing leaves the static pages stale and silent. The
  # shipped Blog chunk is the authority on what the app actually serves, so the
  # two are compared rather than trusted.
  blogjs=$(grep -oE 'Blog-[A-Za-z0-9_-]{8}\.js' "$LOCAL_JS" 2>/dev/null | head -1)
  if [ -z "$blogjs" ] || [ ! -f "assets/$blogjs" ]; then
    red "cannot find the shipped Blog chunk — the drift check did not run"
  else
    shipped=$(grep -oE 'slug:"[a-z0-9-]+"' "assets/$blogjs" | sed 's/slug://;s/"//g' | sort -u)
    static=$(ls -d blog/*/ 2>/dev/null | sed 's|blog/||;s|/$||' | sort)
    if [ "$shipped" = "$static" ]; then
      green "static blog matches the shipped app ($(echo "$shipped" | wc -w | tr -d ' ') posts)"
    else
      red "blog drift: the app ships [$(echo $shipped)] but blog/ holds [$(echo $static)] — rerun build-blog.py"
    fi
  fi
fi

# lastmod is worth having only if it is true. A sitemap that stamps every URL
# with today teaches a crawler to ignore the field, so this checks the dates are
# well-formed, not in the future, and that they actually follow the repository.
python3 - <<'PYLM' || red "sitemap lastmod check failed"
import datetime, os, re, sys
t = open("sitemap.xml", encoding="utf-8").read()
locs = re.findall(r"<loc>([^<]*)</loc>", t)
lms = re.findall(r"<lastmod>([^<]*)</lastmod>", t)
if len(lms) != len(locs):
    print(f"  {len(lms)} lastmod for {len(locs)} URLs"); sys.exit(1)
today = datetime.date.today()
for d in lms:
    try:
        v = datetime.date.fromisoformat(d)
    except ValueError:
        print(f"  malformed lastmod {d!r}"); sys.exit(1)
    if v > today:
        print(f"  lastmod in the future: {d}"); sys.exit(1)
# The old test here was "all the dates are the same, therefore the field is not
# derived". That is a proxy, and today it fired on a true state: this site was
# published fifteen times in one day, so every file's last commit really is
# today and every date really is the same. A proxy that cannot tell a constant
# from a coincidence sends you to argue with a correct number.
#
# So the property is tested directly instead. Take a sample of URLs, ask git
# when their files last changed, and require the sitemap to agree. A fabricated
# or hard-coded field disagrees immediately; a genuine same-day spread passes,
# because it is genuine.
import subprocess
sample = [(u, d) for u, d in zip(locs, lms)][:8]
mismatched = []
for url, d in sample:
    rel = url.replace("https://t27.ai/", "") or "index.html"
    f = rel if os.path.isfile(rel) else os.path.join(rel, "index.html")
    if not os.path.isfile(f):
        continue
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", f],
                             capture_output=True).returncode == 0
    if not tracked:
        continue  # new page: today is right by definition, nothing to compare
    g = subprocess.run(["git", "log", "-1", "--format=%cs", "--", f],
                       capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", f],
                           capture_output=True).returncode
    expected = datetime.date.today().isoformat() if dirty else g
    if expected and d != expected:
        mismatched.append((f, d, expected))
if mismatched:
    for f, got, want in mismatched:
        print(f"  {f}: sitemap says {got}, git says {want}")
    print("  lastmod does not follow the repository — the field is not derived")
    sys.exit(1)
PYLM
[ "$fails" = 0 ] && green "sitemap lastmod: $(grep -c '<lastmod>' sitemap.xml) dates, $(grep -oE '<lastmod>[^<]*' sitemap.xml | sort -u | wc -l | tr -d ' ') distinct, none in the future"

grep -q "Sitemap: $SITE/sitemap.xml" robots.txt 2>/dev/null \
  && green "robots.txt points at the sitemap" \
  || red "robots.txt missing or does not reference the sitemap"

for p in $PAGES; do
  grep -q "<loc>$SITE/$p/</loc>" sitemap.xml 2>/dev/null || red "sitemap.xml does not list /$p/"
done
grep -q "<loc>$SITE/</loc>" sitemap.xml 2>/dev/null \
  && green "sitemap.xml lists the homepage and $(grep -c '<loc>' sitemap.xml) URLs in total" \
  || red "sitemap.xml missing or does not list the homepage"

if [ "${1:-}" = "--local" ]; then
  echo
  [ "$fails" = 0 ] && echo "on-disk checks passed" || echo "$fails problem(s) on disk"
  exit $((fails > 0))
fi

echo
echo "── live ──"

LIVE_JS=$(curl -fsS "$SITE/index.html?cb=$RANDOM" 2>/dev/null | grep -o 'assets/index-[A-Za-z0-9_-]*\.js' | head -1)
if [ -z "$LIVE_JS" ]; then
  red "could not read a bundle reference from the live homepage"
elif [ "$LIVE_JS" = "$LOCAL_JS" ]; then
  green "live bundle matches what is committed ($LIVE_JS)"
else
  red "live is serving $LIVE_JS but this checkout has $LOCAL_JS — not published yet, or not published at all"
fi

for p in "" $PAGES; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -L "$SITE/$p")
  [ "$code" = "200" ] && green "/$p → 200" || red "/$p → $code"
done

for p in "" $PAGES; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -L "$SITE/ru/$p/")
  [ "$code" = "200" ] && green "/ru/$p/ → 200" || red "/ru/$p/ → $code"
done

for f in robots.txt sitemap.xml cv.pdf; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$SITE/$f")
  [ "$code" = "200" ] && green "/$f → 200" || red "/$f → $code"
done

# /blog used to answer 404 and serve the SPA shim, which is the failure this
# whole section exists to catch coming back.
for d in blog/ $BLOG ru/blog/ $(echo "$BLOG" | sed 's|^blog/|ru/blog/|'); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -L "$SITE/${d%/}/")
  [ "$code" = "200" ] && green "/${d%/}/ → 200" || red "/${d%/}/ → $code"
done

# Preview images are the difference between a link that sells and a link that
# looks like spam, and they break silently.
for p in $PAGES; do
  img=$(curl -fsS "$SITE/$p/" 2>/dev/null | grep -o 'og:image" content="[^"]*"' | sed 's/.*content="//;s/"$//')
  if [ -z "$img" ]; then
    red "/$p/ serves no og:image"
    continue
  fi
  code=$(curl -s -o /dev/null -w '%{http_code}' "$img")
  [ "$code" = "200" ] && green "/$p/ preview image → 200" || red "/$p/ preview image $img → $code"
done

# The links behind "read the proof" are the ones that must not rot, and they rot
# silently: an audit on 2026-08-10 found eight returning 404, each shipped in all
# five locales, sitting under the theorem and benchmark figures. Read them out of
# the bundle the site actually serves rather than out of the source, because the
# catalogues live outside src/ and a grep over the source reads clean either way.
bundle=$(curl -fsS "$SITE/index.html?cb=$RANDOM" 2>/dev/null | grep -o 'assets/index-[A-Za-z0-9_-]*\.js' | head -1)
if [ -z "$bundle" ]; then
  red "cannot read the bundle to check proof links"
else
  dead=0
  checked=0
  for u in $(curl -fsS "$SITE/$bundle" 2>/dev/null \
               | grep -Eo 'https://github\.com/gHashTag/[A-Za-z0-9._/-]+\.md' | sort -u); do
    checked=$((checked + 1))
    c=$(curl -s -o /dev/null -w '%{http_code}' -L "$u")
    [ "$c" = "200" ] || { red "dead proof link ($c): $u"; dead=$((dead + 1)); }
  done
  if [ "$checked" = 0 ]; then
    red "found no proof links in the bundle — the pattern or the bundle is wrong"
  elif [ "$dead" = 0 ]; then
    green "all $checked proof links resolve"
  fi
fi

echo
if [ "$fails" = 0 ]; then
  echo "all checks passed"
else
  echo "$fails check(s) failed"
fi
exit $((fails > 0))
