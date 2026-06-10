# Design Contract Enforcement Plan 001

**Document ID:** DESIGN-CONTRACT-ENFORCEMENT-PLAN-001  
**Title:** Design Contract Enforcement Plan 001  
**Status:** **Accepted**  
**Scope:** GeoX / `panel_exp` design output contract enforcement planning  
**Artifact type:** Documentation / governance / enforcement plan — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md)

**Inputs:** [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) · [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) · [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) · [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) · [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md)

**Guardrails:** No code implementation · no schema implementation · no runtime enforcement · no statistical validation execution · no design promotion · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Contract Enforcement Plan 001 |
| Status | **Accepted** |
| Scope | Design output contract enforcement planning |
| Artifact type | Documentation / governance / enforcement plan |

Eighth concrete design audit artifact. Defines **how** required design contract fields should be emitted, validated, and enforced across design output paths — bridging governance classification to future implementation.

**This artifact is a plan, not runtime enforcement. No downstream role is authorized.**

---

## 2. Purpose

This artifact defines the implementation plan for:

1. **Emitting** required fields from [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) on `DesignEvidence`, `ExperimentEvidence`, `geo_runner`, and design registry paths  
2. **Validating** field presence, semantics, and design-family conditionals before governed consumption  
3. **Enforcing** guardrail and suitability decisions via machine-readable contract status — not prose  

Moves the design audit lane from **governance classification** (`DESIGN_GUARDRAILS_001`, `DESIGN_SUITABILITY_FRAMEWORK_001`) toward **contract-complete evidence**.

---

## 3. Why this artifact exists

| Finding | Enforcement need |
|---------|------------------|
| **0/31 contract-complete** designs per implementation validation | Plan closes IV-DES-001–016 systematically |
| Missing `geometry_id`, `forbidden_downstream_claims`, concurrency status | Blocks suitability and all governed downstream use |
| `DesignEvidence` emits assignment + `validation_summary` only | Partial metadata — see `panel_exp/evidence.py` `DesignEvidence` |
| `geo_runner` builds `ExperimentEvidence` without contract envelope | `panel_exp/design/geo_runner.py` — no `geometry_id` emission |
| Guardrails/suitability need machine-readable fields | Enforcement planning precedes `DESIGN_GUARDRAIL_ENFORCEMENT_001` |
| **0 downstream suitable designs** | Positive suitability impossible without contract emission |

Governance artifacts identified blockers; this plan sequences **schema → emission → validation → adapters → bridges → runtime enforcement**.

---

## 4. Scope

Applies to enforcement planning for:

| Surface | Path | Role |
|---------|------|------|
| `DesignEvidence` | `panel_exp/evidence.py` | Primary design-phase evidence envelope |
| `ExperimentEvidence` | `panel_exp/evidence.py` | Wraps design + inference metadata |
| `DesignSpec` | `panel_exp/spec.py` | Run specification and content hash |
| `DesignMethod` | `panel_exp/spec.py` | Registry enum |
| `geo_runner` | `panel_exp/design/geo_runner.py` | Tier-1 geo-run pipeline |
| `GeoExperimentDesign` | `panel_exp/design/geo_experiment_design.py` | Orchestration entry |
| Design registry | `panel_exp/design/registry.py` | `get_design_registry()` paths |
| Tier-1 designs | `panel_exp/design/assign.py` | DES-001–006 |
| Adapter-required | `quickblock.py`, `matched_pair.py`, `trimmed_match.py`, `supergeos.py` | DES-007–010 |
| Validation | `panel_exp/design/validation.py` | `validate_design` — not contract validation today |
| Power/MDE | `panel_exp/design/power.py` | `PowerAnalysis`, `PowerContract` |
| Constraints | `panel_exp/design/constraints.py` | Eligibility helpers |
| Tests | `tests/test_design_registry.py`, fixture `design_evidence_v1.json` | Golden/negative contract tests (planned) |
| Future archives | `track_d/archives/` | JSON compatibility after schema |

---

## 5. Non-goals

- No design, estimator, or inference **code implementation** in this artifact  
- No `DESIGN_CONTRACT_SCHEMA_001` implementation (planned Phase 1)  
- No runtime guardrail enforcement (`DESIGN_GUARDRAIL_ENFORCEMENT_001`)  
- No statistical validation execution (`D5-DES-STAT-*`)  
- No design or combination promotion  
- No TrustReport, CalibrationSignal, MMM, or LLM authorization  

---

## 6. Enforcement status taxonomy

| Status | Meaning |
|--------|---------|
| `planned_not_implemented` | Documented in this plan only — **current default** |
| `schema_required` | Awaiting `DESIGN_CONTRACT_SCHEMA_001` |
| `emission_required` | Schema exists; producer path must emit field |
| `validation_required` | Emission exists; validator must check field |
| `adapter_required` | Non-dict/native output needs adapter before emission |
| `bridge_required` | Bridge metadata fields before cross-geometry claims |
| `test_required` | Contract test must exist before promotion |
| `blocked_until_implemented` | Downstream governed use blocked |
| `future_runtime_enforcement` | Guardrail runtime wiring deferred |

---

## 7. Required contract field inventory

Summary table — full contract in [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) §6–§25.

| Field | Req | Design groups | Producer path (planned) | Validation rule | Blocker if missing | Consumers |
|-------|-----|---------------|------------------------|-----------------|-------------------|-----------|
| `geometry_id` | **Required** | All geo designs | `geo_runner` → `DesignEvidence` contract block | Canonical ID from geometry bridge | BLOCK (IV-DES-001) | Guardrails, matrix, suitability |
| `forbidden_downstream_claims` | **Required** | All | Contract block on evidence | Non-empty list | BLOCK (IV-DES-002) | Guardrails, suitability |
| `concurrent_multi_experiment_compatibility` | **Required** | All | Contract block | Enum per contract §11 | BLOCK (IV-DES-003) | Guardrails, planning |
| `design_method_id` / `design_inventory_id` | **Required** | All | `DesignSpec` + registry | DES-001–031 mapping | BLOCK | Inventory, suitability |
| `design_family` | **Required** | All | Registry metadata | Literature-aligned family | WARN → BLOCK for pairing | Matrix, suitability |
| `treated_units` / `control_units` | **Required** | All assignment designs | Derived from `assignment` dict | Non-empty when assigned | BLOCK | Estimator paths |
| `treatment_labels` / `control_label` | **Required** | All | Assignment keys | `test_*`, `control` present | BLOCK | Readout semantics |
| `unit_id_field` | **Required** | Geo-run | `DesignSpec` | Column name present | BLOCK | Panel construction |
| `eligible_units` / `excluded_units` | **Conditional** | Trim, thin, whitelist | Constraints + design output | Counts reconcile | BLOCK for trim (IV-DES-006) | Bridge, suitability |
| `assignment_by_unit` | **Required** | Dict-path designs | `assignment` dict inversion | Bijection check | BLOCK | Estimators |
| `assignment_probability` | **Optional** | Tier-1 | `geo_runner` / `DesignSpec` | Documented or null policy | WARN | Power, DID |
| `random_seed` | **Required** | All stochastic | `DesignSpec.random_state` | Integer or documented null | WARN | Reproducibility |
| `reproducibility_hash` | **Required** | All | `assignment_hash` + contract hash | Stable across rerun | WARN (IV-DES-012) | Audit |
| `pre_period_window` / `test_window` | **Required** | Geo-run | `DesignSpec` periods | Valid ranges | WARN | Estimators |
| `balance_diagnostics` | **Optional** | Tier-1, stratified | `validation_summary` / metrics | Partial today | WARN | Suitability |
| `target_population_status` | **Required** | Trim, supergeo | Contract block | full/trimmed/supergeo | BLOCK for transitions | Bridge |
| `bridge_status` | **Conditional** | Trim, supergeo, multi-cell | Contract block | direct/bridge_required | BLOCK unsupported claims | Guardrails |
| `adapter_status` | **Conditional** | DES-007–010 | Adapter layer | none/required/satisfied | BLOCK downstream | Suitability |
| `validation_status` | **Required** | All geo-run | `validation_summary.status` | PASS/WARN/FAIL | WARN only — not contract PASS | Legacy gate |
| `artifact_status` | **Required** | All | Contract validator | complete/incomplete/blocked | BLOCK if incomplete | Suitability |
| `guardrail_status` | **Derived** | All | Post-validation evaluator | PASS/WARN/BLOCK/REQUIRES_* | BLOCK | Planning |
| `suitability_status` | **Derived** | All | Suitability evaluator | Category from framework | BLOCK product | Planning |
| `cell_ids` | **Conditional** | multi-cell (`n_test_grps>1`) | `geo_runner` | One per test arm | BLOCK (IV-DES-009) | MCELL |
| `shared_control_policy` | **Conditional** | Multi-cell, shared control | Contract block | Policy enum | BLOCK (IV-DES-008) | Guardrails |
| `control_reuse_policy` | **Conditional** | Shared control | Contract block | Documented burden | BLOCK | Portfolio claims |
| `block_ids` | **Conditional** | QuickBlock, Rerandomization | Design output | Per-unit or per-block | BLOCK for block inference | DES-007, 006 |
| `stratum_ids` | **Conditional** | StratifiedRandomization | Design output | Stratum per unit | BLOCK | DES-004 |
| `pair_ids` | **Conditional** | MatchedPair | Adapter output | Pair structure | BLOCK | DES-008 |
| `trim_metadata` / `excluded_units` | **Conditional** | TrimmedMatch, Thinning | Adapter + contract | Listed exclusions | BLOCK | F-GEO-004 |
| `supergeo_source_unit_map` | **Conditional** | SupergeoModel | Adapter output | Source→supergeo map | BLOCK (IV-DES-005) | F-GEO-003 |
| `power_mde_linkage` | **Conditional** | PowerAnalysis path | `ExperimentEvidence` join | Reference to PowerContract | WARN | Planning only |
| `compatibility_hints` | **Optional** | All | Contract block | Estimator/inference hints | WARN | Matrix |

---

## 8. Current implementation gap table

From [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) §24–§25:

| Gap | Current state | Enforcement status | Phase |
|-----|---------------|-------------------|-------|
| `geometry_id` | **0 matches** in `panel_exp/` | `blocked_until_implemented` | 2 |
| `forbidden_downstream_claims` | Missing repo-wide | `blocked_until_implemented` | 2 |
| `concurrent_multi_experiment_compatibility` | Missing repo-wide | `blocked_until_implemented` | 2 |
| `shared_control_policy` / `control_reuse_policy` | Missing | `blocked_until_implemented` | 6 |
| `cell_ids` | Missing/incomplete | `blocked_until_implemented` | 6 |
| Trim `excluded_units` / target population | Missing envelope | `adapter_required` + `bridge_required` | 4–5 |
| `supergeo_source_unit_map` | Missing envelope | `adapter_required` + `bridge_required` | 4–5 |
| `block_ids` / `stratum_ids` / `pair_ids` | Missing | `emission_required` | 2–4 |
| Power/MDE linkage | Disconnected from evidence | `emission_required` | 7 |
| Rerandomization identity | Not preserved in evidence (IV-DES-013) | `emission_required` | 2 |
| `reproducibility_hash` | Incomplete vs contract spec | `validation_required` | 3 |
| Contract validation tests | **Absent** (IV-DES-016) | `test_required` | 3 |
| Adapter paths (DES-007–010) | No contract adapters | `adapter_required` | 4 |

**Repo inspection:** `DesignEvidence.to_dict()` emits `assignment`, `validation_summary`, `diagnostics` — no `geometry_id` or contract block. Fixture `tests/fixtures/artifact_schemas/design_evidence_v1.json` matches partial schema only.

---

## 9. Producer mapping

| Field group | Primary producer (planned) | Secondary / notes |
|-------------|---------------------------|-------------------|
| Core identity | `DesignSpec` → contract block on `DesignEvidence` | `design_method_id` from registry |
| Assignment | `assignment` dict from design `.assign()` | `geo_runner` normalizes via registry handler |
| Validation summary | `validate_design` → `validation_summary` | **Not** contract validation — separate validator planned |
| Geometry / bridge | New `contract` nested object on `DesignEvidence` | Derived from `n_test_grps`, design family, trim/supergeo flags |
| Multi-cell | `geo_runner` from `geo.n_test_grps` | Cell IDs from assignment keys |
| Power/MDE | `PowerContract` joined in `ExperimentEvidence.build` | Phase 7 |
| Adapter outputs | Per-design adapters → normalized dict | QuickBlock, MatchedPair, Trim, Supergeo |
| Derived guardrail/suitability | Post-build evaluator (future) | Read-only at emission time |

**Current producers (observed):**

- `DesignEvidence.from_assignment(spec, assignment, validation_summary=…)` — `evidence.py:456`  
- `ExperimentEvidence.build(spec, assignment, …)` — via `geo_runner.py:109`  
- `spec_from_geo_design` — `geo_runner._build_geo_spec`  

---

## 10. Consumer mapping

| Consumer | Fields required | Until enforcement |
|----------|----------------|-------------------|
| [`DESIGN_GUARDRAILS_001`](DESIGN_GUARDRAILS_001.md) | `geometry_id`, forbidden claims, concurrency, conditional metadata | Manual policy; runtime blocked |
| [`DESIGN_SUITABILITY_FRAMEWORK_001`](DESIGN_SUITABILITY_FRAMEWORK_001.md) | `artifact_status`, derived categories | All `contract_blocked` today |
| [`DESIGN_COMBINATION_VALIDATION_MATRIX_001`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) | `geometry_id`, design inventory ID, adapter/bridge status | Advisory matrix only |
| `D5-DES-STAT-*` harnesses | Contract completeness or scoped BLOCK in worlds | Not executable for promotion |
| Experiment planning (future) | Full contract block + suitability category | **Blocked** per orchestration roadmap |
| TrustReport / CalibrationSignal (future) | Contract complete + validation + suitability | **Blocked** |
| MMM / LLM (future) | Contract complete + suitability + product gates | **Blocked** |

---

## 11. Enforcement phases

| Phase | Name | Status | Deliverable |
|-------|------|--------|-------------|
| **0** | Docs/planning only | ✅ **Current** | This artifact |
| **1** | Contract schema definition | ✅ **Specified** | [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) — **not implemented in code** |
| **2** | Tier-1 geo-run emission | `emission_required` | `geometry_id`, forbidden claims, concurrency, identity |
| **3** | Validation tests | `test_required` | Negative + family-conditional tests |
| **4** | Adapter plans | `adapter_required` | QuickBlock, MatchedPair, Trim, Supergeo |
| **5** | Bridge metadata | `bridge_required` | Trim/supergeo/pooled/multi-cell bridge fields |
| **6** | Guardrail runtime enforcement | `future_runtime_enforcement` | `DESIGN_GUARDRAIL_ENFORCEMENT_001` |
| **7** | Statistical validation integration | `validation_required` | `D5-DES-STAT-*` reads contract block |
| **8** | Suitability re-evaluation | Planned | Re-run suitability after contract-complete rows exist |

**Rule:** Phases are sequential; Phase 6+ must not ship before Phase 1–3 for tier-1 path.

---

## 12. Phase 1: contract schema definition

**Schema artifact:** **`DESIGN_CONTRACT_SCHEMA_001`** ✅ **Accepted** — [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) defines Phase 1 schema specification. **Implementation does not exist.**

Future code deliverable must:

- Machine-readable schema (JSON Schema and/or typed dataclass spec) for `DesignOutputContract` nested block  
- Field required/conditional rules per design family  
- `artifact_status` enum: `contract_complete` · `contract_incomplete` · `contract_blocked` · `contract_unknown` (legacy)  
- Versioning policy aligned with `EVIDENCE_VERSION` in `evidence.py`  
- Compatibility map to `design_evidence_v1.json` fixture (extend, not silent replace)  

**Enforcement status:** `schema_required` — blocks Phase 2 implementation.

---

## 13. Phase 2: tier-1 emission plan

Target: DES-001–006 via `geo_runner` → `DesignEvidence` / `ExperimentEvidence`.

**Required additions:**

| Addition | Source logic |
|----------|--------------|
| `geometry_id` | Default `unit_panel_single_cell` when `n_test_grps==1`; `multi_cell_per_cell` when `n_test_grps>1` |
| `forbidden_downstream_claims` | Static list per geometry (no pooled lift, no trim-bridge claims, etc.) |
| `concurrent_multi_experiment_compatibility` | Default `not_evaluated` → `restricted` after audit |
| Unit universe | From panel index + whitelists/blacklists |
| Treated/control labels | From assignment dict keys |
| Eligibility/exclusion accounting | From constraint context (future join) |
| Design identity | Preserve `design_method` + rerandomization wrapper identity (IV-DES-013) |
| Reproducibility | `assignment_hash` + `spec_hash` + planned contract hash |
| Balance diagnostics | Extend `validation_summary` / `diagnostics` |
| `artifact_status` | Set `contract_incomplete` until all Phase 2 fields pass validator |

**Non-goal:** Do not claim `contract_complete` until Phase 3 tests pass.

---

## 14. Phase 3: validation test plan

Planned tests (no implementation in this artifact):

| Test | Assertion |
|------|-----------|
| `test_contract_missing_geometry_id_fails` | Validator returns BLOCK / `contract_blocked` |
| `test_contract_missing_forbidden_claims_fails` | BLOCK |
| `test_contract_conditional_cell_ids` | Multi-cell requires `cell_ids` |
| `test_contract_conditional_shared_control` | Shared control requires policy fields |
| `test_contract_trim_requires_excluded_units` | Trim family BLOCK without exclusions |
| `test_contract_supergeo_requires_source_map` | Supergeo BLOCK without map |
| `test_contract_geometry_id_valid` | Must be canonical enum |
| `test_contract_no_silent_pooling` | `pooled_claim_allowed` false by default |
| `test_contract_reproducibility_stable` | Same seed → same hashes |
| `test_contract_design_identity_preserved` | Rerandomization wrapper ≠ base only |
| `test_contract_legacy_output_unknown` | Pre-enforcement artifacts → `contract_unknown` |
| `test_docs_coverage` | Governance docs reference schema |

**CI policy:** Contract tests become required check before any suitability re-evaluation (Phase 8).

---

## 15. Phase 4: adapter-required design plan

| Design | Adapter plan | Output normalization |
|--------|--------------|---------------------|
| **QuickBlock** (DES-007) | `QuickBlockAdapter` → assignment dict + `block_ids` | Map `assign_all` output to contract arms |
| **MatchedPair** (DES-008) | `MatchedPairAdapter` → pair-structured dict + `pair_ids` | DataFrame/vector → unit→arm |
| **TrimmedMatchDesign** (DES-009) | `TrimmedMatchAdapter` + trim metadata | Emit `excluded_units`, `target_population_status=trimmed` |
| **SupergeoModel** (DES-010) | `SupergeoAdapter` | Emit `supergeo_source_unit_map`, `geometry_id=supergeo` |

Each adapter must:

1. Normalize to assignment dict compatible with `validate_assignment_dict`  
2. Attach `adapter_status=satisfied` when complete  
3. Set `artifact_status` only after Phase 3 validator PASS  
4. Register in design registry with `contract_adapter` metadata  

Harness target: `D5-DES-STAT-BLOCK-PAIR-001`, `D5-DES-STAT-TRIM-001`, `D5-DES-STAT-SUPERGEO-001`.

---

## 16. Phase 5: bridge-required metadata plan

| Bridge | Metadata fields | ADR |
|--------|-----------------|-----|
| Trim → full population | `bridge_status=bridge_required`, `target_population_status`, `excluded_units` | F-GEO-004 |
| Supergeo → original geo | `supergeo_source_unit_map`, distortion diagnostics | F-GEO-003 |
| Aggregate → unit panel | `geometry_id` transition flag | Geometry bridge |
| Per-cell → pooled | `pooled_claim_allowed=false`, `portfolio_claim_allowed=false` | Pooling ADR |

Emit `bridge_status` on contract block; default `direct` only when geometry unchanged.

---

## 17. Phase 6: multi-cell / shared-control plan

When `n_test_grps > 1` (DES-011 / `geo_runner`):

| Field | Plan |
|-------|------|
| `cell_ids` | Mirror assignment keys `test_0`, `test_1`, … |
| Treatment cell labels | Document per cell |
| `shared_control_policy` | Required — document donor sharing |
| `control_reuse_policy` | Required when controls shared across cells |
| Assignment exclusivity | Enforce via `validate_assignment_dict` |
| `pooled_claim_allowed` | Default **false** |
| `portfolio_claim_allowed` | Default **false** |

Portfolio lift claims remain BLOCK until pooling ADR + bridge validation.

---

## 18. Phase 7: power / MDE linkage plan

| Item | Plan |
|------|------|
| Join `PowerContract` to `ExperimentEvidence` | Reference `power_contract_id` in contract block |
| Geometry-aligned MDE | `geometry_id` on power run must match design geometry |
| Assumptions metadata | Variance, period, effect scale in linked contract |
| Planning-only guardrail | `forbidden_downstream_claims` includes causal readout |
| No CalibrationSignal/MMM | Power path never sets suitability > `planning_only` |

Harness: `D5-DES-STAT-POWER-MDE-001`.

---

## 19. Guardrail integration plan

Emitted contract fields feed [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md):

| Emitted field | Guardrail rule |
|---------------|----------------|
| Missing universal field | AUTO **BLOCK** (DGR-U-B01–B04) |
| `artifact_status=contract_incomplete` | **BLOCK** |
| `adapter_status=required` (unsatisfied) | **REQUIRES_ADAPTER** |
| `bridge_status=bridge_required` | **REQUIRES_BRIDGE** |
| `guardrail_status` (derived) | Written after evaluation — read-only for consumers |

**Prerequisite:** Phase 2–3 emission + validation before Phase 6 runtime enforcement.

---

## 20. Suitability integration plan

Emitted fields feed [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md):

| Emitted state | Suitability transition |
|---------------|------------------------|
| `artifact_status=contract_complete` | May exit `contract_blocked` → `stat_validation_required` |
| Adapter satisfied | May exit `adapter_required` |
| Bridge metadata present | May exit `bridge_required` for scoped claims |
| `suitability_status` (derived) | Computed post-guardrails — not hand-edited |

**Positive suitability requires contract enforcement implementation** — currently all rows `contract_blocked`.

---

## 21. Statistical validation integration plan

[`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) worlds must:

1. Assert `artifact_status` or explicit scoped BLOCK  
2. Refuse promotion when `contract_incomplete`  
3. Read `geometry_id` for world selection  
4. Use `excluded_units` / `supergeo_source_unit_map` in trim/supergeo worlds  

`D5-DES-STAT-*` harnesses consume contract block from evidence JSON — not inferred from assignment alone.

---

## 22. Experiment planning integration plan

Per [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md):

- Planning/ranking layers consume **`artifact_status=contract_complete`** designs only  
- Until enforcement Phases 1–3 complete: **no experiment planning consumption** of design outputs  
- Suitability categories remain advisory with all designs `contract_blocked`  
- LLM may explain plan status; cannot bypass BLOCK  

---

## 23. Backward compatibility plan

| Policy | Rule |
|--------|------|
| Legacy outputs | `artifact_status=contract_unknown` or `contract_incomplete` |
| No silent upgrade | Old JSON without contract block → downstream BLOCK |
| Historical D5 archives | Remain evidence-only; not re-labeled contract-complete |
| Transitional WARN | Allowed in logs when `validate_design` PASS but contract incomplete |
| Evidence version bump | Minor additive for contract block; document in schema |

---

## 24. Failure modes

| Failure | Detection | Policy |
|---------|-----------|--------|
| Missing required field | Contract validator | BLOCK |
| Invalid `geometry_id` | Enum check | BLOCK |
| Unsupported geometry transition | Bridge evaluator | BLOCK |
| Silent pooled output | `pooled_claim_allowed` false but pooled keys | BLOCK |
| Hidden excluded units | Trim count mismatch | BLOCK |
| Unsupported readout claim | vs `forbidden_downstream_claims` | BLOCK |
| Adapter missing | `adapter_status=required` | BLOCK downstream |
| Bridge missing | `bridge_status=bridge_required` | BLOCK unsupported claim |
| Inconsistent design identity | Rerandomization vs base mismatch | BLOCK |
| Reproducibility failure | Hash mismatch on rerun | BLOCK audit path |

---

## 25. Enforcement decision policy

| Condition | Decision |
|-----------|----------|
| Missing universal required field | **BLOCK** |
| Missing conditional field for design family | **BLOCK** for that family/use |
| Optional field missing | **WARN** if no consumer requires it |
| Invalid field value | **BLOCK** |
| Unknown design family | **BLOCK** or `NOT_EVALUATED` |
| Legacy output without contract block | **BLOCK** for downstream |
| `validate_design` PASS only | **WARN** — does not clear contract BLOCK |

Aligns with [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) universal rules.

---

## 26. Test and CI plan

| Layer | Plan |
|-------|------|
| Unit tests | Schema validator per field/group |
| Golden fixture | Extend `design_evidence_v1.json` with contract block exemplar |
| Negative tests | One test per IV-DES-001–016 blocker class |
| Family-specific tests | Stratified, multi-cell, trim, supergeo, block/pair |
| No backwards silent pass | `validate_design` PASS ≠ contract PASS |
| Docs coverage | `test_validation_coverage_doc.py` references this plan |
| CI gate (future) | Contract tests required before suitability re-evaluation PRs |

---

## 27. Migration plan

```text
1. DESIGN_CONTRACT_SCHEMA_001 (schema)
2. Add contract nested block to DesignEvidence (tier-1 emission)
3. Contract validator module + Phase 3 tests
4. Adapters for DES-007–010
5. Bridge metadata fields (Phase 5)
6. Update design_evidence_v1.json fixture + docs
7. Run full pytest suite (no archive regeneration)
8. Re-evaluate suitability (Phase 8) — expect tier-1 → stat_validation_required only
9. DESIGN_GUARDRAIL_ENFORCEMENT_001 (runtime)
10. D5-DES-STAT-* execution
```

**No promotion** at any step without explicit governance gate.

---

## 28. Risk register

| Risk ID | Description | Mitigation |
|---------|-------------|------------|
| ENF-R01 | Breaking public API on `DesignEvidence` | Minor evidence version bump; additive contract block |
| ENF-R02 | Overfitting contract to current tier-1 only | Conditional rules per design family in schema |
| ENF-R03 | Treating metadata emission as statistical validation | Separate `artifact_status` from D5-DES-STAT outcomes |
| ENF-R04 | Adapter drift from native design outputs | Adapter tests + D5-DES-STAT harnesses |
| ENF-R05 | Geometry bridge misuse | `bridge_status` + forbidden claims |
| ENF-R06 | Power/MDE overclaim | `planning_only` suitability cap |
| ENF-R07 | LLM infers contract-complete from assignment | Require `artifact_status` field |
| ENF-R08 | Historical artifacts mistaken as current | `contract_unknown` default for legacy JSON |

---

## 29. Current status assessment

| Item | Status |
|------|--------|
| Enforcement plan | ✅ Defined (this artifact) |
| Contract schema | ❌ Not implemented |
| Field emission | ❌ Not implemented |
| Contract validation tests | ❌ Not implemented |
| Adapters | ❌ Not implemented |
| Bridge metadata emission | ❌ Not implemented |
| Runtime guardrail enforcement | ❌ Not implemented |
| Downstream governed use | ❌ **Blocked** |
| Downstream suitable designs | **0** |

---

## 30. Relationship to future enforcement artifacts

**Next artifact:** **`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001`** — Phase 2 tier-1 emission.

Schema ✅ [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) — must precede runtime enforcement.

**Follow-on:** **`DESIGN_GUARDRAIL_ENFORCEMENT_001`** — runtime PASS/WARN/BLOCK wiring in `geo_runner`, validators, planning orchestrator (per [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) §27).

Schema first because runtime enforcement requires validated field definitions.

---

## 31. Governance gates

| Gate | Status |
|------|--------|
| Plan defined | ✅ This artifact |
| Enforcement implemented | ❌ |
| Designs promoted | ❌ |
| TrustReport / CalibrationSignal / MMM / LLM | ❌ **BLOCKED** |

This artifact does **not** implement enforcement, validate designs, authorize causal claims, or authorize product layers.

---

## 32. Current status and verdict

| Field | Value |
|-------|-------|
| Verdict | `design_contract_enforcement_plan_defined_not_implemented` |
| Phase | **0** (planning only) |
| Contract-complete designs | **0 / 31** |
| Next implementation artifact | `DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001` |

### Search methodology (2026-06-10)

```bash
grep -R "DESIGN_SUITABILITY_FRAMEWORK_001\|DESIGN_GUARDRAILS_001\|DESIGN_OUTPUT_CONTRACT_001" -n docs
grep -R "DesignEvidence\|ExperimentEvidence\|DesignSpec\|DesignMethod\|PowerContract\|PowerAnalysis" -n panel_exp tests docs
grep -R "geometry_id\|forbidden_downstream_claims\|concurrent_multi_experiment_compatibility\|shared_control_policy" -n panel_exp tests docs
grep -R "assignment\|treatment\|control\|cell_id\|block_id\|stratum\|pair_id\|supergeo\|trim\|thin\|eligible\|excluded\|donor" -n panel_exp/design panel_exp/evidence.py panel_exp/spec.py tests docs
grep -R "PASS\|WARN\|BLOCK\|guardrail\|suitability\|contract_blocked\|stat_validation_required" -n docs tests panel_exp
find panel_exp/design -type f
find tests -iname "*design*" -o -iname "*evidence*" -o -iname "*contract*" -o -iname "*validation*"
```

**Code inspected (read-only):** `evidence.py`, `design/geo_runner.py`, `spec.py`, `design/` (assign, validation, power, constraints, quickblock, matched_pair, trimmed_match, supergeos, geo_experiment_design), registry and Track D tests.

---

## 33. Roadmap

**Next artifact:** **`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001`**

Schema ✅ Phase 1. Then: tier-1 emission (Phase 2) · validation tests (Phase 3) · adapters (Phase 4) · `DESIGN_GUARDRAIL_ENFORCEMENT_001`.

---

## 34. Completion checklist

| Item | Status |
|------|--------|
| Prerequisites inspected | ✅ |
| Code paths inspected | ✅ §4, §9 |
| Required fields inventoried | ✅ §7 |
| Producer/consumer mapping defined | ✅ §9–§10 |
| Enforcement phases defined | ✅ §11 |
| Tests planned | ✅ §14, §26 |
| Roadmap updated | ✅ companion docs |
| No code changed | ✅ |
| Tests run | ✅ (completion report) |

---

## 35. Companion doc updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Enforcement plan Accepted; next = schema |
| [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) | Plan defines implementation phases |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | Blockers routed to enforcement plan |
| [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) | Plan prerequisite for runtime enforcement |
| [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) | Positive suitability requires enforcement |
| [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) | Matrix advisory until fields emitted |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Plan complete |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Implementation bridge after suitability |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Gaps to close |
| [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md) | Planning blocked until enforcement |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Design audit lane |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |

---

*DESIGN-CONTRACT-ENFORCEMENT-PLAN-001 v1.0.1 — Accepted; Phase 1 schema defined by DESIGN_CONTRACT_SCHEMA_001; next = DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.*
