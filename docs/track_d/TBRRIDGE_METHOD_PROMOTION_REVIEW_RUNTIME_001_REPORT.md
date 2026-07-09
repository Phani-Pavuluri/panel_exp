# TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001` |
| **Artifact type** | `tbrridge_method_promotion_review_runtime` |
| **Status** | `completed` |
| **Scope** | `tbrridge_method_promotion_review_runtime_implemented_no_promotion_or_catalog_unblock` |
| **Base commit** | `60ea3a3` (Define TBRRidge method promotion review contract) |
| **Final verdict** | `tbrridge_method_promotion_review_runtime_implemented_no_promotion_or_catalog_unblock` |

**Depends on:** `TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001` · `TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001` · `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001` · `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001`

---

## 2. Source files inspected

- `panel_exp/validation/tbrridge_method_promotion_review_contract_001.py`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001_REPORT.md`
- `docs/track_d/archives/TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001_summary.json`
- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001.md`
- `panel_exp/validation/tbrridge_uncertainty_candidate_review_runtime_001.py`
- `panel_exp/validation/tbrridge_uncertainty_candidate_review_contract_001.py`

---

## 3. Relationship to contract

This runtime **implements** `TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001` by assembling method-promotion review packets from supplied evidence only. Status semantics, risk taxonomy, required evidence, allowed/prohibited surfaces, and failure codes are delegated to `evaluate_method_promotion_review()` in the contract module.

**Core principle:** The runtime reviews supplied evidence and emits structured promotion-readiness summaries. It does not compute evidence, run inference, promote TBRRidge, unblock catalog status, authorize production compatibility, approve uncertainty, authorize CI/p-value/significance claims, compute lift/ROI, or create production readouts.

---

## 4. Relationship to method-promotion evidence audit

Consumes `method_promotion_evidence_audit_report` as the anchor of the promotion evidence chain. The audit defined sufficiency requirements and stop/go criteria; this runtime evaluates whether supplied packets satisfy those requirements without granting promotion.

---

## 5. Relationship to uncertainty-candidate review runtime

Delegates `uncertainty_candidate_review_packet.review_status` to determine whether upstream uncertainty-candidate review is blocking. Blocking uncertainty-candidate statuses propagate to `METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW`. Ready statuses (`UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW`, `UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS`) permit restricted promotion-readiness summaries when all other required evidence is present and non-blocking.

---

## 6. Runtime inputs

Supplied evidence only (dict, dataclass-like object, or list of bundles):

- `method_promotion_evidence_audit_report`
- `uncertainty_candidate_review_packet`
- `false_confidence_audit_report`
- `leakage_diagnostic_report`
- `placebo_calibration_diagnostic_report`
- `coverage_validation_report`
- `interval_semantics_report`
- `null_control_false_positive_report`
- `directional_error_report`
- `positive_control_recovery_report`
- `regime_sensitivity_report`
- `donor_pool_sensitivity_report`
- `regularization_sensitivity_report`
- `outlier_sensitivity_report`
- `fold_geometry_sensitivity_report`
- `metric_estimand_alignment_report`
- `aggregate_pooled_geometry_blocker_report`
- `claim_authorization_boundary_report`
- `production_catalog_status_report`
- `production_compatibility_boundary_report`
- `downstream_readout_safety_report`
- `lineage_provenance_manifest`

Optional: `request_id`, `requested_surface`, `deferred`, method/instrument/catalog metadata.

---

## 7. Runtime packet fields

`review_id` · `review_status` · `method_id` · `instrument_id` · `current_catalog_rank` · `current_catalog_status` · `current_readiness_stage` · `target_review_stage` · `evidence_chain_summary` · `evidence_components_reviewed` · `required_evidence` · `missing_evidence` · `detected_promotion_risks` · `blockers` · `restrictions` · `allowed_surfaces` · `prohibited_surfaces` · `failure_packet` · `recommended_next_action` · `lineage_manifest` · `provenance_hash` · `policy_version`

---

## 8. Status delegation rules

| Upstream signal | Review status |
|-----------------|---------------|
| Missing core evidence | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN` |
| Blocking uncertainty-candidate review | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW` |
| Missing/incomplete interval semantics | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS` |
| Missing null-control false-positive evidence | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE` |
| Missing directional-error evidence | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE` |
| Missing positive-control recovery evidence | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY` |
| Missing regime sensitivity evidence | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_REGIME_SENSITIVITY` |
| Metric/estimand mismatch | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH` |
| Unsupported aggregate/pooled geometry | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_AGGREGATE_POOLED_GEOMETRY` |
| Missing claim authorization boundary | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY` |
| Prohibited surface requested | `METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY` |
| Production compatibility not reviewed (production surfaces) | `METHOD_PROMOTION_REVIEW_REQUIRES_PRODUCTION_COMPATIBILITY_REVIEW` |
| All evidence present with restrictions | `METHOD_PROMOTION_REVIEW_READY_WITH_RESTRICTIONS` |
| All evidence present, non-blocking | `METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW` |

TBRRidge posture remains **RANK_0**, **BLOCKED**, **STAGE_2_DIAGNOSTIC_ONLY** regardless of review status.

---

## 9. Risk detection rules

`detect_tbrridge_method_promotion_risks()` flags risks from supplied report boolean fields only:

- `INTERVAL_SEMANTICS_INCOMPLETE` — interval semantics report flags
- `NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE` — null-control false-positive report flags
- `DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE` — directional-error report flags
- `POSITIVE_CONTROL_RECOVERY_INCOMPLETE` — positive-control recovery report flags
- `REGIME_SENSITIVITY_INCOMPLETE` — regime sensitivity report flags
- `DONOR_POOL_SENSITIVITY_INCOMPLETE` — donor-pool sensitivity report flags
- `REGULARIZATION_SENSITIVITY_INCOMPLETE` — regularization sensitivity report flags
- `OUTLIER_SENSITIVITY_INCOMPLETE` — outlier sensitivity report flags
- `FOLD_GEOMETRY_SENSITIVITY_INCOMPLETE` — fold-geometry sensitivity report flags
- `METRIC_ESTIMAND_MISMATCH` — metric/estimand alignment or interval semantics flags
- `AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED` — aggregate/pooled geometry blocker flags
- `CLAIM_AUTHORIZATION_BOUNDARY_MISSING` — claim authorization boundary flags
- `PRODUCTION_CATALOG_BLOCKED` — production catalog status flags
- `PRODUCTION_COMPATIBILITY_NOT_REVIEWED` — production compatibility boundary flags
- `DOWNSTREAM_READOUT_SAFETY_INCOMPLETE` — downstream readout safety flags
- `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING` — non-ready uncertainty-candidate review status

No statistical quantities are computed.

---

## 10. Failure packet semantics

`build_tbrridge_method_promotion_failure_packet()` emits:

- `failure_code` · `failure_reason` · `detected_promotion_risks` · `missing_evidence` · `required_remediation` · `retry_category`

Failure codes match the contract: `MISSING_METHOD_PROMOTION_EVIDENCE_AUDIT`, `MISSING_UNCERTAINTY_CANDIDATE_REVIEW_PACKET`, `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING`, `INTERVAL_SEMANTICS_INCOMPLETE`, `NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE`, `DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE`, `POSITIVE_CONTROL_RECOVERY_INCOMPLETE`, `REGIME_SENSITIVITY_INCOMPLETE`, `METRIC_ESTIMAND_MISMATCH`, `AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED`, `CLAIM_AUTHORIZATION_BOUNDARY_MISSING`, `PRODUCTION_CATALOG_BLOCKED`, `PRODUCTION_COMPATIBILITY_NOT_REVIEWED`, `METHOD_PROMOTION_SURFACE_BLOCKED`.

---

## 11. Allowed/prohibited surfaces

**Allowed:** `DIAGNOSTIC_ONLY` · `RESEARCH_OR_REVIEW_ONLY` · `METHOD_PROMOTION_EVIDENCE_SUMMARY` · `METHOD_PROMOTION_READINESS_SUMMARY` · `REMAINING_BLOCKERS_SUMMARY` · `FUTURE_PROMOTION_RUNTIME_INPUT` · `PRODUCTION_COMPATIBILITY_REVIEW_INPUT_DESCRIPTION`

**Prohibited (always blocked):** `METHOD_PROMOTION_NOTICE` · `CATALOG_UNBLOCK_NOTICE` · `PRODUCTION_COMPATIBILITY_NOTICE` · `PRODUCTION_AUTHORIZATION_NOTICE` · `PRODUCTION_READOUT` · `UNCERTAINTY_APPROVAL_NOTICE` · `CONFIDENCE_INTERVAL_CLAIM` · `P_VALUE_CLAIM` · `STATISTICAL_SIGNIFICANCE_CLAIM` · `CAUSAL_LIFT_CLAIM` · `ROI_CLAIM`

---

## 12. Deterministic ID/provenance behavior

- `review_id` = `tmpr-` + first 16 hex chars of SHA-256 over canonical `{request_id, method_id, instrument_id, review_status, detected_promotion_risks, current_catalog_rank, current_readiness_stage}`
- `provenance_hash` = SHA-256 over full packet body (excluding provenance_hash field)
- List inputs return independent packets with no ranking

---

## 13. Validation results

| Check | Result |
|-------|--------|
| Contract validation tests | Pass |
| Runtime validation tests | Pass |
| Governance registry tests | Pass |
| `failed_scenarios` | `[]` |

---

## 14. Authorization boundary

**Allowed (true):** `method_promotion_review_runtime_implemented`, `supplied_promotion_evidence_reviewed`, `missing_promotion_evidence_detected`, `uncertainty_candidate_review_status_delegated`, `promotion_risk_detection_implemented`, `promotion_failure_packet_emitted`, `deterministic_provenance_hash_defined`

**Forbidden (false):** method promotion, catalog unblock, production compatibility/authorization, uncertainty approval, CI/p-value/significance, coverage/interval computation, inference/estimator implementation, lift/ROI, MMM runtime, LLM decisioning

---

## 15. Known limitations

- Does not generate or compute any evidence; all inputs must be pre-supplied
- Does not invoke upstream diagnostic runtimes; only consumes their report packets
- Does not promote TBRRidge or change catalog rank/status
- Production compatibility review is a separate deferred lane
- Optional sensitivity evidence gaps yield `READY_WITH_RESTRICTIONS`, not hard blocks

---

## 16. Recommended next artifact

**Primary:** `TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001`

**Alternative:** `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`
