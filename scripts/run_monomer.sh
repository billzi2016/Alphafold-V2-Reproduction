#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

FASTA_PATH="${1:-$ROOT_DIR/examples/fastas/target_example.fasta}"
OUTPUT_DIR="${2:-$ROOT_DIR/artifacts/outputs/manual_run}"
CONFIG_PATH="${3:-$ROOT_DIR/configs/inference/monomer.yaml}"

export PYTHONPATH="$ROOT_DIR/src"

python3 -m af2_repro.cli.predict \
  --fasta-path "$FASTA_PATH" \
  --output-dir "$OUTPUT_DIR" \
  --config-path "$CONFIG_PATH"
