"""残基与原子常量。"""

from __future__ import annotations

RESTYPES = "ACDEFGHIKLMNPQRSTVWY"
RESTYPE_ORDER = {residue: index for index, residue in enumerate(RESTYPES)}
UNK_RESTYPE_INDEX = len(RESTYPES)
BACKBONE_ATOM_NAMES = ("N", "CA", "C")
ATOM_ORDER = {atom_name: index for index, atom_name in enumerate(BACKBONE_ATOM_NAMES)}


def residue_to_index(residue: str) -> int:
    """把氨基酸字符映射到整数索引。

    当前先实现最小可用映射：
    - 标准 20 种氨基酸映射到固定索引
    - 其余允许字符统一映射到 unknown 索引
    """
    return RESTYPE_ORDER.get(residue, UNK_RESTYPE_INDEX)


def atom_name_to_index(atom_name: str) -> int:
    """把 backbone 原子名映射到索引。"""
    if atom_name not in ATOM_ORDER:
        raise KeyError(f"不支持的原子名: {atom_name}")
    return ATOM_ORDER[atom_name]
