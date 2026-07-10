# METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001

## 1. Metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001` |
| **Artifact type** | `method_promotion_generic_adapter_mip_handoff_runtime` |
| **Lane** | Lane A — Method / instrument promotion framework application |
| **Status** | `completed` |
| **Scope** | `package_side_handoff_runtime_no_mip_runtime_no_decision_authorization` |
| **Supported profile count** | `3` |
| **Final verdict** | `package_side_mip_handoff_runtime_implemented_no_mip_runtime_no_decision_authorization` |
| **Recommended next** | `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001` |

**Depends on:**

- `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_CONTRACT_001`
- `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_READINESS_AUDIT_001`
- `METHOD_PROMOTION_GENERIC_RUNTIME_001`

**Runtime module:** `panel_exp.validation.method_promotion_generic_adapter_mip_handoff_runtime_001`

---

## 2. Contract dependency

Implements the typed handoff object defined by `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_CONTRACT_001`:

**`MethodPromotionGenericAdapterMIPHandoff`**

This runtime is package-side only. It builds and serializes a non-authorizing MIP handoff from existing generic adapter governance summaries. It does **not** implement MIP runtime integration, DecisionSurface creation, TrustReport bypass, RecommendationContract authorization, claim/catalog/production authorization, or method/instrument promotion.

---

## 3. Runtime API

```python
from panel_exp.validation.method_promotion_generic_adapter_mip_handoff_runtime_001 import (
    MethodPromotionGenericAdapterMIPHandoff,
    MethodPromotionGenericAdapterMIPHandoffInput,
    MethodPromotionGenericAdapterMIPHandoffStatus,
    MethodPromotionGenericAdapterMIPAuthorizationStatus,
    MethodPromotionGenericAdapterMIPBypassStatus,
    MethodPromotionGenericAdapterMIPPromotionStatus,
    build_method_promotion_generic_adapter_mip_handoff,
    serialize_method_promotion_generic_adapter_mip_handoff,
)
```

---

## 4. Input/output object

### Input (`MethodPromotionGenericAdapterMIPHandoffInput`)

| Field | Required | Notes |
|-------|----------|-------|
| `handoff_id` | yes | Unique handoff id |
| `source_artifact_id` | no | Defaults to this artifact id |
| `source_runtime` | no | Defaults to `METHOD_PROMOTION_GENERIC_RUNTIME_001` |
| `source_runtime_version` | no | Optional version string |
| `governance_summary` | yes for ready | `MethodPromotionGovernanceSummary` or dict |
| `source_packet_ref` | no | Optional packet summary ref |
| `source_decision_ref` | no | Optional decision summary ref |
| `source_governance_summary_ref` | no | Optional governance summary ref |
| `created_from_artifacts` | no | Lineage artifact list |
| `lineage` | no | Audit lineage dict |
| `generic_packet_status` | no | Pass-through enrichment only |
| `generic_eligibility_status` | no | Pass-through enrichment only |
| `generic_decision_status` | no | Pass-through enrichment only |
| `decision_scope` | no | Override only if already known; not recomputed |
| `warnings` | no | Pass-through |
| `boundary_statuses` | no | Override only if already known |
| `source_of_truth_refs` | no | Override only if already known |
| `profile_id` | no | Override only if already known |

### Output (`MethodPromotionGenericAdapterMIPHandoff`)

Includes profile identity, decision scope, generic statuses, source refs, missing evidence, blockers, warnings, prohibited actions, boundary statuses, MIP allowed/prohibited uses, fixed non-authorization statuses, lineage, and `handoff_status`.

---

## 5. Builder behavior

`build_method_promotion_generic_adapter_mip_handoff(handoff_input)`:

1. Derives `profile_id`, `canonical_identity`, `decision_scope`, generic statuses, blockers, warnings, prohibited actions, and boundary statuses from `MethodPromotionGovernanceSummary` (and registered adapter profile lookup by identity).
2. Does **not** recompute packet readiness.
3. Does **not** recompute decision status.
4. Does **not** inspect raw evidence.
5. Does **not** upgrade or repair missing source fields.
6. Preserves source-of-truth refs from the registered profile.
7. Always applies fixed MIP non-authorization statuses.
8. If required fields are missing, returns a blocked handoff status with blockers (does not raise).
9. If `generic_decision_status` is `APPROVE_REVIEW_CONTINUATION`, preserves it only as weak governance context.
10. Serialization produces a JSON-safe dict with enum values as strings.

---

## 6. Fixed statuses

| Status field | Fixed value |
|--------------|-------------|
| `decision_surface_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `trust_report_bypass_status` | `NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF` |
| `recommendation_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `catalog_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `production_readout_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `production_compatibility_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `claim_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `method_promotion_status` | `NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF` |
| `instrument_promotion_status` | `NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF` |
| `spend_roi_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `causal_lift_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `statistical_claim_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |

---

## 7. Allowed/prohibited uses

### MIP allowed uses

- `governance_context`
- `method_review_lineage`
- `profile_identity_display`
- `decision_scope_display`
- `missing_evidence_display`
- `blockers_display`
- `warnings_display`
- `prohibited_actions_display`
- `non_authorization_status_display`
- `routing_to_separate_catalog_review`
- `routing_to_separate_claim_review`
- `routing_to_separate_production_review`
- `preventing_unsupported_recommendations`
- `explaining_restricted_review_or_null_monitor_scope`

### MIP prohibited uses

- `decision_surface_approval`
- `trust_report_bypass`
- `recommendation_contract_authorization`
- `spend_movement_recommendation`
- `budget_optimization_authorization`
- `roi_roas_calculation_or_authorization`
- `production_readout_authorization`
- `production_compatibility_authorization`
- `catalog_unblock`
- `claim_authorization`
- `causal_lift_claim`
- `business_lift_claim`
- `statistical_significance_claim`
- `confidence_interval_claim`
- `p_value_claim`
- `statistical_power_claim`
- `method_promotion`
- `instrument_promotion`
- `overriding_source_packet_runtime`
- `overriding_source_decision_runtime`
- `raw_evidence_quality_scoring`

---

## 8. Valid handoff behavior

When governance summary provides canonical identity, resolvable profile, decision scope, source-of-truth refs, and boundary statuses, builder returns:

`HANDOFF_READY_FOR_MIP_GOVERNANCE_CONTEXT`

This means the handoff is ready for MIP **governance context** consumption only. It does **not** imply MIP runtime readiness, DecisionSurface readiness, recommendation readiness, claim readiness, catalog readiness, or production readiness.

`APPROVE_REVIEW_CONTINUATION` is preserved as weak governance context only.

---

## 9. Blocked handoff behavior

| Status | Trigger |
|--------|---------|
| `HANDOFF_BLOCKED_MISSING_GOVERNANCE_SUMMARY` | No governance summary provided |
| `HANDOFF_BLOCKED_MISSING_PROFILE_ID` | Profile cannot be resolved |
| `HANDOFF_BLOCKED_MISSING_CANONICAL_IDENTITY` | Instrument identity missing |
| `HANDOFF_BLOCKED_MISSING_DECISION_SCOPE` | Decision scope missing |
| `HANDOFF_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS` | Source-of-truth refs missing |
| `HANDOFF_BLOCKED_MISSING_BOUNDARY_STATUSES` | Boundary statuses missing |
| `HANDOFF_BLOCKED_AUTHORIZATION_FLAG_PRESENT` | Authorizing boundary flag detected |
| `HANDOFF_BLOCKED_INVALID_PROHIBITED_USE_POLICY` | Required prohibited uses incomplete |

Blocked handoffs still carry fixed non-authorization statuses and allowed/prohibited use constants.

---

## 10. Supported profiles

| Profile | Canonical identity | Decision scope |
|---------|-------------------|----------------|
| `tbrridge_restricted_review_v1` | `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` | `restricted_review` |
| `scm_jackknife_null_monitor_v1` | `geo.scm.jackknife.single_cell.delta_mu.null_monitor` | `null_monitor` |
| `augsynth_jackknife_restricted_review_v1` | `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` | `restricted_review` |

---

## 11. Non-authorization guarantees

- `handoff_runtime_implemented` = true (package-side only)
- `handoff_builder_implemented` = true
- `handoff_serializer_implemented` = true
- `fixed_mip_non_authorization_statuses_enforced` = true
- `mip_allowed_uses_enforced` = true
- `mip_prohibited_uses_enforced` = true
- `source_of_truth_boundary_preserved` = true
- `raw_evidence_not_inspected` = true
- `packet_readiness_not_recomputed` = true
- `decision_status_not_recomputed` = true
- `generic_runtime_changed` = false
- `new_profile_registered` = false
- `mip_runtime_implemented` = false
- `decision_surface_authorized` = false
- `trust_report_bypassed` = false
- `recommendation_contract_authorized` = false
- `method_promoted` = false
- `instrument_promoted` = false
- `tbrridge_promoted` = false
- `scm_promoted` = false
- `augsynth_promoted` = false
- `did_promoted` = false
- `catalog_unblocked` = false
- `production_compatibility_authorized` = false
- `claim_authorization_changed` = false
- `statistical_claim_authorized` = false
- `confidence_interval_claim_authorized` = false
- `p_value_claim_authorized` = false
- `significance_claim_authorized` = false
- `statistical_power_claim_authorized` = false
- `causal_lift_claim_authorized` = false
- `business_lift_claim_authorized` = false
- `roi_roas_claim_authorized` = false
- `decision_recommendation_authorized` = false
- `production_readout_authorized` = false
- `estimator_implemented` = false
- `inference_implemented` = false
- `new_validation_experiments_run` = false
- `raw_evidence_quality_scored` = false
- `lane_b_runtime_changed` = false

---

## 12. Serialization semantics

`serialize_method_promotion_generic_adapter_mip_handoff(handoff)` returns a JSON-safe `dict`:

- enum fields serialized as strings
- tuples serialized as lists via `dataclasses.asdict`
- no live objects or non-JSON types

---

## 13. Tests/validation

- `tests/validation/test_method_promotion_generic_adapter_mip_handoff_runtime_001.py`
- `tests/governance/test_method_promotion_generic_adapter_mip_handoff_runtime_001.py`
- Summary: [`docs/track_d/archives/METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001_summary.json`](archives/METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001_summary.json)

---

## 14. Recommended next artifact

**`METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001`**

Reason: After package-side runtime exists, checkpoint whether it is stable enough for MIP-side integration planning. Do **not** jump directly to MIP runtime integration.

---

## 15. Non-goals

- No MIP runtime integration
- No DecisionSurface authorization
- No TrustReport bypass
- No RecommendationContract authorization
- No method/instrument promotion
- No claim/catalog/production authorization
- No spend/ROI decisioning
- No generic runtime change
- No new profile registration
- No raw evidence quality scoring
- No packet readiness or decision status recomputation
- No Lane B runtime changes
