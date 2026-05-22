"""
compare_all.py — lancia i 4 orchestratori in parallelo e confronta i risultati.

Uso:
    uv run python docs/demos/compare_all.py

Prerequisiti:
    - .env con ANTHROPIC_API_KEY e OPENAI_API_KEY
    - uv sync (installa rich, anthropic, pydantic-ai, langgraph, python-dotenv)
"""

import asyncio
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from rich.console import Console
    from rich.table import Table

    console = Console()
except ImportError:
    console = None

USER_REQUEST = "Function parse_fattura(xml_path: str) -> dict for FatturaPA XML v1.2"
FATTURA_XML = Path("docs/demos/fattura_esempio.xml")

ACCEPTANCE_SCRIPT = """\
import sys, json
sys.path.insert(0, '{workdir}')
try:
    from parser import parse_fattura
    r = parse_fattura('{xml}')
    ok = (
        r.get('numero') == '2026/001' and
        r.get('piva_cedente') == '01234567890' and
        abs(r.get('totale', 0) - 1220.0) < 0.01
    )
    print('PASS' if ok else f'FAIL: {{r}}')
except Exception as e:
    print(f'ERROR: {{e}}')
"""


async def run_with_timer(name: str, coro) -> dict:
    start = time.monotonic()
    try:
        result = await asyncio.wait_for(coro, timeout=300)
        elapsed = time.monotonic() - start
        return {
            "name": name,
            "ok": result.get("ok", False),
            "elapsed": elapsed,
            "stage": result.get("stage", "?"),
            "error": result.get("error"),
        }
    except Exception as e:
        return {
            "name": name,
            "ok": False,
            "elapsed": time.monotonic() - start,
            "stage": "error",
            "error": str(e),
        }


def check_acceptance(workdir: str) -> str:
    script = ACCEPTANCE_SCRIPT.format(workdir=workdir, xml=str(FATTURA_XML.resolve()))
    r = subprocess.run(["python3", "-c", script], capture_output=True, text=True)
    return (r.stdout or r.stderr).strip()


async def run_claude_p(user_request: str) -> dict:
    # TODO: replace with real implementation from the spec files
    # In produzione: chiama subprocess con run_claude_p.sh (spec-base-claude-p.md)
    await asyncio.sleep(1)
    return {"ok": True, "stage": "complete"}


async def run_agent_sdk(user_request: str) -> dict:
    # TODO: replace with real implementation from the spec files
    # In produzione: importa run_orchestrator da spec-agent-sdk.md
    await asyncio.sleep(1)
    return {"ok": True, "stage": "complete"}


async def run_pydantic(user_request: str) -> dict:
    # TODO: replace with real implementation from the spec files
    await asyncio.sleep(1)
    return {"ok": True, "stage": "complete"}


async def run_langgraph(user_request: str) -> dict:
    # TODO: replace with real implementation from the spec files
    await asyncio.sleep(1)
    return {"ok": True, "stage": "complete"}


RUNNERS = [
    ("claude -p", run_claude_p, "/tmp/invoice_parser_cp"),
    ("Agent SDK", run_agent_sdk, "/tmp/invoice_parser_sdk"),
    ("PydanticAI", run_pydantic, "/tmp/invoice_parser_pydantic"),
    ("LangGraph", run_langgraph, "/tmp/invoice_parser_langgraph"),
]


async def main():
    print(f"Avvio {len(RUNNERS)} pipeline in parallelo...\n")
    tasks = [run_with_timer(name, fn(USER_REQUEST)) for name, fn, _ in RUNNERS]
    results = await asyncio.gather(*tasks)

    # Acceptance test su ogni workdir
    for i, (_, _, workdir) in enumerate(RUNNERS):
        results[i]["acceptance"] = check_acceptance(workdir)

    if console:
        table = Table(title="Confronto 4 Orchestratori — FatturaPA Parser")
        table.add_column("Framework", style="bold cyan")
        table.add_column("Tempo", justify="right")
        table.add_column("Stage")
        table.add_column("Linting")
        table.add_column("Acceptance")
        for r in results:
            ok_icon = "[green]OK[/]" if r["ok"] else "[red]FAIL[/]"
            acc = r.get("acceptance", "—")
            acc_fmt = f"[green]{acc}[/]" if acc == "PASS" else f"[red]{acc}[/]"
            table.add_row(
                r["name"],
                f"{r['elapsed']:.1f}s",
                r["stage"],
                ok_icon,
                acc_fmt,
            )
        console.print(table)
    else:
        for r in results:
            print(
                f"{r['name']:15} {r['elapsed']:.1f}s  stage={r['stage']}  acceptance={r.get('acceptance', '—')}"
            )


if __name__ == "__main__":
    asyncio.run(main())
