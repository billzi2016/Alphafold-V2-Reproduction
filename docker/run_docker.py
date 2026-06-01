"""Docker 运行命令生成器。"""

from __future__ import annotations

import argparse
import shlex
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""
    parser = argparse.ArgumentParser(description="Generate docker run command for af2-repro")
    parser.add_argument("--image", type=str, default="af2-repro:latest", help="Docker 镜像名。")
    parser.add_argument("--repo-root", type=Path, required=True, help="仓库根目录。")
    parser.add_argument("--fasta-path", type=Path, required=True, help="输入 FASTA 路径。")
    parser.add_argument("--output-dir", type=Path, required=True, help="输出目录。")
    parser.add_argument("--config-path", type=Path, required=True, help="推理配置路径。")
    return parser


def build_docker_command(*, image: str, repo_root: Path, fasta_path: Path, output_dir: Path, config_path: Path) -> list[str]:
    """生成 docker run 命令列表。"""
    return [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{repo_root}:/workspace",
        "-w",
        "/workspace",
        image,
        "python3",
        "-m",
        "af2_repro.cli.predict",
        "--fasta-path",
        str(fasta_path),
        "--output-dir",
        str(output_dir),
        "--config-path",
        str(config_path),
    ]


def main() -> None:
    """打印 docker run 命令。"""
    args = build_parser().parse_args()
    command = build_docker_command(
        image=args.image,
        repo_root=args.repo_root,
        fasta_path=args.fasta_path,
        output_dir=args.output_dir,
        config_path=args.config_path,
    )
    print(" ".join(shlex.quote(token) for token in command))


if __name__ == "__main__":
    main()
