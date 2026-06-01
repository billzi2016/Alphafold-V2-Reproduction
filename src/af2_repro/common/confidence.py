"""置信度计算工具。"""

from __future__ import annotations

import torch


def logits_to_expected_value(logits: torch.Tensor, value_min: float, value_max: float) -> torch.Tensor:
    """把离散 logits 转成期望值。

    适用于 pLDDT、PAE 等按 bin 表示的输出。
    """
    probabilities = torch.softmax(logits, dim=-1)
    bins = torch.linspace(value_min, value_max, steps=logits.shape[-1], device=logits.device, dtype=logits.dtype)
    return torch.sum(probabilities * bins, dim=-1)


def mean_plddt(plddt_scores: torch.Tensor) -> float:
    """返回平均 pLDDT。"""
    return float(plddt_scores.detach().float().mean().cpu().item())


def build_ranking_confidence(plddt_scores: torch.Tensor) -> float:
    """构造单模型 ranking confidence。"""
    return mean_plddt(plddt_scores)
