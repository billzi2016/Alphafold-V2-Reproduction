"""结果目录摘要脚本。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""
    parser = argparse.ArgumentParser(description="Summarize AlphaFold V2 Reproduction outputs")
    parser.add_argument("output_dir", type=Path, help="待汇总的输出目录。")
    return parser


def main() -> None:
    """输出当前结果目录的核心摘要。"""
    args = build_parser().parse_args()
    output_dir = args.output_dir

    print(f"output_dir={output_dir}")

    run_config_path = output_dir / "run_config.json"
    ranking_path = output_dir / "ranking_debug.json"
    timings_path = output_dir / "timings.json"

    if run_config_path.exists():
        run_config = json.loads(run_config_path.read_text(encoding="utf-8"))
        print(f"sequence_header={run_config.get('sequence_header')}")
        print(f"sequence_length={run_config.get('sequence_length')}")
        print(f"num_recycle={run_config.get('num_recycle')}")
        print(f"model_preset={run_config.get('model_preset')}")

    if ranking_path.exists():
        ranking = json.loads(ranking_path.read_text(encoding="utf-8"))
        order = ranking.get("order", [])
        print(f"ranking_order={order}")
        if order:
            top_model = order[0]
            print(f"top_model={top_model}")
            print(f"top_plddt={ranking.get('plddts', {}).get(top_model)}")
            print(f"top_ptm={ranking.get('ptm', {}).get(top_model)}")

    if timings_path.exists():
        timings = json.loads(timings_path.read_text(encoding="utf-8"))
        for key, value in timings.items():
            print(f"{key}={value}")


if __name__ == "__main__":
    main()
