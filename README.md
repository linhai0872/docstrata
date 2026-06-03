# doc-layers

一个 Claude Code Skill，按 [CoALA](https://arxiv.org/abs/2309.02427) 四层知识结构为任意项目生成/维护文档。

## 四层

| 子命令 | CoALA 层 | 产出 | 用途 |
|---|---|---|---|
| `wiki` | Semantic | `docs/wiki.md` | 业务全景，所有人可读 |
| `requirements` | Episodic | `docs/requirements.md` | 需求共识 + 开发计划 |
| `knowledge` | Semantic | `docs/knowledge/knowledge.md` | 业务原始材料整理+索引 |
| `dev` | Procedural | `docs/dev.md` | 开发推断与实践结论 |

## 安装

把 `skill/doc/` 复制到你的 skill 目录：

```bash
cp -r skill/doc ~/.claude/skills/doc
```

## 使用

在目标项目里：

```
/doc wiki            # 生成业务 wiki
/doc requirements    # 还原/固化需求
/doc knowledge       # 整理业务材料（先把材料放进 docs/knowledge/raw/）
/doc dev             # 生成开发结论
/doc all             # 按依赖顺序全部生成
```

工具会先自动探索项目上下文，只在信息有缺口时向你提问。

## 设计

本项目自身的文档即用四层结构写成（dogfooding），见 [`docs/`](docs/)：
- [需求共识与全部设计决策](docs/requirements.md)
- [业务全景](docs/wiki.md)

核心方法论见 [`skill/doc/references/methodology.md`](skill/doc/references/methodology.md)。
