# STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001

**Artifact ID:** STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/studentized_randomization_calibration.py`  
**Validation:** `panel_exp/validation/studentized_randomization_null_calibration_001.py`  
**Summary:** [`archives/STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001_summary.json`](archives/STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001_summary.json)

---

## 1. Artifact ID

`STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001`

---

## 2. Purpose

Empirical null calibration of studentized placebo-rank mechanics under known null data-generating processes and governed design-aware assignment generators.

---

## 3. Prior refocus audit context

`METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001` prioritized this artifact as the first P0 implementation after pausing downstream schema, ingestion, and decisioning work.

---

## 4. Studentized placebo-rank method under test

The harness exercises the studentized rank mechanism (`compute_studentized_placebo_rank`) with transparent post-minus-pre effect statistics and pre-period scale estimates. This is a calibration surrogate, not the final SCM estimator statistic.

---

## 5. Null DGPs

| DGP | Description |
|-----|-------------|
| iid_normal | IID Gaussian noise |
| unit_fixed_effect | Unit fixed effects + noise |
| unit_and_time_fixed_effect | Unit and time fixed effects + noise |
| heteroskedastic | Unit-varying noise scale |

---

## 6. Assignment families

| Family | Status in default grid |
|--------|------------------------|
| complete_randomized_set | Tested |
| matched_pair_randomized | Tested (one treated per pair) |
| stratified_randomized | Tested |
| matched_block_randomized | Deferred in grid v1 |
| rerandomized_design_candidate | Deferred in grid v1 |

---

## 7. Statistic modes

- **studentized:** effect / pre-period scale  
- **unstudentized:** raw post-minus-pre effect (comparison mode)

---

## 8. Tail semantics

Inclusive placebo rank on the chosen statistic scale. `empirical_tail_fraction = rank / num_placebo_sets`. Two-sided uses `abs(pseudo) >= abs(observed)`. **Not a production p-value.**

---

## 9. Type-I calculation

For each alpha: `reject = empirical_tail_fraction <= alpha`. `empirical_type_i = mean(reject)`. `type_i_excess = empirical_type_i - alpha`.

Verdict thresholds (preliminary grid): calibrated if type-I ≤ alpha + 0.03; borderline if ≤ alpha + 0.06; else diagnostic-only.

---

## 10. Simulation grid

Default grid: 8 specs × 100 replications × 30 pseudo-assignments. Small deterministic panel sizes (12–16 units). Larger grids required for promotion evidence.

---

## 11. Results summary

See summary JSON for per-spec verdicts, type-I by alpha, and tail-fraction quantiles. Preliminary grid shows mixed calibrated/borderline/not-calibrated outcomes depending on DGP and statistic mode.

---

## 12. Calibration verdicts

| Verdict | Meaning |
|---------|---------|
| calibrated_under_tested_nulls | Type-I within +0.03 tolerance |
| borderline_requires_more_simulation | Within +0.06 tolerance |
| not_calibrated_diagnostic_only | Excess type-I beyond borderline |
| invalid_calibration_spec | Spec or replication failure |

---

## 13. False-confidence / excess type-I findings

Summary JSON reports `max_empirical_type_i_excess` across the grid. Unstudentized mode and some fixed-effect DGPs show higher excess — diagnostic-only pending larger grids.

---

## 14. Limitations

- Surrogate statistic, not SCM/AugSynth estimator output  
- Small panel sizes and 100-replication grid are preliminary  
- Matched-block and rerandomized families not in default grid  
- No SCM-specific adapter contract yet

---

## 15. Required next evidence

- Larger simulation grid  
- SCM-specific statistic calibration (`SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001`)  
- Observed/pseudo estimator adapter contract  
- Assignment-generator stress tests

---

## 16. Downstream authorization boundary

**No** production p-values, causal CIs, TrustReport, CalibrationSignal, MMM, LLM, production decisioning, live API, scheduler, or budget optimization.

---

## 17. Safety checks

All governance flags hardcoded false. Harness validates 37 scenarios with zero failures.

---

## 18. Final verdict

`studentized_randomization_null_calibration_completed_no_downstream_authorization`

This artifact performs empirical null calibration only. Empirical tail fractions are not production p-values. This artifact does not authorize causal confidence intervals. This artifact does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

---

## 19. Recommended next artifact

**`SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001`**

Alternative: `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.studentized_randomization_null_calibration_001 --overwrite
```
