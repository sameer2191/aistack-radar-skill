# Methodology

AI Stack Radar turns heterogeneous technical signals into a deterministic
adoption brief. The engine is intentionally transparent: every score is derived
from fields stored on normalized evidence records.

## Planning

The topic planner detects comparison prompts such as:

- `LangGraph vs OpenAI Agents SDK`
- `CrewAI versus AutoGen`
- `OpenAI Agents SDK, LangGraph, CrewAI`
- `alternatives to LangGraph`

Comparison topics are treated as one research surface with entity labels that
can be used by downstream synthesis.

## Evidence Score

Each evidence item receives a score from `0.0` to `1.0` based on:

- source weight
- declared authority
- recency over a 90-day window
- log-scaled engagement
- sentiment
- source diversity bonus
- operational-positive tags such as `docs`, `tracing`, and `checkpointing`
- risk penalty for negative security or risk evidence

The score is not a truth claim. It is an ordering heuristic for evidence review.

## Recommendation

The brief recommendation is derived from the mean score of top evidence,
evidence count, and risk flags:

- `ADOPT`: strong score, sufficient evidence, and low risk
- `TRIAL`: enough signal for a contained proof of concept
- `WATCH`: thin or mixed signal
- `AVOID`: material risks with weak adoption signal

## Confidence

Confidence increases with source diversity and evidence count. Source warnings
reduce reader confidence indirectly by appearing in the risk section.

## Limitations

Fixture mode is deterministic and useful for validation. Live mode is best
effort: public endpoints can rate-limit, change shape, or return thin results.
Reports therefore include source health lines so readers can distinguish signal
from source availability.

