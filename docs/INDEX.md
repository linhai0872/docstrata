# docstrata — 文档索引

> 一个 Claude Code Skill，按知识性质分层为任意项目生成/维护文档。

last-verified: 2026-06-24

本项目的知识按性质分层组织，按需取用：

| 想了解 | 读这个 | 内容 |
|---|---|---|
| 产品定位、价值原则、roadmap | [docs/prd.md](prd.md) | 对内产品主张（前瞻 intent） |
| 系统是什么、能做什么 | [docs/wiki.md](wiki.md) | 业务全景，所有人可读 |
| 需求共识、为什么这样定 | [docs/requirements.md](requirements.md) | 需求 + 全部设计决策 |
| 实现结论、设计取舍 | [docs/dev.md](dev.md) | 开发推断与实践事实 |

skill 本体在 [skill/docstrata/](../skill/docstrata/)，核心方法论见 `skill/docstrata/references/methodology.md` 与 `source-criticism.md`。

（knowledge 层无业务原始材料，未生成。）

## 变更记录
- 2026-06-24 skill 更名为 docstrata，路径 `skill/docstrata/`，命令 `/docstrata`
- 2026-06-24 新增 prd 层指针，同步至分层结构
- 2026-06-03 首次生成
- 2026-06-24 文风重构
