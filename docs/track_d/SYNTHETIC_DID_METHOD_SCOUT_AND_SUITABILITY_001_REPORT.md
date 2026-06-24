# SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001 Report

## 1. Purpose

This validation-only scout decides whether Synthetic DID is worth implementing in panel_exp, what failure modes and diagnostics matter, what evidence is needed before production compatibility, and how it compares against SCM, AugSynth, DID, and TBRRidge.

This scout defines metadata-only routing. It is **not** a Synthetic DID implementation.

## 2. Why Synthetic DID is being scouted

Per `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`, Synthetic DID is a research/scout candidate with medium fixability. Existing repo code (`panel_exp/methods/synthetic_did.py`) is skipped in batch validation with evidence gaps (`FM-ES-009`, `FM-CP-005`). This scout formalizes suitability before any implementation promotion.

## 3. Current evidence base

Evidence consumed from:

- `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
- `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
- `METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`
- `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
- `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`

## 4. Synthetic DID components

| Component | Scout posture |
|-----------|---------------|
| Point estimate | Method scout candidate; production blocked |
| Unit weights | Implementation candidate after suitability |
| Time weights | Research; staggered remediation required |
| Regularization | Simulation candidate; overfit blocked |
| Balanced panel | Remediation required when unbalanced |
| Missing data | Research/blocked by missingness |
| Donor overlap | Blocked when poor; simulation required |
| Pre-period fit | Blocked when poor |
| Sparse/count/rate | Blocked without DGP coverage |

## 5. Design requirements

Treated/control panel structure, pre/post timing, assignment mechanism documentation, staggered estimand clarity, and balanced-panel or imputation protocol are required before implementation promotion.

## 6. Observed diagnostic dependencies

All paths require observed-panel diagnostics (`OPD-PF-*`, `OPD-DS-*`, `OPD-AD-*`, `OPD-MC-*`, `OPD-OM-*`, `OPD-PS-*`) before method selection.

## 7. DGP coverage dependencies

`DGP-ES-009`, `DGP-CP-002`, balance/stress DGPs, outcome-scale DGPs, and multicell dependence DGPs are required before promotion.

## 8. Failure-registry dependencies

`FM-ES-009`, `FM-CP-005`, `FM-DA-001`, `FM-TE-004`, `FM-DA-009`, and cross-cutting `FM-CP-004` must be consulted.

## 9. Design-assignment stress dependencies

Placebo, randomization, and permutation paths require `ST-AD-009` and `ST-AD-010` compatibility.

## 10. Inference adapter requirements

`SYNTHETIC_DID_INFERENCE_ADAPTER_001` (future artifact) is required for placebo, bootstrap, studentized, and multicell paths before null calibration.

## 11. Null-calibration requirements

Placebo, bootstrap, jackknife, and studentized paths require null FPR and coverage gates. Production p-values and causal CIs remain unauthorized.

## 12. Multicell/shared-control boundary

Multicell/shared-control SDID is blocked or research-only until dependence and multiplicity handling exist per `MULTICELL_MAX_T_RESEARCH_SCOUT_001`.

## 13. Comparison against SCM

SDID must be compared against SCM on donor support, pre-period fit, and estimand clarity. When SCM diagnostics pass and SDID does not, prefer SCM diagnostic lane.

## 14. Comparison against AugSynth

SDID must be compared against AugSynth on augmentation stability and disagreement. Large disagreement blocks promotion.

## 15. Comparison against DID

SDID must be compared against DID on parallel trends and assignment validity. DID suitability audit gates must pass before SDID-DID comparison promotion.

## 16. Comparison against TBRRidge

SDID must be compared against TBRRidge on regularization posture. TBRRidge remains diagnostic-only; SDID must not inherit TBRRidge inference paths.

## 17. Implementation candidate paths

- Unit/time weights after panel diagnostics
- Point estimate after full suitability evidence
- Placebo/bootstrap after adapter + null calibration
- Implementation candidate only after this scout completes

## 18. Blocked paths

- Production inference, p-values, and causal CIs globally
- Unknown/deterministic assignment without falsification labeling
- Multicell without dependence handling
- Poor donor overlap and pre-period fit
- Placebo without valid assignment support

## 19. Required future artifacts

1. `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`
2. `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`
3. `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`
4. `SYNTHETIC_DID_INFERENCE_ADAPTER_001` (when implementation proceeds)

## 20. Updated roadmap sequence

1. ✅ `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
2. ✅ `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001` (this scout)
3. **`BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`** (immediate next)
4. `TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001`
5. `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`

## 21. Downstream boundary

This scout does not implement Synthetic DID.
This scout does not authorize production inference.
This scout does not authorize production p-values.
This scout does not authorize causal confidence intervals.
This scout does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 22. Validation

Harness: `panel_exp/validation/synthetic_did_method_scout_suitability_001.py`
Tests: `tests/validation/test_synthetic_did_method_scout_suitability_001.py`

## 23. Verdict

`synthetic_did_method_scout_and_suitability_completed_no_downstream_authorization`

**Next:** `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`

## Summary JSON location

[`docs/track_d/archives/SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001_summary.json`](archives/SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001_summary.json)
