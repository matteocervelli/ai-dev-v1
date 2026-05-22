# Live Build — Da Repo Vuoto a Configurato (30 min)

## Setup

```bash
mkdir demo-repo && cd demo-repo
git init
```

## Step 1: CLAUDE.md (5 min)

```bash
cat > CLAUDE.md << 'EOF'
# Demo Repo

## Stack
Python 3.12, uv

## Workflow
- TDD obbligatorio
- Conventional commits
- /security-verify scan prima di ogni commit

## Non fare
- Non aggiungere dipendenze senza motivo
- Non usare `--no-verify`
EOF
```

Mostra: Claude ora "sa" il contesto senza che tu lo ripeta ogni volta.

## Step 2: Prima Rule (5 min)

```bash
mkdir -p .claude/rules
cat > .claude/rules/naming.md << 'EOF'
# Naming Conventions

- Funzioni: verbi (get_user, process_ticket)
- Classi: sostantivi (UserService, TicketProcessor)
- File: snake_case, max 500 righe
EOF
```

## Step 3: Primo Hook (10 min)

Esempio di tool use chiamato da Claude:

```json
{
  "session_id": "abc123-def456-...",
  "transcript_path": "/home/<user>/.claude/projects/.../conversation.jsonl",
  "cwd": "/home/<user>/projects/ai-dev-v1",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/test_dir",
    "description": "Cleanup temp directory"
  }
}
```
Esempio di Hook

```bash
mkdir -p $HOME/.claude/hooks
cat > $HOME/.claude/hooks/pre-bash.py << 'EOF'
#!/usr/bin/env python3
import json, sys

payload = json.load(sys.stdin)  # Conversione in tipi Python
tool_input = payload.get("tool_input", {})  # Estrae da payload il dict "tool_input": {"command": "...", "description": "..."}
command = tool_input.get("command", "")  # Estrae la stringa "command" con default vuoto per evitare KeyError

# Valutare espansione della list di flags, come -fr, -r, -f, -R --force, etc. usando shlex.split per tokenizzare e cercare pattern più robusti
BLOCKED = ["rm -rf", "--no-verify", "curl | sh"]
for pattern in BLOCKED:
    if pattern in command:
        print(f"Blocked: {pattern}", file=sys.stderr)
        sys.exit(1)

sys.exit(0)
EOF

chmod +x $HOME/.claude/hooks/pre-bash.py
```

# Registra in settings.json
cat > $HOME/.claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "$HOME/.claude/hooks/pre-bash.py"}]
      }
    ]
  }
}
EOF
```

Test: chiedi a Claude di eseguire `rm -rf /tmp/cartella_di_prova_ad_hoc` → bloccato.

## Step 4: Prima Skill (10 min)

```bash
mkdir -p $HOME/.claude/skills
cat > $HOME/.claude/skills/ticket-triage.md << 'EOF'
---
name: ticket-triage
description: Triage un ticket di supporto e produce bozza di risposta
---

## Workflow

1. Leggi il ticket
2. Categorizza: billing_issue | shipping_delay | technical_problem | other
3. Scrivi bozza risposta (max 3 frasi)
4. Decidi: reply | ask_clarification | escalate
EOF
```

Uso: `/ticket-triage "Il mio ordine è in ritardo"`

## Risultato

In 30 minuti il repo ha:

- Contesto permanente via CLAUDE.md
- Guardrail via hook
- Comportamento disciplinato via rule
- Workflow riusabile via skill

Questi 4 elementi coprono il 90% del valore di un sistema AI-driven ben configurato.
