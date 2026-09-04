import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from pathlib import Path

from aistack_radar.connectors.fixture import load_fixture
from aistack_radar.models import SourceKind, SourceRun
from aistack_radar.scoring import score_evidence


ROOT = Path(__file__).resolve().parents[1]


class FixtureScoringTests(unittest.TestCase):
    def test_fixture_loads_normalized_items(self):
        run = load_fixture(ROOT / "fixtures" / "demo_signal.json")
        self.assertEqual(run.source, SourceKind.FIXTURE)
        self.assertGreaterEqual(len(run.items), 8)
        self.assertTrue(any(item.source == SourceKind.GITHUB for item in run.items))

    def test_fixture_scores_keep_the_reference_time_as_wall_clock_advances(self):
        run = load_fixture(ROOT / "fixtures" / "demo_signal.json")
        self.assertEqual(run.as_of, datetime(2026, 6, 9, tzinfo=timezone.utc))
        expected = score_evidence((run,), now=run.as_of)
        for year in (2030, 2040):
            with self.subTest(year=year), patch("aistack_radar.scoring.datetime") as clock:
                clock.now.return_value = datetime(year, 1, 1, tzinfo=timezone.utc)
                self.assertEqual(score_evidence((run,)), expected)
                clock.now.assert_not_called()

    def test_live_and_mixed_runs_still_age_with_the_wall_clock(self):
        fixture = load_fixture(ROOT / "fixtures" / "demo_signal.json")
        live = SourceRun(source=SourceKind.GITHUB, items=fixture.items)
        for runs in ((live,), (fixture, live)):
            with self.subTest(sources=[run.source for run in runs]):
                with patch("aistack_radar.scoring.datetime") as clock:
                    clock.now.return_value = datetime(2026, 6, 9, tzinfo=timezone.utc)
                    early = score_evidence(runs)
                    clock.now.return_value = datetime(2040, 1, 1, tzinfo=timezone.utc)
                    later = score_evidence(runs)
                self.assertGreater(sum(item.score for item in early), sum(item.score for item in later))

    def test_explicit_clock_overrides_the_fixture_reference(self):
        run = load_fixture(ROOT / "fixtures" / "demo_signal.json")
        current = score_evidence((run,), now=datetime(2040, 1, 1, tzinfo=timezone.utc))
        self.assertNotEqual(score_evidence((run,)), current)

    def test_scoring_orders_high_authority_evidence(self):
        run = load_fixture(ROOT / "fixtures" / "demo_signal.json")
        scored = score_evidence((run,), now=datetime(2026, 6, 9, tzinfo=timezone.utc))
        self.assertEqual(len(scored), len(run.items))
        self.assertGreater(scored[0].score, scored[-1].score)
        self.assertIn(scored[0].item.source, {SourceKind.GITHUB, SourceKind.DOCS})


if __name__ == "__main__":
    unittest.main()

