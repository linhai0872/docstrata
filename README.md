<p align="center">
  <img src="docstrata-logo.svg" alt="docstrata" width="480">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" alt="License"></a>
  <img src="https://img.shields.io/badge/Agent_Skills-compatible-blue" alt="Agent Skills">
  <img src="https://img.shields.io/badge/Claude_Code-skill-orange" alt="Claude Code">
</p>

<p align="center">
  <a href="README_EN.md">English</a> | 中文
</p>

按四层知识结构，为任意项目生成和维护文档。Agent Skill，兼容 Claude Code、Cursor 等主流工具。

---

## 问题的起点

作为一名软件工程师，同时维护多个形态各异的项目——全栈服务、Dify 应用、MCP 工具、Skill。每个项目的文档实际上服务三类使用者：开发者自身、团队的业务与管理侧、以及 coding agent。三者对文档的形式和侧重需求各不相同，却往往被混在同一份 README 里处理，或根本没有对应的地方存放：

| 问题 | docstrata 的解法 |
|---|---|
| 技术文档面向开发者，业务侧缺少可读的系统全景 | **wiki** — 生成面向所有人的业务全景文档 |
| 需求意图散落各处，设计决策缺乏系统留痕 | **requirements** — 固化需求共识与开发决策 |
| 领域材料分散，缺乏统一整理与检索 | **knowledge** — 整理原始材料为可检索索引 |
| 实践经验缺乏沉淀，新成员或 coding agent 难以获取 | **dev + INDEX.md** — 记录推断与结论，提供四层统一检索入口 |
| 文档依赖人工维护，随项目迭代容易失真或过期 | 自动探索项目上下文，仅在信息有缺口时提问；增量更新，保留人工修改 |

根源都是同一个：这四类知识的性质截然不同，现有工具大多只覆盖其中一层，混在一起写才是问题的来源。

这个分层在文献里有迹可循。

[CoALA](https://arxiv.org/abs/2309.02427)（Sumers et al., Princeton/CMU, TMLR 2024）研究 AI agent 的记忆架构，把长期记忆分成三类，和四层文档一一对应：

| CoALA 长期记忆 | 对应层 | 本质 |
|---|---|---|
| Episodic | requirements | 事件与决策的留痕 |
| Semantic | wiki · knowledge | 领域知识 |
| Procedural | dev | 操作经验 |

`INDEX.md` 是四层的检索入口，服务于 coding agent 的 working memory 装填，本身不是那一层。

[Diátaxis](https://diataxis.fr) 把文档分成四个象限（tutorial / how-to / reference / explanation），Ubuntu、NumPy、Django 都在用。这里只借了它"固定骨架 + 自由内容"的结构经验；四层的分类逻辑来自 CoALA，不照搬象限。

docstrata 把这套分层做成了一个 Skill，四个子命令，每个生成一层。

---

## 它怎么运作

每层的生成走同一个五步循环：

| 步骤 | 做什么 |
|---|---|
| **EXPLORE** | 读项目多源信息——代码结构、现有文档、git 历史、开发日志 |
| **MAP** | 把信息映射到每层的信息维度，标置信度（high / medium / low / missing） |
| **GRILL** | 只对 `low` / `missing` 维度提问；一次一个，附推荐答案，代码能回答的不问人 |
| **GENERATE** | 按固定骨架生成，已有文档则增量更新，保留人工修改 |
| **STAMP** | 更新 `last-verified` 时间戳，输出信息健康诊断 |

GRILL 的核心逻辑：每层预先声明一份信息维度集合（completeness contract），问什么由缺口决定——

```
问题 = 契约维度 − 已探索到的信息
```

有完整需求文档和开发日志的项目，GRILL 往往整层跳过。提问模式来自 [grill-with-docs](https://github.com/mattpocock/skills)（Matt Pocock）。

生成时内建信息批判，处理多源信息的质量问题：

- **来源排序**：运行代码 > 测试 > git 历史 > 文档；多源矛盾不静默选一个
- **认知标注**：事实与推断分开标——`[事实]` / `[推断]` / `[待确认]`
- **LLM 偏向**：遇到非标实现，记录项目实际行为，不"纠正"成标准做法

参考：NATO Admiralty Code 来源分级 · [LLM 知识冲突研究](https://arxiv.org/abs/2504.13079)

生成的文件固定放在 `docs/` 目录，随 git 提交：

```
docs/
├── wiki.md
├── requirements.md
├── knowledge/
│   ├── knowledge.md      # 整理后的索引
│   └── raw/              # 原始材料（不改动）
├── dev.md
└── INDEX.md              # coding agent 的四层检索入口
```

---

## 安装

```bash
npx skills add linhai0872/docstrata
```

兼容 Claude Code、Cursor、Gemini CLI、Codex、OpenCode 等支持 [Agent Skills 标准](https://agentskills.io) 的工具。

---

## 使用

在目标项目里调用：

```
/doc wiki            # 业务全景 → docs/wiki.md
/doc requirements    # 需求共识 → docs/requirements.md
/doc knowledge       # 业务材料索引 → docs/knowledge/knowledge.md
/doc dev             # 开发结论 → docs/dev.md
/doc index           # coding agent 检索入口 → docs/INDEX.md
/doc all             # 按依赖顺序全部生成
```

支持任意项目类型，工具自行判断，无需声明。`/doc all` 会跳过无实质价值的层，不强制生成空壳——没有业务材料就跳过 knowledge，功能一目了然的小项目 requirements 也可以不单独成文。

---

## 设计文档

本项目的文档用自身的四层结构写成：

| 文档 | 内容 |
|------|------|
| [需求共识与设计决策 D1–D12](docs/requirements.md) | 全部架构决策，含 CoALA 理论映射 |
| [业务全景](docs/wiki.md) | 一页读懂 docstrata |
| [开发推断与实践结论](docs/dev.md) | 实测迭代记录、被否定的方案 |
| [Completeness Contract 方法论](skill/doc/references/methodology.md) | GRILL 机制的第一性原理 |
| [信息批判准则](skill/doc/references/source-criticism.md) | 来源排序、矛盾处理、事实/推断标注 |
