# D5-INST-AUGSYNTH-ASCM-003 — stratified AugSynth/ASCM OC (diagnostics + fidelity)

**Artifact:** [`archives/D5_INST_AUGSYNTH_ASCM_003_results.json`](archives/D5_INST_AUGSYNTH_ASCM_003_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_augsynth_ascm_003.py`  
**Diagnostics:** [`../validation/scm_augsynth_diagnostics.py`](../validation/scm_augsynth_diagnostics.py) (D5-DIAG-SCM-AUGSYNTH-001)  
**Fidelity audit:** [`../AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md`](../AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md)  

**Overall verdict:** `promising_needs_inference_calibration`  
**Runtime (s):** `1019.2`  
**Promotion audit eligible:** `False`

## 1. Purpose

Run the next stratified operating-characteristic (OC) battery for **AugSynth/ASCM vs A26** after D5-DIAG-SCM-AUGSYNTH-001 and the implementation fidelity audit. Characterize when AugSynth helps, when it fails, and which D5-DIAG fields are useful for future threshold calibration — **without promotion or threshold finalization**.

## 2. Design

- Monte Carlo replicates: **n_mc=4** (target ≥14; reduction reason: 19-world grid runtime in dev environment; harness default n_mc=14 for replay)
- Worlds: **19** (ASCM-002 charter + weak-fit severity grid + donor sparsity/richness extensions + ridge-λ sensitivity worlds)
- Primary arms: A26 SCM+UnitJackKnife, AugSynth point, AugSynth+UnitJackKnife
- Secondary diagnostic arms: AugSynth+Conformal, AugSynth+Kfold (inference context only)
- Panel diagnostics: full D5-DIAG field set on every replicate

## 3. Worlds / strata

| world_id | fit_class | weak_fit_severity | lambda_reg |
|----------|-----------|-------------------|------------|
| `W0_baseline_reference` | baseline | — | 0.0 |
| `W1_strong_scm_fit_inside_hull` | strong_fit | — | 0.0 |
| `W2_weak_scm_fit_inside_hull` | weak_fit | — | 0.0 |
| `W3_weak_scm_fit_outside_hull` | weak_fit_outside_hull | — | 0.0 |
| `W4_sparse_donor_pool` | sparse_donors | — | 0.0 |
| `W5_rich_donor_pool` | rich_donors | — | 0.0 |
| `W6_null_treatment` | null_effect | — | 0.0 |
| `W7_treatment_effect_present` | effect_present | — | 0.0 |
| `W8_post_period_shock` | post_shock | — | 0.0 |
| `W9_noisy_donor` | noisy_donor | — | 0.0 |
| `W10_outlier_market` | outlier_market | — | 0.0 |
| `W11_multi_treated_unit_panel` | multi_treated | — | 0.0 |
| `W2m_mild_weak_fit` | weak_fit | mild | 0.0 |
| `W2s_severe_weak_fit` | weak_fit | severe | 0.0 |
| `W3s_severe_outside_hull` | weak_fit_outside_hull | severe | 0.0 |
| `W4s_ultra_sparse_donor_pool` | sparse_donors | — | 0.0 |
| `W5s_very_rich_donor_pool` | rich_donors | — | 0.0 |
| `W2r_lambda_reg_moderate` | weak_fit | moderate | 0.01 |
| `W2r_lambda_reg_high` | weak_fit | moderate | 0.05 |

## 4. Methods compared

| Arm | Role |
|-----|------|
| `a26_scm_unit_jackknife` | Baseline / null-monitor reference |
| `augsynth_cvxpy_point` | AugSynth point comparator |
| `augsynth_cvxpy_unit_jackknife` | AugSynth inference comparator |
| `augsynth_cvxpy_conformal` | Diagnostic-only (elevated null FPR historically) |
| `augsynth_cvxpy_kfold` | Diagnostic-only |

## 5. Diagnostics included

Panel (D5-DIAG): `scm_pre_rmse`, `scm_pre_rmse_normalized`, `augsynth_pre_rmse`, `augsynth_pre_rmse_normalized`, `fit_improvement_rmse`, `fit_improvement_relative`, `donor_sparsity_n_control`, `hull_min_donor_z_distance`, `weight_herfindahl`, `max_weight`, `n_negative_weights`, `effective_donor_count`, `treated_pre_period_std`, `donor_weighted_pre_period_std`, `scale_bridge_ratio`, `outcome_model_alpha`, `outcome_model_coef_l2_norm`, `outcome_model_available`, `diagnostics_feasible`

Instrument: `false_confidence_flag`, `narrow_interval_poor_fit_flag`

Conflict vs A26: `null_sign_disagreement`, `null_material_point_mismatch`, `null_point_effect_delta`

## 6. Results summary

- AugSynth point beats A26 MAE on **4/7** weak-fit worlds @ 8% injection.
- Inside-hull AugSynth wins: **4/11**.
- Outside-hull AugSynth wins: **1/2**.

## 7. Weak-fit recovery

- **mild**: AugSynth beats A26 on 1/1 worlds.
- **moderate**: AugSynth beats A26 on 1/4 worlds.
- **severe**: AugSynth beats A26 on 2/2 worlds.

## 8. Inside-hull vs outside-hull behavior

Inside-hull strata aggregate worlds with fit classes ['baseline', 'rich_donors', 'sparse_donors', 'strong_fit', 'weak_fit']; outside-hull uses `['weak_fit_outside_hull']`.

| stratum | AugSynth beats A26 @ 8% | world count |
|---------|-------------------------|-------------|
| inside | 4 | 11 |
| outside | 1 | 2 |

## 9. Null FPR / interval behavior

| arm | mean null interval-exclusion FPR | mean null half-width |
|-----|----------------------------------|----------------------|
| `a26_scm_unit_jackknife` | 0.02631578947368421 | 4.436393986981314 |
| `augsynth_cvxpy_point` | — | — |
| `augsynth_cvxpy_unit_jackknife` | 0.013888888888888888 | 5.493126565389594 |
| `augsynth_cvxpy_conformal` | 0.018518518518518517 | 59.876056072594615 |

## 10. Diagnostic usefulness

- Positive `fit_improvement_rmse` → AugSynth wins rate: **0.5882352941176471** (n=17 worlds).
- High hull stress (z≥2) → AugSynth loses rate: **0.3888888888888889** (n=18 worlds).
- Provisional threshold calibration: fields emitted; **numeric cutoffs not finalized**.

## 11. Fidelity-audit caveats carried forward

Audit **AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001** verdict: `fidelity_confirmed_with_caveats`.

- **G4**: D1 scm_pre_rmse uses SciPy SyntheticControl, not inner SyntheticControlCVXPY.
- **G1**: penalty/penalty_strength stored on AugSynthCVXPY but unused on OSQP SCM path.
- **G7**: OC uses level mean_point_effect; summary() uses relative effect estimand.
- **G8**: Hull stress uses z-distance proxy, not true convex hull membership.

## 12. Decision / verdict

**`promising_needs_inference_calibration`** — see findings below. No promotion audit opened.

## 13. Guardrails

| Guardrail | Status |
|-----------|--------|
| Promotion | **No** |
| Threshold finalization | **No** |
| Eligibility change | **No** |
| Estimator behavior change | **No** |
| Inference behavior change | **No** |
| TrustReport / F-DECISION | **No change** |
| CalibrationSignal / MMM | **No** |

## 14. Next step

Continue diagnostic-comparator lane with inference-pairing ADR if `promising_needs_inference_calibration`; otherwise extend threshold calibration on D5-DIAG fields (ASCM-004+). Optional fidelity follow-ups: G4 SCM-leg alignment, G8 hull definition — separate implementation PRs only.

## Findings

- **D5-ASCM3-FIND-001**: Stratified OC with D5-DIAG fields across 19 worlds (n_mc=4).
- **D5-ASCM3-FIND-002**: AugSynth point beats A26 MAE on 4/7 weak-fit worlds @ 8%.
- **D5-ASCM3-FIND-003**: Fidelity audit caveats G1/G4/G7/G8 carried in artifact metadata; interpret diagnostics as provisional comparators only.
- **D5-ASCM3-FIND-005** (info): n_mc=4 (<14): 19-world grid runtime in dev environment; harness default n_mc=14 for replay.

## Weak-fit comparison detail

| world | AugSynth beats A26 MAE @ 8% | A26 JK null FPR | AugSynth JK null FPR |
|-------|------------------------------|-----------------|----------------------|
| `W2_weak_scm_fit_inside_hull` | True | 0.0 | 0.0 |
| `W3_weak_scm_fit_outside_hull` | False | 0.0 | 0.0 |
| `W2m_mild_weak_fit` | True | 0.0 | 0.0 |
| `W2s_severe_weak_fit` | True | 0.0 | 0.0 |
| `W3s_severe_outside_hull` | True | 0.0 | 0.0 |
| `W2r_lambda_reg_moderate` | False | 0.0 | 0.0 |
| `W2r_lambda_reg_high` | False | 0.0 | 0.0 |

