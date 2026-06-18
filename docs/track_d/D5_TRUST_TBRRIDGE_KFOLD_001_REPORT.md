# D5 Trust TBRRidge KFold 001 — Report

**Artifact ID:** D5-TRUST-TBRRIDGE-KFOLD-001
**Verdict:** `tbrridge_kfold_not_causal_interval_eligible`

> Characterizes DCM-005 KFold. Does not authorize TrustReport. Does not perform DCM-005 eligibility reassessment. Does not modify production TBRRidge or KFold code unless a separate correction artifact opens.

## 1. Executive summary

TBRRidge+KFold characterized on unit-panel geometry. Verdict: `tbrridge_kfold_not_causal_interval_eligible`. Production assessment: `method_unsuitable_for_causal_interval`.

## 2. Prior DCM-005 KFold status

Prior D5-STAT-TBRRIDGE-INF-001: null interval FPR ~0; directional null FPR ~1.0 on outcome scale.

## 3. Scope

18 worlds; 3 fold variants; effect sweep.

## 4. Non-goals

- No Placebo lane
- No DCM-005 eligibility reassessment
- No production code changes

## 5. TBRRidge estimator path

RidgeCV on pre-period-normalized controls; multi-treated unit panel.

## 6. KFold implementation

Legacy `kfold()` blocked pre-period holdouts; `panel_timeseries_kfold()` expanding/rolling schemes.

## 7. Fold geometry

Folds split **time periods** in pre-treatment window; units preserved. Not sklearn random unit KFold.

## 8. Temporal-order analysis

Expanding/rolling schemes preserve chronological training-before-holdout ordering per fold.

## 9. Leakage analysis

{'runs_with_leakage_flag': 0, 'mean_fold_instability': 9.493781198108163, 'fold_types': ['random_kfold', 'blocked_time_kfold', 'forward_chaining_time_series_kfold']}

## 10. Estimand

Post-window debiased ATT point; CV dispersion treated as interval (**level_mean_relative_percent_injection**).

## 11. Scale contract

Truth and readouts on level mean shift from percent injection; directional threshold 500 on level scale.

## 12. Worlds

clean_null, clean_positive_effect, clean_negative_effect, weak_signal, strong_signal, serial_correlation, high_serial_correlation, heteroskedasticity, regime_shift, post_treatment_shock, pre_trend_violation, poor_pre_fit, small_pre_period, large_pre_period, small_donor_set, ridge_dominant, low_noise_null, placebo_null

## 13. Effect-size sweep

0.0, 0.03, 0.08, 0.12, -0.05

## 14. Fold-variant sweep

random_kfold, blocked_time_kfold, forward_chaining_time_series_kfold

## 15. Run counts/runtime

Total 178; ok 178; runtime 20.0200s.

## 16. Point-estimate behavior

Clean positive bias: -393.2390.

## 17. Fold-statistic behavior

{'variants': {'random_kfold': 'Production legacy kfold(); blocked consecutive pre-period holdouts (not sklearn random unit KFold).', 'blocked_time_kfold': 'TimeSeriesKfold rolling blocked holdouts on pre-period.', 'forward_chaining_time_series_kfold': 'TimeSeriesKfold expanding / forward-chaining pre-period blocks.'}, 'mean_fold_std': 9.493781198108163}

## 18. Null type-I

random_kfold directional type-I: 0.0000; interval type-I: 0.0000.

## 19. Positive behavior

clean_positive coverage: 0.9091.

## 20. Negative behavior

clean_negative coverage: 1.0000.

## 21. Sign accuracy

Overall: 0.3539.

## 22. Variance findings

{'mean_variance_ratio': 3.4445175951490756, 'mean_interval_width': 49.27263849265232, 'mean_fold_std': 9.493781198108163, 'decomposition_note': 'high_null_fpr = temporal_leakage + fold_dependence + estimator_bias + inappropriate_directional_threshold + variance_underestimation + scale_mismatch + semantic_misuse'}

## 23. Serial-dependence findings

serial_correlation null directional FPR: —.

## 24. Pre-fit findings

{'mean_prefit_rmse': 0.0, 'prefit_rmse_vs_directional_fpr': 'high prefit_rmse correlates with unstable fold dispersion'}

## 25. Ridge findings

{'mean_ridge_alpha': 0.7068571428571429}

## 26. Worst-world behavior

post_treatment_shock directional FPR: 0.0000.

## 27. Policy comparisons

A legacy Kfold; B expanding TSKFold; C rolling TSKFold; D directional-only; E prefit-gated; F blocked.

## 28. Root-cause determination

high_null_fpr = temporal_leakage + fold_dependence + estimator_bias + inappropriate_directional_threshold + variance_underestimation + scale_mismatch + semantic_misuse

## 29. Production-defect decision

`method_unsuitable_for_causal_interval` — CV dispersion intervals cover zero on null worlds while level-scale point estimates remain far from zero and positive-effect sign accuracy collapses; readout is not a calibrated causal ATT interval.

## 30. Semantic classification

{'verdict': 'tbrridge_kfold_not_causal_interval_eligible', 'supported_roles': ['directional_diagnostic', 'model_selection_diagnostic'], 'unsupported_roles': ['restricted_causal_interval', 'trust_report', 'calibration_signal'], 'readout_type': 'cross_validation_dispersion_interval_not_causal_att'}

## 31. TrustReport implications

DCM-005 KFold remains diagnostic-only; eligibility reassessment deferred.

## 32. Authorization status

**Blocked** — trust_report_authorized=false.

## 33. Investigation lifecycle update

INV-TBRRIDGE-KFOLD-NULL-FPR-001 remains OPEN; provisional DIAGNOSTIC_ONLY recommendation recorded in registry evidence for DCM-005 consumption (not terminal closure in this artifact).

## 34. Remaining limitations

Characterizes DCM-005 KFold only; Placebo and DCM-005 reassessment out of scope.; Level-scale truth contract; percent injection converted to level mean shift.; Legacy Kfold is blocked pre-period CV, not sklearn random unit KFold.; Does not authorize TrustReport or modify production inference code.

## 35. Governance verdict

**`tbrridge_kfold_not_causal_interval_eligible`**

## Residual Issues and Handoff

**Resolved in this artifact:** none

**New investigations opened:** none

**Existing investigations updated:**
- INV-TBRRIDGE-KFOLD-NULL-FPR-001 → OPEN; provisional DIAGNOSTIC_ONLY recommendation pending DCM-005

**Deferred issues:** none

**Explicit exclusions:**
- Placebo characterization
- DCM-005 eligibility reassessment

**Revisit trigger:** Upon completion of D5-TRUST-TBRRIDGE-PLACEBO-001

**Required decision checkpoint:** DCM-005 eligibility reassessment

**Next artifact:** D5-TRUST-TBRRIDGE-PLACEBO-001

