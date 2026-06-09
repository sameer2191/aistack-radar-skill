"""Fixture source connector."""

from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any

from ..models import EvidenceItem, SourceKind, SourceRun


def _kind(value: str) -> SourceKind:
    try:
        return SourceKind(value)
    except ValueError:
        return SourceKind.FIXTURE


def _item(raw: dict[str, Any]) -> EvidenceItem:
    return EvidenceItem(
        source=_kind(str(raw.get("source", "fixture"))),
        title=str(raw["title"]),
        url=str(raw.get("url", "")),
        summary=str(raw.get("summary", "")),
        published_at=str(raw.get("published_at", "")),
        author=str(raw.get("author", "")),
        engagement=float(raw.get("engagement", 0)),
        authority=float(raw.get("authority", 0.5)),
        sentiment=float(raw.get("sentiment", 0)),
        tags=tuple(str(tag) for tag in raw.get("tags", [])),
        metadata=dict(raw.get("metadata", {})),
    )


def load_fixture(path: str | Path) -> SourceRun:
    started = perf_counter()
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    items = tuple(_item(raw) for raw in payload.get("items", []))
    warnings = tuple(str(warning) for warning in payload.get("warnings", []))
    elapsed_ms = (perf_counter() - started) * 1000
    return SourceRun(source=SourceKind.FIXTURE, items=items, warnings=warnings, elapsed_ms=elapsed_ms)

