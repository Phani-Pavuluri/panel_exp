# D5-INST-AUGSYNTH-ASCM-002 — AugSynth/ASCM vs A26 stratified OC

**Artifact:** [`archives/D5_INST_AUGSYNTH_ASCM_002_results.json`](archives/D5_INST_AUGSYNTH_ASCM_002_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py`  
**Charter:** [`../AUGSYNTH_ASCM_STRENGTHENING_001.md`](../AUGSYNTH_ASCM_STRENGTHENING_001.md)  

## Summary

**Overall verdict:** `remain_diagnostic_comparator`  
**Exit recommendation:** `remain_diagnostic_comparator`  
**Promotion audit eligible:** `False`

Compares **A26 SCM+UnitJackKnife** to **AugSynthCVXPY** arms across 12 charter worlds (weak SCM fit / hull stress stratified).

## Weak-fit vs A26 (@ 8% injection)

- AugSynth point beats A26 MAE on **1/2** weak-fit worlds.

## Governance

| Flag | Value |
|------|-------|
| Promotion | **No** |
| CalibrationSignal | **No** |
| MMM | **No** |
| A26 baseline | **Unchanged** |
| Primary inference selected | **No** |

## Findings

- **D5-ASCM2-FIND-002**: Stratified weak-fit / hull worlds executed; prior D5 batteries did not.
- **D5-ASCM2-FIND-003**: AugSynth point beats A26 MAE on 1/2 weak-fit worlds @ 8% injection.

## Weak-fit comparison detail

| world | AugSynth beats A26 MAE @ 8% | A26 JK null FPR | AugSynth JK null FPR |
|-------|------------------------------|-----------------|----------------------|
| `W2_weak_scm_fit_inside_hull` | True | 0.0 | 0.0 |
| `W3_weak_scm_fit_outside_hull` | False | 0.0 | 0.0 |

## Worlds

| world_id | fit_class |
|----------|-----------|
| `W0_baseline_reference` | baseline |
| `W1_strong_scm_fit_inside_hull` | strong_fit |
| `W2_weak_scm_fit_inside_hull` | weak_fit |
| `W3_weak_scm_fit_outside_hull` | weak_fit_outside_hull |
| `W4_sparse_donor_pool` | sparse_donors |
| `W5_rich_donor_pool` | rich_donors |
| `W6_null_treatment` | null_effect |
| `W7_treatment_effect_present` | effect_present |
| `W8_post_period_shock` | post_shock |
| `W9_noisy_donor` | noisy_donor |
| `W10_outlier_market` | outlier_market |
| `W11_multi_treated_unit_panel` | multi_treated |

