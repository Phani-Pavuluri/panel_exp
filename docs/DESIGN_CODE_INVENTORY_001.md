# Design Code Inventory 001

**Document ID:** DESIGN-CODE-INVENTORY-001  
**Title:** Design Code Inventory 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` design code and design-like helpers  
**Artifact type:** Documentation / governance / code inventory — **no code changes**  
**Date:** 2026-06-09  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md)

**Guardrails:** No validation · no promotion · no suitability claim · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Code Inventory 001 |
| Status | **Accepted** |
| Scope | GeoX / `panel_exp` design code and design-like helpers |
| Artifact type | Documentation / governance / code inventory |

First concrete design audit artifact after [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md). Enumerates repository design-side code and maps emitted fields to the contract. **Does not validate or promote any design.**

---

## 2. Purpose

This artifact is the **authoritative design-side code inventory** for GeoX/panel_exp. It:

- Re-discovers all design methods, helpers, and output structures from source  
- Maps each item to [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) field groups  
- Identifies emitted vs missing contract fields  
- Records tests, docs, and Track D coverage  
- Assigns conservative audit status and next required artifact  

**Does not:** validate correctness, literature alignment, statistical validity, or downstream suitability.

---

## 3. Why this artifact exists

| Gap | This inventory addresses |
|-----|--------------------------|
| [`METHOD_CODE_INVENTORY_001.md`](METHOD_CODE_INVENTORY_001.md) mixed design with estimators | Design-specific enumeration and contract mapping |
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) §6 discovery table | Superseded by code-backed inventory with contract coverage |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Requires mapping current emissions to required schema |
| Suitability / combination matrix v2 | Must reference inventory IDs, not ad hoc design names |

Future **literature alignment**, **implementation validation**, **statistical validation**, **combination matrix**, **guardrails**, and **design suitability** depend on this inventory.

---

## 4. Scope

Includes:

- Registered designs (`get_design_registry()`)  
- Non-registry design classes (`Rerandomization` wrapper)  
- Assignment generators and constraint helpers  
- Multi-test-group configuration (`n_test_grps`)  
- Validation helpers · power/MDE helpers · donor/eligibility helpers  
- Panel construction helpers · orchestration · dashboards  
- Output structures (`DesignEvidence`, `ExperimentEvidence`, `PowerContract`)  
- Governance-adjacent design spec (`spec.py` `DesignSpec`, `DesignMethod`)  
- Tests and Track D scripts referencing designs  

---

## 5. Non-goals

- No implementation changes  
- No design validation or literature alignment  
- No statistical validation or D5 archive regeneration  
- No design promotion or suitability claim  
- No TrustReport / CalibrationSignal / MMM / LLM authorization  

---

## 6. Search methodology

**Commands run (2026-06-09):**

```bash
grep -R "class .*Design" panel_exp tests docs
grep -R "QuickBlock\|Thinning\|SuperGeo\|Supergeo\|Trimmed\|Greedy\|Match\|Block\|Stratified\|Random\|Rerandomization\|MatchedPair\|CompleteRandomization\|BalancedRandomization" panel_exp tests docs
grep -R "design" panel_exp/design panel_exp/validation tests docs
grep -R "assignment\|treatment\|control\|cell_id\|block_id\|stratum\|pair_id\|supergeo\|trim\|thin\|donor\|eligible\|excluded" panel_exp/design panel_exp/evidence.py tests docs
grep -R "DesignEvidence\|DesignRegistry\|GeoExperimentDesign\|PowerAnalysis\|PowerContract\|validate_design\|validate_assignment_dict" panel_exp tests docs
find panel_exp/design -type f
find tests -iname "*design*" -o -iname "*match*" -o -iname "*block*" -o -iname "*geo*" -o -iname "*power*"
poetry run python -c "from panel_exp.design.registry import get_design_registry; ..."
```

**Directories inspected:** `panel_exp/design/` (17 modules + `modes/`), `panel_exp/evidence.py`, `panel_exp/spec.py` (DesignMethod/DesignSpec), `panel_exp/governance/decision_policy.py` (DesignProfile), `panel_exp/utils/test_designs_evaluation.py`, `panel_exp/validation/track_d_design_inventory_001.py`, `panel_exp/validation/track_d_d5_des_*.py`, `panel_exp/validation/track_d_d5_pow_*.py`, `tests/test_design_*.py`, `tests/track_d/test_design_inventory_001.py`, `tests/fixtures/artifact_schemas/design_evidence_v1.json`.

**Limitations:** Docs-only references (notebooks, gh-pages) not exhaustively parsed. `Rerandomization` not a separate registry entry — discovered via `GeoExperimentDesign.create_design`. No runtime emission audit — field presence inferred from code paths and fixture schema.

---

## 7. Inventory taxonomy

Uses [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) categories plus:

| Category ID | Description |
|-------------|-------------|
| `standard_assignment_design` | Complete/balanced randomization |
| `matching_design` | Greedy match, matched pair |
| `blocking_assignment_design` | QuickBlock, rerandomization wrapper |
| `stratified_assignment_design` | StratifiedRandomization |
| `thinning_design` | ThinningDesign |
| `trimmed_population_design` | TrimmedMatchDesign |
| `supergeo_design` | SupergeoModel |
| `multi_cell_assignment_design` | `n_test_grps > 1` configuration |
| `shared_control_design` | Shared control policy (config + guards) |
| `power_mde_design_helper` | PowerAnalysis, PowerContract, AA calibration |
| `donor_pool_eligibility_helper` | constraints.py helpers |
| `panel_construction_helper` | period_slice, rng, imbalance, registry |
| `validation_helper` | validate_design, validate_assignment_dict |
| `orchestration_helper` | GeoExperimentDesign, geo_runner |
| `dashboard_or_reporting_helper` | test_designs_evaluation dashboard |
| `output_contract_object` | DesignEvidence, ExperimentEvidence |
| `governance_spec_object` | spec.py DesignSpec, DesignProfile |
| `unknown_or_not_evaluated` | Unclassified |

---

## 8. Master inventory table

**Verdict for all rows:** `discovered_not_validated` · `contract_mapping_partial` · `not_contract_validated` · `not_suitability_approved`

| inventory_id | name | category | file path | symbol | registry | API | contract status | next audit |
|--------------|------|----------|-----------|--------|----------|-----|-----------------|------------|
| DES-001 | greedy_match_markets | matching_design | `design/assign.py` | class | yes | public | contract_mapping_partial | DESIGN_LITERATURE_ALIGNMENT_001 |
| DES-002 | CompleteRandomization | standard_assignment | `design/assign.py` | class | yes | public | contract_mapping_partial | DESIGN_LITERATURE_ALIGNMENT_001 |
| DES-003 | BalancedRandomization | standard_assignment | `design/assign.py` | class | yes | public | contract_mapping_partial | DESIGN_LITERATURE_ALIGNMENT_001 |
| DES-004 | StratifiedRandomization | stratified_assignment | `design/assign.py` | class | yes | public | contract_mapping_partial | DESIGN_LITERATURE_ALIGNMENT_001 |
| DES-005 | ThinningDesign | thinning_design | `design/assign.py` | class | yes | public | contract_mapping_partial | DESIGN_LITERATURE_ALIGNMENT_001 |
| DES-006 | Rerandomization | blocking_assignment | `design/assign.py` | class | no | public | contract_mapping_partial | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-007 | QuickBlock | blocking_assignment | `design/quickblock.py` | class | yes | public | contract_required | DESIGN_LITERATURE_ALIGNMENT_001 |
| DES-008 | MatchedPair | matching_design | `design/matched_pair.py` | class | yes | public | contract_required | DESIGN_LITERATURE_ALIGNMENT_001 |
| DES-009 | TrimmedMatchDesign | trimmed_population | `design/trimmed_match.py` | class | yes | public | contract_required | DESIGN_LITERATURE_ALIGNMENT_001 |
| DES-010 | SupergeoModel | supergeo_design | `design/supergeos.py` | class | yes | public | contract_required | DESIGN_LITERATURE_ALIGNMENT_001 |
| DES-011 | multi_test_groups | multi_cell_assignment | config | `n_test_grps` | n/a | public | contract_mapping_partial | DESIGN_COMBINATION_VALIDATION_MATRIX_001 |
| DES-012 | GeoExperimentDesign | orchestration_helper | `design/geo_experiment_design.py` | class | n/a | public | contract_mapping_partial | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-013 | run_geo_experiment_design | orchestration_helper | `design/geo_runner.py` | function | n/a | internal | contract_mapping_partial | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-014 | PowerAnalysis | power_mde_design_helper | `design/power.py` | class | n/a | public | contract_mapping_partial | DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001 |
| DES-015 | PowerContract | power_mde_design_helper | `design/power.py` | dataclass | n/a | public | partial | DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001 |
| DES-016 | prepare_constraint_context | donor_pool_eligibility | `design/constraints.py` | function | n/a | internal | not_emitted_to_contract | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-017 | validate_assignment_dict | validation_helper | `design/constraints.py` | function | n/a | internal | partial | DESIGN_GUARDRAILS_001 |
| DES-018 | validate_design | validation_helper | `design/validation.py` | function | n/a | public | partial | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-019 | slice_wide_to_time_period | panel_construction | `design/period_slice.py` | function | n/a | internal | not_emitted | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-020 | imbalance | panel_construction | `design/design_metrics.py` | function | n/a | internal | not_emitted | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-021 | make_generator | panel_construction | `design/rng.py` | function | n/a | internal | partial | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-022 | DesignRegistry | panel_construction | `design/registry.py` | class | n/a | public | not_applicable | DESIGN_GUARDRAILS_001 |
| DES-023 | balanced_volume_assign | donor_pool_eligibility | `design/constraints.py` | function | n/a | internal | not_emitted | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-024 | bernoulli_complete_assign | donor_pool_eligibility | `design/constraints.py` | function | n/a | internal | not_emitted | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-025 | create_design_comparison_dashboard | dashboard_or_reporting | `utils/test_designs_evaluation.py` | function | n/a | internal | not_emitted | DESIGN_GUARDRAILS_001 |
| DES-026 | DesignEvidence | output_contract_object | `evidence.py` | class | n/a | public | contract_mapping_partial | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-027 | ExperimentEvidence | output_contract_object | `evidence.py` | class | n/a | public | contract_mapping_partial | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-028 | spec.py DesignSpec | governance_spec | `spec.py` | dataclass | n/a | public | partial | DESIGN_IMPLEMENTATION_VALIDATION_001 |
| DES-029 | DesignMethod enum | governance_spec | `spec.py` | Enum | n/a | public | partial | DESIGN_LITERATURE_ALIGNMENT_001 |
| DES-030 | DesignProfile | governance_spec | `governance/decision_policy.py` | dataclass | n/a | internal | not_contract | DESIGN_SUITABILITY_FRAMEWORK_001 |
| DES-031 | track_d_design_inventory_001 | panel_construction | `validation/track_d_design_inventory_001.py` | generator | n/a | internal | superseded_by_this_doc | — |

**Count:** 31 inventory rows (10 registered designs + 1 wrapper + 1 multi-cell config + 19 helpers/output/governance).

---

## 9. Registered design inventory

Registry source: `register_builtin_designs` in `panel_exp/design/modes/__init__.py`. Geo-supported: 5 names (legacy allowlist aligned).

| registry key | class | path | family | geometry impact | target pop. | concurrency | emitted today | missing contract fields | tests |
|--------------|-------|------|--------|-----------------|-------------|-------------|---------------|-------------------------|-------|
| greedy_match_markets | greedy_match_markets | assign.py | matching | unit_panel_single_cell; multi_cell if n_test_grps>1 | preserved | compatible_with_constraints | assignment dict; DesignEvidence via geo_runner | geometry_id, cell_ids, shared_control_policy, concurrency, forbidden_claims, donor_pool explicit | test_design_registry, test_d5_pow_001e, D5-STAT-* reference |
| completerandomization | CompleteRandomization | assign.py | standard | unit_panel_single_cell | preserved | compatible_with_constraints | assignment dict | same as above | test_design_registry, D5-POW-001e |
| balancedrandomization | BalancedRandomization | assign.py | standard | unit_panel_single_cell | preserved | compatible_with_constraints | assignment dict | same | test_design_registry, D5-POW-001e |
| stratifiedrandomization | StratifiedRandomization | assign.py | stratified | unit_panel_single_cell | preserved | compatible_with_constraints | assignment dict | + stratum_ids, stratum_variables | test_design_registry, D5-POW-001e |
| thinningdesign | ThinningDesign | assign.py | thinning | unit_panel_single_cell | preserved (verify) | not_evaluated | assignment dict | thinning_policy, concurrency | test_design_registry, D5-POW-001e |
| quickblock | QuickBlock | quickblock.py | blocking | unknown | preserved | not_evaluated | numpy vector via assign_all | block_ids, geo dict, geometry_id | test_public_api |
| matchedpair | MatchedPair | matched_pair.py | matching | unknown | preserved | not_evaluated | numpy vector / graph | pair_ids, assignment dict | test_public_api |
| trimmedmatch | TrimmedMatchDesign | trimmed_match.py | trimmed | trimmed_geometry | **changed** | restricted | pair DataFrame / subsets | trim_policy, excluded_units, target_population_*, full_population flags | test_d5_des_trim_001 |
| supergeos | SupergeoModel | supergeos.py | supergeo | supergeo | **new units** | blocked_without_bridge | MILP pair DataFrame | supergeo_source_unit_map, geometry_id, original_unit_bridge | test_d5_des_supergeo_001 |

**Rerandomization (DES-006):** Not registered; production path wraps geo tier-1 bases via `GeoExperimentDesign.create_design()`. Emits same assignment dict as base; adds imbalance minimization loop — `rerandomization` identity not in DesignEvidence name (uses base class name).

---

## 10. Design helper inventory

| ID | helper | role | emitted to consumer |
|----|--------|------|---------------------|
| DES-012 | GeoExperimentDesign | Orchestrator: assign, validate, power, evidence | `last_evidence`, `last_validation`, MDE dataframes |
| DES-013 | run_geo_experiment_design | Registry pipeline handler | ExperimentEvidence on geo |
| DES-014 | PowerAnalysis | Simulation MDE / power curves | MDE dataframes; `PowerContract` via attach |
| DES-015 | PowerContract | MDE metadata dataclass | `to_dict()` warnings, semantics |
| DES-016 | prepare_constraint_context | Whitelist/blacklist pinning | internal ConstraintContext only |
| DES-017 | validate_assignment_dict | Post-assign constraint check | pass/fail (not full contract) |
| DES-018 | validate_design | PASS/WARN/FAIL gate | validation_summary in evidence |
| DES-019 | slice_wide_to_time_period | INV-D1-001 pre-period slice | none |
| DES-020 | imbalance | Balance metric | none (used in rerandomization) |
| DES-021 | make_generator | RNG seed contract | seed in DesignSpec if passed |
| DES-022 | DesignRegistry | Registration/dispatch | list_names, resolve |
| DES-023–024 | balanced_volume_assign, bernoulli_complete_assign | Arm assignment primitives | assignment dict fragments |
| DES-025 | create_design_comparison_dashboard | MLflow design ranking UI | ungoverned comparison tables |
| DES-026–027 | DesignEvidence, ExperimentEvidence | Evidence export | see §11 |
| DES-028–029 | DesignSpec, DesignMethod | Experiment specification | spec_hash, design_method in evidence |
| DES-030 | DesignProfile | F-DECISION trust inputs | design_method_id only |

---

## 11. Current emitted output structures

### DesignEvidence (`panel_exp/evidence.py`)

**Emitted fields (v1.0 schema):** `evidence_version`, `experiment_id`, `created_at`, `package_version`, `code_version`, `spec_hash`, `assignment_hash`, `input_data_hash`, `design_name`/`design_method`, `assignment` (control + test_* lists), `validation_summary`, `inference_metadata` (interference, analysis_contract), `warnings`, `errors`, `artifacts`, `diagnostics`.

**Partial contract mapping:** assignment → §9 treated/control; validation_summary.status → balance_pass_warn_fail (partial); spec_hash + design_name → §7 identity (partial); inference_metadata → compatibility hints (partial).

**Not emitted:** `geometry_id`, `concurrent_multi_experiment_compatibility`, `excluded_units`, `cell_ids`, `shared_control_policy`, `donor_pool_units`, `forbidden_downstream_claims`, trim/supergeo fields, power/MDE block (separate path), full unit universe.

### ExperimentEvidence

Wraps `DesignEvidence` + optional inference. Same gaps; adds inference payload when present.

### Geo runner output

Returns `(mde_prc_df, mde_val_df, power_results_df)` — power tables **not** linked into DesignOutputContract envelope today.

### TrimmedMatch / Supergeo direct APIs

Non-standard outputs (pairs, MILP DataFrame) — **not** assignment dict; contract BLOCK without adapter.

**Compliance:** **No** design is **contract_complete** in code. Mapping is **partial** at best.

---

## 12. Contract coverage matrix

Legend: **emitted** · **partial** · **not_emitted** · **not_applicable** · **unknown**

| inventory_id | core | identity | units | assign | multi-cell | geometry | block/pair | donor | trim/thin | supergeo | balance | power | time | outcome | hints | forbidden | TROP/Bayes | exp plan |
|--------------|------|----------|-------|--------|------------|----------|------------|-------|-----------|----------|---------|-------|------|---------|-------|-----------|------------|----------|
| DES-001–005 geo | partial | partial | not_emitted | emitted | partial | not_emitted | n/a | partial | n/a | n/a | partial | partial | partial | partial | not_emitted | not_emitted | not_emitted | not_emitted |
| DES-006 | partial | partial | not_emitted | emitted | partial | not_emitted | n/a | partial | n/a | n/a | partial | partial | partial | partial | not_emitted | not_emitted | not_emitted | not_emitted |
| DES-007–008 | unknown | partial | not_emitted | partial | not_emitted | not_emitted | partial | unknown | n/a | n/a | unknown | n/a | unknown | unknown | not_emitted | not_emitted | not_emitted | not_emitted |
| DES-009 | partial | partial | not_emitted | partial | not_emitted | not_emitted | partial | unknown | partial | n/a | partial | partial | partial | partial | not_emitted | not_emitted | not_emitted | not_emitted |
| DES-010 | partial | partial | not_emitted | partial | not_emitted | not_emitted | n/a | unknown | n/a | partial | n/a | partial | n/a | partial | not_emitted | not_emitted | not_emitted | not_emitted |
| DES-011 | n/a | n/a | n/a | partial | partial | not_emitted | n/a | partial | n/a | n/a | n/a | n/a | n/a | n/a | not_emitted | not_emitted | not_emitted | not_emitted |
| DES-012–013 | partial | partial | not_emitted | emitted | partial | not_emitted | n/a | partial | n/a | n/a | partial | partial | partial | partial | not_emitted | not_emitted | not_emitted | not_emitted |
| DES-014–015 | n/a | n/a | n/a | n/a | n/a | partial | n/a | n/a | n/a | n/a | n/a | partial | partial | n/a | not_emitted | not_emitted | not_emitted | not_emitted |
| DES-026–027 | partial | partial | not_emitted | emitted | not_emitted | not_emitted | n/a | not_emitted | n/a | n/a | partial | not_emitted | not_emitted | partial | partial | not_emitted | not_emitted | not_emitted |

---

## 13. Gap summary by contract group

| Contract group | Emitted today | Partial | Missing (all geo designs) |
|----------------|---------------|---------|---------------------------|
| Core envelope | timestamps, hashes | contract_id/version absent | design_run_id, artifact_status, reproducibility_hash |
| Design identity | design_name, spec_hash | parameters scattered in GeoExperimentDesign | design_family, design_mode, repo_commit |
| Unit universe | assignment lists imply units | — | eligible/excluded maps, target_population_* |
| Assignment | control + test_* dict | — | assignment_by_unit, exclusivity checks as fields |
| Multi-cell / concurrency | n_test_grps in spec only | — | cell_ids, shared_control_policy, concurrency enum |
| Geometry | — | inference hints only | **geometry_id** (hard BLOCK) |
| Block/stratum/pair | — | — | block_ids, stratum_ids, pair_ids |
| Donor pool | control list | — | donor_pool_units, diagnostics |
| Trim/thin | — | — | DES-009/010 specific fields |
| Supergeo | — | — | source_unit_map (hard BLOCK) |
| Balance | validation_summary | imbalance internal only | structured balance diagnostics |
| Power/MDE | PowerContract separate | MDE dataframes | not in DesignEvidence envelope |
| Forbidden claims | — | — | **forbidden_downstream_claims** required |

**Hard blockers for contract PASS:** missing `geometry_id`, missing forbidden claims, missing concurrency status, supergeo/trim population fields.

---

## 14. Geometry and target-population impact summary

| design | preserves units | creates units | removes units | target pop. change | bridge | concurrent restriction |
|--------|-----------------|---------------|---------------|-------------------|--------|------------------------|
| geo tier-1 (001–005) | yes | no | via blacklist only | no | no | compatible_with_constraints |
| Rerandomization | yes | no | via base | no | no | inherits base |
| QuickBlock / MatchedPair | yes | no | unknown | no | no | not_evaluated |
| TrimmedMatch | yes (pairs) | no | yes (trim) | **yes** | trim bridge | restricted |
| Supergeo | no | **yes** | merges markets | **yes** | supergeo bridge | blocked_without_bridge |
| multi_test_groups | yes | no | via design | no | pooled blocked | restricted |
| PowerAnalysis MDE | aggregates | 2-row virtual | n/a | n/a | aggregate≠unit | not_evaluated |

---

## 15. Concurrent multi-experiment compatibility inventory

| design | code support | shared control | control reuse emitted | cell IDs emitted | exclusivity checked | bridge |
|--------|--------------|----------------|----------------------|------------------|---------------------|--------|
| geo tier-1 | n_test_grps param | implicit shared control | **no** | test_0.. keys only | validate_assignment_dict | pooled blocked |
| TrimmedMatch | n_test_groups param | unknown | **no** | partial | pair-level | restricted |
| Supergeo | cluster-based | n/a | **no** | n/a | MILP constraints | blocked_without_bridge |
| QuickBlock / MatchedPair | single vector | n/a | **no** | n/a | unknown | not_evaluated |

**Contract field `concurrent_multi_experiment_compatibility`:** **not_emitted** for any design today.

---

## 16. Supergeo inventory

| Item | Finding |
|------|---------|
| Files | `panel_exp/design/supergeos.py` — `SupergeoModel` |
| Registry | `supergeos` (aliases: supergeo, supergeo_model); geo_run_supported=False |
| Source-unit mapping | **Internal** combo generation; **not** exported as `supergeo_source_unit_map` |
| Aggregation | sum of market series in `total_sales_for_supergeo` |
| Output | MILP-selected pair DataFrame — not control/test dict |
| Contract blockers | geometry_id, supergeo_source_unit_map, forbidden_claims, concurrency |
| Track D | `track_d_d5_des_supergeo_001.py`, `test_d5_des_supergeo_001.py` |
| Next audit | DESIGN_LITERATURE_ALIGNMENT_001 |

---

## 17. Trimmed / thinning inventory

### TrimmedMatchDesign (`trimmedmatch`)

| Item | Finding |
|------|---------|
| Trim rule | `trim_rate` on pair differences; Tp/Te split |
| Excluded units | Computed internally; **not** exported as contract list |
| Target population | Changes with pair/trim selection |
| Contract blockers | trim_policy, excluded_units, target_population_*, full_population_bridge |
| Track D | `track_d_d5_des_trim_001.py` |

### ThinningDesign (`thinningdesign`)

| Item | Finding |
|------|---------|
| Mechanism | Kernel thinning on wide panel |
| Exclusion | Does not obviously remove units — **thinning_policy** not emitted |
| Next audit | DESIGN_LITERATURE_ALIGNMENT_001 (confirm population impact) |

---

## 18. Blocking / stratified / pairing inventory

| design | block/stratum/pair IDs | construction vars | inference hint | emitted | missing |
|--------|------------------------|-------------------|----------------|---------|---------|
| QuickBlock | internal blocks | k-NN graph | unknown | no block_ids field | block_ids, within_block_rule |
| StratifiedRandomization | percentile strata internal | KPI strata | no | no stratum_ids | stratum_ids, stratum_variables |
| MatchedPair | graph pairs | Mahalanobis | unknown | L adjacency internal | pair_ids, geo dict |
| TrimmedMatch | pair IDs internal | linear assignment | pair-aware likely | partial pairs | pair_ids in contract |

---

## 19. Matching / randomization inventory

| design | rule (code) | output | balance | seed | missing contract |
|--------|-------------|--------|---------|------|------------------|
| greedy_match_markets | pre-period KPI matching greedy | control/test_* dict | rerandomization imbalance optional | make_generator / random_state | geometry_id, donor_pool explicit |
| CompleteRandomization | bernoulli_complete_assign | dict | optional rerandomization | yes | same |
| BalancedRandomization | balanced_volume_assign | dict | volume share | yes | same |
| Rerandomization | imbalance minimization loop | inherits base | imbalance metric | yes | wrapper identity in evidence |

---

## 20. Power / MDE inventory

| component | emitted | assumptions | linked to design output | missing |
|-----------|---------|-------------|-------------------------|---------|
| PowerAnalysis.analysis | MDE %, effect grids, dataframes | MDE_SEMANTICS simulation_coverage | **Separate** from DesignEvidence | geometry_id aggregate 2-row; not in contract envelope |
| PowerContract | mde_type, warnings, recommended_use | classical_power=false | attach_power_contract helper | full §18 field set |
| evaluate_aa_calibration | calibration metrics | AA null | optional metadata | contract linkage |
| GeoExperimentDesign._calculate_sensitivity_metrics | calls PowerAnalysis | estimator-dependent | returns dataframes only | power_mde in DesignOutputContract |

---

## 21. Validation / test coverage inventory

| area | tests / reports |
|------|-----------------|
| Registry | `tests/test_design_registry.py`, `test_design_registry_equivalence.py` |
| Validation gate | `tests/test_design_validation_gate.py` |
| Design inventory generator | `tests/track_d/test_design_inventory_001.py` |
| D5-POW design geometry | `test_d5_pow_001e_design_geometry.py`, 001a–d scripts |
| D5-DES supergeo/trim | `test_d5_des_supergeo_001.py`, `test_d5_des_trim_001.py` |
| D5-DES matching | `track_d_d5_des_001a.py` |
| D5-STAT reference design | all D5-STAT Level B (greedy_match_markets reference) |
| Public API | `tests/test_public_api.py` (QuickBlock, MatchedPair) |
| Power contract | `tests/test_power_contract.py` |
| Evidence schema | `tests/fixtures/artifact_schemas/design_evidence_v1.json` |
| Docs-only | `TRACK_D_DESIGN_METHOD_INVENTORY_001.md`, notebooks (not code-validated) |
| QuickBlock geo-run | **no** dedicated integration test |
| TrimmedMatch production geo | **no** geo_runner test |
| Contract completeness | **no** test asserts DesignOutputContract |

---

## 22. Implementation risk register

| risk_id | description | severity |
|---------|-------------|----------|
| R-DES-001 | `geometry_id` not emitted anywhere | BLOCK |
| R-DES-002 | `forbidden_downstream_claims` not emitted | BLOCK |
| R-DES-003 | `concurrent_multi_experiment_compatibility` not emitted | BLOCK |
| R-DES-004 | Shared control policy not documented in output | BLOCK multi-cell |
| R-DES-005 | Supergeo lacks `supergeo_source_unit_map` in export | BLOCK |
| R-DES-006 | TrimmedMatch hides excluded units from contract | BLOCK |
| R-DES-007 | Power/MDE disconnected from DesignEvidence envelope | WARN |
| R-DES-008 | Aggregate MDE geometry ≠ unit-panel SCM readout | WARN |
| R-DES-009 | DesignEvidence name = base randomizer; rerandomization wrapper invisible | WARN |
| R-DES-010 | QuickBlock/MatchedPair non-dict outputs | BLOCK geo integration |
| R-DES-011 | Compatibility hints absent | WARN |
| R-DES-012 | TROP/Bayesian future fields absent (expected) | n/a |
| R-DES-013 | Dashboard ranking ungoverned | WARN |

---

## 23. Downstream consumption status

**No** discovered design or helper is authorized for:

- Suitability role assignment  
- TrustReport role  
- CalibrationSignal eligibility  
- MMM calibration attachment  
- LLM experiment recommendation  

until `DESIGN_IMPLEMENTATION_VALIDATION_001` + contract PASS + later audit ladder steps complete.

Suitability framework must use **inventory_id** (DES-*) or registry key from this document — not ad hoc names.

---

## 24. Relationship to next artifacts

| Next artifact | Uses this inventory |
|---------------|---------------------|
| **DESIGN_LITERATURE_ALIGNMENT_001** | Per-family literature vs DES-001–010 |
| **DESIGN_IMPLEMENTATION_VALIDATION_001** | Emission vs contract §25 checks |
| **DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001** | Worlds per inventory_id |
| **DESIGN_COMBINATION_VALIDATION_MATRIX_001** | design × estimator rows keyed by inventory |
| **DESIGN_GUARDRAILS_001** | Risk register R-DES-* |
| **DESIGN_SUITABILITY_FRAMEWORK_001** | Classification per DES-* |

---

## 25. Current status and verdict

**Verdict:** `design_code_inventory_complete_contract_gaps_identified`

| Metric | Value |
|--------|-------|
| Registered designs | 9 |
| Non-registry design classes | 1 (Rerandomization wrapper) |
| Helpers / output / governance rows | 21 |
| Contract-complete implementations | **0** |
| Geo-run supported | 5 |
| Next audit artifact | **DESIGN_LITERATURE_ALIGNMENT_001** |

**Not claimed:** production-ready, validated, governed, suitable, TrustReport-eligible, CalibrationSignal-eligible, MMM-ready, LLM-ready.

---

## 26. Completion checklist

| Item | Status |
|------|--------|
| Repo searched | ✅ §6 |
| All designs listed | ✅ §8–§9 |
| Helpers listed | ✅ §10 |
| Output structures inspected | ✅ §11 |
| Contract coverage matrix | ✅ §12 |
| Risks registered | ✅ §22 |
| Roadmap updated | ✅ companion docs |
| No code changed | ✅ |
| Tests run | ✅ |

---

## 27. Roadmap and audit updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Inventory complete; next = literature |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Inventory mapping note |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Inventory complete |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Design enumeration source |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Lane status |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Gap summary |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Inventory ID requirement |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Inventory + contract refs |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Inventory-discovered methods |
| [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md) | Prerequisite chain |

---

*DESIGN-CODE-INVENTORY-001 v1.0.0 — Accepted; verdict = design_code_inventory_complete_contract_gaps_identified; next = DESIGN_LITERATURE_ALIGNMENT_001.*
