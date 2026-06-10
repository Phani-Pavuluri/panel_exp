# Design Tier1 Contract Emission Plan 001

**Document ID:** DESIGN-TIER1-CONTRACT-EMISSION-PLAN-001  
**Title:** Design Tier1 Contract Emission Plan 001  
**Status:** **Accepted**  
**Scope:** Tier-1 geo-run design contract emission planning (Phase 2)  
**Artifact type:** Documentation / implementation plan — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) · [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md)

**Inputs:** [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) · [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) · [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) · [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md)

**Guardrails:** No code implementation · no schema validator · no fixture regeneration · no contract-complete status · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Tier1 Contract Emission Plan 001 |
| Status | **Accepted** |
| Scope | Tier-1 geo-run `design_contract` emission planning |
| Artifact type | Documentation / implementation plan |

Tenth design audit / enforcement artifact. **Phase 2** of [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md). Maps [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) fields to tier-1 producer paths for future code emission.

**Emission plan only — not implemented. No design is contract-complete.**

---

## 2. Purpose

This artifact defines:

1. **Which tier-1 designs** (DES-001–004, DES-006, constrained DES-011) emit `design_contract` first  
2. **Where** fields are produced (`geo_runner`, `DesignEvidence.from_assignment`, `DesignSpec`, `ExperimentEvidence`)  
3. **How** each schema block is populated — directly available, derivable, or requires new metadata  
4. **Phased future implementation** steps, fixture plan, and link to validation test plan  

---

## 3. Why this artifact exists

| Gap | Emission plan addresses |
|-----|-------------------------|
| Schema defined, **not emitted** | Maps schema → producers |
| Tier-1 geo-run is first practical path | DES-001–004 via `run_geo_experiment_design` |
| Guardrails/suitability need machine-readable fields | Governance defaults at emission time |
| `DesignEvidence` partial today | Gap analysis vs target blocks |
| Adapter designs should wait | QuickBlock/Trim/Supergeo explicitly out of scope |

---

## 4. Scope

Includes planning for:

- Tier-1 geo-run pipeline: `GeoExperimentDesign` → `run_geo_experiment_design` → `ExperimentEvidence.build`  
- `DesignEvidence.from_assignment` (nested in `ExperimentEvidence`)  
- `DesignSpec` / `spec_from_geo_design`  
- Registry keys DES-001–004; Rerandomization wrapper (DES-006); `n_test_grps` multi-cell (DES-011 partial)  
- Fixture and test **planning** (not regeneration)  
- Backward compatibility for legacy evidence without `design_contract`  

**Out of scope:** QuickBlock, MatchedPair, TrimmedMatch, Supergeo (adapter Phase 4); ThinningDesign (DES-005) deferred pending thinning semantics ADR.

---

## 5. Non-goals

- No Python emission implementation  
- No schema validator module  
- No `design_evidence_v1.json` regeneration  
- No adapter work  
- No trim/supergeo contract blocks  
- No `D5-DES-STAT-*` execution  
- No downstream authorization or design promotion  

---

## 6. Tier-1 design scope

| DES ID | Design name | Registry key | Callable path | Current output | Feasibility | Key missing fields | Plan status |
|--------|-------------|--------------|---------------|----------------|-------------|-------------------|-------------|
| DES-001 | greedy_match_markets | `greedy_match_markets` | `geo_runner` → base via `Rerandomization` | Assignment dict + `validation_summary` | **High** | `geometry_id`, forbidden claims, concurrency, stratum n/a | `planned_not_implemented` |
| DES-002 | CompleteRandomization | `complete_randomization` | Same | Same | **High** | Universal contract blockers | `planned_not_implemented` |
| DES-003 | BalancedRandomization | `balanced_randomization` | Same | Same | **High** | + balance diagnostics linkage | `planned_not_implemented` |
| DES-004 | StratifiedRandomization | `stratified_randomization` | Same | Same | **Medium** | + `stratum_ids` (requires design-specific logic) | `planned_not_implemented` |
| DES-006 | Rerandomization | (wrapper, not registry) | `GeoExperimentDesign.create_design()` always wraps base | Evidence shows **base** class name only (IV-DES-013) | **Medium** | `wrapper_identity`, acceptance metadata | `planned_not_implemented` |
| DES-011 | multi_test_groups | `n_test_grps` config | `geo.n_test_grps > 1` | Assignment keys `test_*` | **Medium** | `cell_ids`, shared-control policy | `planned_partial` |
| DES-005 | ThinningDesign | `thinningdesign` | Geo allowlist but ambiguous population | Partial | **Deferred** | Thinning semantics | `out_of_tier1_wave` |

**0/31 contract-complete at authoring — unchanged by this plan.**

---

## 7. Producer path map

```text
GeoExperimentDesign.run_design()
  → DesignRunContext
  → run_geo_experiment_design(ctx)          # panel_exp/design/geo_runner.py
      1. create_design() → Rerandomization(base_randomizer_cls)
      2. design.assign(...) → rs_dp_grps    # assignment dict
      3. _build_geo_spec() → DesignSpec     # spec_from_geo_design
      4. validate_design(...) → validation_summary
      5. ExperimentEvidence.build(spec, assignment, validation_summary, ...)
           → DesignEvidence.from_assignment(...)  # evidence.py:456
      6. _calculate_sensitivity_metrics()   # power — not linked to contract today
```

| Producer | Emits today | Future `design_contract` role |
|----------|-------------|------------------------------|
| `geo_runner.run_geo_experiment_design` | Orchestration; calls evidence build | **Primary injection point** for geometry, concurrency, multi-cell flags |
| `DesignEvidence.from_assignment` | `assignment`, `validation_summary`, hashes | **Attach `design_contract` nested block** in `to_dict()` |
| `DesignSpec` / `spec_from_geo_design` | Identity, periods, `design_method`, seed | Feed `design_identity`, `time_windows`, `outcomes` |
| `ExperimentEvidence.build` | Wraps design evidence | Surface contract block at experiment level |
| `design/registry.py` | `DesignSpec` metadata per design | `design_inventory_id`, `design_family` lookup |
| Assignment dict | Arm → unit lists | `assignment` block |
| `validate_design` | `validation_summary` | `diagnostics` partial; **not** contract PASS |
| `prepare_constraint_context` | Internal only | Future `units.eligible_units` / exclusions |
| Power sensitivity | DataFrames only | Out of tier-1 contract block (Phase 7 linkage) |

**Observed:** `design_method = design_class_name(geo.base_randomizer_cls)` — **base** randomizer name, not `Rerandomization` (IV-DES-013).

---

## 8. Schema field emission map

| Schema block | Primary source | Status |
|--------------|----------------|--------|
| Envelope (`schema_name`, `schema_version`, …) | Constants + builder | `requires_new_metadata` |
| `design_identity` | Registry + `DesignSpec` + hashes | `derivable` + `requires_new_metadata` (DES IDs) |
| `geometry` | Derived from `n_test_grps`, design family | `requires_new_metadata` |
| `assignment` | Assignment dict | `directly_available` + `derivable` |
| `units` | Panel index + whitelists + constraints | `derivable` + `requires_new_metadata` |
| `time_windows` | `DesignSpec` periods | `directly_available` |
| `outcomes` | `DesignSpec` outcome column | `directly_available` |
| `multi_cell` | `n_test_grps`, assignment keys | `derivable` + `requires_new_metadata` |
| `concurrency` | Static defaults + geo config | `requires_new_metadata` |
| `structure` | Stratified only: stratum map | `requires_design_specific_logic` (DES-004) |
| `trim_thin` / `supergeo` | — | `not_in_tier1_scope` |
| `power_mde` | Power sensitivity (unlinked) | `not_in_tier1_scope` (tier-1 wave) |
| `diagnostics` | `validation_summary`, `diagnostics` | `directly_available` (partial) |
| `governance` | Conservative defaults + guardrail evaluator | `requires_new_metadata` |
| `compatibility` | Matrix hints (conservative) | `requires_new_metadata` |
| `provenance` | Module path, hashes, timestamps | `directly_available` + `derivable` |

---

## 9. Universal field emission plan

| Field | Emission approach | Default until validator |
|-------|-------------------|-------------------------|
| `schema_name` | Constant `"DESIGN-CONTRACT-SCHEMA-001"` | N/A |
| `schema_version` | Constant `"1.0.0"` | N/A |
| `artifact_type` | `"design_output_contract"` | N/A |
| `design_contract_status` | Computed §23 | `contract_incomplete` |
| `design_inventory_id` | Registry lookup table DES-001–004 | Required at emission |
| `design_name` | Registry key / `spec.design_method` | Direct |
| `design_family` | Registry metadata | Direct |
| `registry_key` | Registry name | Direct |
| `geometry_id` | `unit_panel_single_cell` if `n_test_grps==1`; else `multi_cell_per_cell` | **New** |
| `forbidden_downstream_claims` | Static list per geometry (§11) | **New** — non-empty |
| `concurrent_multi_experiment_compatibility` | `"not_evaluated"` → `"restricted"` | **New** |
| `guardrail_status` | `"BLOCK"` or `"REQUIRES_STATISTICAL_VALIDATION"` | Conservative |
| `suitability_status` | `"contract_blocked"` + `"stat_validation_required"` | Conservative |
| `statistical_validation_status` | `"protocol_defined_not_executed"` | Static |
| `downstream_authorization_status` | `"blocked"` | Static |

---

## 10. Identity metadata plan

| Field | Plan |
|-------|------|
| `design_inventory_id` | Map registry key → DES-001–004 |
| `design_method_class` | `geo.base_randomizer_cls.__name__` |
| `wrapper_identity` | When `create_design()` returns `Rerandomization`: emit `"Rerandomization"` + base class — **fix IV-DES-013** |
| `registry_key` | From `get_design_registry().resolve(base)` |
| `random_seed` | `geo.random_state` / `DesignSpec` |
| `reproducibility_hash` | Combine `assignment_hash`, `spec_hash`, contract canonical JSON hash |
| `design_version` | `package_version` from evidence |

---

## 11. Geometry metadata plan

| Rule | Tier-1 default |
|------|----------------|
| `n_test_grps == 1` | `geometry_id = unit_panel_single_cell` |
| `n_test_grps > 1` | `geometry_id = multi_cell_per_cell` |
| `bridge_status` | `direct` for single-cell unit-panel |
| `target_population_status` | `full_panel` (no trim in tier-1 wave) |
| `geometry_claims_forbidden` | `aggregate_two_row`, `pooled_multi_cell`, `supergeo`, `trimmed_geometry` |
| Pooled/portfolio | Forbidden via governance + multi_cell flags |

---

## 12. Assignment metadata plan

| Field | Source |
|-------|--------|
| `assignment_map` | `rs_dp_grps` canonical |
| `treated_units` | Union of `test_*` arms |
| `control_units` | `control` arm |
| `treatment_labels` / `control_labels` | Dict keys |
| `assignment_is_exclusive` | Validate no unit in multiple arms |
| `duplicate_assignment_count` | Count from exclusivity check |
| `missing_assignment_count` | Eligible units not in any arm |
| `assignment_probability` | `tp` from geo_runner when set; else derived |
| `assignment_rule` | Registry design name + rerandomization if wrapped |

**Limitation:** `assignment_probability` not in evidence today — emit from `DesignSpec` at build time.

---

## 13. Unit universe metadata plan

| Field | Plan |
|-------|------|
| `all_units` | Panel wide index |
| `eligible_units` | Post whitelist/blacklist — call or mirror `prepare_constraint_context` |
| `excluded_units` | Set difference; empty if none |
| `donor_pool_units` | Control arm units (tier-1 default) |
| `exclusion_policy` | Document whitelist/blacklist rules from geo config |
| Hidden exclusions | **BLOCK** if eligible ⊂ all without documented reason |

---

## 14. Time window metadata plan

| Field | Source (`DesignSpec` / geo) |
|-------|----------------------------|
| `pre_period_start` / `pre_period_end` | `TimePeriod(0, train_length)` |
| `test_period_start` / `test_period_end` | `train_length` → end |
| `cooldown_*` | `null` / not_applicable |
| `time_granularity` | From panel if known; else `"unknown"` |
| `calendar_alignment_status` | `"unknown"` unless geo documents |

---

## 15. Outcome/covariate metadata plan

| Field | Source |
|-------|--------|
| `primary_outcome` | `geo.outcome_column` |
| `balance_covariates` | Stratified/Balanced/Rerandomization: KPI columns used in assign |
| `covariates_used` | Matching designs: pre-period features if available |
| `missing_covariate_policy` | `"not_declared"` default |
| `metric_definition_id` | Optional null |

---

## 16. Multi-cell / concurrency metadata plan

When `n_test_grps > 1` (DES-011 partial):

| Field | Plan |
|-------|------|
| `is_multi_cell` | `true` |
| `cell_ids` | `test_0`, …, `test_{n-1}` from assignment keys |
| `cell_assignment_map` | Per-key treated lists |
| `shared_control_mode` | Default `"shared"` if single `control` arm |
| `shared_control_policy` | **Required new string** — document donor sharing |
| `control_reuse_policy` | **Required** when shared |
| `pooled_claims_allowed` | `false` |
| `portfolio_claims_allowed` | `false` |
| `concurrent_multi_experiment_compatibility` | `"restricted"` |

---

## 17. Structure metadata plan

| Design | Fields |
|--------|--------|
| DES-001–003, DES-006 | `structure` block omitted or all `not_applicable` |
| DES-004 StratifiedRandomization | `stratum_ids`, `unit_to_stratum_map` — **requires design-specific logic** (assign must expose or post-process) |
| Block/pair | `not_in_tier1_scope` |
| Rerandomization | `structure_respected_by_inference` optional; acceptance iteration count if exposed |

`structure_missing_policy`: `block` for DES-004 if strata required but absent.

---

## 18. Diagnostics metadata plan

| Field | Mapping |
|-------|---------|
| `balance_diagnostics` | From `validation_summary` checks + `diagnostics` dict |
| `diagnostic_completeness_status` | `partial` until full balance export |
| Missing required diagnostics | **WARN** at emission; **BLOCK** only when validator requires |

`validate_design` PASS ≠ contract complete.

---

## 19. Governance metadata plan

| Field | Default at emission |
|-------|---------------------|
| `forbidden_downstream_claims` | Non-empty: trust_report, calibration_signal, mmm_calibration, llm_product_recommendation, production_experiment_recommendation, pooled_portfolio_lift, suitability_approved |
| `guardrail_status` | `REQUIRES_STATISTICAL_VALIDATION` or `BLOCK` |
| `guardrail_reason_codes` | `D-COMB-STAT-VALIDATION-REQUIRED` until D5-DES-STAT |
| `suitability_status` | `contract_blocked` until validator PASS |
| `suitability_reason_codes` | `D-SUIT-CONTRACT-BLOCKED`, `D-SUIT-STAT-VALIDATION-REQUIRED` |
| `combination_matrix_status` | Advisory string from DCM tier-1 rows |
| `downstream_authorization_status` | **`blocked`** |

---

## 20. Compatibility metadata plan

| Field | Tier-1 conservative value |
|-------|---------------------------|
| `compatible_estimators` | Hints only: `scm_jk_unit_panel`, `augsynth_point_unit_panel` — **not approval** |
| `requires_statistical_validation` | `true` |
| `requires_adapter` | `false` |
| `requires_bridge` | `false` only for `unit_panel_single_cell` |
| `incompatible_reason_codes` | Geometry mismatches for TBR/DID without bridge |

---

## 21. Provenance metadata plan

| Field | Source |
|-------|--------|
| `producer_module` | `"panel_exp.design.geo_runner"` |
| `producer_function` | `"run_geo_experiment_design"` |
| `spec_hash` | `DesignEvidence.spec_hash` |
| `source_data_hash` | `input_data_hash` |
| `run_id` | `experiment_id` |
| `repo_commit` | `code_version` env |
| `schema_validation_time` | **Future only** — when validator runs |

---

## 22. Design-specific emission notes

### greedy_match_markets (DES-001)

- **Special:** pre-period matching covariates; donor pool semantics  
- **Limitation:** INV-D1 pre-period matching not in contract today  
- **Tests:** assignment exclusivity; geometry `unit_panel_single_cell`  

### CompleteRandomization (DES-002)

- **Special:** Bernoulli arms; `assignment_probability` from `tp`  
- **Blockers:** universal contract fields still missing until implementation  

### BalancedRandomization (DES-003)

- **Special:** volume-share balance; link balance diagnostics  
- **Tests:** balance covariates in `outcomes` block  

### StratifiedRandomization (DES-004)

- **Special:** `stratum_ids` emission — **requires_design_specific_logic**  
- **Blockers:** IV-DES-007 until strata exposed from assign  
- **Tests:** conditional stratum presence  

### Rerandomization wrapper (DES-006)

- **Special:** preserve `wrapper_identity="Rerandomization"` + `base_randomizer_cls`  
- **Blockers:** IV-DES-013 — evidence currently shows base name only  
- **Tests:** identity fixture must assert wrapper ≠ base in contract  

### multi_test_groups (DES-011 partial)

- **Special:** only when `n_test_grps > 1`  
- **Blockers:** IV-DES-008, IV-DES-009 shared-control / cell metadata  
- **Tests:** multi-cell fixture; pooled claims forbidden  

---

## 23. Contract status computation plan

| Status | Condition (future validator) |
|--------|------------------------------|
| `contract_complete` | All universal + conditional fields valid; validator PASS |
| `contract_complete_with_warnings` | Required present; recommended missing |
| `contract_incomplete` | Emitted block but validator not PASS — **default after first emission** |
| `contract_blocked` | Missing universal field or validator BLOCK |
| `contract_unknown` | No `design_contract` key (legacy) |

**Plan default after implementation:** `contract_incomplete` until `DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001` tests pass. **Never default to `contract_complete` at first emission.**

---

## 24. Backward compatibility plan

| Policy | Rule |
|--------|------|
| Legacy evidence | No `design_contract` → `contract_unknown` |
| No silent upgrade | Old JSON unchanged on disk |
| `to_dict()` | Additive `design_contract` key — minor evidence version bump |
| Field aliases | `design_method` retained; contract uses `design_name` |
| Public API | `DesignEvidence` fields unchanged; new optional nested dict |

---

## 25. Fixture plan

| Fixture | Purpose |
|---------|---------|
| `design_evidence_v1.json` | **Unchanged** at planning time |
| `design_evidence_v2_tier1_complete_randomization.json` (future) | Golden tier-1 with `design_contract` |
| `design_evidence_v2_tier1_negative_missing_geometry.json` (future) | Missing `geometry_id` |
| `design_evidence_v2_tier1_multicell.json` (future) | `n_test_grps=2` |
| `design_evidence_v2_tier1_rerandomization_identity.json` (future) | Wrapper + base identity |
| `design_evidence_v2_tier1_stratified.json` (future) | Stratum IDs |

**No fixture regeneration in this artifact.**

---

## 26. Test plan

**Validation test plan:** [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) ✅ **Accepted** — defines required positive, negative, conditional, fixture, and CI tests **before tier-1 emission can claim contract completeness**. **Tests not implemented.**

Key requirements (see test plan for full matrix):

- Universal field presence after emission  
- Enum validity (`geometry_id`, forbidden claims)  
- Missing universal → BLOCK  
- DES-004 conditional stratum → BLOCK if absent  
- Rerandomization wrapper identity preserved  
- Multi-cell cell_ids + shared-control when `n_test_grps>1`  
- `downstream_authorization_status=blocked` always for tier-1 wave  
- `validate_design` PASS does not imply `contract_complete`  

---

## 27. Implementation phase plan

| Step | Work |
|------|------|
| 1 | Schema constants / typed dict spec (from DESIGN_CONTRACT_SCHEMA_001) |
| 2 | `build_design_contract_tier1(...)` helper (future module) |
| 3 | Extend `DesignEvidence.from_assignment` to accept/emit `design_contract` |
| 4 | Call builder from `geo_runner` before `ExperimentEvidence.build` |
| 5 | Map registry → DES inventory IDs |
| 6 | Conservative governance defaults |
| 7 | Fixture updates (v2) |
| 8 | Validation tests per DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001 |
| 9 | Full pytest suite |
| 10 | Re-run implementation validation + suitability assessment |

---

## 28. Risk register

| ID | Risk | Mitigation |
|----|------|------------|
| T1-R01 | Public API breakage | Additive `design_contract` only |
| T1-R02 | Overclaiming `contract_complete` | Default `contract_incomplete`; validator gate |
| T1-R03 | Silent downstream authorization | `downstream_authorization_status=blocked` |
| T1-R04 | Rerandomization identity loss | Explicit `wrapper_identity` field |
| T1-R05 | Multi-cell silent pooling | `pooled_claims_allowed=false` |
| T1-R06 | Wrong geometry default | Explicit rules §11; tests |
| T1-R07 | Compatibility hints as approval | Document "hints only" |
| T1-R08 | Stale fixture drift | v2 fixtures separate from v1 |

---

## 29. Current status assessment

| Item | Status |
|------|--------|
| Emission plan | ✅ This artifact |
| Code emission | ❌ |
| Fields in `DesignEvidence` | ❌ No `design_contract` |
| Validator | ❌ |
| Fixtures updated | ❌ |
| Contract-complete designs | **0 / 31** |
| Downstream | **Blocked** |

---

## 30. Relationship to adapter-required designs

QuickBlock, MatchedPair, TrimmedMatch, Supergeo — **not in tier-1 emission scope**. Adapter emission plans follow after tier-1 path proves schema + validator pattern per enforcement plan Phase 4.

---

## 31. Relationship to statistical validation

`D5-DES-STAT-TIER1-001` and related harnesses **cannot** consume contract-complete artifacts until emission + validation tests exist. Protocol worlds may assert `contract_incomplete` or explicit BLOCK until then.

---

## 32. Relationship to guardrails / suitability

Tier-1 designs remain **`contract_blocked`** / **`REQUIRES_STATISTICAL_VALIDATION`** in guardrails and suitability until:

1. Emission implemented  
2. Validation tests pass  
3. Optional runtime enforcement (`DESIGN_GUARDRAIL_ENFORCEMENT_001`)  

This plan does not change guardrail or suitability verdicts.

---

## 33. Governance gates

| Gate | Status |
|------|--------|
| Emission plan defined | ✅ |
| Emission implemented | ❌ |
| Designs promoted | ❌ |
| TrustReport / CalibrationSignal / MMM / LLM | ❌ **BLOCKED** |

This artifact does not implement emission, validate completeness, promote designs, or authorize product layers.

---

## 34. Current status and verdict

| Field | Value |
|-------|-------|
| Verdict | `design_tier1_contract_emission_plan_defined_not_implemented` |
| Enforcement phase | **2** (planned; not started) |
| Tier-1 contract-complete | **0** |

### Search methodology (2026-06-10)

```bash
grep -R "DESIGN_CONTRACT_SCHEMA_001\|DESIGN_CONTRACT_ENFORCEMENT_PLAN_001\|DESIGN_OUTPUT_CONTRACT_001" -n docs
grep -R "DesignEvidence\|ExperimentEvidence\|DesignSpec\|from_assignment\|geo_runner\|run_geo_experiment_design" -n panel_exp tests docs
grep -R "geometry_id\|forbidden_downstream_claims\|concurrent_multi_experiment_compatibility\|design_contract" -n panel_exp tests docs
grep -R "CompleteRandomization\|BalancedRandomization\|StratifiedRandomization\|Rerandomization\|greedy_match_markets\|n_test_grps" -n panel_exp tests docs
grep -R "assignment\|treatment\|control\|cell_id\|eligible\|excluded\|seed\|hash\|balance\|validation_summary" -n panel_exp/design panel_exp/evidence.py panel_exp/spec.py tests docs
find tests -iname "*design*" -o -iname "*evidence*" -o -iname "*contract*" -o -iname "*schema*" -o -iname "*validation*"
find panel_exp/design -type f
```

**Code inspected (read-only):** `evidence.py`, `design/geo_runner.py`, `design/geo_experiment_design.py`, `spec.py`, `design/assign.py`, `design/registry.py`, `design/validation.py`, `design_evidence_v1.json`, registry and Track D tests.

---

## 35. Roadmap

**Validator implementation plan:** [`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md`](DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md) ✅ **Accepted** — tier-1 emission must call or be checked by the future validator **before any `contract_complete` claim**. **Validator not implemented.**

**Next artifact:** **`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001`**

Then: fixtures → tests → tier-1 code emission.

---

## 36. Completion checklist

| Item | Status |
|------|--------|
| Prerequisites inspected | ✅ |
| Tier-1 scope defined | ✅ §6 |
| Producer paths mapped | ✅ §7 |
| Schema field emission map | ✅ §8 |
| Design-specific notes | ✅ §22 |
| Fixture/test plan | ✅ §25–§26 |
| Roadmap updated | ✅ companion docs |
| No code changed | ✅ |
| Tests run | ✅ (completion report) |

---

## 37. Companion doc updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Emission plan Accepted; next = validation test plan |
| [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) | Tier-1 emission plan |
| [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) | Phase 2 defined |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | Tier-1 gaps mapped |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Tier-1 emission planned |
| [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) | Runtime waits on emission + tests |
| [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) | Tier-1 remains blocked |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Emission plan complete |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Bridge before validation tests |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Emission gap |
| [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md) | Planning blocked |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Lane status |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |

---

*DESIGN-TIER1-CONTRACT-EMISSION-PLAN-001 v1.0.2 — Accepted; validator plan defined; emission requires validator pass; next = DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001.*
