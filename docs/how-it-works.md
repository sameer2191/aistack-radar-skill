# How It Works

AI Stack Radar runs a short, inspectable pipeline.

## 1. Topic Intake

The runtime accepts a topic such as:

- `LangGraph vs OpenAI Agents SDK`
- `vector database options for agent memory`
- `eval platforms for production LLM applications`

Comparison topics are treated as one research surface so evidence can be scored
against the same decision context.

## 2. Source Collection

The collector loads a fixture and/or queries live public sources. Every source
returns a `SourceRun` with:

- normalized evidence items
- elapsed time
- warnings when collection degrades

Unknown sources become warnings rather than hard failures.

## 3. Normalization

Each source item becomes an evidence record with a common shape:

- source
- title
- URL
- summary
- publication time
- engagement
- authority
- sentiment
- tags
- metadata

This lets the scoring and report layers stay source-agnostic.

## 4. Scoring

Evidence score is deterministic. Inputs include:

- source weight
- authority
- 90-day recency
- log-scaled engagement
- sentiment
- source diversity
- operational-positive tags
- risk penalties

The score orders evidence for review. It is not a claim that one source is
objectively correct.

## 5. Synthesis

The synthesizer computes:

- adoption score
- confidence
- recommendation
- key findings
- risk flags
- source health

Recommendations map to `ADOPT`, `TRIAL`, `WATCH`, or `AVOID`.

## 6. Reporting

The report layer writes:

- `brief.json` for structured consumers
- `brief.md` for readable review
- `brief.html` for sharing without a server

HTML is self-contained and uses no JavaScript.
