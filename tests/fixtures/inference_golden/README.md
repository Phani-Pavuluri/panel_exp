# Inference golden fixtures

Committed numeric baselines for `tests/test_inference_registry_equivalence.py`.

Golden fixtures are generated in the Linux devcontainer. Optimizer-heavy placebo/SCM paths may not be bitwise portable across platforms.

Regenerate after intentional inference changes:

```bash
MPLCONFIGDIR=/tmp/mpl poetry run python scripts/regenerate_inference_golden.py
```

Regenerate a single mode:

```bash
MPLCONFIGDIR=/tmp/mpl poetry run python scripts/regenerate_inference_golden.py --mode Placebo
```

Fixtures use `TBRRidge` (integer `TimePeriod` columns) except `Placebo` (`SyntheticControl` with 6 controls).
`BlockResidualBootstrap` uses `random_state=42` and `n_bootstrap=25`.
