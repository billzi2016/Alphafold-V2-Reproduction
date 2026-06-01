# AlphaFold V2 Reproduction Tasks

## 1. 项目规划与基线

- [x] 通读并确认 `PRD.md` 的目标、范围、交付标准与技术路线
- [x] 明确项目第一阶段目标为单个 `monomer` FASTA 端到端推理
- [x] 明确项目主要验证标准为“可运行 + 输出完整 + 结果尽量与参考实现 match”
- [x] 明确项目核心框架为 `PyTorch`
- [x] 明确项目开发原则为“优先使用现代通用库与成熟工具，保留完整工程结构”
- [x] 明确核心源码必须包含详尽中文注释

## 2. 仓库初始化

- [x] 创建 `README.md`
- [x] 创建 `.gitignore`
- [x] 创建 `pyproject.toml`
- [x] 创建 `requirements/` 目录
- [x] 创建 `configs/` 目录
- [x] 创建 `scripts/` 目录
- [x] 创建 `docker/` 目录
- [x] 创建 `src/af2_repro/` 目录
- [x] 创建 `tests/` 目录
- [x] 创建 `examples/fastas/` 目录
- [x] 创建 `docs/` 目录
- [x] 创建 `artifacts/reports/` 目录

## 3. 依赖与环境设计

- [x] 整理基础 Python 依赖列表
- [x] 整理开发依赖列表
- [x] 整理 Docker 依赖列表
- [x] 明确 `PyTorch` 版本策略
- [ ] 明确 `CUDA` 版本策略
- [x] 明确 `numpy`、`scipy`、`einops`、`biopython` 等基础库版本
- [ ] 明确 `OpenMM` 的接入方式
- [x] 明确 `HH-suite`、`HMMER`、`Kalign` 等外部工具依赖
- [x] 编写环境检查脚本
- [ ] 编写依赖安装说明
- [ ] 编写本地运行环境说明
- [ ] 编写 Docker 环境说明

## 4. 配置系统

- [x] 设计统一的路径配置文件
- [x] 设计推理参数配置文件
- [x] 设计数据库配置文件
- [x] 支持 `monomer` 配置模板
- [x] 支持 `monomer_ptm` 配置模板
- [x] 预留 `multimer` 配置模板
- [x] 支持模型参数路径配置
- [x] 支持输出目录路径配置
- [x] 支持 `max_template_date` 配置
- [x] 支持 `db_preset` 配置
- [x] 支持 `model_preset` 配置
- [x] 支持 `num_recycle` 配置
- [x] 支持随机种子与运行日志配置

## 5. 项目结构与模块骨架

- [x] 创建 `src/af2_repro/cli/`
- [x] 创建 `src/af2_repro/data/`
- [x] 创建 `src/af2_repro/model/`
- [x] 创建 `src/af2_repro/common/`
- [x] 创建 `src/af2_repro/relax/`
- [x] 创建 `src/af2_repro/io/`
- [x] 创建 `src/af2_repro/utils/`
- [x] 创建基础 `__init__.py`
- [x] 创建统一日志模块
- [x] 创建路径管理模块
- [x] 创建运行时工具模块
- [x] 为各模块补充中文说明性注释

## 6. CLI 与运行入口

- [x] 创建主 CLI 入口 `predict.py`
- [x] 支持命令行传入 FASTA 路径
- [x] 支持命令行传入输出目录
- [x] 支持命令行传入配置文件路径
- [x] 支持命令行覆盖关键推理参数
- [x] 支持运行前路径合法性校验
- [x] 支持输出目录自动初始化
- [x] 支持记录完整运行参数
- [x] 支持生成本次运行的基础日志
- [x] 为 CLI 参数解析写详尽中文注释

## 7. 输入处理

- [x] 实现 FASTA 文件解析模块
- [x] 支持单条蛋白质序列读取
- [x] 校验 FASTA header 与序列合法性
- [x] 校验氨基酸字符集
- [x] 生成基础 sequence features
- [x] 实现输入样例文件
- [x] 为输入处理模块补充详尽中文注释

## 8. MSA 检索流水线

- [x] 设计 MSA 检索模块接口
- [x] 接入 `jackhmmer`
- [x] 接入 `hhblits`
- [x] 支持 `db_preset` 选择
- [x] 支持数据库路径检查
- [x] 支持中间检索文件持久化
- [x] 支持生成 `.sto` / `.a3m` 等中间文件
- [x] 支持 `msas/` 输出目录组织
- [ ] 支持 MSA 复用开关
- [x] 支持检索失败时的错误提示
- [x] 为 MSA 流水线补充详尽中文注释

## 9. Template 检索流水线

- [x] 设计 template 检索模块接口
- [x] 接入 `hhsearch` 或等价模板检索工具
- [x] 支持模板数据库路径检查
- [x] 支持 `max_template_date` 过滤
- [ ] 支持 template hit 解析
- [ ] 支持 template 特征生成
- [x] 支持模板中间结果持久化
- [x] 为 template 流水线补充详尽中文注释

## 10. 特征构建

- [x] 设计统一特征构建入口
- [x] 实现 sequence features 构建
- [ ] 实现 MSA features 构建
- [ ] 实现 template features 构建
- [x] 实现 residue index 与 mask 构建
- [ ] 实现 padding 逻辑
- [ ] 实现 shape 对齐逻辑
- [ ] 实现 residue constants 与基础原子映射
- [x] 实现 `features.pkl` 或等价中间结果导出
- [x] 为特征张量 shape、字段含义、构建顺序补充详尽中文注释

## 11. 公共蛋白结构工具

- [ ] 实现 `protein.py`
- [x] 实现 `residue_constants.py`
- [ ] 实现基础坐标与原子映射工具
- [ ] 实现结构对象与张量对象互转工具
- [ ] 实现置信度相关公共函数
- [ ] 为公共结构工具补充详尽中文注释

## 12. PyTorch 模型总体设计

- [x] 设计 `model/config.py`
- [x] 设计 `model/model.py`
- [x] 设计输入 embedding 模块
- [x] 设计 Evoformer 模块边界
- [x] 设计 Structure Module 模块边界
- [x] 设计 confidence heads 模块边界
- [ ] 设计 recycling 模块边界
- [x] 明确模型前向输入输出结构
- [x] 明确各模块张量 shape 约定
- [x] 为模型主干结构补充详尽中文注释

## 13. Evoformer 实现

- [x] 实现输入嵌入层
- [x] 实现 MSA row attention
- [x] 实现 MSA column attention
- [x] 实现 MSA transition
- [x] 实现 outer product mean 或等价 pair 更新
- [x] 实现 triangle multiplicative update
- [x] 实现 triangle attention
- [x] 实现 pair transition
- [x] 实现 Evoformer block 堆叠
- [x] 校验 Evoformer 输入输出 shape
- [x] 为 Evoformer 数据流、模块职责与 shape 变化补充详尽中文注释

## 14. Structure Module 实现

- [x] 实现 single representation 抽取
- [x] 实现 Invariant Point Attention
- [x] 实现残基框架更新逻辑
- [x] 实现 backbone 坐标生成
- [ ] 实现 side-chain 相关输出逻辑
- [x] 校验结构模块输入输出 shape
- [x] 为 Structure Module 的几何更新逻辑补充详尽中文注释

## 15. Recycling 与置信度头

- [x] 实现 recycling 输入组织
- [x] 实现 recycling 特征回灌
- [x] 支持可配置 recycle 次数
- [x] 实现 pLDDT head
- [x] 实现 pTM head
- [x] 实现 PAE 相关输出
- [x] 为 recycling 与 confidence heads 补充详尽中文注释

## 16. 参数加载与权重映射

- [x] 设计参数加载模块
- [x] 明确外部参数文件路径接口
- [x] 设计权重文件检查逻辑
- [ ] 实现参数读取与缓存
- [ ] 实现权重映射策略
- [ ] 校验关键层权重 shape
- [x] 记录参数来源与版本信息
- [ ] 为参数加载与映射流程补充详尽中文注释

## 17. 推理调度与 Runner

- [x] 设计统一 inference runner
- [ ] 串联 FASTA、MSA、template、features、model、outputs 全流程
- [x] 支持 CPU/GPU 设备选择
- [x] 支持推理阶段日志输出
- [x] 支持各阶段耗时统计
- [ ] 支持异常中断时保留已完成中间结果
- [x] 为 runner 的执行顺序和调度逻辑补充详尽中文注释

## 18. 输出组织

- [x] 输出 `features.pkl` 或等价特征文件
- [x] 输出 `result_model_*.pkl` 或等价中间结果
- [x] 输出 `unrelaxed_model_*.pdb`
- [ ] 输出 `relaxed_model_*.pdb`
- [x] 输出 `ranked_*.pdb`
- [x] 输出 `ranking_debug.json`
- [x] 输出 `timings.json`
- [ ] 输出 `msas/` 检索结果目录
- [x] 设计与参考实现兼容的输出命名规则
- [ ] 为每类输出文件的字段与用途补充详尽中文注释

## 19. Relaxation

- [ ] 设计 relaxation 模块接口
- [ ] 接入 `OpenMM`
- [ ] 支持 Amber relaxation 开关
- [ ] 支持 relaxed 与 unrelaxed 输出并存
- [ ] 支持 relaxation 失败时保留未放松结果
- [ ] 为 relaxation 流程补充详尽中文注释

## 20. 脚本与自动化

- [x] 编写环境检查脚本
- [ ] 编写参数下载脚本接口
- [ ] 编写数据库下载脚本接口
- [x] 编写单样例运行脚本
- [x] 编写输出检查脚本
- [x] 编写结果目录摘要脚本
- [x] 为脚本添加中文注释与使用说明

## 21. Docker 支持

- [ ] 编写 `Dockerfile`
- [ ] 固定核心系统依赖
- [ ] 固定 Python 依赖安装流程
- [ ] 固定外部生信工具安装流程
- [ ] 支持挂载数据库目录
- [ ] 支持挂载输出目录
- [ ] 支持容器内单样例推理
- [ ] 编写 Docker 运行说明

## 22. 文档编写

- [x] 编写 `README.md`
- [x] 编写项目简介
- [x] 编写技术路线说明
- [x] 编写项目结构说明
- [x] 编写依赖安装说明
- [x] 编写数据库与参数准备说明
- [x] 编写单样例运行说明
- [x] 编写输出结果说明
- [x] 编写核心模块说明
- [x] 编写 `docs/architecture.md`
- [x] 编写 `docs/data.md`
- [x] 编写 `docs/outputs.md`
- [x] 编写 `docs/references.md`
- [ ] 在文档中说明与参考实现的对齐思路

## 23. 代码注释与可读性

- [ ] 为核心模块统一补充详尽中文注释
- [ ] 为复杂张量 shape 变化补充中文注释
- [ ] 为外部工具调用链路补充中文注释
- [ ] 为关键配置项补充中文注释
- [ ] 为每个核心函数补充中文 docstring
- [ ] 为每个关键类补充中文说明
- [ ] 确保注释解释“为什么这样做”和“输入输出是什么”

## 24. 测试与验证

- [x] 建立 `unit` 测试目录
- [x] 建立 `integration` 测试目录
- [x] 建立 `smoke` 测试目录
- [x] 编写 FASTA 解析测试
- [x] 编写配置加载测试
- [x] 编写特征构建 shape 测试
- [x] 编写模型前向 shape 测试
- [x] 编写输出文件生成测试
- [x] 编写单样例 smoke test
- [x] 编写结果目录完整性检查
- [x] 编写关键模块错误处理测试

## 25. 单样例运行目标

- [x] 准备一个公开蛋白质样例 FASTA
- [ ] 跑通单个 `monomer` FASTA 的端到端预测
- [ ] 生成真实 `msas/` 检索结果
- [x] 生成 `features.pkl` 或等价特征文件
- [x] 生成 `result_model_*.pkl` 或等价中间结果
- [x] 生成 `ranked_0.pdb`
- [x] 生成 `ranking_debug.json`
- [x] 生成 `timings.json`
- [x] 记录一次完整运行日志
- [x] 整理该样例的复现记录

## 26. 结果对齐与分析

- [ ] 选择参考实现作为结果对齐基线
- [ ] 明确对齐指标与对齐方式
- [ ] 检查输出文件结构是否一致
- [ ] 检查关键中间结果是否可解释
- [ ] 检查最终结构结果是否尽量 match
- [ ] 记录可能的偏差来源
- [ ] 整理结果对齐说明文档

## 27. 最终验收

- [ ] 仓库结构完整
- [ ] `PRD.md` 完整
- [ ] `TASKS.md` 完整
- [ ] 项目可安装
- [ ] CLI 可执行
- [ ] 单样例 `monomer` 推理可运行
- [ ] 输出结果完整
- [ ] 结果与参考实现尽量 match
- [ ] 核心源码具备详尽中文注释
- [ ] 文档能够解释项目结构、运行方式与主要输出
