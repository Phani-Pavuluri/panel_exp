# GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001

## 1. Metadata

| Field | Value |
|---|---|
| Artifact ID | `GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001` |
| Type | Docs/tests-only cross-repository compatibility contract |
| Source commit | `ce0168fa6a77c0cb6adf232e3844813529bbedba` |
| Reconciliation dependency | Not present on `main`; proceeding from the alignment audit recommendation |
| Status | `completed` |
| Runtime code changed | `false` |
| MIP repository modified | `false` |

## 2. Purpose

This contract defines the versioned envelope that future GeoX outputs must use
before MIP can safely resolve, explain, TrustReport-route, or dry-run experiment
artifacts. It specifies identity, provenance, lifecycle, authorization, blocked
reasons, and downstream eligibility without implementing a runtime adapter or
authorizing any production surface.

## 3. Prior-artifact dependencies

The GeoX–MIP alignment audit exists and selected this artifact as the next
cross-repository milestone. The P0 state-reconciliation artifact is not present
on `main`; the audit therefore proceeds from the alignment audit alone. Its
decision remains `GEOX_MIP_ALIGNMENT_BLOCKED_BY_MULTIPLE_GAPS` and all
production authorization flags remain false.

## 4. Current GeoX artifact inventory

GeoX currently has typed design/feasibility diagnostics, assignment candidates
and reproducibility manifests, governed randomization artifacts, run/execution
packets, readout plans and diagnostics, typed failure packets, native
`ExperimentEvidence`, post-test spend evidence, and trusted-readout spend
handoffs. These surfaces are bounded, diagnostic, candidate-gated, or
restricted; they are not a complete durable experiment service.

## 5. Current MIP compatibility observations (read-only)

The sibling MIP repository contains experiment-design intake, GeoX input/source
inspection and fixture/materialization contracts, fixture/upload post-test-spend
runtime calls, result ingestion, trust routing, `ExperimentEvidence`,
`CalibrationSignal`, and `TrustReport` contracts. Its GeoX runtime call is
fixture/materialized-upload bounded, and its general GeoX adapter remains a
placeholder/contract surface. The sibling worktree was inspected read-only and
was not modified.

## 6. Envelope design principles

Every artifact is immutable by identity, content-addressable by `schema_hash`
and input/output fingerprints, explicit about source and lifecycle, and safe to
transport when blocked. An envelope may describe a candidate or diagnostic
without becoming an authorization. Unknown versions fail closed. MIP consumes
facts and states; it never calculates causal quantities or chooses markets.

## 7. Versioned envelope overview

Canonical envelope shape (required for every artifact kind):

| Field | Requirement |
|---|---|
| `envelope_version` | Semantic envelope version; incompatible changes require a new major version |
| `artifact_kind` | One of the registered kinds below |
| `artifact_id` / `artifact_uri` | Stable identity and registry address; URI is not a filesystem promise |
| `source_system` / `source_repo` / `source_commit` | Producer and immutable source provenance |
| `created_at` | UTC creation timestamp |
| `run_id` / `experiment_id` / `request_id` | Stable lifecycle and correlation identifiers |
| `input_data_fingerprint` | Content identity for all analytical inputs |
| `method_family` / `instrument_id` | Exact method/instrument identity, never family-only promotion |
| `estimand` / `kpi` | Declared target and metric semantics |
| `geo_scope` / `time_window` / `assignment_scope` | Population, period, and cell/assignment scope |
| `diagnostic_status` / `method_readiness_status` | Diagnostic and method maturity state |
| `release_gate_status` / `authorization_status` | Explicit governance state; current production state is non-authorized |
| `blocked_reasons` / `warnings` | Structured failures and caveats |
| `upstream_artifacts` / `provenance` | Lineage and evidence references |
| `downstream_eligibility` / `mip_consumption_status` | Allowed consumer behavior |
| `schema_hash` | Hash of the canonical schema/version |

## 8. Request envelope requirements

`geox_request` must contain a request ID, experiment requirements, input
fingerprints, KPI/estimand, geo/time scope, assignment intent, requested
diagnostics, exact method/instrument constraints, caller, and authorization
context. A request can ask GeoX to evaluate an assignment or readout; it cannot
carry a market choice as an authoritative decision. MIP-originated requests are
`answerability_context_only` until GeoX returns typed evidence.

## 9. Result envelope requirements

`geox_result` binds the request ID and run ID to result artifacts, statuses,
diagnostics, warnings, blocked reasons, method/readiness state, and lineage. A
numeric estimate is labeled with its estimand and uncertainty semantics and is
never promoted merely because it is present.

## 10. Assignment candidate envelope requirements

`assignment_candidate` records candidate pools, constraints checked, candidate
allocation, reproducibility inputs, and assignment scope. It must state that
candidate generation is not treatment/control authorization and that the LLM or
MIP did not choose markets.

## 11. Assignment manifest envelope requirements

`assignment_manifest` records the governed randomization algorithm, seed or seed
reference, immutable allocation hash, treatment/control/cell labels, panel
fingerprint, constraint trace, and QA status. It is consumable for diagnostic
integrity checks only while `assignment_authorized=false`.

## 12. Run manifest lifecycle requirements

`run_manifest` must support `requested`, `validated`, `queued`, `running`,
`completed`, `blocked`, `failed`, `cancelled`, and `superseded` states with
timestamps, actor, retry/idempotency key, input/output artifact references, and
failure linkage. The current GeoX package has typed fields and packets but not a
durable job, retry, scheduler, retention, or tenant-isolation service.

## 13. Readout packet envelope requirements

`readout_packet` binds post-period data, assignment manifest, estimator,
inference instrument, estimand, diagnostics, uncertainty semantics, claim
authorization, and release state. It may be a diagnostic or restricted packet;
it cannot imply a governed causal readout until the release gate authorizes it.

## 14. Failure packet envelope requirements

`failure_packet` contains a stable failure ID, failed artifact/run/request,
typed reason code, severity, stage, evidence references, safe retry/remediation
category, and blocked downstream uses. Hidden failures must block consumption;
MIP must explain the packet rather than reconstructing an estimate.

## 15. Artifact URI and registry reference requirements

`artifact_uri` is an opaque stable registry reference paired with
`artifact_id`, `schema_hash`, source commit, content fingerprint, creation time,
retention class, and access policy. A URI must not be treated as proof of
authorization or durable availability. Registry resolution must fail closed on
unknown schema, revoked artifact, expired retention, hash mismatch, or tenant
scope mismatch.

## 16. Release and authorization state propagation

`authorization_status` values are `not_authorized`, `diagnostic_only`,
`candidate_gated`, `release_gate_required`, `blocked`, and
`authorized_future_only`. Current production-facing artifacts must remain
non-authorized. `release_gate_status` and method readiness must travel with
every downstream reference; MIP cannot upgrade either state.

## 17. Blocked-reason and diagnostic propagation

`blocked_reasons` are stable, machine-readable codes with source, severity,
scope, and remediation. Diagnostics must distinguish structural validity,
assignment integrity, SRM/balance, statistical promotion, uncertainty, method
suitability, and release-gate failures. A diagnostic p-value, point estimate,
or passing fixture is not a production causal claim.

## 18. MIP ExperimentEvidence compatibility mapping

`experiment_evidence_candidate` is a compatibility candidate only, not an
authorized export. Mapping requires experiment/run/assignment identity,
estimand/KPI/geo/time scope, scalar estimate semantics, uncertainty/interval
semantics, diagnostic summaries, freshness/quality, artifact URI, method and
inference identity, authorization state, and blocked/warning lineage. Native
GeoX evidence and MIP `ExperimentEvidence` currently differ in these semantics;
the future adapter must map or block explicitly and must not invent fields.

## 19. CalibrationSignal eligibility/export boundary

`calibration_signal_candidate` is a compatibility candidate only. It requires a
governed eligible experiment evidence artifact, compatible KPI/estimand, valid
uncertainty, freshness, method promotion, release authorization, and explicit
MMM target mapping. No current artifact meets this export boundary, so
`calibration_signal_export_authorized=false`.

## 20. TrustReport-readiness boundary

TrustReport readiness may consume structured diagnostics, caveats, blockers,
and candidate references. It must redact unauthorized causal, ROI, significance,
interval, production, and recommendation surfaces. `trust_report_candidate`
does not mean a production TrustReport is authorized.

## 21. Non-production dry-run requirements

A future dry run must use fixtures or explicitly materialized uploads, a pinned
envelope/schema hash, deterministic request/result IDs, no live production
loader, no market selection by MIP/LLM, no estimator or inference recomputation
in MIP, no CalibrationSignal creation, no production registry writes, and an
assertion that all authorization flags remain false. It must compare schemas,
lineage, blocked reasons, and redaction behavior end to end.

## 22. Compatibility matrix

The matrix records **Current MIP compatibility**, **Missing/next work**,
**Allowed use now**, and **Blocked use** for each artifact. The
**MIP-compatible ExperimentEvidence** and **CalibrationSignal** rows are
candidate concepts only.

| GeoX artifact | Current MIP compatibility | Missing/next work | Allowed use now | Blocked use |
|---|---|---|---|---|
| assignment candidate | Partial envelope concepts | Stable candidate schema and provenance | Explain/diagnostic context | Market choice/assignment |
| assignment manifest | Partial typed handoff | Durable registry and authorization state | Integrity context | Authorized treatment assignment |
| governed randomization output | Partial | Envelope and persistence mapping | Diagnostic context | Causal inference |
| run manifest | Partial | Durable lifecycle/idempotency/retry | Execution context | Scheduled production execution |
| readout packet | Partial | Native-to-MIP mapping and release fields | Redacted review | Governed causal readout |
| failure packet | Partial | Cross-repo code registry | Explain blockers/retry | Silent recovery or bypass |
| post-test spend evidence | Fixture/upload path | Production data boundary and envelope | Diagnostic spend readiness | ROI/ROAS/calibration claim |
| trusted readout spend handoff | Fixture/upload path | Durable artifact reference | Explain readiness | TrustReport approval |
| native GeoX ExperimentEvidence | Native GeoX only | MIP schema mapping | Candidate inspection | MIP evidence registration |
| future MIP ExperimentEvidence candidate | Not yet mapped | Compatibility adapter and gate | None until mapping | Production evidence export |
| future CalibrationSignal candidate | Not eligible/exported | Eligibility, mapping, authorization | None | MMM calibration |

## 23. Status vocabularies

`mip_consumption_status` values are `not_consumable`,
`diagnostic_context_only`, `answerability_context_only`,
`trust_report_candidate`, `experiment_evidence_candidate`,
`calibration_signal_candidate`, and `blocked`. `downstream_eligibility` values
are `none`, `explain_only`, `diagnostic_summary`,
`trust_report_candidate_after_gate`, `experiment_evidence_after_mapping`, and
`calibration_signal_after_mapping_and_authorization`. Current artifacts must
not be marked production-consumable.

## 24. Explicit non-goals and blocked capabilities

This contract does not implement runtime code, change estimator/model behavior,
authorize inference, assignment, causal readout, CalibrationSignal, or MIP
ExperimentEvidence; create a selector/router, production adapter, or agent; or
modify the MIP repository. The following remain false:

```text
runtime_code_changed = false
production_inference_authorized = false
assignment_authorized = false
causal_readout_authorized = false
calibration_signal_export_authorized = false
mip_experiment_evidence_export_authorized = false
selector_router_runtime_authorized = false
multicell_production_claim_authorized = false
agent_work_authorized = false
mip_repository_modified = false
```

## 25. Future implementation sequence

1. Freeze and review this envelope contract and schema hash.
2. Define a package-side GeoX envelope runtime contract without authorization.
3. Define MIP resolver/registry mapping and failure-code compatibility.
4. Execute a fixture-only cross-repository dry run.
5. Reconcile durable persistence, release gates, multicell evidence, and method
   promotion before considering any production integration.

## 26. Validation and final verdict

The focused docs test verifies this contract, summary flags, artifact kinds,
required fields, compatibility keywords, and the alignment dependency. JSON and
diff validation are required before commit. The final verdict is
`geox_mip_artifact_envelope_compatibility_defined_no_runtime_no_authorization`.

Decision: `PROCEED_TO_NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_PLAN`

Recommended next artifact:
`NON_PRODUCTION_GEOX_MIP_ARTIFACT_ENVELOPE_DRY_RUN_PLAN_001`.
