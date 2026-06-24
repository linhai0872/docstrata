# golden set

评测的输入项目。每个项目锁定版本，长期跟踪。

## 结构

```
projects/
├── own/                    # 自有项目（你最懂业务，能判生成内容准不准）
│   └── docstrata/
│       ├── context.md      # ground truth 摘要（judge 核对来源忠实度用）
│       └── output/         # docstrata 对该项目生成的产物（评测对象）
└── oss/                    # 开源项目（测通用性，省力；用 git submodule 锁版本）
    └── <repo>/
        ├── context.md
        └── output/
```

> docstrata 自身是特例：它的产物就是仓库根的 `docs/`，tests.yaml 直接指向 `../docs/`，不放 output/。

## 加一个项目

1. **放代码**
   - 自有项目：拷贝或软链到 `own/<name>/`
   - 开源项目：`git submodule add <url> oss/<name>/repo` —— submodule 锁 commit，保证可复现
2. **写 context.md** — 项目定位 + 文件树 + 核心事实（参考 `own/docstrata/context.md`）。不必全量代码，judge 用它核对大方向。
3. **生成产物** — 在 agent 里用 docstrata 的非交互模式对该项目跑 `/docstrata all`，把产出的 `wiki.md` 等放进 `<name>/output/`。
4. **登记用例** — 在 `../tests.yaml` 追加 (项目 × 层)。

## golden set 选型建议（混合）

| 形态 | 来源 | 挑选标准 |
|---|---|---|
| 全栈 / Web 服务 | 开源 | 中小型、文档半全不全（文档过全会让 GRILL 整层跳过，测不出机制） |
| CLI 工具 | 开源 | 命令清晰，Node 或 Python |
| 单文件 / 纯前端 / MCP | 开源 | 测非标形态 |
| Skill | 自有 | docstrata 自身（已就位） |
| Dify / CLI | 自有 | dify-dsl-pipe |

避开 react/vue 这类文档极全的大项目——docstrata 会整层跳过 GRILL，且你不懂其业务，judge 失去参照系。
