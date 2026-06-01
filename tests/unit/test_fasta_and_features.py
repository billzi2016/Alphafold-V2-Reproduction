from pathlib import Path

import pytest

from af2_repro.data.fasta import read_single_fasta
from af2_repro.data.feature_pipeline import FeaturePipeline


def test_read_single_fasta_returns_record(tmp_path: Path) -> None:
    """单条 FASTA 应被正确解析。"""
    fasta_path = tmp_path / "sample.fasta"
    fasta_path.write_text(">sample\nACDEFGHIK\n", encoding="utf-8")

    record = read_single_fasta(fasta_path)

    assert record.header == "sample"
    assert record.sequence == "ACDEFGHIK"


def test_read_single_fasta_rejects_invalid_residue(tmp_path: Path) -> None:
    """非法氨基酸字符应被拒绝。"""
    fasta_path = tmp_path / "invalid.fasta"
    fasta_path.write_text(">invalid\nACDEFGHIKJ\n", encoding="utf-8")

    with pytest.raises(ValueError, match="非法氨基酸字符"):
        read_single_fasta(fasta_path)


def test_feature_pipeline_builds_sequence_features(tmp_path: Path) -> None:
    """特征构建应输出最小 sequence features 集合。"""
    fasta_path = tmp_path / "feature.fasta"
    fasta_path.write_text(">feature\nACD\n", encoding="utf-8")

    record = read_single_fasta(fasta_path)
    features = FeaturePipeline(record=record).build()

    assert features["header"] == "feature"
    assert features["sequence"] == "ACD"
    assert features["sequence_length"] == 3
    assert features["aatype"].tolist() == [0, 1, 2]
    assert features["residue_index"].tolist() == [0, 1, 2]
    assert features["seq_mask"].tolist() == [1.0, 1.0, 1.0]
