# POWER_MDE_DIAGNOSTICS_RUNTIME_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `POWER_MDE_DIAGNOSTICS_RUNTIME_001` |
| **Artifact type** | `power_mde_diagnostics_runtime` |
| **Status** | `completed` |
| **Scope** | `runtime_readiness_and_descriptive_sensitivity_only` |
| **Base commit** | `a626fcf` (Define power MDE diagnostics lane contract) |
| **Final verdict** | `power_mde_diagnostics_runtime_implemented_readiness_and_descriptive_sensitivity_only_no_power_mde_or_production_authorization` |

This artifact implements a **conservative deterministic runtime** for power/MDE readiness evaluation. It does not compute formal power, MDE, p-values, confidence intervals, lift, ROI, design generation, estimator selection, or production authorization.

---

## 2. Source files inspected

| File | Role |
|------|------|
| `POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001` | Lane contract this runtime implements |
| `POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001` | Spend handoff consumption rules |
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Upstream spend diagnostics |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Profiler status conventions |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Geo feasibility status conventions |

---

## 3. Implementation scope

**Implemented:**

- Public API `evaluate_power_mde_diagnostics()` (alias `evaluate_power_mde_readiness()`)
- Upstream gate validation (profiler, geo, spend handoff, cell structure, KPI/MDE, noise/history, estimand, method precheck)
- Descriptive KPI/noise history summaries (mean, median, std, variance, p10/p90, CV, missing/zero/negative counts)
- MDE representation validation (absolute vs relative, cell vs aggregate scope)
- Cell structure validation (detection only, no assignment)
- Spend compatibility preservation (handoff status, response bridge provenance, business-response risk)
- Estimand compatibility preservation (dosage/difference-in-policy, control contamination)
- Deterministic runtime mode selection
- Claim boundary enforcement

**Not implemented:**

- Formal power computation
- Formal MDE computation
- p-values, confidence intervals, lift, ROI
- Design generation or treatment/control assignment
- Estimator/inference selection
- MMM runtime calls or calibration
- Production authorization

---

## 4. Relationship to power/MDE lane contract

Implements `POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001` in conservative v1 form:

- All 10 runtime statuses supported
- All 6 runtime modes supported (plus `NOT_EVALUATED`)
- 8 readiness gates evaluated in `PowerMdeReadinessReport`
- `POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME` means inputs are sufficient for allowed diagnostic mode — **not powered**

---

## 5. Relationship to spend handoff contract

Consumes spend handoff metadata via config/input fields:

- `spend_handoff_status`, `required_spend_delta`, `required_spend_delta_source`
- Response bridge provenance (`mmm_advisory_used`, `proxy_response_used`, `back_of_napkin_assumption_used`)
- `business_response_risk`, `control_contamination_flags`, `candidate_manipulation_options`
- Spend-confirmed sensitivity requires ready handoff and known spend delta source

---

## 6. Public API

```python
evaluate_power_mde_diagnostics(input_data, config=None) -> PowerMdeDiagnosticsReport
evaluate_power_mde_readiness(...)  # alias
```

Deterministic, side-effect-free, no network, no randomness, no LLM, no MMM runtime.

---

## 7. Input modes and configurable columns

Supports:

- `list[dict]`
- `pandas.DataFrame` (via `to_dict("records")`)
- `PowerMdeDiagnosticsInput` dataclass
- `GeoKpiSpendProfilerInput`

`PowerMdeColumnMapping` defaults: `geo_unit_id`, `date`, `kpi_value`, `cell_id`, `cell_role`, `design_type`, `time_grain`, `period_role`.

Metadata fields (profiler/geo/spend handoff status, MDE targets, estimand flags) via `PowerMdeDiagnosticsConfig` or `PowerMdeDiagnosticsInput`.

---

## 8. Runtime statuses

| Status | Meaning |
|--------|---------|
| `POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME` | Conservative runtime can run in selected mode (not powered) |
| `POWER_MDE_READY_WITH_WARNINGS` | Ready with non-blocking warnings |
| `POWER_MDE_PROVISIONAL` | Exploratory or missing cell structure |
| `POWER_MDE_BLOCKED_BY_DATA_READINESS` | Profiler or KPI history blocked |
| `POWER_MDE_BLOCKED_BY_GEO_FEASIBILITY` | Geo feasibility blocked |
| `POWER_MDE_BLOCKED_BY_SPEND_HANDOFF` | Spend handoff blocked |
| `POWER_MDE_BLOCKED_BY_CELL_STRUCTURE` | Design-cell mode blocked by missing structure |
| `POWER_MDE_BLOCKED_BY_ESTIMAND_MISMATCH` | MDE representation conflict |
| `POWER_MDE_REQUIRES_METHOD_SUITABILITY_REVIEW` | Dosage/method review required |
| `POWER_MDE_NOT_EVALUATED` | Cannot evaluate |

---

## 9. Runtime modes

| Mode | When allowed |
|------|--------------|
| `KPI_ONLY_SENSITIVITY` | Valid KPI history; spend handoff missing/provisional |
| `SPEND_CONFIRMED_SENSITIVITY` | Spend handoff ready; required spend source preserved |
| `DESIGN_CELL_SENSITIVITY` | Cell structure present with interpretable roles |
| `DOSAGE_CONTRAST_SENSITIVITY` | Dosage/difference-in-policy flags set |
| `EXPLORATORY_BACK_OF_NAPKIN` | Back-of-napkin bridge; advisory only |
| `NOT_EVALUATED` | Upstream gates blocked |

---

## 10. Readiness report behavior

`PowerMdeReadinessReport` evaluates eight gates in order. Profiler or KPI history blocked → runtime blocked. Spend handoff blocked → spend-confirmed mode blocked. Missing cell structure → provisional for KPI-only. Method suitability review required → status `POWER_MDE_REQUIRES_METHOD_SUITABILITY_REVIEW`.

---

## 11. Noise/history report behavior

`PowerMdeNoiseHistoryReport` computes descriptive summaries only:

- Row/geo/period counts, missing/zero/negative KPI counts
- Mean, median, std, variance, p10, p90, coefficient of variation
- Minimum pre-period length check
- Time/geo balance status, IQR outlier summary

Missing KPI is not treated as zero. Descriptive variance is not power or MDE.

---

## 12. MDE representation behavior

`PowerMdeRepresentationReport` validates:

- KPI unit preservation
- Absolute vs relative MDE presence and conflicts
- Cell-level vs aggregate scope
- Baseline KPI level for relative MDE
- Duration-specific MDE flag

No final MDE is computed.

---

## 13. Cell structure report behavior

`PowerMdeCellStructureReport` detects cell IDs, roles, and design type concepts. Supports inference of single treated/control, multi-cell, common control, matched pair, dosage contrast, difference-in-policy, budget reallocation. Does not generate cells or assign treatment/control.

---

## 14. Spend compatibility behavior

`PowerMdeSpendCompatibilityReport` preserves spend handoff inputs and provenance. Spend feasibility is not power. Spend-confirmed mode requires ready handoff and non-unknown spend delta source.

---

## 15. Estimand compatibility behavior

`PowerMdeEstimandCompatibilityReport` preserves dosage/difference-in-policy flags and control contamination. Blocks standard go-dark interpretation when contamination or dosage estimand applies. Method suitability review prevents estimator/inference readiness claims.

---

## 16. Claim boundary behavior

`PowerMdeClaimBoundaryReport` always enforces:

- `power_computed: false`, `mde_computed: false`, `p_value_computed: false`, etc.
- Positive: `runtime_power_mde_diagnostics_implemented`, `readiness_diagnostics_implemented`, `descriptive_noise_summary_implemented`

---

## 17. Mode selection rules

Deterministic priority:

1. Blocked profiler/geo/KPI history → `NOT_EVALUATED`
2. Back-of-napkin → `EXPLORATORY_BACK_OF_NAPKIN`
3. Dosage/difference-in-policy → `DOSAGE_CONTRAST_SENSITIVITY`
4. Cell structure present → `DESIGN_CELL_SENSITIVITY`
5. Spend handoff ready → `SPEND_CONFIRMED_SENSITIVITY`
6. KPI history valid → `KPI_ONLY_SENSITIVITY`

---

## 18. Dosage/difference-in-policy behavior

Routes to `DOSAGE_CONTRAST_SENSITIVITY` when dosage or difference-in-policy flags are set. Requires method-suitability review status before estimator claims. Control contamination blocks standard business-as-usual control assumptions.

---

## 19. Tests added

`tests/validation/test_power_mde_diagnostics_runtime_001.py` — 39 targeted tests covering upstream gates, KPI/noise readiness, MDE representation, cell structure, spend compatibility, dosage/estimand, claim boundaries. No fixture-specific branching.

---

## 20. Validation results

See summary JSON `failed_scenarios: []` after harness run.

---

## 21. Known limitations

- v1 conservative: descriptive noise only, no formal sensitivity formulas
- Upstream reports consumed via status metadata fields, not full report object embedding
- Cell structure detection is heuristic from supplied metadata
- No integration with live profiler/geo/spend diagnostic auto-chaining in v1

---

## 22. Recommended next artifact

**`DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001`**

**Alternative:** `POWER_MDE_FORMULA_AND_SIMULATION_METHOD_REGISTRY_001`

---

## 23. Final verdict

**`power_mde_diagnostics_runtime_implemented_readiness_and_descriptive_sensitivity_only_no_power_mde_or_production_authorization`**

Conservative power/MDE readiness runtime implemented. Upstream gates, descriptive noise summaries, MDE representation validation, cell structure validation, spend/estimand compatibility preservation, and claim boundaries enforced. No formal power/MDE or production authorization.
