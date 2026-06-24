# Requirements — docstrata

> 一个 Agent Skill，按知识性质分层为任意项目生成/维护文档。本文件是本项目自身的需求共识，由结对 grill 过程产出（Episodic 层：记录"约定了什么、为什么这样定"，只增不改写）。
>
> 产品主张（要做成什么、roadmap）见 [docs/prd.md](prd.md)——本文件只记已发生的事实，前瞻愿望归 PRD。

last-verified: 2026-06-24

## Background

需求方有大量形态各异的项目（全栈服务、Dify DSL 应用、CLI/MCP 服务、Skill 形态等），需要一套 agent 时代的工具自动生成/维护文档。市面无单一工具能覆盖全部需求 `[推断]`（基于调研，未穷尽市场），但可用四个对应知识层的能力组合解决。

理论锚点：

- **CoALA**（Sumers et al., Princeton/CMU, TMLR 2024, arXiv:2309.02427）：Agent 记忆架构。三类**长期记忆**（Episodic / Semantic / Procedural）存持久知识；**Working Memory** 是"为当前决策周期维护活跃信息的中央枢纽"（原文：*central hub connecting different components*），知识从长期记忆被 retrieved into working memory 以支撑推理。它是运行时的临时中转，不是知识本身的存放处。
  - **我们的映射**：四层文档对应三类长期记忆（见下表）。Working Memory 是 agent 运行时的 context，**文档工具不生产它**；我们能做的是给它一个高效检索四层长期记忆的入口（`docs/INDEX.md`），优化 retrieval 路径，而非实现 working memory 本身。详见 D10。
- **Diátaxis**（diataxis.fr）：文档四象限（tutorial/how-to/reference/explanation），验证"固定骨架+自由内容"有效。
- **Anthropic Agent Skills**：渐进式披露三层加载（metadata → SKILL.md → references）。

## Goals

1. 为任意项目按需生成各层文档之一或全部。
2. 工具自动探索项目上下文，仅在信息有缺口时才向人类提问（grill）。
3. 把人类当作获取 context 的一种工具，而非每次都从头问。
4. 增量更新，保留人类手改内容。
5. 做成通用工具供团队使用，有价值则开源。

## Non-goals

- 不限定项目类型，工具自行判断，用户无需声明。
- Knowledge 层不从代码逆推业务规则（实用性存疑，明确不做）。
- 第一版不做平台 API 集成（Notion/Confluence 等），仅支持本地文件 + URL。
- 第一版不做文档发布/静态站导出（CLI 发布能力留待后续评估）。

## 分层定义与 CoALA 映射

四层（wiki/requirements/knowledge/dev）对应 CoALA 的**长期记忆**（持久知识），不含 Working Memory（那是 agent 运行时 context，见理论锚点与 D10）。`prd` 是这四层之上的**前瞻产品意图**，不属 CoALA 记忆三类（它是当下主张，不是已沉淀记忆），见 D13。

| 子命令 | 类型 | 本质 | 受众 | 内容来源 |
|---|---|---|---|---|
| `prd` | 前瞻 intent（非 CoALA） | 产品主张：定位/价值/功能范围/roadmap | 产品负责人 + agent（对内） | 人定主张，AI 整理 |
| `wiki` | Semantic | 系统全景，快速理解整个系统 | 所有人（含业务，对外） | AI 生成，从代码/需求推导 |
| `requirements` | Episodic | 需求方与开发者的共识约定 + 开发计划（决策留痕：责任与决策） | PM + 开发 | 部分原始需求 + 部分 AI 整理 |
| `knowledge` | Semantic | 业务专属原始材料库（规章制度、业务规则等 raw data） | 技术 + 业务 | **已有文档为主，AI 整理+索引** |
| `dev` | Procedural | 开发推断与实践结论（推断/实践事实，非原始事实） | 开发 + 维护者 | AI 生成，从代码+需求+知识推导 |

wiki 与 knowledge 同属 Semantic 层但视角不同：wiki 是"系统能做什么"，knowledge 是"做这件事需要的业务背景知识"。prd 与 wiki 在定位/价值上重叠，以 prd 为源、wiki 引用不复制（见 D13）。

## 关键决策（决策留痕）

> 决策记录用四段骨：决策 · 背景 · 备选 · 后果。编号（D1…）是项目里实际流通的交叉引用 handle（commit/对话/文档都在引），保留。去掉的是 ADR/BDR 这类术语黑话，不是结构本身（见 D15）。

### D1 — 一个 skill，多个子命令

一个 skill、多个子命令，共享同一套"探索→评估缺口→grill→生成"逻辑，避免拆成四个 skill 重复维护。

用 SKILL.md 路由表分派，各层契约放 references/ 渐进加载。

- 命令：`/doc wiki | requirements | knowledge | dev | all`
- 支持显式指定单层，也支持 `all` 一键全生成。
- 后续扩展：D13 加 `prd` 层、D14 加 `compact` 收缩操作，当前为 `/doc prd | requirements | knowledge | wiki | dev | index | compact | all`。一 skill 多子命令的结构不变。

### D2 — 层间有依赖顺序，但每层可独立触发

层与层之间有上下游（requirements → wiki/knowledge → dev），跑单层时不强制先跑上游；上游层若存在则自动引用。

### D3 — Grill 触发条件：缺口驱动

先探索、后提问——只有契约维度填不满时才 grill。

工具先自动探索上下文（读文件/现有文档/代码），把信息映射到每层的 **completeness contract**（信息维度），仅对缺失/低置信维度动态提问。信息够则跳过 grill 直接生成。一次问一个问题，附 AI 推荐答案（grill-with-docs 风格）。

### D4 — Grill 方法论：动态提问，不用固定清单

契约维度稳定，具体问题临场算——不用固定必问清单。

每层声明一份 completeness contract（稳定的信息维度），具体问什么由"契约维度 − 已探索信息 = 缺口"临场算出。场景灵活，契约稳定。

各层 completeness contract：

- **PRD**：定位 · 目标用户 · 价值主张与优先级原则 · 功能范围 · 非目标 · roadmap（D13 新增）
- **Wiki**：系统存在的理由 · 目标用户 · 核心能力边界 · 关键概念 · 如何上手
- **Requirements**：原始需求意图 · 共识约定 · 开发计划 · 关键取舍
- **Knowledge**：原始材料来源 · 业务规则提炼 · 分类索引
- **Dev**：需求→实现的推导链 · 实践得出的事实 · 已验证/已否定的方案

### D5 — 输入是路径，工具自判项目类型

用户只给目录路径，项目类型由工具自己判断。

输入一个目录（代码仓库或文档目录均可）。对工具而言都是文件树，探索策略相同，用户无需声明类型。

### D6 — 文档存项目内，约定固定结构

文档落在项目内 `docs/`，结构固定，随 git 走。

```
docs/
├── prd.md                # 产品主张（D13 新增）
├── wiki.md
├── requirements.md
├── knowledge/
│   ├── knowledge.md      # 整理后的索引（导读层）
│   ├── raw/              # 本地原始文档（不改动）
│   └── sources.yaml      # 外部 URL 列表
├── dev.md
└── INDEX.md              # coding agent 检索入口
```

随 git 提交。需要分发到别处由用户自行复制。归档冷存放 `docs/archive/`（compact 折叠的时间线/被取代决策，见 D14）。

### D7 — 增量更新，保留手改

再次生成时 diff 现有文档，只改有实质变化的部分，保留人工修改。

再次触发已存在的层：diff 现有文档与当前上下文，只重写有实质变化的段落，文末记录更新时间与变更摘要。不全量重写。

### D8 — 固定骨架 + 自由内容

section 标题固定（增量锚点 + 跨项目一致），内容由 AI 按上下文生成。

每层有约定 section 标题（增量更新的锚点 + 跨项目一致性），section 内容由 AI 按上下文生成，不是填表。

### D9 — Knowledge 层只整理不生成

knowledge 只整理已有材料，不从零编造业务规则。

用户把原始材料放 `docs/knowledge/raw/`（任意格式）或在 `sources.yaml` 列 URL。工具扫描后生成结构化 `knowledge.md`：每份材料的摘要、关键规则提炼、标签分类、原文件链接。原始文件不动。其他层引用 knowledge.md 摘要，无需重读原始 PDF。

### D10 — 信息批判方法论统一处理信息质量问题

信息质量问题走统一方法论，不靠逐个打补丁。

统一由 `references/source-criticism.md` 四准则处理：来源可信度排序、矛盾处理、认知状态标注、打破 LLM 先验偏向。理论来源经实测精简，砍掉过度设计（完整 ACH、Admiralty 双轴打分、Wang&Strong 全维、W3C PROV）。EXPLORE/MAP/GENERATE 三步引用它。

### D11 — INDEX.md 是长期记忆的检索入口，非 Working Memory 层

INDEX.md 是 coding agent 检索四层长期记忆的轻量导航，不是 Working Memory 本身。

`docs/INDEX.md` 是给 coding agent 的文档导航索引（轻量指针，指向各层，不复制内容）。

CoALA 的 Working Memory 是 agent **运行时**的活跃 context 中央枢纽，文档工具不生产它。INDEX.md 只是优化 agent 检索四层**长期记忆**的入口，服务于 working memory 的装填，本身不是那一层。

边界（明确不做）：运行时动态 memory（对话提炼的踩坑/经验，如 Anthropic memory tool、Mem0、Qoder 的"记忆"）由 agent 运行时自己写，不由本工具生成：避免功能越界。

与 AGENTS.md 的关系：AGENTS.md（事实标准，AAIF 治理）是"怎么干活"的操作契约（命令、约定、红线），定位是精简（实证 ≤150 行，过长反降低 agent 成功率，arXiv:2602.11988）。INDEX.md 是"知识在哪"的导航，两者信息类型不同，不混写。

### D12 — audit 是生成流程的诊断副产物，非独立命令

audit 是生成流程末尾的诊断报告，不是独立命令。

生成过程中 source-criticism 本就会发现跨 context（代码/git/文档/规范文件）的冲突、过期、缺口。把这些汇总成流程末尾的一份"信息健康诊断报告"输出给用户：产出的是判断而非文档。零额外命令。否决了独立 `/doc audit`：我们的结果物是文档，再生成一份文档是冗余；audit 的独特价值是"信任评估/事实说明"，适合做副产物。

### D13 — 新增 prd 层（产品主张，前瞻 intent）

- **决策**：增加 `prd` 层，专门承载产品主张——定位、目标用户、价值原则、功能范围、非目标、roadmap——产出 `docs/prd.md`，放在依赖链最上游。
- **背景**：原来的四层只管"已经定了什么"，缺一个说清楚"要做成什么"的源头；grilling 卡在产品方向时，没有文件可参照。
- **备选**：把产品愿望写进 requirements 的决策记录——否决。下次会话很容易把"还没定的想法"当成"已经拍板的事"。
- **铁律**：prd 记主张（认知更新时直接重写），requirements 记事实（只增不改写）。**prd 不写历史，requirements 不写愿望。**「考虑过 X 但放弃」是事实 → requirements；「未来要支持 Y」是主张 → prd。
- **非 CoALA**：CoALA 三类是已沉淀的长期记忆，prd 是当下前瞻主张，是四层之上的意图锚点。不进 always-on context，同走 INDEX 按需加载，grilling 卡住才读。
- **后果**：prd 与 wiki 在定位/用户/价值上重叠，**以 prd 为源、wiki 引用不复制**——两处各写一份迟早漂移；项目没有 prd 时，wiki 自行覆盖这些维度。

### D14 — 新增 compact 横切收缩操作

- **决策**：增加 `compact` 操作，手动触发（`/doc compact [层]`），用来收缩膨胀的层文档。不自动催、不自动跑。
- **背景**：五步循环只有增量更新，只增不减。长期跑下来，dev 会按日期堆成工程实录，requirements 会无限叠决策；实测单一 markdown + 自由写回会变乱、前后矛盾。
- **核心操作**：先压（丢 code/git 可复原项 + 去重 + **按主题归并**日期块）→ 再拆（压完仍超限才分文件）→ 归档不删（移 `docs/archive/`，可 rehydrate）。
- **毕业门槛**：长期记忆只留 code+git log 复原不出来的——坑、被否方案+原因、非显然决策理由。叙事/统计/一次性流水/working memory 泄漏物丢弃。
- **保真**：叙事可压，硬事实（配置值/错误码/版本号/命令/裁决结论）逐字保留，认知标注不丢。
- **后果**：增量更新管"只增"，compact 管"收缩"，两个合起来才是长期记忆闭环；STAMP 顺手标行数当被动体量信号，由用户判断要不要 compact。

### D15 — 决策记录去黑话，保留四段骨 + 编号当 handle

- **决策**：requirements 里的决策记录保留四段结构（决策/背景/备选/后果），去掉 ADR/BDR 这类术语；编号（D1…）继续当交叉引用 handle。
- **背景**：grill-with-docs 的 ADR 结构（上下文/决策/备选/后果）好用，但"ADR""BDR"对读者是噪音；编号已经在 commit、对话、其他文档里流通了。
- **备选**：再引入 BDR（业务决策记录）等术语做分类——否决，多一层黑话，收益为零。编号 + 四段骨够用。
- **后果**：compact 折叠决策时保留编号，删了会断引用；去掉的是术语，不是编号。

### D16 — 可读性：先修关系，再修表达

- **决策**：doc-conventions 加可读性约束——可选**向上指针**（条目链回上游 requirements/prd）+ **两段式**（自然语言摘要在前、密集细节在后）+ **可读性预算**（箭头链/嵌套括号/slug 上下文设上限）+ 声明式可判定写法。
- **背景**：实测反馈文档"读起来累"。主因是关系链断了——找不到背景和原始需求的映射，理解成本高；次因才是文风太密太干。
- **后果**：表达问题先查关系链，再改文风。文档面向 agent 为主、人偶尔读，两段式两边都能兼顾。

### D17 — dev 层定位收窄：纯引用 + 毕业门槛

- **决策**：dev 层定位收窄为"纯引用、agent 面向"。毕业门槛：只记 code+git log 复原不出来的事实。`现状快照`、`本期进度`这类在途易失状态不写 dev。
- **背景**：长期项目的 dev 容易被运行时记忆污染——比如 claude code 自身记忆——变成臃肿 devlog，混进叙事、统计、一次性流水、进度快照。
- **后果**：进度追踪走 loop 工作区/todos，不写 dev.md。dev 膨胀时 compact 收得最狠。

### D18 — eval 扩展支持 prd 层 + 防 verbosity bias

- **决策**：eval 扩展支持 prd 层——加 `rubric/prd.md`（按 intent 文档校准 source_fidelity/epistemic_accuracy，layer_specific 考核可判定性 + 主张/事实分离）、structure_gate 加 prd 骨架与白名单、tests.yaml 加 prd 用例、`_judge.md` 加"只按 rubric 打分、不被表面特征带偏"。
- **背景**：prd 是 intent 文档，不像其余层能靠代码溯源，需要单独校准的评分维度；LLM judge 还有 verbosity/style bias。
- **后果**：prd 层进打分闭环；eval 仍 reference-free——项目本身是 ground truth，不维护 golden answer。

### D19 — skill 更名为 docstrata

- **决策**：skill 名 `doc` → `docstrata`，用户命令 `/doc` → `/docstrata`，仓库目录 `skill/doc/` → `skill/docstrata/`。
- **背景**：`doc` 过于泛化，和任意「文档操作」混淆；项目已名 docstrata，skill 名应对齐产品。
- **备选**：保留 `/doc` 作 alias——否决，双入口增加认知负担。
- **后果**：历史决策（D1/D12/D14 等）里出现的 `/doc` 是决策当时的事实，不 retroactive 改写。当前操作入口统一 `/docstrata {子命令}`，如 `/docstrata wiki`、`/docstrata compact dev`。

## Constraints

交付形态：Claude Code Skill（开放标准，跨 agent 平台可用）。CLI 留待后续。

Agent 友好文档规范（来自调研）：渐进式披露、小文档、每节带摘要、上下文自包含、Markdown 优先、避免大表格改用多级列表、文档带 last-verified 时间戳。

## 变更记录
- 2026-06-03 首次生成（结对 grill 产出 D1-D9）
- 2026-06-03 更新 理论锚点 + CoALA 映射表（核查 CoALA 原文，更正"Working Memory 层"误用，四层均为长期记忆）；新增 D10（信息批判方法论）、D11（INDEX.md 检索入口定位）、D12（audit 诊断副产物）
- 2026-06-04 Background 市场判断补 [推断] 标注；D4 修正 Wiki 契约（补回"如何上手"第 5 维，与 layer-wiki 对齐）
- 2026-06-24 dogfood 本轮：四层→分层框架，新增 prd 层定义与 CoALA 边界；追加 D13（prd 层）、D14（compact 收缩）、D15（去黑话留四段骨）、D16（可读性）、D17（dev 毕业门槛）、D18（eval 支持 prd）；D1/D6 补扩展指针
- 2026-06-24 文风重构
- 2026-06-24 D19：skill 更名为 docstrata，命令 `/docstrata`，目录 `skill/docstrata/`
