# D5-STAT-SCM-JK-001 — Level B characterization (SCM + UnitJackKnife)

> **Harness correction:** `D5-STAT-SCM-JK-001-HARNESS-CORRECTION` supersedes canonical
> rebuild/coverage interpretation. Historical archive retained at
> `archives/D5_STAT_SCM_JK_001_results_historical_pre_harness_correction.json`.

**Artifact ID:** D5-STAT-SCM-JK-001
**Type:** Level B characterization — **not** calibration or promotion
**Overall verdict:** `characterization_pass_with_caveats`
**Harness correction verdict:** `scm_jk_harness_corrected_level_consistent_baseline_established`

**Archive:** [`archives/D5_STAT_SCM_JK_001_results.json`](archives/D5_STAT_SCM_JK_001_results.json)
**Harness:** `panel_exp/validation/track_d_d5_stat_scm_jk_001.py`
**Canonical effect scale:** `level_effect`

## 1. Purpose

Characterize SCM + UnitJackKnife on unit-panel single-cell geometry under
deterministic synthetic worlds: null behavior, injected lift, interval sanity,
donor/pre-fit stress, and weak/noisy signal.

## 2. Relationship to D5-STAT-SMOKE-CALLABLE-001

Follows smoke callable evidence (`SCM-JK` callable_pass). Smoke does not imply
statistical validation.

## 3. Relationship to suitability framework

`SCM-JK` remains `suitability_candidate_pending_oc`; this artifact supplies
Level B evidence only.

## 4. Scope and exclusions

SCM + UnitJackKnife only. No AugSynth, TBR, TBRRidge, DID, multi-cell pooled,
supergeo, or trim.

## 5. DGP world design

| world_id | intent |
|----------|--------|
| `clean_null` | stable null |
| `clean_positive_lift` | injected post-period level lift |
| `weak_signal_null` | low SNR null |
| `noisy_positive_lift` | injected lift under higher noise |
| `donor_stress` | fewer geos / thinner donor pool |
| `outside_hull_or_poor_prefit` | trend mismatch — harder pre-fit |
| `post_shock_null` | structural break under null |

**Replicates per world:** 15

## 8. Results by world

| world | feasible | null FPR | coverage (level) | coverage (frac %) | mean bias | orient fail rate |
|-------|----------|----------|------------------|-------------------|-----------|------------------|
| `clean_null` | 15/15 | 0.1333 | 0.8667 | 0.8667 | 0.2533 | 0.000 |
| `clean_positive_lift` | 15/15 | — | 1.0000 | 0.0000 | 0.3873 | 0.000 |
| `weak_signal_null` | 15/15 | 0.1333 | 0.8667 | 0.8667 | -0.4911 | 0.000 |
| `noisy_positive_lift` | 15/15 | — | 0.8000 | 0.0000 | -0.2008 | 0.000 |
| `donor_stress` | 15/15 | 0.0667 | 0.9333 | 0.9333 | 0.3326 | 0.000 |
| `outside_hull_or_poor_prefit` | 15/15 | 0.0667 | 0.9333 | 0.9333 | 0.2313 | 0.000 |
| `post_shock_null` | 15/15 | 0.1333 | 0.8667 | 0.8667 | 1.3859 | 0.000 |

## 14. Overall verdict

`characterization_pass_with_caveats`

## 15. What this artifact does not authorize

No production promotion, TrustReport roles, CalibrationSignal, MMM, LLM rec,
or claim that SCM+JK is statistically validated or suitable.

## 16. Recommended next artifacts

`D5-STAT-AUGSYNTH-POINT-001`, `D5-STAT-TBR-AGG-001`

## 17. Guardrails

Level B characterization only; fixed seeds; no estimator/inference changes.

