# SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` |
| **Artifact type** | `spend_requirement_and_manipulation_feasibility_diagnostics` |
| **Status** | `completed` |
| **Base commit** | `08cb9bf` (Define spend requirement and manipulation feasibility contract) |
| **Scope** | `deterministic_spend_requirement_and_manipulation_feasibility_diagnostics` |
| **Final verdict** | `spend_requirement_and_manipulation_feasibility_diagnostics_implemented_no_power_design_roi_or_production_authorization` |

Deterministic spend requirement and manipulation feasibility diagnostics implementing `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001`. **No power/MDE computation, lift/ROI, budget optimization, candidate design, treatment/control assignment, estimator/inference authorization, MMM runtime calls, MMM calibration, LLM decisioning, or production authorization.**

---

## 2. Source files inspected

| File | Role |
|------|------|
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001` | Contract/amendment scope |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Profiler integration |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Upstream feasibility pattern |
| `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` | Prior contrast taxonomy |

---

## 3. Implementation scope

- `panel_exp/validation/spend_requirement_and_manipulation_feasibility_diagnostics_001.py`
- Five subreports per contract
- Consumes panel rows; profiles internally via `profile_geo_kpi_spend_data` when no profile supplied
- No MMM runtime, no power/MDE, no design/inference

---

## 4. Relationship to prior contract

Implements `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001`, which amends `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` with expanded scope: baseline inventory, response bridge, dosage/difference-in-policy, historical support, control contamination.

---

## 5. Public API

```python
evaluate_spend_requirement_and_manipulation_feasibility(
    input_data,
    config=None,
) -> SpendRequirementManipulationFeasibilityReport

evaluate_spend_manipulation_feasibility(...)  # alias
```

Deterministic, side-effect-free, no network, no randomness, no LLM, no MMM runtime.

---

## 6. Input modes and configurable columns

Supports `list[dict]`, pandas DataFrame (`to_dict("records")`), `GeoKpiSpendProfilerInput`.

`SpendRequirementManipulationFeasibilityConfig` includes `SpendDiagnosticsColumnMapping` for geo, date, spend, cell, channel, period role, planned/observed flags, and scalar planning/bridge fields.

---

## 7. Five subreport architecture

| Subreport | Purpose |
|-----------|---------|
| `SpendDataReadinessReport` | Grain, missing/zero/negative spend, planned/observed, windows |
| `BaselineSpendInventoryReport` | Baseline/historical spend summaries by level |
| `ResponseBridgeReport` | KPI MDE → advisory required spend delta |
| `ManipulationFeasibilityReport` | Candidate manipulation options and outcomes |
| `PlanningBoundaryReport` | Strict authorization flags |

---

## 8–17. Behavior summary

- **Spend readiness:** Missing ≠ zero; negative spend warned; sample-schema/ballpark provisional only
- **Baseline inventory:** Derived from explicit window or pre-period before `planned_test_start_date`; `max_reducible_spend` floored at zero
- **Response bridge:** Direct delta supplied, or `kpi_mde / expected_kpi_per_dollar` advisory; MMM/proxy/back-of-napkin flags advisory only
- **Manipulation feasibility:** GO_DARK, HEAVY_UP, GO_LIVE, BUDGET_REALLOCATION, DOSAGE_CONTRAST, DIFFERENCE_IN_POLICY as candidate options
- **Dosage/difference-in-policy:** First-class; estimand shift when control manipulated
- **Historical support:** Compares required spend to p95/max with configurable thresholds
- **Control contamination:** Flags when control cell manipulated; blocks standard go-dark interpretation
- **Planning boundary:** Only `ready_for_downstream_power_diagnostics` may be true when status allows

---

## 18. Claim boundaries

All design/inference/production flags false. `ready_for_downstream_power_diagnostics` allowed only when feasibility status is `READY_FOR_DOWNSTREAM_POWER_DIAGNOSTICS`.

---

## 19. Tests added

32 targeted tests in `tests/validation/test_spend_requirement_and_manipulation_feasibility_diagnostics_001.py` covering readiness, baseline, response bridge, manipulation options, control contamination, claim boundaries.

---

## 20. Validation results

`failed_scenarios: []` in summary JSON after smoke validation.

---

## 21. Known limitations

- Nonlinear MMM curve inversion not implemented; advisory metadata only
- No automatic cell assignment inference beyond provided `cell_role` fields
- Budget reallocation feasibility checks mapping presence, not full source/destination spend arithmetic

---

## 22. Recommended next artifact

**`POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001`**

---

## 23. Final verdict

**`spend_requirement_and_manipulation_feasibility_diagnostics_implemented_no_power_design_roi_or_production_authorization`**
