# ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001` |
| **Artifact type** | `estimator_inference_execution_contract` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_estimator_or_inference_execution` |
| **Base commit** | `3e78fd5` (Implement readout plan runtime) |
| **Final verdict** | `estimator_inference_execution_contract_defined_no_estimator_or_inference_execution` |

This artifact is a **contract/specification document only**. It defines the future governed execution contract for estimator/inference instruments planned by `READOUT_PLAN_RUNTIME_001`. **No estimator execution runtime, inference execution runtime, SCM/TBR/DID/AugSynth fitting, placebo/jackknife/bootstrap/conformal execution, effect estimation, lift/ROI computation, p-values, confidence intervals, uncertainty computation, diagnostic execution, sensitivity execution, claim authorization, MMM runtime calls, LLM decisioning, or production authorization was implemented or authorized.**

---

## 2. Source files inspected

| File | Role |
|------|------|
| `panel_exp/validation/readout_plan_runtime_001.py` | Upstream readout planning runtime |
| `tests/validation/test_readout_plan_runtime_001.py` | Readout plan runtime tests |
| `docs/track_d/READOUT_PLAN_RUNTIME_001_REPORT.md` | Readout plan runtime report |
| `docs/track_d/archives/READOUT_PLAN_RUNTIME_001_summary.json` | Readout plan runtime summary |
| `docs/track_d/READOUT_PLAN_CONTRACT_001_REPORT.md` | Upstream readout plan contract |
| `docs/track_d/archives/READOUT_PLAN_CONTRACT_001_summary.json` | Readout plan contract summary |
| `panel_exp/validation/readout_plan_contract_001.py` | Readout plan contract harness |
| `docs/track_d/READOUT_METHOD_GOVERNANCE_CONTRACT_001_REPORT.md` | Governance eligibility upstream |
| `panel_exp/validation/readout_method_governance_contract_001.py` | Governance contract harness |
| `panel_exp/validation/method_suitability_runtime_001.py` | Instrument suitability matrix upstream |
| `panel_exp/validation/design_assignment_runtime_001.py` | Assignment artifact upstream |
| `docs/track_d/METHOD_SUITABILITY_HANDOFF_CONTRACT_001_REPORT.md` | Estimand handoff upstream |
| `docs/track_d/DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001_REPORT.md` | Assignment contract upstream |
| `docs/track_d/DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001_REPORT.md` | Assignment feasibility upstream |
| `docs/track_d/DESIGN_CELL_STRUCTURE_RUNTIME_001_REPORT.md` | Design structure upstream |
| `docs/track_d/DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001_REPORT.md` | Scenario policy upstream |
| `docs/track_d/POWER_MDE_DIAGNOSTICS_RUNTIME_001_REPORT.md` | Power/MDE readiness upstream |
| `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md` | Method soundness roadmap |
| `docs/ROADMAP_V4.md` | Product roadmap |
| `docs/MIP_AUDIT_REGISTRY.md` | MIP audit registry |
| `docs/governance/OPEN_INVESTIGATIONS_001.json` | Governance investigations |

---

## 3. Why this contract is needed

The current stack validates through readout planning:

Profiler/data readiness → … → Method suitability → Design assignment → Readout method governance → **Readout plan runtime**.

The next unanswered question is:

> Given a governed readout plan with planned primary/sensitivity/diagnostic candidates, what must be true before a future execution runtime may attempt estimator/inference execution, and what typed artifacts must it emit?

Without this contract, future runtimes may:

- execute estimators without explicit data contracts or hashes
- substitute input data silently
- run blocked or not-evaluated planned instruments
- promote diagnostic-only instruments to primary production execution
- emit effect estimates without explicit effect scale semantics
- emit uncertainty without matching planned uncertainty semantics
- interpret diagnostic-only uncertainty as production-claimable
- skip diagnostics/sensitivity prerequisites
- authorize causal, lift, or ROI claims from execution artifacts
- bypass provenance/trace requirements

This contract defines execution input requirements, instrument-specific execution packet fields, effect estimate report schema, uncertainty report schema, inference diagnostic report schema, execution trace/provenance, artifact manifests, and failure packet semantics — without executing estimators or inference.

---

## 4. Core goal statement

`ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001` defines the future governed contract for executing planned estimator/inference instruments from a readout plan and emitting typed execution artifacts. It defines execution input requirements, instrument-specific execution packet fields, effect estimate report schema, uncertainty report schema, inference diagnostic report schema, execution trace/provenance, artifact manifests, and failure packet semantics. It does not execute estimators, compute inference, estimate effects, calculate p-values/CIs, run diagnostics, run sensitivity checks, authorize causal claims, or authorize production readout.

---

## 5. Relationship to readout plan runtime

`READOUT_PLAN_RUNTIME_001` produces planned primary/sensitivity/diagnostic candidates, execution prerequisites, claim scope, and reporting caveats. It does **not** execute estimators or inference.

This contract consumes `readout_plan_report` and `readout_plan_packet`, including `planned_primary_candidates`, `planned_sensitivity_candidates`, `planned_diagnostic_candidates`, `blocked_instruments`, `not_evaluated_instruments`, and `execution_prerequisites`. If the readout plan is blocked, execution readiness is blocked. **A ready readout plan does not mean execution has occurred or claims are authorized.**

---

## 6. Relationship to readout plan contract

`READOUT_PLAN_CONTRACT_001` defined the future readout plan packet structure, stack roles, planning categories, and claim-scope boundaries.

This contract operationalizes the downstream execution boundary: planned candidates become execution candidates only after execution readiness gates pass. The contract preserves diagnostic-only, blocked, and not-evaluated distinctions from planning.

---

## 7. Relationship to method suitability runtime

`METHOD_SUITABILITY_RUNTIME_001` emits `instrument_suitability_matrix` with per-instrument governance compatibility.

Future execution runtime must respect instrument-level suitability and governance restrictions embedded in planned instrument specs. Execution contracts remain **instrument-level** (e.g., `DID + Bootstrap`, `SCM + Placebo`), not broad-family-only.

---

## 8. Relationship to assignment runtime

`DESIGN_ASSIGNMENT_RUNTIME_001` produces assignment plan, candidate, unit allocations, constraint/exclusion traces, and reproducibility manifest.

Future execution runtime must consume `design_assignment_runtime_report`, `assignment_plan`, `assignment_candidate`, `unit_allocation_report`, and `reproducibility_manifest`. Missing or failed assignment artifacts block execution readiness. Each instrument spec must reference `assignment_artifact_id`.

---

## 9. Conceptual distinctions

| # | Concept | Question answered | Rule |
|---|---------|-------------------|------|
| 1 | **Readout plan runtime** | What is the planned stack? | `READOUT_PLAN_RUNTIME_001`; already implemented; does not execute |
| 2 | **Estimator/inference execution contract** | What must future execution consume and emit? | This artifact; does not execute |
| 3 | **Estimator/inference execution runtime** | What numeric readout is computed? | Future `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001` only |
| 4 | **Diagnostics/sensitivity runtime** | Are required checks satisfied? | Future runtime only |
| 5 | **Claim authorization** | Which claims are allowed? | Future governance layer; always false here |
| 6 | **Production readout report** | Product-facing reporting artifact | Future reporting layer; not implemented here |

---

## 10. Future contract concepts

| Concept | Purpose |
|---------|---------|
| `EstimatorInferenceExecutionInput` | Bundled readout plan, assignment artifacts, data contract, instrument specs |
| `EstimatorInferenceExecutionConfig` | Blocking modes, provisional policy, retry policy |
| `EstimatorInferenceExecutionReport` | Top-level execution contract report |
| `EstimatorInferenceExecutionPacket` | Governed execution packet for downstream diagnostics/authorization |
| `InstrumentExecutionRequest` | Per-instrument execution request (not executed here) |
| `InstrumentExecutionResult` | Per-instrument execution result schema (future runtime only) |
| `InstrumentExecutionStatus` | Per-instrument execution status enum |
| `InstrumentExecutionRole` | Execution role within packet |
| `ExecutionInputDataContract` | Required panel data contract with hashes |
| `ExecutionDesignArtifactReference` | Reference to design artifacts |
| `ExecutionAssignmentArtifactReference` | Reference to assignment artifacts |
| `ExecutionEstimandReference` | Declared estimand for execution |
| `ExecutionInstrumentSpec` | Instrument-level execution specification |
| `ExecutionEffectEstimateReport` | Future effect estimate report schema |
| `ExecutionUncertaintyReport` | Future uncertainty report schema |
| `ExecutionIntervalReport` | Future interval sub-report |
| `ExecutionPValueReport` | Future p-value sub-report |
| `ExecutionInferenceDiagnosticReport` | Future inference diagnostic report schema |
| `ExecutionModelDiagnosticReport` | Future model diagnostic report schema |
| `ExecutionAssumptionCheckReport` | Future assumption check report schema |
| `ExecutionTrace` | Execution trace with hashes and provenance |
| `ExecutionProvenanceManifest` | Provenance manifest for execution artifacts |
| `ExecutionArtifactManifest` | Manifest of emitted execution artifacts |
| `ExecutionFailurePacket` | Structured failure packet on blocked/failed readiness |
| `ExecutionRetryPolicy` | Retry policy metadata (diagnostic only; not implemented) |
| `ExecutionClaimBoundaryReport` | Authorization boundary flags |

---

## 11. Execution statuses

| Status | Meaning |
|--------|---------|
| `EXECUTION_READY_FOR_RUNTIME` | Future execution runtime may attempt estimator/inference execution; **does not mean execution occurred or claims authorized** |
| `EXECUTION_READY_WITH_WARNINGS` | Execution may proceed with preserved warnings |
| `EXECUTION_PROVISIONAL` | Incomplete clarity; governed policy may allow provisional readiness |
| `EXECUTION_BLOCKED_BY_READOUT_PLAN` | Upstream readout plan blocked |
| `EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT` | Assignment artifact missing or failed |
| `EXECUTION_BLOCKED_BY_DATA_CONTRACT` | Input data contract missing or failed |
| `EXECUTION_BLOCKED_BY_ESTIMAND` | Estimand missing or incompatible |
| `EXECUTION_BLOCKED_BY_INSTRUMENT_SPEC` | Instrument spec missing or invalid |
| `EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS` | Uncertainty semantics missing or incompatible |
| `EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA` | Required input data unavailable |
| `EXECUTION_BLOCKED_BY_DIAGNOSTIC_REQUIREMENTS` | Diagnostics prerequisites missing |
| `EXECUTION_BLOCKED_BY_SENSITIVITY_REQUIREMENTS` | Sensitivity prerequisites missing |
| `EXECUTION_BLOCKED_BY_GOVERNANCE` | Governance restrictions unresolved |
| `EXECUTION_NOT_EVALUATED` | Execution readiness not yet evaluated |

---

## 12. Instrument execution statuses

| Status | Meaning |
|--------|---------|
| `INSTRUMENT_EXECUTION_READY` | Instrument may be attempted by future runtime |
| `INSTRUMENT_EXECUTION_READY_WITH_WARNINGS` | Instrument may proceed with warnings |
| `INSTRUMENT_EXECUTION_PROVISIONAL` | Provisional instrument readiness |
| `INSTRUMENT_EXECUTION_BLOCKED` | Instrument blocked from execution |
| `INSTRUMENT_EXECUTION_FAILED` | Future runtime failure status |
| `INSTRUMENT_EXECUTION_NOT_RUN` | Instrument not yet run |
| `INSTRUMENT_EXECUTION_COMPLETED` | **Future runtime status only; this contract must not emit completed execution** |

---

## 13. Execution roles

| Role | Meaning |
|------|---------|
| `PRIMARY_EXECUTION_CANDIDATE` | Planned primary instrument promoted after gates pass |
| `SENSITIVITY_EXECUTION_CANDIDATE` | Planned sensitivity instrument |
| `DIAGNOSTIC_EXECUTION_CANDIDATE` | Planned diagnostic instrument only |
| `REFERENCE_ONLY_EXECUTION_CANDIDATE` | Reference-only; not for production claims |
| `BLOCKED_EXECUTION_CANDIDATE` | Must not be executed |
| `NOT_EVALUATED_EXECUTION_CANDIDATE` | Not yet evaluated for execution |

---

## 14. Instrument spec fields

Each `ExecutionInstrumentSpec` must include:

| Field | Purpose |
|-------|---------|
| `instrument_id` | Unique instrument identifier |
| `estimator_family` | Estimator family (e.g., DID, SCM, TBR Ridge) |
| `inference_family` | Inference family (e.g., Bootstrap, Placebo, BRB) |
| `execution_role` | Execution role within packet |
| `estimand_type` | Declared estimand type |
| `metric_name` | Outcome metric name |
| `unit_id_field` | Unit identifier column |
| `time_field` | Time column |
| `outcome_field` | Outcome column |
| `treatment_field` | Treatment indicator column |
| `cell_id_field` | Cell identifier column |
| `assignment_artifact_id` | Assignment artifact reference |
| `pre_period` | Pre-period window |
| `test_period` | Test-period window |
| `covariate_fields` | Covariate columns |
| `spend_fields` | Spend columns |
| `geo_fields` | Geo columns |
| `required_input_grain` | Required data grain |
| `uncertainty_semantics` | Explicit uncertainty semantics |
| `interval_type` | Interval type if present |
| `p_value_semantics` | P-value semantics if present |
| `diagnostic_requirements` | Required diagnostics (not executed here) |
| `sensitivity_requirements` | Required sensitivity checks (not executed here) |
| `governance_restrictions` | Governance caveats and restrictions |

---

## 15. Input data contract

`ExecutionInputDataContract` defines future execution data requirements:

| Field | Purpose |
|-------|---------|
| `panel_data_reference` | Reference to panel data artifact |
| `required_columns` | Required column set |
| `required_grain` | Required unit-time grain |
| `required_time_window` | Required time coverage |
| `required_geo_unit_coverage` | Required geo unit coverage |
| `required_treatment_assignment_join` | Treatment-assignment join requirement |
| `required_metric_availability` | Metric availability requirement |
| `required_covariate_availability` | Covariate availability requirement |
| `required_spend_availability` | Spend availability requirement |
| `missingness_policy` | Missingness handling policy |
| `duplicate_policy` | Duplicate handling policy |
| `outlier_policy` | Outlier handling policy |
| `data_version` | Data version identifier |
| `data_hash` | Content hash for provenance |

**Critical rule:** Execution must reference data artifacts and hashes. **No silent data substitution.**

---

## 16. Future output schemas

Future execution runtime emits typed artifacts per instrument. This contract defines schemas only; no values are computed here.

### Effect estimate report schema

| Field | Purpose |
|-------|---------|
| `effect_estimate_id` | Unique effect estimate identifier |
| `instrument_id` | Source instrument |
| `estimand` | Declared estimand |
| `metric_name` | Outcome metric |
| `effect_scale` | Explicit effect scale |
| `point_estimate` | Point estimate (future runtime only) |
| `baseline_reference` | Baseline reference |
| `relative_lift` | Relative lift if applicable |
| `absolute_lift` | Absolute lift if applicable |
| `unit_scope` | Unit scope |
| `population_scope` | Population scope |
| `time_window` | Time window |
| `cell_contrast` | Cell contrast |
| `sample_size_summary` | Sample size summary |
| `estimation_status` | Estimation status |
| `warnings` | Non-blocking warnings |

**Clarification:** These are future output fields only. This contract does not compute them.

### Uncertainty report schema

| Field | Purpose |
|-------|---------|
| `uncertainty_report_id` | Unique uncertainty report identifier |
| `instrument_id` | Source instrument |
| `uncertainty_semantics` | Must match planned instrument |
| `interval_type` | Interval type |
| `confidence_or_credible_level` | Confidence or credible level |
| `standard_error` | Standard error if applicable |
| `interval_lower` | Interval lower bound |
| `interval_upper` | Interval upper bound |
| `p_value` | P-value if applicable |
| `distribution_summary` | Distribution summary |
| `uncertainty_status` | Uncertainty status |
| `warnings` | Non-blocking warnings |

**Clarification:** Uncertainty semantics must match the planned instrument. Diagnostic-only uncertainty cannot authorize production claims.

### Inference diagnostic report schema

| Field | Purpose |
|-------|---------|
| `diagnostic_report_id` | Unique diagnostic report identifier |
| `instrument_id` | Source instrument |
| `diagnostic_type` | Diagnostic type |
| `diagnostic_status` | Diagnostic status |
| `diagnostic_value` | Diagnostic value (future runtime only) |
| `threshold` | Threshold if applicable |
| `interpretation` | Interpretation |
| `blocking_flag` | Whether diagnostic blocks downstream |
| `warnings` | Non-blocking warnings |

---

## 17. Execution trace/provenance

`ExecutionTrace` future fields:

| Field | Purpose |
|-------|---------|
| `execution_id` | Unique execution identifier |
| `instrument_id` | Source instrument |
| `readout_plan_artifact_id` | Readout plan artifact reference |
| `assignment_artifact_id` | Assignment artifact reference |
| `data_artifact_id` | Data artifact reference |
| `algorithm_version` | Algorithm version |
| `code_version` | Code version |
| `config_hash` | Configuration hash |
| `data_hash` | Input data hash |
| `input_hash` | Full input hash |
| `output_hash` | Output hash (future runtime only) |
| `runtime_environment` | Runtime environment descriptor |
| `execution_timestamp_policy` | Deterministic/provenance timestamp policy |

Deterministic/provenance policy is acceptable. Wall-clock timestamp is not required unless repo convention mandates it.

---

## 18. Readiness gates

Future gate order:

1. `readout_plan_gate`
2. `assignment_artifact_gate`
3. `estimator_inference_instrument_spec_gate`
4. `data_contract_gate`
5. `estimand_compatibility_gate`
6. `uncertainty_semantics_gate`
7. `diagnostics_prerequisite_gate`
8. `sensitivity_prerequisite_gate`
9. `governance_restriction_gate`
10. `provenance_trace_gate`
11. `execution_packet_gate`

**Rules:**

- If readout plan is blocked, execution readiness is blocked.
- If planned instrument is blocked/not evaluated, execution readiness is blocked.
- If assignment artifact is missing or failed, execution readiness is blocked.
- If required input data contract is missing, execution readiness is blocked.
- If estimand is missing or incompatible, execution readiness is blocked.
- If uncertainty semantics are missing or incompatible, execution readiness is blocked/provisional.
- If diagnostics prerequisites are missing, execution readiness is blocked/provisional depending on config.
- If sensitivity prerequisites are missing, execution readiness is blocked/provisional depending on config.
- If governance restrictions are unresolved, execution readiness is blocked/provisional.
- If provenance/trace config is missing, execution readiness is blocked.

---

## 19. Planned role treatment

- Primary planned candidates may become `PRIMARY_EXECUTION_CANDIDATE` only after execution readiness gates pass.
- Sensitivity planned candidates may become `SENSITIVITY_EXECUTION_CANDIDATE`.
- Diagnostic planned candidates may become `DIAGNOSTIC_EXECUTION_CANDIDATE` only.
- **Diagnostic-only instruments must not become primary production execution candidates.**
- Blocked instruments must not be executed.
- **This contract does not promote any candidate to completed execution.**

---

## 20. Instrument family treatment

Execution contracts must remain **instrument-level**, not broad-family-only.

Examples:

| Instrument | Notes |
|------------|-------|
| DID + Bootstrap | Primary candidate; bootstrap uncertainty semantics |
| SCM + Placebo | Diagnostic execution candidate |
| SCM + UnitJackknife | Diagnostic/restricted candidate |
| TBR Ridge + BRB | Restricted; governance caveats required |
| TBR Ridge + KFold | Diagnostic/sensitivity candidate |
| TBR Ridge + Placebo | Diagnostic candidate |
| AugSynth + Jackknife | Diagnostic/restricted; donor-support diagnostics |
| MatchedPair + RandomizationInference | Design-dependent |
| A/B + StandardInference | Blocked for geo-panel design |

Each instrument may have different input, uncertainty, diagnostic, and governance requirements.

---

## 21. Effect/uncertainty semantics treatment

- **Effect scale** must be explicit: absolute, relative lift, log-scale, ratio, incremental units, incremental revenue, or descriptive-only.
- **Uncertainty semantics** must be explicit: jackknife, placebo, bootstrap, conformal, model-based posterior, asymptotic SE, or descriptive-only.
- **P-value semantics** must be explicit if present.
- **Interval semantics** must be explicit if present.
- **No effect or uncertainty may be interpreted without its semantics.**

---

## 22. Failure packet semantics

`ExecutionFailurePacket` fields:

| Field | Purpose |
|-------|---------|
| `failure_id` | Unique failure identifier |
| `execution_id` | Execution identifier |
| `instrument_id` | Source instrument |
| `execution_status` | Resulting execution status |
| `blocking_gates` | Gates that blocked execution |
| `missing_inputs` | Missing input identifiers |
| `data_contract_failures` | Data contract failure details |
| `assignment_artifact_failures` | Assignment artifact failure details |
| `estimand_failures` | Estimand failure details |
| `uncertainty_semantics_failures` | Uncertainty semantics failures |
| `diagnostic_prerequisite_failures` | Diagnostic prerequisite failures |
| `sensitivity_prerequisite_failures` | Sensitivity prerequisite failures |
| `governance_failures` | Governance failure details |
| `suggested_retry_categories` | Diagnostic retry suggestions |
| `claim_boundary_report` | Authorization boundary flags |

**Retry categories (diagnostic only; not implemented):**

- `FIX_INPUT_DATA_CONTRACT`
- `FIX_ASSIGNMENT_ARTIFACT`
- `FIX_ESTIMAND_SPEC`
- `FIX_INSTRUMENT_SPEC`
- `FIX_UNCERTAINTY_SEMANTICS`
- `ADD_REQUIRED_DIAGNOSTICS`
- `ADD_REQUIRED_SENSITIVITY_CHECKS`
- `CHANGE_READOUT_PLAN`
- `BLOCK_INSTRUMENT`
- `BLOCK_DESIGN`

---

## 23. Examples

### Example 1: DID + Bootstrap primary execution candidate

Planned primary candidate with complete data contract and bootstrap uncertainty semantics. After all gates pass, status is `EXECUTION_READY_FOR_RUNTIME` with role `PRIMARY_EXECUTION_CANDIDATE`. Effect scale: incremental units. Uncertainty semantics: bootstrap.

### Example 2: SCM + Placebo diagnostic only

Diagnostic execution candidate only. Cannot support production lift claim. Role: `DIAGNOSTIC_EXECUTION_CANDIDATE`. Uncertainty semantics: placebo (diagnostic-only).

### Example 3: TBR Ridge + BRB restricted

Restricted execution candidate requiring governance caveats. Status may be `EXECUTION_READY_WITH_WARNINGS` or `EXECUTION_PROVISIONAL` depending on config. Governance restrictions must be preserved.

### Example 4: AugSynth + Jackknife diagnostic/restricted

Requires donor-support diagnostics. Role: `DIAGNOSTIC_EXECUTION_CANDIDATE` or provisional primary only with caveats. Cannot authorize production without diagnostics.

### Example 5: A/B + StandardInference blocked for geo-panel

Blocked for geo-panel design. Role: `BLOCKED_EXECUTION_CANDIDATE`. Status: `EXECUTION_BLOCKED_BY_INSTRUMENT_SPEC` or `EXECUTION_BLOCKED_BY_GOVERNANCE`.

### Example 6: Missing assignment artifact

Planned instrument missing `assignment_artifact_id` blocks execution readiness. Status: `EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT`.

### Example 7: Missing required outcome column

Data contract missing `outcome_field` column blocks execution readiness. Status: `EXECUTION_BLOCKED_BY_DATA_CONTRACT` or `EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA`.

### Example 8: Missing uncertainty semantics

Missing `uncertainty_semantics` blocks or provisionalizes execution readiness. Status: `EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS` or `EXECUTION_PROVISIONAL`.

### Example 9: Dosage estimand requires compatible spec

Dosage estimand requires compatible execution spec with explicit effect scale and estimand reference. Incompatible spec blocks at `estimand_compatibility_gate`.

### Example 10: Budget reallocation blocks simple ROI

Budget reallocation estimand blocks simple ROI interpretation without ROI governance. Governance restriction preserved; `roi_claim_authorized` remains false.

---

## 24. Claim boundaries

Always false in this contract:

| Flag | Value |
|------|-------|
| `estimator_inference_execution_runtime_implemented` | `false` |
| `instrument_execution_completed` | `false` |
| `estimator_execution_implemented` | `false` |
| `inference_execution_implemented` | `false` |
| `effect_estimate_computed` | `false` |
| `lift_computed` | `false` |
| `roi_computed` | `false` |
| `p_value_computed` | `false` |
| `confidence_interval_computed` | `false` |
| `uncertainty_computed` | `false` |
| `diagnostic_check_executed` | `false` |
| `sensitivity_check_executed` | `false` |
| `causal_claim_authorized` | `false` |
| `incremental_lift_claim_authorized` | `false` |
| `roi_claim_authorized` | `false` |
| `production_readout_authorized` | `false` |
| `production_authorization_granted` | `false` |
| `mmm_runtime_calls_implemented` | `false` |
| `mmm_calibration_authorized` | `false` |
| `llm_decisioning_authorized` | `false` |

Allowed contract-level positives:

| Flag | Value |
|------|-------|
| `estimator_inference_execution_contract_defined` | `true` |
| `execution_input_contract_defined` | `true` |
| `instrument_execution_request_contract_defined` | `true` |
| `instrument_execution_result_contract_defined` | `true` |
| `effect_estimate_report_contract_defined` | `true` |
| `uncertainty_report_contract_defined` | `true` |
| `inference_diagnostic_report_contract_defined` | `true` |
| `execution_trace_contract_defined` | `true` |
| `execution_failure_packet_contract_defined` | `true` |
| `claim_boundaries_defined` | `true` |

---

## 25. Future implementation acceptance criteria

Future `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001` must:

- consume readout plan artifact
- consume planned instrument candidates
- consume assignment artifacts
- consume execution data contract
- require explicit estimand
- require explicit uncertainty semantics
- require provenance and data hashes
- block blocked/not-evaluated instruments
- keep diagnostic-only instruments diagnostic-only
- emit typed execution result per instrument
- emit effect estimate report only after execution
- emit uncertainty report only after inference execution
- emit diagnostic/inference reports only after checks run
- emit failure packet on blocked/failed execution
- not authorize causal claims
- not authorize production

---

## 26. Future tests

Documented for `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001`:

- blocked readout plan blocks execution readiness
- blocked instrument blocks execution readiness
- missing assignment artifact blocks
- missing input data contract blocks
- missing required outcome column blocks
- missing treatment assignment join blocks
- missing estimand blocks
- incompatible estimand blocks
- missing uncertainty semantics blocks/provisionalizes
- diagnostic-only instrument cannot be primary production execution
- restricted instrument requires governance caveats
- DID+Bootstrap execution packet fields
- SCM+Placebo diagnostic packet fields
- TBR Ridge + BRB restricted packet fields
- failure packet emitted on missing data contract
- execution trace requires hashes/provenance
- no estimator execution in contract
- no inference execution in contract
- no effect/lift/ROI/p-values/CIs
- no claim authorization
- no production authorization
- no fixture-specific branching

---

## 27. Roadmap placement

Sits after `READOUT_PLAN_RUNTIME_001` and before `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001` in the profiler/diagnostics → assignment → governance → readout plan → **execution contract** sequencing lane.

Alternative parallel lane: `READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001` for diagnostics/sensitivity execution contract before or alongside execution runtime.

---

## 28. Recommended next artifact

**Primary:** `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001`

**Alternative:** `READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001`

Do not implement either in this artifact.

---

## 29. Validation

- `python -m json.tool docs/track_d/archives/ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001_summary.json`
- `python -m pytest tests/validation/test_estimator_inference_execution_contract_001.py -q`
- `git diff --check`
- Safety grep: no forbidden `*_true` execution/authorization flags in report or summary

---

## 30. Metadata harness

| File | Role |
|------|------|
| `panel_exp/validation/estimator_inference_execution_contract_001.py` | Metadata-only contract harness |
| `tests/validation/test_estimator_inference_execution_contract_001.py` | Contract validation tests |

The harness defines contract constants, validates authorization boundaries, and writes summary JSON. It does not execute estimators, compute inference, or authorize claims.
