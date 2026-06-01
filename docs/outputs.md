# Outputs

当前输出目录会生成以下文件：

- `run.log`：运行日志
- `run_config.json`：本次运行参数摘要
- `features.pkl`：特征构建结果
- `result_model_1.pkl`：当前模型前向中间结果与结构相关张量
- `ranking_debug.json`：当前 ranking 信息
- `unrelaxed_model_1.pdb`：当前阶段最小 backbone PDB 输出
- `ranked_0.pdb`：当前最优结果文件
- `timings.json`：特征构建与模型前向耗时

说明：

- 当前 `result_model_1.pkl` 包含 `msa_repr`、`pair_repr`、`single_repr`、`translations`、`backbone_positions`、`plddt_logits`、`plddt_scores`、`pae_logits`、`ptm_score` 等张量。
- 当前 `PDB` 输出只包含 backbone 原子，不包含完整 side-chain 恢复。
