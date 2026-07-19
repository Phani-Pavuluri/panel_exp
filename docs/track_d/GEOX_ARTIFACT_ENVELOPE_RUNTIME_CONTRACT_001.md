# GEOX_ARTIFACT_ENVELOPE_RUNTIME_CONTRACT_001

## 1. Metadata

| Field | Value |
|---|---|
| Artifact ID | `GEOX_ARTIFACT_ENVELOPE_RUNTIME_CONTRACT_001` |
| Type | Package-side typed runtime contract |
| Base commit | `d736587` |
| Status | `completed` |
| Runtime contract added | `true` |
| Dry-run runtime added | `false` |
| MIP repository modified | `false` |

## 2. Purpose

Add immutable GeoX package-side envelope types, status enums, validation, and
deterministic JSON-safe serialization. This is the contract layer before the
fixture-only dry-run runtime; it is not production integration.

## 3. Prior-artifact dependencies

The implementation follows `GEOX_MIP_PRODUCTION_ALIGNMENT_READINESS_AUDIT_001`,
`GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001`, and
`NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_PLAN_001`.

## 4. Public API

`panel_exp.contracts.geox_mip_artifact_envelope` provides:

- `GeoXMIPArtifactKind`
- `GeoXMIPAuthorizationStatus`
- `GeoXMIPConsumptionStatus`
- `GeoXMIPDownstreamEligibility`
- frozen `GeoXMIPArtifactEnvelope`
- `build_geox_mip_artifact_envelope`
- `validate_geox_mip_artifact_envelope`
- `serialize_geox_mip_artifact_envelope`

The package `panel_exp.contracts` exports the same public symbols.

## 5. Supported artifact kinds and statuses

Supported kinds are `geox_request`, `geox_result`, `assignment_candidate`,
`assignment_manifest`, `run_manifest`, `readout_packet`, `failure_packet`,
`post_test_spend_evidence`, `trusted_readout_spend_handoff`,
`experiment_evidence_candidate`, and `calibration_signal_candidate`.

Authorization statuses are `not_authorized`, `diagnostic_only`,
`candidate_gated`, `release_gate_required`, `blocked`, and
`authorized_future_only`. Consumption statuses are `not_consumable`,
`diagnostic_context_only`, `answerability_context_only`,
`trust_report_candidate`, `experiment_evidence_candidate`,
`calibration_signal_candidate`, and `blocked`. Downstream eligibility is
restricted to the compatibility vocabulary and cannot imply production use.

## 6. Required envelope fields

The frozen envelope includes `envelope_version`, `artifact_kind`, `artifact_id`,
`artifact_uri`, `source_system`, `source_repo`, `source_commit`, `created_at`,
`run_id`, `experiment_id`, `request_id`, `input_data_fingerprint`,
`method_family`, `instrument_id`, `estimand`, `kpi`, `geo_scope`, `time_window`,
`assignment_scope`, `diagnostic_status`, `method_readiness_status`,
`release_gate_status`, `authorization_status`, `blocked_reasons`, `warnings`,
`upstream_artifacts`, `downstream_eligibility`, `mip_consumption_status`,
`provenance`, and `schema_hash`.

## 7. Validation semantics

Validation rejects empty required strings, invalid enums, blocked envelopes with
no blocked reasons, missing release gate/schema hash, candidate kinds that are
not blocked, assignment candidates that imply authorization, readout packets
that imply causal authorization, production downstream eligibility, and MIP
consumption statuses that imply evidence/calibration export. The validator
returns `(bool, tuple[str, ...])`; serialization raises `ValueError` for an
invalid envelope.

## 8. Serialization semantics

Enums serialize to strings, tuples to lists, mappings use sorted keys, and all
output is JSON-safe. Datetimes are represented by caller-supplied strings. The
serialized dictionary is stable under `json.dumps(..., sort_keys=True)` and
contains no object representations.

## 9. Safety boundaries

The contract blocks experiment-evidence and calibration-signal candidate kinds,
assignment authorization, causal readout authorization, production downstream
eligibility, and MIP production consumption. It does not create MIP artifacts or
calculate any causal quantity.

```text
production_inference_authorized = false
assignment_authorized = false
causal_readout_authorized = false
calibration_signal_export_authorized = false
mip_experiment_evidence_export_authorized = false
trust_report_production_assembly_authorized = false
decision_surface_authorized = false
recommendation_contract_authorized = false
llm_decisioning_authorized = false
budget_optimization_authorized = false
selector_router_runtime_authorized = false
multicell_production_claim_authorized = false
agent_work_authorized = false
mip_repository_modified = false
```

## 10. Test coverage

Focused tests cover valid diagnostic assignment, blocked readout, failure
answerability serialization, post-test spend non-calibration behavior, blocked
CalibrationSignal and ExperimentEvidence candidates, deterministic serialization,
empty required fields, invalid authorization/consumption combinations, and
production eligibility blocking.

## 11. Explicit non-goals and blocked capabilities

This change does not implement fixture dry-run runtime, a MIP adapter, real MIP
ExperimentEvidence, CalibrationSignal, production inference, assignment,
causal readout, TrustReport assembly, DecisionSurface,
RecommendationContract, LLM/provider/orchestration, agents, or estimator/model
behavior. Unrelated lint/test/Docker/archive debt is out of scope.

## 12. Validation and final verdict

`git diff --check`, JSON validation, and the focused contract tests are required
before commit. The final verdict is
`geox_artifact_envelope_runtime_contract_added_no_dry_run_no_authorization`.

Decision: `PROCEED_TO_NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_RUNTIME`

Recommended next artifact:
`NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_RUNTIME_001`.
