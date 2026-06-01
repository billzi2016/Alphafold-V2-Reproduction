"""置信度与输出头模块。"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from af2_repro.common.confidence import logits_to_expected_value


@dataclass(slots=True)
class ConfidenceOutputs:
    """置信度头输出。"""

    plddt_logits: torch.Tensor
    plddt_scores: torch.Tensor
    pae_logits: torch.Tensor
    ptm_score: torch.Tensor


class ConfidenceHeads(nn.Module):
    """从 single/pair 表示中导出置信度结果。"""

    def __init__(self, single_channel: int, pair_channel: int, *, num_plddt_bins: int = 50, num_pae_bins: int = 64) -> None:
        super().__init__()
        self.num_plddt_bins = num_plddt_bins
        self.num_pae_bins = num_pae_bins
        self.plddt_head = nn.Linear(single_channel, num_plddt_bins)
        self.pae_head = nn.Linear(pair_channel, num_pae_bins)
        self.ptm_head = nn.Linear(pair_channel, 1)

    def forward(self, single_repr: torch.Tensor, pair_repr: torch.Tensor) -> ConfidenceOutputs:
        """执行置信度头前向。"""
        plddt_logits = self.plddt_head(single_repr)
        plddt_scores = logits_to_expected_value(plddt_logits, 0.0, 100.0)
        pae_logits = self.pae_head(pair_repr)
        ptm_score = torch.sigmoid(self.ptm_head(pair_repr).mean())

        return ConfidenceOutputs(
            plddt_logits=plddt_logits,
            plddt_scores=plddt_scores,
            pae_logits=pae_logits,
            ptm_score=ptm_score,
        )
