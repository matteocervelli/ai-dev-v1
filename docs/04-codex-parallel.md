# Codex — Lo Stesso Sistema, Implementazione Diversa

> **Key message:** Due tool, lo stesso modello mentale — CLAUDE.md/instructions.md, skills, hooks, rules. Imparare uno significa capire entrambi.

**Documentazione ufficiale:**

- [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code) — primitive, hooks, settings
- [Codex docs](https://platform.openai.com/docs/codex) — config.toml, approval policy, sandbox

## Architettura Speculare

Codex (OpenAI) e Claude Code condividono la stessa filosofia: CLI agent configurabile tramite file. Le differenze sono nell'implementazione, non nel modello mentale.

```
~/.codex/
├── config.toml            # Modello, approval policy, sandbox
├── hooks.json             # Hook events (stesso pattern di Claude)
├── hooks/
│   ├── codex_hook.py      # Dispatcher Python
│   └── handlers/
│       ├── safety.py      # PreToolUse bash safety
│       ├── git_feedback.py
│       └── context_monitor.py
└── instructions.md        # Equivalente del CLAUDE.md globale
```

> **[demo]** `tree ~/.claude/` e `tree ~/.codex/` affiancati nel terminale — mostra la simmetria tra `skills/`, `hooks/handlers/`, `rules/` in entrambi; struttura identica, file format diversi

## config.toml — Configurazione Base

```toml
[model]
model = "gpt-5.5"
reasoning = "high"

[approval]
policy = "on-request"   # never-ask | on-request | always

[sandbox]
mode = "workspace-write"   # read-only | workspace-write | full-access
```

## "Codex Danger" — Full Auto Mode

Profilo `full-auto` in `~/.codex/config.toml`:

```toml
[profiles.full-auto]
model = "gpt-5.4"
approval_policy = "never-ask"
sandbox = "full-access"
```

Attivazione:

```bash
codex --profile full-auto "refactor the entire auth module"
```

Equivalente Claude Code: `--dangerously-skip-permissions` o permission mode `bypassPermissions`.

**Quando usarlo:** task ben definiti, repo con CI robusta, ambiente isolato (container/worktree).
**Non usarlo:** produzione, repo condivisi, task ambigui.

> **[demo]** `codex --profile full-auto "list all files"` vs `claude --dangerously-skip-permissions "list all files"` — stessa semantica, flag diversi; mostra quando usarlo (task ben definiti, CI, ambiente isolato)

> **[fonte]** [How AI Is Transforming Work at Anthropic](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) — i dati reali (132 engineer, ~20 azioni autonome prima di chiedere input) danno una baseline concreta per calibrare `approval_policy = "never-ask"`

## Differenze Pratiche Claude Code vs Codex

| Aspetto        | Claude Code                           | Codex                                 |
| -------------- | ------------------------------------- | ------------------------------------- |
| Config formato | JSON (settings.json)                  | TOML (config.toml)                    |
| Skills         | Markdown (`~/.claude/skills/`)        | Non ha equivalente nativo             |
| Model default  | Claude Sonnet 4.6                     | GPT-5.5                               |
| Sandbox        | Worktree integration                  | workspace-write / full-access         |
| Plugin system  | JSON registry + Anthropic marketplace | Plugin OpenAI (browser, github, docs) |
| Hook system    | Python dispatcher + YAML rules        | Python dispatcher + JSON config       |

## Hook System Codex

`~/.codex/hooks.json` (struttura identica a Claude):

```json
{
  "PreToolUse": [
    {
      "matcher": "shell",
      "hooks": [
        {
          "type": "command",
          "command": "python ~/.codex/hooks/handlers/safety.py"
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "edit_file|write_file",
      "hooks": [
        {
          "type": "command",
          "command": "python ~/.codex/hooks/handlers/git_feedback.py"
        }
      ]
    }
  ]
}
```

> **[demo]** `git commit --no-verify` su Claude Code — il hook `bash.py` blocca con exit code 1; su Codex lo stesso handler `safety.py`; mostra che la logica Python è condivisa e solo `hooks.json` vs `settings.json` cambia

## Usarli Insieme

Il pattern multi-model companion:

- **Claude Code** → orchestrazione, implementazione, skills specializzate
- **Codex** → code review indipendente, bug detection, security check
- **Modelli locali** → task veloci, privacy, costo zero

In pratica: `/review --all` dispatcha lo stesso diff a Codex, Gemini e Claude in parallelo. Il consenso multi-model è il giudice — nessun self-review. Se Claude ha introdotto un bug silenzioso, Codex lo vede perché parte da contesto e training diversi.

Il hook system di entrambi può essere sincronizzato (stessa logica Python, config diversa).

> **[demo]** `/review --all` su un diff aperto — mostra Codex e Gemini che ricevono lo stesso prompt in parallelo; apri un risultato per vedere il reflection loop: `/implementation` scrive, `/review --all` giudica, `/fix` corregge
> **[demo]** Codex review del notebook `skill_writer` — dopo aver generato skill, `codexfa` valuta il Jupyter notebook prodotto: vedi [`docs/demos/demo-skill-writer.md`](demos/demo-skill-writer.md) Step 5.

> **[fonte]** [karpathy/autoresearch](https://github.com/karpathy/autoresearch) — il Ralph Loop dimostra come agenti multipli eseguano ~12 esperimenti/ora, lo stesso pattern del dispatch parallelo di `/review --all`

> **[fonte]** [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — il pattern orchestrator-workers di questa sezione (Claude orchestratore, Codex/Gemini worker specializzati) è esattamente il workflow descritto nell'articolo

> **[fonte]** [Building agents with the Claude Agent SDK](https://claude.com/blog/building-agents-with-the-claude-agent-sdk) — i subagent con context isolation separato sono il meccanismo che rende il giudizio di Codex e Gemini indipendente da Claude, eliminando il self-review bias
