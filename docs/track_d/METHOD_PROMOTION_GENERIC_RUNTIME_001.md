# METHOD_PROMOTION_GENERIC_RUNTIME_001

## Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PROMOTION_GENERIC_RUNTIME_001` |
| **Artifact type** | `method_promotion_generic_runtime` |
| **Lane** | Lane A — Method / instrument promotion framework generic runtime |
| **Status** | completed |
| **Scope** | `generic_adapter_runtime_no_promotion_no_claim_authorization` |
| **Depends on** | `METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001` · `METHOD_PROMOTION_GENERIC_CONTRACTS_001` · `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001` · `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001` · `CLAIM_AUTHORIZATION_RUNTIME_001` |
| **Final verdict** | `generic_method_promotion_adapter_runtime_implemented_no_promotion_no_claim_authorization` |
| **Recommended next** | `METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001` |

## Runtime purpose

Thin generic adapter runtime that summarizes instrument-specific packet and decision outputs into generic method-promotion summaries for governance and MIP-facing review.

This runtime is an **adapter/summarizer only**. Instrument-specific runtimes (`TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001`, `TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001`, `SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001`, `SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001`) remain the **source of truth**.

The adapter may map statuses, preserve source statuses, preserve blockers/missing evidence/warnings/lineage, preserve boundary/non-authorization fields, preserve prohibited actions, and emit generic packet/decision/governance summaries.

The adapter must **not** recompute packet readiness, recompute review decisions, override blockers, repair failed decisions, upgrade missing evidence to approval, convert null-monitor approval into restricted-review approval, convert restricted-review approval into production approval, inspect or score raw evidence quality, run estimators/inference, promote methods/instruments, unblock catalog, authorize production compatibility, authorize claims, or bypass TrustReport or claim authorization.

## Supported profiles

Only two completed applications are supported:

1. **TBRRidge restricted-review** — `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` (`tbrridge_restricted_review_v1`, `decision_scope=restricted_review`)
2. **SCM Jackknife null-monitor** — `geo.scm.jackknife.single_cell.delta_mu.null_monitor` (`scm_jackknife_null_monitor_v1`, `decision_scope=null_monitor`, alias `geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review`)

No AugSynth or DID support is implemented.

## Source-of-truth rule

Instrument-specific packet and decision runtimes are authoritative. The generic adapter:

- cannot change source decision status semantics
- cannot upgrade `REQUEST_ADDITIONAL_EVIDENCE` to approval
- cannot convert null-monitor approval into restricted-review or production approval
- cannot convert restricted-review approval into production/catalog/claim authorization
- does not use Lane B spend/ROI evidence

Generic `APPROVE_REVIEW_CONTINUATION` preserves instrument-specific decision scope (`restricted_review` vs `null_monitor`) and does not imply production, catalog, or claim authorization.

## Input/output models

### Import API

```python
from panel_exp.validation.method_promotion_generic_runtime_001 import (
    MethodPromotionEvidencePacketSummary,
    MethodPromotionReviewDecisionSummary,
    MethodPromotionGovernanceSummary,
    MethodPromotionInstrumentAdapterProfile,
    MethodPromotionGenericAdapterStatus,
    adapt_method_promotion_packet_to_generic_summary,
    adapt_method_promotion_decision_to_generic_summary,
    build_method_promotion_governance_summary,
)
```

### Generic adapter status enum

`MethodPromotionGenericAdapterStatus`: `ADAPTED`, `BLOCKED_MISSING_SOURCE_PACKET`, `BLOCKED_MISSING_SOURCE_DECISION`, `BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY`, `BLOCKED_UNMAPPED_PACKET_STATUS`, `BLOCKED_UNMAPPED_ELIGIBILITY_STATUS`, `BLOCKED_UNMAPPED_DECISION_STATUS`, `BLOCKED_MISSING_BOUNDARY_STATUS`, `BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT`, `BLOCKED_PROHIBITED_ACTION_WEAKENED`, `BLOCKED_SOURCE_OF_TRUTH_MISMATCH`

## Packet summary adaptation

`adapt_method_promotion_packet_to_generic_summary(packet, *, profile=None, summary_id=None, source_packet_ref=None)` accepts instrument-specific packet dataclass or dict, identifies profile by canonical `instrument_identity`, maps packet readiness and eligibility statuses to generic statuses, preserves instrument-specific statuses and all blockers/missing evidence/warnings/lineage, and blocks unknown identity, alias substitution, and unmapped statuses.

## Decision summary adaptation

`adapt_method_promotion_decision_to_generic_summary(decision, *, profile=None, summary_id=None, source_decision_ref=None)` maps `decision_status` to generic status while preserving instrument-specific status and `decision_scope`. Required boundary fields (`claim_authorization_status`, `catalog_status`, `production_compatibility_status`, `method_promotion_status`, `instrument_promotion_status`) must be present. Prohibited next actions must not be weakened below the minimum required set.

## Governance summary rollup

`build_method_promotion_governance_summary(packet_summary=None, decision_summary=None, *, governance_summary_id=None)` combines packet and decision summaries, sets `current_framework_stage` (`packet_only`, `decision_ready`, or `blocked_adapter`), unions unresolved blockers/missing evidence, and emits fixed non-authorization statuses for MIP and TrustReport (`NOT_AUTHORIZED_BY_THIS_ADAPTER`, `NOT_BYPASSED_BY_THIS_ADAPTER`).

## Adapter profiles

### TBRRidge (`tbrridge_restricted_review_v1`)

| Instrument-specific packet status | Generic packet status |
|-----------------------------------|-----------------------|
| `PACKET_READY_FOR_PROMOTION_REVIEW_INPUT` | `PACKET_READY_FOR_REVIEW_INPUT` |
| `PACKET_PARTIAL_DIAGNOSTIC_ONLY` | `PACKET_PARTIAL_DIAGNOSTIC_ONLY` |
| `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` | `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` |
| `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` | `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` |
| `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` | `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` |
| `PACKET_BLOCKED_UNSUPPORTED_SURFACE` | `PACKET_BLOCKED_UNSUPPORTED_SURFACE` |
| `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` |
| `PACKET_BLOCKED_CROSS_GEOMETRY` | `PACKET_BLOCKED_CROSS_GEOMETRY` |
| `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` | `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` |
| `PACKET_NOT_REQUESTED` | `PACKET_NOT_REQUESTED` |

| Instrument-specific eligibility | Generic eligibility |
|--------------------------------|---------------------|
| `ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT` | `ELIGIBLE_AS_REVIEW_INPUT` |
| `NOT_ELIGIBLE_MISSING_EVIDENCE` | `NOT_ELIGIBLE_MISSING_EVIDENCE` |
| `NOT_ELIGIBLE_IDENTITY_MISMATCH` | `NOT_ELIGIBLE_IDENTITY_MISMATCH` |
| `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` |
| `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` | `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` |
| `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` | `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` |

| Instrument-specific decision | Generic decision |
|-------------------------------|------------------|
| `APPROVE_RESTRICTED_REVIEW_CONTINUATION` | `APPROVE_REVIEW_CONTINUATION` |
| `REQUEST_ADDITIONAL_EVIDENCE` | `REQUEST_ADDITIONAL_EVIDENCE` |
| `REJECT_FOR_METHOD_VALIDITY` | `REJECT_FOR_METHOD_VALIDITY` |
| `REJECT_FOR_IDENTITY_MISMATCH` | `REJECT_FOR_IDENTITY_MISMATCH` |
| `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` | `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` |
| `REJECT_FOR_UNSUPPORTED_SURFACE` | `REJECT_FOR_UNSUPPORTED_SURFACE` |
| `REJECT_FOR_CROSS_INFERENCE_FAMILY` | `REJECT_FOR_CROSS_INFERENCE_FAMILY` |
| `REJECT_FOR_CROSS_GEOMETRY` | `REJECT_FOR_CROSS_GEOMETRY` |
| `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` | `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` |
| `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` | `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` |
| `NO_DECISION_PACKET_NOT_READY` | `NO_DECISION_PACKET_NOT_READY` |

### SCM null-monitor (`scm_jackknife_null_monitor_v1`)

| Instrument-specific packet status | Generic packet status |
|-----------------------------------|-----------------------|
| `PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT` | `PACKET_READY_FOR_REVIEW_INPUT` |
| `PACKET_PARTIAL_DIAGNOSTIC_ONLY` | `PACKET_PARTIAL_DIAGNOSTIC_ONLY` |
| `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` | `PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE` |
| `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` | `PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING` |
| `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` | `PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH` |
| `PACKET_BLOCKED_UNSUPPORTED_SURFACE` | `PACKET_BLOCKED_UNSUPPORTED_SURFACE` |
| `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` | `PACKET_BLOCKED_CROSS_INFERENCE_FAMILY` |
| `PACKET_BLOCKED_CROSS_GEOMETRY` | `PACKET_BLOCKED_CROSS_GEOMETRY` |
| `PACKET_BLOCKED_CROSS_ESTIMAND` | `PACKET_BLOCKED_CROSS_ESTIMAND` |
| `PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION` | `PACKET_BLOCKED_SCOPE_VIOLATION` |
| `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` | `PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED` |
| `PACKET_NOT_REQUESTED` | `PACKET_NOT_REQUESTED` |

| Instrument-specific eligibility | Generic eligibility |
|--------------------------------|---------------------|
| `ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT` | `ELIGIBLE_AS_REVIEW_INPUT` |
| `NOT_ELIGIBLE_MISSING_EVIDENCE` | `NOT_ELIGIBLE_MISSING_EVIDENCE` |
| `NOT_ELIGIBLE_IDENTITY_MISMATCH` | `NOT_ELIGIBLE_IDENTITY_MISMATCH` |
| `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` | `NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING` |
| `NOT_ELIGIBLE_NULL_MONITOR_SCOPE_VIOLATION` | `NOT_ELIGIBLE_SCOPE_VIOLATION` |
| `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` | `NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW` |
| `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` | `NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK` |
| `NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW` | `NOT_ELIGIBLE_FOR_CLAIM_REVIEW` |

| Instrument-specific decision | Generic decision |
|-------------------------------|------------------|
| `APPROVE_NULL_MONITOR_REVIEW_CONTINUATION` | `APPROVE_REVIEW_CONTINUATION` |
| `REQUEST_ADDITIONAL_EVIDENCE` | `REQUEST_ADDITIONAL_EVIDENCE` |
| `REJECT_FOR_METHOD_VALIDITY` | `REJECT_FOR_METHOD_VALIDITY` |
| `REJECT_FOR_IDENTITY_MISMATCH` | `REJECT_FOR_IDENTITY_MISMATCH` |
| `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` | `REJECT_FOR_CLAIM_BOUNDARY_VIOLATION` |
| `REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION` | `REJECT_FOR_SCOPE_VIOLATION` |
| `REJECT_FOR_UNSUPPORTED_SURFACE` | `REJECT_FOR_UNSUPPORTED_SURFACE` |
| `REJECT_FOR_CROSS_INFERENCE_FAMILY` | `REJECT_FOR_CROSS_INFERENCE_FAMILY` |
| `REJECT_FOR_CROSS_GEOMETRY` | `REJECT_FOR_CROSS_GEOMETRY` |
| `REJECT_FOR_CROSS_ESTIMAND` | `REJECT_FOR_CROSS_ESTIMAND` |
| `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` | `DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW` |
| `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` | `DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW` |
| `NO_DECISION_PACKET_NOT_READY` | `NO_DECISION_PACKET_NOT_READY` |

## Boundary preservation

Decision summaries preserve `claim_authorization_status`, `catalog_status`, `production_compatibility_status`, `method_promotion_status`, `instrument_promotion_status`, and SCM `null_monitor_scope_status` (as `scope_status` in `boundary_statuses`). Missing boundary fields block adaptation.

## Prohibited action non-weakening

Minimum required prohibited actions: `method_promotion`, `instrument_promotion`, `catalog_unblock`, `production_compatibility_authorization`, `causal_lift_claim_authorization`, `business_lift_claim_authorization`, `confidence_interval_claim_authorization`, `p_value_claim_authorization`, `statistical_significance_claim_authorization`, `roi_roas_claim_authorization`, `decision_recommendation_authorization`, `production_readout_authorization`, `mip_decision_surface_approval`, `trust_report_bypass`, `claim_authorization_runtime_bypass`. Weakened or missing lists block adaptation.

## Alias handling

Canonical instrument identity is preserved. Catalog aliases are emitted separately in `aliases` but cannot substitute for canonical identity in adaptation input. Alias-substitution attempts block with `GENERIC_ADAPTER_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT`.

## Adapter blockers

Stable blocker names: `GENERIC_ADAPTER_BLOCKED_MISSING_SOURCE_PACKET`, `GENERIC_ADAPTER_BLOCKED_MISSING_SOURCE_DECISION`, `GENERIC_ADAPTER_BLOCKED_UNKNOWN_INSTRUMENT_IDENTITY`, `GENERIC_ADAPTER_BLOCKED_UNMAPPED_PACKET_STATUS`, `GENERIC_ADAPTER_BLOCKED_UNMAPPED_ELIGIBILITY_STATUS`, `GENERIC_ADAPTER_BLOCKED_UNMAPPED_DECISION_STATUS`, `GENERIC_ADAPTER_BLOCKED_MISSING_BOUNDARY_STATUS`, `GENERIC_ADAPTER_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT`, `GENERIC_ADAPTER_BLOCKED_PROHIBITED_ACTION_WEAKENED`, `GENERIC_ADAPTER_BLOCKED_SOURCE_OF_TRUTH_MISMATCH`

## MIP-facing summary boundary

Governance summaries expose review state for MIP-facing consumption but do not authorize MIP decisioning or TrustReport bypass. `mip_decisioning_status` and `trust_report_bypass_status` are fixed to non-authorization values.

## Non-goals

- Recompute packet readiness or review decisions
- Promote methods/instruments or unblock catalog
- Authorize production compatibility or claims
- Score raw evidence quality
- Implement AugSynth/DID adapter profiles
- Modify TBRRidge/SCM instrument-specific runtimes or Lane B runtime

## Validation results

`panel_exp/validation/method_promotion_generic_runtime_001.py` `run_validation()` exercises TBRRidge and SCM ready packet/decision chains, confirms generic `PACKET_READY_FOR_REVIEW_INPUT` and `APPROVE_REVIEW_CONTINUATION` mapping with correct `decision_scope`, and verifies non-authorization boundary preservation. Tests in `tests/validation/test_method_promotion_generic_runtime_001.py` and `tests/governance/test_method_promotion_generic_runtime_001.py` pass.

Summary: [`docs/track_d/archives/METHOD_PROMOTION_GENERIC_RUNTIME_001_summary.json`](archives/METHOD_PROMOTION_GENERIC_RUNTIME_001_summary.json)

## Recommended next artifact

**`METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001`**

Now that the generic adapter exists for completed applications, next choose whether AugSynth is ready for an instrument-specific evidence packet contract.
