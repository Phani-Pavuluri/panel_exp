# DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001` |
| **Artifact type** | `design_cell_structure_and_assignment_contract` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_runtime_assignment` |
| **Base commit** | `1861c95` (Implement power MDE diagnostics runtime) |
| **Final verdict** | `design_cell_structure_and_assignment_contract_defined_no_runtime_assignment_or_production_authorization` |

This artifact is a **contract/specification document only**. It defines typed contracts for candidate experiment cell structures, cell roles, assignment constraints, and assignment-readiness statuses. **No runtime design generation, geo assignment, randomization, power/MDE, inference, lift/ROI, or production authorization was implemented or authorized.**

---

## 2. Source files inspected

| File | Role |
|------|------|
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Immediate upstream power/MDE readiness runtime |
| `POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001` | Power/MDE lane contract |
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Spend manipulation semantics |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo feasibility upstream |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Data profiler upstream |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Golden path sequencing |

---

## 3. Why this contract is needed

`POWER_MDE_DIAGNOSTICS_RUNTIME_001` can detect cell structure concepts but does not define the typed contract for design cells and assignment. Without an explicit contract, future layers may incorrectly upgrade:

- assignment readiness → design generated
- cell structure declared → geo units assigned
- go-dark structure → standard untreated control assumed
- dosage contrast feasible → estimator approved
- budget reallocation structure → ROI or budget optimization authorized

This contract defines the boundary before any runtime design-cell or assignment artifact is implemented.

---

## 4. Core goal statement

`DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001` defines the future typed contract for candidate experiment cell structures, cell roles, assignment constraints, manipulation semantics, and assignment-readiness statuses. It establishes how future design-generation and assignment diagnostics may represent go-dark, heavy-up, go-live, budget reallocation, dosage contrast, difference-in-policy, common-control, multi-cell, and matched-pair structures without performing assignment, optimization, inference, or production authorization.

---

## 5. Relationship to profiler

Future design-cell/assignment runtime must consume `GeoKpiSpendDataProfileReport` from `GEO_KPI_SPEND_DATA_PROFILER_001`.

**Profiler gate rules:**

- If profiler readiness is blocked, future assignment runtime must not run
- Profiler establishes data eligibility for geo units but does not authorize assignment or design generation

---

## 6. Relationship to geo feasibility

Future design-cell/assignment runtime must consume `GeoUnitMarketFeasibilityReport` from `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001`.

**Geo feasibility gate rules:**

- If geo/unit feasibility is blocked, future assignment runtime must not run
- Eligible and excluded geo units inform assignment constraints but are not assigned here

---

## 7. Relationship to spend feasibility diagnostics

Future design-cell/assignment runtime must consume `SpendRequirementManipulationFeasibilityReport` from `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001`.

**Spend feasibility rules:**

- Manipulation policies (go-dark, heavy-up, go-live, budget reallocation, dosage) must align with spend feasibility outputs
- Historical support status, required spend delta, and candidate manipulation options inform cell structure compatibility
- Spend feasibility does not authorize assignment or design generation

---

## 8. Relationship to power/MDE runtime

Future design-cell/assignment runtime must consume `PowerMdeDiagnosticsReport` from `POWER_MDE_DIAGNOSTICS_RUNTIME_001`.

**Power/MDE readiness rules:**

- `power_mde_runtime_status` and `power_mde_runtime_mode` inform assignment readiness
- Power/MDE readiness does not mean powered or design-feasible
- Blocked power/MDE readiness blocks power-ready assignment claims

---

## 9. Conceptual distinctions

| Concept | Definition | Implemented here? |
|---------|------------|-------------------|
| **Cell structure** | Abstract planned shape of the experiment | Contract only |
| **Cell role** | Semantic role of a cell (treatment, control, dosage, etc.) | Contract only |
| **Manipulation policy** | Spend/media policy change per cell | Contract only |
| **Assignment constraints** | Rules restricting geo-to-cell assignment | Categories defined |
| **Assignment readiness** | Whether assignment can be attempted later | Statuses defined |
| **Design generation** | Creating candidate designs | Future runtime only |
| **Estimator/inference validity** | Method suitability for estimand | Future method layer only |
| **Production authorization** | Production use | Always blocked |

**Critical non-upgrades:**

- `DESIGN_ASSIGNMENT_READY_FOR_RUNTIME` ≠ design generated
- cell structure declared ≠ geo units assigned
- go-dark structure ≠ standard untreated control
- dosage contrast ≠ estimator approved
- budget reallocation ≠ ROI or budget optimization

---

## 10. Future contract concepts

| Contract | Purpose |
|----------|---------|
| `DesignCellStructureInput` | Top-level input bundle |
| `DesignCellStructureConfig` | Thresholds, constraint flags |
| `DesignCellStructureReport` | Top-level structure report |
| `DesignCellSpec` | Single cell specification (id, role, policy) |
| `DesignCellRole` | Cell role enum |
| `DesignManipulationPolicy` | Manipulation policy enum |
| `DesignStructureType` | Design structure type enum |
| `DesignAssignmentConstraint` | Typed constraint with category and severity |
| `DesignAssignmentConstraintSeverity` | INFO / WARNING / BLOCKING |
| `DesignAssignmentReadinessStatus` | Assignment readiness enum |
| `DesignCellStructureIssue` | Typed issue |
| `DesignCellStructureSeverity` | Issue severity |
| `DesignCellStructureBoundary` | Claim ceiling |
| `DesignSpendCompatibilitySpec` | Spend compatibility bundle |
| `DesignPowerMdeCompatibilitySpec` | Power/MDE compatibility bundle |
| `DesignEstimandCompatibilitySpec` | Estimand compatibility bundle |

---

## 11. Design structure types

Representation contract only — not endorsement that all types are production-governed:

| Type | Description |
|------|-------------|
| `SINGLE_TREATMENT_CONTROL` | One treatment + one control |
| `MULTI_CELL_COMMON_CONTROL` | Multiple treatment cells + shared control |
| `MATCHED_PAIR` | Matched-pair structure |
| `RERANDOMIZED_BLOCK` | Rerandomized block design |
| `THINNING_DESIGN` | Thinning design |
| `QUICK_BLOCK` | Quick block design |
| `DOSAGE_CONTRAST` | Low/medium/high dosage ladder |
| `DIFFERENCE_IN_POLICY` | Intentionally different policies |
| `BUDGET_REALLOCATION` | Source reduction + destination increase |
| `GO_LIVE` | Go-live from near-zero baseline |
| `UNKNOWN` | Unspecified structure |

---

## 12. Cell roles

`TREATMENT`, `CONTROL`, `COMMON_CONTROL`, `BUSINESS_AS_USUAL_CONTROL`, `LOW_DOSAGE`, `MEDIUM_DOSAGE`, `HIGH_DOSAGE`, `SOURCE_REDUCTION`, `DESTINATION_INCREASE`, `GO_LIVE_CELL`, `HOLDOUT`, `EXCLUDED`, `UNKNOWN`

---

## 13. Manipulation policies

`BUSINESS_AS_USUAL`, `GO_DARK`, `HEAVY_UP`, `GO_LIVE`, `BUDGET_REALLOCATION_SOURCE`, `BUDGET_REALLOCATION_DESTINATION`, `LOW_SPEND_POLICY`, `HIGH_SPEND_POLICY`, `DOSAGE_POLICY`, `DIFFERENCE_IN_POLICY`, `UNKNOWN`

---

## 14. Assignment-readiness statuses

| Status | Meaning |
|--------|---------|
| `DESIGN_ASSIGNMENT_READY_FOR_RUNTIME` | Typed inputs sufficient for future assignment diagnostic (not assigned) |
| `DESIGN_ASSIGNMENT_READY_WITH_WARNINGS` | Ready with non-blocking warnings |
| `DESIGN_ASSIGNMENT_PROVISIONAL` | Partial structure or exploratory |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_DATA_READINESS` | Profiler/data blocked |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_GEO_FEASIBILITY` | Geo feasibility blocked |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_SPEND_FEASIBILITY` | Spend feasibility blocked |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_POWER_MDE_READINESS` | Power/MDE readiness blocked |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_CELL_STRUCTURE` | Cell structure missing/invalid |
| `DESIGN_ASSIGNMENT_BLOCKED_BY_CONSTRAINTS` | Assignment constraints violated |
| `DESIGN_ASSIGNMENT_REQUIRES_DOSAGE_ESTIMAND_REVIEW` | Dosage estimand review required |
| `DESIGN_ASSIGNMENT_REQUIRES_METHOD_SUITABILITY_REVIEW` | Method suitability review required |
| `DESIGN_ASSIGNMENT_NOT_EVALUATED` | Not yet evaluated |

---

## 15. Future input dependencies

`profiler_report`, `geo_unit_market_feasibility_report`, `spend_requirement_manipulation_feasibility_report`, `power_mde_diagnostics_report`, `eligible_geo_units`, `excluded_geo_units`, `candidate_cell_count`, `candidate_cell_roles`, `candidate_manipulation_policies`, `candidate_design_structure_type`, `minimum_units_per_cell`, `maximum_units_per_cell`, `geo_hierarchy`, region/country/business-unit constraints, channel/campaign constraints, spend feasibility outputs, `required_spend_delta`, `candidate_manipulation_options`, `historical_support_status`, `control_contamination_flags`, `dosage_contrast_estimand_required`, `difference_in_policy_required`, `business_as_usual_control_preserved`, `method_suitability_review_required`, `power_mde_runtime_status`, `power_mde_runtime_mode`

---

## 16. Future output concepts

`DesignCellStructureReport`, `DesignCellReadinessReport`, `DesignCellRoleReport`, `DesignAssignmentConstraintReport`, `DesignSpendCompatibilityReport`, `DesignPowerMdeCompatibilityReport`, `DesignEstimandCompatibilityReport`, `DesignClaimBoundaryReport`

---

## 17. Readiness gates

Future assignment runtime must evaluate gates in order:

| Order | Gate | Block if failed? |
|-------|------|------------------|
| 1 | **profiler_gate** | Yes |
| 2 | **geo_unit_market_feasibility_gate** | Yes |
| 3 | **spend_feasibility_gate** | Blocks spend-compatible assignment |
| 4 | **power_mde_readiness_gate** | Blocks power-ready assignment |
| 5 | **cell_structure_declaration_gate** | Provisional or blocked |
| 6 | **cell_role_validity_gate** | Blocked if invalid |
| 7 | **manipulation_policy_compatibility_gate** | Blocked if incompatible |
| 8 | **assignment_constraint_gate** | Blocked if violated |
| 9 | **estimand_compatibility_gate** | Blocked or dosage review |
| 10 | **method_suitability_precheck_gate** | Review only; no estimator auth |

---

## 18. Standard go-dark treatment

- Standard go-dark requires a manipulated treatment cell (`GO_DARK`) and a `BUSINESS_AS_USUAL_CONTROL` cell
- A control cell that is also heavy-upped or otherwise manipulated is **not** a standard untreated control
- If control is manipulated, standard go-dark interpretation must be blocked
- Structure may still be represented as `DIFFERENCE_IN_POLICY` if explicitly labeled
- `BUSINESS_AS_USUAL_CONTROL_CONSTRAINT` category applies

---

## 19. Heavy-up treatment

- Heavy-up represented as treatment cell with `HEAVY_UP` policy vs `BUSINESS_AS_USUAL_CONTROL`
- Required heavy-up multiplier and historical support come from spend feasibility diagnostic
- `SPEND_FEASIBILITY_CONSTRAINT` and historical support warnings must be preserved
- Heavy-up structure does not prove powered or estimator-valid

---

## 20. Go-live treatment

- Go-live requires near-zero/no-spend baseline and active planned spend policy
- Structure type `GO_LIVE` with `GO_LIVE_CELL` role
- Must preserve baseline support and spend-readiness flags from spend diagnostics
- Go-live does not automatically imply causal lift can be estimated

---

## 21. Budget reallocation treatment

- Requires `SOURCE_REDUCTION` and `DESTINATION_INCREASE` cells with explicit source/destination policies
- Structure type `BUDGET_REALLOCATION`
- `BUDGET_REALLOCATION_MAPPING_CONSTRAINT` requires explicit source/destination mapping
- Estimand shifts from simple on/off incrementality to policy reallocation impact
- No budget optimization or ROI authorization

---

## 22. Dosage / difference-in-policy treatment

- `DOSAGE_CONTRAST` and `DIFFERENCE_IN_POLICY` are first-class design structures
- Compare low/high or multiple intentionally manipulated policies
- Not standard untreated-control go-dark
- Requires explicit estimand labels and `DESIGN_ASSIGNMENT_REQUIRES_DOSAGE_ESTIMAND_REVIEW`
- Requires future method-suitability review
- Must preserve control contamination flags
- Must not authorize estimator/inference validity

---

## 23. Assignment constraints

Constraint categories (evaluation deferred to future runtime):

`DATA_ELIGIBILITY_CONSTRAINT`, `GEO_FEASIBILITY_CONSTRAINT`, `SPEND_FEASIBILITY_CONSTRAINT`, `POWER_MDE_READINESS_CONSTRAINT`, `CELL_SIZE_CONSTRAINT`, `MUTUAL_EXCLUSIVITY_CONSTRAINT`, `BUSINESS_AS_USUAL_CONTROL_CONSTRAINT`, `DOSAGE_ESTIMAND_CONSTRAINT`, `BUDGET_REALLOCATION_MAPPING_CONSTRAINT`, `MARKET_EXCLUSION_CONSTRAINT`, `GEO_HIERARCHY_CONSTRAINT`, `BALANCE_CONSTRAINT`, `INTERFERENCE_RISK_CONSTRAINT`, `METHOD_SUITABILITY_CONSTRAINT`, `PRODUCTION_AUTHORIZATION_CONSTRAINT`

This contract defines categories only. Future runtime may evaluate them deterministically. This artifact does not solve assignment.

---

## 24. Examples

### Example 1 — Standard go-dark structure

Cell A: `GO_DARK` treatment. Cell B: `BUSINESS_AS_USUAL_CONTROL`. Structure: `SINGLE_TREATMENT_CONTROL`. Assignment readiness may be `DESIGN_ASSIGNMENT_READY_FOR_RUNTIME` if upstream gates pass. **Not claim:** powered, estimator-valid, production-ready.

### Example 2 — Heavy-up structure

Cell A: `HEAVY_UP` with required multiplier from spend diagnostics. Cell B: `BUSINESS_AS_USUAL_CONTROL`. Structure: `SINGLE_TREATMENT_CONTROL`. Historical support warning must be preserved.

### Example 3 — Manipulated control blocks standard go-dark

Cell A: `GO_DARK`. Cell B: `HEAVY_UP`. Business-as-usual control not preserved. Standard go-dark interpretation blocked. May be `DIFFERENCE_IN_POLICY` if explicitly labeled.

### Example 4 — Dosage ladder

Cell A: `LOW_DOSAGE`. Cell B: `MEDIUM_DOSAGE`. Cell C: `HIGH_DOSAGE`. Structure: `DOSAGE_CONTRAST`. Requires dosage estimand and method-suitability review.

### Example 5 — Budget reallocation

Cell A: `SOURCE_REDUCTION`. Cell B: `DESTINATION_INCREASE`. Structure: `BUDGET_REALLOCATION`. Source/destination mapping required. No budget optimization or ROI authorization.

### Example 6 — Missing cell structure

Profiler, geo, spend, and power readiness pass, but candidate cell roles missing. Status: `DESIGN_ASSIGNMENT_PROVISIONAL` or `DESIGN_ASSIGNMENT_BLOCKED_BY_CELL_STRUCTURE`. No assignment runtime can run.

---

## 25. Claim boundaries

**Always false:**

`runtime_design_generation_implemented`, `geo_assignment_computed`, `randomization_computed`, `rerandomization_computed`, `matching_optimization_computed`, `power_computed`, `mde_computed`, `p_value_computed`, `confidence_interval_computed`, `lift_computed`, `roi_computed`, `budget_optimization_authorized`, `candidate_design_authorized`, `treatment_control_assignment_authorized`, `estimator_inference_authorized`, `mmm_runtime_calls_implemented`, `mmm_calibration_authorized`, `production_authorization_granted`, `llm_decisioning_authorized`

**Contract-level positive:** `design_cell_structure_contract_defined`, `assignment_boundary_defined`, `cell_role_semantics_defined`, `manipulation_policy_semantics_defined`, `assignment_constraint_categories_defined`, `dosage_design_structure_defined`, `budget_reallocation_structure_defined`, `claim_boundaries_defined`

---

## 26. Future implementation acceptance criteria

Future `DESIGN_CELL_STRUCTURE_RUNTIME_001` implementation must:

- Consume profiler, geo feasibility, spend feasibility, power/MDE readiness, and candidate cell declaration inputs
- Block if upstream gates are blocked
- Validate cell roles and manipulation-policy compatibility
- Validate business-as-usual control preservation for standard go-dark
- Preserve dosage/difference-in-policy estimand flags
- Preserve budget-reallocation source/destination mapping requirements
- Preserve control contamination flags
- Preserve spend feasibility and historical support flags
- Preserve power/MDE readiness status
- Emit assignment-readiness statuses and constraint reports
- Not assign geo units unless a later runtime assignment artifact explicitly allows it
- Not compute power/MDE, p-values, lift, ROI, estimator validity, or production authorization

---

## 27. Future tests

1. Blocked profiler blocks assignment readiness
2. Blocked geo feasibility blocks assignment readiness
3. Blocked spend feasibility blocks spend-compatible assignment
4. Blocked power/MDE readiness blocks power-ready assignment
5. Missing cell structure blocks/provisional
6. Invalid cell role blocks
7. Standard go-dark requires BAU control
8. Manipulated control blocks standard go-dark interpretation
9. Heavy-up preserves historical support warning
10. Go-live requires near-zero baseline support
11. Budget reallocation requires source/destination mapping
12. Dosage contrast requires dosage estimand
13. Difference-in-policy requires estimand shift
14. Method suitability review required blocks estimator/inference readiness
15. Assignment ready does not assign geo units
16. Assignment ready does not set powered/design/ROI/production flags
17. No fixture-specific branching

---

## 28. Roadmap placement

```
GEO_KPI_SPEND_DATA_PROFILER_001 ✅
→ GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001 ✅
→ SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001 ✅
→ POWER_MDE_DIAGNOSTICS_RUNTIME_001 ✅
→ DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001 ✅ (this artifact)
→ DESIGN_CELL_STRUCTURE_RUNTIME_001 (next)
```

---

## 29. Recommended next artifact

**`DESIGN_CELL_STRUCTURE_RUNTIME_001`**

**Alternative:** `DESIGN_METHOD_SUITABILITY_HANDOFF_CONTRACT_001`

---

## 30. Final verdict

**`design_cell_structure_and_assignment_contract_defined_no_runtime_assignment_or_production_authorization`**

Design-cell structure and assignment contract defined. Cell roles, manipulation policies, design structure types, assignment-readiness statuses, readiness gates, standard go-dark/heavy-up/go-live/budget-reallocation/dosage treatments, and assignment constraint categories documented. No runtime assignment or production authorization granted.
