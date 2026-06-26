# GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` |
| **Artifact type** | `deterministic_geo_unit_market_feasibility_diagnostics` |
| **Status** | `completed` |
| **Base commit** | `7b992f6` (Implement geo KPI spend data profiler) |
| **Implementation scope** | `deterministic_unit_market_coverage_diagnostics_only` |
| **Final verdict** | `geo_unit_market_feasibility_diagnostics_implemented_no_design_inference_or_production_authorization` |

Deterministic geo unit and market feasibility diagnostics consuming `GeoKpiSpendDataProfileReport`. **No final experiment feasibility, candidate design, treatment/control assignment, spend contrast, power, MDE, p-values, CIs, lift, ROI, method recommendation, portfolio tiering, MMM calibration, LLM decisioning, or production authorization.**

---

## 2. Source-of-truth files inspected

| File | Role |
|------|------|
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Profiler implementation and profile report contract |
| `GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001` | Data contract and profiler spec |
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Golden paths and profiler notes |

---

## 3. Implementation scope

- `panel_exp/validation/geo_unit_market_feasibility_diagnostics_001.py`
- Consumes profiler output; does not duplicate profiler logic
- Optional helper `evaluate_geo_unit_market_feasibility_from_panel` routes through profiler first

---

## 4. Public API

```python
evaluate_geo_unit_market_feasibility(
    profile_report: GeoKpiSpendDataProfileReport,
    config: GeoUnitMarketFeasibilityConfig | None = None,
) -> GeoUnitMarketFeasibilityReport

evaluate_geo_unit_market_feasibility_from_panel(
    input_data, profiler_config=None, feasibility_config=None
) -> GeoUnitMarketFeasibilityReport
```

---

## 5. Relationship to GEO_KPI_SPEND_DATA_PROFILER_001

Preferred input is `GeoKpiSpendDataProfileReport` from `profile_geo_kpi_spend_data`. Diagnostics respect profiler claim boundaries and never upgrade blocked, sample-schema, or ballpark inputs. Raw panel data may be passed only via `evaluate_geo_unit_market_feasibility_from_panel`, which calls the profiler internally.

---

## 6. Input expectations

- **Required:** `GeoKpiSpendDataProfileReport`
- **Optional config:** `GeoUnitMarketFeasibilityConfig` with configurable thresholds and optional `rows_for_coverage_balance` for geo/time balance diagnostics

---

## 7. Output contracts/classes

`GeoUnitMarketFeasibilityConfig`, `GeoUnitMarketFeasibilityReport`, `GeoUnitFeasibilityStatus`, `GeoMarketFeasibilityStatus`, `GeoUnitEligibilitySummary`, `GeoCoverageBalanceReport`, `GeoHistoryAvailabilityReport`, `GeoMarketStructureReport`, `GeoUnitFeasibilityIssue`, `GeoUnitFeasibilitySeverity`, `GeoUnitMarketClaimBoundaryReport`

---

## 8. Statuses and claim boundaries

**Feasibility statuses:** `READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS`, `PASS_WITH_WARNINGS`, `PROVISIONAL`, `BLOCKED`

**Claim boundaries:** `UNIT_MARKET_DIAGNOSTIC_ONLY`, `READY_FOR_DOWNSTREAM_DESIGN_DIAGNOSTICS`, `PROVISIONAL_ONLY`, `BLOCKED`

Allowed positive claim: `ready_for_downstream_design_diagnostics` only when full-panel profiler pass and unit/coverage thresholds met.

---

## 9. Unit inventory diagnostics

Reports geo unit count, eligible count, missing geo count, sample units, geo unit type. Configurable thresholds:

- `min_geo_units_for_downstream_diagnostics` (default 2)
- `recommended_min_geo_units_warning` (default 10)

Blocks one geo unit for randomized geo planning readiness. Does not claim final experiment feasibility.

---

## 10. Historical coverage diagnostics

Reports time period count, historical period count, coverage completeness ratio, missing geo/time signals. Configurable thresholds:

- `min_time_periods_for_downstream_diagnostics` (default 4)
- `recommended_min_time_periods_warning` (default 8)

---

## 11. Geo/time balance diagnostics

When `rows_for_coverage_balance` provided, detects material coverage imbalance across geos and missing geo/time KPI cells. Does not run matching or design algorithms.

---

## 12. Market structure notes

Reports provided geo level, unique market count, single-aggregate warnings. DMAs in same state accepted when geo IDs distinct. Country aggregate single unit does not imply randomized geo readiness. Custom clusters accepted at provided geo level without hierarchy resolution.

---

## 13. Eligibility summary rules

Units eligible for downstream diagnostics when geo id present, KPI coverage present, time coverage present, not fully missing. Does not decide treatment/control assignment, matchability, or final design feasibility.

---

## 14. Explicit non-goals

No final experiment feasibility, candidate design, treatment/control assignment, spend contrast feasibility, power, MDE, p-values, CIs, lift, ROI, method recommendation, portfolio tiering, MMM calibration, production authorization, SCM/TBR/DID/matching, or fixture-specific branching.

---

## 15. Tests added

`tests/validation/test_geo_unit_market_feasibility_diagnostics_001.py` — 17 targeted tests.

---

## 16. Roadmap placement

| # | Artifact | Status |
|---|----------|--------|
| 12 | `GEO_KPI_SPEND_DATA_PROFILER_001` | ✅ |
| 13 | `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | ✅ This implementation |
| 14 | `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` | Next |

---

## 17. Governance/authorization boundary

All design/inference/production claim flags remain false in `GeoUnitMarketClaimBoundaryReport`. Diagnostics may set `ready_for_downstream_design_diagnostics` only when profiler and unit/coverage gates pass.

---

## 18. Recommended next artifact

`SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001`

---

## 19. Final verdict

**`geo_unit_market_feasibility_diagnostics_implemented_no_design_inference_or_production_authorization`**

| Output | Path |
|--------|------|
| Module | `panel_exp/validation/geo_unit_market_feasibility_diagnostics_001.py` |
| Summary | `docs/track_d/archives/GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001_summary.json` |
