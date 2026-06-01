"""运行时工具模块。"""

from __future__ import annotations

import torch


def resolve_device(preferred_device: str) -> str:
    """返回当前优先使用的设备字符串。

    在请求 `cuda` 但当前环境不可用时，自动回退到 `cpu`。
    """
    if preferred_device.startswith("cuda") and not torch.cuda.is_available():
        return "cpu"
    return preferred_device
