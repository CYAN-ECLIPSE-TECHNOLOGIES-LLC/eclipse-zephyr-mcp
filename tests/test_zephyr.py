#!/usr/bin/env python3
"""Eclipse Zephyr v0.1 (S2 public-read) — unit tests.
All tests run OFFLINE: the fetcher is replaced with fixture payloads.
The one real captured fixture is profile_bsky_app.json (live public
API response, captured 2026-10-25). Live behavior is exercised only
by smoke.py, and labeled there.
Run: python3 -m unittest discover tests"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import server as Z  # noqa: E402

ROOT = Path(__file__).parent.parent
FIX = ROOT / "fixtures"


def fixture_fetcher(payloads):
    """Return a fetcher(url) that answers from {method-substring: payload}."""
    def fetch(url):
        for key, payload in payloads.items():
            if key in url:
                return payload["response"] if "response" in payload \
                    else payload
        raise AssertionError(f"unexpected URL in offline test: {url}")
    return fetch


def captured(name):
    return json.loads((FIX / name).read_text())


class TestProfileNormalization(unittest.TestCase):
    def test_real_captured_profile_normalizes(self):
        st = Z.empty_state()
        fetch = fixture_fetcher({"getProfile": captured(
            "profile_bsky_app.json")})
        out = Z.t_profile_read(st, {"actor": "bsky.app"}, fetcher=fetch)
        p = out["profile"]
        self.assertEqual(p["handle"], "bsky.app")
        self.assertEqual(p["did"], "did:plc:z72i7hdynmk6r22z27h6tvur")
        self.assertEqual(p["display_name"], "Bluesky")
        self.assertIsInstance(p["followers_count"], int)
        self.assertGreater(p["followers_count"], 1_000_000)
        self.assertEqual(p["source_endpoint"],
                         "app.bsky.actor.getProfile")
        self.assertEqual(out["mode"], "READ_API")

    def test_read_is_receipted(self):
        st = Z.empty_state()
        fetch = fixture_fetcher({"getProfile": captured(
            "profile_bsky_app.json")})
        out = Z.t_profile_read(st, {"actor": "bsky.app"}, fetcher=fetch)
        self.assertEqual(out["receipt_seq"], 1)
        lst = Z.t_receipt_list(st, {})
        self.assertTrue(lst["chain_valid"])
        self.assertEqual(lst["receipts"][0]["detail"]["status"], "ok")


class TestFeedNormalization(unittest.TestCase):
    def test_author_feed_posts_normalized(self):
        st = Z.empty_state()
        fetch = fixture_fetcher({"getAuthorFeed": captured(
            "author_feed_sample.json")})
        out = Z.t_author_feed_read(st, {"actor": "samplemarkets.bsky.social"},
                                   fetcher=fetch)
        self.assertEqual(out["count"], 2)
        first, second = out["posts"]
        self.assertEqual(first["author_handle"],
                         "samplemarkets.bsky.social")
        self.assertIn("$635.6M", first["text"])
        self.assertEqual(first["like_count"], 42)
        self.assertFalse(first["has_media"])
        self.assertTrue(second["has_media"])
        self.assertIn("images", second["embed_type"])


class TestSearchNormalization(unittest.TestCase):
    def test_search_actors_normalized(self):
        st = Z.empty_state()
        fetch = fixture_fetcher({"searchActors": captured(
            "search_actors_sample.json")})
        out = Z.t_actor_search(st, {"query": "sample"}, fetcher=fetch)
        self.assertEqual(out["count"], 2)
        self.assertEqual(out["actors"][0]["handle"],
                         "samplemarkets.bsky.social")
        self.assertEqual(out["actors"][0]["source_endpoint"],
                         "app.bsky.actor.searchActors")


class TestFailureHonesty(unittest.TestCase):
    def test_failed_read_receipted_and_named(self):
        st = Z.empty_state()

        def boom(url):
            raise Z.ToolError("live read failed after retries: "
                              "TimeoutError (fixture)")

        with self.assertRaises(Z.ToolError):
            Z.t_profile_read(st, {"actor": "nobody.example"}, fetcher=boom)
        lst = Z.t_receipt_list(st, {})
        self.assertEqual(lst["count"], 1)
        self.assertEqual(lst["receipts"][0]["detail"]["status"], "error")
        self.assertTrue(lst["chain_valid"])

    def test_no_write_tools_exist(self):
        names = set(Z.TOOLS)
        for forbidden in ("post_create", "publish", "like", "follow",
                          "repost", "delete_post"):
            self.assertNotIn(forbidden, names)
        self.assertEqual(names, {"profile_read", "actor_search",
                                 "author_feed_read", "post_thread_read",
                                 "receipt_list"})


if __name__ == "__main__":
    unittest.main()
