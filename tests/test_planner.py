import unittest

from aistack_radar.planner import plan_topic, source_query


class PlannerTests(unittest.TestCase):
    def test_comparison_topic(self):
        plan = plan_topic("LangGraph vs OpenAI Agents SDK")
        self.assertTrue(plan.comparison)
        self.assertEqual(plan.entities, ("LangGraph", "OpenAI Agents SDK"))
        self.assertEqual(source_query(plan), "LangGraph OpenAI Agents SDK")

    def test_comparison_question_strips_instruction_and_decision_context(self):
        plan = plan_topic("Compare LangGraph, OpenAI Agents SDK, and CrewAI for production agent orchestration in 2026.")
        self.assertTrue(plan.comparison)
        self.assertEqual(plan.entities, ("LangGraph", "OpenAI Agents SDK", "CrewAI"))

    def test_alternatives_topic(self):
        plan = plan_topic("alternatives to LangGraph")
        self.assertTrue(plan.comparison)
        self.assertEqual(plan.entities, ("LangGraph",))
        self.assertIn("LangGraph alternatives", plan.aliases["LangGraph"])

    def test_empty_topic_rejected(self):
        with self.assertRaises(ValueError):
            plan_topic("   ")


if __name__ == "__main__":
    unittest.main()
