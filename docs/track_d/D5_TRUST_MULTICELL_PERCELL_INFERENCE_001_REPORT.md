# D5-TRUST-MULTICELL-PERCELL-INFERENCE-001 Report

## 1. Executive summary

This artifact evaluates per-cell inference for multi-cell designs.
It does not validate pooled multi-cell causal inference.
It does not authorize TrustReport.
It does not perform the full TrustReport eligibility reassessment.

**Verdict:** `multicell_percell_multiplicity_unresolved`
**Aggregate status:** `INSUFFICIENT_EVIDENCE`

## 2. Prior DCM-006 status

DCM-006 was ELIGIBLE_WITH_RESTRICTIONS (design-only); per-cell interval coverage and shared-control dependence unresolved.

## 3. Scope

SCM + UnitJackknife per cell across geometry variants and synthetic worlds.

## 4. Non-goals

No pooled multi-cell causal readout; no TrustReport authorization; no production algorithm changes.

## 5. Multi-cell geometry

Distinguishes multiple test cells from multiple treated units within one cell; per-cell readout only.

## 6. Per-cell estimands

Canonical scale: `level_mean_relative_percent_injection`.

## 7. Cell identity contract

Cell identity preserved; other test units excluded from each cell panel.

## 8. Control-pool policies

Shared, disjoint, and partial-overlap donor constructions evaluated.

## 9. Shared-control structure

{
  "shared_geometry": {
    "n_cell_results": 144,
    "n_ok": 144,
    "coverage": 0.9305555555555556,
    "type_i_error": 0.11842105263157894,
    "mean_bias": 0.39940784078566755,
    "mean_interval_width": 6.015366946801957
  },
  "disjoint_geometry": {
    "n_cell_results": 168,
    "n_ok": 168,
    "coverage": 0.9226190476190477,
    "type_i_error": 0.10714285714285714,
    "mean_bias": 0.2911129268666225,
    "mean_interval_width": 6.966066761310362
  },
  "cross_cell_correlation": 0.900990099009901
}

## 10. Inference path

Primary: `MCELL-PERCELL-SCM-JK`.

## 11. Scale contract

Level mean relative percent injection; intervals on same level scale.

## 12. Worlds

all_cell_null, one_cell_positive_others_null, two_cell_positive, mixed_positive_negative, weak_effects, strong_effects, serial_correlation, high_serial_correlation, heteroskedasticity, poor_pre_fit_one_cell, poor_pre_fit_all_cells, donor_contamination_one_cell, shared_control_shock, cell_specific_post_shock, unequal_cell_sizes, small_donor_pool, heavy_control_reuse, overlapping_timing

## 13. Effect patterns

[[0.0, 0.0], [0.08, 0.0], [0.08, 0.08], [0.08, -0.05], [0.03, 0.03], [0.12, 0.0], [0.08, 0.0, 0.0], [0.08, 0.08, 0.0], [0.08, -0.05, 0.03]]

## 14. Geometry variants

[
  {
    "geometry_id": "two_cells_disjoint_controls",
    "n_cells": 2,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "unrestricted",
    "geometry_supported": true
  },
  {
    "geometry_id": "two_cells_shared_controls",
    "n_cells": 2,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "unrestricted",
    "geometry_supported": true
  },
  {
    "geometry_id": "three_cells_shared_controls",
    "n_cells": 3,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "unrestricted",
    "geometry_supported": true
  },
  {
    "geometry_id": "unequal_cell_sizes",
    "n_cells": 2,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "unrestricted",
    "geometry_supported": true
  },
  {
    "geometry_id": "small_cell",
    "n_cells": 2,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "unrestricted",
    "geometry_supported": true
  },
  {
    "geometry_id": "large_cell",
    "n_cells": 2,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "unrestricted",
    "geometry_supported": true
  },
  {
    "geometry_id": "imbalanced_control_reuse",
    "n_cells": 2,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "heavy_reuse",
    "geometry_supported": true
  },
  {
    "geometry_id": "cell_specific_donor_pools",
    "n_cells": 2,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "unrestricted",
    "geometry_supported": true
  },
  {
    "geometry_id": "common_control_pool",
    "n_cells": 2,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "unrestricted",
    "geometry_supported": true
  },
  {
    "geometry_id": "partially_overlapping_controls",
    "n_cells": 2,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "unrestricted",
    "geometry_supported": true
  },
  {
    "geometry_id": "pooled_multi_cell_negative_control",
    "n_cells": 2,
    "shared_control_policy": "greedy_match_common_pool",
    "control_reuse_policy": "unrestricted",
    "geometry_supported": false
  }
]

## 15. Run counts/runtime

{
  "total_runs": 810,
  "successful_runs": 810,
  "failed_runs": 0,
  "cell_level_results": 1554,
  "runtime_seconds": 59.79
}

## 16. Cell-level point behavior

Mean bias by cell: {"test_0": -0.049592641309445976, "test_1": 0.8881197068386488, "test_2": -0.08775901413314799}

## 17. Cell-level interval behavior

Coverage by geometry: {
  "two_cells_disjoint_controls": {
    "n_cell_results": 168,
    "n_ok": 168,
    "coverage": 0.9226190476190477,
    "type_i_error": 0.10714285714285714,
    "mean_bias": 0.2911129268666225,
    "mean_interval_width": 6.966066761310362
  },
  "two_cells_shared_controls": {
    "n_cell_results": 144,
    "n_ok": 144,
    "coverage": 0.9305555555555556,
    "type_i_error": 0.11842105263157894,
    "mean_bias": 0.39940784078566755,
    "mean_interval_width": 6.015366946801957
  },
  "three_cells_shared_controls": {
    "n_cell_results": 234,
    "n_ok": 234,
    "coverage": 0.9444444444444444,
    "type_i_error": 0.05844155844155844,
    "mean_bias": 0.2849559335061485,
    "mean_interval_width": 6.020186465218476
  },
  "unequal_cell_sizes": {
    "n_cell_results": 144,
    "n_ok": 144,
    "coverage": 0.9444444444444444,
    "type_i_error": 0.06578947368421052,
    "mean_bias": 0.5430747573773681,
    "mean_interval_width": 6.638203883885081
  },
  "small_cell": {
    "n_cell_results": 144,
    "n_ok": 144,
    "coverage": 0.9166666666666666,
    "type_i_error": 0.11842105263157894,
    "mean_bias": 0.3473751579013634,
    "mean_interval_width": 6.842117424360633
  },
  "large_cell": {
    "n_cell_results": 144,
    "n_ok": 144,
    "coverage": 0.9305555555555556,
    "type_i_error": 0.09210526315789473,
    "mean_bias": 0.25480111474417005,
    "mean_interval_width": 5.721492279480551
  },
  "imbalanced_control_reuse": {
    "n_cell_results": 144,
    "n_ok": 144,
    "coverage": 0.9305555555555556,
    "type_i_error": 0.11842105263157894,
    "mean_bias": 0.5952168219402523,
    "mean_interval_width": 6.380536869601891
  },
  "cell_specific_donor_pools": {
    "n_cell_results": 144,
    "n_ok": 144,
    "coverage": 0.9027777777777778,
    "type_i_error": 0.15789473684210525,
    "mean_bias": 0.5744937676727611,
    "mean_interval_width": 7.13756912479442
  },
  "common_control_pool": {
    "n_cell_results": 144,
    "n_ok": 144,
    "coverage": 0.92361111111111

## 18. Per-cell null type-I

{
  "test_0": 0.054455445544554455,
  "test_1": 0.125,
  "test_2": 0.039473684210526314
}

## 19. Familywise type-I

0.2722772277227723

## 20. Per-cell coverage

{
  "test_0": {
    "n_cell_results": 738,
    "n_ok": 738,
    "coverage": 0.9579945799457995,
    "type_i_error": 0.054455445544554455,
    "mean_bias": -0.049592641309445976,
    "mean_interval_width": 6.418629563564775
  },
  "test_1": {
    "n_cell_results": 738,
    "n_ok": 738,
    "coverage": 0.8902439024390244,
    "type_i_error": 0.125,
    "mean_bias": 0.8881197068386488,
    "mean_interval_width": 6.435378902747165
  },
  "test_2": {
    "n_cell_results": 78,
    "n_ok": 78,
    "coverage": 0.9615384615384616,
    "type_i_error": 0.039473684210526314,
    "mean_bias": -0.08775901413314799,
    "mean_interval_width": 6.048682524609023
  }
}

## 21. Simultaneous coverage

0.8563685636856369

## 22. Multiplicity findings

**Unadjusted familywise null type-I:** 0.2722772277227723

Bonferroni/Holm proxy comparison was not a valid calibration test because the current SCM+JK path does not expose compatible per-cell p-values or adjusted confidence-level interval reconstruction. Multiplicity remains unresolved; equal FWER values across unadjusted and proxy-adjusted labels do not establish that Bonferroni or Holm are ineffective.

{
  "unadjusted_familywise_type_i": 0.2722772277227723,
  "bonferroni_proxy": null,
  "holm_proxy": null,
  "proxy_comparison_valid": false,
  "calibration_audit": {
    "bonferroni_threshold_adjusted": false,
    "holm_threshold_adjusted": false,
    "per_cell_p_values_available": false,
    "p_value_source": "none \u2014 SCM+UnitJackknife exposes interval bounds only",
    "rejection_proxy": "interval_excludes_zero (0 in [lower, upper])",
    "adjusted_intervals_reconstructed": false,
    "familywise_from_adjusted_decisions": false,
    "familywise_metric_valid": "unadjusted_interval_excludes_zero_any_cell_only",
    "shared_control_handling": "consistent \u2014 all multiplicity labels reuse the same underlying per-cell JK intervals; shared-control dependence affects intervals but was not modeled separately per policy",
    "proxy_comparison_valid": false,
    "disclaimer": "Bonferroni/Holm proxy comparison was not a valid calibration test because the current SCM+JK path does not expose compatible per-cell p-values or adjusted confidence-level interval reconstruction. Multiplicity remains unresolved; equal FWER values across unadjusted and proxy-adjusted labels do not establish that Bonferroni or Holm are ineffective."
  },
  "disclaimer": "Bonferroni/Holm proxy comparison was not a valid calibration test because the current SCM+JK path does not expose compatible per-cell p-values or adjusted confidence-level interval reconstruction. Multiplicity remains unresolved; equal FWER values across unadjusted and proxy-adjusted labels do not establish that Bonferroni or Holm are ineffective."
}

## 23. Shared-control dependence

{
  "mean_cross_cell_estimate_correlation": 0.900990099009901,
  "familywise_null_fp_rate": 0.2722772277227723,
  "n_null_runs": 214
}

## 24. Disjoint-control findings

{
  "n_cell_results": 168,
  "n_ok": 168,
  "coverage": 0.9226190476190477,
  "type_i_error": 0.10714285714285714,
  "mean_bias": 0.2911129268666225,
  "mean_interval_width": 6.966066761310362
}

## 25. Small-cell findings

{
  "n_cell_results": 144,
  "n_ok": 144,
  "coverage": 0.9166666666666666,
  "type_i_error": 0.11842105263157894,
  "mean_bias": 0.3473751579013634,
  "mean_interval_width": 6.842117424360633
}

## 26. Poor-pre-fit findings

See worlds poor_pre_fit_one_cell and poor_pre_fit_all_cells.

## 27. Donor-support findings

See small_donor_pool and heavy_control_reuse worlds.

## 28. Pooled readout block verification

{
  "attempted": 810,
  "blocked": 810,
  "effect_emitted": 0,
  "interval_emitted": 0,
  "all_blocked": true
}

## 29. Policy comparisons

Policy A (unadjusted per-cell) and E/F (geometry subsets) are calibrated. Policies B/C/D (Bonferroni, Holm, max-stat) were **not** valid calibration tests in this artifact — see §22.

See summary `policy_comparisons`.

## 30. Root-cause determination

Shared-control dependence and multiplicity are structural; not code defects.

## 31. Production-defect decision

{
  "decision": "geometry_or_semantic_limitation",
  "rationale": "shared-control cross-cell dependence and multiplicity are structural; not isolated implementation defects"
}

## 32. Semantic classification

{
  "verdict": "multicell_percell_multiplicity_unresolved",
  "aggregate_status": "INSUFFICIENT_EVIDENCE",
  "geometry_decisions": {
    "disjoint_controls": "per_cell_disjoint_controls_only",
    "shared_controls": "per_cell_with_multiplicity_warning",
    "partial_overlap": "per_cell_restricted",
    "small_cell": "per_cell_restricted",
    "pooled_multi_cell": "not_supported"
  },
  "supported_roles": [
    "per_cell_diagnostic",
    "per_cell_restricted_interval"
  ],
  "unsupported_roles": [
    "pooled_multi_cell_causal",
    "trust_report",
    "simultaneous_multi_cell_decision"
  ]
}

## 33. TrustReport implications

{
  "dcm_006": "per_cell_restricted_no_trustreport_authorization",
  "prior_status": "ELIGIBLE_WITH_RESTRICTIONS_DESIGN_ONLY",
  "reassessment_required": true,
  "full_reassessment_deferred": true
}

## 34. Authorization status

{
  "trust_report_authorized": false,
  "trust_report_ready": false,
  "trust_report_authorized_count": 0
}

## 35. Investigation lifecycle update

Consumed `INV-MULTICELL-PERCELL-INFERENCE-001` → RESOLVED (PER_CELL_RESTRICTED).
Opened `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001`, `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001` as DEFERRED_WITH_TRIGGER.

## 36. Remaining limitations

Evaluates per-cell inference for multi-cell designs; does not validate pooled multi-cell causal inference.; Does not authorize TrustReport.; Does not perform the full TrustReport eligibility reassessment.; SCM+UnitJackknife primary path only; AugSynth/TBR/DID per-cell paths not expanded.; Bonferroni/Holm proxy comparison was not a valid calibration test (no per-cell p-values or adjusted intervals on SCM+JK path).; Multiplicity remains unresolved; equal FWER across proxy labels does not imply Bonferroni/Holm ineffectiveness.; Shared-control dependence is structural; marginal per-cell coverage does not imply valid multi-cell decisioning.

## 37. Governance verdict

**`multicell_percell_multiplicity_unresolved`**

## Residual Issues and Handoff

**Resolved in this artifact:**
- INV-MULTICELL-PERCELL-INFERENCE-001

**New investigations opened:**
- INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001
- INV-MULTICELL-MULTIPLICITY-CALIBRATION-001

**Existing investigations updated:**
- INV-MULTICELL-PERCELL-INFERENCE-001 → RESOLVED (PER_CELL_RESTRICTED)

**Deferred issues:**
- INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001
- INV-MULTICELL-MULTIPLICITY-CALIBRATION-001

**Explicit exclusions:**
- FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT

**Revisit trigger:** After stratified SCM+JK lane and multiplicity remediation

**Required decision checkpoint:** FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT DCM-006 row

**Next artifact:** D5-TRUST-STRATIFIED-SCM-JK-001

