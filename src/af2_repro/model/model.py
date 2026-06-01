"""模型总入口。"""

from __future__ import annotations

from typing import Any

from af2_repro.model.config import InferenceConfig
from af2_repro.model.embeddings import InputEmbedding
from af2_repro.model.evoformer import EvoformerStack
from af2_repro.model.heads import ConfidenceHeads
from af2_repro.model.recycling import RecyclingEmbedder, RecyclingState
from af2_repro.model.structure_module import StructureModule
from torch import nn


class AlphaFoldLikeModel(nn.Module):
    """AlphaFold 2 风格模型总入口。

    当前只保留统一接口，确保后续 Evoformer、Structure Module、
    recycling 和 confidence heads 能按一个稳定入口继续接入。
    """

    def __init__(self, config: InferenceConfig) -> None:
        super().__init__()
        self.config = config
        self.input_embedding = InputEmbedding(config)
        self.recycling = RecyclingEmbedder(config.msa_channel, config.pair_channel)
        self.evoformer = EvoformerStack(config)
        self.structure_module = StructureModule(
            single_channel=config.msa_channel,
            pair_channel=config.pair_channel,
            num_heads=config.num_heads_pair,
        )
        self.confidence_heads = ConfidenceHeads(
            single_channel=config.msa_channel,
            pair_channel=config.pair_channel,
        )

    def forward(self, features: dict[str, Any], recycle_state: RecyclingState | None = None) -> dict[str, Any]:
        """执行模型前向。

        当前返回真实的输入 embedding 和 Evoformer 更新结果，
        但还不生成 3D 结构坐标。
        """
        embedded = self.input_embedding(features)
        msa_repr, pair_repr = self.recycling(embedded["msa_repr"], embedded["pair_repr"], recycle_state)
        msa_repr, pair_repr = self.evoformer(msa_repr, pair_repr)
        structure_outputs = self.structure_module(msa_repr, pair_repr, embedded["seq_mask"])
        confidence_outputs = self.confidence_heads(structure_outputs.single_repr, pair_repr)
        return {
            "msa_repr": msa_repr,
            "pair_repr": pair_repr,
            "seq_mask": embedded["seq_mask"],
            "single_repr": structure_outputs.single_repr,
            "translations": structure_outputs.translations,
            "backbone_positions": structure_outputs.backbone_positions,
            "plddt_logits": confidence_outputs.plddt_logits,
            "plddt_scores": confidence_outputs.plddt_scores,
            "pae_logits": confidence_outputs.pae_logits,
            "ptm_score": confidence_outputs.ptm_score,
            "recycle_state": RecyclingState(
                single_repr=structure_outputs.single_repr,
                pair_repr=pair_repr,
            ),
        }
