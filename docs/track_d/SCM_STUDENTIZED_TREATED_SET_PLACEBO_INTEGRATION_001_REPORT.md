# SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001

**Artifact ID:** SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/scm_studentized_treated_set_placebo.py`  
**Validation:** `panel_exp/validation/scm_studentized_treated_set_placebo_integration_001.py`  
**Summary:** [`archives/SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001_summary.json`](archives/SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001_summary.json)

---

## 1. Artifact ID

`SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001`

---

## 2. Purpose

Connect SCM treated-set placebo integration to the studentized placebo-rank primitive, enabling SCM treated-set comparisons on a studentized scale when effect and scale contracts are valid.

---

## 3. Prior roadmap context

Built on `STUDENTIZED_PLACEBO_RANK_INFERENCE_001` and `SCM_TREATED_SET_PLACEBO_INTEGRATION_001`.

---

## 4. Relationship to studentized placebo-rank primitive

Calls `evaluate_studentized_placebo_rank()` with SCM effect/scale inputs mapped to `StudentizedPlaceboRankSpec`.

---

## 5. Relationship to SCM treated-set placebo integration

Bridges raw SCM effects through `evaluate_scm_treated_set_placebo_integration()` for parallel raw-rank context.

---

## 6. Relationship to SCM governed semantics

`classify_scm_placebo_semantics()` validates use case and assignment role.

---

## 7. Relationship to method-specific randomization validation

`validate_method_randomization_inference()` with `MethodFamily.SCM` and `STUDENTIZED_EFFECT`.

---

## 8. SCM studentized statistic contract

Formula: `(effect - null_value) / scale`. Requires matched pseudo effect/scale assignment IDs.

---

## 9. Candidate configurations

Multi-treated, design-based assignment, valid finite positive scales, sufficient placebo sets.

---

## 10. Diagnostic-only configurations

Single-treated SCM placebo; falsification-only assignment role.

---

## 11. Blocked configurations

Invalid/missing effects or scales, insufficient sets, platform overclaims.

---

## 12. Bridge behavior

Integration returns studentized rank summary plus SCM treated-set, semantics, and method-randomization summaries.

---

## 13. Scenario results

34 deterministic scenarios — all pass under `--strict`.

---

## 14. Downstream integration boundaries

This artifact defines SCM studentized treated-set placebo integration only.  
It does not implement new SCM fitting.  
It does not produce final production p-values or causal confidence intervals.  
Studentized empirical tail fractions are framework-level diagnostics/candidates only.  
Studentization is only allowed when the SCM effect and scale contracts are valid.  
It does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

---

## 15. Safety checks

All summary authorization flags are `false`.

---

## 16. Final verdict

`scm_studentized_treated_set_placebo_integration_defined_no_downstream_authorization`

---

## 17. Recommended next artifact

**`MULTICELL_SHARED_CONTROL_MULTIPLICITY_001`**

Alternatives: `AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001`, `SCM_ESTIMATOR_ADAPTER_CONTRACT_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.scm_studentized_treated_set_placebo_integration_001 --overwrite
```
