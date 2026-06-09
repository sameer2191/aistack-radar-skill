# Concepts

## Skill

The installable agent-facing unit under `skills/aistack-radar/`. A host reads
`SKILL.md`, follows its workflow, and runs the bundled runtime script.

## Runtime

The self-contained Python script at
`skills/aistack-radar/scripts/aistack_radar.py`. It exists so copied skill
installs can run without an editable Python package.

## Package CLI

The development CLI exposed by `python3 -m aistack_radar` and the console
script `aistack-radar`. It shares the same artifact contract as the installed
skill runtime.

## Evidence Item

A normalized record from a fixture or live source. Evidence items carry source,
title, URL, summary, publication time, engagement, authority, sentiment, tags,
and metadata.

## Source Run

The result of querying one source. Source runs preserve item count, elapsed
time, and warnings so briefs can separate missing evidence from negative signal.

## Adoption Score

A deterministic heuristic used to order evidence and derive the recommendation.
It combines source weight, authority, recency, engagement, sentiment, source
diversity, operational-positive tags, and risk penalties.

## Recommendation

One of `ADOPT`, `TRIAL`, `WATCH`, or `AVOID`. Recommendations are review
labels, not truth claims.

## Fixture Mode

Offline deterministic mode backed by `fixtures/demo_signal.json` or the
skill-local copy under `skills/aistack-radar/fixtures/`.

## Live Mode

Best-effort public-source collection. Live mode is useful for current research,
but public endpoints can rate-limit or return thin evidence.
