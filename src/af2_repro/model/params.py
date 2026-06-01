"""模型参数加载与元信息记录。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from af2_repro.io.json_io import save_json
from af2_repro.utils.external_tools import require_existing_path


@dataclass(slots=True)
class ParameterSource:
    """描述模型参数来源。"""

    params_path: Path
    source_name: str
    version: str | None = None


class ParameterLoader:
    """负责参数路径校验与元信息整理。

    当前先把真实可做的部分做好：
    - 参数路径存在性检查
    - 参数来源与版本信息记录
    - 后续权重映射入口预留
    """

    def __init__(self, source: ParameterSource) -> None:
        self.source = source
        self._cached_object: Any | None = None

    def validate(self) -> Path:
        """校验参数路径存在。"""
        return require_existing_path(self.source.params_path, "模型参数路径")

    def build_metadata(self) -> dict[str, Any]:
        """构建参数元信息字典。"""
        validated_path = self.validate()
        return {
            "params_path": str(validated_path),
            "source_name": self.source.source_name,
            "version": self.source.version,
            "is_directory": validated_path.is_dir(),
            "is_file": validated_path.is_file(),
        }

    def save_metadata(self, output_path: Path) -> None:
        """把参数元信息写入 JSON 文件。"""
        save_json(self.build_metadata(), output_path)

    def load_torch_object(self, *, map_location: str = "cpu") -> Any:
        """读取 `.pt/.pth/.ckpt` 等 PyTorch 对象。"""
        if self._cached_object is not None:
            return self._cached_object
        validated_path = self.validate()
        if not validated_path.is_file():
            raise ValueError(f"模型参数路径必须是文件，当前为: {validated_path}")
        self._cached_object = torch.load(validated_path, map_location=map_location, weights_only=False)
        return self._cached_object

    def load_state_dict(self, *, map_location: str = "cpu") -> dict[str, Any]:
        """尽量解析出标准 state_dict。"""
        loaded = self.load_torch_object(map_location=map_location)
        if isinstance(loaded, dict) and "state_dict" in loaded and isinstance(loaded["state_dict"], dict):
            return loaded["state_dict"]
        if isinstance(loaded, dict):
            return loaded
        raise ValueError("无法从当前参数文件解析出 state_dict。")


def resolve_checkpoint_path(params_dir: Path, params_checkpoint: Path | None = None) -> Path | None:
    """解析可直接加载的 checkpoint 文件路径。"""
    if params_checkpoint is not None:
        return params_checkpoint
    if params_dir.is_file():
        return params_dir
    for pattern in ("*.pt", "*.pth", "*.ckpt"):
        matches = sorted(params_dir.glob(pattern))
        if matches:
            return matches[0]
    return None
