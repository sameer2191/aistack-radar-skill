"""Topic planning utilities."""

from __future__ import annotations

import re

from .models import TopicPlan


COMPARISON_SPLIT_RE = re.compile(r"\s+(?:vs\.?|versus|against)\s+|,\s*|\s+\|\s+", re.IGNORECASE)


def plan_topic(topic: str) -> TopicPlan:
    """Create a lightweight plan for source collection and synthesis."""

    normalized = " ".join(topic.strip().split())
    if not normalized:
        raise ValueError("topic must not be empty")

    lower = normalized.lower()
    if lower.startswith("alternatives to "):
        subject = normalized[len("alternatives to ") :].strip()
        return TopicPlan(topic=normalized, entities=(subject,), comparison=True, aliases={subject: (f"{subject} alternatives",)})

    entities = tuple(part.strip(" \"'") for part in COMPARISON_SPLIT_RE.split(normalized) if part.strip(" \"'"))
    comparison = len(entities) > 1
    if not entities:
        entities = (normalized,)
    return TopicPlan(topic=normalized, entities=entities, comparison=comparison)


def source_query(plan: TopicPlan) -> str:
    if plan.comparison:
        return " ".join(plan.entities)
    return plan.topic

