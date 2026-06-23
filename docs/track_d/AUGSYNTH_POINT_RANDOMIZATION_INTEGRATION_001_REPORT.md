# AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001

**Artifact ID:** AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/augsynth_point_randomization.py`  
**Validation:** `panel_exp/validation/augsynth_point_randomization_integration_001.py`  
**Summary:** [`archives/AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001_summary.json`](archives/AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001_summary.json)

---

## 1. Artifact ID

`AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001`

---

## 2. Purpose

Define governed AugSynth point-estimate randomization integration connecting precomputed AugSynth point statistics to design-aware assignment roles, treated-set placebo rank/tail diagnostics, and method-specific randomization readiness.

---

## 3. Prior roadmap context

Built after `STRATIFIED_POOLED_ESTIMAND_CONTRACT_001`. Bridges the design-aware assignment / treated-set placebo / method-specific randomization spine to AugSynth point statistics without implementing new AugSynth fitting.

---

## 4. AugSynth point vs AugSynth JK boundary

AugSynth point estimates may become framework-level randomization candidates when observed and pseudo statistics are comparable under a valid contract. AugSynth JK remains diagnostic-only / characterized-only and is never a production inference path.

---

## 5. AugSynth point statistic contract

Requires observed and pseudo statistics, statistic kind, inference mode, effect direction, estimand, outcome scale, pre/post windows, donor eligibility rule, and augmentation configuration — all matched between observed and pseudo paths.

---

## 6. Design-aware assignment bridge

Uses `AssignmentRole` semantics from `panel_exp/design/assignment_generators.py`: design-based randomization candidate → point randomization candidate; falsification-only → diagnostic-only; blocked → blocked.

---

## 7. Treated-set placebo bridge

Reuses `compute_placebo_rank()` for inclusive placebo rank and empirical tail fraction. Tail fractions are labeled `not_production_p_value`.

---

## 8. Method-specific readiness bridge

Summarizes through `validate_method_randomization_inference()` with `MethodFamily.AUGSYNTH_CVXPY` for AugSynth point statistic kinds.

---

## 9. Candidate configurations

Point, relative point, and studentized point statistics under design-based assignment with valid contract, sufficient pseudo assignments, and no downstream authorization requests.

---

## 10. Diagnostic-only configurations

Falsification-only assignment roles return diagnostic-only decisions with rank/tail diagnostics permitted.

---

## 11. JK diagnostic-only configurations

Jackknife statistic kind or inference mode returns `AUGSYNTH_JK_DIAGNOSTIC_ONLY`. Production JK inference requests are blocked.

---

## 12. Blocked configurations

Missing statistics, contract mismatches, non-finite values, insufficient pseudo assignments, invalid effect direction, blocked assignment roles, and all downstream/platform authorization requests.

---

## 13. Scenario results

34 deterministic scenarios — all pass under `--strict`.

---

## 14. Downstream integration boundaries

This artifact defines AugSynth point randomization integration only.  
It does not implement new AugSynth fitting.  
It does not authorize AugSynth JK as production inference.  
It does not produce final production p-values or causal confidence intervals.  
Empirical tail fractions are framework-level diagnostics/candidates only.  
It does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

---

## 15. Safety checks

All summary authorization flags are `false`, including `augsynth_jk_authorized`.

---

## 16. Final verdict

`augsynth_point_randomization_integration_defined_no_downstream_authorization`

---

## 17. Recommended next artifact

**`METHOD_READINESS_MATRIX_V2_001`**

Alternatives: `AUGSYNTH_STUDENTIZED_RANDOMIZATION_INTEGRATION_001`, `CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.augsynth_point_randomization_integration_001 --overwrite
```
