# Manual Run Record

## 基本信息

- 输出目录：`artifacts/outputs/manual_run_full`
- 输入 FASTA：`examples/fastas/target_example.fasta`
- 配置文件：`configs/inference/monomer.yaml`
- 运行方式：`bash scripts/run_monomer.sh examples/fastas/target_example.fasta artifacts/outputs/manual_run_full configs/inference/monomer.yaml`

## 当前阶段已生成文件

- `run.log`
- `run_config.json`
- `features.pkl`
- `result_model_1.pkl`
- `ranking_debug.json`
- `unrelaxed_model_1.pdb`
- `ranked_0.pdb`
- `timings.json`

## 运行摘要

- `sequence_header`: `target_example`
- `sequence_length`: `34`
- `num_recycle`: `3`
- `model_preset`: `monomer`

## 当前阶段说明

- 本次结果来自当前仓库内已实现的 PyTorch 前向链路。
- 当前已覆盖 `InputEmbedding -> Evoformer -> StructureModule -> ConfidenceHeads -> result/pdb/ranking 输出`。
- 当前 `PDB` 只包含 backbone 原子。
- 当前结果尚未接入真实数据库驱动的 `MSA/template` 检索与真实权重映射，因此不能作为与官方参考实现对齐的最终结果。
