# GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001` |
| **Artifact type** | `geox_final_test_results_spend_roi_readiness_contract` |
| **Lane** | **Lane B — Final trusted readout / spend / ROI readiness** |
| **Status** | `completed` |
| **Base commit** | `96326d9` |
| **Scope** | `spend_roi_readiness_contract_defined_no_runtime_or_claim_authorization` |
| **Final verdict** | `spend_roi_readiness_contract_defined_no_runtime_or_claim_authorization` |
| **Recommended next** | `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` |
| **Return to Lane A after** | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001` |

**Depends on:**

- `FINAL_TEST_RESULTS_EXISTING_ARTIFACT_REUSE_AUDIT_001`
- `GEOX_READOUT_DATAFLOW_AND_SPEND_EXTRACTION_PROCESS_AUDIT_001`
- `TRUSTED_READOUT_REPORT_CONTRACT_001` / `TRUSTED_READOUT_REPORT_RUNTIME_001`
- `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001`
- `estimator_readout_adapter_001.py`
- `CLAIM_AUTHORIZATION_RUNTIME_001`
- `GEO_KPI_SPEND_DATA_PROFILER_001`
- `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001`
- `TRACK_B_ESTIMAND_REGISTRY_001`
- `INFERENCE_READOUT_SEMANTICS_001`

---

## 2. Why this contract exists

Discovery audits established that the platform already has:

- **Final readout/report assembly** — `TRUSTED_READOUT_REPORT_*` assembles governed trusted readout packets from claim authorization and upstream evidence.
- **Estimator execution outputs** — `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001` produces `effect_estimate_report`, `uncertainty_report`, and `claim_boundary_report`.
- **Claim authorization** — `CLAIM_AUTHORIZATION_RUNTIME_001` is the sole package-level owner for what may be claimed.
- **Planning spend profiling** — `GEO_KPI_SPEND_DATA_PROFILER_001` and `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` validate schema and derive **pre-period** baseline spend and planning `required_spend_delta`.

The **missing piece** is a governed contract for **post-test actual spend** and **observed `spend_delta` readiness** so final trusted readouts can expose cost-per, ROAS, and ROI efficiency metrics without duplicating owners or building new ingestion systems.

This contract defines readiness rules only. It does not implement runtime, compute metrics, or authorize claims.

---

## 3. Explicit reuse decision

### Reuse / extend existing owners

| Owner | Action |
|-------|--------|
| `TRUSTED_READOUT_REPORT_*` | Extend with optional spend/efficiency readiness fields (future) |
| `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001` | Consume `effect_estimate_report` / `delta_mu` |
| `estimator_readout_adapter_001.py` | Consume governed readout values |
| `CLAIM_AUTHORIZATION_RUNTIME_001` | Delegate all claim-status decisions |
| `GEO_KPI_SPEND_DATA_*` | Reuse schema, column mapping, currency/grain semantics |
| `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Reuse baseline window and aggregation primitives |
| `TRACK_B_ESTIMAND_REGISTRY_001` | Bind ROI/ROAS estimand IDs |
| `INFERENCE_READOUT_SEMANTICS_001` | Bind observed/counterfactual/lift semantics |

### Does not create

- No new spend ingestion system
- No new final-results module
- No new claim authorization runtime
- No new ROI calculator runtime

**Reuse verdict (from discovery):** `EXTEND_EXISTING_ARTIFACT`  
**Process verdict (from discovery):** `NEEDS_EXISTING_MODULE_REUSE`

---

## 4. Ownership split

| Responsibility | Owner | Existing artifact/module | This contract action |
|---|---|---|---|
| User asks for readout | MIP | Future orchestration / intake | Requires KPI; optionally spend for efficiency metrics |
| KPI/spend upload or source resolution | MIP | `EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001` | Produces dataset refs; package validates rows |
| Schema profiling | panel_exp | `GEO_KPI_SPEND_DATA_PROFILER_001` | Reuse column mapping and readiness gates |
| Planning spend feasibility | panel_exp | `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` | Reuse for baseline/planning; not post-test owner |
| Estimator execution | panel_exp | `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001` | Consume execution outputs |
| Estimator readout adapter | panel_exp | `estimator_readout_adapter_001.py` | Consume governed readout evidence |
| Post-test spend evidence readiness | panel_exp | **Gap** | **Define `PostTestSpendEvidence` contract** |
| Trusted report assembly | panel_exp | `TRUSTED_READOUT_REPORT_*` | Extend with readiness summary fields (future) |
| Claim status | panel_exp | `CLAIM_AUTHORIZATION_RUNTIME_001` | Delegate; no duplication |
| User explanation | MIP | Future `LLM_REPORT_GROUNDING_*` | Consume readiness statuses and blocking reasons |

---

## 5. Readout-time input requirements

### Required for all readouts

| Field group | Fields |
|-------------|--------|
| Experiment identity | `experiment_id` |
| Test window | `test_start_date`, `test_end_date` |
| Post period | `post_period_start`, `post_period_end` |
| Pre period (if estimator requires) | `pre_period_start`, `pre_period_end` |
| Assignment | Geo/unit assignment; treatment/control/cell assignment (`assignment_artifact` or equivalent) |
| KPI dataset | `kpi_dataset_ref` (upload handle or resolved row bundle reference) |
| KPI columns | `kpi_date_column`, `kpi_geo_column`, `kpi_metric_column` |
| KPI metadata | `kpi_unit`, `kpi_name` or declared metric |
| Estimator identity | `estimator_id`, `inference_id`, `instrument_id` (as applicable) |

### Optional — required for spend-derived efficiency metrics

| Field group | Fields |
|-------------|--------|
| Spend dataset | `spend_dataset_ref` or `spend_evidence_ref` (upstream typed evidence reference) |
| Spend columns | `spend_date_column`, `spend_geo_column` or geo mapping, `spend_amount_column` |
| Spend scope | `spend_cell_column`, `spend_campaign_column`, `spend_channel_column`, `spend_platform_column` (when applicable) |
| Spend metadata | `currency`, `spend_source`, `spend_scope`, `spend_window_start`, `spend_window_end` |
| Baseline policy | `spend_baseline_definition`, `experiment_type` / `contrast_type` |

### Optional — required for revenue/profit ROI when KPI is not already revenue

| Field group | Fields |
|-------------|--------|
| Value mapping | `value_per_incremental_kpi`, `revenue_mapping`, `margin_or_profit_mapping` |
| Value metadata | `value_source`, `value_currency`, `value_window_compatible` (must align with post period) |

**Rule:** Missing spend inputs must not block KPI-only readouts (`NOT_REQUESTED`). Missing value mapping must block profit ROI even when `spend_delta` is ready.

---

## 6. Post-test spend evidence contract

### Conceptual object: `PostTestSpendEvidence`

| Field | Type / semantics |
|-------|------------------|
| `experiment_id` | Stable experiment identifier |
| `source_artifact` | Producing artifact ID (future adapter) |
| `source_dataset_ref` | MIP-resolved or upload dataset reference |
| `source_lineage` | Provenance manifest (profiler report ID, column mapping hash) |
| `spend_date_column` | Mapped date column name |
| `spend_geo_column` | Mapped geo column name |
| `spend_amount_column` | Mapped spend amount column |
| `spend_currency` | Declared or inferred single currency |
| `spend_scope` | `total`, `channel`, `campaign`, `cell`, or declared composite |
| `spend_window_start` | Inclusive post-test window start |
| `spend_window_end` | Inclusive post-test window end |
| `experiment_geo_scope` | Geo units in experiment scope (from assignment) |
| `treatment_cell_scope` | Treatment cell IDs included |
| `channel_scope` | Channel filter if applicable |
| `campaign_scope` | Campaign filter if applicable |
| `actual_treatment_spend` | Aggregated observed treatment spend in window |
| `actual_control_or_baseline_spend` | Aggregated control or BAU-equivalent spend |
| `counterfactual_or_bau_spend` | Validated BAU/counterfactual spend reference used in delta |
| `spend_delta` | Observed spend contrast per `spend_delta_definition` |
| `spend_delta_definition` | Named formula ID (see §9) |
| `spend_baseline_policy` | Experiment-type baseline policy label |
| `spend_aggregation_level` | `overall`, `geo`, `cell`, `channel`, `geo_x_channel`, etc. |
| `spend_allocation_method` | Sum rule; must be declared when joining assignment |
| `readiness_status` | Enum from §11 |
| `blocking_reasons` | Tuple of machine-readable blocker codes |
| `warnings` | Non-blocking advisory strings |

**Invariant:** Planning `required_spend_delta` from spend feasibility diagnostics is **not** interchangeable with observed `spend_delta` unless explicitly bridged and labeled in `source_lineage`.

---

## 7. Post-test spend extraction process

Future runtime (`GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001`) must implement this deterministic process:

1. **Resolve spend source** — accept `spend_dataset_ref` or upstream evidence reference; MIP may fetch rows; package validates normalized panel.
2. **Reuse profiler column mapping** — call `profile_geo_kpi_spend_data()` or consume prior `GeoKpiSpendDataProfileReport` from lineage.
3. **Validate spend schema** — required columns present; missing spend ≠ zero; currency declared or flagged.
4. **Map date column** — use `SpendDiagnosticsColumnMapping` or profiler `ColumnMappingReport`.
5. **Filter rows to test/post-period window** — `post_period_start` ≤ date ≤ `post_period_end` (or `test_start_date`/`test_end_date` when post period not separately declared).
6. **Filter to experiment geo scope** — restrict to geos in `assignment_artifact.unit_allocations`.
7. **Join treatment/control/cell assignment** — map geo → cell role; reject silent assignment inference from spend alone.
8. **Group by required scope** — geo/time/cell/channel/campaign per `spend_scope` and experiment type.
9. **Aggregate actual treatment spend** — sum compatible spend rows for treatment scope.
10. **Compute or validate baseline / counterfactual spend** — per experiment-type policy (§9); may reference planning baseline only when labeled `PLANNING_BASELINE_BRIDGE_ADVISORY`.
11. **Derive `spend_delta`** — apply named `spend_delta_definition`; emit formula ID in evidence.
12. **Emit `PostTestSpendEvidence`** — with `readiness_status`, blockers, warnings.
13. **Pass readiness into `TRUSTED_READOUT_REPORT_*`** — attach as optional evidence bundle input; redact efficiency sections when blocked.

---

## 8. Required reuse of primitives

Future runtime **must**:

- Reuse `_weekly_spend_totals()` from `spend_requirement_and_manipulation_feasibility_diagnostics_001.py` for windowed aggregation where grain is compatible.
- Reuse or adapt `_compute_achieved_contrast()` from `design_scenario_policy_feasibility_runtime_001.py` for experiment-type `spend_delta` formulas where compatible.
- Reference `SpendDiagnosticsColumnMapping` field names rather than inventing parallel column contracts.
- **Not** copy/paste duplicate contrast formulas without citing the owning module and bridging planning vs observed semantics.

**Planning-only bridge rule:** When `_derive_baseline_window()` or design-scenario `proposed_spend` values are used, evidence must set `spend_baseline_policy=PLANNING_BASELINE_BRIDGE_ADVISORY` and emit warning `PLANNING_SPEND_NOT_OBSERVED_POST_TEST`.

**Known gap (documented):** `test_window_start` / `test_window_end` in spend diagnostics config today only set `test_window_status`; future adapter must pass test window into `_weekly_spend_totals()`.

---

## 9. Spend baseline policy by experiment type

| Experiment type | Required baseline | spend_delta formula | Required fields | Blocked when |
|---|---|---|---|---|
| **go_dark** | Planned/BAU spend or avoided spend baseline | `BAU_spend − actual_go_dark_spend` (avoided spend) | BAU/planned baseline, actual treatment spend in window | Missing BAU or actual; manipulated BAU control without estimand shift |
| **heavy_up** | Planned BAU / control-equivalent baseline | `actual_heavy_up_spend − BAU_spend` | Actual treatment spend, BAU baseline | Missing BAU or actual |
| **holdout** | Exposed vs holdout/control-equivalent spend | `exposed_spend − control_equiv_spend` | Exposed and control-equivalent spend by scope | Missing control-equivalent; holdout estimand not declared (INV-023) |
| **dosage** | Baseline/control dosage cell spend | `spend_high_cell − spend_baseline_cell` | Per-cell spend, baseline cell ID | Missing baseline cell; dosage estimand not declared |
| **reallocation** | Added and removed spend scopes (source/destination) | `added_spend − removed_spend` with explicit scope | `budget_source_channel`, `budget_destination_channel` or equivalent mapping | Missing offset scope; `BUDGET_REALLOCATION_MAPPING_INCOMPLETE` |

**Alignment with existing planning formulas:**

- Go-dark planning: `comparison_proposed − treatment_proposed` (`_compute_achieved_contrast`, `GO_DARK_VS_BAU`)
- Heavy-up planning: `treatment_proposed − comparison_proposed` (`HEAVY_UP_VS_BAU`)
- Dosage: `high − low` (`DOSAGE_LOW_VS_HIGH`)
- Reallocation: source/destination policy rules (`BUDGET_REALLOCATION`)

Post-test adapter must apply the **observed** analog of these formulas on filtered actual spend, not planning `proposed_spend`, unless explicitly bridged.

---

## 10. Metric readiness rules

| Output | Formula | Required inputs | Readiness status if missing |
|---|---|---|---|
| **absolute_increment** | `delta_mu` | Governed `delta_mu` from execution/adapter | `BLOCKED_MISSING_DELTA_MU` |
| **lift_pct** | `delta_mu / counterfactual_kpi` | `delta_mu`, counterfactual KPI baseline | `BLOCKED_MISSING_COUNTERFACTUAL` |
| **cost_per_incremental_kpi** | `spend_delta / delta_mu` | `spend_delta`, `delta_mu` (non-zero) | `BLOCKED_MISSING_SPEND_DELTA` or `BLOCKED_MISSING_DELTA_MU` |
| **incremental_revenue** | `delta_mu × value_per_kpi` OR revenue `delta_mu` | `delta_mu`, value mapping OR revenue KPI | `BLOCKED_MISSING_VALUE_MAPPING` |
| **ROAS** | `incremental_revenue / spend_delta` | Incremental revenue, `spend_delta` | `BLOCKED_MISSING_REVENUE_OR_SPEND` |
| **profit_ROI** | `incremental_profit / spend_delta` | Profit/margin mapping, `spend_delta` | `BLOCKED_MISSING_MARGIN_MAPPING` |

**Claim separation:** Numeric readiness ≠ claim authorization. Efficiency metrics may reach `READY` or `PARTIAL_DIAGNOSTIC_ONLY` while `roi_claim_authorized` remains false.

---

## 11. Readiness status enum

| Status | Meaning |
|--------|---------|
| `READY` | All required inputs present; metric may be computed by future runtime |
| `NOT_REQUESTED` | User/template did not request spend-derived metrics |
| `PARTIAL_DIAGNOSTIC_ONLY` | Some fields present; efficiency metrics diagnostic-only; claims blocked |
| `BLOCKED_MISSING_KPI` | KPI dataset or columns missing |
| `BLOCKED_MISSING_COUNTERFACTUAL` | Counterfactual baseline missing for lift_pct |
| `BLOCKED_MISSING_DELTA_MU` | Governed effect estimate missing |
| `BLOCKED_MISSING_SPEND_SOURCE` | No spend dataset or evidence reference |
| `BLOCKED_MISSING_POST_TEST_SPEND` | Spend rows absent in post-test window |
| `BLOCKED_MISSING_SPEND_DELTA` | Cannot derive spend_delta |
| `BLOCKED_MISSING_SPEND_BASELINE` | Baseline/BAU spend missing for experiment type |
| `BLOCKED_SPEND_WINDOW_MISMATCH` | Spend window incompatible with post period |
| `BLOCKED_SPEND_GEO_SCOPE_MISMATCH` | Spend geos do not cover assigned units |
| `BLOCKED_SPEND_CELL_SCOPE_MISMATCH` | Cell assignment join failed |
| `BLOCKED_CURRENCY_MISMATCH` | Multiple currencies without mapping |
| `BLOCKED_MISSING_VALUE_MAPPING` | Revenue/value mapping missing |
| `BLOCKED_MISSING_MARGIN_MAPPING` | Profit/margin mapping missing |
| `BLOCKED_UNSUPPORTED_EXPERIMENT_TYPE` | Experiment type not in §9 table |
| `BLOCKED_CLAIM_NOT_AUTHORIZED` | Metric ready but claim type blocked by claim authorization |

---

## 12. Trusted readout extension points

Future extension to `TRUSTED_READOUT_REPORT_*` (contract amendment + runtime input binding):

| Field | Purpose |
|-------|---------|
| `spend_readiness_summary` | High-level readiness enum + metric list |
| `post_test_spend_evidence` | Embedded or referenced `PostTestSpendEvidence` |
| `efficiency_metric_readiness` | Per-metric readiness map (`cost_per`, `ROAS`, `profit_ROI`, etc.) |
| `blocked_efficiency_metrics` | Metrics blocked with reason codes |
| `diagnostic_efficiency_metrics` | Metrics allowed diagnostic-only |
| `roi_claim_authorization_status` | Pass-through from `CLAIM_AUTHORIZATION_RUNTIME_001` (read-only) |
| `spend_lineage` | Profiler + adapter provenance IDs |
| `spend_warnings` | Advisory flags (planning bridge, mixed planned/observed, etc.) |

**Redaction rule:** When `readiness_status` is not `READY`, trusted readout must redact or block efficiency sections per existing `TRUSTED_READOUT_REPORT` redaction policy — same pattern as uncertainty/ROI caveat codes (`NO_ROI_CLAIM`, etc.).

---

## 13. Claim authorization delegation

This contract:

- **Does not** authorize `ROI_CLAIM`, `ROAS_CLAIM`, `INCREMENTAL_LIFT_CLAIM` / business lift, or `TRUSTED_BUSINESS_RECOMMENDATION` / decision recommendation.
- Allows derived metrics to be **numerically ready** while **claim-blocked**.
- Delegates all claim status to `CLAIM_AUTHORIZATION_RUNTIME_001` — the only package-level claim-status owner.
- Leaves TrustReport / F-DECISION / MIP-level interpretation outside this contract.

**Trusted readout handoff:** Final numeric values and readiness statuses feed claim authorization; claim authorization feeds trusted readout sections. No duplicate claim logic in spend readiness.

---

## 14. MIP orchestration requirements

MIP must:

1. **Require KPI dataset** for any readout request.
2. **Require spend dataset/source** only when user requests ROI/ROAS/cost-per or readout template includes spend-derived efficiency metrics.
3. **Require value/margin mapping** when ROI/ROAS requested and KPI is not already revenue/profit.
4. **Ask user or return partial-readout explanation** when required inputs missing — do not silently omit efficiency metrics.
5. **Not compute `spend_delta`** unless MIP owns upstream data transformation; prefer passing normalized spend rows to package adapter for validation.
6. **Validate any MIP-supplied spend evidence** through future package adapter before attaching to trusted readout.

**Suggested missing-input responses** (orchestration layer):

| Condition | MIP response |
|-----------|--------------|
| No KPI panel | Request geo-level KPI history upload or data-source connection |
| No assignment | Request treatment/control assignment artifact |
| No test window | Request test start/end dates |
| Efficiency requested, no spend | Request spend panel or explain KPI-only partial readout |
| ROI requested, no value mapping | Request revenue-per-KPI or margin mapping |
| Claim blocked | Explain claim authorization status; do not present as authorized ROI |

---

## 15. Runtime follow-up plan

**Next artifact:** `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001`

| Responsibility | Owner |
|----------------|-------|
| Reuse profiler column mapping | Adapter runtime |
| Reuse `_weekly_spend_totals()` | Adapter runtime |
| Reuse/adapt `_compute_achieved_contrast()` | Adapter runtime |
| Emit `PostTestSpendEvidence` | Adapter runtime |
| Extend `TRUSTED_READOUT_REPORT_RUNTIME_001` inputs | Trusted readout runtime (separate PR) |
| Claim authorization | **No duplication** — consume existing runtime only |

---

## 16. Non-goals

Confirmed for this artifact:

- [x] No runtime implemented
- [x] No spend ingestion system created
- [x] No new final-results module created
- [x] No ROI calculator runtime created
- [x] No claim authorization duplicated
- [x] No ROI/ROAS/business lift claim authorized
- [x] No production/decision readiness granted
- [x] No estimator behavior changed
- [x] No method/instrument promotion or catalog unblock

---

## 17. Validation results

| Check | Result |
|-------|--------|
| Contract document | `docs/track_d/GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001.md` |
| Summary JSON | `docs/track_d/archives/GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001_summary.json` |
| Governance tests | `tests/governance/test_geox_final_test_results_spend_roi_readiness_contract_001.py` |
| JSON validity | `python -m json.tool` on summary |
| Forbidden flags | All false in summary JSON |
| Capability flags | All required true flags set in summary JSON |

**Positive flags (summary JSON):**

- `spend_roi_readiness_contract_completed`: true
- `existing_readout_stack_reused`: true
- `no_new_final_results_module`: true
- `no_new_spend_ingestion_system`: true
- `post_test_spend_evidence_defined`: true
- `spend_delta_readiness_defined`: true
- `roi_roas_readiness_defined`: true
- `trusted_readout_extension_points_defined`: true
- `claim_authorization_delegated`: true
- `mip_orchestration_requirements_defined`: true
- `runtime_followup_defined`: true

**Forbidden flags (must remain false):** `runtime_implemented`, `spend_ingestion_system_created`, `final_results_module_created`, `roi_calculator_runtime_created`, `claim_authorization_duplicated`, `roi_claim_authorized`, `roas_claim_authorized`, `business_lift_claim_authorized`, `decision_recommendation_authorized`, `production_readout_authorized`, `method_promoted`, `instrument_promoted`, `catalog_unblocked`, `production_compatibility_authorized`, `inference_implemented`, `estimator_implemented`, `simulations_implemented`, `mmm_runtime_calls_implemented`, `llm_decisioning_authorized`
