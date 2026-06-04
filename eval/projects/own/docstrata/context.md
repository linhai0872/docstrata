# 项目上下文：docstrata（judge 核对用 ground truth）

> judge 用它核对待评文档的「来源忠实度」——文档里写的能力/概念/决策能否对上项目真实情况。
> 这是**核心事实摘要，非全量**。文档中超出本摘要但合理、且已标注认知状态的内容（尤其 dev 层的私有实测结论），不等于编造；只有与本摘要**明确矛盾**时才算来源失真。

## 定位

一个 Claude Code Skill（skill 名 `doc`），按 CoALA 四层知识结构为**任意项目类型**生成/维护文档。各层是一个子命令，共享同一套「探索→评估缺口→grill→生成→留痕」执行循环。交付形态是 Agent Skill（开放标准，跨 agent 平台），CLI 留待后续。

## 命令清单（完整）

| 命令 | 层 / 类型 | 产出文件 |
|---|---|---|
| `wiki` | Semantic | `docs/wiki.md` |
| `requirements` | Episodic | `docs/requirements.md` |
| `knowledge` | Semantic | `docs/knowledge/knowledge.md` |
| `dev` | Procedural | `docs/dev.md` |
| `index` | 检索入口（纯派生） | `docs/INDEX.md` |
| `all` | 全部 | 四层 + index |

- `all` 真实存在，按依赖顺序一次生成：`requirements → knowledge → wiki → dev → index`。无实质价值的层（如无业务材料的 knowledge）按「优雅降级」跳过并说明。
- `index` 不走五步循环（无 completeness contract，是纯派生），但遵循增量更新与 STAMP。
- `audit` **不是命令**，是任何生成动作完成后的诊断副产物（汇总信息健康问题：冲突/过期/缺口/孤儿文档），零额外文档。

## 四层定义、受众、内容来源

| 子命令 | CoALA 长期记忆 | 本质 | 受众 | 内容来源 |
|---|---|---|---|---|
| wiki | Semantic | 系统全景，快速理解整个系统 | 所有人（含业务） | AI 从代码/需求推导，业务语言转译 |
| requirements | Episodic | 需求方与开发者的共识约定 + 开发计划（ADR 性质） | PM + 开发 | 部分原始需求 + 部分 AI 整理 |
| knowledge | Semantic | 业务专属原始材料库（规章/规则等 raw data） | 技术 + 业务 | 已有材料为主，AI 整理+索引，**不从代码逆推** |
| dev | Procedural | 开发推断与实践结论（非原始事实） | 开发 + 维护者 | AI 从代码+需求+知识推导 |

wiki 与 knowledge 同属 Semantic 但视角不同：wiki 是「系统能做什么」，knowledge 是「做这件事需要的业务背景知识」。

## 执行循环（五步，所有层通用）

1. **EXPLORE** — 穷尽自动探索：现有层文档 > 项目自述(README/CLAUDE.md/AGENTS.md) > 代码结构 > 配置产物 > git 历史。开发记忆文件(`.workbuddy/memory/`、`.claude/memory/`、`DEVLOG.md`)是 dev 层最高价值来源。
2. **MAP** — 把信息映射到本层 completeness contract 的每个维度，打置信度（high/medium/low/missing）。
3. **GRILL** — 仅对 low/missing 维度提问，一次一个，附 AI 推荐答案；维度全 ≥medium 则整层跳过。非交互/批量模式下改为推断+`[待确认]`+末尾汇总缺口清单。
4. **GENERATE** — 按本层固定骨架生成；已存在则**增量更新**：逐 section diff，只重写有实质变化的段落，**保留人类手改内容**。
5. **STAMP** — 更新 `last-verified` 日期 + 变更记录。

核心公式：`问题 = 契约维度 − 已探索到的信息`。维度稳定（写死在各层 reference），问什么临场算。

## 各层 Completeness Contract（信息维度）

- **wiki**：系统存在的理由 · 目标用户 · 核心能力边界 · 关键概念 · 如何上手
- **requirements**：原始需求意图 · 共识约定(含验收标准) · 开发计划 · 关键取舍
- **knowledge**：原始材料来源 · 业务规则提炼 · 分类索引
- **dev**：需求→实现的推导链 · 实践得出的事实 · 已验证/已否定的方案

## 信息批判（source-criticism，横切方法论）

四准则（EXPLORE/MAP/GENERATE 引用）：
1. **来源可信度排序**：运行代码 > 测试 > git > 注释 > 官方文档 > 设计文档 > 开发记忆 > 口述。核心交付物非代码时（Dify DSL/纯文档/Skill），该形态视为一手事实。
2. **矛盾处理**：绝不静默选一个，按类型标 `[过期]`/`[冲突]` 或进 GRILL；用证伪思维，不数多数。
3. **事实vs推断标注**：`[事实]` / `[推断]` / `[待确认]` / `[过期]` / `[缺口: 缺什么|建议来源]`。推断不得伪装成事实。dev 层另用 `[实测]` 标本项目验证出的结论。
4. **打破 LLM 先验偏向**：项目用非标实现时记录实际行为，不"纠正"成训练数据里的标准做法。

理论来源经实测精简，砍掉过度设计（完整 ACH 八步、Admiralty 双轴打分、Wang&Strong 全维、W3C PROV 本体）。

## 关键决策（requirements.md 的 D1–D12，真实存在）

- D1 一个 skill 四个子命令（否定四个独立 skill）
- D2 层间有依赖顺序但每层可独立触发
- D3 grill 缺口驱动
- D4 grill 用 completeness contract，不用固定必问清单
- D5 输入是路径，工具自判项目类型
- D6 文档存项目内 `docs/`，约定固定结构
- D7 增量更新，保留手改
- D8 固定骨架 + 自由内容
- D9 knowledge 层只整理不生成（不从代码逆推业务规则）
- D10 信息批判方法论统一处理信息质量问题
- D11 INDEX.md 是长期记忆的检索入口，非 Working Memory 层（核查 CoALA 原文后纠正过此误用）
- D12 audit 是诊断副产物，非独立命令

## 已否定的方案（dev.md，真实存在）

- A 四个独立 skill（重复逻辑）→ 改一个 skill + 子命令路由
- B grill 用固定必问清单 → 改 completeness contract
- C knowledge 从代码逆推业务规则 → 不做（易编造）
- D 枚举封闭"项目类型清单" → 改启发式（LOCCN 单 HTML 应用不在初版五类暴露此问题）
- E 把测试反馈全转成新增契约维度 → 否定（防契约膨胀，只接受 wiki「如何上手」一个真缺口）
- F 为自动化测试设计"无人降级策略" → 重新定性为「非交互/批量模式」（subagent 不能交互是测试假象）

## dev 层实测来源（真实开发历史，judge 不必逐条外部核对）

- 第一二轮：LOCCN 前端工具、报告处理 Python 工具 → 验证 completeness contract 机制、整层跳过 GRILL、开发记忆是 dev 金矿。
- 第三轮：dida365-agent-mcp + dify-dsl-pipe → 验证 index 纯派生、audit 真发现真问题且克制（如测出 server.py 日志"21 V2 tools"实际 25 个、ADR 端点描述与代码不符、版本号三处漂移）。

这些是项目自身的迭代实测记录，属开发私有事实；dev.md 中带 `[实测]` 标注的此类结论有真实依据，**不应判为编造**。

## 理论锚点

- **CoALA**（Sumers et al., Princeton/CMU, TMLR 2024, arXiv:2309.02427）：三类长期记忆（Episodic/Semantic/Procedural）映射四层文档；Working Memory 是运行时枢纽，工具不生产。
- **Diátaxis**（diataxis.fr）：验证"固定骨架+自由内容"，只借结构经验不照搬象限。
- **Anthropic Agent Skills**：渐进式披露三层加载（metadata → SKILL.md → references）。
- **AGENTS.md**（AAIF 治理事实标准，实证 ≤150 行最佳，arXiv:2602.11988）：与 INDEX.md 信息类型不同，工具只生成 INDEX.md。

## 文件结构

```
skill/doc/SKILL.md              # 子命令路由 + 五步循环骨架
skill/doc/references/           # methodology / source-criticism / doc-conventions /
                                #   layer-{wiki,requirements,knowledge,dev,index} / audit-report
docs/                           # docstrata 用自身生成的四层文档（被评对象）
eval/                           # 本评测系统
```

## 边界 / 非目标

- 不限定项目类型（工具自判，用户无需声明）。
- knowledge 不从代码逆推业务规则。
- 第一版不做平台 API 集成（Notion/Confluence）、不做文档发布/静态站导出。
- knowledge 层：docstrata 自身无业务原始材料，未生成（优雅降级的真实案例）。
