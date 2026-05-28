# Calibration run 002 — BRB operating-characteristic recheck

**Run ID:** CALIBRATION_RUN_002  
**Investigation:** INV-008 — BRB operating characteristics after bound-ordering fix  
**Generated:** 2026-05-28  
**Harness:** `RecoveryRunner` (investigation-only path; bypasses registry skip for evidence generation)  
**Wall time:** ~57 s  
**Raw JSON (local, not committed):** `.calibration_run_002.json` at repo root  

This document archives **operating-characteristic evidence** only. No estimator, inference, recovery scoring, threshold, or eligibility registry changes were made for this run.

---

## 1. Run metadata

| Field | Value |
|-------|--------|
| **Package version** | 0.2.1 |
| **Branch** | `phase12-run002-brb-oc` |
| **Commit** | `657dcad0184c546c1a24b0694a1c90ff68d90aa8` |
| **Config** | `TBRRidge_BlockResidualBootstrap` |
| **Scenarios** | `recovery_null_effect`, `recovery_positive_effect` |
| **Seeds** | 0, 1, 2 |
| **n_simulations** | 100 per config × scenario × seed |
| **α (nominal)** | 0.05 |
| **Point estimand** | `relative_att_post` |
| **Interval estimand** | `relative_att_post` (aligned) |
| **Interval scale** | `path_period_relative_mean` |
| **DGP** | Standard recovery calibration scenarios; `missingness_policy=none` |
| **Production tier** | Yes (n ≥ 100) |

### Investigation-only eligibility note

| Field | Value |
|-------|--------|
| **`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`** | `{"SCM_UnitJackKnife"}` — **unchanged** |
| **Registry skip reason (persisted)** | `brb_bounds_inverted_run001` |
| **`eligible_for_nominal_calibration`** | **false** for this run (investigation-only) |
| **Rationale** | Phase 12 evidence generation per [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md); no registry change until Phase 13 governance decision |

---

## 2. Run 001 comparison

| Metric | Run 001 BRB (pre-fix) | Run 002 BRB (post-fix) | Change |
|--------|----------------------|------------------------|--------|
| **Null coverage** | 0.000 | **1.000** | Fixed anti-calibration |
| **Null FPR** | 1.000 | **0.000** | Fixed |
| **Positive coverage** | 0.000 | **0.000** | Unchanged (still fails) |
| **Positive power** | 1.000 (degenerate significance) | **0.000** | No longer always-significant |
| **Null failure rate** | 0.000 | 0.000 | Runs complete |
| **Run 001 root cause** | Inverted `y_lower`/`y_upper` → FPR = 1 | Bound-ordering guard + fix applied | Mechanism addressed |

Run 001 diagnosis ([`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) §2.2): inverted bootstrap bounds caused **FPR = 1.0** and **coverage = 0.0** on null despite accurate point estimates. Run 002 shows the **inversion mechanism is gone** on null; positive-scenario behavior **changed materially** (no longer degenerate power = 1.0 with inverted intervals).

---

## 3. Bound-ordering verification

Explicit checks across **600 replications** (100 sims × 3 seeds × 2 scenarios):

| Question | Result |
|----------|--------|
| Are level `y_lower ≤ y_upper` after fix? | **Yes** — 0 inverted post-period periods across 15,000 level period checks (5000 per seed on null; same on positive) |
| Are scalar `ci_lower ≤ ci_upper`? | **Yes** — 600 / 600 aligned replications ordered; 0 scalar inversions |
| Did inverted-bounds failure disappear? | **Yes** — 0 replications with `PATH_INTERVAL_BOUNDS_INVERTED` guard |
| Are invalid bounds rejected rather than silently used? | **Yes** — guard path in `recovery_intervals.py` would reject; no rejections needed because bounds are ordered |

**Conclusion:** The bound-ordering **correctness defect** from Run 001 is **resolved**. Remaining OC issues (positive under-coverage) are **not** explained by inverted bounds.

---

## 4. Results by scenario

Aggregates are **mean / std / min / max** across seeds 0, 1, 2.

### `recovery_null_effect`

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Coverage | 1.000 | 0.000 | 1.000 | 1.000 |
| False positive rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Power | — | — | — | — (not requested on null) |
| Recovery success rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Mean interval width | 0.043 | 0.000 | 0.043 | 0.043 |
| Significance rate | 0.000 | 0.000 | 0.000 | 0.000 |

- **Failure types:** none  
- **Seed variability:** zero std on coverage, FPR, failure rate (stable across seeds)  
- **Interval width behavior:** narrow relative intervals (~0.043 on null); always cover zero → FPR = 0  

### `recovery_positive_effect` (`true_effect = 0.10`)

| Metric | mean | std | min | max |
|--------|------|-----|-----|-----|
| Coverage | 0.000 | 0.000 | 0.000 | 0.000 |
| False positive rate | — | — | — | — (not requested on positive) |
| Power | 0.000 | 0.000 | 0.000 | 0.000 |
| Recovery success rate | 1.000 | 0.000 | 1.000 | 1.000 |
| Failure rate | 0.000 | 0.000 | 0.000 | 0.000 |
| Mean interval width | 0.043 | 0.000 | 0.043 | 0.043 |
| Width / effect ratio | ~0.43 | ~0.00 | ~0.43 | ~0.43 |
| Significance rate | 0.000 | 0.000 | 0.000 | 0.000 |

- **Failure types:** none  
- **Point estimates:** accurate (mean |bias| ≈ 0.008 vs truth 0.10)  
- **Interval width behavior:** width ≈ 0.043 with truth 0.10 — intervals **never contain** true effect (coverage 0) and **never reject** zero (power 0, significance 0)  

---

## 5. Threshold assessment

Frozen thresholds ([`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) Appendix A): **coverage ≥ 0.90**, **FPR ≤ 0.10**, **failure_rate < 0.05** on null; power target **0.80** informative on positive.

### Null scenario (`recovery_null_effect`)

| Metric | Value | Threshold | Overall |
|--------|-------|-----------|---------|
| Coverage | 1.000 | ≥ 0.90 | **pass** |
| FPR | 0.000 | ≤ 0.10 | **pass** |
| Failure rate | 0.000 | < 0.05 | **pass** |
| Seed stability | std = 0 | advisory | **pass** |

### Positive scenario (`recovery_positive_effect`)

| Metric | Value | Threshold | Overall |
|--------|-------|-----------|---------|
| Coverage | 0.000 | ≥ 0.90 (informative) | **fail** |
| Power | 0.000 | target 0.80 (informative) | **fail** |
| Failure rate | 0.000 | < 0.05 | **pass** |

**Overall config assessment:** Null thresholds **pass**; positive OC **fails**. Not sufficient for full nominal-calibration claims on default recovery DGP.

---

## 6. Interpretation

| Dimension | Classification |
|-----------|----------------|
| **Bound-ordering correctness** | **Fixed** — inversion mechanism from Run 001 eliminated |
| **Null scenario** | **Over-conservative** — perfect coverage and zero FPR; narrow intervals always contain zero (similar caution as SCM null monitor) |
| **Positive scenario** | **Under-covering** — zero coverage despite accurate points; intervals do not contain true effect; zero power |
| **Stability** | **Stable across seeds** — zero cross-seed std on headline metrics |
| **Functional status** | **Functional** — 0% run failures; intervals aligned |
| **Nominal calibration (full)** | **Inconclusive / insufficient** — null pass alone does not support lift-detection claims |

**Not** a return of Run 001 anti-calibration (FPR = 1). **Not** evidence of production-ready interval calibration on positive scenarios.

---

## 7. Recommendation

**Keep excluded** from `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` until Phase 13 governance review.

| Rationale | Detail |
|-----------|--------|
| Skip reason | Retain `brb_bounds_inverted_run001` until governance explicitly updates skip reason after Phase 12/13 evidence chain |
| Null monitoring | Null FPR/coverage pass at n = 100 — **candidate for conditional null-only review** in Phase 13, not automatic re-eligibility |
| Positive OC | Systematic under-coverage (coverage 0, power 0) blocks full relative-ATT calibration claims |
| Next step | Optional `PHASE12_INV008_BRB_OC_001.md` deep-dive; failure analysis not required for bound inversion (mechanism fixed) but **positive under-coverage** should be documented in Phase 13 decision |

**Not recommended now:** re-add to eligibility registry; `production_safe`; maturity promotion.

---

## 8. Non-claims

This run **does not**:

- Re-add `TBRRidge_BlockResidualBootstrap` to `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`
- Certify BRB or TBRRidge as nominally calibrated for lift detection
- Promote TBRRidge maturity labels
- Imply `production_safe` or unattended decisioning status
- Change thresholds, estimator code, inference code, or recovery scoring

This run **does**:

- Archive post-fix OC evidence at production scale (n = 100, seeds 0–2)
- Confirm bound-ordering correctness restoration
- Document null vs positive operating-characteristic split for Phase 13

---

## Appendix — investigation execution notes

**Command class:** Local `RecoveryRunner` loop with explicit `investigation_only=True` metadata (registry skip bypassed for evidence only).

**Comparison harness note:** `run_production_nominal_calibration()` would skip this config at `nominal_calibration_registry_skip_reason` without running — intentional for persisted eligibility behavior.

**Related docs:** [`PHASE12_INVESTIGATION_PLAN.md`](PHASE12_INVESTIGATION_PLAN.md) · [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) · [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md)

---

*Evidence archive INV-008 / Run 002. Registry unchanged. Update OPEN_INVESTIGATIONS after Phase 13 decision.*
