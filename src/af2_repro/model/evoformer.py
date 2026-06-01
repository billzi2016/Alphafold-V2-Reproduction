"""Evoformer 模块。"""

from __future__ import annotations

import torch
from torch import nn

from af2_repro.model.config import InferenceConfig
from af2_repro.model.triangle import TriangleAttention, TriangleMultiplicativeUpdate


class Transition(nn.Module):
    """通用前馈过渡层。"""

    def __init__(self, channel: int, multiplier: int) -> None:
        super().__init__()
        hidden_channel = channel * multiplier
        self.net = nn.Sequential(
            nn.LayerNorm(channel),
            nn.Linear(channel, hidden_channel),
            nn.ReLU(),
            nn.Linear(hidden_channel, channel),
        )

    def forward(self, tensor: torch.Tensor) -> torch.Tensor:
        """执行残差前馈更新。"""
        return tensor + self.net(tensor)


class MsaRowAttention(nn.Module):
    """沿残基维度更新每条序列表示。"""

    def __init__(self, msa_channel: int, num_heads: int) -> None:
        super().__init__()
        self.layer_norm = nn.LayerNorm(msa_channel)
        self.attention = nn.MultiheadAttention(msa_channel, num_heads=num_heads, batch_first=True)

    def forward(self, msa_repr: torch.Tensor) -> torch.Tensor:
        """输入 shape: [S, N, C_m]。"""
        normalized = self.layer_norm(msa_repr)
        updated, _ = self.attention(normalized, normalized, normalized, need_weights=False)
        return msa_repr + updated


class MsaColumnAttention(nn.Module):
    """沿 MSA 序列维度更新表示。"""

    def __init__(self, msa_channel: int, num_heads: int) -> None:
        super().__init__()
        self.layer_norm = nn.LayerNorm(msa_channel)
        self.attention = nn.MultiheadAttention(msa_channel, num_heads=num_heads, batch_first=True)

    def forward(self, msa_repr: torch.Tensor) -> torch.Tensor:
        """通过转置把列注意力转成标准 batch-first attention。"""
        transposed = msa_repr.transpose(0, 1)
        normalized = self.layer_norm(transposed)
        updated, _ = self.attention(normalized, normalized, normalized, need_weights=False)
        return (transposed + updated).transpose(0, 1)


class OuterProductMean(nn.Module):
    """把 MSA 表示回流到 pair 表示。"""

    def __init__(self, msa_channel: int, pair_channel: int) -> None:
        super().__init__()
        self.left_projection = nn.Linear(msa_channel, pair_channel)
        self.right_projection = nn.Linear(msa_channel, pair_channel)
        self.output_norm = nn.LayerNorm(pair_channel)

    def forward(self, msa_repr: torch.Tensor, pair_repr: torch.Tensor) -> torch.Tensor:
        """根据所有 MSA 行的均值外积更新 pair 表示。"""
        left = self.left_projection(msa_repr)
        right = self.right_projection(msa_repr)
        update = torch.einsum("snc,smc->nmc", left, right) / max(msa_repr.shape[0], 1)
        return self.output_norm(pair_repr + update)


class PairTransition(Transition):
    """pair 表示前馈更新。"""


class MsaTransition(Transition):
    """MSA 表示前馈更新。"""


class EvoformerBlock(nn.Module):
    """一个简化但真实可运行的 Evoformer block。"""

    def __init__(self, config: InferenceConfig) -> None:
        super().__init__()
        self.msa_row_attention = MsaRowAttention(config.msa_channel, config.num_heads_msa)
        self.msa_column_attention = MsaColumnAttention(config.msa_channel, config.num_heads_msa)
        self.msa_transition = MsaTransition(config.msa_channel, config.transition_multiplier)
        self.outer_product_mean = OuterProductMean(config.msa_channel, config.pair_channel)
        self.triangle_multiplicative_update = TriangleMultiplicativeUpdate(config.pair_channel)
        self.triangle_attention_start = TriangleAttention(
            config.pair_channel,
            num_heads=config.num_heads_pair,
            attend_over_rows=True,
        )
        self.triangle_attention_end = TriangleAttention(
            config.pair_channel,
            num_heads=config.num_heads_pair,
            attend_over_rows=False,
        )
        self.pair_transition = PairTransition(config.pair_channel, config.transition_multiplier)

    def forward(self, msa_repr: torch.Tensor, pair_repr: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """执行一轮 MSA/pair 交替更新。"""
        msa_repr = self.msa_row_attention(msa_repr)
        msa_repr = self.msa_column_attention(msa_repr)
        msa_repr = self.msa_transition(msa_repr)

        pair_repr = self.outer_product_mean(msa_repr, pair_repr)
        pair_repr = self.triangle_multiplicative_update(pair_repr)
        pair_repr = self.triangle_attention_start(pair_repr)
        pair_repr = self.triangle_attention_end(pair_repr)
        pair_repr = self.pair_transition(pair_repr)
        return msa_repr, pair_repr


class EvoformerStack(nn.Module):
    """堆叠多个 Evoformer block。"""

    def __init__(self, config: InferenceConfig) -> None:
        super().__init__()
        self.blocks = nn.ModuleList(EvoformerBlock(config) for _ in range(config.num_evoformer_blocks))

    def forward(self, msa_repr: torch.Tensor, pair_repr: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """顺序执行所有 Evoformer block。"""
        for block in self.blocks:
            msa_repr, pair_repr = block(msa_repr, pair_repr)
        return msa_repr, pair_repr
