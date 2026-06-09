# D5-STAT-DID-BOOTSTRAP-001 — Level B characterization (DID + embedded bootstrap)

**Artifact ID:** D5-STAT-DID-BOOTSTRAP-001
**Type:** Level B characterization — **not** promotion, **not** governed uncertainty validation
**Overall verdict:** `characterization_mixed_requires_followup`

**Archive:** [`archives/D5_STAT_DID_BOOTSTRAP_001_results.json`](archives/D5_STAT_DID_BOOTSTRAP_001_results.json)
**Harness:** `panel_exp/validation/track_d_d5_stat_did_bootstrap_001.py`
**Regenerate:** `python -m panel_exp.validation.track_d_d5_stat_did_bootstrap_001`

## 1. Purpose

Characterize **DID** with **estimator-native embedded moving-block bootstrap** on **single-cell unit-panel** geometry (`multiple_treated="pooled"`). Evaluates callable stability, finite point/interval outputs, interval orientation, null interval behavior, injected cumulative lift recovery, and pretrend/shock sensitivity.

## 2. Relationship to D5-STAT-SMOKE-CALLABLE-001

Smoke established `DID-BOOTSTRAP` as **callable_pass** on `single_cell_unit_level`. This artifact runs a Level B battery — smoke pass does not authorize suitability, TrustReport roles, or CalibrationSignal/MMM.

## 3. Relationship to prior Level B artifacts

Parallel to SCM-JK, AugSynth point, and TBR aggregate characterizations. Prior artifacts are **context only**; injected cumulative level truth is defined on the unit panel after percent injection.

## 4. Relationship to suitability framework

`DID-BOOTSTRAP` remains `suitability_candidate_pending_oc`. This characterization updates evidence only — no suitability tier movement.

## 5. Scope and exclusions

**In scope:** DID estimator, embedded bootstrap inference, single-cell unit panel, seven worlds × 15 replicates.

**Out of scope:** SCM, AugSynth, TBR/TBRRidge, multi-cell pooling, production roles, TrustReport/F-DECISION, CalibrationSignal, MMM, LLM, primary/secondary evidence labels.

## 6. Panel geometry

`single_cell_unit_level`: multiple treated units assigned via `greedy_match_markets`, simultaneous adoption, pooled DID readout. Cumulative ATT (`cumulative_att`) and cumulative bootstrap CI (`treatment_ci`) are the primary interval scale.

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

Fixed seeds: `random_state_base + widx*1000 + rep*17 + attempt`.

## 8. DID execution path

`DID(alpha=0.05)` → `run_analysis(panel, multiple_treated="pooled")` with embedded `_block_bootstrap_inference`. Point: `cumulative_att`. Interval: `treatment_ci` (cumulative absolute scale). Pretrend-violation worlds use `allow_pretrend_violation=True` for characterization under violation (not waiver authorization).

## 9. Metrics

Callable rate, bias/MAE/RMSE vs injected cumulative truth, sign errors, null interval false-positive rate (interval excludes 0), injected-world coverage, interval width, orientation failure rate, negative half-width rate, degenerate interval rate, non-finite rate.

## 10. Results by world

| world | feasible | null FPR | coverage | sign err | orient fail | neg HW | callable fail |
|-------|----------|----------|----------|----------|-------------|--------|---------------|
| `clean_parallel_null` | 15/15 | 0.0000 | 1.0000 | — | 0.000 | 0.000 | 0.000 |
| `clean_parallel_positive_lift` | 15/15 | — | 0.0000 | 0.0000 | 0.000 | 0.000 | 0.000 |
| `weak_signal_null` | 15/15 | 0.0000 | 1.0000 | — | 0.000 | 0.000 | 0.000 |
| `noisy_positive_lift` | 15/15 | — | 0.0000 | 0.0000 | 0.000 | 0.000 | 0.000 |
| `trend_violation_null` | 14/15 | 0.0000 | 1.0000 | — | 0.000 | 0.000 | 0.067 |
| `trend_violation_positive_lift` | 15/15 | — | 0.0000 | 0.0000 | 0.000 | 0.000 | 0.000 |
| `post_shock_null` | 15/15 | 0.0000 | 1.0000 | — | 0.000 | 0.000 | 0.000 |

**Structural checks:** 0 interval orientation failures, 0 negative half-widths across all feasible runs.

## 11. Null behavior

Null worlds show **0% interval false-positive rate** (bootstrap CI contains 0) despite often-large point estimates — wide cumulative intervals absorb null. This is **not** nominal calibration validation; characterization only.

## 12. Injected lift recovery

Injected worlds show **0% sign errors** and point estimates near injected cumulative truth (mean bias &lt; 76 on ~700–800 scale). **Coverage is 0%** on injected worlds — cumulative bootstrap intervals do not cover injected cumulative truth in this battery.

## 13. Bias / MAE / RMSE

Injected worlds: directionally correct cumulative points with moderate MAE vs injected cumulative level. Null/stress worlds: large point MAE under shock/trend stress while intervals still cover 0.

## 14. Trend-violation behavior

`trend_violation_null`: 1 callable failure / 15; remaining runs finite with 0% null FPR. `trend_violation_positive_lift`: 0 sign errors, 0% coverage — pretrend violation does not break callable path but interval width/point alignment remains mixed.

## 15. Post-shock behavior

`post_shock_null`: large spurious cumulative points (~922 mean) but intervals contain 0 (null FPR 0%). Characterizes shock sensitivity without structural interval failure.

## 16. Interval sanity

All emitted intervals satisfy `lower <= upper`; no negative half-widths detected. Degenerate interval rate 0%.

## 17. Failure register

1 failure in `trend_violation_null` (callable_fail); all other worlds 15/15 feasible.

## 18. Overall verdict

`characterization_mixed_requires_followup`

**Rationale:** Structural interval checks pass (orientation, half-width, finiteness in clean worlds), directional recovery is reasonable, but **injected-world coverage is 0%** and stress-world point behavior is unstable — follow-up required before any suitability movement.

## 19. What this artifact does not authorize

No promotion; no TrustReport/F-DECISION roles; no CalibrationSignal/MMM; no LLM recommendations; no governed uncertainty claim; no suitability or production-ready posture; no claim that Level B equals statistical validation.

## 20. Recommended next artifacts

- **`D5-STAT-MCELL-PERCELL-001`**
- **`D5-STAT-TBRRIDGE-INF-001`**

## 21. Guardrails

Level B only; cumulative ATT interval scale explicit; all `forbidden_flags` false; compare to injected cumulative truth, not relative ATT recovery estimand.
