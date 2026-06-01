"""外部工具检查与命令执行辅助。"""

from __future__ import annotations

import subprocess
import shutil
from dataclasses import dataclass
from pathlib import Path


def require_executable(name: str) -> str:
    """校验系统中存在某个可执行文件。"""
    resolved = shutil.which(name)
    if resolved is None:
        raise FileNotFoundError(f"未找到外部工具: {name}")
    return resolved


def require_existing_path(path: Path, description: str) -> Path:
    """校验某个外部路径存在。"""
    if not path.exists():
        raise FileNotFoundError(f"{description}不存在: {path}")
    return path


@dataclass(slots=True)
class CommandResult:
    """描述一次外部命令执行结果。"""

    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def run_command(
    command: list[str],
    *,
    stdout_path: Path | None = None,
    stderr_path: Path | None = None,
    cwd: Path | None = None,
) -> CommandResult:
    """执行外部命令并可选地把 stdout/stderr 落盘。

    这里不吞错误。只要命令返回非 0，直接抛异常，这样上层能明确知道
    是哪个工具失败、失败输出是什么。
    """
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd is not None else None,
        check=False,
        text=True,
        capture_output=True,
    )

    if stdout_path is not None:
        stdout_path.write_text(completed.stdout, encoding="utf-8")
    if stderr_path is not None:
        stderr_path.write_text(completed.stderr, encoding="utf-8")

    result = CommandResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"外部命令执行失败: {' '.join(command)}\n"
            f"returncode={completed.returncode}\n"
            f"stderr={completed.stderr}"
        )
    return result
