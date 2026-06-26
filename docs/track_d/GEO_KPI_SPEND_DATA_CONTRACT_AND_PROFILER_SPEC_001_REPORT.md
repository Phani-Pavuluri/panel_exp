# GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` |
| **Artifact type** | `geo_kpi_spend_data_contract_and_profiler_spec` |
| **Status** | `completed` |
| **Base commit** | `13cef1a` (Audit roadmap implementation detail gaps) |
| **Contract scope** | `geo_kpi_spend_data_contract_profiler_spec_no_runtime` |
| **Final verdict** | `geo_kpi_spend_data_contract_profiler_spec_defined_no_runtime_authorization` |

This artifact is a **contract/specification document only**. It defines geo-level KPI/spend data semantics and profiler output contracts. **No runtime profiler, agents, estimators, design algorithms, inference logic, or production recommendations were implemented or authorized.**

---

## 2. Source-of-truth files audited

| File | Role |
|------|------|
| `ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001` | Identified this as first pending contract |
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001` | Data profiler agent tooling framework |
| `EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001` | Data-first planning architecture |
| `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` | Design/estimator separation |
| `PRODUCTION_READINESS_BACKLOG_LEDGER_001` | Control-plane backlog |

---

## 3. Reason for data contract

Every downstream planner diagnostic (geo feasibility, spend contrast, portfolio tiering, design generation) depends on correct geo/KPI/spend data semantics. Without an explicit contract, Cursor/agents may:

- guess geo units from ambiguous columns
- silently treat missing spend as zero
- mix daily and weekly grains
- use post-treatment data for pre-period diagnostics
- claim unit eligibility without coverage checks

This contract must exist **before** `GEO_KPI_SPEND_DATA_PROFILER_001` runtime implementation.

---

## 4. Data-first planning principle

Uploaded or declared geo/KPI/spend data is the primary evidence source for planner diagnostics. Manual questions are fallback only. The profiler produces typed evidence reports; it does not authorize design feasibility, p-values, or CIs.

**Rule:** No typed profiler report → no downstream claim requiring that report.

---

## 5. Accepted input modes

| Mode | Description | Claim ceiling |
|------|-------------|---------------|
| **Full panel mode** | Geo-unit × date/week × KPI × spend panel with historical pre-period and optional planning-window spend | Supports feasibility diagnostics when quality gates pass |
| **Sample schema mode** | Small sample file to infer schema, columns, grain, missing fields | **No final feasibility claims** |
| **Ballpark mode** | Approximate market-level KPI/spend/duration/unit-count values | **Provisional only**; full contract in `BALLPARK_FEASIBILITY_MODE_CONTRACT_001` |

---

## 6. Required fields

| Field | Requirement |
|-------|-------------|
| `geo_unit_id` | Stable identifier for randomization unit |
| `date_or_week` | Observation date or week anchor |
| `kpi_value` | Outcome metric value |
| `spend_value` | Spend amount aligned to geo/date grain |

**Also required (one of each pair):**

- `kpi_name` **or** single clearly declared KPI column
- `channel` **or** clearly declared total/media spend column

**For portfolio planning, require or mark missing:**

- `campaign_or_test_id`
- `region_or_country`
- `currency`
- `time_grain`

---

## 7. Optional fields

`geo_unit_name`, `geo_unit_type`, `parent_region`, `market_size_weight`, `population`, `baseline_sales_or_conversions`, `revenue`, `orders`, `visitors`, `trials`, `installs`, `new_users`, `existing_users`, `platform`, `product`, `campaign_id`, `campaign_name`, `channel`, `sub_channel`, `spend_type`, `impressions`, `clicks`, `cost`, `control_exposure_flag`, `launch_date`, `promotion_flag`, `holiday_flag`, `seasonality_flag`, `known_blackout_flag`, `eligibility_flag`, `exclusion_reason`.

---

## 8. Accepted grains and grain-detection rules

**Supported grains:** `daily`, `weekly`, `custom_period`

| Rule | Behavior |
|------|----------|
| Grain detection | Profiler must detect grain when possible; emit `TimeGrainReport` |
| Mixed grain | Blocking without explicit mapping |
| Weekly alignment | Week start must be declared |
| Daily-to-week aggregation | Must be explicit; preserve semantics |
| Custom periods | Require explicit start/end dates |
| Fiscal vs calendar | Do not silently mix |

---

## 9. Geo-unit semantics

**Supported types:** DMA, GMA-like unit, state/province, city/metro, postal cluster, sales territory, custom cluster, country/region aggregate.

| Rule | Behavior |
|------|----------|
| `geo_unit_id` | Stable over time |
| `geo_unit_type` | Declared or inferred with warning |
| Country/region aggregate | Not sufficient for randomized geo testing unless decomposed |
| Custom clusters | Require mapping documentation |
| Overlapping units | Blocking unless explicitly resolved |

---

## 10. KPI semantics

**KPI roles:** `primary_kpi`, `secondary_kpi`, `guardrail_kpi`, `diagnostic_kpi`

| Rule | Behavior |
|------|----------|
| Pre-period diagnostics | KPI must be non-post-treatment |
| Transformations | Must be explicit |
| Units | Stable over time |
| Incompatible definitions | Aggregating blocked |
| Low-volume units | Flagged in `UnitEligibilityReport` |
| Missingness | Separated from true zero outcome |

---

## 11. Spend semantics

**Spend types:** `total_media_spend`, `channel_spend`, `campaign_spend`, `incremental_spend`, `planned_spend`, `actual_spend`, `baseline_spend`

| Rule | Behavior |
|------|----------|
| Missing spend | **Not zero** unless explicitly declared imputation |
| Zero spend | Valid only when observed and semantically meaningful |
| Currency | Declared or inferred with warning |
| Grain alignment | Spend aligned to geo/date grain |
| Campaign vs total | Must not be mixed silently |
| Manipulation types | Go-dark, heavy-up, go-live depend on spend semantics |

---

## 12. Channel/campaign semantics

| Rule | Behavior |
|------|----------|
| Mapping stability | Channel/campaign mapping stable across time |
| Row semantics | One row maps to total, channel, campaign, or test-level spend — must be explicit |
| Multiple channels | Profiler summarizes by channel |
| Multiple campaigns/tests | Profiler summarizes by campaign/test |
| Ambiguous mapping | **Blocks** portfolio test feasibility claims |

---

## 13. Date/week/calendar semantics

**Defined windows:** `history_start_date`, `history_end_date`, `planning_window_start`, `planning_window_end`, `pre_period`, `washout_or_cooloff_period`, `excluded_periods`

| Rule | Behavior |
|------|----------|
| Pre-period diagnostics | Must not use treatment-period data |
| Planning-window spend | Planned or historical analog; must be labeled |
| Lagged KPI | Requires explicit lag/window definition |
| Promotions/holidays/blackouts | Flagged when available |

---

## 14. Treatment/planning-window semantics

Treatment assignment is **not** inferred from spend alone. Planning-window spend may be projected or historical analog. Pre-period end and treatment start must be explicitly separated. Post-treatment KPI rows must be excluded from pre-period profiler diagnostics.

---

## 15. Missingness and zero-vs-missing rules

| Rule | Required |
|------|----------|
| Missing KPI ≠ zero KPI | Yes |
| Missing spend ≠ zero spend | Yes |
| Zero KPI | Valid observed zero only |
| Zero spend | Valid observed zero only |
| Missing geo-date rows | Surfaced in `MissingnessReport` |
| Partial channel spend missingness | Surfaced |
| Imputed values | Labeled; cannot support final claims without future contract |

---

## 16. Duplicate and aggregation rules

| Rule | Behavior |
|------|----------|
| Duplicate geo-date-KPI rows | Blocking unless aggregation rule declared |
| Duplicate spend rows | Blocking unless aggregation rule declared |
| Aggregation | Must preserve grain and semantics |
| Summing spend | Allowed only for compatible spend rows |
| Summing KPI | Allowed only for additive KPI definitions |
| Rates/ratios | Require numerator/denominator or weighted aggregation rule |

---

## 17. Pre-period/post-period separation rules

Pre-period profiler diagnostics use only rows before treatment/planning-window start. Post-treatment data used for pre-period diagnostics is a **hard blocker**. `GeoTimeCoverageReport` must label pre-period vs post-period coverage separately.

---

## 18. Unit eligibility rules

Profiler diagnostics for:

- minimum historical coverage
- minimum KPI volume
- minimum spend coverage
- outlier units
- unstable units
- structural breaks
- missing geo/date rows
- incompatible spend mapping
- explicit exclusion flags

**Output fields:** `eligible_units`, `excluded_units`, `exclusion_reasons`, `usable_unit_count`, `coverage_by_unit` in `UnitEligibilityReport`.

---

## 19. Data-quality diagnostics

Emitted via `DataQualityWarningReport`, `MissingnessReport`, `DuplicateRowReport`, `AggregationReadinessReport`. Warnings do not authorize claims; blockers halt downstream feasibility diagnostics.

---

## 20. Profiler output report contracts

| Report | Purpose |
|--------|---------|
| `GeoKpiSpendDataProfileReport` | Top-level profile summary |
| `ColumnMappingReport` | Detected column mappings |
| `TimeGrainReport` | Detected/declared grain |
| `GeoUnitInventoryReport` | Unit inventory and types |
| `GeoTimeCoverageReport` | Coverage by geo and time |
| `KpiSummaryReport` | KPI volume, missingness, distribution |
| `SpendSummaryReport` | Spend coverage and totals |
| `ChannelCampaignMappingReport` | Channel/campaign structure |
| `MissingnessReport` | Missing value patterns |
| `DuplicateRowReport` | Duplicate detection |
| `AggregationReadinessReport` | Aggregation feasibility |
| `UnitEligibilityReport` | Eligible/excluded units |
| `DataQualityWarningReport` | Non-blocking warnings |
| `ProfilerFailureReport` | Hard failures and blockers |

---

## 21. Failure modes and blocking conditions

**Blocking examples:**

- No `geo_unit_id`
- No date/week column
- No KPI column or KPI name
- No spend column when spend feasibility requested
- Mixed grain without mapping
- Overlapping geo units without mapping
- Duplicate rows without aggregation rule
- Ambiguous zero vs missing semantics
- Post-treatment data for pre-period diagnostics
- Unknown channel/campaign mapping for portfolio planning
- Insufficient historical coverage

Emit `ProfilerFailureReport` with blocker codes; downstream agents must not proceed on blocked inputs.

---

## 22. LLM answerability boundaries

**LLM may:** summarize profiler reports; request missing data; explain insufficient data.

**LLM may not:**

- infer missing spend as zero
- infer geography eligibility without `UnitEligibilityReport`
- claim design feasibility from sample schema mode
- claim final feasibility from ballpark mode
- claim p-values/CIs from profiler outputs

---

## 23. Downstream dependencies

This contract is required by:

`EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001`, `GEO_KPI_SPEND_DATA_PROFILER_001`, `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001`, `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001`, `SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001`, `PORTFOLIO_TEST_TIERING_ENGINE_001`, `CANDIDATE_DESIGN_GENERATOR_001`, `SHARED_CONTROL_AND_MULTICELL_INFERENCE_CONTRACT_001`, `DESIGN_BASED_INFERENCE_TOOLING_CONTRACT_001`, `BALLPARK_FEASIBILITY_MODE_CONTRACT_001`, `LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001`, `MODEL_BASED_FALLBACK_ROUTER_001`.

---

## 24. Fixture/scenario test requirements

Required scenario coverage (minimum 20):

Full panel, sample schema, ballpark provisional-only, daily/weekly grain, mixed grain blocking, DMA/GMA/state/custom units, missing KPI blocking, missing spend blocking, missing spend not zero, zero spend valid, duplicate blocking, low-volume flagged, outlier flagged, ambiguous channel blocking, post-treatment exclusion, LLM no design feasibility from sample, LLM no final feasibility from ballpark.

---

## 25. Governance boundaries

All authorization flags remain **false**:

- `geo_kpi_spend_data_contract_runtime_authorized`
- `geo_kpi_spend_profiler_runtime_authorized`
- `data_cleaning_runtime_authorized`
- `unit_eligibility_runtime_authorized`
- `spend_feasibility_runtime_authorized`
- Planner, LLM, production design, p-values, CIs, selector/router, downstream flags

Profiler outputs **do not** authorize design feasibility, p-values, or CIs.

---

## 26. Revised roadmap placement

| # | Artifact | Status |
|---|----------|--------|
| 6 | `ROADMAP_IMPLEMENTATION_DETAIL_GAP_AUDIT_001` | ✅ |
| 7 | `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | ✅ This contract |
| 8 | `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` | Next |
| 9 | `GEO_KPI_SPEND_DATA_PROFILER_001` | After intake + this contract |

Five implementation-detail contracts remain pending after this artifact.

---

## 27. Recommended next artifact

`EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` — intake contracts that reference data availability modes defined here.

Profiler implementation (`GEO_KPI_SPEND_DATA_PROFILER_001`) should follow intake contract stabilization.

---

## 28. Final verdict

**`geo_kpi_spend_data_contract_profiler_spec_defined_no_runtime_authorization`**

Geo KPI/spend data contract and profiler specification defined. Accepted input modes, required fields, grain/geo/KPI/spend semantics, zero-vs-missing rules, blocking conditions, and 14 typed profiler reports documented. Sample schema and ballpark modes cannot support final design claims. All runtime authorization flags remain false.

| Output | Path |
|--------|------|
| Summary | `docs/track_d/archives/GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001_summary.json` |
| Harness | `panel_exp/validation/geo_kpi_spend_data_contract_and_profiler_spec_001.py` |
