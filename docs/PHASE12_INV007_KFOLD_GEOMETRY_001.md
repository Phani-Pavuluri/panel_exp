# Phase 12 INV-007 — KFold geometry characterization 001

**Investigation:** INV-007 — KFold geometry characterization  
**Status:** evidence archive (characterization tier; not nominal calibration)  
**Last updated:** 2026-05-28  
**Package version:** 0.2.1  
**Config:** `TBRRidge_Kfold`  

**Related:** [`PHASE12_INVESTIGATION_PLAN.md`](PHASE12_INVESTIGATION_PLAN.md) · [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) · [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) · [`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) · [`CALIBRATION_RUN_002.md`](CALIBRATION_RUN_002.md)

**Raw JSON (local, not committed):** `.phase12_inv007_kfold_geometry.json`

This document archives **geometry / failure-surface evidence** only. No estimator, inference, recovery scoring, threshold, or eligibility registry changes were made.

---

## 1. Executive summary

**Headline:** TBRRidge Kfold is **single-treated viable** (runs complete, intervals align) and **multi-treated unsupported** (100% `ValueError` with shape `(n_pre, n_treated)` vs `(n_pre,)`).

| Geometry | Verdict |
|----------|---------|
| **n_treated = 1** | **Viable for execution** — 0% failure; `interval_estimand=relative_att_post`; intervals aligned on all replications |
| **n_treated = 2 or 4** | **Systematically fails** — 100% failure rate; broadcast error scales with treated count |
| **Default recovery DGP (~4 treated)** | **Unsupported** — consistent with Run 001 `kfold_multi_treated_unsupported_run001` |
| **Nominal calibration readiness** | **Not demonstrated** — even single-treated positive scenario shows coverage 0 / power 0 at characterization n |

**Classification:** **Multi-treated unsupported** with **single-treated-only partial viability** — not broadly unreliable on all panels, but **not calibration-ready** without further OC and scenario contract work.

**Not inconclusive:** treated-count threshold behavior is sharp (0% vs 100% failure).

---

## 2. Run metadata

| Field | Value |
|-------|--------|
| **Package version** | 0.2.1 |
| **Branch** | `phase12-run002-brb-oc` |
| **Commit** | `8782870` (Run 002 archive) / investigation executed at current branch tip |
| **Config** | `TBRRidge_Kfold` (`TBRRidge(inference="Kfold", alpha=0.05)`) |
| **Scenario bases** | `recovery_null_effect`, `recovery_positive_effect` |
| **Treated counts** | 1, 2, 4 (explicit `treated_units`) |
| **Panel geometry** | `n_geos=20`, `n_periods=50`, `treatment_start=35`, `missingness_policy=none` (matches default recovery except explicit treated units) |
| **Seeds** | 0, 1, 2 |
| **n_simulations** | **30** per cell × seed (characterization tier — **not** n≥100 production calibration) |
| **α** | 0.05 |
| **Harness** | Investigation-only `RecoveryRunner` / `_run_simulation` loop |
| **Wall time** | ~25 s (full 3×2×3 matrix) |
| **Characterization tier** | `characterization_not_nominal_calibration` |

### Investigation-only eligibility note

| Field | Value |
|-------|--------|
| **`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`** | `{"SCM_UnitJackKnife"}` — **unchanged** |
| **Registry skip reason (persisted)** | `kfold_multi_treated_unsupported_run001` |
| **`eligible_for_nominal_calibration`** | **false** for all cells |

---

## 3. Geometry matrix results

Aggregates: **mean / std / min / max** across seeds 0–2 (90 replications per cell = 30 sims × 3 seeds).

### n_treated = 1

#### `recovery_null_effect`

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Interval aligned rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Coverage | 1.000 | 0.000 | 1.000 | 1.000 |
| FPR | 0.000 | 0.000 | 0.000 | 0.000 |
| Recovery success rate | 1.000 | — | — | — |
| Mean interval width | 0.019 | 0.000 | 0.019 | 0.020 |
| Significance rate | 0.000 | 0.000 | 0.000 | 0.000 |

- **Failure types:** none  
- **Interval estimand:** `relative_att_post` (aligned)  
- **Metric availability:** coverage, FPR computed  

#### `recovery_positive_effect` (`true_effect = 0.10`)

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Interval aligned rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Coverage | 0.000 | 0.000 | 0.000 | 0.000 |
| Power | 0.000 | 0.000 | 0.000 | 0.000 |
| Recovery success rate | 1.000 | — | — | — |
| Mean interval width | 0.019 | 0.000 | 0.019 | 0.020 |
| Width / effect | ~0.19 | — | — | — |
| Significance rate | 0.000 | 0.000 | 0.000 | 0.000 |

- **Failure types:** none  
- **Interval behavior:** intervals align but **do not cover** true effect; zero power (parallel to Run 002 BRB positive pattern on default DGP)  

---

### n_treated = 2

#### Both `recovery_null_effect` and `recovery_positive_effect`

| Metric | Value |
|--------|-------|
| Failure rate | **1.000** (all seeds) |
| Interval aligned rate | **0.000** |
| Coverage / FPR / Power | **unavailable** (`interval_estimand=unavailable`) |
| Failure types | **`ValueError`: 90** (30 per seed × 3 seeds) |
| Representative message | `operands could not be broadcast together with shapes (35,2) (35,)` |

---

### n_treated = 4 (Run 001 default geometry)

#### Both `recovery_null_effect` and `recovery_positive_effect`

| Metric | Value |
|--------|-------|
| Failure rate | **1.000** (all seeds) |
| Interval aligned rate | **0.000** |
| Coverage / FPR / Power | **unavailable** |
| Failure types | **`ValueError`: 90** |
| Representative message | `operands could not be broadcast together with shapes (35,4) (35,)` |

**Run 001 consistency:** Message matches Run 001 diagnosis (`35,4` vs `35,` on default ~4-treated recovery panel).

---

### Summary table

| n_treated | Null: fail rate | Null: aligned | Positive: fail rate | Positive: aligned | Top failure |
|-----------|-----------------|---------------|---------------------|---------------------|-------------|
| **1** | 0% | 100% | 0% | 100% | — |
| **2** | 100% | 0% | 100% | 0% | broadcast `(35,2)` vs `(35,)` |
| **4** | 100% | 0% | 100% | 0% | broadcast `(35,4)` vs `(35,)` |

---

## 4. Root-cause interpretation

### Primary mechanism: multi-treated series shape vs aggregate counterfactual

When TBRRidge returns **per-treated** path outputs `y` with shape `(n_pre, n_treated)` but **aggregate** `y_hat` with shape `(n_pre,)`, legacy Kfold paths subtract without compatible broadcasting.

Evidence:

| Observation | Implication |
|-------------|-------------|
| Error shape `(35, n_treated)` vs `(35,)` | **Treated-count scaling** — not random instability |
| n_treated = 1 succeeds | Single column aligns with aggregate subtraction paths |
| n_treated ≥ 2 always fails | **Systematic**, not fold-size edge case |
| pre_t = 35 unchanged across cells | **Not** insufficient pre-period length |

Likely code locus (read-only inspection): `panel_exp/inference/k_fold.py` legacy `cross_fold` bias line subtracts `est.results['y'] - est.results['y_hat']` under treatment mask when `y` is 2D and `y_hat` is 1D — see also residual handling notes in newer fold blocks (~lines 521–540) that partially address shape but **do not** cover all TBRRidge multi-treated call paths.

### Ruled out (for this matrix)

| Cause | Rationale |
|-------|-----------|
| **Fold construction infeasible** | Same k=5 fold geometry works at n_treated=1 |
| **Recovery extraction / alignment** | Failures occur as `ValueError` during `run_analysis`, before interval extraction |
| **Scenario noise / effect** | Null and positive fail identically at n_treated≥2 |
| **Unknown intermittent bug** | 100% failure rate, deterministic message |

### Path aggregation

Not reached on failed cells. Single-treated cells complete extraction with `relative_att_post` alignment.

---

## 5. Eligibility recommendation

**Keep excluded** from `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` on default multi-treated `recovery_*` scenarios.

| Action | Rationale |
|--------|-----------|
| **Keep excluded (default DGP)** | n_treated≈4 remains 100% failure — skip reason `kfold_multi_treated_unsupported_run001` remains valid |
| **Single-treated-only future investigation** | n_treated=1 executes and aligns — any future contract must **explicitly** restrict scenario geometry and document positive OC limits |
| **Fix implementation before multi-treated calibration** | Broadcasting / shape contract must be resolved in inference layer before multi-geo nominal claims |
| **Do not re-enter eligibility from this archive alone** | Characterization n=30; positive single-treated under-coverage; no n≥100 production run |

**Phase 13 input:** Kfold may be recorded as **single-treated-only expert-review path (research)** vs **retired from relative-ATT nominal on default recovery** — not automatic re-eligibility.

---

## 6. Required future evidence (if reconsidered)

Re-entry to nominal calibration or expanded expert-review support requires the full advancement policy chain ([`ROADMAP_V4.md`](ROADMAP_V4.md) § Promotion policy):

| Step | KFold-specific requirement |
|------|----------------------------|
| 1. Estimand | Document single-treated vs multi-treated contract if geometry fix attempted |
| 2. Recovery | Finite metrics on declared scenario battery |
| 3. Calibration | **n ≥ 100** production archive on **each** geometry class claimed (single-treated-only at minimum) |
| 4. Failure analysis | Mechanism doc if multi-treated fix PR — or permanent single-treated skip reason |
| 5. OC characterization | Width, power, geometry matrix extension; compare to Run 002 BRB positive under-coverage |
| 6. Governance decision | Phase 13 memo — registry PR cites archives only |

**For multi-treated support specifically:** prove 0% `ValueError` on default `recovery_*` at n≥100 **and** acceptable null FPR/coverage **and** documented positive OC — not merely “runs complete.”

---

## 7. Non-claims

This investigation **does not**:

- Re-add `TBRRidge_Kfold` to `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`
- Certify Kfold or TBRRidge as nominally calibrated
- Promote TBRRidge maturity labels
- Imply `production_safe` or unattended decisioning status
- Change thresholds, estimator code, inference code, or recovery scoring
- Replace Run 001 failure analysis — it **confirms and sharpens** it with treated-count sweep

This investigation **does**:

- Establish a treated-count failure surface (1 = pass, ≥2 = fail on standard recovery geometry)
- Support continued exclusion on default multi-treated calibration scenarios
- Inform optional single-treated-only scenario catalog work (INV-003 / Phase 13)

---

## Appendix — Run 001 cross-reference

| Run 001 | INV-007 matrix |
|---------|----------------|
| ~4 treated, 100% `ValueError` | n_treated=4: 100% `(35,4)` vs `(35,)` |
| Kfold smoke single-treated only in CI | n_treated=1: 0% failure, aligned intervals |
| Skip reason `kfold_multi_treated_unsupported_run001` | **Still appropriate** for default DGP |

---

*Evidence archive INV-007-001. Registry unchanged. Next Phase 12 track: INV-003 aggregation semantics.*
