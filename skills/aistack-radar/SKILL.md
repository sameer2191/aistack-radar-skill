---
name: aistack-radar
description: Research AI, data, and developer-tool stacks; compare adoption signals; and produce sourced adoption briefs for technical decision makers.
---

# AI Stack Radar

Use this skill when the user asks for research, comparison, or adoption guidance on AI infrastructure, data platforms, developer tools, agent frameworks, model tooling, observability, orchestration, evaluation, retrieval, or related technical stacks.

Do not use this skill for general opinion pieces, unsourced trend summaries, or implementation work that does not require stack research.

## Workflow

1. Clarify the research question, target audience, decision horizon, and any required tools, vendors, or categories.
2. Decide whether to use fixtures or live collection:
   - Use fixtures for demos, tests, reproducible examples, offline runs, or when the user explicitly provides a fixture.
   - Use live collection when the user needs current market signals, recent releases, adoption movement, or source-backed recommendations.
3. Run the CLI to collect and synthesize the brief.
4. Inspect the generated artifacts before answering.
5. Cite artifact paths and source evidence. Avoid unsourced claims.
6. Present the decision-ready brief with clear caveats, confidence, and recommended next steps.

## Commands

Default fixture-backed run:

```bash
python -m aistack_radar research "LangGraph vs OpenAI Agents SDK" --fixture fixtures/demo_signal.json --output runs/demo --emit html
```

Suggested live run shape:

```bash
python -m aistack_radar research "<research question>" --output runs/<slug> --emit html
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
