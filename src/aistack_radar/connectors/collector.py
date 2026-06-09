"""Source collection orchestration."""

from __future__ import annotations

import os
from pathlib import Path

from ..models import EvidenceItem, SourceKind, SourceRun
from ..planner import plan_topic
from .fixture import load_fixture
from . import live


LIVE_CONNECTORS = {
    "github": live.github,
    "hackernews": live.hackernews,
    "reddit": live.reddit,
    "pypi": live.pypi,
    "npm": live.npm,
    "arxiv": live.arxiv,
}


def expand_queries(topic: str) -> tuple[str, ...]:
    plan = plan_topic(topic)
    if plan.comparison:
        return tuple(entity for entity in plan.entities if entity)
    return (plan.topic,)


def merge_source_runs(runs: tuple[SourceRun, ...]) -> SourceRun:
    if not runs:
        return SourceRun(source=SourceKind.WEB)
    seen: set[str] = set()
    items: list[EvidenceItem] = []
    warnings: list[str] = []
    elapsed_ms = 0.0
    source = runs[0].source
    for run in runs:
        elapsed_ms += run.elapsed_ms
        warnings.extend(run.warnings)
        for item in run.items:
            key = item.url or f"{item.source.value}:{item.title}"
            if key in seen:
                continue
            seen.add(key)
            items.append(item)
    return SourceRun(source=source, items=tuple(items), warnings=tuple(warnings), elapsed_ms=elapsed_ms)


def collect_sources(
    topic: str,
    *,
    fixture: str | Path | None = None,
    sources: tuple[str, ...] = (),
    timeout: float | None = None,
) -> tuple[SourceRun, ...]:
    """Collect evidence from fixture and optional live sources."""

    runs: list[SourceRun] = []
    if fixture:
        runs.append(load_fixture(fixture))

    timeout = timeout if timeout is not None else float(os.environ.get("AISTACK_RADAR_TIMEOUT_SECONDS", "8"))
    queries = expand_queries(topic)
    for source in sources:
        connector = LIVE_CONNECTORS.get(source)
        if connector is None:
            runs.append(SourceRun(source=SourceKind.WEB, warnings=(f"unknown source: {source}",)))
            continue
        runs.append(merge_source_runs(tuple(connector(query, timeout=timeout) for query in queries)))
    return tuple(runs)
