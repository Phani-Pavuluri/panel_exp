# Test fixtures

Synthetic helpers for power tests live in `tests/power_helpers.py` (no committed
`examples/data/meta_geo.csv` required). Optional CSV: `power_geo.csv`.

Golden inference baselines: `inference_golden/README.md`.
Power/MDE numeric goldens are not committed; regenerate in the Linux devcontainer.
Optimizer-heavy placebo/SCM paths may not be bitwise portable across platforms.
