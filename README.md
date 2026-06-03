# doc-layers

> 一个 Claude Code Skill，为任意项目生成分层知识文档——业务 wiki、需求共识、知识库、开发结论。

---

## 它解决什么问题

代码仓库里的知识是混沌的：业务背景靠口口相传、需求意图散落在聊天记录里、开发踩过的坑在下一个人重踩、coding agent 拿到的上下文一半是过期文档。

现有工具（DeepWiki、Mintlify、Swimm）只做**技术文档**那一层。但工程师真正需要的知识有四种性质，不能混为一谈：

| 层 | 问题 | 是什么 |
|---|---|---|
| **wiki** | 这个系统是什么 | 业务全景，任何人都能读懂 |
| **requirements** | 为什么这样决策 | 需求共识 + 开发取舍的留痕 |
| **knowledge** | 做这件事需要懂什么 | 业务规则、领域材料的索引 |
| **dev** | 实际怎么做到的 | 实践结论、踩坑、被否定的方案 |

doc-layers 覆盖全部四层，且每层知道自己和其他层的关系。

---

## 理论基础

**知识分层**来自 [CoALA](https://arxiv.org/abs/2309.02427)（Sumers et al., Princeton/CMU, TMLR 2024）——认知科学研究 AI agent 记忆的论文，将持久知识分为 Episodic / Semantic / Procedural 三类长期记忆。四层文档直接对应这个分类。

**文档结构**借鉴 [Diátaxis](https://diataxis.fr)（Ubuntu、NumPy 等大规模采纳）——"固定骨架 + 自由内容"被证明是最能长期维护的文档形态。

**信息批判**来自 NATO Admiralty Code 来源分级、史学史料批判和 LLM 知识冲突研究（arXiv:2504.13079）——生成前先评估每条信息的可信度，代码比文档可信，文档比口述可信，矛盾不静默选一个。

**skill 形态**遵循 [Anthropic Agent Skills 规范](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)——渐进式披露，核心指令轻量常驻，细节按需加载。

**交互机制**受 [grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs)（Matt Pocock）启发：一次一个问题、附推荐答案、能从上下文回答的不问人。原版是领域语言精炼工具，产出 CONTEXT.md 和 ADR，grill 本身是目的。doc-layers 将其改造为**信息补全机制**：grill 是手段，由 completeness contract（信息维度集合）驱动——只对置信度不足的维度提问，所有维度达标后自动终止，进入生成阶段。

---

## 它怎么运作

```
输入：任意项目目录（代码 / Dify DSL / MCP 服务 / 文档集合……）
          │
          ▼
┌─────────────────────────────────────────────────────┐
│                   执行循环（每层）                    │
│                                                     │
│  EXPLORE ──► MAP ──► GRILL ──► GENERATE ──► STAMP   │
│    读项目      评估      缺口时      按固定       留痕  │
│    多源信息    信息      向人提问    骨架生成     时间戳 │
│              完整度              增量更新            │
│                │                                    │
│         source-criticism                            │
│    （来源可信度排序 · 矛盾检测 · 事实/推断标注）       │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│                   四层产出                           │
│                                                     │
│   requirements ──► knowledge ──► wiki ──► dev        │
│   (Episodic)      (Semantic)   (Semantic) (Procedural)│
│   需求共识           业务          系统     实践结论   │
│   开发决策           材料库        全景     踩坑记录   │
│                                    │                │
│                              INDEX.md               │
│                        （coding agent 检索入口）      │
└─────────────────────────────────────────────────────┘
          │
          ▼
    诊断副产物：信息健康报告
    （冲突 · 过期 · 版本漂移 · 缺口 · 孤儿文档）
```

**GRILL** 是结对交互机制：agent 先自动探索，只在发现信息缺口时才向用户提问，一次一个，附推荐答案。信息充分时整层跳过提问。

---

## 安装

```bash
cp -r skill/doc ~/.claude/skills/doc
```

兼容所有支持 [Agent Skills 标准](https://agentskills.io) 的工具（Claude Code、Cursor、VS Code 等）。

## 使用

```
/doc wiki            # 业务全景 → docs/wiki.md
/doc requirements    # 需求共识 → docs/requirements.md
/doc knowledge       # 整理业务材料 → docs/knowledge/knowledge.md
/doc dev             # 开发结论 → docs/dev.md
/doc index           # coding agent 检索入口 → docs/INDEX.md
/doc all             # 按依赖顺序全部生成
```

支持任意项目类型——全栈服务、Dify DSL、MCP 服务、Skill、纯文档目录，工具自动判断，无需声明。

---

## 设计文档

本项目用自身的四层结构写成（dogfooding）：

- [需求共识与全部设计决策 D1–D12](docs/requirements.md)
- [业务全景](docs/wiki.md)
- [开发推断与实践结论](docs/dev.md)
- [方法论：Completeness Contract + Gap-Driven Grill](skill/doc/references/methodology.md)
- [信息批判准则](skill/doc/references/source-criticism.md)
