# SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001

## Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001` |
| **Artifact type** | `scm_jackknife_null_monitor_review_decision_runtime` |
| **Lane** | Lane A — Method / instrument promotion framework application |
| **Status** | completed |
| **Scope** | `review_decision_runtime_no_promotion_no_claim_authorization` |
| **Instrument identity** | `geo.scm.jackknife.single_cell.delta_mu.null_monitor` |
| **Catalog alias** | `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review` |
| **Depends on** | `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001` · `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` · `METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001` · `CLAIM_AUTHORIZATION_RUNTIME_001` |
| **Final verdict** | `scm_jackknife_null_monitor_review_decision_runtime_implemented_no_promotion_no_claim_authorization` |
| **Recommended next** | `METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001` |

## Runtime purpose

Deterministic runtime consuming an `SCMJackknifeNullMonitorPromotionEvidencePacket` from `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` and emitting an `SCMJackknifeNullMonitorReviewDecision` per `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001`.

The runtime applies decision mapping rules, preserves blockers/missing evidence/warnings/lineage, and clearly distinguishes null-monitor review continuation from SCM promotion, SCM+Jackknife promotion, catalog unblock, production compatibility, or claim authorization.

## Exact canonical identity and alias handling

**Canonical instrument identity:** `geo.scm.jackknife.single_cell.delta_mu.null_monitor`

**Catalog alias (preserved, not substituted):** `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review`

On approval, output `instrument_identity` is forced to the canonical identity. The catalog alias is emitted separately and never substitutes for canonical identity in decision output.

## Input model

`SCMJackknifeNullMonitorReviewDecisionInput`:

- `decision_id: str`
- `packet: SCMJackknifeNullMonitorPromotionEvidencePacket | dict`
- `requested_decision_surface: str` (default `null_monitor`)
- `reviewer_notes: str` optional
- `lineage: dict` default empty
- `warnings: list[str]` default empty
- `created_from_artifacts: list[str]` default empty

## Output model

`SCMJackknifeNullMonitorReviewDecision`:

- `decision_id`, `instrument_identity`, `catalog_alias`, `decision_status`, `decision_scope`, `decision_surface`
- `packet_ref`, `evidence_summary`, `missing_evidence`, `blockers`
- `required_followups`, `allowed_next_actions`, `prohibited_next_actions`
- `claim_authorization_status`, `catalog_status`, `production_compatibility_status`
- `method_promotion_status`, `instrument_promotion_status`, `null_monitor_scope_status`
- `warnings`, `lineage`, `created_from_artifacts`

## Decision statuses

`APPROVE_NULL_MONITOR_REVIEW_CONTINUATION`, `REQUEST_ADDITIONAL_EVIDENCE`, `REJECT_FOR_METHOD_VALIDITY`, `REJECT_FOR_IDENTITY_MISMATCH`, `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION`, `REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION`, `REJECT_FOR_UNSUPPORTED_SURFACE`, `REJECT_FOR_CROSS_INFERENCE_FAMILY`, `REJECT_FOR_CROSS_GEOMETRY`, `REJECT_FOR_CROSS_ESTIMAND`, `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW`, `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW`, `NO_DECISION_PACKET_NOT_READY`

## Deterministic mapping / Precedence

Apply in this order:

1. Production/catalog surface deferrals
2. No packet / packet not requested
3. Identity mismatch
4. Cross-inference / cross-geometry / cross-estimand
5. Claim boundary missing
6. Null-monitor scope violation
7. Method-validity blockers
8. Missing evidence / partial diagnostic
9. Unsupported surface
10. Ready + eligible approval
11. Fallback

| Condition | Decision status |
|-----------|-----------------|
| Production surface requested | `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` |
| Catalog surface requested | `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` |
| No packet / `PACKET_NOT_REQUESTED` | `NO_DECISION_PACKET_NOT_READY` |
| Identity mismatch | `REJECT_FOR_IDENTITY_MISMATCH` |
| Cross-inference family | `REJECT_FOR_CROSS_INFERENCE_FAMILY` |
| Cross-geometry | `REJECT_FOR_CROSS_GEOMETRY` |
| Cross-estimand | `REJECT_FOR_CROSS_ESTIMAND` |
| Claim boundary missing | `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` |
| Null-monitor scope violation | `REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION` |
| Method-validity blocker | `REJECT_FOR_METHOD_VALIDITY` |
| Missing evidence / partial diagnostic | `REQUEST_ADDITIONAL_EVIDENCE` |
| Unsupported surface | `REJECT_FOR_UNSUPPORTED_SURFACE` |
| Ready + eligible + null-monitor surface | `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` |
| Fallback | `NO_DECISION_PACKET_NOT_READY` |

## Allowed next actions

**After approval:** `continue_null_monitor_diagnostics`, `prepare_null_monitor_governance_notes`, `collect_additional_null_control_evidence`, `collect_additional_scm_diagnostics`, `open_catalog_governance_review_as_separate_lane`, `open_production_compatibility_review_as_separate_lane`

**After request additional evidence:** `collect_missing_evidence_refs`, `rerun_scm_jackknife_null_monitor_packet_runtime`

**After identity/scope/cross-instrument rejects:** `repair_identity_or_scope`, `separate_cross_instrument_review`

**After claim-boundary reject:** `repair_claim_boundary`

**After method-validity reject:** `reject_or_rework_instrument_validation`

## Prohibited next actions

Always include: `scm_promotion`, `scm_jackknife_promotion`, `method_promotion`, `instrument_promotion`, `catalog_unblock`, `production_compatibility_authorization`, all statistical/causal/business/ROI claim authorizations, `decision_recommendation_authorization`, `production_readout_authorization`, `mip_decision_surface_approval`, `trust_report_bypass`, `claim_authorization_runtime_bypass`

## Fixed non-authorization statuses

Always emitted:

- `claim_authorization_status = NOT_AUTHORIZED_BY_THIS_DECISION`
- `catalog_status = NOT_UNBLOCKED_BY_THIS_DECISION`
- `production_compatibility_status = NOT_AUTHORIZED_BY_THIS_DECISION`
- `method_promotion_status = NOT_PROMOTED_BY_THIS_DECISION`
- `instrument_promotion_status = NOT_PROMOTED_BY_THIS_DECISION`
- `null_monitor_scope_status = NULL_MONITOR_ONLY`

## Null-monitor continuation semantics

The only positive decision is `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION`. Approval permits continued null-monitor diagnostics and governance notes only. It does not promote SCM, SCM+Jackknife, unblock catalog, authorize production compatibility, or authorize any claims.

## Relationship to generalized framework

Second non-TBRRidge application of the generalized method promotion review framework (`METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001`). Reuses packet readiness/eligibility semantics from the SCM null-monitor evidence packet runtime with SCM-specific decision statuses and null-monitor scope enforcement.

## Relationship to claim authorization

`CLAIM_AUTHORIZATION_RUNTIME_001` remains sole package-level claim owner. This runtime does not modify claim authorization; decision status does not authorize claims.

## Relationship to catalog and production

Does not unblock catalog. Catalog status remains not unblocked by this decision. Production compatibility is out of scope; production/catalog surfaces defer to separate lanes.

## Relationship to Lane B and MIP

Lane B spend/ROI readiness is orthogonal. Lane B can support readout compatibility context only. No Lane B runtime changes. MIP decisioning is not authorized by this runtime.

## Evidence quality boundary

The runtime does not score, reinterpret, or validate raw evidence contents. It uses only packet readiness status, promotion review eligibility status, missing evidence, blockers, instrument identity, catalog alias, warnings, lineage, and requested decision surface. It must not judge donor pool adequacy, pre-period fit quality, jackknife stability quality, calculate statistics, or run SCM/jackknife.

## Non-goals

No SCM/SCM+Jackknife promotion, catalog unblock, production compatibility authorization, claim authorization change, statistical claims, estimator/inference implementation, new validation experiments, raw evidence quality scoring, Lane B runtime changes, MIP decisioning, or TrustReport bypass.

## Validation results

- Module: `panel_exp/validation/scm_jackknife_null_monitor_review_decision_runtime_001.py`
- Validation tests: `tests/validation/test_scm_jackknife_null_monitor_review_decision_runtime_001.py`
- Governance tests: `tests/governance/test_scm_jackknife_null_monitor_review_decision_runtime_001.py`
- Summary JSON: `docs/track_d/archives/SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001_summary.json`

Capability flags (all true): `review_decision_runtime_implemented`, `exact_instrument_identity_enforced`, `catalog_alias_preserved_without_substitution`, `decision_mapping_rules_implemented`, `precedence_rules_implemented`, `fixed_non_authorization_statuses_emitted`, `null_monitor_continuation_semantics_preserved`, `evidence_quality_boundary_preserved`.

## Recommended next artifact

`METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001` — checkpoint the Lane A framework application chain before AugSynth/DID expansion.
