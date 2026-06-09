# AI Stack Radar Skill

[![CI](https://github.com/sameer2191/aistack-radar-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/sameer2191/aistack-radar-skill/actions/workflows/ci.yml)

**Agent skill and local research engine for AI, data, and developer-tool adoption briefs.**

AI Stack Radar helps an agent answer questions like "Should we trial LangGraph,
OpenAI Agents SDK, or CrewAI?" with sourced evidence instead of loose opinion.
It collects adoption signals, scores evidence, tracks source health, and emits
portable JSON, Markdown, and HTML briefs.

The repository has two runnable surfaces:

- `skills/aistack-radar/` is the installable skill. It includes its own
  self-contained runtime script and fixture so a copied skill directory can run.
- `src/aistack_radar/` is the package development surface with the same CLI
  behavior and unit tests.

The committed demo and test suite run with Python standard library only. Live
connectors are optional and degrade to source warnings when a public endpoint is
unavailable.

## Quickstart

From a repository checkout:

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

## Install As A Codex Skill

Install the skill folder from GitHub:

```bash
python3 /Users/sameer/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo sameer2191/aistack-radar-skill \
  --path skills/aistack-radar \
  --method git
```

Restart Codex after installation. Then ask:

```text
Use the aistack-radar skill to compare LangGraph, OpenAI Agents SDK, and CrewAI for production agent workflows.
```

If your host supports the Agent Skills CLI, the repo is also laid out for the
standard `skills/<name>/SKILL.md` convention.

## What It Does

- Parses tool, package, trend, and comparison topics.
- Loads deterministic fixture evidence for CI and offline review.
- Collects live signals from GitHub, Hacker News, Reddit, PyPI, npm, and arXiv
  using only standard-library HTTP calls.
- Scores evidence using recency, authority, engagement, source quality,
  sentiment, source diversity, and risk tags.
- Generates an adoption brief with recommendation, confidence, risk flags,
  citations, source warnings, and shareable reports.
- Keeps the installed skill runnable by shipping
  `skills/aistack-radar/scripts/aistack_radar.py` inside the skill directory.

## Use Cases

**Framework selection.** Compare agent frameworks, retrieval stacks, eval tools,
or observability platforms before starting a proof of concept.

```bash
python3 -m aistack_radar research "LangGraph vs OpenAI Agents SDK vs CrewAI" \
  --output runs/agent-frameworks \
  --emit html
```

**Package adoption review.** Pull package metadata, repository activity, and
developer discussion into a single review artifact.

```bash
python3 -m aistack_radar research "lancedb" \
  --source github \
  --source pypi \
  --source hackernews \
  --output runs/lancedb
```

**Offline regression demo.** Use the bundled fixture to verify formatting,
scoring, and artifact generation without network access.

```bash
python3 skills/aistack-radar/scripts/aistack_radar.py research \
  "LangGraph vs OpenAI Agents SDK" \
  --fixture skills/aistack-radar/fixtures/demo_signal.json \
  --output runs/skill-demo \
  --emit html
```

## Sources

| Source | Signal | Notes |
| --- | --- | --- |
| GitHub | repository freshness, stars, issue volume, descriptions | Public API, no token required for basic use |
| Hacker News | technical discussion and comments | Uses Algolia HN search |
| Reddit | practitioner sentiment and community pain points | Public JSON endpoint |
| PyPI | Python package release cadence and metadata | Useful for Python AI tooling |
| npm | JavaScript package release cadence and metadata | Useful for SDKs and front-end tooling |
| arXiv | recent papers and research references | Atom API |
| Fixture | deterministic normalized evidence | CI and offline demos |

Live collection is best effort. Public endpoints can rate-limit, change shape,
or return thin evidence. Source warnings are preserved in generated briefs.

## How It Works

1. The topic is normalized into a research query.
2. Fixture and live source connectors return normalized evidence records.
3. Evidence is scored with transparent heuristics: source weight, authority,
   recency, engagement, sentiment, source diversity, positive operational tags,
   and risk penalties.
4. The synthesizer derives `ADOPT`, `TRIAL`, `WATCH`, or `AVOID` from top
   evidence, risk flags, and evidence volume.
5. The report writer emits durable JSON, Markdown, and optional HTML artifacts.

See [docs/methodology.md](docs/methodology.md) for scoring details and
[docs/how-it-works.md](docs/how-it-works.md) for the runtime flow.

## Recommendation Contract

| Recommendation | Meaning |
| --- | --- |
| `ADOPT` | Strong evidence, sufficient volume, and low detected risk |
| `TRIAL` | Enough signal for a contained proof of concept |
| `WATCH` | Thin, mixed, or incomplete signal |
| `AVOID` | Material risk with weak adoption signal |

Scores are evidence-ordering heuristics, not truth claims. Treat the generated
brief as a review artifact that points to source material.

## Configuration

| Setting | Default | Purpose |
| --- | --- | --- |
| `AISTACK_RADAR_TIMEOUT_SECONDS` | `8` | Per-source live HTTP timeout |
| `--fixture` | unset | Load normalized evidence JSON |
| `--source` | default live set when no fixture is provided | Repeatable source selector |
| `--output` | `runs/aistack-radar` | Artifact directory |
| `--emit` | `md` | Use `html` for Markdown plus self-contained HTML |

See [CONFIGURATION.md](CONFIGURATION.md) for the full reference.

## Repository Layout

```text
skills/aistack-radar/              Installable skill definition and runtime
skills/aistack-radar/scripts/      Self-contained runtime for copied skill installs
skills/aistack-radar/fixtures/     Skill-local deterministic fixture
agents/openai.yaml                 Agent metadata
.claude-plugin/plugin.json         Plugin package metadata
.claude-plugin/marketplace.json    Marketplace metadata
.agents/plugins/marketplace.json   Agent plugin index metadata
src/aistack_radar/                 Package development engine
fixtures/demo_signal.json          Package-level deterministic evidence fixture
tests/                             unittest coverage
docs/                              Methodology, source, usage, and quality docs
.github/workflows/ci.yml           Tests plus fixture demos
```

## Design Boundary

AI Stack Radar is not a general web search engine and it is not a replacement
for architectural judgment. It is a focused technical signal collector for AI
stack decisions. The deterministic fixture path is the CI contract; live sources
are additive and may be rate-limited by their providers.

## Open Source

MIT license. No tracking. No analytics. Fixture mode runs offline. Live mode
uses public endpoints directly from your machine and records source health in
the generated artifact.
