#!/usr/bin/env python3
"""
docstrata repo-wiki 扫描脚本 v1

从代码库提取结构化信息，输出 JSON 供 repo-wiki 层的 EXPLORE 阶段消费。
无 LLM 调用，纯静态分析。

用法：
    python scan-codebase.py --root /path/to/project --output docs/.repo-wiki-scan.json

替换：任何输出符合 layer-repo-wiki.md 定义的 JSON 格式规范的工具都可以替代本脚本。
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ─── 配置 ───────────────────────────────────────────────────────────────────

IGNORE_DIRS = {
    'node_modules', '.git', '.next', '.nuxt', '__pycache__', '.pytest_cache',
    'dist', 'build', 'out', '.output', 'coverage', '.nyc_output', 'vendor',
    '.venv', 'venv', 'env', '.env', 'target', '.gradle', '.idea', '.vscode',
    '.docstrata', '.qoder', '.cursor', '.claude',
}

IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'bun.lockb',
    'Cargo.lock', 'poetry.lock', 'Pipfile.lock', 'composer.lock',
}

LANGUAGE_EXTENSIONS = {
    '.ts': 'TypeScript', '.tsx': 'TypeScript', '.js': 'JavaScript',
    '.jsx': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
    '.py': 'Python', '.go': 'Go', '.rs': 'Rust', '.java': 'Java',
    '.kt': 'Kotlin', '.swift': 'Swift', '.rb': 'Ruby', '.php': 'PHP',
    '.cs': 'C#', '.cpp': 'C++', '.c': 'C', '.h': 'C', '.hpp': 'C++',
    '.vue': 'Vue', '.svelte': 'Svelte', '.dart': 'Dart',
    '.md': 'Markdown', '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
    '.toml': 'TOML', '.sql': 'SQL', '.sh': 'Shell', '.bash': 'Shell',
}

CONFIG_FILE_PATTERNS = {
    '.env.example': 'env', '.env.local': 'env', '.env': 'env',
    'tsconfig.json': 'typescript', 'jsconfig.json': 'javascript',
    'package.json': 'node', 'pyproject.toml': 'python',
    'Cargo.toml': 'rust', 'go.mod': 'go', 'Gemfile': 'ruby',
    'docker-compose.yml': 'docker', 'docker-compose.yaml': 'docker',
    'Dockerfile': 'docker', '.dockerignore': 'docker',
    '.github/workflows': 'ci', '.gitlab-ci.yml': 'ci',
    'Makefile': 'build', 'justfile': 'build',
}

ENTRY_POINT_PATTERNS = [
    ('src/index.ts', 'main'), ('src/index.js', 'main'), ('src/main.ts', 'main'),
    ('src/main.py', 'main'), ('main.go', 'main'), ('src/lib.rs', 'main'),
    ('src/app.ts', 'main'), ('src/app.js', 'main'), ('app.py', 'main'),
    ('src/cli.ts', 'cli'), ('src/cli.js', 'cli'), ('cli.py', 'cli'),
    ('src/server.ts', 'api'), ('src/server.js', 'api'), ('server.py', 'api'),
    ('index.html', 'main'), ('src/index.html', 'main'),
]


# ─── 扫描逻辑 ─────────────────────────────────────────────────────────────────

def should_ignore(path: Path, root: Path) -> bool:
    """判断路径是否应被忽略"""
    parts = path.relative_to(root).parts
    for part in parts:
        if part in IGNORE_DIRS:
            return True
    if path.is_file() and path.name in IGNORE_FILES:
        return True
    return False


def scan_files(root: Path) -> list[Path]:
    """扫描所有源码文件"""
    files = []
    for path in root.rglob('*'):
        if path.is_file() and not should_ignore(path, root):
            files.append(path)
    return files


def detect_languages(files: list[Path]) -> dict[str, float]:
    """检测语言占比"""
    lang_lines = defaultdict(int)
    total_lines = 0
    for f in files:
        ext = f.suffix.lower()
        if ext in LANGUAGE_EXTENSIONS:
            try:
                lines = len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
                lang_lines[LANGUAGE_EXTENSIONS[ext]] += lines
                total_lines += lines
            except (OSError, UnicodeDecodeError):
                pass
    if total_lines == 0:
        return {}
    return {lang: round(lines / total_lines, 3) for lang, lines in
            sorted(lang_lines.items(), key=lambda x: -x[1])}


def detect_entry_points(root: Path) -> list[dict]:
    """识别入口文件"""
    entries = []
    for pattern, entry_type in ENTRY_POINT_PATTERNS:
        path = root / pattern
        if path.exists():
            entries.append({'path': pattern, 'type': entry_type})

    # 从 package.json 的 main/bin 字段提取
    pkg_path = root / 'package.json'
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
            if 'main' in pkg and pkg['main']:
                main = pkg['main']
                if not any(e['path'] == main for e in entries):
                    entries.append({'path': main, 'type': 'main'})
            if 'bin' in pkg:
                bins = pkg['bin']
                if isinstance(bins, str):
                    if not any(e['path'] == bins for e in entries):
                        entries.append({'path': bins, 'type': 'cli'})
                elif isinstance(bins, dict):
                    for _, bin_path in bins.items():
                        if not any(e['path'] == bin_path for e in entries):
                            entries.append({'path': bin_path, 'type': 'cli'})
        except (json.JSONDecodeError, OSError):
            pass

    return entries


def detect_technology_stack(root: Path) -> dict:
    """检测技术栈"""
    stack = {
        'language': '',
        'framework': '',
        'build_tool': '',
        'package_manager': '',
        'key_dependencies': [],
    }

    pkg_path = root / 'package.json'
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

            # 检测框架
            frameworks = ['next', 'nuxt', 'react', 'vue', 'svelte', 'angular',
                          'express', 'fastify', 'hono', 'elysia', 'nest']
            for fw in frameworks:
                if fw in deps or f'@{fw}/core' in deps:
                    stack['framework'] = fw.capitalize()
                    break

            # 检测构建工具
            build_tools = ['vite', 'webpack', 'esbuild', 'tsup', 'rollup', 'turbopack']
            for bt in build_tools:
                if bt in deps:
                    stack['build_tool'] = bt
                    break

            # 检测包管理器
            if (root / 'bun.lockb').exists() or (root / 'bun.lock').exists():
                stack['package_manager'] = 'bun'
            elif (root / 'pnpm-lock.yaml').exists():
                stack['package_manager'] = 'pnpm'
            elif (root / 'yarn.lock').exists():
                stack['package_manager'] = 'yarn'
            elif (root / 'package-lock.json').exists():
                stack['package_manager'] = 'npm'

            # 关键依赖（排除 devDeps 中的纯工具）
            prod_deps = list(pkg.get('dependencies', {}).keys())[:15]
            stack['key_dependencies'] = prod_deps

        except (json.JSONDecodeError, OSError):
            pass

    # Python 项目
    pyproject = root / 'pyproject.toml'
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding='utf-8')
            if 'fastapi' in content.lower():
                stack['framework'] = 'FastAPI'
            elif 'django' in content.lower():
                stack['framework'] = 'Django'
            elif 'flask' in content.lower():
                stack['framework'] = 'Flask'
            stack['package_manager'] = 'pip'
            if 'poetry' in content.lower():
                stack['package_manager'] = 'poetry'
            if 'hatch' in content.lower():
                stack['package_manager'] = 'hatch'
        except OSError:
            pass

    # Go 项目
    if (root / 'go.mod').exists():
        stack['language'] = 'Go'
        stack['package_manager'] = 'go modules'

    # Rust 项目
    if (root / 'Cargo.toml').exists():
        stack['language'] = 'Rust'
        stack['package_manager'] = 'cargo'

    return stack


def parse_imports_ts_js(content: str) -> list[str]:
    """解析 TypeScript/JavaScript 的 import 语句"""
    imports = []
    patterns = [
        r'import\s+.*?\s+from\s+[\'"]([^.\'"@][^\'"]*)[\'"]',  # import x from 'y'
        r'import\s+[\'"]([^.\'"@][^\'"]*)[\'"]',  # import 'y'
        r'require\s*\(\s*[\'"]([^.\'"@][^\'"]*)[\'"]',  # require('y')
        r'import\s+.*?\s+from\s+[\'"](\.{1,2}/[^\'"]*)[\'"]',  # relative imports
        r'require\s*\(\s*[\'"](\.{1,2}/[^\'"]*)[\'"]',  # relative requires
    ]
    for pat in patterns:
        imports.extend(re.findall(pat, content))
    return imports


def parse_imports_python(content: str) -> list[str]:
    """解析 Python 的 import 语句"""
    imports = []
    patterns = [
        r'^from\s+(\S+)\s+import', # from x import y
        r'^import\s+(\S+)',  # import x
    ]
    for line in content.splitlines():
        for pat in patterns:
            match = re.match(pat, line.strip())
            if match:
                imports.append(match.group(1).split('.')[0])
    return imports


def detect_modules(root: Path, files: list[Path]) -> tuple[list[dict], dict]:
    """检测模块边界和依赖关系"""
    # 按第一级 src 子目录分组作为模块
    src_dirs = [root / 'src', root / 'lib', root / 'app', root / 'packages']
    module_root = None
    for d in src_dirs:
        if d.exists() and d.is_dir():
            module_root = d
            break

    if module_root is None:
        module_root = root

    # 收集模块（src 下的一级子目录）
    module_dirs = {}
    for item in sorted(module_root.iterdir()):
        if item.is_dir() and item.name not in IGNORE_DIRS and not item.name.startswith('.'):
            module_dirs[item.name] = item

    # 如果没有子目录，把每个源文件当作一个"模块"
    if not module_dirs:
        return [], {}

    # 分析每个模块的文件和 import
    modules = []
    imports_map = defaultdict(set)  # module -> set of imported modules

    for mod_name, mod_path in module_dirs.items():
        mod_files = [f for f in files if f.is_relative_to(mod_path)]
        if not mod_files:
            continue

        # 收集该模块的 import
        for f in mod_files:
            ext = f.suffix.lower()
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                continue

            if ext in ('.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'):
                raw_imports = parse_imports_ts_js(content)
            elif ext == '.py':
                raw_imports = parse_imports_python(content)
            else:
                continue

            # 将相对 import 解析为模块名
            for imp in raw_imports:
                if imp.startswith('.'):
                    # 相对路径 import，尝试解析到模块
                    resolved = (f.parent / imp).resolve()
                    try:
                        rel = resolved.relative_to(module_root)
                        target_mod = rel.parts[0] if rel.parts else None
                        if target_mod and target_mod != mod_name and target_mod in module_dirs:
                            imports_map[mod_name].add(target_mod)
                    except (ValueError, IndexError):
                        pass
                else:
                    # 非相对 import，检查是否是项目内模块
                    top_level = imp.split('/')[0]
                    if top_level in module_dirs and top_level != mod_name:
                        imports_map[mod_name].add(top_level)

        key_files = []
        index_candidates = ['index.ts', 'index.js', 'index.tsx', 'mod.rs',
                            '__init__.py', 'main.go']
        for ic in index_candidates:
            if (mod_path / ic).exists():
                key_files.append(str((mod_path / ic).relative_to(root)))
                break
        if not key_files and mod_files:
            key_files.append(str(mod_files[0].relative_to(root)))

        line_count = 0
        for f in mod_files:
            try:
                line_count += len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
            except OSError:
                pass

        modules.append({
            'name': mod_name,
            'root_path': str(mod_path.relative_to(root)) + '/',
            'key_files': key_files,
            'imports_from': sorted(imports_map.get(mod_name, set())),
            'imported_by': [],  # 填充在下面
            'file_count': len(mod_files),
            'line_count': line_count,
            'rank': 0.0,  # PageRank 填充在下面
        })

    # 计算 imported_by
    for mod in modules:
        for dep in mod['imports_from']:
            target = next((m for m in modules if m['name'] == dep), None)
            if target:
                target['imported_by'].append(mod['name'])

    # 排序 imported_by
    for mod in modules:
        mod['imported_by'] = sorted(set(mod['imported_by']))

    # 简易 PageRank（基于被引用次数）
    max_refs = max((len(m['imported_by']) for m in modules), default=1) or 1
    for mod in modules:
        mod['rank'] = round(len(mod['imported_by']) / max_refs, 3)

    # 构建依赖图
    dep_graph = {mod['name']: mod['imports_from'] for mod in modules}

    # 按 rank 排序
    modules.sort(key=lambda m: -m['rank'])

    return modules, dep_graph


def detect_config_files(root: Path) -> list[dict]:
    """检测配置文件"""
    configs = []
    for pattern, config_type in CONFIG_FILE_PATTERNS.items():
        path = root / pattern
        if path.exists():
            configs.append({'path': pattern, 'type': config_type})
        # 检查 glob 模式
        elif '*' in pattern:
            for match in root.glob(pattern):
                rel = str(match.relative_to(root))
                configs.append({'path': rel, 'type': config_type})

    # 检查 .github/workflows 目录
    workflows_dir = root / '.github' / 'workflows'
    if workflows_dir.exists():
        for wf in workflows_dir.glob('*.yml'):
            configs.append({'path': str(wf.relative_to(root)), 'type': 'ci'})
        for wf in workflows_dir.glob('*.yaml'):
            configs.append({'path': str(wf.relative_to(root)), 'type': 'ci'})

    return configs


def scan_codebase(root: Path) -> dict:
    """主扫描函数"""
    files = scan_files(root)
    source_files = [f for f in files if f.suffix.lower() in LANGUAGE_EXTENSIONS]

    # 统计
    total_lines = 0
    for f in source_files:
        try:
            total_lines += len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
        except OSError:
            pass

    languages = detect_languages(source_files)
    entry_points = detect_entry_points(root)
    tech_stack = detect_technology_stack(root)
    modules, dep_graph = detect_modules(root, source_files)
    config_files = detect_config_files(root)

    # 设置主语言（如果 tech_stack 没检测到）
    if not tech_stack['language'] and languages:
        tech_stack['language'] = list(languages.keys())[0]

    return {
        'version': '1.0',
        'scanned_at': datetime.now(timezone.utc).isoformat(),
        'root': str(root.resolve()),
        'summary': {
            'total_files': len(source_files),
            'total_lines': total_lines,
            'languages': languages,
        },
        'entry_points': entry_points,
        'modules': modules,
        'dependency_graph': dep_graph,
        'technology_stack': tech_stack,
        'configuration_files': config_files,
    }


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='docstrata repo-wiki 代码库扫描脚本',
        epilog='输出符合 layer-repo-wiki.md JSON 格式规范的结构化数据。'
    )
    parser.add_argument('--root', '-r', type=str, default='.',
                        help='项目根目录路径 (默认: 当前目录)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='输出 JSON 文件路径 (默认: stdout)')
    parser.add_argument('--pretty', '-p', action='store_true',
                        help='格式化 JSON 输出')

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"错误: 目录不存在: {root}", file=sys.stderr)
        sys.exit(1)

    result = scan_codebase(root)

    json_str = json.dumps(result, ensure_ascii=False,
                          indent=2 if args.pretty else None)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_str, encoding='utf-8')
        print(f"扫描完成: {result['summary']['total_files']} 文件, "
              f"{len(result['modules'])} 模块 → {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == '__main__':
    main()
