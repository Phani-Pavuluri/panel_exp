# Examples index

## Current package contract (use these)

| Script | Purpose |
|--------|---------|
| `decision_workflow_example.py` | Full advisory chain: recovery → calibration → maturity → readiness → experiment card |
| `readiness_profile_comparison.py` | Same mocked evidence under exploratory / standard / strict profiles |

Run from repo root:

```bash
poetry run python examples/decision_workflow_example.py
poetry run python examples/readiness_profile_comparison.py
```

## Legacy notebooks (not current contract)

> ⚠ **Legacy example — not current package contract.**

These notebooks are retained for history. They may import **unshipped** or **removed** modules.

| Path | Known stale references |
|------|------------------------|
| `dev_notebooks/pretest_analysis_example.ipynb` | `panel_exp.pretest_analysis` (not shipped) |
| `dev_notebooks/*.ipynb` | May use `panel_exp.util`, old power return patterns |
| `test_design_notebooks/fy24q1_test_designs.ipynb` | `panel_exp.pretest_analysis.mde_ci_module` |
| `test_notebooks/*.ipynb` | Method / inference experiments; verify imports against `panel_exp.__init__` |

**Replacements:** `PowerAnalysis` + `GeoExperimentDesign` for design/power; `docs/VALIDATION_COVERAGE.md` for estimator validation status.

## Data

`examples/data/` — CSV fixtures for notebooks only.
