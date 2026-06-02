from __future__ import annotations

import argparse
import importlib
import os
import subprocess
import sys
from pathlib import Path

from dependency_manifest import (
    ENVIRONMENT_REQUIREMENTS,
    MIN_PYTHON_VERSION,
    PROFILE_EXTERNAL_TOOLS,
    PROFILE_LABELS,
    PYTHON_IMPORT_NAMES,
    R_PACKAGE_NAMES,
    RELEASE_ROOT,
    TOOL_DISPLAY_NAMES,
    TOOL_INSTALL_HINTS,
    detect_command,
    get_selected_profiles,
    get_tool_candidates,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="检查当前发布目录所需的 Python、R、PowerShell 与关键外部工具依赖。"
    )
    parser.add_argument(
        "--profile",
        choices=["all", "python", "maxent", "wgt"],
        default="all",
        help="指定检查范围：python / maxent / wgt / all。",
    )
    return parser


def print_section(title: str) -> None:
    print(f"\n== {title} ==")


def print_result(ok: bool, label: str, detail: str) -> None:
    status = "OK" if ok else "MISSING"
    print(f"[{status}] {label}: {detail}")


def check_python_runtime() -> tuple[bool, list[str]]:
    details = [
        f"当前解释器: {sys.executable}",
        f"当前版本: {sys.version.split()[0]}",
        f"要求版本: {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+",
    ]
    ok = sys.version_info >= MIN_PYTHON_VERSION
    return ok, details


def check_python_packages() -> tuple[bool, list[str]]:
    missing: list[str] = []
    for package_name in PYTHON_IMPORT_NAMES:
        try:
            importlib.import_module(package_name)
        except Exception:
            missing.append(package_name)

    if missing:
        return False, [f"缺失 Python 包: {', '.join(missing)}"]
    return True, [f"已找到 Python 包: {', '.join(PYTHON_IMPORT_NAMES) or '(无)'}"]


def build_r_expression() -> str:
    quoted_packages = ", ".join(f'"{name}"' for name in R_PACKAGE_NAMES)
    return (
        "packages <- c("
        + quoted_packages
        + "); missing <- packages[!vapply(packages, requireNamespace, logical(1), quietly = TRUE)]; "
        + "if (length(missing) > 0) { cat(paste(missing, collapse='\\n')); quit(status = 2) }"
    )


def check_r_packages() -> tuple[bool, list[str]]:
    r_path = detect_command("rscript")
    if not r_path:
        return False, [
            "未检测到 R / Rscript。",
            TOOL_INSTALL_HINTS["rscript"],
        ]

    command = [r_path, "--vanilla", "-e", build_r_expression()]
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode == 0:
        return True, [f"已找到 R 包: {', '.join(R_PACKAGE_NAMES) or '(无)'}"]

    missing_packages = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]
    if missing_packages:
        return False, [f"缺失 R 包: {', '.join(missing_packages)}"]

    stderr = result.stderr.strip() or "R 包检查失败，但未返回明确缺失列表。"
    return False, [stderr]


def check_tool(tool_name: str) -> tuple[bool, str]:
    resolved = detect_command(tool_name)
    display_name = TOOL_DISPLAY_NAMES.get(tool_name, tool_name)
    if resolved:
        return True, f"{display_name} 已加入 PATH: {resolved}"

    candidates = ", ".join(get_tool_candidates(tool_name))
    hint = TOOL_INSTALL_HINTS.get(tool_name, "请安装后重试。")
    return False, f"未在 PATH 中找到候选命令: {candidates}。{hint}"


def resolve_default_path(spec: dict[str, object]) -> Path:
    default_value = spec["default_path"]
    if callable(default_value):
        resolved = default_value()
    else:
        resolved = default_value
    return Path(resolved).expanduser().resolve()


def path_exists(path: Path, path_kind: str) -> bool:
    if path_kind == "file":
        return path.is_file()
    return path.is_dir()


def get_path_kind_label(path_kind: str) -> str:
    if path_kind == "file":
        return "文件"
    return "目录"


def format_environment_examples(spec: dict[str, object]) -> str:
    env_name = str(spec["env_name"])
    linux_example = str(spec["linux_example"])
    powershell_example = str(spec["powershell_example"])
    return (
        f"Linux/macOS 示例: export {env_name}={linux_example} | "
        f'PowerShell 示例: $env:{env_name} = "{powershell_example}"'
    )


def check_environment_requirement(spec: dict[str, object]) -> tuple[bool, str]:
    env_name = str(spec["env_name"])
    purpose = str(spec["purpose"])
    path_kind = str(spec.get("path_kind", "dir"))
    kind_label = get_path_kind_label(path_kind)
    default_path = resolve_default_path(spec)
    configured_value = os.environ.get(env_name, "").strip()

    if configured_value:
        configured_path = Path(configured_value).expanduser().resolve()
        if path_exists(configured_path, path_kind):
            return True, (
                f"用途: {purpose} | 已设置，{kind_label}可用: {configured_path} | "
                f"默认回退路径: {default_path}"
            )
        return False, (
            f"用途: {purpose} | 已设置，但{kind_label}不存在: {configured_path} | "
            f"默认回退路径: {default_path} | {format_environment_examples(spec)}"
        )

    if path_exists(default_path, path_kind):
        return True, f"用途: {purpose} | 未设置，默认路径可用: {default_path}"

    return False, (
        f"用途: {purpose} | 未设置，且默认{kind_label}不存在: {default_path} | "
        f"请设置环境变量 {env_name}。{format_environment_examples(spec)}"
    )


def check_environment_requirements(
    specs: list[dict[str, object]],
) -> tuple[bool, list[str]]:
    details: list[str] = []
    all_ok = True
    for spec in specs:
        ok, detail = check_environment_requirement(spec)
        details.append(f"{spec['env_name']}: {detail}")
        all_ok = all_ok and ok
    return all_ok, details


def run_checks(profile: str) -> int:
    selected_profiles = get_selected_profiles(profile)
    has_failure = False

    print("Acer release 依赖检查")
    print("仓库根目录:", RELEASE_ROOT)
    print("检查范围:", "、".join(PROFILE_LABELS[name] for name in selected_profiles))

    if "python" in selected_profiles:
        print_section("Python")
        python_runtime_ok, python_runtime_details = check_python_runtime()
        print_result(python_runtime_ok, "Python 运行时", " | ".join(python_runtime_details))
        has_failure = has_failure or (not python_runtime_ok)

        python_packages_ok, python_packages_details = check_python_packages()
        print_result(python_packages_ok, "Python 包", " | ".join(python_packages_details))
        has_failure = has_failure or (not python_packages_ok)

    if "maxent" in selected_profiles:
        print_section("MaxEnt / R / PowerShell")
        r_ok, r_details = check_r_packages()
        print_result(r_ok, "R 包", " | ".join(r_details))
        has_failure = has_failure or (not r_ok)

        for spec in ENVIRONMENT_REQUIREMENTS["maxent"]:
            ok, detail = check_environment_requirement(spec)
            print_result(ok, str(spec["env_name"]), detail)
            has_failure = has_failure or (not ok)

        for tool_name in PROFILE_EXTERNAL_TOOLS["maxent"]:
            ok, detail = check_tool(tool_name)
            print_result(ok, TOOL_DISPLAY_NAMES[tool_name], detail)
            has_failure = has_failure or (not ok)

    if "wgt" in selected_profiles:
        print_section("WGT / 外部工具")
        for spec in ENVIRONMENT_REQUIREMENTS["wgt"]:
            ok, detail = check_environment_requirement(spec)
            print_result(ok, str(spec["env_name"]), detail)
            has_failure = has_failure or (not ok)

        for tool_name in PROFILE_EXTERNAL_TOOLS["wgt"]:
            ok, detail = check_tool(tool_name)
            print_result(ok, TOOL_DISPLAY_NAMES[tool_name], detail)
            has_failure = has_failure or (not ok)

    print_section("建议")
    if has_failure:
        print(
            "存在缺失依赖。可先执行 `python install_minimal_dependencies.py` 安装最小 Python 包，"
            "再手动补齐 R、PowerShell 或外部工具。"
        )
        return 1

    print("当前所选范围内的依赖均已满足。")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    try:
        return run_checks(args.profile)
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
