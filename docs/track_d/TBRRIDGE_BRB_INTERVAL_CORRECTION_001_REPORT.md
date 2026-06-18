# TBRRidge BRB Interval Correction 001 — Report

**Artifact ID:** TBRRIDGE-BRB-INTERVAL-CORRECTION-001
**Verdict:** `tbrridge_brb_centering_corrected_variance_issue_remains`

> This artifact corrects TBRRidge BRB interval construction. It does not perform DCM-005 eligibility reassessment. It does not authorize TrustReport. It does not validate KFold or Placebo inference.

## 1. Executive summary

Aligned BRB bootstrap replicates and intervals to mean post-window effect estimand via centered-deviation percentile construction.

## 5. TBRRidge point estimand

`post_window_mean_treated_minus_counterfactual_level`

## 6. BRB replicate estimand before correction

`cumulative_sum_post_window_effect_path`

## 7. Root cause

Cumulative-sum bootstrap replicates (~n_periods × n_units × point) vs mean point readout.

## 10. Selected interval construction

`centered_deviation_percentile_mean_effect`

## 16. Before centering

Gap: -292.56454763226145

## 17. After centering

Gap: 0.005962036865426644

## 19. Positive coverage

Before: 0.21333333333333335 → After: 0.5066666666666667

## 18. Null coverage

Before: 1.0 → After: 0.40476190476190477

## 33. Authorization status

Blocked.

## 35. Governance verdict

`tbrridge_brb_centering_corrected_variance_issue_remains`

## Residual Issues and Handoff

**Resolved in this artifact:**
- INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001

**New investigations opened:**
- INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001

**Existing investigations updated:**
- INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001 → OPEN in [`OPEN_INVESTIGATIONS_001.json`](../governance/OPEN_INVESTIGATIONS_001.json)

**Deferred issues:** none

**Explicit exclusions:**
- KFold/Placebo validation
- DCM-005 eligibility reassessment

**Revisit trigger:** After KFold and Placebo characterization, before DCM-005 eligibility reassessment

**Required decision checkpoint:** DCM-005 eligibility reassessment must consume INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001

**Next artifact:** D5-TRUST-TBRRIDGE-KFOLD-001

