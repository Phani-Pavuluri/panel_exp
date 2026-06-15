# Design Guardrail Runtime Integration 001

**Document ID:** DESIGN-GUARDRAIL-RUNTIME-INTEGRATION-001  
**Title:** Design Guardrail Runtime Integration 001  
**Status:** **Accepted**  
**Scope:** Runtime consumption of emitted `design_contract` and `contract_validation` metadata  
**Artifact type:** Internal validation module + tests — **no production promotion**  
**Date:** 2026-06-10  
**Parent program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md)

**Inputs:** [`DESIGN_CONTRACT_GOLDEN_FIXTURES_001.md`](DESIGN_CONTRACT_GOLDEN_FIXTURES_001.md) · [`panel_exp/validation/design_contract_validator_001.py`](../panel_exp/validation/design_contract_validator_001.py) · [`panel_exp/validation/design_contract_builder_001.py`](../panel_exp/validation/design_contract_builder_001.py) · [`tests/fixtures/artifact_schemas/design_contract_golden_001/`](../tests/fixtures/artifact_schemas/design_contract_golden_001/)

**Guardrails:** No estimator/inference changes · no D5 archive regeneration · no TrustReport/CalibrationSignal/MMM/LLM authorization · no suitability promotion · no production wiring

---

## 1. Title and status

| Field | Value |
|-------|-------|
| Title | Design Guardrail Runtime Integration 001 |
| Status | **Accepted** |
| Scope | Runtime guardrail evaluator for contract metadata |
| Artifact type | Internal module + tests |

Sixteenth design audit / enforcement artifact. Converts emitted `design_contract` and `contract_validation` metadata into inspectable PASS/WARN/BLOCK guardrail decisions.

---

## 2. Purpose

This artifact:

1. **Implements** a pure runtime guardrail evaluator (`design_guardrail_runtime_001.py`)  
2. **Consumes** tier-1 emitted contract metadata without mutating inputs  
3. **Maps** validator severity/status to guardrail PASS/WARN/BLOCK decisions  
4. **Enforces** no-overclaim metadata policy (TrustReport, CalibrationSignal, MMM, LLM, production)  
5. **Gates CI** with golden-fixture-backed integration tests (24 tests)  

The evaluator is **metadata-only** — it does not judge estimator/inference validity or promote any design.

---

## 3. Why runtime guardrails are needed

| Gap | Runtime guardrails address |
|-----|---------------------------|
| Validator emits `contract_validation` summaries | Need machine-consumable PASS/WARN/BLOCK for orchestration |
| Golden fixtures stabilize shape | Need consumer that exercises fixture-backed payloads |
| `DESIGN_GUARDRAILS_001` defines policy only | Need runtime mapping layer before suitability reassessment |
| **0/31 contract-complete designs** | Hard downstream block until reassessment + stat validation |

---

## 4. Scope

Includes:

- Module: [`panel_exp/validation/design_guardrail_runtime_001.py`](../panel_exp/validation/design_guardrail_runtime_001.py)  
- Tests: [`tests/validation/test_design_guardrail_runtime_integration_001.py`](../tests/validation/test_design_guardrail_runtime_integration_001.py)  
- Golden fixture consumption (9 JSON fixtures)  
- Revalidation path when `contract_validation` missing but `design_contract` present  

**Out of scope:** geo_runner wiring, public API export, suitability reassessment, statistical validation execution, D5 archives.

---

## 5. Non-goals

- No estimator/inference code changes  
- No D5 archive regeneration  
- No TrustReport/CalibrationSignal/MMM/LLM product authorization  
- No contract-complete or production-ready claims  
- No suitability role assignment  
- No producer-side blocking (evaluator exists; not wired to execution)  

---

## 6. Inputs consumed

| Input shape | Source key | Handling |
|-------------|------------|----------|
| Full evidence with nested `design.design_contract` | ExperimentEvidence | Extract nested blocks |
| Design evidence with top-level `design_contract` | Golden fixtures / DesignEvidence | Direct extraction |
| Standalone `design_contract` | Validator tests / builder | Revalidate if no summary |
| Standalone `contract_validation` summary | Tier-1 emission | Direct mapping |
| Golden fixture payload | `design_contract_golden_001/` | Both blocks |
| Legacy evidence without contract | `legacy_design_evidence_without_contract.json` | BLOCK/UNKNOWN |

Inputs are **never mutated**.

---

## 7. Guardrail result object

`DesignGuardrailRuntimeResult` fields:

| Field | Type | Default | Meaning |
|-------|------|---------|---------|
| `status` | str | `BLOCK` | `PASS`, `WARN`, `BLOCK`, or `UNKNOWN` |
| `reason_codes` | list[str] | `[]` | `D-GUARDRAIL-*` taxonomy |
| `warnings` | list[str] | `[]` | Human-readable caveats |
| `blocked_roles` | list[str] | all five roles | Downstream roles blocked |
| `contract_status` | str \| None | `None` | Validator contract status |
| `contract_severity` | str \| None | `None` | Validator severity |
| `contract_complete_allowed` | bool | `False` | Always conservative |
| `downstream_authorization_status` | str \| None | `None` | From governance block |
| `guardrail_version` | str | `1.0.0` | Module version |
| `source` | str | — | Input provenance |
| `suitability_may_proceed` | bool | `False` | **Never true** in current governance |
| `downstream_may_proceed` | bool | `False` | **Never true** in current governance |

`.to_dict()` is JSON-serializable.

---

## 8. Status mapping rules

| Condition | Guardrail status | Downstream |
|-----------|------------------|------------|
| Missing `design_contract` and `contract_validation` | `BLOCK` or `UNKNOWN` | `False` |
| `contract_validation.severity == BLOCK` | `BLOCK` | `False` |
| `status in {contract_blocked, contract_incomplete, contract_unknown}` | `BLOCK` | `False` |
| `contract_valid` or `contract_valid_with_warnings` | `WARN` | `False` (+ `D-GUARDRAIL-REQUIRES-STATISTICAL-VALIDATION`) |
| `contract_complete_allowed == False` | (any) | `False` (+ reason code) |
| `downstream_authorization_status` not `blocked`/`not_authorized` | `BLOCK` | `False` |
| Any overclaim flag `true` | `BLOCK` | `False` |
| Empty `forbidden_downstream_claims` | `BLOCK` | `False` |
| Legacy evidence without contract | `BLOCK`/`UNKNOWN` | `False` |

**Clarification:** `WARN` on mechanically valid contracts means metadata completeness only — not downstream authorization.

---

## 9. Reason-code registry

| Code | Trigger |
|------|---------|
| `D-GUARDRAIL-MISSING-CONTRACT` | No `design_contract` present |
| `D-GUARDRAIL-MISSING-CONTRACT-VALIDATION` | Contract present; summary absent (revalidation path) |
| `D-GUARDRAIL-CONTRACT-BLOCKED` | `contract_blocked` or structural blockers |
| `D-GUARDRAIL-CONTRACT-INCOMPLETE` | `contract_incomplete` |
| `D-GUARDRAIL-CONTRACT-UNKNOWN` | `contract_unknown` |
| `D-GUARDRAIL-DOWNSTREAM-AUTH-VIOLATION` | Governance auth not blocked |
| `D-GUARDRAIL-CONTRACT-COMPLETE-NOT-ALLOWED` | `contract_complete_allowed=False` |
| `D-GUARDRAIL-OVERCLAIM-TRUSTREPORT` | `trust_report_eligible=true` |
| `D-GUARDRAIL-OVERCLAIM-CALIBRATION-SIGNAL` | `calibration_signal_eligible=true` |
| `D-GUARDRAIL-OVERCLAIM-MMM` | `mmm_ready` / `mmm_eligible=true` |
| `D-GUARDRAIL-OVERCLAIM-LLM` | `llm_authorized=true` |
| `D-GUARDRAIL-OVERCLAIM-PRODUCTION` | `production_ready` / `causal_readout_authorized=true` |
| `D-GUARDRAIL-REQUIRES-STATISTICAL-VALIDATION` | Valid metadata; stat protocol not executed |
| `D-GUARDRAIL-LEGACY-CONTRACT-UNKNOWN` | Legacy evidence without contract |

---

## 10. Golden fixture relationship

Golden fixtures in `tests/fixtures/artifact_schemas/design_contract_golden_001/` are the **primary regression inputs** for guardrail runtime tests:

- **Positive fixtures** → `WARN` metadata status; `downstream_may_proceed=False`  
- **`tier1_multicell_contract_blocked.json`** → `BLOCK`  
- **Negative fixtures** → `BLOCK` with appropriate reason codes  
- **Legacy fixture** → `BLOCK`/`UNKNOWN` with missing-contract reasons  

---

## 11. Runtime emission relationship

Tier-1 emission (`geo_runner` → `design_contract_builder_001` → `validate_design_contract`) produces:

- `design_contract` block in `DesignEvidence.to_dict()`  
- Compact `contract_validation` summary (`status`, `severity`, `reason_codes`, `contract_complete_allowed`, `blocked_downstream_roles`)  

The guardrail runtime **consumes** these emitted shapes but is **not wired** into producer execution in this artifact.

**Missing `contract_validation` policy:** When `design_contract` is present without `contract_validation`, the runtime **re-validates** the contract via `validate_design_contract()` and emits `D-GUARDRAIL-MISSING-CONTRACT-VALIDATION` as an audit reason while using the revalidated summary.

---

## 12. No-overclaim enforcement

The runtime blocks (or keeps `downstream_may_proceed=False`) when any of these appear authorized/true:

- TrustReport eligibility  
- CalibrationSignal eligibility  
- MMM readiness  
- LLM authorization  
- `production_ready`  
- `causal_readout_authorized`  
- Pooled multi-cell causal geometry (`pooled_multi_cell`)  

This is **metadata guardrail only** — not statistical suitability judgment.

---

## 13. Legacy behavior

`legacy_design_evidence_without_contract.json`:

- No `design_contract` key  
- Guardrail → `BLOCK`/`UNKNOWN`  
- Reason codes: `D-GUARDRAIL-MISSING-CONTRACT`, `D-GUARDRAIL-LEGACY-CONTRACT-UNKNOWN`  
- All downstream roles blocked  

---

## 14. CI gating

```bash
poetry run pytest tests/validation/test_design_guardrail_runtime_integration_001.py -q
```

Companion regression (unchanged):

- `test_design_contract_validator_001.py`  
- `test_design_tier1_contract_emission_001.py`  
- `test_design_contract_golden_fixtures_001.py`  

---

## 15. Current governance status

| Item | Status |
|------|--------|
| Contract-complete designs | **0 / 31** |
| `contract_complete_allowed` | Always `False` |
| Downstream authorization | **Blocked** |
| TrustReport / CalibrationSignal / MMM / LLM | **Blocked** |
| Guardrail runtime evaluator | **Implemented** (not wired to producers) |
| Suitability reassessment | ✅ **Complete** — consumes runtime guardrail results per [`DESIGN_SUITABILITY_REASSESSMENT_001`](DESIGN_SUITABILITY_REASSESSMENT_001.md) |

---

## 16. Failure modes prevented

| Failure mode | Prevention |
|--------------|------------|
| Silent downstream promotion from valid metadata | `downstream_may_proceed` always `False` |
| Overclaim via governance flags | Explicit `D-GUARDRAIL-OVERCLAIM-*` blockers |
| Legacy evidence treated as contract-complete | Missing-contract BLOCK/UNKNOWN |
| Input mutation during evaluation | Deep-copy immutability tests |
| Statistical suitability implied by PASS/WARN | `suitability_may_proceed=False`; stat validation reason required |

---

## 17. Roadmap

**Completed:** Schema → validator → tier-1 emission → golden fixtures → **guardrail runtime integration** → **suitability reassessment**.

**Next artifact:** **`D5-DES-STAT-TIER1-001`** — executed tier-1 design statistical validation.

---

## 18. Completion checklist

| Item | Status |
|------|--------|
| Runtime module implemented | ✅ |
| Result dataclass with `.to_dict()` | ✅ |
| Golden fixture tests | ✅ (24 tests) |
| No-overclaim enforcement | ✅ |
| Input immutability | ✅ |
| Companion docs updated | ✅ |
| No estimator/inference changes | ✅ |
| No D5 archive changes | ✅ |
| No public API export | ✅ |
| No producer wiring | ✅ |

---

## 19. Current status and verdict

**Verdict:** `design_guardrail_runtime_integration_defined_and_tested_no_promotion`

Runtime guardrail evaluator consumes emitted contract metadata, maps validator state to PASS/WARN/BLOCK decisions, and enforces conservative no-overclaim policy. **0/31 contract-complete designs**; downstream authorization remains blocked; no TrustReport/CalibrationSignal/MMM/LLM eligibility; no suitability promotion.

---

*DESIGN-GUARDRAIL-RUNTIME-INTEGRATION-001 v1.0.1 — Accepted; reassessment consumes guardrail results; 0 contract-complete; next = D5-DES-STAT-TIER1-001.*
