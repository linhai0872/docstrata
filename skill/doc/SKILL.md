---
name: doc
description: Generate or maintain layered project documentation across four knowledge layers (wiki, requirements, knowledge, dev). Use when the user asks to document a project, create a wiki/readme for business people, recover/restore requirements, organize business knowledge materials, or write development notes. Works on any project type (full-stack apps, Dify DSL, CLI/MCP services, skills, or plain document folders).
---

# doc — 四层知识文档生成

按 CoALA 四层知识结构为任意项目生成/维护文档。每层是一个子命令，共享同一套执行循环。

## 子命令路由

| 命令 | 层 / 类型 | 产出 | 何时用 |
|---|---|---|---|
| `wiki` | Semantic | `docs/wiki.md` | 让所有人（含业务）快速理解整个系统 |
| `requirements` | Episodic | `docs/requirements.md` | 还原/固化需求共识与开发计划 |
| `knowledge` | Semantic | `docs/knowledge/knowledge.md` | 整理业务原始材料为可检索索引 |
| `dev` | Procedural | `docs/dev.md` | 记录开发推断与实践结论 |
| `index` | 检索入口 | `docs/INDEX.md` | 生成给 coding agent 的四层文档导航索引 |
| `all` | 全部 | 四层 + index | 按依赖顺序一次生成 |

解析用户输入：若用户说了具体层（"生成 wiki"/"还原需求"），走对应层；说"全部文档"走 `all`；不明确则问用户要哪一层。

依赖顺序（`all` 时遵循）：`requirements` → `knowledge` → `wiki` → `dev` → `index`。`index` 是最下游的派生层，从已生成的各层提炼指针，最后生成。每层生成时若上游层文档已存在，读取并引用，但不强制上游必须先存在。

`index` 详见 [references/layer-index.md](references/layer-index.md)。它不走下面的五步生成循环（无 completeness contract，是纯派生），但同样遵循增量更新与 STAMP。

`all` 不强制每层都产出。某层判定无实质价值时（如无业务材料的 knowledge、功能一目了然的小项目 requirements），按"小项目的优雅降级"（见 methodology.md）跳过，并在最终汇报里说明跳过的层和原因。宁可少而实，不要多而空。

## 诊断副产物（audit）

任何生成动作完成后，汇总 source-criticism 在 EXPLORE/MAP 阶段发现的跨 context（代码 / git / 文档 / 规范文件）信息质量问题，向用户输出一份**信息健康诊断报告**（冲突 / 过期 / 缺口 / 无主孤儿文档）。这是流程副产物，不是单独命令，不额外生成文档。详见 [references/audit-report.md](references/audit-report.md)。

## 执行循环（所有层通用）

每层都走这五步。**方法论细节见 [references/methodology.md](references/methodology.md)，务必先读。**

1. **EXPLORE** — 探索项目上下文：读现有 `docs/` 下的层文档、README、代码结构、配置。识别项目类型（代码/Dify DSL/MCP/文档集合），用对应探索策略。
2. **MAP** — 把探索到的信息映射到本层的 **completeness contract**（信息维度，见各层 reference），给每个维度打置信度（high/medium/low/missing）。
3. **GRILL** — 仅对 low/missing 维度向用户提问。一次问一个，附 AI 推荐答案，等回复再问下一个。维度全部达标则跳过。把人类当作补全 context 的工具，不重复问已知信息。
4. **GENERATE** — 按本层固定骨架生成内容。已存在则**增量更新**：diff 现有内容与新上下文，只重写有实质变化的段落，保留人类手改部分。
5. **STAMP** — 文末更新 `last-verified` 日期与本次变更摘要。

## 各层契约与骨架（按需加载）

执行某层时，读取对应 reference 获取该层的 completeness contract 和 section 骨架：

- wiki → [references/layer-wiki.md](references/layer-wiki.md)
- requirements → [references/layer-requirements.md](references/layer-requirements.md)
- knowledge → [references/layer-knowledge.md](references/layer-knowledge.md)
- dev → [references/layer-dev.md](references/layer-dev.md)
- index → [references/layer-index.md](references/layer-index.md)（纯派生，规则不同）

## 横切方法论

- [references/source-criticism.md](references/source-criticism.md)：信息批判，含来源可信度排序、矛盾处理、事实vs推断标注、打破 LLM 先验偏向。处理多源信息时遵循。
- [references/doc-conventions.md](references/doc-conventions.md)：文档写作规范，含每节带摘要、上下文自包含、Markdown 优先、避免大表格、措辞与语气、文档带时间戳。
