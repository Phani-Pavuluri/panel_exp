# SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` |
| **Artifact type** | `scm_jackknife_null_monitor_promotion_evidence_packet_runtime` |
| **Lane** | **Lane A — Method / instrument promotion framework application** |
| **Status** | `completed` |
| **Scope** | `evidence_packet_runtime_no_promotion_no_claim_authorization` |
| **Instrument identity** | `geo.scm.jackknife.single_cell.delta_mu.null_monitor` |
| **Catalog alias** | `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review` |
| **Final verdict** | `scm_jackknife_null_monitor_evidence_packet_runtime_implemented_no_promotion_no_claim_authorization` |
| **Recommended next** | `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001` |

**Depends on:**

- `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001`
- `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001`
- `METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001`
- `CLAIM_AUTHORIZATION_RUNTIME_001`

**Runtime module:** `panel_exp/validation/scm_jackknife_null_monitor_promotion_evidence_packet_runtime_001.py`

---

## 2. Runtime purpose

Deterministic assembly of `SCMJackknifeNullMonitorPromotionEvidencePacket` from explicit evidence references. The runtime:

- Consumes explicit evidence refs only (no fabrication)
- Enforces exact canonical instrument identity
- Reconciles catalog alias as alias only
- Validates required SCM/null-monitor evidence categories
- Preserves blockers, missing evidence, warnings, and lineage
- Emits packet readiness and promotion-review eligibility
- Prepares null-monitor review input only

**Does not:** promote SCM, unblock catalog, authorize claims, compute estimates, run jackknife inference, score raw evidence quality, or run validation experiments.

---

## 3. Exact canonical identity and catalog alias reconciliation

**Canonical:** `geo.scm.jackknife.single_cell.delta_mu.null_monitor`  
**Catalog alias:** `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review`

Output `instrument_identity` is always canonical on success. Catalog alias is preserved in `catalog_alias` when provided on input or evidence refs. Alias presence does not block assembly. Alias cannot substitute canonical identity in output.

---

## 4. Input model

`SCMJackknifeNullMonitorPromotionEvidencePacketInput`:

- `packet_id`
- `instrument_identity` (default canonical)
- `catalog_alias` (optional)
- `evidence_refs`
- `requested_surface` (default `null_monitor`; `None` means not requested)
- `lineage`, `warnings`, `created_from_artifacts`

---

## 5. Evidence reference model

`SCMJackknifeNullMonitorEvidenceReference`:

- `evidence_id`, `evidence_category`, `artifact_ref`
- Optional: `instrument_identity`, `catalog_alias`, `evidence_surface`, `notes`, `metadata`

Non-empty `artifact_ref` required to satisfy a category. Provided non-canonical `instrument_identity` on a ref blocks unless it equals the catalog alias (reconciled only).

---

## 6. Output packet model

`SCMJackknifeNullMonitorPromotionEvidencePacket` with fixed identity fields:

- `estimator_family=scm`, `inference_family=jackknife`, `geometry=single_cell`
- `estimand=delta_mu`, `surface=null_monitor`
- `interval_semantics=not_applicable_for_null_monitor`

Includes `evidence_by_category`, `missing_evidence`, `blockers`, `warnings`, readiness and eligibility statuses.

---

## 7. Required evidence categories

instrument_identity · claim_boundary · metric_estimand_alignment · null_control_false_positive · jackknife_stability · directional_error · donor_pool_diagnostics · pre_period_fit_diagnostics · sensitivity · readout_compatibility

Optional: production_compatibility (not required for null-monitor packet).

---

## 8. Readiness statuses

All contract statuses implemented in `SCMJackknifeNullMonitorPacketReadinessStatus`, including `PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT`, `PACKET_PARTIAL_DIAGNOSTIC_ONLY`, identity/surface/scope blockers, and `PACKET_NOT_REQUESTED`.

---

## 9. Eligibility statuses

All contract statuses implemented in `SCMJackknifeNullMonitorPromotionReviewEligibilityStatus`. Eligibility as null-monitor review input does not authorize promotion or claims.

---

## 10. Readiness/eligibility mapping

Precedence:

1. Empty refs + `requested_surface is None` → `PACKET_NOT_REQUESTED`
2. Input or ref identity mismatch → identity blockers
3. Unsupported requested surface → production / catalog / causal / generic unsupported mapping
4. Missing `claim_boundary` → claim boundary blockers (over generic missing)
5. Other missing required evidence → `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` or `PACKET_PARTIAL_DIAGNOSTIC_ONLY` when some valid evidence present
6. All required present → `PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT` / `ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT`

---

## 11. Blocker semantics

Stable blockers including `BLOCKED_MISSING_*`, `BLOCKED_INSTRUMENT_IDENTITY_MISMATCH`, `BLOCKED_UNSUPPORTED_SURFACE`, `BLOCKED_NULL_MONITOR_SCOPE_VIOLATION`, `BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED`, `BLOCKED_CATALOG_UNBLOCK_REQUESTED`, `BLOCKED_CAUSAL_CLAIM_REQUESTED`, plus substitution warnings for TBRRidge and Lane B evidence.

---

## 12. Evidence substitution rules

Enforced by category name matching and metadata flags:

- TBRRidge evidence (`source_family=tbrridge` or tbrridge artifact paths) cannot satisfy SCM categories
- Lane B spend/ROI evidence cannot satisfy method-validity categories
- Categories are not interchangeable (null-control ≠ donor pool ≠ pre-period fit; jackknife stability ≠ directional error)
- Readout compatibility cannot substitute method validity categories
- SCM placebo semantics do not auto-satisfy jackknife null-monitor without explicit category refs

No content inspection or raw evidence quality scoring.

---

## 13. Relationship to generalized framework

Second instrument-family runtime applying the generalized promotion framework pattern. Reuses packet shape, readiness/eligibility semantics, and non-authorization boundaries from `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001` and the SCM contract.

---

## 14. Relationship to claim authorization

`CLAIM_AUTHORIZATION_RUNTIME_001` remains sole claim owner. Runtime does not modify claim authorization. Null-monitor eligibility does not authorize statistical, causal, business, ROI, or decision claims.

---

## 15. Relationship to catalog and production

Catalog remains restricted. Production compatibility requests are blocked. Null-monitor review is not production review.

---

## 16. Relationship to Lane B and MIP

Lane B spend/ROI readiness is orthogonal. MIP DecisionSurface / TrustReport cannot be bypassed. No MIP decisioning implemented.

---

## 17. Evidence quality boundary

Runtime validates presence and category assignment of evidence references only. It does **not** score, rank, or interpret raw evidence quality. No `evidence_quality_score` or similar fields are emitted.

---

## 18. Non-goals

- No SCM or SCM+Jackknife promotion
- No catalog unblock or production compatibility authorization
- No claim authorization change
- No estimator/inference implementation or execution
- No new validation experiments
- No Lane B runtime changes
- No MIP decisioning or TrustReport bypass
- No raw evidence quality scoring

---

## 19. Validation results

- Validation tests: `tests/validation/test_scm_jackknife_null_monitor_promotion_evidence_packet_runtime_001.py`
- Governance tests: `tests/governance/test_scm_jackknife_null_monitor_promotion_evidence_packet_runtime_001.py`
- Summary JSON: `docs/track_d/archives/SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001_summary.json`

---

## 20. Recommended next artifact

**`SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001`** — review decision contract for null-monitor promotion review input; no runtime, promotion, or claim authorization.
