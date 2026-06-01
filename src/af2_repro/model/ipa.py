"""Invariant Point Attention 模块。"""

from __future__ import annotations

import torch
from torch import nn


class InvariantPointAttention(nn.Module):
    """一个简化但真实可运行的 IPA 模块。

    正式 AlphaFold 2 的 IPA 会同时处理标量特征和点特征，并在局部坐标系中
    做几何相关更新。当前实现先保留两个关键思想：
    - single representation 是结构模块的主输入
    - pair representation 通过 pair bias 影响残基间注意力

    这样后续可以在保持接口稳定的前提下继续把点特征和更精细的几何项接进来。
    """

    def __init__(self, single_channel: int, pair_channel: int, num_heads: int) -> None:
        super().__init__()
        self.num_heads = num_heads
        self.single_norm = nn.LayerNorm(single_channel)
        self.pair_bias_projection = nn.Linear(pair_channel, num_heads)
        self.query_projection = nn.Linear(single_channel, single_channel)
        self.key_projection = nn.Linear(single_channel, single_channel)
        self.value_projection = nn.Linear(single_channel, single_channel)
        self.output_projection = nn.Linear(single_channel, single_channel)

    def forward(self, single_repr: torch.Tensor, pair_repr: torch.Tensor, seq_mask: torch.Tensor) -> torch.Tensor:
        """执行一轮受 pair bias 调制的 single attention 更新。

        输入:
        - `single_repr`: `[N, C_s]`
        - `pair_repr`: `[N, N, C_z]`
        - `seq_mask`: `[N]`
        """
        single_repr = self.single_norm(single_repr)
        query = self.query_projection(single_repr)
        key = self.key_projection(single_repr)
        value = self.value_projection(single_repr)

        head_dim = query.shape[-1] // self.num_heads
        query = query.view(query.shape[0], self.num_heads, head_dim)
        key = key.view(key.shape[0], self.num_heads, head_dim)
        value = value.view(value.shape[0], self.num_heads, head_dim)

        attention_scores = torch.einsum("ihd,jhd->hij", query, key) / max(head_dim, 1) ** 0.5
        pair_bias = self.pair_bias_projection(pair_repr).permute(2, 0, 1)
        attention_scores = attention_scores + pair_bias

        mask = seq_mask[:, None] * seq_mask[None, :]
        attention_scores = attention_scores.masked_fill(mask.unsqueeze(0) == 0, float("-inf"))
        attention_weights = torch.softmax(attention_scores, dim=-1)

        updated = torch.einsum("hij,jhd->ihd", attention_weights, value).reshape(single_repr.shape[0], -1)
        return self.output_projection(updated)
