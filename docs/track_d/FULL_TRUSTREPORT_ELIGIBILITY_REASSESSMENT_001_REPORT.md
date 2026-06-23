# FULL-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 Report

## 1. Executive summary

This artifact performs a matrix-level TrustReport eligibility reassessment.
It does not introduce new estimator, inference, or design algorithms.
It does not remediate deferred statistical defects.
It does not authorize TrustReport unless every required row-level and downstream gate passes.
Deferred remediation lanes remain blocked until their target artifacts complete.

**Governance verdict:** `full_trustreport_reassessment_restricted_candidates_only`
**Global TrustReport authorized:** `False`

## 2. Scope

All governed DCM rows and disposition paths after DCM-001/004/005/006/008 trust lanes.

## 3. Non-goals

No new simulations; no production algorithm changes; no silent promotion.

## 4. Input artifacts

{
  "prior_validation": "docs/track_d/archives/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json",
  "dcm001_reassessment": "docs/track_d/archives/TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
  "dcm004_reassessment": "docs/track_d/archives/DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
  "dcm005_reassessment": "docs/track_d/archives/DCM005_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
  "dcm006_trust": "docs/track_d/archives/D5_TRUST_MULTICELL_PERCELL_INFERENCE_001_summary.json",
  "dcm008_trust": "docs/track_d/archives/D5_TRUST_STRATIFIED_SCM_JK_001_summary.json",
  "dcm005_brb_trust": "docs/track_d/archives/D5_TRUST_TBRRIDGE_BRB_001_summary.json",
  "dcm005_kfold_trust": "docs/track_d/archives/D5_TRUST_TBRRIDGE_KFOLD_001_summary.json",
  "dcm005_placebo_trust": "docs/track_d/archives/D5_TRUST_TBRRIDGE_PLACEBO_001_summary.json",
  "brb_correction": "docs/track_d/archives/TBRRIDGE_BRB_INTERVAL_CORRECTION_001_summary.json"
}

## 5. Decision rules

TrustReport requires statistical calibration, estimand alignment, valid interval semantics, geometry support, governed readout scope, no blocking investigations, and downstream authorization.

## 6. DCM matrix overview

{
  "DCM-001": {
    "trustreport_eligibility": "ELIGIBLE_WITH_RESTRICTIONS",
    "production_role": "restricted_research",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-002": {
    "trustreport_eligibility": "DIAGNOSTIC_ONLY",
    "production_role": "diagnostic_only",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-003": {
    "trustreport_eligibility": "INELIGIBLE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-004": {
    "trustreport_eligibility": "ELIGIBLE_WITH_RESTRICTIONS",
    "production_role": "restricted_research",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-006": {
    "trustreport_eligibility": "ELIGIBLE_WITH_RESTRICTIONS",
    "production_role": "per_cell_diagnostic_restricted",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-007": {
    "trustreport_eligibility": "INELIGIBLE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-008": {
    "trustreport_eligibility": "DIAGNOSTIC_ONLY",
    "production_role": "diagnostic_only",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "SCM-PLACEBO": {
    "trustreport_eligibility": "NULL_MONITOR_ONLY",
    "production_role": "null_monitor",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-005-BRB": {
    "trustreport_eligibility": "DEFERRED_REMEDIATION",
    "production_role": "blocked_pending_remediation",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-005-KFOLD": {
    "trustreport_eligibility": "DIAGNOSTIC_ONLY",
    "production_role": "diagnostic_only",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-005-PLACEBO": {
    "trustreport_eligibility": "NULL_MONITOR_ONLY",
    "production_role": "null_monitor_restricted",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-009": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-010": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-011": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-012": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-013": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-014": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-015": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-016": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-017": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-018": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "production_role": "blocked",
    "downstream_authorization": false,
    "promotion_candidate": false
  },
  "DCM-019": {
    "trustreport_eligibility": "INSUFFICIENT_EVIDENCE",
    "

## 7. Row-by-row decisions

22 rows characterized.

## 8. DCM-001 decision

ELIGIBLE_WITH_RESTRICTIONS; no TrustReport authorization.

## 9. DCM-004 decision

ELIGIBLE_WITH_RESTRICTIONS under supported parallel-timing contract; no TrustReport authorization.

## 10. DCM-005 decisions

BRB: DEFERRED_REMEDIATION; KFold: DIAGNOSTIC_ONLY; Placebo: NULL_MONITOR_ONLY.

## 11. DCM-006 decision

ELIGIBLE_WITH_RESTRICTIONS for parallel marginal per-cell readouts only; familywise/winner/pooled/global blocked; deferred shared-control and multiplicity lanes.

## 12. DCM-008 decision

DIAGNOSTIC_ONLY. Aggregate stratified readout is characterization only, not a governed pooled causal estimand.

## 13. SCM Placebo disposition

NULL_MONITOR_ONLY; investigation resolved at full reassessment.

## 14. AugSynth JK disposition

DIAGNOSTIC_ONLY / descriptive point; investigation resolved at full reassessment.

## 15. Deferred remediation lanes

INV-MULTICELL-MULTIPLICITY-CALIBRATION-001, INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001, INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001

## 16. Diagnostic-only lanes

DCM-002, DCM-008, DCM-005-KFOLD

## 17. Null-monitor-only lanes

SCM-PLACEBO, DCM-005-PLACEBO

## 18. Ineligible lanes

DCM-003, DCM-007

## 19. Insufficient-evidence lanes

DCM-009, DCM-010, DCM-011, DCM-012, DCM-013, DCM-014, DCM-015, DCM-016, DCM-017, DCM-018, DCM-019

## 20. CalibrationSignal implications

CalibrationSignal remains blocked for all rows in current matrix.

## 21. TrustReport implications

{
  "trust_report_authorized": false,
  "trust_report_ready": false,
  "trust_report_authorized_count": 0,
  "blocking_investigation_count": 3,
  "rationale": "No row passes all TrustReport gates; deferred remediation and diagnostic/null-monitor semantics block global authorization"
}

## 22. Downstream authorization implications

{
  "any_downstream_authorized": false,
  "research_restricted_rows": [
    "DCM-001",
    "DCM-004",
    "DCM-006"
  ]
}

## 23. Open investigation consumption

{
  "INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001": {
    "status": "RESOLVED",
    "classification": "resolved_by_prior_artifacts",
    "affected_combination": "DCM-005-BRB",
    "blocking_for_trustreport": false,
    "current_decision": "RESOLVED_BY_PRODUCTION_CORRECTION"
  },
  "INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001": {
    "status": "DEFERRED_WITH_TRIGGER",
    "classification": "deferred_with_trigger",
    "affected_combination": "DCM-005-BRB",
    "blocking_for_trustreport": true,
    "current_decision": "REMEDIATE_PENDING_VARIANCE_CALIBRATION"
  },
  "INV-TBRRIDGE-KFOLD-NULL-FPR-001": {
    "status": "RESOLVED",
    "classification": "resolved_by_prior_artifacts",
    "affected_combination": "DCM-005-KFOLD",
    "blocking_for_trustreport": false,
    "current_decision": "DIAGNOSTIC_ONLY"
  },
  "INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001": {
    "status": "RESOLVED",
    "classification": "resolved_by_prior_artifacts",
    "affected_combination": "DCM-005-PLACEBO",
    "blocking_for_trustreport": false,
    "current_decision": "NULL_MONITOR_ONLY"
  },
  "INV-AUGSYNTH-JK-TRUSTREPORT-DISPOSITION-001": {
    "status": "RESOLVED",
    "classification": "resolved_by_this_artifact",
    "affected_combination": "DCM-002",
    "blocking_for_trustreport": false,
    "current_decision": "DIAGNOSTIC_ONLY"
  },
  "INV-SCM-PLACEBO-GOVERNED-SEMANTICS-001": {
    "status": "RESOLVED",
    "classification": "resolved_by_this_artifact",
    "affected_combination": "DCM-001-PLACEBO",
    "blocking_for_trustreport": false,
    "current_decision": "NULL_MONITOR_ONLY"
  },
  "INV-MULTICELL-PERCELL-INFERENCE-001": {
    "status": "RESOLVED",
    "classification": "resolved_by_prior_artifacts",
    "affected_combination": "DCM-006",
    "blocking_for_trustreport": false,
    "current_decision": "PER_CELL_RESTRICTED"
  },
  "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001": {
    "status": "DEFERRED_WITH_TRIGGER",
    "classification": "deferred_with_trigger",
    "affected_combination": "DCM-006",
    "blocking_for_trustreport": true,
    "current_decision": "REMEDIATE_PENDING_SHARED_CONTROL_FRAMEWORK"
  },
  "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001": {
    "status": "DEFERRED_WITH_TRIGGER",
    "classification": "deferred_with_trigger",
    "affected_combination": "DCM-006",
    "blocking_for_trustreport": true,
    "current_decision": "REMEDIATE_PENDING_SIMULTANEOUS_INFERENCE"
  },
  "INV-MULTICELL-CELL-RELATIONSHIP-DECISION-POLICY-001": {
    "status": "RESOLVED",
    "classification": "resolved_by_prior_artifacts",
    "affected_combination": "DCM-006",
    "blocking_for_trustreport": false,
    "current_decision": "SEMANTIC_GUARDRAIL_ADDED"
  },
  "INV-STRATIFIED-SCM-JK-TRUSTREPORT-DISPOSITION-001": {
    "status": "RESOLVED",
    "classification": "resolved_by_prior_artifacts",
    "affected_combination": "DCM-008",
    "blocking_for_trustreport": false,
    "current_decision": "DIAGNOSTIC_ONLY"
  }
}

## 24. Promotion candidates

[]

## 25. Blocked candidates

22 rows blocked from TrustReport promotion.

## 26. Governance verdict

**`full_trustreport_reassessment_restricted_candidates_only`**

## Residual Issues and Handoff

**Resolved in this artifact:**
- INV-AUGSYNTH-JK-TRUSTREPORT-DISPOSITION-001
- INV-SCM-PLACEBO-GOVERNED-SEMANTICS-001

**New investigations opened:** none

**Existing investigations updated:**
- INV-AUGSYNTH-JK-TRUSTREPORT-DISPOSITION-001 → RESOLVED at full reassessment
- INV-SCM-PLACEBO-GOVERNED-SEMANTICS-001 → RESOLVED at full reassessment

**Deferred issues:**
- INV-MULTICELL-MULTIPLICITY-CALIBRATION-001
- INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001
- INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001

**Explicit exclusions:**
- No new statistical simulations in this artifact

**Revisit trigger:** After deferred remediation lanes or promotion gate review

**Required decision checkpoint:** TRUSTREPORT_DOWNSTREAM_PROMOTION_001

**Next artifact:** TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001

---

## Post-remediation BRB update (2026-06-03)

**Follow-on:** [`DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001_REPORT.md`](DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001_REPORT.md)

**DCM-005-BRB final disposition:** `BRB_DIAGNOSTIC_ONLY` (was `DEFERRED_REMEDIATION`). Null gates remain failed. **`INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001`** no longer deferred — terminally RESOLVED. Global TrustReport authorization unchanged (false).

---

## Downstream promotion update (2026-06-03)

**Follow-on:** [`TRUSTREPORT_DOWNSTREAM_PROMOTION_001_REPORT.md`](TRUSTREPORT_DOWNSTREAM_PROMOTION_001_REPORT.md)

Row-level restricted promotion approved for DCM-001 and DCM-004 only. Global platform, live API, and scheduler authorization remain false.
