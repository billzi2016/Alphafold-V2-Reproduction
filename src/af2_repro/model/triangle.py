"""Triangle 相关模块。"""

from __future__ import annotations

import torch
from torch import nn


class TriangleMultiplicativeUpdate(nn.Module):
    """近似实现 pair 表示的三角乘法更新。

    这里不追求逐行复刻官方实现，但保留核心结构思想：
    pair[i, k] 和 pair[j, k] 的交互会回流到 pair[i, j]。
    """

    def __init__(self, pair_channel: int) -> None:
        super().__init__()
        self.left_projection = nn.Linear(pair_channel, pair_channel)
        self.right_projection = nn.Linear(pair_channel, pair_channel)
        self.output_projection = nn.Linear(pair_channel, pair_channel)
        self.layer_norm = nn.LayerNorm(pair_channel)

    def forward(self, pair_repr: torch.Tensor) -> torch.Tensor:
        """执行三角乘法更新。"""
        left = self.left_projection(pair_repr)
        right = self.right_projection(pair_repr)
        update = torch.einsum("ikc,jkc->ijc", left, right) / max(pair_repr.shape[0], 1)
        return self.layer_norm(pair_repr + self.output_projection(update))


class TriangleAttention(nn.Module):
    """沿 pair 矩阵某一维做注意力更新。"""

    def __init__(self, pair_channel: int, num_heads: int, *, attend_over_rows: bool) -> None:
        super().__init__()
        self.attend_over_rows = attend_over_rows
        self.attention = nn.MultiheadAttention(pair_channel, num_heads=num_heads, batch_first=True)
        self.layer_norm = nn.LayerNorm(pair_channel)

    def forward(self, pair_repr: torch.Tensor) -> torch.Tensor:
        """执行三角注意力。

        - `attend_over_rows=True` 时，把每个起点残基的一整行作为一个序列
        - `attend_over_rows=False` 时，对转置后的列做同样处理
        """
        input_repr = pair_repr if self.attend_over_rows else pair_repr.transpose(0, 1)
        updated, _ = self.attention(input_repr, input_repr, input_repr, need_weights=False)
        updated = self.layer_norm(input_repr + updated)
        return updated if self.attend_over_rows else updated.transpose(0, 1)
