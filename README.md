# AI Stack Radar Skill

AI Stack Radar is an installable agent skill and local research engine for AI,
LLMOps, data, and developer-tool adoption decisions. It collects technical
signals, scores evidence, and emits grounded adoption briefs with source health,
risks, and a clear `ADOPT`, `TRIAL`, `WATCH`, or `AVOID` recommendation.

The committed demo and tests run with Python 3 standard library only. Live
connectors are optional and degrade to source warnings when a source is
unavailable.

## Quickstart

```bash
python3 -m unittest discover -s tests
python3 -m aistack_radar research "LangGraph vs OpenAI Agents SDK" \
  --fixture fixtures/demo_signal.json \
  --output runs/demo \
  --emit html
```

The demo writes:

- `runs/demo/brief.json`
- `runs/demo/brief.md`
- `runs/demo/brief.html`

## What It Does

- Parses tool, package, trend, and comparison topics.
- Loads deterministic fixture evidence for CI and offline review.
- Optionally collects live signals from GitHub, Hacker News, Reddit, PyPI, npm,
  and arXiv using only standard-library HTTP calls.
- Scores evidence using recency, authority, engagement, source quality,
  sentiment, and risk tags.
- Generates a deterministic adoption brief with findings, risk flags, citations,
  source warnings, and shareable reports.
- Ships an agent skill at `skills/aistack-radar/SKILL.md` that tells coding
  agents how to run the research flow and use the artifacts.

## CLI

Fixture run:

```bash
python3 -m aistack_radar research "LangGraph vs OpenAI Agents SDK" \
  --fixture fixtures/demo_signal.json \
  --output runs/demo \
  --emit html
```

Live-source run:

```bash
python3 -m aistack_radar research "LangGraph" \
  --source github \
  --source hackernews \
  --source pypi \
  --output runs/live
```

## Repository Layout

```text
skills/aistack-radar/          Agent skill definition
agents/openai.yaml             Skill UI metadata
.claude-plugin/plugin.json     Plugin package metadata
src/aistack_radar/             Research engine
fixtures/demo_signal.json      Deterministic evidence fixture
tests/                         unittest coverage
docs/                          Source, methodology, and usage docs
.github/workflows/ci.yml       Tests plus fixture demo
```

## Design Boundary

This project is not a general web search engine. It is a focused technical
signal collector for AI stack decisions. The deterministic fixture path is the
contract for CI; live sources are additive and may be rate-limited by their
providers.
