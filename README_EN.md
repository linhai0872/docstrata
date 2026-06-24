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

Generate and maintain layered project documentation organized by the nature of knowledge. An Agent Skill, compatible with Claude Code, Cursor, and other major tools.

---

## What It Does

- **Layered generation**: prd (product intent) / requirements (decisions) / knowledge (domain materials) / wiki (system overview) / dev (engineering conclusions)
- **Zero-config**: one command, tool explores the project itself, asks only when information is genuinely missing
- **Incremental updates**: diffs existing docs, preserves manual edits, never overwrites
- **Shrink to keep bounded**: compact pulls iteratively bloated layers back to a bounded, dense state so long-term memory doesn't rot
- **Broadly compatible**: Claude Code, Cursor, Gemini CLI, Codex, OpenCode, and any tool supporting the [Agent Skills standard](https://agentskills.io)

---

## Background

**Human–agent pair programming still delivers the highest overall throughput.** The role of tooling is to accelerate this loop: humans clarify requirements and make decisions, agents focus on execution — each doing what they do best. But every existing tool has gaps:

- **Spec frameworks** (speckit, BMAD, Superpower, etc.): bundle requirements analysis, task planning, and code generation into a fully automated pipeline. The frameworks themselves are heavy — high learning and onboarding cost. Large tasks run for half an hour and produce something nobody wanted; small tasks require so much boilerplate that the overhead outweighs the benefit.
- **Plan mode**: handles "how to execute this task" — session-scoped execution planning. Over-specifying constrains agent freedom, and decisions stay in the conversation; the next session starts from zero.
- **grill-with-docs** (Matt Pocock): stress-tests your plan against the existing domain model, sharpens terminology, records key decisions into CONTEXT.md and ADRs — persistent across sessions. But information management is scattered: no distinction of who reads what, or where different content belongs.

docstrata builds on grill-with-docs by managing information in typed layers, giving documents independent reading and retrieval value for both humans and agents. The framework does only what it should: clarify requirements, record decisions, leave the rest to the model.

### Why Layer?

A project's documentation serves three audiences: developers, business and management stakeholders, and coding agents. Their needs are fundamentally different, yet they typically end up in a single README — or have no dedicated home at all:

| Problem | docstrata's Solution |
|---|---|
| Product positioning/roadmap has no home; no basis for decisions | **prd** — internal product intent, disambiguates when grilling stalls |
| Technical docs are developer-facing; business stakeholders lack a readable system overview | **wiki** — a system overview everyone can read |
| Requirements intent is scattered; design decisions lack systematic record | **requirements** — codifies consensus and decision history |
| Domain materials are dispersed, with no unified reference or searchability | **knowledge** — organizes raw materials into a searchable index |
| Practical lessons go unrecorded; coding agents can't access them | **dev + INDEX.md** — captures inferences and conclusions, unified retrieval entry |
| Documentation depends on manual upkeep, prone to drift | Auto-explores project context; asks only when information is missing; incremental updates preserve manual edits |
| Long-term projects only ever grow, layers turn bloated | **compact** — manual shrink: condense first then split, archive without delete, hard facts kept verbatim |

These four knowledge types have different natures — mixing them causes contamination. A typical drift scenario: when requirements and dev are written together, a new agent session treats settled architectural decisions as open questions, re-runs the grill loop unnecessarily, and may reverse previous conclusions. Layering solves exactly this.

[CoALA](https://arxiv.org/abs/2309.02427) (Sumers et al., Princeton/CMU, TMLR 2024) studies AI agent long-term memory architecture and divides it into three types, providing theoretical grounding for the four-layer split:

| CoALA Long-term Memory | Layer | Nature |
|---|---|---|
| Episodic | requirements | Record of events and decisions |
| Semantic | wiki · knowledge | Domain knowledge |
| Procedural | dev | Operational experience |

The `prd` layer sits above these as forward-looking product intent (what to build) — not one of CoALA's three memory types, but a present-tense claim, distinct from the already-happened facts requirements records.

`INDEX.md` serves as the retrieval entry across layers, feeding a coding agent's working memory. It is not itself a memory layer.

### AGENTS.md vs. docstrata

AGENTS.md / CLAUDE.md are **behavior constraints**: they tell the agent how to work on every session, loaded in full every session, consuming context tokens every time.

docstrata produces **knowledge layers**: loaded on demand through INDEX.md — read the layer you need, don't pay for what you don't. The two are not alternatives — behavior constraints are still needed; docstrata handles knowledge accumulation outside of them. Cramming everything into AGENTS.md is hard to maintain and means every session pays a context cost for content it won't use.

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

Under long-term iteration layers bloat; `compact` shrinks them manually (condense first — drop what code/git can reconstruct, dedup, merge by topic; then split; archive without delete, hard facts kept verbatim) — a maintenance operation beyond generation.

Generated files are stored in the `docs/` directory and committed with git:

```
docs/
├── prd.md                # product intent (forward-looking, internal)
├── wiki.md
├── requirements.md
├── knowledge/
│   ├── knowledge.md      # organized index
│   └── raw/              # raw materials (untouched)
├── dev.md
└── INDEX.md              # retrieval entry for coding agents
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
/docstrata prd             # product intent → docs/prd.md
/docstrata requirements    # requirements consensus → docs/requirements.md
/docstrata knowledge       # domain materials index → docs/knowledge/knowledge.md
/docstrata wiki            # system overview → docs/wiki.md
/docstrata dev             # development conclusions → docs/dev.md
/docstrata index           # coding agent retrieval entry → docs/INDEX.md
/docstrata compact         # shrink a bloated layer (optional layer name, e.g. /docstrata compact dev)
/docstrata all             # generate all layers in dependency order
```

Works with any project type — full-stack apps, Dify workflows, CLI/MCP services, Skills, plain document directories. The tool determines the type automatically; no declaration needed.

`/docstrata all` skips layers without meaningful content rather than generating empty shells — `knowledge` is skipped if there are no domain materials; `requirements` may be folded into `wiki` for small, self-evident projects.

---

## Evaluation

After changing the skill, how do you know the doc quality actually improved? Gut feeling is easy to fool. `eval/` has an LLM read the generated docs and score them against a fixed rubric — run it before and after a change, compare scores, and you can see whether it's a real improvement or just noise.

Workflow: change a layer's generation spec → regenerate docs for test projects → score → compare with the previous run.

Three scoring tiers, pick what you need:

| Tier | Requires | Use |
|---|---|---|
| **Structure gate** | Nothing — pure Python | Checks for missing skeleton sections, instant, good for CI |
| **Single LLM score** | One API key | One LLM reads and scores the doc, use for daily iteration |
| **Multi-LLM vote** | Multiple API keys | Multiple LLMs score independently, median wins, use before releases |

Scoring criteria: does the doc cover the layer's core dimensions, are inferences correctly labeled, is the audience fit right, and more — 5 dimensions total, 0–3 each, normalized ≥ 0.7 to pass.

docstrata uses its own documentation as the test case — generate with the tool, score with eval. See [eval/README.md](eval/README.md) for full details.

---

## Design Docs

This project's documentation is written using its own layered structure:

| Document | Content |
|------|------|
| [Product Intent](docs/prd.md) | docstrata's own positioning, value principles, scope, and roadmap |
| [Requirements & Design Decisions](docs/requirements.md) | Full architectural decisions, including CoALA theory mapping |
| [System Overview](docs/wiki.md) | docstrata in one page |
| [Development Inferences & Conclusions](docs/dev.md) | Iteration notes, rejected approaches |
| [Completeness Contract Methodology](skill/docstrata/references/methodology.md) | First principles of the GRILL mechanism |
| [Source Criticism Guidelines](skill/docstrata/references/source-criticism.md) | Source ranking, conflict handling, fact/inference annotation |
| [Evaluation Loop](eval/README.md) | Developer tool for validating skill quality after changes (structure gate / single judge / ensemble) |
