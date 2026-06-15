# Design Contract Golden Fixtures 001

**Document ID:** DESIGN-CONTRACT-GOLDEN-FIXTURES-001  
**Title:** Design Contract Golden Fixtures 001  
**Status:** **Accepted**  
**Scope:** Golden fixture stabilization for tier-1 `design_contract` emitted shape  
**Artifact type:** Documentation + test fixtures — **no production promotion**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) · [`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md)

**Inputs:** [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) · [`panel_exp/validation/design_contract_builder_001.py`](../panel_exp/validation/design_contract_builder_001.py) · [`panel_exp/validation/design_contract_validator_001.py`](../panel_exp/validation/design_contract_validator_001.py) · [`tests/validation/test_design_tier1_contract_emission_001.py`](../tests/validation/test_design_tier1_contract_emission_001.py)

**Guardrails:** No estimator/inference changes · no D5 archive regeneration · no `design_evidence_v1.json` overwrite · no contract-complete claims · no downstream authorization

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Contract Golden Fixtures 001 |
| Status | **Accepted** |
| Scope | Golden fixtures for emitted `design_contract` shape |
| Artifact type | Documentation + test fixtures |

Fifteenth design audit / enforcement artifact. Freezes representative tier-1 contract payloads for regression testing before guardrail runtime integration.

---

## 2. Purpose

This artifact:

1. **Stabilizes** emitted `design_contract` shape via golden JSON fixtures  
2. **Protects** against silent drift in builder/validator/emission paths  
3. **Documents** positive, negative, and legacy fixture expectations  
4. **Gates CI** with fixture-based regression tests  

Fixtures are **contract-shape references**, not production evidence archives.

---

## 3. Why golden fixtures are needed

| Gap | Golden fixtures address |
|-----|-------------------------|
| Tier-1 emission wired but shape unprotected | Regression tests on frozen payloads |
| Validator tests use inline dicts only | File-backed representative contracts |
| Guardrail runtime integration pending | Stable target shape for future consumers |
| `design_evidence_v1.json` must not change | Separate v2/golden lane |

---

## 4. Scope

Includes:

- Fixture directory: `tests/fixtures/artifact_schemas/design_contract_golden_001/`  
- Test module: `tests/validation/test_design_contract_golden_fixtures_001.py` (39 tests)  
- Positive tier-1 contracts (DES-002, DES-003, DES-004, DES-006)  
- Negative contract-shape fixtures  
- Legacy evidence without `design_contract`  
- Multi-cell blocked conservative fixture  

**Out of scope:** full D5 archives, `design_evidence_v1.json` overwrite, guardrail runtime, suitability promotion.

---

## 5. Non-goals

- No estimator/inference code changes  
- No D5 archive regeneration  
- No TrustReport/CalibrationSignal/MMM/LLM authorization  
- No contract-complete or production-ready claims  
- No full production evidence golden files (contract blocks only)  

---

## 6. Fixture inventory

| File | Type | Purpose |
|------|------|---------|
| `tier1_complete_randomization_contract.json` | Positive | DES-002 single-cell |
| `tier1_balanced_randomization_contract.json` | Positive | DES-003 single-cell |
| `tier1_stratified_contract.json` | Positive | DES-004 with stratum metadata |
| `tier1_rerandomization_contract.json` | Positive | DES-006 wrapper + base identity |
| `tier1_multicell_contract_blocked.json` | Conservative blocked | Multi-cell missing shared-control policy |
| `legacy_design_evidence_without_contract.json` | Legacy | No `design_contract` key |
| `negative_downstream_authorized_contract.json` | Negative | `downstream_authorization_status=authorized` |
| `negative_missing_geometry_contract.json` | Negative | Missing `geometry_id` |
| `negative_empty_forbidden_claims_contract.json` | Negative | Empty forbidden claims |

---

## 7. Positive fixture expectations

- `validate_design_contract` → `contract_valid` or `contract_valid_with_warnings`  
- `contract_complete_allowed` → `false` in bundled `contract_validation`  
- `downstream_authorization_status` → `blocked`  
- Non-empty `forbidden_downstream_claims`  
- Required top-level blocks present (schema, identity, geometry, assignment, units, time_windows, multi_cell, concurrency, governance, compatibility, provenance)  
- No TrustReport/CalibrationSignal/MMM/LLM/production eligibility `true`  

---

## 8. Negative fixture expectations

| Fixture | Expected validator outcome |
|---------|-------------------------|
| `negative_downstream_authorized_contract.json` | `contract_blocked` + `D-CONTRACT-DOWNSTREAM-AUTH-VIOLATION` |
| `negative_missing_geometry_contract.json` | `contract_blocked` + `D-CONTRACT-MISSING-GEOMETRY-ID` |
| `negative_empty_forbidden_claims_contract.json` | `contract_blocked` + `D-CONTRACT-EMPTY-FORBIDDEN-CLAIMS` |

---

## 9. Legacy fixture expectations

`legacy_design_evidence_without_contract.json`:

- No `design_contract` key  
- `validate_design_evidence_contract` → `contract_unknown` + `D-CONTRACT-LEGACY-UNKNOWN`  
- Does not modify `design_evidence_v1.json`  

---

## 10. Validator relationship

All contract fixtures are validated through `validate_design_contract`. Positive fixtures must pass mechanically; negative fixtures must block with documented reason codes. Fixture `contract_validation` summaries match validator output at fixture creation time.

---

## 11. Runtime builder relationship

Positive fixtures generated from `build_and_validate_tier1_contract` with fixed `created_at`, spec/assignment hashes, and deterministic panel seed (42). Tests compare runtime builder output **structurally** against golden class (required keys, governance defaults) — not byte-for-byte equality on provenance/timestamps.

---

## 12. Backward compatibility

- `design_evidence_v1.json` **unchanged**  
- Legacy fixture is a **new file**  
- Golden fixtures wrap `design_contract` (+ optional `contract_validation`) only  

---

## 13. No-overclaim guarantees

Fixtures explicitly encode:

- `contract_complete_allowed: false`  
- `downstream_authorization_status: blocked`  
- Forbidden downstream claims non-empty  
- No production-ready / TrustReport / CalibrationSignal / MMM / LLM authorization  

---

## 14. CI gating

Required passing suites:

- `tests/validation/test_design_contract_golden_fixtures_001.py`  
- `tests/validation/test_design_contract_validator_001.py`  
- `tests/validation/test_design_tier1_contract_emission_001.py`  
- Design registry + public API + track_d regression  

---

## 15. Current governance status

| Item | Status |
|------|--------|
| Golden fixtures | ✅ Defined and tested |
| Tier-1 runtime emission | ✅ Wired |
| Contract-complete designs | **0 / 31** |
| Downstream authorization | **Blocked** |
| Guardrail runtime | **Not wired** |

---

## 16. Failure modes prevented

| ID | Failure | Mitigation |
|----|---------|------------|
| FM-GF-001 | Silent removal of required contract block | Top-level key tests |
| FM-GF-002 | Governance defaults drift to authorized | Forbidden-claims + downstream-auth tests |
| FM-GF-003 | Stratified metadata dropped | Stratified fixture + reason-code tests |
| FM-GF-004 | Rerandomization identity lost | Wrapper/base identity fixture |
| FM-GF-005 | Legacy evidence silently upgraded | Legacy unknown fixture |
| FM-GF-006 | Negative cases stop blocking | Negative fixture regression |

---

## 17. Roadmap

**Next artifact:** **`D5-DES-STAT-TIER1-001`** — executed tier-1 design statistical validation.

---

## 18. Completion checklist

| Item | Status |
|------|--------|
| Fixture directory created | ✅ |
| 9 fixture files | ✅ |
| Golden fixture tests (39) | ✅ |
| `design_evidence_v1.json` unchanged | ✅ |
| Validator + emission tests pass | ✅ |
| Companion docs updated | ✅ |
| No estimator/inference changes | ✅ |

| Golden fixtures feed guardrail runtime tests | ✅ |

---

## 19. Current status and verdict

**Verdict:** `design_contract_golden_fixtures_defined_and_tested_no_promotion`

| Field | Value |
|-------|-------|
| Fixture status | **Accepted and tested** |
| Contract-complete designs | **0 / 31** |
| Downstream authorization | **Blocked** |

---

*DESIGN-CONTRACT-GOLDEN-FIXTURES-001 v1.0.2 — Accepted; feed guardrail + reassessment; 0 contract-complete; next = D5-DES-STAT-TIER1-001.*
