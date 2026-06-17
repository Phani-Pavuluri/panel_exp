# Design Guardrail Enforcement 001

**Artifact ID:** DESIGN-GUARDRAIL-ENFORCEMENT-001  
**Status:** Implemented — **no downstream promotion**  
**Verdict:** `design_guardrail_enforcement_implemented_no_downstream_promotion`

## 1. Executive summary

Runtime enforcement layer combining contract validation, design guardrails (`design_guardrail_runtime_001.py`), and combination guardrails (`design_combination_guardrail_001.py`) into an authoritative `DesignGuardrailEnforcementResult` attached to `DesignEvidence` at geo-run production time.

## 2. Why enforcement was required

`DESIGN-COMBINATION-VALIDATION-EXECUTION-001` characterized design × estimator combinations but downstream surfaces could ignore guardrail output. This artifact fail-closes blocked/restricted paths.

## 3. Prior evaluator versus enforcement

| Layer | Module | Role |
|-------|--------|------|
| L1 | `design_contract_validator_001` | Contract field validation |
| L2 | `design_guardrail_runtime_001` | PASS/WARN/BLOCK from contract |
| L3 | `design_combination_guardrail_001` | DCM-001–008 combination rules |
| L4 | `design_guardrail_enforcement_001` | Authoritative enforcement + exceptions |

## 4–6. Scope / Non-goals / Architecture

In scope: enforcement result type, combination registry, producer wiring (`geo_runner` → `ExperimentEvidence.build`), consumer `assert_design_path_allowed`, fixtures, tests.

Out of scope: production promotion, TrustReport/CalibrationSignal/MMM/LLM integration, algorithm changes, bypass APIs.

## 7–9. Inputs

- `design_contract`, `contract_validation`
- Optional `design_id`, `estimator_id`, `inference_id`, `geometry_id`, `readout_semantics`
- Executed DCM statuses from combination-validation summary

## 10. Result object

`DesignGuardrailEnforcementResult` — JSON-serializable, frozen, includes `allowed`, `status`, `severity`, `reason_codes`, `blocked_roles`, combination metadata, `enforcement_version`.

## 11. Status taxonomy

- **WARN:** research/diagnostic/validation only; `allowed=True` only for research roles when not blocked
- **BLOCK:** geometry/readout/pooled/downstream/contract violations
- **UNKNOWN:** absent evidence; fails closed to BLOCK when execution requested
- **PASS:** not emitted for production/downstream in this artifact

## 12. Reason-code registry

`D-ENFORCE-*` codes in `design_guardrail_enforcement_001.py` and `design_combination_guardrail_001.py`.

## 13–17. Enforcement rules

Contract, geometry (DCM-003), readout (point-only, forecast, null-monitor), multi-cell (per-cell only, pooled blocked), estimator/inference (DCM-001–008) per combination registry.

## 18–19. Role policy

**Always BLOCK:** TrustReport, CalibrationSignal, MMM, LLM, production_decision, production_recommendation, automated_budget_action, pooled_causal_claim.

**WARN research only:** research, diagnostic, validation, blocked_status_explanation.

## 20–22. Producer wiring / Serialization

`ExperimentEvidence.build` calls `build_producer_guardrail_bundle` when `design_contract` present. Fields: `design_guardrail`, `combination_guardrail`, `guardrail_enforcement` on `DesignEvidence`.

## 23–24. Consumer API / Exceptions

```python
from panel_exp.validation.design_guardrail_enforcement_001 import (
    assert_design_path_allowed,
    enforce_design_decision_path,
    DesignGuardrailViolation,
)
```

`DesignGuardrailViolation` raised for blocked roles; no `force`/`override` parameters.

## 25–26. Fixtures / Tests

`tests/fixtures/artifact_schemas/design_guardrail_enforcement_001/scenarios.json`  
`tests/validation/test_design_guardrail_enforcement_001.py` — 45 tests.

## 27. Runtime example

```python
bundle = build_producer_guardrail_bundle(
    design_contract=contract,
    contract_validation=validation,
    estimator_id="SCM",
    inference_id="UnitJackknife",
)
assert_design_path_allowed(bundle["guardrail_enforcement"], requested_role="research")
```

## 28. Security / no-bypass

No `force=True`, `override_guardrail`, or `bypass_guardrail` APIs. Downstream roles always fail closed.

## 29–32. Governance / Limitations / Follow-up / Verdict

**Verdict:** `design_guardrail_enforcement_implemented_no_downstream_promotion`

All downstream authorization remains false. Next: wire enforcement into estimator readout producers when those paths gain identity metadata.
