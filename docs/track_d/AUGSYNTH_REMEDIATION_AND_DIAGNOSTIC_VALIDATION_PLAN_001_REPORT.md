# AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001 Report

## 1. Purpose

This validation-only artifact defines exactly what AugSynth CVXPY must pass before it can move beyond diagnostic/restricted research use. The registry contains **84 validation rows** across **28 remediation/validation areas** (`failed_scenarios: []`).

This plan defines metadata-only validation requirements. It is **not** a production inference implementation.

## 2. Why AugSynth needs remediation before promotion

Per `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`, `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`, and `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001`, AugSynth is a plausible P2 remediation candidate but remains diagnostic/restricted research until CVXPY solver reliability, donor support, adapter maturity, null calibration, and method disagreement checks are validated.

## 3. Prior-work reconciliation

| Prior artifact | Carried forward |
|---|---|
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001` | AugSynth routing requirements |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | AugSynth backlog items |
| `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001` | Adapter/null calibration gates |
| `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` | Promotion status |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell blockers |
| `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001` | Donor support, fit, overlap |
| `SIMULATION_DGP_COVERAGE_PLAN_001` | DGP evidence |
| `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001` | Assignment stress |
| `METHOD_FAILURE_MODE_REGISTRY_001` | Failure-mode blockers |

Resolved audits are not re-implemented; unresolved AugSynth blockers are encoded as validation requirements.

## 4. Relationship to OPEN_INVESTIGATIONS_001

Open investigations (e.g., `INV-AUGSYNTH-JK-TRUSTREPORT-DISPOSITION-001` resolved) inform diagnostic boundaries. The validation plan consults governance state; investigation resolution does not imply production readiness.

## 5. Relationship to PRODUCTION_READINESS_BACKLOG_LEDGER_001

AugSynth backlog rows (`augsynth_remediation_diagnostic_validation`, `augsynth_adapter_readiness`, `augsynth_null_calibration`, etc.) map directly to validation areas in this plan.

## 6. Relationship to selection-gate requirements

Per `routing_augsynth_remediation_candidate`, AugSynth routes to diagnostic/remediation until adapter, null calibration, donor support, and DGP coverage mature. This plan defines the evidence those routes require.

## 7. Evidence base

- `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
- `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`
- `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`

## 8. AugSynth current status

AugSynth remains **diagnostic/restricted research** until remediation evidence exists. Point estimates do **not** authorize production inference. Production inference, p-values, and causal CIs remain **unauthorized**.

## 9. Validation status definitions

| Status | Meaning |
|---|---|
| `required_blocker` | Must pass before any promotion hypothesis |
| `required_warning` | Must be reviewed; may block promotion if severe |
| `candidate_after_remediation` | Advancement requires remediation evidence |
| `candidate_after_adapter` | Advancement requires statistic adapter maturity |
| `candidate_after_null_calibration` | Advancement requires null calibration evidence |
| `candidate_after_simulation` | Advancement requires DGP simulation coverage |
| `diagnostic_only` | Diagnostic readout only |
| `research_only` | Research handling required |
| `blocked` | Production path blocked |

## 10. Remediation type definitions

| Type | Meaning |
|---|---|
| `solver_reliability` | CVXPY solver availability, convergence, failure handling |
| `diagnostic_validation` | Observed diagnostic thresholds |
| `donor_support_validation` | Donor support, overlap, convex hull |
| `adapter_requirement` | Statistic adapter contract |
| `null_calibration_requirement` | Null calibration gates |
| `simulation_requirement` | DGP simulation coverage |
| `assignment_stress_requirement` | Assignment-generator stress |
| `multicell_boundary` | Multicell/shared-control blockers |
| `release_gate_boundary` | Platform release gate |

## 11. Required validation areas

All 28 areas: point estimate diagnostic, CVXPY solver, convergence, regularization, donor support/overlap, convex hull/extrapolation, pre-period fit/trend, outcome scale, sparse/count/rate, missing data, assignment/design, assignment stress, single/multi/treated-set AugSynth, jackknife, placebo/rank, studentized adapter, null calibration, DGP simulation, failure registry, disagreement vs SCM/DID/Synthetic DID/TBRRidge, multicell boundary, release gate.

## 12. CVXPY solver reliability requirements

CVXPY solver availability and failure handling are **required blockers**. Solver must be available; failures must be surfaced, not silently ignored.

## 13. Solver convergence and failure-handling requirements

Solver convergence diagnostics and explicit failure handling are **required blockers** before promotion hypotheses.

## 14. Regularization sensitivity requirements

Regularization sensitivity is a **required warning**. Weight instability may block promotion if severe.

## 15. Donor support / overlap validation

Donor support (`OPD-DONOR-001`) and overlap diagnostics are **required blockers**.

## 16. Convex-hull and extrapolation-risk validation

Convex-hull (`OPD-DS-005`) and extrapolation-risk diagnostics are **required blockers**.

## 17. Pre-period fit and trend validation

Pre-period fit (`OPD-PF-001`, `OPD-PF-003`) and trend stability (`OPD-PF-002`) are **required blockers**.

## 18. Outcome-scale validation

Outcome-scale compatibility is a **required warning**. Sparse/count/rate outcomes require additional DGP coverage.

## 19. Missing-data and sparse-outcome validation

Missing-data sensitivity and sparse/count/rate outcome handling are **required warnings**.

## 20. Assignment/design validation

Assignment/design validity is a **required blocker**.

## 21. Assignment-generator stress validation

Assignment-generator stress (`ST-AD-001`, `ST-AD-009`, `ST-AD-010`) is a **required blocker**.

## 22. Statistic adapter requirements

Treated-set, jackknife, and studentized paths require `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001` before inferential promotion.

## 23. Null calibration requirements

Null calibration (`null_fpr_gate`, `coverage_replay`) required before placebo-rank or studentized inference promotion.

## 24. DGP simulation requirements

DGP simulation coverage (`DGP-AUGSYNTH-001`, `DGP-ES-007`, `DGP-CP-002`) required before promotion evidence.

## 25. Failure-registry blockers

`FM-ES-001`, `FM-CP-003`, `FM-CP-004`, and `FM-INF-009` must be consulted.

## 26. Method disagreement checks

AugSynth must be compared against SCM, DID, Synthetic DID, and TBRRidge before promotion (`required_warning` per family).

## 27. Single-treated AugSynth path

Single-treated AugSynth is `candidate_after_remediation` — primary near-term path after all gates pass.

## 28. Multi-treated AugSynth boundary

Multi-treated AugSynth is `research_only` until dependence handling is validated.

## 29. Multicell/shared-control boundary

Multicell/shared-control AugSynth is **blocked** until `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` lane is satisfied.

## 30. Allowed current uses

- AugSynth diagnostic point readouts
- Donor-support and pre-period fit diagnostics
- Placebo/null calibration research
- Restricted research exploration

## 31. Forbidden current uses

- AugSynth production inference, p-values, causal CIs
- TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, budget optimization
- Multi-treated/multicell production claims without dependence validation

## 32. Required future artifacts

1. `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` (immediate next)
2. `SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001`
3. `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001`

## 33. Updated roadmap sequence

1. ✅ `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001`
2. ✅ `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` (this plan)
3. **`DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`** (immediate next)

## 34. Downstream boundary

This validation plan does not authorize AugSynth production inference.
This validation plan does not authorize production p-values.
This validation plan does not authorize causal confidence intervals.
This validation plan does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 35. Validation

Harness: `panel_exp/validation/augsynth_remediation_diagnostic_validation_plan_001.py`
Tests: `tests/validation/test_augsynth_remediation_diagnostic_validation_plan_001.py`

## 36. Verdict

`augsynth_remediation_and_diagnostic_validation_plan_defined_no_downstream_authorization`

**Next:** `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`

## Summary JSON location

[`docs/track_d/archives/AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001_summary.json`](archives/AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001_summary.json)
