# Layer: index（检索入口 + Context Triggers）

**文档层的导航索引 + 各层触发条件**——轻量指针指向各层，不复制内容；告诉 agent 项目知识在哪、什么情况下该读哪一层、新认知该写到哪里。

产出：`docs/INDEX.md`

## 定位（重要，先读）

INDEX.md **不是** CoALA 的 Working Memory 层。Working Memory 是 agent **运行时**的活跃 context 中央枢纽，文档工具不生产它。INDEX.md 是五层**长期记忆**的检索入口，优化 agent 把长期记忆装填进运行时 context 的路径。

**与 AGENTS.md 划清边界**（两者信息类型不同，不混写）：
- **AGENTS.md**（事实标准，AAIF 治理）= "怎么干活"的操作契约：构建/测试命令、代码约定、红线。定位精简（实证 ≤150 行，过长反降低 agent 成功率）。
- **INDEX.md** = "知识在哪"的导航：指向各层文档。

本工具只生成 INDEX.md。AGENTS.md 是否生成/维护，不在本工具职责内。若项目已有 AGENTS.md/CLAUDE.md，可在 INDEX.md 里反向提一句"操作约定见 AGENTS.md"，但不改它。

**不做**：运行时动态 memory（对话提炼的踩坑/经验，如 Anthropic memory tool、Mem0）由 agent 运行时自己写，本工具不生成。

## 生成方式（纯派生，不走五步循环）

INDEX.md 没有 completeness contract、不 GRILL。从**已存在的层文档**机械派生：

1. 扫描 `docs/` 下存在哪些层文档（prd/wiki/repo-wiki/requirements/knowledge/dev）。
2. 为每个存在的层生成一行指针：路径 + 一句话“里面有什么、何时该读”。
3. 提炼项目一句话身份（从 wiki 的电梯陈述取）。
4. **生成 context triggers section**：定义各层的触发条件和新认知的落地位置。
5. 不存在的层不写指针。所有层都不存在时，提示用户先生成至少一层。

## 精简纪律（硬约束）

INDEX.md 必须克制。实证（arXiv:2602.11988）：臃肿的 agent context 文件会降低成功率、增加成本。

- **只放指针，不放内容**。知识在各层里，INDEX 只给地址和"何时读"。
- 全文**目标 20-30 行，上限 60 行**。上限是红线不是目标：别为了"写够"而注水。
- 不重复各层已有的描述。一层一行足够。
- 不放构建命令、代码约定（那是 AGENTS.md 的事）。

## Section 骨架

```markdown
# {项目名} — 文档索引

> {一句话项目身份，取自 wiki 电梯陈述}

last-verified: YYYY-MM-DD

本项目的知识按分层组织。按需取用：

| 想了解 | 读这个 | 内容 |
|---|---|---|
| 产品定位、做什么、roadmap | [docs/prd.md](prd.md) | 对内产品主张（前瞻 intent） |
| 系统是什么、能做什么 | [docs/wiki.md](wiki.md) | 业务全景，所有人可读 |
| 代码架构、模块、技术栈 | [docs/repo-wiki.md](repo-wiki.md) | 代码库索引，给 coding agent 用 |
| 需求共识、为什么这样定 | [docs/requirements.md](requirements.md) | 需求 + 开发计划 + 关键决策 |
| 业务规则、领域知识 | [docs/knowledge/knowledge.md](knowledge/knowledge.md) | 业务原始材料索引 |
| 实现结论、踩坑、已否定方案 | [docs/dev.md](dev.md) | 开发推断与实践事实 |

操作约定（构建/测试/红线）：见 {实际存在的那个：AGENTS.md / CLAUDE.md / README 的开发章节}。

## 什么场景读哪层

- 不熟悉代码结构、需要定位模块 → repo-wiki
- 碰到非显然约束、历史踩坑、被否方案 → dev.md
- 质疑某个过去的决策或其理由 → requirements.md
- 不确定产品方向或功能范围 → prd.md

## 新认知写到哪

- 踩坑、被否方案、非显然决策 → dev.md
- 架构或模块变更 → 跑 `/docstrata repo-wiki` 刷新
- 术语变更 → 更新 CONTEXT.md，下次 `/docstrata knowledge` 自动回收

## 变更记录
- YYYY-MM-DD 首次生成
```

规则：
- 只为实际存在的层生成表格行。
- "操作约定"那行指向项目里实际存在的载体：优先 AGENTS.md / CLAUDE.md，都没有则指向 README 的开发/使用章节；若连这些都没有，删掉这行，不要硬写一个不存在的文件。
- 跳过的层可加一行说明（如"knowledge 层无原始材料，已跳过"），让 INDEX 的能力边界可见，比什么都不写更诚实。
