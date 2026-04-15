"""
Run post-hoc estimator diagnostics independently (without re-running the full grid).

Usage:
    # Use BASE_OUTPUT_DIR from run_mmt_estimator_inference_grid.py
    python run_estimator_diagnostics.py

    # Override with a custom output directory
    python run_estimator_diagnostics.py --dir /path/to/output_dir
"""
import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "run_mmt_estimator_inference_grid",
    SCRIPTS_DIR / "run_mmt_estimator_inference_grid.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

BASE_OUTPUT_DIR = _mod.BASE_OUTPUT_DIR
_run_post_hoc_diagnostics = _mod._run_post_hoc_diagnostics

parser = argparse.ArgumentParser()
parser.add_argument(
    "--dir",
    default=BASE_OUTPUT_DIR,
    help=f"Output directory to run diagnostics on (default: {BASE_OUTPUT_DIR})",
)
args = parser.parse_args()

print(f"Running diagnostics on: {args.dir}")
_run_post_hoc_diagnostics(args.dir)
