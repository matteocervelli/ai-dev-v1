# Spec: Orchestratore con Claude Agent SDK — Parser FatturaPA

## Goal

Same as spec-base, but the orchestrator is a Python Agent (claude-opus-4-7)
with spawn tools for sub-agents.

## Architecture

```
OrchestratorAgent (Opus — reasoning, judgment, routing)
  tools: spawn_spec_agent, spawn_build_agent, spawn_quality_agent, load_skill
  → spawns SpecAgent    (Haiku)  — writes SPEC.md
  → spawns BuildAgent   (Sonnet) — writes parser.py
  → spawns QualityAgent (Opus)   — evaluates quality, returns PASS/FAIL
```

## Key Design Decisions

- Orchestrator is an LLM Agent, not control flow — it decides retry/proceed
- Sub-agents are spawned via tools, return structured output
- Skill file loaded once, cached across Build calls (`cache_control`)
- Env: `python-dotenv` loads `.env`, `ANTHROPIC_API_KEY` required
- Permission mode: `acceptEdits` (no interactive prompts)

## OrchestratorAgent System Prompt

```
You orchestrate a 3-agent pipeline for FatturaPA parsing.
Use spawn_* tools in order: spec → build → quality.
After each step, evaluate the output. If insufficient, retry (max 2x).
Quality Agent output is your final judge — PASS means done, FAIL means rework build.
```

## Sub-Agent Specs

| Agent | Model | Tools | max_turns | Responsibility |
|---|---|---|---|---|
| SpecAgent | haiku | Write | 3 | Receives user_request → writes SPEC.md |
| BuildAgent | sonnet | Read, Write, Edit, Bash | 8 | Receives SPEC.md + skill content → writes parser.py |
| QualityAgent | opus | Read, Bash | 5 | Runs ruff + mypy → returns structured verdict |

## Implementation Notes

- Use `claude-agent-sdk` (anthropic package)
- WorkDir: `/tmp/invoice_parser`
- Load `.env` with `python-dotenv` at module import
- `OrchestratorAgent.run()` is the single entry point
- Skill content injected with `cache_control=ephemeral` on first Build call

## Files Produced

- `/tmp/invoice_parser/SPEC.md`
- `/tmp/invoice_parser/parser.py`
- `/tmp/invoice_parser/quality_report.md`

## Implementation Sketch

```python
from __future__ import annotations
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

WORKDIR = Path("/tmp/invoice_parser")
WORKDIR.mkdir(parents=True, exist_ok=True)
SKILL_PATH = Path("./skills/fatturapa-parser/SKILL.md")
MAX_RETRIES = 2

client = anthropic.Anthropic()


def load_skill() -> str:
    return SKILL_PATH.read_text()


def spawn_spec_agent(user_request: str) -> str:
    """Haiku agent: writes SPEC.md, returns its content."""
    result = client.beta.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,
        system="You are a spec writer for software components.",
        messages=[{"role": "user", "content": user_request}],
    )
    spec = result.content[0].text
    (WORKDIR / "SPEC.md").write_text(spec)
    return spec


def spawn_build_agent(spec: str, skill: str) -> str:
    """Sonnet agent: implements parser.py from spec + skill."""
    system = (
        "You are a Python developer. Implement exactly what the spec requires.\n\n"
        f"Skill reference:\n{skill}"
    )
    result = client.beta.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=[
            {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}
        ],
        messages=[{"role": "user", "content": f"Implement per spec:\n\n{spec}"}],
    )
    code = result.content[0].text
    (WORKDIR / "parser.py").write_text(code)
    return code


def run_acceptance_test() -> str:
    """Esegue parser.py sulla fattura_esempio.xml e verifica i campi attesi."""
    result = subprocess.run(
        ["python3", "-c",
         "import sys, json; sys.path.insert(0,'.');"
         "from parser import parse_fattura;"
         "print(json.dumps(parse_fattura('docs/demos/fattura_esempio.xml')))"],
        cwd=WORKDIR, capture_output=True, text=True,
    )
    return result.stdout or result.stderr


def spawn_quality_agent() -> dict[str, str]:
    """Opus agent: runs ruff+mypy+acceptance test, returns structured verdict."""
    import subprocess

    report_lines = []
    for cmd in [
        ["ruff", "check", str(WORKDIR / "parser.py")],
        ["mypy", str(WORKDIR / "parser.py")],
    ]:
        r = subprocess.run(cmd, capture_output=True, text=True)
        report_lines.append(r.stdout + r.stderr)

    acceptance = run_acceptance_test()
    report_lines.append(f"Acceptance test: {acceptance}")

    report = "\n".join(report_lines)
    (WORKDIR / "quality_report.md").write_text(report)

    result = client.beta.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        system=(
            "You are a code quality judge. "
            "Criteri: parse_fattura() deve restituire numero (str), data (str), "
            "piva_cedente (str), imponibile (float), iva (float), totale (float). "
            "Testa su fattura_esempio.xml: totale atteso 1220.0. "
            "Usa run_acceptance_test oltre a ruff e mypy. "
            "Reply with JSON: {\"verdict\": \"PASS\"|\"FAIL\", \"reason\": \"...\"}"
        ),
        messages=[{"role": "user", "content": report}],
    )
    import json
    return json.loads(result.content[0].text)


def run_orchestrator(user_request: str) -> None:
    skill = load_skill()

    # Stage 1: Spec
    spec = ""
    for attempt in range(MAX_RETRIES):
        spec = spawn_spec_agent(user_request)
        verdict = client.beta.messages.create(
            model="claude-opus-4-5",
            max_tokens=64,
            messages=[{"role": "user", "content": f"Is this spec complete? YES or RETRY: <reason>\n\n{spec}"}],
        ).content[0].text.strip()
        if verdict.startswith("YES"):
            break
        if attempt == MAX_RETRIES - 1:
            raise RuntimeError(f"Spec stage failed: {verdict}")

    # Stage 2: Build
    code = ""
    for attempt in range(MAX_RETRIES):
        code = spawn_build_agent(spec, skill)
        verdict = client.beta.messages.create(
            model="claude-opus-4-5",
            max_tokens=64,
            messages=[{"role": "user", "content": f"Does this code implement the spec? YES or RETRY: <reason>\n\n{code}"}],
        ).content[0].text.strip()
        if verdict.startswith("YES"):
            break
        if attempt == MAX_RETRIES - 1:
            raise RuntimeError(f"Build stage failed: {verdict}")

    # Stage 3: Quality
    for attempt in range(MAX_RETRIES):
        result = spawn_quality_agent()
        if result["verdict"] == "PASS":
            print(f"Done. Output: {WORKDIR}/parser.py")
            return
        if attempt == MAX_RETRIES - 1:
            raise RuntimeError(f"Quality stage failed: {result['reason']}")
        # rework: one more build pass with failure context
        spawn_build_agent(spec + f"\n\nFix these issues:\n{result['reason']}", skill)


if __name__ == "__main__":
    run_orchestrator("Parse a FatturaPA XML file into a normalized Python dict.")
```
