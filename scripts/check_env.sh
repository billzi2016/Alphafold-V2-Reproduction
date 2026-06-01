#!/usr/bin/env bash

set -euo pipefail

echo "[1/3] 检查 Python"
python3 --version

echo "[2/3] 检查 PyTorch"
python3 - <<'PY'
try:
    import torch
    print(f"torch={torch.__version__}")
    print(f"cuda_available={torch.cuda.is_available()}")
except Exception as exc:
    print(f"torch_check_failed={exc}")
PY

echo "[3/3] 检查外部工具"
for tool in jackhmmer hhblits hhsearch kalign; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "$tool=FOUND"
  else
    echo "$tool=MISSING"
  fi
done
