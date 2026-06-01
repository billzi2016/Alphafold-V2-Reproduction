from pathlib import Path

import torch

from af2_repro.data.fasta import read_single_fasta
from af2_repro.inference.runner import InferenceRunner
from af2_repro.model.config import build_project_config_bundle
from af2_repro.model.model import AlphaFoldLikeModel


def test_runner_writes_current_outputs(tmp_path: Path) -> None:
    """Runner 应写出当前阶段完整输出文件。"""
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")

    record = read_single_fasta(fasta_path)
    config_bundle = build_project_config_bundle(
        {
            "runtime": {"device": "cpu", "seed": 42},
            "inference": {
                "model_preset": "monomer",
                "db_preset": "reduced_dbs",
                "num_recycle": 2,
                "msa_channel": 32,
                "pair_channel": 16,
                "num_heads_msa": 4,
                "num_heads_pair": 4,
                "num_evoformer_blocks": 1,
            },
        }
    )
    runner = InferenceRunner(output_dir=tmp_path / "outputs", runtime_summary={}, config_bundle=config_bundle)
    runner.run(record)

    assert (tmp_path / "outputs" / "features.pkl").exists()
    assert (tmp_path / "outputs" / "result_model_1.pkl").exists()
    assert (tmp_path / "outputs" / "ranking_debug.json").exists()
    assert (tmp_path / "outputs" / "unrelaxed_model_1.pdb").exists()
    assert (tmp_path / "outputs" / "ranked_0.pdb").exists()
    assert (tmp_path / "outputs" / "timings.json").exists()
    assert (tmp_path / "outputs" / "parameters.json").exists()


def test_runner_loads_compatible_checkpoint(tmp_path: Path) -> None:
    """提供兼容 checkpoint 时，runner 应尝试加载并记录参数状态。"""
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")
    checkpoint_path = tmp_path / "compatible.pt"

    model = AlphaFoldLikeModel(
        build_project_config_bundle(
            {
                "runtime": {"device": "cpu", "seed": 42},
                "inference": {
                    "model_preset": "monomer",
                    "db_preset": "reduced_dbs",
                    "num_recycle": 1,
                    "msa_channel": 32,
                    "pair_channel": 16,
                    "num_heads_msa": 4,
                    "num_heads_pair": 4,
                    "num_evoformer_blocks": 1,
                },
            }
        ).inference
    )
    torch.save(model.state_dict(), checkpoint_path)

    record = read_single_fasta(fasta_path)
    config_bundle = build_project_config_bundle(
        {
            "runtime": {"device": "cpu", "seed": 42},
            "inference": {
                "model_preset": "monomer",
                "db_preset": "reduced_dbs",
                "num_recycle": 1,
                "msa_channel": 32,
                "pair_channel": 16,
                "num_heads_msa": 4,
                "num_heads_pair": 4,
                "num_evoformer_blocks": 1,
            },
        },
        paths_data={
            "paths": {
                "params_dir": str(tmp_path),
                "params_checkpoint": str(checkpoint_path),
                "databases_dir": str(tmp_path / "databases"),
                "output_root": str(tmp_path / "outputs_root"),
                "cache_dir": str(tmp_path / "cache"),
            }
        },
    )
    runner = InferenceRunner(output_dir=tmp_path / "outputs_ckpt", runtime_summary={}, config_bundle=config_bundle)
    runner.run(record)

    parameters_json = (tmp_path / "outputs_ckpt" / "parameters.json").read_text(encoding="utf-8")
    assert "\"status\": \"loaded\"" in parameters_json
