# Search Quality Evaluation

AI Stack Radar uses deterministic scoring so users can inspect why evidence was
ranked. The quality target is not "perfect truth"; it is a reliable review
artifact that keeps source health and caveats visible.

## What Good Output Looks Like

- The brief includes enough source diversity for the decision context.
- The top findings point to concrete source URLs.
- Risk flags surface security, lock-in, API churn, or operational concerns.
- Source warnings are visible rather than hidden.
- Fixture-backed output is labeled as deterministic demo evidence.

## Fixture Regression

The bundled fixture exercises:

- GitHub repository signals
- Hacker News discussion
- Reddit practitioner sentiment
- PyPI release metadata
- documentation evidence
- security/risk evidence

Expected demo behavior:

- recommendation: `TRIAL`
- evidence items: at least 8
- artifacts: `brief.json`, `brief.md`, `brief.html`

Run:

```bash
python3 -m unittest discover -s tests
python3 -m aistack_radar research "LangGraph vs OpenAI Agents SDK" --fixture fixtures/demo_signal.json --output runs/demo --emit html
```

## Live Source Evaluation

Live mode is intentionally best effort. A degraded source should produce a
warning, not crash the run. For example:

```bash
python3 -m aistack_radar research "LangGraph" --source github --source hackernews --output runs/live
```

Review:

- source health section in `brief.md`
- `source_runs` array in `brief.json`
- whether top findings match the requested topic
- whether weak or thin evidence is reflected in confidence

## Known Limits

- Engagement does not equal correctness.
- Public endpoints can rate-limit or change response shape.
- Package metadata can be stale or sparse.
- Heuristic sentiment is source-provided or fixture-provided; it is not an LLM
  judgment.
- A high score should trigger deeper review, not replace it.
