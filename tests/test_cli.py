import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aistack_radar.cli import main
from aistack_radar.models import SourceKind, SourceRun


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_research_fixture_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = main(
                [
                    "research",
                    "LangGraph vs OpenAI Agents SDK",
                    "--fixture",
                    str(ROOT / "fixtures" / "demo_signal.json"),
                    "--output",
                    tmp,
                    "--emit",
                    "html",
                ]
            )
            self.assertEqual(code, 0)
            self.assertTrue((Path(tmp) / "brief.json").exists())
            self.assertTrue((Path(tmp) / "brief.md").exists())
            self.assertTrue((Path(tmp) / "brief.html").exists())
            data = json.loads((Path(tmp) / "brief.json").read_text(encoding="utf-8"))
            self.assertIn(data["recommendation"], {"adopt", "trial", "watch", "avoid"})

    def test_live_defaults_when_no_fixture_or_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("aistack_radar.cli.collect_sources", return_value=(SourceRun(source=SourceKind.GITHUB),)) as mocked:
                code = main(["research", "LangGraph", "--output", tmp])
            self.assertEqual(code, 0)
            self.assertEqual(mocked.call_args.kwargs["sources"], ("github", "hackernews", "pypi"))


if __name__ == "__main__":
    unittest.main()
