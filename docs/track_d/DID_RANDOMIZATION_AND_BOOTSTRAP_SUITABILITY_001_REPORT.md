# DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001 Report

## 1. Purpose

This validation-only audit decides when DID-related paths are suitable for design/randomization inference candidates, bootstrap candidates, diagnostic-only, sensitivity-only, restricted research, blocked, retire/replace, or future validation only.

This audit defines metadata-only routing. It does not run production inference.

## 2. Evidence base

Evidence consumed from:

- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
- `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
- Prior DID bootstrap remediation lanes and `did_interval_policy.py`

## 3. Current DID status

DID point estimates may remain **diagnostic-only** when parallel-trend and pre-period diagnostics pass. All production inference paths (randomization, permutation, bootstrap, cluster bootstrap, cluster robust) remain **blocked** or **non-production**.

## 4. Known DID failure modes

Key failure-mode links: `FM-ES-005`, `FM-DA-001`, `FM-DA-002`, `FM-DA-004`–`FM-DA-006`, `FM-DA-009`, `FM-DA-010`, `FM-INF-003`, `FM-INF-006`, `FM-PF-003`, `FM-PS-004`, `FM-PS-006`, `FM-PS-010`, `FM-OM-003`–`FM-OM-006`, `FM-TE-004`.

## 5. Randomization/permutation suitability

Randomization and permutation require known assignment mechanism and non-degenerate assignment support validated by design stress tests. Neither path is production-authorized.

## 6. Bootstrap/cluster-bootstrap suitability

Bootstrap and cluster bootstrap require dependence/outcome/DGP validation and null calibration. Bootstrap cannot substitute for invalid assignment. Cluster bootstrap and cluster-robust paths are blocked when clusters are too few.

## 7. Parallel-trend and pre-period dependencies

Parallel-trend violations, poor pre-period fit, and short pre-periods block promotion or route to sensitivity/diagnostic-only status.

## 8. Small-N / few-cluster risks

Small-N panels and too-few-clusters block DID inference promotion.

## 9. Staggered timing risks

Staggered activation requires explicit estimand research; naive TWFE is blocked.

## 10. Outcome-scale risks

Sparse/count/binary/rate outcomes require explicit outcome-scale diagnostics and DGP coverage.

## 11. Multicell/shared-control risks

Shared-control dependence, winner-selection risk, and pooled estimand ambiguity require multiplicity research before promotion.

## 12. Observed diagnostic dependencies

All DID paths require observed-panel diagnostics before method selection or promotion.

## 13. DGP coverage dependencies

Bootstrap, outcome-scale, and null-calibration paths require `SIMULATION_DGP_COVERAGE_PLAN_001` triggers.

## 14. Failure-registry links

All DID routing must consult `METHOD_FAILURE_MODE_REGISTRY_001`.

## 15. Design-assignment stress-test dependencies

Randomization and permutation paths require `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001` compatibility.

## 16. Final decision table

See `panel_exp/validation/did_randomization_bootstrap_suitability_001.py` for the full audit registry (≥50 rows).

## 17. Downstream boundary

This audit does not authorize production inference.
This audit does not authorize production p-values.
This audit does not authorize causal confidence intervals.
This audit does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 18. Validation

Harness: `panel_exp/validation/did_randomization_bootstrap_suitability_001.py`
Tests: `tests/validation/test_did_randomization_bootstrap_suitability_001.py`

## 19. Verdict

`did_randomization_and_bootstrap_suitability_completed_no_downstream_authorization`

**Next:** `MULTICELL_MAX_T_RESEARCH_SCOUT_001`

## Summary JSON location

[`docs/track_d/archives/DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001_summary.json`](archives/DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001_summary.json)
