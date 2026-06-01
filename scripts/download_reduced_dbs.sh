#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "用法: bash scripts/download_reduced_dbs.sh <DOWNLOAD_DIR>"
  exit 1
fi

DOWNLOAD_DIR="$1"

cat <<EOF
AlphaFold 官方 reduced_dbs 需要通过官方脚本统一下载和整理。

建议目录:
  $DOWNLOAD_DIR

官方建议命令:
  scripts/download_all_data.sh "$DOWNLOAD_DIR" reduced_dbs

reduced_dbs 主要包含:
- uniref90
- mgnify
- small_bfd
- pdb70
- pdb_mmcif
- params

说明:
- 该脚本当前只输出下载说明，不直接触发大文件下载。
- 官方 README 说明 reduced_dbs 仍需要大约 600 GB 磁盘空间。
EOF
