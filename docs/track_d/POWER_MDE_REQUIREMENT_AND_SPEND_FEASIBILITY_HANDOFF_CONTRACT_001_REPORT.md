# POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001` |
| **Artifact type** | `power_mde_requirement_spend_feasibility_handoff_contract` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_power_mde_runtime` |
| **Base commit** | `b800ba7` (Implement spend requirement manipulation feasibility diagnostics) |
| **Final verdict** | `power_mde_requirement_spend_feasibility_handoff_contract_defined_no_power_mde_or_production_authorization` |

This artifact is a **contract/specification handoff document only**. It defines how future power/MDE diagnostics may consume spend requirement/manipulation feasibility outputs. **No runtime power/MDE computation, spend diagnostics changes, design generation, lift/ROI, MMM runtime, or production authorization was implemented or authorized.**

---

## 2. Source files inspected

| File | Role |
|------|------|
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Upstream spend diagnostics implementation |
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001` | Spend module contract |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Data profiler upstream |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo feasibility upstream |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Golden path sequencing |

---

## 3. Why this handoff contract is needed

`SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` can emit `ready_for_downstream_power_diagnostics`. Without an explicit handoff contract, future layers may incorrectly upgrade:

- spend feasible → powered
- MMM advisory translation → causal truth
- KPI MDE displayed → spend requirement proven
- dosage contrast feasible → estimator approved

This contract defines the boundary before any runtime power/MDE lane is implemented.

---

## 4. Core goal statement

`POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001` defines how future power/MDE diagnostics may consume spend requirement/manipulation feasibility outputs, KPI MDE targets, response-bridge metadata, and candidate manipulation options. It preserves the separation between spend feasibility, KPI sensitivity, statistical power, design feasibility, estimator validity, and production authorization.

---

## 5. Relationship to spend requirement/manipulation feasibility diagnostics

Future handoff consumes `SpendRequirementManipulationFeasibilityReport` from `evaluate_spend_requirement_and_manipulation_feasibility()`, including:

- `SpendDataReadinessReport`
- `BaselineSpendInventoryReport`
- `ResponseBridgeReport`
- `ManipulationFeasibilityReport`
- `PlanningBoundaryReport`

The handoff must not reinterpret spend diagnostics outputs as power, design, or production claims.

---

## 6. Relationship to future power/MDE diagnostics

Recommended next artifact: **`POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001`** (contract for the power/MDE lane itself).

This handoff contract precedes runtime power/MDE implementation. Future runtime artifacts must:

- Validate spend handoff status before computing sensitivity/power
- Preserve all advisory provenance from spend module
- Never upgrade handoff readiness to "powered" or "design feasible"

---

## 7. Conceptual distinctions

| Concept | Definition | Computed here? |
|---------|------------|----------------|
| **KPI MDE** | Minimum detectable effect in actual KPI units (e.g. 500 conversions/cell) | No |
| **Statistical power / sensitivity** | Detectable KPI effect given noise, panel, duration | No |
| **Required spend contrast** | Spend delta needed for planned manipulation (supplied or advisory) | Consumed from spend module |
| **Achievable spend manipulation** | go-dark max, heavy-up multiplier, dosage delta, historical support | Consumed from spend module |
| **Design feasibility** | Whether a candidate design is viable | Future layer only |
| **Estimator/inference validity** | Whether method supports estimand | Future method layer only |
| **Production authorization** | Production use | Always blocked |

**Critical non-upgrades:**

- `READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS` ≠ powered
- spend feasible ≠ design feasible
- MMM advisory translation ≠ causal truth
- KPI MDE displayed ≠ spend requirement proven
- dosage contrast feasible ≠ estimator/inference approved

---

## 8. Handoff statuses

| Status | Meaning |
|--------|---------|
| `SPEND_HANDOFF_READY_FOR_POWER_DIAGNOSTICS` | Spend-side inputs sufficient for power/MDE evaluation (not powered) |
| `SPEND_HANDOFF_READY_WITH_WARNINGS` | Handoff allowed with non-blocking warnings |
| `SPEND_HANDOFF_PROVISIONAL_RESPONSE_BRIDGE` | Advisory or unknown response bridge; exploratory only |
| `SPEND_HANDOFF_BLOCKED_BY_SPEND_DATA` | Spend readiness blocked |
| `SPEND_HANDOFF_BLOCKED_BY_REQUIRED_SPEND_UNKNOWN` | Required spend delta unknown |
| `SPEND_HANDOFF_BLOCKED_BY_MANIPULATION_INFEASIBLE` | No feasible manipulation path |
| `SPEND_HANDOFF_REQUIRES_DOSAGE_ESTIMAND_REVIEW` | Dosage/difference-in-policy estimand required |
| `SPEND_HANDOFF_REQUIRES_METHOD_SUITABILITY_REVIEW` | Method layer must validate estimand support |
| `SPEND_HANDOFF_NOT_EVALUATED` | Handoff not yet requested |

---

## 9. Future input contract

`PowerMdeSpendFeasibilityHandoffInput` may consume from spend report:

`spend_report_id`, `spend_report_artifact_id`, `spend_readiness_status`, `baseline_inventory_status`, `response_bridge_status`, `manipulation_feasibility_status`, `planning_boundary_status`, `candidate_manipulation_options`, `required_spend_delta`, `required_spend_delta_source`, `kpi_mde`, `kpi_unit`, `response_bridge_source`, `response_bridge_advisory_flags`, `mmm_advisory_used`, `proxy_response_used`, `back_of_napkin_assumption_used`, `business_response_risk`, `historical_support_status`, `required_heavy_up_multiplier`, `go_dark_max_delta`, `dosage_delta`, `budget_gap`, `control_contamination_flags`, `estimand_shift_required`, `dosage_contrast_estimand_required`, `method_suitability_review_required`, `ready_for_downstream_power_diagnostics`

---

## 10. Future output contract

Lightweight contract-level definitions (not implemented in this artifact):

| Contract | Purpose |
|----------|---------|
| `PowerMdeSpendFeasibilityHandoffInput` | Input bundle from spend report + KPI MDE targets |
| `PowerMdeSpendFeasibilityHandoffConfig` | Thresholds, exploratory-mode flags |
| `PowerMdeSpendFeasibilityHandoffReport` | Top-level handoff report |
| `PowerMdeSpendHandoffStatus` | Handoff status enum |
| `PowerMdeSpendHandoffIssue` | Typed issue with code, severity, message |
| `PowerMdeSpendHandoffSeverity` | INFO / WARNING / BLOCKING |
| `PowerMdeSpendRequirementSource` | Source of required spend delta |
| `PowerMdeSpendRequirementBoundary` | Claim ceiling for handoff |

---

## 11. Response bridge handling

**Supported sources:** `NONE`, `USER_PROVIDED_REQUIRED_SPEND_DELTA`, `POWER_LAYER_REQUIRED_SPEND_DELTA`, `MMM_RESPONSE_CURVE`, `MMM_ROMS`, `PRIOR_EXPERIMENT`, `PROXY_RESPONSE_CURVE`, `BACK_OF_NAPKIN_USER_ASSUMPTION`

**Rules:**

- Direct required spend delta = supplied input, not computed truth
- MMM/ROMS = advisory-only
- Proxy bridge = advisory-only; preserve `PROXY_LEVEL_MISMATCH` when levels differ
- Back-of-napkin = advisory-only; must be labeled
- Prior experiment = requires scope/freshness/estimand compatibility metadata
- Nonlinear MMM curve inversion = not part of this handoff

**Flags to preserve:** `MMM_ADVISORY_SIGNAL_USED`, `MMM_OUT_OF_SUPPORT`, `OUT_OF_MMM_SUPPORT`, `MMM_CALIBRATION_WEAK`, `PROXY_RESPONSE_USED`, `PROXY_LEVEL_MISMATCH`, `BACK_OF_NAPKIN_ASSUMPTION_USED`, `BUSINESS_RESPONSE_RISK`, `REQUIRED_SPEND_DELTA_UNKNOWN`, `REQUIRED_SPEND_DELTA_ESTIMATED_ADVISORY`, `REQUIRED_SPEND_DELTA_SUPPLIED`

---

## 12. Spend-to-power interaction rules

1. If spend readiness blocked → future power/MDE must not run
2. If required spend delta unknown → power/MDE may run exploratory KPI-only mode only
3. If manipulation feasibility blocked → power/MDE must not claim feasible design
4. If response bridge advisory → preserve advisory provenance in all downstream outputs
5. If business-response risk high → report spend may be operationally feasible but unlikely to produce KPI MDE under advisory assumptions
6. If dosage/difference-in-policy required → route to dosage-compatible design/method lane
7. If control contamination present → do not assume business-as-usual control preserved

---

## 13. Dosage / difference-in-policy handoff

- `DOSAGE_CONTRAST` and `DIFFERENCE_IN_POLICY` are first-class spend manipulation options
- Valid planning options only under explicit low-vs-high policy estimands
- Must not be interpreted as standard go-dark vs untreated business-as-usual control
- Future power/MDE must carry estimand type
- Future method suitability must validate estimator/inference support for dosage estimand
- Handoff preserves control contamination and estimand-shift flags
- `METHOD_SUITABILITY_REVIEW_REQUIRED` when dosage estimand implied

---

## 14. Examples

### Example 1 — Ready handoff

KPI MDE = 500 conversions per cell. Required spend delta supplied = $100K/week. Spend module finds heavy-up can create $100K/week within historical support. Handoff status = `SPEND_HANDOFF_READY_FOR_POWER_DIAGNOSTICS`. **This does not mean powered.**

### Example 2 — Advisory MMM bridge with business-response risk

KPI MDE = 500 conversions per cell. MMM advisory bridge suggests $100K/week produces only ~180 conversions. Spend manipulation operationally feasible, but business-response risk is high. Future power/MDE must preserve `MMM_ADVISORY_SIGNAL_USED` and `BUSINESS_RESPONSE_RISK`.

### Example 3 — Go-dark insufficient

Required spend delta = $120K/week. Baseline spend = $80K/week. Go-dark max delta = $80K/week. Handoff blocks go-dark feasibility; may pass heavy-up/dosage alternatives if available.

### Example 4 — Dosage contrast required

Control cell heavy-upped, test cell go-dark. Spend difference feasible. Standard go-dark interpretation not allowed. Handoff requires `SPEND_HANDOFF_REQUIRES_DOSAGE_ESTIMAND_REVIEW` and `SPEND_HANDOFF_REQUIRES_METHOD_SUITABILITY_REVIEW`.

---

## 15. Claim boundaries

**Always false:**

`runtime_power_diagnostics_implemented`, `power_computed`, `mde_computed`, `p_value_computed`, `confidence_interval_computed`, `lift_computed`, `roi_computed`, `budget_optimization_authorized`, `candidate_design_authorized`, `treatment_control_assignment_authorized`, `estimator_inference_authorized`, `mmm_runtime_calls_implemented`, `mmm_calibration_authorized`, `production_authorization_granted`, `llm_decisioning_authorized`

**Contract-level positive:** `handoff_contract_defined`, `spend_to_power_boundary_defined`, `dosage_handoff_boundary_defined`, `response_bridge_provenance_required`

---

## 16. Future implementation acceptance criteria

Future handoff runtime (if implemented) must:

- Consume `SpendRequirementManipulationFeasibilityReport`
- Validate spend readiness before power/MDE
- Preserve advisory response bridge provenance
- Preserve KPI MDE in actual units
- Preserve required spend delta source
- Preserve business-response risk
- Preserve dosage/difference-in-policy estimand flags
- Preserve control contamination flags
- Emit handoff statuses
- Block unsupported upgrade from spend feasibility to powered/design feasible
- Not compute power/MDE unless in later runtime power artifact
- Not authorize final design, estimator, ROI, budget optimization, or production

---

## 17. Future tests

1. Blocked spend readiness blocks power handoff
2. Required spend unknown creates provisional/exploratory handoff
3. Direct required spend delta produces supplied-source handoff
4. MMM advisory bridge preserves `MMM_ADVISORY_SIGNAL_USED`
5. Proxy bridge preserves `PROXY_LEVEL_MISMATCH`
6. Back-of-napkin bridge preserves `BACK_OF_NAPKIN_ASSUMPTION_USED`
7. Business-response risk preserved
8. Go-dark insufficient blocks go-dark handoff
9. Heavy-up within support → ready or ready with warnings
10. Heavy-up out-of-support preserved as warning/block per config
11. Dosage contrast emits dosage estimand requirement
12. Control contamination prevents standard go-dark interpretation
13. Ready handoff does not set powered/design/ROI/production flags
14. No fixture-specific branching

---

## 18. Roadmap placement

```
GEO_KPI_SPEND_DATA_PROFILER_001 ✅
→ GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001 ✅
→ SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001 ✅
→ SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001 ✅
→ POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001 ✅ (this artifact)
→ POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001 (next)
```

---

## 19. Recommended next artifact

**`POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001`**

---

## 20. Final verdict

**`power_mde_requirement_spend_feasibility_handoff_contract_defined_no_power_mde_or_production_authorization`**

Spend-to-power handoff contract defined. KPI MDE unit preservation, required spend delta provenance, response bridge provenance, business-response risk, dosage/difference-in-policy handoff, control contamination preservation, and method-suitability review requirements documented. No runtime power/MDE or production authorization granted.
