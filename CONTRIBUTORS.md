# Contributors

AI Stack Radar is maintained as a small, dependency-light skill and CLI.

## Contribution Checklist

- Keep the runnable core dependency-free unless a dependency clearly changes the
  capability of the project.
- Add or update tests for behavior changes.
- Keep the skill runtime and package CLI aligned.
- Update `README.md`, `CONFIGURATION.md`, and `skills/aistack-radar/SKILL.md`
  when command behavior changes.
- Do not commit secrets, API keys, cookies, local `.env` files, or generated
  run artifacts.

## Local Verification

```bash
python3 -m unittest discover -s tests
python3 -m aistack_radar research "LangGraph vs OpenAI Agents SDK" --fixture fixtures/demo_signal.json --output runs/demo --emit html
python3 skills/aistack-radar/scripts/aistack_radar.py research "LangGraph vs OpenAI Agents SDK" --fixture skills/aistack-radar/fixtures/demo_signal.json --output runs/skill-demo --emit html
```

## Release Notes

Update `CHANGELOG.md` for user-visible changes. The current public artifact
contract is `brief.json`, `brief.md`, and optional `brief.html`.
