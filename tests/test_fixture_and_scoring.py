import unittest
from datetime import datetime, timezone
from pathlib import Path

from aistack_radar.connectors.fixture import load_fixture
from aistack_radar.models import SourceKind
from aistack_radar.scoring import score_evidence


ROOT = Path(__file__).resolve().parents[1]


class FixtureScoringTests(unittest.TestCase):
    def test_fixture_loads_normalized_items(self):
        run = load_fixture(ROOT / "fixtures" / "demo_signal.json")
        self.assertEqual(run.source, SourceKind.FIXTURE)
        self.assertGreaterEqual(len(run.items), 8)
        self.assertTrue(any(item.source == SourceKind.GITHUB for item in run.items))

    def test_scoring_orders_high_authority_evidence(self):
        run = load_fixture(ROOT / "fixtures" / "demo_signal.json")
        scored = score_evidence((run,), now=datetime(2026, 6, 9, tzinfo=timezone.utc))
        self.assertEqual(len(scored), len(run.items))
        self.assertGreater(scored[0].score, scored[-1].score)
        self.assertIn(scored[0].item.source, {SourceKind.GITHUB, SourceKind.DOCS})


if __name__ == "__main__":
    unittest.main()

