# AlphaFold V2 Reproduction PRD

## 1. 项目目标

本项目用于构建一个基于 PyTorch 的 AlphaFold 2 风格复现工程，围绕真实推理链路完成从蛋白质氨基酸序列到 3D 结构结果的端到端实现。系统将覆盖 MSA 检索、模板检索、特征构建、Evoformer、Structure Module、recycling 与可选的 Amber relaxation，并输出可检查的结构文件与置信度指标。

本 PRD 以 AlphaFold 2 为主体，补充少量 AlphaFold 1 对比，用于体现对两代架构演进和工程实现差异的理解。

## 2. 实现原则

本项目采用以下实现原则：

- 使用真实 FASTA 输入、真实数据库检索、真实模型参数推理与真实输出文件完成整条流水线。
- 使用 PyTorch 作为核心深度学习框架，结合现代通用库完成模型搭建、张量计算和结果持久化。
- 使用成熟的生信检索工具完成 MSA 与 template 搜索，保证输入特征来源真实可追踪。
- 在本仓库内保留清晰的模块分层与数据流结构，使模型、特征工程与推理流程具备独立可读性和可维护性。
- 在核心实现中提供详尽中文注释，重点解释特征构建、张量形状变化、Evoformer 数据流、Structure Module 更新逻辑、recycling 机制与结果导出流程。
- 对所有关键外部依赖、参数来源、数据库版本和运行边界进行明确记录，确保结果可复查、可复现、可对齐。

## 3. 项目范围

### 3.1 第一阶段范围

第一阶段目标是完成 AlphaFold 2 monomer 推理复现，范围包括：

- FASTA 输入解析
- MSA 检索流程接入
- template 检索与过滤
- AlphaFold 2 特征构建
- 模型参数加载
- Evoformer 主干实现或对齐
- Structure Module 推理
- recycling 推理
- pLDDT / pTM / PAE 等结果解析
- unrelaxed / relaxed / ranked 输出组织

### 3.2 第二阶段范围

第二阶段可扩展：

- multimer 模式
- 预计算 MSA 复用
- 批量推理调度
- Docker / Singularity / 本地 Python 三种运行入口
- 更系统的 benchmark 与结果对齐

### 3.3 阶段定位

第一阶段聚焦于单个 monomer FASTA 的端到端推理复现，以可运行、可验证、结果可对齐为核心交付目标。项目将优先完成 inference pipeline、输出组织和文档说明，并在此基础上为后续 multimer、批量推理和更系统的 benchmark 预留扩展接口。

## 4. AlphaFold 1 与 AlphaFold 2 的关键差异

该部分只保留最能体现架构理解的对比，不展开成历史综述。

### 4.1 AlphaFold 1

- 核心思路是先预测残基间距离 / 接触 / 几何约束，再做结构优化或采样。
- 网络输出更偏“势能面”或约束信息，后处理优化的权重更重。
- 工程上更接近“深度学习约束预测 + 独立结构搜索/优化”。

### 4.2 AlphaFold 2

- 改为端到端结构生成。
- 主干网络直接联合建模 MSA 表示与 pair 表示。
- Evoformer 在 MSA 和 pair 之间反复交换信息。
- Structure Module 直接在 3D 空间中迭代更新残基框架。
- recycling 将上一轮预测重新送回网络，形成迭代 refinement。

### 4.3 对本项目的意义

因此，本项目将完整打通以下 AlphaFold 2 关键链路：

- 原始序列到 MSA/template 检索
- 特征到 Evoformer
- pair/single 表示到 3D 结构模块
- recycling 与 confidence heads
- 最终结构与评估输出

## 5. 外部调研结论

基于官方论文与 DeepMind 官方仓库，项目采用以下事实依据：

- DeepMind 官方开源仓库提供的是 AlphaFold v2 inference pipeline。
- 官方推荐运行方式是 Linux + Docker + NVIDIA GPU。
- 官方完整数据库下载量约 556 GB，解压后约 2.62 TB。
- `reduced_dbs` 方案仍需要约 600 GB 磁盘空间。
- 官方参数文件约 5.3 GB。
- 官方结果目录包含 `features.pkl`、`result_model_*.pkl`、`ranked_*.pdb`、`relaxed_model_*.pdb`、`timings.json`、`msas/` 等真实产物。

据此，项目的资源组织策略如下：

- 仓库内保留代码、脚本、配置、示例输入和文档。
- 大型数据库与模型权重通过仓库外部路径或环境变量挂载。
- 第一阶段优先围绕最小必要数据集和单样例推理完成工程闭环。

## 6. 交付目标定义

### 6.1 最小真实可交付版本

最小可交付版本应满足：

- 输入一个真实单链 FASTA
- 调用真实 MSA 工具与真实数据库
- 调用真实 template 搜索
- 使用真实公开参数完成模型推理
- 输出真实 PDB 与置信度文件
- 输出目录结构与参考实现风格一致或高度兼容

### 6.2 验收标准

- 能对单个 monomer FASTA 完成端到端预测
- 输出 `ranked_0.pdb`
- 输出 `ranking_debug.json`
- 输出 `timings.json`
- 输出 `msas/` 检索结果
- 输出 `result_model_*.pkl` 或等价中间结果持久化
- 文档中能解释每个主要输出文件的含义
- 至少对一个公开蛋白样例完成复现记录

### 6.3 结果可信度要求

项目交付结果需满足以下要求：

- 推理流程包含真实 MSA 与 template 检索步骤。
- 本地代码能够完整组织 FASTA、特征、模型前向与结果导出链路。
- 输出文件内容与文件名保持一致，所有结构与中间结果均来自真实运行。
- 文档中明确参数文件来源、数据库版本和模板日期约束。
- 所有样例结果具备可复查的配置、运行参数和输出说明。

## 7. 技术方案

### 7.1 总体流水线

目标流水线如下：

1. 输入 FASTA
2. 执行序列检索，生成 MSA
3. 执行模板检索，筛选合法 template
4. 构建 AlphaFold 2 所需输入特征
5. 加载模型配置与参数
6. 运行 Evoformer + Structure Module
7. 执行 recycling
8. 计算 pLDDT / pTM / PAE 等输出
9. 执行可选 relaxation
10. 生成 ranked 结构和调试产物

### 7.2 主要模块

#### A. 输入与配置层

- FASTA 解析
- 运行参数解析
- `max_template_date`
- `db_preset`
- `model_preset`
- 输出目录管理

#### B. 数据检索层

- `jackhmmer` / `hhblits` / `hhsearch` / `hmmsearch` 等外部工具封装
- 数据库路径配置
- 中间 `.sto` / `.a3m` / template hit 文件持久化
- 可选 MSA 复用

#### C. 特征工程层

- sequence features
- MSA features
- template features
- mask 与 padding
- residue 常量与原子映射

#### D. 模型层

- PyTorch 2.x 作为核心实现框架
- 输入嵌入
- Evoformer block
- pair update
- MSA row/column attention
- triangle multiplicative update
- triangle attention
- single representation 抽取
- Structure Module
- Invariant Point Attention
- side-chain / confidence heads
- recycling

#### E. 输出层

- unrelaxed PDB
- relaxed PDB
- ranked PDB
- result pickle
- ranking JSON
- timings JSON

### 7.3 运行形态

项目采用现代化、模块化的运行形态，优先通过通用工具栈完成工程实现：

- 本地 Python 入口：便于调试代码与逐模块验证
- Docker 入口：便于固定依赖环境与跨机器复现
- Shell 包装脚本：便于一键运行和参数透传

核心实现策略如下：

- 使用 `PyTorch`、`numpy`、`scipy`、`einops`、`biopython` 等通用库承载张量计算、科学计算与蛋白质文件处理。
- 使用 `HH-suite`、`HMMER`、`Kalign`、`OpenMM` 等成熟工具承载检索、比对与 relaxation 环节。
- 在本仓库内实现清晰的 `data / model / inference / io / relax` 模块结构，使整体工程可独立阅读、调试和扩展。

优先级建议：

1. 先完成本地 Python 入口
2. 再补 Docker
3. 最后补批处理与部署包装

## 8. 数据、权重与存储策略

### 8.1 必需外部资源

按照官方公开实现，主要外部资源包括：

- UniRef90
- MGnify
- BFD 或 `small_bfd`
- UniRef30 / UniClust30
- PDB mmCIF
- PDB70
- 参数文件 `alphafold_params_2022-12-06.tar`

若后续扩展到 multimer，还需要：

- UniProt
- PDB seqres

### 8.2 下载策略

本项目的数据准备按以下顺序推进：

- 先定义下载脚本接口、目标路径、资源来源与用途。
- 优先准备单样例推理所需的最小必要资源集合。
- 在本机资源允许的前提下逐步扩展数据库覆盖范围。

### 8.3 仓库内外边界

仓库内只保留：

- 源码
- 配置
- 小型示例 FASTA
- 文档
- 轻量测试工件

仓库外保留：

- 所有大型数据库
- 模型参数
- 推理输出
- 临时搜索缓存

推荐目录边界：

```text
repo_root=/Users/bizi/Desktop/GitHub/Alphafold-V2-Reproduction
external_data_root=/data/alphafold
external_output_root=/data/alphafold_outputs
```

如果本机没有 `/data` 盘位，则用显式环境变量代替，不把大文件放进仓库。

## 9. 建议仓库结构

当前仓库是空目录，因此以下是建议落地结构，而不是现状扫描结果。

```text
Alphafold-V2-Reproduction/
├── PRD.md
├── README.md
├── .gitignore
├── pyproject.toml
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── docker.txt
├── configs/
│   ├── paths.example.yaml
│   ├── inference/
│   │   ├── monomer.yaml
│   │   ├── monomer_ptm.yaml
│   │   └── multimer.yaml
│   └── data/
│       ├── reduced_dbs.yaml
│       └── full_dbs.yaml
├── scripts/
│   ├── check_env.sh
│   ├── download_params.sh
│   ├── download_reduced_dbs.sh
│   ├── run_monomer.sh
│   └── inspect_outputs.py
├── docker/
│   ├── Dockerfile
│   └── run_docker.py
├── src/
│   └── af2_repro/
│       ├── __init__.py
│       ├── cli/
│       │   └── predict.py
│       ├── data/
│       │   ├── fasta.py
│       │   ├── msa_pipeline.py
│       │   ├── template_pipeline.py
│       │   ├── feature_pipeline.py
│       │   └── parsers.py
│       ├── model/
│       │   ├── config.py
│       │   ├── embeddings.py
│       │   ├── evoformer.py
│       │   ├── triangle.py
│       │   ├── ipa.py
│       │   ├── structure_module.py
│       │   ├── heads.py
│       │   ├── recycling.py
│       │   └── model.py
│       ├── common/
│       │   ├── residue_constants.py
│       │   ├── protein.py
│       │   └── confidence.py
│       ├── relax/
│       │   └── amber_relaxation.py
│       ├── io/
│       │   ├── pdb.py
│       │   ├── pickle_io.py
│       │   └── json_io.py
│       └── utils/
│           ├── paths.py
│           ├── runtime.py
│           └── logging.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── smoke/
├── examples/
│   └── fastas/
│       └── target_example.fasta
├── docs/
│   ├── architecture.md
│   ├── data.md
│   ├── outputs.md
│   └── references.md
└── artifacts/
    └── reports/
```

## 10. 分阶段实施计划

### 阶段 0：仓库初始化

- 建立基础目录
- 建立依赖管理
- 建立 README、`.gitignore`、配置模板
- 约定仓库外数据路径

交付标准：

- 项目可安装
- CLI 入口可运行到参数校验阶段

### 阶段 1：数据检索链路

- 接入 FASTA 解析
- 接入 MSA 工具
- 接入 template 搜索
- 固化中间文件格式

交付标准：

- 给定 FASTA 能生成真实 `msas/` 与 template hit 文件

### 阶段 2：特征构建

- 对齐 AlphaFold 2 输入特征
- 完成 shape、mask、padding 与序列映射

交付标准：

- 能导出与模型前向兼容的 `features.pkl` 或等价特征文件

### 阶段 3：模型推理

- 参数加载
- Evoformer
- Structure Module
- recycling
- confidence heads

交付标准：

- 能输出 `result_model_*.pkl` 与 `unrelaxed_model_*.pdb`

### 阶段 4：结果整理与 relaxation

- ranked 结构排序
- 可选 Amber relaxation
- timings 与 debug 信息落盘

交付标准：

- 输出目录结构接近官方结果布局

### 阶段 5：验证与文档

- 跑通公开样例
- 整理运行文档
- 写清限制、版本、数据来源与参数来源

交付标准：

- 外部读者可以按文档独立复现一次完整预测

## 11. 风险与对应策略

### 11.1 数据体积风险

风险：

- 官方数据库体积极大，远超普通仓库存储能力。

策略：

- 代码与数据强分离。
- 第一阶段只支持外部挂载路径。
- 优先支持 `reduced_dbs`。

### 11.2 训练级复现风险

风险：

- 论文与开源仓库公开重点集中在 inference pipeline，训练级复现需要额外的大规模数据准备与算力支持。

策略：

- 第一阶段聚焦真实 inference reproduction。
- 后续如扩展训练路线，可单独规划训练数据、算力和实验设计。

### 11.3 环境复杂性风险

风险：

- PyTorch、CUDA、容器与外部生信工具之间的版本组合需要精确管理。

策略：

- 优先固定 Docker 环境。
- 本地 Python 环境仅作为调试入口，不作为唯一标准交付。

### 11.4 结果波动风险

风险：

- 官方文档明确指出，少量 target 对输入数据库变化和随机性敏感。

策略：

- 固定数据库版本、模板日期、模型 preset、recycle 次数。
- 记录完整运行参数和时间戳。

## 12. 验收产物清单

第一阶段完成后，仓库至少应具备：

- `README.md`
- `PRD.md`
- 可安装依赖定义
- 可执行的 monomer 推理入口
- 带详尽中文注释的核心源码实现
- 真实数据库路径配置模板
- 真实输出目录说明
- 一份公开样例运行说明

对应真实运行结果至少应具备：

- `ranked_0.pdb`
- `ranking_debug.json`
- `timings.json`
- `features.pkl`
- `msas/`
- `result_model_*.pkl`

## 13. 成功标准

若本项目达到以下状态，可视为“AlphaFold 2 工程复现的合格第一版”：

- 具备完整、可运行的端到端推理链路
- 支持本地或容器化执行
- 具备 Evoformer + Structure Module + recycling 的核心结构
- 核心代码包含足够细致的中文注释，便于阅读、讲解与后续维护
- 保留最终结构文件与关键中间调试产物
- 明确依赖公开参数与可追踪的数据资源

## 14. 参考资料

- DeepMind AlphaFold 官方开源仓库：<https://github.com/google-deepmind/alphafold>
- AlphaFold 2 论文：Jumper et al., Nature 2021, <https://www.nature.com/articles/s41586-021-03819-2>
- AlphaFold 1 论文：Senior et al., Nature 2020, <https://www.nature.com/articles/s41586-019-1923-7>

## 15. 当前结论

从调研结果看，AlphaFold 2 适合按“PyTorch 工程复现 + 真实 inference pipeline + 单样例先跑通”的方式推进：

- 先完成 monomer 端到端推理
- 以输出结果与参考实现尽量 match 为主要验证标准
- 通过清晰的模块分层保留完整工程结构
- 逐步扩展 multimer、批量推理与更完整的数据配置

这条路线兼顾可运行性、工程质量和后续扩展空间，能够形成结构完整、结果可信、便于展示的项目成果。
