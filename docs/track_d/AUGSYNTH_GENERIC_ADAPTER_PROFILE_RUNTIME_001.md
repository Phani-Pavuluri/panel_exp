# AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001

## Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001` |
| **Artifact type** | `augsynth_generic_adapter_profile_runtime` |
| **Lane** | Lane A — Method / instrument promotion framework application |
| **Status** | completed |
| **Scope** | `generic_adapter_profile_registration_summarizer_only_no_promotion_no_claim_authorization` |
| **Canonical identity** | `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| **Alias-related identity (lineage only)** | `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` |
| **Profile ID** | `augsynth_jackknife_restricted_review_v1` |
| **Decision scope** | `restricted_review` |
| **Depends on** | `AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001` · `METHOD_PROMOTION_GENERIC_RUNTIME_001` · `AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001` · `AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001` |
| **Final verdict** | `augsynth_generic_adapter_profile_registered_summarizer_only_no_promotion_no_claim_authorization` |
| **Recommended next** | `METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001` |

## Why profile registration exists

`AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001` concluded AugSynth packet and decision runtimes are ready for generic adapter summarization. This runtime registers `augsynth_jackknife_restricted_review_v1` as the third supported profile in `METHOD_PROMOTION_GENERIC_RUNTIME_001`, alongside TBRRidge and SCM Jackknife null-monitor profiles.

Registration adapts AugSynth packet readiness, eligibility, and decision statuses into generic summaries without changing AugSynth source runtimes or authorizing promotion, claims, catalog unblock, production compatibility, MIP decisioning, or TrustReport bypass.

## Profile identity

| Field | Value |
|-------|-------|
| **profile_id** | `augsynth_jackknife_restricted_review_v1` |
| **canonical_identity** | `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` |
| **aliases (lineage only)** | `geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` |
| **decision_scope** | `restricted_review` |
| **surface** | `restricted_review` |

Canonical identity is required. Alias/research-only identity is preserved for lineage only and cannot substitute restricted_review or diagnostic_interval semantics.

## Status mappings

### Packet readiness

| AugSynth packet status | Generic packet status |
|------------------------|----------------------|
| `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` | `PACKET_READY_FOR_REVIEW_INPUT` |
| `PACKET_PARTIAL_DIAGNOSTIC_ONLY` | `PACKET_PARTIAL_DIAGNOSTIC_ONLY` |
| `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` | `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` |
| `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` | `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` |
| `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` | `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` |
| `PACKET_BLOCKED_UNSUPPORTED_SURFACE` | `PACKET_BLOCKED_UNSUPPORTED_SURFACE` |
| `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` |
| `PACKET_BLOCKED_CROSS_GEOMETRY` | `PACKET_BLOCKED_CROSS_GEOMETRY` |
| `PACKET_BLOCKED_CROSS_ESTIMAND` | `PACKET_BLOCKED_CROSS_ESTIMAND` |
| `PACKET_BLOCKED_SCOPE_VIOLATION` | `PACKET_BLOCKED_SCOPE_VIOLATION` |
| `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` | `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` |
| `PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT` | `PACKET_BLOCKED_SCOPE_VIOLATION` |
| `PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT` | `PACKET_BLOCKED_SCOPE_VIOLATION` |
| `PACKET_NOT_REQUESTED` | `PACKET_NOT_REQUESTED` |

### Eligibility

| AugSynth eligibility | Generic eligibility |
|---------------------|---------------------|
| `ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT` | `ELIGIBLE_AS_REVIEW_INPUT` |
| `NOT_ELIGIBLE_MISSING_EVIDENCE` | `NOT_ELIGIBLE_MISSING_EVIDENCE` |
| `NOT_ELIGIBLE_IDENTITY_MISMATCH` | `NOT_ELIGIBLE_IDENTITY_MISMATCH` |
| `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` |
| `NOT_ELIGIBLE_SCOPE_VIOLATION` | `NOT_ELIGIBLE_SCOPE_VIOLATION` |
| `NOT_ELIGIBLE_ALIAS_SUBSTITUTION` | `NOT_ELIGIBLE_SCOPE_VIOLATION` |
| `NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION` | `NOT_ELIGIBLE_SCOPE_VIOLATION` |
| `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` | `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` |
| `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` | `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` |
| `NOT_ELIGIBLE_FOR_CLAIM_REVIEW` | `NOT_ELIGIBLE_FOR_CLAIM_REVIEW` |

### Decision

| AugSynth decision | Generic decision |
|------------------|------------------|
| `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | `APPROVE_REVIEW_CONTINUATION` |
| `REQUEST_ADDITIONAL_EVIDENCE` | `REQUEST_ADDITIONAL_EVIDENCE` |
| `REJECT_FOR_METHOD_VALIDITY` | `REJECT_FOR_METHOD_VALIDITY` |
| `REJECT_FOR_IDENTITY_MISMATCH` | `REJECT_FOR_IDENTITY_MISMATCH` |
| `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` | `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` |
| `REJECT_FOR_SCOPE_VIOLATION` | `REJECT_FOR_SCOPE_VIOLATION` |
| `REJECT_FOR_ALIAS_SUBSTITUTION` | `REJECT_FOR_SCOPE_VIOLATION` |
| `REJECT_FOR_RESEARCH_ONLY_SUBSTITUTION` | `REJECT_FOR_SCOPE_VIOLATION` |
| `REJECT_FOR_UNSUPPORTED_SURFACE` | `REJECT_FOR_UNSUPPORTED_SURFACE` |
| `REJECT_FOR_CROSS_INFERENCE_FAMILY` | `REJECT_FOR_CROSS_INFERENCE_FAMILY` |
| `REJECT_FOR_CROSS_GEOMETRY` | `REJECT_FOR_CROSS_GEOMETRY` |
| `REJECT_FOR_CROSS_ESTIMAND` | `REJECT_FOR_CROSS_ESTIMAND` |
| `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` | `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` |
| `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` | `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` |
| `NO_DECISION_PACKET_NOT_READY` | `NO_DECISION_PACKET_NOT_READY` |

## Source-of-truth behavior

AugSynth packet runtime (`AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001`) and decision runtime (`AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001`) remain authoritative. The generic adapter:

- maps statuses only; does not recompute packet readiness or decisions
- preserves instrument-specific statuses in summary lineage fields
- preserves missing evidence, blockers, warnings, prohibited actions, and boundary statuses
- keeps `decision_scope=restricted_review` on approval
- maps `APPROVE_RESTRICTED_REVIEW_CONTINUATION` to generic `APPROVE_REVIEW_CONTINUATION` only

The generic adapter does not repair packets, upgrade request-additional-evidence to approval, or convert restricted-review continuation into production/catalog/claim authorization.

## Alias / research-only boundary

`geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only` is emitted in `aliases` for lineage but cannot be used as canonical `instrument_identity` in adaptation input. Alias-substitution attempts block with `GENERIC_ADAPTER_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT`.

## Boundary status preservation

Generic decision summaries preserve AugSynth boundary fields:

- `claim_authorization_status` = `NOT_AUTHORIZED_BY_THIS_DECISION`
- `catalog_status` = `NOT_UNBLOCKED_BY_THIS_DECISION`
- `production_compatibility_status` = `NOT_AUTHORIZED_BY_THIS_DECISION`
- `method_promotion_status` = `NOT_PROMOTED_BY_THIS_DECISION`
- `instrument_promotion_status` = `NOT_PROMOTED_BY_THIS_DECISION`
- `mip_decisioning_status` = `NOT_AUTHORIZED_BY_THIS_ADAPTER` (governance rollup)
- `trust_report_bypass_status` = `NOT_BYPASSED_BY_THIS_ADAPTER` (governance rollup)

## Generic governance summary behavior

`build_method_promotion_governance_summary(...)` supports AugSynth:

- **packet_only** when only packet summary is provided
- **decision_ready** when packet and decision summaries adapt successfully
- **blocked_adapter** when alias/research-only substitution or unmapped statuses block adaptation

MIP and TrustReport non-authorization boundaries are fixed in governance summaries.

## Relationship to AugSynth packet/decision runtime

This artifact registers the adapter profile in `panel_exp/validation/method_promotion_generic_runtime_001.py`. It does not modify `augsynth_jackknife_promotion_evidence_packet_runtime_001.py` or `augsynth_jackknife_review_decision_runtime_001.py`.

## Relationship to TBRRidge/SCM profiles

AugSynth joins two existing profiles:

1. `tbrridge_restricted_review_v1` — TBRRidge restricted review
2. `scm_jackknife_null_monitor_v1` — SCM Jackknife null monitor

All three profiles share the same generic adapter contract: summarizer-only, source-of-truth preserved, no promotion or claim authorization.

## Non-goals

- No AugSynth packet runtime changes
- No AugSynth decision runtime changes
- No method/instrument promotion or AugSynth promotion
- No catalog unblock, production compatibility authorization, or claim authorization
- No MIP DecisionSurface authorization or TrustReport bypass
- No Lane B runtime changes
- No new validation experiments, estimator/inference implementation, or raw evidence quality scoring

## Validation results

- `python -m pytest tests/validation/test_method_promotion_generic_runtime_001.py -q` — AugSynth profile mapping tests pass
- `python -m pytest tests/governance/test_augsynth_generic_adapter_profile_runtime_001.py -q` — governance assertions pass
- `python -m pytest tests/governance/test_method_promotion_generic_runtime_001.py -q` — updated generic runtime governance pass
- Safety grep: promotion/claim/catalog/production/MIP/trust flags remain false
- Capability grep: `augsynth_profile_registered`, `supported_profile_count: 3`, mappings implemented

Summary: [`docs/track_d/archives/AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001_summary.json`](archives/AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001_summary.json)

## Recommended next artifact

**`METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001`** — checkpoint that all three generic adapter profiles (TBRRidge, SCM, AugSynth) are registered and governed consistently before further Lane A expansion.
