# STUDENTIZED_PLACEBO_RANK_INFERENCE_001

**Artifact ID:** STUDENTIZED_PLACEBO_RANK_INFERENCE_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/studentized_placebo_rank.py`  
**Validation:** `panel_exp/validation/studentized_placebo_rank_inference_001.py`  
**Summary:** [`archives/STUDENTIZED_PLACEBO_RANK_INFERENCE_001_summary.json`](archives/STUDENTIZED_PLACEBO_RANK_INFERENCE_001_summary.json)

---

## 1. Artifact ID

`STUDENTIZED_PLACEBO_RANK_INFERENCE_001`

---

## 2. Purpose

Extend the placebo-rank / empirical-tail-fraction framework by comparing observed and pseudo-treated-set effects on a **studentized statistic scale** when a valid scale/standard-error/dispersion contract is available. Reduces scale sensitivity in placebo-rank comparisons.

---

## 3. Prior roadmap context

Built on `SCM_TREATED_SET_PLACEBO_INTEGRATION_001` and the treated-set placebo framework spine. Generic primitive usable by SCM, DID, and AugSynth diagnostics.

---

## 4. Relationship to design-aware assignment generators

Design-based assignment role is required for candidate classification; falsification-only roles downgrade to diagnostic-only.

---

## 5. Relationship to treated-set placebo framework

Reuses rank/tail semantics from `compute_placebo_rank` logic but applies them to studentized statistics `(effect - null_value) / scale`.

---

## 6. Relationship to SCM treated-set integration

`scm_treated_set_placebo.py` may later call this module when scale contracts are available. This artifact does not modify SCM integration.

---

## 7. Studentized statistic contract

Formula: `(effect - null_value) / scale`

Required inputs: observed/pseudo effects, observed/pseudo scales, effect direction, assignment role.

---

## 8. Scale validity rules

Block when: missing scale, non-positive scale, non-finite effect/scale, effect/scale ID mismatch, insufficient placebo sets, unknown scale source.

---

## 9. Rank / empirical tail fraction semantics

- **greater:** count `pseudo_studentized >= observed_studentized`
- **less:** count `pseudo_studentized <= observed_studentized`
- **two_sided:** count `abs(pseudo_studentized) >= abs(observed_studentized)`
- `empirical_tail_fraction = rank / num_placebo_sets` — **not** a final p-value

---

## 10. Candidate configurations

Design-based assignment, valid finite positive scales, sufficient placebo sets, no platform overclaims.

---

## 11. Diagnostic-only configurations

Falsification-only assignment role with valid scale contract.

---

## 12. Blocked configurations

Invalid scales, insufficient sets, blocked assignment roles, final p-value/CI requests, platform overclaims.

---

## 13. Scenario results

28 deterministic scenarios — all pass under `--strict`.

---

## 14. Downstream integration boundaries

This artifact defines a studentized placebo-rank inference primitive only.  
It does not produce final production p-values or causal confidence intervals.  
Empirical tail fractions are framework-level diagnostics/candidates only.  
Studentization is only allowed when the scale contract is valid.  
It does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

---

## 15. Safety checks

All summary authorization flags are `false`.

---

## 16. Final verdict

`studentized_placebo_rank_inference_defined_no_downstream_authorization`

---

## 17. Recommended next artifact

**`SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001`**

Alternatives: `MULTICELL_SHARED_CONTROL_MULTIPLICITY_001`, `AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001`

Regenerate:

```bash
poetry run python -m panel_exp.validation.studentized_placebo_rank_inference_001 --overwrite
```
