import unittest
from pathlib import Path

from aistack_radar.connectors import collect_sources


ROOT = Path(__file__).resolve().parents[1]


class CollectorTests(unittest.TestCase):
    def test_unknown_source_becomes_warning(self):
        runs = collect_sources("LangGraph", sources=("unknown",))
        self.assertEqual(len(runs), 1)
        self.assertIn("unknown source", runs[0].warnings[0])

    def test_fixture_and_unknown_source_can_coexist(self):
        runs = collect_sources("LangGraph", fixture=ROOT / "fixtures" / "demo_signal.json", sources=("unknown",))
        self.assertEqual(len(runs), 2)
        self.assertGreater(len(runs[0].items), 0)
        self.assertTrue(runs[1].warnings)


if __name__ == "__main__":
    unittest.main()

