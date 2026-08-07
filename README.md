<p align="center">
  <img src="docstrata-logo.svg" alt="docstrata" width="480">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" alt="License"></a>
  <img src="https://img.shields.io/badge/Agent_Skills-compatible-blue" alt="Agent Skills">
  <img src="https://img.shields.io/badge/Claude_Code-skill-orange" alt="Claude Code">
</p>

<p align="center">
  English | <a href="README_ZH.md">中文</a>
</p>

**docstrata** — Structured project memory for coding agents. Layered context that persists across sessions, so agents stop re-learning your project from scratch.

---

## The Problem

Code generation is fast now. The real bottleneck is context.

Every new agent session starts cold. The agent doesn't know why you chose architecture B over A, what you tried and rejected last month, or which module has a subtle constraint that breaks if you touch it wrong. You re-explain. It re-discovers. Old mistakes repeat.

Most developers manage context by hand — a `CONTEXT.md` here, some ADRs there, maybe a shared doc. It works until the project grows. Human memory fades with time and blurs with volume. Three weeks later you can't recall the reasoning; three months later you forgot the decision existed.

No dedicated tool existed for structured, layered project context management. Existing approaches were too lightweight — a single flat file can't capture the different *kinds* of knowledge a real project accumulates. So I built one.

---

## How docstrata Thinks About It

### Structured memory over manual notes

Project knowledge naturally splits by kind: product intent, historical decisions, domain knowledge, codebase structure, engineering lessons learned. Mixing them in one file makes everything harder to find — for you and for agents.

docstrata gives each kind its own layer, with a clear audience and purpose. The layered design draws from long-term memory classification in cognitive architecture research ([CoALA](https://arxiv.org/abs/2309.02427)): episodic memory (decisions, what happened), semantic memory (domain knowledge, codebase structure), procedural memory (engineering lessons, what works).

### Grill: the pair-programming lever

When docstrata generates a layer, it first explores everything it can find on its own — code structure, existing docs, configs, git history. Questions that can be answered by looking, it answers by looking.

Only the questions that require *your* judgment get asked. These are decisions: trade-offs, priorities, constraints only you know. The grill mechanism batches these into frontier rounds — each round surfaces all unlocked questions at once, typically done in 3–5 rounds. Small input from you, large output from the system.

### Simplicity

A useful tool shouldn't require learning a framework first. docstrata has layers because context naturally has layers. It has a grill because some knowledge lives only in your head. Beyond that, it stays out of your way.

---

## What docstrata Does

docstrata is the structured memory for your project. It covers context that humans need (product intent, business knowledge, historical decisions) and context that coding agents need (codebase structure, module relationships, engineering pitfalls) — in the same system.

```
prd → requirements → knowledge → [wiki, repo-wiki] → dev → index
                                    ↑ parallel, independent
```

| Layer | Output | Content | Audience |
|---|---|---|---|
| **prd** | `docs/prd.md` | Product intent: positioning, value, roadmap | Internal team |
| **requirements** | `docs/requirements.md` | Requirements consensus + key decisions | PM + developers |
| **knowledge** | `docs/knowledge/knowledge.md` | Domain materials index + Glossary | Everyone |
| **wiki** | `docs/wiki.md` | System overview (business language) | Everyone incl. business |
| **repo-wiki** | `docs/repo-wiki.md` | Codebase index: architecture/modules/stack/data flow | Coding agents + devs |
| **dev** | `docs/dev.md` | Engineering conclusions: pitfalls, rejected approaches, non-obvious decisions | Engineers + agents |
| **index** | `docs/INDEX.md` | Doc navigation + context triggers | Coding agents |

### Works with Matt Pocock's Skills

docstrata and [Matt Pocock's engineering skills](https://github.com/mattpocock/skills) are complementary. Matt's skills handle development methodology — TDD, code review, grilling for specs. docstrata handles what those skills assume exists: the project context that makes an agent effective. Use them together or independently.

A typical combined workflow:

```
Before:  agent reads repo-wiki + dev.md       → knows the codebase and past lessons
During:  /matt-grilling → /implement → /review → Matt skills handle execution
After:   /docstrata update                    → detects what changed, refreshes affected layers
```

docstrata bookends the development cycle: load context before coding, detect and sync changes after. Matt's skills handle everything in between. Periodically, `/docstrata compact` shrinks bloated layers back to bounded size.

---

## Installation

```bash
npx skills add linhai0872/docstrata
```

Compatible with [Agent Skills standard](https://agentskills.io): Claude Code, Cursor, Gemini CLI, Codex, OpenCode, etc.

---

## Usage

```
/docstrata prd             # product intent
/docstrata requirements    # requirements consensus
/docstrata knowledge       # domain materials index
/docstrata wiki            # system overview
/docstrata repo-wiki       # codebase index (architecture/modules/stack)
/docstrata dev             # development conclusions
/docstrata index           # doc navigation + context triggers
/docstrata compact         # shrink bloated layers
/docstrata update          # detect changes, refresh affected layers
/docstrata all             # generate all in dependency order
```

Works with any project type — auto-detected. `/docstrata all` skips layers without meaningful content.

---

## Design Docs

This project's documentation uses its own layered structure:

| Document | Content |
|------|------|
| [Product Intent](docs/prd.md) | Positioning, value principles, scope, roadmap |
| [Requirements & Decisions](docs/requirements.md) | All architectural decisions + CoALA mapping |
| [System Overview](docs/wiki.md) | docstrata in one page |
| [Development Conclusions](docs/dev.md) | Iteration notes, rejected approaches |
| [Methodology](skill/docstrata/references/methodology.md) | First principles of the GRILL mechanism |
| [Source Criticism](skill/docstrata/references/source-criticism.md) | Source ranking, conflict handling, annotations |
