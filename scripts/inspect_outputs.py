"""输出目录检查脚本。"""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""
    parser = argparse.ArgumentParser(description="Inspect AlphaFold V2 Reproduction outputs")
    parser.add_argument("output_dir", type=Path, help="待检查的输出目录。")
    return parser


def main() -> None:
    """检查输出目录中已经生成的关键文件。"""
    args = build_parser().parse_args()
    output_dir = args.output_dir

    expected_files = [
        "run.log",
        "run_config.json",
        "features.pkl",
        "result_model_1.pkl",
        "timings.json",
        "ranking_debug.json",
        "unrelaxed_model_1.pdb",
        "ranked_0.pdb",
    ]

    print(f"output_dir={output_dir}")
    for name in expected_files:
        path = output_dir / name
        status = "FOUND" if path.exists() else "MISSING"
        print(f"{name}={status}")


if __name__ == "__main__":
    main()
