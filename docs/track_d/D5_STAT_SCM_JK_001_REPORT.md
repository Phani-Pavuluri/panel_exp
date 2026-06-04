# D5-STAT-SCM-JK-001 — Level B characterization (SCM + UnitJackKnife)

**Artifact ID:** D5-STAT-SCM-JK-001
**Type:** Level B characterization — **not** calibration or promotion
**Overall verdict:** `characterization_mixed_requires_followup`

**Archive:** [`archives/D5_STAT_SCM_JK_001_results.json`](archives/D5_STAT_SCM_JK_001_results.json)
**Harness:** `panel_exp/validation/track_d_d5_stat_scm_jk_001.py`

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

**Replicates per world:** 15 (characterization-only; not promotion-grade MC)

## 6. SCM+JK execution path

`SyntheticControlCVXPY` + `UnitJackKnife`, `greedy_match_markets` assignment, percent post-period injection (D5-POW-001b pattern), fixed seed base `20260604`.

## 7. Metrics

Null FPR (interval excludes zero on effect scale), coverage, bias/MAE/RMSE, interval width, orientation failure rate, negative half-width rate, pre-fit RMSE, donor count.

## 8. Results by world

| world | feasible | null FPR | coverage | mean bias | orient fail rate |
|-------|----------|----------|----------|-----------|------------------|
| `clean_null` | 15/15 | 0.0667 | 0.9333 | 0.0752 | 0.000 |
| `clean_positive_lift` | 15/15 | — | 0.0667 | 8.5915 | 0.000 |
| `weak_signal_null` | 13/15 | 0.2308 | 0.7692 | -0.0629 | 0.000 |
| `noisy_positive_lift` | 15/15 | — | 0.0667 | 7.5251 | 0.000 |
| `donor_stress` | 12/15 | 0.0000 | 1.0000 | 0.4883 | 0.000 |
| `outside_hull_or_poor_prefit` | 14/15 | 0.0714 | 0.9286 | -0.2260 | 0.000 |
| `post_shock_null` | 15/15 | 0.3333 | 0.6667 | 0.9964 | 0.000 |

## 9. Null behavior

`clean_null` null FPR ≈ 6.7%. `weak_signal_null` ≈ 23% (elevated). `post_shock_null` ≈ 33% (elevated under structural break). Interval orientation passes on all feasible runs.

## 10. Injected lift recovery

Point estimates track positive injection (correct sign; `sign_error_rate` 0) but **coverage vs injected percent is not calibrated** on this battery (level-scale gap between 0.08 fractional injection and level readouts). Follow-up: readout-aligned effect scale for Level C.

## 11. Interval orientation and width checks

**Zero** orientation failures and **zero** negative half-widths across feasible runs. Mean interval widths vary by world (≈4–10 level units).

## 12. Donor/pre-fit stress behavior

`donor_stress`: 12/15 feasible (assignment retries). `outside_hull_or_poor_prefit`: higher pre-fit RMSE, modest null FPR. No silent geometry bypass.

## 13. Failure register

6 assignment failures (`insufficient control units`) across weak_signal, donor_stress, outside_hull worlds — recorded in JSON `failure_register`.

## 14. Overall verdict

`characterization_mixed_requires_followup` — structural interval checks pass; null FPR elevated under weak signal and post-shock; lift coverage metric needs readout alignment before suitability claims.

## 15. What this artifact does not authorize

No production promotion, TrustReport roles, CalibrationSignal, MMM, LLM rec,
or claim that SCM+JK is statistically validated or suitable.

## 16. Recommended next artifacts

**D5-STAT-AUGSYNTH-POINT-001:** ✅ complete — see [`D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](D5_STAT_AUGSYNTH_POINT_001_REPORT.md) (compare to injected truth, not this SCM-JK battery).

Next: **`D5-STAT-TBR-AGG-001`**

## 17. Guardrails

Level B characterization only; fixed seeds; no estimator/inference changes.

