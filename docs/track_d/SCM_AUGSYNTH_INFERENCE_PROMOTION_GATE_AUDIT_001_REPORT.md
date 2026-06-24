# SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001 Report

## 1. Purpose

This validation-only audit decides what must be true before SCM and AugSynth CVXPY inference can move from diagnostic/restricted research into a future production-compatible candidate lane.

This audit defines metadata-only promotion gates. It is **not** production inference.

## 2. Why SCM/AugSynth are promotion-gate candidates

Per `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`, SCM is the strongest near-term production-compatible candidate (gated), and AugSynth CVXPY requires inference adapter and null calibration remediation. Both families have governed statistic adapter contracts and prior null-calibration lanes, but no family may claim production inference until this promotion gate audit and downstream criteria matrix are satisfied.

## 3. Current evidence base

Evidence consumed from:

- `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
- `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`
- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
- `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`
- `SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001`
- Prior studentized placebo and null-calibration lanes

## 4. SCM current status

SCM point estimates may support diagnostic readouts when donor support and pre-period fit diagnostics pass. SCM is the **strongest near-term candidate** but **production inference, p-values, and causal CIs remain unauthorized**. Unit jackknife is restricted/diagnostic unless null calibrated. Placebo rank requires valid assignment support. Studentized and treated-set placebo require adapter + null calibration.

## 5. AugSynth current status

AugSynth CVXPY point estimates may remain diagnostic/restricted research. **Production inference remains unauthorized.** Jackknife paths are retire/replace candidates unless adapter proves viability. All placebo/studentized paths require statistic adapter, null calibration, donor-support diagnostics, and DGP coverage.

## 6. SCM inference path assessment

| Path | Status |
|------|--------|
| Point estimate | Diagnostic-only; candidate after promotion gate |
| Unit jackknife | Restricted; requires calibration |
| Placebo rank | Null-monitor diagnostic; candidate after null calibration |
| Studentized placebo | Candidate after adapter + null calibration |
| Treated-set placebo | Candidate after adapter + null calibration |
| Multi-treated | Blocked/research until dependence handling |
| Donor-support / convex hull | Blocker when support poor |
| Pre-period fit / trend | Blocker when fit poor |
| Sparse/count/rate | Blocked without DGP coverage |
| Multicell/shared-control | Blocked/research until multiplicity handled |

## 7. AugSynth inference path assessment

| Path | Status |
|------|--------|
| Point estimate | Diagnostic/restricted research |
| Jackknife | Retire/replace or candidate after adapter |
| Placebo/rank | Candidate after adapter + null calibration |
| Studentized adapter | Candidate after adapter + null calibration |
| Donor extrapolation | Promotion blocker |
| Method disagreement | Diagnostic warning or block |
| Scale bridge | Remediation required |
| Sparse/count/rate | Blocked without simulation |
| Multicell/shared-control | Blocked/research |

## 8. Statistic-adapter requirements

All studentized, treated-set, and AugSynth inference paths require `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001` compliance. No promotion without governed adapter.

## 9. Null-calibration requirements

Placebo, studentized, jackknife, and treated-set paths require null FPR and coverage gates on appropriate DGPs before any candidate-lane promotion.

## 10. Observed diagnostic dependencies

All paths require observed-panel diagnostics (`OPD-PF-*`, `OPD-DS-*`, `OPD-AD-*`, `OPD-MC-*`, `OPD-OM-*`) before method selection or promotion.

## 11. DGP coverage dependencies

Simulation DGP coverage (`DGP-CP-002`, `DGP-INF-*`, `DGP-MC-*`, `DGP-OM-*`) is required before inference promotion.

## 12. Design-assignment stress dependencies

Placebo and randomization paths require `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001` compatibility (`ST-AD-009`, `ST-AD-010`).

## 13. Failure-registry dependencies

All promotion paths must consult `METHOD_FAILURE_MODE_REGISTRY_001` (`FM-CP-004` and path-specific modes).

## 14. Donor-support and extrapolation risks

Poor donor support, convex-hull violations, and AugSynth extrapolation are promotion blockers (`FM-DS-006`, `FM-DS-007`).

## 15. Pre-period fit and trend risks

Poor pre-period fit and trend stress block SCM promotion (`FM-PF-001`, `FM-PF-003`).

## 16. SCM/AugSynth disagreement gate

SCM/AugSynth disagreement must trigger diagnostic warning or block promotion (`FM-ES-005`). Large disagreement blocks promotion until resolved.

## 17. Multicell/shared-control boundary

Multi-treated and multicell/shared-control inference remain blocked or research-only until dependence and multiplicity handling exist per `MULTICELL_MAX_T_RESEARCH_SCOUT_001`.

## 18. Promotion candidate paths

- SCM point after full promotion gate evidence
- SCM studentized placebo after adapter + null calibration
- SCM treated-set placebo after adapter + null calibration
- AugSynth studentized after adapter + null calibration
- Disagreement-gate satisfied promotion candidate

## 19. Blocked paths

- SCM/AugSynth production inference globally
- SCM/AugSynth production p-values and causal CIs
- Multi-treated/multicell without dependence handling
- Placebo without valid assignment support
- Studentized paths without adapter
- Donor extrapolation and poor support

## 20. Required future artifacts

1. `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
2. `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`
3. `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`
4. `SCM_AUGSYNTH_DISAGREEMENT_DIAGNOSTICS_001` (when disagreement triggered)

## 21. Updated roadmap sequence

1. ✅ `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
2. ✅ `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001` (this audit)
3. **`SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`** (immediate next)
4. `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`
5. `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`

## 22. Downstream boundary

This audit does not authorize production inference.
This audit does not authorize production p-values.
This audit does not authorize causal confidence intervals.
This audit does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 23. Validation

Harness: `panel_exp/validation/scm_augsynth_inference_promotion_gate_audit_001.py`
Tests: `tests/validation/test_scm_augsynth_inference_promotion_gate_audit_001.py`

## 24. Verdict

`scm_augsynth_inference_promotion_gate_audit_completed_no_downstream_authorization`

**Next:** `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`

## Summary JSON location

[`docs/track_d/archives/SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001_summary.json`](archives/SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001_summary.json)
