# Spec: Orchestratore con `claude -p` — Parser FatturaPA

## Goal

Parse a FatturaPA XML file into a normalized dict using a 3-agent pipeline.
The orchestrator uses `claude -p` (headless Claude) to make routing decisions.

## Architecture

```
ORCH (bash script + claude -p for decisions)
  → Spec Agent   (claude -p --model haiku)
  → Build Agent  (claude -p --model sonnet)
  → Quality Agent (claude -p --model opus as judge)
```

## Key Design Decisions

- Orchestrator is a bash script that calls `claude -p` for LLM decisions
- Each agent is a `claude -p` call with specific system prompt + tools
- Skill is loaded from `./skills/fatturapa-parser/SKILL.md` and injected into system prompt
- Env: `ANTHROPIC_API_KEY` loaded from `.env`
- Output: `parser.py` in `/tmp/invoice_parser/`

## Inputs/Outputs per Agent

| Agent | Input | Output |
|---|---|---|
| Spec | user_request | SPEC.md |
| Build | SPEC.md + skill content | parser.py |
| Quality | parser.py + ruff/mypy output | PASS or FAIL+reason |

## Orchestrator Decision Points (`claude -p` calls)

1. After spec: `"Is this spec complete enough? YES or RETRY: <reason>"`
2. After build: `"Does this code implement the spec correctly? YES or RETRY: <reason>"`
3. After quality: `"Are the issues critical? ACCEPT or REWORK: <reason>"`

## Error Handling

- Max 2 retries per stage
- If retry limit hit: fail with stage + last error
- Load `.env` before any API call

## Files Produced

- `/tmp/invoice_parser/SPEC.md`
- `/tmp/invoice_parser/parser.py`
- `/tmp/invoice_parser/quality_report.txt`

## Example Orchestrator Shell Sketch

```bash
#!/usr/bin/env bash
set -euo pipefail
source .env

WORKDIR=/tmp/invoice_parser
mkdir -p "$WORKDIR"
SKILL=$(cat ./skills/fatturapa-parser/SKILL.md)
MAX_RETRIES=2

# Stage 1: Spec
for attempt in $(seq 1 $MAX_RETRIES); do
  claude -p --model haiku \
    --system "You are a spec writer. $SKILL" \
    "Write a SPEC.md for a FatturaPA XML parser" \
    > "$WORKDIR/SPEC.md"

  decision=$(claude -p "Is this spec complete enough? Reply YES or RETRY: <reason>" \
    < "$WORKDIR/SPEC.md")
  [[ "$decision" == YES* ]] && break
  [[ $attempt -eq $MAX_RETRIES ]] && { echo "FAIL: spec stage — $decision"; exit 1; }
done

# Stage 2: Build
for attempt in $(seq 1 $MAX_RETRIES); do
  claude -p --model sonnet \
    --system "You are a Python developer. Skill: $SKILL" \
    --allowedTools Write \
    "Implement parser.py per SPEC: $(cat "$WORKDIR/SPEC.md")" \
    > "$WORKDIR/parser.py"

  decision=$(claude -p "Does this code implement the spec correctly? YES or RETRY: <reason>" \
    < "$WORKDIR/parser.py")
  [[ "$decision" == YES* ]] && break
  [[ $attempt -eq $MAX_RETRIES ]] && { echo "FAIL: build stage — $decision"; exit 1; }
done

# Stage 3: Quality
RUFF_OUT=$(ruff check "$WORKDIR/parser.py" 2>&1 || true)
MYPY_OUT=$(mypy "$WORKDIR/parser.py" 2>&1 || true)
printf "%s\n%s\n" "$RUFF_OUT" "$MYPY_OUT" > "$WORKDIR/quality_report.txt"

### Verifica funzionale (acceptance test)

Dopo ruff/mypy, il Quality step esegue il parser sulla fattura reale:

```bash
VERIFY=$(python3 -c "
import sys; sys.path.insert(0, '/tmp/invoice_parser')
from parser import parse_fattura
r = parse_fattura('docs/demos/fattura_esempio.xml')
checks = [
    r.get('numero') == '2026/001',
    r.get('piva_cedente') == '01234567890',
    isinstance(r.get('imponibile'), float),
    abs(r.get('totale', 0) - 1220.0) < 0.01,
]
print('PASS' if all(checks) else f'FAIL: {r}')
" 2>&1)
```

L'orchestratore Opus giudica ruff + mypy + acceptance test insieme:

```bash
VERDICT=$(printf "Ruff: %s\nMypy: %s\nAcceptance: %s\nCriteri: numero, data, piva_cedente, imponibile, iva, totale con tipi corretti. PASS o REWORK: <motivo>" \
  "$RUFF_OUT" "$MYPY_OUT" "$VERIFY" | claude -p --model claude-opus-4-7)
```

for attempt in $(seq 1 $MAX_RETRIES); do
  decision=$(claude -p --model opus \
    "Are the issues critical? ACCEPT or REWORK: <reason>" \
    < "$WORKDIR/quality_report.txt")
  [[ "$decision" == ACCEPT* ]] && break
  [[ $attempt -eq $MAX_RETRIES ]] && { echo "FAIL: quality stage — $decision"; exit 1; }
  # rework: re-run build stage once more
  claude -p --model sonnet \
    --system "Fix the following issues: $(cat "$WORKDIR/quality_report.txt")" \
    "$(cat "$WORKDIR/parser.py")" > "$WORKDIR/parser.py"
done

echo "Done. Output: $WORKDIR/parser.py"
```
