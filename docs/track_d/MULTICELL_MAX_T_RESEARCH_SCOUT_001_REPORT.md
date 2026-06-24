# MULTICELL_MAX_T_RESEARCH_SCOUT_001 Report

## 1. Purpose

This validation-only research scout decides which multiplicity and dependence approaches are plausible future candidates for multicell GeoX inference, and which paths remain blocked, diagnostic-only, research-only, or require remediation.

This scout defines metadata-only routing. It is **not** an implementation of production max-T or stepdown inference.

## 2. Why multicell/shared-control inference is cross-cutting

Multicell and shared-control geometries induce cross-cell dependence through overlapping donor pools, correlated counterfactual errors, and joint null structure. Evidence from `D5-TRUST-MULTICELL-PERCELL-INFERENCE-001` shows familywise type-I ~0.272 under naive per-cell readouts with cross-cell estimate correlation ~0.901. No estimator family (SCM, AugSynth, DID, TBRRidge, Synthetic DID) may claim production-compatible family-level evidence until dependence is modeled or calibrated and multiplicity paths are validated.

## 3. Current evidence base

Evidence consumed from:

- `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`
- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
- `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
- `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
- `D5-TRUST-MULTICELL-PERCELL-INFERENCE-001`
- `MULTICELL-CELL-RELATIONSHIP-AND-DECISION-POLICY-CONTRACT-001`

## 4. Max-T candidates

Single-step max-T and Westfall-Young style max-T paths are **research candidates only** (`candidate_after_simulation`, `candidate_after_null_calibration`, or `research_only`). They require shared-control dependence modeling, null calibration on multicell DGPs, and simulation coverage before any adapter work.

## 5. Stepdown candidates

Stepdown max-T and Romano-style stepdown under positive dependence remain **research_only** or **candidate_after_null_calibration**. No stepdown path is production-authorized.

## 6. Baseline multiplicity controls

Bonferroni and Holm paths are **baseline_control_only** — usable as conservative sensitivity upper bounds, not as promotion evidence.

## 7. Shared-control dependence risks

Shared-control covariance handling is mandatory before promotion. Rows route through `OPD-MC-001`, `DGP-MC-002`, and failure modes `FM-INF-009`, `FM-INF-010`, `FM-TE-006`. Donor contamination across multicell units is **blocked**.

## 8. Winner-selection risks

Winner-selection and best-cell selection risks are explicitly identified. Competing-cell multiplicity is required; marginal per-cell readouts cannot authorize selection claims.

## 9. Multiple KPI / horizon risks

Multiple KPI and multiple horizon multiplicity is a distinct failure class. Each additional endpoint or horizon compounds familywise risk and requires explicit control or restriction.

## 10. Estimator-family implications

| Family | Multicell implication |
|--------|----------------------|
| SCM | Per-cell placebo with dependence warning; treated-set placebo research-only; promotion gates wait |
| AugSynth | Multicell adapter + null calibration required before any family-level readout |
| DID | Multicell DID blocked for pooled/global; per-cell marginal diagnostic-only |
| TBRRidge | Multicell BRB/placebo paths blocked or diagnostic-only |
| Synthetic DID | Multicell Synthetic DID requires simulation and adapter before promotion |

Estimator-specific promotion gates must wait for this scout outcome and downstream artifacts.

## 11. Blocked paths

- Naive per-cell p-values as family-level evidence
- Pooled/global multicell inference without validated dependence and multiplicity
- Production max-T/stepdown without null calibration
- Winner-selection without multiplicity control
- Donor-contaminated shared-control geometries

## 12. Research-candidate paths

- Single-step max-T after simulation
- Westfall-Young max-T after null calibration
- Stepdown max-T after adapter + calibration
- Min-P / adjusted p-value paths after adapter
- Cell-wise placebo rank with dependence warning (diagnostic)
- Treated-set placebo under multicell (research)
- Leave-one-treated-out under multicell (research)

## 13. Required future simulation

Multicell shared-control DGPs (`DGP-MC-001`–`DGP-MC-004`) must cover dependence structure, positive correlation, spillover, and heterogeneous effects before any max-T/stepdown candidate advances.

## 14. Required future adapters

Estimator-specific statistic adapters for multicell readouts (SCM/AugSynth studentized paths, DID cluster structure, TBRRidge geometry) are prerequisites for `candidate_after_adapter` rows.

## 15. Required future null calibration

Null calibration on joint multicell nulls is required for Westfall-Young, stepdown, and min-P paths. Bootstrap shortcuts cannot substitute for invalid assignment or unmodeled dependence.

## 16. Updated roadmap sequence

1. ✅ `MULTICELL_MAX_T_RESEARCH_SCOUT_001` (this scout)
2. **`SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`** (immediate next)
3. `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
4. `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`

## 17. Downstream boundary

This scout does not authorize production inference.
This scout does not authorize production p-values.
This scout does not authorize causal confidence intervals.
This scout does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 18. Validation

Harness: `panel_exp/validation/multicell_max_t_research_scout_001.py`
Tests: `tests/validation/test_multicell_max_t_research_scout_001.py`

## 19. Verdict

`multicell_max_t_research_scout_completed_no_downstream_authorization`

**Next:** `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`

## Summary JSON location

[`docs/track_d/archives/MULTICELL_MAX_T_RESEARCH_SCOUT_001_summary.json`](archives/MULTICELL_MAX_T_RESEARCH_SCOUT_001_summary.json)
