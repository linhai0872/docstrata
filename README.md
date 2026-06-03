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

为任意项目生成四层分层知识文档——让你的团队、业务人员和 coding agent 都能快速理解一个项目。

---

## 为什么需要分层

文档腐烂的根因不是懒，是**知识性质不同却混写在一起**。

四种知识有完全不同的受众、更新频率和可信度标准，硬塞进一个 README 必然一团混乱：

<table>
<tr><td><b>wiki</b></td><td>系统是什么、能做什么，任何人都能读懂</td></tr>
<tr><td><b>requirements</b></td><td>需求意图和开发决策的留痕，需求方与开发者的共识约定</td></tr>
<tr><td><b>knowledge</b></td><td>业务规则、领域材料的索引，做这件事必须了解的背景</td></tr>
<tr><td><b>dev</b></td><td>实现过程中得出的实践结论——踩坑、被否定的方案、推断边界</td></tr>
</table>

分层之后，每种知识找到对的受众，更新时知道改哪里，agent 读到的是可信的信息而不是过期文档。

---

## 它怎么运作

```
输入：任意项目目录（代码 / Dify DSL / MCP 服务 / Skill / 文档集合……）
          │
          ▼
┌─────────────────────────────────────────────────────┐
│                   执行循环（每层）                    │
│                                                     │
│  EXPLORE ──► MAP ──► GRILL ──► GENERATE ──► STAMP   │
│    读项目      评估      缺口时      按固定       留痕  │
│    多源信息    信息      向人提问    骨架生成     时间戳 │
│              完整度     一次一个    增量更新      +诊断 │
│                │                                    │
│         source-criticism                            │
│  （来源可信度排序 · 矛盾检测 · 事实/推断标注）         │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│               四层产出 + 检索入口                    │
│                                                     │
│  requirements ──► knowledge ──► wiki ──► dev        │
│  (Episodic)      (Semantic)   (Semantic) (Procedural)│
│                                          │          │
│                                    INDEX.md         │
│                              （coding agent 入口）   │
└─────────────────────────────────────────────────────┘
          │
          ▼
    信息健康诊断（副产物）
    冲突 · 过期 · 版本漂移 · 缺口 · 孤儿文档
```

**GRILL** 是结对交互机制，来自 [grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs)（Matt Pocock）的改造：agent 先自动探索项目上下文，只在发现信息缺口时才向你提问，一次一个，附推荐答案。信息充分时整层跳过提问。

---

## 理论基础

**知识分层**基于 [CoALA](https://arxiv.org/abs/2309.02427)（Sumers et al., Princeton/CMU, TMLR 2024）——将 AI agent 的持久知识分为 Episodic / Semantic / Procedural 三类长期记忆，四层文档直接对应这个分类。

**文档结构**借鉴 [Diátaxis](https://diataxis.fr)（Ubuntu、NumPy、GNOME 等大规模采纳）——固定骨架 + 自由内容，被证明是最能长期维护的文档形态。

**信息批判**内建于生成过程：来源可信度排序（代码 > 注释 > 文档）、矛盾不静默选一个、事实与推断分开标注。理论来自 NATO Admiralty Code 来源分级、史学史料批判和 LLM 知识冲突研究（[arXiv:2504.13079](https://arxiv.org/abs/2504.13079)）。

**Skill 形态**遵循 [Anthropic Agent Skills 规范](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)——渐进式披露，核心指令轻量常驻，细节按需加载，跨平台可移植。

---

## 安装

```bash
npx skills add linhai0872/docstrata
```

兼容 Claude Code、Cursor、Gemini CLI、Codex、OpenCode 等支持 [Agent Skills 标准](https://agentskills.io)的工具。

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

支持任意项目类型——全栈服务、Dify DSL、MCP 服务、Skill、纯文档目录，工具自动判断，无需声明。每次生成后附带信息健康诊断，报告跨源冲突、过期文档和版本漂移。

---

## 设计文档

本项目用自身的四层结构写成（dogfooding）：

| 文档 | 内容 |
|------|------|
| [需求共识与设计决策 D1–D12](docs/requirements.md) | 全部架构决策，含 CoALA 理论映射 |
| [业务全景](docs/wiki.md) | 一页读懂 docstrata |
| [开发推断与实践结论](docs/dev.md) | 实测迭代记录、被否定的方案 |
| [方法论：Completeness Contract](skill/doc/references/methodology.md) | GRILL 机制的第一性原理 |
| [信息批判准则](skill/doc/references/source-criticism.md) | 来源排序、矛盾处理、事实/推断标注 |
