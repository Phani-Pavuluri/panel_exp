# READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001` |
| **Artifact type** | `readout_diagnostics_sensitivity_runtime` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `runtime_evidence_planning_and_sufficiency_only_no_diagnostic_or_sensitivity_execution` |
| **Base commit** | `dc4f132` (Define readout diagnostics sensitivity contract) |
| **Final verdict** | `readout_diagnostics_sensitivity_runtime_implemented_evidence_planning_and_sufficiency_only_no_diagnostic_or_sensitivity_execution` |

This runtime evaluates diagnostic/sensitivity evidence planning and sufficiency without executing diagnostics, sensitivity checks, estimators, or inference. It does not authorize claims or production readouts.

---

## 2. Source files inspected

- `panel_exp/validation/readout_diagnostics_sensitivity_contract_001.py`
- `tests/validation/test_readout_diagnostics_sensitivity_contract_001.py`
- `docs/track_d/READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001_REPORT.md`
- `panel_exp/validation/estimator_inference_executor_adapters_002.py`
- `panel_exp/validation/estimator_inference_execution_runtime_001.py`
- `panel_exp/validation/readout_plan_runtime_001.py`
- `panel_exp/validation/method_suitability_runtime_001.py`
- `docs/ROADMAP_V4.md`
- `docs/MIP_AUDIT_REGISTRY.md`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`

---

## 3. Implementation scope

Implemented:

- Deterministic public runtime `evaluate_readout_diagnostics_sensitivity(input_data, config=None)`
- Execution artifact presence gate
- Diagnostic/sensitivity requirement planning
- Evidence packet generation from provided results (not computed)
- Missing/blocked/inconclusive evidence handling
- Evidence sufficiency classification
- Typed failure packets with retry categories
- Diagnostic-only production claim boundary
- Multiple-request support without ranking
- Strict claim-boundary enforcement

Not implemented:

- Real placebo/jackknife/bootstrap/conformal/parallel-trend/donor-support/pre-period-fit/outlier/interference/spend computations
- Diagnostic or sensitivity check execution
- Pass/fail computation from raw data
- Estimator or inference execution
- Claim or production authorization

---

## 4. Relationship to diagnostics/sensitivity contract

`READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001` defined requirement/plan/result schemas, statuses, evidence gates, and failure semantics. This runtime implements conservative evidence planning and sufficiency evaluation using those contract statuses without computing diagnostic or sensitivity results.

---

## 5. Relationship to estimator/inference execution runtime shell

The execution runtime shell emits execution packets with `INSTRUMENT_EXECUTION_NOT_RUN` by default. This runtime consumes execution artifacts and instrument execution results, and by default treats incomplete execution as `EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED`.

---

## 6. Relationship to executor adapters

Governed executor adapters provide dry-run envelopes and adapter availability metadata. This runtime can consume execution artifacts produced downstream of adapter-aware execution packets but does not invoke adapters or executors.

---

## 7. Public API

```python
from panel_exp.validation.readout_diagnostics_sensitivity_runtime_001 import (
    evaluate_readout_diagnostics_sensitivity,
    evaluate_diagnostics_sensitivity_evidence,
    ReadoutDiagnosticsSensitivityRuntimeConfig,
)
```

- `evaluate_readout_diagnostics_sensitivity(input_data, config=None) -> ReadoutDiagnosticsSensitivityRuntimeReport`
- `evaluate_diagnostics_sensitivity_evidence(...)` is an alias

Deterministic and side-effect-free: no network calls, no random execution, no LLM/MMM calls, no diagnostic/sensitivity computation.

---

## 8. Input support

Supported `input_data` forms: `dict`, `list[dict]`, dataclass-like objects.

Minimum request fields: `design_id`, `execution_status`, `execution_artifacts`, `instrument_execution_results`, `diagnostic_requirements`, `sensitivity_requirements`, `diagnostic_results`, `sensitivity_results`, `claim_scope`, `production_governance_config`.

---

## 9. Output report structure

`ReadoutDiagnosticsSensitivityRuntimeReport` emits:

- `artifact_id`, `design_id`, `evidence_sufficiency_status`
- `diagnostic_plans`, `sensitivity_plans`
- `diagnostic_evidence_packets`, `sensitivity_evidence_packets`
- `diagnostic_failure_packets`, `sensitivity_failure_packets`
- `evidence_aggregation_report`, `evidence_sufficiency_report`
- `claim_boundary_report`
- `warnings`, `blocking_reasons`, `issues`
- `design_reports` in multi-request mode

---

## 10. Diagnostic/sensitivity statuses

Uses contract statuses for planned and provided-result evidence evaluation. Plans default to `DIAGNOSTIC_PLANNED_NOT_RUN` / `SENSITIVITY_PLANNED_NOT_RUN` with `planned_execution_mode = not_run`.

---

## 11. Evidence sufficiency statuses

Aggregates per-requirement evidence into overall sufficiency using priority ordering. `EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW` enables future claim review only; it is not claim authorization.

---

## 12. Runtime gates

Implements contract evidence gate order conservatively:

1. execution artifact presence
2. diagnostic/sensitivity requirement presence
3. plan generation
4. provided result evaluation
5. failure/inconclusive handling
6. evidence sufficiency aggregation
7. claim review handoff (non-authorizing)

---

## 13. Requirement planning behavior

Each diagnostic/sensitivity requirement produces a typed plan with `planned_execution_mode = not_run`. No diagnostic or sensitivity checks are executed in this runtime.

---

## 14. Provided result handling

If caller supplies pre-computed result statuses (e.g. `DIAGNOSTIC_PASSED`), the runtime classifies evidence sufficiency accordingly without computing `result_value`, thresholds, or pass/fail from data.

---

## 15. Missing evidence handling

Missing required results with `blocking_if_missing` produce insufficient missing diagnostics/sensitivity statuses. Nonblocking missing results produce provisional evidence with warnings.

---

## 16. Diagnostic-only boundary

Diagnostic-only instruments with `required_for_production` cannot support production/causal/incremental-lift claim evidence when `allow_diagnostic_only_for_production_claim` is false (default).

---

## 17. Claim boundaries

Runtime-positive flags:

- `diagnostics_sensitivity_runtime_implemented = true`
- `diagnostic_plans_generated = true`
- `sensitivity_plans_generated = true`
- `diagnostic_evidence_packets_generated = true`
- `sensitivity_evidence_packets_generated = true`
- `evidence_sufficiency_evaluated = true`
- `failure_packets_generated = true/false`

Always false:

- `diagnostic_check_executed`
- `sensitivity_check_executed`
- `diagnostic_result_computed`
- `sensitivity_result_computed`
- `diagnostic_pass_fail_computed`
- `sensitivity_pass_fail_computed`
- all estimator/inference/effect/claim/production authorization flags

---

## 18. Tests added

`tests/validation/test_readout_diagnostics_sensitivity_runtime_001.py` covers public API, execution artifact gate, plan generation, missing/failed/inconclusive evidence, diagnostic-only boundary, failure packet retry categories, multi-request behavior, and claim-boundary enforcement.

---

## 19. Validation results

- JSON summary validation passed
- targeted runtime pytest passed
- contract and upstream regressions passed
- governance tests passed when governance files updated
- safety/capability/fixture-branching greps passed

---

## 20. Known limitations

- No governed diagnostic or sensitivity computations
- Evidence sufficiency depends on caller-provided result statuses when present
- Default execution-not-completed blocking reflects current execution shell behavior
- No claim authorization or production authorization

---

## 21. Recommended next artifact

**Primary:** `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR`  
**Alternative:** `CLAIM_AUTHORIZATION_CONTRACT_001`

---

## 22. Final verdict

`readout_diagnostics_sensitivity_runtime_implemented_evidence_planning_and_sufficiency_only_no_diagnostic_or_sensitivity_execution`
