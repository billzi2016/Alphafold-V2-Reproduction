"""推理调度入口。"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from af2_repro.common.protein import build_backbone_protein
from af2_repro.data.fasta import FastaRecord
from af2_repro.data.feature_pipeline import FeaturePipeline
from af2_repro.data.msa_pipeline import MsaPipeline
from af2_repro.data.template_pipeline import TemplatePipeline
from af2_repro.io.pdb import write_backbone_pdb
from af2_repro.io.json_io import save_json
from af2_repro.io.pickle_io import save_pickle
from af2_repro.model.config import ProjectConfigBundle
from af2_repro.model.model import AlphaFoldLikeModel
from af2_repro.model.params import ParameterLoader, ParameterSource, resolve_checkpoint_path
from af2_repro.relax.amber_relaxation import run_relaxation
from af2_repro.utils.logging import get_logger
from af2_repro.utils.paths import ensure_directory
from af2_repro.utils.runtime import resolve_device


@dataclass(slots=True)
class InferenceRunner:
    """统一管理推理阶段的执行顺序。

    当前版本已经覆盖：
    - 输入解析与 sequence features
    - 模型前向
    - 多轮 recycle 调度
    - result pickle / ranking / PDB / timings 输出
    """

    output_dir: Path
    runtime_summary: dict[str, Any]
    config_bundle: ProjectConfigBundle

    def _to_serializable(self, value: Any) -> Any:
        """把模型输出转换成可 pickle/JSON 的对象。"""
        if isinstance(value, torch.Tensor):
            return value.detach().cpu()
        return value

    def _build_ranking_debug(self, model_outputs: dict[str, Any]) -> dict[str, Any]:
        """根据当前置信度输出构造 ranking 信息。"""
        plddt_scores = model_outputs["plddt_scores"].detach().cpu()
        mean_plddt = float(plddt_scores.mean().item())
        ptm_score = float(model_outputs["ptm_score"].detach().cpu().item())
        return {
            "order": ["model_1"],
            "plddts": {"model_1": mean_plddt},
            "ptm": {"model_1": ptm_score},
            "ranking_confidence": {"model_1": mean_plddt},
        }

    def _prepare_features(self, record: FastaRecord, logger) -> dict[str, Any]:
        """准备模型输入特征。

        若提供了数据库配置，则优先执行真实 MSA/template 流程；
        否则回退为纯序列特征。
        """
        msa_records = None
        template_hits = None

        if self.config_bundle.paths is not None and self.config_bundle.databases is not None:
            database_paths = self.config_bundle.databases.entries
            msa_pipeline = MsaPipeline(
                output_dir=self.output_dir,
                db_preset=self.config_bundle.inference.db_preset,
                databases_dir=self.config_bundle.paths.databases_dir,
                fasta_path=Path(self.runtime_summary["fasta_path"]),
                database_paths=database_paths,
            )
            logger.info("开始执行 MSA 流程")
            msa_result = msa_pipeline.run()
            msa_records = msa_result.get("msa_records")  # type: ignore[assignment]

            msas_dir = msa_pipeline.prepare_output_dir()
            preferred_a3m = msa_pipeline.locate_preferred_a3m(msas_dir)
            if preferred_a3m is not None:
                logger.info("开始执行 template 流程")
                template_pipeline = TemplatePipeline(
                    databases_dir=self.config_bundle.paths.databases_dir,
                    max_template_date=self.config_bundle.inference.max_template_date,
                    fasta_path=Path(self.runtime_summary["fasta_path"]),
                    output_dir=self.output_dir,
                    database_paths=database_paths,
                )
                template_result = template_pipeline.run(input_a3m=preferred_a3m)
                template_hits = template_result.get("template_hits")  # type: ignore[assignment]
            else:
                logger.info("未找到可用于 template 搜索的 A3M 文件，跳过 template 流程")

        feature_pipeline = FeaturePipeline(
            record=record,
            msa_records=msa_records,
            template_hits=template_hits,
        )
        return feature_pipeline.build()

    def _load_model_parameters(self, model: AlphaFoldLikeModel, logger) -> dict[str, Any]:
        """按当前配置尝试加载兼容参数。"""
        if self.config_bundle.paths is None:
            return {"status": "skipped", "reason": "paths config not provided"}

        params_dir = self.config_bundle.paths.params_dir
        checkpoint_path = resolve_checkpoint_path(params_dir, self.config_bundle.paths.params_checkpoint)
        metadata = {
            "params_dir": str(params_dir),
            "checkpoint_path": str(checkpoint_path) if checkpoint_path is not None else None,
        }
        if checkpoint_path is None:
            metadata["status"] = "skipped"
            metadata["reason"] = "no compatible checkpoint file found"
            return metadata

        loader = ParameterLoader(
            ParameterSource(
                params_path=checkpoint_path,
                source_name="local-compatible-checkpoint",
            )
        )
        state_dict = loader.load_state_dict(map_location="cpu")
        load_result = model.load_state_dict(state_dict, strict=False)
        metadata.update(
            {
                "status": "loaded",
                "missing_keys": list(load_result.missing_keys),
                "unexpected_keys": list(load_result.unexpected_keys),
            }
        )
        logger.info("已尝试加载 checkpoint: %s", checkpoint_path)
        return metadata

    def run(self, record: FastaRecord) -> dict[str, Any]:
        """执行当前阶段完整可运行推理流程。"""
        ensure_directory(self.output_dir)
        logger = get_logger("af2_repro.inference.runner", log_path=self.output_dir / "run.log")
        status_path = self.output_dir / "run_status.json"
        device = resolve_device(self.config_bundle.runtime.device)
        try:
            preprocess_start = time.perf_counter()
            logger.info("开始构建输入特征")
            features = self._prepare_features(record, logger)
            preprocess_seconds = time.perf_counter() - preprocess_start

            save_pickle(features, self.output_dir / "features.pkl")
            logger.info("features.pkl 已写出")

            model = AlphaFoldLikeModel(self.config_bundle.inference).to(device)
            parameter_status = self._load_model_parameters(model, logger)
            save_json(parameter_status, self.output_dir / "parameters.json")
            recycle_state = None
            model_outputs: dict[str, Any] | None = None

            model_start = time.perf_counter()
            logger.info("开始执行模型前向")
            for recycle_index in range(self.config_bundle.inference.num_recycle):
                logger.info("执行 recycle 轮次 %s", recycle_index + 1)
                model_outputs = model(features, recycle_state=recycle_state)
                recycle_state = model_outputs["recycle_state"]
            model_seconds = time.perf_counter() - model_start

            assert model_outputs is not None
            serializable_outputs = {
                key: self._to_serializable(value)
                for key, value in model_outputs.items()
                if key != "recycle_state"
            }
            save_pickle(serializable_outputs, self.output_dir / "result_model_1.pkl")
            logger.info("result_model_1.pkl 已写出")

            ranking_debug = self._build_ranking_debug(model_outputs)
            save_json(ranking_debug, self.output_dir / "ranking_debug.json")
            logger.info("ranking_debug.json 已写出")

            protein = build_backbone_protein(
                sequence=record.sequence,
                residue_index=torch.as_tensor(features["residue_index"]),
                backbone_positions=model_outputs["backbone_positions"],
            )
            unrelaxed_path = self.output_dir / "unrelaxed_model_1.pdb"
            ranked_path = self.output_dir / "ranked_0.pdb"
            write_backbone_pdb(protein, unrelaxed_path)
            write_backbone_pdb(protein, ranked_path)
            logger.info("unrelaxed_model_1.pdb 已写出")
            logger.info("ranked_0.pdb 已写出")

            relaxation_result = None
            if self.config_bundle.inference.run_relaxation:
                relaxed_path = self.output_dir / "relaxed_model_1.pdb"
                relaxation_result = run_relaxation(unrelaxed_path, relaxed_path)
                save_json(
                    {
                        "success": relaxation_result.success,
                        "output_path": str(relaxation_result.output_path) if relaxation_result.output_path else None,
                        "message": relaxation_result.message,
                    },
                    self.output_dir / "relaxation.json",
                )

            timings = {
                "feature_build_seconds": round(preprocess_seconds, 6),
                "model_inference_seconds": round(model_seconds, 6),
            }
            save_json(timings, self.output_dir / "timings.json")
            save_json({"status": "success"}, status_path)
            logger.info("timings.json 已写出")

            return {
                "features": features,
                "model_outputs": serializable_outputs,
                "ranking_debug": ranking_debug,
                "timings": timings,
                "relaxation_result": relaxation_result,
                "parameter_status": parameter_status,
            }
        except Exception as exc:
            save_json({"status": "failed", "error": str(exc)}, status_path)
            logger.exception("推理流程失败")
            raise
