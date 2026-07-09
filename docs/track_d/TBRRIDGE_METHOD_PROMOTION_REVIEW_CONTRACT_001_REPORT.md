# TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001` |
| **Artifact type** | `tbrridge_method_promotion_review_contract` |
| **Status** | `completed` |
| **Scope** | `tbrridge_method_promotion_review_contract_defined_no_promotion_or_catalog_unblock` |
| **Base commit** | `5f296e6` (Add TBRRidge method promotion evidence audit) |
| **Final verdict** | `tbrridge_method_promotion_review_contract_defined_no_promotion_or_catalog_unblock` |

**Depends on:** `TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001` · `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001` · `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001` · `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001` · `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001` · `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001.md`
- `docs/track_d/archives/TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001_summary.json`
- `docs/track_d/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001_REPORT.md`
- `panel_exp/validation/tbrridge_uncertainty_candidate_review_contract_001.py`
- `panel_exp/validation/tbrridge_uncertainty_candidate_review_runtime_001.py`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`
- `docs/track_d/METHOD_PROMOTION_CANDIDATE_AUDIT_001.md`
- `docs/track_d/METHOD_PROMOTION_REVIEW_CONTRACT_001_REPORT.md`

---

## 3. Relationship to method-promotion evidence audit

`TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001` found TBRRidge KFold at `METHOD_PROMOTION_EVIDENCE_READY_FOR_CONTRACT` with complete diagnostic scaffolding but incomplete evidence batteries. This contract **operationalizes** that audit into governed promotion-review statuses, risk taxonomy, required evidence, packet shape, failure semantics, and future runtime acceptance criteria.

**Core principle:** Defining a promotion-review contract does not promote TBRRidge or change RANK_0 / catalog-blocked / diagnostic-only posture.

---

## 4. Relationship to uncertainty-candidate review runtime

Method-promotion review must consume a non-blocking `uncertainty_candidate_review_packet` at `UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW` or `READY_WITH_RESTRICTIONS`. Blocking uncertainty-candidate statuses block promotion review with `METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW`.

Uncertainty-candidate review is a prerequisite gate, not a promotion authorization.

---

## 5. Relationship to sophisticated-method evidence ladder

Per `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001`, TBRRidge KFold remains at **STAGE_2_DIAGNOSTIC_ONLY** with target review stage **STAGE_5_METHOD_PROMOTION_CANDIDATE**. This contract defines the governed gate shape without advancing the ladder or granting promotion.

---

## 6. Relationship to production compatibility boundary

`PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` remains **deferred**. Production compatibility surfaces require separate review via `METHOD_PROMOTION_REVIEW_REQUIRES_PRODUCTION_COMPATIBILITY_REVIEW`. Method promotion and production compatibility are explicitly separated.

---

## 7. Promotion review statuses

| Status | Meaning |
|--------|---------|
| `METHOD_PROMOTION_REVIEW_NOT_EVALUATED` | No promotion-review evidence submitted |
| `METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW` | Evidence chain present and non-blocking |
| `METHOD_PROMOTION_REVIEW_READY_WITH_RESTRICTIONS` | Restricted summary allowed with flagged risks |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN` | Required evidence missing |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW` | Uncertainty-candidate review blocking |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS` | Interval semantics incomplete |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE` | Null-control FPR evidence missing |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE` | Directional-error evidence missing |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY` | Positive-control recovery missing |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_REGIME_SENSITIVITY` | Regime sensitivity missing |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH` | Metric/estimand mismatch |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_AGGREGATE_POOLED_GEOMETRY` | Aggregate/pooled geometry unsupported |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY` | Claim boundary missing or prohibited surface |
| `METHOD_PROMOTION_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG_STATUS` | Catalog blocked for production surfaces |
| `METHOD_PROMOTION_REVIEW_REQUIRES_PRODUCTION_COMPATIBILITY_REVIEW` | Production compatibility not reviewed |
| `METHOD_PROMOTION_REVIEW_DEFERRED` | Explicitly deferred |

**No status grants method promotion, catalog unblock, production compatibility, uncertainty approval, or production readout authorization.**

---

## 8. Promotion risk taxonomy

`MISSING_EVIDENCE_CHAIN` · `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING` · `INTERVAL_SEMANTICS_INCOMPLETE` · `NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE` · `DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE` · `POSITIVE_CONTROL_RECOVERY_INCOMPLETE` · `REGIME_SENSITIVITY_INCOMPLETE` · `DONOR_POOL_SENSITIVITY_INCOMPLETE` · `REGULARIZATION_SENSITIVITY_INCOMPLETE` · `OUTLIER_SENSITIVITY_INCOMPLETE` · `FOLD_GEOMETRY_SENSITIVITY_INCOMPLETE` · `METRIC_ESTIMAND_MISMATCH` · `AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED` · `CLAIM_AUTHORIZATION_BOUNDARY_MISSING` · `PRODUCTION_CATALOG_BLOCKED` · `PRODUCTION_COMPATIBILITY_NOT_REVIEWED` · `DOWNSTREAM_READOUT_SAFETY_INCOMPLETE`

---

## 9. Required evidence

`method_promotion_evidence_audit_report` · `uncertainty_candidate_review_packet` · `false_confidence_audit_report` · `leakage_diagnostic_report` · `placebo_calibration_diagnostic_report` · `coverage_validation_report` · `interval_semantics_report` · `null_control_false_positive_report` · `directional_error_report` · `positive_control_recovery_report` · `regime_sensitivity_report` · `donor_pool_sensitivity_report` · `regularization_sensitivity_report` · `outlier_sensitivity_report` · `fold_geometry_sensitivity_report` · `metric_estimand_alignment_report` · `aggregate_pooled_geometry_blocker_report` · `claim_authorization_boundary_report` · `production_catalog_status_report` · `production_compatibility_boundary_report` · `downstream_readout_safety_report` · `lineage_provenance_manifest`

---

## 10. Future runtime packet fields

`review_id` · `review_status` · `method_id` · `instrument_id` · `current_catalog_rank` · `current_catalog_status` · `current_readiness_stage` · `target_review_stage` · `evidence_chain_summary` · `evidence_components_reviewed` · `required_evidence` · `missing_evidence` · `detected_promotion_risks` · `blockers` · `restrictions` · `allowed_surfaces` · `prohibited_surfaces` · `failure_packet` · `recommended_next_action` · `lineage_manifest` · `provenance_hash` · `policy_version`

---

## 11. Allowed / prohibited surfaces

**Allowed:** `DIAGNOSTIC_ONLY` · `RESEARCH_OR_REVIEW_ONLY` · `METHOD_PROMOTION_EVIDENCE_SUMMARY` · `METHOD_PROMOTION_READINESS_SUMMARY` · `REMAINING_BLOCKERS_SUMMARY` · `FUTURE_PROMOTION_RUNTIME_INPUT` · `PRODUCTION_COMPATIBILITY_REVIEW_INPUT_DESCRIPTION`

**Prohibited:** `METHOD_PROMOTION_NOTICE` · `CATALOG_UNBLOCK_NOTICE` · `PRODUCTION_COMPATIBILITY_NOTICE` · `PRODUCTION_AUTHORIZATION_NOTICE` · `PRODUCTION_READOUT` · `UNCERTAINTY_APPROVAL_NOTICE` · `CONFIDENCE_INTERVAL_CLAIM` · `P_VALUE_CLAIM` · `STATISTICAL_SIGNIFICANCE_CLAIM` · `CAUSAL_LIFT_CLAIM` · `ROI_CLAIM`

---

## 12. Failure packet semantics

| Field | Purpose |
|-------|---------|
| `failure_code` | Standardized blocker |
| `failure_reason` | Human-readable summary |
| `detected_promotion_risks` | Failed risk taxonomy items |
| `missing_evidence` | Required reports not present |
| `required_remediation` | Retry category |
| `retry_category` | Governed remediation action |

**Failure codes:** `MISSING_METHOD_PROMOTION_EVIDENCE_AUDIT` · `MISSING_UNCERTAINTY_CANDIDATE_REVIEW_PACKET` · `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING` · `INTERVAL_SEMANTICS_INCOMPLETE` · `NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE` · `DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE` · `POSITIVE_CONTROL_RECOVERY_INCOMPLETE` · `REGIME_SENSITIVITY_INCOMPLETE` · `METRIC_ESTIMAND_MISMATCH` · `AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED` · `CLAIM_AUTHORIZATION_BOUNDARY_MISSING` · `PRODUCTION_CATALOG_BLOCKED` · `PRODUCTION_COMPATIBILITY_NOT_REVIEWED` · `METHOD_PROMOTION_SURFACE_BLOCKED`

---

## 13. Future runtime acceptance criteria

- Blocks without method-promotion evidence audit
- Blocks without uncertainty-candidate review packet
- Blocks when uncertainty-candidate review is blocking
- Blocks without interval semantics, null FPR, directional-error, positive-control recovery, regime sensitivity evidence
- Blocks on metric/estimand mismatch and unsupported aggregate/pooled geometry
- Blocks without claim authorization boundary
- Blocks production surfaces while catalog remains blocked
- Requires separate production compatibility review before production claims
- Permits restricted promotion-readiness summary only when evidence present and non-blocking
- Always blocks method promotion, catalog unblock, production compatibility, uncertainty approval, CI/p-value/significance, lift, ROI, and production readout surfaces
- Emits deterministic `review_id`/`provenance_hash`
- All forbidden computation/authorization flags false

---

## 14. Authorization boundary

| Flag | Value |
|------|-------|
| `tbrridge_method_promotion_review_contract_defined` | true |
| `promotion_review_statuses_defined` | true |
| `promotion_risk_taxonomy_defined` | true |
| `promotion_required_evidence_defined` | true |
| `promotion_failure_packet_semantics_defined` | true |
| `promotion_future_runtime_tests_documented` | true |
| `method_promotion_review_runtime_implemented` | false |
| `method_promoted` | false |
| `method_promotion_authorized` | false |
| `production_catalog_unblocked` | false |
| `uncertainty_authorized` | false |
| `production_readout_authorized` | false |

---

## 15. Validation results

- Contract module validates all statuses, risks, evidence, surfaces, and flags
- Summary JSON valid
- Governance and validation tests pass
- Safety grep: no forbidden `true` promotion/authorization/computation flags

---

## 16. Known limitations

- Contract only; no promotion-review runtime implementation
- Does not re-run D5-TRUST-TBRRIDGE-KFOLD-001 batteries
- Does not upgrade RANK_0 or unblock catalog
- BRB path out of scope; KFold-specific

---

## 17. Recommended next artifact

**Primary:** `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001`

**Alternative:** `TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`
