# D5-STAT-DID-BOOTSTRAP-001 — Level B characterization (DID + embedded bootstrap)

> **Harness correction:** `D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION` supersedes canonical
> rebuild geometry and coverage interpretation. Historical archive:
> [`archives/D5_STAT_DID_BOOTSTRAP_001_results_historical_pre_harness_correction.json`](archives/D5_STAT_DID_BOOTSTRAP_001_results_historical_pre_harness_correction.json).
> Correction report: [`D5_STAT_DID_BOOTSTRAP_001_HARNESS_CORRECTION_REPORT.md`](D5_STAT_DID_BOOTSTRAP_001_HARNESS_CORRECTION_REPORT.md).
> **Does not supersede production bootstrap behavior.**

**Artifact ID:** D5-STAT-DID-BOOTSTRAP-001
**Type:** Level B characterization — **not** promotion, **not** governed uncertainty validation
**Overall verdict:** `characterization_mixed_requires_followup`
**Harness correction verdict:** `did_bootstrap_harness_corrected_production_miscoverage_confirmed`

**Archive:** [`archives/D5_STAT_DID_BOOTSTRAP_001_results.json`](archives/D5_STAT_DID_BOOTSTRAP_001_results.json)
**Harness:** `panel_exp/validation/track_d_d5_stat_did_bootstrap_001.py`
**Regenerate:** `poetry run python -m panel_exp.validation.track_d_d5_stat_did_bootstrap_001 --output docs/track_d/archives/D5_STAT_DID_BOOTSTRAP_001_results.json --overwrite`

## 1. Purpose

Characterize **DID** with **estimator-native embedded moving-block bootstrap** on **single-cell unit-panel** geometry (`multiple_treated="pooled"`). Evaluates callable stability, finite point/interval outputs, interval orientation, null interval behavior, injected cumulative lift recovery, bootstrap center diagnostics, and pretrend/shock sensitivity.

## 2. Relationship to D5-STAT-SMOKE-CALLABLE-001

Smoke established `DID-BOOTSTRAP` as **callable_pass** on `single_cell_unit_level`. This artifact runs a Level B battery — smoke pass does not authorize suitability, TrustReport roles, or CalibrationSignal/MMM.

## 3. Relationship to prior Level B artifacts

Parallel to SCM-JK, AugSynth point, and TBR aggregate characterizations. Prior artifacts are **context only**; injected cumulative level truth is defined on the unit panel after percent injection.

## 4. Relationship to suitability framework

`DID-BOOTSTRAP` remains `suitability_candidate_pending_oc`. This characterization updates evidence only — no suitability tier movement.

## 5. Scope and exclusions

**In scope:** DID estimator, embedded bootstrap inference, single-cell unit panel, common simultaneous timing, seven worlds × 15 replicates.

**Out of scope:** SCM, AugSynth, TBR/TBRRidge, multi-cell pooling, production roles, TrustReport/F-DECISION, CalibrationSignal, MMM, LLM, primary/secondary evidence labels, production bootstrap recentering.

## 6. Panel geometry

`single_cell_unit_level`: treated units from explicit `test_0`; controls from explicit `control` (never `groups.values()`). Simultaneous adoption (`common_simultaneous_adoption`). Pooled DID readout. Cumulative ATT (`cumulative_att`) and cumulative bootstrap CI (`treatment_ci`) on **cumulative level** scale.

## 7. DGP world design

| world | scenario | injection |
|-------|----------|-----------|
| `clean_parallel_null` | `did_parallel_trends_holds` | 0% |
| `clean_parallel_positive_lift` | `did_parallel_trends_holds` | 8% |
| `weak_signal_null` | `scm_low_signal` (weak) | 0% |
| `noisy_positive_lift` | `scm_low_signal` (noisy) | 8% |
| `trend_violation_null` | `did_parallel_trends_violation` | 0% |
| `trend_violation_positive_lift` | `did_parallel_trends_violation` | 8% |
| `post_shock_null` | `scm_structural_break` | 0% |

Fixed seeds: `random_state_base + widx*1000 + rep*17 + attempt` (base `20260608`).

## 8. DID execution path

`DID(alpha=0.05)` → `run_analysis(panel, multiple_treated="pooled")` with embedded `_block_bootstrap_inference`. Point: `cumulative_att`. Interval: `treatment_ci` (cumulative level scale). Pretrend-violation worlds use `allow_pretrend_violation=True` for characterization under violation (not waiver authorization).

## 9. Metrics

Callable rate, assignment geometry (`n_treated`, `n_control`), bias/MAE/RMSE vs injected cumulative truth, sign errors, null/positive coverage (separate), type-I error, bootstrap center vs point gap, interval width, orientation failure rate, negative half-width rate, degenerate interval rate, non-finite rate.

## 10. Results by world

| world | feasible | null FPR | coverage | sign err | orient fail | callable fail |
|-------|----------|----------|----------|----------|-------------|---------------|
| `clean_parallel_null` | 15/15 | 0.0000 | 1.0000 | — | 0.000 | 0.000 |
| `clean_parallel_positive_lift` | 15/15 | — | 0.0000 | 0.0000 | 0.000 | 0.000 |
| `weak_signal_null` | 15/15 | 0.0000 | 1.0000 | — | 0.000 | 0.000 |
| `noisy_positive_lift` | 15/15 | — | 0.0667 | 0.0000 | 0.000 | 0.000 |
| `trend_violation_null` | 15/15 | 0.0000 | 1.0000 | — | 0.000 | 0.000 |
| `trend_violation_positive_lift` | 15/15 | — | 0.0667 | 0.0000 | 0.000 | 0.000 |
| `post_shock_null` | 15/15 | 0.0000 | 1.0000 | — | 0.000 | 0.000 |

**Structural checks:** 0 interval orientation failures, 0 negative half-widths, 105/105 feasible runs post-correction.

## 11. Null behavior

Null worlds show **0% type-I error** (bootstrap CI contains 0) with **100% null coverage** on cumulative level truth. Wide cumulative intervals absorb null point noise — characterization only, not nominal calibration.

## 12. Injected lift recovery

Injected worlds show **0% sign errors** and point estimates near injected cumulative truth (clean positive mean bias ~−8.5 on ~318 scale). **Positive coverage ~4.4% aggregate** (clean parallel 0%) — bootstrap intervals remain miscentered relative to `cumulative_att` under corrected geometry (production defect reproduced honestly).

## 13. Bias / MAE / RMSE

Injected worlds: directionally correct cumulative points; RMSE ~27 on clean positive lift. Null/stress worlds: larger point bias under shock/trend stress while intervals still cover 0.

## 14. Trend-violation behavior

All pretrend-violation runs feasible post-correction. Sign accuracy 100%; positive coverage ~6.7% on violation+lift world.

## 15. Post-shock behavior

`post_shock_null`: spurious cumulative points but intervals contain 0 (null FPR 0%, null coverage 100%).

## 16. Interval sanity

All emitted intervals satisfy `lower <= upper`; no negative half-widths. Bootstrap center (`bootstrap_mean`) misaligned with `cumulative_att` on positive worlds — supports separate production correction artifact.

## 17. Failure register

0 failures post-correction (vs pre-correction all-treated geometry failures on rebuild).

## 18. Overall verdict

`characterization_mixed_requires_followup`

**Rationale:** Structural interval checks pass; directional recovery is correct under fixed assignment; **injected-world coverage remains poor** due to production bootstrap miscentering — follow-up via `DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001` before any suitability movement.

## 19. What this artifact does not authorize

No promotion; no TrustReport/F-DECISION roles; no CalibrationSignal/MMM; no LLM recommendations; no governed uncertainty claim; no suitability or production-ready posture; no claim that Level B equals statistical validation.

## 20. Recommended next artifacts

- **`DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001`** (production bootstrap readout alignment)
- DCM-004 eligibility reassessment (after production correction if required)
- **`D5-STAT-TBRRIDGE-INF-001`** (already complete; context)

## 21. Guardrails

Level B only; cumulative level ATT interval scale explicit; explicit `test_0`/`control` assignment; all `forbidden_flags` false; compare to injected cumulative truth on level scale.
