import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_smoke(tmp_path: Path) -> None:
    """命令行入口应能跑通当前阶段完整流程。"""
    repo_root = Path(__file__).resolve().parents[2]
    fasta_path = repo_root / "examples" / "fastas" / "target_example.fasta"
    config_path = repo_root / "configs" / "inference" / "monomer.yaml"
    output_dir = tmp_path / "smoke_outputs"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")

    command = [
        sys.executable,
        "-m",
        "af2_repro.cli.predict",
        "--fasta-path",
        str(fasta_path),
        "--output-dir",
        str(output_dir),
        "--config-path",
        str(config_path),
    ]

    subprocess.run(command, check=True, cwd=repo_root, env=env)

    config_data = json.loads((output_dir / "run_config.json").read_text(encoding="utf-8"))
    assert config_data["sequence_length"] == 34
    assert (output_dir / "features.pkl").exists()
    assert (output_dir / "result_model_1.pkl").exists()
    assert (output_dir / "ranking_debug.json").exists()
    assert (output_dir / "unrelaxed_model_1.pdb").exists()
    assert (output_dir / "ranked_0.pdb").exists()
    assert (output_dir / "timings.json").exists()
