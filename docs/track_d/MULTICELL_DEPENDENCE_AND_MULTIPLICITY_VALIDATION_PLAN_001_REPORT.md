# MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001 Report

## 1. Purpose

This validation-only artifact defines exactly what must be validated before any future multicell or shared-control production claim is allowed. It is a metadata-only validation-plan registry across **78 rows** and **26 validation areas** (`failed_scenarios: []`).

This plan defines validation requirements and boundaries. It is **not** a production inference implementation and does **not** authorize any downstream production behavior.

## 2. Why multicell dependence/multiplicity is a cross-family blocker

Per `MULTICELL_MAX_T_RESEARCH_SCOUT_001`, `D5-TRUST-MULTICELL-PERCELL-INFERENCE-001`, and `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`, multicell/shared-control geometries induce cross-cell dependence (shared control correlation ≈ 0.901) and familywise type-I inflation (≈ 0.272 under naive per-cell testing). These failures are not family-specific: they block SCM, DID, AugSynth, Synthetic DID, TBRRidge, Bayesian TBR, TROP, and classic aggregate TBR multicell promotion paths until dependence is modeled/simulated/validated and multiplicity is controlled.

**Multicell/shared-control remains a cross-family blocker.** No multicell production claim is authorized by this validation plan.

## 3. Evidence base

Evidence consumed from:

- `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
- `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`
- `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001`
- `MULTICELL_MAX_T_RESEARCH_SCOUT_001`
- `SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001`
- `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`
- `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
- `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
- `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
- `METHOD_FAILURE_MODE_REGISTRY_001`
- `SIMULATION_DGP_COVERAGE_PLAN_001`
- `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
- `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`

## 4. Current multicell status

Multicell/shared-control inference is **blocked/research-only** across all method families. Naive independent per-cell p-values are **blocked**. Naive pooled/global overclaiming is **blocked**. Max-T and stepdown remain **validation candidates only** — not production-authorized procedures.

## 5. Validation status definitions

| Status | Meaning |
|---|---|
| `required_blocker` | Must pass before any multicell promotion hypothesis |
| `required_warning` | Must be reviewed; may block promotion if severe |
| `candidate_after_validation` | Advancement requires validation evidence |
| `candidate_after_adapter` | Advancement requires statistic adapter maturity |
| `candidate_after_null_calibration` | Advancement requires null calibration evidence |
| `candidate_after_simulation` | Advancement requires DGP simulation coverage |
| `research_required` | Research handling required before promotion |
| `diagnostic_only` | Diagnostic readout only; not sufficient for production claim |
| `blocked` | Multicell production path blocked |

## 6. Claim-scope definitions

| Claim scope | Meaning |
|---|---|
| `per_cell` | Single-cell marginal claim; requires per-cell validation evidence |
| `pooled` | Pooled across cells; separate validation from per-cell |
| `global` | Global/winner-selection claim; highest multiplicity burden |
| `aggregate` | Aggregate lift claim; separate validation from per-cell |
| `cell_by_kpi` | Cell × KPI cross-product claim family |
| `method_family` | Method-family-specific multicell boundary |
| `release_gate` | Platform authorization release gate dependency |

Per-cell, pooled, global, and aggregate claims **require separate validation evidence**.

## 7. Method-family scope definitions

| Scope | Meaning |
|---|---|
| `cross_family` | Applies across all method families |
| `scm` | SCM multicell interaction boundary |
| `did` | DID multicell interaction boundary |
| `augsynth_cvxpy` | AugSynth multicell interaction boundary |
| `synthetic_did` | Synthetic DID multicell interaction boundary |
| `tbrridge` | TBRRidge multicell interaction boundary |
| `classic_aggregate_tbr` | Classic aggregate TBR multicell interaction boundary |
| `bayesian_tbr` | Bayesian TBR multicell interaction boundary |
| `trop` | TROP multicell interaction boundary |

## 8. Shared-control dependence requirements

Shared-control dependence must be **modeled, simulated, or otherwise validated** before promotion. Rows in `shared_control_dependence` and `common_control_boundary` areas require cross-cell correlation diagnostics, shared-vs-disjoint null comparison, and DGP coverage for shared-control geometries.

## 9. Cell-level dependence requirements

Cell-level dependence (`cell_level_dependence`) requires explicit handling of within-experiment correlation across treated cells sharing controls. Independence assumptions are blocked.

## 10. KPI/outcome multiplicity requirements

KPI/outcome multiplicity (`kpi_outcome_multiplicity`) requires familywise control when multiple outcomes or KPIs are tested. Multiple metric/outcome families cannot share a single marginal alpha without adjustment evidence.

## 11. Cell × KPI multiplicity requirements

Cell × KPI multiplicity (`cell_kpi_multiplicity`) requires validation of the cross-product claim family. Testing multiple cells across multiple KPIs compounds multiplicity beyond per-cell or per-KPI margins alone.

## 12. Familywise error requirements

Familywise error control (`familywise_error_control`) is **required** for any simultaneous multicell decision. Marginal per-cell readouts cannot authorize familywise winner selection.

## 13. Max-T validation candidate

Max-T (`max_t_candidate_validation`) is a **validation candidate only until validated**. It is not a production-authorized procedure. Requires shared-control dependence handling and null calibration before any promotion hypothesis.

## 14. Stepdown validation candidate

Stepdown (`stepdown_candidate_validation`) is a **validation candidate only until validated**. Same boundary as max-T: research/validation path only.

## 15. Studentized statistic adapter requirements

Studentized statistic adapters (`studentized_statistic_requirements`) are **required** before inferential promotion. Per `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`, scale contracts and adapter maturity must be demonstrated.

## 16. Null calibration requirements

Null calibration (`permutation_randomization_null_calibration`) is **required** before inferential promotion. Permutation/randomization null paths must pass `null_fpr_gate` and related calibration evidence.

## 17. Per-cell claim boundary

Per-cell claims (`per_cell_claim_boundary`) are allowed only as diagnostic/research readouts until validated. **Naive independent per-cell p-values are blocked.**

## 18. Pooled/global claim boundary

Pooled and global claims (`pooled_global_claim_boundary`) require separate validation evidence. **Naive pooled/global overclaiming is blocked.**

## 19. Aggregate claim boundary

Aggregate lift claims (`aggregate_lift_boundary`) require separate validation from per-cell and pooled claims. Stratified aggregate readouts remain diagnostic unless contract evidence passes.

## 20. SCM multicell boundary

SCM multicell claims (`scm_multicell_interaction`) remain **blocked/research-only** until this validation lane is satisfied.

## 21. DID multicell boundary

DID multicell claims (`did_multicell_interaction`) remain **blocked/research-only** unless future evidence changes status. Per `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`, bootstrap cannot fix invalid assignment.

## 22. AugSynth multicell boundary

AugSynth multicell claims (`augsynth_multicell_interaction`) remain **blocked/research-only** until adapter/null calibration remediation completes.

## 23. Synthetic DID multicell boundary

Synthetic DID multicell claims (`synthetic_did_multicell_interaction`) remain **blocked/research-only** per `SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001`.

## 24. TBRRidge multicell boundary

TBRRidge multicell claims (`tbrridge_multicell_interaction`) remain **blocked/research-only** per `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`.

## 25. Bayesian TBR multicell boundary

Bayesian TBR multicell claims (`bayesian_tbr_multicell_interaction`) remain **blocked/research-only** until calibration replay research completes.

## 26. TROP multicell boundary

TROP multicell claims (`trop_multicell_interaction`) remain **blocked/research-only** unless future evidence changes status.

## 27. DGP simulation requirements

DGP simulation coverage (`SIMULATION_DGP_COVERAGE_PLAN_001`) is **required** for sparse/count/rate outcomes, shared-control geometries, and cross-family dependence validation.

## 28. Assignment-stress requirements

Assignment-generator stress (`DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`) is **required** for multicell designs with unbalanced cells, small cell counts, and shared-control policies.

## 29. Failure-registry blockers

`METHOD_FAILURE_MODE_REGISTRY_001` must be consulted. Unresolved failure modes for multicell dependence, multiplicity inflation, and shared-control correlation block promotion.

## 30. Allowed current uses

- Multicell research exploration and diagnostic readouts
- Dependence/multiplicity boundary documentation
- Max-T/stepdown validation candidate research
- Per-cell marginal diagnostic readouts (not production claims)
- DGP simulation and assignment-stress planning

## 31. Forbidden current uses

- Multicell production claims of any scope
- Naive independent per-cell p-values for simultaneous decisions
- Naive pooled/global/winner-selection overclaiming
- Production inference, p-values, causal CIs
- TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, budget optimization

## 32. Required future artifacts

1. `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` (immediate next)
2. `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
3. `SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001`
4. `METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001`
5. `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001`

## 33. Updated roadmap sequence

1. ✅ `PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001`
2. ✅ `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
3. ✅ `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` (this plan)
4. **`AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`** (immediate next)

## 34. Downstream boundary

This validation plan does not authorize multicell production claims.
This validation plan does not authorize production inference.
This validation plan does not authorize production p-values.
This validation plan does not authorize causal confidence intervals.
This validation plan does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## 35. Validation

Harness: `panel_exp/validation/multicell_dependence_multiplicity_validation_plan_001.py`
Tests: `tests/validation/test_multicell_dependence_multiplicity_validation_plan_001.py`

## 36. Verdict

`multicell_dependence_and_multiplicity_validation_plan_defined_no_downstream_authorization`

**Next:** `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`

## Summary JSON location

[`docs/track_d/archives/MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001_summary.json`](archives/MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001_summary.json)
