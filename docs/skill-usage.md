# AI Stack Radar Skill Usage

AI Stack Radar is an installable agent skill for researching AI, data, and developer-tool stacks. It helps agents run a repeatable CLI workflow, inspect generated artifacts, and produce sourced adoption briefs.

## Local Checkout

From a local checkout:

```bash
cd aistack-radar-skill
```

Install or expose the skill directory using the host agent's normal local-skill mechanism:

```text
skills/aistack-radar/
```

The OpenAI-facing metadata lives at:

```text
agents/openai.yaml
```

## Codex or Claude-Style Usage

Ask the agent to use the skill when the task involves AI, data, or developer-tool stack research:

```text
Use the aistack-radar skill to compare LangGraph and OpenAI Agents SDK for a production agent workflow.
```

The agent should:

- Confirm the research question and decision context.
- Choose fixture-backed or live collection.
- Run the CLI.
- Inspect and cite generated artifacts.
- Avoid unsupported claims.

For deterministic demos or offline checks, ask for fixture mode:

```text
Use aistack-radar with the demo fixture and generate an HTML brief.
```

For current market research, ask for live collection:

```text
Use aistack-radar to research current adoption signals for vector database options in AI application platforms.
```

## CLI Examples

Fixture-backed demo:

```bash
python -m aistack_radar research "LangGraph vs OpenAI Agents SDK" --fixture fixtures/demo_signal.json --output runs/demo --emit html
```

Live collection shape:

```bash
python -m aistack_radar research "LangGraph vs OpenAI Agents SDK" --output runs/langgraph-openai-agents --emit html
```

Suggested artifact review:

```bash
ls runs/demo
```

The final agent response should cite generated artifacts such as `runs/demo/brief.html`, `runs/demo/brief.md`, or `runs/demo/brief.json` when those files exist.

## Output Standard

A complete brief should include the question, recommendation, evidence summary, risks, caveats, and artifact links. Fixture-backed output must be labeled as fixture-backed and should not be described as current market evidence.
