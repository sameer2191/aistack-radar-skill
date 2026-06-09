"""Deterministic brief synthesis."""

from __future__ import annotations

from statistics import mean

from .models import RadarBrief, Recommendation, SourceRun, utc_now_iso
from .planner import plan_topic
from .scoring import score_evidence, top_evidence


def _recommendation(adoption_score: float, risk_count: int, evidence_count: int) -> Recommendation:
    if evidence_count < 3:
        return Recommendation.WATCH
    if risk_count >= 3 and adoption_score < 0.7:
        return Recommendation.AVOID
    if adoption_score >= 0.78 and risk_count <= 1:
        return Recommendation.ADOPT
    if adoption_score >= 0.62:
        return Recommendation.TRIAL
    return Recommendation.WATCH


def _risk_flags(scored_items) -> tuple[str, ...]:
    flags = []
    for scored in scored_items:
        tags = set(scored.item.tags)
        if {"security", "risk"} & tags:
            flags.append(f"{scored.item.title}: {scored.item.summary}")
        elif "api-churn" in tags or "lock-in" in tags:
            flags.append(f"{scored.item.title}: {scored.item.summary}")
    return tuple(flags[:5])


def build_brief(topic: str, source_runs: tuple[SourceRun, ...]) -> RadarBrief:
    plan = plan_topic(topic)
    scored = score_evidence(source_runs)
    leaders = top_evidence(scored, 8)
    risk_flags = _risk_flags(scored)

    if leaders:
        adoption_score = round(mean(item.score for item in leaders), 4)
        confidence = round(min(0.98, 0.38 + len(leaders) * 0.05 + len({item.item.source for item in leaders}) * 0.06), 3)
    else:
        adoption_score = 0.0
        confidence = 0.1

    recommendation = _recommendation(adoption_score, len(risk_flags), len(scored))
    entity_text = " vs ".join(plan.entities) if plan.comparison else plan.topic
    source_count = len({entry.item.source for entry in scored})
    summary = (
        f"{entity_text} has {len(scored)} normalized evidence items across {source_count} source types. "
        f"The current deterministic score is {adoption_score:.2f}, producing a {recommendation.value.upper()} recommendation."
    )

    findings = []
    for entry in leaders[:6]:
        findings.append(f"{entry.item.title} [{entry.item.source.value}, score {entry.score:.2f}] - {entry.item.summary}")
    if not findings:
        findings.append("No evidence was collected. Re-run with a fixture or live sources.")

    warnings = [warning for run in source_runs for warning in run.warnings]
    if warnings:
        risk_flags = tuple(list(risk_flags) + [f"Source warning: {warning}" for warning in warnings[:3]])

    return RadarBrief(
        topic=topic,
        generated_at=utc_now_iso(),
        recommendation=recommendation,
        confidence=confidence,
        summary=summary,
        key_findings=tuple(findings),
        risk_flags=risk_flags,
        source_runs=source_runs,
        scored_items=scored,
        adoption_score=adoption_score,
    )

