# READOUT_PLAN_RUNTIME_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `READOUT_PLAN_RUNTIME_001` |
| **Artifact type** | `readout_plan_runtime` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `runtime_plans_readout_stack_only_no_estimator_execution_or_claim_authorization` |
| **Base commit** | `4e54f29` (Define readout plan contract) |
| **Final verdict** | `readout_plan_runtime_implemented_planning_only_no_estimator_execution_or_claim_authorization` |

`READOUT_PLAN_RUNTIME_001` implements deterministic governed readout planning only. It can construct planned primary/sensitivity/diagnostic candidate lists and produce a readout planning packet. It does not execute estimators, compute inference, estimate effects, calculate p-values/CIs, run diagnostics or sensitivity checks, authorize claims, or authorize production readout.

---

## 2. Source files inspected

- `docs/track_d/READOUT_PLAN_CONTRACT_001_REPORT.md`
- `docs/track_d/archives/READOUT_PLAN_CONTRACT_001_summary.json`
- `panel_exp/validation/readout_plan_contract_001.py`
- `tests/validation/test_readout_plan_contract_001.py`
- `docs/track_d/READOUT_METHOD_GOVERNANCE_CONTRACT_001_REPORT.md`
- `docs/track_d/archives/READOUT_METHOD_GOVERNANCE_CONTRACT_001_summary.json`
- `panel_exp/validation/readout_method_governance_contract_001.py`
- `tests/validation/test_readout_method_governance_contract_001.py`
- `panel_exp/validation/design_assignment_runtime_001.py`
- `tests/validation/test_design_assignment_runtime_001.py`
- `panel_exp/validation/method_suitability_runtime_001.py`
- `tests/validation/test_method_suitability_runtime_001.py`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`
- `docs/ROADMAP_V4.md`
- `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`
- `docs/MIP_AUDIT_REGISTRY.md`

---

## 3. Implementation scope

Implemented:

- Deterministic `build_readout_plan(input_data, config=None)` runtime
- Input normalization for dict, list-of-dicts, and dataclass-like objects
- Gate evaluation for governance, assignment artifact, reproducibility, instrument availability, estimand scope, uncertainty scope, diagnostics prerequisites, and sensitivity prerequisites
- Instrument slotting into primary/sensitivity/diagnostic/blocked/not-evaluated roles
- Readout plan packet emission with execution prerequisites, claim scope, reporting caveats, warnings, and blocking reasons
- Multi-request evaluation without ranking designs
- Claim-boundary report with runtime-positive planning flags and strict false authorization/execution flags

Not implemented:

- Estimator execution
- Inference execution
- Effect/lift/ROI computation
- p-value/CI/uncertainty computation
- Diagnostic/sensitivity execution
- Causal claim authorization
- Production readout authorization
- MMM/LLM/production authorization behavior

---

## 4. Relationship to readout plan contract

`READOUT_PLAN_CONTRACT_001` defined statuses, stack roles, packet fields, and gate order.  
`READOUT_PLAN_RUNTIME_001` operationalizes those definitions with deterministic planning behavior while preserving contract boundaries.

Contract status alias support:

- Accepts input alias `READOUT_PLAN_READY_FOR_RUNTIME_PLANNING`
- Emits runtime status `READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT`

---

## 5. Relationship to readout method governance contract

This runtime consumes `readout_method_governance_status` and optional `readout_method_governance_packet` context. If governance is blocked and config requires blocking, readout plan status is `READOUT_PLAN_BLOCKED_BY_READOUT_GOVERNANCE`.

---

## 6. Relationship to assignment runtime

This runtime consumes assignment artifacts (`assignment_plan`, `assignment_candidate`, `reproducibility_manifest`, plus status). Missing or blocked assignment artifacts can block planning based on config. Deterministic explicit-pool assignment limitations are propagated as reporting caveats.

---

## 7. Relationship to method suitability runtime

This runtime consumes instrument matrix rows and explicit planning lists (`eligible_instruments_for_planning`, `restricted_instruments`, `diagnostic_only_instruments`, `blocked_instruments`, `not_evaluated_instruments`) and preserves instrument-level governance in slotting.

---

## 8. Public API

```python
from panel_exp.validation.readout_plan_runtime_001 import (
    build_readout_plan,
    plan_readout_stack,
    ReadoutPlanRuntimeConfig,
)
```

- `build_readout_plan(input_data, config=None) -> ReadoutPlanRuntimeReport`
- `plan_readout_stack(...)` is an alias

Deterministic and side-effect-free: no randomness, no network calls, no estimator/inference calls, no global mutable state.

---

## 9. Input format

Each request supports:

- `design_id`
- `readout_method_governance_status`
- `readout_method_governance_packet`
- `assignment_artifact_status`
- `assignment_plan`
- `assignment_candidate`
- `reproducibility_manifest`
- `instrument_suitability_matrix`
- `eligible_instruments_for_planning`
- `restricted_instruments`
- `diagnostic_only_instruments`
- `blocked_instruments`
- `not_evaluated_instruments`
- `estimand_scope`
- `uncertainty_scope`
- `required_diagnostics`
- `required_sensitivity_checks`
- `claim_eligibility_reports`
- `production_governance_config`

Instrument rows support:

- `instrument_id`, `estimator_family`, `inference_family`
- `governance_status`, `planning_category`, `suitability_status`
- `review_requirements`, `required_diagnostics`, `required_sensitivity_checks`
- `uncertainty_semantics`, `estimand_compatibility_status`
- `warnings`, `blocking_reasons`, `diagnostic_only_reason`, `restricted_reason`

---

## 10. Output reports

Per request, runtime emits:

- `readout_plan_status`
- `readout_plan_packet`
- `planned_readout_stack`
- `planned_primary_candidates`
- `planned_sensitivity_candidates`
- `planned_diagnostic_candidates`
- `blocked_instruments`
- `not_evaluated_instruments`
- `execution_prerequisites`
- `estimand_scope`
- `uncertainty_scope`
- `required_diagnostics`
- `required_sensitivity_checks`
- `claim_scope`
- `reporting_caveats`
- `claim_boundary_report`
- `issues`, `warnings`, `blocking_reasons`

Multi-request mode returns `design_reports` and aggregate summary without ranking.

---

## 11. Readout plan statuses

Runtime output statuses:

- `READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT`
- `READOUT_PLAN_READY_WITH_WARNINGS`
- `READOUT_PLAN_PROVISIONAL`
- `READOUT_PLAN_BLOCKED_BY_READOUT_GOVERNANCE`
- `READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT`
- `READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS`
- `READOUT_PLAN_BLOCKED_BY_ESTIMAND`
- `READOUT_PLAN_BLOCKED_BY_UNCERTAINTY_SEMANTICS`
- `READOUT_PLAN_BLOCKED_BY_MISSING_DIAGNOSTICS`
- `READOUT_PLAN_BLOCKED_BY_MISSING_SENSITIVITY_REQUIREMENTS`
- `READOUT_PLAN_BLOCKED_BY_PRODUCTION_GOVERNANCE`
- `READOUT_PLAN_REQUIRES_DIAGNOSTIC_PLAN`
- `READOUT_PLAN_REQUIRES_SENSITIVITY_PLAN`
- `READOUT_PLAN_NOT_EVALUATED`

---

## 12. Stack roles

- `PRIMARY_READOUT_CANDIDATE`
- `SENSITIVITY_READOUT_CANDIDATE`
- `DIAGNOSTIC_READOUT_CANDIDATE`
- `BLOCKED_READOUT_INSTRUMENT`
- `REFERENCE_ONLY_INSTRUMENT`
- `NOT_EVALUATED_INSTRUMENT`

---

## 13. Instrument planning categories

- `PLANNING_ELIGIBLE_PRIMARY_CANDIDATE`
- `PLANNING_ELIGIBLE_WITH_WARNINGS`
- `PLANNING_RESTRICTED_REQUIRES_REVIEW`
- `PLANNING_DIAGNOSTIC_ONLY`
- `PLANNING_BLOCKED`
- `PLANNING_NOT_EVALUATED`

---

## 14. Readiness gates

Implemented gate sequence:

1. Readout method governance gate
2. Assignment artifact gate
3. Reproducibility manifest gate
4. Eligible/restricted instrument gate
5. Diagnostic-only instrument gate
6. Blocked instrument gate
7. Estimand scope gate
8. Uncertainty semantics gate
9. Diagnostics requirement gate
10. Sensitivity requirement gate
11. Execution prerequisite gate
12. Claim scope boundary gate
13. Readout plan packet gate

---

## 15. Instrument slotting logic

- Eligible instruments become primary candidates.
- Eligible-with-warnings instruments become primary and sensitivity candidates with caveats.
- Restricted instruments become primary and sensitivity candidates with caveats and required diagnostics.
- Diagnostic-only instruments become diagnostic candidates only.
- Blocked instruments remain blocked.
- Not-evaluated instruments remain not evaluated.
- No winner is selected; multiple primary candidates are preserved.

---

## 16. Primary/sensitivity/diagnostic planning behavior

- Primary candidate generation is allowed and represented by `planned_primary_candidates_generated`.
- Sensitivity candidate generation is allowed and represented by `planned_sensitivity_candidates_generated`.
- Diagnostic candidate generation is allowed and represented by `planned_diagnostic_candidates_generated`.
- Even when candidates are planned, selection flags remain false:
  - `primary_readout_stack_selected = false`
  - `sensitivity_stack_selected = false`
  - `diagnostic_stack_selected = false`
  - `method_winner_selected = false`

---

## 17. Claim scope behavior

Runtime generates planned claim scope (with defaults/caveats when required fields are missing), but does not authorize claims.

Special caveat behavior:

- ROI claim scope requires explicit ROI governance; otherwise caveat indicates ROI not planned.
- Dosage estimand adds dosage-compatibility caveat and blocks simple standard incrementality interpretation.
- Budget reallocation estimand adds caveat blocking simple ROI claim scope.
- Diagnostic-only-only plans add caveat that production lift/ROI claims are not supported.

---

## 18. Diagnostics/sensitivity prerequisite behavior

- Required diagnostics and sensitivity checks are preserved as prerequisites.
- Missing diagnostics emits diagnostic-plan-required warnings and status transitions.
- Missing sensitivity checks emits sensitivity-plan-required warnings and status transitions.
- Runtime does not execute any diagnostic or sensitivity checks.

---

## 19. Reporting caveats

Runtime emits caveats for:

- Restricted instrument usage
- Missing claim-scope fields (defaulted and caveated)
- Missing estimand/uncertainty/diagnostic/sensitivity prerequisites
- Deterministic assignment artifact limitations
- ROI governance not explicit
- Production-governance blocked roles

---

## 20. Required examples (runtime behavior)

1. Eligible DID + Bootstrap planned primary; SCM + Placebo planned diagnostic.
2. Multiple eligible primary instruments emitted without winner selection.
3. Only diagnostic-only instruments available; no primary candidate and blocked/provisional based on config.
4. All instruments blocked; plan blocked.
5. Restricted TBR Ridge + BRB planned with caveats and diagnostics prerequisites.
6. Dosage contrast estimand emits dosage caveat and standard-incrementality limitation.
7. Budget reallocation estimand emits source/destination and simple ROI-block caveat.
8. Missing reproducibility manifest blocks planning.
9. Missing uncertainty semantics blocks/provisionalizes by config.
10. Deterministic explicit-pool assignment limitation preserved as reporting caveat.

---

## 21. Claim boundaries

Runtime-positive capability flags:

- `readout_plan_runtime_implemented = true`
- `readout_plan_generated = true/false` per request
- `planned_primary_candidates_generated = true/false`
- `planned_sensitivity_candidates_generated = true/false`
- `planned_diagnostic_candidates_generated = true/false`
- `blocked_instruments_preserved = true`
- `execution_prerequisites_generated = true/false`
- `claim_scope_generated = true/false`
- `reporting_caveats_generated = true/false`

Always false:

- `primary_readout_stack_selected`
- `sensitivity_stack_selected`
- `diagnostic_stack_selected`
- `method_winner_selected`
- `estimator_execution_implemented`
- `inference_execution_implemented`
- `effect_estimate_computed`
- `lift_computed`
- `roi_computed`
- `p_value_computed`
- `confidence_interval_computed`
- `uncertainty_computed`
- `diagnostic_check_executed`
- `sensitivity_check_executed`
- `causal_claim_authorized`
- `incremental_lift_claim_authorized`
- `roi_claim_authorized`
- `production_readout_authorized`
- `production_authorization_granted`
- `mmm_runtime_calls_implemented`
- `mmm_calibration_authorized`
- `llm_decisioning_authorized`

---

## 22. Tests added

`tests/validation/test_readout_plan_runtime_001.py` covers:

- Eligible/restricted/diagnostic/blocked/not-evaluated slotting
- Governance/assignment/reproducibility/estimand/uncertainty block rules
- Diagnostics and sensitivity prerequisite behavior
- Claim scope and caveat behavior (including ROI/dosage/budget caveats)
- Claim-boundary enforcement (no selection/execution/authorization)
- Multi-request behavior without ranking
- Alias handling and summary validation

---

## 23. Validation results

- `python -m json.tool docs/track_d/archives/READOUT_PLAN_RUNTIME_001_summary.json`
- `git diff --check`
- `python -m pytest tests/validation/test_readout_plan_runtime_001.py -q`
- Targeted regression suite executed for readout-plan, readout-method-governance, assignment runtime, method suitability, assignment feasibility, design-cell, scenario policy, power/MDE, spend diagnostics, geo feasibility, and profiler validation modules.
- Governance test suite executed after governance updates.
- Safety grep executed for forbidden `*true` authorization/execution flags.
- Capability-positive grep executed for allowed planning capability flags.
- Fixture-specific branching grep executed (no fixture-specific branching in runtime).

---

## 24. Known limitations

- Runtime plans candidates; it does not execute or score candidate quality.
- Claim scope is a planning artifact and remains non-authorizing.
- Production roles remain blocked regardless of planned candidates.

---

## 25. Recommended next artifact

**Primary:** `ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001`  
**Alternative:** `READOUT_METHOD_GOVERNANCE_RUNTIME_001`

---

## 26. Final verdict

`readout_plan_runtime_implemented_planning_only_no_estimator_execution_or_claim_authorization`
