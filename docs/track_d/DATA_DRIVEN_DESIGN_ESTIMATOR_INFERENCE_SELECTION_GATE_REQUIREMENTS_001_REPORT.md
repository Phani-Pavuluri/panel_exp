# DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001 Report

## 1. Purpose

This requirements-only artifact defines the data-driven design × estimator × inference selection gate that will eventually answer: given observed panel data, experiment metadata, KPI/outcome type, assignment information, cell structure, and governance state — which design, estimator, and inference paths are eligible, diagnostic-only, research-only, or blocked?

The registry contains **96 requirement rows** across **14 selection layers** (`failed_scenarios: []`). This artifact defines requirements only; it does **not** implement the production router.

## 2. Why this selector requirements artifact exists

Per `PRODUCTION_READINESS_BACKLOG_LEDGER_001`, the data-driven selection gate is a **P1 first-candidate blocker** that must not be lost across reports, investigations, and method-specific lanes. Without explicit requirements, router logic could be implemented ad hoc, conflating design eligibility with estimator eligibility and inference authorization.

## 3. Prior-work reconciliation

This artifact reconciles against resolved and open prior work without duplicating it:

| Prior artifact | Carried forward |
|---|---|
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | Unfinished backlog items as router inputs |
| `MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001` | Multicell blockers, multiplicity requirements |
| `SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001` | SCM point-estimate gates vs inference blockers |
| `METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` | Method-family promotion status |
| `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001` | Design/estimator/inference suitability |
| `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001` | Diagnostic router inputs |
| `METHOD_FAILURE_MODE_REGISTRY_001` | Failure-mode blockers |
| `SIMULATION_DGP_COVERAGE_PLAN_001` | DGP evidence requirements |
| `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001` | Assignment stress gates |
| Method-family audits (DID, AugSynth, Synthetic DID, TBRRidge, Bayesian TBR, TROP) | Family-specific routing examples |

Resolved audits/plans are **not** re-implemented here; unresolved blockers are encoded as routing requirements.

## 4. Relationship to OPEN_INVESTIGATIONS_001

The selector must consult open investigations and governance state. Blocking open investigations prevent production routing. Investigation resolution does not imply production readiness.

## 5. Relationship to PRODUCTION_READINESS_BACKLOG_LEDGER_001

Every backlog item maps to a selector input. The selector must consult the backlog ledger before returning routes. Backlog items with `production_ready: false` remain blocked or diagnostic/research-only.

## 6. Relationship to method-family promotion criteria

`METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001` defines promotion hypotheses per family. The selector uses promotion status to route method families to eligible, diagnostic-only, research-only, or blocked paths.

## 7. Selection-layer definitions

| Layer | Role |
|---|---|
| `data_intake` | Panel data schema and intake contract |
| `experiment_metadata` | Experiment ID, cell structure, KPI declarations |
| `assignment_mechanism` | Randomization, placebo, or deterministic assignment |
| `design_eligibility` | Whether design supports requested readout |
| `estimator_eligibility` | Whether estimator is suitable for design/outcome |
| `inference_eligibility` | Whether inference path is authorized |
| `outcome_kpi_compatibility` | Outcome scale and KPI multiplicity |
| `observed_diagnostics` | Observed panel diagnostic thresholds |
| `simulation_dgp_coverage` | DGP simulation evidence |
| `failure_registry` | Unresolved failure modes |
| `multicell_dependence_multiplicity` | Shared-control and multiplicity state |
| `method_family_promotion_status` | Per-family promotion/blocker status |
| `release_gate` | Platform authorization release gate |
| `downstream_boundary` | TrustReport, CS, MMM, LLM, API, scheduler, budget |

## 8. Decision-target definitions

| Target | Meaning |
|---|---|
| `design` | Design path only |
| `estimator` | Estimator path only |
| `inference` | Inference path only |
| `design_estimator_pair` | Design + estimator tuple |
| `estimator_inference_pair` | Estimator + inference tuple |
| `full_design_estimator_inference_tuple` | Complete DEI tuple |
| `method_family` | Method-family routing |
| `downstream_authorization` | Downstream role authorization |

## 9. Route-status definitions

| Status | Meaning |
|---|---|
| `eligible` | Route permitted for requested scope |
| `eligible_after_warning` | Permitted with warnings surfaced |
| `candidate_after_validation` | Candidate pending validation evidence |
| `diagnostic_only` | Diagnostic readout only |
| `research_only` | Research exploration only |
| `blocked` | Route blocked with reason |
| `release_gate_required` | Requires platform release-gate authorization |

## 10. Required inputs

The selector must accept: observed panel data, experiment metadata, KPI/outcome type, assignment information, cell structure, observed diagnostics, DGP coverage state, failure-registry state, multicell geometry, method-family promotion status, backlog ledger state, open investigations, and release-gate state.

## 11. Data intake requirements

Panel schema validation, required columns, and unit/time index contracts must pass before any routing.

## 12. Experiment metadata requirements

Experiment ID, cell structure, KPI declarations, and treatment timing must be present and consistent.

## 13. Assignment mechanism requirements

Assignment mechanism must be declared. Unknown or deterministic assignment without stress compatibility blocks design-based inference.

## 14. Design eligibility requirements

Design eligibility is **separate** from estimator eligibility. A valid design does not authorize an estimator or inference path.

## 15. Estimator eligibility requirements

Estimator allowed **does not imply** inference allowed. Estimator eligibility consults method-family promotion criteria, diagnostics, and DGP coverage.

## 16. Inference eligibility requirements

Inference eligibility requires adapter maturity, null calibration, and release-gate authorization where applicable. Point estimate allowed **does not imply** causal uncertainty allowed.

## 17. Outcome/KPI compatibility requirements

Outcome scale checks required. Sparse/count/rate outcomes require DGP coverage. Multiple KPIs/cells require multiplicity handling before inferential claims.

## 18. Observed diagnostic requirements

Observed panel diagnostics (`OPD-*`) feed router eligibility. Donor support, pre-period fit, convex hull, and outcome-scale diagnostics gate SCM and AugSynth routes.

## 19. DGP/simulation evidence requirements

DGP simulation coverage from `SIMULATION_DGP_COVERAGE_PLAN_001` required for promotion hypotheses.

## 20. Failure-registry requirements

Unresolved failure modes from `METHOD_FAILURE_MODE_REGISTRY_001` block routing.

## 21. Multicell/shared-control requirements

Multicell/shared-control routes to blocked/research-only unless dependence/multiplicity validation and release gate exist. Naive per-cell p-values and pooled/global overclaim blocked.

## 22. Release-gate requirements

No production authorization without `PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001` completion.

## 23. Downstream authorization boundary

No route may authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization without release-gate authorization.

## 24. SCM routing requirements

- Point estimate: eligible only when donor support, convex hull, pre-period fit/trend, outcome scale, and assignment validity pass
- Production inference: blocked until adapter, null calibration, and release gate
- Treated-set placebo: requires statistic adapter and null calibration

## 25. DID routing requirements

DID conditional candidate only when assignment/design, parallel trends, cluster/outcome suitability, and bootstrap suitability are acceptable. Bootstrap cannot fix invalid assignment.

## 26. AugSynth routing requirements

AugSynth diagnostic/remediation candidate until adapter, null calibration, donor support, and DGP coverage mature.

## 27. Synthetic DID routing requirements

Synthetic DID remains readiness/scout candidate until implementation-readiness and suitability validation exist.

## 28. TBRRidge routing requirements

TBRRidge remains diagnostic unless remediation plan proves otherwise.

## 29. Classic/Aggregate TBR routing requirements

Classic/Aggregate TBR overclaim paths route to retire/replace or blocked per `BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001`.

## 30. Bayesian TBR routing requirements

Bayesian TBR posterior intervals route to posterior diagnostic only, not causal CI. Calibration replay required.

## 31. TROP routing requirements

TROP routes to research-only; production recommendations, budget, and decisioning blocked.

## 32. Blocked-reason requirements

The selector must return machine-readable blocked reasons for every blocked route.

## 33. Next-best alternative requirements

The selector must return next-best diagnostic or research alternatives when primary routes are blocked.

## 34. Recommended next artifacts

1. `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001` (immediate next)
2. `DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`
3. `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001`

## 35. Updated roadmap sequence

1. ✅ `PRODUCTION_READINESS_BACKLOG_LEDGER_001`
2. ✅ `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001` (this artifact)
3. **`AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`** (immediate next)

## 36. Validation

Harness: `panel_exp/validation/data_driven_design_estimator_inference_selection_gate_requirements_001.py`
Tests: `tests/validation/test_data_driven_design_estimator_inference_selection_gate_requirements_001.py`

## 37. Verdict

`data_driven_selection_gate_requirements_defined_no_downstream_authorization`

**Next:** `AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`

## Downstream boundary

This requirements artifact does not implement the production selector.
This requirements artifact does not authorize production routing.
This requirements artifact does not authorize production inference.
This requirements artifact does not authorize production p-values.
This requirements artifact does not authorize causal confidence intervals.
This requirements artifact does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

## Summary JSON location

[`docs/track_d/archives/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001_summary.json`](archives/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001_summary.json)
