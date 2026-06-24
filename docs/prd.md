# PRD — docstrata

> docstrata 把开发中反复发生的决策与事实，用 grilling 固化成分层、不膨胀、人机皆可读的项目知识；它只做"澄清需求、记录决策"，执行交给模型。

last-verified: 2026-06-24 | prd.md 64 行

## 定位

docstrata 是一个 Agent Skill：把结对开发里产生的决策与事实，按知识性质分层，固化成项目的长期记忆。它提速的是"人说清需求、做出决策，agent 专注执行"这个小闭环，不是自动写代码。

与三类相邻工具的差异（定位锚点，几乎不变）：

- **vs spec 框架（speckit / BMAD 等）**：spec 框架把需求分析、任务规划、代码生成全编排进来，追求一键全自动——框架重、大任务沉没成本高、小任务负担大于收益。docstrata 只固化"需求与决策"，编排与执行不接管。
- **vs plan 模式**：plan 解决"这次任务怎么做"，决策留在会话里、下次从头来。docstrata 把跨会话长期有效的决策沉淀进文件。
- **vs grill-with-docs（Matt Pocock）**：同样用 grilling 固化决策，但信息管理扁平，不区分谁看什么、什么性质放哪。docstrata 按 CoALA 知识性质分层，让文档对人、对 agent 都有独立检索价值。

## 目标用户

用 agent 结对开发的人，尤其跑长周期项目、受够了"决策散落对话、文档随迭代失真、新会话把已定决策当开放问题重跑"的开发者。

产出的文档服务三类读者：开发者读 dev/requirements，业务与管理侧读 wiki（对外），coding agent 经 INDEX 按需检索各层。docstrata 自己（产品负责人 + agent）在拿不准产品决策时读 PRD。

## 价值主张与优先级原则

核心主张：一切 agent 行为由四个来源决定——agent 能力、用户决策（grilling 得到）、产品定位（本文档）、事实本身（代码/文档/执行中发现）。docstrata 负责把后三者可靠固化，让无数决策稳定堆叠成产品。

优先级原则（用来裁决"该不该加某个机制"）：

- **框架只做该做的**：澄清需求、记录决策；能交给模型的不写进框架。任何"为完整而加的仪式"优先砍。
- **按需加载 > always-on**：知识走 INDEX 按需取用，不学 Kiro/speckit 每次全量加载、为用不到的内容付 token。
- **结构 > 指令**：防污染靠结构（单写入口、毕业 gate、分层），不靠"写好规则"指望模型自觉。
- **手动 > 自动**：郑重操作（如 compact）手动触发，不自动催、不自动跑。
- **轻量可选 > 强制**：降低负担的约定优先于强制声明仪式。
- **诚实 > 完整**：事实与推断分开标注，宁缺毋造；记录项目真实行为，不"纠正"成标准做法。

## 功能范围

docstrata 覆盖"固化—检索—维护"全程。下面每条是产品意图（要做成什么），不是命令清单：

- **分层固化**：prd（产品主张）/ requirements（需求共识与决策）/ knowledge（业务材料索引）/ wiki（对外全景）/ dev（开发结论）。按知识性质分开，互不污染。
- **grilling 消歧**：completeness contract 驱动，只对探索不到的缺口提问；信息足则整层跳过。卡在产品决策时 PRD 兜底。
- **检索入口**：INDEX.md 给 coding agent 一个按需装填四层长期记忆的轻量导航。
- **收缩维护**：compact 把随迭代膨胀的层收回有界（先压再拆、归档不删、硬事实保真），让长期记忆长期可用。
- **自验闭环**：eval 用 reference-free rubric + 跨厂商 ensemble 给生成质量打分，让 skill 迭代是真改进而非自我感觉。

## 非目标

docstrata 明确不碰以下领域：

- **不做全自动 spec 编排**：不接管任务拆分、代码生成、测试的全流程（那是 speckit 的路，与"框架只做该做的"冲突）。
- **不做会话内执行规划**：plan 模式那种"这次怎么做"的细化留给 agent 运行时；docstrata 只固化跨会话有效的决策。
- **不生成运行时动态 memory**：对话提炼的即时经验由 agent 运行时自己写（Anthropic memory tool / Mem0 那类），docstrata 不越界。
- **不做行为约束**：AGENTS.md/CLAUDE.md 的"怎么干活"操作契约是另一回事，docstrata 做"知识在哪"，两者不混写。
- **不维护标准答案**：eval 是 reference-free，项目本身是 ground truth，不背 golden answer 的维护成本。
- **v1 不做平台集成 / 静态站发布**：仅本地文件 + URL，不接 Notion/Confluence、不导出静态站。

## Roadmap

按近→远排列，条目带日期。这是前瞻主张，随认知更新重写。

- **2026-06 已落地**：新增 prd 层 + compact 收缩操作；dev 层加毕业 gate（只记 code/git 复原不出来的）；文风加两段式 + 可选向上指针；eval 支持 PRD 层评分。
- **下一步（grilling 中）**：开发周期闭环（loop）——读取文档、grilling 出待办、research/POC、按需求大小决定做法、分档 test/review、验收落库、提交。载体不预设（skill / rule / 原生 / 不要），逐节点 grill 出最佳实践。docstrata 是这个闭环的长期记忆地基，读写两端都接它。
- **评估中**：eval 回归打分上 pairwise（改前/改后同时给 judge 选，比绝对分敏感），等绝对分判断不准时再做。

## 变更记录
- 2026-06-24 首次生成（dogfood 新增的 prd 层；产品主张前瞻 intent，与 requirements 的已发生决策分离）
- 2026-06-24 文风重构
