# TRUSTREPORT-RESEARCH-MODE-REVIEW-WORKFLOW-001 Report

## 1. Executive summary

This artifact defines the research-mode human-review workflow for exported TrustReport artifacts.
It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.
Review approval is research-mode review approval only.
Only DCM-001 and DCM-004 are accepted for research-mode review.
All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.

**Governance verdict:** `trustreport_research_mode_review_workflow_passed`
**Accepted rows:** ['DCM-001', 'DCM-004']

## 2. Scope

Human-review workflow for DCM-001 (SCM+JK) and DCM-004 (DID+bootstrap) exported artifacts.

## 3. Non-goals

- No live API, scheduler, production automation
- No CalibrationSignal, budget optimization, stakeholder production approval
- No new statistical simulations or algorithm changes

## 4. Input artifacts

{
  "artifact_export": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_summary.json",
  "renderer_summary": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_RESEARCH_MODE_RENDERER_001_summary.json",
  "integration_dry_run": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_INTEGRATION_DRY_RUN_001_summary.json",
  "downstream_promotion": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json",
  "export_manifest": "/workspace/panel_exp/docs/track_d/examples/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_manifest.json"
}

## 5. Research-mode review workflow contract

[
  "decision_record",
  "artifact_id",
  "review_id",
  "row_id",
  "blocked_uses_present",
  "created_at",
  "restrictions_present",
  "open_investigation_check",
  "review_status",
  "review_mode",
  "warnings_present",
  "manifest_verified",
  "content_hash_verified",
  "required_banners_present",
  "review_checklist",
  "audit_trail_present",
  "reviewer_role",
  "sanitization_verified",
  "export_id",
  "authorization_boundaries_verified"
]

## 6. Reviewer role model

{
  "valid_roles": [
    "causal_methods_reviewer",
    "governance_reviewer",
    "research_reviewer"
  ],
  "invalid_roles": [
    "api_operator",
    "budget_optimizer",
    "production_approver",
    "scheduler_operator",
    "unknown"
  ],
  "workflow_action_allowed": "RESEARCH_MODE_REVIEW_APPROVAL",
  "workflow_actions_blocked": [
    "PRODUCTION_APPROVAL",
    "LIVE_API_APPROVAL",
    "SCHEDULER_APPROVAL",
    "CALIBRATION_SIGNAL_APPROVAL",
    "BUDGET_OPTIMIZATION_APPROVAL",
    "AUTO_RECOMMENDATION_APPROVAL",
    "GLOBAL_PLATFORM_APPROVAL"
  ]
}

## 7. Review checklist

[
  "research_mode_banner_present",
  "not_for_production_banner_present",
  "not_for_budget_optimization_banner_present",
  "no_calibration_signal_banner_present",
  "no_live_api_banner_present",
  "no_scheduler_banner_present",
  "sanitized_artifact_export_banner_present",
  "row_identity_preserved",
  "method_identity_preserved",
  "warnings_present",
  "restrictions_present",
  "blocked_uses_present",
  "audit_trail_present",
  "manifest_present",
  "content_hash_matches",
  "payload_placeholder_or_synthetic_only",
  "no_raw_live_measurement_payload",
  "no_production_recommendation",
  "no_budget_allocation_recommendation"
]

## 8. Review decision classes

Accepted: `REVIEW_ACCEPTED_RESEARCH_MODE`, `REVIEW_ACCEPTED_MANIFEST_ONLY`. All other decisions block or reject.

## 9. DCM-001 review result

{
  "request_id": "pos-dcm001-placeholder",
  "row_id": "DCM-001",
  "export_id": "export-pos-dcm001-placeholder",
  "request_type": "research_review",
  "decision": "REVIEW_ACCEPTED_RESEARCH_MODE",
  "accepted": true,
  "review_status": "RESEARCH_REVIEW_APPROVED",
  "audit_record_id": "review-audit-pos-dcm001-placeholder",
  "gate_results": {
    "row_promoted": true,
    "checklist_complete": true,
    "research_mode_review_only": true,
    "production_approval": false
  },
  "reason": "Research-mode review approved (not production authorization)"
}

## 10. DCM-004 review result

{
  "request_id": "pos-dcm004-placeholder",
  "row_id": "DCM-004",
  "export_id": "export-pos-dcm004-placeholder",
  "request_type": "research_review",
  "decision": "REVIEW_ACCEPTED_RESEARCH_MODE",
  "accepted": true,
  "review_status": "RESEARCH_REVIEW_APPROVED",
  "audit_record_id": "review-audit-pos-dcm004-placeholder",
  "gate_results": {
    "row_promoted": true,
    "checklist_complete": true,
    "research_mode_review_only": true,
    "production_approval": false
  },
  "reason": "Research-mode review approved (not production authorization)"
}

## 11. Manifest-only review behavior

Manifest-only exports receive `REVIEW_ACCEPTED_MANIFEST_ONLY` when checklist passes.

## 12. Hash verification behavior

[
  {
    "request_id": "pos-dcm001-placeholder",
    "export_id": "export-pos-dcm001-placeholder",
    "verified": true,
    "content_hash": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e"
  },
  {
    "request_id": "pos-dcm001-synthetic",
    "export_id": "export-pos-dcm001-synthetic",
    "verified": true,
    "content_hash": "f9a0960bbb06cca2d2373a6918a03c0fe2cc5939700f101c593a95f6f3b8c495"
  },
  {
    "request_id": "pos-dcm001-manifest",
    "export_id": "export-pos-dcm001-manifest",
    "verified": true,
    "content_hash": "f8372f936de17b4ad8a53c8507f189c5a607fa46b8ae39910e33ec7797cd8754"
  },
  {
    "request_id": "pos-dcm004-placeholder",
    "export_id": "export-pos-dcm004-placeholder",
    "verified": true,
    "content_hash": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516"
  },
  {
    "request_id": "pos-dcm004-synthetic",
    "export_id": "export-pos-dcm004-synthetic",
    "verified": true,
    "content_hash": "c54cb2b171ee51efe79bb901a8839dcb09a74249e57d5cf14d99929239c7662c"
  },
  {
    "request_id": "pos-dcm004-manifest",
    "export_id": "export-pos-dcm004-manifest",
    "verified": true,
    "content_hash": "e51becb6cf3628ba9b0cbe7d21ac356499f01d35f5f022a74cb451340962326b"
  }
]

## 13. Sanitization verification behavior

[
  {
    "request_id": "pos-dcm001-placeholder",
    "sanitized": true,
    "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
  },
  {
    "request_id": "pos-dcm001-synthetic",
    "sanitized": true,
    "measurement_label": "SYNTHETIC_DRY_RUN_PAYLOAD"
  },
  {
    "request_id": "pos-dcm001-manifest",
    "sanitized": true,
    "measurement_label": "MANIFEST_ONLY_EXPORT"
  },
  {
    "request_id": "pos-dcm004-placeholder",
    "sanitized": true,
    "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
  },
  {
    "request_id": "pos-dcm004-synthetic",
    "sanitized": true,
    "measurement_label": "SYNTHETIC_DRY_RUN_PAYLOAD"
  },
  {
    "request_id": "pos-dcm004-manifest",
    "sanitized": true,
    "measurement_label": "MANIFEST_ONLY_EXPORT"
  }
]

## 14. Negative-control review requests

[
  {
    "request_id": "neg-missing-banner",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-placeholder",
    "request_type": "missing_banner",
    "decision": "REVIEW_BLOCKED_MISSING_BANNER",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-missing-banner",
    "gate_results": {
      "missing_banner": true
    },
    "reason": "Required banners missing"
  },
  {
    "request_id": "neg-missing-warnings",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-placeholder",
    "request_type": "missing_warnings",
    "decision": "REVIEW_BLOCKED_MISSING_WARNING",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_REJECTED",
    "audit_record_id": "review-audit-neg-missing-warnings",
    "gate_results": {
      "missing_warnings": true
    },
    "reason": "Required warnings missing"
  },
  {
    "request_id": "neg-missing-restrictions",
    "row_id": "DCM-004",
    "export_id": "export-pos-dcm004-placeholder",
    "request_type": "missing_restrictions",
    "decision": "REVIEW_BLOCKED_MISSING_RESTRICTION",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_REJECTED",
    "audit_record_id": "review-audit-neg-missing-restrictions",
    "gate_results": {
      "missing_restrictions": true
    },
    "reason": "Required restrictions missing"
  },
  {
    "request_id": "neg-missing-audit",
    "row_id": "DCM-004",
    "export_id": "export-pos-dcm004-placeholder",
    "request_type": "missing_audit_trail",
    "decision": "REVIEW_BLOCKED_MISSING_AUDIT_TRAIL",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-missing-audit",
    "gate_results": {
      "missing_audit_trail": true
    },
    "reason": "Audit trail missing"
  },
  {
    "request_id": "neg-hash-mismatch",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-synthetic",
    "request_type": "hash_mismatch",
    "decision": "REVIEW_BLOCKED_HASH_MISMATCH",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-hash-mismatch",
    "gate_results": {
      "hash_mismatch": true
    },
    "reason": "Content hash mismatch"
  },
  {
    "request_id": "neg-manifest-mismatch",
    "row_id": "DCM-004",
    "export_id": "export-pos-dcm004-synthetic",
    "request_type": "manifest_mismatch",
    "decision": "REVIEW_BLOCKED_MANIFEST_MISMATCH",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-manifest-mismatch",
    "gate_results": {
      "manifest_mismatch": true
    },
    "reason": "Manifest mismatch"
  },
  {
    "request_id": "neg-unsanitized",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-placeholder",
    "request_type": "unsanitized_payload",
    "decision": "REVIEW_BLOCKED_UNSANITIZED_PAYLOAD",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-unsanitized",
    "gate_results": {
      "unsanitized_payload": true
    },
    "reason": "Unsanitized payload"
  },
  {
    "request_id": "neg-live-payload",
    "row_id": "DCM-004",
    "export_id": "export-pos-dcm004-placeholder",
    "request_type": "live_measurement_payload",
    "decision": "REVIEW_BLOCKED_LIVE_MEASUREMENT_PAYLOAD",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-live-payload",
    "gate_results": {
      "live_measurement_payload": true
    },
    "reason": "Raw/live measurement payload"
  },
  {
    "request_id": "neg-prod-rec",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-placeholder",
    "request_type": "production_recommendation",
    "decision": "REVIEW_BLOCKED_PRODUCTION_RECOMMENDATION",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-prod-rec",
    "gate_results": {
      "production_recommendation": true
    },
    "reason": "Production recommendation present"
  },
  {
    "request_id": "neg-budget-rec",
    "row_id": "DCM-004",
    "export_id": "export-pos-dcm004-placeholder",
    "request_type": "budget_recommendation",
    "decision": "REVIEW_BLOCKED_BUDGET_RECOMMENDATION",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-budget-rec",
    "gate_results": {
      "budget_recommendation": true
    },
    "reason": "Budget allocation recommendation present"
  },
  {
    "request_id": "neg-invalid-role",
    "row_id": "DCM-001",
    "export_id": "",
    "request_type": "invalid_reviewer_role",
    "decision": "REVIEW_BLOCKED_INVALID_REVIEWER_ROLE",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-invalid-role",
    "gate_results": {
      "invalid_reviewer_role": true
    },
    "reason": "Invalid reviewer role: production_approver"
  },
  {
    "request_id": "neg-brb",
    "row_id": "DCM-005-BRB",
    "export_id": "",
    "request_type": "causal_trustreport",
    "decision": "REVIEW_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-brb",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-005-BRB is diagnostic-only"
  },
  {
    "request_id": "neg-kfold",
    "row_id": "DCM-005-KFOLD",
    "export_id": "",
    "request_type": "causal_trustreport",
    "decision": "REVIEW_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-kfold",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-005-KFOLD is diagnostic-only"
  },
  {
    "request_id": "neg-placebo",
    "row_id": "DCM-005-PLACEBO",
    "export_id": "",
    "request_type": "causal_trustreport",
    "decision": "REVIEW_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-placebo",
    "gate_results": {
      "null_monitor_causal_reuse": true
    },
    "reason": "Null-monitor path cannot receive causal TrustReport review"
  },
  {
    "request_id": "neg-dcm006",
    "row_id": "DCM-006",
    "export_id": "",
    "request_type": "global_claim",
    "decision": "REVIEW_BLOCKED_NOT_PROMOTED",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-dcm006",
    "gate_results": {
      "multicell_global_blocked": true
    },
    "reason": "DCM-006 global/winner/pooled review blocked"
  },
  {
    "request_id": "neg-dcm008",
    "row_id": "DCM-008",
    "export_id": "",
    "request_type": "aggregate_stratified",
    "decision": "REVIEW_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-dcm008",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-008 is diagnostic-only"
  },
  {
    "request_id": "neg-cal",
    "row_id": "DCM-001",
    "export_id": "",
    "request_type": "calibration_approval",
    "decision": "REVIEW_BLOCKED_CALIBRATION_SIGNAL",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-cal",
    "gate_results": {
      "CALIBRATION_SIGNAL_APPROVAL_blocked": true
    },
    "reason": "Workflow action CALIBRATION_SIGNAL_APPROVAL forbidden"
  },
  {
    "request_id": "neg-live",
    "row_id": "DCM-004",
    "export_id": "",
    "request_type": "live_api_approval",
    "decision": "REVIEW_BLOCKED_LIVE_API",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-live",
    "gate_results": {
      "LIVE_API_APPROVAL_blocked": true
    },
    "reason": "Workflow action LIVE_API_APPROVAL forbidden"
  },
  {
    "request_id": "neg-scheduler",
    "row_id": "DCM-001",
    "export_id": "",
    "request_type": "scheduler_approval",
    "decision": "REVIEW_BLOCKED_SCHEDULER",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-scheduler",
    "gate_results": {
      "SCHEDULER_APPROVAL_blocked": true
    },
    "reason": "Workflow action SCHEDULER_APPROVAL forbidden"
  },
  {
    "request_id": "neg-prod",
    "row_id": "DCM-004",
    "export_id": "",
    "request_type": "production_approval",
    "decision": "REVIEW_BLOCKED_PRODUCTION_DECISIONING",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-prod",
    "gate_results": {
      "PRODUCTION_APPROVAL_blocked": true
    },
    "reason": "Workflow action PRODUCTION_APPROVAL forbidden"
  },
  {
    "request_id": "neg-budget",
    "row_id": "DCM-001",
    "export_id": "",
    "request_type": "budget_approval",
    "decision": "REVIEW_BLOCKED_BUDGET_OPTIMIZATION",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-budget",
    "gate_results": {
      "BUDGET_OPTIMIZATION_APPROVAL_blocked": true
    },
    "reason": "Workflow action BUDGET_OPTIMIZATION_APPROVAL forbidden"
  },
  {
    "request_id": "neg-unknown",
    "row_id": "DCM-999",
    "export_id": "",
    "request_type": "unknown_row",
    "decision": "REVIEW_BLOCKED_UNKNOWN_ROW",
    "accepted": false,
    "review_status": "RESEARCH_REVIEW_BLOCKED",
    "audit_record_id": "review-audit-neg-unknown",
    "gate_results": {
      "unknown_row": true
    },
    "reason": "Unknown row: DCM-999"
  }
]

## 15. Blocked diagnostic-only rows

DCM-002, DCM-005-BRB, DCM-005-KFOLD, DCM-008 — REVIEW_BLOCKED_DIAGNOSTIC_ONLY

## 16. Blocked null-monitor causal reuse

DCM-005-PLACEBO — REVIEW_BLOCKED_NULL_MONITOR_CAUSAL_REUSE

## 17. Blocked multi-cell/global claims

DCM-006 — REVIEW_BLOCKED_NOT_PROMOTED

## 18. Blocked stratified aggregate claims

DCM-008 — REVIEW_BLOCKED_DIAGNOSTIC_ONLY

## 19. CalibrationSignal boundary

{
  "any_calibration_signal_allowed": false
}

## 20. Live API boundary

{
  "live_api_authorized": false,
  "research_mode_review_only": true
}

## 21. Scheduler boundary

{
  "scheduler_authorized": false,
  "research_mode_review_only": true
}

## 22. Production decisioning boundary

{
  "any_production_decisioning_allowed": false
}

## 23. Budget optimization boundary

{
  "any_budget_optimization_allowed": false
}

## 24. Audit record verification

Audit records: 28

## 25. Open investigation check

{
  "deferred_investigations": [
    "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
    "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001"
  ],
  "blocking_for_review": []
}

## 26. Governance verdict

`trustreport_research_mode_review_workflow_passed`

## Residual Issues and Handoff

**Resolved in this artifact:** none

**New investigations opened:** none

**Existing investigations updated:** none

**Deferred issues:**
- INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001
- INV-MULTICELL-MULTIPLICITY-CALIBRATION-001

**Explicit exclusions:**
- DCM-005-BRB
- DCM-005-KFOLD
- DCM-005-PLACEBO
- DCM-006
- DCM-008
- DCM-999

**Revisit trigger:** After TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001

**Required decision checkpoint:** TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001

**Next artifact:** TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001


## Residual Issues and Handoff

Next artifact: `TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001`
