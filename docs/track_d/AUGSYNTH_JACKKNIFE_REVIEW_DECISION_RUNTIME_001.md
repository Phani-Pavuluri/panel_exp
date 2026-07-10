# AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001

## Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001` |
| **Artifact type** | `augsynth_jackknife_review_decision_runtime` |
| **Lane** | Lane A — Method / instrument promotion framework application |
| **Status** | `completed` |
| **Scope** | `review_decision_runtime_no_promotion_no_claim_authorization` |
| **Instrument identity** | `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| **Alias-related identity** | `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` |
| **Final verdict** | `augsynth_jackknife_review_decision_runtime_implemented_no_promotion_no_claim_authorization` |
| **Recommended next** | `AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001` |

**Depends on:** `AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001` · `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` · `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` · `METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001` · `METHOD_PROMOTION_GENERIC_CONTRACTS_001` · `CLAIM_AUTHORIZATION_RUNTIME_001`

## Runtime purpose

Deterministic review decision runtime consuming `AugSynthJackknifePromotionEvidencePacket` and emitting `AugSynthJackknifeReviewDecision` per `AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001`.

The runtime is a **governance interpretation gate only**: it applies packet readiness/eligibility mapping with fixed precedence. It does **not** inspect raw evidence, score evidence quality, run AugSynth, or authorize promotion/claims.

## Exact identity and alias/research-only boundary

**Canonical:** `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review`

**Alias-related (non-substitutable):** `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only`

Research-only and alias substitution attempts reject with dedicated decision statuses. Canonical identity is enforced on approval.

## Input model

`AugSynthJackknifeReviewDecisionInput`: `decision_id`, `packet` (dataclass or dict), `requested_decision_surface`, `reviewer_notes`, `lineage`, `warnings`, `created_from_artifacts`

## Output model

`AugSynthJackknifeReviewDecision`: full decision envelope with `decision_status`, `allowed_next_actions`, `prohibited_next_actions`, fixed non-authorization statuses, preserved `missing_evidence`, `blockers`, `warnings`, `lineage`

## Decision statuses

`APPROVE_RESTRICTED_REVIEW_CONTINUATION`, `REQUEST_ADDITIONAL_EVIDENCE`, `REJECT_FOR_METHOD_VALIDITY`, `REJECT_FOR_IDENTITY_MISMATCH`, `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION`, `REJECT_FOR_SCOPE_VIOLATION`, `REJECT_FOR_ALIAS_SUBSTITUTION`, `REJECT_FOR_RESEARCH_ONLY_SUBSTITUTION`, `REJECT_FOR_UNSUPPORTED_SURFACE`, `REJECT_FOR_CROSS_INFERENCE_FAMILY`, `REJECT_FOR_CROSS_GEOMETRY`, `REJECT_FOR_CROSS_ESTIMAND`, `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW`, `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW`, `NO_DECISION_PACKET_NOT_READY`

## Mapping / Decision precedence

1. Production/catalog deferrals → 2. no packet / not requested → 3. research-only substitution → 4. alias substitution → 5. identity mismatch → 6. cross-inference/geometry/estimand → 7. claim boundary → 8. scope violation → 9. method-validity blockers → 10. missing/partial evidence → 11. unsupported surface → 12. ready+eligible approval → 13. fallback

## Positive decision semantics

`APPROVE_RESTRICTED_REVIEW_CONTINUATION` means the packet may continue as AugSynth restricted-review governance input only. It does **not** authorize promotion, claims, catalog unblock, production compatibility, readout, statistical claims, ROI/ROAS, MIP, or TrustReport bypass.

## Allowed / prohibited actions

**Allowed (approval):** `continue_augsynth_restricted_review_diagnostics`, `prepare_augsynth_governance_notes`, collect additional diagnostics/evidence, open catalog/production/claim reviews as separate lanes.

**Always prohibited:** `augsynth_promotion`, `method_promotion`, `instrument_promotion`, `catalog_unblock`, all claim authorizations, `generic_adapter_profile_for_augsynth_registration`, `mip_decision_surface_approval`, `trust_report_bypass`, etc.

## Fixed non-authorization statuses

`NOT_AUTHORIZED_BY_THIS_DECISION`, `NOT_UNBLOCKED_BY_THIS_DECISION`, `NOT_PROMOTED_BY_THIS_DECISION`, `NOT_REGISTERED_BY_THIS_DECISION`, `NOT_BYPASSED_BY_THIS_DECISION`

## Evidence quality boundary

Runtime uses packet metadata only. No raw evidence inspection, no quality scoring, no donor-pool/pre-period-fit/augmentation/synthetic-weight adequacy decisions, no statistics.

## Generic framework compatibility

`APPROVE_RESTRICTED_REVIEW_CONTINUATION` maps to generic `APPROVE_REVIEW_CONTINUATION` with `decision_scope=restricted_review`. AugSynth is **not** added to the generic runtime in this artifact.

## Relationships

| Component | Relationship |
|-----------|--------------|
| **Packet runtime** | Source of readiness/eligibility |
| **Generic runtime** | Not registered for AugSynth |
| **TBRRidge/SCM** | Framework precedents only |
| **Claim authorization** | Unchanged; `CLAIM_AUTHORIZATION_RUNTIME_001` remains sole owner |
| **Catalog/production** | Separate lanes |
| **Lane B** | Orthogonal |
| **MIP** | Cannot authorize DecisionSurface/TrustReport |

## Non-goals

No promotion, no claim/catalog/production authorization, no generic adapter profile, no estimator/inference, no raw evidence scoring, no Lane B/MIP changes.

## Validation results

- Module: `panel_exp/validation/augsynth_jackknife_review_decision_runtime_001.py`
- Tests: `tests/validation/test_augsynth_jackknife_review_decision_runtime_001.py`, `tests/governance/test_augsynth_jackknife_review_decision_runtime_001.py`
- Summary: `docs/track_d/archives/AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001_summary.json`

## Recommended next artifact

**`AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001`** — audit whether AugSynth is ready for generic adapter registration. Do not register automatically.
