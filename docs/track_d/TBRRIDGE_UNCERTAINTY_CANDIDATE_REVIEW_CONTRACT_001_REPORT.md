# TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001` |
| **Artifact type** | `tbrridge_uncertainty_candidate_review_contract` |
| **Status** | `completed` |
| **Scope** | `tbrridge_uncertainty_candidate_review_contract_defined_no_runtime_or_uncertainty_approval` |
| **Base commit** | `145c3f0` (Add TBRRidge uncertainty candidate review audit) |
| **Final verdict** | `tbrridge_uncertainty_candidate_review_contract_defined_no_runtime_or_uncertainty_approval` |

**Depends on:** `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001` · `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001` · `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001` · `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001.md`
- `docs/track_d/archives/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001_summary.json`
- `docs/track_d/TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001_REPORT.md`
- `docs/track_d/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001_REPORT.md`
- `panel_exp/validation/tbrridge_kfold_leakage_diagnostic_runtime_001.py`
- `panel_exp/validation/tbrridge_placebo_calibration_diagnostic_runtime_001.py`
- `panel_exp/validation/tbrridge_kfold_coverage_validation_runtime_001.py`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`
- `docs/track_d/METHOD_PROMOTION_CANDIDATE_AUDIT_001.md`
- `docs/track_d/METHOD_PROMOTION_REVIEW_CONTRACT_001_REPORT.md`
- `docs/track_d/METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md`

---

## 3. Relationship to uncertainty candidate review audit

`TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001` reviewed the TBRRidge KFold diagnostic chain, evidence sufficiency matrix, remaining blockers, and stop/go criteria. It found diagnostic scaffolding ready for a future restricted uncertainty-candidate review contract, but evidence batteries remain incomplete for uncertainty approval.

This contract **operationalizes** that audit into governed review statuses, risk taxonomy, required evidence chain, packet shape, failure semantics, allowed/prohibited surfaces, and future runtime acceptance criteria.

**Core principle:** Diagnostic evidence must not convert into uncertainty approval or production readiness. This contract defines what a future restricted review packet may summarize; it does not approve uncertainty, promote TBRRidge, or unblock the catalog.

---

## 4. Relationship to leakage / placebo / coverage runtimes

Uncertainty-candidate review must consume upstream diagnostic runtime outputs:

| Upstream runtime | Contract dependency |
|------------------|---------------------|
| KFold leakage diagnostic | `kfold_leakage_diagnostic_report` required; blocking leakage statuses block candidate review |
| Placebo calibration diagnostic | `placebo_calibration_diagnostic_report` required; blocking placebo statuses block candidate review |
| KFold coverage validation | `coverage_validation_report` required; blocking coverage statuses block candidate review |

Clean or restricted upstream diagnostics may permit **diagnostic review-readiness summary only** — not uncertainty authorization, CI claims, or production surfaces.

---

## 5. Relationship to sophisticated-method evidence ladder

Per `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001`, TBRRidge KFold remains at **STAGE_2_DIAGNOSTIC_ONLY** with candidate review target **STAGE_4_UNCERTAINTY_CANDIDATE**. This contract defines the governed gate between diagnostic evidence accumulation and any future uncertainty-candidate review runtime. It does not advance the ladder stage or grant STAGE_5+ authorization.

---

## 6. Relationship to method promotion and production compatibility boundaries

Per `METHOD_PROMOTION_REVIEW_CONTRACT_001` and `METHOD_PROMOTION_CANDIDATE_AUDIT_001`, TBRRidge has no RANK_4 promotion path. `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001` remains **deferred**.

This contract requires `method_promotion_boundary_report` and `production_catalog_status_report` in the evidence chain but **never** authorizes method promotion, production compatibility, or catalog unblock. Prohibited surfaces include `METHOD_PROMOTION_NOTICE`, `PRODUCTION_COMPATIBILITY_NOTICE`, and `CATALOG_UNBLOCK_NOTICE`.

---

## 7. Review statuses

| Status | Meaning |
|--------|---------|
| `UNCERTAINTY_CANDIDATE_REVIEW_NOT_EVALUATED` | No candidate-review evidence submitted |
| `UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW` | Evidence chain present and non-blocking for restricted summary |
| `UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS` | Restricted summary allowed with flagged risks |
| `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN` | Core or required evidence missing |
| `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC` | Leakage diagnostic blocking |
| `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PLACEBO_CALIBRATION` | Placebo calibration blocking |
| `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_COVERAGE_VALIDATION` | Coverage validation blocking |
| `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS` | Interval semantics incomplete |
| `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH` | Metric/estimand mismatch |
| `UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG_STATUS` | Production catalog blocked for production surfaces |
| `UNCERTAINTY_CANDIDATE_REVIEW_REQUIRES_METHOD_REVIEW` | Prohibited surface requested |
| `UNCERTAINTY_CANDIDATE_REVIEW_DEFERRED` | Candidate review explicitly deferred |

**No status grants uncertainty approval, method promotion, production approval, catalog unblock, CI authorization, or p-value/significance authorization.**

---

## 8. Review risk taxonomy

`MISSING_EVIDENCE_CHAIN` · `LEAKAGE_DIAGNOSTIC_BLOCKING` · `PLACEBO_CALIBRATION_BLOCKING` · `COVERAGE_VALIDATION_BLOCKING` · `INTERVAL_SEMANTICS_INCOMPLETE` · `NULL_CONTROL_EVIDENCE_INCOMPLETE` · `POSITIVE_CONTROL_EVIDENCE_INCOMPLETE` · `REGIME_SENSITIVITY_INCOMPLETE` · `REGULARIZATION_SENSITIVITY_INCOMPLETE` · `DONOR_POOL_SENSITIVITY_INCOMPLETE` · `OUTLIER_SENSITIVITY_INCOMPLETE` · `METRIC_ESTIMAND_MISMATCH` · `AGGREGATE_POOLED_SURFACE_UNSUPPORTED` · `CLAIM_AUTHORIZATION_BOUNDARY_MISSING` · `STATISTICAL_PROMOTION_EVIDENCE_INCOMPLETE` · `PRODUCTION_CATALOG_BLOCKED` · `METHOD_PROMOTION_BOUNDARY_MISSING`

---

## 9. Required evidence

`false_confidence_audit_report` · `kfold_leakage_diagnostic_report` · `placebo_calibration_diagnostic_report` · `coverage_validation_report` · `interval_semantics_report` · `null_control_evidence_report` · `positive_control_evidence_report` · `regime_sensitivity_report` · `regularization_sensitivity_report` · `donor_pool_sensitivity_report` · `outlier_sensitivity_report` · `metric_estimand_alignment_report` · `aggregate_pooled_surface_blocker_report` · `statistical_promotion_threshold_report` · `production_catalog_status_report` · `claim_authorization_boundary_report` · `method_promotion_boundary_report` · `lineage_provenance_manifest`

---

## 10. Future runtime packet fields

`review_id` · `review_status` · `method_id` · `instrument_id` · `estimator_family` · `inference_family` · `current_readiness_stage` · `candidate_review_target_stage` · `evidence_chain_summary` · `evidence_components_reviewed` · `required_evidence` · `missing_evidence` · `detected_review_risks` · `blockers` · `restrictions` · `allowed_surfaces` · `prohibited_surfaces` · `failure_packet` · `recommended_next_action` · `lineage_manifest` · `provenance_hash` · `policy_version`

---

## 11. Allowed / prohibited surfaces

**Allowed:** `DIAGNOSTIC_ONLY` · `RESEARCH_OR_REVIEW_ONLY` · `UNCERTAINTY_CANDIDATE_REVIEW_READINESS_SUMMARY` · `EVIDENCE_SUFFICIENCY_SUMMARY` · `REMAINING_BLOCKERS_SUMMARY` · `METHOD_REVIEW_INPUT_PACKET_DESCRIPTION`

**Prohibited:** `UNCERTAINTY_APPROVAL_NOTICE` · `CONFIDENCE_INTERVAL_CLAIM` · `P_VALUE_CLAIM` · `STATISTICAL_SIGNIFICANCE_CLAIM` · `COVERAGE_APPROVAL_CLAIM` · `CAUSAL_LIFT_CLAIM` · `ROI_CLAIM` · `PRODUCTION_READOUT` · `METHOD_PROMOTION_NOTICE` · `PRODUCTION_COMPATIBILITY_NOTICE` · `CATALOG_UNBLOCK_NOTICE`

---

## 12. Failure packet semantics

| Field | Purpose |
|-------|---------|
| `failure_code` | Standardized blocker |
| `failure_reason` | Human-readable summary |
| `detected_review_risks` | Failed risk taxonomy items |
| `missing_evidence` | Required reports not present |
| `required_remediation` | Retry category |
| `retry_category` | Governed remediation action |

**Failure codes:** `MISSING_FALSE_CONFIDENCE_AUDIT` · `MISSING_KFOLD_LEAKAGE_DIAGNOSTIC` · `MISSING_PLACEBO_CALIBRATION_DIAGNOSTIC` · `MISSING_COVERAGE_VALIDATION_REPORT` · `LEAKAGE_DIAGNOSTIC_BLOCKING` · `PLACEBO_CALIBRATION_BLOCKING` · `COVERAGE_VALIDATION_BLOCKING` · `INTERVAL_SEMANTICS_INCOMPLETE` · `NULL_CONTROL_EVIDENCE_INCOMPLETE` · `POSITIVE_CONTROL_EVIDENCE_INCOMPLETE` · `REGIME_SENSITIVITY_INCOMPLETE` · `METRIC_ESTIMAND_MISMATCH` · `PRODUCTION_CATALOG_BLOCKED` · `UNCERTAINTY_APPROVAL_SURFACE_BLOCKED`

**Retry categories:** `ADD_FALSE_CONFIDENCE_AUDIT` · `ADD_KFOLD_LEAKAGE_DIAGNOSTIC` · `ADD_PLACEBO_CALIBRATION_DIAGNOSTIC` · `ADD_COVERAGE_VALIDATION_REPORT` · `ADD_INTERVAL_SEMANTICS_REPORT` · `ADD_NULL_CONTROL_EVIDENCE` · `ADD_POSITIVE_CONTROL_EVIDENCE` · `ADD_REGIME_SENSITIVITY_EVIDENCE` · `ADD_METRIC_ESTIMAND_ALIGNMENT` · `RESTRICT_TO_DIAGNOSTIC_ONLY` · `BLOCK_UNCERTAINTY_APPROVAL_SURFACE` · `REQUIRE_METHOD_REVIEW` · `DEFER_CANDIDATE_REVIEW`

---

## 13. Future runtime acceptance criteria

- Blocks without false-confidence audit report
- Blocks without KFold leakage diagnostic report
- Blocks when KFold leakage diagnostic is blocking
- Blocks without placebo calibration diagnostic report
- Blocks when placebo calibration diagnostic is blocking
- Blocks without coverage validation report
- Blocks when coverage validation is blocking
- Blocks without interval semantics evidence
- Blocks without null-control evidence
- Blocks without positive-control evidence
- Blocks without regime sensitivity evidence
- Blocks on metric/estimand mismatch
- Blocks when production catalog remains blocked for production surfaces
- Permits restricted review-readiness summary only when evidence chain is present and non-blocking
- Always blocks uncertainty approval, CI, p-value, significance, causal lift, ROI, production, method promotion, production compatibility, and catalog-unblock surfaces
- Emits deterministic `review_id`/`provenance_hash`
- All forbidden computation/authorization flags false

---

## 14. Authorization boundary

| Flag | Value |
|------|-------|
| `uncertainty_candidate_review_contract_defined` | true |
| `review_statuses_defined` | true |
| `review_risk_taxonomy_defined` | true |
| `required_evidence_defined` | true |
| `evidence_chain_requirements_defined` | true |
| `failure_packet_semantics_defined` | true |
| `future_runtime_tests_documented` | true |
| `uncertainty_candidate_review_runtime_implemented` | false |
| `uncertainty_candidate_approved` | false |
| `uncertainty_authorized` | false |
| `confidence_interval_authorized` | false |
| `p_value_authorized` | false |
| `statistical_significance_authorized` | false |
| `coverage_approval_authorized` | false |
| `method_promotion_authorized` | false |
| `production_compatibility_authorized` | false |
| `catalog_unblock_authorized` | false |
| `coverage_computed` | false |
| `interval_computed` | false |
| `method_promoted` | false |
| `production_readout_authorized` | false |

---

## 15. Validation results

- Contract module validates all statuses, risks, evidence, surfaces, and flags
- Summary JSON valid
- Governance and validation tests pass
- Safety grep: no forbidden `true` computation/promotion/authorization flags

---

## 16. Known limitations

- Contract only; no uncertainty-candidate review runtime implementation
- Does not run or re-run D5-TRUST-TBRRIDGE-KFOLD-001 evidence batteries
- Does not prescribe numeric coverage tolerance bands — deferred to runtime after interval semantics closure
- Optional sensitivity/boundary reports may flag risks without blocking restricted summary
- BRB coverage path out of scope; KFold-specific

---

## 17. Recommended next artifact

**Primary:** `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001`

**Alternative:** `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`
