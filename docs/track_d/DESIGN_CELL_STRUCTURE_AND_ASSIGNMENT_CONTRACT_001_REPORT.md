# DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001` |
| **Artifact type** | `design_cell_structure_assignment_and_scenario_contract` |
| **Artifact version** | `1.1.0` (amended with scenario-planner concepts) |
| **Status** | `completed` |
| **Scope** | `contract_only_no_runtime_assignment_or_scenario_optimization` |
| **Base commit** | `1861c95` (Implement power MDE diagnostics runtime) |
| **Final verdict** | `design_cell_contrast_and_scenario_contract_defined_no_runtime_assignment_or_scenario_optimization` |

This artifact is a **contract/specification document only**. It defines typed contracts for candidate experiment cells, contrast-specific roles, shared-control dependencies, scenario-level spend-policy plans, assignment constraints, and redesign/recheck resolution options. **No runtime design generation, geo assignment, scenario optimization, randomization, power/MDE, inference, lift/ROI, or production authorization was implemented or authorized.**

---

## 2. Source files inspected

| File | Role |
|------|------|
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Immediate upstream power/MDE readiness runtime |
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Spend manipulation semantics |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo feasibility upstream |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Data profiler upstream |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Golden path sequencing |

---

## 3. Why this contract is needed

In multi-test geo setups, the same common-control cell can serve different statistical roles across different contrasts. Changing a shared cell's spend level may help one contrast while breaking another. Without an explicit contract covering **cells + contrasts + scenario policy plans + shared-control dependencies + cross-contrast conflicts + redesign/recheck options**, future planners may:

- treat cell count as sufficient structure
- silently reuse a manipulated common cell as clean BAU control
- optimize one contrast while invalidating others
- recommend split-control redesigns as immediately feasible

This contract defines the boundary before any runtime design-cell, scenario, or assignment artifact is implemented.

---

## 4. Core goal statement

`DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001` defines the future typed contract for candidate experiment cells, contrast-specific roles, shared-control dependencies, scenario-level spend-policy plans, assignment constraints, and redesign/recheck resolution options. It establishes how future design and scenario diagnostics may represent go-dark, heavy-up, go-live, budget reallocation, dosage contrast, difference-in-policy, common-control, multi-cell, and matched-pair structures without performing assignment, scenario optimization, inference, or production authorization.

---

## 5. Relationship to profiler

Future design-cell/scenario/assignment runtime must consume `GeoKpiSpendDataProfileReport`. If profiler readiness is blocked, future assignment runtime must not run.

---

## 6. Relationship to geo feasibility

Future runtime must consume `GeoUnitMarketFeasibilityReport`. Eligible and excluded geo units inform assignment constraints but are not assigned here.

---

## 7. Relationship to spend feasibility diagnostics

Future runtime must consume `SpendRequirementManipulationFeasibilityReport` for manipulation policies, historical support, required spend contrasts, and candidate manipulation options.

---

## 8. Relationship to power/MDE runtime

Future runtime must consume `PowerMdeDiagnosticsReport` for `power_mde_runtime_status`, `power_mde_runtime_mode`, and per-contrast KPI MDE targets. Power/MDE readiness does not mean powered.

---

## 9. Conceptual distinctions

| Concept | Definition | Implemented here? |
|---------|------------|-------------------|
| **Cell structure** | Abstract planned shape (cells and roles) | Contract only |
| **Cell role** | Global operational role of a cell | Contract only |
| **Contrast-specific role** | Cell's role within one comparison | Contract only |
| **Manipulation policy** | Spend/media policy per cell in a scenario | Contract only |
| **Contrast** | Statistical comparison with required spend/KPI targets | Contract only |
| **Scenario policy plan** | Full-cell spend-policy configuration | Contract only |
| **Shared-control dependency** | Common cell used by multiple contrasts | Contract only |
| **Assignment readiness** | Whether assignment can be attempted later | Statuses defined |
| **Redesign/recheck resolution** | Structural fixes requiring downstream recheck | Options defined |
| **Design generation** | Creating candidate designs | Future runtime only |
| **Estimator/inference validity** | Method suitability | Future method layer only |
| **Production authorization** | Production use | Always blocked |

**Critical non-upgrades:**

- `DESIGN_ASSIGNMENT_READY_FOR_RUNTIME` ≠ design generated
- scenario feasible ≠ production-ready
- cell structure declared ≠ geo units assigned
- split common control ≠ immediately feasible recommendation

---

## 10. Future contract concepts

`DesignCellStructureInput`, `DesignCellStructureConfig`, `DesignCellStructureReport`, `DesignCellSpec`, `DesignCellRole`, `ContrastCellRole`, `DesignContrastSpec`, `DesignContrastType`, `DesignScenarioSpec`, `CellPolicyPlan`, `SharedControlDependency`, `CrossContrastConflict`, `ScenarioResolutionOption`, `ScenarioFeasibilityStatus`, `DesignManipulationPolicy`, `DesignStructureType`, `DesignAssignmentConstraint`, `DesignAssignmentConstraintSeverity`, `DesignAssignmentReadinessStatus`, `DesignCellStructureIssue`, `DesignCellStructureSeverity`, `DesignCellStructureBoundary`, `DesignSpendCompatibilitySpec`, `DesignPowerMdeCompatibilitySpec`, `DesignEstimandCompatibilitySpec`, `HistoricalSupportSpec`

---

## 11. Design structure types

`SINGLE_TREATMENT_CONTROL`, `MULTI_CELL_COMMON_CONTROL`, `MULTI_CELL_SPLIT_CONTROL`, `MATCHED_PAIR`, `RERANDOMIZED_BLOCK`, `THINNING_DESIGN`, `QUICK_BLOCK`, `DOSAGE_CONTRAST`, `DIFFERENCE_IN_POLICY`, `BUDGET_REALLOCATION`, `GO_LIVE`, `UNKNOWN`

Representation contract only — not endorsement that all types are production-governed.

---

## 12. Contrast types

`GO_DARK_VS_BAU`, `HEAVY_UP_VS_BAU`, `GO_LIVE_VS_NO_OR_LOW_SPEND`, `DOSAGE_LOW_VS_HIGH`, `DIFFERENCE_IN_POLICY`, `BUDGET_REALLOCATION_SOURCE_VS_DESTINATION`, `MULTI_CELL_COMMON_CONTROL_CONTRAST`, `UNKNOWN`

Each contrast must carry: `contrast_id`, `contrast_type`, cell ids, `required_kpi_mde`, `required_spend_contrast`, `estimand_type`, BAU-control requirement, method-suitability review requirement.

---

## 13. Cell roles

`TEST_CELL`, `TREATMENT`, `CONTROL`, `COMMON_CONTROL`, `COMMON_REFERENCE_CELL`, `BUSINESS_AS_USUAL_CONTROL`, `LOW_DOSAGE`, `MEDIUM_DOSAGE`, `HIGH_DOSAGE`, `SOURCE_REDUCTION`, `DESTINATION_INCREASE`, `GO_LIVE_CELL`, `HOLDOUT`, `EXCLUDED`, `UNKNOWN`

---

## 14. Contrast-specific roles

`TREATMENT_FOR_CONTRAST`, `COMPARISON_FOR_CONTRAST`, `BAU_CONTROL_FOR_CONTRAST`, `LOW_POLICY_ANCHOR_FOR_CONTRAST`, `HIGH_POLICY_CELL_FOR_CONTRAST`, `SOURCE_CELL_FOR_REALLOCATION_CONTRAST`, `DESTINATION_CELL_FOR_REALLOCATION_CONTRAST`, `EXCLUDED_FROM_CONTRAST`, `UNKNOWN`

**Rule:** The same physical cell may serve different contrast-specific roles across comparisons only when policies are compatible and explicitly labeled.

---

## 15. Manipulation policies

`BUSINESS_AS_USUAL`, `GO_DARK`, `HEAVY_UP`, `GO_LIVE`, `BUDGET_REALLOCATION_SOURCE`, `BUDGET_REALLOCATION_DESTINATION`, `LOW_SPEND_POLICY`, `HIGH_SPEND_POLICY`, `DOSAGE_POLICY`, `DIFFERENCE_IN_POLICY`, `UNKNOWN`

---

## 16. Scenario feasibility statuses

| Status | Meaning |
|--------|---------|
| `SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE` | Scenario satisfies structural/spend/estimand constraints under current cell structure |
| `SCENARIO_PARTIALLY_FEASIBLE` | Some contrasts feasible, others not |
| `SCENARIO_REQUIRES_ESTIMAND_SHIFT` | Manipulated controls require dosage/difference-in-policy estimand |
| `SCENARIO_REQUIRES_COMMON_CONTROL_MANIPULATION` | Shared control must be changed to satisfy contrasts |
| `SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT` | Split-control redesign proposed |
| `SCENARIO_REQUIRES_POWER_MDE_RECHECK` | Power/MDE must be re-evaluated after scenario change |
| `SCENARIO_REQUIRES_ASSIGNMENT_RECHECK` | Assignment must be re-evaluated after redesign |
| `SCENARIO_REQUIRES_METHOD_SUITABILITY_REVIEW` | Method layer review required |
| `SCENARIO_OUT_OF_HISTORICAL_SUPPORT` | Proposed spend exceeds historical support |
| `SCENARIO_BLOCKED` | Scenario cannot proceed |
| `SCENARIO_NOT_EVALUATED` | Not yet evaluated |

Scenario feasibility does not mean production-ready.

---

## 17. Assignment-readiness statuses

| Status | Meaning |
|--------|---------|
| `DESIGN_ASSIGNMENT_READY_FOR_RUNTIME` | Typed inputs sufficient for future assignment diagnostic (not assigned) |
| `DESIGN_ASSIGNMENT_READY_WITH_WARNINGS` | Ready with warnings |
| `DESIGN_ASSIGNMENT_PROVISIONAL` | Partial structure |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_DATA_READINESS` | Profiler/data blocked |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_GEO_FEASIBILITY` | Geo blocked |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_SPEND_FEASIBILITY` | Spend blocked |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_POWER_MDE_READINESS` | Power/MDE blocked |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_CELL_STRUCTURE` | Cell structure missing/invalid |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_CONTRAST_STRUCTURE` | Contrast specs missing/invalid |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_SCENARIO_CONFLICT` | Cross-contrast conflict |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_CONSTRAINTS` | Constraint violation |
| `DESIGN_ASSIGNMENT_REQUIRES_DOSAGE_ESTIMAND_REVIEW` | Dosage estimand review |
| `DESIGN_ASSIGNMENT_REQUIRES_METHOD_SUITABILITY_REVIEW` | Method review |
| `DESIGN_ASSIGNMENT_REQUIRES_REDESIGN_RECHECK` | Redesign proposal requires recheck |
| `DESIGN_ASSIGNMENT_NOT_EVALUATED` | Not evaluated |

---

## 18. Future input dependencies

`profiler_report`, `geo_unit_market_feasibility_report`, `spend_requirement_manipulation_feasibility_report`, `power_mde_diagnostics_report`, `eligible_geo_units`, `excluded_geo_units`, `candidate_cell_count`, `candidate_cell_roles`, `candidate_contrast_specs`, `candidate_scenario_specs`, `candidate_manipulation_policies`, `candidate_design_structure_type`, `minimum_units_per_cell`, `maximum_units_per_cell`, `geo_hierarchy`, region/country/business-unit constraints, channel/campaign constraints, `baseline_spend_by_cell`, `historical_spend_support_by_cell`, spend feasibility outputs, `required_spend_delta_by_contrast`, `candidate_manipulation_options`, `historical_support_status`, `control_contamination_flags`, `dosage_contrast_estimand_required`, `difference_in_policy_required`, `business_as_usual_control_preserved`, `shared_control_dependencies`, `method_suitability_review_required`, `power_mde_runtime_status`, `power_mde_runtime_mode`

---

## 19. Future output concepts

`DesignCellStructureReport`, `DesignCellReadinessReport`, `DesignCellRoleReport`, `DesignContrastReport`, `DesignScenarioReport`, `SharedControlDependencyReport`, `CrossContrastConflictReport`, `ScenarioResolutionReport`, `DesignAssignmentConstraintReport`, `DesignSpendCompatibilityReport`, `DesignPowerMdeCompatibilityReport`, `DesignEstimandCompatibilityReport`, `DesignClaimBoundaryReport`

---

## 20. Readiness gates

| Order | Gate |
|-------|------|
| 1 | profiler_gate |
| 2 | geo_unit_market_feasibility_gate |
| 3 | spend_feasibility_gate |
| 4 | power_mde_readiness_gate |
| 5 | cell_structure_declaration_gate |
| 6 | contrast_structure_gate |
| 7 | cell_role_validity_gate |
| 8 | manipulation_policy_compatibility_gate |
| 9 | scenario_policy_plan_gate |
| 10 | shared_control_dependency_gate |
| 11 | assignment_constraint_gate |
| 12 | estimand_compatibility_gate |
| 13 | method_suitability_precheck_gate |

If a shared control is manipulated, every contrast using it must be reclassified or blocked. If changing a shared control helps one contrast but weakens another, emit `CrossContrastConflict`.

---

## 21. Scenario planner contract logic

Future runtime algorithm (contract level only — **not implemented here**):

For each candidate scenario:
1. Assign proposed spend policy to each cell
2. Compute achieved spend contrast for every contrast
3. Compare achieved contrast against required spend contrast
4. Check historical support for every proposed cell spend level
5. Check whether BAU control is preserved where required
6. Detect whether one shared cell's policy helps one contrast but harms another
7. Classify estimand shifts
8. Classify method-suitability review requirements
9. Emit scenario feasibility status
10. Emit resolution options

---

## 22. Four-cell common-control scenario example

**Setup:** C0 = common BAU control; T1, T2, T3 = test cells.

**Baselines (weekly):** C0=$100K, T1=$80K, T2=$120K, T3=$100K

**Required spend contrasts:** T1 vs C0=$150K; T2 vs C0=$100K; T3 vs C0=$60K

**Historical max:** C0=$130K, T1=$120K, T2=$250K, T3=$180K

### Scenario A — preserve common BAU control

C0=$100K BAU; T1=$0 go-dark; T2=$220K heavy-up; T3=$160K heavy-up

- T1 achieved=$100K, required=$150K → insufficient
- T2 achieved=$120K, required=$100K → feasible
- T3 achieved=$60K, required=$60K → feasible
- BAU preserved=true
- Status: `SCENARIO_PARTIALLY_FEASIBLE`
- Resolutions: extend duration, lower MDE, convert T1 to high-spend/dosage, split controls, drop/sequence T1

### Scenario B — raise common control to help go-dark

C0=$150K manipulated; T1=$0; T2=$220K; T3=$160K

- T1 achieved=$150K → operational contrast feasible
- T2 achieved=$70K → insufficient
- T3 achieved=$10K → insufficient
- BAU preserved=false; C0 exceeds historical max
- Status: `SCENARIO_REQUIRES_ESTIMAND_SHIFT`, `SCENARIO_OUT_OF_HISTORICAL_SUPPORT`
- Resolutions: reframe as difference-in-policy, avoid manipulating C0, split controls, redesign

### Scenario C — lower common control to help heavy-up

C0=$60K manipulated; T1=$0; T2=$160K; T3=$120K

- T1 achieved=$60K → insufficient
- T2 achieved=$100K → feasible
- T3 achieved=$60K → feasible
- BAU preserved=false
- Status: `SCENARIO_REQUIRES_ESTIMAND_SHIFT`, `SCENARIO_PARTIALLY_FEASIBLE`
- Resolutions: reframe as dosage/difference-in-policy, preserve BAU and accept T1 failure, split controls, redesign

### Scenario D — preserve BAU, convert T1 to high-spend/dosage

C0=$100K BAU; T1=$250K high-spend; T2=$220K; T3=$160K

- T1 achieved=$150K → feasible
- T2=$120K → feasible; T3=$60K → feasible
- BAU preserved=true; T1 exceeds historical max
- Status: `SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE` with out-of-support warning
- Resolutions: cap T1 spend, extend duration, lower MDE, business-response-risk scenario

### Scenario E — split common control (redesign proposal)

Original: C0 shared by T1, T2, T3. Proposed: C1/C2/C3 separate controls.

- **Not a direct feasible recommendation** — redesign proposal
- Changes cell count, assignment, match quality, power/MDE
- Status: `SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT`, `SCENARIO_REQUIRES_POWER_MDE_RECHECK`, `SCENARIO_REQUIRES_ASSIGNMENT_RECHECK`
- Must recheck before feasibility claimed

---

## 23. Standard go-dark treatment

Requires go-dark treatment cell + `BUSINESS_AS_USUAL_CONTROL`. Manipulated control blocks standard go-dark. May be `DIFFERENCE_IN_POLICY` if labeled.

---

## 24. Heavy-up treatment

Heavy-up vs BAU control. Shared control manipulation affects achievable contrast. Does not prove powered or estimator-valid.

---

## 25. Go-live treatment

Near-zero baseline + active planned spend. Preserves baseline support flags. Does not imply causal lift estimable.

---

## 26. Budget reallocation treatment

Source-reduction + destination-increase cells required. Estimand shifts to reallocation impact. No ROI or budget optimization authorization.

---

## 27. Dosage / difference-in-policy treatment

First-class design and scenario structure. Not standard go-dark. Requires estimand labels and method-suitability review.

---

## 28. Shared/common control treatment

Common control shared only when policy compatible with every contrast. BAU manipulation reclassifies or blocks dependent contrasts. Cross-contrast conflicts required when one contrast gains at another's expense.

---

## 29. Assignment constraints

`DATA_ELIGIBILITY_CONSTRAINT`, `GEO_FEASIBILITY_CONSTRAINT`, `SPEND_FEASIBILITY_CONSTRAINT`, `POWER_MDE_READINESS_CONSTRAINT`, `CELL_SIZE_CONSTRAINT`, `MUTUAL_EXCLUSIVITY_CONSTRAINT`, `BUSINESS_AS_USUAL_CONTROL_CONSTRAINT`, `CONTRAST_STRUCTURE_CONSTRAINT`, `SHARED_CONTROL_DEPENDENCY_CONSTRAINT`, `SCENARIO_POLICY_COMPATIBILITY_CONSTRAINT`, `DOSAGE_ESTIMAND_CONSTRAINT`, `BUDGET_REALLOCATION_MAPPING_CONSTRAINT`, `MARKET_EXCLUSION_CONSTRAINT`, `GEO_HIERARCHY_CONSTRAINT`, `BALANCE_CONSTRAINT`, `INTERFERENCE_RISK_CONSTRAINT`, `METHOD_SUITABILITY_CONSTRAINT`, `REDESIGN_RECHECK_CONSTRAINT`, `PRODUCTION_AUTHORIZATION_CONSTRAINT`

Categories only — future runtime evaluates; this artifact does not solve assignment.

---

## 30. Examples (summary)

1. Standard go-dark: GO_DARK + BAU control — ready if gates pass, not powered
2. Heavy-up: HEAVY_UP + BAU — historical support preserved
3. Manipulated control blocks go-dark — may be DIFFERENCE_IN_POLICY
4. Dosage ladder: LOW/MEDIUM/HIGH — dosage estimand required
5. Budget reallocation: SOURCE + DESTINATION — mapping required
6. Common control across contrasts: contrast-specific roles required
7. Shared control conflict: raising C0 helps T1, weakens T2/T3 — `CrossContrastConflict`
8. Split common control: redesign/recheck required, not immediately feasible

---

## 31. Claim boundaries

**Always false:** `runtime_design_generation_implemented`, `runtime_scenario_planner_implemented`, `geo_assignment_computed`, `randomization_computed`, `rerandomization_computed`, `matching_optimization_computed`, `power_computed`, `mde_computed`, `p_value_computed`, `confidence_interval_computed`, `lift_computed`, `roi_computed`, `budget_optimization_authorized`, `candidate_design_authorized`, `treatment_control_assignment_authorized`, `estimator_inference_authorized`, `mmm_runtime_calls_implemented`, `mmm_calibration_authorized`, `production_authorization_granted`, `llm_decisioning_authorized`

**Contract positive:** contrast/scenario/shared-control/cross-contrast/resolution contracts defined

---

## 32. Future implementation acceptance criteria

Future implementation must consume cells, contrasts, and scenario specs; block on upstream gates; validate contrast-specific roles; detect cross-contrast conflicts; emit scenario feasibility and redesign/recheck requirements; not assign geo units or authorize production.

---

## 33. Future tests

17+ tests documented in harness including: missing contrast specs, contrast-specific roles, common control BAU compatibility, shared control manipulation reclassification, raising/lowering C0 tradeoffs, split common control redesign/recheck.

---

## 34. Roadmap placement

```
… → POWER_MDE_DIAGNOSTICS_RUNTIME_001 ✅
→ DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001 ✅ (this artifact, v1.1 scenario amendment)
→ DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001 (next)
```

---

## 35. Recommended next artifact

**`DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001`**

**Alternative:** `DESIGN_CELL_STRUCTURE_RUNTIME_001`

---

## 36. Final verdict

**`design_cell_contrast_and_scenario_contract_defined_no_runtime_assignment_or_scenario_optimization`**

Design-cell, contrast, and scenario contract defined. Cells plus contrasts plus scenario policy plans plus shared-control dependencies plus cross-contrast conflicts plus redesign/recheck resolution options documented. No runtime assignment or scenario optimization granted.
