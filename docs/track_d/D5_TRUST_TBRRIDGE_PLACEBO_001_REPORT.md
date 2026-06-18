# D5 Trust TBRRidge Placebo 001 — Report

**Artifact ID:** D5-TRUST-TBRRIDGE-PLACEBO-001
**Verdict:** `tbrridge_placebo_single_treated_restricted`

> This artifact characterizes TBRRidge Placebo as a null-reference and falsification path.
> It does not establish causal confidence-interval validity.
> It does not authorize TrustReport.
> It does not perform the DCM-005 eligibility reassessment.

## 1. Executive summary

TBRRidge+Placebo characterized. Verdict: `tbrridge_placebo_single_treated_restricted`. Assessment: `method_unsuitable_for_causal_interval`.

## 2. Prior DCM-005 Placebo status

Prior eligibility harness: INSUFFICIENT_EVIDENCE; placebo-in-space semantics unvalidated for TBRRidge.

## 3. Scope

18 worlds; 4 geometry variants.

## 4. Non-goals

- No DCM-005 eligibility reassessment
- No TrustReport authorization
- No production algorithm changes

## 5. TBRRidge estimator path

RidgeCV on pre-period-normalized controls.

## 6. Placebo implementation

Placebo-in-space: each control unit assigned treated window; reference distribution of post-window ATT.

## 7. Placebo-unit construction

One control unit pseudo-treated per draw; observed unit retained; RMSPE pre-fit filter optional.

## 8. Geometry assumptions

Exactly **one** treated unit; >=5 control units for production path.

## 9. Exchangeability assumptions

Donors exchangeable under placebo reassignment; serial dependence invalidates exchangeability.

## 10. Estimand

Post-window mean treated-minus-counterfactual effect (level_mean_relative_percent_injection).

## 11. Scale contract

Level mean shift from percent injection; placebo statistics on same scale.

## 12. Worlds

clean_null, clean_positive_effect, clean_negative_effect, weak_signal, strong_signal, serial_correlation, high_serial_correlation, heteroskedasticity, regime_shift, post_treatment_shock, pre_trend_violation, poor_pre_fit, outlier_period, small_donor_set, large_donor_set, low_noise_null, contaminated_donor, placebo_null

## 13. Effect-size sweep

0.0, 0.03, 0.08, 0.12, -0.05

## 14. Geometry sweep

single_treated_unit, multiple_treated_units, small_control_pool, large_control_pool

## 15. Run counts/runtime

Total 232; ok 179; runtime 9.8800s.

## 16. Point-estimate behavior

{'mean_bias_clean_positive': 0.5610826065916746, 'sign_accuracy_positive': 1.0}

## 17. Placebo distribution behavior

{'mean_placebo_draws': 11.865921787709498, 'mean_placebo_std': 2.0188914562581033}

## 18. Null-rank calibration

{'mean_rank_null': 0.5896799472457367, 'uniform_reference': 0.5}

## 19. Null type-I

type_i_null: 0.0000; mean_p_null: 0.6304.

## 20. Positive-effect power

power_positive: 0.2373.

## 21. Negative-effect power

{'type_i_error': None, 'power': None, 'negative_power': 0.23076923076923078, 'sign_accuracy': 1.0, 'mean_placebo_rank_null': None, 'n_null': 0, 'n_positive': 0, 'n_negative': 13, 'n_ok': 13}

## 22. Serial-dependence findings

{'assumed_under_placebo_in_space': {'type_i_error': 0.0, 'power': 0.2222222222222222, 'negative_power': 0.23076923076923078, 'sign_accuracy': 1.0, 'mean_placebo_rank_null': 0.5896799472457367, 'n_null': 48, 'n_positive': 99, 'n_negative': 13, 'n_ok': 160}, 'serial_dependence_caveat': {'type_i_error': None, 'power': 0.3157894736842105, 'negative_power': None, 'sign_accuracy': 1.0, 'mean_placebo_rank_null': None, 'n_null': 0, 'n_positive': 19, 'n_negative': 0, 'n_ok': 19}}

## 23. Pre-fit findings

{'low_prefit_rmse': {'type_i_error': None, 'power': None, 'negative_power': None, 'sign_accuracy': None, 'mean_placebo_rank_null': None, 'n_null': 0, 'n_positive': 0, 'n_negative': 0, 'n_ok': 0}, 'high_prefit_rmse': {'type_i_error': None, 'power': None, 'negative_power': None, 'sign_accuracy': None, 'mean_placebo_rank_null': None, 'n_null': 0, 'n_positive': 0, 'n_negative': 0, 'n_ok': 0}}

## 24. Donor-support findings

{'small': {'type_i_error': 0.0, 'power': 0.0, 'negative_power': 0.0, 'sign_accuracy': 1.0, 'mean_placebo_rank_null': 0.5999999999999999, 'n_null': 14, 'n_positive': 38, 'n_negative': 3, 'n_ok': 55}, 'medium': {'type_i_error': 0.0, 'power': 0.0, 'negative_power': 0.0, 'sign_accuracy': 1.0, 'mean_placebo_rank_null': 0.6004784688995215, 'n_null': 19, 'n_positive': 39, 'n_negative': 7, 'n_ok': 65}, 'large': {'type_i_error': 0.0, 'power': 0.6829268292682927, 'negative_power': 1.0, 'sign_accuracy': 1.0, 'mean_placebo_rank_null': 0.5663697705802968, 'n_null': 15, 'n_positive': 41, 'n_negative': 3, 'n_ok': 59}}

## 25. Multiple-treated findings

{'type_i_error': None, 'power': 0.0, 'negative_power': None, 'sign_accuracy': 1.0, 'mean_placebo_rank_null': None, 'n_null': 0, 'n_positive': 2, 'n_negative': 0, 'n_ok': 2}

## 26. Worst-world behavior

post_treatment_shock type_i: 0.0000.

## 27. Policy comparisons

A current; B prefit-gated; C single-treated; D min controls; E null-monitor; F blocked.

## 28. Root-cause determination

Placebo envelope is null-reference / falsification; not causal ATT uncertainty.

## 29. Production-defect decision

`method_unsuitable_for_causal_interval` — Placebo-in-space produces a null-reference envelope and randomization p-value; it is not a causal sampling distribution for ATT intervals on TBRRidge.; Production requires exactly one treated unit and >=5 controls; multi-treated geometry is unsupported by design.

## 30. Semantic classification

{'verdict': 'tbrridge_placebo_single_treated_restricted', 'supported_roles': ['null_monitor', 'falsification_diagnostic'], 'unsupported_roles': ['restricted_causal_interval', 'trust_report', 'calibration_signal'], 'readout_types': {'path_band': 'null_monitor_interval', 'p_value': 'placebo_p_value', 'inversion_ci': 'falsification_score_not_causal_interval'}}

## 31. TrustReport implications

Null-monitor / falsification only; causal-interval and TrustReport blocked.

## 32. Authorization status

**Blocked** — trust_report_authorized=false.

## 33. Investigation lifecycle update

INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001 remains OPEN with provisional NULL_MONITOR_ONLY recommendation for DCM-005.

## 34. Remaining limitations

Characterizes DCM-005 Placebo only; DCM-005 eligibility reassessment out of scope.; Placebo distribution ≠ causal sampling distribution.; Single-treated-unit geometry required; multi-treated unsupported in production.; Does not authorize TrustReport or modify production inference code.

## 35. Governance verdict

**`tbrridge_placebo_single_treated_restricted`**

## Residual Issues and Handoff

**Resolved in this artifact:** none

**New investigations opened:** none

**Existing investigations updated:**
- INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001 → OPEN; provisional NULL_MONITOR_ONLY recommendation pending DCM-005

**Deferred issues:** none

**Explicit exclusions:**
- DCM-005 eligibility reassessment

**Revisit trigger:** Before DCM-005 TrustReport eligibility reassessment

**Required decision checkpoint:** DCM-005 eligibility reassessment

**Next artifact:** DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001

