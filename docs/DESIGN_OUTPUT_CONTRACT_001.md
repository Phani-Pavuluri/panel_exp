# Design Output Contract 001

**Document ID:** DESIGN-OUTPUT-CONTRACT-001  
**Title:** Design Output Contract 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` design-output governance  
**Artifact type:** Documentation / governance — **no code changes**  
**Date:** 2026-06-09  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md)

**Companions:** [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) · [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md)

**Guardrails:** No implementation · no design promotion · no suitability claim · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Output Contract 001 |
| Status | **Accepted** |
| Scope | GeoX / `panel_exp` design-output governance |
| Artifact type | Documentation / governance |

This artifact defines the **minimum governed metadata and diagnostics** every design must emit before downstream estimator, inference, readout, suitability, TrustReport, CalibrationSignal, MMM, or LLM layers may consume design output.

---

## 2. Purpose

Design methods determine **assignment geometry**, **target population**, **donor pool**, **cell structure**, and **estimator/inference feasibility**. Downstream layers (D5 characterization, suitability framework, experiment planning) currently assume reference-design assignment dicts without a unified metadata contract.

**DesignOutputContract** (§6) operationalizes [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) geometry IDs, [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) readout prerequisites, and [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) audit requirements into a **required output schema** for all current and future designs.

**This artifact does not validate, promote, or authorize any design or combination.**

---

## 3. Why this artifact exists

| Gap | This contract addresses |
|-----|-------------------------|
| Estimator/inference D5 used **reference designs** (`greedy_match_markets`) without governed design metadata | Defines fields every design must emit |
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) identified design-side audit parity gap | First concrete output contract under design audit lane |
| [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) blocked trim/supergeo/pooled transitions without metadata | Requires `geometry_id`, bridge flags, source maps, exclusion lists |
| [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) requires explicit readout targets | Requires scale hints, time windows, forbidden claims |
| Current `DesignEvidence` (`panel_exp/evidence.py`) emits assignment + validation summary only | Documents full target schema; implementation gap acknowledged |

**Repo inspection (no modifications):** `panel_exp/design/` (17 modules), `DesignEvidence.from_assignment`, `run_geo_experiment_design`, `prepare_constraint_context`, `validate_design`, `PowerAnalysis` / `build_power_contract`, D5 harness assignment patterns.

---

## 4. Scope

Applies to:

- All registered designs (`get_design_registry()`)  
- All design helpers that create assignments  
- Multi-cell / shared-control configurations (`n_test_grps > 1`)  
- Thinning, trim, supergeo outputs  
- Orchestration surfaces (`GeoExperimentDesign`, `run_geo_experiment_design`)  
- **All future design methods** and **future experiment recommendation flows** ([`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md))

---

## 5. Non-goals

- No design, estimator, or inference implementation changes  
- No validation harness or D5 archive changes  
- No design promotion or suitability claim  
- No TrustReport role, CalibrationSignal eligibility, MMM, or LLM authorization  
- No claim that any current design satisfies this contract in code today  

---

## 6. Core contract object: DesignOutputContract

Conceptual governed object emitted (or validated) at design completion.

| Field | Type / notes | Required |
|-------|--------------|----------|
| `contract_id` | `"DESIGN-OUTPUT-CONTRACT-001"` | Yes |
| `contract_version` | Semver string (e.g. `"1.0.0"`) | Yes |
| `design_run_id` | Unique run identifier | Yes |
| `design_method_id` | Canonical registry or helper ID | Yes |
| `design_family` | Taxonomy from design audit program | Yes |
| `design_version` | Implementation version string | Yes |
| `design_status` | `completed` · `failed` · `partial` | Yes |
| `artifact_status` | `contract_complete` · `contract_incomplete` · `contract_blocked` | Yes |
| `created_at` | ISO-8601 UTC | Yes |
| `source_code_ref` | Module path + symbol | Yes |
| `random_seed` | Integer or documented null policy | Yes |
| `reproducibility_hash` | Hash over assignment + key metadata | Yes |

Nested field groups §7–§24 compose the full contract payload.

---

## 7. Design identity fields

| Field | Required |
|-------|----------|
| `design_method_id` | Yes |
| `design_family` | Yes |
| `design_variant` | When applicable |
| `design_registry_name` | When registered |
| `design_class_or_function` | Yes |
| `design_mode` | e.g. `geo_run` · `direct_api` · `helper` |
| `design_parameters` | JSON-serializable dict of run parameters |
| `random_seed` | Yes |
| `deterministic_run` | Boolean — expected determinism given seed |
| `software_version` | Package version |
| `repo_commit` | Git commit when available |

---

## 8. Unit universe fields

| Field | Required |
|-------|----------|
| `unit_id_field` | Column/index name for unit identity |
| `all_candidate_units` | Full input universe |
| `eligible_units` | Units eligible after constraints |
| `ineligible_units` | Units ruled ineligible pre-assignment |
| `excluded_units` | Units excluded by design (trim/blacklist) |
| `exclusion_reason_by_unit` | Map unit → reason code |
| `n_candidate_units` | Count |
| `n_eligible_units` | Count |
| `n_excluded_units` | Count |
| `target_population_pre_design` | Named population before design |
| `target_population_post_design` | Named population after design |
| `target_population_changed` | Boolean |
| `target_population_change_reason` | When changed |

---

## 9. Assignment fields

| Field | Required |
|-------|----------|
| `treated_units` | All treated unit IDs (union across cells) |
| `control_units` | Control / donor-eligible control IDs |
| `holdout_units` | If holdout arm exists |
| `unassigned_units` | Eligible but unassigned (must be empty or documented) |
| `assignment_by_unit` | Map unit → arm label |
| `assignment_probability` | Declared or estimated treatment probability |
| `requested_n_treated` / `realized_n_treated` | Greedy (DES-001): requested vs realized unit counts via `greedy_match_markets.last_feasibility_metadata` when `feasibility_policy != legacy` |
| `requested_per_cell_shares` / `realized_per_cell_shares` | Multi-cell (DES-011): via `last_multicell_metadata` when `multicell_policy != legacy` |
| `assignment_rule` | Human-readable rule name |
| `randomization_unit` | Unit of randomization |
| `treatment_labels` | Allowed treated labels (`test_0`, …) |
| `control_label` | Control arm label (default `control`) |
| `assignment_exclusive` | Boolean — no unit in multiple arms |
| `duplicate_assignment_check` | Result: pass/fail |
| `missing_assignment_check` | Result: pass/fail |

**Current code partial match:** geo designs emit `assignment` dict via `DesignEvidence`; exclusivity checked in `validate_assignment_dict`.

---

## 10. Multi-cell and concurrent-experiment fields

| Field | Required when multi-cell |
|-------|--------------------------|
| `supports_multi_cell` | Yes |
| `n_cells` | Yes |
| `cell_ids` | Yes |
| `experiment_ids` | When multiple experiments |
| `test_group_ids` | Yes |
| `control_group_ids` | Yes |
| `treated_units_by_cell` | Map cell → treated list |
| `control_units_by_cell` | Map cell → control list (if cell-specific) |
| `shared_control_used` | Boolean |
| `shared_control_policy` | **Required if shared control** |
| `control_reuse_policy` | **Required if shared control** |
| `cell_assignment_exclusive` | Boolean |
| `unit_reuse_policy` | Document cross-cell reuse |
| `cell_failure_policy` | No silent drop |
| `pooled_claim_requested` | Boolean — default false |
| `pooled_claim_allowed` | Boolean — default false per geometry bridge |
| `portfolio_claim_allowed` | Boolean — default false |

---

## 11. Concurrent multi-experiment compatibility

**Required field:** `concurrent_multi_experiment_compatibility`

| Value | Meaning |
|-------|---------|
| `compatible` | Multiple simultaneous experiments supported |
| `compatible_with_constraints` | Supported under documented constraints |
| `restricted` | Limited reuse; isolation rules apply |
| `blocked_without_bridge` | Bridge artifact required |
| `not_evaluated` | Default until design audit completes |

**Required supporting fields:**

`max_cells_supported` · `max_test_groups_supported` · `shared_control_allowed` · `independent_controls_allowed` · `overlapping_campaigns_allowed` · `assignment_collision_policy` · `concurrency_blocking_reasons` · `bridge_required_for_concurrency`

**Rules:**

- **Supergeo designs** create new units → **`restricted`** or **`blocked_without_bridge`** for ordinary concurrent multi-experiment use unless bridge-approved.  
- **Trimmed/thinning designs** that alter eligible population → **`restricted`** or **`compatible_with_constraints`**; exclusion policy and population shift must be governed.  

---

## 12. Geometry fields

Canonical IDs from [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) §5:

| `geometry_id` | Typical design source |
|---------------|----------------------|
| `unit_panel_single_cell` | Geo tier-1 assignment dict, single cell |
| `aggregate_two_row` | PowerAnalysis MDE path aggregation |
| `pooled_treated_control_panel` | Pooled arm construction (DID context) |
| `multi_cell_per_cell` | `n_test_grps > 1` per-cell sub-geometry |
| `pooled_multi_cell` | **Blocked** without bridge |
| `supergeo` | SupergeoModel output |
| `trimmed_geometry` | TrimmedMatchDesign output |
| `time_series_operator_geometry` | Operator / forecast layouts |

| Field | Required |
|-------|----------|
| `geometry_id` | **Yes — hard BLOCK if missing** |
| `assignment_geometry` | Post-design layout description |
| `estimator_input_geometry` | Expected estimator panel shape |
| `inference_geometry_hint` | Inference layout hint |
| `reporting_geometry_hint` | Product readout layout |
| `geometry_transform_used` | Boolean |
| `geometry_transform_type` | e.g. `none` · `aggregate` · `supergeo` · `trim` |
| `bridge_required` | Boolean |
| `bridge_artifact_id` | When bridged |
| `blocked_geometry_reason` | When blocked |

---

## 13. Block / stratum / pair fields

Required **when applicable**:

| Field | Applies to |
|-------|------------|
| `block_ids` | QuickBlock, blocking designs |
| `block_variables` | Block construction covariates |
| `block_construction_rule` | Algorithm reference |
| `within_block_assignment_rule` | Randomization within block |
| `treated_count_by_block` | Per-block counts |
| `control_count_by_block` | Per-block counts |
| `stratum_ids` | StratifiedRandomization |
| `stratum_variables` | Strata definition |
| `pair_ids` | TrimmedMatch, MatchedPair |
| `pairing_rule` | Pair construction |
| `inference_must_respect_blocks` | Boolean hint |
| `inference_must_respect_pairs` | Boolean hint |

---

## 14. Donor-pool and eligibility fields

| Field | Required |
|-------|----------|
| `donor_pool_units` | Control units eligible as donors |
| `donor_pool_by_cell` | When multi-cell |
| `donor_exclusion_rules` | Documented rules |
| `donor_pool_size` | Count |
| `minimum_control_support_met` | Boolean + threshold |
| `minimum_donor_support_met` | Boolean (≥2 for SCM+JK) |
| `control_support_diagnostics` | Structured diagnostics |
| `donor_pool_diagnostics` | Overlap, thin pool flags |

**Separation note (MAT-004):** design matching stage ≠ SCM donor pool at estimation — both must be documented.

---

## 15. Trim / thinning fields

Required **when** `trim_or_thin_used` is true:

| Field | Notes |
|-------|-------|
| `trim_or_thin_used` | Boolean |
| `trim_policy` | TrimmedMatch rules |
| `thinning_policy` | ThinningDesign kernel/rule |
| `trimmed_units` / `thinned_units` / `excluded_units` | Lists |
| `exclusion_reason_by_unit` | Map |
| `trim_scope` / `thinning_scope` | `global` · `cell` · `pair` |
| `global_vs_cell_specific_trim` | Enum |
| `target_population_pre_trim` / `post_trim` | Named populations |
| `full_population_claim_allowed` | Default **false** |
| `full_population_bridge_required` | Default **true** when population changed |

**Clarification:** Trimmed/thinned-scope claims ≠ full-population claims. Full-population claims **blocked without bridge** ([`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) §14).

**ThinningDesign** (kernel thinning) may not exclude units — `thinning_policy` must document whether assignment space only is thinned vs units removed.

---

## 16. Supergeo fields

Required **when** `supergeo_used` is true:

| Field | Notes |
|-------|-------|
| `supergeo_used` | Boolean |
| `supergeo_ids` | Constructed unit IDs |
| `supergeo_source_unit_map` | **Required — hard BLOCK if missing** |
| `supergeo_construction_rule` | MILP / heuristic reference |
| `supergeo_aggregation_weights` | Sum/mean/weighted |
| `source_units_per_supergeo` | Cardinality map |
| `original_unit_claim_allowed` | Default **false** |
| `original_unit_bridge_required` | Default **true** |
| `supergeo_spillover_assumption` | Declared or `unknown` |
| `supergeo_power_mde_adjustment` | Document MDE geometry mismatch |

**Clarification:** Supergeo **creates new experimental units**. Original-geo claims **blocked without bridge** ([`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) §13).

---

## 17. Balance diagnostics

| Field | Required |
|-------|----------|
| `pre_period_outcome_balance` | Structured metrics |
| `covariate_balance` | When covariates used |
| `seasonality_balance` | When applicable |
| `trend_balance` | Pre-period trend comparison |
| `spend_balance` | When spend data used |
| `baseline_kpi_balance` | Primary KPI balance |
| `imbalance_score` | Scalar from `design_metrics.imbalance` or equivalent |
| `balance_metric_name` | e.g. `l2`, `l1` |
| `balance_thresholds` | Declared thresholds |
| `balance_pass_warn_fail` | PASS · WARN · FAIL |
| `balance_failure_reasons` | When WARN/FAIL |

---

## 18. Power and MDE fields

| Field | Required when power/MDE computed |
|-------|----------------------------------|
| `power_analysis_available` | Boolean |
| `mde_available` | Boolean |
| `power_method` | e.g. `simulation_coverage` |
| `mde_method` | Per `MDE_SEMANTICS` in `power.py` |
| `minimum_detectable_effect` | Grid result |
| `target_power` | Threshold used |
| `alpha` | Significance level |
| `test_duration` | Period count |
| `pre_period_length` | Period count |
| `post_period_length` | Period count |
| `expected_effect_scale` | Per readout semantics |
| `power_assumptions` | Estimator, inference dependency |
| `mde_assumptions` | Simulation grid, window sampling |
| `power_mde_warnings` | From `PowerContract.warnings` |

**Note:** Geo `PowerAnalysis` often uses **aggregate 2-row** geometry — must not be silently equated to unit-panel SCM readout (D5-POW vs D5-STAT gap).

---

## 19. Time-window fields

| Field | Required |
|-------|----------|
| `pre_period_start` / `pre_period_end` | Labels or indices |
| `test_period_start` / `test_period_end` | Labels or indices |
| `cooldown_period` | When applicable |
| `blackout_periods` | When applicable |
| `seasonality_flags` | Metadata |
| `holiday_flags` | Metadata |
| `time_index_field` | Column name |
| `frequency` | e.g. `W`, `D` |

**INV-D1-001:** pre-period matching must reference sliced window via `slice_wide_to_time_period` semantics.

---

## 20. Outcome / covariate metadata

| Field | Required |
|-------|----------|
| `primary_outcome` | Column name |
| `secondary_outcomes` | List |
| `kpi_family` | Business KPI category |
| `covariate_fields` | Available covariates |
| `required_covariates` | For design method |
| `optional_covariates` | List |
| `missing_covariate_policy` | fail · impute · omit |
| `outcome_transform_hint` | level · log · percent |
| `scale_hint` | Aligns with readout semantics |

---

## 21. Estimator and inference compatibility hints

| Field | Required |
|-------|----------|
| `estimator_compatibility_hints` | List of `{estimator, geometry, status}` |
| `inference_compatibility_hints` | List of `{inference, status}` |
| `known_blocked_estimators` | Explicit blocks |
| `known_blocked_inference_methods` | Explicit blocks |
| `requires_block_aware_inference` | Boolean |
| `requires_pair_aware_inference` | Boolean |
| `requires_geometry_bridge` | Boolean |
| `requires_readout_semantics` | Boolean — always true for causal readout |
| `requires_design_specific_validation` | Boolean |

**Clarification:** Hints are **not** suitability approval. [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) remains authority.

---

## 22. Future TROP / triply robust support fields

**Future metadata only** — TROP remains deferred ([`TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md`](TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md)):

| Field | Purpose |
|-------|---------|
| `assignment_model_available` | Propensity / assignment mechanism |
| `assignment_probability_available` | Per-unit probabilities |
| `covariate_panel_available` | Unit × time covariates |
| `selection_model_metadata_available` | Eligibility / transport |
| `eligibility_model_metadata_available` | Inclusion rules |
| `transport_target_population` | Transport estimand population |
| `positivity_diagnostics_available` | Overlap checks |
| `cross_fitting_groups_available` | Sample splits |

No current design is authorized to populate these for production use.

---

## 23. Future Bayesian support fields

**Future metadata only** — Bayesian deferred until `BAYESIAN_METHOD_SPECIFICATION_001`:

| Field | Purpose |
|-------|---------|
| `hierarchical_grouping_fields` | Group structure |
| `pooling_structure_hint` | Partial pooling layout |
| `prior_information_available` | Declared priors |
| `likelihood_family_hint` | Model family |
| `posterior_estimand_hint` | Target quantity |
| `bayesian_geometry_hint` | Hierarchical geometry ID |

---

## 24. Forbidden downstream claims

**Required fields:** `forbidden_downstream_claims` (list) · `forbidden_reason_codes` (map code → description)

**Standard forbidden claims (always include until explicit gates pass):**

| Claim | Reason code |
|-------|-------------|
| No suitability claim | `no_suitability_claim` |
| No TrustReport role | `no_trustreport_role` |
| No CalibrationSignal eligibility | `no_calibration_signal` |
| No MMM calibration use | `no_mmm_calibration` |
| No LLM recommendation use | `no_llm_recommendation` |
| No pooled causal claim without bridge | `no_pooled_causal_without_bridge` |
| No pooled interval without bridge | `no_pooled_interval_without_bridge` |
| No full-population claim after trim without bridge | `no_trim_generalization_without_bridge` |
| No original-geo claim after supergeo without bridge | `no_supergeo_original_geo_without_bridge` |

Design-specific forbidden claims may extend this list (e.g. aggregate MDE → unit-panel SCM).

---

## 25. Contract validation checks

Future `DESIGN_IMPLEMENTATION_VALIDATION_001` and harness validators must assert:

| Check | Severity |
|-------|----------|
| Required fields present per design family | BLOCK |
| Unit identity preserved unless transform declared | BLOCK |
| `geometry_id` present | BLOCK |
| Treated/control labels present | BLOCK |
| No duplicate assignments | BLOCK |
| No missing eligible units unless in `excluded_units` | BLOCK |
| Excluded units documented with reasons | BLOCK |
| Cell metadata when `n_cells > 1` | BLOCK |
| Shared-control policy when `shared_control_used` | BLOCK |
| Block IDs when block design | BLOCK |
| Supergeo source map when `supergeo_used` | BLOCK |
| Trim/thin metadata when `trim_or_thin_used` | BLOCK |
| Balance diagnostics present | WARN if missing |
| Power/MDE metadata when analysis run | WARN if missing |
| `forbidden_downstream_claims` present | PASS requirement |
| Bridge status when `bridge_required` | BLOCK |

---

## 26. Pass / warn / block policy

| Status | Definition |
|--------|------------|
| **PASS** | Contract complete; no BLOCK triggers; downstream **research/characterization** may consume with forbidden claims enforced |
| **WARN** | Non-critical metadata missing; **no** product/suitability/TrustReport consumption |
| **BLOCK** | Required identity/geometry/assignment fields missing, or bridge-required condition undocumented |

**Hard BLOCK examples:**

- Missing `geometry_id`  
- Missing treated/control labels  
- Missing unit IDs  
- Hidden excluded units  
- Supergeo without `supergeo_source_unit_map`  
- Trim/thin without exclusion policy  
- Multi-cell without `cell_ids`  
- Shared control without `control_reuse_policy`  
- Concurrent use declared without `concurrent_multi_experiment_compatibility`  

**PASS does not imply** suitability, promotion, or TrustReport eligibility.

---

## 27. Relationship to design audit ladder

This artifact is the **first concrete output contract** under [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md). It **feeds**:

| Next artifact | Use of contract |
|---------------|-----------------|
| **`DESIGN_CODE_INVENTORY_001`** | ✅ Maps which fields each implementation emits today vs required — [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) |
| **`DESIGN_LITERATURE_ALIGNMENT_001`** | ✅ Align population/assignment semantics to literature — [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) |
| **`DESIGN_IMPLEMENTATION_VALIDATION_001`** | ✅ Validate emission against §25 checks — [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) |
| **`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001`** | ✅ Assert contract completeness or scoped BLOCK in simulation worlds — [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) |
| **`DESIGN_COMBINATION_VALIDATION_MATRIX_001`** | ✅ Rows consume design output fields — [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) |
| **`DESIGN_GUARDRAILS_001`** | ✅ Hard blockers reference forbidden claims — [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md); **missing required contract fields are BLOCK conditions** per §12 |
| **`DESIGN_SUITABILITY_FRAMEWORK_001`** | ✅ Suitability requires contract completeness — [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) |
| **`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001`** | ✅ **Defines implementation phases** — [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) |
| **`DESIGN_CONTRACT_SCHEMA_001`** | ✅ **Defines schema representation** of contract fields — [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) |

**Enforcement plan note:** [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) sequences schema → tier-1 emission → validation tests → adapters → bridge metadata → runtime enforcement. **No field in this contract is enforced in code until those phases complete.**

**Tier-1 emission implementation plan:** [`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md) ✅ **Accepted** — design outputs **will eventually include** nested `design_contract` per this schema; **plan-only artifact; not implemented in code**; 0/31 contract-complete unchanged.

**Guardrail note:** Missing required fields in §25 → **BLOCK** per [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) §12.

---

## 28. Relationship to future experiment recommendation

Parked per [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md):

| Artifact | Requires this contract |
|----------|------------------------|
| `EXPERIMENT_RECOMMENDATION_CONTRACT_001` | Yes — recommended package cites design output |
| `DESIGN_CANDIDATE_RANKING_POLICY_001` | Yes — hard filters use geometry/concurrency fields |
| `EXPERIMENT_PLANNING_DECISION_SURFACE_001` | Yes — decision surface embeds contract summary |

No experiment-planning artifact may proceed until design outputs satisfy this schema (validation TBD in implementation phase).

---

## 29. Current status of discovered designs

All rows: **`contract_required`** · **`not_contract_validated`** · **not suitability-approved**. No design is **`contract_complete`** in code today.

| Name | Category | Expected key fields | Likely blockers | Concurrency | Next audit artifact |
|------|----------|---------------------|-----------------|-------------|---------------------|
| greedy_match_markets | matching | assignment, geometry, donor pool, balance | partial metadata only | compatible_with_constraints | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| CompleteRandomization | standard | assignment, geometry, donor pool | partial metadata | compatible_with_constraints | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| BalancedRandomization | standard | assignment, geometry, balance KPI | partial metadata | compatible_with_constraints | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| StratifiedRandomization | stratified | + stratum_ids | stratum IDs not emitted | compatible_with_constraints | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| ThinningDesign | thinning | + thinning_policy | thinning metadata gap | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| Rerandomization | wrapper | inherits base + imbalance | wrapper identity | compatible_with_constraints | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| QuickBlock | blocking | + block_ids | not geo-run; block IDs absent | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| MatchedPair | matching | pair_ids, numpy vector | non-dict output | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| TrimmedMatchDesign | trimmed | trim fields, pair_ids | population shift; no flat dict | restricted | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| SupergeoModel | supergeo | supergeo_source_unit_map | MILP pairs ≠ assignment dict | blocked_without_bridge | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| multi_test_groups | multi_cell | cell_ids, shared_control_policy | cell metadata partial in D5 | restricted | DESIGN_COMBINATION_VALIDATION_MATRIX_001 |
| GeoExperimentDesign | orchestration | full contract envelope | emits partial DesignEvidence | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| run_geo_experiment_design | orchestration | pipeline metadata | no contract object | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| PowerAnalysis | power_mde | power/MDE §18; aggregate geometry | 2-row vs unit-panel mismatch | not_evaluated | DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001 |
| prepare_constraint_context | eligibility | excluded_units, eligible_units | not surfaced as contract | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| validate_assignment_dict | eligibility | assignment checks | validator only | not_evaluated | DESIGN_GUARDRAILS_001 |
| validate_design | validation | balance_pass_warn_fail | partial validation_summary | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| slice_wide_to_time_period | helper | time-window refs | helper only | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| imbalance | helper | imbalance_score | helper only | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| make_generator | helper | random_seed | helper only | not_evaluated | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DesignRegistry | registry | design_method_id lookup | registry only | not_evaluated | DESIGN_GUARDRAILS_001 |
| create_design_comparison_dashboard | utility | ranking outputs ungoverned | not in contract path | not_evaluated | DESIGN_GUARDRAILS_001 |

---

## 30. Governance gates

| Gate | Status |
|------|--------|
| This artifact validates designs | **No** — schema only |
| This artifact promotes designs | **No** |
| This artifact authorizes estimator/inference combinations | **No** |
| TrustReport / CalibrationSignal / MMM / LLM | **Blocked** |
| Future consumption | Requires contract validation PASS + design audit ladder + suitability role |

---

## 31. Completion checklist

| Item | Status |
|------|--------|
| Prior docs inspected | ✅ |
| Design modules inspected (`panel_exp/design/`, evidence, geo_runner) | ✅ |
| Contract schema defined (§6–§24) | ✅ |
| Concurrency rules defined (§11) | ✅ |
| Geometry fields aligned with geometry bridge (§12) | ✅ |
| TROP/Bayesian future metadata (§22–§23) | ✅ |
| Experiment recommendation lane parked (§28) | ✅ |
| Roadmap/audit docs updated | ✅ |
| No code changed | ✅ |
| Tests run | ✅ |

---

## 32. Roadmap and audit updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | First concrete output contract complete |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Statistical protocol Accepted; next = DESIGN_COMBINATION_VALIDATION_MATRIX_001 |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Design-output contract prerequisite |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | State updated |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Metadata gap cross-link |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Suitability requires contract |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Matrix consumes contract fields |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Design validation asserts completeness |
| [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md) | Prerequisite marked Accepted |

**D5 reports inspected:** SCM-JK, AugSynth point, TBR aggregate, DID bootstrap, MCELL per-cell, TBRRidge inference; D5-POW/D5-DES supergeo/trim; design inventory 001.

---

**Literature alignment:** [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) reinforces required fields for assignment, geometry, target population, block/stratum/pair IDs, trim/supergeo metadata, concurrency, balance, power/MDE, and forbidden claims.

**Implementation validation:** [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) evaluated current emitted fields against this contract — **0/31 contract-complete; not implemented repo-wide**.

**Statistical validation:** [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) requires contract completeness or explicit scoped BLOCK per simulation world (§25); **no repo-wide contract PASS**.

---

**Tier-1 emission plan:** [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) ✅ **Accepted** — maps contract fields to geo-run producer paths; **not implemented**; 0/31 contract-complete; no downstream authorization.

**Validation test plan:** [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) ✅ **Accepted** — contract fields require schema validation tests before governed product consumption; **tests not implemented**.

*DESIGN-OUTPUT-CONTRACT-001 v1.1.1 — Validation tests planned; next = DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.*
