# DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001` |
| **Artifact type** | `design_assignment_feasibility_runtime` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `runtime_evaluates_assignment_feasibility_no_assignment_or_matching` |
| **Base commit** | `3bc56d2` (Define design assignment feasibility contract) |
| **Final verdict** | `design_assignment_feasibility_runtime_implemented_no_assignment_or_matching` |

This artifact implements conservative deterministic evaluation of whether a validated design structure has enough eligible units, cell capacity, constraint clarity, and downstream handoff readiness for a **future** assignment/matching runtime to attempt assignment. It does not assign geo units, generate matched pairs, randomize cells, compute power/MDE, or authorize production decisions.

---

## 2. Source files inspected

| File | Role |
|------|------|
| `DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001` | Contract source of truth |
| `DESIGN_CELL_STRUCTURE_RUNTIME_001` | Upstream design structure status pattern |
| `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` | Scenario handoff preservation pattern |
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Power/MDE handoff pattern |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo feasibility upstream |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Profiler upstream |

---

## 3. Implementation scope

**Implemented:** `evaluate_design_assignment_feasibility` / `evaluate_assignment_feasibility`; eligible/excluded/available unit counting; cell capacity evaluation; common-control capacity check; split-control redesign/recheck detection; mutual exclusivity reporting; geo hierarchy and market exclusion reporting; balance-readiness covariate reporting; interference-risk reporting; scenario/power/MDE/method-suitability handoff preservation; assignment feasibility status emission; multiple candidates without ranking.

**Not implemented:** geo assignment, matched pairs, blocks, randomization, rerandomization, thinning design, matching optimization, balance optimization, interference adjustment, scenario policy feasibility computation, scenario enumeration/optimization, runtime design generation, power/MDE, p-values/CIs, lift/ROI, estimator selection, production authorization.

---

## 4. Relationship to assignment feasibility contract

Implements runtime evaluation for contract concepts: `DesignAssignmentFeasibilityInput`, `AssignmentUnitSpec`, `AssignmentCellRequirementSpec`, readiness gates, assignment feasibility statuses, constraint categories, handoff reports, and claim boundaries defined in `DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001`.

---

## 5. Relationship to design cell structure runtime

Consumes `design_cell_structure_status` from upstream handoff. Blocks assignment feasibility when design structure is blocked. Does not re-validate cell/contrast structure.

---

## 6. Relationship to scenario policy feasibility runtime

Preserves `scenario_policy_feasibility_status` via `AssignmentScenarioHandoffReport`. Does not recompute scenario policy feasibility (`scenario_policy_feasibility_computed` remains false).

---

## 7. Relationship to power/MDE runtime

Preserves `power_mde_status` via `AssignmentPowerMdeHandoffReport`. Blocks power-ready assignment claims when configured; provisional by default when power/MDE is blocked. Does not compute power or MDE.

---

## 8. Public API

```python
from panel_exp.validation.design_assignment_feasibility_runtime_001 import (
    evaluate_design_assignment_feasibility,
    evaluate_assignment_feasibility,
    DesignAssignmentFeasibilityConfig,
    AssignmentFeasibilityStatus,
)
```

Deterministic, side-effect-free, no network/randomness/LLM/MMM.

---

## 9. Input format

Per candidate: `design_id`, `assignment_units`, `cell_requirements`, `upstream_statuses`, `constraints`, `balance_covariates`, `interference_risks`, `method_suitability_review_required`.

---

## 10. Output reports

`DesignAssignmentFeasibilityReport` with subreports: readiness, eligibility, cell capacity, mutual exclusivity, shared control, split control, hierarchy, market exclusion, balance readiness, interference risk, scenario handoff, power/MDE handoff, method suitability handoff, claim boundary.

---

## 11. Assignment feasibility statuses

All 14 contract statuses implemented including `ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME`, blocked variants, `ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK`, and `ASSIGNMENT_FEASIBILITY_REQUIRES_METHOD_SUITABILITY_REVIEW`.

`ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME` does not mean units were assigned, markets matched, design is powered, estimator is valid, or production is authorized.

---

## 12. Assignment constraint statuses

Seven constraint statuses implemented for per-constraint and subreport evaluation.

---

## 13. Eligibility counting

Only units with `eligible=true` and `available_for_assignment=true` count as available. Excluded and prior-assigned units (by default) are removed. Missing `unit_id` is blocking.

---

## 14. Cell capacity logic

Per-cell minimum/maximum/target validation against eligible unit pool or global fallback. Does not allocate units to cells.

---

## 15. Common-control capacity logic

Validates common-control cell requirements exist and meet minimum capacity. Preserves scenario shared-control conflict flags.

---

## 16. Split-control redesign/recheck logic

Emits `ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK` when `split_control_required` or `scenario_recheck_required`. Does not mark immediately feasible.

---

## 17. Mutual exclusivity logic

Reports undeclared mutual exclusivity as requires-user-input/provisional. Does not resolve conflicts.

---

## 18. Geo hierarchy and market exclusion logic

Missing hierarchy metadata requires user input when configured. Market exclusions preserved; excluded units not counted toward capacity.

---

## 19. Balance-readiness reporting

Reports balance covariate availability. Does not compute balance statistics or optimize balance.

---

## 20. Interference-risk reporting

Flags high/unknown interference as warning or blocker per config. Does not adjust for interference.

---

## 21. Scenario handoff behavior

Preserves upstream scenario status. Blocks or provisional per config when scenario is blocked. Does not recompute scenario feasibility.

---

## 22. Power/MDE handoff behavior

Preserves `power_mde_status`. Provisional by default when blocked; blocking when `block_power_mde_blocked=true`.

---

## 23. Method-suitability handoff behavior

Emits `ASSIGNMENT_FEASIBILITY_REQUIRES_METHOD_SUITABILITY_REVIEW` when required. Estimator/inference readiness remains blocked.

---

## 24. Claim boundaries

`runtime_assignment_feasibility_implemented` and evaluation flags true. All assignment/computation/authorization flags false.

---

## 25. Tests added

47 targeted tests in `tests/validation/test_design_assignment_feasibility_runtime_001.py` covering upstream gates, eligibility, cell capacity, split/shared control, constraints, balance/interference, method suitability, claim boundaries, and multiple candidates.

---

## 26. Validation results

- Runtime pytest: pass
- Contract regression: pass
- Safety grep: pass
- JSON summary: pass

---

## 27. Known limitations

- Does not evaluate pairability diagnostics for matched-pair designs beyond capacity flags.
- Does not validate block metadata completeness for block designs.
- Global pool fallback emits a single design-level warning when used.
- Scenario policy statuses are preserved, not recomputed.

---

## 28. Recommended next artifact

**Primary:** `METHOD_SUITABILITY_HANDOFF_CONTRACT_001`

**Alternative:** `DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001`

---

## Appendix: Examples

| Example | Outcome |
|---------|---------|
| Two-cell, 30 eligible units, min 10/cell | Ready for runtime (with optional global-pool warning) |
| Three test + common control, 25 units, min 8/cell | Blocked by insufficient eligible units |
| Common control min 15, 10 control units | Blocked by cell capacity |
| Split control required | Requires redesign/recheck |
| Method suitability review required | Structurally feasible; method review required |
