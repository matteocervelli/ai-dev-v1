# Reading List — AI-Driven Development

Fonti organizzate per topic. Le fonti con ★ sono prioritarie per chi ha poco tempo.

## Fonti Primarie Anthropic

Tre articoli pubblicati il 29 settembre 2025 che aggiornano le best practice per chi costruisce con Claude.

- ★ **[A1]** [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  "Right altitude" per system prompt: evita prompts hardcoded brittle e prompts troppo vaghi. Agentic systems, overeagerness prevention, hallucination minimization.

- ★ **[A2]** [Building agents with the Claude Agent SDK](https://claude.com/blog/building-agents-with-the-claude-agent-sdk)
  Loop agente: **gather context → take action → verify work**. Subagents per parallelizzazione e context isolation. Compaction per sessioni lunghe. Tre modi di verifica: rules-based, visual feedback, LLM-as-judge.

- ★ **[A3]** [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  Context engineering vs prompt engineering. Context rot: n² relazioni tra token → attenzione si diluisce. Just-in-time retrieval, progressive disclosure, compaction, NOTES.md, sub-agent architecture.

- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — Anthropic: patterns workflow (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer). "Start simple with LLM APIs directly."

- [How AI Is Transforming Work at Anthropic](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) — Studio interno: 132 engineer, Claude Code gestisce ~20 azioni autonome prima di chiedere input. Shift da debugging a feature implementation (14% → 37%).

## Tool Design & MCP

- ★ [Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — Anthropic: prototipazione, eval, iterazione con Claude Code. Namespacing, token efficiency, prompt-engineering delle descrizioni tool.
- [MCP Deep Dive — Future of AI Tooling](https://a16z.com/a-deep-dive-into-mcp-and-the-future-of-ai-tooling/) — a16z: standard aperto, marketplace, agentic workflow

## Prompt Engineering

- ★ [Prompt Engineering](https://readwise-assets.s3.amazonaws.com/media/wisereads/articles/prompt-engineering/22365_3_Prompt-Engineering_v7-1.pdf) — Google whitepaper (Lee Boonstra): zero-shot, few-shot, chain of thought, temperature, top-P
- [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) — Lilian Weng (OpenAI): architettura tri-componente (Planning, Memory, Tool Use). AutoGPT, GPT-Engineer, BabyAGI. Riferimento fondamentale.

## Memory & Harnessing

- ★ [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Anthropic: initializer + coding agent, claude-progress.txt, feature_list.json, git-based recovery. Due failure mode da evitare: one-shot attempt, premature victory.
- ★ [Karpathy LLM Wiki (gist)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — pattern raw/ → wiki/ senza vector DB. Tre layer: raw (immutabile), wiki (LLM-owned), schema (CLAUDE.md). Ingest, query, health check.
- [karpathy/autoresearch](https://github.com/karpathy/autoresearch) — Ralph Loop: AI agenti su ML research in loop autonomo (~12 esperimenti/ora). program.md come "research org code" controllato dall'umano.
- [My LLM codegen workflow atm](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/) — Harper Lee: tre fasi (brainstorm spec → plan a plan → execute). Loop discreti tra fasi. Approccio sia greenfield che legacy.

## Claude Code Architecture

- **Nick Spisak — "Claude Code Source Leaked — Here's what you can use today"** (maggio 2026)
  Analisi del source map trapelato (512K righe TypeScript, 1900 file). 4 tier context management: Snip, Micro, Full, Reactive Collapse. Cerca il post su X/@NickSpisak\_.

- ★ [2025 LLM Year in Review](https://karpathy.bearblog.dev/year-in-review-2025/) — Karpathy: 6 paradigm shift dell'anno (RLVR/DeepSeek R1, jagged intelligence, Cursor, Claude Code, vibe coding, agent infrastructure). Sezione Claude Code: "localhost over cloud", autonomy slider, LLM come OS.

## Supply Chain Security

- ★ [New Era of Supply Chain Attacks: Python Developers Hacked](https://www.encryptionconsulting.com/the-new-era-of-supply-chain-attacks-python-developers-hacked-in-sophisticated-supply-chain-attack/) — Caso Colorama (150M+ download): typosquatting, malware nascosto in whitespace, furto cookie GitHub. 62% intrusioni di sistema via supply chain (Verizon report).
- [Less is safer: how Obsidian reduces supply chain risk](https://obsidian.md/blog/less-is-safer/) — Filosofia dipendenze di Obsidian: reimplementare utility piccole, forkare moduli medi, version-locking grandi librerie, disabilitare postinstall scripts. Blueprint per qualsiasi progetto.

## Agenti Autonomi — Architettura e Pattern

- ★ [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) — Lilian Weng: Tre componenti (Planning, Memory, Tool Use). Sezione Memory: short-term vs long-term, vector stores, sensory/short-term/long-term analogy. Ancora il riferimento teorico più completo.
- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — Anthropic: workflows vs agents (predefined vs model-driven), quando usare frameworks vs raw API. "Incorrect assumptions about what's under the hood are a common source of customer error."

## Produttività e Impatto

- ★ [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developers](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) — METR: RCT con 16 developer esperti. AI ha causato il **19% di rallentamento** nonostante i developer pensassero di essere 20% più veloci. Dati critici per decision-making in produzione.
- [Lean and AI?](https://www.lean.org/the-lean-post/articles/lean-and-ai/) — Lean.org: 400+ ore di AI coding. Context window ~10-15 minuti effettivi. Demo-to-reliable-production cost è esponenziale. "AI amplifica il bisogno di lean problem-solving, non lo sostituisce."
- [AI-assisted Coding for Teams That Can't Get Away With Vibes](https://blog.nilenso.com/blog/2025/05/29/ai-assisted-coding/) — Nilenso: AI come moltiplicatore (engineer esperti estraggono di più). Metaprompting: chiedi al modello di far emergere i tradeoff, poi passa la spec a un agente. RULES.md, test coverage, ADR come prerequisiti.

## Vibe Coding & Software 3.0

- ★ [Andrej Karpathy: Software Is Changing (Again)](https://www.youtube.com/watch?v=LCEmiRjPEtQ) — YC AI Startup School keynote: Software 1.0/2.0/3.0, LLM come OS, vibe coding, autonomy slider, "siamo negli anni '60 degli LLM." 38 min.
- [2025 LLM Year in Review](https://karpathy.bearblog.dev/year-in-review-2025/) — (vedi Claude Code Architecture) — anche sezione open source: "Llama = Linux", RLVR e DeepSeek R1 come moment-shift per l'open source.
