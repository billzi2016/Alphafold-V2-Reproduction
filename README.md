# AlphaFold V2 Reproduction

一个基于 PyTorch 的 AlphaFold 2 风格工程复现项目，目标是在真实推理链路下完成单个 monomer FASTA 的端到端结构预测，并输出与参考实现风格兼容的中间结果与结构文件。

## 已实现

当前仓库已包含：

- 单个 monomer FASTA 推理
- 真实 MSA 与 template 工具执行层
- PyTorch 模型主干、Evoformer、Structure Module 与 confidence heads
- 结果输出组织与可追踪运行记录
- 详尽中文注释

## 可生成输出

- `features.pkl`
- `result_model_1.pkl`
- `unrelaxed_model_1.pdb`
- `ranked_0.pdb`
- `ranking_debug.json`
- `timings.json`
- `run.log`
- `run_config.json`

说明：

- 当前 `PDB` 输出基于 backbone 坐标生成，只覆盖最小 backbone 原子集合。
- `msas/`、真实模板产物、完整权重映射和最终可对齐结果仍需外部数据库、工具和权重继续接入。

## 快速运行

```bash
bash scripts/run_monomer.sh
```

或直接调用 CLI：

```bash
PYTHONPATH=src python3 -m af2_repro.cli.predict \
  --fasta-path examples/fastas/target_example.fasta \
  --output-dir artifacts/outputs/manual_run \
  --config-path configs/inference/monomer.yaml
```

## 输出检查

检查关键文件是否生成：

```bash
python3 scripts/inspect_outputs.py artifacts/outputs/manual_run
```

输出目录摘要：

```bash
python3 scripts/summarize_outputs.py artifacts/outputs/manual_run
```

## 项目结构

详见 [PRD.md](./PRD.md) 与 [TASKS.md](./TASKS.md)。
