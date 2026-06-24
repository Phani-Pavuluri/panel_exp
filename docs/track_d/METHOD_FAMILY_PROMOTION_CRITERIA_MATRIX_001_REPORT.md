# METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001 Report

## 1. Purpose

This validation-only artifact consolidates all prior method-control, diagnostic, DGP, failure-mode, assignment-stress, estimator-specific, and boundary audits into one explicit promotion criteria matrix. It defines what is required for each method family to move into production-compatible candidate, remediation-required, diagnostic-only, research-only, retire/replace, or blocked posture.

This matrix defines metadata-only routing. It is **not** a production inference implementation.

## 2. Why this matrix exists

Per `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001` and the completed estimator-specific gate audits (`SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`, `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`, `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`, `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`), no family may advance without explicit promotion criteria. This matrix is the consolidated control layer before any production compatibility workplan.

## 3. Evidence base

Evidence consumed from:

- `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`
- `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`
- `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
- `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
- `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
- `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
- `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
- `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`

## 4. Promotion status definitions

| Status | Meaning |
|---|---|
| `production_candidate_gated` | Strongest near-term candidate; all gates must pass before promotion |
| `remediation_required` | Known blockers; remediation plan required before advancement |
| `diagnostic_only` | Diagnostic readout only; no production inference |
| `research_only` | Research/scout exploration only |
| `retire_or_replace` | Retire or replace path; exit criteria defined |
| `blocked` | Production path blocked |
| `candidate_after_simulation` | Advancement requires simulation/DGP evidence |
| `candidate_after_adapter` | Advancement requires inference adapter maturity |
| `candidate_after_null_calibration` | Advancement requires null calibration evidence |
| `candidate_after_calibration_replay` | Advancement requires calibration/replay coverage |

## 5. Required criteria dimensions

All families are evaluated across: estimand clarity, assignment/design validity, observed-panel diagnostics, DGP simulation coverage, failure-registry review, assignment-generator stress compatibility, inference adapter availability, null calibration/replay evidence, multiplicity/dependence handling, outcome-scale compatibility, donor support/overlap, pre-period fit/trend stability, method disagreement handling, allowed current use, forbidden current use, promotion evidence, retirement/replace criteria, and downstream authorization boundary.

## 6. Method-family criteria matrix

The harness defines a family × dimension matrix with per-row required conditions, artifacts, failure modes, and promotion evidence.

## 7. SCM criteria

SCM is the **strongest near-term production-compatible candidate**, but remains **gated**. Requires observed diagnostics, DGP coverage, null calibration, donor support, pre-period fit, and failure-registry review before any promotion hypothesis.

## 8. AugSynth criteria

AugSynth CVXPY remains **diagnostic/restricted research** until inference adapter, null calibration, donor-support diagnostics, and DGP coverage mature. `candidate_after_adapter` and `candidate_after_null_calibration` paths defined.

## 9. DID criteria

DID is a **conditional candidate only** under strong design/trend/cluster/outcome conditions per `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`.

## 10. Synthetic DID criteria

Synthetic DID is an **implementation/scout candidate only** after suitability evidence per `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`. `candidate_after_simulation` required.

## 11. TBRRidge criteria

TBRRidge remains **diagnostic-only** unless future remediation proves otherwise per `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`.

## 12. Classic/Aggregate TBR criteria

Classic/aggregate TBR overclaim paths are **blocked** or **retire/replace** candidates per `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`.

## 13. Bayesian TBR criteria

Bayesian TBR remains **posterior-diagnostic/research-only** until calibration/replay evidence proves causal coverage. Posterior intervals are not causal CIs.

## 14. TROP criteria

TROP remains **research-only** unless future simulation and calibration/replay evidence prove otherwise per `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`.

## 15. Multicell/shared-control criteria

Multicell/shared-control is a **cross-family blocker** until dependence/multiplicity handling is validated per `MULTICELL_MAX_T_RESEARCH_SCOUT_001`.

## 16. Cross-family blockers

- Multicell dependence/multiplicity unhandled
- Missing observed diagnostics
- Incomplete DGP coverage
- Unconsulted failure-registry modes
- Assignment stress incompatibility
- Downstream authorization (all families: paused)

## 17. Promotion evidence requirements

All promotion hypotheses require: observed diagnostics, DGP coverage, failure-registry review, assignment-stress compatibility. Adapter, null calibration, and multiplicity/dependence evidence required when applicable.

## 18. Remediation requirements

Families with `remediation_required` status must complete family-specific remediation before advancing (AugSynth adapter, TBRRidge inference, classic TBR aggregate geometry, multicell dependence).

## 19. Retire/replace criteria

Classic/aggregate TBR and causal overclaim paths have explicit retirement/exit criteria. `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001` is the recommended execution artifact.

## 20. Allowed current uses

Per-family diagnostic readouts, research exploration, method comparison, simulation planning, and calibration/replay planning (not authorization).

## 21. Forbidden current uses

Production inference, p-values, causal CIs, TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, budget optimization, production decisioning.

## 22. Recommended next artifacts

1. `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`
2. `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
3. `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001`

## 23. Updated roadmap sequence

1. ✅ `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`
2. ✅ `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` (this matrix)
3. **`PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`** (immediate next)

## 24. Downstream boundary

This matrix does not authorize production inference.
This matrix does not authorize production p-values.
This matrix does not authorize causal confidence intervals.
This matrix does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 25. Validation

Harness: `panel_exp/validation/method_family_promotion_criteria_matrix_001.py`
Tests: `tests/validation/test_method_family_promotion_criteria_matrix_001.py`

## 26. Verdict

`method_family_promotion_criteria_matrix_defined_no_downstream_authorization`

**Next:** `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`

## Summary JSON location

[`docs/track_d/archives/METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001_summary.json`](archives/METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001_summary.json)
