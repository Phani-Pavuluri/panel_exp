# DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001` |
| **Artifact type** | `design_assignment_feasibility_contract` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_runtime_assignment_or_matching` |
| **Base commit** | `e396f2e` (Implement design cell structure runtime) |
| **Final verdict** | `design_assignment_feasibility_contract_defined_no_runtime_assignment_or_matching` |

This artifact is a **contract/specification document only**. It defines the typed assignment-feasibility layer for evaluating whether a validated design-cell structure has enough eligible units and constraint clarity to attempt future assignment/matching. **No runtime assignment feasibility, geo assignment, matching, randomization, power/MDE, inference, or production authorization was implemented or authorized.**

---

## 2. Source files inspected

| File | Role |
|------|------|
| `DESIGN_CELL_STRUCTURE_RUNTIME_001` | Immediate upstream structure validation |
| `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` | Scenario policy handoff upstream |
| `DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001` | Design/assignment contract foundation |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo/unit eligibility upstream |
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Power/MDE readiness handoff |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Golden path sequencing |

---

## 3. Why this contract is needed

The current stack validates data readiness, geo feasibility, spend manipulation, power/MDE readiness, declared design-cell structure, and scenario policy feasibility for provided scenarios. The next unanswered question is:

> Given a validated design structure and scenario handoff, do we have enough eligible units and constraints clarity to attempt future assignment/matching?

Without this contract, future planners may:

- conflate design structure readiness with assignment capacity
- count excluded units toward cell capacity
- ignore common-control unit reservation requirements
- treat split-control redesign as immediately assignment-feasible
- claim assignment-ready when scenario policy or method suitability is blocked

This contract defines what future assignment feasibility must consume, emit, block, warn, and hand off — without performing assignment.

---

## 4. Core goal statement

`DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001` defines the future typed contract for evaluating whether a validated design-cell structure has enough eligible units, cell-size support, assignment constraints, and handoff readiness to attempt assignment/matching in a future deterministic runtime. It does not assign geo units, generate matched markets, randomize cells, optimize balance, compute power/MDE, validate estimators, or authorize production decisions.

---

## 5. Relationship to profiler

Future assignment-feasibility runtime must consume `GeoKpiSpendDataProfileReport`. If profiler/data readiness is blocked, assignment feasibility must be blocked.

---

## 6. Relationship to geo feasibility

Future runtime must consume `GeoUnitMarketFeasibilityReport` for eligible and excluded geo units. Geo feasibility blocked → assignment feasibility blocked.

---

## 7. Relationship to design cell structure runtime

Future runtime must consume `DesignCellStructureRuntimeReport` for cell roles, contrast structure, manipulation-policy compatibility, shared-control dependencies, and structural assignment-readiness status. Design structure blocked → assignment feasibility blocked.

---

## 8. Relationship to scenario policy feasibility runtime

Future runtime must consume `DesignScenarioPolicyFeasibilityReport` for scenario policy status, recheck requirements, and shared-control conflict handoff. Scenario policy blocked → assignment feasibility blocked or provisional. **This contract does not recompute scenario policy feasibility.**

---

## 9. Relationship to power/MDE runtime

Future runtime must consume `PowerMdeDiagnosticsReport` for power/MDE readiness handoff. Power/MDE blocked → must not claim power-ready assignment feasibility.

---

## 10. Conceptual distinctions

| # | Concept | Definition | Rule |
|---|---------|------------|------|
| 1 | **Design structure readiness** | From `DESIGN_CELL_STRUCTURE_RUNTIME_001` | Structurally coherent; does not mean units can be assigned |
| 2 | **Scenario policy feasibility** | From `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` | Spend-contrast evaluated; does not mean units can be assigned |
| 3 | **Assignment feasibility** | This future layer | Enough eligible units + constraint clarity to attempt assignment; not actual assignment |
| 4 | **Assignment generation** | Future runtime only | Not implemented or authorized here |
| 5 | **Matching / randomization** | Future governed runtime | Not implemented or authorized here |
| 6 | **Method suitability** | Future layer | Assignment-feasible ≠ estimator-valid |
| 7 | **Production authorization** | Always false here | Never granted by this contract |

---

## 11. Future contract concepts

| Concept | Purpose |
|---------|---------|
| `DesignAssignmentFeasibilityInput` | Bundled upstream reports, unit inventory, cell requirements |
| `DesignAssignmentFeasibilityConfig` | Thresholds, blocking vs warning modes |
| `DesignAssignmentFeasibilityReport` | Top-level assignment feasibility report |
| `AssignmentUnitSpec` | Per-unit eligibility and metadata |
| `AssignmentCellRequirementSpec` | Per-cell min/max/target unit requirements |
| `AssignmentConstraintSpec` | Typed constraint with category and status |
| `AssignmentEligibilityReport` | Eligible/excluded/available unit counts |
| `AssignmentCellCapacityReport` | Per-cell capacity vs requirements |
| `AssignmentMutualExclusivityReport` | Cross-cell exclusivity validation |
| `AssignmentHierarchyConstraintReport` | Geo hierarchy constraint status |
| `AssignmentMarketExclusionReport` | Market exclusion audit |
| `AssignmentBalanceReadinessReport` | Pre-assignment balance covariate readiness |
| `AssignmentInterferenceRiskReport` | Interference risk flags |
| `AssignmentSharedControlReport` | Common-control unit reservation |
| `AssignmentScenarioHandoffReport` | Scenario policy status handoff |
| `AssignmentPowerMdeHandoffReport` | Power/MDE readiness handoff |
| `AssignmentMethodSuitabilityHandoffReport` | Method-suitability review handoff |
| `AssignmentFeasibilityStatus` | Assignment feasibility enum |
| `AssignmentConstraintStatus` | Per-constraint status enum |
| `AssignmentIssue` / `AssignmentIssueSeverity` | Issue records |
| `AssignmentClaimBoundaryReport` | Authorization boundaries |

---

## 12. Assignment feasibility statuses

| Status | Meaning |
|--------|---------|
| `ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME` | Future assignment runtime may attempt assignment; **no units assigned** |
| `ASSIGNMENT_FEASIBILITY_READY_WITH_WARNINGS` | Ready with advisory warnings |
| `ASSIGNMENT_FEASIBILITY_PROVISIONAL` | Conditional; missing metadata or upstream provisional |
| `ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DATA_READINESS` | Profiler/data blocked |
| `ASSIGNMENT_FEASIBILITY_BLOCKED_BY_GEO_FEASIBILITY` | Geo feasibility blocked |
| `ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DESIGN_STRUCTURE` | Design cell structure blocked |
| `ASSIGNMENT_FEASIBILITY_BLOCKED_BY_SCENARIO_POLICY` | Scenario policy blocked |
| `ASSIGNMENT_FEASIBILITY_BLOCKED_BY_POWER_MDE_READINESS` | Power/MDE blocked |
| `ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS` | Not enough eligible units |
| `ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY` | Cell min/max cannot be met |
| `ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CONSTRAINTS` | Hard constraint violation |
| `ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK` | Split-control or redesign pending |
| `ASSIGNMENT_FEASIBILITY_REQUIRES_METHOD_SUITABILITY_REVIEW` | Estimator/inference blocked |
| `ASSIGNMENT_FEASIBILITY_NOT_EVALUATED` | Prerequisites missing |

---

## 13. Assignment constraint statuses

| Status | Meaning |
|--------|---------|
| `ASSIGNMENT_CONSTRAINT_SATISFIED` | Constraint met |
| `ASSIGNMENT_CONSTRAINT_SATISFIED_WITH_WARNINGS` | Met with warnings |
| `ASSIGNMENT_CONSTRAINT_PROVISIONAL` | Conditional / incomplete metadata |
| `ASSIGNMENT_CONSTRAINT_BLOCKING` | Hard block |
| `ASSIGNMENT_CONSTRAINT_REQUIRES_REDESIGN` | Redesign/recheck needed |
| `ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT` | User must supply missing rules |
| `ASSIGNMENT_CONSTRAINT_NOT_EVALUATED` | Not yet evaluated |

---

## 14. Assignment unit concepts

| Field | Purpose |
|-------|---------|
| `unit_id` | Unique assignment unit identifier |
| `geo_id` / `geo_name` | Geo reference |
| `region` / `country` / `market_group` / `business_unit` | Hierarchy dimensions |
| `eligible` | Eligibility flag |
| `exclusion_reason` | Why excluded |
| `available_for_assignment` | Available after exclusions |
| `prior_assignment_cell` | Prior cell assignment if any |
| `hierarchy_path` | Hierarchy path metadata |
| `metadata` | Additional audit fields |

**Rule:** Unit eligibility is necessary but not sufficient for assignment feasibility.

---

## 15. Cell requirement concepts

| Field | Purpose |
|-------|---------|
| `cell_id` / `cell_role` | Cell identity |
| `minimum_units` / `maximum_units` / `target_units` | Capacity bounds |
| `requires_bau_control` / `requires_common_control` / `requires_split_control` | Control structure flags |
| `requires_matched_pair` | Matched-pair design flag |
| `requires_source_destination_mapping` | Budget reallocation flag |
| `eligible_unit_pool` / `blocked_unit_pool` | Unit pool constraints |

---

## 16. Assignment constraint categories

`DATA_ELIGIBILITY_CONSTRAINT` · `GEO_FEASIBILITY_CONSTRAINT` · `DESIGN_STRUCTURE_CONSTRAINT` · `SCENARIO_POLICY_CONSTRAINT` · `POWER_MDE_READINESS_CONSTRAINT` · `MINIMUM_UNIT_COUNT_CONSTRAINT` · `MAXIMUM_UNIT_COUNT_CONSTRAINT` · `CELL_CAPACITY_CONSTRAINT` · `MUTUAL_EXCLUSIVITY_CONSTRAINT` · `COMMON_CONTROL_CONSTRAINT` · `SPLIT_CONTROL_REDESIGN_CONSTRAINT` · `MATCHED_PAIR_REQUIREMENT_CONSTRAINT` · `BLOCK_REQUIREMENT_CONSTRAINT` · `GEO_HIERARCHY_CONSTRAINT` · `MARKET_EXCLUSION_CONSTRAINT` · `BUSINESS_UNIT_CONSTRAINT` · `REGION_COUNTRY_CONSTRAINT` · `BALANCE_READINESS_CONSTRAINT` · `INTERFERENCE_RISK_CONSTRAINT` · `SOURCE_DESTINATION_MAPPING_CONSTRAINT` · `METHOD_SUITABILITY_CONSTRAINT` · `PRODUCTION_AUTHORIZATION_CONSTRAINT`

This contract defines categories only. Future runtime may evaluate them deterministically. This artifact does not solve assignment.

---

## 17. Future input dependencies

`profiler_report` · `geo_unit_market_feasibility_report` · `spend_requirement_manipulation_feasibility_report` · `power_mde_diagnostics_report` · `design_cell_structure_runtime_report` · `design_scenario_policy_feasibility_report` · `eligible_units` · `excluded_units` · `assignment_unit_universe` · `cell_requirements` · `design_structure_type` · `scenario_policy_status` · `scenario_recheck_requirements` · `split_control_required` · `common_control_cells` · `cell_roles` · `contrast_specs` · `minimum_units_per_cell` · `maximum_units_per_cell` · `target_units_per_cell` · `geo_hierarchy_constraints` · `market_exclusion_constraints` · `business_unit_constraints` · `region_country_constraints` · `mutual_exclusivity_constraints` · `balance_readiness_requirements` · `interference_risk_constraints` · `method_suitability_review_required`

---

## 18. Future output concepts

`DesignAssignmentFeasibilityReport` · `AssignmentReadinessReport` · `AssignmentEligibilityReport` · `AssignmentCellCapacityReport` · `AssignmentConstraintReport` · `AssignmentMutualExclusivityReport` · `AssignmentSharedControlReport` · `AssignmentSplitControlReport` · `AssignmentHierarchyReport` · `AssignmentMarketExclusionReport` · `AssignmentBalanceReadinessReport` · `AssignmentInterferenceRiskReport` · `AssignmentScenarioHandoffReport` · `AssignmentPowerMdeHandoffReport` · `AssignmentMethodSuitabilityHandoffReport` · `AssignmentClaimBoundaryReport`

---

## 19. Future report fields

`artifact_id` · `design_id` · `assignment_feasibility_status` · `assignment_readiness_summary` · `eligible_unit_count` · `excluded_unit_count` · `available_unit_count` · `required_cell_count` · `cell_capacity_reports` · `constraint_reports` · `mutual_exclusivity_report` · `shared_control_report` · `split_control_report` · `hierarchy_report` · `market_exclusion_report` · `balance_readiness_report` · `interference_risk_report` · `scenario_handoff_report` · `power_mde_handoff_report` · `method_suitability_handoff_report` · `claim_boundary_report` · `issues` · `warnings` · `blocking_reasons`

---

## 20. Readiness gates

| # | Gate | Block rule |
|---|------|------------|
| 1 | profiler/data readiness | Blocked → assignment blocked |
| 2 | geo unit/market feasibility | Blocked → assignment blocked |
| 3 | design cell structure | Blocked → assignment blocked |
| 4 | scenario policy feasibility | Blocked → blocked/provisional |
| 5 | power/MDE readiness | Blocked → no power-ready assignment |
| 6 | assignment unit universe | Missing → blocked |
| 7 | eligible unit inventory | Insufficient → blocked |
| 8 | cell requirement | Missing → blocked |
| 9 | cell capacity | Min not met → blocked |
| 10 | mutual exclusivity | Violation → blocked |
| 11 | shared-control/split-control | Split → redesign/recheck |
| 12 | geo hierarchy/market exclusion | Ambiguous → provisional/user input |
| 13 | balance-readiness | Missing covariates → warn |
| 14 | interference-risk | High/uncharacterized → warn/block |
| 15 | method-suitability precheck | Review required → estimator blocked |

---

## 21. Common-control treatment

- Common-control designs must reserve enough eligible units for the shared control cell
- Common control creates dependency across contrasts
- Must not assume validity if scenario policy flagged shared-control conflict
- Structurally valid + scenario conflicted → provisional or blocked
- Common-control assignment readiness does not authorize estimator/inference validity

---

## 22. Split-control redesign treatment

- Split control is a redesign/recheck proposal
- Changes required cell count and units per contrast
- Requires reassessing cell capacity, assignment feasibility, power/MDE, and method suitability
- Must not be marked immediately feasible just because it avoids common-control conflict
- Future runtime emits `ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK` until downstream gates pass

---

## 23. Matched-pair / block / rerandomized treatment

- **Matched-pair:** requires even/paired capacity and pairability diagnostics in future runtime
- **Block:** requires sufficient units per block and block metadata
- **Rerandomized:** requires candidate assignment generation and balance diagnostics in later runtime
- This contract does not generate pairs, blocks, or randomizations

---

## 24. Geo hierarchy and exclusion treatment

- Geo hierarchy constraints must be preserved before assignment
- Market exclusions must be explicit and auditable
- Region/country/business-unit constraints must not be silently ignored
- Missing hierarchy or exclusion rules → provisional or `ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT`

---

## 25. Balance-readiness and interference-risk treatment

- Balance readiness is pre-assignment diagnostic readiness, not balance achieved
- Future runtime reports whether balance covariates are available for minimum balance checks
- Interference risk carried as warning or blocker depending severity
- No balance optimization or interference adjustment in this contract
- No estimator selection in this contract

---

## 26. Examples

### Example 1 — simple two-cell assignment feasibility

Design: one treatment cell, one BAU control cell. Eligible units: 30. Minimum per cell: 10. **Status:** `ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME`. No units assigned.

### Example 2 — insufficient eligible units

Design: three test cells plus one common control. Minimum per cell: 8. Eligible units: 25. Required minimum: 32. **Status:** `ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS`.

### Example 3 — common-control capacity issue

Design: T1, T2, T3 share C0. C0 requires 15 units. Only 10 eligible control units remain. **Status:** `ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY`.

### Example 4 — split-control redesign

Scenario policy proposed split controls C1, C2, C3. Increases cell count and changes power/MDE. **Status:** `ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK`.

### Example 5 — matched-pair requirement

Design: matched-pair. Eligible units: 21. Pairing requires even units or allowed holdout. **Status:** `ASSIGNMENT_FEASIBILITY_PROVISIONAL`. No pairs generated.

### Example 6 — geo hierarchy constraint

Design requires balanced region representation. Region metadata missing for some units. **Status:** `ASSIGNMENT_FEASIBILITY_PROVISIONAL` / `ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT`.

### Example 7 — market exclusion

Markets excluded due to legal/business constraints. Excluded units not counted toward capacity. **Status:** uses only eligible units.

### Example 8 — method-suitability review required

Dosage/difference-in-policy design. Assignment capacity sufficient. **Status:** structurally feasible but `ASSIGNMENT_FEASIBILITY_REQUIRES_METHOD_SUITABILITY_REVIEW`; estimator/inference blocked.

---

## 27. Claim boundaries

### Always false

`runtime_assignment_feasibility_implemented` · `geo_assignment_computed` · `matched_pairs_generated` · `blocks_generated` · `randomization_computed` · `rerandomization_computed` · `thinning_design_generated` · `matching_optimization_computed` · `balance_optimization_computed` · `interference_adjustment_computed` · `scenario_policy_feasibility_computed` · `power_computed` · `mde_computed` · `production_authorization_granted` · etc.

### Allowed contract-level positives

`assignment_feasibility_contract_defined` · `eligible_unit_contract_defined` · `cell_capacity_contract_defined` · `assignment_constraint_categories_defined` · `common_control_assignment_boundary_defined` · `split_control_redesign_boundary_defined` · `matched_pair_block_boundary_defined` · `hierarchy_exclusion_boundary_defined` · `balance_readiness_boundary_defined` · `interference_risk_boundary_defined` · `claim_boundaries_defined`

---

## 28. Future implementation acceptance criteria

Future `DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001` must:

1. Consume profiler, geo feasibility, design-cell structure, scenario policy feasibility, power/MDE, eligible/excluded units, and cell requirements
2. Block if upstream hard gates are blocked
3. Validate assignment unit universe
4. Count eligible/excluded/available units (excluded not counted as available)
5. Validate min/max/target units per cell
6. Evaluate cell capacity before assignment
7. Preserve common-control and split-control implications
8. Preserve scenario recheck and power/MDE handoff
9. Validate mutual exclusivity and hierarchy/exclusion constraints
10. Report balance-readiness and interference-risk (no optimization)
11. Emit assignment-feasibility and constraint statuses
12. **Not** assign units, generate matches/pairs/blocks, randomize, optimize balance, or compute power/MDE/lift/ROI/estimator validity/production authorization

---

## 29. Future tests

Future runtime tests should cover all cases listed in the contract harness `FUTURE_IMPLEMENTATION_TESTS` (24 cases), including blocked upstream gates, insufficient units, cell capacity, mutual exclusivity, common-control capacity, split-control recheck, matched-pair pairability, hierarchy metadata, market exclusions, balance covariate reporting, interference risk reporting, method suitability blocking, and claim-boundary enforcement.

---

## 30. Roadmap placement

```
GEO_KPI_SPEND_DATA_PROFILER_001
  → GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001
  → … → DESIGN_CELL_STRUCTURE_RUNTIME_001
  → DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001
  → DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001 ✅ (this artifact)
  → DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001 (recommended next)
```

---

## 31. Recommended next artifact

**Primary:** `DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001` — conservative deterministic runtime implementing the contract algorithm without geo assignment or matching.

**Alternative:** `METHOD_SUITABILITY_HANDOFF_CONTRACT_001` — if roadmap prefers method governance before assignment runtime.

**Do not implement either in this artifact.**

---

## Appendix: Metadata harness

| File | Role |
|------|------|
| `panel_exp/validation/design_assignment_feasibility_contract_001.py` | Metadata-only contract harness |
| `tests/validation/test_design_assignment_feasibility_contract_001.py` | Contract validation tests |
| `docs/track_d/archives/DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001_summary.json` | Machine-readable summary |
