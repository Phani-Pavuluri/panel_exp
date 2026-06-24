# SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001

**Artifact ID:** SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/scm_treated_set_placebo_calibration.py`  
**Validation:** `panel_exp/validation/scm_treated_set_placebo_null_calibration_001.py`  
**Summary:** [`archives/SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001_summary.json`](archives/SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001_summary.json)

---

## 1. Artifact ID

`SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001`

---

## 2. Purpose

SCM-specific empirical null calibration for treated-set placebo rank inference under known null DGPs and governed assignment families.

---

## 3. Prior studentized calibration context

`STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001` calibrated generic studentized placebo-rank mechanics. This artifact applies SCM-style treated-set statistics with observed/pseudo recomputation consistency.

---

## 4. SCM treated-set placebo method under test

Treated-set placebo rank on SCM-style statistics computed for observed and pseudo-treated sets from the same assignment family.

---

## 5. SCM-style statistic adapter

Lightweight adapter (not production SCM):

- Fit non-negative donor weights on pre-period outcomes (numpy lstsq / inverse-distance fallback)
- Predict synthetic post-period counterfactual from donor weights
- Effect = treated post mean − synthetic post mean
- Studentized mode divides by pre-period residual scale

---

## 6. Null DGPs

| DGP | Description |
|-----|-------------|
| iid_normal | IID Gaussian noise |
| unit_fixed_effect | Unit fixed effects |
| unit_and_time_fixed_effect | Unit + time fixed effects |
| heteroskedastic | Unit-varying noise scale |
| donor_matched_latent_factor | Latent factor with unit loadings |

---

## 7. Assignment families

complete_randomized_set · matched_pair_randomized · stratified_randomized

---

## 8. Statistic modes

| Mode | Description |
|------|-------------|
| scm_style_effect | SCM-style treated-set effect |
| scm_style_studentized_effect | SCM-style effect / pre-period scale |
| simple_diff_in_means_baseline | Post treated − post control mean |

---

## 9. Tail semantics

Inclusive placebo rank; `empirical_tail_fraction = rank / num_placebo_sets`. Two-sided uses absolute values. **Not a production p-value.**

---

## 10. Type-I calculation

`reject = empirical_tail_fraction <= alpha`. Verdict: calibrated ≤ alpha+0.03; borderline ≤ alpha+0.06; else diagnostic-only.

---

## 11. Simulation grid

10 specs × 100 replications × 30 pseudo-assignments. Preliminary grid only.

---

## 12. Results summary

See summary JSON for per-spec verdicts and comparison metrics.

---

## 13. SCM-style vs studentized vs diff-in-means comparison

Summary JSON `comparison_summary` reports:

- `max_type_i_excess_by_statistic_mode` across all three modes
- `studentized_vs_unstudentized_note`
- `scm_vs_diff_in_means_note` under donor-matched latent-factor null
- `fragile_assignment_families` and `fragile_dgps`

Preliminary grid only — do not overclaim.

---

## 14. Calibration verdicts

Mixed calibrated/borderline/not-calibrated across DGP and mode combinations in preliminary grid.

---

## 15. False-confidence / excess type-I findings

`max_empirical_type_i_excess` reported in summary JSON. Some DGP/mode pairs show excess type-I beyond borderline tolerance.

---

## 16. Limitations

- SCM-style adapter is not production SCM fitting
- Small panel sizes and 100-replication grid are preliminary
- No production estimator adapter contract yet

---

## 17. Required next evidence

- Larger simulation grid
- Production SCM estimator adapter
- SCM/AugSynth shared statistic adapter (`SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`)
- Assignment-generator stress tests

---

## 18. Downstream authorization boundary

No production p-values, causal CIs, TrustReport, CalibrationSignal, MMM, LLM, production decisioning, live API, scheduler, or budget optimization.

---

## 19. Safety checks

All governance flags false. 43 validation scenarios, zero failures.

---

## 20. Final verdict

`scm_treated_set_placebo_null_calibration_completed_no_downstream_authorization`

This artifact performs SCM-specific empirical null calibration only. The SCM-style statistic adapter is a calibration harness, not production SCM fitting. Empirical tail fractions are not production p-values. This artifact does not authorize causal confidence intervals. This artifact does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

---

## 21. Recommended next artifact

**`SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`**

Alternative: `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.scm_treated_set_placebo_null_calibration_001 --overwrite
```
