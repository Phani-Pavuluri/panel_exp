# Design Statistical Validation Protocol 001

**Document ID:** DESIGN-STATISTICAL-VALIDATION-PROTOCOL-001  
**Title:** Design Statistical Validation Protocol 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` design statistical validation protocol  
**Artifact type:** Documentation / governance / statistical validation protocol — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md)

**Inputs:** [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) · [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) · [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) · [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md)

**Method-side counterpart:** [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) (estimator/inference Layer 4)

**Guardrails:** No validation execution · no harness implementation · no contract adapters · no archive regeneration · no design promotion · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Statistical Validation Protocol 001 |
| Status | **Accepted** |
| Scope | GeoX / `panel_exp` design statistical validation protocol |
| Artifact type | Documentation / governance / statistical validation protocol |

Fourth concrete design audit artifact. Defines **how** design methods will be statistically characterized across simulation worlds, diagnostics, metrics, and pass/warn/block rules **before** suitability, combination-matrix promotion, or downstream product use.

**This artifact defines protocol only. No design has been statistically validated by this artifact.**

---

## 2. Purpose

This artifact answers:

1. Which **simulation worlds** and stress conditions apply to each inventory design row?  
2. Which **diagnostics** and **metrics** must future harnesses record?  
3. What **pass/warn/block** rules govern future design statistical validation?  
4. Which designs are **eligible**, **adapter-scoped**, **blocked**, or **helper-only** given **observed** implementation behavior?  
5. What **future harness artifacts** (e.g. `D5-DES-STAT-*`) are required before combination-matrix or suitability rows may advance?

Design statistical validation tests **assignment quality, support, balance, population semantics, and contract completeness** — not causal readout error rates (those belong to estimator/inference validation).

---

## 3. Why this artifact exists

| Prior artifact | Provided |
|----------------|----------|
| [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) | 31 DES rows; emitted-field mapping; **0 contract-complete** |
| [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) | Conceptual families; G-DES-001–014 open gaps |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | Observed behavior; adapter-required paths; hard blockers |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Required governed metadata envelope |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Estimator/inference OC worlds — **does not substitute** for design-side validation |

Without this protocol, future simulations would risk testing **intended design names** rather than **observed assignment paths**, repeating the gap closed by implementation validation.

**Protocol definition ≠ statistical validation ≠ suitability approval.**

---

## 4. Scope

Includes protocol rows for:

- Registered design methods (9 registry keys) + `Rerandomization` wrapper  
- Tier-1 geo-run supported designs (`balancedrandomization`, `completerandomization`, `greedy_match_markets`, `stratifiedrandomization`, `thinningdesign`)  
- Adapter-required designs (`quickblock`, `matchedpair`, `trimmedmatch`, `supergeos`)  
- Multi-test-group / shared-control logic (`n_test_grps > 1`)  
- Power/MDE helpers (`PowerAnalysis`, `PowerContract`)  
- Validation/output objects (`DesignEvidence`, `ExperimentEvidence`, `DesignSpec`) where they affect auditable design output  
- Trim/supergeo special geometries (bridge-gated)  
- Block/stratum/pair designs (`QuickBlock`, `MatchedPair`, `StratifiedRandomization`)

**Evidence basis (not statistical proof):** D5-DES-TRIM-001 · D5-DES-SUPERGEO-001 · D5-POW-001e · Track D design inventory reports.

---

## 5. Non-goals

- No actual validation execution or D5-DES-STAT archive generation  
- No design, estimator, or inference code changes  
- No contract adapters or `DesignEvidence` envelope fixes  
- No design promotion, suitability claim, or production-ready claim  
- No TrustReport, CalibrationSignal, MMM, or LLM authorization  
- No claim that defining worlds validates any design  

---

## 6. Protocol status taxonomy

| Status | Meaning |
|--------|---------|
| `protocol_defined_not_executed` | Row has defined worlds/metrics; no OC archive exists |
| `eligible_for_future_validation` | Observed path auditable; may enter tier-1 or scoped harness after preconditions |
| `eligible_with_contract_adapter` | Behavior characterizable only after output adapter + scoped harness |
| `blocked_until_contract_fields` | Missing required contract fields (`geometry_id`, `forbidden_downstream_claims`, etc.) |
| `blocked_until_geometry_bridge` | Trim/supergeo/pooled transitions require bridge ADR |
| `blocked_until_semantics_clarified` | Population/geometry semantics ambiguous in implementation |
| `helper_not_directly_validated` | Support component; validated only via parent design path |
| `superseded_or_historical` | Prior generator superseded |

**Default for all DES rows in this artifact:** `protocol_defined_not_executed`.

---

## 7. Validation result taxonomy (future execution)

| Result | Meaning |
|--------|---------|
| `design_stat_validation_pass` | Required diagnostics + contract fields present for declared scope |
| `design_stat_validation_pass_with_caveats` | Auditable with documented partial contract or balance gaps |
| `design_stat_validation_mixed_requires_followup` | Mixed worlds; characterization only |
| `design_stat_validation_fail` | Assignment infeasible, non-auditable, or contract BLOCK triggered |
| `design_stat_validation_blocked` | Preconditions unmet; harness must not claim validation |
| `not_evaluated` | No execution attempted |

**Even `design_stat_validation_pass` does not imply suitability, promotion, TrustReport, CalibrationSignal, MMM, or LLM authorization.**

---

## 8. Design scope table

**Source of implementation status:** [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) §9.

**Downstream status (all rows):** `not_statistically_validated` · `not_suitability_approved` · `not_contract_complete` (unless future execution proves otherwise within scope).

| ID | Name | Impl. status | Protocol eligibility | Validation scope | Required preconditions | Excluded claims | Future harness target |
|----|------|--------------|---------------------|------------------|------------------------|-----------------|----------------------|
| DES-001 | greedy_match_markets | impl_aligned_contract_partial | eligible_for_future_validation | Tier-1 geo dict path; matched-market worlds | Pre-period slice when configured; constraint context | Production-ready; flat readout without bridge | `D5-DES-STAT-TIER1-001` |
| DES-002 | CompleteRandomization | impl_aligned_contract_partial | eligible_for_future_validation | Tier-1 Bernoulli assignment dict | Exclusivity validation path | π-in-evidence assumed | `D5-DES-STAT-TIER1-001` |
| DES-003 | BalancedRandomization | impl_partially_aligned_contract_partial | eligible_for_future_validation | Tier-1 volume-balance dict | KPI volume columns present | Bernoulli π semantics | `D5-DES-STAT-TIER1-001` |
| DES-004 | StratifiedRandomization | impl_partially_aligned_contract_partial | blocked_until_contract_fields | Tier-1 strata + balance | **stratum_ids** emission or scoped BLOCK | Stratum-aware inference without metadata | `D5-DES-STAT-TIER1-001` |
| DES-005 | ThinningDesign | impl_behavior_ambiguous | blocked_until_semantics_clarified | Tier-1 dict only after thinning policy ADR | Candidate-space vs exclusion clarified | Population exclusion claims | `D5-DES-STAT-TIER1-001` (scoped) |
| DES-006 | Rerandomization | impl_aligned_contract_partial | eligible_for_future_validation | Geo wrapper over tier-1 bases | Rerandomization identity in evidence | Bare-base equivalence without caveat | `D5-DES-STAT-TIER1-001` |
| DES-007 | QuickBlock | adapter_required | eligible_with_contract_adapter | Block/pair harness after adapter | numpy→dict adapter; `block_ids` | Geo-run production path | `D5-DES-STAT-BLOCK-PAIR-001` |
| DES-008 | MatchedPair | adapter_required | eligible_with_contract_adapter | Pair harness after adapter | `pair_ids` emission | Geo-run without adapter | `D5-DES-STAT-BLOCK-PAIR-001` |
| DES-009 | TrimmedMatchDesign | adapter_required | blocked_until_geometry_bridge | Trim pair population | F-GEO-004 bridge; trim metadata | Full-population SCM+JK | `D5-DES-STAT-TRIM-001` |
| DES-010 | SupergeoModel | adapter_required | blocked_until_geometry_bridge | Supergeo MILP output | F-GEO-003 bridge; source-unit map | Original-geo unit-panel claims | `D5-DES-STAT-SUPERGEO-001` |
| DES-011 | multi_test_groups | impl_partially_aligned_contract_partial | blocked_until_contract_fields | Per-cell assignment only | `cell_ids`; shared-control policy | Pooled/portfolio lift | `D5-DES-STAT-MULTICELL-001` |
| DES-012 | GeoExperimentDesign | helper_not_design_family | helper_not_directly_validated | Via tier-1 child design | Child design eligibility | Standalone design family | Inherited from child |
| DES-013 | run_geo_experiment_design | helper_not_design_family | helper_not_directly_validated | Pipeline orchestration audit | Registry dispatch | — | Harness integration only |
| DES-014 | PowerAnalysis | impl_partially_aligned_contract_partial | eligible_for_future_validation | MDE simulation worlds | Geometry consistency (unit vs 2-row) | Linked to final design envelope | `D5-DES-STAT-POWER-MDE-001` |
| DES-015 | PowerContract | helper_not_design_family | helper_not_directly_validated | Via PowerAnalysis linkage | Joined to DesignEvidence | Standalone power claim | `D5-DES-STAT-POWER-MDE-001` |
| DES-016 | prepare_constraint_context | helper_not_design_family | helper_not_directly_validated | Eligible/excluded accounting | Surfaced in contract | — | Tier-1 precondition |
| DES-017 | validate_assignment_dict | helper_not_design_family | helper_not_directly_validated | Exclusivity/collision checks | Results in contract or harness | — | Tier-1 diagnostic |
| DES-018 | validate_design | helper_not_design_family | helper_not_directly_validated | PASS/WARN/FAIL gate | Partial balance in summary | — | Guardrails input |
| DES-019 | slice_wide_to_time_period | helper_not_design_family | helper_not_directly_validated | Pre-period window | Time window in evidence | — | Tier-1 precondition |
| DES-020 | imbalance | helper_not_design_family | helper_not_directly_validated | Rerandomization metric | Emitted in evidence | — | Rerandomization worlds |
| DES-021 | make_generator | helper_not_design_family | helper_not_directly_validated | Reproducibility | `reproducibility_hash` | — | All harnesses |
| DES-022 | DesignRegistry | helper_not_design_family | helper_not_directly_validated | Registry introspection | — | — | Guardrails |
| DES-023 | balanced_volume_assign | helper_not_directly_validated | helper_not_directly_validated | Primitive under DES-003 | — | — | Tier-1 |
| DES-024 | bernoulli_complete_assign | helper_not_directly_validated | helper_not_directly_validated | Primitive under DES-002 | — | — | Tier-1 |
| DES-025 | create_design_comparison_dashboard | helper_not_design_family | helper_not_directly_validated | MLflow UI only | — | Governed claims | Guardrails |
| DES-026 | DesignEvidence | helper_not_design_family | blocked_until_contract_fields | Contract envelope | geometry_id; forbidden_claims | Contract-complete platform | Contract coverage table |
| DES-027 | ExperimentEvidence | helper_not_design_family | blocked_until_contract_fields | Wraps DES-026 | Same | Same | Contract coverage table |
| DES-028 | DesignSpec | helper_not_design_family | helper_not_directly_validated | Partial identity | contract_id/version | — | Harness seed input |
| DES-029 | DesignMethod enum | helper_not_design_family | helper_not_directly_validated | Taxonomy only | — | — | — |
| DES-030 | DesignProfile | helper_not_design_family | helper_not_directly_validated | F-DECISION input | — | Suitability output | Suitability framework |
| DES-031 | track_d_design_inventory_001 | superseded_or_historical | superseded_or_historical | Historical only | — | — | — |

**Contract-complete designs at protocol authoring:** **0 / 31**

---

## 9. Tier-1 geo-run validation scope

**Callable path:** `run_geo_experiment_design` → assignment **dict** (`control`, `test_0`, …) via registered tier-1 designs.

| Design | Observed path | Primary worlds | Contract caveat |
|--------|---------------|----------------|-----------------|
| greedy_match_markets | Dict; pre-period slice optional | `balanced_markets`, `matched_market_poor_match_world`, `weak_donor_pool` | No `geometry_id` |
| CompleteRandomization | Bernoulli dict | `complete_randomization_unbalanced_covariate_world`, `assignment_infeasibility` | π not in evidence |
| BalancedRandomization | Volume-balance dict | `balanced_randomization_volume_dominance_world`, `spend_imbalance` | Not Bernoulli family |
| StratifiedRandomization | Strata + balance dict | `stratified_bad_strata_world` | **No stratum_ids** |
| ThinningDesign | Norm-weight dict | `thinning_candidate_shift_world` | Semantics ambiguous |
| Rerandomization | Wrapper loop | `rerandomization_selection_effect_world` | Base name in evidence |
| multi_test_groups | `test_0..n-1` + shared `control` | `multi_cell_shared_control_overload_world`, `many_test_groups_world` | No cell_ids / reuse policy |

**First execution priority:** `D5-DES-STAT-TIER1-001` — common dict output enables shared harness scaffolding, but all tier-1 rows remain **contract-incomplete** until contract-coverage table passes or explicit scoped BLOCK is recorded.

---

## 10. Adapter-required validation scope

| Design | Output shape | Adapter requirement | Harness |
|--------|--------------|---------------------|---------|
| QuickBlock | numpy vector | Dict adapter + `block_ids` | `D5-DES-STAT-BLOCK-PAIR-001` |
| MatchedPair | numpy vector | Dict adapter + `pair_ids` | `D5-DES-STAT-BLOCK-PAIR-001` |
| TrimmedMatchDesign | pair DataFrame / dict | Bridge F-GEO-004 + trim metadata adapter | `D5-DES-STAT-TRIM-001` |
| SupergeoModel | MILP DataFrame | Bridge F-GEO-003 + `supergeo_source_unit_map` | `D5-DES-STAT-SUPERGEO-001` |

**Rule:** Full design statistical validation on adapter-required paths is **`eligible_with_contract_adapter` only**. Harnesses may run **characterization** sub-batteries on raw outputs if labeled `design_stat_validation_blocked` for governed downstream use.

---

## 11. Blocked/ambiguous validation scope

| Blocker | Affected rows | Clarification required |
|---------|---------------|------------------------|
| Thinning semantics (G-DES-002) | DES-005 | Candidate-space thinning vs population exclusion |
| Supergeo bridge (F-GEO-003) | DES-010 | Unit-panel readout from supergeo geometry |
| Trim bridge (F-GEO-004) | DES-009 | Flat readout vs trimmed target population |
| Pooled multi-cell (F-MCELL-001) | DES-011 | Pooled lift ADR; per-cell only until bridge |
| Shared-control policy gap | DES-011 | `shared_control_policy`, control reuse burden |
| Missing `geometry_id` | DES-001–006, tier-1 | All geometry-scoped claims |
| Missing `forbidden_downstream_claims` | All design families | TrustReport/CalibrationSignal gates |
| Missing `concurrent_multi_experiment_compatibility` | All tier-1 | Concurrent experiment claims |
| No design contract-validation tests | Repo-wide | Harness must add contract coverage assertions |

---

## 12. Core validation worlds

Baseline simulation worlds applicable across eligible tier-1 and adapter-scoped designs:

| World ID | Intent |
|----------|--------|
| `balanced_markets` | Symmetric markets; baseline balance reference |
| `weak_donor_pool` | Few viable controls; donor support stress |
| `high_unit_heterogeneity` | Scale dispersion across units |
| `small_n_markets` | Low unit count feasibility |
| `high_pre_period_noise` | Noisy pre-treatment outcomes |
| `strong_seasonality` | Seasonal pattern mismatch risk |
| `trend_mismatch` | Divergent pre-period trends |
| `sparse_outcomes` | Zero-inflated or sparse KPIs |
| `spend_imbalance` | Spend/volume concentration |
| `geographic_cluster_correlation` | Spatial correlation among units |
| `assignment_infeasibility` | Constraint-induced infeasible draws |
| `missing_covariates` | Incomplete matching/blocking inputs |
| `outlier_markets` | Heavy-tail unit behavior |
| `unstable_pre_period` | Short or volatile pre-period |

**Null companion:** All core worlds must include a **no-effect** variant (§18) for design-balance characterization.

---

## 13. Design-family-specific worlds

| World ID | Target family / row |
|----------|---------------------|
| `matched_market_poor_match_world` | DES-001 greedy_match_markets |
| `complete_randomization_unbalanced_covariate_world` | DES-002 |
| `balanced_randomization_volume_dominance_world` | DES-003 |
| `stratified_bad_strata_world` | DES-004 |
| `quickblock_bad_block_world` | DES-007 |
| `matchedpair_pair_mismatch_world` | DES-008 |
| `rerandomization_selection_effect_world` | DES-006 |
| `thinning_candidate_shift_world` | DES-005 |
| `trimming_target_shift_world` | DES-009 |
| `supergeo_aggregation_distortion_world` | DES-010 |
| `multi_cell_shared_control_overload_world` | DES-011 |
| `many_test_groups_world` | DES-011 (`n_test_grps` high) |
| `pooled_claim_trap_world` | DES-011 — must BLOCK pooled claims |
| `power_mde_miscalibration_world` | DES-014 PowerAnalysis |

Literature-aligned failure modes from [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) §21–§22 map into these worlds (G-DES-001–014).

---

## 14. Required diagnostics

Future harnesses must record (per design scope):

| Diagnostic | Applies when |
|------------|--------------|
| Pre-period outcome balance | All tier-1 matching/randomization |
| Covariate balance | Matching, stratified, rerandomization |
| Trend balance | All tier-1 |
| Seasonality balance | Seasonal KPI panels |
| Spend balance | Volume-balanced designs |
| Baseline KPI balance | All |
| Control support | All |
| Donor-pool support | Matching designs |
| Eligible/excluded unit accounting | Trim/thin/constraints |
| Assignment exclusivity | Dict path |
| Duplicate assignment checks | Multi-cell |
| Missing assignment checks | All |
| Cell balance | multi_test_groups |
| Shared-control burden | multi_test_groups |
| Block/stratum/pair balance | QuickBlock, MatchedPair, Stratified |
| Target-population shift | TrimmedMatch |
| Supergeo distortion | SupergeoModel |
| Trim/thin shift | Thinning, TrimmedMatch |
| Reproducibility | Seeded runs |
| Assignment probability availability | Bernoulli / declared π |
| Geometry consistency | When geometry claim requested |
| Contract completeness | All governed runs |

---

## 15. Required metrics

| Metric | Typical use |
|--------|-------------|
| `imbalance_score` | Rerandomization acceptance |
| `standardized_mean_difference` | Covariate/outcome balance |
| `pre_period_rmse` / `pre_period_mape` | Pre-fit quality |
| `trend_slope_difference` | Trend mismatch worlds |
| `seasonality_mismatch_score` | Seasonal stress |
| `donor_pool_size` | Matching support |
| `control_support_ratio` | Feasibility |
| `assignment_feasibility_rate` | Constraint stress |
| `assignment_collision_rate` | Multi-cell |
| `duplicate_assignment_rate` | Exclusivity |
| `missing_assignment_rate` | Coverage |
| `excluded_unit_rate` | Trim/thin |
| `target_population_drift_score` | Trim |
| `cell_imbalance_score` | Multi-cell |
| `shared_control_overload_score` | Shared control |
| `block_pair_within_group_balance_score` | Block/pair designs |
| `supergeo_aggregation_distortion_score` | Supergeo |
| `trim_thin_population_shift_score` | Thin/trim |
| `power_mde_calibration_error` | PowerAnalysis |
| `reproducibility_failure_rate` | Seed stability |
| `contract_field_coverage_rate` | Contract completeness (§25) |

---

## 16. Family-specific metric requirements

| Family | Required metric subset |
|--------|------------------------|
| Matched-market / greedy (DES-001) | SMD, pre_period_rmse, donor_pool_size, control_support_ratio, trend_slope_difference |
| Complete randomization (DES-002) | SMD, assignment_feasibility_rate, assignment_probability availability |
| Balanced randomization (DES-003) | spend balance, cell_imbalance_score (if multi), volume dominance |
| Stratified/blocking (DES-004, DES-007) | block_pair_within_group_balance_score, stratum balance, SMD within stratum |
| Matched pair (DES-008) | block_pair_within_group_balance_score, pair mismatch rate |
| Rerandomization (DES-006) | imbalance_score, accepted-design identity, candidate draw count |
| Thinning (DES-005) | trim_thin_population_shift_score, excluded_unit_rate |
| Trimmed match (DES-009) | target_population_drift_score, excluded_unit_rate, trim_thin_population_shift_score |
| Supergeo (DES-010) | supergeo_aggregation_distortion_score, source-unit map completeness |
| Multi-cell/shared control (DES-011) | cell_imbalance_score, shared_control_overload_score, collision rates |
| Power/MDE (DES-014) | power_mde_calibration_error, duration/unit sensitivity |

---

## 17. Pass/warn/block rules

Conceptual thresholds (numeric gates proposed until OC calibration):

| Rule | Verdict |
|------|---------|
| Missing assignment labels (`control`, `test_*`) | **BLOCK** |
| Missing `geometry_id` when downstream geometry claim requested | **BLOCK** |
| Hidden excluded units (trim/thin) | **BLOCK** |
| Supergeo without `supergeo_source_unit_map` | **BLOCK** |
| Multi-cell without `cell_ids` or shared-control policy | **BLOCK** |
| Pooled/portfolio lift claim without bridge | **BLOCK** |
| `adapter_required` design used on geo-run path without adapter | **BLOCK** |
| Partial balance diagnostics but auditable assignment | **WARN** |
| MDE documented but not linked to DesignEvidence | **WARN** |
| Rerandomization without inference caveat emission | **WARN** |
| Required diagnostics + contract fields present for scope | **PASS** (future execution only) |

**Contract field coverage:** `contract_field_coverage_rate < 1.0` for governed scope → **WARN** minimum; critical fields missing → **BLOCK** (see §25).

---

## 18. Null / no-effect design validation

Under **no-effect** worlds (`null_no_effect` companion to each core world):

- Design balance must not induce **systematic directional imbalance** detectable by diagnostics  
- Assignment must remain **feasible and auditable**  
- Donor/control support must remain **above documented minimum** (harness-defined)  
- Diagnostics must **flag** weak geometry, poor match, or imbalance risk  

**Clarification:** Causal FPR/FNR belong to [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md). Design validation measures **design-induced imbalance risk** and **support adequacy** only.

---

## 19. Injected-effect design validation

Under injected-effect stress (support preservation, not causal recovery):

- Design must preserve **enough treated/control support** for estimation  
- Assignment structures must not make recovery **impossible by construction** (e.g. zero treated units)  
- Power/MDE assumptions stressed in `power_mde_miscalibration_world`  
- Per-cell support adequate in multi-cell worlds  

---

## 20. Multi-cell/shared-control validation

| Check | Requirement |
|-------|-------------|
| Many test cells | `test_0..n-1` exclusivity |
| One shared control | Control reuse burden metric |
| Independent controls | Only if policy emitted |
| Cell assignment exclusivity | No duplicate unit across cells |
| Collision checks | `assignment_collision_rate` |
| Pooled claim | **BLOCK** unless pooling ADR + bridge |
| Portfolio claim | **BLOCK** unless bridge exists |

Harness: `D5-DES-STAT-MULTICELL-001`.

---

## 21. Trim/thinning validation

| Check | Requirement |
|-------|-------------|
| Excluded/thinned unit accounting | Auditable list or rate |
| Target population pre/post | Drift score |
| Population shift metrics | `trim_thin_population_shift_score` |
| Full-population claim | **BLOCK** without explicit policy |
| Concurrency | **BLOCK** concurrent claims unless emitted |
| Bridge | F-GEO-004 before flat readout combinations |

Harnesses: tier-1 thinning (`D5-DES-STAT-TIER1-001` scoped) · trim (`D5-DES-STAT-TRIM-001`).

---

## 22. Supergeo validation

| Check | Requirement |
|-------|-------------|
| Source-unit map completeness | **BLOCK** if missing |
| Aggregation distortion | `supergeo_aggregation_distortion_score` |
| Source units per supergeo | Minimum support per cluster |
| Power/MDE adjustment | Aggregate geometry consistency |
| Original-geo claim | **BLOCK** |
| Concurrent multi-experiment | **BLOCK** unless bridge + policy |

Harness: `D5-DES-STAT-SUPERGEO-001` (after F-GEO-003).

---

## 23. Rerandomization validation

| Check | Requirement |
|-------|-------------|
| Acceptance threshold | `target_imbalance` documented |
| Candidate draw count | `max_iter` recorded |
| Reproducibility | Seeded rerandomization loop |
| Accepted design identity | **WARN/BLOCK** if only base class name recorded |
| Balance improvement | imbalance_score vs bare base |
| Inference caveat | **WARN** if not emitted (selection bias risk) |

Observed gap: `geo_runner.py` records base design class name — harness must test identity preservation.

---

## 24. Power/MDE validation

| Check | Requirement |
|-------|-------------|
| Simulated MDE calibration | `power_mde_calibration_error` |
| Duration sensitivity | Vary post-period length |
| Unit count sensitivity | Vary panel size |
| Variance assumption sensitivity | Stress variance model |
| Aggregate vs unit geometry | **BLOCK** mismatch vs final readout |
| DesignEvidence linkage | **BLOCK** if power not in envelope |

Harness: `D5-DES-STAT-POWER-MDE-001`. Evidence basis: D5-POW-001e (not auto-pass).

---

## 25. Contract-completeness validation

Required contract checks per [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) (future harness **contract coverage table**):

| Field | Block if missing (governed scope) |
|-------|-----------------------------------|
| `geometry_id` | Yes — geometry claims |
| `forbidden_downstream_claims` | Yes — downstream gating |
| `concurrent_multi_experiment_compatibility` | Yes — concurrency claims |
| Treated/control labels | Yes |
| Unit universe | Yes |
| Excluded units | Yes — trim/thin |
| Cell IDs | Yes — multi-cell |
| Control reuse policy | Yes — shared control |
| Block/stratum/pair IDs | Yes — when applicable |
| Trim/thin metadata | Yes — DES-005/009 |
| Supergeo source map | Yes — DES-010 |
| Power/MDE linkage | Yes — when power run |
| Compatibility hints | WARN if partial |

**Repo status at authoring:** **0** `panel_exp/` matches for `geometry_id`, `forbidden_downstream_claims`, `concurrent_multi_experiment_compatibility`, `shared_control_policy` — all tier-1 governed runs would **BLOCK** on contract completeness until implementation work or explicit scoped characterization with `design_stat_validation_blocked` for downstream use.

---

## 26. Future harness requirements

Expected future execution outputs (not created by this artifact):

| Requirement | Description |
|-------------|-------------|
| Machine-readable JSON archive | Per `D5-DES-STAT-*` artifact |
| Validation runner | `panel_exp/validation/track_d_d5_des_stat_*` (future) |
| Deterministic seeds | Documented per world |
| Simulation world definitions | Catalog from §12–§13 |
| Design candidate outputs | Raw + adapted where applicable |
| Diagnostics table | §14 |
| Contract coverage table | §25 |
| Pass/warn/block summary | §17 |
| Prohibited claim checks | `forbidden_downstream_claims` |
| No silent archive overwrite | Explicit artifact version bump |

---

## 27. Validation artifact naming

Future execution artifacts (protocol-defined; **not executed**):

| Artifact ID | Scope |
|-------------|-------|
| `D5-DES-STAT-TIER1-001` | Tier-1 geo dict designs + rerandomization wrapper |
| `D5-DES-STAT-MULTICELL-001` | `n_test_grps` per-cell paths |
| `D5-DES-STAT-TRIM-001` | TrimmedMatchDesign (post F-GEO-004) |
| `D5-DES-STAT-SUPERGEO-001` | SupergeoModel (post F-GEO-003) |
| `D5-DES-STAT-BLOCK-PAIR-001` | QuickBlock, MatchedPair (post adapter) |
| `D5-DES-STAT-POWER-MDE-001` | PowerAnalysis / PowerContract linkage |

---

## 28. Relationship to estimator/inference validation

| Layer | Responsibility |
|-------|----------------|
| **Design validation (this protocol)** | Assignment quality, balance, support, population semantics, contract completeness |
| **Estimator/inference validation** | Causal readout, intervals, coverage, null FPR — [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) |
| **Combination matrix** | Allowed design × estimator × inference × geometry packages |
| **Rule** | No design validation result alone authorizes causal uncertainty or TrustReport roles |

---

## 29. Relationship to geometry bridge

[`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) governs transitions among `unit_panel_single_cell`, `aggregate_two_row`, `multi_cell_per_cell`, `pooled_multi_cell`, `supergeo`, `trimmed_geometry`.

Protocol marks **bridge-required** transitions as `blocked_until_geometry_bridge` until bridge artifacts exist. Statistical validation must not use flat unit-panel readout claims on supergeo/trim outputs without bridge PASS.

---

## 30. Relationship to experiment planning orchestration

[`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md):

- Future experiment recommendation **cannot rank** designs until `D5-DES-STAT-*` outcomes exist  
- Blocked or adapter-only designs **cannot** score as normal candidates  
- LLM may **explain** protocol gates but **cannot override** validation BLOCK results  

---

## 31. Governance gates

| Gate | Status |
|------|--------|
| Protocol defined | ✅ This artifact |
| Statistical validation executed | ❌ None |
| Design promoted | ❌ None |
| Suitability role assigned | ❌ None |
| TrustReport / CalibrationSignal / MMM / LLM authorized | ❌ None |

---

## 32. Current status and verdict

| Field | Value |
|-------|-------|
| Verdict | `design_statistical_validation_protocol_defined_not_executed` |
| Designs statistically validated | **0 / 31** |
| Contract-complete designs | **0 / 31** |
| Executed harnesses | **0** |

---

## 33. Roadmap

**Next artifact:** **`DESIGN_COMBINATION_VALIDATION_MATRIX_001`** — design × geometry × estimator × inference × readout rows must consume this protocol's eligibility statuses and future `D5-DES-STAT-*` outcomes.

Then: `DESIGN_GUARDRAILS_001` → `DESIGN_SUITABILITY_FRAMEWORK_001`.

---

## 34. Completion checklist

| Item | Status |
|------|--------|
| Prerequisites inspected | ✅ |
| Implementation statuses consumed | ✅ §8 from DESIGN_IMPLEMENTATION_VALIDATION_001 |
| Literature failure modes mapped | ✅ §13 |
| Validation worlds defined | ✅ §12–§13 |
| Diagnostics defined | ✅ §14 |
| Metrics defined | ✅ §15–§16 |
| Pass/warn/block rules defined | ✅ §17 |
| Adapter-required designs scoped | ✅ §10 |
| Blocked/ambiguous designs scoped | ✅ §11 |
| Future harness requirements defined | ✅ §26–§27 |
| Roadmap updated | ✅ companion docs |
| No code changed | ✅ |
| Tests run | ✅ (see completion report) |

---

## 35. Search methodology (2026-06-10)

```bash
grep -R "DESIGN_IMPLEMENTATION_VALIDATION_001\|DESIGN_LITERATURE_ALIGNMENT_001\|DESIGN_CODE_INVENTORY_001" -n docs
grep -R "geometry_id\|forbidden_downstream_claims\|concurrent_multi_experiment_compatibility\|shared_control_policy" -n panel_exp tests docs
grep -R "CompleteRandomization\|BalancedRandomization\|StratifiedRandomization\|ThinningDesign\|Rerandomization\|QuickBlock\|MatchedPair\|TrimmedMatch\|Supergeo\|greedy_match_markets" -n panel_exp tests docs
grep -R "assignment\|treatment\|control\|cell_id\|block_id\|stratum\|pair_id\|supergeo\|trim\|thin\|eligible\|excluded\|donor" -n panel_exp/design panel_exp/evidence.py panel_exp/spec.py tests docs
find tests/track_d -iname "*design*" -o -iname "*des*" -o -iname "*pow*"
find panel_exp/design -type f
poetry run python -c "from panel_exp.design.registry import get_design_registry; print(sorted(get_design_registry().list_names()))"
poetry run python -c "from panel_exp.design.registry import geo_run_design_supported; print(sorted(geo_run_design_supported()))"
```

**Registry keys (9):** `balancedrandomization`, `completerandomization`, `greedy_match_markets`, `matchedpair`, `quickblock`, `stratifiedrandomization`, `supergeos`, `thinningdesign`, `trimmedmatch`

**Geo-run supported (5):** `balancedrandomization`, `completerandomization`, `greedy_match_markets`, `stratifiedrandomization`, `thinningdesign`

**Contract field grep in `panel_exp/`:** **0 matches** for `geometry_id`, `forbidden_downstream_claims`, `concurrent_multi_experiment_compatibility`, `shared_control_policy`.

---

## 36. Companion doc updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Statistical protocol Accepted; next = combination matrix |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | Protocol derived from impl statuses |
| [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) | Worlds map literature failure modes |
| [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) | Protocol consumes DES IDs |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Contract completeness or scoped BLOCK |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Protocol complete; next = combination matrix |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Design-side statistical protocol registered |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Design audit lane updated |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | DESIGN-STATISTICAL-VALIDATION-PROTOCOL-001 registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Protocol + remaining blockers |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Suitability blocked until execution |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Matrix must use protocol outcomes |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Design counterpart cross-link |
| [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md) | Planning gated on future DES-STAT |

---

*DESIGN-STATISTICAL-VALIDATION-PROTOCOL-001 v1.0.0 — Accepted; verdict = design_statistical_validation_protocol_defined_not_executed; next = DESIGN_COMBINATION_VALIDATION_MATRIX_001.*
