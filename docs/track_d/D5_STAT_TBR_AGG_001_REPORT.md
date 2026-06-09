# D5-STAT-TBR-AGG-001 — Level B characterization (TBR aggregate point)

**Artifact ID:** D5-STAT-TBR-AGG-001
**Type:** Level B aggregate point characterization — **not** unit-panel TBR, **not** inference validation
**Overall verdict:** `characterization_mixed_requires_followup`

**Archive:** [`archives/D5_STAT_TBR_AGG_001_results.json`](archives/D5_STAT_TBR_AGG_001_results.json)
**Harness:** `panel_exp/validation/track_d_d5_stat_tbr_agg_001.py`
**Regenerate:** `python -m panel_exp.validation.track_d_d5_stat_tbr_agg_001`

## 1. Purpose

Characterize class **TBR** (`inference=None`) **point** estimates on **aggregate 2-row** geometry: one summed treated series and one summed control series. This is characterization-only evidence for aggregate ATT readout behavior under synthetic DGP worlds — not production promotion.

## 2. Relationship to D5-STAT-SMOKE-CALLABLE-001

Smoke artifact **`D5-STAT-SMOKE-CALLABLE-001`** established `TBR-AGG-POINT` as **callable_pass** on `aggregate_two_series` geometry. This artifact executes a Level B battery (recovery, null behavior, stress worlds) on that same geometry. Smoke pass does **not** imply suitability, governed uncertainty, or unit-panel generalization.

## 3. Relationship to SCM-JK and AugSynth point artifacts

**`D5-STAT-SCM-JK-001`** and **`D5-STAT-AUGSYNTH-POINT-001`** are parallel Level B batteries on **unit-panel** geometry. They provide **context only** — injected level truth here is defined on the **aggregate** panel after percent injection, not SCM or AugSynth counterfactuals.

## 4. Relationship to suitability framework

Per **`DESIGN-ESTIMATOR-INFERENCE-SUITABILITY-FRAMEWORK-001`**, `TBR-AGG-POINT` remains **`suitability_candidate_pending_oc`**. This characterization updates evidence posture only; it does **not** advance suitability tier or trust role.

## 5. Scope and exclusions

**In scope:** TBR aggregate point, aggregate 2-row geometry, seven synthetic worlds, 15 replicates/world, fixed seeds.

**Out of scope (explicit):** unit-panel TBR; TBR + UnitJackKnife; TBRRidge; BRB / Conformal / KFold uncertainty claims; SCM; AugSynth; DID; multi-cell pooling; supergeo; trim; production role assignment; TrustReport; CalibrationSignal; MMM; LLM recommendations; primary/secondary evidence labels.

## 6. Aggregate 2-row geometry definition

Panel has exactly **two rows** (`treated`, `control`) and **one** treated unit id (`treated`). Unit-level geos are summed into aggregate series before estimation. A geometry guard rejects panels that are not 2-row aggregate before and after injection.

## 7. DGP world design

Deterministic worlds from `RECOVERY_SCENARIO_REGISTRY` + `greedy_match_markets` assignment + percent post-period injection (injected level truth). Worlds: `clean_null`, `clean_positive_lift`, `weak_signal_null`, `noisy_positive_lift`, `trend_mismatch_null`, `post_shock_null`, `short_post_positive_lift` (32 pre / 4 post). **15 replicates** per world; seeds `random_state_base + widx*1000 + rep*17 + attempt`.

## 8. TBR execution path

`TBR(inference=None, alpha=0.05)` → `run_analysis(panel)` on aggregate panel. Point readout: mean post-window `(y - y_hat)` on treated aggregate path. No interval fields; `interval_present: false`, `interval_validation_applicable: false` on every run.

## 9. Metrics

Per world: callable rate, bias/MAE/RMSE, sign error (injected), null directional false-positive rate (|point| > 1.0 on null worlds), point recovery ratio vs injected level, over/understatement, non-finite rate, pre-fit RMSE/R² means, geometry violation count.

## 10. Results by world

| world | feasible | null dir. FPR | recovery mean | sign err | callable fail | geom viol |
|-------|----------|---------------|---------------|----------|---------------|-----------|
| `clean_null` | 15/15 | 0.8667 | — | — | 0.000 | 0 |
| `clean_positive_lift` | 15/15 | — | 0.9946 | 0.0000 | 0.000 | 0 |
| `weak_signal_null` | 15/15 | 1.0000 | — | — | 0.000 | 0 |
| `noisy_positive_lift` | 15/15 | — | 1.0036 | 0.0000 | 0.000 | 0 |
| `trend_mismatch_null` | 15/15 | 0.8667 | — | — | 0.000 | 0 |
| `post_shock_null` | 15/15 | 1.0000 | — | — | 0.000 | 0 |
| `short_post_positive_lift` | 15/15 | — | 1.0504 | 0.0000 | 0.000 | 0 |

All runs: **105** total; **0** callable failures; **0** geometry violations.

## 11. Null behavior

Null worlds show **high directional false-signal rates** under the fixed threshold (|point| > 1.0): `clean_null` 0.87, `weak_signal_null` 1.0, `trend_mismatch_null` 0.87, `post_shock_null` 1.0. Median null point estimates are smaller than means (heavy-tail positive/negative spikes). This is **not** a claim of valid null calibration — characterization only.

## 12. Injected lift recovery

`clean_positive_lift` and `noisy_positive_lift` show **directionally correct** signs (0% sign error) with recovery ratios near 1.0 (means 0.99 and 1.00). `short_post_positive_lift` recovery mean 1.05 with 4-period post window — directionally stable, modest over-recovery vs injected level.

## 13. Bias / MAE / RMSE

Injected worlds: mean bias near zero vs injected level (~−0.3 to +5.4); MAE/RMSE reflect aggregate scale and pre-fit noise. Null worlds: large MAE/RMSE driven by spurious post-period point mass under shock/trend stress — consistent with mixed verdict.

## 14. Trend mismatch behavior

`trend_mismatch_null`: high null directional FPR (0.87), pre-fit R² mean elevated (~0.97) but post readout still produces directional mass — trend divergence without injection is **not** neutralized by TBR aggregate point readout.

## 15. Post-shock behavior

`post_shock_null`: null directional FPR **1.0**, very large mean point (~225), pre-fit R² mean **~0.06** — structural break world breaks pre-fit and drives strong false post signal.

## 16. Short post-period behavior

`short_post_positive_lift`: 15/15 feasible, 0 sign errors, recovery ~1.05 — **unstable vs long-post worlds** in magnitude dispersion but callable and directional. Characterization does **not** authorize short-post production defaults.

## 17. Failure register

Empty — no exceptions across 105 runs. Non-finite post readout rate **0** on feasible runs.

## 18. Overall verdict

`characterization_mixed_requires_followup`

**Rationale:** Callable/finite behavior is stable and injected worlds recover directionally with ratios near 1.0, but null/trend/shock worlds show **high false directional signal** — follow-up artifacts required before any suitability movement.

## 19. What this artifact does not authorize

No unit-panel TBR validation; no TBRRidge; no governed uncertainty; no promotion; no TrustReport/F-DECISION roles; no CalibrationSignal or MMM; no LLM recommendation; no claim that Level B equals statistical validation; no suitability or production-ready posture.

## 20. Recommended next artifacts

- **`D5-STAT-DID-BOOTSTRAP-001`**
- **`D5-STAT-MCELL-PERCELL-001`**
- **`D5-STAT-TBRRIDGE-INF-001`** (aggregate inference — separate scope; not implied by this point characterization)

## 21. Guardrails

- `unit_panel_generalization_allowed`: **false** (JSON `forbidden_flags` and summary).
- All promotion/trust/calibration/MMM/LLM/suitability/governed-uncertainty flags: **false**.
- Aggregate 2-row only; compare to **injected level** truth, not SCM/AugSynth.
- Interval validation explicitly **not applicable**.
