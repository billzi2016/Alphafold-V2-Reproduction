#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "用法: bash scripts/download_params.sh <DOWNLOAD_DIR>"
  exit 1
fi

DOWNLOAD_DIR="$1"
PARAMS_DIR="$DOWNLOAD_DIR/params"
PARAMS_URL="https://storage.googleapis.com/alphafold/alphafold_params_2022-12-06.tar"
ARCHIVE_PATH="$DOWNLOAD_DIR/alphafold_params_2022-12-06.tar"

mkdir -p "$PARAMS_DIR"

cat <<EOF
将执行以下步骤：
1. 下载官方参数压缩包到:
   $ARCHIVE_PATH
2. 解压到:
   $PARAMS_DIR

参考来源:
- DeepMind AlphaFold 官方 README
- 参数地址: $PARAMS_URL

建议手动执行:
  curl -L "$PARAMS_URL" -o "$ARCHIVE_PATH"
  tar -xf "$ARCHIVE_PATH" -C "$PARAMS_DIR"
EOF
