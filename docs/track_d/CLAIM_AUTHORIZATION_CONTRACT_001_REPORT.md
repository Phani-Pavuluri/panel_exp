# CLAIM_AUTHORIZATION_CONTRACT_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `CLAIM_AUTHORIZATION_CONTRACT_001` |
| **Artifact type** | `claim_authorization_contract` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `contract_only_no_claim_or_production_authorization` |
| **Base commit** | `8b43d34` (Add first governed DID diagnostic) |
| **Final verdict** | `claim_authorization_contract_defined_no_claim_or_production_authorization` |

CLAIM_AUTHORIZATION_CONTRACT_001 defines the future governed contract for evaluating whether a readout may make specific claim types from execution artifacts, effect estimate reports, uncertainty artifacts, diagnostics/sensitivity evidence, method/instrument governance, estimand scope, assignment artifacts, and production governance. It defines claim request schemas, claim decision statuses, required evidence gates, blocker semantics, caveats, failure packets, and handoff to trusted readout reporting. It does not authorize claims or production in this artifact.

---

## 2. Source files inspected

- `panel_exp/validation/readout_did_diagnostics_002.py`
- `tests/validation/test_readout_did_diagnostics_002.py`
- `docs/track_d/READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC_REPORT.md`
- `docs/track_d/archives/READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC_summary.json`
- `panel_exp/validation/readout_diagnostics_sensitivity_runtime_001.py`
- `tests/validation/test_readout_diagnostics_sensitivity_runtime_001.py`
- `docs/track_d/READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001_REPORT.md`
- `panel_exp/validation/estimator_inference_did_executor_003.py`
- `tests/validation/test_estimator_inference_did_executor_003.py`
- `docs/track_d/ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR_REPORT.md`
- `panel_exp/validation/estimator_inference_execution_runtime_001.py`
- `tests/validation/test_estimator_inference_execution_runtime_001.py`
- `panel_exp/validation/readout_plan_runtime_001.py`
- `tests/validation/test_readout_plan_runtime_001.py`
- `panel_exp/validation/method_suitability_runtime_001.py`
- `tests/validation/test_method_suitability_runtime_001.py`
- `panel_exp/validation/readout_diagnostics_sensitivity_contract_001.py`
- `docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`
- `docs/ROADMAP_V4.md`
- `docs/MIP_AUDIT_REGISTRY.md`
- `docs/governance/OPEN_INVESTIGATIONS_001.json`

---

## 3. Why this contract is needed

Governed DID point-estimate execution and coverage/pre-period diagnostics now exist, and diagnostics/sensitivity runtime can evaluate evidence sufficiency for claim review. None of these layers decide which claims a readout may make.

Future trusted readout reporting requires an explicit contract separating effect estimates, diagnostic evidence, evidence sufficiency, claim review eligibility, claim authorization, and production readout authorization. Without this contract, downstream reporting could conflate review eligibility with authorization or treat point estimates as causal lift claims.

This artifact defines the future claim-authorization decision contract without authorizing any claims or production readout.

---

## 4. Relationship to DID point-estimate executor

`ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR` emits governed DID point estimates behind an opt-in execution gate. A point estimate is an execution artifact, not a claim. This contract defines how a future `POINT_ESTIMATE_CLAIM` may be requested and reviewed when an effect estimate report exists, with mandatory caveats when uncertainty is absent. It forbids using the current DID executor alone to support causal lift, incremental lift, ROI, or production claims.

---

## 5. Relationship to DID diagnostic runtime

`READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC` implements coverage/pre-period structural diagnostics. Diagnostic results inform claim review eligibility but do not authorize claims. This contract consumes diagnostic evidence packets and enforces that failed blocking diagnostics block causal/incremental claim review.

---

## 6. Relationship to diagnostics/sensitivity evidence sufficiency

`READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001` may emit `EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW` with `claim_authorized: false`. Evidence sufficiency allows review only; claim authorization runtime must still enforce claim-specific gates. This contract defines the downstream claim-type gates that sufficiency alone cannot satisfy.

---

## 7. Conceptual distinctions

1. **Effect estimate:** A numerical estimate emitted by a governed executor. Not itself a claim.
2. **Diagnostic/sensitivity evidence:** Evidence about whether the estimate is reviewable. Not itself authorization.
3. **Evidence sufficiency:** May allow claim review. Not itself claim authorization.
4. **Claim authorization contract:** Defines future decision contract. This artifact. Does not authorize.
5. **Claim authorization runtime:** Future runtime that can authorize, restrict, or block claim types.
6. **Trusted readout report:** Future report that can display only authorized claims.

---

## 8. Future contract concepts

| Concept | Purpose |
|---------|---------|
| `ClaimAuthorizationInput` | Bundles claim request, evidence bundle, and config for evaluation |
| `ClaimAuthorizationConfig` | Governance toggles, gate strictness, audience restrictions |
| `ClaimRequest` | Typed request for a specific claim with scope and language requirements |
| `ClaimDecision` | Future decision outcome for one claim request |
| `ClaimAuthorizationReport` | Aggregate report over multiple claim decisions |
| `ClaimEvidenceBundle` | Normalized evidence references from execution and governance |
| `ClaimScope` | Population, unit, time, contrast, and metric scope for a claim |
| `ClaimType` | Enumerated claim type (see section 9) |
| `ClaimStatus` | Enumerated decision status (see section 10) |
| `ClaimBlocker` | Structured blocker with category and remediation hint |
| `ClaimCaveat` | Required disclosure limiting claim interpretation |
| `ClaimRestriction` | Authorized scope reduction (e.g. diagnostic-only) |
| `ClaimBoundaryReport` | Explicit boundary flags for what was not authorized |
| `ClaimFailurePacket` | Structured failure when gates cannot be satisfied |
| `ClaimTrace` | Audit trace of gate evaluations |
| `ClaimProvenanceManifest` | Provenance chain for evidence bundle |
| `TrustedReadoutHandoffPacket` | Future handoff to trusted readout reporting |

---

## 9. Claim types

| Claim type | Description |
|------------|-------------|
| `DIAGNOSTIC_ONLY_CLAIM` | Structural/diagnostic disclosure only |
| `DESCRIPTIVE_EFFECT_CLAIM` | Descriptive effect language without causal incrementality |
| `POINT_ESTIMATE_CLAIM` | Point estimate with explicit uncertainty caveats |
| `INCREMENTAL_LIFT_CLAIM` | Incremental lift with full evidence gates |
| `CAUSAL_LIFT_CLAIM` | Causal lift with governance allowing causal language |
| `ROI_CLAIM` | ROI with spend/cost/revenue and ROI governance |
| `PRODUCTION_READOUT_CLAIM` | Production-facing readout with production governance |
| `METHOD_COMPARISON_CLAIM` | Method comparison disclosure |
| `SENSITIVITY_ONLY_CLAIM` | Sensitivity evidence disclosure only |
| `INSUFFICIENT_EVIDENCE_CLAIM` | Safe negative claim, e.g. evidence insufficient for causal lift |

---

## 10. Claim statuses

| Status | Meaning |
|--------|---------|
| `CLAIM_AUTHORIZATION_READY_FOR_RUNTIME` | Contract-valid request ready for future runtime |
| `CLAIM_REVIEW_ELIGIBLE` | Evidence supports review; not authorization |
| `CLAIM_REVIEW_ELIGIBLE_WITH_WARNINGS` | Review eligible with warnings |
| `CLAIM_PROVISIONAL_REVIEW_ONLY` | Provisional review only |
| `CLAIM_AUTHORIZED` | **Future runtime only** — not emitted by this contract |
| `CLAIM_AUTHORIZED_WITH_RESTRICTIONS` | **Future runtime only** — not emitted by this contract |
| `CLAIM_RESTRICTED_TO_DIAGNOSTIC_ONLY` | Restricted to diagnostic-only interpretation |
| `CLAIM_BLOCKED_BY_MISSING_EXECUTION` | No execution artifact |
| `CLAIM_BLOCKED_BY_MISSING_EFFECT_ESTIMATE` | No effect estimate |
| `CLAIM_BLOCKED_BY_MISSING_UNCERTAINTY` | Uncertainty required but absent |
| `CLAIM_BLOCKED_BY_MISSING_DIAGNOSTICS` | Required diagnostics absent |
| `CLAIM_BLOCKED_BY_FAILED_DIAGNOSTICS` | Blocking diagnostic failed |
| `CLAIM_BLOCKED_BY_MISSING_SENSITIVITY` | Required sensitivity absent |
| `CLAIM_BLOCKED_BY_FAILED_SENSITIVITY` | Blocking sensitivity failed |
| `CLAIM_BLOCKED_BY_INCOMPATIBLE_ESTIMAND` | Estimand incompatible with claim |
| `CLAIM_BLOCKED_BY_METHOD_GOVERNANCE` | Method governance blocks claim |
| `CLAIM_BLOCKED_BY_ASSIGNMENT_ARTIFACT` | Assignment artifact restriction |
| `CLAIM_BLOCKED_BY_PRODUCTION_GOVERNANCE` | Production governance missing |
| `CLAIM_BLOCKED_BY_ROI_GOVERNANCE` | ROI governance missing |
| `CLAIM_NOT_EVALUATED` | Not yet evaluated |

---

## 11. Claim request fields

Each future `ClaimRequest` must include: `claim_request_id`, `claim_type`, `requested_metric`, `requested_estimand`, `requested_population_scope`, `requested_unit_scope`, `requested_time_window`, `requested_cell_contrast`, `requested_effect_scale`, `requested_uncertainty_semantics`, `requires_production_readout`, `requires_roi_support`, `requires_causal_language`, `requires_incrementality_language`, `requires_diagnostic_disclosure`, `requested_output_audience`, `governance_source`, `notes`.

---

## 12. Evidence bundle fields

`ClaimEvidenceBundle` must include: `execution_artifact_id`, `instrument_id`, `estimator_family`, `inference_family`, `effect_estimate_report`, `uncertainty_report`, `inference_diagnostic_report`, `diagnostic_evidence_packets`, `sensitivity_evidence_packets`, `evidence_sufficiency_report`, `assignment_artifact_reference`, `readout_plan_artifact_reference`, `method_suitability_reference`, `executor_adapter_reference`, `estimand_scope`, `claim_scope`, `provenance_manifest`.

---

## 13. Claim decision fields

Future `ClaimDecision` must include: `claim_decision_id`, `claim_request_id`, `claim_type`, `claim_status`, `authorized_claim_text`, `authorized_claim_scope`, `restrictions`, `caveats`, `blockers`, `required_disclosures`, `evidence_bundle_references`, `claim_boundary_report`, `trusted_readout_handoff`, `warnings`.

`authorized_claim_text` is a future field. This contract does not generate authorized claim text.

---

## 14. Blocker categories

`MISSING_EXECUTION_ARTIFACT`, `MISSING_EFFECT_ESTIMATE`, `MISSING_UNCERTAINTY_ARTIFACT`, `MISSING_DIAGNOSTIC_EVIDENCE`, `FAILED_DIAGNOSTIC_EVIDENCE`, `MISSING_SENSITIVITY_EVIDENCE`, `FAILED_SENSITIVITY_EVIDENCE`, `INCONCLUSIVE_EVIDENCE`, `INCOMPATIBLE_ESTIMAND`, `INCOMPATIBLE_EFFECT_SCALE`, `UNSUPPORTED_CLAIM_TYPE`, `METHOD_GOVERNANCE_RESTRICTION`, `ASSIGNMENT_ARTIFACT_RESTRICTION`, `DIAGNOSTIC_ONLY_INSTRUMENT`, `ROI_GOVERNANCE_MISSING`, `PRODUCTION_GOVERNANCE_MISSING`, `PROVENANCE_MISSING`.

---

## 15. Gate order

Future claim authorization runtime must evaluate gates in order:

1. claim request schema gate
2. execution artifact gate
3. effect estimate gate
4. uncertainty/inference gate
5. diagnostic evidence gate
6. sensitivity evidence gate
7. estimand compatibility gate
8. method/instrument governance gate
9. assignment artifact gate
10. ROI governance gate
11. production governance gate
12. provenance/trace gate
13. claim scope/caveat gate
14. trusted readout handoff gate

**Rules:**
- Diagnostic-only claims may proceed without uncertainty if clearly labeled diagnostic-only.
- Point-estimate claims require effect estimate but do not require p-values/CIs if labeled point-estimate-only.
- Incremental/causal lift claims require compatible estimand, effect estimate, uncertainty semantics, diagnostics, sensitivity evidence, and method governance.
- ROI claims require explicit ROI governance and cost/revenue support.
- Production readout claims require production governance, provenance, evidence sufficiency, and compatible claim scope.
- Diagnostic-only instruments cannot support production causal lift or ROI claims.
- Evidence sufficiency allows review only; claim runtime must still enforce claim-specific gates.

---

## 16. Claim-type evidence matrix

| Claim type | Required evidence |
|------------|-------------------|
| `DIAGNOSTIC_ONLY_CLAIM` | Diagnostic evidence or diagnostic-only instrument status; no causal language; no production claim |
| `POINT_ESTIMATE_CLAIM` | Effect estimate; must disclose no uncertainty if uncertainty missing; no causal claim unless separately authorized |
| `INCREMENTAL_LIFT_CLAIM` | Effect estimate, compatible estimand, uncertainty semantics, diagnostics, sensitivity evidence; no failed blocking diagnostics |
| `CAUSAL_LIFT_CLAIM` | All incremental-lift gates plus method/assignment governance allowing causal language |
| `ROI_CLAIM` | Causal/incremental lift authorization plus ROI governance, spend/cost/revenue support, ROI estimand compatibility |
| `PRODUCTION_READOUT_CLAIM` | Production governance, provenance, claim scope, evidence sufficiency, no unresolved blockers |

---

## 17. Current DID point-estimate treatment

The current DID point-estimate executor may support a future `POINT_ESTIMATE_CLAIM` if the effect estimate report exists and caveats disclose that no inference has been executed. It must not support causal lift, incremental lift, ROI, or production claims without additional uncertainty, diagnostic/sensitivity, estimand, and governance evidence. The current DID coverage/pre-period diagnostic may support future claim review but does not authorize claims.

---

## 18. Failure packet semantics

`ClaimFailurePacket` fields: `failure_id`, `claim_request_id`, `claim_type`, `claim_status`, `blocking_gates`, `blockers`, `missing_evidence`, `failed_evidence`, `inconclusive_evidence`, `governance_failures`, `required_remediation`, `claim_boundary_report`.

Retry/remediation categories: `ADD_EXECUTION_ARTIFACT`, `ADD_EFFECT_ESTIMATE`, `ADD_UNCERTAINTY_ARTIFACT`, `ADD_DIAGNOSTIC_EVIDENCE`, `ADD_SENSITIVITY_EVIDENCE`, `FIX_ESTIMAND_SCOPE`, `FIX_ASSIGNMENT_ARTIFACT`, `RESTRICT_TO_POINT_ESTIMATE_CLAIM`, `RESTRICT_TO_DIAGNOSTIC_ONLY_CLAIM`, `ADD_ROI_GOVERNANCE`, `ADD_PRODUCTION_GOVERNANCE`, `BLOCK_CLAIM`.

---

## 19. Examples

1. **DID point estimate with no uncertainty** — eligible only for point-estimate review with caveats disclosing absent inference.
2. **DID point estimate plus coverage diagnostic** — still cannot authorize causal lift without uncertainty and sensitivity evidence.
3. **Failed blocking diagnostic** — blocks causal/incremental claim review.
4. **Diagnostic-only instrument** — supports diagnostic-only claim only.
5. **Missing effect estimate** — blocks point-estimate claim.
6. **Missing uncertainty** — blocks causal lift claim.
7. **Missing sensitivity evidence** — blocks incremental lift claim.
8. **ROI claim** — blocked without ROI governance and cost/revenue support.
9. **Production readout** — blocked without production governance.
10. **Insufficient evidence claim** — allowed as safe negative reporting (e.g. evidence insufficient to support causal lift).

---

## 20. Claim boundaries

Always false in this artifact:

- `claim_authorization_runtime_implemented`
- `claim_authorized`
- `claim_authorized_with_restrictions`
- `authorized_claim_text_generated`
- `trusted_readout_handoff_generated`
- `production_readout_authorized`
- `causal_claim_authorized`
- `incremental_lift_claim_authorized`
- `roi_claim_authorized`
- `production_authorization_granted`
- `estimator_execution_implemented`
- `inference_execution_implemented`
- `effect_estimate_computed`
- `diagnostic_check_executed`
- `sensitivity_check_executed`
- `p_value_computed`
- `confidence_interval_computed`
- `uncertainty_computed`
- `mmm_runtime_calls_implemented`
- `mmm_calibration_authorized`
- `llm_decisioning_authorized`

Allowed contract-level positives: `claim_authorization_contract_defined`, `claim_request_contract_defined`, `claim_evidence_bundle_contract_defined`, `claim_decision_contract_defined`, `claim_statuses_defined`, `claim_blockers_defined`, `claim_gate_order_defined`, `claim_type_evidence_matrix_defined`, `claim_failure_packet_contract_defined`, `claim_boundaries_defined` — all true.

---

## 21. Future implementation acceptance criteria

Future `CLAIM_AUTHORIZATION_RUNTIME_001` must:

- consume claim requests, execution artifacts, effect estimate reports, uncertainty reports (when needed), diagnostics/sensitivity evidence, evidence sufficiency reports, method/instrument governance, assignment artifacts, and provenance manifests
- evaluate claim-specific gates in defined order
- emit claim decisions, blockers, caveats, restrictions, and failure packets
- generate trusted readout handoff only for authorized/restricted claims
- not compute effects, run diagnostics, run inference, or authorize production unless production governance gates pass

---

## 22. Future tests

Future runtime tests should cover:

- missing execution artifact blocks claims
- missing effect estimate blocks point-estimate claim
- DID point estimate without uncertainty only allows point-estimate review caveat
- missing uncertainty blocks causal lift claim
- missing diagnostics blocks causal lift claim
- failed blocking diagnostic blocks causal lift claim
- missing sensitivity blocks incremental lift claim
- diagnostic-only instrument restricted to diagnostic-only claim
- ROI claim blocked without ROI governance
- production readout blocked without production governance
- insufficient evidence claim allowed
- claim authorization does not compute effect/inference/diagnostics
- no fixture-specific branching

---

## 23. Roadmap placement

Follows `READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC`. Precedes `CLAIM_AUTHORIZATION_RUNTIME_001` and `TRUSTED_READOUT_REPORT_CONTRACT_001`.

---

## 24. Recommended next artifact

**Primary:** `CLAIM_AUTHORIZATION_RUNTIME_001`

**Alternative:** `TRUSTED_READOUT_REPORT_CONTRACT_001`

Do not implement either in this artifact.
