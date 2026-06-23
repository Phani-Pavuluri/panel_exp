# TRUSTREPORT-RESEARCH-MODE-RENDERER-001 Report

## 1. Executive summary

This artifact renders restricted row-level TrustReport contracts in research mode only.
It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, budget optimization, or global platform rollout.
Only DCM-001 and DCM-004 are accepted for research-mode rendering.
All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.

**Governance verdict:** `trustreport_research_mode_renderer_passed`
**Accepted rows:** ['DCM-001', 'DCM-004']

## 2. Scope

Research-mode TrustReport renderer for DCM-001 (SCM+JK) and DCM-004 (DID+bootstrap).

## 3. Non-goals

- No live API, scheduler, production automation
- No CalibrationSignal, budget optimization, recommendations
- No new statistical simulations or algorithm changes

## 4. Input artifacts

{
  "integration_dry_run": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_INTEGRATION_DRY_RUN_001_summary.json",
  "downstream_promotion": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json",
  "full_reassessment": "/workspace/panel_exp/docs/track_d/archives/FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json"
}

## 5. Research-mode renderer contract

[
  "readout_scope",
  "required_warnings",
  "inference_method",
  "allowed_geometry",
  "research_mode_only",
  "design_family",
  "blocked_roles",
  "minimum_pre_period",
  "minimum_post_period",
  "required_diagnostics",
  "audit_artifacts",
  "dry_run_approval_artifact",
  "interval_semantics",
  "promotion_artifact",
  "blocked_geometry",
  "row_id",
  "estimand",
  "estimator",
  "allowed_role"
]

## 6. Rendered output schema

{
  "required_fields": [
    "title",
    "artifact_id",
    "row_id",
    "method_identity",
    "estimand",
    "allowed_scope",
    "measurement",
    "diagnostic_requirements",
    "warnings",
    "restrictions",
    "blocked_uses",
    "audit_trail",
    "authorization_boundaries",
    "banners",
    "render_status"
  ],
  "placeholder_label": "NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED",
  "synthetic_label": "SYNTHETIC_DRY_RUN_PAYLOAD"
}

## 7. DCM-001 render result

{
  "request_id": "pos-dcm001-valid",
  "row_id": "DCM-001",
  "request_type": "valid_research",
  "decision": "RENDER_ACCEPTED_PLACEHOLDER_RESEARCH_MODE",
  "accepted": true,
  "audit_record_id": "render-audit-pos-dcm001-valid",
  "render_status": "accepted",
  "gate_results": {
    "row_promoted": true,
    "dry_run_approved": true,
    "contract_complete": true,
    "warnings_present": true,
    "research_mode_only": true,
    "live_api_blocked": true,
    "scheduler_blocked": true,
    "calibration_signal_blocked": true
  },
  "reason": "Research-mode TrustReport render accepted"
}

## 8. DCM-004 render result

{
  "request_id": "pos-dcm004-valid",
  "row_id": "DCM-004",
  "request_type": "valid_research",
  "decision": "RENDER_ACCEPTED_PLACEHOLDER_RESEARCH_MODE",
  "accepted": true,
  "audit_record_id": "render-audit-pos-dcm004-valid",
  "render_status": "accepted",
  "gate_results": {
    "row_promoted": true,
    "dry_run_approved": true,
    "contract_complete": true,
    "warnings_present": true,
    "research_mode_only": true,
    "live_api_blocked": true,
    "scheduler_blocked": true,
    "calibration_signal_blocked": true
  },
  "reason": "Research-mode TrustReport render accepted"
}

## 9. Placeholder payload behavior

When no live readout is supplied, measurement section uses `NO_LIVE_MEASUREMENT_PAYLOAD_SUPPLIED`.

## 10. Synthetic dry-run payload behavior

Synthetic payloads labeled `SYNTHETIC_DRY_RUN_PAYLOAD` with `synthetic: true` and `non_decisioning: true`.

## 11. Negative-control render requests

[
  {
    "request_id": "neg-dcm001-missing-warnings",
    "row_id": "DCM-001",
    "request_type": "missing_warnings",
    "decision": "RENDER_BLOCKED_MISSING_CONTRACT",
    "accepted": false,
    "audit_record_id": "render-audit-neg-dcm001-missing-warnings",
    "render_status": "blocked",
    "gate_results": {
      "warnings_missing": true
    },
    "reason": "Required warnings missing"
  },
  {
    "request_id": "neg-dcm004-missing-diagnostics",
    "row_id": "DCM-004",
    "request_type": "missing_diagnostics",
    "decision": "RENDER_BLOCKED_MISSING_DIAGNOSTICS",
    "accepted": false,
    "audit_record_id": "render-audit-neg-dcm004-missing-diagnostics",
    "render_status": "blocked",
    "gate_results": {
      "diagnostics_missing": true
    },
    "reason": "Parallel-trends diagnostics required for DCM-004"
  },
  {
    "request_id": "neg-dcm001-bad-geometry",
    "row_id": "DCM-001",
    "request_type": "unsupported_geometry",
    "decision": "RENDER_BLOCKED_UNSUPPORTED_GEOMETRY",
    "accepted": false,
    "audit_record_id": "render-audit-neg-dcm001-bad-geometry",
    "render_status": "blocked",
    "gate_results": {
      "unsupported_geometry": true
    },
    "reason": "Geometry aggregate_1x1 blocked"
  },
  {
    "request_id": "neg-dcm004-bad-timing",
    "row_id": "DCM-004",
    "request_type": "unsupported_timing",
    "decision": "RENDER_BLOCKED_UNSUPPORTED_GEOMETRY",
    "accepted": false,
    "audit_record_id": "render-audit-neg-dcm004-bad-timing",
    "render_status": "blocked",
    "gate_results": {
      "unsupported_geometry": true
    },
    "reason": "Geometry parallel_trends_violation blocked"
  },
  {
    "request_id": "neg-brb",
    "row_id": "DCM-005-BRB",
    "request_type": "causal_trustreport",
    "decision": "RENDER_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "audit_record_id": "render-audit-neg-brb",
    "render_status": "blocked",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-005-BRB is diagnostic-only"
  },
  {
    "request_id": "neg-kfold",
    "row_id": "DCM-005-KFOLD",
    "request_type": "causal_trustreport",
    "decision": "RENDER_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "audit_record_id": "render-audit-neg-kfold",
    "render_status": "blocked",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-005-KFOLD is diagnostic-only"
  },
  {
    "request_id": "neg-placebo",
    "row_id": "DCM-005-PLACEBO",
    "request_type": "causal_trustreport",
    "decision": "RENDER_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
    "accepted": false,
    "audit_record_id": "render-audit-neg-placebo",
    "render_status": "blocked",
    "gate_results": {
      "null_monitor_causal_reuse": true
    },
    "reason": "Null-monitor path cannot render causal TrustReport"
  },
  {
    "request_id": "neg-dcm006-global",
    "row_id": "DCM-006",
    "request_type": "global_claim",
    "decision": "RENDER_BLOCKED_NOT_PROMOTED",
    "accepted": false,
    "audit_record_id": "render-audit-neg-dcm006-global",
    "render_status": "blocked",
    "gate_results": {
      "multicell_global_blocked": true
    },
    "reason": "DCM-006 global/winner/pooled render blocked"
  },
  {
    "request_id": "neg-dcm008-aggregate",
    "row_id": "DCM-008",
    "request_type": "aggregate_stratified",
    "decision": "RENDER_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "audit_record_id": "render-audit-neg-dcm008-aggregate",
    "render_status": "blocked",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-008 is diagnostic-only"
  },
  {
    "request_id": "neg-cal",
    "row_id": "DCM-001",
    "request_type": "calibration",
    "decision": "RENDER_BLOCKED_CALIBRATION_SIGNAL",
    "accepted": false,
    "audit_record_id": "render-audit-neg-cal",
    "render_status": "blocked",
    "gate_results": {
      "calibration_signal_blocked": true
    },
    "reason": "CalibrationSignal render forbidden"
  },
  {
    "request_id": "neg-live",
    "row_id": "DCM-004",
    "request_type": "live_api",
    "decision": "RENDER_BLOCKED_LIVE_API",
    "accepted": false,
    "audit_record_id": "render-audit-neg-live",
    "render_status": "blocked",
    "gate_results": {
      "live_api_blocked": true
    },
    "reason": "Live API render mode forbidden"
  },
  {
    "request_id": "neg-scheduler",
    "row_id": "DCM-001",
    "request_type": "scheduler",
    "decision": "RENDER_BLOCKED_SCHEDULER",
    "accepted": false,
    "audit_record_id": "render-audit-neg-scheduler",
    "render_status": "blocked",
    "gate_results": {
      "scheduler_blocked": true
    },
    "reason": "Scheduler render mode forbidden"
  },
  {
    "request_id": "neg-prod",
    "row_id": "DCM-004",
    "request_type": "production",
    "decision": "RENDER_BLOCKED_PRODUCTION_DECISIONING",
    "accepted": false,
    "audit_record_id": "render-audit-neg-prod",
    "render_status": "blocked",
    "gate_results": {
      "production_mode_blocked": true
    },
    "reason": "Production render mode forbidden"
  },
  {
    "request_id": "neg-budget",
    "row_id": "DCM-001",
    "request_type": "budget",
    "decision": "RENDER_BLOCKED_BUDGET_OPTIMIZATION",
    "accepted": false,
    "audit_record_id": "render-audit-neg-budget",
    "render_status": "blocked",
    "gate_results": {
      "budget_optimization_blocked": true
    },
    "reason": "Budget optimization render forbidden"
  },
  {
    "request_id": "neg-unknown",
    "row_id": "DCM-999",
    "request_type": "unknown",
    "decision": "RENDER_BLOCKED_UNKNOWN_ROW",
    "accepted": false,
    "audit_record_id": "render-audit-neg-unknown",
    "render_status": "blocked",
    "gate_results": {
      "unknown_row": true
    },
    "reason": "Unknown row: DCM-999"
  }
]

## 12. Blocked diagnostic-only rows

DCM-002, DCM-005-BRB, DCM-005-KFOLD, DCM-008 — RENDER_BLOCKED_DIAGNOSTIC_ONLY

## 13. Blocked null-monitor causal reuse

DCM-005-PLACEBO causal render — RENDER_BLOCKED_NULL_MONITOR_CAUSAL_REUSE

## 14. Blocked multi-cell/global claims

DCM-006 — RENDER_BLOCKED_NOT_PROMOTED

## 15. Blocked stratified aggregate claims

DCM-008 aggregate — RENDER_BLOCKED_DIAGNOSTIC_ONLY

## 16. CalibrationSignal boundary

{
  "any_calibration_signal_allowed": false
}

## 17. Live API boundary

{
  "live_api_authorized": false,
  "research_mode_only": true
}

## 18. Scheduler boundary

{
  "scheduler_authorized": false,
  "research_mode_only": true
}

## 19. Production decisioning boundary

{
  "any_production_decisioning_allowed": false
}

## 20. Budget optimization boundary

{
  "any_budget_optimization_allowed": false
}

## 21. Audit record verification

Audit records: 21

## 22. Open investigation check

{
  "deferred_investigations": [
    "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
    "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001"
  ],
  "blocking_for_renderer": []
}

## 23. Governance verdict

`trustreport_research_mode_renderer_passed`

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

**Revisit trigger:** After TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001

**Required decision checkpoint:** TRUSTREPORT_RESEARCH_MODE_RENDERER_001

**Next artifact:** TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001


## Residual Issues and Handoff

Next artifact: `TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001` (✅ complete — see [`TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_REPORT.md`](TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_REPORT.md); next: `TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001`)
