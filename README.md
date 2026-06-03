<p align="center">
  <img src="assets/logo.svg" alt="docstrata" width="480">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" alt="License"></a>
  <img src="https://img.shields.io/badge/Agent_Skills-compatible-blue" alt="Agent Skills">
  <img src="https://img.shields.io/badge/Claude_Code-skill-orange" alt="Claude Code">
</p>

<p align="center">
  <a href="README_EN.md">English</a> | 中文
</p>

一个 Claude Code Skill，为项目生成分层的知识文档。

---

## 背景

手上有很多形态各异的项目——全栈服务、Dify DSL 应用、MCP 服务、Skill……每个项目都需要文档，但文档始终是一团乱：业务人员看不懂技术向的 README，需求意图散落在各处没人整理，开发踩过的坑没有留痕，coding agent 拿到的上下文一半过期了。

尝试用现有工具解决，发现它们大多只覆盖"技术参考文档"这一层。但项目里实际需要的知识有几种不同的性质，混在一起写是问题的来源：

<table>
<tr><td><b>wiki</b></td><td>系统是什么、能做什么，面向所有人</td></tr>
<tr><td><b>requirements</b></td><td>需求意图和开发决策的留痕，需求方与开发者的共识</td></tr>
<tr><td><b>knowledge</b></td><td>业务规则、领域材料，做这件事需要了解的背景</td></tr>
<tr><td><b>dev</b></td><td>实践过程中得出的结论——踩坑、被否定的方案、推断边界</td></tr>
</table>

这个分层思路来自 [CoALA](https://arxiv.org/abs/2309.02427)（Sumers et al., Princeton/CMU, TMLR 2024）对 AI agent 记忆结构的研究——Episodic / Semantic / Procedural 三类长期记忆，四层文档与之对应。文档结构参考了 [Diátaxis](https://diataxis.fr) 的骨架设计（Ubuntu、NumPy 等在用）。

docstrata 基于这套分层，做成了一个 Skill，为任意项目按需生成每一层的文档。

---

## 它怎么运作

每层文档的生成走同一个循环：

```
  EXPLORE ──► MAP ──► GRILL ──► GENERATE ──► STAMP
    读项目      评估      缺口时      按固定       留痕
    多源信息    信息      向人提问    骨架生成     时间戳
              完整度     一次一个    增量更新      +诊断
```

GRILL 的交互模式来自 [grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs)（Matt Pocock）：一次一个问题，附推荐答案，能从代码回答的不问人，信息充分时直接跳过。原版用于精炼领域语言；这里把它改造成信息补全机制，由「信息维度完整性契约」驱动，所有维度达标后自动进入生成阶段。

生成过程中内建信息批判——来源可信度排序（代码 > 注释 > 文档）、发现矛盾时不静默选一个、事实与推断分开标注。这部分参考了 NATO Admiralty Code 来源分级和 LLM 知识冲突研究（[arXiv:2504.13079](https://arxiv.org/abs/2504.13079)）。

四层产出结构：

```
  requirements ──► knowledge ──► wiki ──► dev
  (Episodic)      (Semantic)   (Semantic) (Procedural)
                                          │
                                    INDEX.md
                              （coding agent 检索入口）
```

每次生成后输出一份信息健康诊断，汇总在探索过程中发现的跨源冲突、过期文档、版本漂移和缺口。

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

支持任意项目类型，工具自动判断，无需声明。

---

## 设计文档

本项目用自身的四层结构写成：

| 文档 | 内容 |
|------|------|
| [需求共识与设计决策 D1–D12](docs/requirements.md) | 全部架构决策，含 CoALA 理论映射 |
| [业务全景](docs/wiki.md) | 一页读懂 docstrata |
| [开发推断与实践结论](docs/dev.md) | 实测迭代记录、被否定的方案 |
| [方法论：Completeness Contract](skill/doc/references/methodology.md) | GRILL 机制的第一性原理 |
| [信息批判准则](skill/doc/references/source-criticism.md) | 来源排序、矛盾处理、事实/推断标注 |
