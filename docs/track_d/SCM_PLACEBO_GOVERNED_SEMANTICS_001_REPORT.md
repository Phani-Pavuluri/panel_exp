# SCM_PLACEBO_GOVERNED_SEMANTICS_001

**Artifact ID:** `SCM_PLACEBO_GOVERNED_SEMANTICS_001`  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/scm_placebo_semantics.py`  
**Validation:** `panel_exp/validation/scm_placebo_governed_semantics_001.py`  
**Summary:** [`archives/SCM_PLACEBO_GOVERNED_SEMANTICS_001_summary.json`](archives/SCM_PLACEBO_GOVERNED_SEMANTICS_001_summary.json)

---

## 1. Artifact ID

`SCM_PLACEBO_GOVERNED_SEMANTICS_001`

---

## 2. Purpose

Define and enforce governed semantics for SCM placebo usage across single-treated falsification, multi-treated treated-set placebo, leave-one-treated-out sensitivity, and design-aware pseudo-assignment candidates.

This artifact prevents semantic misuse and routes SCM placebo outputs into the correct governed role. It does **not** authorize SCM placebo as production causal inference.

---

## 3. Prior evidence context

- **DCM-001 SCM+JK:** restricted TrustReport eligibility; causal intervals via jackknife only under restrictions.
- **SCM+Placebo (A27/A28):** single-treated falsification/null-monitor only; multi-treated blocked at geometry layer.
- **FULL-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001:** SCM Placebo `NULL_MONITOR_ONLY`.
- **MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001:** treated-set placebo framework with design-aware pseudo-assignments.

---

## 4. Relationship to design-aware assignment generators

`DESIGN_AWARE_ASSIGNMENT_GENERATORS_001` supplies `AssignmentRole` semantics (`design_based_randomization_candidate`, `falsification_only`, `blocked`). SCM placebo semantics **must not** upgrade falsification-only or blocked generator outputs to design-based validity.

---

## 5. Relationship to treated-set placebo framework

`MULTITREATED_TREATED_SET_PLACEBO-FRAMEWORK_001` provides placebo rank and empirical tail fraction at the framework layer. This artifact classifies what those outputs **mean** for SCM — framework candidate or falsification diagnostic only, never production p-value/CI.

`classify_from_treated_set_placebo_result()` bridges framework results into SCM semantics.

---

## 6. SCM placebo semantic roles

| Role | Meaning |
|------|---------|
| `null_monitor_only` | Single-treated SCM placebo falsification envelope |
| `falsification_diagnostic` | Non-design-based or single-path diagnostic |
| `design_based_randomization_candidate` | Multi-treated treated-set path with valid design-based pseudo-assignments |
| `sensitivity_only` | Leave-one-treated-out robustness — not placebo |
| `blocked` | Invalid geometry, overclaim, or insufficient pseudo-assignments |

---

## 7. Supported / downgraded / blocked configurations

**Supported (governed, not production):**

- Single-treated SCM placebo → null-monitor/falsification only
- Multi-treated treated-set with design-based pseudo-assignments → framework candidate
- Multi-treated with falsification-only assignments → falsification diagnostic
- Leave-one-treated-out labeled as sensitivity → sensitivity only

**Blocked / downgraded:**

- Final p-value or causal CI requests
- TrustReport, CalibrationSignal, production, live API, scheduler, budget optimization
- Unknown use case, zero treated units, wrong treated count for use case
- Insufficient or missing pseudo-assignments for treated-set placebo
- Leave-one-treated-out requested as placebo inference

---

## 8. Scenario results

19 deterministic validation scenarios — all pass under `--strict`:

- 3 single-treated paths (supported + p-value/CI blocked)
- 5 multi-treated / design-aware paths
- 2 leave-one-treated-out paths
- 9 platform overclaim / invalid geometry paths

---

## 9. Governance boundaries

SCM single-treated placebo remains falsification/null-monitor only.  
Leave-one-treated-out is sensitivity analysis, not placebo inference.  
Treated-set placebo can only become a design-based randomization candidate when the pseudo-assignment generator preserves the original assignment constraints.  
This artifact does not authorize TrustReport, CalibrationSignal, production decisioning, live API, scheduler, MMM ingestion, or budget optimization.

All summary authorization flags are `false`.

---

## 10. Safety checks

- No `*_authorized: true` in summary JSON
- No production p-value or CI semantics emitted
- Placebo rank / empirical tail fraction not labeled as final p-value
- TrustReport ops remain frozen

---

## 11. Final verdict

`scm_placebo_governed_semantics_defined_no_authorization`

---

## 12. Recommended next artifact

**`METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001`** — wire SCM (and other estimators) to supply statistics into the treated-set placebo framework under these semantics.

Regenerate:

```bash
poetry run python -m panel_exp.validation.scm_placebo_governed_semantics_001 --overwrite
```

---

## Residual Issues and Handoff

### Resolved in this artifact

- SCM placebo semantic roles defined across four use cases
- `INV-MULTITREATED-DESIGN-AWARE-PLACEBO-001` advanced: SCM semantics layer complete pending method-specific validation

### Deferred (unchanged)

- `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001`
- `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001`

### Next artifact

`METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001`
