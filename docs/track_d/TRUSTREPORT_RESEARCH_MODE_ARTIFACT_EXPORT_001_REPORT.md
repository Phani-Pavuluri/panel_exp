# TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001 Report

## 1. Executive summary

This artifact exports restricted row-level TrustReport research-mode artifacts only.
It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.
Only DCM-001 and DCM-004 are accepted for sanitized research-mode artifact export.
All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.

**Governance verdict:** `trustreport_research_mode_artifact_export_passed`
**Accepted rows:** ['DCM-001', 'DCM-004']

## 2. Scope

Sanitized research-mode artifact export for DCM-001 (SCM+JK) and DCM-004 (DID+bootstrap).

## 3. Non-goals

- No live API, scheduler, production automation
- No CalibrationSignal, budget optimization, recommendations
- No new statistical simulations or algorithm changes
- No unsanitized live measurement payloads

## 4. Input artifacts

{
  "renderer_summary": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_RESEARCH_MODE_RENDERER_001_summary.json",
  "integration_dry_run": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_INTEGRATION_DRY_RUN_001_summary.json",
  "downstream_promotion": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json"
}

## 5. Research-mode artifact export contract

[
  "export_manifest",
  "dry_run_artifact",
  "content_hash",
  "sanitized_payload",
  "authorization_boundaries",
  "audit_trail",
  "method_identity",
  "schema_version",
  "blocked_uses",
  "warnings",
  "created_at",
  "restrictions",
  "research_mode_only",
  "renderer_summary_artifact",
  "artifact_id",
  "promotion_artifact",
  "readout_scope",
  "estimand",
  "export_id",
  "row_id",
  "render_source_artifact"
]

## 6. Exported artifact schema

{
  "required_fields": [
    "export_manifest",
    "dry_run_artifact",
    "content_hash",
    "sanitized_payload",
    "authorization_boundaries",
    "audit_trail",
    "method_identity",
    "schema_version",
    "blocked_uses",
    "warnings",
    "created_at",
    "restrictions",
    "research_mode_only",
    "renderer_summary_artifact",
    "artifact_id",
    "promotion_artifact",
    "readout_scope",
    "estimand",
    "export_id",
    "row_id",
    "render_source_artifact"
  ],
  "banners": [
    "RESEARCH MODE ONLY",
    "NOT FOR PRODUCTION DECISIONING",
    "NOT FOR BUDGET OPTIMIZATION",
    "NO CALIBRATIONSIGNAL AUTHORIZATION",
    "NO LIVE API AUTHORIZATION",
    "NO SCHEDULER AUTHORIZATION",
    "SANITIZED ARTIFACT EXPORT"
  ],
  "placeholder_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
  "synthetic_label": "SYNTHETIC_DRY_RUN_PAYLOAD",
  "manifest_only_label": "MANIFEST_ONLY_EXPORT"
}

## 7. Manifest schema

{
  "required_fields": [
    "export_id",
    "row_id",
    "export_type",
    "schema_version",
    "content_hash",
    "sanitized",
    "research_mode_only",
    "measurement_label",
    "created_at"
  ]
}

## 8. Sanitization rules

Accepted exports must not include live data, raw identifiers, production recommendations, budget allocation, CalibrationSignal fields, scheduler/API payloads, or hidden authorization flags. Synthetic payloads require `synthetic: true` and `non_decisioning: true`. Placeholder payloads use `NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED`.

## 9. DCM-001 export result

{
  "request_id": "pos-dcm001-placeholder",
  "row_id": "DCM-001",
  "request_type": "placeholder_export",
  "decision": "EXPORT_ACCEPTED_PLACEHOLDER_RESEARCH_MODE",
  "accepted": true,
  "audit_record_id": "export-audit-pos-dcm001-placeholder",
  "export_status": "accepted",
  "gate_results": {
    "row_promoted": true,
    "dry_run_approved": true,
    "contract_complete": true,
    "warnings_present": true,
    "sanitized_payload": true,
    "research_mode_only": true,
    "live_api_blocked": true,
    "scheduler_blocked": true,
    "calibration_signal_blocked": true
  },
  "reason": "Research-mode TrustReport export accepted",
  "content_hash": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e"
}

## 10. DCM-004 export result

{
  "request_id": "pos-dcm004-placeholder",
  "row_id": "DCM-004",
  "request_type": "placeholder_export",
  "decision": "EXPORT_ACCEPTED_PLACEHOLDER_RESEARCH_MODE",
  "accepted": true,
  "audit_record_id": "export-audit-pos-dcm004-placeholder",
  "export_status": "accepted",
  "gate_results": {
    "row_promoted": true,
    "dry_run_approved": true,
    "contract_complete": true,
    "warnings_present": true,
    "sanitized_payload": true,
    "research_mode_only": true,
    "live_api_blocked": true,
    "scheduler_blocked": true,
    "calibration_signal_blocked": true
  },
  "reason": "Research-mode TrustReport export accepted",
  "content_hash": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516"
}

## 11. Placeholder export behavior

Placeholder exports use `NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED` with null point/interval.

## 12. Synthetic export behavior

Synthetic exports labeled `SYNTHETIC_DRY_RUN_PAYLOAD` with `synthetic: true` and `non_decisioning: true`.

## 13. Manifest-only export behavior

Manifest-only exports include metadata and content hash without measurement payload.

## 14. Negative-control export requests

[
  {
    "request_id": "neg-dcm001-missing-warnings",
    "row_id": "DCM-001",
    "request_type": "missing_warnings",
    "decision": "EXPORT_BLOCKED_MISSING_CONTRACT",
    "accepted": false,
    "audit_record_id": "export-audit-neg-dcm001-missing-warnings",
    "export_status": "blocked",
    "gate_results": {
      "warnings_missing": true
    },
    "reason": "Required warnings missing",
    "content_hash": null
  },
  {
    "request_id": "neg-dcm004-missing-diagnostics",
    "row_id": "DCM-004",
    "request_type": "missing_diagnostics",
    "decision": "EXPORT_BLOCKED_MISSING_DIAGNOSTICS",
    "accepted": false,
    "audit_record_id": "export-audit-neg-dcm004-missing-diagnostics",
    "export_status": "blocked",
    "gate_results": {
      "diagnostics_missing": true
    },
    "reason": "Parallel-trends diagnostics required for DCM-004",
    "content_hash": null
  },
  {
    "request_id": "neg-dcm001-bad-geometry",
    "row_id": "DCM-001",
    "request_type": "unsupported_geometry",
    "decision": "EXPORT_BLOCKED_UNSUPPORTED_GEOMETRY",
    "accepted": false,
    "audit_record_id": "export-audit-neg-dcm001-bad-geometry",
    "export_status": "blocked",
    "gate_results": {
      "unsupported_geometry": true
    },
    "reason": "Geometry aggregate_1x1 blocked",
    "content_hash": null
  },
  {
    "request_id": "neg-dcm004-bad-timing",
    "row_id": "DCM-004",
    "request_type": "unsupported_timing",
    "decision": "EXPORT_BLOCKED_UNSUPPORTED_GEOMETRY",
    "accepted": false,
    "audit_record_id": "export-audit-neg-dcm004-bad-timing",
    "export_status": "blocked",
    "gate_results": {
      "unsupported_geometry": true
    },
    "reason": "Geometry parallel_trends_violation blocked",
    "content_hash": null
  },
  {
    "request_id": "neg-brb",
    "row_id": "DCM-005-BRB",
    "request_type": "causal_trustreport",
    "decision": "EXPORT_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "audit_record_id": "export-audit-neg-brb",
    "export_status": "blocked",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-005-BRB is diagnostic-only",
    "content_hash": null
  },
  {
    "request_id": "neg-kfold",
    "row_id": "DCM-005-KFOLD",
    "request_type": "causal_trustreport",
    "decision": "EXPORT_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "audit_record_id": "export-audit-neg-kfold",
    "export_status": "blocked",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-005-KFOLD is diagnostic-only",
    "content_hash": null
  },
  {
    "request_id": "neg-placebo",
    "row_id": "DCM-005-PLACEBO",
    "request_type": "causal_trustreport",
    "decision": "EXPORT_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
    "accepted": false,
    "audit_record_id": "export-audit-neg-placebo",
    "export_status": "blocked",
    "gate_results": {
      "null_monitor_causal_reuse": true
    },
    "reason": "Null-monitor path cannot export causal TrustReport",
    "content_hash": null
  },
  {
    "request_id": "neg-dcm006-global",
    "row_id": "DCM-006",
    "request_type": "global_claim",
    "decision": "EXPORT_BLOCKED_NOT_PROMOTED",
    "accepted": false,
    "audit_record_id": "export-audit-neg-dcm006-global",
    "export_status": "blocked",
    "gate_results": {
      "multicell_global_blocked": true
    },
    "reason": "DCM-006 global/winner/pooled export blocked",
    "content_hash": null
  },
  {
    "request_id": "neg-dcm008-aggregate",
    "row_id": "DCM-008",
    "request_type": "aggregate_stratified",
    "decision": "EXPORT_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "audit_record_id": "export-audit-neg-dcm008-aggregate",
    "export_status": "blocked",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-008 is diagnostic-only",
    "content_hash": null
  },
  {
    "request_id": "neg-cal",
    "row_id": "DCM-001",
    "request_type": "calibration",
    "decision": "EXPORT_BLOCKED_CALIBRATION_SIGNAL",
    "accepted": false,
    "audit_record_id": "export-audit-neg-cal",
    "export_status": "blocked",
    "gate_results": {
      "calibration_signal_payload_blocked": true
    },
    "reason": "Export type calibration_signal_payload forbidden",
    "content_hash": null
  },
  {
    "request_id": "neg-live",
    "row_id": "DCM-004",
    "request_type": "live_api",
    "decision": "EXPORT_BLOCKED_LIVE_API",
    "accepted": false,
    "audit_record_id": "export-audit-neg-live",
    "export_status": "blocked",
    "gate_results": {
      "live_api_payload_blocked": true
    },
    "reason": "Export type live_api_payload forbidden",
    "content_hash": null
  },
  {
    "request_id": "neg-scheduler",
    "row_id": "DCM-001",
    "request_type": "scheduler",
    "decision": "EXPORT_BLOCKED_SCHEDULER",
    "accepted": false,
    "audit_record_id": "export-audit-neg-scheduler",
    "export_status": "blocked",
    "gate_results": {
      "scheduler_payload_blocked": true
    },
    "reason": "Export type scheduler_payload forbidden",
    "content_hash": null
  },
  {
    "request_id": "neg-prod",
    "row_id": "DCM-004",
    "request_type": "production",
    "decision": "EXPORT_BLOCKED_PRODUCTION_DECISIONING",
    "accepted": false,
    "audit_record_id": "export-audit-neg-prod",
    "export_status": "blocked",
    "gate_results": {
      "decisioning_payload_blocked": true
    },
    "reason": "Export type decisioning_payload forbidden",
    "content_hash": null
  },
  {
    "request_id": "neg-budget",
    "row_id": "DCM-001",
    "request_type": "budget",
    "decision": "EXPORT_BLOCKED_BUDGET_OPTIMIZATION",
    "accepted": false,
    "audit_record_id": "export-audit-neg-budget",
    "export_status": "blocked",
    "gate_results": {
      "budget_optimization_payload_blocked": true
    },
    "reason": "Export type budget_optimization_payload forbidden",
    "content_hash": null
  },
  {
    "request_id": "neg-unknown",
    "row_id": "DCM-999",
    "request_type": "unknown",
    "decision": "EXPORT_BLOCKED_UNKNOWN_ROW",
    "accepted": false,
    "audit_record_id": "export-audit-neg-unknown",
    "export_status": "blocked",
    "gate_results": {
      "unknown_row": true
    },
    "reason": "Unknown row: DCM-999",
    "content_hash": null
  },
  {
    "request_id": "neg-unsanitized",
    "row_id": "DCM-001",
    "request_type": "unsanitized_payload",
    "decision": "EXPORT_BLOCKED_UNSANITIZED_PAYLOAD",
    "accepted": false,
    "audit_record_id": "export-audit-neg-unsanitized",
    "export_status": "blocked",
    "gate_results": {
      "unsanitized_payload": true
    },
    "reason": "Unsanitized live measurement payload blocked",
    "content_hash": null
  },
  {
    "request_id": "neg-missing-audit",
    "row_id": "DCM-004",
    "request_type": "missing_audit_trail",
    "decision": "EXPORT_BLOCKED_MISSING_AUDIT_TRAIL",
    "accepted": false,
    "audit_record_id": "export-audit-neg-missing-audit",
    "export_status": "blocked",
    "gate_results": {
      "audit_trail_missing": true
    },
    "reason": "Audit trail required for export",
    "content_hash": null
  }
]

## 15. Blocked diagnostic-only rows

DCM-002, DCM-005-BRB, DCM-005-KFOLD, DCM-008 — EXPORT_BLOCKED_DIAGNOSTIC_ONLY

## 16. Blocked null-monitor causal reuse

DCM-005-PLACEBO causal export — EXPORT_BLOCKED_NULL_MONITOR_CAUSAL_REUSE

## 17. Blocked multi-cell/global claims

DCM-006 — EXPORT_BLOCKED_NOT_PROMOTED

## 18. Blocked stratified aggregate claims

DCM-008 aggregate — EXPORT_BLOCKED_DIAGNOSTIC_ONLY

## 19. CalibrationSignal boundary

{
  "any_calibration_signal_allowed": false
}

## 20. Live API boundary

{
  "live_api_authorized": false,
  "research_mode_only": true
}

## 21. Scheduler boundary

{
  "scheduler_authorized": false,
  "research_mode_only": true
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

Audit records: 23

## 25. Content-hash verification

{
  "pos-dcm001-placeholder": "2168462379e105571df6b660984cc36b64163e3c8b5190eee680486e7017de5e",
  "pos-dcm004-placeholder": "b2a4748bae9383ae45ccc51fc2c14c104f097d170303113e405c11730994f516",
  "pos-dcm001-synthetic": "f9a0960bbb06cca2d2373a6918a03c0fe2cc5939700f101c593a95f6f3b8c495",
  "pos-dcm004-synthetic": "c54cb2b171ee51efe79bb901a8839dcb09a74249e57d5cf14d99929239c7662c",
  "pos-dcm001-manifest": "f8372f936de17b4ad8a53c8507f189c5a607fa46b8ae39910e33ec7797cd8754",
  "pos-dcm004-manifest": "e51becb6cf3628ba9b0cbe7d21ac356499f01d35f5f022a74cb451340962326b"
}

## 26. Open investigation check

{
  "deferred_investigations": [
    "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
    "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001"
  ],
  "blocking_for_export": []
}

## 27. Governance verdict

`trustreport_research_mode_artifact_export_passed`

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

**Revisit trigger:** After TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001

**Required decision checkpoint:** TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001

**Next artifact:** TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001


## Residual Issues and Handoff

Next artifact: `TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001`
