# METHOD_SUITABILITY_HANDOFF_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_SUITABILITY_HANDOFF_CONTRACT_001` |
| **Artifact type** | `method_suitability_handoff_contract` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_method_selection_or_inference_authorization` |
| **Base commit** | `9e680f9` (Implement design assignment feasibility runtime) |
| **Final verdict** | `method_suitability_handoff_contract_defined_no_method_selection_or_inference_authorization` |

METHOD_SUITABILITY_HANDOFF_CONTRACT_001 defines the future typed handoff from design-cell structure, scenario-policy feasibility, assignment feasibility, spend, and power/MDE diagnostics into method-suitability evaluation. It preserves design shape, contrast semantics, estimand requirements, BAU-control preservation, assignment readiness, scenario conflicts, and governance flags so a future deterministic method-suitability runtime can evaluate method-family eligibility without this artifact selecting estimators, computing inference, estimating lift, or authorizing production readout.

---

## 2. Source files inspected

| File | Role |
|------|------|
| `DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001` | Immediate upstream handoff source |
| `DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001` | Assignment feasibility contract boundary |
| `DESIGN_CELL_STRUCTURE_RUNTIME_001` | Design structure and estimand detection |
| `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` | Scenario policy and shared-control conflicts |
| `POWER_MDE_DIAGNOSTICS_RUNTIME_001` | Power/MDE readiness handoff |
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Spend contrast and manipulation semantics |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo feasibility upstream |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Profiler upstream |
| `METHOD_SOUNDNESS_AND_GAP_ROADMAP_001` | Method governance stance |

---

## 3. Why this contract is needed

The stack can now validate data readiness, geo feasibility, spend manipulation feasibility, power/MDE readiness, design cell structure, scenario policy feasibility, and assignment feasibility. The next question is:

**Given validated design, scenario, and assignment diagnostics, what typed packet must a future method-suitability runtime receive before it can evaluate method-family eligibility?**

This contract defines that handoff. It does not select methods, compute inference, or authorize production.

---

## 4. Relationship to profiler

Consumes `profiler_report` and `profiler_data_readiness_gate`. If profiler/data readiness is blocked, method handoff must be blocked.

---

## 5. Relationship to geo feasibility

Consumes `geo_unit_market_feasibility_report`. If geo feasibility is blocked, method handoff must be blocked.

---

## 6. Relationship to spend feasibility diagnostics

Consumes `spend_requirement_manipulation_feasibility_report` and `required_vs_achieved_spend_contrast_status`. If spend feasibility is blocked, handoff preserves spend risk and may block or mark provisional depending severity.

---

## 7. Relationship to power/MDE runtime

Consumes `power_mde_diagnostics_report` and preserves `power_mde_status`. If power/MDE readiness is blocked, method handoff must not claim method-ready inference.

---

## 8. Relationship to design cell structure runtime

Consumes `design_cell_structure_runtime_report`, `design_structure_type`, `contrast_types`, `estimand_labels`, and `manipulation_policies`. If design structure is blocked, method handoff must be blocked.

---

## 9. Relationship to scenario policy feasibility runtime

Consumes `design_scenario_policy_feasibility_report`, `bau_control_preservation_status`, `shared_control_conflicts`, and `historical_support_status`. If scenario policy is blocked, handoff is blocked or provisional depending severity. Does not recompute scenario feasibility.

---

## 10. Relationship to assignment feasibility runtime

Consumes `design_assignment_feasibility_report`, `assignment_feasibility_status`, `eligible_unit_count`, `cell_capacity_status`, `balance_readiness_status`, and `interference_risk_status`. If assignment feasibility is blocked, handoff is blocked or provisional depending severity. Does not recompute assignment feasibility.

---

## 11. Conceptual distinctions

### 11.1 Method-suitability handoff

The typed packet of facts passed into future method review. It is not method selection.

### 11.2 Method-suitability evaluation

Future runtime only. May later evaluate whether method families are eligible, restricted, diagnostic-only, or blocked.

### 11.3 Estimator/inference selection

Future governed runtime only. Not implemented here.

### 11.4 Method promotion / production compatibility

Future governance layer only. Not implemented here.

### 11.5 Causal readout

Future readout layer only. Not implemented here.

---

## 12. Future contract concepts

`MethodSuitabilityHandoffInput`, `MethodSuitabilityHandoffConfig`, `MethodSuitabilityHandoffReport`, `MethodSuitabilityHandoffPacket`, `MethodSuitabilityDesignSummary`, `MethodSuitabilityContrastSummary`, `MethodSuitabilityAssignmentSummary`, `MethodSuitabilityScenarioSummary`, `MethodSuitabilityPowerMdeSummary`, `MethodSuitabilitySpendSummary`, `MethodSuitabilityGovernanceSummary`, `MethodFamilyEligibilityInput`, `MethodFamilyRestriction`, `MethodFamilyWarning`, `MethodSuitabilityHandoffStatus`, `MethodSuitabilityReviewRequirement`, `MethodSuitabilityIssue`, `MethodSuitabilityIssueSeverity`, `MethodSuitabilityClaimBoundaryReport`.

---

## 13. Handoff statuses

| Status | Meaning |
|--------|---------|
| `METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW` | Future suitability runtime has enough typed inputs to review method families |
| `METHOD_HANDOFF_READY_WITH_WARNINGS` | Handoff complete with non-blocking warnings |
| `METHOD_HANDOFF_PROVISIONAL` | Incomplete constraint clarity or user input needed |
| `METHOD_HANDOFF_BLOCKED_BY_DATA_READINESS` | Profiler/data gate blocked |
| `METHOD_HANDOFF_BLOCKED_BY_GEO_FEASIBILITY` | Geo gate blocked |
| `METHOD_HANDOFF_BLOCKED_BY_DESIGN_STRUCTURE` | Design structure gate blocked |
| `METHOD_HANDOFF_BLOCKED_BY_SCENARIO_POLICY` | Scenario policy gate blocked |
| `METHOD_HANDOFF_BLOCKED_BY_ASSIGNMENT_FEASIBILITY` | Assignment feasibility gate blocked |
| `METHOD_HANDOFF_BLOCKED_BY_POWER_MDE_READINESS` | Power/MDE gate blocked |
| `METHOD_HANDOFF_BLOCKED_BY_MISSING_ESTIMAND` | Estimand label missing |
| `METHOD_HANDOFF_BLOCKED_BY_UNSUPPORTED_DESIGN` | Design type unsupported for handoff |
| `METHOD_HANDOFF_REQUIRES_DOSAGE_REVIEW` | Dosage contrast review required |
| `METHOD_HANDOFF_REQUIRES_DIFFERENCE_IN_POLICY_REVIEW` | Difference-in-policy review required |
| `METHOD_HANDOFF_REQUIRES_BUDGET_REALLOCATION_REVIEW` | Budget reallocation review required |
| `METHOD_HANDOFF_REQUIRES_REDESIGN_RECHECK` | Split-control or redesign recheck required |
| `METHOD_HANDOFF_NOT_EVALUATED` | Not yet evaluated |

`METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW` does not mean any method is approved, estimator-valid, inference-valid, or production-ready.

---

## 14. Review requirement types

`STANDARD_INCREMENTALITY_REVIEW`, `DOSAGE_CONTRAST_REVIEW`, `DIFFERENCE_IN_POLICY_REVIEW`, `BUDGET_REALLOCATION_REVIEW`, `GO_LIVE_REVIEW`, `COMMON_CONTROL_REVIEW`, `SPLIT_CONTROL_REDESIGN_REVIEW`, `MATCHED_PAIR_REVIEW`, `BLOCKED_OR_CLUSTERED_DESIGN_REVIEW`, `RERANDOMIZATION_REVIEW`, `INTERFERENCE_RISK_REVIEW`, `LOW_POWER_OR_HIGH_MDE_REVIEW`, `OUT_OF_HISTORICAL_SUPPORT_REVIEW`, `ASSIGNMENT_FEASIBILITY_REVIEW`, `METHOD_GOVERNANCE_REVIEW`.

---

## 15. Method-family categories as review targets

`SCM_FAMILY`, `AUGSYNTH_FAMILY`, `TBR_RIDGE_FAMILY`, `DID_FAMILY`, `MATCHED_PAIR_FAMILY`, `BLOCKED_RANDOMIZATION_FAMILY`, `RERANDOMIZATION_FAMILY`, `PLACEBO_INFERENCE_FAMILY`, `JACKKNIFE_INFERENCE_FAMILY`, `BOOTSTRAP_INFERENCE_FAMILY`, `CONFORMAL_INFERENCE_FAMILY`, `AB_TEST_FAMILY`, `UNKNOWN_METHOD_FAMILY`.

Listing a method family in this handoff does not make it eligible or recommended. Future method-suitability runtime must evaluate eligibility/restriction/blocking under governed rules.

---

## 16. Future input dependencies

`profiler_report`, `geo_unit_market_feasibility_report`, `spend_requirement_manipulation_feasibility_report`, `power_mde_diagnostics_report`, `design_cell_structure_runtime_report`, `design_scenario_policy_feasibility_report`, `design_assignment_feasibility_report`, `design_structure_type`, `contrast_specs`, `contrast_types`, `estimand_labels`, `manipulation_policies`, `bau_control_preservation_status`, `shared_control_conflicts`, `split_control_required`, `scenario_recheck_requirements`, `assignment_feasibility_status`, `eligible_unit_count`, `cell_capacity_status`, `balance_readiness_status`, `interference_risk_status`, `required_vs_achieved_spend_contrast_status`, `historical_support_status`, `method_suitability_review_required_flags`, `instrument_catalog_status`, `method_roadmap_status`.

---

## 17. Future output concepts

`MethodSuitabilityHandoffReport`, `MethodSuitabilityHandoffPacket`, `MethodSuitabilityDesignSummary`, `MethodSuitabilityContrastSummary`, `MethodSuitabilityAssignmentSummary`, `MethodSuitabilityScenarioSummary`, `MethodSuitabilityPowerMdeSummary`, `MethodSuitabilitySpendSummary`, `MethodSuitabilityGovernanceSummary`, `MethodSuitabilityReviewRequirementReport`, `MethodSuitabilityBlockingReasonReport`, `MethodSuitabilityClaimBoundaryReport`.

---

## 18. Future handoff packet fields

`artifact_id`, `design_id`, `handoff_status`, `design_structure_type`, `contrast_summaries`, `estimand_summaries`, `scenario_policy_summary`, `assignment_feasibility_summary`, `power_mde_summary`, `spend_summary`, `governance_summary`, `review_requirements`, `candidate_method_family_review_targets`, `warnings`, `blocking_reasons`, `claim_boundary_report`.

---

## 19. Readiness gates

1. profiler/data readiness gate
2. geo unit/market feasibility gate
3. spend feasibility gate
4. power/MDE readiness gate
5. design cell structure gate
6. scenario policy feasibility gate
7. assignment feasibility gate
8. estimand declaration gate
9. design/contrast compatibility gate
10. method governance/catalog availability gate
11. method-suitability handoff packet gate

**Rules:** blocked profiler → blocked handoff; blocked geo → blocked; blocked spend → preserve risk, block/provisional; blocked power/MDE → no method-ready inference claim; blocked design structure → blocked; blocked scenario → blocked/provisional; blocked assignment → blocked/provisional; missing estimand → blocked; dosage/difference-in-policy → review requirement, no standard incrementality label; split-control redesign → redesign recheck; out-of-support → historical support review; high/unknown interference → interference review.

---

## 20. Design type treatment

- **Single treatment/control:** may be eligible for standard incrementality review if BAU preserved and upstream gates pass.
- **Multi-cell common-control:** must preserve common-control dependency status and shared-control conflicts.
- **Split-control:** must preserve redesign/recheck status.
- **Dosage/difference-in-policy:** requires explicit estimand labels and method-suitability review.
- **Budget reallocation:** requires source/destination semantics and explicit estimand.
- **Matched-pair/block/rerandomized:** requires assignment and balance metadata before method review is meaningful.

---

## 21. Estimand treatment

Future method-suitability review requires explicit estimand labels. Standard go-dark vs BAU differs from dosage low-vs-high and difference-in-policy. Manipulated control blocks standard BAU-control interpretation. Budget reallocation must not be treated as simple on/off incrementality unless explicitly governed. Missing estimand labels should block or make handoff provisional.

---

## 22. Method-family review target treatment

This contract may list candidate method-family review targets but must not select or recommend methods.

- Standard two-cell BAU contrast may later be reviewed against DID/TBR/SCM-family rules.
- Single-treated or limited donor settings may later be reviewed against SCM/AugSynth restrictions.
- Dosage/difference-in-policy may require specialized method review.
- Matched-pair/block structures may later be reviewed against corresponding inference families.

The future method-suitability runtime must decide eligibility/restriction/blocking.

---

## 23. Governed/restricted/diagnostic-only method treatment

The handoff must preserve current governance stance from method roadmaps/catalogs. Method families may later be governed, restricted, diagnostic-only, characterized, or blocked. This handoff does not promote any method. This handoff does not convert diagnostic-only methods into production methods.

---

## 24. Examples

### Example 1 — standard two-cell go-dark handoff

Design: one go-dark treatment, one BAU control. BAU preserved. Assignment feasibility ready. Handoff status: ready for future suitability review. No method selected.

### Example 2 — heavy-up vs BAU handoff

Design: heavy-up treatment vs BAU control. Historical support warning preserved. Handoff requires out-of-historical-support review if proposed spend exceeds support. No method selected.

### Example 3 — dosage contrast handoff

Design: low-spend vs high-spend policy. Estimand: dosage contrast. Handoff requires dosage contrast review and method-suitability review. Standard incrementality interpretation blocked.

### Example 4 — difference-in-policy handoff

Design: manipulated control or low/high policy comparison. Handoff requires difference-in-policy review. BAU-control interpretation blocked.

### Example 5 — budget reallocation handoff

Design: source reduction vs destination increase. Handoff requires budget reallocation review. No ROI or optimization authorization.

### Example 6 — shared common-control conflict

Scenario feasibility reports shared-control conflict. Handoff preserves the conflict and prevents clean method-ready status until resolved or reclassified.

### Example 7 — split-control redesign

Assignment feasibility reports split-control redesign/recheck. Handoff requires redesign recheck and does not proceed as method-ready.

### Example 8 — assignment feasible but method review required

Assignment feasibility is ready. Design is dosage/difference-in-policy. Handoff can be structurally ready but must require method-suitability review. No estimator/inference approved.

---

## 25. Claim boundaries

Always false: `runtime_method_suitability_implemented`, `method_family_selected`, `estimator_selected`, `inference_method_selected`, `method_promotion_authorized`, `method_production_compatibility_authorized`, `geo_assignment_computed`, `matched_pairs_generated`, `blocks_generated`, `randomization_computed`, `rerandomization_computed`, `thinning_design_generated`, `matching_optimization_computed`, `balance_optimization_computed`, `scenario_policy_feasibility_computed`, `assignment_feasibility_computed`, `power_computed`, `mde_computed`, `p_value_computed`, `confidence_interval_computed`, `lift_computed`, `roi_computed`, `budget_optimization_authorized`, `candidate_design_authorized`, `treatment_control_assignment_authorized`, `estimator_inference_authorized`, `mmm_runtime_calls_implemented`, `mmm_calibration_authorized`, `production_authorization_granted`, `llm_decisioning_authorized`.

Allowed contract positives: `method_suitability_handoff_contract_defined`, `method_handoff_packet_defined`, `estimand_handoff_defined`, design/scenario/assignment/power/spend/governance summary handoff flags, `review_requirement_types_defined`, `method_family_review_targets_defined`, `claim_boundaries_defined`.

---

## 26. Future implementation acceptance criteria

Future runtime must: consume all upstream reports; block or mark provisional when upstream hard gates blocked; require explicit estimand labels; preserve BAU-control, shared-control conflict, split-control redesign, assignment feasibility, power/MDE, historical support, interference-risk, and method-review flags; emit typed review requirements; emit method-family review targets only as candidates; not select estimators; not select inference methods; not promote methods; not compute lift/ROI/p-values/CIs; not authorize production.

---

## 27. Future tests

Future runtime tests should cover: blocked profiler/geo/design structure; blocked assignment/scenario provisional; blocked power/MDE prevents method-ready inference; missing estimand blocks; standard go-dark emits standard incrementality review; manipulated control emits difference-in-policy review; dosage/budget reviews; shared-control conflict preserved; split-control recheck preserved; out-of-historical-support and interference preserved; assignment-ready ≠ method-ready; method-family targets not selected; no estimator/inference authorization; no lift/ROI/p-value/CI; no production authorization; no fixture-specific branching.

---

## 28. Roadmap placement

Completes the handoff lane opened by `DESIGN-ASSIGNMENT-FEASIBILITY-RUNTIME-001`. Bridges design/scenario/assignment diagnostics to future `METHOD_SUITABILITY_RUNTIME_001`.

---

## 29. Recommended next artifact

**Primary:** `METHOD_SUITABILITY_RUNTIME_001`

**Alternative:** `DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001`

Do not implement either in this artifact.
