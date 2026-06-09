# D5-STAT-AUGSYNTH-POINT-001 — Level B characterization (AugSynthCVXPY point)

**Artifact ID:** D5-STAT-AUGSYNTH-POINT-001
**Type:** Level B point characterization — **not** inference validation
**Overall verdict:** `characterization_mixed_requires_followup`

**Archive:** [`archives/D5_STAT_AUGSYNTH_POINT_001_results.json`](archives/D5_STAT_AUGSYNTH_POINT_001_results.json)
**Harness:** `panel_exp/validation/track_d_d5_stat_augsynth_point_001.py`

## 1. Purpose

Characterize AugSynthCVXPY **point** estimates on unit-panel single-cell geometry.
Compare to **injected level truth**, not SCM+JK (prior SCM-JK was mixed).

## 2. Relationship to D5-STAT-SMOKE-CALLABLE-001

`AUGSYNTH-POINT` smoke callable_pass — does not authorize inference or suitability.

## 3. Relationship to D5-STAT-SCM-JK-001

Parallel Level B battery; SCM-JK is **context only**, not ground truth for AugSynth.

## 4. Relationship to suitability framework

`AUGSYNTH-POINT` remains `diagnostic_candidate_pending_oc`; G1–G8 fidelity still open.

## 5. Scope and exclusions

Point only. No JK, Conformal, KFold uncertainty, multi-cell, supergeo, trim, TBR, DID.

## 6. DGP world design

Same seven-world family as SCM-JK (15 replicates/world, fixed seeds).

## 7. AugSynthCVXPY execution path

`AugSynthCVXPY(inference=None)` + `greedy_match_markets` + percent injection.

## 8. Metrics

Point recovery ratio vs injected level, null directional false-signal rate, bias/MAE/RMSE,
over/understatement on injected worlds.

## 9. Results by world

| world | feasible | null dir. FPR | recovery mean | sign err | callable fail |
|-------|----------|-----------------|---------------|----------|---------------|
| `clean_null` | 14/15 | 0.2143 | — | — | 0.067 |
| `clean_positive_lift` | 15/15 | — | 0.9868 | 0.0000 | 0.000 |
| `weak_signal_null` | 14/15 | 0.7143 | — | — | 0.067 |
| `noisy_positive_lift` | 15/15 | — | 1.0790 | 0.0000 | 0.000 |
| `donor_stress` | 12/15 | 0.2500 | — | — | 0.200 |
| `outside_hull_or_poor_prefit` | 14/15 | 0.1429 | — | — | 0.067 |
| `post_shock_null` | 15/15 | 1.0000 | — | — | 0.000 |

## 17. Overall verdict

`characterization_mixed_requires_followup`

## 18. What this artifact does not authorize

No governed uncertainty, suitability, promotion, TrustReport, CalibrationSignal, MMM, LLM.
No claim that point characterization validates AugSynth inference.

## 19. Recommended next artifacts

TBR aggregate Level B: ✅ **D5-STAT-TBR-AGG-001**. Next: **`D5-STAT-DID-BOOTSTRAP-001`**, **`D5-STAT-MCELL-PERCELL-001`**

## 20. Guardrails

Level B only; interval fields explicitly not applicable.

