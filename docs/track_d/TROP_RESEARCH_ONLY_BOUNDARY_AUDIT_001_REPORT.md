# TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001 Report

## 1. Purpose

This validation-only audit defines the research-only boundary for TROP (triply robust / treatment-response optimization policy estimator family). It decides whether TROP remains research-only, which paths deserve future scouting/remediation, what evidence would be required for promotion, and which paths are retire/replace candidates.

This audit defines metadata-only routing. It is **not** a TROP implementation.

## 2. Why this boundary audit exists

Per `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001` and `TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001`, TROP is parked as a future candidate estimator family with `research_only` status today. Existing TROP code remains skipped in batch validation. Failure modes `FM-ES-009` and `FM-INF-012` document triply-robust overclaim and heterogeneous-effect misuse. This audit consolidates TROP boundaries after `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`.

## 3. Current TROP evidence base

Evidence consumed from:

- `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`
- `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
- `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
- `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
- `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
- `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`

## 4. TROP current status

TROP remains **research-only** unless future calibration/replay and simulation evidence proves otherwise. Production inference, p-values, causal CIs, recommendations, budget allocation, and decisioning remain **unauthorized**.

## 5. Allowed research-only uses

- Point/score diagnostic readouts
- Method scout exploration
- Simulation/stress-test planning
- Method comparison research against SCM, DID, Synthetic DID, and TBRRidge
- Multicell research exploration (without production inference)
- Calibration/replay planning (not execution authorization)

## 6. Forbidden production uses

- Production inference and causal claims
- Production p-values and causal confidence intervals
- Production policy recommendations
- Budget/allocation recommendations
- Production decisioning outputs
- TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, budget optimization

## 7. Treatment-response ranking risks

Treatment-response ranking without design-valid causal evidence risks heterogeneous overclaim (`FM-INF-012`, `FM-DA-010`). Ranking paths are **research-only** or **blocked** for production.

## 8. Policy recommendation risks

Policy recommendation paths conflate optimization with causal identification. Production policy outputs are **blocked**. Research exploration only.

## 9. Budget/allocation risks

Budget/allocation recommendation implies budget optimization, which is unauthorized. Paths are **blocked** or **method_scout_candidate** for future evidence only.

## 10. Heterogeneous-effect claim risks

Heterogeneous-effect claims require design-valid causal evidence before any promotion hypothesis. Without such evidence, paths are **blocked**.

## 11. Observed diagnostic dependencies

All paths require observed-panel diagnostics (`OPD-PF-*`, `OPD-DS-*`, `OPD-AD-*`, `OPD-MC-*`, `OPD-OM-*`) before method selection.

## 12. DGP coverage dependencies

`DGP-ES-009`, `DGP-CP-003`, `DGP-HT-002`, `DGP-MC-001`, and `DGP-OM-001` are required before promotion hypotheses.

## 13. Design-assignment stress dependencies

Assignment stress paths require `ST-AD-001`, `ST-AD-009`, `ST-AD-010`, `ST-AD-011`, and `ST-AD-012` compatibility.

## 14. Failure-registry dependencies

`FM-ES-009`, `FM-INF-012`, `FM-DA-009`, `FM-DA-010`, and `FM-CP-005` must be consulted.

## 15. Calibration/replay requirements

`candidate_after_calibration_replay` paths require null FPR gates and coverage replay before any promotion hypothesis.

## 16. Simulation requirements

`candidate_after_simulation` paths require DGP coverage and assignment stress completion before promotion evidence.

## 17. Multicell/shared-control boundary

TROP multicell/shared-control use is **blocked** or **research-only** without dependence/multiplicity handling per `MULTICELL_MAX_T_RESEARCH_SCOUT_001`.

## 18. Comparison against SCM

TROP must be compared against SCM before any promotion. SCM remains a stronger near-term candidate for causal panel claims.

## 19. Comparison against DID

TROP must be compared against DID design-based benchmarks before promotion.

## 20. Comparison against Synthetic DID

TROP must be compared against Synthetic DID per `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001` scout conclusions.

## 21. Comparison against TBRRidge

TROP must be compared against TBRRidge. `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001` decisions are preserved; this audit does not reverse them.

## 22. Retire/replace candidates

- Production decisioning/recommendation paths
- TROP causal overclaim without triply-robust validation

## 23. Promotion hypothesis

No promotion hypothesis is authorized today. Future promotion requires calibration/replay, simulation stress, method comparisons, and `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`.

## 24. Updated roadmap sequence

1. ✅ `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`
2. ✅ `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001` (this audit)
3. **`METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`** (immediate next)

## 25. Downstream boundary

This audit does not implement TROP.
This audit does not authorize production inference.
This audit does not authorize production p-values.
This audit does not authorize causal confidence intervals.
This audit does not authorize production recommendations, budget allocation, or decisioning.
This audit does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 26. Validation

Harness: `panel_exp/validation/trop_research_only_boundary_audit_001.py`
Tests: `tests/validation/test_trop_research_only_boundary_audit_001.py`

## 27. Verdict

`trop_research_only_boundary_audit_completed_no_downstream_authorization`

**Next:** `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`

## Summary JSON location

[`docs/track_d/archives/TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001_summary.json`](archives/TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001_summary.json)
