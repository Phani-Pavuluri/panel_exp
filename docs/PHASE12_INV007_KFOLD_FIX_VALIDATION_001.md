# Phase 12 INV-007 — KFold multi-treated geometry fix validation 001

**Investigation:** INV-007 corrective validation (post-fix)  
**Status:** evidence archive (production-tier characterization; not nominal calibration)  
**Last updated:** 2026-05-20  
**Package version:** 0.2.1  
**Config:** `TBRRidge_Kfold`  
**Branch:** `fix-kfold-multitreated-geometry`

**Related:** [`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md) · [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) · [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md)

**Raw JSON (local, not committed):** `.phase12_inv007_kfold_fix_validation.json`

This document archives **post-fix geometry validation and OC characterization** only. No estimand, threshold, eligibility registry, maturity label, recovery scoring, or release-gate changes were made.

---

## 1. Executive summary

**Headline:** The localized TBRRidge KFold multi-treated geometry bug is **fixed**. All post-fix OC cells (`n_treated` = 1, 2, 4, default recovery DGP) complete with **0% failure rate** at **n=100 × seeds 0–2** (production-tier characterization).

| Geometry | Pre-fix (INV-007) | Post-fix |
|----------|-------------------|----------|
| **n_treated = 1** | 0% failure | 0% failure (unchanged) |
| **n_treated = 2 or 4** | 100% `ValueError` broadcast | **0% failure** |
| **Default recovery DGP (~4 treated)** | 100% failure | **0% failure** |
| **Interval alignment** | 100% when runs complete | **100%** across all cells |
| **Bound ordering (when aligned)** | N/A for multi-treated | **100%** (`ci_lower ≤ ci_upper`) |
| **Nominal calibration readiness** | Not demonstrated | **Still not demonstrated** (positive-scenario coverage/power remain poor) |

**Classification:** **Runnable under multi-treated geometry** — not trusted for nominal calibration without further governance and OC evidence.

---

## 2. Bug fixed

**Failure:** `ValueError: operands could not be broadcast together with shapes (n_pre, n_treated) vs (n_pre,)`

**Location:** `panel_exp/inference/k_fold.py`, function `debias()`, pre-treatment bias computation:

```python
bias = (est.results['y'] - est.results['y_hat'])[treatment_mask].mean()
```

**Root cause:** TBRRidge exports per-unit treated outcomes `y` with shape `(n_pre, n_treated)` but a **pooled** counterfactual `y_hat` with shape `(n_pre,)`. Element-wise subtraction attempted invalid broadcasting.

**Fix:** Introduced `_aggregate_treatment_residuals()` and used it in `debias()` (and refactored the existing TimeSeries KFold diagnostics path to share the same helper). Pre-treatment bias is now computed on **period-level aggregate residuals** rather than raw per-unit subtraction.

---

## 3. Geometry semantics chosen

When `y` is 2D (per treated unit) and `y_hat` is 1D (pooled aggregate counterfactual — TBRRidge multi-treated geometry):

1. Sum treated `y` across units: `y_full = y.sum(axis=1)` → shape `(n_pre,)`
2. Flatten pooled counterfactual: `y_hat_full = y_hat.ravel()`
3. Residual series: `resid_full = y_full - y_hat_full`
4. Bias: mean of `resid_full` over pre-treatment fold periods

**Per-unit ATT paths** in `cross_fold` / `kfold` remain per treated unit (subtract pooled `y_hat` and scalar aggregate bias from each unit’s post-period outcomes). This matches the existing single-treated path and preserves downstream interval extraction via `_align_post_series` (nanmean pooling over units).

**Unsupported geometry:** If residual lengths cannot be reconciled after aggregation, callers should fail with an actionable error (existing reshape guard retained in the helper).

---

## 4. Regression test coverage

Added/updated in `tests/test_recovery_inference_calibration.py`:

| Test | Assertion |
|------|-----------|
| `test_tbrridge_kfold_null_on_single_treated_panel` | Single-treated null still passes; no failures |
| `test_tbrridge_kfold_multi_treated_null_no_broadcast_failure` (n=2, 4) | 0% failure; no `ValueError` in failure types |
| `test_tbrridge_kfold_default_recovery_geometry_no_failure` | Default recovery DGP (~4 treated) completes |
| `test_tbrridge_kfold_interval_bounds_ordered_when_aligned` | When `interval_aligned`, `ci_lower ≤ ci_upper`; estimand metadata present |

Full suite: **661 passed**, 2 skipped (`poetry run pytest tests/ -q`).

---

## 5. Post-fix OC matrix

**Harness:** `scripts/phase12_inv007_kfold_fix_validation.py` (investigation-only)  
**Tier:** `production_characterization` (n=100 feasible; ~236 s wall time)  
**Seeds:** 0, 1, 2  
**α:** 0.05  
**Panel:** default recovery geometry (`n_geos=20`, `n_periods=50`, `treatment_start=35`)

Aggregates: **mean across seeds** (300 replications per cell = 100 sims × 3 seeds).

### `recovery_null_effect`

| n_treated | failure_rate | interval_aligned | bound_order | coverage | FPR | recovery_success | significance | mean_width |
|-----------|--------------|------------------|-------------|----------|-----|------------------|--------------|------------|
| 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 0.000 | 0.020 |
| 2 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.036 |
| 4 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.028 |
| default (~4) | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.028 |

- **Failure types:** none in any cell  
- **Interval estimand:** `relative_att_post` (100% of successful runs)  
- **Interval scale:** `path_period_relative_mean`  
- **Point estimand:** `relative_att_post`

### `recovery_positive_effect`

| n_treated | failure_rate | interval_aligned | bound_order | coverage | power | recovery_success | significance | mean_width |
|-----------|--------------|------------------|-------------|----------|-------|------------------|--------------|------------|
| 1 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.020 |
| 2 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.038 |
| 4 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.029 |
| default (~4) | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.029 |

- **Failure types:** none  
- **Coverage / power:** intervals align but do not cover true effect or detect significance under default recovery thresholds — consistent with pre-fix single-treated characterization in INV-007

---

## 6. Remaining limitations

1. **Statistical performance unchanged by geometry fix:** Positive-scenario coverage = 0 and power = 0 across all treated counts; this PR does not address interval width, bias, or power.
2. **Multi-treated recovery success rate:** Null multi-treated cells show `recovery_success_rate = 0` despite 0% failures — point-estimate recovery scoring thresholds are tight relative to multi-treated ATT paths; not a geometry defect.
3. **Pooled-counterfactual semantics:** Aggregate-residual bias debiasing assumes TBRRidge’s pooled `y_hat` is the appropriate counterfactual reference for all treated units; per-unit heterogeneity is not modeled separately in KFold debias.
4. **No cross-estimator generalization claim:** Fix validated for `TBRRidge_Kfold` on default recovery DGPs only.
5. **Runnable ≠ trusted:** 0% failure rate is necessary but not sufficient for calibration re-entry.

---

## 7. Eligibility implications

| Field | Value |
|-------|--------|
| **`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`** | `{"SCM_UnitJackKnife"}` — **unchanged** |
| **Registry skip reason (persisted)** | `kfold_multi_treated_unsupported_run001` — **unchanged** |
| **`eligible_for_nominal_calibration`** | **false** for `TBRRidge_Kfold` |

**Explicit governance stance:**

- This PR **only** makes KFold **runnable** under multi-treated geometry.
- **Trust** for nominal calibration or maturity promotion still depends on OC evidence and a **later governance decision**.
- Eligibility remains excluded until governance review — not automatic upon geometry fix.

---

## 8. Non-claims

This archive **does not** claim or imply:

- KFold is calibration-ready or nominally calibrated
- KFold should be promoted in maturity labels or release gates
- Multi-treated KFold intervals are unbiased or well-calibrated
- `recovery_success_rate` deficits are resolved
- `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` should include `TBRRidge_Kfold`
- The geometry fix substitutes for Phase 12/13 governance restrictions on KFold

**Principle:** Fixing KFold makes it runnable. It does not make it trusted.
