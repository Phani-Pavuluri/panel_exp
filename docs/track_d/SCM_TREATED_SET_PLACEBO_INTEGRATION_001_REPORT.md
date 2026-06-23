# SCM_TREATED_SET_PLACEBO_INTEGRATION_001

**Artifact ID:** SCM_TREATED_SET_PLACEBO_INTEGRATION_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/scm_treated_set_placebo.py`  
**Validation:** `panel_exp/validation/scm_treated_set_placebo_integration_001.py`  
**Summary:** [`archives/SCM_TREATED_SET_PLACEBO_INTEGRATION_001_summary.json`](archives/SCM_TREATED_SET_PLACEBO_INTEGRATION_001_summary.json)

---

## 1. Artifact ID

`SCM_TREATED_SET_PLACEBO_INTEGRATION_001`

---

## 2. Purpose

Move from method-specific randomization readiness classification to a concrete SCM integration path connecting:

- design-aware pseudo-assignment roles
- precomputed SCM observed/pseudo treated-set statistics
- treated-set placebo rank and empirical tail fraction
- SCM placebo governed semantics
- method-specific randomization validation

---

## 3. Prior roadmap context

Completed spine through `METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001`. This artifact wires SCM into the treated-set placebo framework under governed semantics.

---

## 4. Integration layers

| Layer | Module |
|-------|--------|
| Assignment roles | `assignment_generators.py` |
| Placebo rank/tail | `treated_set_placebo.py` |
| SCM semantics | `scm_placebo_semantics.py` |
| Method readiness | `method_specific_randomization.py` |
| SCM integration | `scm_treated_set_placebo.py` |

---

## 5. SCM statistic contract

`SCMStatisticContract` accepts precomputed observed and pseudo SCM statistics (statistic-first integration). Supported kinds: `absolute_effect`, `relative_effect`, `studentized_effect`, `signed_effect`, `rank_statistic`. Effect directions: `greater`, `less`, `two_sided`.

---

## 6. Treated-set placebo integration behavior

When statistics are comparable and assignment role is design-based with `num_treated_units >= 2`:

- `empirical_tail_fraction` and `placebo_rank` are computed via `compute_placebo_rank`
- Decision: `scm_treated_set_randomization_candidate`
- Warnings: framework-level candidate only; not a final production p-value; no causal CI authorized

---

## 7. SCM semantics bridge

`classify_scm_placebo_semantics` validates use case (single-treated vs multi-treated), assignment role, and pseudo-assignment sufficiency before integration proceeds.

---

## 8. Method-specific randomization bridge

`validate_method_randomization_inference` with `MethodFamily.SCM` confirms method-level readiness. Integration is blocked if either SCM semantics or method-specific validation blocks.

---

## 9. Candidate configurations

Multi-treated (`num_treated_units >= 2`), design-based assignment role, comparable precomputed statistics, sufficient pseudo assignments.

---

## 10. Falsification-only configurations

- Single-treated SCM placebo → null-monitor/falsification only
- Falsification-only assignment role → diagnostic with rank/tail if statistics valid

---

## 11. Blocked configurations

- Missing/mismatched/non-numeric statistics
- Insufficient pseudo assignments
- Blocked/unknown assignment roles
- Final p-value, causal CI, or platform overclaim requests

---

## 12. Scenario results

23 deterministic scenarios — all pass under `--strict`.

---

## 13. Downstream integration boundaries

This artifact defines SCM treated-set placebo integration only.  
It does not implement new SCM fitting.  
It does not produce final production p-values or causal confidence intervals.  
Empirical tail fractions are framework-level diagnostics/candidates only.  
It does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.

A method can only be a design-based randomization candidate when assignment generation preserves the original design constraints and observed/pseudo statistics are comparable under the same statistic contract.

---

## 14. Safety checks

All summary authorization flags are `false`. No production p-value or CI semantics.

---

## 15. Final verdict

`scm_treated_set_placebo_integration_defined_no_downstream_authorization`

---

## 16. Recommended next artifact

**`STUDENTIZED_PLACEBO_RANK_INFERENCE_001`**

Alternatives:

- `MULTICELL_SHARED_CONTROL_MULTIPLICITY_001`
- `SCM_ESTIMATOR_ADAPTER_CONTRACT_001` (if estimator adapter gap emerges)

Regenerate:

```bash
poetry run python -m panel_exp.validation.scm_treated_set_placebo_integration_001 --overwrite
```

---

## Residual Issues and Handoff

### Advanced in this artifact

- Statistic-first SCM treated-set placebo integration path
- Bridges to treated-set placebo, SCM semantics, and method-specific validation

### Deferred unchanged

- Estimator adapter for live SCM fitting inside integration
- Multicell multiplicity investigations
- Studentized placebo rank inference

### Next artifact

`STUDENTIZED_PLACEBO_RANK_INFERENCE_001`
