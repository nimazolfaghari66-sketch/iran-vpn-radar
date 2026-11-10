"""Tests for the automatic README subscription section."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar import config as cfg  # noqa: E402
from radar import readme  # noqa: E402
from radar.generate import build_priority_files, write_files  # noqa: E402
from radar.normalize import parse_uri  # noqa: E402
from radar.quality import apply_success  # noqa: E402
from radar.tunnel_verify import TUNNEL_VERIFIED  # noqa: E402

RAW = "https://raw.githubusercontent.com/o/r/main"


def _priority(uri: str):
    """A config that qualifies for the iran-priority tier."""
    conf = parse_uri(uri)
    apply_success(conf, {})
    conf.tunnel_status = TUNNEL_VERIFIED
    conf.iran_reachability = cfg.IRAN_TCP_REACHABLE
    return conf


class TestCounting(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.sub = Path(self.tmp.name) / "subscriptions"

    def tearDown(self):
        self.tmp.cleanup()

    def _write_tier(self, lines: dict[str, list[str]]):
        tier = self.sub / "iran-priority"
        tier.mkdir(parents=True, exist_ok=True)
        for name, entries in lines.items():
            (tier / name).write_text("\n".join(entries) + ("\n" if entries else ""), encoding="utf-8")

    def test_counts_unique_valid_configs(self):
        self._write_tier(
            {
                "all": [
                    "vless://u1@a.com:443?security=tls#a",
                    "vless://u1@a.com:443?security=tls#different-tag",  # same fingerprint
                    "trojan://pw@b.com:443#b",
                    "not-a-valid-uri",
                ],
                "vless": ["vless://u1@a.com:443?security=tls#a"],
                "trojan": ["trojan://pw@b.com:443#b"],
                **{p: [] for p, _ in readme.ROWS if p not in ("vless", "trojan")},
            }
        )
        counts, errors = readme.count_tier(self.sub)
        self.assertEqual(counts["all"], 2)  # duplicate + invalid dropped
        self.assertEqual(counts["vless"], 1)
        self.assertEqual(counts["trojan"], 1)
        self.assertEqual(errors, {})

    def test_missing_file_reported_not_zero(self):
        self._write_tier({"all": ["vless://u1@a.com:443?security=tls#a"]})
        counts, errors = readme.count_tier(self.sub)
        self.assertIn("vless", errors)
        self.assertIn("missing", errors["vless"])

    def test_empty_file_is_valid_zero(self):
        self._write_tier({name: [] for name, _ in readme.ROWS} | {"all": []})
        counts, errors = readme.count_tier(self.sub)
        self.assertEqual(errors, {})
        self.assertEqual(counts["vless"], 0)
        self.assertEqual(counts["all"], 0)


class TestRenderAndReplace(unittest.TestCase):
    def test_block_has_exact_columns_and_full_urls(self):
        block = readme.render_block("en", RAW, {p: 0 for p, _ in readme.ROWS} | {"all": 0}, {})
        self.assertIn("| Protocol | Subscription link | Active configs |", block)
        for proto, display in readme.ROWS:
            url = f"{RAW}/subscriptions/iran-priority/{proto}"
            self.assertIn(f"| **{display}** | [{url}]({url}) |", block)
        all_url = f"{RAW}/subscriptions/iran-priority/all"
        self.assertIn(f"**All protocols (all):** [{all_url}]({all_url})", block)
        self.assertNotIn("subscriptions/vless)", block)

    def test_unavailable_marker_when_file_missing(self):
        block = readme.render_block("en", RAW, {"all": 0}, {"tuic": "file is missing"})
        self.assertIn("⚠️ unavailable", block)

    def test_replace_only_between_markers(self):
        text = "HEAD\n" + readme.START + "\nold\n" + readme.END + "\nTAIL"
        new_block = readme.render_block("en", RAW, {"all": 3}, {})
        out, status = readme.update_readme_text(text, new_block)
        self.assertEqual(status, "updated")
        self.assertTrue(out.startswith("HEAD\n"))
        self.assertTrue(out.endswith("\nTAIL"))
        self.assertNotIn("old", out)

    def test_no_markers_leaves_text_untouched(self):
        text = "no markers here\n"
        out, status = readme.update_readme_text(text, "block")
        self.assertEqual(status, "no-markers")
        self.assertEqual(out, text)


class TestUpdateReadmes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.sub = self.root / "subscriptions"
        # Build real iran-priority files from configs so counts match the files.
        configs = {}
        for uri in (
            "vless://u1@a.com:443?security=tls#a",
            "vless://u2@b.com:443?security=tls#b",
            "trojan://pw@c.com:443#c",
        ):
            conf = _priority(uri)
            configs[conf.fingerprint] = conf
        files = build_priority_files(configs, self.sub)
        write_files(files)
        self.settings = cfg.load_settings(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def _seed_readme(self, name: str, lang: str):
        body = (
            f"# Title\n\n{readme.START}\nplaceholder\n{readme.END}\n\n"
            "## Unrelated\n\nDo not touch me.\n"
        )
        (self.root / name).write_text(body, encoding="utf-8")

    def test_updates_all_languages_and_preserves_unrelated(self):
        for name, lang in readme.README_LANGS:
            self._seed_readme(name, lang)
        result = readme.update_readmes(self.settings)
        self.assertTrue(result.ok, result.problems)
        self.assertEqual(sorted(result.updated), sorted(n for n, _ in readme.README_LANGS))
        self.assertEqual(result.counts["vless"], 2)
        self.assertEqual(result.counts["trojan"], 1)
        for name, lang in readme.README_LANGS:
            text = (self.root / name).read_text(encoding="utf-8")
            self.assertIn("Do not touch me.", text)
            self.assertIn(readme.L[lang]["headers"][0], text)
            self.assertIn(f"iran-priority/vless", text)
            self.assertNotIn("placeholder", text)

    def test_idempotent_second_run(self):
        for name, lang in readme.README_LANGS:
            self._seed_readme(name, lang)
        readme.update_readmes(self.settings)
        result = readme.update_readmes(self.settings)
        self.assertEqual(result.updated, [])
        self.assertEqual(sorted(result.skipped), sorted(n for n, _ in readme.README_LANGS))

    def test_missing_readme_reported(self):
        self._seed_readme("README.md", "fa")
        result = readme.update_readmes(self.settings)
        self.assertFalse(result.ok)
        self.assertTrue(any("README.en.md: missing" in p for p in result.problems))


class TestCountsMatchGeneratorRules(unittest.TestCase):
    """The displayed count must equal the number of unique valid URIs in the file."""

    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "subscriptions"
            configs = {}
            for uri in (
                "vless://u1@a.com:443?security=tls#a",
                "vless://u1@a.com:443?security=tls#b",  # duplicate fingerprint
                "vmess://" + __import__("base64").b64encode(
                    b'{"add":"x.com","port":"443","id":"11111111-1111-1111-1111-111111111111","net":"ws","tls":"tls"}'
                ).decode(),
                "trojan://pw@c.com:443#c",
            ):
                conf = _priority(uri)
                configs.setdefault(conf.fingerprint, conf)
            files = build_priority_files(configs, sub)
            write_files(files)
            by_name = {f.name: f for f in files}
            counts, errors = readme.count_tier(sub)
            self.assertEqual(errors, {})
            for name, gen in by_name.items():
                short = name.split("/", 1)[1]
                self.assertEqual(counts[short], gen.count)


if __name__ == "__main__":
    unittest.main()
