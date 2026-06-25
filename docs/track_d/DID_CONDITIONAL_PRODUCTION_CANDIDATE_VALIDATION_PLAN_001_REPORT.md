# DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001 Report

## 1. Purpose

This validation-only artifact defines exactly when DID is eligible as a **conditional production-candidate** method and when it must remain diagnostic-only, research-only, or blocked. The registry contains **87 validation rows** across **29 validation areas** (`failed_scenarios: []`).

This plan defines metadata-only validation requirements. It is **not** a production inference implementation.

## 2. Why DID is conditional, not generally production-ready

Per `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`, `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001`, `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`, and `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`, DID is a **conditional production-candidate only under eligible designs**. DID point estimates do **not** authorize production inference. Parallel-trend support, assignment validity, cluster adequacy, outcome-scale compatibility, and method disagreement checks must pass before any future promotion hypothesis.

DID is **not** generally production-ready because:

- Invalid or unknown assignment cannot be repaired by bootstrap or permutation inference.
- Parallel-trend violations and pretrend failures block promotion.
- Staggered treatment and TWFE overclaim paths remain blocked or research-only until explicitly validated.
- Multicell/shared-control DID remains blocked without dependence/multiplicity handling.
- Production inference, p-values, and causal CIs remain **unauthorized**.

## 3. Prior-work reconciliation

| Prior artifact | Carried forward |
|---|---|
| `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` | Method disagreement vs AugSynth |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001` | DID routing and eligibility gates |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | DID backlog items |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell/shared-control blockers |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | Method disagreement vs SCM |
| `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001` | Bootstrap cannot fix invalid design/trends |
| `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001` | Assignment stress compatibility |
| `METHOD_FAILURE_MODE_REGISTRY_001` | Failure-mode blockers |
| `SIMULATION_DGP_COVERAGE_PLAN_001` | DGP evidence requirements |
| `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001` | Pretrend, fit, overlap diagnostics |
| `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001` | DID inference suitability boundaries |

Resolved audits are not re-implemented; unresolved DID blockers are encoded as validation requirements.

## 4. Relationship to OPEN_INVESTIGATIONS_001

`INV-DID-CONDITIONAL-PRODUCTION-CANDIDATE-VALIDATION-PLAN-001` is resolved by this artifact. Open investigations for Synthetic DID implementation readiness, selection-gate implementation, method-family retire/replace, and production authorization release gate remain **PLANNED**. Investigation resolution does **not** imply production readiness.

## 5. Relationship to PRODUCTION_READINESS_BACKLOG_LEDGER_001

DID backlog rows (`did_conditional_production_candidate_validation`, `did_parallel_trend_validation`, `did_cluster_suitability`, `did_bootstrap_boundary`, etc.) map directly to validation areas in this plan.

## 6. Relationship to selection-gate requirements

Per `routing_did_conditional_candidate`, DID routes to conditional-candidate validation only when design, trend, cluster, and outcome eligibility pass observed diagnostics and assignment stress. Point estimates alone do not satisfy selection-gate promotion. This plan defines the evidence those routes require.

## 7. Evidence base

- `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
- `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001`
- `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`
- `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`
- `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001`
- `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
- `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`

## 8. DID current status

DID is **`conditional_candidate_gated`**. Point estimates are permitted for diagnostic/research readout only. DID production inference, production p-values, and causal confidence intervals remain **unauthorized**.

## 9. Validation status definitions

| Status | Meaning |
|---|---|
| `required_blocker` | Must pass before any promotion hypothesis |
| `required_warning` | Must be reviewed; may block promotion if severe |
| `conditional_candidate` | Eligible only under validated design/trend/cluster conditions |
| `candidate_after_validation` | Advancement requires validation evidence |
| `candidate_after_adapter` | Advancement requires statistic adapter maturity |
| `candidate_after_null_calibration` | Advancement requires null calibration evidence |
| `candidate_after_simulation` | Advancement requires DGP simulation coverage |
| `diagnostic_only` | Diagnostic readout only |
| `research_only` | Research handling required before promotion |
| `blocked` | Production path blocked |

## 10. Eligibility type definitions

| Type | Meaning |
|---|---|
| `design_eligibility` | Assignment, control comparability, treated/control balance |
| `trend_eligibility` | Parallel trends, pre-period stability, event-study/pretrend |
| `outcome_eligibility` | Outcome scale, sparse/count/rate, missing data |
| `cluster_eligibility` | Cluster count, dependence, serial correlation |
| `inference_eligibility` | Bootstrap, cluster bootstrap, placebo, permutation |
| `simulation_requirement` | DGP simulation coverage |
| `assignment_stress_requirement` | Assignment-generator stress compatibility |
| `multicell_boundary` | Multicell/shared-control dependence boundary |
| `release_gate_boundary` | Production authorization release gate |

## 11. Required validation areas

All DID conditional promotion paths require validation across: point-estimate eligibility, parallel-trend support, pre-period trend stability, event-study/pretrend diagnostics, assignment/design validity, assignment-generator stress, control-group comparability, treated/control balance, cluster count adequacy, cluster dependence, serial correlation, outcome-scale compatibility, sparse/count/rate outcomes, missing data sensitivity, post-period shock sensitivity, staggered treatment boundary, TWFE overclaim boundary, bootstrap suitability, cluster/bootstrap inference boundary, placebo/pre-period falsification, randomization/permutation candidate, DGP simulation coverage, failure-registry blockers, method disagreement checks (SCM, AugSynth, Synthetic DID, TBRRidge), multicell/shared-control boundary, and release-gate boundary.

## 12. Design and assignment eligibility

Assignment/design validity (`ST-AD-001`, `ST-AD-009`) is a **required blocker**. Unknown or deterministic assignment without stress compatibility blocks promotion. Assignment-generator stress compatibility is **required** before promotion.

## 13. Parallel-trend validation

Parallel-trend support (`OPD-PF-002`, `parallel_trend_support`) is a **required blocker**. Parallel-trend failure blocks any promotion hypothesis.

## 14. Pre-period trend and event-study diagnostics

Pre-period trend stability (`OPD-PF-002`, `OPD-PF-003`) and event-study/pretrend diagnostics are **required blockers**. Pretrend violations block promotion.

## 15. Control-group comparability

Control-group comparability and treated/control balance are required. Control comparability under eligible designs is `candidate_after_validation` — conditional production-candidate path only after all gates pass.

## 16. Cluster and dependence requirements

Cluster count adequacy and cluster dependence structure are **required blockers**. Too few clusters or unhandled cluster dependence block inference promotion.

## 17. Serial-correlation requirements

Serial correlation handling is a **required warning**. Unhandled serial correlation may block inference promotion.

## 18. Outcome-scale requirements

Outcome-scale compatibility and sparse/count/rate outcome handling are **required warnings**. Incompatible outcome scales require additional DGP coverage (`DGP-DID-001`, `DGP-CP-002`).

## 19. Bootstrap suitability boundary

Bootstrap suitability is `conditional_candidate` — eligible only when design, trends, clusters, and outcomes are already valid. Bootstrap does **not** authorize production inference by itself.

## 20. Why bootstrap does not fix invalid design or trends

Per `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`, bootstrap cannot repair invalid assignment, parallel-trend violations, too few clusters, or incompatible outcomes. Resampling invalid designs produces invalid inference.

## 21. Staggered/TWFE boundary

Staggered treatment paths are `research_only`. TWFE overclaim paths are **blocked** until explicitly validated. TWFE must not be treated as a default production path.

## 22. DGP simulation requirements

DGP simulation coverage (`DGP-DID-001`, `DGP-ES-007`, `DGP-CP-002`) is required before promotion evidence. Simulation is `candidate_after_simulation`.

## 23. Failure-registry blockers

`FM-ES-001`, `FM-CP-004`, and related failure modes must be consulted. Unresolved failure modes block promotion.

## 24. Method disagreement checks

DID must be compared against SCM, AugSynth, Synthetic DID, and TBRRidge before promotion. Disagreement without resolution is a **required warning** that may block promotion.

## 25. Multicell/shared-control boundary

Multicell/shared-control DID is **blocked** until `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` dependence/multiplicity handling is implemented and validated.

## 26. Allowed current uses

- DID diagnostic readout under eligible designs
- Conditional research use with explicit gate documentation
- Point-estimate reporting without production inference claims
- Pretrend/event-study diagnostic workflows
- Assignment stress and DGP simulation evidence collection

## 27. Forbidden current uses

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
- TWFE/staggered production claims without validation
- Multicell/shared-control production claims without dependence handling

## 28. Required future artifacts

| Artifact | Role |
|---|---|
| `SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001` | **Immediate next** — Synthetic DID readiness |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Selection-gate implementation |
| `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001` | Retire/replace execution |
| `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` | Release gate before any authorization |

## 29. Updated roadmap sequence

✅ `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` → ✅ **`DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`** → **`SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001`**

## 30. Downstream boundary

This validation plan does not authorize DID production inference.
This validation plan does not authorize production p-values.
This validation plan does not authorize causal confidence intervals.
This validation plan does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.
Downstream work remains paused.

## 31. Validation

Harness: `panel_exp/validation/did_conditional_production_candidate_validation_plan_001.py`  
Summary: `docs/track_d/archives/DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_summary.json`  
Tests: `tests/validation/test_did_conditional_production_candidate_validation_plan_001.py`

## 32. Verdict

**`did_conditional_production_candidate_validation_plan_defined_no_downstream_authorization`**

DID is a conditional production-candidate only under eligible designs. All authorization flags remain **false**. Recommended next artifact: **`SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001`**.
