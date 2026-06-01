"""模型与推理配置定义。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RuntimeConfig:
    """运行时配置。"""

    device: str = "cpu"
    seed: int = 42


@dataclass(slots=True)
class InferenceConfig:
    """推理阶段配置。

    当前只保留第一阶段最核心的配置项，后续再往这里补 batch、chunk、
    template 开关和更细粒度的模型选择逻辑。
    """

    model_preset: str = "monomer"
    db_preset: str = "reduced_dbs"
    num_recycle: int = 3
    max_template_date: str = "2021-11-01"
    run_relaxation: bool = False
    msa_channel: int = 256
    pair_channel: int = 128
    num_heads_msa: int = 8
    num_heads_pair: int = 4
    transition_multiplier: int = 4
    num_evoformer_blocks: int = 2


@dataclass(slots=True)
class PathsConfig:
    """仓库外部数据、参数和输出路径配置。"""

    params_dir: Path
    databases_dir: Path
    output_root: Path
    cache_dir: Path
    params_checkpoint: Path | None = None


@dataclass(slots=True)
class DatabaseConfig:
    """数据库路径配置。"""

    entries: dict[str, Path]


@dataclass(slots=True)
class ProjectConfigBundle:
    """把本次运行所需的配置聚合到一个对象里。"""

    runtime: RuntimeConfig
    inference: InferenceConfig
    paths: PathsConfig | None = None
    databases: DatabaseConfig | None = None


def _require_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    """读取一个必须为字典的配置段。"""
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"配置字段 {key} 必须是字典。")
    return value


def build_runtime_config(data: dict[str, Any]) -> RuntimeConfig:
    """从原始 YAML 字典构建 RuntimeConfig。"""
    runtime = _require_dict(data, "runtime")
    return RuntimeConfig(
        device=str(runtime.get("device", "cpu")),
        seed=int(runtime.get("seed", 42)),
    )


def build_inference_config(data: dict[str, Any]) -> InferenceConfig:
    """从原始 YAML 字典构建 InferenceConfig。"""
    inference = _require_dict(data, "inference")
    return InferenceConfig(
        model_preset=str(inference.get("model_preset", "monomer")),
        db_preset=str(inference.get("db_preset", "reduced_dbs")),
        num_recycle=int(inference.get("num_recycle", 3)),
        max_template_date=str(inference.get("max_template_date", "2021-11-01")),
        run_relaxation=bool(inference.get("run_relaxation", False)),
        msa_channel=int(inference.get("msa_channel", 256)),
        pair_channel=int(inference.get("pair_channel", 128)),
        num_heads_msa=int(inference.get("num_heads_msa", 8)),
        num_heads_pair=int(inference.get("num_heads_pair", 4)),
        transition_multiplier=int(inference.get("transition_multiplier", 4)),
        num_evoformer_blocks=int(inference.get("num_evoformer_blocks", 2)),
    )


def build_paths_config(data: dict[str, Any]) -> PathsConfig:
    """从原始 YAML 字典构建 PathsConfig。"""
    paths = _require_dict(data, "paths")
    return PathsConfig(
        params_dir=Path(paths["params_dir"]),
        databases_dir=Path(paths["databases_dir"]),
        output_root=Path(paths["output_root"]),
        cache_dir=Path(paths["cache_dir"]),
        params_checkpoint=Path(paths["params_checkpoint"]) if paths.get("params_checkpoint") else None,
    )


def build_database_config(data: dict[str, Any]) -> DatabaseConfig:
    """从原始 YAML 字典构建 DatabaseConfig。"""
    databases = _require_dict(data, "databases")
    return DatabaseConfig(entries={key: Path(value) for key, value in databases.items()})


def build_project_config_bundle(
    inference_data: dict[str, Any],
    *,
    paths_data: dict[str, Any] | None = None,
    database_data: dict[str, Any] | None = None,
) -> ProjectConfigBundle:
    """组装项目运行所需的配置对象。"""
    return ProjectConfigBundle(
        runtime=build_runtime_config(inference_data),
        inference=build_inference_config(inference_data),
        paths=build_paths_config(paths_data) if paths_data is not None else None,
        databases=build_database_config(database_data) if database_data is not None else None,
    )
