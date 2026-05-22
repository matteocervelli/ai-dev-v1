# Demo: Parser FatturaPA — Pipeline Spec→Build→Quality

**Durata:** 20 min · **Livello:** intermedio · **Prerequisiti:** `.env` con `ANTHROPIC_API_KEY`

Costruzione live di una pipeline a 3 agenti per parsare fatture FatturaPA (XML).
Due implementazioni a confronto: orchestratore bash con `claude -p` e orchestratore Python con Agent SDK.
Tutti e quattro i framework (Claude Agent SDK, Codex SDK, PydanticAI, LangGraph) vengono lanciati in parallelo alla fine.

## Riferimenti

- User story: [`user-story-fatturapa-parser.md`](user-story-fatturapa-parser.md)
- Fattura di esempio: [`fattura_esempio.xml`](fattura_esempio.xml)
- Spec orchestratore bash: [`spec-base-claude-p.md`](spec-base-claude-p.md)
- Spec orchestratore Agent SDK: [`spec-agent-sdk.md`](spec-agent-sdk.md)
- Confronto 4 SDK: [`agentic_sdks_comparison.md`](agentic_sdks_comparison.md)

## Step 1 — Scaffold live (3 min)

Crea il repo di lavoro da zero davanti al pubblico:

```bash
mkdir fatturapa-compare && cd fatturapa-compare
git init
cp /path/to/ai-dev-v1/docs/demos/fattura_esempio.xml .
mkdir -p skills/fatturapa-parser
cp /path/to/ai-dev-v1/docs/demos/skills/fatturapa-parser/* skills/fatturapa-parser/
cp /path/to/ai-dev-v1/docs/demos/spec-base-claude-p.md .
cp /path/to/ai-dev-v1/docs/demos/spec-agent-sdk.md .
cp /path/to/ai-dev-v1/docs/demos/compare_all.py .
```

Mostra la struttura risultante:

```bash
tree .
```

```
fatturapa-compare/
  fattura_esempio.xml        ← la fattura reale da parsare
  skills/fatturapa-parser/   ← skill con XPath e script di riferimento
    SKILL.md
    parse_xml.py
  spec-base-claude-p.md      ← spec versione bash
  spec-agent-sdk.md          ← spec versione Python SDK
  compare_all.py             ← runner parallelo 4 framework
```

Mostra brevemente la fattura:

```bash
grep -E "Numero|Data|Denominazione|ImponibileImporto|ImportoTotale" fattura_esempio.xml
```

## Step 2 — Avvio in background (1 min)

Lancia entrambe le pipeline **prima di spiegare** — elaborano mentre il pubblico ascolta.

```bash
# Terminale 1: orchestratore bash con claude -p
ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY .env | cut -d= -f2) \
bash run_claude_p.sh "parse FatturaPA XML" > /tmp/log_cp.txt 2>&1 &
echo "PID claude-p: $!"

# Terminale 2: orchestratore Agent SDK
uv run python orchestrate_sdk.py > /tmp/log_sdk.txt 2>&1 &
echo "PID sdk: $!"
```

I processi girano in background. Il pubblico vede i PID — il lavoro è avviato.

## Step 3 — Confronto concettuale (10 min)

Mentre le pipeline elaborano, apri [`agentic_sdks_comparison.md`](agentic_sdks_comparison.md) e percorri:

1. **Schema architetturale** — immagine Excalidraw: User → Orchestrator → Spec/Build/Quality → Result
2. **Orchestratore bash vs Agent SDK** — la differenza non è il modello, è chi decide il retry
3. **PydanticAI** — output tipati, ma nessun tool filesystem nativo
4. **LangGraph** — il loop `quality → build → quality` è un'edge condizionale, una riga di codice

Punti da enfatizzare:
- Tutti e 4 usano gli stessi modelli (Haiku/Sonnet/Opus), gli stessi dati, la stessa skill
- La differenza è l'**ergonomia del controllo**: quanto codice serve per gestire un retry?
- In `claude -p`: il retry è `if [ "$DECISION" == "RETRY" ]` — bash puro
- In Agent SDK: l'orchestratore Opus decide autonomamente quando riprovare

## Step 4 — Risultati (3 min)

Controlla che le pipeline abbiano terminato:

```bash
jobs  # mostra processi in background
cat /tmp/log_cp.txt | tail -10
cat /tmp/log_sdk.txt | tail -10
```

Confronta gli output prodotti:

```bash
# Struttura del parser generato da claude -p
head -30 /tmp/invoice_parser_cp/parser.py

# Struttura del parser generato da Agent SDK
head -30 /tmp/invoice_parser_sdk/parser.py
```

Verifica manuale dell'acceptance test su entrambi:

```bash
python3 -c "
import sys, json
for workdir, label in [('/tmp/invoice_parser_cp', 'claude -p'), ('/tmp/invoice_parser_sdk', 'Agent SDK')]:
    sys.path.insert(0, workdir)
    try:
        from parser import parse_fattura
        r = parse_fattura('fattura_esempio.xml')
        ok = abs(r.get('totale', 0) - 1220.0) < 0.01
        print(f'{label}: {\"PASS\" if ok else \"FAIL\"} → {r}')
    except Exception as e:
        print(f'{label}: ERROR → {e}')
    sys.path.pop(0)
"
```

## Step 5 — Tutti e 4 in parallelo con `compare_all.py` (3 min)

```bash
uv run python compare_all.py
```

Output atteso (Rich table):

```
┌─────────────────┬─────────┬────────┬──────────┬──────────────────┐
│ Framework       │ Tempo   │ Stage  │ Linting  │ Acceptance Test  │
├─────────────────┼─────────┼────────┼──────────┼──────────────────┤
│ claude -p       │ 45.2s   │ done   │ PASS     │ PASS             │
│ Agent SDK       │ 38.7s   │ done   │ PASS     │ PASS             │
│ PydanticAI      │ 52.1s   │ done   │ PASS     │ FAIL             │
│ LangGraph       │ 41.4s   │ done   │ PASS     │ PASS             │
└─────────────────┴─────────┴────────┴──────────┴──────────────────┘
```

Il risultato di PydanticAI è `FAIL` sull'acceptance test perché non ha tools filesystem nativi:
senza `run_acceptance_test` registrato esplicitamente, il Quality Agent non esegue il parser sulla fattura reale — passa il linter ma non verifica l'output funzionale.

Questa è la differenza concreta tra un framework con tool discovery nativa (Claude Agent SDK, LangGraph)
e uno dove ogni tool va registrato esplicitamente (PydanticAI).

## Cleanup

```bash
rm -rf /tmp/invoice_parser_cp /tmp/invoice_parser_sdk /tmp/invoice_parser_pydantic /tmp/invoice_parser_langgraph
```
