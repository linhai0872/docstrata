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

## 定位

- **四层生成**：wiki（业务全景）/ requirements（需求决策）/ knowledge（领域材料）/ dev（开发结论）
- **开箱即用**：一条命令，工具自行探索项目，只在信息有缺口时提问
- **增量更新**：已有文档则 diff 更新，保留人工修改，不覆盖
- **兼容主流**：Claude Code、Cursor、Gemini CLI、Codex、OpenCode 等 Agent Skills 标准工具

---

## 背景

**人与 agent 结对编程的综合效率依然最高。** 工具的意义是提速这个小闭环：让人说清需求、做出决策，agent 专注执行，各司其职。但现有工具各有短板：

- **spec 框架**（speckit、BMAD、Superpower 等）：把需求分析、任务规划、代码生成全部编排进来，追求一键全自动。框架本身过重，理解和上手成本高；大型任务跑半小时出来的不是想要的结果，沉没成本大；小型任务准备一堆文档，负担大于收益。
- **plan 模式**：处理"这次任务怎么做"，执行规划会话内有效。细化过多会约束 agent 的发挥，且决策留在会话里，下次从头来过。
- **grill-with-docs**（Matt Pocock）：对照已有领域模型逐一审问计划，澄清术语、记录决策，跨会话持久有效。但信息管理散，没有区分谁看什么、什么性质的内容放哪里。

docstrata 在 grill-with-docs 的基础上，把信息按性质分层管理，让文档对人、对 agent 都有独立的阅读和检索价值。框架只做该做的事：澄清需求、记录决策，其他交给模型。

### 为什么要分层

项目文档服务三类读者：开发者、业务管理侧、coding agent。三者对文档的形式需求完全不同，却往往被混进同一份 README，或根本没有对应的地方存放：

| 问题 | docstrata 的解法 |
|---|---|
| 技术文档面向开发者，业务侧缺系统全景 | **wiki** — 所有人都能读的业务全景 |
| 需求意图散落，设计决策缺留痕 | **requirements** — 固化需求共识与架构决策 |
| 领域材料分散，缺统一检索 | **knowledge** — 整理原始材料为可检索索引 |
| 实践经验没有沉淀，coding agent 读不到 | **dev + INDEX.md** — 记录推断与结论，提供四层统一入口 |
| 文档靠人工维护，随迭代失真过期 | 自动探索上下文，缺口才提问；增量更新，保留人工修改 |

这四类知识的信息性质不同，混在一起写会相互污染。典型的漂移场景：requirements 和 dev 混写后，新的 agent 会话会把已确定的架构决策当作开放问题重新讨论，无谓地重跑 grill，甚至推翻之前的结论。分层解决的正是这个问题。

[CoALA](https://arxiv.org/abs/2309.02427)（Sumers et al., Princeton/CMU, TMLR 2024）研究 AI agent 长期记忆架构，把长期记忆分成三类，为四层划分提供了理论依据：

| CoALA 长期记忆 | 对应层 | 本质 |
|---|---|---|
| Episodic | requirements | 事件与决策的留痕 |
| Semantic | wiki · knowledge | 领域知识 |
| Procedural | dev | 操作经验 |

`INDEX.md` 是四层的检索入口，服务 coding agent 的 working memory 装填，本身不是那一层。

### 和 AGENTS.md 的区别

AGENTS.md / CLAUDE.md 的定位是**行为约束**：告诉 agent 每次该怎么干活，每次会话全量加载，每次都消耗 context token。

docstrata 产出的是**知识层**：通过 INDEX.md 按需加载，用到哪层读哪层，不用的不付 token。两者不是替代关系：行为约束仍然需要，docstrata 做的是行为约束之外的知识沉淀。把所有内容塞进 AGENTS.md 既难维护，也意味着每次会话都为用不到的内容付出 context 代价。

---

## 怎么运作

每层走同一个五步循环：

| 步骤 | 做什么 |
|---|---|
| **EXPLORE** | 读项目多源信息：代码结构、现有文档、git 历史、开发日志 |
| **MAP** | 把信息映射到该层的信息维度，标置信度（high / medium / low / missing） |
| **GRILL** | 只对 `low` / `missing` 维度提问；一次一个，附推荐答案，代码能回答的不问人 |
| **GENERATE** | 按固定骨架生成；已有文档则增量更新，保留人工修改 |
| **STAMP** | 更新 `last-verified` 时间戳，输出信息健康诊断 |

GRILL 的核心逻辑：每层预先声明一份**信息维度集合**（completeness contract），缺口决定问什么：

```
问题 = 契约维度 − 已探索到的信息
```

有完整需求文档和开发日志的项目，GRILL 往往整层跳过。提问模式来自 [grill-with-docs](https://github.com/mattpocock/skills)（Matt Pocock）。

生成时内建信息批判，处理多源信息的质量问题：

- **来源排序**：运行代码 > 测试 > git 历史 > 文档；多源矛盾不静默选一个
- **认知标注**：事实与推断分开标，标注格式 `[事实]` / `[推断]` / `[待确认]`
- **LLM 偏向**：遇到非标实现，记录项目实际行为，不"纠正"成标准做法

生成的文件固定放在 `docs/`，随 git 提交：

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

兼容支持 [Agent Skills 标准](https://agentskills.io) 的工具：Claude Code、Cursor、Gemini CLI、Codex、OpenCode 等。

---

## 使用

```
/doc wiki            # 业务全景 → docs/wiki.md
/doc requirements    # 需求共识 → docs/requirements.md
/doc knowledge       # 业务材料索引 → docs/knowledge/knowledge.md
/doc dev             # 开发结论 → docs/dev.md
/doc index           # coding agent 检索入口 → docs/INDEX.md
/doc all             # 按依赖顺序全部生成
```

支持任意项目类型，工具自行判断，无需声明。`/doc all` 会跳过无实质价值的层：没有业务材料就跳过 knowledge，功能一目了然的小项目 requirements 也可以不单独成文。

---

## 评测

改了 skill 之后，怎么知道文档质量有没有真的变好？靠主观感觉容易自欺欺人。`eval/` 让 LLM 替你读生成的文档、按固定标准打分——改前改后各跑一次，对比分数，是真改进还是噪声一目了然。

流程：改某层生成规范 → 对测试项目重新生成文档 → 打分 → 与上一轮对比。

打分分三档，按需选用：

| 档 | 需要什么 | 用途 |
|---|---|---|
| **结构门** | 无，纯 Python | 检查骨架有没有缺段落，秒出结果，适合 CI |
| **单 LLM 打分** | 一个 API key | 一个 LLM 读文档评分，日常迭代用 |
| **多 LLM 合议** | 多个 API key | 多家 LLM 独立打分取中位数，结果更可靠，发版前用 |

打分标准：文档覆不覆盖该层的核心维度、有没有把推断误标成事实、受众是否适配等，共 5 项，每项 0–3 分，归一化后 ≥ 0.7 算通过。

docstrata 用自身文档作为测试案例——先用工具生成，再用 eval 打分，自己验自己。详见 [eval/README.md](eval/README.md)。

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
| [评测闭环](eval/README.md) | skill 迭代后验证质量的开发工具（结构门 / 单 judge / ensemble 三档） |
