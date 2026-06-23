# TRUSTREPORT-RESEARCH-MODE-ACCESS-CONTROL-001 Report

## 1. Executive summary

This artifact defines research-mode access control for exported TrustReport artifacts.
It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.
Access approval is research-mode access approval only.
Only DCM-001 and DCM-004 are accepted for research-mode access.
All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.

**Governance verdict:** `trustreport_research_mode_access_control_passed`
**Accepted rows:** ['DCM-001', 'DCM-004']

## 2. Scope

Research-mode access control for DCM-001 (SCM+JK) and DCM-004 (DID+bootstrap).

## 3. Non-goals

- No live API, scheduler, production automation, deployment approval
- No CalibrationSignal, budget optimization, stakeholder production approval
- No new statistical simulations or algorithm changes

## 4. Input artifacts

{
  "review_workflow": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001_summary.json",
  "artifact_export": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_summary.json",
  "renderer_summary": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_RESEARCH_MODE_RENDERER_001_summary.json",
  "integration_dry_run": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_INTEGRATION_DRY_RUN_001_summary.json",
  "downstream_promotion": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json",
  "export_manifest": "/workspace/panel_exp/docs/track_d/examples/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_manifest.json"
}

## 5. Research-mode access-control contract

[
  "decision_reason",
  "review_status",
  "allowed_permissions",
  "access_request_id",
  "artifact_scope",
  "decision",
  "sanitization_verified",
  "audit_record",
  "created_at",
  "requested_access_mode",
  "requester_scope",
  "research_mode_only",
  "manifest_verified",
  "blocked_permissions",
  "content_hash_verified",
  "artifact_id",
  "requester_role",
  "row_id"
]

## 6. Role model

[
  "audit_viewer",
  "causal_methods_reviewer",
  "governance_reviewer",
  "research_exporter",
  "research_mode_admin",
  "research_reviewer",
  "research_viewer"
]

## 7. Role-permission matrix

{
  "research_viewer": [
    "MANIFEST_VIEW",
    "RESEARCH_VIEW"
  ],
  "research_exporter": [
    "MANIFEST_VIEW",
    "RESEARCH_EXPORT",
    "RESEARCH_VIEW"
  ],
  "research_reviewer": [
    "AUDIT_VIEW",
    "MANIFEST_VIEW",
    "RESEARCH_REVIEW",
    "RESEARCH_VIEW"
  ],
  "causal_methods_reviewer": [
    "AUDIT_VIEW",
    "MANIFEST_VIEW",
    "RESEARCH_REVIEW",
    "RESEARCH_REVIEW_APPROVE",
    "RESEARCH_VIEW"
  ],
  "governance_reviewer": [
    "AUDIT_VIEW",
    "MANIFEST_VIEW",
    "RESEARCH_REVIEW",
    "RESEARCH_REVIEW_APPROVE",
    "RESEARCH_VIEW"
  ],
  "audit_viewer": [
    "AUDIT_VIEW",
    "MANIFEST_VIEW"
  ],
  "research_mode_admin": [
    "AUDIT_VIEW",
    "MANIFEST_VIEW",
    "RESEARCH_EXPORT",
    "RESEARCH_REVIEW",
    "RESEARCH_REVIEW_APPROVE",
    "RESEARCH_VIEW"
  ]
}

## 8. Access decision classes

Granted: research view/export/review/approve, manifest view, audit view. All production modes blocked.

## 9. DCM-001 access result

{
  "request_id": "pos-view-dcm001",
  "row_id": "DCM-001",
  "export_id": "export-pos-dcm001-placeholder",
  "request_type": "research_view",
  "decision": "ACCESS_GRANTED_RESEARCH_VIEW",
  "granted": true,
  "audit_record_id": "access-audit-pos-view-dcm001",
  "gate_results": {
    "row_promoted": true,
    "role_permitted": true,
    "manifest_verified": true,
    "hash_verified": true,
    "sanitization_verified": true,
    "research_mode_only": true,
    "production_permissions_blocked": true
  },
  "reason": "Research-mode access granted"
}

## 10. DCM-004 access result

{
  "request_id": "pos-view-dcm004",
  "row_id": "DCM-004",
  "export_id": "export-pos-dcm004-placeholder",
  "request_type": "research_view",
  "decision": "ACCESS_GRANTED_RESEARCH_VIEW",
  "granted": true,
  "audit_record_id": "access-audit-pos-view-dcm004",
  "gate_results": {
    "row_promoted": true,
    "role_permitted": true,
    "manifest_verified": true,
    "hash_verified": true,
    "sanitization_verified": true,
    "research_mode_only": true,
    "production_permissions_blocked": true
  },
  "reason": "Research-mode access granted"
}

## 11. Manifest/hash/sanitization gates

{
  "manifest": [
    {
      "request_id": "pos-view-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-view-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-export-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-export-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-review-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-review-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-approve-causal-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-approve-causal-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-approve-gov-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-approve-gov-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-manifest-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-manifest-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-audit-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-audit-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-admin-view-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true
    },
    {
      "request_id": "pos-admin-export-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true
    }
  ],
  "hash": [
    {
      "request_id": "pos-view-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true,
      "content_hash": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e"
    },
    {
      "request_id": "pos-view-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true,
      "content_hash": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516"
    },
    {
      "request_id": "pos-export-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true,
      "content_hash": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e"
    },
    {
      "request_id": "pos-export-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true,
      "content_hash": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516"
    },
    {
      "request_id": "pos-review-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true,
      "content_hash": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e"
    },
    {
      "request_id": "pos-review-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true,
      "content_hash": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516"
    },
    {
      "request_id": "pos-approve-causal-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true,
      "content_hash": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e"
    },
    {
      "request_id": "pos-approve-causal-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true,
      "content_hash": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516"
    },
    {
      "request_id": "pos-approve-gov-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true,
      "content_hash": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e"
    },
    {
      "request_id": "pos-approve-gov-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true,
      "content_hash": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516"
    },
    {
      "request_id": "pos-manifest-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true,
      "content_hash": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e"
    },
    {
      "request_id": "pos-manifest-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true,
      "content_hash": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516"
    },
    {
      "request_id": "pos-audit-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true,
      "content_hash": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e"
    },
    {
      "request_id": "pos-audit-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true,
      "content_hash": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516"
    },
    {
      "request_id": "pos-admin-view-dcm001",
      "export_id": "export-pos-dcm001-placeholder",
      "verified": true,
      "content_hash": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e"
    },
    {
      "request_id": "pos-admin-export-dcm004",
      "export_id": "export-pos-dcm004-placeholder",
      "verified": true,
      "content_hash": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516"
    }
  ],
  "sanitization": [
    {
      "request_id": "pos-view-dcm001",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-view-dcm004",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-export-dcm001",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-export-dcm004",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-review-dcm001",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-review-dcm004",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-approve-causal-dcm001",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-approve-causal-dcm004",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-approve-gov-dcm001",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-approve-gov-dcm004",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-manifest-dcm001",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-manifest-dcm004",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-audit-dcm001",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-audit-dcm004",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-admin-view-dcm001",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    },
    {
      "request_id": "pos-admin-export-dcm004",
      "sanitized": true,
      "measurement_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED"
    }
  ]
}

## 12. Review-status gate

[
  {
    "request_id": "pos-view-dcm001",
    "export_request_id": "pos-dcm001-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-view-dcm004",
    "export_request_id": "pos-dcm004-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-export-dcm001",
    "export_request_id": "pos-dcm001-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-export-dcm004",
    "export_request_id": "pos-dcm004-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-review-dcm001",
    "export_request_id": "pos-dcm001-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-review-dcm004",
    "export_request_id": "pos-dcm004-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-approve-causal-dcm001",
    "export_request_id": "pos-dcm001-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-approve-causal-dcm004",
    "export_request_id": "pos-dcm004-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-approve-gov-dcm001",
    "export_request_id": "pos-dcm001-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-approve-gov-dcm004",
    "export_request_id": "pos-dcm004-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-manifest-dcm001",
    "export_request_id": "pos-dcm001-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-manifest-dcm004",
    "export_request_id": "pos-dcm004-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-audit-dcm001",
    "export_request_id": "pos-dcm001-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-audit-dcm004",
    "export_request_id": "pos-dcm004-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-admin-view-dcm001",
    "export_request_id": "pos-dcm001-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  },
  {
    "request_id": "pos-admin-export-dcm004",
    "export_request_id": "pos-dcm004-placeholder",
    "review_approved": true,
    "review_status": "RESEARCH_REVIEW_APPROVED"
  }
]

## 13. Negative-control access requests

[
  {
    "request_id": "neg-viewer-export",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-placeholder",
    "request_type": "viewer_export",
    "decision": "ACCESS_BLOCKED_ROLE_NOT_PERMITTED",
    "granted": false,
    "audit_record_id": "access-audit-neg-viewer-export",
    "gate_results": {
      "role_not_permitted": true
    },
    "reason": "Role research_viewer cannot RESEARCH_EXPORT"
  },
  {
    "request_id": "neg-exporter-approve",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-placeholder",
    "request_type": "exporter_approve",
    "decision": "ACCESS_BLOCKED_ROLE_NOT_PERMITTED",
    "granted": false,
    "audit_record_id": "access-audit-neg-exporter-approve",
    "gate_results": {
      "role_not_permitted": true
    },
    "reason": "Role research_exporter cannot RESEARCH_REVIEW_APPROVE"
  },
  {
    "request_id": "neg-reviewer-approve",
    "row_id": "DCM-004",
    "export_id": "export-pos-dcm004-placeholder",
    "request_type": "reviewer_approve",
    "decision": "ACCESS_BLOCKED_ROLE_NOT_PERMITTED",
    "granted": false,
    "audit_record_id": "access-audit-neg-reviewer-approve",
    "gate_results": {
      "role_not_permitted": true
    },
    "reason": "Role research_reviewer cannot RESEARCH_REVIEW_APPROVE"
  },
  {
    "request_id": "neg-audit-export",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-placeholder",
    "request_type": "audit_export",
    "decision": "ACCESS_BLOCKED_ROLE_NOT_PERMITTED",
    "granted": false,
    "audit_record_id": "access-audit-neg-audit-export",
    "gate_results": {
      "role_not_permitted": true
    },
    "reason": "Role audit_viewer cannot RESEARCH_EXPORT"
  },
  {
    "request_id": "neg-invalid-role",
    "row_id": "DCM-001",
    "export_id": "",
    "request_type": "invalid_role",
    "decision": "ACCESS_BLOCKED_INVALID_ROLE",
    "granted": false,
    "audit_record_id": "access-audit-neg-invalid-role",
    "gate_results": {
      "invalid_role": true
    },
    "reason": "Invalid role: production_approver"
  },
  {
    "request_id": "neg-unknown",
    "row_id": "DCM-999",
    "export_id": "",
    "request_type": "unknown_row",
    "decision": "ACCESS_BLOCKED_UNKNOWN_ROW",
    "granted": false,
    "audit_record_id": "access-audit-neg-unknown",
    "gate_results": {
      "unknown_row": true
    },
    "reason": "Unknown row: DCM-999"
  },
  {
    "request_id": "neg-brb",
    "row_id": "DCM-005-BRB",
    "export_id": "",
    "request_type": "causal_trustreport",
    "decision": "ACCESS_BLOCKED_DIAGNOSTIC_ONLY",
    "granted": false,
    "audit_record_id": "access-audit-neg-brb",
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
    "decision": "ACCESS_BLOCKED_DIAGNOSTIC_ONLY",
    "granted": false,
    "audit_record_id": "access-audit-neg-kfold",
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
    "decision": "ACCESS_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
    "granted": false,
    "audit_record_id": "access-audit-neg-placebo",
    "gate_results": {
      "null_monitor_causal_reuse": true
    },
    "reason": "Null-monitor causal TrustReport access blocked"
  },
  {
    "request_id": "neg-dcm006",
    "row_id": "DCM-006",
    "export_id": "",
    "request_type": "global_claim",
    "decision": "ACCESS_BLOCKED_NOT_PROMOTED",
    "granted": false,
    "audit_record_id": "access-audit-neg-dcm006",
    "gate_results": {
      "multicell_global_blocked": true
    },
    "reason": "DCM-006 global/winner/pooled access blocked"
  },
  {
    "request_id": "neg-dcm008",
    "row_id": "DCM-008",
    "export_id": "",
    "request_type": "aggregate_stratified",
    "decision": "ACCESS_BLOCKED_DIAGNOSTIC_ONLY",
    "granted": false,
    "audit_record_id": "access-audit-neg-dcm008",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-008 is diagnostic-only"
  },
  {
    "request_id": "neg-cal",
    "row_id": "DCM-001",
    "export_id": "",
    "request_type": "calibration_write",
    "decision": "ACCESS_BLOCKED_CALIBRATION_SIGNAL",
    "granted": false,
    "audit_record_id": "access-audit-neg-cal",
    "gate_results": {
      "CALIBRATION_SIGNAL_WRITE_blocked": true
    },
    "reason": "Blocked access mode: CALIBRATION_SIGNAL_WRITE"
  },
  {
    "request_id": "neg-live-api",
    "row_id": "DCM-004",
    "export_id": "",
    "request_type": "live_api",
    "decision": "ACCESS_BLOCKED_LIVE_API",
    "granted": false,
    "audit_record_id": "access-audit-neg-live-api",
    "gate_results": {
      "LIVE_API_EXECUTE_blocked": true
    },
    "reason": "Blocked access mode: LIVE_API_EXECUTE"
  },
  {
    "request_id": "neg-scheduler",
    "row_id": "DCM-001",
    "export_id": "",
    "request_type": "scheduler",
    "decision": "ACCESS_BLOCKED_SCHEDULER",
    "granted": false,
    "audit_record_id": "access-audit-neg-scheduler",
    "gate_results": {
      "SCHEDULER_EXECUTE_blocked": true
    },
    "reason": "Blocked access mode: SCHEDULER_EXECUTE"
  },
  {
    "request_id": "neg-prod",
    "row_id": "DCM-004",
    "export_id": "",
    "request_type": "production_approve",
    "decision": "ACCESS_BLOCKED_PRODUCTION_DECISIONING",
    "granted": false,
    "audit_record_id": "access-audit-neg-prod",
    "gate_results": {
      "PRODUCTION_DECISION_APPROVE_blocked": true
    },
    "reason": "Blocked access mode: PRODUCTION_DECISION_APPROVE"
  },
  {
    "request_id": "neg-budget",
    "row_id": "DCM-001",
    "export_id": "",
    "request_type": "budget",
    "decision": "ACCESS_BLOCKED_BUDGET_OPTIMIZATION",
    "granted": false,
    "audit_record_id": "access-audit-neg-budget",
    "gate_results": {
      "BUDGET_OPTIMIZATION_EXECUTE_blocked": true
    },
    "reason": "Blocked access mode: BUDGET_OPTIMIZATION_EXECUTE"
  },
  {
    "request_id": "neg-global-admin",
    "row_id": "DCM-001",
    "export_id": "",
    "request_type": "global_admin",
    "decision": "ACCESS_BLOCKED_GLOBAL_PLATFORM",
    "granted": false,
    "audit_record_id": "access-audit-neg-global-admin",
    "gate_results": {
      "GLOBAL_PLATFORM_ADMIN_blocked": true
    },
    "reason": "Blocked access mode: GLOBAL_PLATFORM_ADMIN"
  },
  {
    "request_id": "neg-unsanitized",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-placeholder",
    "request_type": "unsanitized",
    "decision": "ACCESS_BLOCKED_UNSANITIZED_ARTIFACT",
    "granted": false,
    "audit_record_id": "access-audit-neg-unsanitized",
    "gate_results": {
      "unsanitized_artifact": true
    },
    "reason": "Unsanitized artifact access blocked"
  },
  {
    "request_id": "neg-hash",
    "row_id": "DCM-004",
    "export_id": "export-pos-dcm004-placeholder",
    "request_type": "hash_mismatch",
    "decision": "ACCESS_BLOCKED_HASH_MISMATCH",
    "granted": false,
    "audit_record_id": "access-audit-neg-hash",
    "gate_results": {
      "hash_mismatch": true
    },
    "reason": "Content hash mismatch"
  },
  {
    "request_id": "neg-manifest",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-placeholder",
    "request_type": "manifest_mismatch",
    "decision": "ACCESS_BLOCKED_MANIFEST_MISMATCH",
    "granted": false,
    "audit_record_id": "access-audit-neg-manifest",
    "gate_results": {
      "manifest_mismatch": true
    },
    "reason": "Manifest mismatch"
  },
  {
    "request_id": "neg-unreviewed",
    "row_id": "DCM-001",
    "export_id": "export-pos-dcm001-synthetic",
    "request_type": "unreviewed_approve",
    "decision": "ACCESS_BLOCKED_UNREVIEWED_ARTIFACT",
    "granted": false,
    "audit_record_id": "access-audit-neg-unreviewed",
    "gate_results": {
      "unreviewed_artifact": true
    },
    "reason": "Artifact not research-review approved"
  }
]

## 14. Blocked diagnostic-only rows

DCM-002, DCM-005-BRB, DCM-005-KFOLD, DCM-008 — ACCESS_BLOCKED_DIAGNOSTIC_ONLY

## 15. Blocked null-monitor causal reuse

DCM-005-PLACEBO — ACCESS_BLOCKED_NULL_MONITOR_CAUSAL_REUSE

## 16. Blocked multi-cell/global claims

DCM-006 — ACCESS_BLOCKED_NOT_PROMOTED

## 17. Blocked stratified aggregate claims

DCM-008 — ACCESS_BLOCKED_DIAGNOSTIC_ONLY

## 18. CalibrationSignal boundary

{
  "any_calibration_signal_allowed": false
}

## 19. Live API boundary

{
  "live_api_authorized": false,
  "research_mode_only": true
}

## 20. Scheduler boundary

{
  "scheduler_authorized": false,
  "research_mode_only": true
}

## 21. Production decisioning boundary

{
  "any_production_decisioning_allowed": false
}

## 22. Budget optimization boundary

{
  "any_budget_optimization_allowed": false
}

## 23. Global platform boundary

`trust_report_platform_authorized`: false; `GLOBAL_PLATFORM_ADMIN` blocked

## 24. Audit record verification

Audit records: 37

## 25. Open investigation check

{
  "deferred_investigations": [
    "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
    "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001"
  ],
  "blocking_for_access": []
}

## 26. Governance verdict

`trustreport_research_mode_access_control_passed`

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

**Revisit trigger:** After TRUSTREPORT_RESEARCH_MODE_AUDIT_LOG_001

**Required decision checkpoint:** TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001

**Next artifact:** TRUSTREPORT_RESEARCH_MODE_AUDIT_LOG_001


## Residual Issues and Handoff

Next artifact: `TRUSTREPORT_RESEARCH_MODE_AUDIT_LOG_001`
