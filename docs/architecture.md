# Architecture

当前工程结构按以下数据流组织：

1. `FASTA -> FeaturePipeline`
2. `InputEmbedding -> EvoformerStack`
3. `StructureModule -> backbone_positions`
4. `ConfidenceHeads -> pLDDT / pTM / PAE`
5. `InferenceRunner -> result_model_1.pkl / ranked_0.pdb / ranking_debug.json`

核心模块：

- `src/af2_repro/data/`：输入解析、MSA/template 流水线接口与命令执行层
- `src/af2_repro/model/`：embedding、Evoformer、IPA、Structure Module、confidence heads、recycling
- `src/af2_repro/inference/runner.py`：把特征构建、模型前向、recycle 和结果输出串起来
- `src/af2_repro/io/`：PDB、JSON、pickle 输出

当前边界：

- 已有真实 PyTorch 前向链路和结果文件输出
- 已有真实外部工具命令执行层
- 仍待补完整权重映射、side-chain、relaxation、真实数据库驱动的 MSA/template 结果
