# Configuration

AI Stack Radar is designed to run without API keys. Configuration is limited to
source selection, timeout behavior, fixture use, and artifact output.

## CLI Flags

| Flag | Default | Description |
| --- | --- | --- |
| `topic` | required | Tool, package, trend, or comparison topic |
| `--fixture PATH` | unset | Load normalized evidence from a local JSON fixture |
| `--source NAME` | default live set when no fixture is provided | Repeatable source selector |
| `--output PATH` | `runs/aistack-radar` | Output directory for artifacts |
| `--emit md|html` | `md` | `html` writes Markdown plus HTML |
| `--timeout SECONDS` | env or `8` | Per-source live HTTP timeout |
| `--print-json` | false | Print the generated brief JSON to stdout |

Supported live sources:

- `github`
- `hackernews`
- `reddit`
- `pypi`
- `npm`
- `arxiv`

When no fixture is provided and no `--source` flags are given, the runtime uses
the conservative default set: `github`, `hackernews`, `reddit`, and `arxiv`.

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `AISTACK_RADAR_TIMEOUT_SECONDS` | `8` | Per-source live HTTP timeout when `--timeout` is not passed |

## Fixture Mode

Fixture mode is deterministic and safe for CI:

```bash
python3 -m aistack_radar research "LangGraph vs OpenAI Agents SDK" \
  --fixture fixtures/demo_signal.json \
  --output runs/demo \
  --emit html
```

Installed skill fixture mode:

```bash
SKILL_DIR="${SKILL_DIR:-$HOME/.codex/skills/aistack-radar}"
python3 "$SKILL_DIR/scripts/aistack_radar.py" research "LangGraph vs OpenAI Agents SDK" \
  --fixture "$SKILL_DIR/fixtures/demo_signal.json" \
  --output runs/demo \
  --emit html
```

## Live Mode

Live mode queries public endpoints and may produce warnings if a source is
unavailable:

```bash
python3 -m aistack_radar research "LangGraph" \
  --source github \
  --source hackernews \
  --source pypi \
  --output runs/live
```

Warnings are written into `brief.json` and `brief.md` under source health and
risk/caveat sections.

## Artifacts

Every run writes:

- `brief.json`: structured data for automation and downstream agents
- `brief.md`: readable Markdown brief with citations and source health

When `--emit html` is used, the run also writes:

- `brief.html`: self-contained, offline-readable HTML

The `runs/` directory is ignored by git because reports are reproducible output.
