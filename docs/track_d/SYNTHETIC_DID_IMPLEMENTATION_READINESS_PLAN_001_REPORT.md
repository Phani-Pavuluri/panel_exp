# SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001 Report

## 1. Purpose

This planning-only artifact defines exactly what Synthetic DID must satisfy before it can be implemented as a governed candidate method. The registry contains **114 readiness rows** across **38 readiness areas** (`failed_scenarios: []`).

This plan defines metadata-only implementation-readiness requirements. It is **not** a Synthetic DID implementation.

## 2. Why Synthetic DID needs implementation-readiness planning

Per `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`, `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`, and `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`, Synthetic DID is a research/scout candidate with medium fixability. Existing repo code (`panel_exp/methods/synthetic_did.py`) is skipped in batch validation with evidence gaps (`FM-ES-009`, `FM-CP-005`). Before any implementation work, explicit contracts for unit weights, time weights, regularization/tuning, donor support, diagnostics, adapters, null calibration, and method disagreement checks must be defined.

## 3. Prior-work reconciliation

| Prior artifact | Carried forward |
|---|---|
| `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001` | Scout routing and failure modes |
| `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | DID parallel-trend and assignment gates |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | SCM donor support and pre-period fit |
| `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` | AugSynth disagreement boundary |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001` | Selection-gate routing |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | Synthetic DID backlog items |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell blockers |
| `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001` | Adapter/null calibration gates |
| `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001` | Donor support, fit, overlap |
| `SIMULATION_DGP_COVERAGE_PLAN_001` | DGP evidence |
| `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001` | Assignment stress |
| `METHOD_FAILURE_MODE_REGISTRY_001` | `FM-ES-009`, `FM-CP-005` blockers |

Resolved audits are not re-implemented; unresolved Synthetic DID blockers are encoded as readiness requirements.

## 4. Relationship to OPEN_INVESTIGATIONS_001

`INV-SYNTHETIC-DID-IMPLEMENTATION-READINESS-PLAN-001` is resolved by this artifact. Open investigations for method-family retire/replace, selection-gate implementation, and production authorization release gate remain **PLANNED**. Investigation resolution does **not** imply production readiness.

## 5. Relationship to PRODUCTION_READINESS_BACKLOG_LEDGER_001

Synthetic DID backlog rows (`synthetic_did_implementation_readiness`, `synthetic_did_unit_time_weights`, `synthetic_did_adapter_readiness`, etc.) map directly to readiness areas in this plan.

## 6. Relationship to selection-gate requirements

Per `routing_synthetic_did_implementation_candidate`, Synthetic DID routes to implementation-readiness planning until design, diagnostic, adapter, and null-calibration contracts mature. Point estimates alone do not satisfy selection-gate promotion.

## 7. Relationship to Synthetic DID scout and suitability work

`SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001` established Synthetic DID as a scout candidate with production inference unauthorized. This readiness plan carries forward scout conclusions into explicit implementation prerequisites without duplicating scout routing.

## 8. Evidence base

- `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
- `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
- `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
- `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`
- `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`
- `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`
- `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`

## 9. Synthetic DID current status

Synthetic DID is **`implementation_readiness_candidate`**. It is **not implemented or production-authorized** by this artifact. Point estimates do **not** authorize production inference. Production inference, p-values, and causal CIs remain **unauthorized**.

## 10. Readiness status definitions

| Status | Meaning |
|---|---|
| `required_blocker` | Must pass before any implementation hypothesis |
| `required_warning` | Must be reviewed; may block implementation if severe |
| `implementation_candidate` | Eligible for governed implementation planning only |
| `candidate_after_design` | Advancement requires design eligibility evidence |
| `candidate_after_adapter` | Advancement requires statistic adapter maturity |
| `candidate_after_null_calibration` | Advancement requires null calibration evidence |
| `candidate_after_simulation` | Advancement requires DGP simulation coverage |
| `diagnostic_only` | Diagnostic/scout readout only |
| `research_only` | Research handling required before promotion |
| `blocked` | Production/implementation path blocked |

## 11. Readiness type definitions

| Type | Meaning |
|---|---|
| `implementation_scope` | Method scope and candidate boundary |
| `data_requirement` | Data shape, panel balance, pre/post periods |
| `diagnostic_requirement` | Donor support, fit, trends, comparisons |
| `estimator_component_requirement` | Unit weights, time weights, regularization |
| `inference_adapter_requirement` | Placebo, jackknife, bootstrap, studentized adapters |
| `null_calibration_requirement` | Null calibration gates |
| `simulation_requirement` | DGP simulation coverage |
| `assignment_stress_requirement` | Assignment-generator stress compatibility |
| `multicell_boundary` | Multicell/shared-control dependence boundary |
| `release_gate_boundary` | Production authorization release gate |

## 12. Required readiness areas

All Synthetic DID implementation paths require readiness across: method scope, implementation candidate boundary, data-shape requirements, panel balance, pre/post periods, treated/control support, unit-weight requirements, time-weight requirements, regularization/tuning, donor support/overlap, pre-period fit, pre-period trend stability, parallel-trend relation to DID, synthetic-control relation to SCM, comparisons against SCM/DID/AugSynth/TBRRidge, outcome-scale compatibility, sparse/count/rate outcomes, missing data, assignment/design validity, assignment stress, single-treated path, multi-treated path, treated-set path, multicell boundary, point-estimate implementation, inference adapters, placebo/rank, jackknife, bootstrap, studentized statistic, null calibration, DGP simulation, failure-registry blockers, method disagreement checks, and release-gate boundary.

## 13. Data-shape and panel-balance requirements

Data-shape and panel-balance requirements are **required blockers**. Incompatible panel structure blocks implementation.

## 14. Pre/post period requirements

Pre/post period length and alignment are **required blockers** before implementation.

## 15. Treated/control support requirements

Treated/control support diagnostics are **required blockers**. Insufficient support blocks implementation.

## 16. Unit-weight requirements

Explicit unit-weight contract, normalization, and stability diagnostics are **required blockers** before implementation.

## 17. Time-weight requirements

Explicit time-weight contract, normalization, and stability diagnostics are **required blockers** before implementation.

## 18. Regularization/tuning requirements

Regularization/tuning contract, grid specification, and stability diagnostics are **required blockers** before implementation.

## 19. Donor support and overlap validation

Donor support (`OPD-DONOR-001`) and overlap (`OPD-DS-005`) are **required blockers**.

## 20. Pre-period fit and trend validation

Pre-period fit (`OPD-PF-001`, `OPD-PF-003`) and trend stability (`OPD-PF-002`) are **required blockers**.

## 21. Relation to DID

Parallel-trend relation to DID is a **required blocker**. DID conditional validation gates must pass before Synthetic DID-DID comparison promotion.

## 22. Relation to SCM

Synthetic-control relation to SCM is a **required warning**. SCM donor support and pre-period fit diagnostics must be compared.

## 23. Relation to AugSynth

Comparison against AugSynth is a **required warning**. Large disagreement blocks promotion.

## 24. Outcome-scale requirements

Outcome-scale compatibility is a **required warning**. Sparse/count/rate outcomes require additional DGP coverage.

## 25. Assignment/design validation

Assignment/design validity is a **required blocker**. Unknown assignment blocks implementation.

## 26. Assignment-generator stress validation

Assignment-generator stress compatibility (`ST-AD-001`, `ST-AD-009`, `ST-AD-010`) is a **required blocker**.

## 27. Implementation component requirements

Point-estimate implementation requires unit-weight, time-weight, and regularization contracts. Point estimates remain `diagnostic_only` — not sufficient for production inference.

## 28. Inference adapter requirements

Placebo/rank, jackknife, bootstrap, and studentized statistic paths require `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001` adapter maturity (`candidate_after_adapter`).

## 29. Null calibration requirements

Null calibration (`null_fpr_gate`, `coverage_replay`) is required before placebo-rank or studentized inference promotion hypotheses.

## 30. DGP simulation requirements

DGP simulation coverage (`DGP-SDID-001`, `DGP-ES-007`, `DGP-CP-002`) is required before promotion evidence.

## 31. Failure-registry blockers

`FM-ES-009`, `FM-CP-005`, and related failure modes must be consulted. Unresolved failure modes block implementation.

## 32. Method disagreement checks

Synthetic DID must be compared against SCM, DID, AugSynth, and TBRRidge before promotion. Unresolved disagreement is a **required warning**.

## 33. Single-treated Synthetic DID path

Single-treated Synthetic DID is `candidate_after_design` — the primary near-term implementation path after all gates pass.

## 34. Multi-treated Synthetic DID boundary

Multi-treated Synthetic DID is `research_only` until dependence/multiplicity handling is validated.

## 35. Treated-set Synthetic DID boundary

Treated-set Synthetic DID is `research_only` until dependence/multiplicity handling is validated.

## 36. Multicell/shared-control boundary

Multicell/shared-control Synthetic DID is **blocked** until `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` completes.

## 37. Allowed current uses

- Implementation-readiness planning and scout research
- Diagnostic readout specification (not execution)
- Contract definition for unit weights, time weights, and tuning
- Evidence collection for DGP simulation and assignment stress
- Method disagreement analysis against SCM, DID, AugSynth, TBRRidge

## 38. Forbidden current uses

- Synthetic DID implementation (by this artifact)
- Production p-values
- Causal confidence intervals
- TrustReport production authorization
- CalibrationSignal ingestion
- MMM ingestion
- LLM decisioning
- Live API production endpoints
- Scheduler production runs
- Budget optimization
- Production inference authorization
- Multi-treated/treated-set/multicell production claims without dependence handling

## 39. Required future artifacts

| Artifact | Role |
|---|---|
| `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001` | **Immediate next** — retire/replace execution |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Selection-gate implementation |
| `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` | Release gate before any authorization |

## 40. Updated roadmap sequence

✅ `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` → ✅ **`SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001`** → **`METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001`**

## 41. Downstream boundary

This readiness plan does not implement Synthetic DID.
This readiness plan does not authorize Synthetic DID production inference.
This readiness plan does not authorize production p-values.
This readiness plan does not authorize causal confidence intervals.
This readiness plan does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.
Downstream work remains paused.

## 42. Validation

Harness: `panel_exp/validation/synthetic_did_implementation_readiness_plan_001.py`  
Summary: `docs/track_d/archives/SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001_summary.json`  
Tests: `tests/validation/test_synthetic_did_implementation_readiness_plan_001.py`

## 43. Verdict

**`synthetic_did_implementation_readiness_plan_defined_no_downstream_authorization`**

Synthetic DID is an implementation-readiness candidate only. All authorization flags remain **false**. Recommended next artifact: **`METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001`**.
