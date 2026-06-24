# SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001

**Artifact ID:** SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/scm_augsynth_statistic_adapter.py`  
**Validation:** `panel_exp/validation/scm_augsynth_statistic_adapter_contract_001.py`  
**Summary:** [`archives/SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001_summary.json`](archives/SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001_summary.json)

---

## 1. Artifact ID

`SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`

---

## 2. Purpose

Define the shared statistic-adapter contract guaranteeing observed and pseudo-treated-set statistics are recomputed consistently across SCM and AugSynth randomization paths.

---

## 3. Prior null-calibration context

`STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001` and `SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001` established preliminary null-calibration evidence. This artifact defines the adapter contract required before estimator-backed promotion.

---

## 4. Why a shared statistic adapter is needed

SCM and AugSynth paths are statistic-first. Without a governed adapter contract, observed/pseudo comparability, estimand alignment, and provenance cannot be validated.

---

## 5. Adapter schema

`AdaptedStatisticSet` bundles observed statistic, pseudo statistics, `StatisticAdapterConfig`, and `StatisticProvenance`.

---

## 6. Required config fields

estimand_id · outcome_scale · pre_period_id · post_period_id · donor_eligibility_rule_id · estimator_config_id · treated_set_aggregation_rule_id · effect_direction · missing_data_policy_id · statistic_kind · studentization_scale_id (when studentized)

---

## 7. Required provenance fields

estimator_family · estimator_version · adapter_version · config_hash · source_artifact_id · computation_mode

---

## 8. SCM statistic boundary

- `scm_style_calibration` → calibration-harness-only  
- `scm` → randomization-candidate-only (not production)

---

## 9. AugSynth statistic boundary

`augsynth_cvxpy` with point/relative/studentized effect kinds → randomization-candidate-only. No AugSynth JK production inference.

---

## 10. Cross-family comparison boundary

SCM and AugSynth may be compared only under explicit shared estimand/config contracts; estimator equivalence is not assumed.

---

## 11. Observed/pseudo consistency rules

All config fields must match between observed and pseudo statistic sets when provided separately.

---

## 12. Compatible configurations

Same-family sets with complete config, provenance, finite statistics, and sufficient pseudo assignments.

---

## 13. Calibration-harness-only configurations

`scm_style_calibration` family from null-calibration harness.

---

## 14. Randomization-candidate-only configurations

`scm` and `augsynth_cvxpy` families with supported statistic kinds.

---

## 15. Blocked configurations

Missing statistics, non-finite values, config/provenance gaps, mismatches, unsupported families.

---

## 16. Readiness matrix

Five rows: SCM-style calibration harness, SCM randomization candidate, AugSynth point/relative/studentized.

---

## 17. Scenario results

See summary JSON — 41 scenarios, zero failures.

---

## 18. Required next evidence

Production estimator-backed adapter, larger null grids, assignment-generator stress tests, SCM vs AugSynth disagreement diagnostics.

---

## 19. Downstream authorization boundary

No production p-values, causal CIs, TrustReport, CalibrationSignal, MMM, LLM, production decisioning, live API, scheduler, or budget optimization.

---

## 20. Safety checks

All governance flags false.

---

## 21. Final verdict

`scm_augsynth_statistic_adapter_contract_defined_no_downstream_authorization`

This artifact defines a shared SCM/AugSynth statistic adapter contract only. It does not implement production SCM fitting. It does not implement production AugSynth fitting. SCM and AugSynth statistics may be compared only under explicit shared estimand/config contracts; estimator equivalence is not assumed. Empirical tail fractions remain calibration diagnostics only, not production p-values. This artifact does not authorize causal confidence intervals. This artifact does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

---

## 22. Recommended next artifact

**`DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`**

Alternative: `MULTICELL_MAX_T_RESEARCH_SCOUT_001` or `SCM_AUGSYNTH_DISAGREEMENT_DIAGNOSTICS_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.scm_augsynth_statistic_adapter_contract_001 --overwrite
```
