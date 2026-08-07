# docstrata — 文档索引

> Project Context System：按知识性质分层管理项目认知资产，让 coding agent 带着正确 context 开发。

last-verified: 2026-08-07

本项目的知识按分层组织。按需取用：

| 想了解 | 读这个 | 内容 |
|---|---|---|
| 产品定位、做什么、roadmap | [docs/prd.md](prd.md) | 对内产品主张（前瞻 intent） |
| 系统是什么、能做什么 | [docs/wiki.md](wiki.md) | 业务全景，所有人可读 |
| 代码架构、模块、技术栈 | [docs/repo-wiki.md](repo-wiki.md) | 代码库索引，给 coding agent 用 |
| 需求共识、为什么这样定 | [docs/requirements.md](requirements.md) | 需求 + 开发计划 + 关键决策 |
| 业务规则、领域知识 | [docs/knowledge/knowledge.md](knowledge/knowledge.md) | 业务原始材料索引 |
| 实现结论、踩坑、已否定方案 | [docs/dev.md](dev.md) | 开发推断与实践事实 |

操作约定（构建/测试/红线）：见项目根目录 README.md 的使用章节。

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
- 2026-06-03 首次生成
- 2026-08-07 v2 重写：新增 repo-wiki 指针、Context Contract 改为条件触发式（context not control）
