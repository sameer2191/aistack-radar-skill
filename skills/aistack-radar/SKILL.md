---
name: aistack-radar
version: "0.1.0"
description: Research AI, data, and developer-tool stacks; compare adoption signals; and produce sourced adoption briefs for technical decision makers.
argument-hint: 'aistack-radar LangGraph vs OpenAI Agents SDK | aistack-radar vector database options | aistack-radar eval platforms'
allowed-tools: Bash, Read, Write, WebSearch
homepage: https://github.com/sameer2191/aistack-radar-skill
repository: https://github.com/sameer2191/aistack-radar-skill
author: Sameeruddin Mir
license: MIT
user-invocable: true
metadata:
  tags:
    - ai
    - llmops
    - agent-frameworks
    - developer-tools
    - data-platforms
    - adoption-research
    - technical-due-diligence
  requires:
    env: []
    optionalEnv:
      - AISTACK_RADAR_TIMEOUT_SECONDS
    bins:
      - python3
    files:
      - scripts/aistack_radar.py
      - fixtures/demo_signal.json
---

# AI Stack Radar

Use this skill when the user asks for research, comparison, or adoption guidance on AI infrastructure, data platforms, developer tools, agent frameworks, model tooling, observability, orchestration, evaluation, retrieval, or related technical stacks.

Do not use this skill for general opinion pieces, unsourced trend summaries, or implementation work that does not require stack research.

## Workflow

1. Clarify the research question, target audience, decision horizon, and any required tools, vendors, or categories.
2. Decide whether to use fixtures or live collection:
   - Use fixtures for demos, tests, reproducible examples, offline runs, or when the user explicitly provides a fixture.
   - Use live collection when the user needs current market signals, recent releases, adoption movement, or source-backed recommendations.
3. Run the installed skill runtime to collect and synthesize the brief.
4. Inspect the generated artifacts before answering.
5. Cite artifact paths and source evidence. Avoid unsourced claims.
6. Present the decision-ready brief with clear caveats, confidence, and recommended next steps.

## Commands

When this skill is installed, set `SKILL_DIR` to the directory that contains this `SKILL.md`.

Default fixture-backed run:

```bash
SKILL_DIR="${SKILL_DIR:-$HOME/.codex/skills/aistack-radar}"
python3 "$SKILL_DIR/scripts/aistack_radar.py" research "LangGraph vs OpenAI Agents SDK" --fixture "$SKILL_DIR/fixtures/demo_signal.json" --output runs/demo --emit html
```

Suggested live run shape:

```bash
SKILL_DIR="${SKILL_DIR:-$HOME/.codex/skills/aistack-radar}"
python3 "$SKILL_DIR/scripts/aistack_radar.py" research "<research question>" --output runs/<slug> --emit html
```

If the CLI supports additional emit formats, prefer durable artifacts such as Markdown, JSON, and HTML so later agents can inspect the same evidence.

## Output Expectations

The agent response should include:

- The exact research question investigated.
- A concise recommendation or decision frame.
- Key findings grouped by adoption signal, technical fit, ecosystem maturity, risks, and watch items.
- Artifact paths for generated reports, raw signals, or rendered HTML.
- Source citations from the generated artifacts or collected evidence.
- Explicit caveats where evidence is incomplete, stale, fixture-based, or inconclusive.

Do not claim that a tool is winning, declining, production-ready, deprecated, secure, compliant, or broadly adopted unless the artifact evidence supports it.

## Output Contract

- Start with the recommendation and confidence from `brief.json`.
- Label fixture-backed runs as fixture-backed.
- For live runs, mention source warnings when any source degrades or times out.
- Cite `brief.md`, `brief.json`, and `brief.html` paths when they exist.
- Use inline source names from the evidence table rather than adding unsupported claims.
- If no evidence is collected, say that and suggest a fixture run or explicit live sources.

## Artifact Citation

After running the CLI, cite the relevant files directly, for example:

- `runs/demo/brief.html`
- `runs/demo/brief.md`
- `runs/demo/brief.json`

When summarizing evidence, name the artifact and the underlying source captured in that artifact. If an artifact is missing or incomplete, state that clearly and avoid filling gaps with assumptions.

## Fixture vs Live Collection

Use fixture mode when:

- The user asks for a demo, smoke test, or deterministic example.
- Network access is unavailable or not approved.
- The goal is to verify formatting, rendering, parsing, or agent behavior.

Use live collection when:

- The user asks for current or recent adoption signals.
- The answer depends on new releases, pricing, ecosystem changes, benchmarks, community movement, or vendor positioning.
- The brief will inform a real technical decision.

Fixture-backed results must be labeled as fixture-backed and should not be presented as current market research.

## Direct Repository Development

From a full repository checkout, developers can also run the package CLI:

```bash
python3 -m aistack_radar research "LangGraph vs OpenAI Agents SDK" --fixture fixtures/demo_signal.json --output runs/demo --emit html
python3 -m unittest discover -s tests
```

The installed skill runtime and the package CLI should produce the same artifact contract: `brief.json`, `brief.md`, and optionally `brief.html`.
