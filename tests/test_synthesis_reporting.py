import json
import tempfile
import unittest
from pathlib import Path

from aistack_radar.connectors.fixture import load_fixture
from aistack_radar.models import Recommendation
from aistack_radar.reporting import write_reports
from aistack_radar.synthesis import build_brief


ROOT = Path(__file__).resolve().parents[1]


class SynthesisReportingTests(unittest.TestCase):
    def test_brief_contains_recommendation_and_findings(self):
        run = load_fixture(ROOT / "fixtures" / "demo_signal.json")
        brief = build_brief("LangGraph vs OpenAI Agents SDK", (run,))
        self.assertIn(brief.recommendation, set(Recommendation))
        self.assertGreaterEqual(len(brief.key_findings), 3)
        self.assertGreater(brief.confidence, 0.5)

    def test_report_artifacts_are_written(self):
        run = load_fixture(ROOT / "fixtures" / "demo_signal.json")
        brief = build_brief("LangGraph vs OpenAI Agents SDK", (run,))
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = write_reports(brief, tmp, emit_html=True)
            self.assertEqual(set(artifacts), {"json", "markdown", "html"})
            data = json.loads(Path(artifacts["json"]).read_text(encoding="utf-8"))
            self.assertEqual(data["topic"], "LangGraph vs OpenAI Agents SDK")
            self.assertIn("Recommendation", Path(artifacts["markdown"]).read_text(encoding="utf-8"))
            self.assertIn("<!doctype html>", Path(artifacts["html"]).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

