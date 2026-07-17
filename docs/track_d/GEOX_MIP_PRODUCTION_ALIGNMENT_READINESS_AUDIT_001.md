# GEOX_MIP_PRODUCTION_ALIGNMENT_READINESS_AUDIT_001

**Audit date:** 2026-07-17
**Audited commit:** `7e1519e00eb5a1045624afd180dfb206ece9d31e` (`origin/main`)
**Type:** docs and committed-runtime audit; no implementation or promotion
**Verdict:** `GEOX_MIP_ALIGNMENT_BLOCKED_BY_MULTIPLE_GAPS`

## Executive conclusion

GeoX is a governed experimentation-engine foundation, not a production
experimentation service. It can deterministically inspect data and feasibility,
plan readouts, create explicit-pool assignment candidates, enforce method and
claim boundaries, emit typed failure packets, execute a narrowly governed DID
point-estimate path, and construct post-test spend evidence. These capabilities
do not authorize assignment, formal power/MDE, production p-values or intervals,
causal lift, a causal readout, MMM calibration, an LLM decision, scheduling, or
an API.

MIP has product-side intake, fixture materialization, result-ingestion, and trust
routing contracts. Its general GeoX adapter is a placeholder, and its executable
package call is constrained to fixture or materialized-upload post-test spend
evidence. It does not invoke a complete design-to-readout experiment lifecycle.

The intended ownership boundary is correct: GeoX owns deterministic causal-engine
outputs; MIP owns conversation, orchestration, artifact governance, explanation,
TrustReport assembly, and UI. It is incomplete in both runtime and contract form.
A static sample demo may show bounded fixtures and diagnostic artifacts. A
real-team pilot and production experiment-design workflow are not ready.

## Evidence discipline and audit state

Only the clean worktree at the audited commit was used. The dirty primary
checkout's archive changes were not evidence. This audit treats implemented,
tested, validated, promoted, candidate-gated, and authorized as distinct states.
A plan, fixture, metadata harness, diagnostic p-value, or point estimate is not
production authorization.

The latest completed alignment-facing milestone is
`METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001`
(commit `42f4484` in audited ancestry), with verdict
`package_side_handoff_runtime_stable_for_mip_integration_planning_not_runtime_integration`
and `ready_for_mip_runtime_integration: false`.

The authoritative investigation registry has no `IN_PROGRESS` item. Unresolved
work is deferred/planned: shared-control dependence, multicell multiplicity,
multi-treated placebo, P0 governed-runtime hardening, Bayesian TBR replay,
TBRRidge remediation, and a TROP scout. The multicell/multi-treated items block
production, TrustReport, and CalibrationSignal roles.

## Experiment workflow readiness

| Capability | Status | Runtime / typed output | Restriction and next work |
|---|---|---|---|
| Data intake / panel profiling | `restricted` | `profile_geo_kpi_spend_data`; profiler reports | Profile only; needs governed materialized input boundary |
| Panel validation | `restricted` | assignment-panel integrity and observed-panel diagnostics | Can block execution; needs observed-diagnostic closeout |
| KPI / estimand definition | `restricted` | design/estimand and readout-plan contracts | Captures scope, not approved production estimand |
| Pre-period diagnostics | `restricted` | DID coverage/pre-period diagnostic; diagnostic packets | Structural only, not inference |
| Matchability | `restricted` | geo-market and assignment-feasibility reports | No governed matching optimization |
| Power / MDE | `diagnostic_only` | `evaluate_power_mde_diagnostics` | Descriptive sensitivity; no formal power/MDE authorization |
| Design feasibility | `restricted` | scenario and assignment-feasibility reports | Supplied scenarios only; no enumeration/optimization |
| Assignment mechanism | `restricted` | `run_governed_randomization` | No inference or claim authorization |
| Treatment/control assignment | `restricted` | assignment plan/candidate, reproducibility manifest, failure packet | Explicit-pool allocation only; no authorized selection |
| Estimator / inference eligibility | `restricted` | method suitability and readout plan | Classification only; no selection or authorization |
| Multicell/shared control | `blocked` | family/contrast runtime | No multiplicity inference; pooled/winner claims blocked |
| Experiment monitoring | `not_implemented` | none | No scheduler/live monitoring service |
| Post-test readout | `restricted` | DID point executor; trusted report packet | No executed inference or authorized causal readout |
| Evidence export | `restricted` | native evidence, manifests, generic handoff, spend evidence | No MIP-complete authorized evidence export |
| Failure recovery | `restricted` | assignment/execution/readout failure packets | No durable job/idempotency/retry service |

## Method-family truth

| Family | Current truth | Interval / claim boundary | Promotion dependency |
|---|---|---|---|
| SCM | `production_candidate_gated` | Placebo null-monitor and bounded JK work; no production inference | Donor support, null calibration, multicell handling, release review |
| AugSynth CVXPY | `remediation_required` / diagnostic point candidate | No calibrated production inference | Adapter, null calibration, donor diagnostics, DGP evidence |
| DID | conditional candidate | First governed runtime is point estimate only; bootstrap/CI not executed | Eligible design, trends/clusters/assignment evidence, calibration |
| Synthetic DID | research/scout | Implementation-readiness plan; no production path | Implement then validate suitability/DGP coverage |
| TBRRidge | diagnostic only | KFold/BRB/placebo/JK bounded to diagnostic/falsification semantics | Remediation evidence or retirement |
| Classic/aggregate TBR | retire/replace blocked | Aggregate point readout is not causal inference | Retire unsafe aggregate/global path or replace |
| Bayesian TBR | posterior diagnostic/research | Posterior interval is not a causal CI | Calibration replay and prior sensitivity |
| TROP | research only | No promotion-grade causal inference | Scout and validation evidence |
| Multicell/shared control | blocked | Per-cell restricted at most; no simultaneous/pooling inference | Dependence, FWER, selection semantics, release review |

No family is `production_ready`. SCM is the nearest candidate, but its candidate
label authorizes neither a production p-value nor a causal interval, lift, or
readout.

## Selection and release gates

The selection gate is **requirements and metadata/implementation planning only**.
Requirements define fourteen ordered layers, blocked reasons, failure-registry
links, alternatives, method status, multicell restrictions, and release-gate
dependency. The planned `ExperimentSelectionDecision` is not a callable decision.
The implementation plan says `implementation_plan_only_no_runtime_router: true`
and `production_selection_router_authorized: false`. `METHOD_SUITABILITY_RUNTIME_001`
classifies/requires review; it does not select an estimator, inference method, or
primary readout stack.

The release gate is plan-only. It has no runtime authorization engine or decision
record implementation. It leaves method, inference, causal uncertainty, p-value,
multicell, router, TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler,
and package-agent authorization false or blocked.

## Assignment and causal-claim boundary

GeoX may receive a governed assignment request and can calculate an explicit-pool
candidate/plan with reproducibility and constraint traces. It can also run
governed randomization. It cannot select a candidate, optimize matched markets,
balance, or rerandomization, or create an authorized treatment/control assignment.

MIP may collect requirements and request a governed GeoX assignment evaluation;
it may not choose treatment markets. An LLM may describe options or request the
calculation, but may not choose markets. Production p-values, CIs, lift,
power/MDE, assignment, multicell claims, and readout approval are all false.

## MIP handoff inventory

| Required handoff | Existing artifact / entrypoint | Runtime-tested | Authorized | Missing work |
|---|---|---:|---:|---|
| Experiment requirements | MIP `ExperimentDesignIntake`; GeoX planning inputs | Yes, contracts | No | Versioned package request and resolver |
| Data validation / feasibility / matchability | profiler, market/scenario/assignment reports | Yes | No | Stable MIP export/persistence and contract test |
| Power/MDE diagnostics | `evaluate_power_mde_diagnostics` | Yes | No | Formal method-specific power/MDE and release evidence |
| Selection decision / alternatives | planned selection decision; suitability runtime | No production router | No | Implement and shadow validate router |
| Blocked reasons | typed packet/status taxonomies | Yes | No | Cross-repo canonical mapping |
| Assignment manifest | `AssignmentPlan` and `AssignmentReproducibilityManifest` | Yes | No | Authorized selection, durable store, MIP envelope |
| Run manifest / failure packet | execution contracts and typed packets | Shell/dry-run | No | Durable run, idempotency, retry ownership |
| Readout artifact | `ReadoutEvidence`, trusted report packet | Yes, guarded | No | Governed estimator/inference readout export |
| ExperimentEvidence | native `panel_exp.evidence.ExperimentEvidence` | Yes native | No | MIP adapter and authorization fields |
| CalibrationSignal | none | No | No | Eligibility gate, export and registry path |
| PostTestSpendEvidence | `build_post_test_spend_evidence` | Yes | No | Live service/data boundary; MIP path remains bounded |

Native GeoX `ExperimentEvidence` has stable evidence version, experiment and
assignment identity/hashes, validation/inference metadata, warnings and errors.
MIP `ExperimentEvidence` instead requires a scalar estimate, optional SE/CI/p,
three diagnostic summaries, quality/freshness, confidence tier, artifact status,
and URI. No committed adapter maps the schemas, preserves interval semantics, and
enforces release/claim authorization. This is a semantic contract gap.

## Readout and MIP runtime reality

The actual package path is partial:

```text
execution metadata / materialized post-period spend
  -> package PostTestSpendEvidence
  -> package trusted-readout spend handoff
  -> MIP result-ingestion / trust-routing envelope
```

`build_post_test_spend_evidence(...)` is real deterministic package code. It
computes spend/readiness facts and explicitly does not calculate ROI/ROAS or
authorize claims. MIP's `call_geox_post_test_spend_runtime_for_fixture` is
explicitly `FIXTURE_ONLY`; the upload bridge is also limited to materialized CSV
post-test spend. Neither is full experiment execution, lift calculation, or
CalibrationSignal production.

MIP has design intake, source inspection, fixture/upload materialization, result
ingestion, and TrustReport routing. `src/mip/adapters/geox/` is absent; the actual
`src/mip/adapters/geox.py` returns a documented placeholder with no estimate or
execution. This is a contract skeleton, not a general engine adapter.

## Ownership and operating requirements

| Concern | Owner | Current state |
|---|---|---|
| Deterministic analysis, feasibility, assignment/inference/readout packets | GeoX | Partly implemented, all bounded |
| Conversation, requirements, artifact resolution, explanation/UI | MIP | Partly implemented contracts/workflows |
| Metadata/artifact persistence | MIP/platform | Unresolved; GeoX registry is contract-first |
| Jobs, idempotency, retries, observability, audit logs | MIP/platform | Not evidenced as a production path |
| Data access, tenant isolation, credentials, retention | Platform/MIP | Not evidenced in GeoX |
| Causal release/claim decision | GeoX governance, consumed by MIP | Guardrail/plan only; no authorization |
| Rollback and monitoring | Platform plus GeoX revocation facts | Release-gate plan only |

GeoX must not become MIP's application control plane. MIP must not calculate
power, MDE, lift, estimates, intervals, or assignments outside GeoX.

## Authorization matrix

All required authorizations are false on committed evidence:

| Authorization | Value | Evidence boundary |
|---|---:|---|
| production_design_feasibility_authorized | false | Feasibility evaluates supplied facts only |
| production_power_mde_authorized | false | Diagnostics are descriptive sensitivity only |
| production_assignment_authorized | false | Candidate generation only |
| production_selection_router_authorized | false | Requirements/plan, no runtime router |
| scm_production_inference_authorized | false | Candidate-gated metadata only |
| augsynth_production_inference_authorized | false | Remediation required |
| did_production_inference_authorized | false | Point executor only |
| synthetic_did_production_inference_authorized | false | Research/readiness only |
| tbrridge_production_inference_authorized | false | Diagnostic/remediation lane |
| multicell_production_claim_authorized | false | Dependence/multiplicity unresolved |
| production_readout_authorized | false | Packet/report mechanics block unsupported surfaces |
| experiment_evidence_export_authorized | false | Native evidence is not governed MIP export |
| calibration_signal_export_authorized | false | No eligibility/export |
| post_test_spend_export_authorized | false | Readiness evidence, not downstream authorization |
| mip_runtime_handoff_authorized | false | Planning-stable package handoff only |
| scheduled_execution_authorized | false | Scheduler domain remains blocked |

## Workflow alignment and next milestones

| MIP node | GeoX state | MIP need | Blocked dependency |
|---|---|---|---|
| Identify an evidence gap | Restricted diagnostics | intake/resolver/explanation | canonical request and persisted artifacts |
| Design GeoX | Restricted feasibility and sensitivity | requirements/proposal UI | selection router, power/MDE, assignment authorization |
| Review GeoX evidence | Restricted point/diagnostic packets | ingestion and TrustReport review | calibrated inference and evidence adapter |
| Refresh MMM | No CalibrationSignal | registry/calibration routing | eligibility/export/MMM authorization |
| Produce decision package | Restricted claim packet | decision/explanation | release decision and authorized readout |

**GeoX next:** `AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001`, then deterministic
selection-router implementation and shadow validation only after prerequisites.
Do not start package-side agents.

**MIP next:** `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001`, expanded into
a versioned GeoX artifact resolver/evidence mapping boundary that cannot invent
causal facts.

**Cross-repository next:**
`GEOX_MIP_GOVERNED_EXPERIMENT_ARTIFACT_ENVELOPE_AND_COMPATIBILITY_001` for
request/result/failure/assignment/run/readout/authorization schemas and a
non-production integration dry run.

## Required conclusions and MIP alignment packet

1. A sample demo is possible only with fixture/diagnostic/blocked surfaces.
2. A real-team pilot is not ready.
3. Production experiment design is not ready.
4. Treatment assignment and production power/MDE are not authorized.
5. No method has production causal inference authorization.
6. Guarded readout packets exist; a governed causal readout does not.
7. Native ExperimentEvidence serializes, but governed MIP export does not exist.
8. CalibrationSignal cannot be exported.
9. MIP's only real package call is bounded post-test-spend fixture/upload runtime.
10. The evidence supports GeoX as causal engine and MIP as control plane/product;
    no exception supports MIP causal recomputation or GeoX control-plane ownership.

```text
GeoX HEAD: 7e1519e00eb5a1045624afd180dfb206ece9d31e
Verdict: GEOX_MIP_ALIGNMENT_BLOCKED_BY_MULTIPLE_GAPS
Candidates: SCM gated; DID conditional
Diagnostic: AugSynth point path, TBRRidge, guarded readout/claim packets
Research: Synthetic DID, Bayesian TBR, TROP
Blocked: classic/aggregate TBR causal path; multicell production claims
Selection/release: plan-only; no authorized router or release runtime
MIP runtime: fixture/materialized-upload post-test spend only; general adapter placeholder
Every required production authorization: false
Next: P0 GeoX hardening; MIP consumer contract; shared artifact envelope
```

## Validation record

This docs-only audit adds no runtime/method/test changes and does not regenerate
existing archives. Exact validation commands and statuses are captured in the
summary JSON after final validation.
