# READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001` |
| **Artifact type** | `readout_diagnostics_sensitivity_contract` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_diagnostic_or_sensitivity_execution` |
| **Base commit** | `0c3f5ff` (Add governed estimator executor adapters) |
| **Final verdict** | `readout_diagnostics_sensitivity_contract_defined_no_diagnostic_or_sensitivity_execution` |

READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001 defines the future governed contract for representing diagnostic and sensitivity requirements, plans, results, statuses, failure packets, and evidence boundaries around readout execution. It specifies how diagnostics and sensitivity checks must be attached to planned/executed estimator-inference instruments before claim authorization can be considered. It does not execute diagnostics or sensitivity checks, execute estimators, compute effects, compute uncertainty, authorize claims, or authorize production readout.

---

## 2. Source files inspected

- `panel_exp/validation/estimator_inference_executor_adapters_002.py`
- `tests/validation/test_estimator_inference_executor_adapters_002.py`
- `docs/track_d/ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS_REPORT.md`
- `docs/track_d/archives/ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS_summary.json`
- `panel_exp/validation/estimator_inference_execution_runtime_001.py`
- `tests/validation/test_estimator_inference_execution_runtime_001.py`
- `docs/track_d/ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001_REPORT.md`
- `docs/track_d/archives/ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001_summary.json`
- `docs/track_d/ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001_REPORT.md`
- `panel_exp/validation/estimator_inference_execution_contract_001.py`
- `tests/validation/test_estimator_inference_execution_contract_001.py`
- `panel_exp/validation/readout_plan_runtime_001.py`
- `tests/validation/test_readout_plan_runtime_001.py`
- `panel_exp/validation/method_suitability_runtime_001.py`
- `tests/validation/test_method_suitability_runtime_001.py`
- `docs/ROADMAP_V4.md`
- `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`
- `docs/MIP_AUDIT_REGISTRY.md`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`

---

## 3. Why this contract is needed

Estimator/inference execution runtime and governed executor adapters now produce typed execution packets and adapter-aware envelopes, but they do not define how diagnostic and sensitivity evidence must be planned, represented, aggregated, or evaluated before claim review.

Future claim authorization requires explicit evidence boundaries: which diagnostics must pass, which sensitivity checks must be present, how diagnostic-only instruments differ from production candidates, and how missing/failed/inconclusive evidence restricts claim review.

This contract defines those future schemas and gate semantics without executing diagnostics or sensitivity checks.

---

## 4. Relationship to readout plan runtime

`READOUT_PLAN_RUNTIME_001` produces planned primary/sensitivity/diagnostic candidates and attaches diagnostic/sensitivity requirement references to instrument specs. This contract consumes those planned requirements and defines how they must be expanded into diagnostic/sensitivity plans and future result artifacts.

---

## 5. Relationship to estimator/inference execution runtime shell

`ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001` validates execution readiness and emits execution packets with diagnostic/sensitivity prerequisite checks. This contract defines the downstream evidence contract that a future diagnostics/sensitivity runtime must satisfy after execution artifacts exist.

---

## 6. Relationship to governed executor adapters

`ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS` maps instruments to governed adapters and dry-run envelopes. This contract adds `EXECUTOR_AVAILABILITY_DIAGNOSTIC` and related evidence requirements so adapter availability and dry-run posture can be represented in evidence aggregation without executing estimators.

---

## 7. Conceptual distinctions

1. **Readout plan runtime:** Plans primary/sensitivity/diagnostic candidates. Already implemented. Does not execute.
2. **Estimator/inference execution runtime shell:** Validates readiness and emits execution packets. Already implemented. Does not execute estimators.
3. **Governed executor adapters:** Map instruments to governed adapters/dry-run envelopes. Already implemented. Does not execute estimators.
4. **Diagnostics and sensitivity contract:** Defines evidence requirements and result schemas. This artifact. Does not execute.
5. **Diagnostics and sensitivity runtime:** Future runtime that may compute or collect diagnostic/sensitivity results.
6. **Claim authorization:** Future layer that decides which claims can be made from execution + diagnostics + sensitivity.
7. **Trusted readout report:** Future final reporting artifact.

---

## 8. Future contract concepts

Future concepts defined by this contract:

- `ReadoutDiagnosticRequirement`
- `ReadoutSensitivityRequirement`
- `ReadoutDiagnosticPlan`
- `ReadoutSensitivityPlan`
- `ReadoutDiagnosticResult`
- `ReadoutSensitivityResult`
- `ReadoutDiagnosticStatus`
- `ReadoutSensitivityStatus`
- `ReadoutDiagnosticEvidencePacket`
- `ReadoutSensitivityEvidencePacket`
- `ReadoutDiagnosticFailurePacket`
- `ReadoutSensitivityFailurePacket`
- `ReadoutDiagnosticTrace`
- `ReadoutSensitivityTrace`
- `ReadoutEvidenceAggregationReport`
- `ReadoutEvidenceSufficiencyReport`
- `ReadoutDiagnosticSensitivityClaimBoundaryReport`

---

## 9. Diagnostic types

Defined diagnostic types:

- `PRE_PERIOD_FIT_DIAGNOSTIC`
- `COVARIATE_BALANCE_DIAGNOSTIC`
- `ASSIGNMENT_REPRODUCIBILITY_DIAGNOSTIC`
- `PLACEBO_DIAGNOSTIC`
- `DONOR_SUPPORT_DIAGNOSTIC`
- `PARALLEL_TREND_DIAGNOSTIC`
- `OUTLIER_DIAGNOSTIC`
- `INTERFERENCE_RISK_DIAGNOSTIC`
- `SPEND_SUPPORT_DIAGNOSTIC`
- `COMMON_CONTROL_CONFLICT_DIAGNOSTIC`
- `SPLIT_CONTROL_RECHECK_DIAGNOSTIC`
- `DATA_CONTRACT_DIAGNOSTIC`
- `INSTRUMENT_GOVERNANCE_DIAGNOSTIC`
- `UNCERTAINTY_SEMANTICS_DIAGNOSTIC`
- `EXECUTOR_AVAILABILITY_DIAGNOSTIC`

---

## 10. Sensitivity types

Defined sensitivity types:

- `JACKKNIFE_SENSITIVITY`
- `BOOTSTRAP_SENSITIVITY`
- `PLACEBO_SENSITIVITY`
- `KFOLD_SENSITIVITY`
- `DONOR_SET_SENSITIVITY`
- `OUTLIER_EXCLUSION_SENSITIVITY`
- `WINDOW_LENGTH_SENSITIVITY`
- `COVARIATE_SET_SENSITIVITY`
- `SPEND_SUPPORT_SENSITIVITY`
- `ASSIGNMENT_VARIANT_SENSITIVITY`
- `INTERFERENCE_ASSUMPTION_SENSITIVITY`
- `ESTIMAND_RECLASSIFICATION_SENSITIVITY`

---

## 11. Diagnostic statuses

Defined diagnostic statuses:

- `DIAGNOSTIC_REQUIRED_NOT_PLANNED`
- `DIAGNOSTIC_PLANNED_NOT_RUN`
- `DIAGNOSTIC_NOT_APPLICABLE`
- `DIAGNOSTIC_BLOCKED`
- `DIAGNOSTIC_FAILED`
- `DIAGNOSTIC_PASSED`
- `DIAGNOSTIC_PASSED_WITH_WARNINGS`
- `DIAGNOSTIC_INCONCLUSIVE`
- `DIAGNOSTIC_NOT_EVALUATED`

`DIAGNOSTIC_PASSED` and `DIAGNOSTIC_FAILED` are future runtime result statuses. This contract must not emit computed diagnostic results.

---

## 12. Sensitivity statuses

Defined sensitivity statuses:

- `SENSITIVITY_REQUIRED_NOT_PLANNED`
- `SENSITIVITY_PLANNED_NOT_RUN`
- `SENSITIVITY_NOT_APPLICABLE`
- `SENSITIVITY_BLOCKED`
- `SENSITIVITY_FAILED`
- `SENSITIVITY_PASSED`
- `SENSITIVITY_PASSED_WITH_WARNINGS`
- `SENSITIVITY_INCONCLUSIVE`
- `SENSITIVITY_NOT_EVALUATED`

`SENSITIVITY_PASSED` and `SENSITIVITY_FAILED` are future runtime result statuses. This contract must not emit computed sensitivity results.

---

## 13. Evidence sufficiency statuses

Defined evidence sufficiency statuses:

- `EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW`
- `EVIDENCE_SUFFICIENT_WITH_WARNINGS`
- `EVIDENCE_PROVISIONAL`
- `EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS`
- `EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY`
- `EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS`
- `EVIDENCE_INSUFFICIENT_FAILED_SENSITIVITY`
- `EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED`
- `EVIDENCE_BLOCKED_BY_GOVERNANCE`
- `EVIDENCE_NOT_EVALUATED`

`EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW` is not claim authorization.

---

## 14. Requirement fields

Each diagnostic/sensitivity requirement must include:

- `requirement_id`
- `requirement_type`
- `applies_to_instrument_id`
- `applies_to_execution_role`
- `applies_to_estimand`
- `required_for_claim_type`
- `required_for_production`
- `required_before_execution`
- `required_after_execution`
- `blocking_if_missing`
- `blocking_if_failed`
- `minimum_evidence_level`
- `threshold_policy`
- `governance_source`
- `notes`

---

## 15. Plan fields

Each future diagnostic/sensitivity plan must include:

- `plan_id`
- `requirement_id`
- `instrument_id`
- `execution_artifact_id`
- `planned_check_type`
- `planned_input_artifacts`
- `planned_output_artifacts`
- `planned_threshold_policy`
- `planned_execution_mode`
- `planned_status`
- `blocking_policy`
- `warnings`

---

## 16. Result fields

Each future diagnostic/sensitivity result must include:

- `result_id`
- `plan_id`
- `requirement_id`
- `instrument_id`
- `execution_artifact_id`
- `result_status`
- `result_value`
- `threshold`
- `threshold_direction`
- `passed`
- `blocking_result`
- `interpretation`
- `evidence_level`
- `artifact_references`
- `warnings`

These are future result fields only. This contract does not compute `result_value`, threshold comparisons, or pass/fail outcomes.

---

## 17. Failure packet semantics

Diagnostic/sensitivity failure packets must include:

- `failure_id`
- `requirement_id`
- `plan_id`
- `instrument_id`
- `execution_artifact_id`
- `failure_status`
- `missing_inputs`
- `blocked_requirements`
- `failed_requirements`
- `inconclusive_requirements`
- `governance_failures`
- `suggested_retry_categories`
- `claim_boundary_report`

Retry categories:

- `ADD_REQUIRED_DIAGNOSTIC_PLAN`
- `ADD_REQUIRED_SENSITIVITY_PLAN`
- `FIX_DIAGNOSTIC_INPUTS`
- `FIX_SENSITIVITY_INPUTS`
- `RERUN_EXECUTION_WITH_REQUIRED_TRACE`
- `CHANGE_READOUT_PLAN`
- `RESTRICT_CLAIM_SCOPE`
- `BLOCK_CLAIM`
- `BLOCK_INSTRUMENT`
- `BLOCK_DESIGN`

Suggested retries are diagnostic only. This contract does not implement retries.

---

## 18. Readiness/evidence gates

Gate order:

1. execution artifact presence gate
2. diagnostic requirement presence gate
3. sensitivity requirement presence gate
4. diagnostic plan gate
5. sensitivity plan gate
6. diagnostic result gate
7. sensitivity result gate
8. diagnostic failure/inconclusive gate
9. sensitivity failure/inconclusive gate
10. evidence sufficiency gate
11. claim review handoff gate

Rules:

- If execution artifact is missing/not completed, evidence sufficiency is blocked.
- If required diagnostics are missing, evidence sufficiency is insufficient.
- If required sensitivity checks are missing, evidence sufficiency is insufficient.
- If diagnostic plans are missing, future runtime must block/provisionalize.
- If sensitivity plans are missing, future runtime must block/provisionalize.
- If required diagnostic result fails and `blocking_if_failed` is true, evidence sufficiency is insufficient.
- If required sensitivity result fails and `blocking_if_failed` is true, evidence sufficiency is insufficient.
- If results are inconclusive, evidence sufficiency is provisional or insufficient based on blocking policy.
- Evidence sufficiency may allow claim review only; it must not authorize claims.

---

## 19. Instrument-family treatment

### DID + Bootstrap

- parallel-trend diagnostics
- pre-period fit diagnostics
- bootstrap stability sensitivity
- covariate balance checks

### SCM + Placebo

- pre-period fit diagnostics
- donor support diagnostics
- placebo diagnostic evidence
- diagnostic-only boundary

### SCM + UnitJackknife

- pre-period fit diagnostics
- donor support diagnostics
- jackknife stability sensitivity

### TBR Ridge + BRB

- pre-period fit diagnostics
- ridge stability/restriction caveats
- BRB uncertainty semantics check
- outlier sensitivity

### TBR Ridge + KFold

- k-fold stability sensitivity
- predictive/pre-period fit diagnostics
- diagnostic/restricted boundary

### AugSynth + Jackknife

- donor support diagnostics
- convex hull/range stress diagnostics
- jackknife stability sensitivity
- restricted/diagnostic boundary

### MatchedPair + RandomizationInference

- assignment reproducibility diagnostics
- pair balance diagnostics
- randomization inference semantics check

### A/B + StandardInference

- only when assignment and unit independence semantics are governed
- blocked for incompatible geo-panel designs

---

## 20. Claim-boundary treatment

- Diagnostics and sensitivity evidence may support future claim review, but cannot authorize claims.
- Failed or missing required evidence must restrict or block claim review.
- Diagnostic-only evidence cannot become production causal evidence.
- Sensitivity checks cannot repair invalid estimands or invalid assignment artifacts.
- Evidence sufficiency is not production authorization.

---

## 21. Examples

1. DID + Bootstrap requires parallel-trend diagnostic and bootstrap stability sensitivity before claim review.
2. SCM + Placebo produces diagnostic-only evidence; cannot support production lift claim.
3. SCM + UnitJackknife requires donor support and jackknife stability evidence.
4. TBR Ridge + BRB requires pre-period fit and outlier sensitivity.
5. AugSynth + Jackknife requires donor support/range stress and jackknife sensitivity.
6. Missing diagnostic plan blocks evidence sufficiency.
7. Missing sensitivity result blocks/provisionalizes claim review.
8. Failed blocking diagnostic prevents claim review.
9. Inconclusive sensitivity produces provisional evidence.
10. Execution not completed blocks diagnostic/sensitivity evidence sufficiency.

---

## 22. Claim boundaries

Always false in this contract:

- `diagnostics_sensitivity_runtime_implemented`
- `diagnostic_check_executed`
- `sensitivity_check_executed`
- `diagnostic_result_computed`
- `sensitivity_result_computed`
- `diagnostic_pass_fail_computed`
- `sensitivity_pass_fail_computed`
- `evidence_sufficiency_computed`
- `estimator_execution_implemented`
- `inference_execution_implemented`
- `effect_estimate_computed`
- `lift_computed`
- `roi_computed`
- `p_value_computed`
- `confidence_interval_computed`
- `uncertainty_computed`
- `causal_claim_authorized`
- `incremental_lift_claim_authorized`
- `roi_claim_authorized`
- `production_readout_authorized`
- `production_authorization_granted`
- `mmm_runtime_calls_implemented`
- `mmm_calibration_authorized`
- `llm_decisioning_authorized`

Allowed contract-level positives:

- `diagnostics_sensitivity_contract_defined = true`
- `diagnostic_requirement_contract_defined = true`
- `sensitivity_requirement_contract_defined = true`
- `diagnostic_plan_contract_defined = true`
- `sensitivity_plan_contract_defined = true`
- `diagnostic_result_contract_defined = true`
- `sensitivity_result_contract_defined = true`
- `evidence_sufficiency_contract_defined = true`
- `failure_packet_contract_defined = true`
- `claim_boundaries_defined = true`

---

## 23. Future implementation acceptance criteria

Future runtime must:

- consume execution artifacts
- consume diagnostic requirements
- consume sensitivity requirements
- build diagnostic plans
- build sensitivity plans
- optionally execute governed diagnostics only
- optionally execute governed sensitivity checks only
- emit typed diagnostic results
- emit typed sensitivity results
- emit evidence sufficiency report
- emit failure packets for missing/failed/inconclusive evidence
- preserve diagnostic-only boundaries
- not authorize causal claims
- not authorize production

---

## 24. Future tests

Future runtime tests should cover:

- missing execution artifact blocks evidence sufficiency
- missing required diagnostic blocks/provisionalizes
- missing required sensitivity blocks/provisionalizes
- diagnostic-only instrument cannot support production claim evidence
- failed blocking diagnostic blocks claim review
- failed nonblocking diagnostic produces warning/provisional status
- inconclusive sensitivity produces provisional status
- DID+Bootstrap requires parallel-trend and bootstrap stability evidence
- SCM+Placebo remains diagnostic-only
- AugSynth+Jackknife requires donor support/range stress and jackknife sensitivity
- TBR Ridge+BRB requires pre-period fit and outlier sensitivity
- evidence sufficiency does not authorize claims
- no estimator execution
- no inference execution
- no effect/lift/ROI/p-values/CIs
- no production authorization
- no fixture-specific branching

---

## 25. Roadmap placement

This contract sits after governed executor adapters and before diagnostics/sensitivity runtime implementation. It defines the evidence contract that must be satisfied before claim authorization can be considered.

---

## 26. Recommended next artifact

**Primary:** `READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001`  
**Alternative:** `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR`

---

## 27. Final verdict

`readout_diagnostics_sensitivity_contract_defined_no_diagnostic_or_sensitivity_execution`
