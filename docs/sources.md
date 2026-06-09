# Sources

AI Stack Radar supports deterministic fixture runs and optional live collection.

## Fixture Mode

Fixture mode is the default validation path. It reads normalized evidence from
JSON and does not require network access or credentials:

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

## Live Sources

Live connectors use Python standard-library HTTP calls and degrade to warnings
instead of failing the run.

| Source | Endpoint | Notes |
| --- | --- | --- |
| GitHub | `api.github.com/search/repositories` | Unauthenticated rate limits apply. |
| Hacker News | Algolia HN API | Searches recent stories and discussions. |
| Reddit | Public JSON search | May rate-limit or block some clients. |
| PyPI | `pypi.org/pypi/{package}/json` | Best when the topic starts with a package name. |
| npm | `registry.npmjs.org/{package}` | Best when the topic starts with a package name. |
| arXiv | Atom API | Searches recent papers. |

Use live sources explicitly:

```bash
python3 -m aistack_radar research "LangGraph" \
  --source github --source hackernews --source pypi \
  --output runs/live
```

Reports include source warnings so readers can see when a live source was thin,
rate-limited, or unavailable.
