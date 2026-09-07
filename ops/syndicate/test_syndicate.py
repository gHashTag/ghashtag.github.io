"""Isolated dispatch/state regressions. No real config, state, or API access."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch


SPEC = importlib.util.spec_from_file_location(
    "syndicate", Path(__file__).with_name("syndicate.py")
)
syndicate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(syndicate)


class DispatchTests(unittest.TestCase):
    target = "phi-is-a-scale-not-information"
    newer = "tri-claw-an-agent-you-can-audit"

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="t27-syndicate-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.state = self.root / "state" / "state.json"
        self.config = self.root / "config.json"
        self.lock = self.state.with_name("state.json.lock")
        self.posts = [
            {"slug": self.target, "date": "2026-08-20"},
            {"slug": self.newer, "date": "2026-08-31"},
            {"slug": "not-yet-published", "date": "2099-01-01"},
        ]
        (self.root / "blog-posts.json").write_text(json.dumps(self.posts))
        self.channels = {
            name: {field: "test-only" for field in fields}
            for name, fields in syndicate.REQUIRED.items()
        }
        self.write_config()
        self.posters = {
            name: Mock(side_effect=lambda post, channel, dry, name=name: {
                "ok": True, "id": f"{name}:{post['slug']}", "dry": dry,
            }) for name in syndicate.VALID_CHANNELS
        }
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        for attribute, value in {
            "REPO": self.root, "CONFIG_PATH": self.config,
            "STATE_PATH": self.state, "POSTERS": self.posters,
        }.items():
            stack.enter_context(patch.object(syndicate, attribute, value))
        stack.enter_context(patch.object(syndicate.time, "strftime", return_value="2026-09-07"))
        stack.enter_context(patch.object(
            syndicate.requests.sessions.Session, "request",
            side_effect=AssertionError("network is forbidden in these tests"),
        ))

    def write_config(self):
        self.config.write_text(json.dumps({"channels": self.channels}))

    def write_state(self, value):
        self.state.parent.mkdir(parents=True, exist_ok=True)
        self.state.write_text(json.dumps(value))

    def read_state(self):
        return json.loads(self.state.read_text())

    def run_main(self, *args):
        self.output = io.StringIO()
        self.errors = io.StringIO()
        with contextlib.redirect_stdout(self.output), contextlib.redirect_stderr(self.errors):
            return syndicate.main(list(args))

    def assert_no_dispatch(self):
        for poster in self.posters.values():
            poster.assert_not_called()

    def test_exact_slug_and_channel_do_not_pick_newest_or_other_channels(self):
        self.assertEqual(self.run_main("--slug", self.target, "--channel", "telegram"), 0)
        self.posters["telegram"].assert_called_once_with(
            self.posts[0], self.channels["telegram"], False,
        )
        for name in syndicate.VALID_CHANNELS[1:]:
            self.posters[name].assert_not_called()
        self.assertEqual(self.read_state(), {self.target: {"telegram": f"telegram:{self.target}"}})

    def test_unknown_slug_fails_without_creating_state_or_lock(self):
        for value in ("does-not-exist", "phi-is-a-scale", "", self.target.upper()):
            with self.subTest(slug=value), self.assertRaises(SystemExit) as result:
                self.run_main("--slug", value, "--channel", "telegram")
            self.assertEqual(result.exception.code, 2)
        self.assert_no_dispatch()
        self.assertFalse(self.state.parent.exists())

    def test_future_dated_slug_is_not_a_published_article(self):
        with self.assertRaises(SystemExit) as result:
            self.run_main("--slug", "not-yet-published", "--channel", "telegram")
        self.assertEqual(result.exception.code, 2)
        self.assert_no_dispatch()

    def test_unknown_channel_fails_before_dispatch(self):
        with self.assertRaises(SystemExit) as result:
            self.run_main("--slug", self.target, "--channel", "unknown")
        self.assertEqual(result.exception.code, 2)
        self.assert_no_dispatch()
        self.assertFalse(self.state.parent.exists())

    def test_explicit_unconfigured_channel_fails_instead_of_silent_skip(self):
        self.channels["telegram"]["bot_token"] = ""
        self.write_config()
        with self.assertRaises(SystemExit) as result:
            self.run_main("--slug", self.target, "--channel", "telegram")
        self.assertEqual(result.exception.code, 2)
        self.assertIn("not configured", self.errors.getvalue())
        self.assert_no_dispatch()

    def test_selectors_cannot_be_ignored_by_update_profile(self):
        with patch.object(syndicate, "update_profile") as update:
            with self.assertRaises(SystemExit) as result:
                self.run_main("--slug", self.target, "--update-profile")
            self.assertEqual(result.exception.code, 2)
            update.assert_not_called()

    def test_dry_run_never_creates_state_directory_or_lock(self):
        self.assertEqual(self.run_main("--slug", self.target, "--channel", "telegram", "--dry-run"), 0)
        self.posters["telegram"].assert_called_once_with(
            self.posts[0], self.channels["telegram"], True,
        )
        self.assertFalse(self.state.parent.exists())

    def test_dry_run_preserves_existing_state_bytes_and_mtime(self):
        self.write_state({self.newer: {"indexnow": "ok"}})
        before = self.state.read_bytes(), self.state.stat().st_mtime_ns
        self.assertEqual(self.run_main("--slug", self.target, "--channel", "telegram", "--dry-run"), 0)
        self.assertEqual((self.state.read_bytes(), self.state.stat().st_mtime_ns), before)
        self.assertFalse(self.lock.exists())

    def test_legacy_string_receipts_deduplicate_without_rewriting_state(self):
        self.write_state({self.target: {"telegram": "42", "indexnow": "ok"}})
        before = self.state.read_bytes(), self.state.stat().st_mtime_ns
        self.assertEqual(self.run_main("--slug", self.target, "--channel", "telegram"), 0)
        self.assert_no_dispatch()
        self.assertEqual((self.state.read_bytes(), self.state.stat().st_mtime_ns), before)

    def test_channel_selection_filters_backlog_by_that_channel_only(self):
        self.write_state({self.newer: {"telegram": "42"}})
        self.assertEqual(self.run_main("--channel", "telegram"), 0)
        self.posters["telegram"].assert_called_once_with(self.posts[0], self.channels["telegram"], False)
        for name in syndicate.VALID_CHANNELS[1:]:
            self.posters[name].assert_not_called()

    def test_held_lock_blocks_dispatch_and_releases_for_next_run(self):
        with syndicate.state_lock(self.state):
            self.assertEqual(self.run_main("--slug", self.target, "--channel", "telegram"), 1)
            self.assertIn("holds the state lock", self.errors.getvalue())
            self.assert_no_dispatch()
        self.assertEqual(self.run_main("--slug", self.target, "--channel", "telegram"), 0)
        self.posters["telegram"].assert_called_once()

    def test_state_is_loaded_after_lock_acquisition(self):
        real_lock = syndicate.state_lock

        @contextlib.contextmanager
        def competing_writer(path):
            self.write_state({self.target: {"telegram": "already-sent"}})
            with real_lock(path):
                yield

        with patch.object(syndicate, "state_lock", competing_writer):
            self.assertEqual(self.run_main("--slug", self.target, "--channel", "telegram"), 0)
        self.assert_no_dispatch()

    def test_partial_success_is_saved_before_next_channel_and_failures_are_nonzero(self):
        self.write_state({"legacy-post": {"telegram": "9", "indexnow": "ok"}})
        observed_before_next_channel = []

        def fail_after_first_save(*args):
            observed_before_next_channel.append(self.read_state()[self.target])
            raise RuntimeError("simulated downstream outage")

        self.posters["devto"].side_effect = fail_after_first_save
        self.assertEqual(self.run_main("--slug", self.target), 1)
        self.assertEqual(observed_before_next_channel, [{"telegram": f"telegram:{self.target}"}])
        state = self.read_state()
        self.assertEqual(state["legacy-post"], {"telegram": "9", "indexnow": "ok"})
        self.assertNotIn("devto", state[self.target])
        self.assertEqual(set(state[self.target]), {"telegram", "hashnode", "medium", "indexnow"})

    def test_interrupt_after_first_success_preserves_receipt(self):
        self.posters["devto"].side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.run_main("--slug", self.target)
        self.assertEqual(self.read_state(), {self.target: {"telegram": f"telegram:{self.target}"}})
        self.posters["hashnode"].assert_not_called()
        with syndicate.state_lock(self.state):
            pass

    def test_failed_atomic_replace_keeps_old_state_and_stops_dispatch(self):
        self.write_state({"legacy-post": {"telegram": "9"}})
        before = self.state.read_bytes()
        with patch.object(syndicate.os, "replace", side_effect=OSError("disk failure")):
            self.assertEqual(self.run_main("--slug", self.target), 1)
        self.assertEqual(self.state.read_bytes(), before)
        self.assertFalse(list(self.state.parent.glob(".state.json.*.tmp")))
        self.posters["telegram"].assert_called_once()
        self.posters["devto"].assert_not_called()


if __name__ == "__main__":
    unittest.main()
