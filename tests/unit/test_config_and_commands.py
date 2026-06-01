from pathlib import Path

import pytest

from af2_repro.data import msa_pipeline as msa_pipeline_module
from af2_repro.data import template_pipeline as template_pipeline_module
from af2_repro.data.msa_pipeline import MsaPipeline
from af2_repro.data.template_pipeline import TemplatePipeline
from af2_repro.model.config import build_project_config_bundle
from af2_repro.model.params import ParameterLoader, ParameterSource


def test_build_project_config_bundle_parses_fields() -> None:
    """配置对象应能正确解析核心字段。"""
    bundle = build_project_config_bundle(
        {
            "runtime": {"device": "cuda", "seed": 7},
            "inference": {
                "model_preset": "monomer",
                "db_preset": "reduced_dbs",
                "num_recycle": 4,
                "max_template_date": "2021-11-01",
                "msa_channel": 192,
                "pair_channel": 96,
            },
        },
        paths_data={
            "paths": {
                "params_dir": "/tmp/params",
                "databases_dir": "/tmp/databases",
                "output_root": "/tmp/outputs",
                "cache_dir": "/tmp/cache",
            }
        },
        database_data={
            "databases": {
                "uniref90": "/tmp/databases/uniref90",
                "pdb70": "/tmp/databases/pdb70",
            }
        },
    )

    assert bundle.runtime.device == "cuda"
    assert bundle.runtime.seed == 7
    assert bundle.inference.num_recycle == 4
    assert bundle.inference.msa_channel == 192
    assert bundle.inference.pair_channel == 96
    assert bundle.paths is not None
    assert bundle.databases is not None


def test_msa_pipeline_plans_reduced_db_commands(tmp_path: Path) -> None:
    """轻量数据库配置应规划出真实 MSA 命令列表。"""
    databases_dir = tmp_path / "databases"
    (databases_dir / "uniref90").mkdir(parents=True)
    (databases_dir / "mgnify").mkdir(parents=True)
    (databases_dir / "small_bfd").mkdir(parents=True)
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")

    pipeline = MsaPipeline(
        output_dir=tmp_path / "outputs",
        db_preset="reduced_dbs",
        databases_dir=databases_dir,
        fasta_path=fasta_path,
    )

    commands = pipeline.plan_commands()

    assert len(commands) == 3
    assert commands[0][0] == "jackhmmer"
    assert commands[1][0] == "jackhmmer"
    assert commands[2][0] == "hhblits"


def test_template_pipeline_builds_hhsearch_command(tmp_path: Path) -> None:
    """模板检索应能拼出 hhsearch 命令。"""
    databases_dir = tmp_path / "databases"
    (databases_dir / "pdb70").mkdir(parents=True)
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")
    input_a3m = tmp_path / "query.a3m"
    input_a3m.write_text(">target\nACDE\n", encoding="utf-8")

    pipeline = TemplatePipeline(
        databases_dir=databases_dir,
        max_template_date="2021-11-01",
        fasta_path=fasta_path,
        output_dir=tmp_path / "outputs",
    )

    command = pipeline.build_hhsearch_command(
        input_a3m=input_a3m,
        output_hhr=tmp_path / "outputs" / "template_hits.hhr",
    )

    assert command[0] == "hhsearch"
    assert "-i" in command
    assert "-d" in command


def test_msa_pipeline_run_writes_command_plan(tmp_path: Path, monkeypatch) -> None:
    """MSA pipeline 运行时应写出命令计划并逐条调用执行器。"""
    databases_dir = tmp_path / "databases"
    (databases_dir / "uniref90").mkdir(parents=True)
    (databases_dir / "mgnify").mkdir(parents=True)
    (databases_dir / "small_bfd").mkdir(parents=True)
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")

    called_commands: list[list[str]] = []

    monkeypatch.setattr(msa_pipeline_module, "require_executable", lambda name: f"/usr/bin/{name}")

    def fake_run_command(command, **kwargs):
        called_commands.append(command)
        return None

    monkeypatch.setattr(msa_pipeline_module, "run_command", fake_run_command)

    pipeline = MsaPipeline(
        output_dir=tmp_path / "outputs",
        db_preset="reduced_dbs",
        databases_dir=databases_dir,
        fasta_path=fasta_path,
    )
    result = pipeline.run()

    assert len(called_commands) == 3
    assert (tmp_path / "outputs" / "msas" / "msa_commands.json").exists()
    assert "commands" in result


def test_msa_pipeline_reuses_existing_outputs(tmp_path: Path, monkeypatch) -> None:
    """已有 MSA 文件时应直接复用，不重复执行命令。"""
    databases_dir = tmp_path / "databases"
    databases_dir.mkdir()
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")
    msas_dir = tmp_path / "outputs" / "msas"
    msas_dir.mkdir(parents=True)
    (msas_dir / "small_bfd_hits.a3m").write_text(">target\nACDE\n", encoding="utf-8")

    monkeypatch.setattr(msa_pipeline_module, "require_executable", lambda name: f"/usr/bin/{name}")

    pipeline = MsaPipeline(
        output_dir=tmp_path / "outputs",
        db_preset="reduced_dbs",
        databases_dir=databases_dir,
        fasta_path=fasta_path,
        reuse_existing=True,
    )
    result = pipeline.run()

    assert result["commands"] == []
    assert result["msa_records"] == [("target", "ACDE")]


def test_template_pipeline_run_writes_command_plan(tmp_path: Path, monkeypatch) -> None:
    """Template pipeline 运行时应写出命令计划并调用执行器。"""
    databases_dir = tmp_path / "databases"
    (databases_dir / "pdb70").mkdir(parents=True)
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")
    input_a3m = tmp_path / "query.a3m"
    input_a3m.write_text(">target\nACDE\n", encoding="utf-8")

    called_commands: list[list[str]] = []

    monkeypatch.setattr(template_pipeline_module, "require_executable", lambda name: f"/usr/bin/{name}")

    def fake_run_command(command, **kwargs):
        called_commands.append(command)
        return None

    monkeypatch.setattr(template_pipeline_module, "run_command", fake_run_command)

    pipeline = TemplatePipeline(
        databases_dir=databases_dir,
        max_template_date="2021-11-01",
        fasta_path=fasta_path,
        output_dir=tmp_path / "outputs",
    )
    result = pipeline.run(input_a3m=input_a3m)

    assert len(called_commands) == 1
    assert (tmp_path / "outputs" / "templates" / "template_command.json").exists()
    assert result["command"][0] == "hhsearch"


def test_template_pipeline_reuses_existing_output(tmp_path: Path, monkeypatch) -> None:
    """已有 HHR 文件时应直接复用。"""
    databases_dir = tmp_path / "databases"
    databases_dir.mkdir()
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")
    templates_dir = tmp_path / "outputs" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "template_hits.hhr").write_text(
        " No Hit                             Prob E-value Score Cols Query HMM  Template HMM\n"
        "  1 1abc_A                          99.8 1E-20 200.0 50   1-50       1-50\n\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(template_pipeline_module, "require_executable", lambda name: f"/usr/bin/{name}")

    pipeline = TemplatePipeline(
        databases_dir=databases_dir,
        max_template_date="2021-11-01",
        fasta_path=fasta_path,
        output_dir=tmp_path / "outputs",
        reuse_existing=True,
    )
    result = pipeline.run(input_a3m=fasta_path)

    assert result["command"] == []
    assert len(result["template_hits"]) == 1


def test_parameter_loader_builds_metadata(tmp_path: Path) -> None:
    """参数加载器应能记录路径与来源信息。"""
    params_dir = tmp_path / "params"
    params_dir.mkdir()

    loader = ParameterLoader(
        ParameterSource(
            params_path=params_dir,
            source_name="deepmind-official",
            version="2022-12-06",
        )
    )

    metadata = loader.build_metadata()

    assert metadata["params_path"] == str(params_dir)
    assert metadata["source_name"] == "deepmind-official"
    assert metadata["version"] == "2022-12-06"
    assert metadata["is_directory"] is True


def test_msa_pipeline_rejects_invalid_db_preset(tmp_path: Path) -> None:
    """非法 db_preset 应被拒绝。"""
    databases_dir = tmp_path / "databases"
    databases_dir.mkdir()
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")

    pipeline = MsaPipeline(
        output_dir=tmp_path / "outputs",
        db_preset="invalid",
        databases_dir=databases_dir,
        fasta_path=fasta_path,
    )

    with pytest.raises(ValueError, match="不支持的 db_preset"):
        pipeline.validate_inputs()


def test_template_pipeline_requires_template_date(tmp_path: Path) -> None:
    """模板日期不能为空。"""
    databases_dir = tmp_path / "databases"
    databases_dir.mkdir()
    fasta_path = tmp_path / "target.fasta"
    fasta_path.write_text(">target\nACDE\n", encoding="utf-8")

    pipeline = TemplatePipeline(
        databases_dir=databases_dir,
        max_template_date="",
        fasta_path=fasta_path,
        output_dir=tmp_path / "outputs",
    )

    with pytest.raises(ValueError, match="max_template_date 不能为空"):
        pipeline.validate_inputs()
