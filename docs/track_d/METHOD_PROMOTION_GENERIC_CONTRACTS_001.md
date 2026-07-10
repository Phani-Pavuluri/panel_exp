# METHOD_PROMOTION_GENERIC_CONTRACTS_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PROMOTION_GENERIC_CONTRACTS_001` |
| **Artifact type** | `method_promotion_generic_contracts` |
| **Lane** | Lane A — Method / instrument promotion framework generic contracts |
| **Status** | `completed` |
| **Scope** | `generic_contracts_docs_only_no_runtime_no_promotion` |
| **Final verdict** | `generic_method_promotion_contracts_defined_no_runtime_no_promotion` |
| **Recommended next** | `METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001` |

**Depends on:**

- `METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001`
- `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001`
- `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001`
- `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`

---

## 2. Why this artifact exists

TBRRidge restricted-review and SCM null-monitor proved the method promotion review framework pattern end-to-end. `METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001` recommended **`PAUSE_NEW_INSTRUMENT_LANES_AND_FORMALIZE_GENERIC_CONTRACTS`**.

Repeated contract/runtime structures are now visible across both applications. Adding AugSynth/DID instrument lanes before formalizing shared vocabulary would increase copy-paste drift in status enums, boundary fields, prohibited actions, and precedence rules.

This artifact defines **generic conceptual contracts and vocabulary only**. It does not implement runtime, generic dataclasses in `panel_exp`, or modify existing TBRRidge/SCM runtimes. Future instrument-specific artifacts should plug into these abstractions.

---

## 3. Contract design principles

- **Exact-instrument scoped by default** — promotion review applies to one canonical identity unless a separate family-level artifact explicitly authorizes broader scope
- **No method-family inheritance** — cross-inference, cross-geometry, cross-estimand, and cross-surface inheritance blocked unless separately authorized
- **Packet readiness is not promotion** — a ready packet is review input only
- **Review decision is not claim authorization** — positive decision means review continuation on the stated surface only
- **Catalog and production require separate lanes** — deferrals route to catalog governance or production compatibility review
- **Evidence references are pointers, not quality judgments** — refs certify category presence and artifact linkage, not evidence quality
- **Runtime must preserve lineage/warnings/blockers** — decision outputs merge and pass through packet state
- **Instrument-specific contracts may extend but not weaken generic boundaries** — extensions add categories/statuses; cannot remove prohibited actions or non-authorization statuses
- **MIP/TrustReport/DecisionSurface cannot be bypassed** — generic contracts do not authorize readout, business decisions, or MIP surfaces

---

## 4. Generic object: MethodPromotionInstrumentIdentity

**Conceptual fields:**

| Field | Description |
|-------|-------------|
| `identity_id` | Stable identifier for the identity record |
| `modality` | Domain/modality (e.g. `geo`) |
| `estimator_family` | Estimator family (e.g. `tbrridge`, `scm`) |
| `inference_family` | Inference family (e.g. `kfold`, `jackknife`) |
| `geometry` | Unit/aggregation geometry (e.g. `single_cell`) |
| `point_estimand` | Point estimand (e.g. `delta_mu`) |
| `interval_semantics` | Interval semantics (e.g. `diagnostic_interval`) — optional |
| `surface` | Review/readout surface (e.g. `restricted_review`, `null_monitor`) |
| `metric_family` | Optional metric family |
| `aggregation_level` | Optional aggregation level |
| `design_family` | Optional design family |
| `assignment_family` | Optional assignment family |
| `readout_surface` | Optional readout surface |
| `catalog_tier` | Optional catalog tier |
| `aliases` | Optional catalog or legacy aliases (list) |
| `canonical_identity_string` | Governed dotted identity string |

**Rules:**

- Canonical identity is the governed identity used in promotion review
- Aliases may be preserved but **cannot substitute** canonical identity in decision output
- Cross-inference/geometry/estimand/surface inheritance is blocked by default
- Family-level promotion requires a separate explicit artifact

**Examples:**

- `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review`
- `geo.scm.jackknife.single_cell.delta_mu.null_monitor`

---

## 5. Generic object: MethodPromotionEvidenceReference

**Conceptual fields:**

| Field | Description |
|-------|-------------|
| `evidence_id` | Stable evidence reference identifier |
| `evidence_category` | Category name (must match required/optional registry) |
| `artifact_ref` | Path or URI to governing artifact |
| `instrument_identity` | Identity the evidence applies to |
| `evidence_surface` | Surface the evidence supports |
| `source_family` | Estimator/inference family of source |
| `source_lane` | Lane that produced evidence (e.g. Lane A, Lane B) |
| `source_artifact_type` | Type of source artifact |
| `notes` | Optional reviewer notes |
| `metadata` | Optional structured metadata (non-scoring) |

**Rules:**

- `artifact_ref` must be non-empty to satisfy an evidence category
- Category names must match declared required categories for the instrument
- Evidence references do **not** certify quality, fit, or validity
- Wrong instrument/family/lane cannot satisfy required categories unless explicitly mapped in instrument contract
- Lane B spend/ROI evidence **cannot** satisfy method-validity evidence categories

---

## 6. Generic object: MethodPromotionEvidencePacket

**Conceptual fields:**

| Field | Description |
|-------|-------------|
| `packet_id` | Stable packet identifier |
| `instrument_identity` | Canonical `MethodPromotionInstrumentIdentity` |
| `aliases` | Preserved aliases (separate from canonical) |
| `evidence_by_category` | Map category → evidence references |
| `required_evidence_categories` | Declared required categories for this instrument |
| `optional_evidence_categories` | Declared optional categories |
| `missing_evidence` | Categories not satisfied |
| `blockers` | Blocking conditions |
| `warnings` | Non-blocking warnings |
| `packet_readiness_status` | `MethodPromotionPacketReadinessStatus` |
| `promotion_review_eligibility_status` | `MethodPromotionReviewEligibilityStatus` |
| `allowed_surfaces` | Surfaces permitted for this packet |
| `prohibited_surfaces` | Surfaces explicitly blocked |
| `boundary_statuses` | `MethodPromotionBoundaryStatus` |
| `lineage` | Provenance dict |
| `created_from_artifacts` | Artifacts that contributed to packet |

**Rules:**

- Packet is **review input only** — not promotion, not claim authorization
- Packet readiness does not equal promotion
- Packet may be complete but still non-authorizing (boundary statuses remain negative)
- Packet runtime may validate reference presence/category/identity only unless instrument-specific contract says otherwise
- Raw evidence quality scoring belongs elsewhere, not in generic packet assembly

---

## 7. Generic enum family: MethodPromotionPacketReadinessStatus

| Status | Meaning |
|--------|---------|
| `PACKET_READY_FOR_REVIEW_INPUT` | Sufficient evidence for review input |
| `PACKET_PARTIAL_DIAGNOSTIC_ONLY` | Partial evidence; diagnostic only |
| `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` | Missing required categories |
| `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` | Claim boundary evidence missing |
| `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` | Identity mismatch |
| `PACKET_BLOCKED_UNSUPPORTED_SURFACE` | Unsupported surface requested |
| `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | Cross-inference family violation |
| `PACKET_BLOCKED_CROSS_GEOMETRY` | Cross-geometry violation |
| `PACKET_BLOCKED_CROSS_ESTIMAND` | Cross-estimand violation |
| `PACKET_BLOCKED_SCOPE_VIOLATION` | Surface/scope violation |
| `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` | Production compatibility not yet in scope |
| `PACKET_NOT_REQUESTED` | No packet assembly requested |

**Instrument-specific mappings:**

| Instrument-specific | Generic |
|---------------------|---------|
| TBRRidge `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` | `PACKET_READY_FOR_REVIEW_INPUT` |
| SCM `PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT` | `PACKET_READY_FOR_REVIEW_INPUT` |
| SCM `PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION` | `PACKET_BLOCKED_SCOPE_VIOLATION` |

---

## 8. Generic enum family: MethodPromotionReviewEligibilityStatus

| Status | Meaning |
|--------|---------|
| `ELIGIBLE_AS_REVIEW_INPUT` | Eligible for review decision input on declared surface |
| `NOT_ELIGIBLE_MISSING_EVIDENCE` | Missing required evidence |
| `NOT_ELIGIBLE_IDENTITY_MISMATCH` | Identity mismatch |
| `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | Claim boundary missing |
| `NOT_ELIGIBLE_SCOPE_VIOLATION` | Scope/surface violation |
| `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` | Production review out of scope |
| `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` | Catalog unblock out of scope |
| `NOT_ELIGIBLE_FOR_CLAIM_REVIEW` | Causal/statistical claim review out of scope |

**Instrument-specific mappings:**

| Instrument-specific | Generic |
|---------------------|---------|
| TBRRidge `ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT` | `ELIGIBLE_AS_REVIEW_INPUT` |
| SCM `ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT` | `ELIGIBLE_AS_REVIEW_INPUT` |
| SCM `NOT_ELIGIBLE_NULL_MONITOR_SCOPE_VIOLATION` | `NOT_ELIGIBLE_SCOPE_VIOLATION` |
| SCM `NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW` | `NOT_ELIGIBLE_FOR_CLAIM_REVIEW` |

---

## 9. Generic object: MethodPromotionReviewDecision

**Conceptual fields:**

| Field | Description |
|-------|-------------|
| `decision_id` | Stable decision identifier |
| `instrument_identity` | Canonical identity |
| `aliases` | Preserved aliases |
| `decision_status` | `MethodPromotionReviewDecisionStatus` |
| `decision_scope` | Scope label (e.g. `restricted_review`, `null_monitor`) |
| `decision_surface` | Requested decision surface |
| `packet_ref` | Reference to source packet |
| `evidence_summary` | Non-scoring summary of packet evidence metadata |
| `missing_evidence` | Preserved from packet |
| `blockers` | Preserved from packet |
| `required_followups` | Required next steps |
| `allowed_next_actions` | `MethodPromotionAllowedAction` list |
| `prohibited_next_actions` | `MethodPromotionProhibitedAction` list |
| `boundary_statuses` | `MethodPromotionBoundaryStatus` |
| `warnings` | Merged warnings |
| `lineage` | Merged lineage |
| `created_from_artifacts` | Contributing artifacts |

**Rules:**

- Review decision consumes packet state
- Preserves blockers, missing evidence, warnings, lineage from packet and input
- Positive decision only means the stated **review continuation** on `decision_scope`
- Positive decision does **not** promote, unblock catalog, authorize claims, or approve production

---

## 10. Generic enum family: MethodPromotionReviewDecisionStatus

| Status | Meaning |
|--------|---------|
| `APPROVE_REVIEW_CONTINUATION` | Continue review on declared scope/surface |
| `REQUEST_ADDITIONAL_EVIDENCE` | Missing or partial evidence |
| `REJECT_FOR_METHOD_VALIDITY` | Method-validity blocker present |
| `REJECT_FOR_IDENTITY_MISMATCH` | Identity mismatch |
| `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` | Claim boundary missing |
| `REJECT_FOR_SCOPE_VIOLATION` | Scope/surface violation |
| `REJECT_FOR_UNSUPPORTED_SURFACE` | Unsupported surface |
| `REJECT_FOR_CROSS_INFERENCE_FAMILY` | Cross-inference violation |
| `REJECT_FOR_CROSS_GEOMETRY` | Cross-geometry violation |
| `REJECT_FOR_CROSS_ESTIMAND` | Cross-estimand violation |
| `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` | Production surface deferred |
| `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` | Catalog surface deferred |
| `NO_DECISION_PACKET_NOT_READY` | Packet not ready |

**Instrument-specific positive mappings:**

| Instrument-specific | Generic |
|---------------------|---------|
| TBRRidge `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | `APPROVE_REVIEW_CONTINUATION` with `decision_scope=restricted_review` |
| SCM `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` | `APPROVE_REVIEW_CONTINUATION` with `decision_scope=null_monitor` |

---

## 11. Generic object: MethodPromotionBoundaryStatus

**Fields:**

| Field | Fixed non-authorization values |
|-------|-------------------------------|
| `claim_authorization_status` | `NOT_AUTHORIZED_BY_THIS_DECISION` |
| `catalog_status` | `NOT_UNBLOCKED_BY_THIS_DECISION` |
| `production_compatibility_status` | `NOT_AUTHORIZED_BY_THIS_DECISION` |
| `method_promotion_status` | `NOT_PROMOTED_BY_THIS_DECISION` |
| `instrument_promotion_status` | `NOT_PROMOTED_BY_THIS_DECISION` |
| `scope_status` | `SCOPE_ONLY` / `REVIEW_ONLY` / `NULL_MONITOR_ONLY` / `RESTRICTED_REVIEW_ONLY` |

Instrument-specific contracts set `scope_status` to the appropriate scope-only label. Generic contracts require all boundary fields to remain non-authorizing unless a separate authorized artifact changes them.

---

## 12. Generic allowed/prohibited actions

**MethodPromotionAllowedAction examples:**

- `continue_review_diagnostics`
- `prepare_governance_notes`
- `collect_additional_evidence`
- `rerun_packet_runtime`
- `open_catalog_governance_review_as_separate_lane`
- `open_production_compatibility_review_as_separate_lane`
- `open_claim_authorization_review_as_separate_lane`

**MethodPromotionProhibitedAction (always include):**

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

Instrument-specific contracts may add surface-specific allowed actions (e.g. `continue_null_monitor_diagnostics`) but must preserve the full prohibited list.

---

## 13. Generic precedence rules

Default decision precedence (instrument-specific contracts may refine but not weaken):

1. Production/catalog surface deferrals
2. No packet / packet not requested
3. Identity mismatch
4. Cross-inference / cross-geometry / cross-estimand
5. Claim boundary missing
6. Scope violation
7. Method-validity blockers
8. Missing evidence / partial diagnostic
9. Unsupported surface
10. Ready + eligible approval
11. Fallback → no decision

---

## 14. Generic evidence quality boundary

Generic packet/runtime contracts **may check:**

- Identity alignment
- Category presence
- `artifact_ref` presence
- Blocker presence
- Missing evidence lists
- Warnings and lineage
- Allowed/requested surface

They **must not:**

- Score raw evidence quality
- Judge model fit (donor pool, pre-period fit, jackknife stability quality, etc.)
- Compute estimates
- Run estimator/inference
- Run new validation experiments
- Certify method validity

Method validity is indicated only by explicit blocker markers in packet state, not by runtime judgment of evidence contents.

---

## 15. Mapping from completed applications

| Generic concept | TBRRidge | SCM null-monitor |
|-----------------|----------|------------------|
| **Instrument identity** | `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` | `geo.scm.jackknife.single_cell.delta_mu.null_monitor` (+ catalog alias) |
| **Evidence reference** | `TBRRidgeEvidenceReference` | `SCMJackknifeNullMonitorEvidenceReference` |
| **Evidence packet** | `TBRRidgePromotionEvidencePacket` | `SCMJackknifeNullMonitorPromotionEvidencePacket` |
| **Readiness (ready)** | `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` | `PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT` |
| **Eligibility (eligible)** | `ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT` | `ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT` |
| **Review decision** | `TBRRidgePromotionReviewDecision` | `SCMJackknifeNullMonitorReviewDecision` |
| **Decision (positive)** | `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` |
| **Boundary scope** | implicit restricted-review | `NULL_MONITOR_ONLY` |
| **Allowed action** | `continue_restricted_review_diagnostics` | `continue_null_monitor_diagnostics` |
| **Prohibited actions** | universal list + TBRRidge-specific | universal list + SCM-specific |
| **Evidence quality boundary** | packet metadata only | packet metadata only |

---

## 16. Required compatibility for future instrument-specific artifacts

Future instrument-specific packet/review artifacts **must:**

- Declare canonical identity and aliases separately
- Declare required and optional evidence categories
- Map instrument-specific readiness/eligibility/decision statuses to generic statuses
- Preserve generic prohibited actions in full
- Preserve non-authorization boundary statuses
- Preserve exact-instrument scoping (no family inheritance)
- State evidence quality boundary explicitly
- Name next runtime/contract artifact explicitly
- Update roadmap, MIP audit registry, and OPEN_INVESTIGATIONS

---

## 17. Relationship to claim authorization / catalog / production / Lane B / MIP

- **`CLAIM_AUTHORIZATION_RUNTIME_001`** remains sole package-level claim owner
- Catalog unblock requires separate catalog governance lane
- Production compatibility requires separate production compatibility artifact
- Lane B spend/ROI readiness is orthogonal; cannot substitute method-validity categories
- MIP DecisionSurface / TrustReport / RecommendationContract cannot be bypassed
- Generic contracts do not authorize readout, business decisions, or ROI claims

---

## 18. Future runtime plan

**Recommended next artifact:** `METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001`

Define, still docs/tests-only, how a future runtime would adapt instrument-specific packet/decision outputs into generic framework summaries **without replacing** instrument-specific runtimes.

No runtime yet.

---

## 19. Non-goals

This artifact does **not**:

- Implement runtime, generic runtime, or generic dataclasses in `panel_exp`
- Promote any method, instrument, TBRRidge, SCM, AugSynth, or DID
- Unblock catalog or authorize production compatibility
- Change claim authorization or authorize statistical/causal/business/ROI claims
- Authorize decision recommendations or production readout
- Implement estimator/inference behavior
- Run new validation experiments or score raw evidence quality
- Modify Lane B runtime, implement MIP decisioning, or bypass TrustReport

---

## 20. Validation results

- Contract doc: `docs/track_d/METHOD_PROMOTION_GENERIC_CONTRACTS_001.md`
- Summary JSON: `docs/track_d/archives/METHOD_PROMOTION_GENERIC_CONTRACTS_001_summary.json`
- Governance tests: `tests/governance/test_method_promotion_generic_contracts_001.py`

Capability flags (all true): `generic_contracts_defined`, `instrument_identity_contract_defined`, `evidence_reference_contract_defined`, `evidence_packet_contract_defined`, `review_decision_contract_defined`, `generic_precedence_rules_defined`, `evidence_quality_boundary_defined`, `completed_applications_mapped_to_generic_contracts`.
