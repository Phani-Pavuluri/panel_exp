# GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001

## Artifact metadata

| Field | Value |
|-------|-------|
| **artifact_id** | `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` |
| **artifact_type** | `geox_post_test_spend_readiness_adapter_runtime` |
| **lane** | Lane B — Final trusted readout / spend / ROI readiness |
| **status** | completed |
| **scope** | `post_test_spend_readiness_adapter_runtime_no_claim_authorization_or_roi_calculator` |
| **final_verdict** | `post_test_spend_readiness_adapter_runtime_completed_no_claim_authorization_or_roi_calculator` |
| **module** | `panel_exp/validation/post_test_spend_readiness_adapter_runtime_001.py` |
| **recommended_next_artifact** | `GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001` |
| **return_to_lane_a_after** | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001` |

## Why this runtime exists

`GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001` defines `PostTestSpendEvidence` and spend_delta readiness rules, but no executable path existed to derive observed post-test spend from profiled spend rows. This runtime is the first Lane B step that turns the contract into deterministic behavior without creating a new spend ingestion system, final-results module, or ROI calculator.

## Contract dependency

Depends on:

- `FINAL_TEST_RESULTS_EXISTING_ARTIFACT_REUSE_AUDIT_001`
- `GEOX_READOUT_DATAFLOW_AND_SPEND_EXTRACTION_PROCESS_AUDIT_001`
- `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001`
- `GEO_KPI_SPEND_DATA_PROFILER_001`
- `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001`
- `TRUSTED_READOUT_REPORT_RUNTIME_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`

## Reused primitives

| Primitive | Owner module | Runtime use |
|-----------|--------------|-------------|
| `_weekly_spend_totals()` | `spend_requirement_and_manipulation_feasibility_diagnostics_001` | Post-test window validation (passes `window_start` / `window_end` for observed period) |
| `_parse_date()`, `_to_float()` | same | Date coercion and numeric spend parsing |
| `SpendDiagnosticsColumnMapping` | same | Column mapping compatibility with profiler output |
| `_compute_achieved_contrast()` | `design_scenario_policy_feasibility_runtime_001` | Planning contrast semantics reference only; observed `spend_delta` is computed separately |

**Important:** Planning `required_spend_delta` is never used as observed `spend_delta`. When `planning_required_spend_delta` is present on input, a warning is emitted.

## Input object

`PostTestSpendInput` (dataclass):

- `experiment_id`, `spend_rows`, `post_period_start`, `post_period_end`, `experiment_type`
- Column mappings: `spend_date_column`, `spend_geo_column`, `spend_amount_column`, optional cell/channel/campaign/currency columns
- `assignment_rows` with geo/cell/role columns
- Optional scopes: `experiment_geo_scope`, `treatment_cell_values`, `control_cell_values`
- Optional baseline inputs: `counterfactual_or_bau_spend`, `baseline_spend`, `spend_baseline_policy`
- Reallocation scopes: `added_spend_scope`, `removed_spend_scope`, `budget_source_channel`, `budget_destination_channel`
- Lineage: `source_artifact`, `source_dataset_ref`, `source_lineage`

## Output evidence object

`PostTestSpendEvidence` (dataclass) with:

- window, geo/cell/channel/campaign scope
- `actual_treatment_spend`, `actual_control_or_baseline_spend`, `counterfactual_or_bau_spend`
- `spend_delta`, `spend_delta_definition`
- `readiness_status`, `blocking_reasons`, `warnings`

Trusted-readout handoff via `build_trusted_readout_spend_handoff()`:

- `spend_readiness_summary`
- `post_test_spend_evidence`
- `blocked_efficiency_metrics`
- `spend_lineage`
- `spend_warnings`

Efficiency metrics (`cost_per_incremental_kpi`, `ROAS`, `profit_ROI`) are explicitly **NOT_COMPUTED**.

## Deterministic extraction steps

1. Validate `spend_rows` non-empty and required columns present.
2. Coerce/validate post-period dates.
3. Filter rows to `post_period_start <= date <= post_period_end`.
4. Filter to `experiment_geo_scope` when provided.
5. Join assignment by geo; derive treatment/control role.
6. Aggregate spend at declared level.
7. Compute `actual_treatment_spend` and `actual_control_or_baseline_spend`.
8. Compute or validate `counterfactual_or_bau_spend` when provided.
9. Derive `spend_delta` by experiment type.
10. Emit readiness status, blockers, and warnings (never fail silently).

## Experiment-type spend_delta formulas

| experiment_type | spend_delta | Blocked when |
|-----------------|-------------|--------------|
| `go_dark` | `counterfactual_or_bau_spend - actual_treatment_spend` | missing BAU/counterfactual |
| `heavy_up` | `actual_treatment_spend - counterfactual_or_bau_spend` | missing BAU/counterfactual |
| `holdout` | `actual_treatment_spend - actual_control_or_baseline_spend` | missing control/baseline spend |
| `dosage` | treatment cell spend − baseline/control cell spend | missing baseline cell |
| `reallocation` | added scope spend − removed scope spend | missing added/removed scope → `PARTIAL_DIAGNOSTIC_ONLY` or blocked |

Planning contrast mapping (`_compute_achieved_contrast`): `GO_DARK` uses `c−t`, `HEAVY_UP` uses `t−c`, `DOSAGE_CONTRAST` uses `high−low`, `BUDGET_REALLOCATION` uses destination−source semantics.

## Readiness statuses

Implemented statuses:

- `READY`
- `NOT_REQUESTED`
- `PARTIAL_DIAGNOSTIC_ONLY`
- `BLOCKED_MISSING_SPEND_SOURCE`
- `BLOCKED_MISSING_POST_TEST_SPEND`
- `BLOCKED_MISSING_SPEND_DELTA`
- `BLOCKED_MISSING_SPEND_BASELINE`
- `BLOCKED_SPEND_WINDOW_MISMATCH`
- `BLOCKED_SPEND_GEO_SCOPE_MISMATCH`
- `BLOCKED_SPEND_CELL_SCOPE_MISMATCH`
- `BLOCKED_CURRENCY_MISMATCH`
- `BLOCKED_UNSUPPORTED_EXPERIMENT_TYPE`

Contract-only statuses (ROI/value mapping) remain delegated to trusted readout integration and claim authorization.

## Blockers and warnings

Blockers are explicit strings in `blocking_reasons` (e.g. `BLOCKED_MISSING_COLUMN:date`, `BLOCKED_MISSING_SPEND_BASELINE`). Warnings include currency issues, missing weekly values in window, planning delta not reused, and reallocation scope guidance.

## Non-goals

- No spend ingestion system
- No final-results module
- No ROI calculator runtime
- No claim authorization duplication
- No ROI/ROAS/business claim authorization
- No estimator/inference logic
- No method promotion or catalog unblock
- No MIP orchestration
- No user file prompts from panel_exp

## Validation results

- `python -m pytest tests/validation/test_post_test_spend_readiness_adapter_runtime_001.py` — pass
- `python -m pytest tests/governance/test_geox_post_test_spend_readiness_adapter_runtime_001.py` — pass
- Summary JSON: `docs/track_d/archives/GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001_summary.json`

Capability flags (all true): `post_test_spend_readiness_adapter_completed`, `post_test_window_filter_implemented`, `spend_assignment_join_implemented`, `actual_treatment_spend_implemented`, `spend_delta_readiness_implemented`, `trusted_readout_consumable_output_defined`.

Forbidden flags (all false): `spend_ingestion_system_created`, `final_results_module_created`, `roi_calculator_runtime_created`, `claim_authorization_duplicated`, `roi_claim_authorized`, `roas_claim_authorized`, `business_lift_claim_authorized`, `decision_recommendation_authorized`, `production_readout_authorized`, `method_promoted`, `instrument_promoted`, `catalog_unblocked`, `production_compatibility_authorized`, `estimator_implemented`, `inference_implemented`, `mmm_runtime_calls_implemented`, `llm_decisioning_authorized`.

## Next integration artifact

`GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001` — wire `build_trusted_readout_spend_handoff()` output into `TRUSTED_READOUT_REPORT_RUNTIME_001` without duplicating claim authorization.
