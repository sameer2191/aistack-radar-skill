"""Source collection orchestration."""

from __future__ import annotations

import os
from pathlib import Path

from ..models import SourceKind, SourceRun
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
    for source in sources:
        connector = LIVE_CONNECTORS.get(source)
        if connector is None:
            runs.append(SourceRun(source=SourceKind.WEB, warnings=(f"unknown source: {source}",)))
            continue
        runs.append(connector(topic, timeout=timeout))
    return tuple(runs)

