"""Recycling 模块。"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass(slots=True)
class RecyclingState:
    """保存上一轮推理可回灌的状态。"""

    single_repr: torch.Tensor
    pair_repr: torch.Tensor


class RecyclingEmbedder(nn.Module):
    """把上一轮 single/pair 表示回灌到当前轮前向。

    这里先实现最小可运行版本：
    - `single_repr` 映射回 query 所在的 MSA 行
    - `pair_repr` 通过残差方式回流
    """

    def __init__(self, msa_channel: int, pair_channel: int) -> None:
        super().__init__()
        self.single_projection = nn.Linear(msa_channel, msa_channel)
        self.pair_projection = nn.Linear(pair_channel, pair_channel)
        self.single_norm = nn.LayerNorm(msa_channel)
        self.pair_norm = nn.LayerNorm(pair_channel)

    def forward(
        self,
        msa_repr: torch.Tensor,
        pair_repr: torch.Tensor,
        previous_state: RecyclingState | None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """把上一轮状态回灌到当前表示。"""
        if previous_state is None:
            return msa_repr, pair_repr

        recycled_single = self.single_projection(previous_state.single_repr).unsqueeze(0)
        recycled_pair = self.pair_projection(previous_state.pair_repr)

        msa_repr = self.single_norm(msa_repr + recycled_single)
        pair_repr = self.pair_norm(pair_repr + recycled_pair)
        return msa_repr, pair_repr
