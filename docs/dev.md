# Development Notes — doc-layers

> 这个 skill 在设计与实测中沉淀的工程结论：契约该放哪、哪些反馈是测试假象、为什么克制加维度。

last-verified: 2026-06-03

参考上游：[wiki](wiki.md) · [requirements](requirements.md)

## 需求到实现的映射

| 需求点 | 实现方式 | 备注 |
|---|---|---|
| 四层文档（D1） | 一个 skill + 子命令路由，非四个 skill | 共享"探索→评估→grill→生成"循环，避免逻辑重复四遍 |
| 缺口驱动 grill（D3/D4） | completeness contract：每层声明信息维度，`问题 = 维度 − 已探索信息` | 维度写死在各层 reference，问什么临场算 |
| 渐进披露 | SKILL.md 精简（路由+五步循环），细节进 references/ 按需加载 | 遵循 Anthropic Agent Skills 规范 |
| 增量更新（D7） | 逐 section diff，只重写变化段，保留人工内容 | section 骨架固定 = 增量锚点 |
| 任意项目类型（D5） | 项目类型作启发式而非封闭清单 | 见"已否定的方案" |

## 关键实现决策

**契约放 methodology.md，不放 SKILL.md 正文**

核心方法论（completeness contract、gap-driven grill、五步循环细节）全部下沉到 `references/methodology.md`，SKILL.md 只留路由表和五步骨架。理由：渐进披露——SKILL.md 常驻 context 要轻；方法论是执行某层时才需要的深度内容。

**改动集中在 methodology.md，克制改各层契约**

实测暴露的 12 个问题，优先用 methodology.md 的通用规则覆盖（跳过条件、非交互模式、过期文档、小项目降级、开发记忆探索），而非给每层契约加维度。各层契约只做了两处最小新增（wiki「如何上手」、requirements 验收并入共识）。理由见下方"已否定的方案 E"。

## 实践结论

### completeness contract 机制经实测有效 [实测]

两个真实项目（LOCCN 前端工具、报告处理 Python 工具）的测试报告都确认："维度 − 置信度 − 行动"三列模型让 agent 避免了模糊的"生成文档"指令，MAP 步骤是五步里最顺畅的。机制本身不需要改。

### 信息充分的项目会整层跳过 GRILL [实测]

当项目有完整原始材料（需求 txt + CLAUDE.md + 子任务文档 + 开发日志），low/missing 维度极少，GRILL 实质无内容可问。初版没写明"何时跳过"，导致两个测试者都要自行判断。已补：所有维度 ≥medium 直接跳过。

### 开发记忆文件是 dev 层金矿 [实测]

`.workbuddy/memory/`、`.claude/memory/` 直接提供踩坑记录和被否定方案——报告工具的 dev.md 里 5 个"已否定方案"全部来自开发日志，质量远超从代码反推。初版 EXPLORE 清单漏了这类文件，已补且标为高于 git log 的优先级。

### 生成质量：业务转译与工程提炼都达标 [实测]

- wiki 层把"REST endpoint/ExcelJS"转译成了"支持批量导出订单"级别的业务语言，非技术读者可读。
- dev 层把开发日志的零散踩坑结构化成了"已否定的方案"清单（procedural 层的核心价值）。
人工审阅确认两个项目的 6 份产物清晰、可用。

## 已否定的方案

**方案A：四个独立 skill**
- 结论：否定（D1）
- 原因：四层共享同一执行循环，拆开会重复逻辑四遍，维护成本高。改用一个 skill + 子命令路由。

**方案B：grill 用固定必问清单**
- 结论：否定（D4）
- 原因：场景灵活，固定清单要么问冗余要么问不全。改用 completeness contract，维度稳定、问题临场。

**方案C：knowledge 层从代码逆推业务规则**
- 结论：不做（需求方明确）
- 原因：实用性存疑，且容易编造不存在的业务规则。knowledge 只整理已有材料。

**方案D：枚举封闭的"项目类型清单"让 agent 匹配**
- 结论：否定
- 原因：LOCCN 是"单 HTML 文件应用"，不在初版五类里，测试者被迫自行归类。封闭清单越列越脆。改为：类型是启发式，先判断"核心交付物/逻辑在哪"，自定探索重心，清单只作参考。

**方案E：把测试反馈全部转成新增契约维度**
- 结论：否定
- 原因：测试提了"加验收标准维度""加启动入口维度""拆实践/延伸维度"等。若每条都加维度，契约会膨胀，违背"渐进披露+不膨胀"。只接受了 wiki「如何上手」一个真缺口维度，其余用"并入已有维度 + 一句判断标准"处理。

**方案F：为自动化测试设计"无人降级策略"**
- 结论：重新定性，未照搬
- 原因：subagent 不能交互才痛，这是**测试假象**——真实用户在 Claude Code 里能正常 grill。但它指向真需求：批量生成时不想被打断。所以改成「非交互/批量模式」开关（推断+`[待确认]`+末尾汇总缺口清单），而非"测试降级"。

### 边界类问题统一成方法论，而非逐个打补丁 [实测]

实测反馈里"来源该信哪个""旧文档误导""需求 txt 归 knowledge 还是 requirements"看似三个独立 bug，本质都是**信息质量问题**。调研了成熟学科（NATO Admiralty Code 来源分级、史学史料批判、情报分析 ACH、三角验证、LLM 知识冲突研究、信息质量维度框架、认知状态追踪 FPF），抽象出 `source-criticism.md` 四条准则统一处理：
1. 来源可信度排序（代码=一手事实 > 文档=解读）
2. 矛盾处理（不静默选一个，标 `[过期]`/`[冲突]`）
3. 事实vs推断标注（`[事实]/[推断]/[待确认]/[过期]/[缺口]`）
4. 打破 LLM 先验偏向（非标实现记录实际行为，不"纠正"成标准做法）

这条准则4 是 agent 特有的——调研里最硬的发现：LLM 会用训练数据静默覆盖项目特定信息。对"项目形态各异、不少非标实现"的场景最对症。

**关键克制**：这些方法论原是给人类分析师的，照搬会过度设计。明确砍掉了完整 ACH 八步、Admiralty 双轴打分、Wang&Strong 全15维、W3C PROV 本体——只留对 agent 有操作价值的核心。

### CoALA 原文核查纠正了一处概念误用 [实测]

设计 INDEX.md 时，一度把它称作"Working Memory 层"。核查 CoALA 原文（§4.1）后否定：Working Memory 是 "central hub...for the current decision cycle"——agent **运行时**的活跃 context 枢纽，知识从长期记忆 "retrieved into working memory"。它是动态运行时的，不是静态文件。

更正：四层文档全部对应**长期记忆**（episodic/semantic/procedural）；INDEX.md 是长期记忆的**检索入口**，服务于 working memory 的装填，本身不是那一层。教训：拿框架术语给自己的设计贴标签前，回原文核对定义，别用类比凑等号。

### INDEX.md 与 AGENTS.md 的边界 [实测]

调研确认 AGENTS.md 是事实标准（AAIF 治理，6万+ repo），但它的定位是"怎么干活"的操作契约，且实证 ≤150 行、过长反降低 agent 成功率（arXiv:2602.11988）。所以 INDEX.md（"知识在哪"的导航）不塞进 AGENTS.md，两者信息类型不同。本工具只生成 INDEX.md，不碰 AGENTS.md，更不生成运行时动态 memory——边界清晰避免越界。

### audit 定位：诊断副产物而非命令 [推断]

否决独立 `/doc audit`。理由：我们的结果物是文档，audit 再生成文档是冗余。audit 的独特价值是"信任评估"——产出判断而非文档，且对象是全部 context（代码/git/文档/规范文件）。做成生成流程的副产物，零额外命令。source-criticism 在 EXPLORE/MAP 本就发现了这些问题，audit 只是汇总输出。

### index/audit 经 MCP + Dify 工具项目实测有效 [实测]

第三轮实测（dida365-agent-mcp + dify-dsl-pipe）验证：
- **index 纯派生顺畅**：17 行、只放指针、与已有 README 边界处理得当（无 AGENTS.md 时反向引用 README 开发章节）。
- **audit 真发现真问题且克制**：dida 测出 server.py 日志"21 V2 tools"实际 25 个；dify-pipe 测出 ADR-0003 端点描述与代码不符、版本号三处漂移（package.json/index.ts/SKILL.md）。两个测试者都遵守了"不夸大""有限度声明（列出未读文件）"。
- **准则1 交付物形态判断正确**：dify-pipe 测试者正确区分"项目交付物（TS代码）vs 处理对象（Dify DSL）"，未混淆。

据实测做的泛化修改：index 骨架的操作约定兜底（AGENTS.md→CLAUDE.md→README，都没有则删行）、行数改"目标 20-30 上限 60"；audit 新增"版本漂移""待验证外部假设"两类、补单跑 index 无 audit、补输出时序。

## 延伸知识

**理论锚点的取舍** [实测]
- CoALA 四层（Working/Episodic/Semantic/Procedural）给了文档分层的学术依据，四个子命令一一对应。
- Diátaxis 验证了"固定骨架+自由内容"有效，但它纯面向人类、无 episodic 维度，所以只借结构经验不照搬象限。
- wiki 与 knowledge 同属 Semantic 层但视角不同（系统能做什么 vs 业务背景知识），这是把"业务 wiki"和"业务知识库"分成两个子命令的依据。

**agent 友好文档规律**（来自调研）
- 每节带摘要改善 RAG 检索；避免大表格（LLM 线性读取丢二维关系）；Markdown 优先；描述能力/概念优先于写死文件路径（路径随重构过期）。

## 变更记录
- 2026-06-03 首次生成（基于 LOCCN + 报告工具双项目实测后的 skill 迭代）
- 2026-06-03 新增"边界类问题统一成方法论"实践结论（引入 source-criticism.md 信息批判四准则）
- 2026-06-03 新增 CoALA 核查纠正、INDEX.md/AGENTS.md 边界、audit 定位三条实践结论（对应 D11/D12）
- 2026-06-03 第三轮实测（MCP + Dify 工具项目）后泛化修改 index/audit，新增实测结论
