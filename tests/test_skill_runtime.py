import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "aistack-radar"


def load_skill_runtime():
    spec = importlib.util.spec_from_file_location("aistack_radar_skill_runtime", SKILL_DIR / "scripts" / "aistack_radar.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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

    def test_skill_runtime_fetch_json_falls_back_to_curl(self):
        module = load_skill_runtime()
        completed = subprocess.CompletedProcess(args=["curl"], returncode=0, stdout='{"ok": true}', stderr="")

        with patch.object(module.urllib.request, "urlopen", side_effect=OSError("certificate verify failed")):
            with patch.object(module.shutil, "which", return_value="/usr/bin/curl"):
                with patch.object(module.subprocess, "run", return_value=completed) as run:
                    payload = module.fetch_json("https://example.test/data.json", timeout=2)

        self.assertEqual(payload, {"ok": True})
        self.assertIn("https://example.test/data.json", run.call_args.args[0])

    def test_skill_runtime_expands_comparison_topics(self):
        module = load_skill_runtime()
        self.assertEqual(
            module.expand_queries("LangGraph vs OpenAI Agents SDK vs CrewAI"),
            ("LangGraph", "OpenAI Agents SDK", "CrewAI"),
        )
        self.assertEqual(
            module.expand_queries("Compare LangGraph, OpenAI Agents SDK, and CrewAI for production agent orchestration in 2026."),
            ("LangGraph", "OpenAI Agents SDK", "CrewAI"),
        )

    def test_skill_runtime_package_aliases(self):
        module = load_skill_runtime()
        self.assertEqual(module.package_name("LangGraph"), "langgraph")
        self.assertEqual(module.package_name("OpenAI Agents SDK"), "openai-agents")
        self.assertEqual(module.package_name("CrewAI"), "crewai")

    def test_skill_runtime_github_aliases(self):
        module = load_skill_runtime()
        self.assertEqual(module.github_repo_alias("LangGraph"), "langchain-ai/langgraph")
        self.assertEqual(module.github_repo_alias("OpenAI Agents SDK"), "openai/openai-agents-python")
        self.assertEqual(module.github_repo_alias("CrewAI"), "crewAIInc/crewAI")


if __name__ == "__main__":
    unittest.main()
