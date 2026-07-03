# AlphaFold V2 Reproduction

A PyTorch-based reproduction project in the style of AlphaFold 2. The goal is to run end-to-end structure prediction for a single monomer FASTA through a realistic inference pipeline and generate intermediate artifacts and structure files that are compatible in spirit with the reference implementation.

## Implemented

The repository currently includes:

- Single monomer FASTA inference
- Real MSA and template tool execution layers
- The PyTorch model backbone, Evoformer, Structure Module, and confidence heads
- Output organization and traceable run records
- Detailed Chinese code comments

## Generated Outputs

- `features.pkl`
- `result_model_1.pkl`
- `unrelaxed_model_1.pdb`
- `ranked_0.pdb`
- `ranking_debug.json`
- `timings.json`
- `run.log`
- `run_config.json`

Notes:

- The current `PDB` output is generated from backbone coordinates and only covers the minimal backbone atom set.
- `msas/`, real template artifacts, full weight mapping, and the final fully aligned outputs still require additional external databases, tools, and weights to be connected.

## Quick Start

```bash
bash scripts/run_monomer.sh
```

Or invoke the CLI directly:

```bash
PYTHONPATH=src python3 -m af2_repro.cli.predict \
  --fasta-path examples/fastas/target_example.fasta \
  --output-dir artifacts/outputs/manual_run \
  --config-path configs/inference/monomer.yaml
```

## Output Inspection

Check whether the key files were generated:

```bash
python3 scripts/inspect_outputs.py artifacts/outputs/manual_run
```

Summarize the output directory:

```bash
python3 scripts/summarize_outputs.py artifacts/outputs/manual_run
```

## Project Structure

See [PRD.md](./PRD.md) and [TASKS.md](./TASKS.md) for details.
