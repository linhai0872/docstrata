# Layer: repo-wiki (Semantic — 代码缓存)

**代码库的索引层**——从代码自动提炼的技术全景，让 coding agent 启动时快速建立全局认知、精准定位模块、遵守架构约束。

产出：`docs/repo-wiki.md`（中小项目单文件）或 `docs/repo-wiki/`（大型项目多文件）

## 定位（先读）

repo-wiki 存的是"代码虽能复原，但提前提炼出来让 agent 不用每次从零理解的全景地图"——是**缓存**，不是结论。

### 与其他层的边界

- **wiki 层**：面向所有人（含业务），业务语言。repo-wiki 面向开发者和 coding agent，技术语言。
- **dev 层**：存 code+git 复原不出来的结论（踩坑、被否方案、非显然决策）。repo-wiki 存的是代码能复原但提炼出来省时间的结构化信息。
- **INDEX.md**：docstrata context contract 的索引。repo-wiki 是代码库的索引。两者平行。

### 对 coding agent 的三重作用

1. **启动装载**：agent 开始任务前读 repo-wiki，建立全局认知（架构、模块关系、技术栈），减少"不了解全局而瞎猜"的幻觉。
2. **定位加速**：agent 查 repo-wiki 找到"这个功能涉及哪些文件/模块"，精准打开对应代码，减少"在错误地方改代码"或"漏改关联模块"。
3. **约束注入**：repo-wiki 记录的架构约束（依赖方向、禁止的调用路径）在开发时被 agent 遵守，减少破坏架构的技术债。

## EXPLORE 特殊处理

repo-wiki 层的 EXPLORE 不靠 agent 手动读代码，而是**读取扫描脚本的结构化 JSON 输出**。

### 扫描脚本调用

```bash
python scripts/scan-codebase.py --root {项目根目录} --output docs/.repo-wiki-scan.json
```

若脚本不可用（未安装、运行失败），fallback 到手动探索代码（目录树 + 入口文件 + import 关系）。扫描结果作为 EXPLORE 的主要输入，但不取代对现有文档的读取——仍需读 wiki/dev 等层获取语义理解。

### JSON 输出格式规范

扫描脚本（或任何替代工具）必须输出符合此格式的 JSON：

```json
{
  "version": "1.0",
  "scanned_at": "ISO-8601 时间戳",
  "root": "项目根目录绝对路径",
  "summary": {
    "total_files": "number",
    "total_lines": "number",
    "languages": {"语言名": "占比 0-1"}
  },
  "entry_points": [
    {"path": "相对路径", "type": "main|cli|api|test"}
  ],
  "modules": [
    {
      "name": "模块名",
      "root_path": "模块根目录相对路径",
      "key_files": ["关键文件相对路径"],
      "imports_from": ["依赖的模块名"],
      "imported_by": ["被依赖的模块名"],
      "file_count": "number",
      "line_count": "number",
      "rank": "0-1 重要性分数（PageRank）"
    }
  ],
  "dependency_graph": {
    "模块名": ["依赖的模块名"]
  },
  "technology_stack": {
    "language": "主语言",
    "framework": "主框架",
    "build_tool": "构建工具",
    "package_manager": "包管理器",
    "key_dependencies": ["核心依赖"]
  },
  "configuration_files": [
    {"path": "相对路径", "type": "env|typescript|docker|ci|..."}
  ]
}
```

## Completeness Contract（信息维度）

借鉴 Qoder Repo Wiki 章节体系：

1. **System Overview** — 系统技术定位：用一段话说清这个代码库做什么、技术栈选择、整体规模。
2. **Technology Stack** — 语言、框架、核心依赖、构建工具、包管理器。从扫描 JSON 的 `technology_stack` 直接提取。
3. **Architecture Overview** — 整体分层/模块关系 + Mermaid 架构图。从 `dependency_graph` 生成。
4. **Module Breakdown** — 每个核心模块的职责、关键文件、公开接口、依赖关系。从 `modules` 生成，按 `rank` 排序（高重要性模块先写）。
5. **Data Flow** — 主要数据如何在模块间流转。需要 LLM 从代码结构推导（GRILL 可能需要问用户确认）。
6. **API Surface** — 对外暴露的端点/命令/工具清单。从入口文件和路由定义提取。
7. **Configuration** — 环境变量、配置文件、启动参数。从 `configuration_files` 和 .env.example 提取。
8. **Architecture Constraints** — 模块间调用规则、依赖方向、禁止的路径。需要 LLM 从依赖图推导 + GRILL 问用户确认。

## 探索重点

- **扫描 JSON 优先**：summary/modules/dependency_graph/technology_stack 直接提取。
- **代码补充**：API 路由定义、数据模型、中间件链等扫描脚本覆盖不到的语义信息。
- **上游引用**：wiki 层（如果有）提供系统目的，dev 层提供架构决策背景。
- **活跃模块优先**：若有 git log，参考最近 20 次 commit 涉及的路径，活跃模块详写，冷门模块简略。

## Section 骨架

```markdown
# Repo Wiki — {项目名}

> {一句话：这个代码库的技术定位}

last-verified: YYYY-MM-DD
scan-version: {扫描 JSON 的 scanned_at 或 hash}

## System Overview
{系统做什么，技术语言，2-3 句。规模：X 文件 / Y 行代码}

## Technology Stack
- **语言**: {主语言}
- **框架**: {主框架}
- **构建**: {构建工具}
- **包管理**: {包管理器}
- **核心依赖**: {列出关键依赖}

## Architecture Overview
{整体分层/模块关系描述}

```mermaid
graph TD
    {从 dependency_graph 生成}
```

## Modules

### {模块名}（rank: {重要性}）
- **职责**: {做什么}
- **关键文件**: {入口文件、核心文件路径}
- **公开接口**: {对外暴露的函数/类/端点}
- **依赖**: {imports_from}
- **被依赖**: {imported_by}

{按 rank 排序，高重要性模块先写。冷门模块可合并简述}

## Data Flow
{主要数据流转路径}

```mermaid
sequenceDiagram
    {主要交互序列}
```

## API Surface
{对外暴露的端点/命令/工具清单，按功能分组}

## Configuration
| 文件 | 类型 | 说明 |
|---|---|---|
| {path} | {type} | {一句话说明} |

{关键环境变量说明}

## Architecture Constraints
{模块间调用规则。以"X → Y 允许"/"X → Z 禁止"的形式写清}
- {依赖方向规则}
- {禁止的调用路径}
- {分层约束}
```

## Grill 示例（仅 decisions）

- Data Flow missing：「扫描能看到模块间的 import 关系，但主要的业务数据（比如订单/用户）是怎么在这些模块间流转的？从哪进来、经过哪些处理、最终存到哪？」
- Architecture Constraints low：「依赖图显示 {模块A} 和 {模块B} 互相引用。这是有意的双向依赖还是需要解耦的技术债？有没有架构上"不应该直接调用"的规则？」

## 大型项目拆分

文件超过 200 行时拆分为目录结构：

```
docs/repo-wiki/
├── README.md          # System Overview + Technology Stack + Architecture Overview
├── modules/
│   ├── {module-a}.md  # 单个模块详解
│   └── {module-b}.md
├── data-flow.md       # Data Flow
├── api-surface.md     # API Surface
└── constraints.md     # Architecture Constraints + Configuration
```

拆分后 `docs/repo-wiki/README.md` 作为入口，包含指针到各子文件。
