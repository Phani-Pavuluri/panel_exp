# NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_PLAN_001

## 1. Metadata

| Field | Value |
|---|---|
| Artifact ID | `NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_PLAN_001` |
| Type | Docs/tests-only fixture dry-run plan |
| Base commit | `19e4027` |
| Status | `completed` |
| Runtime code changed | `false` |
| MIP repository modified | `false` |

## 2. Purpose

Define a future fixture-only rehearsal proving:

```text
GeoX fixture artifact
→ governed envelope candidate
→ compatibility validation
→ expected MIP consumption status
→ blocked/diagnostic-only result
→ no production authorization
```

This plan does not implement the envelope runtime or a MIP adapter.

## 3. Prior-artifact dependencies

The alignment audit and governed artifact-envelope compatibility contract are
present on `main`. The compatibility contract selected this plan. Its envelope
fields, status vocabularies, and authorization boundaries are the source of
truth for the later dry-run implementation.

The dependencies are `GEOX_MIP_PRODUCTION_ALIGNMENT_READINESS_AUDIT_001` and
`GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001`.

## 4. Dry-run principle and fixture-only input scope

Use deterministic synthetic or repository fixture inputs only. Every fixture is
content-addressed, pinned to a source commit, and marked non-production. No
warehouse/API loader, live credential, production registry write, market choice,
estimator recomputation in MIP, or downstream recommendation is permitted.

Required fields for every fixture:

`fixture_id`, `artifact_kind`, `artifact_id`, `run_id`, `experiment_id`,
`source_commit`, `method_family`, `instrument_id`, `estimand`, `kpi`,
`geo_scope`, `time_window`, `authorization_status`,
`mip_consumption_status`, `blocked_reasons`, `warnings`, and
`expected_validation_status`.

## 5. Artifact kinds included

The plan covers `geox_request`, `geox_result`, `assignment_candidate`,
`assignment_manifest`, `run_manifest`, `readout_packet`, `failure_packet`,
`post_test_spend_evidence`, `trusted_readout_spend_handoff`,
`experiment_evidence_candidate`, and `calibration_signal_candidate`.

## 6. Envelope-field coverage expectations

Each fixture envelope must carry `envelope_version`, `artifact_kind`,
`artifact_id`, `artifact_uri`, `source_system`, `source_repo`, `source_commit`,
`created_at`, `run_id`, `experiment_id`, `request_id`,
`input_data_fingerprint`, `method_family`, `instrument_id`, `estimand`, `kpi`,
`geo_scope`, `time_window`, `assignment_scope`, `diagnostic_status`,
`method_readiness_status`, `release_gate_status`, `authorization_status`,
`blocked_reasons`, `warnings`, `upstream_artifacts`, `downstream_eligibility`,
`mip_consumption_status`, `provenance`, and `schema_hash`.

Fixture-only URIs may use an explicit `fixture://` scheme but must still carry
an artifact ID, content fingerprint, and schema hash.

## 7. Compatibility validation checks

The later implementation must check:

- required envelope fields are present and non-empty;
- artifact kind is registered and allowed;
- authorization flags are false;
- blocked reasons and warnings are preserved exactly;
- release gate status is present;
- artifact URI is present or explicitly marked fixture-only;
- MIP consumption status is in the allowed vocabulary;
- CalibrationSignal and ExperimentEvidence candidates are blocked;
- assignment candidates and readout packets are not authorized;
- failure packets are not converted to recommendations;
- summaries contain no production claim;
- no `DecisionSurface` or `RecommendationContract` eligibility is emitted;
- serialization is deterministic and schema-hash stable.

## 8. Expected MIP consumption statuses

Allowed statuses are `not_consumable`, `diagnostic_context_only`,
`answerability_context_only`, `trust_report_candidate`,
`experiment_evidence_candidate`, `calibration_signal_candidate`, and
`blocked`. The dry run may use diagnostic or answerability context only. No
fixture is production-consumable.

## 9. Expected blocked reasons and diagnostic-only answerability

Expected reason codes include `authorization_missing`,
`release_gate_required`, `assignment_not_authorized`,
`causal_readout_not_authorized`, `evidence_mapping_missing`,
`calibration_mapping_missing`, `method_not_production_safe`,
`multicell_dependence_unresolved`, `fixture_only_input`, and
`production_registry_write_blocked`. MIP may explain readiness, caveats, and
next steps, but may not turn diagnostics into causal claims or recommendations.

## 10. Required dry-run cases

### Case A — diagnostic-only assignment candidate

Envelope an explicit-pool candidate and inspect it as diagnostic context.
Expected: `mip_consumption_status=diagnostic_context_only`,
`assignment_authorized=false`, `production_inference_authorized=false`, and no
treatment/control authorization claim.

### Case B — blocked readout packet

Envelope a readout-like packet with missing release/claim authorization.
Expected: `mip_consumption_status=blocked`,
`causal_readout_authorized=false`, and a reason containing missing
authorization/release gate.

### Case C — failure packet propagation

Carry a typed GeoX failure to MIP without recommendation conversion. Expected:
`mip_consumption_status=answerability_context_only`, original blocked/warning
reasons preserved, and no recommendation generated.

### Case D — post-test spend evidence diagnostic handoff

Carry bounded post-test spend evidence. Expected:
`mip_consumption_status=diagnostic_context_only`,
`calibration_signal_export_authorized=false`, and no MMM calibration export.

### Case E — CalibrationSignal candidate blocked

Represent a candidate concept without eligibility/mapping/authorization.
Expected: `mip_consumption_status=blocked`,
`calibration_signal_export_authorized=false`, and a mapping/authorization
missing reason.

### Case F — ExperimentEvidence candidate blocked

Represent a MIP evidence candidate without native-to-MIP mapping or release.
Expected: `mip_consumption_status=blocked`,
`mip_experiment_evidence_export_authorized=false`, and an evidence
mapping/authorization missing reason.

## 11. Expected success and failure cases

Success means deterministic envelope serialization, complete identity and
provenance, allowed kind, preserved blockers, and the expected diagnostic or
answerability status. Failure means missing required fields, unknown kind,
hash mismatch, changed blocked reasons, authorization drift, absent release
state, non-deterministic bytes, or any attempt to create a recommendation or
production artifact; each must produce a typed blocked result.

## 12. Summary artifact expectations

The future dry-run summary must identify fixture IDs, envelope/schema hashes,
case outcomes, expected versus actual MIP consumption statuses, blocked reasons,
warnings, authorization flags, source commits, and deterministic validation
results. It must not contain a causal estimate claim, DecisionSurface,
RecommendationContract, CalibrationSignal, or MIP ExperimentEvidence export.

## 13. Test strategy

Use focused docs/schema tests plus fixture contract tests for all six cases.
Test deterministic serialization twice, required-field and kind validation,
blocked-reason preservation, false authorization flags, status vocabulary,
fixture URI semantics, candidate blocking, failure propagation, and absence of
recommendation artifacts. Do not run or repair unrelated full-suite failures.

## 14. Later implementation sequence

1. Define package-side envelope dataclasses/types and schema hash rules.
2. Add fixture builders for Cases A–F without production imports or writes.
3. Add compatibility validator and deterministic summary serializer.
4. Run a read-only MIP-style consumer simulation against fixtures.
5. Review blocked outputs and lineage; do not add production authorization.
6. Reassess only after durable registry, release, multicell, and method gates are
   separately evidenced.

## 15. Explicit non-goals and blocked capabilities

No runtime code, production MIP adapter, real ExperimentEvidence,
CalibrationSignal, production causal inference, treatment/control assignment,
causal readout, TrustReport production assembly, DecisionSurface,
RecommendationContract, LLM/provider/orchestration, agents, estimator/model
changes, or unrelated lint/test/Docker/archive/generated-result remediation.

The following remain false:

```text
runtime_code_changed = false
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

## 16. Merge/checkpoint criteria

The later runtime-contract/dry-run task may merge only when all six cases are
deterministic, required fields validate, blocked reasons round-trip, all
authorization flags remain false, no recommendation or production artifact is
created, MIP sibling files remain unchanged, and the fixture summary records
expected statuses and hashes.

## 17. Validation and final verdict

The focused docs test validates this plan, summary flags, case labels, fixture
fields, validation checks, and roadmap/registry references. The final verdict is
`non_production_geox_mip_artifact_envelope_dry_run_planned_no_runtime_no_authorization`.

Decision: `PROCEED_TO_GEOX_ARTIFACT_ENVELOPE_RUNTIME_CONTRACT`

Recommended next artifact: `GEOX_ARTIFACT_ENVELOPE_RUNTIME_CONTRACT_001`.
