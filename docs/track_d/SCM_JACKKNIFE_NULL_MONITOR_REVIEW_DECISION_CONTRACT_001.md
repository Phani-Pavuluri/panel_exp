# SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001` |
| **Artifact type** | `scm_jackknife_null_monitor_review_decision_contract` |
| **Lane** | **Lane A — Method / instrument promotion framework application** |
| **Status** | `completed` |
| **Scope** | `review_decision_contract_defined_no_runtime_no_promotion_no_claim_authorization` |
| **Instrument identity** | `geo.scm.jackknife.single_cell.delta_mu.null_monitor` |
| **Catalog alias** | `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review` |
| **Final verdict** | `scm_jackknife_null_monitor_review_decision_contract_defined_no_runtime_no_promotion` |
| **Recommended next** | `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001` |

**Depends on:**

- `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001`
- `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001`
- `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001`
- `METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`
- `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001`
- `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001`

---

## 2. Why this contract exists

`SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` and `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` now define and assemble governed null-monitor review inputs: explicit evidence references, packet readiness statuses, promotion-review eligibility statuses, blockers, and lineage for the exact SCM Jackknife null-monitor instrument.

This contract defines the **allowed review decision surface** for a future decision runtime consuming `SCMJackknifeNullMonitorPromotionEvidencePacket`. It mirrors the generalized framework and TBRRidge review-decision pattern, but uses **null-monitor continuation semantics** — not restricted-review causal/readout approval.

**Review decision is a governed interpretation of packet readiness and evidence completeness, not a statistical computation.** Decision eligibility does not promote SCM, SCM+Jackknife, or authorize any claim. This artifact is docs-only; no runtime is implemented here.

---

## 3. Exact instrument identity

**Canonical governed identity:** `geo.scm.jackknife.single_cell.delta_mu.null_monitor`

**Catalog alias:** `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review`

| Field | Value |
|-------|-------|
| `modality` | `geo` |
| `estimator_family` | `scm` |
| `inference_family` | `jackknife` |
| `geometry` | `single_cell` |
| `point_estimand` | `delta_mu` |
| `surface` | `null_monitor` |
| `interval_semantics` | `not_applicable_for_null_monitor` |

**Identity rules:**

- Canonical identity remains decision identity
- Catalog alias may appear in lineage/catalog notes only; alias cannot substitute canonical identity
- No cross-inference-family inheritance (e.g. placebo, bootstrap)
- No cross-geometry inheritance (e.g. aggregate_pooled, multi_cell)
- No cross-estimand inheritance
- No SCM family-level promotion
- No SCM placebo promotion
- No SCM production-readout promotion
- TBRRidge pilot evidence/decisions do not inherit to this instrument

---

## 4. Decision scope

### Only positive decision

**`APPROVE_NULL_MONITOR_REVIEW_CONTINUATION`**

**Meaning:**

- Assembled packet may continue as null-monitor review input
- Diagnostic/null behavior review may continue
- Missing evidence is not blocking at packet level
- Identity and null-monitor scope are consistent

**Not meaning:**

- SCM promoted · SCM+Jackknife promoted · catalog unblocked · production compatible
- Causal lift · business lift · CI · p-value · significance · statistical power authorized
- ROI/ROAS · decision recommendation · production readout authorized

---

## 5. Conceptual input object

**`SCMJackknifeNullMonitorReviewDecisionInput`**

| Field | Description |
|-------|-------------|
| `decision_id` | Unique decision request identifier |
| `packet_ref` | Reference to assembled evidence packet |
| `packet_readiness_status` | From packet assembly runtime |
| `promotion_review_eligibility_status` | From packet assembly runtime |
| `instrument_identity` | Canonical identity (§3) |
| `catalog_alias` | Optional catalog alias (lineage only) |
| `evidence_by_category` | Grouped evidence references from packet |
| `missing_evidence` | Missing required evidence categories |
| `blockers` | Active blocker codes from packet |
| `warnings` | Packet warnings |
| `requested_decision_surface` | Requested decision surface (default `null_monitor`) |
| `reviewer_notes` | Optional reviewer notes |
| `lineage` | Provenance dict |
| `created_from_artifacts` | Source artifact IDs |

**Input must come from:** `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` output (`SCMJackknifeNullMonitorPromotionEvidencePacket`).

---

## 6. Conceptual output object

**`SCMJackknifeNullMonitorReviewDecision`**

| Field | Description |
|-------|-------------|
| `decision_id` | Unique decision identifier |
| `instrument_identity` | Canonical identity (§3) |
| `catalog_alias` | Preserved alias if present; not substituted for identity |
| `decision_status` | One of §7 statuses |
| `decision_scope` | `null_monitor` |
| `decision_surface` | Governed decision surface emitted |
| `packet_ref` | Reference to source packet |
| `evidence_summary` | Summary of evidence completeness |
| `missing_evidence` | Propagated missing categories |
| `blockers` | Propagated blockers |
| `required_followups` | Required follow-up actions |
| `allowed_next_actions` | Actions permitted by this decision |
| `prohibited_next_actions` | Actions explicitly blocked |
| `claim_authorization_status` | Fixed non-authorization (§11) |
| `catalog_status` | Fixed non-authorization (§11) |
| `production_compatibility_status` | Fixed non-authorization (§11) |
| `method_promotion_status` | Fixed non-authorization (§11) |
| `instrument_promotion_status` | Fixed non-authorization (§11) |
| `null_monitor_scope_status` | `NULL_MONITOR_ONLY` |
| `warnings` | Decision warnings |
| `lineage` | Provenance dict |
| `created_from_artifacts` | Source artifact IDs |

---

## 7. Decision statuses

| Status | Meaning |
|--------|---------|
| `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` | Sufficient packet for null-monitor review continuation only |
| `REQUEST_ADDITIONAL_EVIDENCE` | Evidence packet incomplete or partial diagnostic only |
| `REJECT_FOR_METHOD_VALIDITY` | Method-validity evidence failed or structurally insufficient |
| `REJECT_FOR_IDENTITY_MISMATCH` | Wrong instrument or scope |
| `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` | Claim boundary missing or violated |
| `REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION` | Request exceeds null-monitor scope |
| `REJECT_FOR_UNSUPPORTED_SURFACE` | Requested surface outside null-monitor decision |
| `REJECT_FOR_CROSS_INFERENCE_FAMILY` | Not the exact jackknife instrument |
| `REJECT_FOR_CROSS_GEOMETRY` | Not single-cell geometry |
| `REJECT_FOR_CROSS_ESTIMAND` | Not delta_mu estimand scope |
| `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` | Production compatibility requested; outside this decision |
| `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` | Catalog unblock requested; outside this decision |
| `NO_DECISION_PACKET_NOT_READY` | No valid review input; assemble packet first |

**Important:** `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` permits null-monitor diagnostic review continuation only. It does **not** mean production approval, catalog unblock, method promotion, claim authorization, or production compatibility.

---

## 8. Decision mapping rules

Deterministic mapping from packet readiness, eligibility, blockers, and requested surface:

| Rule | Condition | Decision status |
|------|-----------|-----------------|
| **A** | `PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT` + `ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT` + surface ∈ `{null_monitor, diagnostic_null_monitor, restricted_review_null_monitor}` | `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` |
| **B** | `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` or `missing_evidence` non-empty | `REQUEST_ADDITIONAL_EVIDENCE` |
| **C** | `PACKET_PARTIAL_DIAGNOSTIC_ONLY` | `REQUEST_ADDITIONAL_EVIDENCE` (+ required_followups list missing categories) |
| **D** | `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` or `NOT_ELIGIBLE_IDENTITY_MISMATCH` | `REJECT_FOR_IDENTITY_MISMATCH` |
| **E** | `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` or `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` |
| **F** | `PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION` or `NOT_ELIGIBLE_NULL_MONITOR_SCOPE_VIOLATION` or `NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW` | `REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION` |
| **G** | `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | `REJECT_FOR_CROSS_INFERENCE_FAMILY` |
| **H** | `PACKET_BLOCKED_CROSS_GEOMETRY` | `REJECT_FOR_CROSS_GEOMETRY` |
| **I** | `PACKET_BLOCKED_CROSS_ESTIMAND` | `REJECT_FOR_CROSS_ESTIMAND` |
| **J** | `requested_decision_surface` ∈ `{production, production_readout, production_compatibility, prod_compatibility}` | `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` |
| **K** | `requested_decision_surface` ∈ `{catalog, catalog_unblock, catalog_promotion}` | `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` |
| **L** | `PACKET_BLOCKED_UNSUPPORTED_SURFACE` | `REJECT_FOR_UNSUPPORTED_SURFACE` |
| **M** | `PACKET_NOT_REQUESTED` or no valid packet | `NO_DECISION_PACKET_NOT_READY` |
| **N** | Blockers include method-validity failure markers: `failed_null_control_evidence`, `failed_jackknife_stability_evidence`, `failed_directional_error_evidence`, `failed_donor_pool_diagnostics`, `failed_pre_period_fit_diagnostics` | `REJECT_FOR_METHOD_VALIDITY` |

Mapping is deterministic. No statistical computation, evidence fabrication, or raw evidence quality scoring.

### Precedence (when multiple conditions apply)

1. Production/catalog surface deferrals (J, K)
2. No valid packet / not requested (M)
3. Identity mismatch (D)
4. Cross-inference / cross-geometry / cross-estimand (G, H, I)
5. Claim boundary missing (E)
6. Null-monitor scope violation (F)
7. Method-validity blockers (N)
8. Missing evidence / partial diagnostic (B, C)
9. Unsupported surface (L)
10. Ready + eligible approval (A)

---

## 9. Allowed next actions

### After `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION`

- `continue_null_monitor_diagnostics`
- `prepare_null_monitor_governance_notes`
- `collect_additional_null_control_evidence`
- `collect_additional_scm_diagnostics`
- `open_catalog_governance_review_as_separate_lane`
- `open_production_compatibility_review_as_separate_lane`

### After `REQUEST_ADDITIONAL_EVIDENCE`

- `collect_missing_evidence_refs`
- `rerun_scm_jackknife_null_monitor_packet_runtime`

### After rejects

- `repair_identity_or_scope`
- `repair_claim_boundary`
- `separate_cross_instrument_review`
- `reject_or_rework_instrument_validation`

---

## 10. Always prohibited next actions

Always prohibited by this contract:

- `scm_promotion`
- `scm_jackknife_promotion`
- `method_promotion`
- `instrument_promotion`
- `catalog_unblock`
- `production_compatibility_authorization`
- `causal_lift_claim_authorization`
- `business_lift_claim_authorization`
- `confidence_interval_claim_authorization`
- `p_value_claim_authorization`
- `statistical_significance_claim_authorization`
- `statistical_power_claim_authorization`
- `roi_roas_claim_authorization`
- `decision_recommendation_authorization`
- `production_readout_authorization`
- `mip_decision_surface_approval`
- `trust_report_bypass`
- `claim_authorization_runtime_bypass`

---

## 11. Fixed non-authorization statuses

Always emit on every decision output:

| Field | Value |
|-------|-------|
| `claim_authorization_status` | `NOT_AUTHORIZED_BY_THIS_DECISION` |
| `catalog_status` | `NOT_UNBLOCKED_BY_THIS_DECISION` |
| `production_compatibility_status` | `NOT_AUTHORIZED_BY_THIS_DECISION` |
| `method_promotion_status` | `NOT_PROMOTED_BY_THIS_DECISION` |
| `instrument_promotion_status` | `NOT_PROMOTED_BY_THIS_DECISION` |
| `null_monitor_scope_status` | `NULL_MONITOR_ONLY` |

Even `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` does not change these statuses.

---

## 12. Relationship to generalized framework

This contract is the **second instrument-family framework application** after the TBRRidge pilot. It reuses:

- Decision contract pattern
- Readiness/eligibility → decision mapping
- Exact-instrument scoping
- Non-authorization status fields
- Blocker and lineage preservation

It extends with:

- Null-monitor continuation semantics (weaker than TBRRidge restricted-review continuation)
- SCM-specific method-validity blocker names
- Catalog alias preservation without identity substitution

---

## 13. Relationship to claim authorization

- `CLAIM_AUTHORIZATION_RUNTIME_001` remains the sole package-level claim owner
- This review decision contract does **not** modify claim authorization
- Even approval only permits null-monitor review continuation — no statistical, causal, business, ROI, or decision claims

---

## 14. Relationship to catalog and production

- Catalog remains restricted/blocked unless a separate catalog governance artifact changes tier
- Production compatibility is out of scope
- Approval is **not** production readiness or catalog promotion

---

## 15. Relationship to Lane B and MIP

- Lane B spend/ROI readiness is orthogonal
- MIP DecisionSurface / TrustReport / RecommendationContract cannot be bypassed
- No MIP decisioning implemented by this contract
- Readout compatibility cannot substitute for method evidence

---

## 16. Future runtime plan

**Recommended future artifact:** `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001`

| Responsibility | Owner |
|----------------|-------|
| Consume `SCMJackknifeNullMonitorPromotionEvidencePacket` | Runtime |
| Apply deterministic decision mapping (§8) with precedence | Runtime |
| Preserve blockers, missing evidence, warnings, lineage | Runtime |
| Emit `SCMJackknifeNullMonitorReviewDecision` | Runtime |
| Promote SCM / authorize claims / unblock catalog | **No** |

---

## 17. Non-goals

- No runtime implemented
- No SCM or SCM+Jackknife promotion
- No catalog unblock or production compatibility authorization
- No claim authorization change
- No statistical / CI / p-value / significance / power claim authorization
- No causal/business lift or ROI/ROAS claim authorization
- No decision recommendation or production readout authorization
- No estimator/inference implementation or execution
- No new validation experiments
- No raw evidence quality scoring
- No Lane B runtime changes
- No MIP decisioning or TrustReport bypass

---

## 18. Validation results

- Contract doc: `docs/track_d/SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001.md`
- Summary JSON: `docs/track_d/archives/SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001_summary.json`
- Governance tests: `tests/governance/test_scm_jackknife_null_monitor_review_decision_contract_001.py`
- Safety grep: forbidden capability flags must remain `false` (except none allowed true for contract)
- Capability grep: contract completion flags must be `true`
