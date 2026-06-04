# D5-INF-AUGSYNTH-JK-CALIBRATION-001 — AugSynth+UnitJackKnife inference calibration

**Artifact:** [`archives/D5_INF_AUGSYNTH_JK_CALIBRATION_001_results.json`](archives/D5_INF_AUGSYNTH_JK_CALIBRATION_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inf_augsynth_jk_calibration_001.py`  

**Overall verdict:** `jk_unsafe_under_diagnostics`  
**Runtime (s):** `69.8`  

## 1. Purpose

Calibrate and characterize **AugSynth+UnitJackKnife** inference after ASCM-003 (`promising_needs_inference_calibration`). This PR does **not** promote AugSynth+JK or add it to governed uncertainty.

## 2. Prior evidence from ASCM-003

- Prior artifact: `D5-INST-AUGSYNTH-ASCM-003`  
- Prior verdict: `promising_needs_inference_calibration`  
- AugSynth point showed partial weak-fit MAE gains; JK null FPR was 0.0 on weak-fit worlds in ASCM-003 slice but sample was small (`n_mc=4`).

## 3. Design

- Monte Carlo: **n_mc=4** (target 8+; reduction: 19-world JK calibration grid runtime; harness default n_mc=8 for replay)
- Worlds: **19** (ASCM-003 registry)
- Calibration effect: **0.08**
- Arms: A26 SCM+UnitJackKnife vs AugSynth+UnitJackKnife only

## 4. Worlds / strata

Same 19-world ASCM-003 registry with weak-fit severity, hull, donor sparsity/richness, and ridge-λ worlds. Diagnostic strata: good/poor prefit, inside/outside hull, donor pool, weak-fit severity bands.

## 5. Methods compared

| Arm | Role |
|-----|------|
| `a26_scm_unit_jackknife` | Governed null-monitor reference |
| `augsynth_cvxpy_unit_jackknife` | Calibration target (not promoted) |

## 6. Diagnostics used

D5-DIAG panel fields (`scm_pre_rmse`, `hull_min_donor_z_distance`, `fit_improvement_rmse`, …) plus instrument flags (`false_confidence_flag`, `narrow_interval_poor_fit_flag`) and null-world `conflict_vs_a26` disagreement.

## 7. Null FPR

| arm | mean null interval-exclusion FPR |
|-----|----------------------------------|
| A26 JK | 0.02631578947368421 |
| AugSynth JK | 0.014705882352941176 |

Unsafe AugSynth+JK worlds (FPR > 0.15): `['W8_post_period_shock']`

## 8. Effect coverage

@ 0.08 injection:

| arm | mean covers injected effect |
|-----|----------------------------|
| A26 JK | 0.9722222222222222 |
| AugSynth JK | 0.984375 |

## 9. Interval width / conservatism

- Mean AugSynth/A26 half-width ratio @ null: `1.514746722516573`
- Mean AugSynth/A26 half-width ratio @ effect: `1.5233956999298992`
- Conservative threshold ratio: `1.35`

## 10. False-confidence behavior

Rates for narrow interval + poor prefit, high donor stress, and high SCM/AugSynth disagreement:

- `false_conf_narrow_poor_prefit` (AugSynth JK @ null): mean `0.0`
- `false_conf_narrow_high_donor_stress` (AugSynth JK @ null): mean `0.0`
- `false_conf_narrow_high_disagreement` (AugSynth JK @ null): mean `0.0`

## 11. Diagnostic-conditioned results

See artifact `diagnostic_strata.at_null` and `diagnostic_strata.at_effect` for FPR, coverage, and half-width by prefit, hull, donor-pool, and weak-fit severity.

## 12. Comparison to A26

Per-world comparison in artifact `a26_vs_aug_jk_comparison.comparisons` (FPR, coverage, half-width, point MAE).

## 13. Verdict

**`jk_unsafe_under_diagnostics`** — AugSynth+JK remains **diagnostic / not governed uncertainty**.

## 14. Guardrails

| Guardrail | Status |
|-----------|--------|
| Promotion | **No** |
| Governed uncertainty allowlist | **No change** |
| Threshold finalization | **No** |
| Estimator / inference code change | **No** |

## 15. Next step

If `jk_safe_but_conservative`: continue comparator lane; optional larger-n OC. If `jk_promising_needs_more_oc`: extend n_mc and weak-fit strata before any calibration-candidate discussion. No promotion audit.

## Findings

- **D5-JKCAL-FIND-001**: JK calibration battery on 19 ASCM-003 worlds (n_mc=4) after D5-INST-AUGSYNTH-ASCM-003 verdict `promising_needs_inference_calibration`.
- **D5-JKCAL-FIND-002**: AugSynth+JK unsafe null-FPR worlds (>0.15): 1 — ['W8_post_period_shock']
- **D5-JKCAL-FIND-003** (info): n_mc=4; 19-world JK calibration grid runtime; harness default n_mc=8 for replay
- **D5-JKCAL-FIND-005** (high): Elevated null FPR under one or more worlds/diagnostic strata.

