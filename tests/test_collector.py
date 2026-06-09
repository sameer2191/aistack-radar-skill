import unittest
from pathlib import Path
from unittest.mock import patch

from aistack_radar.connectors import collector
from aistack_radar.connectors import collect_sources
from aistack_radar.connectors.live import github_repo_alias, package_name
from aistack_radar.models import EvidenceItem, SourceKind, SourceRun


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

    def test_comparison_topics_fan_out_per_entity(self):
        calls = []

        def stub_github(topic: str, timeout: float = 8.0) -> SourceRun:
            calls.append(topic)
            return SourceRun(
                source=SourceKind.GITHUB,
                items=(
                    EvidenceItem(
                        source=SourceKind.GITHUB,
                        title=f"{topic} repository",
                        url=f"https://example.test/{topic.lower().replace(' ', '-')}",
                        summary="demo",
                    ),
                ),
            )

        with patch.dict(collector.LIVE_CONNECTORS, {"github": stub_github}):
            runs = collect_sources("LangGraph vs OpenAI Agents SDK vs CrewAI", sources=("github",))

        self.assertEqual(calls, ["LangGraph", "OpenAI Agents SDK", "CrewAI"])
        self.assertEqual(len(runs), 1)
        self.assertEqual(len(runs[0].items), 3)

    def test_python_package_aliases(self):
        self.assertEqual(package_name("LangGraph"), "langgraph")
        self.assertEqual(package_name("OpenAI Agents SDK"), "openai-agents")
        self.assertEqual(package_name("CrewAI"), "crewai")

    def test_github_repo_aliases(self):
        self.assertEqual(github_repo_alias("LangGraph"), "langchain-ai/langgraph")
        self.assertEqual(github_repo_alias("OpenAI Agents SDK"), "openai/openai-agents-python")
        self.assertEqual(github_repo_alias("CrewAI"), "crewAIInc/crewAI")


if __name__ == "__main__":
    unittest.main()
