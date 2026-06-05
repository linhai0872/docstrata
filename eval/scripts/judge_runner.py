#!/usr/bin/env python3
"""docstrata 文档质量评测 runner —— LLM judge 打分 + ensemble 聚合。

判分链路：每个 enabled judge 按 rubric/_judge.md 给一份文档打 5 维分，归一化到 0-1。
- 启用 1 个 judge  → 快速档，直接出分。
- 启用 ≥2 个 judge → ensemble：取中位数为综合分（抗单家极端值），并报极差 spread
  作为分歧度。分歧大说明该用例评分不可信，建议人工复核。

配置：
  judges.yaml  —— judge 端点/模型/参数（换厂商只改这里，支持 OpenAI 兼容 + Anthropic）
  tests.yaml   —— 评测用例（与 structure_gate 共用）
  .env         —— 各 provider 的 API key

跑：python3 scripts/judge_runner.py
"""

import json
import os
import re
import statistics
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent.parent

try:
    import yaml
except ImportError:
    sys.exit("需要 pyyaml：pip install pyyaml")


def load_env():
    """把 eval/.env 读进 os.environ（不覆盖已有值）。"""
    envf = EVAL_DIR / ".env"
    if not envf.exists():
        return
    for line in envf.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def resolve(value: str) -> str:
    """支持 judges.yaml 中的 $VAR_NAME 语法，从环境变量读取实际值。"""
    if isinstance(value, str) and value.startswith("$"):
        return os.environ.get(value[1:], "")
    return value


def load_config():
    cfg = yaml.safe_load((EVAL_DIR / "judges.yaml").read_text())
    judges = [j for j in cfg.get("judges", []) if j.get("enabled")]
    if not judges:
        sys.exit("judges.yaml 里没有 enabled 的 judge")
    return judges, cfg.get("params", {})


def load_cases():
    return yaml.safe_load((EVAL_DIR / "tests.yaml").read_text())


def build_prompt(case):
    tmpl = (EVAL_DIR / "rubric" / "_judge.md").read_text()
    rubric = (EVAL_DIR / case["rubric"]).read_text()
    ctx = (EVAL_DIR / case["context"]).read_text()
    doc = (EVAL_DIR / case["document"]).read_text()
    return (tmpl.replace("{{rubric}}", rubric)
                .replace("{{project_context}}", ctx)
                .replace("{{output}}", doc))


def extract_json(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _post(url, headers, body, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def call_openai(judge, prompt, params):
    """OpenAI 及一切兼容端点（Ollama/OpenRouter/ZenMux/vLLM…）。"""
    key = os.environ.get(judge.get("api_key_env") or "", "")
    base_url = resolve(judge["base_url"])
    model = resolve(judge["model"])
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    body = {
        "model": model,
        "temperature": params.get("temperature", 0),
        "max_tokens": params.get("max_tokens", 16000),
        "messages": [{"role": "user", "content": prompt}],
    }
    d = _post(base_url.rstrip("/") + "/chat/completions",
              headers, body, params.get("timeout_s", 300))
    return d["choices"][0]["message"].get("content") or ""


def call_anthropic(judge, prompt, params):
    """Anthropic 官方 Messages API。"""
    key = os.environ.get(judge.get("api_key_env") or "", "")
    base_url = resolve(judge["base_url"])
    model = resolve(judge["model"])
    headers = {
        "Content-Type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
    }
    body = {
        "model": model,
        "max_tokens": params.get("max_tokens", 16000),
        "temperature": params.get("temperature", 0),
        "messages": [{"role": "user", "content": prompt}],
    }
    d = _post(base_url.rstrip("/") + "/v1/messages",
              headers, body, params.get("timeout_s", 300))
    blocks = [b.get("text", "") for b in d.get("content", []) if b.get("type") == "text"]
    return "".join(blocks)


PROTOCOLS = {"openai": call_openai, "anthropic": call_anthropic}


def call_judge(judge, prompt, params):
    fn = PROTOCOLS.get(judge.get("protocol", "openai"))
    if not fn:
        return {"error": f"未知 protocol: {judge.get('protocol')}"}
    last = None
    for _ in range(params.get("retries", 2)):
        try:
            content = fn(judge, prompt, params)
            parsed = extract_json(content)
            if parsed and "score" in parsed:
                return parsed
            last = "解析失败：" + repr(content[:120])
        except Exception as e:  # noqa: BLE001 — 网络/超时统一重试
            last = str(e)
    return {"error": last}


def run_case(case, judges, params):
    prompt = build_prompt(case)
    out = {}
    with ThreadPoolExecutor(max_workers=len(judges)) as ex:
        futs = {ex.submit(call_judge, j, prompt, params): j["name"] for j in judges}
        for fut in futs:
            out[futs[fut]] = fut.result()
    return case["layer"], out


def main():
    load_env()
    judges, params = load_config()
    cases = load_cases()
    mode = "单 judge 快速档" if len(judges) == 1 else f"{len(judges)} judge ensemble（综合=中位数）"

    with ThreadPoolExecutor(max_workers=len(cases)) as ex:
        results = list(ex.map(lambda c: run_case(c, judges, params), cases))

    report = {}
    print("\n" + "=" * 78)
    print(f"docstrata 文档评测  ·  {mode}  ·  temperature={params.get('temperature', 0)}")
    print("=" * 78)
    for layer, judged in results:
        scores = {}
        print(f"\n## {layer}")
        for j in judges:
            name = j["name"]
            r = judged.get(name, {})
            if "error" in r:
                print(f"  {name:<14} [失败] {r['error'][:78]}")
            else:
                s = round(float(r.get("score", 0)), 2)
                scores[name] = s
                print(f"  {name:<14} {s:<6} {r.get('reason', '')[:68]}")
        vals = list(scores.values())
        if not vals:
            report[layer] = {"error": "all judges failed"}
            continue
        if len(vals) == 1:
            score = vals[0]
            verdict = "PASS" if score >= 0.7 else "FAIL"
            print(f"  {'判定':<12} {score}  [{verdict}]")
            report[layer] = {"score": score, "verdict": verdict, "scores": scores}
        else:
            med = round(statistics.median(vals), 2)
            spread = round(max(vals) - min(vals), 2)
            flag = "  ⚠ 分歧大，建议人工复核" if spread >= 0.2 else ""
            verdict = "PASS" if med >= 0.7 else "FAIL"
            print(f"  {'综合(中位数)':<10} {med}  [{verdict}]  极差={spread}{flag}")
            report[layer] = {"median": med, "spread": spread, "verdict": verdict, "scores": scores}

    out_path = EVAL_DIR / "runs" / "latest.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n报告已存：{out_path.relative_to(EVAL_DIR)}")


if __name__ == "__main__":
    main()
