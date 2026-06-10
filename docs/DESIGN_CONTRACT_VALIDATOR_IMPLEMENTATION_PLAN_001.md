# Design Contract Validator Implementation Plan 001

**Document ID:** DESIGN-CONTRACT-VALIDATOR-IMPLEMENTATION-PLAN-001  
**Title:** Design Contract Validator Implementation Plan 001  
**Status:** **Accepted**  
**Scope:** Validator architecture and implementation sequencing for `design_contract` blocks  
**Artifact type:** Documentation / implementation plan — **no code changes**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) · [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md)

**Inputs:** [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) · [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) · [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) · [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) · [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md)

**Guardrails:** No validator implementation · no test implementation · no fixture regeneration · no field emission · no contract-complete status · no TrustReport/CalibrationSignal/MMM/LLM authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Contract Validator Implementation Plan 001 |
| Status | **Accepted** |
| Scope | Validator architecture and implementation sequencing |
| Artifact type | Documentation / implementation plan |

Twelfth design audit / enforcement artifact. Defined validator architecture; **implementation complete** as DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001 (`panel_exp/validation/design_contract_validator_001.py`). **Not wired to tier-1 emission.**

---

## 2. Purpose

This artifact defines:

1. **Module target** — where the validator lives in `panel_exp`  
2. **Input/output shapes** — contract dict in, structured validation result out  
3. **Status and severity taxonomy** — how field outcomes aggregate to contract status  
4. **Reason-code registry** — `D-CONTRACT-*` codes for machine-readable failures  
5. **Universal and conditional rules** — tier-1 first; adapters/bridges deferred  
6. **Integration** — guardrails, suitability, combination matrix, tests, CI  
7. **Implementation phases** — constants → validator → fixtures → tests → emission wiring  

The validator **computes** contract status; it does **not** promote designs or authorize downstream use.

---

## 3. Why this artifact exists

| Gap | Validator plan addresses |
|-----|--------------------------|
| Schema + emission + test plans without executable validator | Architecture for PASS/WARN/BLOCK computation |
| Contract completeness must not be asserted by emission code | `compute_contract_status()` separate from emitter |
| Guardrails need machine-readable field outcomes | `guardrail_inputs` on result object |
| Suitability needs validator PASS + separate stat validation | `suitability_inputs`; `contract_valid` ≠ production-ready |
| **0/31 contract-complete** today | Validator defaults conservative |

**Observed:** No `design_contract` in `panel_exp/evidence.py` `DesignEvidence.to_dict()`. **0 matches** in `panel_exp/` for `geometry_id`, `forbidden_downstream_claims`, `design_contract`. No validator module under `panel_exp/validation/` at authoring.

---

## 4. Scope

Includes planning for:

- Validator module at `panel_exp/validation/design_contract_validator_001.py` (proposed)  
- `validate_design_contract()` / `validate_design_evidence_contract()` / `compute_contract_status()`  
- `DesignContractValidationResult` typed structure  
- Universal field validation (geometry, forbidden claims, concurrency, governance)  
- Conditional validation (stratified, multi-cell, rerandomization, trim/supergeo triggers)  
- No-overclaim validation (TrustReport, CalibrationSignal, MMM, LLM, production-ready)  
- Reason codes `D-CONTRACT-*`  
- Mapping to [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) test IDs  
- Tier-1 scope: DES-001–004, DES-006, constrained DES-011  

**Out of scope:** adapter validators (Phase 4), statistical validation (`D5-DES-STAT-*`), runtime guardrail enforcement module.

---

## 5. Non-goals

- No Python validator implementation in this artifact  
- No pytest test files  
- No `design_evidence_v2` fixture regeneration  
- No `design_contract` field emission  
- No statistical validation execution  
- No design promotion or downstream authorization  

---

## 6. Proposed module target

**Path (proposed):** `panel_exp/validation/design_contract_validator_001.py`

Follows repo convention: `panel_exp/validation/*_001.py` paired with `tests/validation/test_*_001.py` and governance doc `DESIGN-*-001.md`.

**Likely public functions:**

```python
def validate_design_contract(
    contract: Mapping[str, Any],
    *,
    context: DesignContractValidationContext | None = None,
) -> DesignContractValidationResult:
    """Validate a standalone design_contract block."""

def validate_design_evidence_contract(
    evidence: Mapping[str, Any],
) -> DesignContractValidationResult:
    """Validate design_contract nested in DesignEvidence / ExperimentEvidence dict."""

def compute_contract_status(
    result: DesignContractValidationResult,
) -> str:
    """Aggregate field_results → design_contract_status enum."""
```

**Optional context fields:** `design_inventory_id`, `n_test_grps`, `is_stratified`, `is_rerandomization_wrapped`, `emitter_claimed_status` (to detect false-complete).

**Consumers (future):** tier-1 emission builder (post-emit check), pytest suite, guardrail runtime (`DESIGN_GUARDRAIL_ENFORCEMENT_001`), planning orchestrator (blocked until PASS).

---

## 7. Proposed result object

**Type:** `@dataclass` `DesignContractValidationResult` (or `TypedDict` if repo prefers JSON-first).

| Field | Type | Description |
|-------|------|-------------|
| `status` | enum | §8 validator status taxonomy |
| `severity` | enum | `pass` · `warn` · `block` |
| `reason_codes` | `list[str]` | Aggregated `D-CONTRACT-*` + cross-refs to DGR/D-SUIT |
| `field_results` | `dict[str, FieldValidationResult]` | Per-field outcome |
| `missing_required_fields` | `list[str]` | Dot-paths, universal |
| `missing_conditional_fields` | `list[str]` | Dot-paths, trigger-active |
| `invalid_fields` | `list[str]` | Dot-paths with invalid type/enum |
| `warnings` | `list[str]` | Human-readable warn messages |
| `blocked_downstream_roles` | `list[str]` | trust_report, calibration_signal, mmm, llm, production |
| `contract_complete_allowed` | `bool` | **False** unless full PASS and no BLOCK |
| `guardrail_inputs` | `dict` | `guardrail_status`, `guardrail_reason_codes` for runtime |
| `suitability_inputs` | `dict` | `suitability_status`, `suitability_reason_codes` |
| `schema_name` | `str \| None` | Echo from contract |
| `schema_version` | `str \| None` | Echo from contract |
| `validator_version` | `str` | e.g. `"1.0.0"` |

**Serializable:** `to_dict()` for archives and test assertions.

---

## 8. Validator status taxonomy

| Status | Meaning | Production-ready? |
|--------|---------|-----------------|
| `contract_valid` | Universal + active conditionals PASS; no BLOCK fields | **No** — stat validation still required |
| `contract_valid_with_warnings` | Required present; recommended missing only | **No** |
| `contract_incomplete` | Partial block; emission started but not full PASS | **No** |
| `contract_blocked` | Universal or conditional BLOCK | **No** |
| `contract_unknown` | No `design_contract` block (legacy) | **No** |
| `contract_not_applicable` | Helper/planning artifact types only | **No** |

**Critical:** `contract_valid` means **metadata schema validation passed** — not statistically validated, not suitability-approved, not TrustReport-eligible.

Maps to schema `design_contract_status` with rule: emitter may not set `contract_complete` unless validator returns `contract_valid` or `contract_valid_with_warnings` **and** `contract_complete_allowed=True` (future gate: also requires D5-DES-STAT).

---

## 9. Field result taxonomy

| Outcome | Maps from schema §9 | Aggregates to |
|---------|---------------------|---------------|
| `field_valid` | `field_valid` | Continue |
| `field_missing_block` | `field_missing_block` | `contract_blocked` |
| `field_missing_warn` | `field_missing_warn` | `contract_valid_with_warnings` |
| `field_invalid_block` | `field_invalid_block` | `contract_blocked` |
| `field_invalid_warn` | (validator extension) | WARN |
| `field_not_applicable` | `field_not_applicable` | Pass |
| `field_future_reserved` | `field_future_reserved` | Pass |

Each `FieldValidationResult`: `{ outcome, reason_code, severity, message }`.

---

## 10. Severity aggregation rules

| Rule | Outcome |
|------|---------|
| Any `required_universal` missing | → `contract_blocked`, severity `block` |
| Any invalid enum in required field | → `contract_blocked` |
| Conditional required missing when trigger true | → `contract_blocked` |
| Recommended missing only | → `contract_valid_with_warnings`, severity `warn` |
| Unknown top-level key (not in schema) | → WARN unless reserved namespace violation → BLOCK |
| `downstream_authorization_status` ≠ `blocked` (tier-1) | → `contract_blocked` |
| Emitter claims `contract_complete` without validator PASS | → `contract_blocked`, `D-CONTRACT-CONTRACT-COMPLETE-FALSE-CLAIM` |
| `forbidden_downstream_claims` empty | → `contract_blocked` |
| TrustReport/CalibrationSignal/MMM/LLM not in forbidden list | → `contract_blocked` |
| `statistical_validation_status` implies complete without D5 | → WARN minimum; BLOCK if implies production |

**`contract_complete_allowed`:** `True` only when status ∈ {`contract_valid`, `contract_valid_with_warnings`} AND zero `field_missing_block` / `field_invalid_block` AND tier-1 negative test matrix would PASS. **At first implementation: default `False` for all tier-1 rows until full test suite green.**

---

## 11. Universal validation rules

| Field / rule | Validator check | Reason code if fail |
|--------------|-----------------|---------------------|
| `design_contract` key exists | Presence on evidence | `D-CONTRACT-MISSING-DESIGN-CONTRACT` |
| `schema_name` | = `DESIGN-CONTRACT-SCHEMA-001` | `D-CONTRACT-INVALID-ENUM` |
| `schema_version` | Semver parseable | `D-CONTRACT-INVALID-ENUM` |
| `artifact_type` | `design_output_contract` for tier-1 | `D-CONTRACT-INVALID-ENUM` |
| `geometry.geometry_id` | Canonical enum §13 | `D-CONTRACT-MISSING-GEOMETRY-ID` / `D-CONTRACT-INVALID-ENUM` |
| `governance.forbidden_downstream_claims` | Non-empty list | `D-CONTRACT-MISSING-FORBIDDEN-CLAIMS` / `D-CONTRACT-EMPTY-FORBIDDEN-CLAIMS` |
| `concurrency.concurrent_multi_experiment_compatibility` | Valid enum | `D-CONTRACT-MISSING-CONCURRENCY` |
| `governance.downstream_authorization_status` | `blocked` (tier-1) | `D-CONTRACT-DOWNSTREAM-AUTH-VIOLATION` |
| `governance.guardrail_status` | Not `PASS` for tier-1 wave | WARN if ambiguous |
| `governance.suitability_status` | Includes blocked/required validation | WARN if production-suitable |
| `governance.statistical_validation_status` | Not falsely `validated` | WARN/BLOCK |
| Forbidden list includes product roles | trust_report, calibration_signal, mmm, llm | `D-CONTRACT-DOWNSTREAM-AUTH-VIOLATION` |

---

## 12. Conditional validation rules

| Trigger | Required fields | Reason code |
|---------|-----------------|-------------|
| `design_family=stratified_assignment` or DES-004 | `structure.stratum_ids`, `structure.unit_to_stratum_map` | `D-CONTRACT-MISSING-STRATUM-IDS` |
| `multi_cell.is_multi_cell=true` or `n_test_grps>1` | `multi_cell.cell_ids`, `multi_cell.shared_control_policy` | `D-CONTRACT-MISSING-CELL-IDS`, `D-CONTRACT-MISSING-SHARED-CONTROL-POLICY` |
| Rerandomization wrapper (DES-006) | `design_identity.wrapper_identity`, base class | `D-CONTRACT-MISSING-RERANDOMIZATION-IDENTITY` |
| `geometry_id=trimmed_geometry` | `trim_thin.excluded_units`, policy | `D-CONTRACT-MISSING-TRIM-METADATA` (future) |
| `geometry_id=supergeo` | `supergeo.supergeo_source_unit_map` | `D-CONTRACT-MISSING-SUPERGEO-MAP` (future) |
| `power_mde` block present | Must not set causal/MMM/TrustReport authorization | `D-CONTRACT-POWER-MDE-OVERCLAIM` |

Tier-1 wave: trim/supergeo triggers → `field_not_applicable` unless adapter scope.

---

## 13. Enum validation plan

Validator enforces **exact** values from [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) §10:

| Enum | Enforcement |
|------|-------------|
| `geometry_id` | 8 canonical values; tier-1 expects `unit_panel_single_cell` or `multi_cell_per_cell` |
| `design_contract_status` / `contract_status` | 4 values; reject `contract_complete` from emitter without validator |
| `artifact_type` | 3 values |
| `target_population_status` | 7 values |
| `concurrent_multi_experiment_compatibility` | Per schema concurrency enum |
| `guardrail_status` | Per guardrails doc |
| `downstream_authorization_status` | `blocked` · `restricted` · `authorized` — tier-1 only `blocked` |
| `design_family` | Per schema §10 |

Invalid value → `field_invalid_block`, `D-CONTRACT-INVALID-ENUM`.

---

## 14. Reason-code registry

| Code | Description | Default severity |
|------|-------------|----------------|
| `D-CONTRACT-MISSING-DESIGN-CONTRACT` | No nested block | BLOCK |
| `D-CONTRACT-MISSING-GEOMETRY-ID` | Missing `geometry_id` | BLOCK |
| `D-CONTRACT-MISSING-FORBIDDEN-CLAIMS` | Missing forbidden list | BLOCK |
| `D-CONTRACT-MISSING-CONCURRENCY` | Missing concurrency field | BLOCK |
| `D-CONTRACT-INVALID-ENUM` | Enum/type violation | BLOCK |
| `D-CONTRACT-EMPTY-FORBIDDEN-CLAIMS` | Empty forbidden list | BLOCK |
| `D-CONTRACT-DOWNSTREAM-AUTH-VIOLATION` | Unauthorized downstream role | BLOCK |
| `D-CONTRACT-CONTRACT-COMPLETE-FALSE-CLAIM` | Emitter claims complete without validator | BLOCK |
| `D-CONTRACT-MISSING-CELL-IDS` | Multi-cell without cell IDs | BLOCK |
| `D-CONTRACT-MISSING-SHARED-CONTROL-POLICY` | Multi-cell without policy | BLOCK |
| `D-CONTRACT-MISSING-STRATUM-IDS` | Stratified without strata | BLOCK |
| `D-CONTRACT-MISSING-RERANDOMIZATION-IDENTITY` | Wrapper identity missing | BLOCK |
| `D-CONTRACT-MISSING-TRIM-METADATA` | Trim geometry without metadata | BLOCK (future) |
| `D-CONTRACT-MISSING-SUPERGEO-MAP` | Supergeo without source map | BLOCK (future) |
| `D-CONTRACT-POWER-MDE-OVERCLAIM` | Power/MDE implies causal/product auth | BLOCK |
| `D-CONTRACT-LEGACY-UNKNOWN` | Legacy evidence without contract | BLOCK for downstream |

Cross-reference: emit `DGR-*` / `D-SUIT-*` / `D-COMB-*` in `guardrail_inputs` / `suitability_inputs` when mapping known IV-DES blockers.

---

## 15. Field-to-reason-code mapping

| Field path | Severity | Reason code |
|------------|----------|-------------|
| `design_contract` | BLOCK | `D-CONTRACT-MISSING-DESIGN-CONTRACT` |
| `schema_name` | BLOCK | `D-CONTRACT-INVALID-ENUM` |
| `geometry.geometry_id` | BLOCK | `D-CONTRACT-MISSING-GEOMETRY-ID` |
| `governance.forbidden_downstream_claims` | BLOCK | `D-CONTRACT-MISSING-FORBIDDEN-CLAIMS` |
| `governance.forbidden_downstream_claims` (empty) | BLOCK | `D-CONTRACT-EMPTY-FORBIDDEN-CLAIMS` |
| `concurrency.concurrent_multi_experiment_compatibility` | BLOCK | `D-CONTRACT-MISSING-CONCURRENCY` |
| `governance.downstream_authorization_status` | BLOCK | `D-CONTRACT-DOWNSTREAM-AUTH-VIOLATION` |
| `design_contract_status=contract_complete` (emitter) | BLOCK | `D-CONTRACT-CONTRACT-COMPLETE-FALSE-CLAIM` |
| `multi_cell.cell_ids` | BLOCK | `D-CONTRACT-MISSING-CELL-IDS` |
| `multi_cell.shared_control_policy` | BLOCK | `D-CONTRACT-MISSING-SHARED-CONTROL-POLICY` |
| `structure.stratum_ids` | BLOCK | `D-CONTRACT-MISSING-STRATUM-IDS` |
| `design_identity.wrapper_identity` | BLOCK | `D-CONTRACT-MISSING-RERANDOMIZATION-IDENTITY` |
| `trim_thin.*` | BLOCK | `D-CONTRACT-MISSING-TRIM-METADATA` |
| `supergeo.supergeo_source_unit_map` | BLOCK | `D-CONTRACT-MISSING-SUPERGEO-MAP` |
| `power_mde.authorization_*` | BLOCK | `D-CONTRACT-POWER-MDE-OVERCLAIM` |
| (legacy, no block) | BLOCK downstream | `D-CONTRACT-LEGACY-UNKNOWN` |

---

## 16. Tier-1 validation behavior

| DES ID | Expected validator behavior (after emission) | Until tests pass |
|--------|---------------------------------------------|------------------|
| DES-001 greedy_match_markets | Universal rules; geometry `unit_panel_single_cell`; donor semantics in assignment/units | `contract_incomplete` or BLOCK if fields missing |
| DES-002 CompleteRandomization | + `assignment_probability` when available | Not `contract_complete` |
| DES-003 BalancedRandomization | + balance diagnostics recommended | WARN if diagnostics partial |
| DES-004 StratifiedRandomization | **BLOCK** without stratum metadata | Not `contract_complete` |
| DES-006 Rerandomization | **BLOCK** without wrapper identity | Not `contract_complete` |
| DES-011 multi_test_groups | **BLOCK** without cell + shared-control when multi-cell | Not `contract_complete`; pooled forbidden |

**Current expected result (today):** all paths → `contract_unknown` (no emission) or `contract_blocked` (negative fixtures). **0 designs reach `contract_complete`.**

---

## 17. Legacy artifact behavior

| Input | Validator status | Downstream |
|-------|------------------|------------|
| `DesignEvidence.to_dict()` without `design_contract` | `contract_unknown` | BLOCK |
| `design_evidence_v1.json` fixture | `contract_unknown` | BLOCK |
| Partial `design_contract` (future) | `contract_incomplete` | BLOCK |
| Silent upgrade to `contract_complete` | `contract_blocked` + false-claim code | BLOCK |

No silent upgrade. Public API may still load legacy evidence for internal use; governed consumers must check validator result.

---

## 18. No-overclaim behavior

Validator **must BLOCK** when contract or evidence implies:

| Claim | Check |
|-------|-------|
| TrustReport eligibility | Role not in allowed; must be in `forbidden_downstream_claims` |
| CalibrationSignal eligibility | Same |
| MMM readiness / calibration | Same |
| LLM authorization | Same |
| Production-ready / experiment recommendation | `downstream_authorization_status` must be `blocked` |
| Causal readout from power/MDE | `D-CONTRACT-POWER-MDE-OVERCLAIM` |
| Suitability approved | `suitability_status` must not imply production |
| Statistical validation complete | Without D5-DES-STAT archive reference |

Product gates may authorize later — **not** via schema validator alone.

---

## 19. Guardrail integration plan

Per [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md):

| Validator output | Guardrail mapping |
|------------------|-------------------|
| `contract_blocked` | `guardrail_status=BLOCK` |
| `contract_unknown` / `contract_incomplete` | `BLOCK` or `REQUIRES_STATISTICAL_VALIDATION` |
| `contract_valid_with_warnings` | `WARN` — still not downstream PASS |
| `contract_valid` | `REQUIRES_STATISTICAL_VALIDATION` minimum — **not PASS** |
| `reason_codes` | Map to `DGR-*` / `D-COMB-*` in `guardrail_inputs` |
| Compatibility hints | Never downgrade BLOCK |

Runtime `DESIGN_GUARDRAIL_ENFORCEMENT_001` will call validator before PASS/WARN/BLOCK emission.

---

## 20. Suitability integration plan

Per [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md):

| Validator output | Suitability mapping |
|------------------|---------------------|
| `contract_blocked` / `contract_unknown` | `contract_blocked` |
| `contract_incomplete` | `contract_blocked` |
| `contract_valid*` + no D5-DES-STAT | `stat_validation_required` |
| `contract_valid` alone | **Not** production-suitable |
| Positive suitability | Requires validator PASS **and** statistical validation **and** governance gates |

`suitability_inputs` on result object pre-populates `D-SUIT-CONTRACT-BLOCKED`, `D-SUIT-STAT-VALIDATION-REQUIRED` as appropriate.

---

## 21. Combination matrix integration plan

Per [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md):

- Matrix rows may **read** `geometry_id`, `design_inventory_id`, adapter/bridge flags from validated contract  
- Validator BLOCK does **not** auto-upgrade matrix row  
- `restricted_requires_contract_fields` stays restricted until validator PASS  
- Field presence alone does not change BLOCK → PASS  

Future matrix v2 generator may consume `validate_design_evidence_contract()` output as advisory input only.

---

## 22. Test integration plan

Maps to [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md):

| Test plan section | Validator function |
|-------------------|-------------------|
| §9 Universal positive | `validate_design_contract` on golden v2 |
| §10 Universal negative | Same on negative fixtures |
| §11 Conditional | Context triggers in `DesignContractValidationContext` |
| §12 Tier-1 emission | Per DES-ID parametrized tests |
| §14 Contract status | `compute_contract_status` |
| §15–17 Integration | Assert `guardrail_inputs` / `suitability_inputs` |
| §18–20 Family-specific | Conditional branches |
| §21 Backward compat | `validate_design_evidence_contract` on v1 |
| §22 No-overclaim | Forbidden list + auth status |

**Tests not implemented** — this plan defines architecture they will exercise.

---

## 23. Fixture integration plan

| Fixture | Validator expected status |
|---------|---------------------------|
| `design_evidence_v2_tier1_*.json` (golden) | `contract_incomplete` or `contract_valid_with_warnings` — **not** `contract_complete` at first |
| Negative missing geometry | `contract_blocked` |
| Negative invalid enum | `contract_blocked` |
| Negative multi-cell | `contract_blocked` |
| Negative rerandomization | `contract_blocked` |
| Negative stratified | `contract_blocked` |
| Negative downstream auth | `contract_blocked` |
| `design_evidence_v1.json` | `contract_unknown` |

No fixture regeneration in this artifact.

---

## 24. Implementation sequence

| Phase | Work | Status |
|-------|------|--------|
| **0** | Docs/planning (this artifact) | ✅ **Current** |
| **1** | Schema constants / enums module | Planned |
| **2** | `DesignContractValidationResult` dataclass | Planned |
| **3** | Universal field validator | Planned |
| **4** | Conditional validator (tier-1 triggers) | Planned |
| **5** | `compute_contract_status` aggregator | Planned |
| **6** | v2 + negative fixtures | Planned |
| **7** | `test_design_contract_schema_001.py` + emission tests | Planned |
| **8** | Tier-1 emission calls validator post-build | Planned |
| **9** | Guardrail/suitability runtime wiring | Planned |

**Order:** Phases 1–7 **before** Phase 8 emission merge. Phase 8 must not ship without Phase 7 green.

---

## 25. API stability and compatibility

- Validator is **internal** first; not exported in public `panel_exp` API until stable  
- `DesignEvidence.from_assignment` signature additive only — optional `design_contract` param  
- Legacy evidence loads unchanged; validator returns `contract_unknown`  
- Results JSON-serializable for archives and D5 harnesses  
- `validator_version` bumped on rule changes; tied to schema_version  

---

## 26. CI gating plan

| Gate | Policy |
|------|--------|
| `test_design_contract_schema_001.py` | Required before validator PR merges |
| Negative fixture suite | Required before any `contract_complete` claim in docs/code |
| `tests/test_validation_coverage_doc.py` | Register new doc + module |
| D5 + design registry suites | Must remain green |
| Downstream auth violation | CI must fail (assert `contract_complete_allowed is False` for tier-1) |

Docs-only PRs (this artifact) do not waive gates.

---

## 27. Risk register

| ID | Risk | Mitigation |
|----|------|------------|
| V-R01 | Validator treated as causal/statistical validation | Separate `statistical_validation_status`; D5-DES-STAT gate |
| V-R02 | Metadata completeness = production-ready | `contract_valid` ≠ suitable; suitability doc §30 |
| V-R03 | False `contract_complete` | `D-CONTRACT-CONTRACT-COMPLETE-FALSE-CLAIM`; `contract_complete_allowed` |
| V-R04 | Compatibility hints as approval | No-overclaim tests; guardrail integration |
| V-R05 | Legacy silent upgrade | `D-CONTRACT-LEGACY-UNKNOWN`; v1 fixture test |
| V-R06 | Multi-cell silent pooling | Conditional BLOCK on pooled claims |
| V-R07 | Reason-code drift | Central registry §14; test asserts codes |
| V-R08 | Schema-validator mismatch | `schema_version` lock; schema doc as source of truth |

---

## 28. Current status assessment

| Item | Status |
|------|--------|
| Validator implementation plan | ✅ This artifact |
| Validator module | ✅ Implemented — `design_contract_validator_001.py` |
| Validator tests | ✅ `test_design_contract_validator_001.py` (26 tests) |
| Tier-1 emission wiring | ❌ Not implemented |
| Validation tests | ❌ Not implemented |
| Fixtures v2 / negative | ❌ Not regenerated |
| Tier-1 emission | ❌ Not implemented |
| Contract-complete designs | **0 / 31** |
| Downstream governed use | ❌ **Blocked** |

### Search methodology (2026-06-10)

```bash
grep -R "DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001\|DESIGN_CONTRACT_SCHEMA_001\|DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001" -n docs
grep -R "DesignEvidence\|ExperimentEvidence\|DesignSpec\|from_assignment\|to_dict\|geo_runner\|run_geo_experiment_design" -n panel_exp tests docs
grep -R "design_contract\|geometry_id\|forbidden_downstream_claims\|concurrent_multi_experiment_compatibility\|shared_control_policy" -n panel_exp tests docs
grep -R "contract_complete\|contract_incomplete\|contract_blocked\|contract_unknown\|validator\|reason_code" -n panel_exp tests docs
grep -R "PASS\|WARN\|BLOCK\|guardrail\|suitability\|CalibrationSignal\|TrustReport\|MMM\|LLM" -n docs tests panel_exp
find tests -iname "*design*" -o -iname "*evidence*" -o -iname "*contract*" -o -iname "*schema*" -o -iname "*validation*"
find panel_exp -iname "*validation*" -o -iname "*contract*" -o -iname "*evidence*"
```

**Code inspected (read-only):** `panel_exp/evidence.py`, `panel_exp/design/geo_runner.py`, `panel_exp/spec.py`, `panel_exp/design/geo_experiment_design.py`, `panel_exp/design/validation.py`, `panel_exp/design/constraints.py`, `panel_exp/design/assign.py`, `panel_exp/design/power.py`, `panel_exp/design/registry.py`, `panel_exp/validation/design_estimator_inference_suitability_framework_001.py`, `tests/fixtures/artifact_schemas/design_evidence_v1.json`, design registry tests, validation doc tests, Track D tests.

---

## 29. Governance gates

| Gate | Status |
|------|--------|
| Validator plan defined | ✅ |
| Validator implemented | ❌ |
| Tests implemented | ❌ |
| Designs promoted | ❌ |
| Contract-complete claims | ❌ **Forbidden** |
| TrustReport / CalibrationSignal / MMM / LLM | ❌ **BLOCKED** |

This artifact does **not** implement the validator, validate contracts, promote designs, or authorize product layers.

---

## 30. Current status and verdict

| Field | Value |
|-------|-------|
| Verdict | `design_contract_validator_implementation_plan_defined_not_implemented` |
| Enforcement phase | **3** (validator planning complete; implementation not started) |
| Contract-complete designs | **0 / 31** |

---

## 31. Roadmap

**Implementation:** ✅ **`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001`** — `panel_exp/validation/design_contract_validator_001.py` + `tests/validation/test_design_contract_validator_001.py`.

**Tier-1 emission implementation plan:** [`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md) ✅ **Accepted** — plans runtime validator invocation at emission; **not wired yet**.

**Next artifact:** **`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001`** — runtime emission code.

---

## 32. Completion checklist

| Item | Status |
|------|--------|
| Prerequisites inspected | ✅ |
| Code paths inspected | ✅ §3, §28 |
| Validator target defined | ✅ §6 |
| Result object defined | ✅ §7 |
| Reason codes defined | ✅ §14–§15 |
| Severity aggregation defined | ✅ §10 |
| Integration plans defined | ✅ §19–§23 |
| Roadmap updated | ✅ companion docs |
| No code changed | ✅ |
| Tests run | ✅ (completion report) |

---

## 33. Companion doc updates checked

| Document | Update |
|----------|--------|
| [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) | Validator plan Accepted; next = implementation |
| [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) | Maps tests to validator architecture |
| [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) | Future validator consumes schema |
| [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) | Emission must pass validator |
| [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) | Validator planning defined |
| [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) | Blockers until validator + tests |
| [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) | Runtime consumes validator |
| [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) | PASS + stat validation required |
| [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) | Validator plan complete |
| [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) | Prerequisite for enforcement |
| [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) | Validator gap |
| [`EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md`](EXPERIMENT_PLANNING_ORCHESTRATION_ROADMAP_001.md) | Planning blocked until validator |
| [`ROADMAP_V4.md`](ROADMAP_V4.md) | Lane status |
| [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Registered |

---

*DESIGN-CONTRACT-VALIDATOR-IMPLEMENTATION-PLAN-001 v1.0.2 — Accepted; validator implemented; tier-1 emission wiring plan defined; runtime not wired; next = DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001.*
