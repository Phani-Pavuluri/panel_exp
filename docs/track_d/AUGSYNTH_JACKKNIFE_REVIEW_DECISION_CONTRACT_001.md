# AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001` |
| **Artifact type** | `augsynth_jackknife_review_decision_contract` |
| **Lane** | **Lane A — Method / instrument promotion framework application** |
| **Status** | `completed` |
| **Scope** | `review_decision_contract_docs_only_no_runtime_no_promotion` |
| **Instrument identity** | `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| **Alias-related identity** | `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` |
| **Final verdict** | `augsynth_jackknife_review_decision_contract_defined_no_runtime_no_promotion` |
| **Recommended next** | `AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001` |

**Depends on:**

- `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001`
- `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001`
- `METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001`
- `METHOD_PROMOTION_GENERIC_CONTRACTS_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`

---

## 2. Why this contract exists

`AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` and `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` now define and assemble governed restricted-review inputs: explicit evidence references, packet readiness statuses, promotion-review eligibility statuses, blockers, warnings, and lineage for the exact AugSynth Jackknife restricted-review instrument.

The next step is a **review decision contract** that defines deterministic decision statuses and boundaries for a future decision runtime consuming `AugSynthJackknifePromotionEvidencePacket`. Without this contract, downstream artifacts could accidentally interpret packet readiness as AugSynth method promotion, catalog unblock, production compatibility, or claim authorization.

**Review decision is a governed interpretation of packet readiness and evidence completeness, not a statistical computation.** This contract does **not** implement runtime. This contract does **not** approve AugSynth as a method. This contract only defines whether a packet may continue as restricted-review governance input.

---

## 3. Exact identity and alias boundary

**Canonical governed identity:** `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review`

**Alias-related / non-substitutable identity:** `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only`

| Field | Value |
|-------|-------|
| `modality` | `geo` |
| `estimator_family` | `augsynth` |
| `inference_family` | `jackknife` |
| `geometry` | `single_cell` |
| `point_estimand` | `delta_mu` |
| `interval_semantics` | `diagnostic_interval` |
| `surface` | `restricted_review` |

**Identity rules:**

- Canonical identity required on all decision inputs
- `research_only` cannot substitute `restricted_review`
- `research_interval` cannot substitute `diagnostic_interval`
- Alias-related identity may appear in lineage only; alias cannot substitute canonical identity
- Alias/research-only substitution must reject with dedicated decision statuses
- No cross-inference-family inheritance (e.g. placebo, bootstrap, conformal)
- No cross-geometry inheritance (e.g. aggregate_pooled, multi_cell)
- No cross-estimand inheritance
- TBRRidge/SCM pilot evidence/decisions do not inherit to this instrument

---

## 4. Decision input contract

Conceptual input object: **`AugSynthJackknifeReviewDecisionInput`**

| Field | Description |
|-------|-------------|
| `decision_id` | Unique decision request identifier |
| `packet_ref` | Reference to assembled evidence packet |
| `packet_readiness_status` | From packet assembly runtime |
| `promotion_review_eligibility_status` | From packet assembly runtime |
| `instrument_identity` | Canonical identity (§3) |
| `alias_related_identity` | Alias-related identity preserved for lineage |
| `evidence_by_category` | Grouped evidence references from packet |
| `missing_evidence` | Missing required evidence categories |
| `blockers` | Active blocker codes from packet |
| `warnings` | Packet warnings |
| `requested_decision_surface` | Requested decision surface (default `restricted_review`) |
| `reviewer_notes` | Optional reviewer notes |
| `lineage` | Provenance dict |
| `created_from_artifacts` | Source artifact IDs |

**Produced by:** `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` output (`AugSynthJackknifePromotionEvidencePacket`).

---

## 5. Decision output contract

Conceptual output object: **`AugSynthJackknifeReviewDecision`**

| Field | Description |
|-------|-------------|
| `decision_id` | Unique decision identifier |
| `instrument_identity` | Canonical identity (§3) |
| `alias_related_identity` | Preserved alias-related identity; not substituted for canonical |
| `decision_status` | One of §6 statuses |
| `decision_scope` | `restricted_review` |
| `decision_surface` | Governed decision surface emitted |
| `packet_ref` | Reference to source packet |
| `evidence_summary` | Summary of evidence completeness |
| `missing_evidence` | Propagated missing categories |
| `blockers` | Propagated blockers |
| `required_followups` | Required follow-up actions |
| `allowed_next_actions` | Actions permitted by this decision |
| `prohibited_next_actions` | Actions explicitly blocked |
| `claim_authorization_status` | Fixed non-authorization (§12) |
| `catalog_status` | Fixed non-authorization (§12) |
| `production_compatibility_status` | Fixed non-authorization (§12) |
| `method_promotion_status` | Fixed non-authorization (§12) |
| `instrument_promotion_status` | Fixed non-authorization (§12) |
| `generic_adapter_status` | Fixed non-authorization (§12) |
| `mip_decisioning_status` | Fixed non-authorization (§12) |
| `trust_report_bypass_status` | Fixed non-authorization (§12) |
| `warnings` | Decision warnings |
| `lineage` | Provenance dict |
| `created_from_artifacts` | Source artifact IDs |

---

## 6. Decision statuses

| Status | Meaning |
|--------|---------|
| `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | Sufficient packet for AugSynth restricted-review governance continuation only |
| `REQUEST_ADDITIONAL_EVIDENCE` | Evidence packet incomplete or partial diagnostic only |
| `REJECT_FOR_METHOD_VALIDITY` | Method-validity evidence failed or structurally insufficient |
| `REJECT_FOR_IDENTITY_MISMATCH` | Wrong instrument or scope |
| `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` | Claim boundary missing or violated |
| `REJECT_FOR_SCOPE_VIOLATION` | Request exceeds restricted-review scope |
| `REJECT_FOR_ALIAS_SUBSTITUTION` | Alias-related identity attempted to substitute canonical |
| `REJECT_FOR_RESEARCH_ONLY_SUBSTITUTION` | Research-only identity attempted to substitute restricted-review |
| `REJECT_FOR_UNSUPPORTED_SURFACE` | Requested surface outside restricted-review decision |
| `REJECT_FOR_CROSS_INFERENCE_FAMILY` | Not the exact jackknife instrument |
| `REJECT_FOR_CROSS_GEOMETRY` | Not single-cell geometry |
| `REJECT_FOR_CROSS_ESTIMAND` | Not delta_mu estimand scope |
| `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` | Production compatibility requested; outside this decision |
| `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` | Catalog unblock requested; outside this decision |
| `NO_DECISION_PACKET_NOT_READY` | No valid review input; assemble packet first |

**Important:** `APPROVE_RESTRICTED_REVIEW_CONTINUATION` is the **only positive decision**. It permits restricted-review governance continuation only. It does **not** mean AugSynth promotion, method promotion, instrument promotion, catalog unblock, production compatibility, claim authorization, or production readout.

---

## 7. Decision mapping

Deterministic mapping from packet readiness, eligibility, blockers, missing evidence, and requested surface:

| Rule | Condition | Decision status |
|------|-----------|-----------------|
| **A** | `requested_decision_surface` ∈ `{production, production_readout, production_compatibility}` | `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` |
| **B** | `requested_decision_surface` ∈ `{catalog, catalog_unblock, catalog_promotion}` | `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` |
| **C** | `packet_readiness_status == PACKET_NOT_REQUESTED` or packet missing | `NO_DECISION_PACKET_NOT_READY` |
| **D** | `packet_readiness_status == PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT` or `promotion_review_eligibility_status == NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION` | `REJECT_FOR_RESEARCH_ONLY_SUBSTITUTION` |
| **E** | `packet_readiness_status == PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT` or `promotion_review_eligibility_status == NOT_ELIGIBLE_ALIAS_SUBSTITUTION` | `REJECT_FOR_ALIAS_SUBSTITUTION` |
| **F** | `packet_readiness_status == PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` or `promotion_review_eligibility_status == NOT_ELIGIBLE_IDENTITY_MISMATCH` | `REJECT_FOR_IDENTITY_MISMATCH` |
| **G** | `packet_readiness_status == PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | `REJECT_FOR_CROSS_INFERENCE_FAMILY` |
| **H** | `packet_readiness_status == PACKET_BLOCKED_CROSS_GEOMETRY` | `REJECT_FOR_CROSS_GEOMETRY` |
| **I** | `packet_readiness_status == PACKET_BLOCKED_CROSS_ESTIMAND` | `REJECT_FOR_CROSS_ESTIMAND` |
| **J** | `packet_readiness_status == PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` or `promotion_review_eligibility_status == NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` |
| **K** | `packet_readiness_status == PACKET_BLOCKED_SCOPE_VIOLATION` or `promotion_review_eligibility_status == NOT_ELIGIBLE_SCOPE_VIOLATION` | `REJECT_FOR_SCOPE_VIOLATION` |
| **L** | Blockers include any of: `failed_null_control_evidence`, `failed_directional_error_evidence`, `failed_positive_control_recovery_evidence`, `failed_sensitivity_evidence`, `failed_donor_pool_diagnostics`, `failed_pre_period_fit_diagnostics`, `failed_augmentation_component_diagnostics`, `failed_synthetic_weight_diagnostics`, `failed_regularization_or_model_component_diagnostics`, `failed_jackknife_stability`, `failed_method_disagreement_or_scm_bridge`, `failed_support_overlap_or_donor_hull_stress` | `REJECT_FOR_METHOD_VALIDITY` |
| **M** | `packet_readiness_status` ∈ `{PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE, PACKET_PARTIAL_DIAGNOSTIC_ONLY}` or `missing_evidence` non-empty | `REQUEST_ADDITIONAL_EVIDENCE` |
| **N** | `packet_readiness_status == PACKET_BLOCKED_UNSUPPORTED_SURFACE` | `REJECT_FOR_UNSUPPORTED_SURFACE` |
| **O** | `packet_readiness_status == PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` and `promotion_review_eligibility_status == ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT` and `requested_decision_surface` ∈ `{restricted_review, diagnostic_restricted_review, augsynth_restricted_review}` | `APPROVE_RESTRICTED_REVIEW_CONTINUATION` |
| **P** | Fallback | `NO_DECISION_PACKET_NOT_READY` |

Mapping is deterministic. No statistical computation, evidence fabrication, or raw evidence quality scoring.

---

## 8. Decision precedence

When multiple conditions apply, apply exact precedence:

1. Production/catalog surface deferrals (A, B)
2. No packet / packet not requested (C)
3. Research-only substitution (D)
4. Alias substitution (E)
5. Identity mismatch (F)
6. Cross-inference / cross-geometry / cross-estimand (G, H, I)
7. Claim boundary missing (J)
8. Scope violation (K)
9. Method-validity blockers (L)
10. Missing evidence / partial diagnostic (M)
11. Unsupported surface (N)
12. Ready + eligible approval (O)
13. Fallback no decision (P)

---

## 9. Positive decision semantics

**`APPROVE_RESTRICTED_REVIEW_CONTINUATION` means:**

- Packet may continue as AugSynth restricted-review governance input
- Future review runtime may proceed to generic adapter only after decision runtime exists
- Additional evidence collection may continue

**It does not mean:**

- AugSynth method promotion
- AugSynth instrument promotion
- Catalog unblock
- Production compatibility
- Claim authorization
- Production readout
- Confidence interval validity
- Statistical significance
- Causal/business lift validity
- ROI/ROAS readiness
- MIP DecisionSurface approval
- TrustReport bypass

---

## 10. Allowed next actions

### After `APPROVE_RESTRICTED_REVIEW_CONTINUATION`

- `continue_augsynth_restricted_review_diagnostics`
- `prepare_augsynth_governance_notes`
- `collect_additional_augsynth_diagnostics`
- `collect_additional_null_control_evidence`
- `collect_additional_donor_pool_evidence`
- `collect_additional_pre_period_fit_evidence`
- `open_catalog_governance_review_as_separate_lane`
- `open_production_compatibility_review_as_separate_lane`
- `open_claim_authorization_review_as_separate_lane`

### After `REQUEST_ADDITIONAL_EVIDENCE`

- `collect_missing_evidence_refs`
- `rerun_augsynth_jackknife_packet_runtime`

### After substitution/identity rejects

- `repair_identity_or_scope`
- `remove_alias_or_research_only_substitution`
- `separate_cross_instrument_review`

### After method validity reject

- `reject_or_rework_augsynth_validation`

---

## 11. Always prohibited actions

Always prohibit:

- `augsynth_promotion`
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
- `generic_adapter_profile_for_augsynth_registration`
- `mip_decision_surface_approval`
- `trust_report_bypass`
- `claim_authorization_runtime_bypass`

---

## 12. Fixed non-authorization statuses

Always emit on every decision output:

| Field | Value |
|-------|-------|
| `claim_authorization_status` | `NOT_AUTHORIZED_BY_THIS_DECISION` |
| `catalog_status` | `NOT_UNBLOCKED_BY_THIS_DECISION` |
| `production_compatibility_status` | `NOT_AUTHORIZED_BY_THIS_DECISION` |
| `method_promotion_status` | `NOT_PROMOTED_BY_THIS_DECISION` |
| `instrument_promotion_status` | `NOT_PROMOTED_BY_THIS_DECISION` |
| `generic_adapter_status` | `NOT_REGISTERED_BY_THIS_DECISION` |
| `mip_decisioning_status` | `NOT_AUTHORIZED_BY_THIS_DECISION` |
| `trust_report_bypass_status` | `NOT_BYPASSED_BY_THIS_DECISION` |

---

## 13. Evidence quality boundary

**Decision contract may use:**

- Packet readiness
- Eligibility
- Missing evidence
- Blockers
- Identity
- Alias/research-only markers
- Warnings
- Lineage
- Requested surface

**Decision contract may not:**

- Inspect raw evidence contents
- Score evidence quality
- Decide donor pool adequacy
- Decide pre-period fit quality
- Decide augmentation component quality
- Decide synthetic weight quality
- Run AugSynth
- Run jackknife
- Compute statistics
- Infer causal validity

---

## 14. Generic framework compatibility

| AugSynth decision | Generic mapping |
|-------------------|-----------------|
| `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | `APPROVE_REVIEW_CONTINUATION` with `decision_scope=restricted_review` |
| `REQUEST_ADDITIONAL_EVIDENCE` | `REQUEST_ADDITIONAL_EVIDENCE` |
| Alias/research-only substitution rejects | Scope/identity reject families |
| `REJECT_FOR_METHOD_VALIDITY` | `REJECT_FOR_METHOD_VALIDITY` |

AugSynth should **not** be added to `METHOD_PROMOTION_GENERIC_RUNTIME_001` until the decision runtime exists and passes governance.

---

## 15. Relationships and boundaries

| Relationship | Boundary |
|--------------|----------|
| **Packet runtime** | Source of packet readiness/eligibility; decision consumes `AugSynthJackknifePromotionEvidencePacket` only |
| **Generic runtime** | Not yet registered for AugSynth; no generic adapter profile |
| **TBRRidge/SCM** | Framework precedents only; no evidence/decision inheritance |
| **Claim authorization runtime** | Unchanged; sole claim owner remains `CLAIM_AUTHORIZATION_RUNTIME_001` |
| **Catalog governance** | Separate lane; catalog remains blocked unless separate artifact unblocks |
| **Production compatibility** | Separate lane; production compatibility is out of scope |
| **Lane B spend/ROI** | Orthogonal; cannot satisfy method validity or promotion decision |
| **MIP** | Cannot authorize DecisionSurface, TrustReport, or RecommendationContract |

---

## 16. Recommended next artifact

**`AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001`**

**Scope:**

- Implement deterministic decision runtime from this contract
- Consume AugSynth packet runtime output
- No promotion
- No claim authorization
- No generic adapter profile yet

---

## 17. Non-goals

- No runtime implemented
- No AugSynth decision runtime implemented
- No generic runtime changes
- No generic adapter profile for AugSynth implemented
- No method promoted
- No instrument promoted
- No AugSynth promotion
- No DID promotion
- No catalog unblock
- No production compatibility authorization
- No claim authorization change
- No statistical claim authorization
- No CI/p-value/significance/power claim authorization
- No causal/business lift claim authorization
- No ROI/ROAS claim authorization
- No decision recommendation authorization
- No production readout authorization
- No estimator/inference implementation
- No new validation experiments
- No raw evidence quality scoring
- No Lane B runtime changes
- No MIP decisioning
- No TrustReport bypass

---

## 18. Validation results

- Contract: `docs/track_d/AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001.md`
- Summary: `docs/track_d/archives/AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001_summary.json`
- Governance tests: `tests/governance/test_augsynth_jackknife_review_decision_contract_001.py`
- Safety grep: no forbidden `true` flags in contract/summary
- Capability grep: all required capability flags present
