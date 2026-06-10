# Design Implementation Validation 001

**Document ID:** DESIGN-IMPLEMENTATION-VALIDATION-001  
**Title:** Design Implementation Validation 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` design implementation validation  
**Artifact type:** Documentation / governance / implementation validation — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md)

**Inputs:** [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) · [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) (audit-program artifact; where absent on branch, [`METHOD_LITERATURE_ALIGNMENT_001.md`](METHOD_LITERATURE_ALIGNMENT_001.md) §5 + inventory apply) · [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md)

**Guardrails:** No code fixes · no statistical validation · no promotion · no suitability claim · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Implementation Validation 001 |
| Status | **Accepted** |
| Scope | GeoX / `panel_exp` design implementation validation |
| Artifact type | Documentation / governance / implementation validation |

Third concrete design audit artifact. Validates whether current design code **behavior** and **emitted outputs** match inventory identity, literature-aligned conceptual families, and `DesignOutputContract` requirements. **Does not fix gaps.**

---

## 2. Purpose

This artifact answers:

1. Does each DES row's **implementation** match its literature-aligned conceptual family?  
2. Does each design/output path emit fields required by [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md)?  
3. What **hard blockers** prevent contract-complete or downstream consumption?

**Implementation validation ≠ statistical validation ≠ suitability approval.**

---

## 3. Why this artifact exists

| Prior artifact | Provided |
|--------------|----------|
| [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) | What exists (31 rows) |
| [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) | Intended conceptual families |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Required governed metadata |

This artifact **compares actual code paths and emitted artifacts** against those three. Without it, statistical validation and combination-matrix rows would validate **intended** behavior rather than **observed** behavior.

---

## 4. Scope

- Registered designs (9 keys) + `Rerandomization` wrapper  
- Assignment primitives (`bernoulli_complete_assign`, `balanced_volume_assign`)  
- Multi-cell (`n_test_grps`) logic in tier-1 + geo runner  
- Orchestration (`GeoExperimentDesign`, `run_geo_experiment_design`)  
- Output objects (`DesignEvidence`, `ExperimentEvidence`, `DesignSpec`)  
- Validation/eligibility helpers  
- Power/MDE (`PowerAnalysis`, `PowerContract`)  
- Dashboard helper (downstream consumer only)  
- Tests, fixtures, D5-DES/D5-POW reports as **evidence basis** (not statistical proof)

---

## 5. Non-goals

- No code, harness, fixture, or D5 archive changes  
- No statistical OC or new validation harness  
- No design promotion or suitability claim  
- No TrustReport / CalibrationSignal / MMM / LLM authorization  
- No claim that fixing gaps is in scope of this artifact  

---

## 6. Validation status taxonomy

| Status | Meaning |
|--------|---------|
| `implementation_aligned_contract_complete` | Behavior matches family; contract fields complete — **none found in repo** |
| `implementation_aligned_contract_partial` | Behavior largely matches family; contract emission partial |
| `implementation_partially_aligned_contract_partial` | Family fidelity gaps and contract gaps |
| `implementation_behavior_ambiguous` | Cannot determine population/geometry semantics from code+output |
| `implementation_mismatch` | Behavior conflicts with literature-aligned family |
| `adapter_required` | Non-standard output shape; contract BLOCK without adapter |
| `helper_not_design_family` | Support component, not a design method |
| `superseded_or_historical` | Prior generator only |

**Even `implementation_aligned_contract_complete` would not imply statistical validity or suitability.**

---

## 7. Evaluation criteria

Per DES row, assess:

| Criterion | Source of truth |
|-----------|-----------------|
| Inventory identity | [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) §8 |
| Conceptual family | [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) §8 |
| Contract fields | [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) §6–§24 |
| Observed behavior | Code paths + tests + fixtures |

Checklist: registry/API · assignment behavior · seed/reproducibility · assignment probability · exclusivity · multi-cell · shared control · geometry · target population · block/stratum/pair · trim/thin · supergeo map · power/MDE linkage · forbidden claims · tests/docs coverage.

---

## 8. Search methodology and registry introspection

**Commands run (2026-06-10):**

```bash
grep -R "class .*Design" panel_exp tests docs
grep -R "CompleteRandomization\|BalancedRandomization\|StratifiedRandomization\|ThinningDesign\|Rerandomization\|QuickBlock\|MatchedPair\|TrimmedMatch\|Supergeo\|greedy_match_markets" panel_exp tests docs
grep -R "DesignEvidence\|ExperimentEvidence\|DesignSpec\|DesignMethod\|DesignProfile\|PowerContract" panel_exp tests docs
grep -R "assignment\|treatment\|control\|cell_id\|block_id\|stratum\|pair_id\|supergeo\|trim\|thin\|eligible\|excluded\|donor" panel_exp/design panel_exp/evidence.py panel_exp/spec.py tests docs
grep -R "geometry_id\|forbidden_downstream_claims\|concurrent_multi_experiment_compatibility\|shared_control\|control_reuse" panel_exp tests docs
find panel_exp/design -type f
find tests -iname "*design*" -o -iname "*match*" -o -iname "*block*" -o -iname "*geo*" -o -iname "*power*"
poetry run python -c "from panel_exp.design.registry import get_design_registry; print(sorted(get_design_registry().list_names()))"
poetry run python -c "from panel_exp.design.registry import geo_run_design_supported; print(sorted(geo_run_design_supported()))"
```

**Registry keys:** `balancedrandomization`, `completerandomization`, `greedy_match_markets`, `matchedpair`, `quickblock`, `stratifiedrandomization`, `supergeos`, `thinningdesign`, `trimmedmatch`

**Geo-run supported (5):** `balancedrandomization`, `completerandomization`, `greedy_match_markets`, `stratifiedrandomization`, `thinningdesign`

**Contract field grep in `panel_exp/`:** **0 matches** for `geometry_id`, `forbidden_downstream_claims`, `concurrent_multi_experiment_compatibility`, `shared_control_policy`, `control_reuse_policy`.

---

## 9. Master implementation validation table

**Downstream status (all rows unless noted):** `not_contract_complete` · `not_statistically_validated` · `not_suitability_approved`

| ID | Name | Impl. status | Contract | Observed behavior | Major gaps | Hard blockers | Next action |
|----|------|--------------|----------|-------------------|------------|---------------|-------------|
| DES-001 | greedy_match_markets | impl_aligned_contract_partial | partial | Dict `control`+`test_*`; pre-period slice when set; greedy objective | No geometry_id; no donor_pool explicit; no concurrency | geometry_id; forbidden_claims | Statistical protocol |
| DES-002 | CompleteRandomization | impl_aligned_contract_partial | partial | Bernoulli via `bernoulli_complete_assign`; exclusivity validated | π not in evidence; no unit universe | geometry_id; forbidden_claims; concurrency | Statistical protocol |
| DES-003 | BalancedRandomization | impl_partially_aligned_contract_partial | partial | KPI-volume balance — **not** Bernoulli | Naming vs complete randomization | Same as tier-1 | Statistical protocol |
| DES-004 | StratifiedRandomization | impl_partially_aligned_contract_partial | partial | Percentile strata; volume balance within stratum | **stratum_ids not emitted** | geometry_id; stratum_ids; forbidden_claims | Statistical protocol |
| DES-005 | ThinningDesign | impl_behavior_ambiguous | partial | Norm-weight heuristic; cites kernel thinning | Candidate-space vs exclusion **ambiguous** | thinning_policy; geometry_id | Statistical protocol |
| DES-006 | Rerandomization | impl_aligned_contract_partial | partial | Loop until imbalance threshold; geo wraps all tier-1 | **Evidence uses base class name** (`geo_runner` L59) | rerandomization identity; inference caveat | Statistical protocol |
| DES-007 | QuickBlock | adapter_required | missing | numpy vector; kNN blocks internal | Not geo-run; no block_ids in output | adapter; geometry_id; block_ids | Adapter + impl fix |
| DES-008 | MatchedPair | adapter_required | missing | Mahalanobis matching graph; numpy vector | No pair_ids; not geo-run | adapter; pair_ids | Adapter + impl fix |
| DES-009 | TrimmedMatchDesign | adapter_required | missing | Tp/Te pairs; trim; dict/DataFrame hybrid | Excluded units internal only | adapter; trim metadata; population fields | Bridge + adapter |
| DES-010 | SupergeoModel | adapter_required | missing | MILP pair DataFrame | No source_unit_map in envelope | adapter; supergeo_source_unit_map; geometry_id | Bridge + adapter |
| DES-011 | multi_test_groups | impl_partially_aligned_contract_partial | partial | `test_0..n-1` keys; shared `control` | No cell_ids; no reuse policy | shared_control_policy; cell_ids | Combination matrix |
| DES-012 | GeoExperimentDesign | helper_not_design_family | partial | Rerandomization wrap; evidence via runner | Power not in evidence | Same as tier-1 envelope | Statistical protocol |
| DES-013 | run_geo_experiment_design | helper_not_design_family | partial | Pipeline order documented in `geo_runner.py` | Base design identity only | — | — |
| DES-014 | PowerAnalysis | impl_partially_aligned_contract_partial | partial | Simulation MDE; aggregate subsets | Not in DesignEvidence | power not in envelope | Statistical protocol |
| DES-015 | PowerContract | helper_not_design_family | partial | `to_dict()` semantics only | Not joined to evidence | linkage | Statistical protocol |
| DES-016 | prepare_constraint_context | helper_not_design_family | missing | Internal `ConstraintContext` | Not surfaced to contract | eligible/excluded emission | Future impl work |
| DES-017 | validate_assignment_dict | helper_not_design_family | partial | Exclusivity + constraint checks | Results not contract fields | — | Guardrails |
| DES-018 | validate_design | helper_not_design_family | partial | PASS/WARN/FAIL checks | Partial balance in summary | — | Guardrails |
| DES-019 | slice_wide_to_time_period | helper_not_design_family | missing | Pre-period slice helper | Not in evidence | time window fields | Future impl work |
| DES-020 | imbalance | helper_not_design_family | missing | Metric for rerandomization | Not in evidence | balance diagnostics | Future impl work |
| DES-021 | make_generator | helper_not_design_family | partial | Seed in DesignSpec when passed | No reproducibility_hash on evidence | reproducibility_hash | Future impl work |
| DES-022 | DesignRegistry | helper_not_design_family | n/a | 9 keys registered | — | — | Guardrails |
| DES-023 | balanced_volume_assign | helper_not_design_family | missing | Volume primitive | Not emitted | assignment_probability | Future impl work |
| DES-024 | bernoulli_complete_assign | helper_not_design_family | missing | Bernoulli primitive | Not emitted | assignment_probability | Future impl work |
| DES-025 | create_design_comparison_dashboard | helper_not_design_family | missing | MLflow UI | Ungoverned | — | Guardrails |
| DES-026 | DesignEvidence | helper_not_design_family | partial | v1.0 schema; assignment + validation_summary | No contract envelope | geometry_id; forbidden_claims | Future impl work |
| DES-027 | ExperimentEvidence | helper_not_design_family | partial | Wraps design evidence | Same gaps | Same | Future impl work |
| DES-028 | DesignSpec | helper_not_design_family | partial | spec_hash, design_method, n_test_groups | Partial identity | contract_id/version | Future impl work |
| DES-029 | DesignMethod enum | helper_not_design_family | partial | Taxonomy enum | Not full contract | — | — |
| DES-030 | DesignProfile | helper_not_design_family | not_applicable | F-DECISION input | Not design output | — | Suitability framework |
| DES-031 | track_d_design_inventory_001 | superseded_or_historical | n/a | Superseded | — | — | — |

**Contract-complete designs: 0 / 31**

---

## 10. Registered design validation

| Registry key | Class | Registry | Geo-run | Output shape | Adapter | geometry_id | forbidden_claims | concurrency | Verdict |
|--------------|-------|----------|---------|--------------|---------|-------------|-------------------|-------------|---------|
| greedy_match_markets | greedy_match_markets | yes | yes | assignment dict | no | **no** | **no** | **no** | impl_aligned_contract_partial |
| completerandomization | CompleteRandomization | yes | yes | assignment dict | no | **no** | **no** | **no** | impl_aligned_contract_partial |
| balancedrandomization | BalancedRandomization | yes | yes | assignment dict | no | **no** | **no** | **no** | impl_partially_aligned_contract_partial |
| stratifiedrandomization | StratifiedRandomization | yes | yes | assignment dict | no | **no** | **no** | **no** | impl_partially_aligned_contract_partial |
| thinningdesign | ThinningDesign | yes | yes | assignment dict | no | **no** | **no** | **no** | impl_behavior_ambiguous |
| quickblock | QuickBlock | yes | **no** | numpy vector | **required** | **no** | **no** | **no** | adapter_required |
| matchedpair | MatchedPair | yes | **no** | numpy vector | **required** | **no** | **no** | **no** | adapter_required |
| trimmedmatch | TrimmedMatchDesign | yes | **no** | pair DataFrame / dict | **required** | **no** | **no** | **no** | adapter_required |
| supergeos | SupergeoModel | yes | **no** | MILP DataFrame | **required** | **no** | **no** | **no** | adapter_required |

**Note:** Registry `run` handler is `run_geo_experiment_design` for all keys, but `geo_run_supported=False` designs fail at orchestration for unsupported paths.

---

## 11. Greedy / matched-market (DES-001)

| Check | Result |
|-------|--------|
| Objective | `func_to_optimize`: corr / dtw / l2_imbalance — **verified** in `assign.py` |
| Pre-period | `slice_wide_to_time_period` when `pre_treatment_period` set — **verified** |
| Labels | `control`, `test_0`, … — **verified** |
| Donor pool | Control list only; donor_pool not explicit in evidence |
| Balance | Internal to rerandomization; `validation_summary` partial |
| Seed | `random_state` on Design — **partial** in spec |
| Contract gaps | geometry_id, concurrency, forbidden_claims, donor_pool_units |

**Status:** `implementation_aligned_contract_partial`

---

## 12. Complete / balanced / stratified (DES-002–004, DES-023–024)

### CompleteRandomization (DES-002)

- **Behavior:** `bernoulli_complete_assign` + `validate_assignment_dict` — matches Bernoulli family.  
- **Gaps:** `assignment_probability` not in evidence envelope.

### BalancedRandomization (DES-003)

- **Behavior:** `balanced_volume_assign` — KPI-volume targets.  
- **Gap:** Literature labels this differently from complete randomization; product naming risk (G-DES-011).

### StratifiedRandomization (DES-004)

- **Behavior:** Percentile strata (`n_percentiles`); balanced within stratum.  
- **Gap:** **No `stratum_ids` in assignment dict or evidence.**

**Status:** DES-002 `implementation_aligned_contract_partial`; DES-003/004 `implementation_partially_aligned_contract_partial`

---

## 13. Rerandomization (DES-006)

| Check | Result |
|-------|--------|
| Acceptance rule | `imbalance_val <= target_imbalance` or best after `max_iter` |
| Balance threshold | `target_imbalance` default 1e-2 |
| Candidate draws | `max_iter` default 1000 |
| Identity in evidence | **`design_method = design_class_name(base_randomizer_cls)`** — rerandomization **not** recorded (`geo_runner.py` L59) |
| Inference caveat | **Not emitted** in evidence |

**Status:** `implementation_aligned_contract_partial` — behavior matches Morgan–Rubin loop; metadata incomplete.

---

## 14. QuickBlock (DES-007)

| Check | Result |
|-------|--------|
| Algorithm | kNN graph blocking + optional block split — **verified** `quickblock.py` |
| Registry | yes; `geo_run_supported=False` |
| Block IDs | Internal `block_membership`; **not exported** |
| Output | numpy treatment vector — **adapter_required** |
| Inference metadata | `requires_block_aware_inference` **not emitted** |

**Status:** `adapter_required`

---

## 15. MatchedPair (DES-008)

| Check | Result |
|-------|--------|
| Pair construction | `max_weight_matching` on Mahalanobis distance |
| Pair IDs | Internal `blocks`; **not exported** |
| Output | numpy vector — **adapter_required** |

**Status:** `adapter_required`

---

## 16. ThinningDesign (DES-005)

| Check | Result |
|-------|--------|
| Objective | Norm-based weights; docstring cites Dwivedi & Mackey (2021) |
| Unit exclusion | No excluded_units list — assigns all eligible units |
| Ambiguity | **Candidate-space thinning vs population exclusion unresolved** (G-DES-002) |
| `assign_all` | Raises — not implemented |

**Status:** `implementation_behavior_ambiguous`

---

## 17. TrimmedMatchDesign (DES-009)

| Check | Result |
|-------|--------|
| Tp/Te split | `test_size` fraction — **verified** |
| Trim | `trim_rate` on pair response quantiles |
| Excluded units | Computed internally — **not in contract envelope** |
| Output | `best_design` dict + pairs — **not** standard geo evidence path |
| Full-population guard | **Not emitted** (`full_population_claim_allowed`) |
| D5-DES-TRIM | `target_population_shift_severe` |

**Status:** `adapter_required` + bridge-required

---

## 18. SupergeoModel (DES-010)

| Check | Result |
|-------|--------|
| New units | Supergeo aggregates from DMA combinations |
| MILP | Pair selection — **verified** `supergeos.py` |
| Source map | **Internal only** — not `supergeo_source_unit_map` in output |
| Output | DataFrame columns `Supergeo_1`, `Supergeo_2`, … |
| Original-geo guard | **Not emitted** |
| D5-DES-SUPERGEO | `separate_geometry_design`; flat SCM+JK invalid |

**Status:** `adapter_required` + bridge-required

---

## 19. Multi-test group / shared control (DES-011)

| Check | Result |
|-------|--------|
| `n_test_grps` | Supported in tier-1 `assign()` |
| Labels | `test_0`, `test_1`, … + single `control` |
| Shared control | **Implicit** — same control list for all test arms |
| cell_ids | **Not emitted** |
| control_reuse_policy | **Not emitted** |
| Exclusivity | `validate_assignment_dict` — **checked**, not emitted as field |
| Pooled/portfolio guards | **Not in evidence** |

**Status:** `implementation_partially_aligned_contract_partial`

---

## 20. Power / MDE (DES-014, DES-015)

| Check | Result |
|-------|--------|
| Semantics | `MDE_SEMANTICS`: simulation_coverage — **documented** `power.py` |
| Classical power | `classical_power: false` in PowerContract |
| Geometry | MDE runs on **subset panels** per test/control pair — aggregate tendency |
| DesignEvidence link | **None** — MDE dataframes returned separately from `run_design` |
| PowerContract | `to_dict()` exists; not attached to evidence in geo_runner |

**Status:** DES-014 `implementation_partially_aligned_contract_partial`; DES-015 `helper_not_design_family`

---

## 21. Output object validation (DES-026–029)

### DesignEvidence (`evidence.py` + fixture `design_evidence_v1.json`)

**Emitted:** `evidence_version`, `experiment_id`, `created_at`, `package_version`, `code_version`, `spec_hash`, `assignment_hash`, `input_data_hash`, `design_name`, `assignment`, `validation_summary`, `inference_metadata`, `warnings`, `errors`, `artifacts`, `diagnostics`

**Missing (contract):** `contract_id`, `contract_version`, `design_run_id`, `artifact_status`, `geometry_id`, `eligible_units`, `excluded_units`, `concurrent_multi_experiment_compatibility`, `shared_control_policy`, `donor_pool_units`, `forbidden_downstream_claims`, `reproducibility_hash`, trim/supergeo/block fields, power/MDE block

**Forbidden claims:** **Not emitted** — repo-wide grep confirms absence in `panel_exp/`

**Contract envelope:** **Does not exist** as `DesignOutputContract` object — partial `DesignEvidence` only

**Status:** `implementation_partially_aligned_contract_partial` for envelope support

---

## 22. Helper / validation validation (DES-016–025)

| ID | Classification | Finding |
|----|----------------|---------|
| DES-016 | eligibility helper | `prepare_constraint_context` builds eligible universe — not exported |
| DES-017 | validation helper | Exclusivity enforced; results not contract fields |
| DES-018 | validation helper | Balance KPI checks → `validation_summary.status` partial |
| DES-019 | panel helper | INV-D1-001 pre-period slice — used by greedy, not recorded |
| DES-020 | panel helper | Imbalance metric — rerandomization only |
| DES-021 | panel helper | RNG seed — partial via DesignSpec |
| DES-022 | registry | 9 keys; resolves classes correctly |
| DES-025 | reporting | Ungoverned MLflow rankings |

All: `helper_not_design_family`

---

## 23. Contract coverage matrix

Legend: **complete** · **partial** · **missing** · **not_applicable** · **unknown**

| ID | core | identity | units | assign | multi-cell | geometry | block/pair | donor | trim/thin | supergeo | balance | power | time | outcome | hints | forbidden | TROP | exp plan |
|----|------|----------|-------|--------|------------|----------|------------|-------|-----------|----------|---------|-------|------|---------|-------|-----------|------|----------|
| DES-001–006 geo path | partial | partial | missing | partial | partial | missing | n/a | partial | n/a | n/a | partial | partial | partial | partial | missing | missing | missing | missing |
| DES-007–008 | partial | partial | missing | partial | missing | missing | partial | unknown | n/a | n/a | unknown | n/a | unknown | unknown | missing | missing | missing | missing |
| DES-009 | partial | partial | missing | partial | missing | missing | partial | unknown | partial | n/a | partial | partial | partial | partial | missing | missing | missing | missing |
| DES-010 | partial | partial | missing | partial | missing | missing | n/a | unknown | n/a | partial | n/a | partial | n/a | partial | missing | missing | missing | missing |
| DES-011 | n/a | n/a | missing | partial | partial | missing | n/a | partial | n/a | n/a | n/a | n/a | n/a | n/a | missing | missing | missing | missing |
| DES-014–015 | n/a | n/a | n/a | n/a | n/a | partial | n/a | n/a | n/a | n/a | n/a | partial | partial | n/a | missing | missing | missing | missing |
| DES-026–027 | partial | partial | missing | partial | missing | missing | n/a | missing | n/a | n/a | partial | missing | missing | partial | partial | missing | missing | missing |

**Repo-wide:** **0** rows with **complete** contract coverage.

---

## 24. Implementation gap register

| Gap ID | Description | Affected |
|--------|-------------|----------|
| IV-DES-001 | `geometry_id` not emitted anywhere | All geo designs, evidence |
| IV-DES-002 | `forbidden_downstream_claims` not emitted | All designs |
| IV-DES-003 | `concurrent_multi_experiment_compatibility` not emitted | All designs |
| IV-DES-004 | Non-dict outputs lack contract adapters | DES-007–010 |
| IV-DES-005 | `supergeo_source_unit_map` not in output envelope | DES-010 |
| IV-DES-006 | Trim `excluded_units` / target_population not in envelope | DES-009 |
| IV-DES-007 | `block_ids` / `stratum_ids` / `pair_ids` not emitted | DES-004, 007, 008 |
| IV-DES-008 | `shared_control_policy` / `control_reuse_policy` not emitted | DES-011, tier-1 |
| IV-DES-009 | `cell_ids` not emitted | DES-011 |
| IV-DES-010 | Power/MDE not linked to DesignEvidence | DES-012–014, geo_runner |
| IV-DES-011 | `assignment_probability` not in evidence | Tier-1 designs |
| IV-DES-012 | `reproducibility_hash` incomplete | Evidence envelope |
| IV-DES-013 | Rerandomization identity not preserved in evidence | DES-006, geo_runner L59 |
| IV-DES-014 | Inference caveats (rerandomization, blocks, pairs) not emitted | DES-006–008 |
| IV-DES-015 | Thinning population semantics ambiguous | DES-005 |
| IV-DES-016 | No `DesignOutputContract` validation tests | Repo-wide |
| IV-DES-017 | TROP/Bayesian future metadata absent | Expected — not a blocker |

---

## 25. Hard blockers

Preventing contract-complete or governed downstream consumption:

1. **Missing `geometry_id`** on all design output paths (IV-DES-001)  
2. **Missing `forbidden_downstream_claims`** (IV-DES-002)  
3. **Missing `concurrent_multi_experiment_compatibility`** (IV-DES-003)  
4. **No contract adapter** for QuickBlock, MatchedPair, TrimmedMatch, Supergeo (IV-DES-004)  
5. **Missing `supergeo_source_unit_map`** in supergeo envelope (IV-DES-005)  
6. **Missing trim/exclusion metadata** for TrimmedMatch envelope (IV-DES-006)  
7. **Missing multi-cell** `cell_ids` / shared-control / control-reuse metadata (IV-DES-008, 009)  
8. **No design contract validation tests** (IV-DES-016)  

**PASS on `validate_design` does not clear these blockers.**

---

## 26. Test coverage and evidence basis

| Evidence | Role |
|----------|------|
| `tests/test_design_registry.py` | Registry keys, geo_run flags |
| `tests/test_public_api.py` | QuickBlock, MatchedPair API surface |
| `tests/track_d/test_design_inventory_001.py` | Prior inventory generator |
| `tests/track_d/test_d5_des_trim_001.py` | Trim population shift characterization |
| `tests/track_d/test_d5_des_supergeo_001.py` | Supergeo geometry characterization |
| `tests/track_d/test_d5_pow_001e_design_geometry.py` (+ 001a–001d) | Tier-1 power/geometry |
| `tests/track_d/test_d5_des_001a_pre_period_matching.py` | Pre-period matching |
| `tests/fixtures/artifact_schemas/design_evidence_v1.json` | Emitted field schema |
| `tests/test_validation_coverage_doc.py` | Doc/governance coverage |
| D5-STAT reports | Reference designs only — not design validation |

Tests prove **coverage and smoke behavior**, not statistical validity or contract completeness.

---

## 27. Implications for future implementation work

Documented for later — **not in scope here:**

- Introduce/extend governed `DesignOutputContract` object  
- Emit `geometry_id`, `forbidden_downstream_claims`, concurrency status  
- Adapters: QuickBlock/MatchedPair → assignment dict; Trim/Supergeo → contract envelope  
- Emit block/stratum/pair IDs  
- Emit trim/supergeo metadata and population fields  
- Join `PowerContract` / MDE results to `DesignEvidence`  
- Preserve rerandomization identity and inference caveats in evidence  
- Emit compatibility hints  
- Add contract validation tests (harness)  

---

## 28. Implications for statistical validation

[`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) (design-side, future) must:

- Scope worlds to **observed** behavior from this artifact  
- Treat `adapter_required` designs as **blocked** or separately scoped until adapters exist  
- Treat `implementation_behavior_ambiguous` designs (ThinningDesign) as **blocked** until Layer 3 ambiguity resolved  
- Not assume contract fields that implementation validation proved missing  

---

## 29. Relationship to combination matrix and suitability

- [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) v2 rows must include **implementation validation status**, not design names alone  
- [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) consumes implementation statuses for DCM rows  
- [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md): **hard implementation blockers (§25) feed design guardrails** — IV-DES-001–016 map to BLOCK / REQUIRES_ADAPTER  
- [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md): suitability requires implementation validation pass **and** statistical validation **and** guardrails satisfied  
- Combinations with missing contract fields or `adapter_required` status remain **blocked**  

---

## 30. Governance gates

| Gate | Status |
|------|--------|
| Authorizes any design | **No** |
| Marks repo-wide contract compliance | **No** — 0/31 complete |
| Overrides DESIGN_OUTPUT_CONTRACT_001 | **No** |
| Allows MMM/MIP/LLM recommendations | **No** |
| Allows TrustReport / CalibrationSignal | **No** |

---

## 31. Current status and verdict

**Verdict:** `design_implementation_validation_complete_contract_blockers_identified`

| Metric | Value |
|--------|-------|
| Rows validated | 31 / 31 |
| `implementation_aligned_contract_complete` | **0** |
| `adapter_required` | 4 |
| `implementation_behavior_ambiguous` | 1 |
| Hard blockers | 8 classes (IV-DES-001–016) |
| Contract-complete | **0** |

**Not claimed:** production-ready, statistically validated, suitable, TrustReport-eligible, CalibrationSignal-eligible, MMM-ready, LLM-ready.

---

## 32. Roadmap

**Statistical validation protocol:** [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) — **Accepted**; derived from observed implementation statuses, contract blockers, and adapter-required scopes in this artifact (§9–§25). **Does not change implementation verdicts.**

**Suitability:** [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) ✅ **Accepted** — **current implementation blockers (§25) prevent downstream-ready suitability**; 0 contract-complete designs → universal `contract_blocked`.

**Enforcement plan:** [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) ✅ **Accepted** — **current implementation blockers (§24–§25) are routed into phased enforcement** (IV-DES-001–016 → Phases 2–4).

**Schema:** [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) ✅ **Accepted** — contract fields are **schema-defined but still not emitted** in code (0/31 contract-complete unchanged).

**Tier-1 emission plan:** [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) ✅ **Accepted** — **tier-1 gaps (IV-DES-001–016) mapped to emission plan**; **implementation verdict unchanged** (0/31 contract-complete; no fields emitted).

**Validation test plan:** [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) ✅ **Accepted** — **implementation blockers (IV-DES-001–016) remain unresolved until validation tests are implemented and pass**; verdict unchanged (0/31 contract-complete).

**Next artifact:** **`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001`**.

Guardrails: [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) ✅ **Accepted** — consumes hard blockers from §25.

---

## 33. Completion checklist

| Item | Status |
|------|--------|
| Inventory consumed | ✅ |
| Literature alignment consumed | ✅ |
| Output contract consumed | ✅ |
| Code inspected | ✅ §8 |
| Implementation behavior classified | ✅ §9–§22 |
| Contract coverage matrix | ✅ §23 |
| Blockers registered | ✅ §24–§25 |
| Roadmap updated | ✅ companion docs |
| No code changed | ✅ |
| Tests run | ✅ |

---

## 34. Companion doc updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Implementation validation complete |
| [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) | Consumed by validation |
| [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) | Fidelity checked |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Emission evaluated |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Next = statistical protocol |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Prerequisite for design statistical validation |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Lane status |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Implementation gaps |
| [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) | Requires impl + stat validation |
| [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Impl status required |
| [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) | Scope to validated behavior |

---

*DESIGN-IMPLEMENTATION-VALIDATION-001 v1.0.8 — Accepted; blockers until validation tests pass; verdict unchanged; next = DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.*
