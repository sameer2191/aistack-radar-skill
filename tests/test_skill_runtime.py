import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "aistack-radar"


class SkillRuntimeTests(unittest.TestCase):
    def test_skill_runtime_generates_fixture_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_DIR / "scripts" / "aistack_radar.py"),
                    "research",
                    "LangGraph vs OpenAI Agents SDK",
                    "--fixture",
                    str(SKILL_DIR / "fixtures" / "demo_signal.json"),
                    "--output",
                    tmp,
                    "--emit",
                    "html",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("AI Stack Radar complete: TRIAL", result.stdout)
            self.assertTrue((Path(tmp) / "brief.json").exists())
            self.assertTrue((Path(tmp) / "brief.md").exists())
            self.assertTrue((Path(tmp) / "brief.html").exists())
            data = json.loads((Path(tmp) / "brief.json").read_text(encoding="utf-8"))
            self.assertEqual(data["topic"], "LangGraph vs OpenAI Agents SDK")
            self.assertGreaterEqual(len(data["evidence"]), 8)

    def test_skill_fixture_matches_package_fixture(self):
        package_fixture = json.loads((ROOT / "fixtures" / "demo_signal.json").read_text(encoding="utf-8"))
        skill_fixture = json.loads((SKILL_DIR / "fixtures" / "demo_signal.json").read_text(encoding="utf-8"))
        self.assertEqual(package_fixture, skill_fixture)


if __name__ == "__main__":
    unittest.main()
