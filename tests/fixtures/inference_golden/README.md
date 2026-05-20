# Inference golden fixtures

Committed numeric baselines for `tests/test_inference_registry_equivalence.py`.

Regenerate after intentional inference changes:

```bash
MPLCONFIGDIR=/tmp/mpl .venv/bin/python scripts/regenerate_inference_golden.py
```

Fixtures use `TBRRidge` (integer `TimePeriod` columns) except `Placebo` (`SyntheticControl` with 6 controls).
`BlockResidualBootstrap` uses `random_state=42` and `n_bootstrap=25`.
