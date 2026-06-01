"""输入嵌入模块。"""

from __future__ import annotations

from typing import Any

import torch
from torch import nn

from af2_repro.model.config import InferenceConfig


class InputEmbedding(nn.Module):
    """把序列级输入投影到 MSA 表示和 pair 表示。

    当前实现的是第一批真实 PyTorch 模块：
    - `aatype` 先进入可训练 embedding
    - 单序列表达扩展成 `msa_repr`
    - 残基两两组合形成初始 `pair_repr`

    这不是完整 AlphaFold 2 输入层，但它已经建立了后续 Evoformer 所需的
    两类主表示张量接口。
    """

    def __init__(self, config: InferenceConfig) -> None:
        super().__init__()
        self.config = config
        self.aatype_embedding = nn.Embedding(21, config.msa_channel)
        self.pair_left_projection = nn.Linear(config.msa_channel, config.pair_channel)
        self.pair_right_projection = nn.Linear(config.msa_channel, config.pair_channel)

    def forward(self, features: dict[str, Any]) -> dict[str, torch.Tensor]:
        """根据最小 sequence features 构建输入表示。"""
        device = self.aatype_embedding.weight.device
        aatype = torch.as_tensor(features["aatype"], dtype=torch.long, device=device)
        seq_embedding = self.aatype_embedding(aatype)

        # `msa_repr` 当前只有 1 条序列，即 query 本身，shape 为 [1, N, C_m].
        msa_repr = seq_embedding.unsqueeze(0)

        left = self.pair_left_projection(seq_embedding)
        right = self.pair_right_projection(seq_embedding)

        # 初始 pair 表示通过残基两两组合得到，shape 为 [N, N, C_z].
        pair_repr = left[:, None, :] + right[None, :, :]
        seq_mask = torch.as_tensor(features["seq_mask"], dtype=torch.float32, device=device)

        return {
            "msa_repr": msa_repr,
            "pair_repr": pair_repr,
            "seq_mask": seq_mask,
        }
