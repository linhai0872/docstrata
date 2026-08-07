# Update — 变更驱动的增量刷新

检测项目变更，判断哪些层文档可能过期，按影响面批量刷新。手动或自动触发。

## 定位

`update` 补上 docstrata 工作流的"结尾自驱"——开发完成后，自动检测什么变了、哪些层受影响、执行刷新。与 Context Triggers（INDEX.md 的被动指引"新认知写到哪"）互补：triggers 告诉 agent 该往哪写，`update` 检测写了之后哪些层需要同步。

```
开发前：INDEX Context Triggers → agent 读对应层
开发中：docstrata 不参与
开发后：/docstrata update → 检测变更 → 刷新受影响的层
```

## 触发方式

```
/docstrata update              # 交互模式：报告影响面，确认后刷新
/docstrata update --auto       # 自动模式：跳过确认，直接刷新
/docstrata update --dry-run    # 只报告，不刷新
```

默认交互模式。`--auto` 适合 CI / git hook / loop 场景。

## 执行步骤

### 1. 收集变更信号

从两个来源检测变更：

- **git diff**：`git diff --stat` 对比 HEAD 与各层 `last-verified` 时间点的差异。若 git 不可用，fallback 到文件 mtime。
- **层文档 last-verified 时间戳**：各层 `docs/*.md` 头部的 `last-verified` 日期，与当前日期的间隔。

输出：变更文件清单 + 变更类型（新增 / 修改 / 删除）。

### 2. 影响面映射（启发式）

按变更文件的类型和位置，映射到可能受影响的层：

| 变更信号 | 受影响的层 | 理由 |
|---|---|---|
| `src/` 下结构变更（新增/删除/移动文件或目录） | **repo-wiki** | 代码结构变了，索引过期 |
| `src/` 下逻辑变更（修改已有文件） | **dev** | 可能有新踩坑、新决策 |
| `docs/knowledge/raw/` 或 `sources.yaml` 变更 | **knowledge** | 原始材料变了 |
| `prd.md` 手动修改 | **wiki** | wiki 引用 prd 的定位/价值 |
| `requirements.md` 手动修改 | **wiki**, **dev** | 新决策可能影响全景和工程结论 |
| `package.json` / `pyproject.toml` / 配置文件变更 | **repo-wiki** | 技术栈或依赖变了 |
| 任何层文档的 `last-verified` 超过 14 天 | **该层** | 时效性下降（弱信号，仅提示） |

映射规则是启发式，不是精确依赖分析。宁可多报不漏报——用户确认时可以跳过不需要的层。

### 3. 输出影响面报告

格式：

```
## docstrata update report

检测范围：git diff HEAD~15 (since 2026-07-25)

受影响的层：
  ● repo-wiki  — src/ 下 12 文件变更（3 新增、2 删除、7 修改）
  ● dev        — src/ 有逻辑变更，可能有新踩坑
  ○ wiki       — prd.md 14 天未更新（弱信号）

建议刷新顺序：repo-wiki → dev → wiki

确认刷新？(y/n/选择性跳过)
```

`●` = 强信号（有实质变更），`○` = 弱信号（仅时效性）。

### 4. 执行刷新

确认后，按层间依赖顺序（上游先于下游）逐层执行标准五步循环。每层走的是正常的 EXPLORE → MAP → GRILL → GENERATE → STAMP，与直接跑 `/docstrata {layer}` 完全一致。

`update` 的价值在步骤 1-3（检测+映射+报告），步骤 4 复用已有逻辑。

刷新完毕后，更新 `docs/INDEX.md` 的 `last-verified`。

### 5. 诊断副产物

与其他层一样，刷新过程中产出信息健康诊断（audit）。`update` 的 audit 额外标注：哪些层被刷新了、哪些被跳过了、跳过的理由。

## --auto 模式的行为

- 跳过步骤 3 的确认环节，直接刷新所有 `●` 强信号层
- `○` 弱信号层默认跳过（只有强信号才自动刷新）
- 无变更检测到时静默退出（no-op）
- 适合作为 git post-commit hook 或 CI step

## 边界

- `update` 检测的是"哪些层可能过期"，具体刷新走标准五步循环——不是一套独立的生成逻辑
- 影响面映射是启发式，有假阳性（报了但其实不需要更新），没有假阴性保证
- 不替代 `compact`：`update` 管"同步到最新"，`compact` 管"收缩膨胀"，两个独立操作
- 不替代手动跑单层：用户明确知道要刷哪一层时，直接 `/docstrata {layer}` 更快
