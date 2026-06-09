#!/usr/bin/env python3
"""Self-contained AI Stack Radar runtime for installed skill copies.

This file intentionally avoids third-party dependencies so a copied
`skills/aistack-radar/` directory can run without the repository package.
The package CLI in `src/aistack_radar/` remains the development entrypoint.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Callable


VERSION = "0.1.0"
DEFAULT_LIVE_SOURCES = ("github", "hackernews", "pypi")
COMPARISON_SPLIT_RE = re.compile(r"\s+(?:vs\.?|versus|against)\s+|,\s*|\s+\|\s+", re.IGNORECASE)
PYTHON_PACKAGE_ALIASES = {
    "langgraph": "langgraph",
    "openai agents sdk": "openai-agents",
    "openai agent sdk": "openai-agents",
    "openai agents": "openai-agents",
    "crewai": "crewai",
}
GITHUB_REPO_ALIASES = {
    "langgraph": "langchain-ai/langgraph",
    "openai agents sdk": "openai/openai-agents-python",
    "openai agent sdk": "openai/openai-agents-python",
    "openai agents": "openai/openai-agents-python",
    "crewai": "crewAIInc/crewAI",
}


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


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def source_kind(value: str) -> SourceKind:
    try:
        return SourceKind(value)
    except ValueError:
        return SourceKind.WEB


def expand_queries(topic: str) -> tuple[str, ...]:
    normalized = " ".join(topic.strip().split())
    if not normalized:
        raise ValueError("topic must not be empty")
    entities = tuple(part.strip(" \"'") for part in COMPARISON_SPLIT_RE.split(normalized) if part.strip(" \"'"))
    if len(entities) > 1:
        return entities
    return (normalized,)


def package_name(topic: str) -> str:
    normalized = " ".join(topic.lower().strip().split())
    if normalized in PYTHON_PACKAGE_ALIASES:
        return PYTHON_PACKAGE_ALIASES[normalized]
    if "openai" in normalized and "agent" in normalized:
        return "openai-agents"
    return topic.strip().split()[0].strip(",;").lower()


def github_repo_alias(topic: str) -> str | None:
    normalized = " ".join(topic.lower().strip().split())
    if normalized in GITHUB_REPO_ALIASES:
        return GITHUB_REPO_ALIASES[normalized]
    if "openai" in normalized and "agent" in normalized:
        return "openai/openai-agents-python"
    return None


def github_item(repo: dict[str, Any]) -> EvidenceItem:
    stars = float(repo.get("stargazers_count", 0) or 0)
    return EvidenceItem(
        source=SourceKind.GITHUB,
        title=str(repo.get("full_name", "GitHub repository")),
        url=str(repo.get("html_url", "")),
        summary=str(repo.get("description") or "No repository description."),
        published_at=str(repo.get("pushed_at", "")),
        engagement=stars,
        authority=min(1.0, 0.35 + stars / 50000),
        sentiment=0.2,
        tags=("github", "repository"),
        metadata={"stars": stars, "open_issues": repo.get("open_issues_count", 0)},
    )


def load_fixture(path: str | Path) -> SourceRun:
    started = perf_counter()
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    items = []
    for raw in payload.get("items", []):
        items.append(
            EvidenceItem(
                source=source_kind(str(raw.get("source", "fixture"))),
                title=str(raw.get("title", "")),
                url=str(raw.get("url", "")),
                summary=str(raw.get("summary", "")),
                published_at=str(raw.get("published_at", "")),
                author=str(raw.get("author", "")),
                engagement=float(raw.get("engagement", 0) or 0),
                authority=float(raw.get("authority", 0.5) or 0.5),
                sentiment=float(raw.get("sentiment", 0) or 0),
                tags=tuple(str(tag) for tag in raw.get("tags", [])),
                metadata=dict(raw.get("metadata", {})),
            )
        )
    return SourceRun(source=SourceKind.FIXTURE, items=tuple(items), elapsed_ms=(perf_counter() - started) * 1000)


def user_agent() -> str:
    return os.environ.get("AISTACK_RADAR_USER_AGENT", f"aistack-radar/{VERSION}")


def fetch_text_urllib(url: str, timeout: float, accept: str) -> str:
    request = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": user_agent()})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def fetch_text_curl(url: str, timeout: float, accept: str) -> str:
    curl = shutil.which("curl")
    if not curl:
        raise RuntimeError("urllib failed and curl is not available")
    completed = subprocess.run(
        [
            curl,
            "-fsSL",
            "--max-time",
            str(max(1.0, timeout)),
            "-A",
            user_agent(),
            "-H",
            f"Accept: {accept}",
            url,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"curl exited with status {completed.returncode}")
    return completed.stdout


def fetch_text(url: str, timeout: float, accept: str = "*/*") -> str:
    try:
        return fetch_text_urllib(url, timeout, accept)
    except Exception as urllib_exc:  # pragma: no cover - network dependent
        try:
            return fetch_text_curl(url, timeout, accept)
        except Exception as curl_exc:
            raise RuntimeError(f"urllib failed: {urllib_exc}; curl failed: {curl_exc}") from curl_exc


def fetch_json(url: str, timeout: float) -> dict[str, Any]:
    return json.loads(fetch_text(url, timeout, accept="application/json"))


def run_source(kind: SourceKind, fetcher: Callable[[], tuple[EvidenceItem, ...]]) -> SourceRun:
    started = perf_counter()
    try:
        items = fetcher()
        warnings: tuple[str, ...] = ()
    except Exception as exc:  # pragma: no cover - network dependent
        items = ()
        warnings = (f"{kind.value} unavailable: {exc}",)
    return SourceRun(source=kind, items=items, warnings=warnings, elapsed_ms=(perf_counter() - started) * 1000)


def github(topic: str, timeout: float = 8.0, limit: int = 8) -> SourceRun:
    def fetch() -> tuple[EvidenceItem, ...]:
        items = []
        alias = github_repo_alias(topic)
        if alias:
            items.append(github_item(fetch_json(f"https://api.github.com/repos/{alias}", timeout)))
        query = urllib.parse.urlencode({"q": f"{topic} in:name,description", "sort": "stars", "order": "desc", "per_page": limit})
        payload = fetch_json(f"https://api.github.com/search/repositories?{query}", timeout)
        for repo in payload.get("items", [])[:limit]:
            item = github_item(repo)
            if item.url not in {existing.url for existing in items}:
                items.append(item)
        return tuple(items[:limit])

    return run_source(SourceKind.GITHUB, fetch)


def hackernews(topic: str, timeout: float = 8.0, limit: int = 8) -> SourceRun:
    def fetch() -> tuple[EvidenceItem, ...]:
        query = urllib.parse.urlencode({"query": topic, "tags": "story", "hitsPerPage": limit})
        payload = fetch_json(f"https://hn.algolia.com/api/v1/search?{query}", timeout)
        items = []
        for hit in payload.get("hits", [])[:limit]:
            points = float(hit.get("points", 0) or 0)
            comments = float(hit.get("num_comments", 0) or 0)
            items.append(
                EvidenceItem(
                    source=SourceKind.HACKER_NEWS,
                    title=str(hit.get("title") or hit.get("story_title") or "Hacker News item"),
                    url=str(hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
                    summary=f"{int(points)} points and {int(comments)} comments on Hacker News.",
                    published_at=str(hit.get("created_at", "")),
                    engagement=points + comments * 2,
                    authority=0.7,
                    tags=("hackernews", "discussion"),
                )
            )
        return tuple(items)

    return run_source(SourceKind.HACKER_NEWS, fetch)


def reddit(topic: str, timeout: float = 8.0, limit: int = 8) -> SourceRun:
    def fetch() -> tuple[EvidenceItem, ...]:
        query = urllib.parse.urlencode({"q": topic, "sort": "top", "t": "month", "limit": limit})
        payload = fetch_json(f"https://www.reddit.com/search.json?{query}", timeout)
        items = []
        for child in payload.get("data", {}).get("children", [])[:limit]:
            data = child.get("data", {})
            created = datetime.fromtimestamp(float(data.get("created_utc", 0)), timezone.utc).isoformat().replace("+00:00", "Z")
            score = float(data.get("score", 0) or 0)
            comments = float(data.get("num_comments", 0) or 0)
            permalink = data.get("permalink", "")
            items.append(
                EvidenceItem(
                    source=SourceKind.REDDIT,
                    title=str(data.get("title", "Reddit discussion")),
                    url=f"https://www.reddit.com{permalink}",
                    summary=str(data.get("selftext", ""))[:300] or f"{int(score)} upvotes and {int(comments)} comments.",
                    published_at=created,
                    engagement=score + comments * 2,
                    authority=0.55,
                    tags=("reddit", "discussion"),
                )
            )
        return tuple(items)

    return run_source(SourceKind.REDDIT, fetch)


def pypi(topic: str, timeout: float = 8.0) -> SourceRun:
    package = package_name(topic)

    def fetch() -> tuple[EvidenceItem, ...]:
        payload = fetch_json(f"https://pypi.org/pypi/{package}/json", timeout)
        info: dict[str, Any] = payload.get("info", {})
        releases = payload.get("releases", {})
        latest = str(info.get("version", ""))
        urls = releases.get(latest, [])
        uploaded = str(urls[-1].get("upload_time_iso_8601", "")) if urls else ""
        return (
            EvidenceItem(
                source=SourceKind.PYPI,
                title=f"PyPI package {info.get('name', package)} {latest}",
                url=str(info.get("package_url", f"https://pypi.org/project/{package}/")),
                summary=str(info.get("summary") or "Python package metadata."),
                published_at=uploaded,
                engagement=float(len(releases)),
                authority=0.65,
                sentiment=0.1,
                tags=("pypi", "package"),
                metadata={"version": latest, "release_count": len(releases)},
            ),
        )

    return run_source(SourceKind.PYPI, fetch)


def npm(topic: str, timeout: float = 8.0) -> SourceRun:
    package = package_name(topic)

    def fetch() -> tuple[EvidenceItem, ...]:
        payload = fetch_json(f"https://registry.npmjs.org/{package}", timeout)
        latest = payload.get("dist-tags", {}).get("latest", "")
        version = payload.get("versions", {}).get(latest, {})
        modified = payload.get("time", {}).get("modified", "")
        return (
            EvidenceItem(
                source=SourceKind.NPM,
                title=f"npm package {payload.get('name', package)} {latest}",
                url=f"https://www.npmjs.com/package/{package}",
                summary=str(version.get("description") or payload.get("description") or "npm package metadata."),
                published_at=str(modified),
                engagement=float(len(payload.get("versions", {}))),
                authority=0.62,
                sentiment=0.1,
                tags=("npm", "package"),
                metadata={"version": latest, "release_count": len(payload.get("versions", {}))},
            ),
        )

    return run_source(SourceKind.NPM, fetch)


def arxiv(topic: str, timeout: float = 8.0, limit: int = 5) -> SourceRun:
    def fetch() -> tuple[EvidenceItem, ...]:
        query = urllib.parse.urlencode({"search_query": f"all:{topic}", "start": 0, "max_results": limit, "sortBy": "submittedDate", "sortOrder": "descending"})
        xml = fetch_text(f"https://export.arxiv.org/api/query?{query}", timeout=timeout, accept="application/atom+xml")
        root = ET.fromstring(xml)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        items = []
        for entry in root.findall("a:entry", ns)[:limit]:
            title = " ".join((entry.findtext("a:title", default="", namespaces=ns) or "").split())
            summary = " ".join((entry.findtext("a:summary", default="", namespaces=ns) or "").split())[:400]
            items.append(
                EvidenceItem(
                    source=SourceKind.ARXIV,
                    title=title,
                    url=entry.findtext("a:id", default="", namespaces=ns) or "",
                    summary=summary,
                    published_at=entry.findtext("a:published", default="", namespaces=ns) or "",
                    engagement=10,
                    authority=0.78,
                    tags=("arxiv", "paper"),
                )
            )
        return tuple(items)

    return run_source(SourceKind.ARXIV, fetch)


LIVE_CONNECTORS: dict[str, Callable[[str, float], SourceRun]] = {
    "github": github,
    "hackernews": hackernews,
    "reddit": reddit,
    "pypi": pypi,
    "npm": npm,
    "arxiv": arxiv,
}


def collect_sources(topic: str, *, fixture: str | Path | None = None, sources: tuple[str, ...] = (), timeout: float | None = None) -> tuple[SourceRun, ...]:
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
        source_runs = tuple(connector(query, timeout=timeout) for query in queries)
        seen: set[str] = set()
        items: list[EvidenceItem] = []
        warnings: list[str] = []
        elapsed_ms = 0.0
        source_kind_value = source_runs[0].source if source_runs else SourceKind.WEB
        for source_run in source_runs:
            elapsed_ms += source_run.elapsed_ms
            warnings.extend(source_run.warnings)
            for item in source_run.items:
                key = item.url or f"{item.source.value}:{item.title}"
                if key in seen:
                    continue
                seen.add(key)
                items.append(item)
        runs.append(SourceRun(source=source_kind_value, items=tuple(items), warnings=tuple(warnings), elapsed_ms=elapsed_ms))
    return tuple(runs)


def score_item(item: EvidenceItem, *, now: datetime | None = None, diversity_bonus: float = 0.0) -> ScoredEvidence:
    now = now or datetime.now(timezone.utc)
    recency = max(0.0, 1.0 - min(item.age_days(now), 90.0) / 90.0)
    engagement = min(1.0, math.log10(max(1.0, item.engagement) + 1) / 5.0)
    sentiment = (item.sentiment + 1.0) / 2.0
    risk_penalty = 0.08 if set(item.tags) & RISK_TAGS and item.sentiment < 0 else 0.0
    positive_bonus = 0.05 if set(item.tags) & POSITIVE_TAGS else 0.0
    score = (
        SOURCE_WEIGHTS.get(item.source, 0.5) * 0.24
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
    items = tuple(item for run in runs for item in run.items)
    counts = Counter(item.source for item in items)
    scored = [score_item(item, now=now, diversity_bonus=0.04 if counts[item.source] <= 2 else 0.0) for item in items]
    return tuple(sorted(scored, key=lambda entry: (-entry.score, entry.item.source.value, entry.item.title)))


def recommendation(adoption_score: float, risk_count: int, evidence_count: int) -> Recommendation:
    if evidence_count < 3:
        return Recommendation.WATCH
    if risk_count >= 3 and adoption_score < 0.7:
        return Recommendation.AVOID
    if adoption_score >= 0.78 and risk_count <= 1:
        return Recommendation.ADOPT
    if adoption_score >= 0.62:
        return Recommendation.TRIAL
    return Recommendation.WATCH


def build_brief(topic: str, source_runs: tuple[SourceRun, ...]) -> RadarBrief:
    scored = score_evidence(source_runs)
    leaders = scored[:8]
    risks = []
    for scored_item in scored:
        tags = set(scored_item.item.tags)
        if {"security", "risk"} & tags or "api-churn" in tags or "lock-in" in tags:
            risks.append(f"{scored_item.item.title}: {scored_item.item.summary}")
    risk_flags = tuple(risks[:5])
    if leaders:
        adoption_score = round(mean(item.score for item in leaders), 4)
        confidence = round(min(0.98, 0.38 + len(leaders) * 0.05 + len({item.item.source for item in leaders}) * 0.06), 3)
    else:
        adoption_score = 0.0
        confidence = 0.1
    rec = recommendation(adoption_score, len(risk_flags), len(scored))
    source_count = len({entry.item.source for entry in scored})
    summary = f"{topic} has {len(scored)} normalized evidence items across {source_count} source types. The current deterministic score is {adoption_score:.2f}, producing a {rec.value.upper()} recommendation."
    findings = tuple(
        f"{entry.item.title} [{entry.item.source.value}, score {entry.score:.2f}] - {entry.item.summary}"
        for entry in leaders[:6]
    ) or ("No evidence was collected. Re-run with a fixture or live sources.",)
    warnings = [warning for run in source_runs for warning in run.warnings]
    if warnings:
        risk_flags = tuple(list(risk_flags) + [f"Source warning: {warning}" for warning in warnings[:3]])
    return RadarBrief(
        topic=topic,
        generated_at=utc_now_iso(),
        recommendation=rec,
        confidence=confidence,
        summary=summary,
        key_findings=findings,
        risk_flags=risk_flags,
        source_runs=source_runs,
        scored_items=scored,
        adoption_score=adoption_score,
    )


def markdown(brief: RadarBrief) -> str:
    lines = [
        f"# AI Stack Radar: {brief.topic}",
        "",
        f"Generated: `{brief.generated_at}`",
        f"Recommendation: **{brief.recommendation.value.upper()}**",
        f"Confidence: `{brief.confidence:.2f}`",
        f"Adoption score: `{brief.adoption_score:.2f}`",
        "",
        "## Summary",
        "",
        brief.summary,
        "",
        "## Key Findings",
        "",
    ]
    lines.extend(f"- {finding}" for finding in brief.key_findings)
    lines.extend(["", "## Risks And Caveats", ""])
    lines.extend(f"- {risk}" for risk in brief.risk_flags or ("No material risk flags were detected in the collected evidence.",))
    lines.extend(["", "## Evidence", ""])
    for scored in brief.scored_items[:12]:
        lines.append(f"- [{scored.item.title}]({scored.item.url}) - `{scored.item.source.value}` score `{scored.score:.2f}`")
    lines.extend(["", "## Source Health", ""])
    for run in brief.source_runs:
        warning_text = "; ".join(run.warnings) if run.warnings else "ok"
        lines.append(f"- `{run.source.value}`: {len(run.items)} items, {run.elapsed_ms:.1f} ms, {warning_text}")
    lines.append("")
    return "\n".join(lines)


def write_reports(brief: RadarBrief, output_dir: str | Path, *, emit_html: bool = False) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "json": output_path / "brief.json",
        "markdown": output_path / "brief.md",
    }
    artifacts["json"].write_text(json.dumps(brief.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    body = markdown(brief)
    artifacts["markdown"].write_text(body, encoding="utf-8")
    if emit_html:
        content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Stack Radar - {html.escape(brief.topic)}</title>
  <style>
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0f172a; color: #e5e7eb; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 48px 22px; }}
    pre {{ white-space: pre-wrap; line-height: 1.55; background: #111827; border: 1px solid #334155; border-radius: 8px; padding: 24px; }}
    .badge {{ display: inline-block; padding: 6px 10px; border: 1px solid #38bdf8; color: #bae6fd; border-radius: 999px; margin-bottom: 18px; }}
  </style>
</head>
<body>
<main>
  <div class="badge">{html.escape(brief.recommendation.value.upper())} - confidence {brief.confidence:.2f}</div>
  <pre>{html.escape(body)}</pre>
</main>
</body>
</html>
"""
        artifacts["html"] = output_path / "brief.html"
        artifacts["html"].write_text(content, encoding="utf-8")
    return artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aistack-radar", description="Research AI stack adoption signals.")
    sub = parser.add_subparsers(dest="command")
    research = sub.add_parser("research", help="Collect evidence and write an adoption brief.")
    research.add_argument("topic", help="Tool, package, trend, or comparison topic.")
    research.add_argument("--fixture", help="Path to normalized evidence fixture JSON.")
    research.add_argument("--source", action="append", default=[], help="Optional live source: github, hackernews, reddit, pypi, npm, arxiv. Defaults to github, hackernews, and pypi when no fixture is provided.")
    research.add_argument("--output", default="runs/aistack-radar", help="Output directory for report artifacts.")
    research.add_argument("--emit", choices=["md", "html"], default="md", help="Emit Markdown only or Markdown plus HTML.")
    research.add_argument("--timeout", type=float, default=None, help="Per-source live HTTP timeout in seconds.")
    research.add_argument("--print-json", action="store_true", help="Print the generated brief JSON to stdout.")
    return parser


def run_research(args: argparse.Namespace) -> int:
    sources = tuple(args.source) or (() if args.fixture else DEFAULT_LIVE_SOURCES)
    runs = collect_sources(args.topic, fixture=args.fixture, sources=sources, timeout=args.timeout)
    brief = build_brief(args.topic, runs)
    artifacts = write_reports(brief, args.output, emit_html=args.emit == "html")
    print(f"AI Stack Radar complete: {brief.recommendation.value.upper()} score={brief.adoption_score:.2f} confidence={brief.confidence:.2f}")
    for name, path in artifacts.items():
        print(f"{name}: {path}")
    if args.print_json:
        print(json.dumps(brief.to_dict(), indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "research":
        return run_research(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
