"""蛋白结构对象与坐标工具。"""

from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass(slots=True)
class ProteinStructure:
    """保存最小 backbone 蛋白结构。"""

    sequence: str
    residue_index: torch.Tensor
    backbone_positions: torch.Tensor
    atom_mask: torch.Tensor


def build_backbone_protein(sequence: str, residue_index: torch.Tensor, backbone_positions: torch.Tensor) -> ProteinStructure:
    """根据 backbone 坐标构建最小蛋白结构对象。

    当前只覆盖 N/CA/C 三个 backbone 原子，因此 atom_mask 全为 1。
    """
    atom_mask = torch.ones(backbone_positions.shape[:2], dtype=torch.float32, device=backbone_positions.device)
    return ProteinStructure(
        sequence=sequence,
        residue_index=residue_index,
        backbone_positions=backbone_positions,
        atom_mask=atom_mask,
    )


def protein_to_tensor_dict(protein: ProteinStructure) -> dict[str, torch.Tensor | str]:
    """把 ProteinStructure 转成统一字典。"""
    return {
        "sequence": protein.sequence,
        "residue_index": protein.residue_index,
        "backbone_positions": protein.backbone_positions,
        "atom_mask": protein.atom_mask,
    }


def tensor_dict_to_protein(data: dict[str, torch.Tensor | str]) -> ProteinStructure:
    """把统一字典恢复为 ProteinStructure。"""
    return ProteinStructure(
        sequence=str(data["sequence"]),
        residue_index=torch.as_tensor(data["residue_index"]),
        backbone_positions=torch.as_tensor(data["backbone_positions"]),
        atom_mask=torch.as_tensor(data["atom_mask"]),
    )
