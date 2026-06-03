# D5-DIAG-SCM-AUGSYNTH-001 — SCM/AugSynth diagnostic implementation

**Artifact ID:** D5-DIAG-SCM-AUGSYNTH-001  
**Type:** Diagnostic implementation (validation layer only)  
**Status:** **complete**  
**Date:** 2026-06-03  
**Verdict:** Reusable SCM/AugSynth diagnostic helpers implemented and wired into ASCM-002-style validation output. **No threshold finalization. No promotion.**

**Module:** [`panel_exp/validation/scm_augsynth_diagnostics.py`](../../panel_exp/validation/scm_augsynth_diagnostics.py)  
**Integration:** [`panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py`](../../panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py)  
**Tests:** [`tests/track_d/test_scm_augsynth_diagnostics.py`](../../tests/track_d/test_scm_augsynth_diagnostics.py) · [`tests/track_d/test_d5_inst_augsynth_ascm_002.py`](../../tests/track_d/test_d5_inst_augsynth_ascm_002.py)

**Inputs:** [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](../SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) · [`AUGSYNTH_ASCM_STRENGTHENING_001.md`](../AUGSYNTH_ASCM_STRENGTHENING_001.md) §5 D1–D11 · ASCM-002 harness/archive

---

## 1. Purpose

Implement **code-backed, descriptive** SCM/AugSynth diagnostics required by the threshold audit and future **D5-INST-AUGSYNTH-ASCM-003** OC. Diagnostics are **provisional** — numeric cutoffs remain for ASCM-003 calibration.

**This PR is not:** promotion, eligibility change, estimator/inference behavior change, TrustReport/F-DECISION/CalibrationSignal/MMM/LLM change, or threshold finalization.

---

## 2. Implemented diagnostics

| # | Diagnostic | JSON field(s) | Layer |
|---|------------|---------------|-------|
| 1 | SCM pretreatment RMSE | `scm_pre_rmse` | panel |
| 2 | Normalized SCM pretreatment error | `scm_pre_rmse_normalized` | panel |
| 3 | AugSynth pretreatment RMSE | `augsynth_pre_rmse` | panel |
| 4 | Normalized AugSynth pretreatment error | `augsynth_pre_rmse_normalized` | panel |
| 5 | AugSynth fit improvement over SCM | `fit_improvement_rmse` (absolute), `fit_improvement_relative` (D3 ratio) | panel |
| 6 | Donor weight concentration | `weight_herfindahl`, `max_weight` | panel |
| 7 | Effective donor count | `effective_donor_count` | panel |
| 8 | Donor hull / extrapolation stress | `hull_min_donor_z_distance` | panel |
| 9 | Treated-vs-donor scale bridge | `treated_pre_period_std`, `donor_weighted_pre_period_std`, `scale_bridge_ratio` | panel |
| 10 | Method point-estimate disagreement | `conflict_vs_a26.null_material_point_mismatch`, `null_point_effect_delta` | replicate |
| 11 | Sign disagreement | `conflict_vs_a26.null_sign_disagreement` | replicate |
| 12 | False-confidence flag | `false_confidence_flag` | instrument |
| 13 | Narrow-interval-with-poor-fit flag | `narrow_interval_poor_fit_flag` | instrument |
| — | Outcome-model descriptors (D8) | `outcome_model_alpha`, `outcome_model_coef_l2_norm`, `outcome_model_available` | panel |
| — | Sparsity / feasibility | `donor_sparsity_n_control`, `diagnostics_feasible`, `blocked_reason` | panel |

**Missing-weight / blocked runs:** weight and scale-bridge fields emit **`NaN`** with `diagnostics_feasible=0` and optional `blocked_reason` — no crash.

**D8 note:** Descriptive outcome-model fields from the fitted AugSynth leg only; **no alternate ridge-λ refit grid** in this PR (reserved for ASCM-003 sensitivity grid).

---

## 3. Integration

- ASCM-002 harness delegates panel diagnostics to `compute_panel_scm_augsynth_diagnostics`.
- Per-instrument flags via `compute_instrument_diagnostics`.
- Null-world disagreement via `compute_method_disagreement`.
- **Estimator and inference code unchanged** — diagnostics run only in validation harness fits.

---

## 4. Test evidence

| Test file | Coverage |
|-----------|----------|
| `test_scm_augsynth_diagnostics.py` | RMSE/normalization, weights, effective donor count, scale bridge, hull distance, disagreement, false-confidence, narrow-interval flags, field catalog |
| `test_d5_inst_augsynth_ascm_002.py` | Full panel field presence on fast worlds; instrument flags; conflict delta |

**Threshold labels:** not asserted — descriptive fields only.

---

## 5. Limitations

- Provisional flag rules (`false_confidence_flag`, `narrow_interval_poor_fit_flag`) use **fixed research thresholds** (not calibrated cutoffs).
- `fit_improvement_rmse` retains **absolute** delta for ASCM-002 archive compatibility; **`fit_improvement_relative`** is the threshold-audit D3 ratio.
- No full D8 ridge-λ sweep; no D9 placebo slice.
- Existing committed ASCM-002 JSON archive **not regenerated** in this PR (optional refresh deferred).

---

## 6. Guardrails (confirmed)

| Guardrail | Status |
|-----------|--------|
| No threshold finalization | ✅ |
| No promotion / demotion | ✅ |
| No eligibility change | ✅ |
| No estimator behavior change | ✅ |
| No inference behavior change | ✅ |
| No TrustReport / F-DECISION change | ✅ |
| No CalibrationSignal / MMM change | ✅ |
| No LLM integration | ✅ |

---

## 7. Next steps

1. **D5-INST-AUGSYNTH-ASCM-003** — larger n_mc; calibrate provisional threshold cutoffs; optional ridge sensitivity grid.
2. **AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001** — fidelity doc against harness output.
3. Optional: regenerate ASCM-002 archive slice with expanded diagnostic schema.

---

*D5-DIAG-SCM-AUGSYNTH-001 v1.0.0 — diagnostics module complete.*
