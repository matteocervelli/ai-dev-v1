# Demo: skill_writer — Generare Skill Programmaticamente

**Durata:** ~12 min | **Rischio:** basso — tutto locale, nessun deploy

Il punto meta della demo: usiamo l'API Anthropic per scrivere skill di Claude Code.
Poi usiamo `/review` con Codex come giudice esterno per valutare quello che abbiamo prodotto.

## Setup

```bash
uv sync  # crea .venv e installa dipendenze
source .venv/bin/activate
```

Verifica che l'API key sia caricata:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:20])"
```

## Step 1 — Scope detection (2 min)

Mostra dove il tool scrive in base al contesto:

```python
from src.skill_writer import SkillWriter

sw = SkillWriter()              # auto-detect: siamo in un repo con .claude/ → project
print(sw.scope_name, sw.scope_path)

sw_global = SkillWriter(scope="global")
print(sw_global.scope_name, sw_global.scope_path)
```

**Talking point:** stessa logica del `--global` / `--project` di Claude Code. Il tool sa dove sei.

## Step 2 — Creazione manuale (3 min)

```python
result = sw.skill(
    name="summarize-it",
    description="Riassumi qualsiasi testo in 5 punti in italiano",
    content=(
        "Leggi il contenuto fornito e restituisci un riassunto conciso.\n\n"
        "Formato obbligatorio:\n"
        "- Massimo 5 punti\n"
        "- Ogni punto max 20 parole\n"
        "- Lingua: italiano\n\n"
        "Input: $ARGUMENTS"
    ),
    overwrite=True,
)
print(result)
print(result.path.read_text())
```

Apri il file generato nell'editor: mostra il frontmatter YAML + il corpo.

## Step 3 — Claude scrive una skill per Claude Code (5 min)

```python
# Claude (Haiku, economico) genera il contenuto
result = sw.skill(
    name="security-review-py",
    description="Analizza codice Python per vulnerabilità OWASP Top 10",
    generate=True,   # chiama Anthropic API
    overwrite=True,
)
print(result)
print(result.path.read_text())
```

**Talking point:** `generate=True` usa `claude-haiku-4-5` con system prompt stretto.
Il modello genera le istruzioni — noi scriviamo il file. Separazione netta.

## Step 4 — CLI (2 min)

```bash
# Stesso risultato da terminale
skill-writer skill create commit-msg \
  --description "Genera conventional commit message per le modifiche staged" \
  --generate \
  --scope project \
  --overwrite

# Inventario
skill-writer list
```

## Step 5 — Codex review del notebook (bonus, 5 min)

Apriamo Codex come giudice esterno sul notebook prodotto:

```bash
# Da Claude Code, con Codex come companion reviewer
# La skill /review dispatcha a Codex in parallelo
/review gate notebooks/skill_writer_demo.ipynb
```

Oppure direttamente da Codex:

```bash
codexfa "Leggi notebooks/skill_writer_demo.ipynb. Valuta:
1. Il codice è corretto e robusto?
2. Mancano edge case (API key non settata, file già esistente, nome non valido)?
3. La demo è comprensibile per un pubblico sviluppatore non esperto di Claude Code?
Riporta massimo 5 issue con priorità."
```

**Talking point:** `/review` non è auto-review. Codex ha training diverso, cieca spot diversi.
Questo è il companion pattern applicato al codice del workshop stesso.

## File prodotti

```
.claude/skills/
  summarize-it.md
  security-review-py.md
  commit-msg.md
```

## Cleanup (opzionale)

```bash
skill-writer list  # mostra cosa c'è
rm .claude/skills/summarize-it.md .claude/skills/security-review-py.md .claude/skills/commit-msg.md
```
