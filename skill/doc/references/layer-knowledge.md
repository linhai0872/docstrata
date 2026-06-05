# Layer: knowledge (Semantic)

业务专属的**原始材料库**：规章制度、业务规则、流程文档等 raw data。需求通常附带这类材料。

**本层只整理 + 索引，不生成、不从代码逆推业务规则。** 工具是导读员，不是作者。

**与 requirements 层的边界**：需求文档（PRD、需求 txt、需求 issue）属于 **requirements 层**，表达"需求方想要什么"。knowledge 层只收业务领域的**原始事实材料**：规章制度、业务规则、行业标准、流程规范，即"做这件事必须遵守/了解的客观知识"。判断标准：这份材料就算换一个项目做同样业务也仍然成立 → knowledge；它是针对本项目提出的诉求 → requirements。

产出：`docs/knowledge/knowledge.md`（索引/导读层），原始材料保留在 `docs/knowledge/raw/` 与外部源。

## Completeness Contract（信息维度）

1. **原始材料来源** — 材料在哪？本地 `docs/knowledge/raw/`（任意格式：PDF/Word/Markdown/…）+ `docs/knowledge/sources.yaml` 列的外部 URL。
2. **业务规则提炼** — 每份材料里的关键规则/约束/术语，提炼成可检索摘要。
3. **分类索引** — 按主题给材料分组、打标签，让其他层能快速定位引用。

## 输入约定

```
docs/knowledge/
├── knowledge.md      # 本层产出：索引 + 摘要 + 规则提炼
├── raw/              # 用户放置的本地原始材料（工具只读不改）
└── sources.yaml      # 外部 URL 列表
```

`sources.yaml` 格式：
```yaml
sources:
  - url: https://example.com/business-rule-doc
    title: 退款政策 v3
    tags: [refund, policy]
```

## 处理流程

1. 扫描 `raw/` 下所有文件 + `sources.yaml` 的 URL（URL 用 WebFetch 抓取）。
2. 每份材料生成一个条目：摘要、关键规则提炼、标签、原文件/URL 链接。
3. 按标签/主题聚类，生成索引。
4. **不动原始文件**。`knowledge.md` 是它们的导读层。
5. 缺材料时不臆造：若 `raw/` 与 `sources.yaml` 都空，提示用户放入材料，不要从代码编业务规则。

## Section 骨架

```markdown
# Knowledge — {项目名}

> {一句话：这个项目涉及哪些业务领域的原始知识}

last-verified: YYYY-MM-DD

## Index
{按主题/标签分组的材料清单，每项链到下方条目}

## Materials
### {材料标题}
- **来源**: {raw/xxx.pdf 或 URL}
- **标签**: {tag1, tag2}
- **摘要**: {这份材料讲了什么}
- **关键规则**: {提炼出的业务规则/约束/术语，列表}

## Glossary
{从材料中提炼的业务术语权威定义，供其他层引用}
```

## Grill 示例（仅缺口）

- 来源 missing：「`docs/knowledge/raw/` 和 `sources.yaml` 都是空的。请把业务原始材料放进 raw/ 目录，或在 sources.yaml 里列出外部链接，我再来整理。」
- 分类 low：「这几份材料我按 {退款, 风控, 物流} 分了类——分类合理吗？还是有你们内部更习惯的归类方式？」
