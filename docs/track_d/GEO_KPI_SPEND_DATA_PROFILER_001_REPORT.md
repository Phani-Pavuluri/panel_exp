# GEO_KPI_SPEND_DATA_PROFILER_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `GEO_KPI_SPEND_DATA_PROFILER_001` |
| **Artifact type** | `deterministic_geo_kpi_spend_data_profiler` |
| **Status** | `completed` |
| **Base commit** | `ea9178a` (Golden path acceptance contract follow-up) |
| **Implementation scope** | `deterministic_schema_coverage_profile_only` |
| **Final verdict** | `geo_kpi_spend_data_profiler_implemented_no_design_inference_or_production_authorization` |

First code-backed deterministic profiler after golden-path acceptance contract. Profiles geo KPI/spend input for schema readiness and coverage only. **No design feasibility, spend contrast, power, MDE, p-values, CIs, lift, ROI, method recommendation, portfolio tiering, MMM calibration, LLM decisioning, or production authorization.**

---

## 2. Source-of-truth files inspected

| File | Role |
|------|------|
| `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | Data contract and profiler spec |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Golden paths and profiler implementation notes |
| `PANEL_EXP_ARTIFACT_REGISTRY_AND_PROVENANCE_CONTRACT_001` | Artifact provenance patterns |
| `PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001` | Agent run envelope patterns |

---

## 3. Implementation scope

Deterministic, side-effect-free profiler module:

- `panel_exp/validation/geo_kpi_spend_data_profiler_001.py`
- Public API: `profile_geo_kpi_spend_data(input_data, config=None)`
- Input modes: `FULL_PANEL`, `SAMPLE_SCHEMA`, `BALLPARK`
- Output: `GeoKpiSpendDataProfileReport` with nested coverage/mapping reports
- No file IO, network, LLM, or randomness in core API

---

## 4. Public API

```python
profile_geo_kpi_spend_data(
    input_data: GeoKpiSpendProfilerInput | list[dict] | pandas.DataFrame,
    config: GeoKpiSpendProfilerConfig | None = None,
) -> GeoKpiSpendDataProfileReport
```

---

## 5. Input modes supported

| Mode | Input | Claim ceiling |
|------|-------|---------------|
| `FULL_PANEL` | Row-level geo/time/KPI(/spend) data | `READY_FOR_DOWNSTREAM_DIAGNOSTICS` when pass |
| `SAMPLE_SCHEMA` | Column names / sample schema only | `SCHEMA_ONLY`; no final claims |
| `BALLPARK` | Rough counts/volumes/duration | `PROVISIONAL_ONLY`; no final claims |

---

## 6. Output contracts/classes

`GeoKpiSpendProfilerInput`, `GeoKpiSpendProfilerConfig`, `GeoKpiSpendDataProfileReport`, `ColumnMappingReport`, `InputModeReport`, `TimeGrainReport`, `GeoUnitInventoryReport`, `GeoTimeCoverageReport`, `KpiCoverageReport`, `SpendCoverageReport`, `MissingnessReport`, `DuplicateRowReport`, `DataQualityIssue`, `ProfilerClaimBoundary`, `ProfilerStatus`, `ClaimBoundary`, `InputMode`, `DataQualitySeverity`, `TimeGrain`

---

## 7. Profiler statuses and claim boundaries

**Statuses:** `PASS`, `PASS_WITH_WARNINGS`, `PROVISIONAL`, `BLOCKED`

**Claim boundaries:** `SCHEMA_ONLY`, `PROFILE_ONLY`, `PROVISIONAL_ONLY`, `READY_FOR_DOWNSTREAM_DIAGNOSTICS`, `BLOCKED`

Unauthorized claims always false: design feasibility, spend contrast, power, MDE, p-values, CIs, lift, ROI, method recommendation, portfolio tiering, MMM calibration, production authorization, LLM decisioning.

---

## 8. Full-panel behavior

- Auto-detect or map geo, date, KPI, spend columns
- Block when required geo/date/KPI missing
- Block spend when `spend_coverage_requested` and spend column missing
- Report geo inventory, time coverage, KPI/spend coverage, missingness, duplicates
- `PASS` / `PASS_WITH_WARNINGS` may set `ready_for_downstream_diagnostics: true`

---

## 9. Sample-schema behavior

- Checklist for required column presence
- `SCHEMA_ONLY` claim boundary
- `ready_for_downstream_diagnostics: false`
- No final feasibility/design/inference claims

---

## 10. Ballpark behavior

- Accept rough planning inputs
- `PROVISIONAL_ONLY` claim boundary
- `provisional_planning_input_available: true`
- No final feasibility/design/inference claims

---

## 11. Missingness/zero handling

- Missing KPI ≠ zero KPI; missing spend ≠ zero spend
- `missingness_report.missing_*_treated_as_zero` always false
- `hidden_imputation_applied` always false
- Zero counts reported separately from missing counts

---

## 12. Duplicate handling

- Detect duplicate geo/time row pairs
- Block when duplicates exist without `aggregation_rule` in config
- `duplicate_rows_silently_aggregated` always false

---

## 13. Planned test date handling

When `planned_test_start_date` is set in config:

- Flag rows on/after start date unless `period_type` is `planned`/`future`/`planning`
- Emit `planned_test_start_overlap` warning

---

## 14. Lightweight KPI note

Rate/ratio column names produce diagnostic INFO note only. Additive KPIs preferred for future calibration. No default blocking for rate columns.

---

## 15. Lightweight geo note

Profile at provided geo level. DMAs in same state are valid distinct units. Single country aggregate does not imply randomized geo design readiness (INFO only).

---

## 16. Explicit non-goals

No spend contrast feasibility, design feasibility, power, MDE, p-values, CIs, lift, ROI, method recommendation, portfolio tiering, MMM calibration, production authorization, hidden imputation, fixture-specific branching, or LLM inference.

---

## 17. Tests added

`tests/validation/test_geo_kpi_spend_data_profiler_001.py` — 16 targeted tests covering full-panel pass, missing column blocks, sample/ballpark modes, missing vs zero spend, duplicates, planned start overlap, unauthorized claims, rate KPI note, DMA same-state, country aggregate note, no fixture branching.

---

## 18. Roadmap placement

| # | Artifact | Status |
|---|----------|--------|
| 11 | `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | ✅ |
| 12 | `GEO_KPI_SPEND_DATA_PROFILER_001` | ✅ This implementation |
| 13 | `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Next |

---

## 19. Governance/authorization boundary

Profiler implementation authorized for schema/coverage profiling only. All design/inference/production claim flags remain false in `ProfilerClaimBoundary`. Downstream diagnostics may consume profile reports when `ready_for_downstream_diagnostics` is true.

---

## 20. Recommended next artifact

`GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001`

---

## 21. Final verdict

**`geo_kpi_spend_data_profiler_implemented_no_design_inference_or_production_authorization`**

| Output | Path |
|--------|------|
| Module | `panel_exp/validation/geo_kpi_spend_data_profiler_001.py` |
| Summary | `docs/track_d/archives/GEO_KPI_SPEND_DATA_PROFILER_001_summary.json` |
