"""Pickle 结果输出工具。"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any


def save_pickle(data: dict[str, Any], output_path: Path) -> None:
    """把中间结果以 pickle 形式落盘。"""
    with output_path.open("wb") as file_obj:
        pickle.dump(data, file_obj)
