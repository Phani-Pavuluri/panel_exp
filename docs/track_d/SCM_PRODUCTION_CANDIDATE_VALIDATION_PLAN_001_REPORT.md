# SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001 Report

## 1. Purpose

This validation-only artifact defines exactly what SCM must pass before any future artifact can consider production-compatible inference. SCM is the first production-compatible candidate lane per `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`, but remains **gated**.

This plan defines metadata-only validation requirements. It is **not** a production inference implementation.

## 2. Why SCM is first production-candidate lane

Per `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` and `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`, SCM is the strongest near-term production-compatible candidate. Donor-pool diagnostics, pre-period fit, placebo/null calibration infrastructure, and promotion gate audits are most mature for SCM relative to other families.

## 3. Evidence base

Evidence consumed from:

- `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`
- `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`
- `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
- `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`

## 4. SCM current status

SCM is `production_candidate_gated`. Point estimates alone are **not sufficient** for production inference. Production inference, p-values, and causal CIs remain **unauthorized**.

## 5. Validation status definitions

| Status | Meaning |
|---|---|
| `required_blocker` | Must pass before any promotion hypothesis |
| `required_warning` | Must be reviewed; may block promotion if severe |
| `candidate_after_validation` | Advancement requires validation evidence |
| `candidate_after_adapter` | Advancement requires statistic adapter maturity |
| `candidate_after_null_calibration` | Advancement requires null calibration evidence |
| `candidate_after_simulation` | Advancement requires DGP simulation coverage |
| `diagnostic_only` | Diagnostic readout only |
| `blocked` | Production path blocked |
| `research_required` | Research handling required before promotion |

## 6. Required validation areas

All SCM promotion paths require validation across: point-estimate validity, donor pool eligibility, donor support/convex hull, pre-period fit, pre-period trend stability, outcome-scale compatibility, sparse/count/rate outcomes, assignment/design validity, assignment-generator stress, single-treated SCM, multi-treated SCM, treated-set placebo, unit jackknife, placebo rank inference, studentized placebo statistic, null calibration, DGP simulation coverage, failure-registry blockers, method disagreement checks, multicell/shared-control boundary, and release-gate boundary.

## 7. Donor support and convex-hull validation

Donor support (`OPD-DONOR-001`) and convex-hull diagnostics (`OPD-DS-005`) are **required blockers** before promotion. Donor pool eligibility must be confirmed.

## 8. Pre-period fit and trend validation

Pre-period fit quality (`OPD-PF-001`, `OPD-PF-003`) and trend stability (`OPD-PF-002`) are **required blockers**. Poor pre-period fit blocks promotion.

## 9. Outcome-scale validation

Outcome-scale compatibility is a **required warning**. Sparse/count/rate outcomes require additional outcome-scale DGP coverage.

## 10. Assignment/design validation

Assignment/design validity is a **required blocker**. Unknown or deterministic assignment without stress compatibility blocks promotion.

## 11. Assignment-generator stress validation

Assignment-generator stress compatibility (`ST-AD-001`, `ST-AD-009`, `ST-AD-010`) is a **required blocker** per `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`.

## 12. Treated-set placebo adapter requirements

Treated-set placebo requires `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001` adapter readiness and null calibration before promotion.

## 13. Studentized statistic adapter requirements

Studentized placebo statistic paths require adapter contract maturity and null calibration evidence.

## 14. Null calibration requirements

Null calibration (`null_fpr_gate`, `coverage_replay`) is required before placebo-rank or studentized inference promotion hypotheses.

## 15. DGP simulation requirements

DGP simulation coverage (`DGP-SCM-001`, `DGP-ES-007`, `DGP-CP-002`) is required before promotion evidence.

## 16. Failure-registry blockers

`FM-ES-001`, `FM-CP-003`, `FM-CP-004`, and `FM-INF-009` must be consulted. Unresolved failure modes block promotion.

## 17. Single-treated SCM path

Single-treated SCM is `candidate_after_validation` — the primary near-term promotion path after all gates pass.

## 18. Multi-treated SCM boundary

Multi-treated SCM is `research_required` until dependence/multiplicity handling is validated.

## 19. Multicell/shared-control boundary

Multicell/shared-control SCM is **blocked** until `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` completes.

## 20. Allowed current uses

- Diagnostic SCM point readouts
- Donor-support and pre-period fit diagnostics
- Placebo/null calibration research
- Single-treated validation planning

## 21. Forbidden current uses

- Production inference, p-values, causal CIs
- TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, budget optimization
- Multi-treated/multicell production claims without dependence validation

## 22. Required future artifacts

1. `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001`
2. `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`
3. `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
4. `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001`

## 23. Updated roadmap sequence

1. ✅ `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`
2. ✅ `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` (this plan)
3. **`MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001`** (immediate next)

## 24. Downstream boundary

This validation plan does not authorize production inference.
This validation plan does not authorize production p-values.
This validation plan does not authorize causal confidence intervals.
This validation plan does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 25. Validation

Harness: `panel_exp/validation/scm_production_candidate_validation_plan_001.py`
Tests: `tests/validation/test_scm_production_candidate_validation_plan_001.py`

## 26. Verdict

`scm_production_candidate_validation_plan_defined_no_downstream_authorization`

**Next:** `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001`

## Summary JSON location

[`docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_summary.json`](archives/SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_summary.json)
