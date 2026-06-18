# D5 Trust TBRRidge BRB 001 — Report

**Artifact ID:** D5-TRUST-TBRRIDGE-BRB-001
**Verdict:** `tbrridge_brb_production_defect_confirmed`

> This artifact characterizes DCM-005 BRB. It does not authorize TrustReport. It does not perform DCM-005 eligibility reassessment. It does not modify production TBRRidge or BRB code unless a separate correction artifact is opened.

## 1. Executive summary

TBRRidge+BRB characterized on unit-panel geometry with level-scale truth contract. Verdict: `tbrridge_brb_production_defect_confirmed`. Production defect: `production_defect_confirmed`.

## 2. Prior DCM-005 BRB status

`restricted_requires_statistical_validation`; prior harness `INSUFFICIENT_EVIDENCE` with scale mismatch (level readout vs percent truth).

## 3. Scope

18 diagnostic worlds; effect-size sweep; block-length sweep; policy comparisons.

## 4. Non-goals

- No KFold/Placebo lanes
- No TrustReport promotion
- No production code changes in this artifact

## 5. TBRRidge estimator path

RidgeCV on pre-period-normalized controls; multi-treated unit panel supported.

## 6. BRB implementation

Model-conditional moving-block residual bootstrap; residuals from expanding-window OOS pre-period blocks.

## 7. Estimand

Post-window mean treated-minus-counterfactual residual effect (**level_mean_relative_percent_injection** level readout).

## 8. Geometry

Unit-panel single-cell; treated + control donors; not aggregate 2-row TBR.

## 9. Scale contract

Truth, point, bootstrap replicates, and intervals evaluated on **level mean shift** derived from percent injection.

## 10. Residual construction

Expanding-window OOS pre-period forecast errors; centered by default (`center_residuals=True`).

## 11. Block resampling

Contiguous moving blocks from residual pool; serial dependence preserved within blocks.

## 12. Worlds

clean_null, clean_positive_effect, clean_negative_effect, weak_signal, strong_signal, serial_correlation, high_serial_correlation, heteroskedastic_residuals, autocorrelated_shocks, regime_shift, post_treatment_shock, poor_pre_fit, outlier_period, small_pre_period, small_donor_support, ridge_dominant, low_noise, placebo_null

## 13. Effect-size sweep

0.0, 0.03, 0.08, 0.12, -0.05

## 14. Block-length sweep

2, 3, 7

## 15. Run counts/runtime

Total 248; ok 248; runtime 8.3815s.

## 16. Point-estimate behavior

Clean positive bias: 0.9240; RMSE: 1.7098.

## 17. Bootstrap centering

Mean bootstrap center gap: -292.5645.

## 18. Variance calibration

Mean variance ratio: 11.0076; mean width: 14.0595.

## 19. Null coverage

clean_null: 1.0000.

## 20. Positive coverage

clean_positive_effect: 0.1250.

## 21. Negative coverage

clean_negative_effect: 0.9167.

## 22. Type-I error

clean_null type-I: 0.0000.

## 23. Serial-dependence findings

{'clean_iid': {'null_coverage': 1.0, 'type_i_error': 0.0, 'positive_coverage': 0.24603174603174602, 'negative_coverage': 0.9, 'n_null': 30, 'n_positive': 126, 'n_negative': 20}, 'serial_correlation': {'null_coverage': None, 'type_i_error': None, 'positive_coverage': 0.0, 'negative_coverage': None, 'n_null': 0, 'n_positive': 12, 'n_negative': 0}, 'high_serial_correlation': {'null_coverage': None, 'type_i_error': None, 'positive_coverage': 0.08333333333333333, 'negative_coverage': None, 'n_null': 

## 24. Heteroskedasticity findings

heteroskedastic world positive coverage: 1.0000.

## 25. Pre-fit findings

{'mean_prefit_rmse_clean': None, 'mean_prefit_rmse_poor_pre_fit': None}

## 26. Ridge-regularization findings

{'mean_ridge_alpha': 0.6431209677419355, 'ridge_dominant_mean_alpha': 0.6175}

## 27. Worst-world behavior

post_treatment_shock null coverage: 1.0000.

## 28. Policy comparisons

A current BRB; B uncentered diagnostic; C block-restricted; D serial-supported; E prefit-gated; F diagnostic-only; G blocked.

## 29. Root-cause determination

{'dominant_tags': {'interval_miscentering': 248, 'variance_overestimation': 244, 'point_bias': 53, 'variance_underestimation': 1}, 'historical_scale_mismatch_note': 'D5-STAT-TBRRIDGE-INF-001 compared level readout to percent true_effect; this artifact uses level_mean_relative truth.', 'harness_assignment_note': 'D5-STAT-TBRRIDGE-INF-001 groups.values() flattening defect avoided via explicit test_0 assignment in this artifact.'}

## 30. Production-defect decision

`production_defect_confirmed` — Point estimate acceptable on clean worlds but interval miscentering/coverage failure persists.

## 31. Semantic classification

`tbrridge_brb_production_defect_confirmed` — BRB reflects residual/forecast uncertainty under stable pre-period dynamics.

## 32. TrustReport implications

DCM-005 BRB production defect addressed in **`TBRRIDGE_BRB_INTERVAL_CORRECTION_001`**; eligibility reassessment deferred until KFold/Placebo lanes complete.

## 33. Authorization status

**Blocked** — trust_report_authorized=false.

## 34. Remaining limitations

Characterizes DCM-005 BRB only; KFold/Placebo out of scope.; Level-scale truth contract; percent injection converted to level mean shift.; Does not authorize TrustReport or modify production TBRRidge/BRB.; Policy B/C comparisons are diagnostic; no production changes applied.

## 35. Governance verdict

**`tbrridge_brb_production_defect_confirmed`**

## Residual Issues and Handoff

**Resolved in this artifact:** none

**New investigations opened:**
- INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001

**Existing investigations updated:** none

**Deferred issues:** none

**Explicit exclusions:**
- KFold and Placebo characterization
- DCM-005 eligibility reassessment
- Production TBRRidge/BRB code changes

**Revisit trigger:** Upon opening TBRRIDGE-BRB-INTERVAL-CORRECTION-001 production correction

**Required decision checkpoint:** DCM-005 eligibility reassessment (after KFold/Placebo lanes)

**Next artifact:** TBRRIDGE-BRB-INTERVAL-CORRECTION-001

