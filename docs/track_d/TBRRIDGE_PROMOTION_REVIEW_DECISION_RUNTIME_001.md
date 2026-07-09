# TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001

## Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001` |
| **Artifact type** | `tbrridge_promotion_review_decision_runtime` |
| **Lane** | Lane A — Method / instrument promotion |
| **Status** | completed |
| **Scope** | `review_decision_runtime_no_promotion_no_claim_authorization` |
| **Instrument identity** | `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| **Depends on** | `TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001` · `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` · `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001` · `CLAIM_AUTHORIZATION_RUNTIME_001` |
| **Final verdict** | `tbrridge_promotion_review_decision_runtime_implemented_no_promotion_no_claim_authorization` |
| **Recommended next** | `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001` |

## Runtime purpose

Deterministic runtime consuming a `TBRRidgePromotionEvidencePacket` from `TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001` and emitting a `TBRRidgePromotionReviewDecision` per `TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001`.

The runtime applies decision mapping rules, preserves blockers/missing evidence/warnings/lineage, and clearly distinguishes restricted-review continuation from promotion, catalog unblock, production compatibility, or claim authorization.

## Exact instrument scope

`geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review`

No estimator-family promotion, global TBRRidge promotion, cross-inference-family decision, cross-geometry decision, or production/catalog decision.

## Input model

`TBRRidgePromotionReviewDecisionInput`:

- `decision_id: str`
- `packet: TBRRidgePromotionEvidencePacket | dict`
- `requested_decision_surface: str` (default `restricted_review`)
- `reviewer_notes: str` optional
- `lineage: dict` default empty
- `warnings: list[str]` default empty
- `created_from_artifacts: list[str]` default empty

## Output decision model

`TBRRidgePromotionReviewDecision`:

- `decision_id`, `instrument_identity`, `decision_status`, `decision_scope`, `decision_surface`
- `packet_ref`, `evidence_summary`, `missing_evidence`, `blockers`
- `required_followups`, `allowed_next_actions`, `prohibited_next_actions`
- `claim_authorization_status`, `catalog_status`, `production_compatibility_status`
- `method_promotion_status`, `instrument_promotion_status`
- `warnings`, `lineage`, `created_from_artifacts`

## Decision statuses

`APPROVE_RESTRICTED_REVIEW_CONTINUATION`, `REQUEST_ADDITIONAL_EVIDENCE`, `REJECT_FOR_METHOD_VALIDITY`, `REJECT_FOR_IDENTITY_MISMATCH`, `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION`, `REJECT_FOR_UNSUPPORTED_SURFACE`, `REJECT_FOR_CROSS_INFERENCE_FAMILY`, `REJECT_FOR_CROSS_GEOMETRY`, `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW`, `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW`, `NO_DECISION_PACKET_NOT_READY`

## Deterministic mapping rules

| Condition | Decision status |
|-----------|-----------------|
| Ready + eligible + `restricted_review` surface | `APPROVE_RESTRICTED_REVIEW_CONTINUATION` |
| Missing evidence / blocked missing | `REQUEST_ADDITIONAL_EVIDENCE` |
| Method-validity blocker in packet | `REJECT_FOR_METHOD_VALIDITY` |
| Identity mismatch | `REJECT_FOR_IDENTITY_MISMATCH` |
| Claim boundary missing | `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` |
| Unsupported surface | `REJECT_FOR_UNSUPPORTED_SURFACE` |
| Cross-inference family | `REJECT_FOR_CROSS_INFERENCE_FAMILY` |
| Cross-geometry | `REJECT_FOR_CROSS_GEOMETRY` |
| Production surface requested | `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` |
| Catalog surface requested | `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` |
| Packet not ready | `NO_DECISION_PACKET_NOT_READY` |

## Precedence rules

1. Production/catalog requested surfaces defer before normal approval
2. Identity mismatch overrides missing evidence
3. Claim boundary missing overrides generic missing evidence
4. Cross-family/cross-geometry are specific rejects
5. Ready/eligible approval applies only to `restricted_review` surface

## Fixed non-authorization statuses

Always emitted:

- `claim_authorization_status = NOT_AUTHORIZED_BY_THIS_DECISION`
- `catalog_status = NOT_UNBLOCKED_BY_THIS_DECISION`
- `production_compatibility_status = NOT_AUTHORIZED_BY_THIS_DECISION`
- `method_promotion_status = NOT_PROMOTED_BY_THIS_DECISION`
- `instrument_promotion_status = NOT_PROMOTED_BY_THIS_DECISION`

## Allowed / prohibited next actions

**Allowed after approval:** `continue_restricted_review_diagnostics`, `prepare_restricted_review_governance_notes`, `collect_more_validation_evidence`, `open_production_compatibility_review_as_separate_lane`, `open_catalog_governance_review_as_separate_lane`

**Always prohibited:** method/instrument promotion, catalog unblock, production compatibility authorization, all statistical/causal/business/ROI claims, decision recommendations, production readout, MIP decisioning, TrustReport bypass, claim authorization runtime bypass

## Relationship to claim authorization

`CLAIM_AUTHORIZATION_RUNTIME_001` remains sole package-level claim owner. This runtime does not modify claim authorization; decision status does not authorize claims.

## Relationship to catalog governance

Does not unblock catalog. Catalog status remains not unblocked by this decision. Restricted-review continuation is not catalog promotion.

## Relationship to production compatibility

Production compatibility is out of scope. Production compatibility evidence may be recorded but cannot change this decision into production approval.

## Relationship to Lane B

Lane B spend/ROI readiness is orthogonal. Lane B can support readout compatibility context only. No Lane B runtime changes.

## Evidence quality boundary

Do not score, reinterpret, or validate raw evidence. The runtime uses only packet readiness status, promotion review eligibility status, missing evidence, blockers, instrument identity, warnings, and lineage.

## Non-goals

No method/instrument promotion, catalog unblock, production compatibility authorization, claim authorization change, statistical claims, estimator/inference implementation, new validation experiments, raw evidence quality scoring, Lane B runtime changes, MIP decisioning, or TrustReport bypass.

## Validation results

- Module: `panel_exp/validation/tbrridge_promotion_review_decision_runtime_001.py`
- Validation tests: `tests/validation/test_tbrridge_promotion_review_decision_runtime_001.py`
- Governance tests: `tests/governance/test_tbrridge_promotion_review_decision_runtime_001.py`
- Summary JSON: `docs/track_d/archives/TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001_summary.json`

Capability flags (all true): `review_decision_runtime_implemented`, `decision_mapping_rules_implemented`, `packet_status_consumed`, `promotion_review_eligibility_consumed`, `fixed_non_authorization_statuses_emitted`, `evidence_quality_boundary_preserved`.

## Recommended next artifact

`METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001` — stop deepening the single TBRRidge config; generalize the promotion review framework.
