# Design Tier1 Contract Emission Implementation Plan 001

**Document ID:** DESIGN-TIER1-CONTRACT-EMISSION-IMPLEMENTATION-PLAN-001  
**Title:** Design Tier1 Contract Emission Implementation Plan 001  
**Status:** **Accepted**  
**Scope:** Implementation plan for tier-1 runtime `design_contract` emission wiring  
**Artifact type:** Documentation / implementation plan — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) · [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md)

**Inputs:** [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) · [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) · [`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md`](DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md) · [`panel_exp/validation/design_contract_validator_001.py`](../panel_exp/validation/design_contract_validator_001.py) · [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) · [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) · [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md)

**Guardrails:** No runtime emission implementation · no fixture regeneration · no contract-complete status · no TrustReport/CalibrationSignal/MMM/LLM authorization · no guardrail runtime integration · no suitability promotion

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Tier1 Contract Emission Implementation Plan 001 |
| Status | **Accepted** |
| Scope | Implementation plan for tier-1 runtime contract emission |
| Artifact type | Documentation / implementation plan |

Fourteenth design audit / enforcement artifact. Decomposes [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) into **concrete wiring steps** for the next code artifact (`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001`). **Plan only — runtime emission not implemented.**

---

## 2. Purpose

This artifact defines **how** tier-1 geo-run design outputs should begin emitting conservative `design_contract` blocks:

1. **Producer wiring** — where contract construction and validation attach in `geo_runner` / `DesignEvidence`  
2. **Field population** — schema blocks populated from existing `DesignSpec`, assignment, validation, and geo config  
3. **Validator invocation** — candidate contract validated before serialization; status validator-derived  
4. **Test and fixture strategy** — tests required in the implementation artifact  
5. **Rollout sequencing** — phased implementation without breaking legacy evidence  

Emission must start **conservatively**: `contract_incomplete` or validator-derived status; never `contract_complete`.

---

## 3. Why this artifact exists

| Gap | This plan addresses |
|-----|---------------------|
| Validator exists, **runtime emission absent** | Connects `design_contract_validator_001.py` to producers |
| Schema + tier-1 emission plan defined, **no wiring spec** | Concrete module targets, call order, data model |
| `DesignEvidence.to_dict()` has **no `design_contract`** | Placement options and recommended integration |
| Legacy artifacts must stay `contract_unknown` | Backward compatibility and non-inference rules |
| **0/31 contract-complete** | Explicit no-promotion defaults at emission time |

**Observed at authoring:**

- `panel_exp/evidence.py` — `DesignEvidence.to_dict()` emits assignment, validation, diagnostics; **no `design_contract` key**  
- `panel_exp/design/geo_runner.py` — `run_geo_experiment_design` builds `ExperimentEvidence` via `DesignEvidence.from_assignment`  
- `panel_exp/validation/design_contract_validator_001.py` — standalone validator; **not imported by producers**  
- `tests/fixtures/artifact_schemas/design_evidence_v1.json` — legacy fixture; **no `design_contract`**  

---

## 4. Scope

Includes planning for:

- **Producer paths:** `GeoExperimentDesign.run_design()` → `run_geo_experiment_design` → `ExperimentEvidence.build` → `DesignEvidence`  
- **Tier-1 design families:** DES-001–004, DES-006 (wrapper), constrained DES-011 (`n_test_grps > 1`)  
- **Schema field population** per [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md)  
- **Validator invocation** via `validate_design_contract` / `validate_design_evidence_contract`  
- **Tests to add** in implementation artifact (inline first; optional v2 fixture lane)  
- **Backward compatibility** for evidence without `design_contract`  
- **No-overclaim defaults** at emission  
- **Rollout sequencing** (builder → field → emission → validator → tests)  

**Out of scope:** thinning/trim, supergeo, adapter designs, pooled multi-cell causal claims, estimator/inference changes, D5 archive regeneration, guardrail runtime module, suitability promotion.

---

## 5. Non-goals

- No Python emission implementation in **this** artifact  
- No modification of `panel_exp/evidence.py`, `geo_runner.py`, or fixtures  
- No `design_evidence_v1.json` overwrite  
- No D5 archive regeneration  
- No estimator/inference code changes  
- No TrustReport / CalibrationSignal / MMM / LLM authorization  
- No `contract_complete` or production-ready claims  
- No guardrail runtime integration yet  
- No suitability status promotion  

---

## 6. Producer path map

```text
GeoExperimentDesign.run_design()                    # geo_experiment_design.py
  → DesignRunContext
  → run_geo_experiment_design(ctx)                  # geo_runner.py
      1. design_method = design_class_name(geo.base_randomizer_cls)  # base only today
      2. design = geo.create_design()               # always Rerandomization(base)
      3. rs_dp_grps = design.assign(...)            # assign.py / modes
      4. spec = spec_from_geo_design(...)           # spec.py via _build_geo_spec
      5. validate_design(...) → validation_summary  # design/validation.py (optional gate)
      6. ExperimentEvidence.build(spec, assignment, validation_summary, ...)
           → DesignEvidence.from_assignment(...)    # evidence.py:456
      7. geo.last_evidence = ExperimentEvidence
      8. _calculate_sensitivity_metrics()           # power — out of tier-1 contract block
```

| Stage | Module | Emits today | Future `design_contract` role |
|-------|--------|-------------|------------------------------|
| Assignment | `design.assign` / modes | `rs_dp_grps` dict | Feed `assignment` block; stratified stratum map (DES-004) |
| Spec | `spec_from_geo_design` | `DesignSpec` identity, periods | Feed `design_identity`, `time_windows`, `outcomes` |
| Validation | `validate_design` | `validation_summary` | Feed `diagnostics` partial; **not** contract PASS |
| Evidence build | `DesignEvidence.from_assignment` | Frozen assignment + hashes | Optional `design_contract` field on dataclass |
| Serialization | `DesignEvidence.to_dict` | JSON evidence dict | **Attach nested `design_contract` + compact validation summary** |
| Orchestration | `geo_runner` | Sets `geo.last_evidence` | Pass geo context to builder (wrapper, n_test_grps, whitelists) |

**Observed gap (IV-DES-013):** `design_method` / `design_name` reflects **base** randomizer (`complete_randomization`), not `Rerandomization` wrapper. Implementation must emit `wrapper_identity` separately.

---

## 7. Primary implementation target

**Recommended next-artifact code targets:**

| Priority | Target | Role |
|----------|--------|------|
| 1 | `panel_exp/validation/design_contract_builder_001.py` *(new)* | Pure builder: inputs → candidate `design_contract` dict |
| 2 | `panel_exp/evidence.py` | Optional `design_contract` + `contract_validation` fields; `to_dict()` emission |
| 3 | `panel_exp/design/geo_runner.py` | Invoke builder + validator after assignment/validation; pass context |
| 4 | `tests/validation/test_design_tier1_contract_emission_001.py` *(new)* | Tier-1 emission integration tests |

**Prefer:** dedicated **builder helper** (Option D) called from `geo_runner` or `DesignEvidence.from_assignment`, with **`to_dict()` integration** (Option A partial). Avoid bloating `from_assignment` with geo-specific logic — pass a pre-built contract or builder context.

**Public API:** No new top-level exports unless `tests/test_public_api.py` convention requires it. Validator remains internal.

---

## 8. Tier-1 design scope

| DES ID | Design | Registry key | Callable | Implementation notes |
|--------|--------|--------------|----------|----------------------|
| DES-001 | greedy_match_markets | `greedy_match_markets` | `geo_runner` | `geometry_id=unit_panel_single_cell`; matching covariates if exposed |
| DES-002 | CompleteRandomization | `complete_randomization` | Same | Universal fields; simplest path |
| DES-003 | BalancedRandomization | `balanced_randomization` | Same | + balance diagnostics linkage |
| DES-004 | StratifiedRandomization | `stratified_randomization` | Same | **Requires** `structure.stratum_ids`, `unit_to_stratum_map` |
| DES-006 | Rerandomization | (wrapper) | `create_design()` always wraps | **Requires** `wrapper_identity` + base randomizer class |
| DES-011 | multi_test_groups | `n_test_grps > 1` | geo config | **Requires** `cell_ids`, shared-control policy; `pooled_claims_allowed=false` |

**Out of tier-1 implementation wave:**

- DES-005 ThinningDesign / trim geometry  
- Supergeo / QuickBlock / MatchedPair adapters  
- Pooled multi-cell causal authorization  
- Estimator/inference suitability promotion  
- Power/MDE causal readout authorization  

**0/31 contract-complete — unchanged.**

---

## 9. Schema field population plan

| Block | Population source | Tier-1 default |
|-------|-------------------|----------------|
| Envelope | Constants | `schema_name=DESIGN-CONTRACT-SCHEMA-001`, `schema_version=1.0.0`, `artifact_type=design_output_contract` |
| `design_identity` | Registry lookup + `DesignSpec` + geo | `design_inventory_id` DES-001–004 map; `registry_key`; `design_method_class` = base cls; `wrapper_identity` when wrapped |
| `geometry` | `n_test_grps`, design family | `unit_panel_single_cell` if single cell; `multi_cell_per_cell` if `n_test_grps>1`; `target_population_status=full_panel` |
| `assignment` | `rs_dp_grps` canonical | `assignment_map`, treated/control unions, exclusivity counts |
| `units` | Panel index + geo whitelists | `all_units`, `eligible_units` via constraint context mirror |
| `time_windows` | `DesignSpec` periods | pre/test from `train_length` |
| `outcomes` | `geo.outcome_column` | `primary_outcome`; balance covariates when known |
| `multi_cell` | `n_test_grps`, assignment keys | `is_multi_cell`, `cell_ids`, `shared_control_policy` when multi-cell |
| `concurrency` | Static conservative | `concurrent_multi_experiment_compatibility=not_evaluated` (or `restricted` for multi-cell) |
| `structure` | Stratified only | `stratum_ids`, `unit_to_stratum_map` for DES-004; omitted otherwise |
| `trim_thin` / `supergeo` | — | Omitted (not in tier-1) |
| `power_mde` | — | Omitted or planning-only flags; **no causal authorization** |
| `diagnostics` | `validation_summary` | Partial balance/SRM; `diagnostic_completeness_status=partial` |
| `governance` | Conservative defaults §10 | Non-empty forbidden claims; blocked downstream auth |
| `compatibility` | Matrix hints advisory | `requires_statistical_validation=true`; no eligibility `true` |
| `provenance` | Module paths, hashes | `producer_module`, `spec_hash`, `assignment_hash`, `run_id` |

---

## 10. Conservative governance defaults

**Required at emission (implementation artifact):**

| Field | Value |
|-------|-------|
| `design_contract_status` | `contract_incomplete` **or** validator-derived (`contract_valid`, `contract_valid_with_warnings`, `contract_blocked`, `contract_incomplete`) — **never `contract_complete`** |
| `governance.forbidden_downstream_claims` | Non-empty list including: `trust_report`, `calibration_signal`, `mmm_calibration`, `llm_product_recommendation`, `production_experiment_recommendation` |
| `governance.downstream_authorization_status` | `blocked` or `not_authorized` |
| `governance.statistical_validation_status` | `protocol_defined_not_executed` |
| `governance.guardrail_status` | `BLOCK` or `REQUIRES_STATISTICAL_VALIDATION` |
| `governance.suitability_status` | `contract_blocked` |
| `contract_complete_allowed` | **Not emitted as true**; validator result always `False` in tier-1 wave |
| TrustReport / CalibrationSignal / MMM / LLM flags | **Absent or explicitly false** — never `true` |
| `compatibility` hints | Advisory only; `requires_statistical_validation=true` |

---

## 11. Validator invocation plan

```text
1. build_design_contract(context) → candidate dict
2. result = validate_design_contract(candidate)
3. status = compute_contract_status(result)  # or result.status after finalize
4. candidate["design_contract_status"] = status   # validator-derived, not manual
5. Attach compact contract_validation summary to evidence (optional field)
6. Serialize via DesignEvidence.to_dict() → nested design_contract
```

**Rules:**

- Validator **must run** on every emitted contract in tier-1 implementation  
- Failed validation → `contract_blocked` or `contract_incomplete`; reason codes **must not** be dropped  
- **Never** set `design_contract_status=contract_complete` in emission code  
- `contract_complete_allowed` from validator is always `False` — do not override  
- Embed **compact summary** only: `{status, severity, reason_codes, validator_version}` — full `field_results` optional in diagnostics artifact, not required in top-level evidence  
- Legacy evidence without `design_contract` → `validate_design_evidence_contract` returns `contract_unknown` + `D-CONTRACT-LEGACY-UNKNOWN` (unchanged)  

**Import path:** `from panel_exp.validation.design_contract_validator_001 import validate_design_contract, compute_contract_status` — internal only.

---

## 12. Emission placement options

| Option | Location | Pros | Cons | Verdict |
|--------|----------|------|------|---------|
| **A** | `DesignEvidence.to_dict()` | Single serialization point; tests read evidence JSON | Builder needs contract on instance or lazy build | **Partial — attach pre-built contract** |
| **B** | `DesignEvidence.from_assignment()` | Contract co-created with evidence | Geo context not available; fattens evidence ctor | **Not recommended alone** |
| **C** | `geo_runner` before evidence | Full geo context; clear orchestration | Duplication if other producers emerge | **Good for builder invocation** |
| **D** | Dedicated `design_contract_builder_001.py` | Testable; keeps evidence thin | Extra module | **Recommended primary** |

**Recommendation:** **Option D + C + A**

1. `design_contract_builder_001.build_tier1_design_contract(geo, spec, assignment, validation_summary, ...)`  
2. Called from `geo_runner` after validation, before `ExperimentEvidence.build`  
3. Pass built contract + validation summary into `DesignEvidence.from_assignment(..., design_contract=..., contract_validation=...)`  
4. `to_dict()` includes `design_contract` key when present  

---

## 13. Backward compatibility plan

| Concern | Plan |
|---------|------|
| Existing evidence JSON | All legacy keys unchanged; `design_contract` **additive** optional key |
| `from_dict` / `from_json` | Ignore unknown `design_contract` on read until v2; optional field with default `None` |
| Public API | No breaking constructor changes; new fields keyword-only with defaults |
| Validator export | Remains internal unless public API audit requires re-export |
| Fixtures | `design_evidence_v1.json` **unchanged**; optional `design_evidence_v2.json` only after emission stabilizes |
| Legacy validation | `validate_design_evidence_contract` on v1 → `contract_unknown` — **no silent upgrade** |
| Key ordering | Add `design_contract` to `_EXPERIMENT_EVIDENCE_KEY_ORDER` append-only (minor evidence version bump if needed) |

---

## 14. Test plan for implementation artifact

**New test module:** `tests/validation/test_design_tier1_contract_emission_001.py` (proposed)

| Test ID | Requirement |
|---------|-------------|
| T1-EMIT-001 | Tier-1 `run_geo_experiment_design` output evidence contains `design_contract` |
| T1-EMIT-002 | Emitted contract passes `validate_design_evidence_contract` for DES-002 minimal path |
| T1-EMIT-003 | Legacy `from_dict` without `design_contract` still works |
| T1-EMIT-004 | `forbidden_downstream_claims` non-empty; downstream auth blocked |
| T1-EMIT-005 | No-overclaim flags false/absent (TrustReport, CalibrationSignal, MMM, LLM, production) |
| T1-EMIT-006 | DES-004 stratified run emits stratum metadata or blocks with `D-CONTRACT-MISSING-STRATUM-IDS` |
| T1-EMIT-007 | DES-006 rerandomization emits `wrapper_identity` + base class |
| T1-EMIT-008 | DES-011 multi-cell emits `cell_ids` + shared-control policy |
| T1-EMIT-009 | `design_contract_status` never `contract_complete` |
| T1-EMIT-010 | Validator reason codes present when status is `contract_blocked` |
| T1-EMIT-011 | `tests/test_public_api.py` still passes |
| T1-EMIT-012 | `tests/validation/test_design_contract_validator_001.py` still passes |
| T1-EMIT-013 | Input evidence dict not mutated by emission path |

**Regression suites (CI):** design registry, track_d design inventory, D5 DES trim/supergeo/pow, D5 stat smoke, validation coverage doc.

---

## 15. Fixture strategy

| Phase | Strategy |
|-------|----------|
| Implementation wave 1 | **Inline dict tests** + live `run_geo_experiment_design` on small panel fixtures in tests |
| Optional wave 2 | `tests/fixtures/artifact_schemas/design_evidence_v2.json` with `design_contract` — **new file only** |
| Negative fixtures | Remain validator-owned under `tests/fixtures/artifact_schemas/design_contract_validator_001/` if needed |
| Do not overwrite | `design_evidence_v1.json` |
| D5 archives | No regeneration in tier-1 emission implementation |

---

## 16. Tier-1 expected validator outcomes

| Design | Expected mechanical outcome | Contract-complete? | Downstream eligible? |
|--------|----------------------------|--------------------|----------------------|
| DES-001 / DES-002 / DES-003 | `contract_valid` or `contract_valid_with_warnings` if universal fields populated | **No** | **No** |
| DES-004 | `contract_valid*` only if stratum metadata emitted; else `contract_blocked` | **No** | **No** |
| DES-006 | `contract_valid*` only if wrapper + base identity present; else `contract_blocked` | **No** | **No** |
| DES-011 | `contract_valid*` only if cell IDs + shared-control policy; else `contract_blocked` | **No** | **No** |
| Any missing conditional | `contract_blocked` with `D-CONTRACT-*` reason | **No** | **No** |

**Note:** `contract_valid` ≠ production-ready. `contract_complete_allowed` remains `False`.

---

## 17. Data model changes

**Proposed optional fields on `DesignEvidence` (implementation artifact):**

```python
design_contract: Mapping[str, Any] | None = None
contract_validation: Mapping[str, Any] | None = None  # compact validator summary
```

| Change | Breaking? |
|--------|-------------|
| Optional dataclass fields with defaults | **No** |
| `to_dict()` adds `design_contract` when non-None | **No** (additive) |
| `from_assignment(..., design_contract=None)` | **No** (keyword-only optional) |
| Evidence version bump `1.0` → `1.1` | **Minor** if only additive fields |

**No breaking constructor changes.** Builder function stays separate module.

---

## 18. No-overclaim enforcement

Implementation **must block or omit** at emission:

- `trust_report_eligible` / `trustreport_eligible`  
- `calibration_signal_eligible`  
- `mmm_ready` / `mmm_eligible`  
- `llm_authorized` / `llm_eligible`  
- `production_ready` / `production_ready_status`  
- `causal_readout_authorized` (including under `power_mde`)  
- `multi_cell.pooled_claims_allowed=true` without geometry bridge  
- `governance.downstream_authorization_status=authorized`  
- `design_contract_status=contract_complete`  

Validator re-checks on emission; doubly conservative.

---

## 19. Reason-code propagation

**Recommendation:** Emit **compact validation summary** on evidence:

```json
"contract_validation": {
  "status": "contract_valid_with_warnings",
  "severity": "WARN",
  "reason_codes": [],
  "validator_version": "1.0.0",
  "contract_complete_allowed": false
}
```

When `contract_blocked` or `contract_incomplete`, include **non-empty `reason_codes`**. Full `field_results` optional under `design_contract.diagnostics.contract_validation_detail` — not required in tier-1 wave.

---

## 20. Failure mode register

| ID | Failure | Mitigation |
|----|---------|------------|
| FM-EMIT-001 | Emitted contract missing required universal field | Builder checklist + validator BLOCK before serialize |
| FM-EMIT-002 | Manual `contract_complete` assertion in emission code | Code review gate; validator `RC_FALSE_COMPLETE_CLAIM` |
| FM-EMIT-003 | Validator result ignored or stripped | Require `contract_validation` summary; test T1-EMIT-010 |
| FM-EMIT-004 | Compatibility hints treated as approval | Hints labeled advisory; no `*_eligible=true` |
| FM-EMIT-005 | Stratified metadata dropped (DES-004) | Builder extracts stratum from assign path; conditional test |
| FM-EMIT-006 | Rerandomization wrapper identity lost | Pass `create_design()` type + base cls to builder |
| FM-EMIT-007 | Multi-cell pooled overclaim | Force `pooled_claims_allowed=false`; validator check |
| FM-EMIT-008 | Public API break | Run `test_public_api.py`; no `__all__` changes without audit |
| FM-EMIT-009 | Fixture drift | Do not rewrite v1; v2 optional separate file |
| FM-EMIT-010 | Legacy artifact silently upgraded | No inference from `design_method` alone; missing block → `contract_unknown` |

---

## 21. Implementation sequencing

| Phase | Deliverable | Artifact |
|-------|-------------|----------|
| **0** | This implementation plan | **DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001** ✅ |
| **1** | Contract builder helper module | `design_contract_builder_001.py` |
| **2** | Optional `DesignEvidence` fields | `evidence.py` |
| **3** | `to_dict()` emission of `design_contract` | `evidence.py` |
| **4** | Validator call in geo pipeline | `geo_runner.py` |
| **5** | Tier-1 emission tests | `test_design_tier1_contract_emission_001.py` |
| **6** | Docs / roadmap / MIP registry update | Companion docs |
| **7** | Optional `design_evidence_v2.json` | Separate fixture lane |

Phases 1–5 = **`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001`**.

---

## 22. CI gating plan

| Suite | Required |
|-------|----------|
| `tests/validation/test_design_contract_validator_001.py` | ✅ Must pass |
| `tests/validation/test_design_tier1_contract_emission_001.py` | ✅ New — must pass after implementation |
| `tests/test_public_api.py` | ✅ Must pass |
| `tests/test_design_registry.py` | ✅ Must pass |
| Track D design tests (inventory, trim, supergeo, pow geometry) | ✅ Must pass |
| D5 stat smoke tests | ✅ Must pass |
| `tests/test_validation_coverage_doc.py` | ✅ Must pass |
| D5 archive regeneration | ❌ **Not required** |

---

## 23. Current status assessment

| Item | Status |
|------|--------|
| Validator module | ✅ Implemented — `design_contract_validator_001.py` |
| Validator tests | ✅ 26 tests passing |
| Runtime emission | ❌ Not wired |
| `design_contract` in `DesignEvidence.to_dict()` | ❌ Absent |
| Implementation plan (this artifact) | ✅ Defined |
| Contract-complete designs | **0 / 31** |
| Downstream (TrustReport, CalibrationSignal, MMM, LLM) | **Blocked** |

---

## 24. Governance gates

This artifact:

- **Does not** implement emission  
- **Does not** mark any design contract-complete  
- **Does not** promote designs or suitability  
- **Does not** authorize TrustReport, CalibrationSignal, MMM, or LLM use  
- **Does not** wire guardrails at runtime  

Next artifact (`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001`) may emit `design_contract` but must preserve all conservative defaults above.

---

## 25. Current status and verdict

**Verdict:** `design_tier1_contract_emission_implementation_plan_defined_not_implemented`

| Field | Value |
|-------|-------|
| Plan status | **Accepted** |
| Code emission | **Not implemented** |
| Contract-complete designs | **0 / 31** |
| Downstream authorization | **Blocked** |

---

## 26. Roadmap

**Next artifact:** **`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001`** — tier-1 runtime `design_contract` emission code + tests per §14.

**Follow-on (deferred):** guardrail runtime enforcement, suitability integration, D5-DES-STAT execution, adapter/trim/supergeo emission waves.

---

## 27. Completion checklist

| Item | Status |
|------|--------|
| Prerequisites inspected (schema, tier-1 plan, validator, test plan) | ✅ |
| Producer paths inspected (`geo_runner`, `evidence.py`, `geo_experiment_design`) | ✅ |
| Tier-1 scope defined (DES-001–004, DES-006, DES-011 partial) | ✅ |
| Implementation targets defined (builder + evidence + geo_runner) | ✅ |
| Validator invocation plan defined | ✅ |
| Test plan defined | ✅ |
| Fixture strategy defined | ✅ |
| No code changed | ✅ |
| No fixtures changed | ✅ |
| Roadmap / audit docs updated | ✅ |
| Validation tests run | ✅ |

**Searches recorded:**

```bash
grep -R "DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001|..." -n docs
grep -R "design_contract|validate_design_contract|..." -n panel_exp tests docs
grep -R "DesignEvidence|geo_runner|..." -n panel_exp tests docs
grep -R "greedy_match_markets|CompleteRandomization|..." -n panel_exp tests docs
grep -R "contract_complete|forbidden_downstream_claims|..." -n panel_exp tests docs
find panel_exp/design -maxdepth 2 -type f
find tests -iname "*design*" -o -iname "*contract*" ...
```

---

## Companion references

| Document | Relationship |
|----------|--------------|
| [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) | Parent Phase 2 plan — field maps decomposed here into wiring steps |
| [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) | Schema fields emission must populate |
| [`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001`](../panel_exp/validation/design_contract_validator_001.py) | Validator to invoke at emission |
| [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) | Tier-1 emission tests planned until implementation |
| [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) | Phase 2 implementation sequencing |

---

*DESIGN-TIER1-CONTRACT-EMISSION-IMPLEMENTATION-PLAN-001 v1.0.0 — Accepted; decomposes tier-1 emission into concrete wiring; runtime not implemented; 0 contract-complete; next = DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001.*
