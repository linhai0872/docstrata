# docstrata

> Project Context System：为任意项目管理分层认知资产，让 coding agent 带着正确 context 开发、把新认知沉淀回来。

last-verified: 2026-08-07

## 这是什么

docstrata 是一个 Agent Skill，定位**项目的结构化记忆系统**——管理和提供高杠杆 context，不指挥具体执行。与工程执行 skill（如 Matt Pocock skills）兼容协作，零重叠。

## 解决什么问题

coding agent 开发时的三个痛点：

1. **启动成本高**：每次新会话从零探索代码库，重复理解架构
2. **决策散落**：踩过的坑、否定的方案留在对话里，下次从头来
3. **context 污染**：不同性质的知识混在一起，agent 分不清什么是事实、什么是过期的推断

docstrata 用分层结构解决：正确的知识在正确的地方，agent 按需取用。

## 谁在用

用 coding agent 开发的团队和个人，尤其长周期项目。文档同时服务三类读者：业务侧读 wiki，开发者读 dev/requirements，coding agent 经 INDEX.md 按需检索。

## 核心功能

每个子命令产出一层文档。先自动探索项目，只在人类必须拍板时才提问（frontier grill），增量更新保留人工修改。

- **prd** — 产品意图：定位、价值、功能范围、roadmap
- **requirements** — 需求共识与关键决策
- **knowledge** — 业务原始材料的可检索索引 + 领域术语 Glossary
- **wiki** — 面向所有人的系统全景（业务语言）
- **repo-wiki** — 代码库索引：架构、模块关系、技术栈、数据流、API 表面积（技术语言，给 coding agent）
- **dev** — 工程结论：code+git 复原不出来的踩坑、被否方案、非显然决策
- **index** — 文档导航 + 各层触发条件（什么场景读哪层、新认知写到哪）
- **compact** — 收缩膨胀的层文档

## 关键概念

- **Context Triggers** — 定义各层的触发条件：什么场景该读哪层、新认知该写到哪里。写在 INDEX.md 里，按需而非强制。
- **Completeness Contract** — 每层声明的信息维度集合，驱动 GRILL：`问题 = 维度 − 已探索信息`。
- **Facts vs Decisions** — EXPLORE 阶段主动解决 agent 能查的事实缺口；GRILL 只问需要人类判断的决策。
- **Frontier Grill** — 每轮问出所有前置条件已满足的问题，3-5 轮完成全部提问。
- **CoALA 分层** — 文档分层的学术依据：Episodic / Semantic / Procedural 三类长期记忆。

## 如何运转（概览）

```
EXPLORE（穷尽自动探索 + 解决 facts）
    → MAP（映射到 completeness contract）
    → GRILL（只问 decisions，frontier 轮次）
    → GENERATE（固定骨架 + writing-for-agents 质量标准）
    → STAMP（时间戳）
```

repo-wiki 层的 EXPLORE 调用内置扫描脚本（无 LLM 消耗）自动提取代码结构，LLM 在 GENERATE 阶段补语义描述和架构图。

## 如何上手

```bash
npx skills add linhai0872/docstrata
```

在目标项目里跑 `/docstrata all` 或指定层。兼容 Claude Code、Cursor、Gemini CLI、Codex、OpenCode。

## 边界

- 不限定项目类型，工具自行判断
- 不指挥具体开发执行（那是 coding agent / 执行 skill 的事）
- knowledge 层只整理已有材料，不从代码逆推业务规则
- 不生成运行时动态 memory，不碰 AGENTS.md 的行为约束
- 与 Matt Pocock skills 兼容协作：docstrata 管 context，Matt skills 管执行纪律
