"""Evidence scoring."""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timezone

from .models import EvidenceItem, ScoredEvidence, SourceKind, SourceRun


SOURCE_WEIGHTS = {
    SourceKind.GITHUB: 0.95,
    SourceKind.DOCS: 0.92,
    SourceKind.SECURITY: 0.9,
    SourceKind.ARXIV: 0.84,
    SourceKind.PYPI: 0.78,
    SourceKind.NPM: 0.76,
    SourceKind.HACKER_NEWS: 0.72,
    SourceKind.REDDIT: 0.62,
    SourceKind.WEB: 0.55,
    SourceKind.FIXTURE: 0.5,
}

RISK_TAGS = {"risk", "security", "lock-in", "api-churn", "incident", "deprecation"}
POSITIVE_TAGS = {"release-cadence", "docs", "checkpointing", "guardrails", "tracing", "repository"}


def flatten_runs(runs: tuple[SourceRun, ...]) -> tuple[EvidenceItem, ...]:
    return tuple(item for run in runs for item in run.items)


def score_item(item: EvidenceItem, *, now: datetime | None = None, diversity_bonus: float = 0.0) -> ScoredEvidence:
    now = now or datetime.now(timezone.utc)
    age = item.age_days(now)
    recency = max(0.0, 1.0 - min(age, 90.0) / 90.0)
    engagement = min(1.0, math.log10(max(1.0, item.engagement) + 1) / 5.0)
    source_weight = SOURCE_WEIGHTS.get(item.source, 0.5)
    sentiment = (item.sentiment + 1.0) / 2.0
    risk_penalty = 0.08 if set(item.tags) & RISK_TAGS and item.sentiment < 0 else 0.0
    positive_bonus = 0.05 if set(item.tags) & POSITIVE_TAGS else 0.0

    score = (
        source_weight * 0.24
        + item.authority * 0.24
        + recency * 0.2
        + engagement * 0.16
        + sentiment * 0.08
        + diversity_bonus
        + positive_bonus
        - risk_penalty
    )
    score = round(max(0.0, min(1.0, score)), 4)

    reasons = [
        f"source={item.source.value}",
        f"authority={item.authority:.2f}",
        f"recency={recency:.2f}",
        f"engagement={engagement:.2f}",
    ]
    if positive_bonus:
        reasons.append("positive-operational-signal")
    if risk_penalty:
        reasons.append("risk-penalty")
    if diversity_bonus:
        reasons.append("source-diversity")
    return ScoredEvidence(item=item, score=score, reasons=tuple(reasons))


def score_evidence(runs: tuple[SourceRun, ...], *, now: datetime | None = None) -> tuple[ScoredEvidence, ...]:
    items = flatten_runs(runs)
    counts = Counter(item.source for item in items)
    scored = []
    for item in items:
        diversity_bonus = 0.04 if counts[item.source] <= 2 else 0.0
        scored.append(score_item(item, now=now, diversity_bonus=diversity_bonus))
    return tuple(sorted(scored, key=lambda entry: (-entry.score, entry.item.source.value, entry.item.title)))


def top_evidence(scored: tuple[ScoredEvidence, ...], limit: int = 8) -> tuple[ScoredEvidence, ...]:
    return scored[:limit]

