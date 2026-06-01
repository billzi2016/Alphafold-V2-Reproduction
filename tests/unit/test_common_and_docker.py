from pathlib import Path

import torch

from af2_repro.common.protein import build_backbone_protein, protein_to_tensor_dict, tensor_dict_to_protein
from af2_repro.model.params import ParameterLoader, ParameterSource, resolve_checkpoint_path
from docker.run_docker import build_docker_command


def test_protein_tensor_roundtrip() -> None:
    """ProteinStructure 应能在对象和张量字典之间往返。"""
    residue_index = torch.tensor([0, 1], dtype=torch.int64)
    backbone_positions = torch.zeros((2, 3, 3), dtype=torch.float32)
    protein = build_backbone_protein("AC", residue_index, backbone_positions)

    data = protein_to_tensor_dict(protein)
    restored = tensor_dict_to_protein(data)

    assert restored.sequence == "AC"
    assert torch.equal(restored.residue_index, residue_index)
    assert torch.equal(restored.backbone_positions, backbone_positions)


def test_parameter_loader_loads_state_dict(tmp_path: Path) -> None:
    """参数加载器应能从普通 torch 文件读取 state_dict。"""
    state_dict_path = tmp_path / "weights.pt"
    torch.save({"layer.weight": torch.ones((2, 2))}, state_dict_path)

    loader = ParameterLoader(ParameterSource(params_path=state_dict_path, source_name="local"))
    state_dict = loader.load_state_dict()

    assert "layer.weight" in state_dict


def test_resolve_checkpoint_path_finds_checkpoint(tmp_path: Path) -> None:
    """应能从目录中解析出兼容 checkpoint 文件。"""
    checkpoint_path = tmp_path / "model.pt"
    checkpoint_path.write_bytes(b"checkpoint")

    resolved = resolve_checkpoint_path(tmp_path)

    assert resolved == checkpoint_path


def test_build_docker_command_contains_core_arguments(tmp_path: Path) -> None:
    """Docker 命令应包含仓库挂载和 CLI 调用。"""
    command = build_docker_command(
        image="af2-repro:latest",
        repo_root=tmp_path,
        fasta_path=tmp_path / "input.fasta",
        output_dir=tmp_path / "outputs",
        config_path=tmp_path / "config.yaml",
    )

    assert command[0] == "docker"
    assert "af2_repro.cli.predict" in command
    assert str(tmp_path / "input.fasta") in command
