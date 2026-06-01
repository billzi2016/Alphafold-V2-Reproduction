from pathlib import Path

from af2_repro.data.feature_pipeline import FeaturePipeline
from af2_repro.data.fasta import read_single_fasta
from af2_repro.data.parsers import parse_a3m, parse_hhr, parse_stockholm


def test_parse_a3m_returns_records() -> None:
    """A3M 解析应返回 header/sequence 列表。"""
    records = parse_a3m(">a\nACD-\n>b\nACE-\n")
    assert records == [("a", "ACD-"), ("b", "ACE-")]


def test_parse_stockholm_returns_records() -> None:
    """Stockholm 解析应合并同名序列片段。"""
    records = parse_stockholm("# STOCKHOLM 1.0\na ACD\nb ACE\n//\n")
    assert records == [("a", "ACD"), ("b", "ACE")]


def test_parse_hhr_extracts_hits() -> None:
    """HHR 解析应提取简化 hit 表。"""
    text = (
        " No Hit                             Prob E-value Score Cols Query HMM  Template HMM\n"
        "  1 1abc_A                          99.8 1E-20 200.0 50   1-50       1-50\n"
        "\n"
    )
    hits = parse_hhr(text)
    assert len(hits) == 1
    assert hits[0].name == "1-50"


def test_feature_pipeline_adds_msa_and_template_features(tmp_path: Path) -> None:
    """扩展后的特征构建应包含 MSA 和 template 容器字段。"""
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")
    record = read_single_fasta(fasta_path)
    features = FeaturePipeline(record=record, msa_records=[("target", "ACDE")]).build()

    assert features["msa_count"] == 1
    assert features["msa_aatype"].shape == (1, 4)
    assert features["msa_mask"].shape == (1, 4)
    assert features["template_mask"].shape == (4, 4)
    assert features["template_probability"].shape == (4,)
