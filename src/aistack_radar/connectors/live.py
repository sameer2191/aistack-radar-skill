"""Optional live source connectors.

These functions avoid third-party dependencies and degrade to warnings when a
source is unavailable. The deterministic fixture path remains the CI contract.
"""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable

from ..models import EvidenceItem, SourceKind, SourceRun
from .http import FetchError, fetch_json, fetch_text, urlencode


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


def _run(kind: SourceKind, fetcher: Callable[[], tuple[EvidenceItem, ...]]) -> SourceRun:
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
        query = urlencode({"q": f"{topic} in:name,description", "sort": "stars", "order": "desc", "per_page": limit})
        payload = fetch_json(f"https://api.github.com/search/repositories?{query}", timeout)
        for repo in payload.get("items", [])[:limit]:
            item = github_item(repo)
            if item.url not in {existing.url for existing in items}:
                items.append(item)
        return tuple(items[:limit])

    return _run(SourceKind.GITHUB, fetch)


def hackernews(topic: str, timeout: float = 8.0, limit: int = 8) -> SourceRun:
    def fetch() -> tuple[EvidenceItem, ...]:
        query = urlencode({"query": topic, "tags": "story", "hitsPerPage": limit})
        payload = fetch_json(f"https://hn.algolia.com/api/v1/search?{query}", timeout)
        items = []
        for hit in payload.get("hits", [])[:limit]:
            created = str(hit.get("created_at", ""))
            points = float(hit.get("points", 0) or 0)
            comments = float(hit.get("num_comments", 0) or 0)
            items.append(
                EvidenceItem(
                    source=SourceKind.HACKER_NEWS,
                    title=str(hit.get("title") or hit.get("story_title") or "Hacker News item"),
                    url=str(hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
                    summary=f"{int(points)} points and {int(comments)} comments on Hacker News.",
                    published_at=created,
                    engagement=points + comments * 2,
                    authority=0.7,
                    sentiment=0.0,
                    tags=("hackernews", "discussion"),
                )
            )
        return tuple(items)

    return _run(SourceKind.HACKER_NEWS, fetch)


def reddit(topic: str, timeout: float = 8.0, limit: int = 8) -> SourceRun:
    def fetch() -> tuple[EvidenceItem, ...]:
        query = urlencode({"q": topic, "sort": "top", "t": "month", "limit": limit})
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
                    sentiment=0.0,
                    tags=("reddit", "discussion"),
                )
            )
        return tuple(items)

    return _run(SourceKind.REDDIT, fetch)


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

    return _run(SourceKind.PYPI, fetch)


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

    return _run(SourceKind.NPM, fetch)


def arxiv(topic: str, timeout: float = 8.0, limit: int = 5) -> SourceRun:
    def fetch() -> tuple[EvidenceItem, ...]:
        # Atom parsing via stdlib keeps this dependency-free.
        import urllib.parse
        import xml.etree.ElementTree as ET

        query = urllib.parse.urlencode({"search_query": f"all:{topic}", "start": 0, "max_results": limit, "sortBy": "submittedDate", "sortOrder": "descending"})
        xml = fetch_text(f"https://export.arxiv.org/api/query?{query}", timeout=timeout, accept="application/atom+xml")
        root = ET.fromstring(xml)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        items = []
        for entry in root.findall("a:entry", ns)[:limit]:
            title = " ".join((entry.findtext("a:title", default="", namespaces=ns) or "").split())
            summary = " ".join((entry.findtext("a:summary", default="", namespaces=ns) or "").split())[:400]
            published = entry.findtext("a:published", default="", namespaces=ns) or ""
            url = entry.findtext("a:id", default="", namespaces=ns) or ""
            items.append(
                EvidenceItem(
                    source=SourceKind.ARXIV,
                    title=title,
                    url=url,
                    summary=summary,
                    published_at=published,
                    engagement=10,
                    authority=0.78,
                    sentiment=0.0,
                    tags=("arxiv", "paper"),
                )
            )
        return tuple(items)

    return _run(SourceKind.ARXIV, fetch)
