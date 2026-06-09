"""Topic planning utilities."""

from __future__ import annotations

import re

from .models import TopicPlan


COMPARISON_SPLIT_RE = re.compile(r"\s+(?:vs\.?|versus|against)\s+|,\s*(?:and\s+)?|\s+\|\s+|\s+and\s+(?=[A-Z0-9])", re.IGNORECASE)
QUESTION_PREFIX_RE = re.compile(
    r"^(?:compare|evaluate|assess|benchmark|research|analyze|choose\s+between|pick\s+between)\s+",
    re.IGNORECASE,
)
CONTEXT_SUFFIX_RE = re.compile(
    r"\s+(?:for|when|where|in)\s+(?:production|enterprise|technical|agent|ai|llm|rag|developer|data|202\d|the\s+enterprise|real-world)\b.*$",
    re.IGNORECASE,
)


def _comparison_subject(topic: str) -> str:
    subject = QUESTION_PREFIX_RE.sub("", topic).strip()
    if subject.lower().startswith("between "):
        subject = subject[len("between ") :].strip()
    context_match = re.search(r"\s+for\s+", subject, flags=re.IGNORECASE)
    if context_match:
        prefix = subject[: context_match.start()]
        if len(COMPARISON_SPLIT_RE.split(prefix)) > 1:
            subject = prefix.strip()
    return subject


def _clean_entity(entity: str) -> str:
    cleaned = entity.strip(" \"'.:;")
    cleaned = re.sub(r"^(?:and|or)\s+", "", cleaned, flags=re.IGNORECASE).strip(" \"'.:;")
    cleaned = CONTEXT_SUFFIX_RE.sub("", cleaned).strip(" \"'.:;")
    return cleaned


def plan_topic(topic: str) -> TopicPlan:
    """Create a lightweight plan for source collection and synthesis."""

    normalized = " ".join(topic.strip().split())
    if not normalized:
        raise ValueError("topic must not be empty")

    lower = normalized.lower()
    if lower.startswith("alternatives to "):
        subject = normalized[len("alternatives to ") :].strip()
        return TopicPlan(topic=normalized, entities=(subject,), comparison=True, aliases={subject: (f"{subject} alternatives",)})

    subject = _comparison_subject(normalized)
    entities = tuple(
        entity
        for entity in (_clean_entity(part) for part in COMPARISON_SPLIT_RE.split(subject))
        if entity
    )
    comparison = len(entities) > 1
    if not entities:
        entities = (normalized,)
    return TopicPlan(topic=normalized, entities=entities, comparison=comparison)


def source_query(plan: TopicPlan) -> str:
    if plan.comparison:
        return " ".join(plan.entities)
    return plan.topic
