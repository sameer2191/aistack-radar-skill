"""Core data models for AI Stack Radar."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SourceKind(str, Enum):
    FIXTURE = "fixture"
    GITHUB = "github"
    HACKER_NEWS = "hackernews"
    REDDIT = "reddit"
    PYPI = "pypi"
    NPM = "npm"
    ARXIV = "arxiv"
    WEB = "web"
    SECURITY = "security"
    DOCS = "docs"


class Recommendation(str, Enum):
    ADOPT = "adopt"
    TRIAL = "trial"
    WATCH = "watch"
    AVOID = "avoid"


@dataclass(frozen=True)
class EvidenceItem:
    """Normalized source evidence."""

    source: SourceKind
    title: str
    url: str
    summary: str
    published_at: str = ""
    author: str = ""
    engagement: float = 0.0
    authority: float = 0.5
    sentiment: float = 0.0
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def age_days(self, now: datetime | None = None) -> float:
        if not self.published_at:
            return 30.0
        now = now or datetime.now(timezone.utc)
        try:
            value = datetime.fromisoformat(self.published_at.replace("Z", "+00:00"))
        except ValueError:
            return 30.0
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return max(0.0, (now - value).total_seconds() / 86400)


@dataclass(frozen=True)
class SourceRun:
    source: SourceKind
    items: tuple[EvidenceItem, ...] = ()
    warnings: tuple[str, ...] = ()
    elapsed_ms: float = 0.0


@dataclass(frozen=True)
class TopicPlan:
    topic: str
    entities: tuple[str, ...]
    comparison: bool = False
    aliases: dict[str, tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class ScoredEvidence:
    item: EvidenceItem
    score: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RadarBrief:
    topic: str
    generated_at: str
    recommendation: Recommendation
    confidence: float
    summary: str
    key_findings: tuple[str, ...]
    risk_flags: tuple[str, ...]
    source_runs: tuple[SourceRun, ...]
    scored_items: tuple[ScoredEvidence, ...]
    adoption_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "generated_at": self.generated_at,
            "recommendation": self.recommendation.value,
            "confidence": self.confidence,
            "adoption_score": self.adoption_score,
            "summary": self.summary,
            "key_findings": list(self.key_findings),
            "risk_flags": list(self.risk_flags),
            "source_runs": [
                {
                    "source": run.source.value,
                    "warnings": list(run.warnings),
                    "elapsed_ms": run.elapsed_ms,
                    "count": len(run.items),
                }
                for run in self.source_runs
            ],
            "evidence": [
                {
                    "source": scored.item.source.value,
                    "title": scored.item.title,
                    "url": scored.item.url,
                    "summary": scored.item.summary,
                    "published_at": scored.item.published_at,
                    "engagement": scored.item.engagement,
                    "authority": scored.item.authority,
                    "sentiment": scored.item.sentiment,
                    "tags": list(scored.item.tags),
                    "score": scored.score,
                    "reasons": list(scored.reasons),
                }
                for scored in self.scored_items
            ],
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

