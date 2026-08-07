# Methodology — Completeness Contract & Gap-Driven Grill

每层文档靠 **completeness contract**（完整性契约）驱动，不靠固定问题清单。各生成层通用（prd/requirements/knowledge/wiki/repo-wiki/dev；index 纯派生、compact 收缩操作不走此循环）。

## 第一性原理

文档要"成立"，必须覆盖若干**信息维度**。维度稳定，契约写死在各层 reference 里；具体问什么由缺口当场算出，场景再灵活，契约不变。

```
问题 = 契约维度 − 已探索到的信息
```

> **横切方法论**：EXPLORE / MAP / GENERATE 处理多源信息时，遵循 source-criticism 准则——来源可信度排序、矛盾处理、事实 vs 推断标注、打破 LLM 先验偏向。横切方法论的入口见 SKILL.md，下文只点出各步在哪里用它。

## EXPLORE：先穷尽自动探索，主动解决 facts

先读项目，后问人。EXPLORE 的职责不仅是"读现有文档"，还包括**主动解决 agent 能查到的事实类缺口**。

### Facts vs Decisions 分离

信息缺口分两类：

- **Facts**（事实）：agent 能通过探索环境查到的——读代码、看配置、跑命令、查文档。在 EXPLORE 阶段自行解决，不留给 GRILL。
- **Decisions**（决策）：需要人类判断/拍板的——产品定位、用户优先级、设计取舍、业务规则确认。留给 GRILL。

判断标准：这个缺口能不能通过探索代码/配置/文档/运行结果得到确定答案？能 → fact，自己查；不能 → decision，问人。

### 探索来源排序

探索来源按性价比排序，可信度见 source-criticism 准则1：

1. **现有层文档** — `docs/` 下已有的 wiki/repo-wiki/requirements/knowledge/dev，互为上下文。
2. **项目自述** — README、CLAUDE.md / AGENTS.md、package.json/pyproject.toml 的 description。
3. **代码结构** — 目录树、入口文件、路由/接口定义、数据模型。
4. **扫描脚本输出** — `scripts/scan-codebase.py` 的结构化 JSON（仅 repo-wiki 层）。若脚本不可用，fallback 到手动探索代码。
5. **配置与产物** — Dify DSL（YAML）、MCP manifest、SKILL.md、CI 配置、环境变量。
6. **历史** — git log（若可用）、CHANGELOG、commit message 里的"为什么"。

**项目类型是启发式，不是封闭清单。** 先定核心交付物和逻辑所在，再定探索重心。常见类型参考：

- **全栈服务**：路由、数据模型、前后端边界、对外 API。
- **CLI/MCP/Skill**：命令/工具清单、参数 schema、调用契约。
- **Dify DSL / workflow**：节点图、输入输出变量、prompt、外部工具调用。

列表外的形态自行归纳重心，勿硬套。

### 开发记忆文件优先

开发日志是 dev 层最高价值来源。`.workbuddy/memory/`、`.claude/memory/`、`DEVLOG.md` 等 AI/人工日志直接含踩坑记录、被否定的方案、实测结论，优先级高于 git log。EXPLORE 时主动找这类文件。

## MAP：给每个维度打置信度

探索结果映射到本层契约的每个维度，打置信度标签：

| 置信度 | 含义 | 行动 |
|---|---|---|
| `high` | 上下文里有明确、一致的证据 | 直接用，不问 |
| `medium` | 有线索但可能不全/需确认 | 生成时按推断填，可在文末标注"推断" |
| `low` | 仅有微弱迹象 | 提问 |
| `missing` | 完全无信息 | 提问 |

**置信度受来源可信度调节。** 同一维度有多个来源时，按 source-criticism 准则1 排序，代码佐证 > 文档佐证。仅文档支撑、无代码佐证的，置信度不要给到 high。

**矛盾处理**：跨来源不一致时，按 source-criticism 准则2 处理，绝不静默选一个。旧文档记录已否定方案也属于此类——文档写 Flask 但代码已是纯前端。按冲突类型标 `[过期]` / `[冲突]` 或进 GRILL，并在 dev 层"已否定的方案"留痕。

## GRILL：只问 decisions，frontier 轮次

GRILL 只问 `low` / `missing` 维度中**需要人类拍板的 decisions**。Facts 已在 EXPLORE 解决。

### 核心规则

- 只对 `low` / `missing` 维度提问。`high` / `medium` 不问。
- **跳过条件**：本层所有契约维度都 ≥ `medium` 时，直接跳过 GRILL 进入 GENERATE，勿为问而问。信息充分的项目（完整需求文档/CLAUDE.md/开发日志）常常整层跳过。
- 每个问题**附带 AI 的推荐答案**，确认/纠正比从零回答省力。
- 用户回答后更新该维度置信度，继续下一个缺口。所有维度达标 → 停止提问，进入 GENERATE。
- 措辞：精确化模糊语言（"你说的'账户'指 Customer 还是 User？"）、用具体场景压边界。

### Frontier 轮次（默认模式）

每轮问出所有**前置条件已满足**的问题（frontier），编号呈现。用户按编号回答，回答后重算 frontier，下一轮问出新解锁的问题。通常 3-5 轮完成全部问题。

每个问题固定格式：
```
❓ **Q{N}** — **{标题}**
{问题体（prose 或多选）}
➡️ 推荐：{AI 的推荐答案}
```

**可配置为一次一个**：若用户在全局 CLAUDE.md/AGENTS.md 中声明偏好一次一个（如 `grill-style: one-at-a-time`），则退回逐个提问模式。

### Prototype 子动作（spike）

GRILL 过程中，若某个 decision 的答案依赖于技术可行性验证，agent 可自主发起 prototype（spike）：UI 类渲染多个方案让用户选择，技术类做最小验证测试比较不同路径。prototype 是 throwaway code，结论回馈到 GRILL 继续推进。

### 非交互 / 批量模式

用户显式要求批量静默生成，或运行在无法交互的环境时：按最佳推断填充 `low`/`missing` 维度，标 `[待确认]`；全部生成完毕后汇总输出缺口问题清单。facts 仍在 EXPLORE 解决，不受影响。

## GENERATE：固定骨架，增量更新

按本层 reference 的 section 骨架生成；文档已存在则做增量 diff，保留人类手改。

- 骨架固定（增量锚点 + 跨项目一致），内容自由。
- 文档已存在 → 逐 section diff，只重写有实质变化的段落，**保留人类手改**。
- 按 source-criticism 准则3 标注认知状态：默认 trust 事实不标，只标 `[推断]`/`[待确认]`/`[过期]`。推断不得伪装成事实。
- 遇非标实现按 source-criticism 准则4：记录项目实际行为，勿"纠正"成训练数据里的标准做法。

产出文档写作规范见 [doc-conventions.md](doc-conventions.md)。

## STAMP：留痕

头部标 `last-verified` 和行数，文末维护变更记录。

文档头部维护 `last-verified: YYYY-MM-DD`（当前日期，从环境获取，不要编造）。

**顺手标体量**：长期累积的层（尤其 dev、requirements）在 `last-verified` 行附带当前行数，如 `last-verified: 2026-06-24 | dev.md 312 行`。这是给用户的被动体量信号，要不要 `/docstrata compact` 由用户判断，不主动催、不自动跑。

文末维护变更日志，区分首次与增量：
```
## 变更记录
- 2026-06-03 首次生成
- 2026-06-10 更新 核心功能（新增批量导出）、边界
```
增量更新时追加一行：日期 + 改了哪些 section + 一句话原因。

收缩靠 `/docstrata compact` 手动触发，见 [compact.md](compact.md)。

## 小项目的优雅降级

小项目不必填满全部层。对几百行脚本、单文件应用等小工具，主动判断哪些层有实质价值：

- **prd** 个人小工具/无产品定位诉求时跳过（见 layer-prd.md），勿为没有产品决策的项目硬造主张。
- **knowledge** 无原始业务材料时跳过（见 layer-knowledge.md），勿生成空壳。
- **requirements** 有原始需求文档则有价值（固化共识）；完全没有且功能一目了然时，可在 GENERATE 时合并进 wiki 的"解决什么问题"，不单独成文。
- **wiki + dev** 几乎总有价值，是小项目的核心两层。

跑 `/docstrata all` 时，判定无价值的层勿硬生成：记录跳过原因（写入对应位置或汇报给用户），由用户决定是否仍要生成。宁可少而实，勿多而空。
