# AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001

## Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` |
| **Artifact type** | `augsynth_jackknife_promotion_evidence_packet_runtime` |
| **Lane** | Lane A — Method / instrument promotion framework application |
| **Status** | `completed` |
| **Scope** | `evidence_packet_runtime_no_promotion_no_claim_authorization` |
| **Instrument identity** | `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| **Alias-related identity** | `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` |
| **Final verdict** | `augsynth_jackknife_evidence_packet_runtime_implemented_no_promotion_no_claim_authorization` |
| **Recommended next** | `AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001` |

**Depends on:** `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001` · `METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001` · `METHOD_PROMOTION_GENERIC_RUNTIME_001` · `METHOD_PROMOTION_GENERIC_CONTRACTS_001` · `CLAIM_AUTHORIZATION_RUNTIME_001`

## Runtime purpose

Deterministic packet assembly runtime for AugSynth Jackknife restricted-review promotion evidence packets per `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001`.

The runtime is an **assembly gate only**: it validates canonical identity, requested surface, evidence reference presence, and category grouping. It does **not** run AugSynth, run Jackknife, compute estimates, score evidence quality, or inspect raw evidence contents.

## Exact canonical identity and alias handling

**Canonical:** `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review`

**Alias-related (non-substitutable):** `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only`

- Input identity must equal canonical identity
- Research-only identity on input → `PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT`
- Non-canonical identity → `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH`
- Research-only identity on evidence refs → blocked; refs must use canonical identity

## Input model

`AugSynthJackknifePromotionEvidencePacketInput`: `packet_id`, `instrument_identity`, `requested_surface`, `evidence_references`, `required_evidence_categories`, `optional_evidence_categories`, `lineage`, `warnings`, `created_from_artifacts`

## Evidence reference model

`AugSynthJackknifeEvidenceReference`: `evidence_id`, `evidence_category`, `artifact_ref`, `instrument_identity`, `evidence_surface`, `source_family`, `source_lane`, `source_artifact_type`, `notes`, `metadata`

Rules: non-empty `artifact_ref` required; `source_family` cannot be `tbrridge`, `scm`, `lane_b`, `spend`, `roi`, or `mip`.

## Output packet model

`AugSynthJackknifePromotionEvidencePacket`: `packet_id`, `instrument_identity`, `alias_related_identity`, `evidence_by_category`, `missing_evidence`, `blockers`, `warnings`, `packet_readiness_status`, `promotion_review_eligibility_status`, `allowed_surfaces`, `prohibited_surfaces`, `boundary_statuses`, `lineage`, `created_from_artifacts`

## Required / optional evidence categories

**Core (8):** `instrument_identity`, `claim_boundary`, `metric_estimand_alignment`, `null_control_false_positive`, `directional_error`, `positive_control_recovery`, `sensitivity`, `readout_compatibility`

**AugSynth-specific (8):** `donor_pool_diagnostics`, `pre_period_fit_diagnostics`, `augmentation_component_diagnostics`, `synthetic_weight_diagnostics`, `regularization_or_model_component_diagnostics`, `jackknife_stability`, `method_disagreement_or_scm_bridge`, `support_overlap_or_donor_hull_stress`

**Optional:** `placebo_evidence`, `conformal_evidence`, `bootstrap_evidence`, `production_compatibility`, `catalog_governance`, `external_method_review`

## Readiness statuses

`PACKET_READY_FOR_PROMOTION_REVIEW_INPUT`, `PACKET_PARTIAL_DIAGNOSTIC_ONLY`, `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE`, `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING`, `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH`, `PACKET_BLOCKED_UNSUPPORTED_SURFACE`, `PACKET_BLOCKED_SCOPE_VIOLATION`, `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED`, `PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT`, `PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT`, `PACKET_NOT_REQUESTED`, plus cross-inference/geometry/estimand blockers reserved for future enforcement.

## Eligibility statuses

`ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT`, `NOT_ELIGIBLE_MISSING_EVIDENCE`, `NOT_ELIGIBLE_IDENTITY_MISMATCH`, `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING`, `NOT_ELIGIBLE_SCOPE_VIOLATION`, `NOT_ELIGIBLE_ALIAS_SUBSTITUTION`, `NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION`, `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW`, `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK`, `NOT_ELIGIBLE_FOR_CLAIM_REVIEW`

## Readiness precedence

1. `PACKET_NOT_REQUESTED` (no refs + empty surface)
2. Research-only substitution (input identity)
3. Alias / identity mismatch
4. Production compatibility required
5. Unsupported surface (catalog / claim / MIP / business / other)
6. Claim boundary missing (over generic missing evidence)
7. Missing required evidence / partial diagnostic
8. Ready when all required categories satisfied

## Blockers / warnings

Stable blockers: `AUGSYNTH_PACKET_BLOCKED_*` including SCM/TBRRidge/Lane B substitution, alias/research-only substitution, unsupported surface, claim authorization attempt.

Always-emitted warnings: `AUGSYNTH_WARNING_DIAGNOSTIC_INTERVAL_NOT_PRODUCTION_CI`, `AUGSYNTH_WARNING_RESTRICTED_REVIEW_NOT_PROMOTION`, `AUGSYNTH_WARNING_GENERIC_ADAPTER_PROFILE_NOT_AVAILABLE_YET`

## Fixed non-authorization statuses

`claim_authorization_status`, `catalog_status`, `production_compatibility_status`, `method_promotion_status`, `instrument_promotion_status`, `generic_adapter_status`, `mip_decisioning_status`, `trust_report_bypass_status` — all fixed to `NOT_AUTHORIZED_BY_THIS_PACKET`, `NOT_UNBLOCKED_BY_THIS_PACKET`, `NOT_PROMOTED_BY_THIS_PACKET`, `NOT_REGISTERED_BY_THIS_PACKET`, or `NOT_BYPASSED_BY_THIS_PACKET` on every packet.

## Evidence quality boundary

Runtime validates reference metadata presence only. No raw evidence inspection, no quality scoring, no method-validity evaluation.

## Generic framework compatibility

Maps to generic contract abstractions for future adapter profile. AugSynth is **not** added to the generic runtime (`METHOD_PROMOTION_GENERIC_RUNTIME_001`) until packet + decision runtimes exist.

## Relationship to TBRRidge / SCM / Lane B / MIP

- **TBRRidge:** framework precedent only; TBRRidge `source_family` or artifact refs blocked
- **SCM:** bridge/disagreement category allowed from AugSynth-family refs only; SCM substitution blocked
- **Lane B:** spend/ROI evidence blocked for method-validity categories
- **MIP:** `mip_decision_surface` blocked; no DecisionSurface or TrustReport bypass

## Non-goals

No AugSynth execution, no decision contract, no generic adapter profile, no promotion, no claim/catalog/production authorization, no estimator/inference implementation, no raw evidence scoring.

## Validation results

- Module: `panel_exp/validation/augsynth_jackknife_promotion_evidence_packet_runtime_001.py`
- Tests: `tests/validation/test_augsynth_jackknife_promotion_evidence_packet_runtime_001.py`, `tests/governance/test_augsynth_jackknife_promotion_evidence_packet_runtime_001.py`
- Summary: `docs/track_d/archives/AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001_summary.json`

## Recommended next artifact

**`AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001`** — docs/tests-only review decision contract for the same canonical identity; no runtime until contract is accepted.
