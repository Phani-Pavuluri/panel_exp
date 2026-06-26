# SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` |
| **Artifact type** | `spend_contrast_feasibility_tooling_contract` |
| **Status** | `completed` |
| **Base commit** | `9b3c304` (Implement geo unit market feasibility diagnostics) |
| **Contract scope** | `spend_contrast_tooling_contract_no_runtime_diagnostics` |
| **Final verdict** | `spend_contrast_feasibility_tooling_contract_defined_no_runtime_diagnostics_or_production_authorization` |

This artifact is a **contract/specification document only**. It defines spend contrast diagnostic scope, report contracts, claim boundaries, and future implementation requirements. **No runtime spend contrast computation, budget reallocation engine, power/MDE calculation, design feasibility, candidate design generation, treatment/control assignment, lift/ROI, p-values/CIs, MMM calibration, LLM decisioning, or production authorization was implemented or authorized.**

---

## 2. Source-of-truth files inspected

| File | Role |
|------|------|
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Profiler implementation and spend coverage reports |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Unit/market readiness gate before spend contrast |
| `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | Spend data semantics, zero vs missing rules |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Golden path sequencing and claim boundaries |
| `ROADMAP_V4.md` | Planner lane ordering |
| `OPEN_INVESTIGATIONS_001.json` | Governance lane bindings |

---

## 3. Reason this contract is needed before spend diagnostics implementation

Geo unit/market feasibility diagnostics confirm that geo units and historical coverage are usable for downstream planning. The next question is whether **planned or observed spend variation** is directionally compatible with the intended manipulation (go-dark, heavy-up, go-live, budget reallocation).

Without an explicit contract, future implementations or agents may:

- treat spend coverage as spend contrast readiness
- infer power/MDE from spend deltas
- mix planned and observed spend silently
- treat missing spend as zero spend
- claim design feasibility from contrast diagnostics
- recommend budget optimization from contrast reports

This contract must exist **before** `SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001` runtime implementation.

---

## 4. Relationship to profiler and geo unit/market feasibility diagnostics

| Upstream artifact | Role for spend contrast |
|-------------------|-------------------------|
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Provides spend coverage, column mapping, missingness, channel/campaign mapping, zero vs missing semantics |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Confirms geo units and time coverage are ready for downstream design diagnostics; spend contrast must not upgrade blocked/provisional geo feasibility |

**Sequencing rule:** Future spend contrast diagnostics consume profiler output and geo feasibility output. They must respect profiler and geo feasibility claim boundaries (sample-schema, ballpark, blocked inputs cannot be upgraded to final contrast readiness).

**Core principle:** Spend contrast feasibility is not power/MDE. Spend contrast feasibility is not final design feasibility. Spend contrast feasibility is not ROI/lift/readout. Spend contrast feasibility is not budget optimization. Spend contrast feasibility is a deterministic diagnostic about whether planned or observed spend variation is adequate enough to pass to downstream design/power diagnostics.

---

## 5. Allowed spend contrast diagnostic scope

Future spend contrast tooling **may** evaluate:

- spend data availability and coverage by geo/time/channel
- whether spend exists for baseline, planning, and treatment windows
- whether spend direction is compatible with declared manipulation type
- spend delta magnitude and direction (diagnostic only, not power)
- channel/campaign spend mapping completeness
- budget reallocation source/destination mapping presence
- planned vs observed spend label integrity
- zero spend vs missing spend separation
- provisional classification when manipulation type is unknown

**Allowed positive claim:** `ready_for_downstream_power_diagnostics` — spend contrast is ready to be consumed by future power/MDE diagnostics. This does **not** mean powered, feasible, recommended, or production-ready.

---

## 6. Disallowed / non-goal scope

Future spend contrast tooling **must not**:

- compute power, MDE, sample size, or detectability
- compute p-values, confidence intervals, or causal readout
- compute lift, ROI, or incrementality
- generate candidate designs or treatment/control assignments
- decide final experiment feasibility
- recommend method or portfolio tier
- optimize budgets or reallocate spend
- authorize MMM calibration or production use
- use LLM inference on raw data without typed spend contrast report

---

## 7. Supported manipulation types

| Type | Description |
|------|-------------|
| `GO_DARK` | Turn off or reduce spend in treatment geos/channels |
| `HEAVY_UP` | Increase spend incrementally above baseline |
| `GO_LIVE` | Launch spend from near-zero baseline |
| `BUDGET_REALLOCATION` | Move spend from source to destination geos/channels |
| `UNKNOWN` | Manipulation type not declared; provisional classification only |

Do not over-engineer platform-specific rules. Manipulation type must be declared or inferred provisionally with explicit uncertainty.

---

## 8. Spend input requirements

**Required where applicable:**

| Field | Requirement |
|-------|-------------|
| `geo_unit_id` | Stable geo unit identifier |
| `time period` | Date/week or custom period aligned to grain |
| `spend amount` | Numeric spend value |
| `channel` or spend source | Required when channel-level contrast is requested |
| Period role | `baseline` / `planned` / `treatment` / `post`, or enough dates to derive relative to `planned_test_start_date` |
| `manipulation_type` | One of supported manipulation types |

**Optional:**

`campaign`, `platform`, `market`, `currency`, `budget_source`, `budget_destination`, `planned_spend`, `observed_spend`, `baseline_window`, `treatment_window`, `group_label` (treated/control/candidate)

---

## 9. Spend coverage vs spend contrast distinction

| Concept | Definition |
|---------|------------|
| **Spend coverage** | Spend data exists and has usable non-missing values for requested geo/time/channel scope |
| **Spend contrast** | Planned or observed spend differences are directionally compatible with the requested manipulation type |

The profiler may report spend coverage (`SpendSummaryReport`, `MissingnessReport`). Future spend diagnostics evaluate contrast. **Neither computes power/MDE.**

Coverage status taxonomy: `AVAILABLE`, `PARTIAL`, `MISSING`, `NOT_REQUESTED`.

Contrast may remain `NOT_EVALUATED` when coverage is available but manipulation type or windows are missing.

---

## 10. Planned spend vs observed spend distinction

| Type | Use | Label requirement |
|------|-----|-------------------|
| **Planned spend** | Planning diagnostics before execution | Must be labeled `planned` |
| **Observed spend** | Execution/readout diagnostics | Must be labeled `actual` or `observed` |

Rules:

- Planned spend may support planning diagnostics
- Observed spend may support execution/readout diagnostics
- Do not mix planned and observed spend silently
- Contrast diagnostics must declare which spend basis was used

---

## 11. Go-dark diagnostic contract

**Requirements:**

- Observed baseline spend exists in treatment geos/channels (or declared planned baseline)
- Planned or observed reduction or zero spend in treatment geos/channels during treatment/planning window

**Directional check:** Treatment spend < baseline spend (or observed/planned zero)

**Blocking:** No baseline spend when go-dark requested

**Allowed output:** `DIRECTIONALLY_COMPATIBLE`, `WEAK_OR_INSUFFICIENT`, `CONFLICTS_WITH_MANIPULATION`, `UNKNOWN`

---

## 12. Heavy-up diagnostic contract

**Requirements:**

- Baseline spend exists
- Planned or observed incremental spend increase in treatment geos/channels

**Directional check:** Treatment spend > baseline spend

**Warning:** Incremental signal weak or below configurable threshold (diagnostic only, not MDE)

**Blocking:** No baseline spend or no incremental signal when heavy-up requested

---

## 13. Go-live diagnostic contract

**Requirements:**

- Baseline near-zero or no spend
- Planned or observed launch spend in treatment geos/channels

**Directional check:** Treatment spend >> baseline spend (from near-zero)

**Warning:** Baseline already has substantial spend — go-live may be misclassified; suggest heavy-up or reallocation instead

**Blocking:** Cannot evaluate go-live without treatment window spend data

---

## 14. Budget reallocation diagnostic contract

**Requirements:**

- Source spend decrease and/or destination spend increase
- Explicit source/destination mapping (geo, channel, or budget bucket)
- Not only total spend change

**Directional check:** Net movement from source to destination consistent with declared mapping

**Blocking:** Budget reallocation requested but source/destination mapping missing

---

## 15. Channel/campaign spend mapping requirements

When channel-level contrast is requested:

- Channel or spend source column must be present and mapped
- Ambiguous channel mapping → warning or blocking per config
- Campaign-level contrast requires campaign identifier
- Total spend-only panels cannot support channel-level contrast without decomposition

Future report: `ChannelSpendMappingReport`

---

## 16. Baseline spend period requirements

Baseline window must be declared or derivable from `planned_test_start_date` and historical coverage.

Requirements:

- Sufficient baseline periods for declared manipulation type
- Baseline spend computed from observed spend unless explicitly labeled planned baseline
- Post-treatment data must not be used for baseline diagnostics

Future report: `SpendBaselineWindowReport`

---

## 17. Treatment/planning period spend requirements

Treatment or planning window must be declared or derivable.

Requirements:

- Planned or observed spend for treatment/planning window
- Window boundaries explicit or derivable from dates
- Group labels required when group-level contrast requested (treated/control/candidate)

Future report: `SpendPlanningWindowReport`

---

## 18. Zero spend vs missing spend rules

Preserve profiler semantics:

| Case | Rule |
|------|------|
| Observed zero spend | Means observed zero; supports go-dark/go-live when explicitly observed or planned as zero |
| Missing spend | Means unknown; must not be treated as zero |
| Planned zero | Must be labeled planned zero |
| Mixed basis | Planned and observed must not be silently combined |

---

## 19. Spend delta/contrast quality status taxonomy

**Spend contrast status:**

| Status | Meaning |
|--------|---------|
| `READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS` | Contrast directionally compatible; ready for power/MDE lane |
| `PASS_WITH_WARNINGS` | Contrast evaluable with non-blocking warnings |
| `PROVISIONAL` | Sample-schema, ballpark, or incomplete inputs |
| `BLOCKED` | Cannot evaluate contrast |
| `NOT_EVALUATED` | Coverage present but contrast not yet requested/evaluated |

**Spend contrast quality:**

| Quality | Meaning |
|---------|---------|
| `DIRECTIONALLY_COMPATIBLE` | Spend direction matches manipulation type |
| `WEAK_OR_INSUFFICIENT` | Direction correct but magnitude may be insufficient (not MDE) |
| `CONFLICTS_WITH_MANIPULATION` | Spend direction contradicts manipulation type |
| `UNKNOWN` | Cannot classify |

**Severity:** `INFO`, `WARNING`, `BLOCKING`

---

## 20. Required future output report contracts

Lightweight contract-level definitions (not implemented in this artifact):

| Contract | Purpose |
|----------|---------|
| `SpendContrastFeasibilityInput` | Input bundle: profiler report, geo feasibility report, spend panel, manipulation type, windows |
| `SpendContrastFeasibilityConfig` | Thresholds, channel-level flags, severity overrides |
| `SpendContrastFeasibilityReport` | Top-level diagnostic report |
| `SpendManipulationType` | Enum of supported manipulation types |
| `SpendCoverageStatus` | Coverage availability enum |
| `SpendContrastStatus` | Overall contrast readiness enum |
| `SpendContrastQuality` | Directional compatibility enum |
| `SpendBaselineWindowReport` | Baseline window spend summary |
| `SpendPlanningWindowReport` | Treatment/planning window spend summary |
| `SpendDeltaSummary` | Delta magnitude/direction by geo/channel (diagnostic only) |
| `ChannelSpendMappingReport` | Channel/campaign mapping completeness |
| `BudgetReallocationMappingReport` | Source/destination mapping report |
| `SpendContrastIssue` | Typed issue with code, severity, message |
| `SpendContrastSeverity` | INFO / WARNING / BLOCKING |
| `SpendContrastClaimBoundary` | Claim ceiling for report |

---

## 21. Claim boundaries and authorization flags

**Claim boundaries:**

| Boundary | Meaning |
|----------|---------|
| `SPEND_CONTRAST_DIAGNOSTIC_ONLY` | Diagnostic output only |
| `READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS` | May feed power/MDE lane |
| `PROVISIONAL_ONLY` | Sample-schema or ballpark ceiling |
| `BLOCKED` | No downstream claims |

**Always false** (this contract and future spend diagnostics unless later artifact explicitly authorizes):

- `final_experiment_feasibility_authorized`
- `candidate_design_authorized`
- `treatment_control_assignment_authorized`
- `power_authorized`
- `mde_authorized`
- `p_value_authorized`
- `confidence_interval_authorized`
- `lift_authorized`
- `roi_authorized`
- `method_recommendation_authorized`
- `portfolio_tiering_authorized`
- `budget_optimization_authorized`
- `mmm_calibration_authorized`
- `production_authorization_granted`
- `llm_decisioning_authorized`

**Allowed future positive claim:** `ready_for_downstream_power_diagnostics` only.

---

## 22. Failure/provisional modes

Documented failure and provisional modes:

- missing spend column when contrast requested
- missing manipulation type
- missing channel mapping when channel-level contrast requested
- missing baseline spend window
- missing planned/treatment spend window
- all spend missing
- missing treated/control or candidate group labels when group-level contrast requested
- planned spend mixed with observed spend without labels
- go-dark requested but no baseline spend exists
- heavy-up requested but no incremental spend signal exists
- go-live requested but baseline already has substantial spend
- budget reallocation requested but source/destination mapping missing
- negative spend values without correction/credit flag
- currency mismatch without currency mapping
- sample-schema mode overclaim
- ballpark mode overclaim

---

## 23. Agent/LLM explanation boundary

Agents/LLMs **may:**

- explain spend contrast reports and missing inputs
- summarize contrast quality and blocking reasons
- request the smallest missing input when contrast is blocked/provisional

Agents/LLMs **must not:**

- infer spend contrast from raw data without a typed `SpendContrastFeasibilityReport`
- upgrade spend contrast readiness into design feasibility, power/MDE, ROI, or production claims
- recommend budget optimization or treatment assignment from contrast diagnostics

If contrast is missing/blocked/provisional, agents should ask for the smallest missing input.

---

## 24. Report-builder boundary

Report builders **may:**

- render typed spend contrast outputs
- display coverage, contrast status, quality, issues, and claim boundaries

Report builders **must not:**

- compute contrast, power, MDE, design feasibility, lift, ROI, budget recommendations, or production claims
- upgrade provisional/blocked reports to final readiness in UI copy

---

## 25. Future implementation acceptance criteria

Future `SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001` should:

- consume profiler output and geo feasibility output
- separate spend coverage from spend contrast
- respect sample-schema and ballpark claim boundaries
- evaluate manipulation-compatible spend direction
- preserve missing vs zero spend semantics
- support planned vs observed spend labels
- emit typed `SpendContrastFeasibilityReport`
- never compute power/MDE, p-values/CIs, lift/ROI, design choice, or budget optimization
- remain deterministic, side-effect-free, no network, no LLM, no randomness

Suggested public API: `evaluate_spend_contrast_feasibility(profile_report, geo_feasibility_report, config=None) -> SpendContrastFeasibilityReport`

---

## 26. Tests expected for future implementation

Future implementation tests should cover at least:

1. missing spend blocks contrast when requested
2. spend coverage available but contrast not evaluated until manipulation type/window provided
3. go-dark directionally compatible contrast
4. go-dark blocked when baseline spend missing
5. heavy-up directionally compatible contrast
6. heavy-up weak/insufficient contrast warning
7. go-live directionally compatible contrast
8. go-live warning when baseline spend already substantial
9. budget reallocation requires source/destination mapping
10. planned vs observed spend labels preserved
11. missing spend not treated as zero
12. observed zero spend counted separately from missing
13. sample-schema mode cannot produce final contrast readiness
14. ballpark mode provisional only
15. no power/MDE/p-value/CI/lift/ROI/design/production authorization
16. no fixture-specific branching

---

## 27. Roadmap placement

Golden path sequence:

```
GEO_KPI_SPEND_DATA_PROFILER_001 ✅
→ GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001 ✅
→ SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001 ✅ (this artifact)
→ SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001 (next implementation)
```

---

## 28. Recommended next artifact

**`SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001`** — deterministic runtime implementation of spend contrast and budget reallocation diagnostics per this contract.

---

## 29. Final verdict

**`spend_contrast_feasibility_tooling_contract_defined_no_runtime_diagnostics_or_production_authorization`**

Spend contrast feasibility tooling contract defined. Supported manipulation types, coverage vs contrast distinction, planned vs observed spend rules, zero vs missing spend rules, future output contracts, status taxonomy, failure/provisional modes, LLM/report-builder boundaries, and future implementation acceptance criteria documented. No runtime spend diagnostics, power/MDE, design inference, or production authorization granted.
