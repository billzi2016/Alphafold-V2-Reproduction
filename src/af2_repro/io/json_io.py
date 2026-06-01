"""JSON 结果输出工具。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_json(data: dict[str, Any], output_path: Path) -> None:
    """把字典结果写成 JSON 文件。"""
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
