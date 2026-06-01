"""AlphaFold 2 风格推理 CLI 入口。"""

from __future__ import annotations

import argparse
from pathlib import Path

from af2_repro.data.fasta import read_single_fasta
from af2_repro.inference.runner import InferenceRunner
from af2_repro.utils.config import load_project_config_bundle
from af2_repro.utils.logging import get_logger
from af2_repro.utils.paths import ensure_directory, validate_file
from af2_repro.utils.runtime import resolve_device
from af2_repro.io.json_io import save_json


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。

    这里先把第一阶段最关键的入参固定下来：
    - FASTA 路径
    - 输出目录
    - 推理配置路径
    - 关键推理参数覆盖项
    """
    parser = argparse.ArgumentParser(description="AlphaFold V2 Reproduction CLI")
    parser.add_argument("--fasta-path", type=Path, required=True, help="输入 FASTA 文件路径。")
    parser.add_argument("--output-dir", type=Path, required=True, help="推理结果输出目录。")
    parser.add_argument(
        "--config-path",
        type=Path,
        required=True,
        help="推理配置文件路径。",
    )
    parser.add_argument("--paths-config-path", type=Path, default=None, help="路径配置文件路径。")
    parser.add_argument("--database-config-path", type=Path, default=None, help="数据库配置文件路径。")
    parser.add_argument("--device", type=str, default=None, help="覆盖配置中的推理设备。")
    parser.add_argument("--num-recycle", type=int, default=None, help="覆盖配置中的 recycle 次数。")
    parser.add_argument(
        "--max-template-date",
        type=str,
        default=None,
        help="覆盖配置中的最大模板日期，格式示例：2021-11-01。",
    )
    return parser


def _build_runtime_summary(args: argparse.Namespace, config) -> dict:
    """组装本次运行的摘要信息。

    当前先把最关键的输入、配置和推理参数记下来，后续再逐步补充
    数据库版本、模型参数来源和各阶段耗时。
    """
    inference_config = config.inference
    runtime_config = config.runtime
    num_recycle = args.num_recycle if args.num_recycle is not None else inference_config.num_recycle
    max_template_date = args.max_template_date or inference_config.max_template_date
    preferred_device = args.device or runtime_config.device

    return {
        "fasta_path": str(args.fasta_path),
        "output_dir": str(args.output_dir),
        "config_path": str(args.config_path),
        "paths_config_path": str(args.paths_config_path) if args.paths_config_path is not None else None,
        "database_config_path": str(args.database_config_path) if args.database_config_path is not None else None,
        "device": resolve_device(preferred_device),
        "model_preset": inference_config.model_preset,
        "db_preset": inference_config.db_preset,
        "num_recycle": num_recycle,
        "max_template_date": max_template_date,
        "msa_channel": inference_config.msa_channel,
        "pair_channel": inference_config.pair_channel,
    }


def main() -> None:
    """执行第一阶段最小可运行入口。

    当前职责：
    1. 校验输入路径。
    2. 读取 FASTA 与 YAML 配置。
    3. 创建输出目录。
    4. 记录运行摘要和基础日志。

    后续会在此基础上继续串联 MSA、template、feature pipeline 和模型前向。
    """
    args = build_parser().parse_args()
    validate_file(args.fasta_path, "FASTA 文件")
    validate_file(args.config_path, "推理配置文件")
    if args.paths_config_path is not None:
        validate_file(args.paths_config_path, "路径配置文件")
    if args.database_config_path is not None:
        validate_file(args.database_config_path, "数据库配置文件")
    ensure_directory(args.output_dir)

    log_path = args.output_dir / "run.log"
    logger = get_logger("af2_repro.cli.predict", log_path=log_path)

    config = load_project_config_bundle(
        inference_path=args.config_path,
        paths_path=args.paths_config_path,
        database_path=args.database_config_path,
    )
    record = read_single_fasta(args.fasta_path)
    runtime_summary = _build_runtime_summary(args, config)
    runtime_summary["sequence_length"] = len(record.sequence)
    runtime_summary["sequence_header"] = record.header

    save_json(runtime_summary, args.output_dir / "run_config.json")

    runner = InferenceRunner(
        output_dir=args.output_dir,
        runtime_summary=runtime_summary,
        config_bundle=config,
    )
    runner.run(record)

    logger.info("CLI 初始化完成")
    logger.info("FASTA header: %s", record.header)
    logger.info("Sequence length: %s", len(record.sequence))
    logger.info("Runtime summary saved to %s", args.output_dir / "run_config.json")
    logger.info("当前阶段已完成当前可用模型前向与结果落盘")


if __name__ == "__main__":
    main()
