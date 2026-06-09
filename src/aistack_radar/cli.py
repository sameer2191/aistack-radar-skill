"""Command-line interface for AI Stack Radar."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .connectors import collect_sources
from .planner import plan_topic, source_query
from .reporting import write_reports
from .synthesis import build_brief


DEFAULT_LIVE_SOURCES = ("github", "hackernews", "reddit", "arxiv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aistack-radar", description="Research AI stack adoption signals.")
    sub = parser.add_subparsers(dest="command")

    research = sub.add_parser("research", help="Collect evidence and write an adoption brief.")
    research.add_argument("topic", help="Tool, package, trend, or comparison topic.")
    research.add_argument("--fixture", help="Path to normalized evidence fixture JSON.")
    research.add_argument("--source", action="append", default=[], help="Optional live source: github, hackernews, reddit, pypi, npm, arxiv. Defaults to github, hackernews, reddit, and arxiv when no fixture is provided.")
    research.add_argument("--output", default="runs/aistack-radar", help="Output directory for report artifacts.")
    research.add_argument("--emit", choices=["md", "html"], default="md", help="Emit Markdown only or Markdown plus HTML.")
    research.add_argument("--timeout", type=float, default=None, help="Per-source live HTTP timeout in seconds.")
    research.add_argument("--print-json", action="store_true", help="Print the generated brief JSON to stdout.")

    return parser


def run_research(args: argparse.Namespace) -> int:
    plan = plan_topic(args.topic)
    query = source_query(plan)
    sources = tuple(args.source) or (() if args.fixture else DEFAULT_LIVE_SOURCES)
    runs = collect_sources(query, fixture=args.fixture, sources=sources, timeout=args.timeout)
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
