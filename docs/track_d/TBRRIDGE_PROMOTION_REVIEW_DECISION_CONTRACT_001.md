# TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001` |
| **Artifact type** | `tbrridge_promotion_review_decision_contract` |
| **Lane** | **Lane A — Method / instrument promotion** |
| **Status** | `completed` |
| **Scope** | `review_decision_contract_defined_no_runtime_no_promotion` |
| **Instrument identity** | `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| **Final verdict** | `tbrridge_promotion_review_decision_contract_defined_no_runtime_no_promotion` |
| **Recommended next** | `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001` |

**Depends on:**

- `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001`
- `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001`
- `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`
- `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001`
- `METHOD_INSTRUMENT_CATALOG_TRIAGE_AUDIT_001`

---

## 2. Why this contract exists

`TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001` and `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` now define and assemble governed review inputs: explicit evidence references, packet readiness statuses, promotion-review eligibility statuses, blockers, and lineage for the exact restricted-review TBRRidge KFold instrument.

The next step is to define the **allowed review decision surface** — what a future review decision may say after consuming a completed `TBRRidgePromotionEvidencePacket`. Without this contract, downstream artifacts could accidentally interpret packet readiness as method promotion, catalog unblock, production compatibility, or claim authorization.

**Review decision is a governed interpretation of packet readiness and evidence completeness, not a statistical computation.** This contract is docs-only; no runtime is implemented here.

---

## 3. Exact instrument scope

**Full identity:** `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review`

| Field | Value |
|-------|-------|
| `modality` | `geo` |
| `estimator_family` | `tbrridge` |
| `inference_family` | `kfold` |
| `geometry` | `single_cell` |
| `estimand` | `delta_mu` |
| `interval_semantics` | `diagnostic_interval` |
| `surface` | `restricted_review` |

**Scope constraints:**

- No estimator-family promotion (TBRRidge family-wide)
- No global TBRRidge promotion
- No cross-inference-family decision (e.g. Jackknife, Bootstrap, Conformal)
- No cross-geometry decision (e.g. aggregate_pooled, multi_cell)
- No production/catalog decision within this contract

---

## 4. Required input

Conceptual input object: **`TBRRidgePromotionReviewDecisionInput`**

| Field | Description |
|-------|-------------|
| `decision_id` | Unique decision request identifier |
| `packet_ref` | Reference to assembled evidence packet |
| `packet_readiness_status` | From packet assembly runtime |
| `promotion_review_eligibility_status` | From packet assembly runtime |
| `instrument_identity` | Exact identity string (§3) |
| `evidence_by_category` | Grouped evidence references from packet |
| `missing_evidence` | Missing required evidence categories |
| `blockers` | Active blocker codes from packet |
| `warnings` | Packet warnings |
| `requested_decision_surface` | Requested decision surface (default `restricted_review`) |
| `reviewer_notes` | Optional reviewer notes |
| `lineage` | Provenance dict |
| `created_from_artifacts` | Source artifact IDs |

**Input must come from:** `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` output (`TBRRidgePromotionEvidencePacket`).

Valid packet readiness inputs include:

- `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT`
- `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE`
- `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING`
- `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH`
- `PACKET_BLOCKED_UNSUPPORTED_SURFACE`
- `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY`
- `PACKET_BLOCKED_CROSS_GEOMETRY`
- `PACKET_NOT_REQUESTED`

---

## 5. Review decision object

Conceptual output object: **`TBRRidgePromotionReviewDecision`**

| Field | Description |
|-------|-------------|
| `decision_id` | Unique decision identifier |
| `instrument_identity` | Exact identity string (§3) |
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
| `claim_authorization_status` | `NOT_AUTHORIZED` / `NOT_EVALUATED` |
| `catalog_status` | `BLOCKED` / `RESTRICTED` |
| `production_compatibility_status` | `NOT_REVIEWED` / `DEFERRED` |
| `method_promotion_status` | `NOT_PROMOTED` |
| `instrument_promotion_status` | `NOT_PROMOTED` |
| `warnings` | Decision warnings |
| `lineage` | Provenance dict |
| `created_from_artifacts` | Source artifact IDs |

---

## 6. Decision statuses

| Status | Meaning |
|--------|---------|
| `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | Sufficient packet for restricted-review lane continuation only |
| `REQUEST_ADDITIONAL_EVIDENCE` | Evidence packet incomplete |
| `REJECT_FOR_METHOD_VALIDITY` | Method-validity evidence insufficient for continuation |
| `REJECT_FOR_IDENTITY_MISMATCH` | Wrong instrument or scope |
| `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` | Claim boundary missing or violated |
| `REJECT_FOR_UNSUPPORTED_SURFACE` | Requested surface outside restricted-review |
| `REJECT_FOR_CROSS_INFERENCE_FAMILY` | Not the exact kfold instrument |
| `REJECT_FOR_CROSS_GEOMETRY` | Not single-cell geometry |
| `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` | Production compatibility requested; outside this decision |
| `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` | Catalog unblock requested; outside this decision |
| `NO_DECISION_PACKET_NOT_READY` | No valid review input; assemble packet first |

**Important:** `APPROVE_RESTRICTED_REVIEW_CONTINUATION` means only that the exact restricted-review instrument can continue in the restricted-review lane. It does **not** mean production approval, catalog unblock, method promotion, claim authorization, or production compatibility.

---

## 7. Decision mapping rules

| Packet state / eligibility | Decision status | Meaning | Authorized next action |
|----------------------------|-----------------|---------|------------------------|
| `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` + `ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT` | `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | Sufficient packet for restricted-review continuation | Proceed to restricted-review governance, not production |
| Missing required evidence / `NOT_ELIGIBLE_MISSING_EVIDENCE` | `REQUEST_ADDITIONAL_EVIDENCE` | Evidence packet incomplete | Collect missing evidence |
| Method-validity evidence structurally insufficient | `REJECT_FOR_METHOD_VALIDITY` | Method-validity lane cannot continue | Repair method-validity evidence |
| Identity mismatch / `NOT_ELIGIBLE_IDENTITY_MISMATCH` | `REJECT_FOR_IDENTITY_MISMATCH` | Wrong instrument/scope | Rebuild packet with exact identity |
| Claim boundary missing / `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` | Decision unsafe | Repair claim boundary evidence |
| Unsupported surface / `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` | `REJECT_FOR_UNSUPPORTED_SURFACE` | Requested surface outside restricted-review | Restrict scope or create separate review |
| Cross-inference family | `REJECT_FOR_CROSS_INFERENCE_FAMILY` | Not the exact kfold instrument | Create separate instrument lane |
| Cross-geometry | `REJECT_FOR_CROSS_GEOMETRY` | Not single-cell geometry | Create separate instrument lane |
| Production compatibility requested | `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` | Outside restricted-review decision | Open production compatibility lane |
| Catalog unblock requested | `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` | Outside this decision | Open catalog governance lane |
| Packet not ready / `PACKET_NOT_REQUESTED` | `NO_DECISION_PACKET_NOT_READY` | No valid review input | Assemble packet first |

Mapping is deterministic: packet readiness and eligibility statuses from the assembly runtime drive decision status. No statistical computation or evidence fabrication.

---

## 8. Allowed next actions

### After `APPROVE_RESTRICTED_REVIEW_CONTINUATION`

- Continue restricted-review diagnostics
- Prepare restricted-review governance notes
- Collect more validation evidence
- Open production compatibility review as separate future lane
- Open catalog governance review as separate future lane
- Prepare future runtime for review decision (`TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001`)

### After `REQUEST_ADDITIONAL_EVIDENCE`

- Collect missing evidence refs
- Rerun packet assembly runtime
- Repair artifact references
- Update evidence packet

---

## 9. Prohibited next actions

Always prohibited by this contract:

- Method promotion
- Instrument promotion
- Catalog unblock
- Production compatibility authorization
- Confidence interval claim authorization
- P-value claim authorization
- Statistical significance claim authorization
- Statistical power claim authorization
- Causal lift claim authorization
- Business lift claim authorization
- ROI/ROAS claim authorization
- Decision recommendation authorization
- Production readout authorization
- MIP decision surface approval
- TrustReport bypass
- Claim authorization runtime bypass

---

## 10. Relationship to claim authorization

- `CLAIM_AUTHORIZATION_RUNTIME_001` remains the sole package-level claim owner
- This review decision contract does **not** modify claim authorization
- Decision status does **not** authorize claims
- All claim authorization fields remain `NOT_AUTHORIZED` / `NOT_EVALUATED` unless explicitly decided by claim authorization runtime in a separate lane

---

## 11. Relationship to catalog governance

- This contract does **not** unblock the catalog
- Catalog status remains `BLOCKED` / `RESTRICTED` unless a separate catalog governance artifact changes it
- Restricted-review continuation is **not** catalog promotion

---

## 12. Relationship to production compatibility

- Production compatibility is explicitly out of scope
- Production compatibility requires a separate review lane (`PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_*`)
- Production compatibility evidence, if present, may be recorded but cannot change this decision into production approval

---

## 13. Relationship to Lane B

- Lane B final readout/spend/ROI readiness is orthogonal
- Lane B can support readout compatibility context only
- Spend/ROI readiness cannot satisfy method validity or promotion decision
- No Lane B runtime changes

---

## 14. Future runtime plan

**Recommended future artifact:** `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001`

**Runtime responsibilities:**

- Consume `TBRRidgePromotionEvidencePacket`
- Apply deterministic decision mapping rules (§7)
- Emit `TBRRidgePromotionReviewDecision`
- Preserve blockers, warnings, and lineage
- Not promote methods or instruments
- Not authorize claims
- Not unblock catalog

---

## 15. Non-goals

- No runtime implemented
- No method promotion
- No instrument promotion
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
- No Lane B runtime changes
- No MIP decisioning or TrustReport bypass

---

## 16. Validation results

- Contract doc: `docs/track_d/TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001.md`
- Summary JSON: `docs/track_d/archives/TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001_summary.json`
- Governance tests: `tests/governance/test_tbrridge_promotion_review_decision_contract_001.py`

Capability flags (all true): `review_decision_contract_completed`, `exact_instrument_scope_defined`, `review_decision_object_defined`, `decision_statuses_defined`, `decision_mapping_rules_defined`, `future_runtime_defined`.

Forbidden flags (all false): `runtime_implemented`, method/instrument promotion, catalog unblock, production compatibility, claim authorization changes, statistical claims, estimator/inference implementation, new validation experiments, Lane B runtime changes, MIP decisioning, TrustReport bypass.
