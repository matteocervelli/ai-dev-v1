# Difesa Supply Chain — TeamPCP, Mini Shai-Hulud e Contromisure

> **Key message:** Gli attaccanti non aspettano il codice in produzione. Attaccano nel momento in cui installi le dipendenze — sul tuo laptop, nel CI, nell'agent workspace quando un LLM esegue `pip install` troppo in fretta.

## TeamPCP — Chi È e Come Funziona

**TeamPCP** è il nome assegnato da Datadog a un threat actor persistente che esegue attacchi coordinati alla supply chain del software, documentato a partire dal 2024. Non è una singola campagna: è un'operazione continuativa che cambia bersaglio e scala.

**Caratteristiche distintive:**

- **Multi-ecosistema e simultaneo**: PyPI, npm, Docker Hub, GitHub Actions vengono colpiti insieme
- **Non compromette il sorgente**: prende il controllo del *canale di distribuzione* — CI, token, registry auth
- **Scala per test e poi per danno**: attacchi preliminari più piccoli affinano la tecnica prima degli attacchi principali
- **Conosce il workflow degli sviluppatori**: sfrutta la fiducia implicita in pacchetti known-good e CI trusted

La campagna ha avuto diverse operazioni nel 2024-2025 prima di scalare nel 2026. Il **29 aprile 2026** è arrivato l'attacco SAP/BUN — stesso pattern, stessa infrastruttura, scala minore. Era un test. L'11 maggio ha scalato su PyPI e npm contemporaneamente.

**Il principio fondamentale di TeamPCP**: non basta verificare il codice sorgente. L'attaccante non modifica il sorgente — modifica ciò che viene _distribuito_.

## Mini Shai-Hulud — L'Operazione dell'11 Maggio 2026

**Mini Shai-Hulud** è il nome dell'operazione del maggio 2026 contro l'ecosistema AI/ML Python. Due pacchetti trusted compromessi:

| Pacchetto | Versione malevola | Comportamento all'import |
|-----------|------------------|--------------------------|
| `mistralai` | `2.4.6` | Esfiltra credenziali verso server C2 |
| `guardrails-ai` | `0.10.1` | Esegue codice arbitrario remoto |

**Come funziona tecnicamente:** entrambe le versioni usano gli **import hook** di Python. All'esecuzione di `import mistralai`, prima di restituire il modulo, il codice malevolo si attiva silenziosamente: legge variabili d'ambiente (API key, token CI/CD, credenziali), le cifra e le invia a un endpoint remoto. Il pacchetto poi funziona normalmente — nessun segnale visibile.

> **[demo]** show the import hook mechanism — what happens in the live session

> **[fonte]** [New Era of Supply Chain Attacks: Python Developers Hacked](https://www.encryptionconsulting.com/the-new-era-of-supply-chain-attacks-python-developers-hacked-in-sophisticated-supply-chain-attack/) — Approfondisce il meccanismo tecnico degli import hook e del typosquatting usati da TeamPCP: il caso Colorama mostra esattamente come un pacchetto trusted viene compromesso per esfiltrare credenziali, stesso pattern di Mini Shai-Hulud.

```
2026-04-29  Attacco SAP/BUN — test dell'infrastruttura, scala minore
2026-05-11 mattina     Versioni malevole pubblicate su PyPI/npm
2026-05-11 pomeriggio  Prime segnalazioni Datadog/community
2026-05-11 sera        Quarantena PyPI
2026-05-12             Constraint-dependencies aggiunte a questo repo
```

La finestra di esposizione: **ore**. Chi ha eseguito `uv sync` in quel periodo senza protezione ha potenzialmente eseguito il codice malevolo.

### La catena TanStack (npm, stesso periodo)

In parallelo, sulla stessa infrastruttura TeamPCP:

- **42 pacchetti** `@tanstack/*` compromessi, **84 versioni malevole** pubblicate
- Vettore: GitHub Actions → cache poisoning → estrazione token OIDC dalla memoria del runner
- Ogni token rubato permetteva publish npm con le credenziali legittime del maintainer — il prossimo rilascio del maintainer reale diventava vettore per l'utente successivo

## Il Vettore LLM — Perché gli Agenti Sono il Target Ideale

Un agente LLM esegue `pip install` o `uv add` senza i freni cognitivi di uno sviluppatore esperto.

| Scenario | Sviluppatore | Agente LLM |
|----------|-------------|------------|
| Velocità di install | 1 comando alla volta | Decine in secondi |
| Verifica manuale | Spesso | Mai |
| Log visibili | Sì | Solo se configurati |
| Blast radius | Macchina locale | Macchina + CI + credenziali nel context |

Un agente che lavora su codice ha nel context API key, token di deploy, path di configurazione. Se installa un pacchetto malevolo, tutto questo è esposto — non solo la macchina locale.

> **[fonte]** [Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — Approfondisce la superficie di attacco specifica degli agenti LLM: le descrizioni dei tool sono un vettore di prompt injection, rilevante per capire perché un agente che esegue `pip install` senza hook è più esposto di un developer umano.

## Come lo Vediamo in Questo Repo

```toml
# pyproject.toml
[tool.uv]
constraint-dependencies = [
  "mistralai!=2.4.6",       # Mini Shai-Hulud 2026-05-11: esfiltra credenziali all'import
  "guardrails-ai!=0.10.1",  # Mini Shai-Hulud 2026-05-11: esegue codice remoto all'import
  "urllib3>=2.7.0",          # GHSA-mf9v-mfxr-j63j + GHSA-qccp-gfcp-xxvc: fix in 2.7.0
]
```

L'operatore `!=` esclude la versione specifica dalla risoluzione — anche se una dipendenza transitiva la richiedesse, `uv` rifiuta. Zero runtime overhead, contratto dichiarativo.

> **[demo]** show the `pyproject.toml` exclusions — `mistralai!=2.4.6`, `guardrails-ai!=0.10.1`, and the comments explaining each pin

## Livelli di Difesa

| Layer | Strumento | Cosa blocca | Quando agisce |
|-------|-----------|-------------|---------------|
| 1 | **Socket Firewall (`sfw`)** | Pacchetti malevoli noti, publish sospetti | Prima del download |
| 2 | **`constraint-dependencies`** | Versioni specifiche quarantinate | Alla risoluzione uv/pip |
| 3 | **Lockfile pinning** (`uv.lock`) | Deriva non autorizzata | Ad ogni sync |
| 4 | **Hook PreToolUse** | Agenti che eseguono `pip install` raw | Prima dell'esecuzione |
| 5 | **`/supply-chain-audit`** | Dipendenze transitive, pattern IOC | Periodicamente |
| 6 | **`/deps`** | Freshness + CVE attivi | Su richiesta |

**Layer 1 — Socket Firewall:** `sfw` wrappa il package manager. Un normale `pip install requests` diventa una richiesta verificata in tempo reale contro il database Socket prima del download. Se Socket rileva un pacchetto compromesso, blocca prima che arrivi in locale.

**Layer 4 — Hook PreToolUse:** il blocco è in codice Python con `exit 2`, non in un suggerimento nel prompt. Un agente che tenta `pip install foo` senza `sfw` riceve PermissionDenied — non può ignorarlo.

> **[demo]** show the `supply-chain-guard.py` hook — the `exit 2` pattern that blocks raw `pip install` calls from agents

> **[fonte]** [Less is safer: how Obsidian reduces supply chain risk](https://obsidian.md/blog/less-is-safer/) — Blueprint per la filosofia di difesa strutturale adottata in questo repo: reimplementare le utility piccole, fare version-locking delle grandi, disabilitare i postinstall scripts — la contromisura al problema di superficie prima ancora che arrivino gli attacchi.

## Regole per gli Agenti LLM

Prima di aggiungere una dipendenza:

1. Verificare che non sia già nel progetto
2. Controllare `constraint-dependencies` per versioni note malevole
3. Età del pacchetto — pubblicato < 7 giorni = alert
4. Usare il wrapper `sfw`, non il binario diretto

Dopo l'installazione: verificare il diff del `uv.lock` — solo le dipendenze attese devono essere cambiate.

> **[fonte]** [Building agents with the Claude Agent SDK](https://claude.com/blog/building-agents-with-the-claude-agent-sdk) — Approfondisce i trust boundary nei sistemi agentici — il modello di isolamento del context tra subagent che riduce il blast radius se un pacchetto malevolo viene eseguito in un workspace condiviso.
