from pathlib import Path

import torch

from af2_repro.data.fasta import read_single_fasta
from af2_repro.data.feature_pipeline import FeaturePipeline
from af2_repro.model.config import InferenceConfig
from af2_repro.model.model import AlphaFoldLikeModel


def test_model_forward_returns_expected_shapes(tmp_path: Path) -> None:
    """最小模型前向应返回稳定的表示张量 shape。"""
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")

    record = read_single_fasta(fasta_path)
    features = FeaturePipeline(record=record).build()
    model = AlphaFoldLikeModel(
        InferenceConfig(
            msa_channel=32,
            pair_channel=16,
            num_heads_msa=4,
            num_heads_pair=4,
            num_evoformer_blocks=2,
        )
    )

    outputs = model(features)
    model_device = next(model.parameters()).device

    assert isinstance(outputs["msa_repr"], torch.Tensor)
    assert isinstance(outputs["pair_repr"], torch.Tensor)
    assert isinstance(outputs["single_repr"], torch.Tensor)
    assert isinstance(outputs["translations"], torch.Tensor)
    assert isinstance(outputs["backbone_positions"], torch.Tensor)
    assert isinstance(outputs["plddt_logits"], torch.Tensor)
    assert isinstance(outputs["plddt_scores"], torch.Tensor)
    assert isinstance(outputs["pae_logits"], torch.Tensor)
    assert isinstance(outputs["ptm_score"], torch.Tensor)
    assert outputs["msa_repr"].shape == (1, 4, 32)
    assert outputs["pair_repr"].shape == (4, 4, 16)
    assert outputs["seq_mask"].shape == (4,)
    assert outputs["single_repr"].shape == (4, 32)
    assert outputs["translations"].shape == (4, 3)
    assert outputs["backbone_positions"].shape == (4, 3, 3)
    assert outputs["plddt_logits"].shape == (4, 50)
    assert outputs["plddt_scores"].shape == (4,)
    assert outputs["pae_logits"].shape == (4, 4, 64)
    assert outputs["ptm_score"].shape == ()
    assert outputs["msa_repr"].device == model_device
    assert outputs["pair_repr"].device == model_device
    assert outputs["single_repr"].device == model_device
