"""配置读取工具模块。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from af2_repro.model.config import ProjectConfigBundle, build_project_config_bundle


def load_yaml(path: Path) -> dict[str, Any]:
    """读取 YAML 配置文件并返回字典。

    当前项目大量依赖路径配置、推理配置和数据库配置，统一从这里读取，
    后续如果需要补 schema 校验，也集中在这里扩展。
    """
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"配置文件内容必须是字典结构: {path}")
    return data


def load_project_config_bundle(
    *,
    inference_path: Path,
    paths_path: Path | None = None,
    database_path: Path | None = None,
) -> ProjectConfigBundle:
    """统一加载本次运行的配置集合。

    这样 CLI 和后续 runner 都拿到同一份结构化配置对象，避免散落的
    字典访问逻辑越来越多。
    """
    inference_data = load_yaml(inference_path)
    paths_data = load_yaml(paths_path) if paths_path is not None else None
    database_data = load_yaml(database_path) if database_path is not None else None
    return build_project_config_bundle(
        inference_data,
        paths_data=paths_data,
        database_data=database_data,
    )
