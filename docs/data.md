# Data

当前数据边界如下：

- 仓库内保存代码、配置、示例 FASTA、文档和轻量测试工件
- 仓库外保存大型数据库、模型权重与大规模检索结果

当前配置文件：

- `configs/paths.example.yaml`
- `configs/inference/monomer.yaml`
- `configs/data/reduced_dbs.yaml`
- `configs/data/full_dbs.yaml`

外部数据库和参数路径通过配置挂载，不直接存入仓库。

当前已经接入的工具层：

- `jackhmmer`
- `hhblits`
- `hhsearch`
- `kalign` 与 `OpenMM` 仍待进一步接入完整流程
