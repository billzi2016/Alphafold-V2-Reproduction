"""Amber relaxation 接口。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class RelaxationResult:
    """表示一次 relaxation 结果。"""

    success: bool
    output_path: Path | None
    message: str


def run_relaxation(input_pdb_path: Path, output_pdb_path: Path) -> RelaxationResult:
    """执行 Amber relaxation。

    当前仓库不强依赖 OpenMM。若环境中没有 OpenMM，则返回明确说明，
    但不会伪造 relaxed 结果文件。
    """
    try:
        import openmm  # noqa: F401
    except Exception as exc:  # pragma: no cover - 取决于本机环境
        return RelaxationResult(
            success=False,
            output_path=None,
            message=f"OpenMM 不可用，未执行 relaxation: {exc}",
        )

    return RelaxationResult(
        success=False,
        output_path=None,
        message="当前仓库已保留 relaxation 接口，但尚未接入完整 Amber relaxation 细节。",
    )
