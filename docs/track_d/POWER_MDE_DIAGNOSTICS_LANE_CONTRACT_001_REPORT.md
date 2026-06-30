# POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001` |
| **Artifact type** | `power_mde_diagnostics_lane_contract` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_runtime_power_mde` |
| **Base commit** | `13294ff` (Define power MDE spend feasibility handoff contract) |
| **Final verdict** | `power_mde_diagnostics_lane_contract_defined_no_runtime_power_mde_or_production_authorization` |

This artifact is a **contract/specification document only**. It defines the future deterministic power/MDE diagnostics lane for GeoX planning. **No runtime power/MDE computation, p-values, confidence intervals, lift, ROI, design generation, estimator selection, MMM runtime, or production authorization was implemented or authorized.**

---

## 2. Source files inspected

| File | Role |
|------|------|
| `POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001` | Immediate upstream handoff contract |
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Spend feasibility diagnostics |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Data profiler upstream |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo feasibility upstream |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Golden path sequencing |

---

## 3. Why this lane contract is needed

`POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001` defines how spend feasibility outputs cross into power/MDE planning, but does not define the power/MDE lane itself. Without an explicit lane contract, future implementations may incorrectly upgrade:

- spend handoff ready → powered
- KPI MDE target displayed → detectability proven
- sensitivity readiness → design feasible
- dosage contrast feasible → estimator approved
- MMM advisory bridge → causal truth

This contract defines the deterministic power/MDE diagnostics lane boundary before any runtime implementation.

---

## 4. Core goal statement

`POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001` defines the future deterministic power/MDE diagnostics lane for GeoX planning. It specifies required inputs, output contracts, status semantics, diagnostic boundaries, and handoff rules from profiler, geo feasibility, spend feasibility, and future design/cell structures. It does not implement runtime power/MDE, p-values, confidence intervals, lift, ROI, design generation, estimator selection, or production authorization.

---

## 5. Relationship to profiler

Future power/MDE diagnostics must consume `GeoKpiSpendProfilerReport` from `GEO_KPI_SPEND_DATA_PROFILER_001`.

**Profiler gate rules:**

- If profiler readiness is blocked, future power/MDE diagnostics must not run
- Profiler establishes data readiness (KPI/spend schema, coverage, time grain) but does not authorize power, design, or production claims
- Profiler outputs inform noise/history readiness but do not substitute for KPI history validation

---

## 6. Relationship to geo feasibility

Future power/MDE diagnostics must consume `GeoUnitMarketFeasibilityReport` from `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001`.

**Geo feasibility gate rules:**

- If geo/unit feasibility is blocked, future power/MDE diagnostics must not run
- Geo feasibility establishes unit/market structure viability but does not authorize design assignment or estimator validity
- Geo unit IDs and market structure inform cell structure evaluation when candidate cells are supplied

---

## 7. Relationship to spend feasibility diagnostics

Future power/MDE diagnostics must consume `SpendRequirementManipulationFeasibilityReport` from `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` via the spend handoff layer.

**Spend feasibility rules:**

- Spend feasibility is an input to power/MDE diagnostics, not a substitute for power/MDE
- Spend manipulation feasibility does not imply design feasibility
- Candidate manipulation options inform spend compatibility but do not authorize treatment/control assignment

---

## 8. Relationship to power/MDE spend handoff contract

Future power/MDE diagnostics must consume `PowerMdeSpendFeasibilityHandoffReport` from `POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001`.

**Handoff consumption rules:**

- Preserve `required_spend_delta_source` and all response bridge advisory flags
- Preserve `business_response_risk`, dosage/difference-in-policy flags, and control contamination flags
- `SPEND_HANDOFF_READY_FOR_POWER_DIAGNOSTICS` enables spend-confirmed sensitivity mode only; it does not mean powered
- Blocked spend handoff blocks spend-confirmed sensitivity; KPI-only exploratory mode may remain available per config

---

## 9. Conceptual distinctions

| Concept | Definition | Computed here? |
|---------|------------|----------------|
| **KPI MDE** | Minimum detectable effect target in actual KPI units (e.g. 500 conversions/cell) | No — target only |
| **Power** | Probability of detecting a true effect of given size under assumptions | No — contract only |
| **Sensitivity / MDE** | Effect size detectable under proposed design assumptions | No — contract only |
| **Spend feasibility** | Whether spend manipulation can create required spend contrast | Consumed from spend module |
| **Design feasibility** | Whether cell assignment, geography, duration, balance support a design | Future design layer only |
| **Estimator/inference validity** | Whether SCM/TBR/DID/etc. are valid for design and estimand | Future method layer only |
| **Production authorization** | Production use | Always blocked |

**Critical non-upgrades:**

- `POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME` ≠ powered
- spend feasible ≠ design feasible
- KPI MDE target ≠ detectability proven
- sensitivity readiness ≠ estimator approved
- MMM advisory translation ≠ causal truth

---

## 10. Future input contracts

Lightweight contract-level definitions (not implemented in this artifact):

| Contract | Purpose |
|----------|---------|
| `PowerMdeDiagnosticsInput` | Top-level input bundle for future runtime |
| `PowerMdeDiagnosticsConfig` | Mode flags, gate thresholds, exploratory allowances |
| `PowerMdeDiagnosticsReport` | Top-level lane report (contract concept) |
| `PowerMdeDiagnosticStatus` | Lane status enum |
| `PowerMdeDiagnosticIssue` | Typed issue with code, severity, message |
| `PowerMdeDiagnosticSeverity` | INFO / WARNING / BLOCKING |
| `PowerMdeEstimandSpec` | Estimand type and compatibility metadata |
| `PowerMdeNoiseModelSpec` | Noise/history assumptions for future sensitivity |
| `PowerMdePanelHistorySpec` | Pre-period KPI history requirements |
| `PowerMdeCellStructureSpec` | Candidate cell structure metadata |
| `PowerMdeSpendHandoffSpec` | Spend handoff bundle from upstream contract |
| `PowerMdeSensitivityTarget` | KPI MDE target with unit and scope |
| `PowerMdeClaimBoundary` | Claim ceiling for lane outputs |

**Future runtime may consume:**

`profiler_report`, `geo_unit_market_feasibility_report`, `spend_requirement_manipulation_feasibility_report`, `power_mde_spend_feasibility_handoff_report`, `candidate_cell_structure`, `geo_unit_ids`, `cell_ids`, `cell_roles`, `time_grain`, `pre_period_window`, `test_duration`, `post_period_window`, `kpi_column`, `kpi_unit`, `kpi_mde`, `relative_mde`, `absolute_mde`, `baseline_kpi_mean`, `baseline_kpi_variance`, `historical_noise_summary`, `seasonality_summary`, `cell_balance_summary`, `spend_handoff_status`, `required_spend_delta`, `candidate_manipulation_options`, `dosage_or_difference_in_policy_flags`, `control_contamination_flags`, `method_suitability_review_required`

---

## 11. Future output contracts

| Contract | Purpose |
|----------|---------|
| `PowerMdeDiagnosticsReport` | Top-level lane diagnostic report |
| `PowerMdeReadinessReport` | Readiness gate evaluation summary |
| `PowerMdeSensitivityReport` | Future sensitivity/MDE diagnostic outputs (contract only) |
| `PowerMdeNoiseReadinessReport` | Noise/history readiness evaluation |
| `PowerMdeCellStructureReport` | Cell structure compatibility evaluation |
| `PowerMdeSpendCompatibilityReport` | Spend handoff compatibility evaluation |
| `PowerMdeEstimandCompatibilityReport` | Estimand compatibility evaluation |
| `PowerMdeIssue` | Typed lane issue |
| `PowerMdeClaimBoundaryReport` | Explicit claim ceiling report |

These are contract concepts only. No runtime values are computed in this artifact.

---

## 12. Readiness gates

Future power/MDE runtime must evaluate gates in order:

| Order | Gate | Block if failed? |
|-------|------|------------------|
| 1 | **profiler_gate** | Yes — blocks all runtime |
| 2 | **geo_unit_market_feasibility_gate** | Yes — blocks all runtime |
| 3 | **spend_handoff_gate** | Blocks spend-confirmed modes; KPI-only may remain |
| 4 | **cell_structure_gate** | Provisional or blocked depending on mode |
| 5 | **kpi_mde_target_gate** | Blocks if KPI MDE target missing/invalid |
| 6 | **noise_history_gate** | Yes — blocks runtime if KPI history missing |
| 7 | **estimand_compatibility_gate** | Blocks or routes to dosage mode |
| 8 | **method_suitability_precheck_gate** | Warning/review only; does not authorize estimator |

**Gate rules:**

1. If profiler blocked → future power/MDE must not run
2. If geo feasibility blocked → future power/MDE must not run
3. If spend handoff blocked → spend-confirmed sensitivity blocked; KPI-only exploratory allowed if configured
4. If required spend delta unknown → must not claim spend-confirmed feasibility
5. If dosage/difference-in-policy required → carry dosage estimand flags
6. If control contamination present → do not assume business-as-usual control
7. If candidate cell structure missing → provisional or blocked depending on mode
8. If baseline KPI history/noise missing → blocked

---

## 13. Future runtime modes

Modes are contract-defined only. No runtime implementation in this artifact.

| Mode | Semantics |
|------|-----------|
| `KPI_ONLY_SENSITIVITY` | Uses KPI history/noise and duration only; does not claim spend can create the effect |
| `SPEND_CONFIRMED_SENSITIVITY` | Requires spend handoff ready or ready with warnings; preserves response bridge provenance |
| `DESIGN_CELL_SENSITIVITY` | Requires candidate cell structure |
| `DOSAGE_CONTRAST_SENSITIVITY` | Requires dosage/difference-in-policy estimand flags and method-suitability review |
| `EXPLORATORY_BACK_OF_NAPKIN` | Advisory only; cannot produce final readiness or design claims |

---

## 14. Spend handoff treatment

- Spend feasibility is an input to power/MDE diagnostics, not a substitute for power/MDE
- Power/MDE readiness must preserve `required_spend_delta_source`
- MMM/proxy/back-of-napkin bridges remain advisory
- Business-response risk must be carried into power/MDE outputs
- Dosage/difference-in-policy flags must be carried into power/MDE outputs
- Control contamination flags must be carried into power/MDE outputs

**Flags to preserve from handoff:** `MMM_ADVISORY_SIGNAL_USED`, `MMM_OUT_OF_SUPPORT`, `OUT_OF_MMM_SUPPORT`, `MMM_CALIBRATION_WEAK`, `PROXY_RESPONSE_USED`, `PROXY_LEVEL_MISMATCH`, `BACK_OF_NAPKIN_ASSUMPTION_USED`, `BUSINESS_RESPONSE_RISK`, `REQUIRED_SPEND_DELTA_UNKNOWN`, `REQUIRED_SPEND_DELTA_ESTIMATED_ADVISORY`, `REQUIRED_SPEND_DELTA_SUPPLIED`

---

## 15. KPI MDE treatment

Future diagnostics must represent KPI MDE with explicit scope:

| Representation | Rule |
|----------------|------|
| **Absolute KPI MDE** | Effect in KPI units (e.g. 500 conversions) |
| **Relative KPI MDE** | Effect as proportion of baseline (e.g. 3% lift) |
| **Baseline KPI level** | Required context for relative MDE |
| **Cell-level MDE** | Per-cell target |
| **Aggregate-panel MDE** | Panel-wide target |
| **Duration-specific MDE** | MDE scoped to test duration |

**Rules:**

- Absolute and relative MDE must not be silently mixed
- Cell-level and aggregate-panel MDE must not be silently mixed
- KPI unit must be preserved
- If KPI is conversions and spend is channel-level, estimand remains total KPI response to channel spend policy change

---

## 16. Noise/history treatment

Future noise/history readiness requirements (contract only; no formulas defined here):

- Pre-period KPI history
- Time grain alignment
- Missing KPI values policy
- Zero KPI values policy
- Outlier handling policy
- Seasonality indicators
- Cell-level variance
- Geo-level variance
- Pre-period trend balance
- Historical volatility summary
- Minimum pre-period length

If baseline KPI history or noise summary is missing, future power/MDE runtime must be blocked.

---

## 17. Design/cell structure treatment

Future power/MDE runtime must know which design type is being evaluated:

- Single treated cell vs control
- Multi-cell design
- Common control design
- Matched-pair design
- Dosage contrast design
- Difference-in-policy design
- Budget reallocation design

**If candidate cell structure is not supplied:**

- Status must be `POWER_MDE_PROVISIONAL` or `POWER_MDE_BLOCKED_BY_CELL_STRUCTURE` depending on mode
- No design feasibility claim allowed
- Do not generate design candidates in this artifact

---

## 18. Dosage / difference-in-policy treatment

- Dosage/difference-in-policy is a first-class future sensitivity mode (`DOSAGE_CONTRAST_SENSITIVITY`)
- It is not standard untreated-control go-dark
- Future power/MDE must carry the estimand type
- Future method-suitability must validate estimator/inference compatibility
- Control contamination prevents standard business-as-usual control assumptions
- Readiness for dosage sensitivity does not authorize estimator or inference validity
- When dosage estimand required, emit `POWER_MDE_REQUIRES_METHOD_SUITABILITY_REVIEW`

---

## 19. Examples

### Example 1 — Ready for runtime, not powered

Profiler, geo feasibility, spend handoff, KPI history, and candidate cells are ready. Status: `POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME`. **Claim:** future diagnostic can run. **Not claim:** experiment is powered.

### Example 2 — Spend handoff blocked

Spend handoff blocked because required spend delta is unknown. Power/MDE lane blocks spend-confirmed sensitivity and allows only `KPI_ONLY_SENSITIVITY` or `EXPLORATORY_BACK_OF_NAPKIN` if configured.

### Example 3 — MMM advisory bridge

MMM advisory bridge supplies required spend delta and business-response risk is high. Power/MDE must preserve `MMM_ADVISORY_SIGNAL_USED` and `BUSINESS_RESPONSE_RISK`. No ROI or MMM calibration claim allowed.

### Example 4 — Dosage contrast

Spend handoff requires `DOSAGE_CONTRAST_ESTIMAND_REQUIRED`. Power/MDE may route to `DOSAGE_CONTRAST_SENSITIVITY` mode but must require method-suitability review before estimator/inference claims.

### Example 5 — Cell structure missing

KPI history and spend handoff are ready, but no candidate cell structure exists. Status: `POWER_MDE_PROVISIONAL` or `POWER_MDE_BLOCKED_BY_CELL_STRUCTURE`. No design feasibility claim allowed.

---

## 20. Claim boundaries

**Always false:**

`runtime_power_mde_diagnostics_implemented`, `power_computed`, `mde_computed`, `p_value_computed`, `confidence_interval_computed`, `lift_computed`, `roi_computed`, `budget_optimization_authorized`, `candidate_design_authorized`, `treatment_control_assignment_authorized`, `estimator_inference_authorized`, `mmm_runtime_calls_implemented`, `mmm_calibration_authorized`, `production_authorization_granted`, `llm_decisioning_authorized`

**Contract-level positive:** `power_mde_lane_contract_defined`, `spend_handoff_dependency_defined`, `kpi_mde_representation_defined`, `noise_history_requirements_defined`, `dosage_sensitivity_mode_defined`, `claim_boundaries_defined`

---

## 21. Future implementation acceptance criteria

Future `POWER_MDE_DIAGNOSTICS_RUNTIME_001` implementation must:

- Consume profiler, geo feasibility, spend handoff, and optional cell-structure inputs
- Block if upstream gates are blocked
- Preserve KPI units
- Preserve absolute vs relative MDE distinction
- Preserve cell-level vs aggregate MDE distinction
- Preserve response bridge provenance
- Preserve business-response risk
- Preserve dosage/difference-in-policy flags
- Preserve control contamination flags
- Emit readiness/status outputs
- Support KPI-only exploratory mode separately from spend-confirmed sensitivity
- Support dosage sensitivity mode only with explicit estimand flag
- Not compute design generation, estimator validity, lift, ROI, budget optimization, or production authorization

---

## 22. Future tests

1. Blocked profiler blocks power/MDE runtime
2. Blocked geo feasibility blocks power/MDE runtime
3. Blocked spend handoff blocks spend-confirmed sensitivity
4. Required spend unknown allows only KPI-only exploratory mode
5. KPI MDE units preserved
6. Absolute and relative MDE not silently mixed
7. Cell-level and aggregate-panel MDE not silently mixed
8. MMM advisory flags preserved
9. Business-response risk preserved
10. Proxy mismatch preserved
11. Dosage contrast routes to dosage sensitivity mode
12. Control contamination blocks standard go-dark interpretation
13. Missing candidate cell structure produces provisional/blocked status
14. Missing KPI history blocks runtime
15. Ready-for-runtime status does not set powered/design/ROI/production flags
16. No fixture-specific branching

---

## 23. Roadmap placement

```
GEO_KPI_SPEND_DATA_PROFILER_001 ✅
→ GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001 ✅
→ SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001 ✅
→ SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001 ✅
→ POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001 ✅
→ POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001 ✅ (this artifact)
→ POWER_MDE_DIAGNOSTICS_RUNTIME_001 (next)
```

---

## 24. Recommended next artifact

**`POWER_MDE_DIAGNOSTICS_RUNTIME_001`**

---

## 25. Final verdict

**`power_mde_diagnostics_lane_contract_defined_no_runtime_power_mde_or_production_authorization`**

Power/MDE diagnostics lane contract defined. Profiler, geo feasibility, spend handoff dependencies documented. KPI MDE representation, absolute/relative and cell/aggregate separation, noise/history requirements, cell structure requirements, runtime modes, dosage sensitivity mode, response bridge provenance, business-response risk, and control contamination preservation documented. No runtime power/MDE or production authorization granted.
