<p align="center">
  <img src="docstrata-logo.svg" alt="docstrata" width="480">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" alt="License"></a>
  <img src="https://img.shields.io/badge/Agent_Skills-compatible-blue" alt="Agent Skills">
  <img src="https://img.shields.io/badge/Claude_Code-skill-orange" alt="Claude Code">
</p>

<p align="center">
  <a href="README.md">English</a> | 中文
</p>

**docstrata** — coding agent 的结构化项目记忆。分层 context 跨 session 持久化，让 agent 不用每次从零了解你的项目。

---

## 问题

现在代码生成已经很快了，真正的瓶颈其实在 context。

每次新开一个 agent session，它都是冷启动——上个月你否掉的方案、三个模块之间的隐含约束、当初选架构 B 的理由，这些它全都不知道。你得重新解释一遍，它再重新踩一遍坑，旧错误就这样反复出现。

大部分开发者都是靠手动管理 context 的：这里放个 `CONTEXT.md`，那里写几个 ADR，也许还有个共享文档。项目小的时候确实够用，但项目一大，人自己的记忆其实也靠不住。时间一长你就记不清当时的理由了，内容一多更是想不起来。三周后你说不出为什么做了那个决定，三个月后你可能连做过这个决策都忘了。

我发现之前没有一个专门的工具来做结构化的项目 context 管理。已有的方案都太轻量了——一个平面文件根本装不下一个真实项目积累的不同类别的知识。所以我就做了 docstrata。

---

## 设计思路

### 分层，因为知识本身就有类别

一个项目积累下来的知识，天然是分类别的：产品意图、历史决策、领域知识、代码结构、工程经验教训。把它们都塞在一个文件里，无论是人还是 agent，找起来都费劲。

docstrata 把每种知识单独放一层，每层有明确的受众和用途。这个分层思路参考了认知架构研究里的长期记忆分类（[CoALA](https://arxiv.org/abs/2309.02427)）：情景记忆负责记录决策和发生过的事，语义记忆存放领域知识和代码结构，程序记忆保留工程教训和实践经验。

### Grill：你投入少，系统产出大

当 docstrata 生成某一层文档的时候，它会先自己把能查的都查了——代码结构、现有文档、配置文件、git 历史。能通过查阅回答的问题，它自己解决。

留给你的只有那些真正需要你判断的问题：比如权衡取舍、优先级排序、只有你知道的约束条件。grill 机制会把这些问题按 frontier 轮次批量推出来——每轮一次性问出所有当前可以问的问题，通常 3–5 轮就能收工。

### 大道至简

好用的工具不该要求你先学一套概念体系。docstrata 之所以有分层，是因为 context 天然就有层次。之所以有 grill，是因为有些知识只存在你脑子里。除了这两点，它不会挡你的路。

---

## 功能

docstrata 是你项目的结构化记忆系统。人关心的那些 context——产品意图、业务知识、历史决策，和 coding agent 关心的那些 context——代码结构、模块关系、工程踩坑，都在同一个系统里管理。

```
prd → requirements → knowledge → [wiki, repo-wiki] → dev → index
                                    ↑ 平行，互不依赖
```

| 层 | 产出 | 内容 | 面向谁 |
|---|---|---|---|
| **prd** | `docs/prd.md` | 产品意图：定位、价值、roadmap | 团队内部 |
| **requirements** | `docs/requirements.md` | 需求共识 + 关键决策 | PM + 开发 |
| **knowledge** | `docs/knowledge/knowledge.md` | 业务材料索引 + 术语表 | 所有人 |
| **wiki** | `docs/wiki.md` | 系统全景（业务语言） | 所有人含业务 |
| **repo-wiki** | `docs/repo-wiki.md` | 代码库索引：架构/模块/技术栈/数据流 | coding agent + 开发者 |
| **dev** | `docs/dev.md` | 工程结论：踩坑、否掉的方案、非显然决策 | 工程师 + agent |
| **index** | `docs/INDEX.md` | 文档导航 + context 触发条件 | coding agent |

### 和 Matt Pocock Skills 的关系

docstrata 和 [Matt Pocock 的工程 skills](https://github.com/mattpocock/skills) 是互补的。Matt 那套 skills 管的是开发方法论——TDD、code review、spec grilling。而 docstrata 管的是这些 skills 默认你已经有的东西：让 agent 能有效工作的项目 context。两者可以配合用，也可以各自独立使用。

典型的联合工作流：

```
开发前：agent 读 repo-wiki + dev.md          → 了解代码结构和历史踩坑
开发中：/matt-grilling → /implement → /review → Matt skills 管执行纪律
开发后：/docstrata update                    → 检测变更，刷新受影响的层
```

docstrata 包住开发周期的两头：编码前加载 context，编码后检测变更并同步。中间的执行交给 Matt 的 skills。定期用 `/docstrata compact` 把膨胀的层收缩回来。

---

## 安装

```bash
npx skills add linhai0872/docstrata
```

兼容 [Agent Skills 标准](https://agentskills.io)：Claude Code、Cursor、Gemini CLI、Codex、OpenCode 等。

---

## 使用

```
/docstrata prd             # 产品意图
/docstrata requirements    # 需求共识
/docstrata knowledge       # 业务材料索引
/docstrata wiki            # 业务全景
/docstrata repo-wiki       # 代码库索引（架构/模块/技术栈）
/docstrata dev             # 开发结论
/docstrata index           # 文档导航 + context 触发条件
/docstrata compact         # 收缩膨胀的层
/docstrata update          # 检测变更，刷新受影响的层
/docstrata all             # 按依赖顺序全部生成
```

支持任意项目类型，工具会自动识别。`/docstrata all` 会跳过没有实质内容的层。

---

## 设计文档

这个项目的文档本身就是用 docstrata 的分层结构写成的：

| 文档 | 内容 |
|------|------|
| [产品主张](docs/prd.md) | 定位、价值原则、功能范围、roadmap |
| [需求与决策](docs/requirements.md) | 全部架构决策 + CoALA 理论映射 |
| [业务全景](docs/wiki.md) | 一页读懂 docstrata |
| [开发结论](docs/dev.md) | 实测记录、否掉的方案 |
| [方法论](skill/docstrata/references/methodology.md) | GRILL 机制的第一性原理 |
| [信息批判](skill/docstrata/references/source-criticism.md) | 来源排序、矛盾处理、认知标注 |
