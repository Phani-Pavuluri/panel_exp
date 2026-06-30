# DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001` |
| **Artifact type** | `design_scenario_policy_feasibility_contract` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_runtime_scenario_planner_or_optimization` |
| **Base commit** | `e121dff` (Amend design cell contract with scenario planner concepts) |
| **Final verdict** | `design_scenario_policy_feasibility_contract_defined_no_runtime_scenario_planner_or_optimization` |

This artifact is a **contract/specification document only**. It defines the typed scenario-policy feasibility layer for evaluating candidate spend-policy plans across cells and contrasts. **No runtime scenario enumeration, scenario optimization, spend recommendation, design generation, geo assignment, randomization, power/MDE computation, inference, lift/ROI, or production authorization was implemented or authorized.**

---

## 2. Source files inspected

| File | Role |
|------|------|
| `docs/track_d/DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001_REPORT.md` | Immediate upstream design-cell/contrast/scenario contract |
| `docs/track_d/archives/DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001_summary.json` | Design-cell contract summary |
| `panel_exp/validation/design_cell_structure_and_assignment_contract_001.py` | Design-cell metadata harness |
| `tests/validation/test_design_cell_structure_and_assignment_contract_001.py` | Design-cell contract tests |
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Power/MDE readiness runtime |
| `POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001` | Spend/power handoff contract |
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Spend manipulation diagnostics |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo feasibility upstream |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Data profiler upstream |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Golden path sequencing |

---

## 3. Why this contract is needed

`DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001` v1.1 defined cells, contrasts, shared-control dependencies, and scenario-planner concepts at the design-cell level. That contract establishes **what** the experiment shape is and **how** contrasts relate to cells.

This artifact isolates the **scenario-policy feasibility layer**: given candidate cells, contrasts, baseline spend, required spend deltas, and proposed cell policies, how should future runtime classify whether a scenario is feasible, partially feasible, out-of-support, estimand-shifted, or requiring redesign/recheck?

Without this contract, future planners may:

- conflate required spend contrast with power or causal lift
- treat achieved spend contrast as sufficient without checking historical support
- manipulate a common control to fix one contrast while silently breaking others
- recommend split-control redesign as immediately feasible
- claim scenario feasibility when upstream profiler, geo, spend, or power/MDE gates are blocked

---

## 4. Core goal statement

`DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001` defines the future typed contract for evaluating candidate scenario-level spend-policy plans across cells and contrasts. It specifies how future deterministic runtime may compare required versus achieved spend contrast, preserve historical support warnings, detect shared-control conflicts, classify estimand shifts, and emit redesign/recheck resolution options without enumerating scenarios, optimizing spend, assigning geo units, computing power/MDE, or authorizing production decisions.

---

## 5. Relationship to design-cell structure contract

| Design-cell contract provides | Scenario-policy feasibility consumes |
|------------------------------|--------------------------------------|
| `DesignCellSpec`, cell roles | Declared cells for policy assignment |
| `DesignContrastSpec`, contrast types | Contrast list for requirement comparison |
| `DesignScenarioSpec`, scenario policy plans | Candidate scenario structure |
| `SharedControlDependency` | Shared-control conflict detection |
| `CrossContrastConflict` semantics | Cross-contrast tradeoff classification |
| Scenario A–E example (structural) | Scenario A–E example (feasibility classification) |

The design-cell contract defines structure; this contract defines **feasibility evaluation** of candidate policies against that structure.

---

## 6. Relationship to spend feasibility diagnostics

Future scenario-policy feasibility runtime must consume `SpendRequirementManipulationFeasibilityReport` for:

- required spend deltas by contrast
- candidate manipulation options
- historical spend support by cell
- business-response risk signals

Spend feasibility diagnostics establish whether manipulation is structurally possible; this contract evaluates whether a **specific candidate scenario plan** achieves required contrasts while respecting support and shared-control constraints.

---

## 7. Relationship to power/MDE runtime

Future scenario-policy feasibility runtime must consume `PowerMdeDiagnosticsReport` for:

- `power_mde_runtime_status`
- `power_mde_runtime_mode`
- `required_kpi_mde_by_contrast`
- response bridge provenance

Required spend contrast is **derived from** power/MDE diagnostics (via response bridge or user override) but is **not** power itself. If power/MDE readiness is blocked, scenario feasibility runtime must not claim power-ready feasibility.

---

## 8. Conceptual distinctions

| # | Concept | Definition | Rule |
|---|---------|------------|------|
| 1 | **Cell structure** | Declared experiment shape from design-cell contract | Examples: one common control + three test cells; split controls; dosage ladder; source/destination reallocation |
| 2 | **Contrast** | Specific comparison to evaluate | Examples: T1 vs C0; high-policy vs low-policy anchor; source-reduction vs destination-increase |
| 3 | **Required spend contrast** | Spend-policy contrast needed for plausible KPI MDE hit | Derived from power/MDE, response bridge, MMM advisory, proxy, or user assumption. **Not power.** |
| 4 | **Achieved spend contrast** | Actual spend difference from candidate scenario plan | Examples: BAU minus go-dark; heavy-up minus BAU. **Not causal lift.** |
| 5 | **Scenario policy plan** | Full candidate spend-policy assignment to all cells | Example: C0=BAU, T1=go-dark, T2=heavy-up $220K, T3=high-spend $160K |
| 6 | **Scenario feasibility** | Whether scenario satisfies structural, spend-contrast, support, and estimand constraints | **Not** production authorization, design approval, assignment feasibility, or estimator validity |
| 7 | **Shared-control conflict** | Conflict when common cell used across contrasts with incompatible policies | Raising C0 helps go-dark but weakens heavy-up; manipulating C0 breaks BAU interpretation |
| 8 | **Resolution option** | Proposed way to handle failing scenario | Some are direct adjustments; split control is always redesign/recheck |

---

## 9. Future contract concepts

| Concept | Purpose |
|---------|---------|
| `DesignScenarioPolicyFeasibilityInput` | Bundled upstream inputs and candidate scenario specs |
| `DesignScenarioPolicyFeasibilityConfig` | Thresholds, blocking vs warning modes, support boundaries |
| `DesignScenarioPolicyFeasibilityReport` | Top-level feasibility report |
| `ScenarioPolicyPlanSpec` | Full cell-policy assignment for one candidate scenario |
| `CellPolicySpec` | Per-cell baseline, proposed spend, policy label |
| `ContrastRequirementSpec` | Required spend delta, KPI MDE, response bridge source |
| `ContrastFeasibilityReport` | Per-contrast feasibility classification |
| `ScenarioFeasibilityReport` | Scenario-level rollup |
| `SharedControlConflictReport` | Shared-control conflict details |
| `HistoricalSupportReport` | Per-cell policy support classification |
| `ScenarioResolutionOption` | Typed resolution with category and recheck flags |
| `ScenarioRecheckRequirement` | Downstream artifact rerun requirement |
| `ScenarioClaimBoundaryReport` | Authorization boundary flags |
| `ScenarioFeasibilityStatus` | Scenario-level status enum |
| `ContrastFeasibilityStatus` | Contrast-level status enum |
| `PolicySupportStatus` | Cell-policy historical support enum |
| `ResolutionOptionType` | Resolution option type enum |
| `SharedControlConflictType` | Shared-control conflict type enum |
| `ScenarioIssue` | Issue record with severity |
| `ScenarioIssueSeverity` | `INFO`, `WARNING`, `BLOCKING` |

---

## 10. Scenario feasibility statuses

| Status | Meaning |
|--------|---------|
| `SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE` | All contrasts feasible under current structure; support warnings may apply |
| `SCENARIO_PARTIALLY_FEASIBLE` | Some contrasts feasible; others insufficient or blocked |
| `SCENARIO_REQUIRES_ESTIMAND_SHIFT` | Achieved contrast may meet spend differential but BAU estimand invalid |
| `SCENARIO_REQUIRES_COMMON_CONTROL_MANIPULATION` | Feasibility requires non-BAU common control |
| `SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT` | Split-control redesign proposed; not immediately feasible |
| `SCENARIO_REQUIRES_POWER_MDE_RECHECK` | Structural/spend change requires power/MDE rerun |
| `SCENARIO_REQUIRES_ASSIGNMENT_RECHECK` | Design change requires assignment feasibility rerun |
| `SCENARIO_REQUIRES_METHOD_SUITABILITY_REVIEW` | Estimand reframing requires method review |
| `SCENARIO_OUT_OF_HISTORICAL_SUPPORT` | One or more cell policies exceed historical support |
| `SCENARIO_BLOCKED` | Upstream gate blocked or unrecoverable conflict |
| `SCENARIO_NOT_EVALUATED` | Prerequisites missing |

---

## 11. Contrast feasibility statuses

| Status | Meaning |
|--------|---------|
| `CONTRAST_FEASIBLE` | Achieved ≥ required; gates pass; estimand compatible |
| `CONTRAST_PARTIALLY_FEASIBLE` | Marginal or conditional feasibility |
| `CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL` | Achieved < required spend contrast |
| `CONTRAST_OUT_OF_HISTORICAL_SUPPORT` | Proposed spend exceeds historical support |
| `CONTRAST_REQUIRES_ESTIMAND_SHIFT` | Spend differential met but BAU interpretation invalid |
| `CONTRAST_BLOCKED_BY_SHARED_CONTROL_CONFLICT` | Shared-control manipulation blocks contrast |
| `CONTRAST_REQUIRES_POWER_MDE_RECHECK` | Policy change invalidates prior power/MDE |
| `CONTRAST_REQUIRES_ASSIGNMENT_RECHECK` | Policy change affects assignment |
| `CONTRAST_REQUIRES_METHOD_SUITABILITY_REVIEW` | Dosage/difference-in-policy reframing needed |
| `CONTRAST_BLOCKED` | Hard block |
| `CONTRAST_NOT_EVALUATED` | Missing requirements or policy plan |

---

## 12. Policy support statuses

| Status | Meaning |
|--------|---------|
| `POLICY_WITHIN_HISTORICAL_SUPPORT` | Proposed spend within historical envelope |
| `POLICY_NEAR_HISTORICAL_SUPPORT_BOUNDARY` | Within tolerance of p90/p95/max |
| `POLICY_OUT_OF_HISTORICAL_SUPPORT` | Exceeds historical max (or configured threshold) |
| `POLICY_BELOW_HISTORICAL_SUPPORT` | Below observed historical minimum |
| `POLICY_REQUIRES_BUSINESS_OVERRIDE` | Out-of-support but override path documented |
| `POLICY_SUPPORT_UNKNOWN` | Profiler/support data missing |
| `POLICY_NOT_EVALUATED` | Not yet evaluated |

---

## 13. Shared-control conflict types

| Type | Meaning |
|------|---------|
| `NO_SHARED_CONTROL_CONFLICT` | Common control compatible across contrasts |
| `COMMON_CONTROL_MANIPULATED` | Common control spend differs from BAU baseline |
| `BAU_CONTROL_NOT_PRESERVED` | BAU-dependent contrasts cannot use standard interpretation |
| `COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER` | Cross-contrast tradeoff from C0 manipulation |
| `COMMON_CONTROL_INSUFFICIENT_FOR_ONE_OR_MORE_CONTRASTS` | C0 level cannot satisfy all contrast requirements |
| `COMMON_CONTROL_OUT_OF_HISTORICAL_SUPPORT` | Manipulated C0 exceeds historical max |
| `COMMON_CONTROL_SPLIT_REQUIRED_FOR_CLEAN_ESTIMANDS` | Split redesign needed for clean BAU per contrast |
| `COMMON_CONTROL_ROLE_AMBIGUOUS` | Cell role unclear across contrasts |

---

## 14. Resolution option types

| Type | Category |
|------|----------|
| `EXTEND_DURATION` | Direct scenario adjustment (power/MDE recheck) |
| `RELAX_MDE_TARGET` | Direct scenario adjustment (stakeholder acceptance) |
| `CHANGE_TEST_POLICY_TO_HEAVY_UP` | Direct scenario adjustment |
| `CHANGE_TEST_POLICY_TO_GO_DARK` | Direct scenario adjustment |
| `REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY` | Estimand reframing (method-suitability review) |
| `CAP_SPEND_WITHIN_HISTORICAL_SUPPORT` | Direct scenario adjustment |
| `SPLIT_COMMON_CONTROL` | Redesign/recheck proposal |
| `ADD_OR_REALLOCATE_CELLS` | Redesign/recheck proposal |
| `DROP_CONTRAST` | Direct scenario adjustment |
| `SEQUENCE_TESTS` | Direct scenario adjustment |
| `RERUN_POWER_MDE` | Redesign/recheck proposal |
| `RERUN_ASSIGNMENT_FEASIBILITY` | Redesign/recheck proposal |
| `REQUIRE_METHOD_SUITABILITY_REVIEW` | Estimand reframing |
| `BUSINESS_OVERRIDE_REQUIRED` | Business override |
| `BLOCK_SCENARIO` | Blocking recommendation |

---

## 15. Future input dependencies

Future `DesignScenarioPolicyFeasibilityInput` may consume:

- `profiler_report`
- `geo_unit_market_feasibility_report`
- `spend_requirement_manipulation_feasibility_report`
- `power_mde_diagnostics_report`
- `design_cell_structure_report`
- `candidate_scenario_specs`
- `candidate_contrast_specs`
- `cell_policy_plan`
- `baseline_spend_by_cell`
- `proposed_spend_by_cell`
- `historical_spend_support_by_cell`
- `historical_p90_by_cell`
- `historical_p95_by_cell`
- `historical_max_by_cell`
- `required_spend_delta_by_contrast`
- `required_kpi_mde_by_contrast`
- `response_bridge_source_by_contrast`
- `business_response_risk_by_contrast`
- `candidate_manipulation_options`
- `shared_control_dependencies`
- `business_as_usual_control_required_by_contrast`
- `business_as_usual_control_preserved_by_scenario`
- `dosage_contrast_estimand_required`
- `difference_in_policy_required`
- `control_contamination_flags`
- `method_suitability_review_required`
- `power_mde_runtime_status`
- `power_mde_runtime_mode`

---

## 16. Future output concepts

| Output | Purpose |
|--------|---------|
| `DesignScenarioPolicyFeasibilityReport` | Top-level report |
| `ScenarioReadinessReport` | Upstream gate readiness summary |
| `ScenarioPolicyPlanReport` | Cell-policy plan details |
| `ContrastRequirementReport` | Required spend/KPI MDE by contrast |
| `ContrastFeasibilityReport` | Per-contrast feasibility |
| `RequiredVsAchievedSpendContrastReport` | Side-by-side contrast comparison |
| `HistoricalSupportReport` | Per-cell support classification |
| `SharedControlConflictReport` | Shared-control conflicts |
| `EstimandShiftReport` | BAU/dosage/difference-in-policy flags |
| `ScenarioResolutionReport` | Resolution options |
| `ScenarioRecheckRequirementReport` | Downstream recheck requirements |
| `ScenarioClaimBoundaryReport` | Authorization boundaries |

---

## 17. Future report fields

Future `DesignScenarioPolicyFeasibilityReport` must include:

- `artifact_id`
- `scenario_id`
- `scenario_status`
- `overall_feasibility_summary`
- `cell_policy_plan`
- `contrast_feasibility_reports`
- `required_vs_achieved_spend_contrast_by_contrast`
- `historical_support_by_cell`
- `shared_control_conflicts`
- `estimand_shift_flags`
- `resolution_options`
- `recheck_requirements`
- `claim_boundary_report`
- `issues`
- `warnings`
- `blocking_reasons`

---

## 18. Readiness gates

Future scenario-policy feasibility runtime must evaluate gates in order:

| # | Gate | Block rule |
|---|------|------------|
| 1 | profiler gate | Blocked profiler → no feasibility claim |
| 2 | geo unit/market feasibility gate | Blocked geo → no feasibility claim |
| 3 | spend feasibility gate | Blocked spend → no spend-compatible feasibility |
| 4 | power/MDE readiness gate | Blocked power/MDE → no power-ready feasibility |
| 5 | design cell structure gate | Missing/blocked structure → no scenario feasibility |
| 6 | contrast requirement gate | Missing requirements → no required-vs-achieved comparison |
| 7 | scenario policy-plan gate | Missing plan → no scenario feasibility |
| 8 | required-vs-achieved contrast gate | Achieved < required → insufficient differential |
| 9 | historical support gate | Out-of-support → warning or block per config |
| 10 | shared-control dependency gate | Manipulated C0 → reclassify BAU contrasts |
| 11 | estimand compatibility gate | Cross-contrast conflict → emit conflict |
| 12 | resolution/recheck gate | Split control → redesign/recheck, not immediate feasibility |
| 13 | method-suitability precheck gate | Review required → estimator readiness blocked |

---

## 19. Future runtime algorithm (contract level only)

For each candidate scenario:

1. Validate upstream readiness gates
2. Validate declared cells and contrasts
3. Read baseline spend by cell
4. Read proposed spend policy by cell
5. Read required spend contrast by contrast
6. Compute achieved spend contrast by contrast
7. Compare achieved against required contrast
8. Classify each contrast as feasible, insufficient, out-of-support, estimand-shifted, or blocked
9. Check historical support for every proposed cell policy
10. Identify shared/common-control dependencies
11. Detect shared-control conflicts
12. Classify scenario-level status
13. Emit resolution options
14. Emit downstream recheck requirements
15. Preserve claim boundaries

**This artifact does not implement this algorithm.**

---

## 20. Four-cell common-control example

### Setup

| Cell | Role | Baseline weekly spend | Historical max |
|------|------|----------------------|----------------|
| C0 | Common BAU control | $100K | $130K |
| T1 | Test 1 | $80K | $120K |
| T2 | Test 2 | $120K | $250K |
| T3 | Test 3 | $100K | $180K |

**Required spend contrasts** (from power/MDE + response bridge):

| Contrast | Required |
|----------|----------|
| T1 vs C0 | $150K |
| T2 vs C0 | $100K |
| T3 vs C0 | $60K |

Achieved spend contrast formula: `|proposed_test − proposed_control|` (sign convention per contrast type).

---

### Scenario A — preserve common BAU control

| Cell | Proposed |
|------|----------|
| C0 | $100K BAU |
| T1 | $0 go-dark |
| T2 | $220K heavy-up |
| T3 | $160K heavy-up |

| Contrast | Achieved | Required | Status |
|----------|----------|----------|--------|
| T1 vs C0 | $100K | $150K | `CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL` |
| T2 vs C0 | $120K | $100K | `CONTRAST_FEASIBLE` |
| T3 vs C0 | $60K | $60K | `CONTRAST_FEASIBLE` |

- BAU control preserved = **true**
- Scenario status = `SCENARIO_PARTIALLY_FEASIBLE`
- Resolution options: `EXTEND_DURATION`, `RELAX_MDE_TARGET`, `REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY`, `SPLIT_COMMON_CONTROL`, `DROP_CONTRAST`, `SEQUENCE_TESTS`

---

### Scenario B — raise common control to help go-dark

| Cell | Proposed |
|------|----------|
| C0 | $150K manipulated upward |
| T1 | $0 go-dark |
| T2 | $220K heavy-up |
| T3 | $160K heavy-up |

| Contrast | Achieved | Required | Status |
|----------|----------|----------|--------|
| T1 vs C0 | $150K | $150K | Operational contrast feasible but **estimand-shifted** |
| T2 vs C0 | $70K | $100K | `CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL` |
| T3 vs C0 | $10K | $60K | `CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL` |

- BAU control preserved = **false**
- C0 exceeds historical max $130K → `POLICY_OUT_OF_HISTORICAL_SUPPORT`
- Shared-control conflict = `COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER`
- Standard go-dark/heavy-up vs BAU interpretation **blocked**
- Scenario status = `SCENARIO_REQUIRES_ESTIMAND_SHIFT` and `SCENARIO_OUT_OF_HISTORICAL_SUPPORT`
- Resolution options: `REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY`, `CAP_SPEND_WITHIN_HISTORICAL_SUPPORT`, `SPLIT_COMMON_CONTROL`, `RERUN_POWER_MDE`, `RERUN_ASSIGNMENT_FEASIBILITY`

---

### Scenario C — lower common control to help heavy-up cells

| Cell | Proposed |
|------|----------|
| C0 | $60K manipulated downward |
| T1 | $0 go-dark |
| T2 | $160K heavy-up |
| T3 | $120K heavy-up |

| Contrast | Achieved | Required | Status |
|----------|----------|----------|--------|
| T1 vs C0 | $60K | $150K | `CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL` |
| T2 vs C0 | $100K | $100K | `CONTRAST_FEASIBLE` |
| T3 vs C0 | $60K | $60K | `CONTRAST_FEASIBLE` |

- BAU control preserved = **false**
- Shared-control conflict = `COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER`
- Standard heavy-up vs BAU interpretation **blocked**
- Scenario status = `SCENARIO_REQUIRES_ESTIMAND_SHIFT` and `SCENARIO_PARTIALLY_FEASIBLE`
- Resolution options: `REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY`, preserve BAU and accept T1 failure, `SPLIT_COMMON_CONTROL`, `RERUN_POWER_MDE`

---

### Scenario D — preserve BAU and convert T1 to high-spend/dosage

| Cell | Proposed |
|------|----------|
| C0 | $100K BAU |
| T1 | $250K high-spend policy |
| T2 | $220K heavy-up |
| T3 | $160K heavy-up |

| Contrast | Achieved | Required | Status |
|----------|----------|----------|--------|
| T1 vs C0 | $150K | $150K | Feasible by contrast |
| T2 vs C0 | $120K | $100K | `CONTRAST_FEASIBLE` |
| T3 vs C0 | $60K | $60K | `CONTRAST_FEASIBLE` |

- BAU control preserved = **true**
- T1 exceeds historical max $120K → `POLICY_OUT_OF_HISTORICAL_SUPPORT`
- Scenario status = `SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE` with out-of-support warning
- Resolution options: `CAP_SPEND_WITHIN_HISTORICAL_SUPPORT`, `EXTEND_DURATION`, `RELAX_MDE_TARGET`, `BUSINESS_OVERRIDE_REQUIRED`, `REQUIRE_METHOD_SUITABILITY_REVIEW`

---

### Scenario E — split common control

**Original:** C0 common BAU control used by T1, T2, T3.

**Redesign proposal:**

| Cell | Role |
|------|------|
| C1 | BAU control for T1 |
| C2 | BAU control for T2 |
| C3 | BAU/low-policy anchor for T3 |

**Classification:**

- This is **not** a direct feasible recommendation; it is a **redesign proposal**
- Changes design structure, cell count, control allocation, assignment equation, match quality, and power/MDE
- Scenario status = `SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT`, `SCENARIO_REQUIRES_POWER_MDE_RECHECK`, `SCENARIO_REQUIRES_ASSIGNMENT_RECHECK`
- Resolution status = requires redesign/recheck before feasibility can be claimed

**User-facing interpretation:** Splitting the common control may preserve cleaner BAU interpretations for multiple tests, but it reduces markets per comparison and changes the design. The planner may propose it, but must send it back through assignment feasibility and power/MDE before treating it as feasible.

---

## 21. Historical support treatment

- Historical support must be evaluated at the **cell-policy level**
- Proposed spend above historical p90/p95/max must be flagged
- Out-of-support does **not** automatically mean impossible, but increases business-response risk
- MMM/proxy/back-of-napkin response bridges must preserve advisory/out-of-support flags
- Future runtime must **not** silently recommend spend levels beyond historical support

---

## 22. Required vs achieved spend contrast treatment

- Required spend contrast is derived from KPI MDE and response bridge or supplied directly
- Achieved spend contrast is computed from scenario policy levels
- If achieved < required → contrast is insufficient (`CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL`)
- If achieved ≥ required but requires non-BAU control manipulation → estimand shift must be flagged
- If achieved ≥ required but spend is out of historical support → historical-support warning must be emitted
- Spend contrast feasibility is **not** causal lift or ROI

---

## 23. Shared/common-control treatment

- A common control may be shared across contrasts only when its policy is compatible with every contrast that uses it
- If common control remains BAU, it may support standard go-dark/heavy-up vs BAU contrasts
- If common control is manipulated, all BAU-dependent contrasts must be reclassified or blocked
- Raising common control can help go-dark but hurt heavy-up
- Lowering common control can help heavy-up but hurt go-dark
- Future runtime must emit cross-contrast conflicts rather than silently averaging or hiding tradeoffs

---

## 24. Split-control redesign treatment

- Split control is a **redesign proposal**, not an immediate feasible scenario
- It changes cell count, control allocation, assignment equations, match quality, and power/MDE
- It must emit power/MDE recheck and assignment recheck requirements
- It may preserve cleaner BAU estimands but can reduce sample size per contrast
- It must **not** be marked feasible until downstream rechecks pass

---

## 25. Resolution option treatment

Resolution options are classified as:

| Category | Examples |
|----------|----------|
| **Direct scenario adjustment** | extend duration, relax MDE, cap spend, drop contrast, sequence tests |
| **Estimand reframing** | reframe as dosage/difference-in-policy |
| **Redesign/recheck proposal** | split common control, add cells, rerun power/MDE, rerun assignment |
| **Business override** | exceed historical support with documented override |
| **Blocking recommendation** | block scenario |

Rules:

- `EXTEND_DURATION` = direct adjustment requiring power/MDE recheck
- `RELAX_MDE_TARGET` = direct adjustment requiring stakeholder acceptance
- `REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY` = estimand reframing requiring method-suitability review
- `SPLIT_COMMON_CONTROL` = redesign/recheck proposal (never immediate feasibility)
- Exceed historical support = business override / advisory risk
- `BLOCK_SCENARIO` = blocking recommendation

---

## 26. Claim boundaries

### Always false in this contract

| Flag | Value |
|------|-------|
| `runtime_scenario_feasibility_implemented` | false |
| `runtime_scenario_enumeration_implemented` | false |
| `runtime_scenario_optimization_implemented` | false |
| `runtime_design_generation_implemented` | false |
| `geo_assignment_computed` | false |
| `randomization_computed` | false |
| `rerandomization_computed` | false |
| `matching_optimization_computed` | false |
| `power_computed` | false |
| `mde_computed` | false |
| `p_value_computed` | false |
| `confidence_interval_computed` | false |
| `lift_computed` | false |
| `roi_computed` | false |
| `budget_optimization_authorized` | false |
| `candidate_design_authorized` | false |
| `treatment_control_assignment_authorized` | false |
| `estimator_inference_authorized` | false |
| `mmm_runtime_calls_implemented` | false |
| `mmm_calibration_authorized` | false |
| `production_authorization_granted` | false |
| `llm_decisioning_authorized` | false |

### Allowed contract-level positives

| Flag | Value |
|------|-------|
| `scenario_policy_feasibility_contract_defined` | true |
| `required_vs_achieved_spend_contrast_defined` | true |
| `historical_support_contract_defined` | true |
| `shared_control_conflict_contract_defined` | true |
| `split_control_redesign_recheck_defined` | true |
| `scenario_resolution_options_defined` | true |
| `claim_boundaries_defined` | true |

---

## 27. Future implementation acceptance criteria

Future `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` must:

1. Consume profiler, geo feasibility, spend feasibility, power/MDE readiness, design-cell structure, candidate scenario specs, contrast specs, required spend deltas, baseline spend, proposed spend, and historical support
2. Block if upstream gates are blocked
3. Validate scenario policy plans
4. Validate contrast requirements
5. Compute achieved spend contrast by contrast
6. Compare achieved vs required spend contrast
7. Flag insufficient spend differential
8. Evaluate historical support at cell-policy level
9. Preserve response bridge provenance and business-response risk
10. Detect shared-control conflicts
11. Classify BAU-control preservation
12. Classify estimand shifts
13. Emit scenario feasibility statuses
14. Emit contrast feasibility statuses
15. Emit resolution options
16. Emit recheck requirements for split-control/redesign proposals
17. **Not** assign geo units, optimize spend, compute power/MDE, p-values, lift, ROI, estimator validity, or production authorization

---

## 28. Future tests

Future runtime tests should cover:

- blocked profiler prevents scenario feasibility claim
- blocked geo feasibility prevents scenario feasibility claim
- blocked spend feasibility prevents spend-compatible feasibility
- blocked power/MDE readiness prevents power-ready feasibility
- missing design cell structure blocks scenario feasibility
- missing contrast requirements blocks required-vs-achieved comparison
- missing scenario policy plan blocks scenario feasibility
- achieved spend below required marks contrast insufficient
- achieved spend equal to required marks contrast feasible when other gates pass
- out-of-support proposed spend emits historical support warning/status
- common control BAU preserved allows standard go-dark/heavy-up interpretation
- common control manipulated blocks/reclassifies BAU-dependent contrasts
- raising common control helps go-dark but weakens heavy-up
- lowering common control helps heavy-up but weakens go-dark
- split common control emits redesign/recheck requirement
- scenario feasible does not assign markets
- scenario feasible does not compute power/MDE
- scenario feasible does not authorize estimator/inference or production
- no fixture-specific branching

---

## 29. Roadmap placement

```
GEO_KPI_SPEND_DATA_PROFILER_001
  → GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001
  → SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001
  → POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001
  → POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001
  → POWER_MDE_DIAGNOSTICS_RUNTIME_001
  → DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001 ✅
  → DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001 ✅ (this artifact)
  → DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001 (recommended next)
```

---

## 30. Recommended next artifact

**Primary:** `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` — conservative deterministic runtime implementing the contract algorithm without scenario enumeration or optimization.

**Alternative:** `DESIGN_SCENARIO_POLICY_FEASIBILITY_METADATA_001` — intermediate metadata harness if roadmap prefers an additional validation step before runtime.

**Do not implement either in this artifact.**

---

## Appendix: Metadata harness

| File | Role |
|------|------|
| `panel_exp/validation/design_scenario_policy_feasibility_contract_001.py` | Metadata-only contract harness |
| `tests/validation/test_design_scenario_policy_feasibility_contract_001.py` | Contract validation tests |
| `docs/track_d/archives/DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001_summary.json` | Machine-readable summary |
