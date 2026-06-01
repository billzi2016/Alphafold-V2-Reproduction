"""Structure Module 模块。"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from af2_repro.model.ipa import InvariantPointAttention


BACKBONE_OFFSETS = torch.tensor(
    [
        [-1.45, 0.10, 0.00],  # N
        [0.00, 0.00, 0.00],   # CA
        [1.52, -0.10, 0.00],  # C
    ],
    dtype=torch.float32,
)


@dataclass(slots=True)
class StructureOutputs:
    """结构模块输出。"""

    single_repr: torch.Tensor
    translations: torch.Tensor
    backbone_positions: torch.Tensor


class StructureModule(nn.Module):
    """一个简化但真实可运行的结构模块。

    当前版本完成这些事情：
    - 从 Evoformer 的 `msa_repr[0]` 抽取 `single_repr`
    - 用 IPA 结合 `pair_repr` 更新 `single_repr`
    - 预测每个残基的平移向量
    - 基于固定 backbone offset 生成一个最小 backbone 坐标张量

    这还不是完整的 AlphaFold 2 结构生成器，但它已经建立了从表示张量到
    几何张量的真实前向链路。
    """

    def __init__(self, single_channel: int, pair_channel: int, num_heads: int) -> None:
        super().__init__()
        self.single_norm = nn.LayerNorm(single_channel)
        self.ipa = InvariantPointAttention(single_channel, pair_channel, num_heads=num_heads)
        self.transition = nn.Sequential(
            nn.LayerNorm(single_channel),
            nn.Linear(single_channel, single_channel * 4),
            nn.ReLU(),
            nn.Linear(single_channel * 4, single_channel),
        )
        self.translation_head = nn.Linear(single_channel, 3)

    def forward(self, msa_repr: torch.Tensor, pair_repr: torch.Tensor, seq_mask: torch.Tensor) -> StructureOutputs:
        """执行结构模块前向。"""
        single_repr = msa_repr[0]
        single_repr = self.single_norm(single_repr)
        single_repr = single_repr + self.ipa(single_repr, pair_repr, seq_mask)
        single_repr = single_repr + self.transition(single_repr)

        translations = self.translation_head(single_repr)
        offsets = BACKBONE_OFFSETS.to(device=translations.device, dtype=translations.dtype)
        backbone_positions = translations[:, None, :] + offsets[None, :, :]

        return StructureOutputs(
            single_repr=single_repr,
            translations=translations,
            backbone_positions=backbone_positions,
        )
