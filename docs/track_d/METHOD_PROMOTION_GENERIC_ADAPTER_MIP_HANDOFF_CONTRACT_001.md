# METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_CONTRACT_001` |
| **Artifact type** | `method_promotion_generic_adapter_mip_handoff_contract` |
| **Lane** | Lane A — Method / instrument promotion framework application |
| **Status** | `completed` |
| **Scope** | `typed_handoff_contract_docs_only_no_mip_runtime_no_decision_authorization` |
| **Supported profile count** | `3` |
| **Final verdict** | `mip_handoff_contract_defined_no_runtime_no_decision_authorization` |
| **Recommended next** | `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001` |

**Depends on:**

- `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_READINESS_AUDIT_001`
- `METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001`
- `METHOD_PROMOTION_GENERIC_RUNTIME_001`

---

## 2. Why this contract exists

`METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_READINESS_AUDIT_001` concluded that generic adapter summaries are **READY_FOR_MIP_HANDOFF_CONTRACT** and **NOT_READY_FOR_MIP_RUNTIME_INTEGRATION**.

This contract formalizes the typed handoff object MIP may consume. Runtime integration is not authorized. MIP receives **governance context only**.

The contract prevents generic `APPROVE_REVIEW_CONTINUATION` from being interpreted as:

- DecisionSurface approval
- TrustReport bypass
- RecommendationContract authorization
- production readiness
- claim authorization
- catalog unblock
- production readout authorization
- spend/ROI recommendation
- business recommendation
- causal lift claim
- method/instrument promotion

---

## 3. Source surfaces

| Surface | Source owner | Source of truth | Handoff role |
|---------|--------------|-----------------|--------------|
| `MethodPromotionEvidencePacketSummary` | `panel_exp` | Instrument-specific packet runtime + generic adapter summary | Governance context only |
| `MethodPromotionReviewDecisionSummary` | `panel_exp` | Instrument-specific decision runtime + generic adapter summary | Governance context only |
| `MethodPromotionGovernanceSummary` | `panel_exp` | Rollup of packet/decision summaries via generic adapter | Governance context only |

No source surface authorizes MIP decisioning, RecommendationContract emission, TrustReport bypass, catalog unblock, production readiness, or claim authorization.

---

## 4. Supported profiles

| Profile | Canonical identity | Decision scope | Generic positive mapping | MIP interpretation |
|---------|-------------------|----------------|--------------------------|-------------------|
| `tbrridge_restricted_review_v1` | `geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review` | `restricted_review` | `APPROVE_REVIEW_CONTINUATION` | Method-governance context only; **not** production decisioning |
| `scm_jackknife_null_monitor_v1` | `geo.scm.jackknife.single_cell.delta_mu.null_monitor` | `null_monitor` | `APPROVE_REVIEW_CONTINUATION` | Diagnostic/null-monitor context only; **not** causal lift or production readout |
| `augsynth_jackknife_restricted_review_v1` | `geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review` | `restricted_review` | `APPROVE_REVIEW_CONTINUATION` | Method-governance context only; **not** production decisioning |

---

## 5. Handoff contract object

Conceptual object: **`MethodPromotionGenericAdapterMIPHandoff`**

| Field | Description |
|-------|-------------|
| `handoff_id` | Unique handoff record id |
| `source_package` | Always `panel_exp` |
| `source_artifact_id` | Generic adapter / handoff source artifact id |
| `source_runtime` | Generic adapter runtime id |
| `source_runtime_version` | Optional runtime version string |
| `profile_id` | Registered adapter profile |
| `canonical_identity` | Exact instrument identity |
| `decision_scope` | `restricted_review` or `null_monitor` |
| `generic_packet_status` | Mapped packet readiness |
| `generic_eligibility_status` | Mapped eligibility |
| `generic_decision_status` | Mapped decision (weak continuation only) |
| `generic_governance_stage` | `packet_only`, `decision_ready`, or `blocked_adapter` |
| `source_packet_ref` | Source packet summary/ref |
| `source_decision_ref` | Source decision summary/ref |
| `source_governance_summary_ref` | Source governance summary/ref |
| `source_of_truth_refs` | Packet/decision runtime artifact ids |
| `missing_evidence` | Preserved missing categories |
| `blockers` | Preserved blockers |
| `warnings` | Preserved warnings |
| `prohibited_actions` | Preserved prohibited actions |
| `boundary_statuses` | Source boundary fields |
| `mip_allowed_uses` | Enumerated allowed uses |
| `mip_prohibited_uses` | Enumerated prohibited uses |
| `decision_surface_authorization_status` | Fixed non-authorization |
| `trust_report_bypass_status` | Fixed non-bypass |
| `recommendation_authorization_status` | Fixed non-authorization |
| `catalog_authorization_status` | Fixed non-authorization |
| `production_readout_authorization_status` | Fixed non-authorization |
| `production_compatibility_authorization_status` | Fixed non-authorization |
| `claim_authorization_status` | Fixed non-authorization |
| `method_promotion_status` | Fixed non-promotion |
| `instrument_promotion_status` | Fixed non-promotion |
| `spend_roi_authorization_status` | Fixed non-authorization |
| `causal_lift_authorization_status` | Fixed non-authorization |
| `statistical_claim_authorization_status` | Fixed non-authorization |
| `lineage` | Audit lineage |
| `created_from_artifacts` | Artifact lineage list |

---

## 6. Required fields

**Required:**

- `handoff_id`
- `source_package` = `panel_exp`
- `profile_id`
- `canonical_identity`
- `decision_scope`
- `generic_decision_status`
- `source_of_truth_refs`
- `boundary_statuses`
- `mip_allowed_uses`
- `mip_prohibited_uses`
- all fixed MIP non-authorization statuses (section 7)
- `lineage`

**Optional:**

- `source_packet_ref`
- `source_decision_ref`
- `source_governance_summary_ref`
- `missing_evidence`
- `blockers`
- `warnings`
- `prohibited_actions`
- `source_runtime_version`
- `created_from_artifacts`

---

## 7. Fixed MIP-side non-authorization statuses

Always define:

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

## 8. MIP allowed uses

MIP may use handoff for:

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

---

## 9. MIP prohibited uses

MIP must not use handoff for:

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

## 10. Generic decision semantics for MIP

**`APPROVE_REVIEW_CONTINUATION` means only:**

- profile may continue through method-promotion governance review context
- governance summary is displayable/explainable
- MIP may route to further review lanes

**`APPROVE_REVIEW_CONTINUATION` does not mean:**

- production readiness
- business decision approval
- causal validity
- statistical validity
- catalog eligibility
- MIP RecommendationContract readiness
- MIP DecisionSurface approval

---

## 11. Handoff validity conditions

**Handoff is valid only if:**

- `profile_id` is supported by generic runtime
- `canonical_identity` is present
- `decision_scope` is present
- `source_of_truth_refs` are present
- fixed MIP non-authorization statuses are present
- MIP allowed/prohibited uses are present
- source summary is not used to override source runtimes
- generic runtime summary remains source-of-truth for summarization only

**Invalid handoff conditions:**

- missing canonical identity
- missing `decision_scope`
- missing source-of-truth refs
- missing fixed MIP non-authorization statuses
- missing prohibited uses
- any DecisionSurface / Recommendation / TrustReport / claim / catalog / production authorization flag true
- any method/instrument promotion flag true
- generic approval interpreted as production or recommendation readiness

---

## 12. MIP routing implications

**Allowed routes:**

- show governance summary
- show missing evidence / blockers / warnings
- route to catalog governance review as separate lane
- route to claim authorization review as separate lane
- route to production compatibility review as separate lane
- request package-side clarification
- block recommendation generation when handoff is non-authorizing

**Blocked routes:**

- create DecisionSurface
- emit RecommendationContract
- approve budget/spend movement
- produce ROI/ROAS recommendation
- bypass TrustReport
- claim causal lift / statistical significance
- mark method production-ready

---

## 13. Relationship to existing boundaries

| Boundary | Relationship |
|----------|--------------|
| Generic adapter runtime | Source summary provider; summarizer only |
| Source packet/decision runtimes | Authoritative instrument-specific source |
| Claim Authorization runtime | Separate; not bypassed |
| Catalog governance | Separate; not unblocked |
| Production compatibility | Separate; not authorized |
| Lane B spend/ROI | Orthogonal; not authorized |
| MIP | Downstream consumer of governance context only |

---

## 14. Recommended next artifact

**`METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001`**

Scope:

- implement package-side handoff builder/serializer from generic adapter summaries
- no MIP runtime integration
- no DecisionSurface authorization
- no TrustReport bypass
- no RecommendationContract authorization
- no promotion / claim / catalog / production authorization

---

## 15. Non-goals

- No generic runtime changed
- No new profile registered
- No MIP runtime implemented
- No MIP handoff runtime implemented
- No DecisionSurface authorized
- No TrustReport bypass
- No RecommendationContract authorized
- No method promoted
- No instrument promoted
- No TBRRidge, SCM, AugSynth, or DID promotion
- No catalog unblock
- No production compatibility authorization
- No claim authorization change
- No statistical, CI, p-value, significance, or power claim authorization
- No causal/business lift or ROI/ROAS claim authorization
- No decision recommendation or production readout authorization
- No estimator/inference implementation
- No new validation experiments
- No raw evidence quality scoring
- No Lane B runtime changes

---

## 16. Validation results

- `python -m json.tool docs/track_d/archives/METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_CONTRACT_001_summary.json` — valid JSON
- `python -m pytest tests/governance/test_method_promotion_generic_adapter_mip_handoff_contract_001.py -q` — governance assertions pass
- `python -m pytest tests/governance -q` — full governance suite pass
- Safety grep — no forbidden promotion/MIP/runtime/authorization flags true
- Capability grep — handoff contract/object, fixed non-authorization statuses, allowed/prohibited uses, and source-of-truth boundary flags true

Summary: [`docs/track_d/archives/METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_CONTRACT_001_summary.json`](archives/METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_CONTRACT_001_summary.json)
