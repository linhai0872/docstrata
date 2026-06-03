<p align="center">
  <img src="docstrata-logo.svg" alt="docstrata" width="480">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" alt="License"></a>
  <img src="https://img.shields.io/badge/Agent_Skills-compatible-blue" alt="Agent Skills">
  <img src="https://img.shields.io/badge/Claude_Code-skill-orange" alt="Claude Code">
</p>

<p align="center">
  <a href="README.md">中文</a> | English
</p>

Generate and maintain layered project documentation across four knowledge layers. An Agent Skill, compatible with Claude Code, Cursor, and other major tools.

---

## The Problem

As a software engineer maintaining several projects of different types in parallel — full-stack services, Dify applications, MCP tools, Skills — documentation for each project serves three distinct audiences: the developer, the business and management team, and coding agents. These three have fundamentally different documentation needs, yet they're often squeezed into a single README, or left without any dedicated place:

| Problem | docstrata's Solution |
|---|---|
| Technical docs are developer-facing; business stakeholders lack a readable system overview | **wiki** — generates a system overview accessible to everyone |
| Requirements intent is scattered; design decisions lack systematic record | **requirements** — codifies consensus and decision history |
| Domain materials are dispersed, with no unified reference or searchability | **knowledge** — organizes raw materials into a searchable index |
| Practical lessons go unrecorded; new members or coding agents can't access them | **dev + INDEX.md** — captures inferences and conclusions, provides a unified retrieval entry |
| Documentation depends on manual upkeep, prone to drift or becoming outdated | Auto-explores project context; asks only when information is genuinely missing; incremental updates preserve manual edits |

The root cause is the same in every case: these four knowledge types have fundamentally different natures, and existing tools typically address only one of them. Mixing them together is where the problem starts.

This layering has roots in the research literature.

[CoALA](https://arxiv.org/abs/2309.02427) (Sumers et al., Princeton/CMU, TMLR 2024) studies AI agent memory architecture and divides long-term memory into three types, each mapping directly to a documentation layer:

| CoALA Long-term Memory | Layer | Nature |
|---|---|---|
| Episodic | requirements | Record of events and decisions |
| Semantic | wiki · knowledge | Domain knowledge |
| Procedural | dev | Operational experience |

`INDEX.md` serves as the retrieval entry for all four layers, feeding a coding agent's working memory — it is not itself a memory layer.

[Diátaxis](https://diataxis.fr) divides documentation into four quadrants (tutorial / how-to / reference / explanation), used by Ubuntu, NumPy, and Django. This project borrows its "fixed skeleton + free content" structural approach; the four-layer classification logic comes from CoALA, not Diátaxis's quadrants.

docstrata packages this layering as a single Skill with four subcommands, each generating one layer.

---

## How It Works

Every layer follows the same five-step cycle:

| Step | What It Does |
|---|---|
| **EXPLORE** | Reads multi-source project information — code structure, existing docs, git history, dev logs |
| **MAP** | Maps information to each layer's dimension set, assigning confidence levels (high / medium / low / missing) |
| **GRILL** | Questions only `low` / `missing` dimensions; one at a time, with a suggested answer; skips what code can answer |
| **GENERATE** | Generates content against a fixed skeleton; incrementally updates existing docs, preserving manual edits |
| **STAMP** | Updates the `last-verified` timestamp; outputs an information health report |

**GRILL's core logic**: each layer pre-declares a set of information dimensions (a completeness contract). What gets asked is determined by the gap:

```
Questions = Contract Dimensions − Already-Explored Information
```

Projects with complete requirements docs and dev logs often skip GRILL entirely. The questioning pattern is adapted from [grill-with-docs](https://github.com/mattpocock/skills) (Matt Pocock).

Built-in source criticism handles multi-source information quality:

- **Source ranking**: running code > tests > git history > docs; conflicts are never silently resolved
- **Epistemic annotation**: facts and inferences are labeled separately — `[fact]` / `[inference]` / `[unverified]`
- **LLM bias**: for non-standard implementations, records actual project behavior rather than "correcting" it to convention

References: NATO Admiralty Code source grading · [LLM Knowledge Conflict Research](https://arxiv.org/abs/2504.13079)

Generated files are stored in the `docs/` directory and committed with git:

```
docs/
├── wiki.md
├── requirements.md
├── knowledge/
│   ├── knowledge.md      # organized index
│   └── raw/              # raw materials (untouched)
├── dev.md
└── INDEX.md              # four-layer retrieval entry for coding agents
```

---

## Installation

```bash
npx skills add linhai0872/docstrata
```

Compatible with Claude Code, Cursor, Gemini CLI, Codex, OpenCode, and any tool supporting the [Agent Skills standard](https://agentskills.io).

---

## Usage

Run inside the target project:

```
/doc wiki            # system overview → docs/wiki.md
/doc requirements    # requirements consensus → docs/requirements.md
/doc knowledge       # domain materials index → docs/knowledge/knowledge.md
/doc dev             # development conclusions → docs/dev.md
/doc index           # coding agent retrieval entry → docs/INDEX.md
/doc all             # generate all layers in dependency order
```

Works with any project type — full-stack apps, Dify workflows, CLI/MCP services, Skills, plain document directories. The tool determines the type automatically; no declaration needed.

`/doc all` skips layers without meaningful content rather than generating empty shells — `knowledge` is skipped if there are no domain materials; `requirements` may be folded into `wiki` for small, self-evident projects.

---

## Design Docs

This project's documentation is written using its own four-layer structure:

| Document | Content |
|------|------|
| [Requirements & Design Decisions D1–D12](docs/requirements.md) | Full architectural decisions, including CoALA theory mapping |
| [System Overview](docs/wiki.md) | docstrata in one page |
| [Development Inferences & Conclusions](docs/dev.md) | Iteration notes, rejected approaches |
| [Completeness Contract Methodology](skill/doc/references/methodology.md) | First principles of the GRILL mechanism |
| [Source Criticism Guidelines](skill/doc/references/source-criticism.md) | Source ranking, conflict handling, fact/inference annotation |
