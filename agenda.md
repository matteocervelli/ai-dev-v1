# Agenda — AI-Driven Development with Claude Code

**22 maggio 2026 · 4 ore (9:00–13:00)**

## Programma

| Orario    | Blocco                             | Contenuto                                                                                                                   | Rischio |
| --------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------- |
| 0:00–0:15 | **Cold Open**                      | Pipeline live `/discovery`→`/ship` · supply chain 30s                                                                       | ALTO    |
| 0:15–1:20 | **Anatomia e Configurazione**      | →                                                                                                                           | MEDIO   |
|           | 0:15–0:18                          | [CLAUDE.md e struttura](docs/01-claude-code-anatomy.md) · before/after repo                                                 |         |
|           | 0:18–0:27                          | settings.json · permission modes · context rot                                                                              |         |
|           | 0:27–0:35                          | [Agents vs Skills vs Commands](docs/01-claude-code-anatomy.md) · MCP                                                        |         |
|           | 0:35–0:45                          | [Skills](docs/01-claude-code-anatomy.md) · `/pre-commit` live su Claude e [Codex](docs/04-codex-parallel.md)                |         |
|           | 0:45–0:55                          | [Hooks — 5 eventi](docs/01-claude-code-anatomy.md) · trigger live · [Sandbox e permissions](docs/05-sandbox-permissions.md) |         |
|           | 0:55–1:10                          | Rules · prompt injection · agents · plugin                                                                                  |         |
|           | 1:10–1:20                          | [Supply chain — TeamPCP](docs/08-supply-chain-defense.md) · import hook · livelli difesa                                    |         |
| 1:20–1:35 | **PAUSA**                          |                                                                                                                             | —       |
| 1:35–2:05 | **Persistent Memory**              | →                                                                                                                           | MEDIO   |
|           | 1:35–1:45                          | [Stop hook live · continuation.md](docs/03-persistent-memory.md)                                                            |         |
|           | 1:45–1:55                          | `/memory recall` live                                                                                                       |         |
|           | 1:55–2:05                          | Strategie di memoria · tradeoff context/costo                                                                               |         |
| 2:05–2:15 | **PAUSA**                          |                                                                                                                             | —       |
| 2:15–2:50 | **Modelli Alternativi**            | →                                                                                                                           | ALTO    |
|           | 2:15–2:25                          | [Panoramica tool e modelli](docs/06-alternative-models.md) · routing intelligente                                           |         |
|           | 2:25–2:40                          | Demo MLX Studio (`make proxy-mlx` · `claude-mlx`)                                                                           |         |
|           | 2:40–2:45                          | Demo DeepSeek (`make proxy-deepseek` · `claude-deepseek`)                                                                   |         |
|           | 2:45–2:50                          | [OpenCode](docs/06-alternative-models.md) · fallback Ollama                                                                 |         |
| 2:50–3:00 | **PAUSA**                          |                                                                                                                             | —       |
| 3:00–3:30 | **Harnessing — Workflow Completo** | →                                                                                                                           | MEDIO   |
|           | 3:00–3:05                          | [Spec-driven dev](docs/02-harnessing.md) · context engineering layers                                                       |         |
|           | 3:05–3:20                          | Ciclo completo `/implementation`→`/pre-commit`→`/ship`→`/release`                                                           |         |
|           | 3:20–3:23                          | [Reflection loop](docs/02-harnessing.md) · quality gates non bypassabili                                                    |         |
|           | 3:23–3:28                          | [Ralph Loop · `/loop` nativo](docs/02-harnessing.md)                                                                        |         |
|           | 3:28–3:30                          | Pattern avanzati: worktrees · headless                                                                                      |         |
| 3:30–3:35 | **PAUSA**                          |                                                                                                                             | —       |
| 3:35–4:00 | **Pattern Esterni**                | →                                                                                                                           | BASSO   |
|           | 3:35–3:40                          | [7 layer — architettura agentica](docs/07-external-patterns.md)                                                             |         |
|           | 3:40–3:50                          | GSD · BMAD · Superpowers — cosa risolvono                                                                                   |         |
|           | 3:50–3:58                          | [Il nostro SDLC vs framework](docs/07-external-patterns.md) · confronto diretto                                             |         |
|           | 3:58–4:00                          | Il ruolo che cambia — chiusura                                                                                              |         |

## Documentazione

| Doc                                                            | Argomento                                                                     | Blocco      |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------- |
| [00 — Cos'è un Agent Harness](docs/00-cosa-e-un-harness.md)    | Definizione harness, 9 componenti, loop in azione, 7 decisioni architetturali | pre-reading |
| [01 — Anatomia Claude Code](docs/01-claude-code-anatomy.md)    | Skills, hooks, rules, agents, context rot                                     | B2          |
| [02 — Harnessing](docs/02-harnessing.md)                       | CLAUDE.md come contratto, spec-driven dev, reflection loop                    | B5          |
| [03 — Persistent Memory](docs/03-persistent-memory.md)         | Stop hook, memory recall, strategie context window                            | B3          |
| [04 — Codex in Parallelo](docs/04-codex-parallel.md)           | Architettura speculare Claude Code/Codex, multi-model review                  | B2          |
| [05 — Sandbox e Permissions](docs/05-sandbox-permissions.md)   | Permission modes, allow/deny rules, worktrees                                 | B2          |
| [06 — Modelli Alternativi](docs/06-alternative-models.md)      | MLX Studio, DeepSeek, OpenRouter, opusplan, OpenCode                          | B4          |
| [07 — SDLC vs Framework Esterni](docs/07-external-patterns.md) | GSD, BMAD, Superpowers, confronto 7 layer                                     | B6          |
| [08 — Supply Chain Defense](docs/08-supply-chain-defense.md)   | TeamPCP, Mini Shai-Hulud, livelli di difesa                                   | B1+B2       |
| [09 — Mappa Skill](docs/09-tool-tier-map.md)                   | Tier 1/2/3, reflection loop chain                                             | ref         |
| [10 — Come Scrivere CLAUDE.md](docs/10-claudemd-agents.md)     | Architettura a layer, template, enforcement                                   | bonus       |
| [11 — Prompt Engineering](docs/11-prompt-engineering.md)       | 10 layer, mapping CLAUDE.md, anti-pattern                                     | bonus       |

## Risorse

[Reading list](docs/resources/reading_list.md) · [Diagrammi](public/) · [Demo script](docs/demos/live-build-script.md)
