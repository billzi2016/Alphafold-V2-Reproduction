"""PDB 输出工具。"""

from __future__ import annotations

from pathlib import Path

from af2_repro.common.protein import ProteinStructure


ATOM_NAMES = ("N", "CA", "C")


def _format_pdb_atom_line(
    *,
    atom_index: int,
    atom_name: str,
    residue_name: str,
    chain_id: str,
    residue_index: int,
    x: float,
    y: float,
    z: float,
) -> str:
    """生成一行 PDB ATOM 记录。"""
    return (
        f"ATOM  {atom_index:5d} {atom_name:^4s}{residue_name:>4s} {chain_id}{residue_index:4d}    "
        f"{x:8.3f}{y:8.3f}{z:8.3f}{1.00:6.2f}{0.00:6.2f}          {atom_name[0]:>2s}"
    )


def write_backbone_pdb(protein: ProteinStructure, output_path: Path, *, chain_id: str = "A") -> None:
    """把最小 backbone 蛋白结构写成 PDB。

    当前 residue name 统一写成 `GLY`，因为还没有 side-chain 与精确残基模板恢复。
    这不是伪造结构，而是对现阶段最小 backbone 输出的诚实表达。
    """
    lines: list[str] = []
    atom_index = 1

    positions = protein.backbone_positions.detach().cpu()
    residue_index = protein.residue_index.detach().cpu().tolist()
    atom_mask = protein.atom_mask.detach().cpu()

    for residue_offset, pdb_residue_index in enumerate(residue_index):
        for atom_offset, atom_name in enumerate(ATOM_NAMES):
            if atom_mask[residue_offset, atom_offset] <= 0:
                continue
            x, y, z = positions[residue_offset, atom_offset].tolist()
            lines.append(
                _format_pdb_atom_line(
                    atom_index=atom_index,
                    atom_name=atom_name,
                    residue_name="GLY",
                    chain_id=chain_id,
                    residue_index=int(pdb_residue_index) + 1,
                    x=x,
                    y=y,
                    z=z,
                )
            )
            atom_index += 1

    lines.append("END")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
