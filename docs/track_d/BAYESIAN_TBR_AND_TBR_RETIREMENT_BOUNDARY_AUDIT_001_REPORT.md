# BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001 Report

## 1. Purpose

This validation-only audit defines boundary and retirement posture for Bayesian TBR and classic/aggregate TBR. It decides which TBR-family paths remain diagnostic/research-only, which are retire/replace candidates, and what evidence would be required before any future promotion.

This audit defines metadata-only routing. It is **not** a production inference implementation.

## 2. Why this boundary audit exists

Per `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`, TBR aggregate/classic TBR is retire/block likely and Bayesian TBR is posterior diagnostic/research-only. Failure modes `FM-ES-007`, `FM-ES-008`, and `FM-INF-008` document aggregate overclaim and posterior-as-causal-CI misuse. This audit consolidates TBR-family boundaries without reversing `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`.

## 3. Current evidence base

Evidence consumed from:

- `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
- `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
- `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
- `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`

## 4. Classic TBR current status

Classic TBR point estimates may support diagnostic readouts. Aggregate/global overclaim paths are **blocked** or **retire/replace**. Production inference, p-values, and causal CIs remain **unauthorized**.

## 5. Bayesian TBR current status

Bayesian TBR may remain **posterior-diagnostic/research-only** unless future calibration/replay evidence proves causal coverage. Production inference remains **unauthorized**.

## 6. Why posterior intervals are not causal confidence intervals

Posterior/credible intervals reflect Bayesian uncertainty under the model and prior. They are not governed causal confidence intervals (`FM-ES-008`, `FM-INF-008`). Mislabeling credible intervals as causal CIs is **blocked**.

## 7. Classic/aggregate TBR overclaim risks

Aggregate geometry mismatch (`FM-ES-007`) and global causal overclaim (`FM-INF-011`) block promotion. Geo-aggregate readouts without explicit estimand remediation are retire/replace candidates.

## 8. Bayesian TBR posterior diagnostic boundary

Posterior diagnostics, posterior intervals, and PPC paths are `posterior_diagnostic_only` or `research_only`. Prior sensitivity requires remediation before any promotion hypothesis.

## 9. Calibration/replay evidence required before promotion

`candidate_after_calibration_replay` paths require posterior coverage replay and null FPR gates before any promotion hypothesis. Simulation DGP coverage is prerequisite.

## 10. Observed diagnostic dependencies

All paths require observed-panel diagnostics (`OPD-PF-*`, `OPD-DS-*`, `OPD-AD-*`, `OPD-MC-*`, `OPD-OM-*`) before method selection.

## 11. DGP coverage dependencies

`DGP-ES-007`, `DGP-ES-008`, `DGP-CP-002`, and outcome-scale DGPs are required before promotion hypotheses.

## 12. Design-assignment stress dependencies

Placebo and randomization paths require `ST-AD-009` and `ST-AD-010` compatibility.

## 13. Failure-registry dependencies

`FM-ES-007`, `FM-ES-008`, `FM-INF-008`, `FM-DA-009`, and `FM-CP-004` must be consulted.

## 14. Multicell/shared-control boundary

TBR-family multicell inference is blocked or research-only without dependence/multiplicity handling per `MULTICELL_MAX_T_RESEARCH_SCOUT_001`.

## 15. TBRRidge boundary preservation

`TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001` decisions are preserved. This audit must not reverse TBRRidge remediation/retirement conclusions. TBR and TBRRidge diagnostic lanes remain separate.

## 16. Retire/replace candidates

- Classic/aggregate global TBR
- TBR vs SCM/AugSynth for causal claims (SCM is stronger near-term candidate)

## 17. Research-only candidates

- Classic TBR point/bootstrap research paths
- Bayesian posterior interval research
- TBR vs DID comparison research
- Multicell TBR-family paths

## 18. Required future artifacts

1. `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`
2. `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`

## 19. Updated roadmap sequence

1. ✅ `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
2. ✅ `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001` (this audit)
3. **`TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`** (immediate next)
4. `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`

## 20. Downstream boundary

This audit does not authorize production inference.
This audit does not authorize production p-values.
This audit does not authorize causal confidence intervals.
This audit does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 21. Validation

Harness: `panel_exp/validation/bayesian_tbr_and_tbr_retirement_boundary_audit_001.py`
Tests: `tests/validation/test_bayesian_tbr_and_tbr_retirement_boundary_audit_001.py`

## 22. Verdict

`bayesian_tbr_and_tbr_retirement_boundary_audit_completed_no_downstream_authorization`

**Next:** `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`

## Summary JSON location

[`docs/track_d/archives/BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001_summary.json`](archives/BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001_summary.json)
