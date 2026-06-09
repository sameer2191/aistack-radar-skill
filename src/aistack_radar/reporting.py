"""Report writers."""

from __future__ import annotations

import html
import json
from pathlib import Path

from .models import RadarBrief


def write_json(brief: RadarBrief, output_dir: str | Path) -> Path:
    path = Path(output_dir) / "brief.json"
    path.write_text(json.dumps(brief.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def markdown(brief: RadarBrief) -> str:
    lines = [
        f"# AI Stack Radar: {brief.topic}",
        "",
        f"Generated: `{brief.generated_at}`",
        f"Recommendation: **{brief.recommendation.value.upper()}**",
        f"Confidence: `{brief.confidence:.2f}`",
        f"Adoption score: `{brief.adoption_score:.2f}`",
        "",
        "## Summary",
        "",
        brief.summary,
        "",
        "## Key Findings",
        "",
    ]
    for finding in brief.key_findings:
        lines.append(f"- {finding}")
    lines.extend(["", "## Risks And Caveats", ""])
    if brief.risk_flags:
        for risk in brief.risk_flags:
            lines.append(f"- {risk}")
    else:
        lines.append("- No material risk flags were detected in the collected evidence.")
    lines.extend(["", "## Evidence", ""])
    for scored in brief.scored_items[:12]:
        item = scored.item
        lines.append(f"- [{item.title}]({item.url}) - `{item.source.value}` score `{scored.score:.2f}`")
    lines.extend(["", "## Source Health", ""])
    for run in brief.source_runs:
        warning_text = "; ".join(run.warnings) if run.warnings else "ok"
        lines.append(f"- `{run.source.value}`: {len(run.items)} items, {run.elapsed_ms:.1f} ms, {warning_text}")
    lines.append("")
    return "\n".join(lines)


def write_markdown(brief: RadarBrief, output_dir: str | Path) -> Path:
    path = Path(output_dir) / "brief.md"
    path.write_text(markdown(brief), encoding="utf-8")
    return path


def write_html(brief: RadarBrief, output_dir: str | Path) -> Path:
    body = markdown(brief)
    escaped = html.escape(body)
    content = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>AI Stack Radar - {html.escape(brief.topic)}</title>
  <style>
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; background: #0f172a; color: #e5e7eb; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 48px 22px; }}
    pre {{ white-space: pre-wrap; line-height: 1.55; background: #111827; border: 1px solid #334155; border-radius: 8px; padding: 24px; }}
    .badge {{ display: inline-block; padding: 6px 10px; border: 1px solid #38bdf8; color: #bae6fd; border-radius: 999px; margin-bottom: 18px; }}
  </style>
</head>
<body>
<main>
  <div class=\"badge\">{html.escape(brief.recommendation.value.upper())} · confidence {brief.confidence:.2f}</div>
  <pre>{escaped}</pre>
</main>
</body>
</html>
"""
    path = Path(output_dir) / "brief.html"
    path.write_text(content, encoding="utf-8")
    return path


def write_reports(brief: RadarBrief, output_dir: str | Path, *, emit_html: bool = False) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "json": write_json(brief, output_path),
        "markdown": write_markdown(brief, output_path),
    }
    if emit_html:
        artifacts["html"] = write_html(brief, output_path)
    return artifacts

