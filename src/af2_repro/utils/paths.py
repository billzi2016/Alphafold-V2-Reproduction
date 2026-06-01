"""路径管理工具模块。"""

from __future__ import annotations

from pathlib import Path


def ensure_directory(path: Path) -> Path:
    """确保目录存在并返回该路径。

    这里保留单一职责，后续所有输出目录初始化都复用这一个入口。
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_file(path: Path, description: str) -> Path:
    """校验一个必须存在的文件路径。"""
    if not path.exists():
        raise FileNotFoundError(f"{description}不存在: {path}")
    if not path.is_file():
        raise ValueError(f"{description}不是文件: {path}")
    return path
