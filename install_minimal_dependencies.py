from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from dependency_manifest import PYTHON_REQUIREMENTS_FILE, PYTHON_IMPORT_NAMES, RELEASE_ROOT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="安装当前发布目录所需的最小 Python 依赖。"
    )
    parser.add_argument(
        "--python-executable",
        default=sys.executable,
        help="用于执行 pip 的 Python 解释器，默认使用当前解释器。",
    )
    parser.add_argument(
        "--requirements-file",
        default=str(PYTHON_REQUIREMENTS_FILE),
        help="Python 依赖清单路径，默认使用仓库内的最小依赖文件。",
    )
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="安装时附加 `--upgrade`。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅打印将要执行的 pip 命令，不实际安装。",
    )
    return parser


def ensure_requirements_file(file_path: Path) -> list[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"未找到依赖清单文件: {file_path}")

    packages = [
        line.strip()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not packages:
        raise ValueError(f"依赖清单为空: {file_path}")
    return packages


def ensure_pip_available(python_executable: str) -> None:
    result = subprocess.run(
        [python_executable, "-m", "pip", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "当前 Python 解释器不可用 `pip`。请先安装/启用 pip，再重试本脚本。"
        )


def install_packages(
    python_executable: str,
    requirements_file: Path,
    upgrade: bool,
    dry_run: bool,
) -> int:
    command = [python_executable, "-m", "pip", "install", "-r", str(requirements_file)]
    if upgrade:
        command.append("--upgrade")

    print("仓库根目录:", RELEASE_ROOT)
    print("目标 Python:", python_executable)
    print("依赖清单:", requirements_file)
    print("最小 Python 依赖:", ", ".join(PYTHON_IMPORT_NAMES) or "(空)")
    print("执行命令:", " ".join(command))

    if dry_run:
        print("\n已启用 --dry-run，未实际安装。")
        return 0

    ensure_pip_available(python_executable)
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        print("\nPython 依赖安装失败，请检查上方 pip 输出。")
        return result.returncode

    print("\nPython 最小依赖安装完成。")
    print("建议继续执行:")
    print(f"  {python_executable} check_dependencies.py --profile python")
    print(f"  {python_executable} check_dependencies.py --profile all")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    requirements_file = Path(args.requirements_file).expanduser().resolve()

    try:
        ensure_requirements_file(requirements_file)
        return install_packages(
            python_executable=args.python_executable,
            requirements_file=requirements_file,
            upgrade=args.upgrade,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
