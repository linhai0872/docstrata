# Requirements — docstrata

> 一个 Claude Code Skill，按四层知识结构为任意项目生成/维护文档。本文件是本项目自身的需求共识，由结对 grill 过程产出（Episodic 层：记录"约定了什么、为什么这样定"）。

last-verified: 2026-06-04

## Background

需求方有大量形态各异的项目（全栈服务、Dify DSL 应用、CLI/MCP 服务、Skill 形态等），需要一套 agent 时代的工具自动生成/维护文档。市面无单一工具能覆盖全部需求 `[推断]`（基于调研，未穷尽市场），但可用四个对应知识层的能力组合解决。

理论锚点：
- **CoALA**（Sumers et al., Princeton/CMU, TMLR 2024, arXiv:2309.02427）：Agent 记忆架构。三类**长期记忆**（Episodic / Semantic / Procedural）存持久知识；**Working Memory** 是"为当前决策周期维护活跃信息的中央枢纽"（原文：*central hub connecting different components*），知识从长期记忆被 retrieved into working memory 以支撑推理。它是运行时的临时中转，不是知识本身的存放处。
  - **我们的映射**：四层文档对应三类长期记忆（见下表）。Working Memory 是 agent 运行时的 context，**文档工具不生产它**；我们能做的是给它一个高效检索四层长期记忆的入口（`docs/INDEX.md`），优化 retrieval 路径，而非实现 working memory 本身。详见 D10。
- **Diátaxis**（diataxis.fr）：文档四象限（tutorial/how-to/reference/explanation），验证"固定骨架+自由内容"有效。
- **Anthropic Agent Skills**：渐进式披露三层加载（metadata → SKILL.md → references）。

## Goals

1. 为任意项目按需生成四层文档之一或全部。
2. 工具自动探索项目上下文，仅在信息有缺口时才向人类提问（grill）。
3. 把人类当作获取 context 的一种工具，而非每次都从头问。
4. 增量更新，保留人类手改内容。
5. 做成通用工具供团队使用，有价值则开源。

## Non-goals

- 不限定项目类型，工具自行判断，用户无需声明。
- Knowledge 层不从代码逆推业务规则（实用性存疑，明确不做）。
- 第一版不做平台 API 集成（Notion/Confluence 等），仅支持本地文件 + URL。
- 第一版不做文档发布/静态站导出（CLI 发布能力留待后续评估）。

## 四层定义与 CoALA 映射

四层文档全部对应 CoALA 的**长期记忆**（持久知识），不含 Working Memory（那是 agent 运行时 context，见理论锚点与 D10）。

| 子命令 | CoALA 长期记忆类型 | 本质 | 受众 | 内容来源 |
|---|---|---|---|---|
| `wiki` | Semantic | 系统全景，快速理解整个系统 | 所有人（含业务） | AI 生成，从代码/需求推导 |
| `requirements` | Episodic | 需求方与开发者的共识约定 + 开发计划（ADR 性质：责任与决策） | PM + 开发 | 部分原始需求 + 部分 AI 整理 |
| `knowledge` | Semantic | 业务专属原始材料库（规章制度、业务规则等 raw data） | 技术 + 业务 | **已有文档为主，AI 整理+索引** |
| `dev` | Procedural | 开发推断与实践结论（推断/实践事实，非原始事实） | 开发 + 维护者 | AI 生成，从代码+需求+知识推导 |

说明：wiki 与 knowledge 同属 Semantic 层但视角不同：wiki 是"系统能做什么"，knowledge 是"做这件事需要的业务背景知识"。

## 关键决策（ADR 性质）

### D1 — 一个 skill，四个子命令
四层共享同一套"探索→评估缺口→grill→生成"执行逻辑。拆四个 skill 会重复逻辑。用 SKILL.md 路由表分派，各层契约放 references/ 渐进加载。
- 命令：`/doc wiki | requirements | knowledge | dev | all`
- 支持显式指定单层，也支持 `all` 一键全生成。

### D2 — 层间有依赖顺序，但每层可独立触发
第一性原理上存在上下游（requirements → wiki/knowledge → dev）。允许跑某一层；上游层若存在则自动引用，不强制先跑上游。

### D3 — Grill 触发条件：缺口驱动
工具先自动探索上下文（读文件/现有文档/代码），把信息映射到每层的 **completeness contract**（信息维度），仅对缺失/低置信维度动态提问。信息够则跳过 grill 直接生成。一次问一个问题，附 AI 推荐答案（grill-with-docs 风格）。

### D4 — Grill 方法论：动态提问，不用固定清单
每层声明一份 completeness contract（稳定的信息维度），具体问什么由"契约维度 − 已探索信息 = 缺口"临场算出。场景灵活，契约稳定。

各层 completeness contract：
- **Wiki**：系统存在的理由 · 目标用户 · 核心能力边界 · 关键概念 · 如何上手
- **Requirements**：原始需求意图 · 共识约定 · 开发计划 · 关键取舍
- **Knowledge**：原始材料来源 · 业务规则提炼 · 分类索引
- **Dev**：需求→实现的推导链 · 实践得出的事实 · 已验证/已否定的方案

### D5 — 输入是路径，工具自判项目类型
输入一个目录（代码仓库或文档目录均可）。对工具而言都是文件树，探索策略相同，用户无需声明类型。

### D6 — 文档存项目内，约定固定结构
```
docs/
├── wiki.md
├── requirements.md
├── knowledge/
│   ├── knowledge.md      # 整理后的索引（导读层）
│   ├── raw/              # 本地原始文档（不改动）
│   └── sources.yaml      # 外部 URL 列表
└── dev.md
```
随 git 提交。需要分发到别处由用户自行复制。

### D7 — 增量更新，保留手改
再次触发已存在的层：diff 现有文档与当前上下文，只重写有实质变化的段落，文末记录更新时间与变更摘要。不全量重写。

### D8 — 固定骨架 + 自由内容
每层有约定 section 标题（增量更新的锚点 + 跨项目一致性），section 内容由 AI 按上下文生成，不是填表。

### D9 — Knowledge 层只整理不生成
用户把原始材料放 `docs/knowledge/raw/`（任意格式）或在 `sources.yaml` 列 URL。工具扫描后生成结构化 `knowledge.md`：每份材料的摘要、关键规则提炼、标签分类、原文件链接。原始文件不动。其他层引用 knowledge.md 摘要，无需重读原始 PDF。

### D10 — 信息批判方法论统一处理信息质量问题
来源可信度、矛盾、过期、缺失、事实vs推断混淆，本质都是信息质量问题，统一由 `references/source-criticism.md` 四准则处理（来源可信度排序、矛盾处理、认知状态标注、打破 LLM 先验偏向），而非逐个打补丁。理论来源经实测精简，砍掉过度设计（完整 ACH、Admiralty 双轴打分、Wang&Strong 全维、W3C PROV）。EXPLORE/MAP/GENERATE 三步引用它。

### D11 — INDEX.md 是长期记忆的检索入口，非 Working Memory 层
`docs/INDEX.md` 是给 coding agent 的四层文档导航索引（轻量指针，指向各层，不复制内容）。

定位澄清（基于 CoALA 原文核查）：CoALA 的 Working Memory 是 agent **运行时**的活跃 context 中央枢纽，文档工具不生产它。INDEX.md 只是优化 agent 检索四层**长期记忆**的入口，服务于 working memory 的装填，本身不是那一层。

边界（明确不做）：运行时动态 memory（对话提炼的踩坑/经验，如 Anthropic memory tool、Mem0、Qoder 的"记忆"）由 agent 运行时自己写，不由本工具生成：避免功能越界。

与 AGENTS.md 的关系：AGENTS.md（事实标准，AAIF 治理）是"怎么干活"的操作契约（命令、约定、红线），定位是精简（实证 ≤150 行，过长反降低 agent 成功率，arXiv:2602.11988）。INDEX.md 是"知识在哪"的导航，两者信息类型不同，不混写。

### D12 — audit 是生成流程的诊断副产物，非独立命令
生成过程中 source-criticism 本就会发现跨 context（代码/git/文档/规范文件）的冲突、过期、缺口。把这些汇总成流程末尾的一份"信息健康诊断报告"输出给用户：产出的是判断而非文档。零额外命令。否决了独立 `/doc audit`：我们的结果物是文档，再生成一份文档是冗余；audit 的独特价值是"信任评估/事实说明"，适合做副产物。

## Constraints

- 交付形态：Claude Code Skill（开放标准，跨 agent 平台可用）。CLI 留待后续。
- Agent 友好文档规范（来自调研）：渐进式披露、小文档、每节带摘要、上下文自包含、Markdown 优先、避免大表格改用多级列表、文档带 last-verified 时间戳。

## 变更记录
- 2026-06-03 首次生成（结对 grill 产出 D1-D9）
- 2026-06-03 更新 理论锚点 + CoALA 映射表（核查 CoALA 原文，更正"Working Memory 层"误用，四层均为长期记忆）；新增 D10（信息批判方法论）、D11（INDEX.md 检索入口定位）、D12（audit 诊断副产物）
- 2026-06-04 Background 市场判断补 [推断] 标注；D4 修正 Wiki 契约（补回"如何上手"第 5 维，与 layer-wiki 对齐）
