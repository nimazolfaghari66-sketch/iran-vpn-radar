"""Integration: the README subscription table updates inside a real cycle.

Runs ``pipeline.run_cycle`` with all network stages disabled and a seeded state
store, so it exercises the exact code path the 2-hour scheduler uses — proving
the README refresh is part of the cycle and not a one-off script.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar import config as cfg  # noqa: E402
from radar import readme  # noqa: E402
from radar.normalize import parse_uri  # noqa: E402
from radar.pipeline import run_cycle  # noqa: E402
from radar.quality import apply_success  # noqa: E402
from radar.storage import Store  # noqa: E402
from radar.tunnel_verify import TUNNEL_VERIFIED  # noqa: E402


class TestCycleUpdatesReadme(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sources").mkdir()
        (self.root / "sources" / "seed_sources.json").write_text("[]", encoding="utf-8")
        for name, _lang in readme.README_LANGS:
            (self.root / name).write_text(
                f"# T\n\n{readme.START}\nstale\n{readme.END}\n\n## X\n\nkeep\n", encoding="utf-8"
            )

        # Seed a store with one iran-priority config so a file is produced.
        conf = parse_uri("vless://u1@a.com:443?security=tls#a")
        apply_success(conf, {})
        conf.tunnel_status = TUNNEL_VERIFIED
        conf.iran_reachability = cfg.IRAN_TCP_REACHABLE
        store = Store(self.root / "data")
        store.save_configs({conf.fingerprint: conf})

        self.settings = cfg.load_settings(self.root)
        self.settings.max_sources_per_run = 0
        self.settings.checkhost_enabled = False
        self.settings.globalping_enabled = False
        self.settings.tunnel_enabled = False
        self.settings.publish_enabled = False
        self.settings.dry_run = False

    def tearDown(self):
        self.tmp.cleanup()

    def test_readme_refreshed_by_cycle(self):
        stats = run_cycle(self.settings)
        self.assertIn("readme", stats.to_dict())
        self.assertIn("README.en.md", stats.readme["updated"])
        text = (self.root / "README.en.md").read_text(encoding="utf-8")
        self.assertNotIn("stale", text)
        self.assertIn("keep", text)
        # The seeded config is in the iran-priority file, so the table shows it.
        self.assertEqual(stats.readme["counts"]["vless"], 1)
        self.assertIn("iran-priority/vless", text)


if __name__ == "__main__":
    unittest.main()
