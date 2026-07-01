# DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` |
| **Artifact type** | `design_scenario_policy_feasibility_runtime` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `runtime_evaluates_provided_scenarios_no_enumeration_or_optimization` |
| **Base commit** | `afa68e9` (Define design scenario policy feasibility contract) |
| **Final verdict** | `design_scenario_policy_feasibility_runtime_implemented_for_provided_scenarios_no_enumeration_or_optimization` |

This artifact implements a **conservative deterministic runtime** that evaluates **provided** scenario-level spend-policy plans. It does not enumerate scenarios, optimize spend, assign geo units, compute power/MDE, or authorize production decisions.

---

## 2. Source files inspected

| File | Role |
|------|------|
| `DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001` | Immediate upstream contract |
| `DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001` | Cell/contrast structure semantics |
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Upstream power/MDE readiness pattern |
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Spend manipulation semantics |

---

## 3. Implementation scope

**Implemented:**

- `evaluate_design_scenario_policy_feasibility(input_data, config=None)`
- `evaluate_scenario_policy_feasibility` alias
- Readiness gate validation (profiler, geo, spend, power/MDE, design structure, contrast requirements, policy plan)
- Achieved spend contrast computation by contrast type
- Required-vs-achieved spend contrast comparison
- Contrast and scenario feasibility classification
- Historical support evaluation at cell-policy level
- Shared-control conflict detection
- BAU-control preservation checks
- Estimand-shift flags
- Split-control redesign/recheck detection
- Resolution option emission (diagnostic suggestions only)
- Multiple provided scenarios in one call (no ranking)

**Not implemented:** scenario enumeration, optimization, design generation, geo assignment, randomization, power/MDE, inference, production authorization.

---

## 4. Relationship to scenario policy feasibility contract

This runtime implements the contract algorithm from `DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001` for **provided** inputs only. All statuses, conflict types, and resolution option types match the contract.

---

## 5. Relationship to design-cell structure contract

Consumes declared cells, contrasts, and shared-control dependencies from scenario input. Does not generate or modify cell structure.

---

## 6. Relationship to spend feasibility diagnostics

Respects `spend_feasibility_status` upstream gate. When blocked, spend-compatible feasibility claims are withheld.

---

## 7. Relationship to power/MDE runtime

Respects `power_mde_status` upstream gate. When blocked, emits `SCENARIO_REQUIRES_POWER_MDE_RECHECK` and recheck requirements. Does not compute power or MDE.

---

## 8. Public API

```python
from panel_exp.validation.design_scenario_policy_feasibility_runtime_001 import (
    evaluate_design_scenario_policy_feasibility,
    evaluate_scenario_policy_feasibility,
    DesignScenarioPolicyFeasibilityConfig,
)
```

Properties: deterministic, side-effect-free, no network, no randomness, no LLM/MMM calls.

---

## 9. Input format

Single scenario dict or list of scenario dicts. Each scenario supports:

- `scenario_id`, `cells`, `contrasts`, `shared_control_dependencies`, `upstream_statuses`
- `split_control_proposal` (bool) for redesign proposals
- Per cell: `cell_id`, `baseline_spend`, `proposed_spend`, `policy`, `historical_max`, `is_common_control`, `is_bau_policy`
- Per contrast: `contrast_id`, `contrast_type`, `treatment_cell_id`, `comparison_cell_id`, `required_spend_contrast`, `bau_control_required`

---

## 10. Output reports

`DesignScenarioPolicyFeasibilityReport` includes:

- `ScenarioReadinessReport` (via `scenario_reports[].readiness_report`)
- `ScenarioPolicyPlanReport` (`cell_policy_plan`)
- `ContrastFeasibilityReport` per contrast
- `RequiredVsAchievedSpendContrastReport` entries
- `HistoricalSupportReport` per cell
- `SharedControlConflictReport` entries
- `EstimandShiftReport`
- `ScenarioResolutionOption` list
- `ScenarioRecheckRequirement` list
- `ScenarioClaimBoundaryReport`

---

## 11–14. Status enums

Scenario, contrast, policy support, and shared-control conflict types match `DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001`.

---

## 15. Readiness gates

1. profiler → blocked = `SCENARIO_BLOCKED`
2. geo feasibility → blocked = `SCENARIO_BLOCKED`
3. spend feasibility → blocks spend-compatible claims
4. power/MDE → emits recheck when blocked
5. design cell structure → blocked = `SCENARIO_BLOCKED`
6. contrast requirements → missing prevents comparison
7. scenario policy plan → missing blocks feasibility

---

## 16. Required-vs-achieved spend contrast logic

| Contrast type | Achieved formula |
|---------------|------------------|
| `GO_DARK_VS_BAU` | comparison proposed − treatment proposed |
| `HEAVY_UP_VS_BAU` | treatment proposed − comparison proposed |
| `DOSAGE_LOW_VS_HIGH` | high − low |
| `DIFFERENCE_IN_POLICY` | absolute difference |
| `UNKNOWN` | `CONTRAST_NOT_EVALUATED` |

If achieved ≥ required and gates pass → `CONTRAST_FEASIBLE`. If achieved < required → `CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL`. Go-dark vs manipulated BAU with achieved ≥ required → `CONTRAST_REQUIRES_ESTIMAND_SHIFT`.

---

## 17. Historical support logic

Default config: `near_historical_boundary_ratio=0.95`, `block_out_of_support=false`, `require_business_override_for_out_of_support=true`.

Proposed > historical max → out-of-support / business override required. Proposed ≥ p95 threshold → near boundary.

---

## 18. Shared/common-control conflict logic

Detects: manipulation, BAU not preserved, cross-contrast tradeoffs, insufficient for contrasts, out-of-support, split required.

---

## 19. Estimand-shift logic

When common control BAU not preserved → scenario-level `SCENARIO_REQUIRES_ESTIMAND_SHIFT`. Go-dark contrasts with manipulated BAU control → contrast-level estimand shift.

---

## 20. Split-control redesign/recheck logic

`split_control_proposal=true` → `SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT`, power/MDE and assignment recheck requirements. Not marked immediately feasible.

---

## 21. Four-cell common-control scenarios A–E

Validated by tests:

| Scenario | Status |
|----------|--------|
| A — preserve BAU | `SCENARIO_PARTIALLY_FEASIBLE` (T1 insufficient) |
| B — raise C0 | `SCENARIO_REQUIRES_ESTIMAND_SHIFT` + out-of-support |
| C — lower C0 | `SCENARIO_REQUIRES_ESTIMAND_SHIFT` + partially feasible |
| D — T1 high-spend | `SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE` + out-of-support |
| E — split control | `SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT` + rechecks |

---

## 22. Tests added

`tests/validation/test_design_scenario_policy_feasibility_runtime_001.py` — 23 tests covering scenarios A–E, gate blocking, missing inputs, unknown contrast types, business override, claim boundaries, and multiple scenarios.

---

## 23. Validation results

- Runtime pytest: 23 passed
- Contract regression: passed
- Governance pytest: passed
- Safety grep: passed
- Fixture-specific branching grep: passed

---

## 24. Known limitations

- Does not consume full upstream report objects (status strings only)
- Resolution options are diagnostic, not ranked or optimized
- Budget reallocation directional semantics require explicit policy labels
- Does not validate geo-unit assignment feasibility directly

---

## 25. Claim boundaries

| Allowed true | Always false |
|--------------|--------------|
| `runtime_scenario_feasibility_implemented` | `runtime_scenario_enumeration_implemented` |
| `provided_scenario_evaluation_implemented` | `runtime_scenario_optimization_implemented` |
| `required_vs_achieved_spend_contrast_implemented` | `geo_assignment_computed` |
| `historical_support_evaluation_implemented` | `power_computed`, `mde_computed` |
| `shared_control_conflict_detection_implemented` | `production_authorization_granted` |
| `resolution_option_emission_implemented` | `llm_decisioning_authorized` |

---

## 26. Recommended next artifact

**Primary:** `DESIGN_CELL_STRUCTURE_RUNTIME_001`

**Alternative:** `DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001`
