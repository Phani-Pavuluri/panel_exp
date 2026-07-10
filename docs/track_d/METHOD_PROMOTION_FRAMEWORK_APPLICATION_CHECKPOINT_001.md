# METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001` |
| **Artifact type** | `method_promotion_framework_application_checkpoint` |
| **Lane** | Lane A — Method / instrument promotion framework checkpoint |
| **Status** | `completed` |
| **Scope** | `framework_application_checkpoint_docs_only_no_runtime_no_promotion` |
| **Final verdict** | `framework_checkpoint_completed_two_applications_reviewed_no_runtime_no_promotion` |
| **Recommended next** | `METHOD_PROMOTION_GENERIC_CONTRACTS_001` |

**Depends on:**

- `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001`
- `METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001`
- `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001`
- `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001`

---

## 2. Why this checkpoint exists

The method promotion review framework now has **two complete instrument applications**:

1. **TBRRidge restricted-review pilot** — `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review`
2. **SCM Jackknife null-monitor application** — `geo.scm.jackknife.single_cell.delta_mu.null_monitor`

Each application completed the full governed chain: evidence packet contract → packet runtime → review decision contract → review decision runtime. Both preserved fixed non-authorization statuses, claim/catalog/production boundaries, and evidence quality boundaries.

This is the right point to **stop and assess the framework** before adding AugSynth/DID lanes or overfitting to one instrument family. Two applications are enough to see repeated structure and copy-paste drift risk, but not enough to justify blindly scaling bespoke artifacts.

The goal of this checkpoint is to determine whether to proceed directly to another instrument lane or first formalize generic framework contracts that next lanes plug into common abstractions.

---

## 3. Completed applications compared

| Dimension | TBRRidge application | SCM null-monitor application | Generalized framework implication |
|-----------|-------------------|------------------------------|-----------------------------------|
| **Exact identity** | `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` | `geo.scm.jackknife.single_cell.delta_mu.null_monitor` | Exact-instrument scoping works; no family promotion |
| **Surface** | `restricted_review` | `null_monitor` | Surface is instrument-specific; generic contract needs surface field |
| **Positive decision meaning** | `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` | Single positive decision per surface; not promotion |
| **Packet contract** | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001` | `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` | Same four-stage chain; instrument-specific naming |
| **Packet runtime** | `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` | `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` | Same assembly pattern; category registry differs |
| **Review decision contract** | `TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001` | `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001` | Same input/output/decision mapping shape |
| **Review decision runtime** | `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001` | `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001` | Same precedence ladder; status names differ |
| **Required evidence categories** | identity, claim_boundary, metric_estimand_alignment, null_control_false_positive, directional_error, positive_control_recovery, sensitivity, readout_compatibility | identity, claim_boundary, metric_estimand_alignment, null_control_false_positive, jackknife_stability, directional_error, donor_pool_diagnostics, pre_period_fit_diagnostics, sensitivity, readout_compatibility | Core categories overlap; instrument extensions differ |
| **Instrument-specific categories** | positive_control_recovery, KFold coverage/leakage context | jackknife_stability, donor_pool_diagnostics, pre_period_fit_diagnostics | Extension registry per instrument; cannot replace core |
| **Readiness statuses** | `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT`, blocked/partial variants | `PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT`, blocked/partial variants | Same status family; surface-specific ready label |
| **Eligibility statuses** | `ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT`, NOT_ELIGIBLE_* | `ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT`, NOT_ELIGIBLE_* (+ causal-claim guard) | Same eligibility family; SCM adds null-monitor scope guards |
| **Decision statuses** | `APPROVE_RESTRICTED_REVIEW_CONTINUATION`, rejects, defers | `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION`, rejects (+ cross-estimand), defers | Same decision taxonomy; instrument-specific positive label |
| **Fixed non-authorization statuses** | NOT_AUTHORIZED / NOT_UNBLOCKED / NOT_PROMOTED | Same + `NULL_MONITOR_ONLY` scope status | Reusable boundary status enum |
| **Alias/catalog handling** | Exact identity only | Canonical identity + catalog alias preserved separately | SCM proves alias reconciliation pattern |
| **Evidence quality boundary** | Packet metadata only; no raw scoring | Packet metadata only; no raw scoring | Reusable rule across both |
| **Claim boundary** | `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` | SCM claim boundary category required | Claim boundary is per-instrument prerequisite |
| **Catalog/production boundary** | Defer to separate lanes; never authorized here | Defer to separate lanes; never authorized here | Reusable deferral semantics |
| **Lane B/MIP boundary** | Lane B evidence cannot substitute method validity | Lane B evidence cannot substitute method validity | Reusable separation rule |

---

## 4. What generalized cleanly

Reusable pieces that worked across both applications:

- **Exact instrument identity** — canonical dotted identity enforced; no cross-inference/geometry/estimand inheritance
- **Evidence packet contract/runtime pattern** — refs → grouped categories → readiness/eligibility → blockers/missing evidence
- **Packet readiness / eligibility status family** — ready, partial, blocked-missing, blocked-identity, blocked-claim, blocked-cross-*, not-requested
- **Review decision contract/runtime pattern** — consume packet → precedence mapping → allowed/prohibited actions
- **Blocker/missing evidence preservation** — decision runtime passes through packet blockers unchanged
- **Warnings/lineage preservation** — input and packet lineage merged deterministically
- **Allowed/prohibited next actions** — surface-appropriate allowed set + universal prohibition list
- **Fixed non-authorization statuses** — claims, catalog, production, promotion always negative
- **Evidence quality boundary** — no raw evidence inspection or scoring in decision runtime
- **Claim/catalog/production separation** — production/catalog surfaces defer; never conflated with continuation approval
- **Lane B/MIP separation** — spend/ROI readiness cannot substitute method-validity categories

---

## 5. What remained instrument-specific

- **TBRRidge KFold diagnostic interval categories** — positive_control_recovery, KFold leakage/coverage context
- **SCM null-monitor categories** — jackknife_stability, donor_pool_diagnostics, pre_period_fit_diagnostics
- **SCM donor pool / pre-period / jackknife-stability diagnostics** — SCM-specific method-validity evidence
- **Null-monitor-specific scope semantics** — `NULL_MONITOR_ONLY`, `NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW`, cross-estimand reject
- **Catalog alias reconciliation for SCM** — `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review` preserved without substitution
- **Approval semantics**
  - TBRRidge = `APPROVE_RESTRICTED_REVIEW_CONTINUATION` on `restricted_review` surface
  - SCM = `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` on `null_monitor` surface
- **Method-validity blocker names**
  - TBRRidge: `FAILED_NULL_CONTROL_EVIDENCE`, `FAILED_POSITIVE_CONTROL_RECOVERY`, `FAILED_DIRECTIONAL_ERROR_EVIDENCE`, etc.
  - SCM: `failed_null_control_evidence`, `failed_jackknife_stability_evidence`, `failed_donor_pool_diagnostics`, etc.

---

## 6. Framework gaps discovered

Gaps before scaling to AugSynth/DID:

- **No generic typed framework contract yet** — each instrument has bespoke dataclass names
- **No shared generic packet base class/runtime yet** — duplicated assembly and decision modules
- **Repeated non-authorization field patterns** — same six boundary fields copy-pasted per runtime
- **Repeated status families with instrument-specific prefixes** — ready/eligible labels differ (`PROMOTION_REVIEW` vs `NULL_MONITOR_REVIEW`)
- **Possible future need for generic `MethodPromotionInstrumentIdentity` object** — modality/estimator/inference/geometry/estimand/surface fields
- **Possible future need for generic `MethodPromotionEvidenceReference` object** — evidence_id, category, artifact_ref, optional identity
- **Possible future need for common blocker vocabulary** — normalize `BLOCKED_*` vs `failed_*` naming
- **Possible future need for runtime adapters** — instrument-specific packets → generic summaries for cross-instrument reporting
- **Need to decide whether generic runtime should exist before AugSynth/DID** — this checkpoint recommends contracts first, runtime later

---

## 7. Risk assessment before AugSynth/DID

| Risk | Assessment |
|------|------------|
| **AugSynth** | Higher strategic value (ranked secondary in selection audit) but higher evidence/method-risk burden; JK coverage and ASCM remediation gaps remain |
| **DID bootstrap** | Needs explicit parallel-trends/assumptions evidence and claim boundary work; `DID_BOOTSTRAP` still blocklisted for production |
| **Premature instrument lanes** | Adding either before checkpoint remediation could create duplicated bespoke artifacts and naming drift |
| **Framework maturity** | Directionally reusable but not yet formalized as generic typed contracts; two applications prove pattern viability, not completeness |

---

## 8. Decision: proceed vs pause

**Recommended decision:** `PAUSE_NEW_INSTRUMENT_LANES_AND_FORMALIZE_GENERIC_CONTRACTS`

**Reason:**

- Two applications prove pattern viability (TBRRidge pilot + SCM null-monitor)
- Repeated structure is now visible across contract/runtime pairs
- Before AugSynth/DID, create generic framework contracts so next lanes plug into common abstractions
- Avoids copy-paste drift in status enums, boundary fields, and prohibited-action lists

---

## 9. Recommended next artifact

**`METHOD_PROMOTION_GENERIC_CONTRACTS_001`**

Define generic docs/tests-only contracts for:

- `MethodPromotionInstrumentIdentity`
- `MethodPromotionEvidenceReference`
- `MethodPromotionEvidencePacket`
- `MethodPromotionPacketReadinessStatus`
- `MethodPromotionReviewEligibilityStatus`
- `MethodPromotionReviewDecision`
- `MethodPromotionReviewDecisionStatus`
- `MethodPromotionBoundaryStatus`
- `MethodPromotionAllowedAction`
- `MethodPromotionProhibitedAction`

Still docs/tests-only. No runtime yet.

---

## 10. Alternative next artifacts

| Alternative | Why not now |
|-------------|-------------|
| `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` | Defer until generic contracts exist; avoid third bespoke chain |
| `DID_BOOTSTRAP_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` | Defer; assumptions/claim boundary burden too high |
| `METHOD_PROMOTION_GENERIC_RUNTIME_001` | Too early; generic contract should stabilize vocabulary first |
| Catalog unblock lane | Premature; no instrument has earned catalog movement |
| Production compatibility lane | Premature; gate-triggered after RANK_4 candidate |

---

## 11. Acceptance criteria for moving to AugSynth/DID

Before opening AugSynth or DID instrument lanes:

- Generic contracts defined (`METHOD_PROMOTION_GENERIC_CONTRACTS_001`)
- Common identity/evidence/packet/decision vocabulary documented
- Mapping from instrument-specific artifacts to generic concepts documented
- Claim/catalog/production boundaries still enforced in generic contracts
- No loss of exact-instrument scoping
- No generic runtime until contracts stabilize

---

## 12. Non-goals

This checkpoint does **not**:

- Implement runtime, generic runtime, or generic contract runtime
- Promote any method, instrument, SCM, TBRRidge, AugSynth, or DID
- Unblock catalog or authorize production compatibility
- Change claim authorization or authorize statistical/causal/business/ROI claims
- Authorize decision recommendations or production readout
- Implement estimator/inference behavior
- Run new validation experiments or score raw evidence quality
- Modify Lane B runtime, implement MIP decisioning, or bypass TrustReport/claim authorization

---

## 13. Validation results

- Checkpoint doc: `docs/track_d/METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001.md`
- Summary JSON: `docs/track_d/archives/METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001_summary.json`
- Governance tests: `tests/governance/test_method_promotion_framework_application_checkpoint_001.py`

Capability flags (all true): `framework_checkpoint_completed`, `two_applications_reviewed`, `reusable_patterns_identified`, `instrument_specific_patterns_identified`, `framework_gaps_identified`, `augsynth_did_risk_assessed`, `pause_new_instrument_lanes_recommended`, `generic_contracts_recommended`.
