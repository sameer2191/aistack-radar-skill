# AI Stack Radar Skill

Agent-facing orientation for contributors working in this repository.

## Structure

- `skills/aistack-radar/SKILL.md` is the installable skill contract that agent hosts read.
- `skills/aistack-radar/scripts/aistack_radar.py` is the self-contained runtime copied with the skill.
- `skills/aistack-radar/fixtures/demo_signal.json` is the skill-local deterministic fixture.
- `src/aistack_radar/` is the package development engine.
- `fixtures/demo_signal.json` is the package-level deterministic fixture.
- `tests/` covers both the package CLI and the installed skill runtime.
- `docs/` contains user-facing methodology, source, usage, and quality references.

## Development Rules

- Keep the installed skill runtime and package CLI behavior aligned.
- If `fixtures/demo_signal.json` changes, update `skills/aistack-radar/fixtures/demo_signal.json` too.
- If the artifact contract changes, update `README.md`, `skills/aistack-radar/SKILL.md`, and `docs/skill-usage.md`.
- Do not add real credentials, browser cookies, API tokens, or `.env` contents.
- Keep examples deterministic unless the command is explicitly labeled as live mode.
- Prefer Python standard library for the runnable core.
- Run `python3 -m unittest discover -s tests` before claiming the repo is working.

## Useful Commands

```bash
python3 -m unittest discover -s tests
python3 -m aistack_radar research "LangGraph vs OpenAI Agents SDK" --fixture fixtures/demo_signal.json --output runs/demo --emit html
python3 skills/aistack-radar/scripts/aistack_radar.py research "LangGraph vs OpenAI Agents SDK" --fixture skills/aistack-radar/fixtures/demo_signal.json --output runs/skill-demo --emit html
```

## Public Positioning

This is a technical adoption-research tool. Public docs should explain how the
engine works, what evidence it uses, and where the limits are. Avoid personal
or application-process framing in README, docs, code comments, and metadata.
