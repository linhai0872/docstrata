# docstrata 评测闭环

给 **skill 作者**用的开发期工具：改了 `methodology.md` 或某层契约后，验证这次迭代是真改进还是退步。不进用户的安装包。

docstrata 的迭代过去全靠"我觉得变好了"。这套评测把"觉得"换成可重复的分数：改动前后跑同一组项目，对比每层得分。

## 设计取舍

- **reference-free**：judge 拿「生成的文档 + 项目上下文」按 rubric 打分，不维护"标准答案"。项目本身就是 ground truth，省掉维护标准答案这份最大的人工成本。
- **三档可选**：结构硬门（零依赖）→ 单 judge（快）→ 多 judge ensemble（严谨）。
- **ensemble 去相关**：多个不同厂商的 judge 独立打分，取**中位数**（抗单家极端值），报**极差**作分歧度；分歧大说明该用例评分不可信，需人工复核。
- **rubric 复用 source-criticism**：评分维度直接用 docstrata 已有的认知状态体系（事实/推断标注），不另起一套。

## 三段分档

| 档 | 工具 | 依赖 | 何时用 |
|---|---|---|---|
| **0 结构硬门** | `scripts/structure_gate.py` | 纯 Python，无 key 无网络 | 随手筛结构问题，CI 阻塞门 |
| **1 单 judge** | `judge_runner.py`（启用 1 个 judge） | 一个 API key | 日常迭代快速看分 |
| **2 ensemble** | `judge_runner.py`（启用 ≥2 个 judge） | 多个 key（或一个聚合 key） | 发版/重大改动，要可信判定 |

结构硬门检查固定骨架是否完整、`last-verified` 在不在，不过门直接阻塞。
LLM judge 按 5 维度各 0-3 打分（契约覆盖度 / 来源忠实度 / 认知状态准确 / 受众适配 / 层专属），归一化 ≥ 0.7 为 pass。

## 配置 judge（换厂商只改 `judges.yaml`，不碰代码）

两类协议覆盖所有主流服务：

- `protocol: openai`：OpenAI 及一切兼容端点：官方 / **Ollama**（本地离线）/ OpenRouter / ZenMux / vLLM / DeepSeek 官方 …
- `protocol: anthropic`：Anthropic 官方 Messages API

`judges.yaml` 默认配置了一组去相关 ensemble（DeepSeek / OpenAI / 阿里，经 ZenMux 聚合）。换成自己的端点，照文件里的注释范例修改 `base_url` + `model` + `api_key_env`。启用 1 个 = 快速档，启用 ≥2 个 = ensemble。

## 跑

```bash
cd eval

# 第 0 档：结构硬门（免 key，先跑）
python3 scripts/structure_gate.py --all

# 第 1/2 档：LLM 评分
cp .env.example .env && vi .env     # 填 judges.yaml 用到的 key（Ollama 无需 key）
pip install pyyaml                  # runner 唯一依赖
python3 scripts/judge_runner.py     # 单/多 judge 由 judges.yaml 的 enabled 决定
```

## 闭环工作流 + grill 式复盘

```
改 methodology / 某层契约
   │
   ├─► 对 golden set 跑 docstrata 生成产物
   ├─► python3 scripts/structure_gate.py --all     # 硬门
   ├─► python3 scripts/judge_runner.py             # 打分 → runs/latest.json
   └─► grill 式复盘（下方提示词），人只做最小决策
```

**grill 式复盘**是评测的收尾。用 `/grill-with-docs` 的范式（一次一个、附推荐答案、agent 起草人审批）处理改进项：agent 负责**发现+起草**，人只**决策**。跑完评测后，把下面这段交给 agent：

> 读 `eval/runs/latest.json` 和各 judge 的 reason。按以下规则带我复盘，一次抛一项，等我回复再下一项：
> 1. **真信号**（多 judge 收敛批评同一点）：说明问题 + 影响哪些层 + 你建议的改法 + 起草具体 diff，让我选 `采纳 / 跳过 / 改方案`。
> 2. **待复核**（极差 ≥0.2 的分歧项）：这是 judge 分歧，需我判是真问题还是误读。给出你的看法 + 证据，让我 `确认 / 否决`。
> 3. **疑似评测自身问题**（如某 judge 把项目真实存在的东西判为编造）：标出来，建议改 `context.md` 或 rubric 校准，而非改文档。
> 我确认后你再执行修改，改完重跑评测对比上一轮。

**区分真改进和噪声**：v1 用简易法，同一文档跑 2-3 次看分数波动（judge 有 temperature=0 但仍有微抖动），波动盖过的差异不算数。积累十几轮数据后再考虑算正式噪声基线（σ₀）。

## 文件

```
eval/
├── judges.yaml            # judge 端点/模型/参数（换厂商改这里）
├── tests.yaml             # 评测用例：runner 与 structure_gate 共用的单一用例源
├── rubric/
│   ├── _judge.md          # judge 模板：通用四维度 + 校准规则 + 输出格式
│   └── {wiki,requirements,knowledge,dev}.md   # 各层契约 + 专属维度
├── scripts/
│   ├── structure_gate.py  # 第 0 档：结构硬门（纯 Python）
│   └── judge_runner.py    # 第 1/2 档：LLM 评分 + ensemble 聚合
├── projects/              # golden set（输入项目 + context.md）
└── runs/latest.json       # 最近一轮分数（供 grill 复盘读取）
```

## 加项目

见 [projects/README.md](projects/README.md)。首批用 docstrata 自身跑通，扩 golden set 时加开源项目 + dify-dsl-pipe。
