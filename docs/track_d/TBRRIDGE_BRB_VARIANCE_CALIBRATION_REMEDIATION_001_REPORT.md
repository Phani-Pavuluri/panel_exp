# TBRRIDGE-BRB-VARIANCE-CALIBRATION-REMEDIATION-001 Report

## 1. Executive summary

This artifact remediates or adjudicates the TBRRidge + BRB variance/null-calibration issue.
It does not authorize TrustReport.
It does not perform the full TrustReport eligibility reassessment.
Any successful remediation requires a subsequent reassessment before promotion.

**Verdict:** `tbrridge_brb_variance_remediation_candidate_only`
**Selected policy:** `larger_block_length_brb`
**Production variance policy added:** `False`

## 2. Prior evidence state

TBRRIDGE_BRB_INTERVAL_CORRECTION_001 fixed centering; null type-I and positive coverage remained unacceptable.

## 3. Scope

TBRRidge + BlockResidualBootstrap across 22 diagnostic worlds and 7 implemented candidate policies.

## 4. Non-goals

No TrustReport authorization; no full matrix reassessment; no SCM/DID/KFold/Placebo changes.

## 5. Root-cause questions

[
  {
    "question": "Is undercoverage caused by bootstrap replicate variance being too small?",
    "finding": "Partially on mean-effect scale: calibration_ratio_mean_effect often < 1 (baseline mean 0.8820238084299761); cumulative variance_ratio is inflated by scale mismatch.",
    "tags": [
      "mean_replicate_underestimation",
      "cumulative_diagnostic_mismatch"
    ]
  },
  {
    "question": "Is null type-I high because intervals are too narrow?",
    "finding": "Partially: type-I 0.5 with null coverage 0.5; null_calibrated widening helps marginally but does not reach gates.",
    "tags": [
      "interval_width",
      "null_type_i"
    ]
  },
  {
    "question": "Is the interval centered correctly after the prior correction?",
    "finding": "Yes: mean |bootstrap_center_minus_point| \u2248 0.22939460717250748 (prior gap 0.005962036865426644).",
    "tags": [
      "centering_resolved"
    ]
  },
  {
    "question": "Does ridge shrinkage bias interact with bootstrap variance?",
    "finding": "Yes: null worlds show material point bias (mean bias 2.679097659155361); conditional BRB cannot correct estimator bias.",
    "tags": [
      "point_bias",
      "ridge_shrinkage"
    ]
  },
  {
    "question": "Does BRB condition on fitted ridge coefficients correctly?",
    "finding": "Conditional resampling (no refit) ignores coefficient-estimation uncertainty.",
    "tags": [
      "conditional_bootstrap",
      "coefficient_uncertainty_omitted"
    ]
  }
]

## 6. Candidate remediation policies

{
  "baseline_corrected_brb": {
    "implemented": true,
    "variance_calibration_policy": "none",
    "bootstrap_type": "block",
    "block_length": 3,
    "description": "Centered-deviation BRB after TBRRIDGE_BRB_INTERVAL_CORRECTION_001"
  },
  "variance_scaled_brb": {
    "implemented": true,
    "variance_calibration_policy": "residual_scaled",
    "bootstrap_type": "block",
    "block_length": 3,
    "description": "Residual-pool scaled deviation CI"
  },
  "studentized_brb": {
    "implemented": true,
    "variance_calibration_policy": "studentized",
    "bootstrap_type": "block",
    "block_length": 3,
    "description": "Bootstrap-t pivot on mean-effect replicates"
  },
  "wild_block_brb": {
    "implemented": true,
    "variance_calibration_policy": "none",
    "bootstrap_type": "wild",
    "block_length": 3,
    "description": "Wild (Rademacher) residual bootstrap"
  },
  "larger_block_length_brb": {
    "implemented": true,
    "variance_calibration_policy": "none",
    "bootstrap_type": "block",
    "block_length": 7,
    "description": "Longer moving blocks (length 7)"
  },
  "adaptive_block_length_brb": {
    "implemented": true,
    "variance_calibration_policy": "none",
    "bootstrap_type": "block",
    "block_length": null,
    "description": "Adaptive T^(1/3) block length"
  },
  "null_calibrated_brb": {
    "implemented": true,
    "variance_calibration_policy": "null_calibrated",
    "bootstrap_type": "block",
    "block_length": 3,
    "description": "Minimum half-width from residual-pool null calibration"
  },
  "restricted_worlds_only_brb": {
    "implemented": false,
    "reason": "evaluation filter only; not a production policy"
  }
}

## 7. Worlds

clean_null, weak_signal, clean_positive_effect, strong_signal, clean_negative_effect, serial_correlation, high_serial_correlation, heteroskedastic_residuals, heavy_tailed_noise, regime_shift, post_treatment_shock, donor_contamination, poor_pre_fit, low_noise, small_pre_period, long_pre_period, short_post_period, long_post_period, small_donor_support, ridge_dominant, low_ridge_shrinkage, outlier_period

## 10. Baseline corrected-BRB behavior

Null type-I: 0.5; null coverage: 0.5; positive coverage: 0.5789473684210527; center gap: 0.22939460717250748.

## 11. Candidate comparison

{
  "baseline_corrected_brb": {
    "gate_pass_count": 2,
    "all_gates_pass": false,
    "type_i_under_null": 0.5,
    "null_coverage": 0.5,
    "positive_coverage": 0.5789473684210527,
    "calibration_ratio": 0.8820238084299761
  },
  "variance_scaled_brb": {
    "gate_pass_count": 2,
    "all_gates_pass": false,
    "type_i_under_null": 0.6666666666666666,
    "null_coverage": 0.3333333333333333,
    "positive_coverage": 0.5964912280701754,
    "calibration_ratio": 0.9940474960895067
  },
  "studentized_brb": {
    "gate_pass_count": 2,
    "all_gates_pass": false,
    "type_i_under_null": 0.6666666666666666,
    "null_coverage": 0.3333333333333333,
    "positive_coverage": 0.5789473684210527,
    "calibration_ratio": 1.0385754279455393
  },
  "wild_block_brb": {
    "gate_pass_count": 2,
    "all_gates_pass": false,
    "type_i_under_null": 1.0,
    "null_coverage": 0.0,
    "positive_coverage": 0.43859649122807015,
    "calibration_ratio": 0.49610675968795676
  },
  "larger_block_length_brb": {
    "gate_pass_count": 3,
    "all_gates_pass": false,
    "type_i_under_null": 0.5,
    "null_coverage": 0.5,
    "positive_coverage": 0.543859649122807,
    "calibration_ratio": 1.017787532819671
  },
  "adaptive_block_length_brb": {
    "gate_pass_count": 2,
    "all_gates_pass": false,
    "type_i_under_null": 0.8333333333333334,
    "null_coverage": 0.16666666666666666,
    "positive_coverage": 0.49122807017543857,
    "calibration_ratio": 0.9217951631941322
  },
  "null_calibrated_brb": {
    "gate_pass_count": 2,
    "all_gates_pass": false,
    "type_i_under_null": 0.5,
    "null_coverage": 0.5,
    "positive_coverage": 0.7192982456140351,
    "calibration_ratio": 0.8297865569358582
  }
}

## 12. Null calibration

{
  "baseline_corrected_brb": 0.5,
  "variance_scaled_brb": 0.6666666666666666,
  "studentized_brb": 0.6666666666666666,
  "wild_block_brb": 1.0,
  "larger_block_length_brb": 0.5,
  "adaptive_block_length_brb": 0.8333333333333334,
  "null_calibrated_brb": 0.5
}

## 13. Positive/negative coverage

{
  "baseline_corrected_brb": {
    "null": 0.5,
    "positive": 0.5789473684210527,
    "negative": 0.0
  },
  "variance_scaled_brb": {
    "null": 0.3333333333333333,
    "positive": 0.5964912280701754,
    "negative": 0.6666666666666666
  },
  "studentized_brb": {
    "null": 0.3333333333333333,
    "positive": 0.5789473684210527,
    "negative": 0.3333333333333333
  },
  "wild_block_brb": {
    "null": 0.0,
    "positive": 0.43859649122807015,
    "negative": 0.6666666666666666
  },
  "larger_block_length_brb": {
    "null": 0.5,
    "positive": 0.543859649122807,
    "negative": 1.0
  },
  "adaptive_block_length_brb": {
    "null": 0.16666666666666666,
    "positive": 0.49122807017543857,
    "negative": 0.6666666666666666
  },
  "null_calibrated_brb": {
    "null": 0.5,
    "positive": 0.7192982456140351,
    "negative": 0.6666666666666666
  }
}

## 16. Calibration ratio analysis

{
  "baseline_corrected_brb": 0.8820238084299761,
  "variance_scaled_brb": 0.9940474960895067,
  "studentized_brb": 1.0385754279455393,
  "wild_block_brb": 0.49610675968795676,
  "larger_block_length_brb": 1.017787532819671,
  "adaptive_block_length_brb": 0.9217951631941322,
  "null_calibrated_brb": 0.8297865569358582
}

## 21. Selected policy

`larger_block_length_brb` — gate pass count 3; all gates pass: False.

## 22. Production changes

Added optional `variance_calibration_policy` (`residual_scaled`, `studentized`, `null_calibrated`) to `block_residual_bootstrap.py`; default `none` preserves corrected baseline.

## 23. Pass/fail gate results

{
  "gates": {
    "null_type_i": false,
    "null_coverage_zero": false,
    "truth_coverage_clean": true,
    "interval_center_gap": true,
    "failure_rate": true
  },
  "all_pass": false,
  "pass_count": 3,
  "truth_coverage_aggregate": 0.8888888888888888
}

## 25. Semantic classification

`remediation_candidate_pending_reassessment`

## 27. Authorization status

{
  "trust_report_authorized": false,
  "trust_report_ready": false,
  "trust_report_authorized_count": 0,
  "candidate_for_reassessment": true
}

## 28. Investigation lifecycle update

{
  "investigation_id": "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001",
  "terminal_decision": "REMEDIATION_CANDIDATE_PENDING_REASSESSMENT"
}

## 30. Governance verdict

`tbrridge_brb_variance_remediation_candidate_only`

## Residual Issues and Handoff

**Resolved in this artifact:**
- INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001

**New investigations opened:** none

**Existing investigations updated:**
- INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001

**Deferred issues:** none

**Explicit exclusions:** none

**Revisit trigger:** Post-remediation reassessment if candidate

**Required decision checkpoint:** DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001

**Next artifact:** DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001


## Residual Issues and Handoff

Next artifact: `DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001`
