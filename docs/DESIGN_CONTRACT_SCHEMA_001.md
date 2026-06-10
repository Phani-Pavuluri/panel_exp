# Design Contract Schema 001

**Document ID:** DESIGN-CONTRACT-SCHEMA-001  
**Title:** Design Contract Schema 001  
**Status:** **Accepted**  
**Scope:** Machine-readable schema specification for design output contract metadata  
**Artifact type:** Documentation / schema specification — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md)

**Inputs:** [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) · [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) · [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) · [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md)

**Guardrails:** No runtime code · no field emission · no schema validator implementation · no fixture regeneration · no contract-complete status · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Contract Schema 001 |
| Status | **Accepted** |
| Scope | Schema specification for design output contract |
| Artifact type | Documentation / schema specification |

Ninth concrete design audit artifact. **Phase 1** of [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md). Defines typed/nested schema shape for contract fields future implementation will emit from `DesignEvidence`, `geo_runner`, and design adapter paths.

**Schema specified only — not implemented in code. No design is contract-complete.**

---

## 2. Purpose

This artifact defines:

- **Schema shape** — top-level envelope and nested blocks  
- **Required vs conditional fields** — per design family and geometry  
- **Enumerations** — canonical values aligned with geometry bridge and governance artifacts  
- **Validation rules** — presence, type, enum, membership, exclusivity  
- **Missing-field semantics** — BLOCK / WARN / not applicable  

Enables future: tier-1 emission · schema validator · golden fixtures · guardrail runtime enforcement.

---

## 3. Why this artifact exists

| Gap | Schema addresses |
|-----|------------------|
| Enforcement plan Phase 1 requires machine-readable schema | This artifact **is** Phase 1 (spec only) |
| Guardrails/suitability need structured fields | Nested blocks with enums — not prose |
| `DesignEvidence` partial today | Maps gap vs target (`evidence.py` — no `design_contract` block) |
| **0/31 contract-complete** | Schema defines target; emission not started |
| Fixture `design_evidence_v1.json` lacks contract block | Future minor evidence version adds `design_contract` |

---

## 4. Scope

Schema covers nested blocks for:

- Top-level design contract envelope  
- Design identity · geometry · assignment · unit universe  
- Time windows · outcomes/covariates  
- Multi-cell / shared-control · block/stratum/pair structure  
- Trim/thin · supergeo · power/MDE  
- Diagnostics · governance · compatibility · provenance  
- Forbidden downstream claims · compatibility hints  

Applies to all DES-001–DES-031 inventory rows when emitted; helper-only rows may use `artifact_type=helper_output`.

---

## 5. Non-goals

- No runtime Python/JSON Schema file in `panel_exp/` (future implementation)  
- No field emission from `geo_runner` or `DesignEvidence`  
- No schema validator implementation  
- No `design_evidence_v1.json` fixture regeneration  
- No `artifact_status=contract_complete` for any design today  
- No design promotion or downstream authorization  

---

## 6. Schema design principles

1. **Explicit over inferred** — no downstream consumer may infer `geometry_id` from assignment shape alone  
2. **Missing required fields are blocking** — `field_missing_block` → `contract_validation_status=BLOCK`  
3. **Conditional fields** depend on `design_family`, `geometry_id`, `is_multi_cell`, adapter/bridge flags  
4. **Downstream claims forbidden by default** — `forbidden_downstream_claims` must be non-empty  
5. **No silent pooling** — `pooled_claims_allowed=false`, `portfolio_claims_allowed=false` unless bridge ADR  
6. **No silent target-population shifts** — trim/supergeo must declare `target_population_status`  
7. **No geometry transition without `bridge_status`** — cross-geometry claims require bridge artifact ID  
8. **Versioned schema** — `schema_name` + `schema_version` semver  
9. **Backward compatible, not silently upgraded** — legacy evidence without block → `contract_unknown`  

---

## 7. Top-level schema envelope

Proposed nested object: **`design_contract`** (future child of `DesignEvidence.to_dict()` / `ExperimentEvidence`).

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `schema_name` | string | Yes | `"DESIGN-CONTRACT-SCHEMA-001"` |
| `schema_version` | string | Yes | Semver, e.g. `"1.0.0"` |
| `artifact_type` | enum | Yes | `design_output_contract` · `helper_output` · `planning_metadata` |
| `design_contract_status` | enum | Yes | See §10 `contract_status` |
| `producer` | string | Yes | e.g. `geo_runner` · `QuickBlockAdapter` |
| `created_at` | ISO-8601 | Yes | UTC timestamp |
| `design_identity` | object | Yes | §11 |
| `geometry` | object | Yes | §12 |
| `assignment` | object | Yes | §13 |
| `units` | object | Yes | §14 |
| `time_windows` | object | Yes | §15 |
| `outcomes` | object | Recommended | §16 |
| `multi_cell` | object | Conditional | §17 |
| `concurrency` | object | Yes | §17 (concurrency fields) |
| `structure` | object | Conditional | §18 |
| `population` | object | Conditional | §19–§20 (trim/thin/supergeo) |
| `trim_thin` | object | Conditional | §19 |
| `supergeo` | object | Conditional | §20 |
| `power_mde` | object | Conditional | §21 |
| `diagnostics` | object | Recommended | §22 |
| `governance` | object | Yes | §23 |
| `compatibility` | object | Recommended | §24 |
| `provenance` | object | Yes | §25 |

**Not implemented in code at authoring.**

---

## 8. Required field severity taxonomy

| Severity | Meaning |
|----------|---------|
| `required_universal` | Every `artifact_type=design_output_contract` row |
| `required_conditional` | Required when trigger (family, geometry, flag) true |
| `recommended` | WARN if missing when consumer needs it |
| `optional` | No block if absent |
| `future_reserved` | Namespace reserved; no block if absent |
| `not_applicable` | Must not appear or must be null for helper outputs |

---

## 9. Field validation outcome taxonomy

| Outcome | Meaning | Maps to |
|---------|---------|---------|
| `field_valid` | Present, typed, enum-valid | Continue |
| `field_missing_block` | Required/conditional required absent | BLOCK |
| `field_missing_warn` | Recommended absent | WARN |
| `field_invalid_block` | Present but invalid value/type | BLOCK |
| `field_not_applicable` | Correctly omitted for family | Pass |
| `field_future_reserved` | Reserved namespace only | Pass |

---

## 10. Enumerations

### `geometry_id` (canonical — [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) §5)

| Value | Description |
|-------|-------------|
| `unit_panel_single_cell` | Unit-panel, single cell |
| `aggregate_two_row` | Treated aggregate + control aggregate |
| `pooled_treated_control_panel` | Pooled treated/control groups |
| `multi_cell_per_cell` | Per-cell unit panels |
| `pooled_multi_cell` | Pooled multi-cell (blocked default) |
| `supergeo` | Constructed geo units |
| `trimmed_geometry` | Post-trim population |
| `time_series_operator_geometry` | Operator/forecast geometry |

### `contract_status` / `design_contract_status`

`contract_unknown` · `contract_incomplete` · `contract_complete` · `contract_blocked`

### `artifact_status`

Same as `contract_status` — alias for governance consumers.

### `design_family`

`matching_design` · `standard_assignment` · `stratified_assignment` · `thinning_design` · `blocking_assignment` · `trimmed_population` · `supergeo_design` · `multi_cell_assignment` · `power_mde_design_helper` · `orchestration_helper` · `validation_helper` · `helper_output`

### `target_population_status`

`full_panel` · `trimmed` · `thinned` · `supergeo` · `restricted_eligible` · `ambiguous` · `unknown`

### `concurrent_multi_experiment_compatibility`

`compatible` · `compatible_with_constraints` · `restricted` · `blocked_without_bridge` · `not_evaluated`

### `bridge_status`

`direct` · `bridge_required` · `bridge_satisfied` · `blocked`

### `adapter_status`

`not_applicable` · `none` · `required` · `satisfied` · `failed`

### `guardrail_status`

`PASS` · `WARN` · `BLOCK` · `NOT_EVALUATED` · `DEFERRED` · `REQUIRES_ADAPTER` · `REQUIRES_BRIDGE` · `REQUIRES_STATISTICAL_VALIDATION`

### `suitability_status`

Per [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) §6 categories.

### `validation_status` / `contract_validation_status`

`not_run` · `PASS` · `WARN` · `BLOCK` · `FAIL`

### `readout_semantics` (compatibility hints)

`point_only` · `prediction_interval` · `forecast_interval` · `null_decision` · `causal_interval_candidate` · `causal_interval_validated` · `planning_metadata_only`

### `forbidden_downstream_claim` (list items)

`trust_report` · `calibration_signal` · `mmm_calibration` · `llm_product_recommendation` · `production_experiment_recommendation` · `pooled_portfolio_lift` · `full_population_causal_claim` · `original_geo_causal_claim` · `causal_uncertainty_from_point_only` · `causal_uncertainty_from_power_mde` · `suitability_approved` · `geometry_transition_without_bridge`

### `compatibility_hint`

`scm_jk_unit_panel` · `augsynth_point_unit_panel` · `tbr_aggregate_two_row` · `did_pooled_panel` · `mcell_per_cell` · `tbrridge_operator` · `planning_only_power` · `adapter_required` · `bridge_required` · `stat_validation_required`

### `missing_field_policy`

`block` · `warn` · `ignore` · `not_applicable`

---

## 11. Design identity block (`design_identity`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `design_inventory_id` | required_universal | string | DES-001–DES-031 |
| `design_name` | required_universal | string | Registry or inventory name |
| `design_family` | required_universal | enum | §10 |
| `design_method_class` | required_universal | string | Class/function symbol |
| `design_version` | required_universal | string | Package + impl version |
| `is_registry_design` | required_universal | boolean | |
| `registry_key` | required_conditional | string | When registered |
| `wrapper_identity` | required_conditional | string | Rerandomization wrapper ≠ base (DES-006) |
| `random_seed` | required_universal | int \| null | Documented null policy |
| `reproducibility_hash` | required_universal | string | Assignment + spec + contract hash |

---

## 12. Geometry block (`geometry`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `geometry_id` | required_universal | enum | §10 geometry_id |
| `geometry_scope` | required_universal | string | Human-readable scope |
| `source_geometry_id` | optional | enum | Pre-bridge geometry |
| `target_geometry_id` | optional | enum | Claimed readout geometry |
| `bridge_status` | required_universal | enum | Default `direct` |
| `bridge_artifact_id` | required_conditional | string | When `bridge_required` |
| `target_population_status` | required_universal | enum | §10 |
| `geometry_claims_allowed` | recommended | string[] | Scoped claims |
| `geometry_claims_forbidden` | required_universal | string[] | Default cross-geometry |

---

## 13. Assignment block (`assignment`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `assignment_map` | required_universal | object | Arm → unit ID list |
| `treated_units` | required_universal | string[] | Union across cells |
| `control_units` | required_universal | string[] | |
| `treatment_labels` | required_universal | string[] | e.g. `test_0` |
| `control_labels` | required_universal | string[] | Default `control` |
| `assignment_rule` | recommended | string | Rule name |
| `assignment_probability` | optional | number | Tier-1 Bernoulli |
| `assignment_is_exclusive` | required_universal | boolean | No duplicate arms |
| `duplicate_assignment_count` | required_universal | int | Must be 0 |
| `missing_assignment_count` | required_universal | int | Documented gaps |

---

## 14. Unit universe block (`units`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `all_units` | required_universal | string[] | Input universe |
| `eligible_units` | required_universal | string[] | Post-constraint |
| `excluded_units` | required_conditional | string[] | Trim/thin/blacklist |
| `donor_pool_units` | recommended | string[] | SCM/TBRRidge |
| `source_units` | required_conditional | string[] | Supergeo sources |
| `unit_count_total` | required_universal | int | |
| `unit_count_eligible` | required_universal | int | |
| `unit_count_excluded` | required_conditional | int | When exclusions |
| `exclusion_policy` | required_conditional | string | Trim/thin |
| `exclusion_reason_codes` | required_conditional | string[] | Per-unit or policy |

---

## 15. Time window block (`time_windows`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `pre_period_start` | required_universal | int \| date | Index or ISO |
| `pre_period_end` | required_universal | int \| date | |
| `test_period_start` | required_universal | int \| date | |
| `test_period_end` | required_universal | int \| null | |
| `cooldown_period_start` | optional | int \| date | |
| `cooldown_period_end` | optional | int \| date | |
| `time_granularity` | recommended | string | week/day |
| `duration_weeks` | optional | number | Power alignment |
| `calendar_alignment_status` | optional | enum | `aligned` · `unknown` |

---

## 16. Outcome/covariate block (`outcomes`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `primary_outcome` | recommended | string | Column name |
| `secondary_outcomes` | optional | string[] | |
| `covariates_used` | optional | string[] | |
| `balance_covariates` | recommended | string[] | Stratified/rerandomization |
| `outcome_scale` | recommended | enum | level/relative/log |
| `metric_definition_id` | optional | string | |
| `missing_covariate_policy` | optional | string | |

---

## 17. Multi-cell / shared-control + concurrency

### `multi_cell` (conditional when `is_multi_cell=true`)

| Field | Severity | Type |
|-------|----------|------|
| `is_multi_cell` | required_universal | boolean |
| `cell_ids` | required_conditional | string[] |
| `cell_assignment_map` | required_conditional | object |
| `shared_control_mode` | required_conditional | enum: `shared` · `independent` · `mixed` · `unspecified` |
| `shared_control_units` | required_conditional | string[] |
| `control_reuse_policy` | required_conditional | string |
| `control_reuse_burden` | recommended | number |
| `pooled_claims_allowed` | required_conditional | boolean (default false) |
| `portfolio_claims_allowed` | required_conditional | boolean (default false) |

### `concurrency` (required_universal)

| Field | Severity | Type |
|-------|----------|------|
| `concurrent_multi_experiment_compatibility` | required_universal | enum §10 |
| `concurrency_constraints` | recommended | string[] |
| `concurrent_experiment_ids` | optional | string[] |

---

## 18. Structure block (`structure`) — block/stratum/pair

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `block_ids` | required_conditional | string[] | QuickBlock, Rerandomization |
| `stratum_ids` | required_conditional | string[] | StratifiedRandomization |
| `pair_ids` | required_conditional | string[] | MatchedPair |
| `unit_to_block_map` | required_conditional | object | |
| `unit_to_stratum_map` | required_conditional | object | |
| `unit_to_pair_map` | required_conditional | object | |
| `structure_respected_by_inference` | optional | boolean | Future |
| `structure_missing_policy` | required_conditional | enum | `block` if inference ignores structure |

---

## 19. Trim/thin block (`trim_thin`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `is_trimmed` | required_conditional | boolean | DES-009 |
| `is_thinned` | required_conditional | boolean | DES-005 |
| `trim_policy` | required_conditional | string | |
| `thin_policy` | required_conditional | string | |
| `trimmed_units` | required_conditional | string[] | |
| `thinned_units` | required_conditional | string[] | |
| `pre_trim_population` | required_conditional | string | |
| `post_trim_population` | required_conditional | string | |
| `population_shift_score` | optional | number | |
| `full_population_claim_allowed` | required_conditional | boolean | Default **false** |

---

## 20. Supergeo block (`supergeo`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `is_supergeo` | required_conditional | boolean | DES-010 |
| `supergeo_ids` | required_conditional | string[] | |
| `supergeo_source_unit_map` | required_conditional | object | supergeo → [sources] |
| `supergeo_weights` | optional | object | |
| `source_units_per_supergeo` | required_conditional | object | |
| `aggregation_distortion_score` | recommended | number | |
| `original_geo_claim_allowed` | required_conditional | boolean | Default **false** |
| `supergeo_bridge_required` | required_conditional | boolean | Default **true** |

---

## 21. Power/MDE block (`power_mde`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `power_contract_id` | required_conditional | string | When power run |
| `mde` | optional | number | |
| `power` | optional | number | |
| `alpha` | optional | number | |
| `duration_assumption` | optional | object | |
| `variance_assumption` | optional | object | |
| `geometry_alignment_status` | required_conditional | enum | `aligned` · `mismatch` · `unknown` |
| `planning_only_flag` | required_conditional | boolean | Default **true** |
| `causal_readout_authorized` | required_conditional | boolean | Default **false** |

---

## 22. Diagnostics block (`diagnostics`)

| Field | Severity | Type |
|-------|----------|------|
| `balance_diagnostics` | recommended | object |
| `pre_period_fit_diagnostics` | optional | object |
| `trend_balance` | optional | object |
| `seasonality_balance` | optional | object |
| `spend_balance` | optional | object |
| `donor_pool_support` | optional | object |
| `control_support_ratio` | optional | number |
| `target_population_drift` | optional | object |
| `diagnostic_completeness_status` | recommended | enum: `complete` · `partial` · `missing` |

---

## 23. Governance block (`governance`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `forbidden_downstream_claims` | required_universal | enum[] | §10 — **non-empty** |
| `guardrail_status` | required_universal | enum | Derived; default BLOCK |
| `guardrail_reason_codes` | required_universal | string[] | DGR-* / D-COMB-* |
| `suitability_status` | required_universal | enum | Default `contract_blocked` |
| `suitability_reason_codes` | required_universal | string[] | D-SUIT-* |
| `combination_matrix_status` | recommended | string | Advisory until emission |
| `statistical_validation_status` | required_universal | enum | `protocol_defined_not_executed` |
| `contract_validation_status` | required_universal | enum | `not_run` until validator |
| `downstream_authorization_status` | required_universal | enum | `blocked` (default) |

---

## 24. Compatibility block (`compatibility`)

| Field | Severity | Type |
|-------|----------|------|
| `compatible_estimators` | optional | string[] |
| `compatible_inference_families` | optional | string[] |
| `compatible_readout_semantics` | optional | enum[] |
| `incompatible_estimators` | optional | string[] |
| `incompatible_reason_codes` | optional | string[] |
| `requires_adapter` | required_conditional | boolean |
| `requires_bridge` | required_conditional | boolean |
| `requires_statistical_validation` | required_universal | boolean (default true) |

---

## 25. Provenance block (`provenance`)

| Field | Severity | Type | Notes |
|-------|----------|------|-------|
| `producer_module` | required_universal | string | e.g. `panel_exp.design.geo_runner` |
| `producer_function` | required_universal | string | e.g. `run_geo_experiment_design` |
| `source_artifacts` | optional | string[] | |
| `source_data_hash` | recommended | string | `input_data_hash` |
| `spec_hash` | required_universal | string | From `DesignSpec` |
| `created_by` | optional | string | |
| `run_id` | required_universal | string | `experiment_id` |
| `repo_commit` | optional | string | |
| `schema_validation_time` | optional | ISO-8601 | When validator runs |

---

## 26. Conditional requirements by design group

| Design group | DES | Universal + conditional highlights |
|--------------|-----|-----------------------------------|
| Tier-1 geo-run | DES-001–006 | Universal + `geometry_id`, forbidden claims, concurrency; `structure` n/a unless stratified/block wrapper |
| StratifiedRandomization | DES-004 | + `stratum_ids`, `unit_to_stratum_map` |
| Rerandomization | DES-006 | + `wrapper_identity` |
| QuickBlock / MatchedPair | DES-007–008 | + `adapter_status=required`; structure block; adapter before `contract_complete` |
| ThinningDesign | DES-005 | + `trim_thin`; `target_population_status=ambiguous` until ADR |
| TrimmedMatchDesign | DES-009 | + `trim_thin`, `bridge_status`, excluded units |
| SupergeoModel | DES-010 | + `supergeo` block, `geometry_id=supergeo` |
| multi_test_groups | DES-011 | + `multi_cell` block, cell IDs, shared-control |
| PowerAnalysis | DES-014–015 | + `power_mde`; `planning_only_flag=true` |
| Helpers DES-016–025 | — | `artifact_type=helper_output`; governance minimal |
| Adapter-required | DES-007–010 | `adapter_status` before emission complete |

---

## 27. Missing-field policy

| Severity | Missing policy | Outcome |
|----------|----------------|---------|
| `required_universal` | `block` | `field_missing_block` → contract BLOCK |
| `required_conditional` (trigger true) | `block` | Family/use BLOCK |
| `recommended` | `warn` | `field_missing_warn` |
| `optional` | `ignore` | No block |
| `future_reserved` | `ignore` | No block |
| `not_applicable` | `not_applicable` | Must not be required |
| Unknown keys in `design_contract` | `warn` | Namespace pollution WARN; unknown top-level → BLOCK |

Aligns with [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) universal BLOCK rules.

---

## 28. Schema validation rules

1. **Enum validation** — all enum fields ∈ §10  
2. **Required presence** — universal fields must exist  
3. **Conditional presence** — evaluate triggers before block  
4. **List/map types** — JSON-serializable; no null lists where array required  
5. **Unit membership** — treated ∩ control = ∅; subsets of `eligible_units`  
6. **Assignment exclusivity** — `duplicate_assignment_count == 0`  
7. **Period order** — pre_end < test_start where applicable  
8. **No pooled claims without bridge** — if `pooled_claims_allowed` true → `bridge_artifact_id` required  
9. **No causal authorization from power/MDE** — `causal_readout_authorized` must be false when `planning_only_flag` true  
10. **No downstream authorization by default** — `downstream_authorization_status=blocked`  
11. **`forbidden_downstream_claims` non-empty** — must include product-layer forbids  
12. **`geometry_id` valid** — must match assignment layout or bridge documented  

---

## 29. Example minimal contract: tier-1 geo-run

**Illustrative only — not emitted by current code.**

```json
{
  "design_contract": {
    "schema_name": "DESIGN-CONTRACT-SCHEMA-001",
    "schema_version": "1.0.0",
    "artifact_type": "design_output_contract",
    "design_contract_status": "contract_incomplete",
    "producer": "geo_runner",
    "created_at": "2026-06-10T12:00:00Z",
    "design_identity": {
      "design_inventory_id": "DES-002",
      "design_name": "complete_randomization",
      "design_family": "standard_assignment",
      "design_method_class": "CompleteRandomization",
      "design_version": "panel_exp-0.2.1",
      "is_registry_design": true,
      "registry_key": "complete_randomization",
      "wrapper_identity": null,
      "random_seed": 42,
      "reproducibility_hash": "sha256:example-tier1"
    },
    "geometry": {
      "geometry_id": "unit_panel_single_cell",
      "geometry_scope": "single test cell, unit-level arms",
      "bridge_status": "direct",
      "target_population_status": "full_panel",
      "geometry_claims_forbidden": ["aggregate_two_row", "pooled_multi_cell"]
    },
    "assignment": {
      "assignment_map": {"control": ["u0", "u1"], "test_0": ["u2"]},
      "treated_units": ["u2"],
      "control_units": ["u0", "u1"],
      "treatment_labels": ["test_0"],
      "control_labels": ["control"],
      "assignment_is_exclusive": true,
      "duplicate_assignment_count": 0,
      "missing_assignment_count": 0
    },
    "units": {
      "all_units": ["u0", "u1", "u2"],
      "eligible_units": ["u0", "u1", "u2"],
      "unit_count_total": 3,
      "unit_count_eligible": 3
    },
    "multi_cell": {"is_multi_cell": false},
    "concurrency": {
      "concurrent_multi_experiment_compatibility": "not_evaluated"
    },
    "governance": {
      "forbidden_downstream_claims": [
        "trust_report",
        "calibration_signal",
        "mmm_calibration",
        "llm_product_recommendation",
        "production_experiment_recommendation",
        "pooled_portfolio_lift",
        "suitability_approved"
      ],
      "guardrail_status": "BLOCK",
      "guardrail_reason_codes": ["D-COMB-MISSING-CONTRACT-FIELDS"],
      "suitability_status": "contract_blocked",
      "suitability_reason_codes": ["D-SUIT-CONTRACT-BLOCKED"],
      "statistical_validation_status": "protocol_defined_not_executed",
      "contract_validation_status": "not_run",
      "downstream_authorization_status": "blocked"
    },
    "provenance": {
      "producer_module": "panel_exp.design.geo_runner",
      "producer_function": "run_geo_experiment_design",
      "spec_hash": "a36ce9f635cdd8c40f4f285182fc2b53",
      "run_id": "example-exp-001"
    }
  }
}
```

Status `contract_incomplete` reflects schema-spec example — full validator not run.

---

## 30. Example conditional contract: multi-cell / shared-control

**Illustrative only.**

```json
{
  "design_contract": {
    "schema_name": "DESIGN-CONTRACT-SCHEMA-001",
    "schema_version": "1.0.0",
    "design_contract_status": "contract_blocked",
    "geometry": {
      "geometry_id": "multi_cell_per_cell",
      "bridge_status": "direct",
      "target_population_status": "full_panel"
    },
    "multi_cell": {
      "is_multi_cell": true,
      "cell_ids": ["test_0", "test_1"],
      "cell_assignment_map": {
        "test_0": ["u10", "u11"],
        "test_1": ["u20"]
      },
      "shared_control_mode": "shared",
      "shared_control_units": ["u0", "u1", "u2"],
      "control_reuse_policy": "shared_donors_across_cells_documented",
      "control_reuse_burden": 0.33,
      "pooled_claims_allowed": false,
      "portfolio_claims_allowed": false
    },
    "governance": {
      "forbidden_downstream_claims": ["pooled_portfolio_lift", "trust_report"],
      "guardrail_status": "BLOCK",
      "suitability_status": "contract_blocked",
      "suitability_reason_codes": ["D-SUIT-MULTICELL-METADATA-MISSING"]
    }
  }
}
```

Shows required cell IDs and shared-control policy when `is_multi_cell=true`.

---

## 31. Example conditional contract: trim / supergeo

**Illustrative only.**

```json
{
  "design_contract": {
    "schema_name": "DESIGN-CONTRACT-SCHEMA-001",
    "schema_version": "1.0.0",
    "design_contract_status": "contract_blocked",
    "geometry": {
      "geometry_id": "trimmed_geometry",
      "bridge_status": "bridge_required",
      "bridge_artifact_id": "F-GEO-004",
      "target_population_status": "trimmed"
    },
    "trim_thin": {
      "is_trimmed": true,
      "trimmed_units": ["u99", "u100"],
      "pre_trim_population": "full_panel",
      "post_trim_population": "trimmed_match_eligible",
      "full_population_claim_allowed": false
    },
    "supergeo": {
      "is_supergeo": false
    },
    "governance": {
      "forbidden_downstream_claims": ["full_population_causal_claim", "original_geo_causal_claim"],
      "guardrail_status": "REQUIRES_BRIDGE",
      "suitability_status": "bridge_required"
    },
    "compatibility": {
      "requires_bridge": true,
      "requires_adapter": true
    }
  }
}
```

Supergeo variant would set `geometry_id=supergeo`, `supergeo.is_supergeo=true`, `supergeo_source_unit_map` populated, `bridge_artifact_id=F-GEO-003`.

---

## 32. Backward compatibility

| Policy | Rule |
|--------|------|
| Legacy `DesignEvidence` without `design_contract` | `design_contract_status=contract_unknown` |
| `validation_summary.status=PASS` alone | Does **not** imply contract complete |
| No silent promotion | Historical JSON unchanged |
| Transition WARN | Internal docs may WARN; downstream **BLOCK** |
| Evidence version | Minor bump when `design_contract` block added (additive) |

Current fixture `tests/fixtures/artifact_schemas/design_evidence_v1.json` — **no `design_contract` key** at authoring.

---

## 33. Future implementation path

| Step | Artifact / work |
|------|-----------------|
| 1 | **`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001`** ✅ — Phase 2 emission spec ([`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md)); **fields not emitted yet** |
| 2 | Implement `design_contract` block in `DesignEvidence.from_assignment` |
| 3 | Schema validator module + negative tests |
| 4 | Golden fixture extension |
| 5 | Adapters (DES-007–010) |
| 6 | Bridge metadata emission |
| 7 | **`DESIGN_GUARDRAIL_ENFORCEMENT_001`** — runtime |
| 8 | `D5-DES-STAT-*` integration |

Optional parallel: `DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001` — may follow emission plan.

---

## 34. Current status assessment

| Item | Status |
|------|--------|
| Schema specified | ✅ This artifact |
| Schema in code | ❌ |
| Field emission | ❌ |
| Validator | ❌ |
| Contract-complete designs | **0 / 31** |
| Downstream governed use | ❌ **Blocked** |

---

## 35. Governance gates

| Gate | Status |
|------|--------|
| Schema defined | ✅ |
| Schema implemented | ❌ |
| Designs promoted | ❌ |
| TrustReport / CalibrationSignal / MMM / LLM | ❌ **BLOCKED** |

This artifact does **not** implement schema, validate designs, authorize causal claims, or authorize product layers.

---

## 36. Current status and verdict

| Field | Value |
|-------|-------|
| Verdict | `design_contract_schema_defined_not_implemented` |
| Enforcement phase | **1** (spec complete; implementation not started) |
| Contract-complete designs | **0** |

### Search methodology (2026-06-10)

```bash
grep -R "DESIGN_CONTRACT_ENFORCEMENT_PLAN_001\|DESIGN_OUTPUT_CONTRACT_001\|DESIGN_SUITABILITY_FRAMEWORK_001" -n docs
grep -R "DesignEvidence\|ExperimentEvidence\|DesignSpec\|DesignMethod\|PowerContract\|PowerAnalysis" -n panel_exp tests docs
grep -R "geometry_id\|forbidden_downstream_claims\|concurrent_multi_experiment_compatibility\|shared_control_policy" -n panel_exp tests docs
grep -R "assignment\|treatment\|control\|cell_id\|block_id\|stratum\|pair_id\|supergeo\|trim\|thin\|eligible\|excluded\|donor" -n panel_exp/design panel_exp/evidence.py panel_exp/spec.py tests docs
grep -R "schema\|contract\|validator\|fixture\|json" -n panel_exp tests docs
find tests -iname "*design*" -o -iname "*evidence*" -o -iname "*contract*" -o -iname "*schema*" -o -iname "*validation*"
find panel_exp/design -type f
```

**Code inspected (read-only):** `evidence.py`, `design/geo_runner.py`, `spec.py`, `design/` modules, `design_evidence_v1.json`, registry and Track D tests.

---

## 37. Roadmap

**Tier-1 emission plan:** [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) ✅ **Accepted** — defines Phase 2 producer mapping for DES-001–004, DES-006, constrained DES-011. **Fields are not emitted yet; no validator; 0/31 contract-complete.**

**Validation test plan:** [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) ✅ **Accepted** — defines tests required before schema implementation can be trusted; **tests not implemented**.

**Validator implementation plan:** [`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md`](DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md) ✅ **Accepted** — future validator will consume schema blocks, enums, and severity rules (§8–§10). **Not implemented.**

**Validator:** ✅ **`panel_exp/validation/design_contract_validator_001.py`** — schema enforced by validator; **no runtime emission yet**.

**Tier-1 emission implementation plan:** [`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md) ✅ — tier-1 emission **must populate schema fields conservatively** per §9; **not implemented in code**.

**Next artifact:** **`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001`**

---

## 38. Completion checklist

| Item | Status |
|------|--------|
| Prerequisites inspected | ✅ |
| Code paths inspected | ✅ |
| Schema envelope defined | ✅ §7 |
| Field blocks defined | ✅ §11–§25 |
| Enums defined | ✅ §10 |
| Conditional requirements defined | ✅ §26 |
| Missing-field policy defined | ✅ §27 |
| Examples included | ✅ §29–§31 |
| Roadmap updated | ✅ companion docs |
| No code changed | ✅ |
| Tests run | ✅ (completion report) |

---

## 39. Companion doc updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Tier-1 emission plan Accepted; next = validation test plan |
| [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) | Maps schema fields to tier-1 producers — not implemented |
| [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) | Phase 1 defined |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Schema representation |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | Fields schema-defined, not emitted |
| [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) | Future enforcement consumes schema |
| [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) | Schema necessary, insufficient |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Schema complete |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Schema precursor |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Emission gap |
| [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md) | Planning blocked |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Lane status |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |

---

*DESIGN-CONTRACT-SCHEMA-001 v1.0.5 — Accepted; tier-1 emission wiring plan defined; fields not emitted; next = DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001.*
