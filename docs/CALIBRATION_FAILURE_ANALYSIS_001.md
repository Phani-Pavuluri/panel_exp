# Calibration failure analysis 001

**Date:** 2026-05-20  
**Inputs:** `docs/CALIBRATION_RUN_001.md`, `.calibration_run_001.json` (local), targeted read-only replication diagnostics (n=50, seeds 0–49)  
**Package version:** 0.2.1  
**Constraint:** No estimator, inference, threshold, or recovery-scoring changes in this analysis.

This document diagnoses **why** Run 001 configs passed or failed. It is the first roadmap gate that may **remove** work (drop configs from relative-ATT nominal calibration) rather than add it.

---

## 1. Failure summary

| Config | Scenario | Run 001 headline | Primary diagnosis | Issue category |
|--------|----------|------------------|-------------------|----------------|
| **SCM_UnitJackKnife** | null | coverage 1.0, FPR 0.0 | Intervals wide enough to always cover 0; conservative jackknife | inference (conservative) + scenario (multi-treated pooling) |
| **SCM_UnitJackKnife** | positive | power 0.0, coverage 1.0 | Same: intervals never exclude 0 despite accurate point estimates | inference (conservative) |
| **TBRRidge_BlockResidualBootstrap** | null | coverage 0.0, FPR 1.0 | Level bootstrap bounds inverted (`y_lower > y_upper`); relative CI mis-ordered; significance always true | inference |
| **TBRRidge_BlockResidualBootstrap** | positive | power 1.0, coverage 0.0 | Degenerate significance (always reject); truth outside inverted interval | inference |
| **TBRRidge_Kfold** | both | failure_rate 1.0, ineligible | `ValueError` broadcast `(35,4)` vs `(35,)` — multi-treated path | geometry + inference |

**Not failures of:** recovery scoring (point recovery success ≈ 1.0 for SCM and BRB), DGP missingness (`missingness_policy=none`), or production harness aggregation.

---

## 2. Root cause by config

### 2.1 SCM_UnitJackKnife

#### Observed behavior (Run 001 + diagnostics)

- Null (n=100×3 seeds): coverage **1.0**, FPR **0.0**, failure_rate **0.0**.
- Positive: power **0.0**, coverage **1.0**, recovery_success_rate **1.0**.
- Single-rep diagnostic (`recovery_positive_effect`, seed 0): point ≈ **0.102** (truth 0.10), CI ≈ **[-0.68, 0.88]**, width ≈ **1.56**, `significant=False`.
- n=50 aggregate: mean point ≈ **0.100**, mean width ≈ **1.53**, significance rate **0%**, coverage **100%**.

#### Likely mechanism

**Intervals are too wide (conservative), not point estimates too weak.**

Unit jackknife path intervals are pooled over **4 treated units** on the default recovery DGP (`n_geos=20` → `n_treated ≈ n_geos//5`). Jackknife leave-one-donor variation produces wide post-period relative bounds. Significance uses `significance_from_ci`: reject only if `ci_lower > 0` or `ci_upper < 0`. With truth = 0.10 and intervals spanning zero on every replication, **power is mechanically zero** while **coverage stays at 1.0**.

Null “perfect” calibration is consistent with **over-coverage** (intervals always contain 0 and the true null), not necessarily correct nominal 90% two-sided behavior at α=0.05.

#### Evidence

| Source | Finding |
|--------|---------|
| Run 001 JSON | `interval_estimand=relative_att_post`, `interval_aligned=true`, zero failures |
| Diagnostic script | Positive mean point ≈ true effect; width ~1.5 >> |effect| |
| `recovery_intervals.py` | Significance from CI exclusion of zero |
| `synthetic_world.py` | Default `treated_units` sample size = `max(1, min(n_geos-1, n_geos//5))` → 4 treated on recovery panels |

#### Confidence level

**High** for “power = 0 due to wide CIs, not biased point estimates.”  
**Medium** for “null coverage = 1.0 is over-conservative rather than exactly nominal 95%.”

#### Recommended next action

| Priority | Action |
|----------|--------|
| **Later** | Characterize jackknife width vs donor count / treated count on recovery DGP (documentation + targeted tests). |
| **Later** | Consider single-treated calibration scenario for power benchmarking (does not change estimator math). |
| **Do not fix** | Do not tune `true_effect`, thresholds, or jackknife math in a calibration-doc PR. |

---

### 2.2 TBRRidge_BlockResidualBootstrap

#### Observed behavior

- Null: coverage **0.0**, FPR **1.0** (all 100 reps significant).
- Positive: power **1.0**, coverage **0.0**.
- Single-rep null: point ≈ **0.011**, reported CI **lo=0.036, hi=-0.009** (inverted), `significant=True`.
- n=50: mean width ≈ **-0.04** (negative because lo > hi), significance rate **100%**, coverage **0%**.

#### Likely mechanism

**Block residual bootstrap exports path-level bounds with `y_lower > y_upper` on every post period** for multi-treated TBRRidge output shape `(n_times, n_treated)`.

`extract_recovery_interval` converts level bounds to relative ATT via `(y - y_upper)/y_hat` and `(y - y_lower)/y_hat`, which **does not repair** inverted level ordering. Aggregated scalar `ci_lower` can exceed `ci_upper`. Significance (`lo > 0 or hi < 0`) fires whenever `ci_lower > 0`, yielding **FPR = 1** on null even when the point estimate is near zero.

This is an **inference / interval construction + recovery extraction interaction**, not a failure of the ridge point fit.

#### Evidence

| Source | Finding |
|--------|---------|
| Raw `est.results` (seed 0, null) | `y_lower`, `y_upper` shape `(50, 4)`; **100%** of post periods have `y_lower > y_upper` at outcome level |
| Run 001 | `interval_aligned=true` (extraction succeeds but bounds are wrong-ordered) |
| Diagnostic aggregates | Negative mean “width”; sig rate 1.0 on null and positive |

#### Confidence level

**High** for “FPR=1 and coverage=0 driven by inverted bootstrap bounds and CI-based significance.”

#### Recommended next action

| Priority | Action |
|----------|--------|
| **Immediate (process)** | **Remove** `TBRRidge_BlockResidualBootstrap` from `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` until bounds are validated. |
| **Later (code)** | Fix bootstrap path bound ordering or reject/mark unaligned when `y_lower > y_upper` at level (inference layer — out of scope here). |
| **Do not fix** | Do not rescale intervals or relax FPR thresholds to pass Run 001. |

---

### 2.3 TBRRidge_Kfold

#### Observed behavior

- All seeds/scenarios: `failure_rate=1.0`, `failure_types: {"ValueError": 100}`.
- `interval_estimand=unavailable`, `ineligible_reason=interval_not_aligned`.
- Failure message (representative): `operands could not be broadcast together with shapes (35,4) (35,)`.

#### Likely mechanism

**Multi-treated panel geometry incompatible with the k-fold inference path on default recovery scenarios**, not insufficient pre-period length.

Default recovery panel: **pre_t = 35**, **post = 15**, **4 treated units** — fold holdout is feasible (`holdout = 7` for k=5). The run fails inside inference with a **shape broadcast error** between `(n_pre, n_treated)` and `(n_pre,)`, consistent with code paths that assume a single treated series.

CI tests only assert k-fold on a **custom single-treated** scenario (`tests/test_recovery_inference_calibration.py::test_tbrridge_kfold_null_on_single_treated_panel`), not on `recovery_null_effect` / `recovery_positive_effect`.

#### Evidence

| Source | Finding |
|--------|---------|
| Run 001 JSON | 100× `ValueError` per seed |
| Panel geometry check | `n_treated=4`, pre_t=35 — rules out “k > pre_t” / “holdout ≤ 0” |
| Test suite | Kfold smoke uses `treated_units=("geo_0",)` only |

#### Confidence level

**High** for “100% failure = multi-treated broadcast bug / unsupported geometry.”  
**Medium** on exact line in `k_fold.py` (not required for roadmap decision).

#### Recommended next action

| Priority | Action |
|----------|--------|
| **Immediate (process)** | **Remove** `TBRRidge_Kfold` from default relative-ATT nominal calibration eligibility on `recovery_*` scenarios. |
| **Later** | Either fix multi-treated k-fold broadcasting or document **single-treated-only** eligibility + alternate scenario. |
| **Do not fix** | Do not force alignment or weaken `interval_not_aligned` gating. |

---

## 3. Categorize issue (summary)

| Config | Primary category | Secondary |
|--------|------------------|-----------|
| SCM_UnitJackKnife (null pass) | inference (conservative SE) | scenario (multi-treated pooling) |
| SCM_UnitJackKnife (power fail) | inference | — |
| TBRRidge_BlockResidualBootstrap | inference | recovery (extraction does not guard inverted bounds) |
| TBRRidge_Kfold | geometry | inference (multi-treated path) |

---

## 4. Recommended actions

| Action | Classification |
|--------|----------------|
| Drop BRB and Kfold from `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` (registry/docs PR) | **Immediate** |
| Archive SCM null results with “over-coverage / zero power” caveat in expert-review guidance | **Immediate** |
| Add eligibility guard: fail alignment when `ci_lower > ci_upper` | **Later** |
| Fix BRB bootstrap bound ordering for multi-treated outputs | **Later** |
| Fix or scope Kfold to single-treated panels | **Later** |
| Add single-treated `recovery_*` variant for power characterization only | **Later** |
| Tune `true_effect` or thresholds to pass calibration | **Do not fix** |
| Change jackknife / bootstrap estimator math without inference PR | **Do not fix** |

---

## 5. Updated recommendation

### Should TBRRidge_BlockResidualBootstrap remain calibration eligible?

**No.** Remove from relative-ATT nominal calibration until bootstrap path bounds are ordered and validated on multi-treated recovery panels. Point-estimate recovery for `TBRRidge` may continue.

### Should TBRRidge_Kfold remain calibration eligible?

**No** on default `recovery_null_effect` / `recovery_positive_effect`. Re-eligibility only after multi-treated support is proven or scenario restricted to single-treated (as in existing CI test).

### Should SCM_UnitJackKnife remain eligible?

**Yes, with explicit limits.** Null metrics pass but are consistent with **very wide** intervals; positive-scenario **power is not usable** for lift detection at DGP `true_effect=0.10`. Keep for null FPR/coverage monitoring; do not cite as full operating-characteristic proof.

### Is production calibration feasible without estimator/inference changes?

**Not for the current 3-config bundle.**

| Path | Feasible without code change? |
|------|-------------------------------|
| SCM unit jackknife null monitoring on default recovery DGP | **Partially** — yes for “no excess FPR” read; no for power |
| Package claim “aligned configs are nominally calibrated” | **No** |
| TBRRidge inference configs on default recovery DGP | **No** — require inference fixes or removal from eligibility |

### Next implementation PR (recommended)

**PR: Tighten nominal calibration eligibility + alignment guards (docs/registry only or minimal gating).**

1. Set `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = {"SCM_UnitJackKnife"}` (or equivalent doc-driven registry change).  
2. Add `CALIBRATION_FAILURE_ANALYSIS_001.md` cross-reference in `VALIDATION_COVERAGE.md`.  
3. Optional follow-up inference PR: BRB bound ordering; Kfold multi-treated support.

---

*Diagnosis only. Run 001 raw JSON remains local and uncommitted.*
