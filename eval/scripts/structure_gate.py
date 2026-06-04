#!/usr/bin/env python3
"""结构硬门：LLM 评分前的 0 成本规则检查。

检查一份层文档是否满足固定骨架与时间戳约定。不过门则红灯，
不必浪费 token 送 LLM 评分。

用法：
    python structure_gate.py <layer> <doc.md>
    python structure_gate.py --all            # 扫描 tests.yaml 里全部用例

layer ∈ {wiki, requirements, knowledge, dev, index}
退出码：0 = 全过，1 = 有用例不过门。
"""
import re
import sys
from pathlib import Path

# 每层必需的 section（取自 skill/doc/references/layer-*.md 的骨架）。
# 每个 section 给一组别名，命中任一即算覆盖——骨架标题允许中英/措辞微调，
# 字面精确匹配太脆（如 "Key Decisions" vs "关键决策"）。
REQUIRED_SECTIONS = {
    # "如何上手"不进硬门：它有上下文弹性（项目常有独立 README 覆盖启动/使用，
    # 不在 skill 生成范围）。降级到 LLM 软评的契约覆盖度，由 judge 结合上下文判断。
    "wiki": [
        ["这是什么"],
        ["解决什么问题"],
        ["核心功能"],
        ["边界"],
    ],
    "requirements": [
        ["Background", "背景"],
        ["Goals", "目标"],
        ["Non-goals", "Non-Goals", "非目标"],
        ["Key Decisions", "关键决策", "决策"],
    ],
    "knowledge": [
        ["Index", "索引"],
        ["Materials", "材料"],
    ],
    "dev": [
        ["需求到实现的映射", "需求→实现"],
        ["实践结论"],
        ["已否定的方案", "否定的方案"],
    ],
    "index": [],  # 纯派生层，无固定骨架
}

LAST_VERIFIED = re.compile(r"last-verified:\s*\d{4}-\d{2}-\d{2}")


def check(layer: str, path: Path) -> list[str]:
    """返回问题列表，空列表表示通过。"""
    if layer not in REQUIRED_SECTIONS:
        return [f"未知层类型: {layer}"]
    if not path.exists():
        return [f"文件不存在: {path}"]

    text = path.read_text(encoding="utf-8")
    problems = []

    if not LAST_VERIFIED.search(text):
        problems.append("缺 last-verified: YYYY-MM-DD 时间戳")

    headings = set(re.findall(r"^#{1,6}\s+(.+?)\s*$", text, re.MULTILINE))
    for aliases in REQUIRED_SECTIONS[layer]:
        if not any(alias in h for alias in aliases for h in headings):
            problems.append(f"缺必需 section: {aliases[0]}")

    return problems


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1

    if args[0] == "--all":
        return run_all()

    if len(args) != 2:
        print("用法: python structure_gate.py <layer> <doc.md>")
        return 1

    layer, doc = args[0], Path(args[1])
    problems = check(layer, doc)
    if problems:
        print(f"[FAIL] {doc} ({layer})")
        for p in problems:
            print(f"   - {p}")
        return 1
    print(f"[PASS] {doc} ({layer})")
    return 0


def run_all() -> int:
    """从 tests.yaml 提取所有 (layer, document) 跑门禁。"""
    try:
        import yaml
    except ImportError:
        print("--all 需要 pyyaml：pip install pyyaml")
        return 1

    root = Path(__file__).resolve().parent.parent
    tests = yaml.safe_load((root / "tests.yaml").read_text(encoding="utf-8"))

    failed = 0
    for t in tests:
        layer = t.get("layer")
        doc_ref = t.get("document", "")
        doc_path = root / doc_ref
        problems = check(layer, doc_path)
        label = f"{layer} ({doc_ref})"
        if problems:
            failed += 1
            print(f"[FAIL] {label}")
            for p in problems:
                print(f"   - {p}")
        else:
            print(f"[PASS] {label}")

    print(f"\n{len(tests) - failed}/{len(tests)} 过门")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
