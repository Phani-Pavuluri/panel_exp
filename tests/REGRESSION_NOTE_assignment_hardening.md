# Regression note: assignment constraint hardening

**Targeted suite** (`test_assignment_*`, `test_design_validation_gate`, `test_audit_fixes`, `test_design_registry*`): **90 passed**, 4 skipped.

**Full** `pytest tests/ --ignore=tests/util_test.py`: **174 passed**, **26 failed**, 9 skipped.

**Ruff**: not run — `ruff` is not installed in `.venv` (`python -m ruff` → `No module named ruff`).

## Constraint-contract fix (resolved)

`tests/greedymatch_test.py` previously used an incompatible fixture (`control_whitelist="2"` with `test_blacklist="2"`, and `test_whitelist="1"` with `control_blacklist="1"`). Under the stricter contract, whitelisted units must be assignable to their declared arm. The test now uses non-conflicting lists (`control_whitelist="3"`, `test_whitelist="5"`) and asserts dict assignment output.

## Pre-existing / out-of-scope full-suite failures (26)

| Test file | # | First error class | Notes |
|-----------|---|-------------------|--------|
| `tests/trop_test.py` | 9 | `RuntimeError` | TROP `stability_first` — no feasible grid configuration |
| `tests/synthetic_did_test.py` | 9 | `ValueError` / `AssertionError` | `treated_periods` length vs `treated_units` in `panel_data.py` |
| `tests/test_scm.py` | 5 | `ModuleNotFoundError` | missing `osqp` (cvxpy SCM path) |
| `tests/test_counterfactual_stability.py` | 2 | `ModuleNotFoundError` | missing `osqp` |
| `tests/notebook_test.py` | 1 | `FileNotFoundError` | `pytest` executable not on PATH in notebook runner |

**Collection error** (excluded from 26): `tests/util_test.py` — `ModuleNotFoundError: panel_exp.util`.

## Scope confirmation

Assignment-hardening commits do **not** modify TROP, SDID, SCM/cvxpy, notebooks, inference registry, `ImpactAnalyzer`, or power/MDE logic.
