# F-INF-003 — Interval orientation fix

**Document ID:** F-INF-003  
**Type:** Implementation fix (Track F backlog)  
**Status:** **complete**  
**Date:** 2026-06-03  
**Depends on:** F-INF-001 ✅ · F-BACKLOG-001 ✅

**Prior:** [`F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md`](F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md)

---

## Goal

Fix interval **orientation** at the source for **Conformal** and **TimeSeriesKfold** readouts (AUDIT-010 **A05**, **A19**) so post-treatment paths have `y_lower <= y_upper` and non-negative half-width, without weakening F-INF-001 classification or silently normalizing invalid bands in the classifier.

---

## Root cause

Effect-scale bounds from conformal and time-series k-fold were mapped to outcome space with **`-effect + y`**, which inverts order when `effect_lo < effect_hi` on the treatment-effect scale.

**Correct mapping** (aligned with `apply_bounds_to_results` for Kfold/BRB/Placebo):

- Counterfactual point: `y_hat = y - effect_point`
- Outcome intervals: `y_lower = y_hat + effect_lo`, `y_upper = y_hat + effect_hi`

---

## Code changes

| Path | Change |
|------|--------|
| [`panel_exp/inference/modes/impl.py`](../panel_exp/inference/modes/impl.py) | `run_conformal` → `apply_effect_bounds_to_results`; `run_timeseries_kfold` → `apply_bounds_to_results` |
| [`panel_exp/inference/_impact_common.py`](../panel_exp/inference/_impact_common.py) | New `apply_effect_bounds_to_results` helper |
| [`tests/governance/test_f_inf_003_interval_orientation.py`](../tests/governance/test_f_inf_003_interval_orientation.py) | Structural validity + F-INF-001 preservation |
| Golden fixtures | `Conformal.npz`, `TimeSeriesKfold.npz` regenerated |

**Not changed:** F-INF-001 classifier logic, F-GEO-001, F-CAT-001, TrustReport, Track B, MMM, CalibrationSignal.

---

## Outcome per tuple (post-fix, pre-OC)

| Tuple | Structural validity | Governed uncertainty | Next step |
|-------|---------------------|----------------------|-----------|
| **A05** AugSynthCVXPY + Conformal | **`structurally_valid_interval_ready_for_OC`** | **No** | Targeted OC rerun |
| **A19** TBRRidge + TimeSeriesKfold | **`structurally_valid_interval_ready_for_OC`** | **No** | Targeted OC rerun |

Null interval-exclusion FPR and behavioral semantics remain subject to **D5-INF-POSTFIX-001** (or F-INF-003-OC) — unit tests do **not** substitute for OC.

F-INF-001 may still classify combos as `callable_unverified_interval_semantics` when null FPR ≥ threshold even with valid band orientation.

---

## Stop condition (met)

| Criterion | Status |
|-----------|--------|
| Conformal / TimeSeriesKfold produce non-negative HW on registry/TBRRidge fixture | ✅ |
| F-INF-001 still blocks manually inverted readouts | ✅ |
| No governed uncertainty claim | ✅ |
| A05/A19 ready for targeted OC (not promotion) | ✅ |

**Next:** **D5-INF-POSTFIX-001** / **F-INF-003-OC** — targeted rerun for A05 + A19.

---

*F-INF-003 v1.0.0 — effect-scale bounds mapped via y_hat + effect; not governed export.*
