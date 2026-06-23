# TRUSTREPORT-INTEGRATION-DRY-RUN-001 Report

## 1. Executive summary

This artifact performs a dry-run integration check for restricted row-level TrustReport contracts.
It does not authorize live APIs, scheduler execution, production decisioning, CalibrationSignal, or budget optimization.
Only DCM-001 and DCM-004 are accepted for restricted TrustReport research-mode dry-run.
All diagnostic-only, null-monitor-only, deferred, ineligible, global multi-cell, and stratified aggregate paths remain blocked.

**Governance verdict:** `trustreport_integration_dry_run_passed`
**Accepted rows:** ['DCM-001', 'DCM-004']

## 2. Scope

Dry-run restricted TrustReport integration for DCM-001 (SCM+JK) and DCM-004 (DID+bootstrap) only.

## 3. Non-goals

- No live API authorization
- No scheduler authorization
- No production automation
- No CalibrationSignal promotion
- No new statistical simulations
- No estimator/inference/design changes

## 4. Input artifacts

{
  "downstream_promotion": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_DOWNSTREAM_PROMOTION_001_summary.json",
  "full_reassessment": "/workspace/panel_exp/docs/track_d/archives/FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
  "dcm001_reassessment": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
  "dcm004_reassessment": "/workspace/panel_exp/docs/track_d/archives/DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
  "prior_validation": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"
}

## 5. Dry-run contract

[
  "row_id",
  "design_family",
  "interval_semantics",
  "audit_artifacts",
  "minimum_post_period",
  "estimand",
  "required_warnings",
  "inference_method",
  "readout_scope",
  "minimum_pre_period",
  "allowed_role",
  "blocked_roles",
  "blocked_geometry",
  "estimator",
  "allowed_geometry",
  "required_diagnostics"
]

## 6. Promoted row contracts

{
  "DCM-001": {
    "row_id": "DCM-001",
    "design_family": "single_cell",
    "estimator": "scm",
    "inference_method": "unit_jackknife",
    "estimand": "treated_unit_effect_level",
    "readout_scope": "restricted_causal_interval",
    "allowed_geometry": "unit_panel_single_cell",
    "blocked_geometry": [
      "aggregate_1x1",
      "multi_cell_pooled",
      "staggered_timing"
    ],
    "minimum_pre_period": "provisional_for_trustreport_reassessment_only",
    "minimum_post_period": "provisional_for_trustreport_reassessment_only",
    "required_diagnostics": [
      "prefit_warning_required",
      "donor_support_gate"
    ],
    "required_warnings": [
      "noisy_world_coverage_caveat",
      "type_i_caveat"
    ],
    "interval_semantics": "restricted_causal_interval_level_scale",
    "allowed_role": "restricted_trustreport_research_only",
    "blocked_roles": [
      "budget_optimization_input",
      "calibration_signal",
      "global_trustreport_platform",
      "live_api",
      "production_automation",
      "production_decisioning",
      "scheduler"
    ],
    "audit_artifacts": [
      "TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
      "D5-STAT-SCM-JK-001"
    ]
  },
  "DCM-004": {
    "row_id": "DCM-004",
    "design_family": "single_cell",
    "estimator": "did",
    "inference_method": "bootstrap",
    "estimand": "cumulative_att_level",
    "readout_scope": "restricted_causal_interval",
    "allowed_geometry": "unit_panel_single_cell",
    "blocked_geometry": [
      "parallel_trends_violation",
      "stress_or_outlier",
      "staggered_timing",
      "staggered_pooled",
      "aggregate_1x1"
    ],
    "minimum_pre_period": 4,
    "minimum_post_period": "support_gated",
    "required_diagnostics": [
      "parallel_trends_diagnostic_required",
      "pretrend_diagnostic_required"
    ],
    "required_warnings": [
      "unsupported_worlds_excluded"
    ],
    "interval_semantics": "restricted_causal_interval",
    "allowed_role": "restricted_trustreport_research_only",
    "blocked_roles": [
      "budget_optimization_input",
      "calibration_signal",
      "global_trustreport_platform",
      "live_api",
      "production_automation",
      "production_decisioning",
      "scheduler"
    ],
    "audit_artifacts": [
      "DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
      "D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001"
    ]
  }
}

## 7. DCM-001 dry-run result

{
  "request_id": "pos-dcm001-valid",
  "row_id": "DCM-001",
  "request_type": "valid_restricted",
  "decision": "DRY_RUN_ACCEPTED_RESTRICTED_TRUSTREPORT",
  "accepted": true,
  "audit_record_id": "audit-pos-dcm001-valid",
  "gate_results": {
    "row_promoted": true,
    "contract_complete": true,
    "warnings_present": true,
    "restrictions_present": true,
    "geometry_allowed": true,
    "dry_run_only": true,
    "live_api_blocked": true,
    "scheduler_blocked": true,
    "calibration_signal_blocked": true
  },
  "reason": "Restricted TrustReport dry-run accepted (research mode only)"
}

## 8. DCM-004 dry-run result

{
  "request_id": "pos-dcm004-valid",
  "row_id": "DCM-004",
  "request_type": "valid_restricted",
  "decision": "DRY_RUN_ACCEPTED_RESTRICTED_TRUSTREPORT",
  "accepted": true,
  "audit_record_id": "audit-pos-dcm004-valid",
  "gate_results": {
    "row_promoted": true,
    "contract_complete": true,
    "warnings_present": true,
    "restrictions_present": true,
    "geometry_allowed": true,
    "dry_run_only": true,
    "live_api_blocked": true,
    "scheduler_blocked": true,
    "calibration_signal_blocked": true
  },
  "reason": "Restricted TrustReport dry-run accepted (research mode only)"
}

## 9. Negative-control rows

[
  {
    "request_id": "neg-dcm001-missing-warnings",
    "row_id": "DCM-001",
    "request_type": "missing_warnings",
    "decision": "DRY_RUN_BLOCKED_MISSING_CONTRACT",
    "accepted": false,
    "audit_record_id": "audit-neg-dcm001-missing-warnings",
    "gate_results": {
      "warnings_missing": true
    },
    "reason": "Required warnings contract absent"
  },
  {
    "request_id": "neg-dcm004-missing-pt-warning",
    "row_id": "DCM-004",
    "request_type": "missing_parallel_trends_warning",
    "decision": "DRY_RUN_BLOCKED_MISSING_CONTRACT",
    "accepted": false,
    "audit_record_id": "audit-neg-dcm004-missing-pt-warning",
    "gate_results": {
      "parallel_trends_warning_missing": true
    },
    "reason": "Parallel-trends warning required for DCM-004"
  },
  {
    "request_id": "neg-dcm001-bad-geometry",
    "row_id": "DCM-001",
    "request_type": "unsupported_geometry",
    "decision": "DRY_RUN_BLOCKED_UNSUPPORTED_GEOMETRY",
    "accepted": false,
    "audit_record_id": "audit-neg-dcm001-bad-geometry",
    "gate_results": {
      "unsupported_geometry": true
    },
    "reason": "Geometry aggregate_1x1 blocked for DCM-001"
  },
  {
    "request_id": "neg-dcm004-bad-timing",
    "row_id": "DCM-004",
    "request_type": "unsupported_timing",
    "decision": "DRY_RUN_BLOCKED_UNSUPPORTED_GEOMETRY",
    "accepted": false,
    "audit_record_id": "audit-neg-dcm004-bad-timing",
    "gate_results": {
      "unsupported_geometry": true
    },
    "reason": "Geometry parallel_trends_violation blocked for DCM-004"
  },
  {
    "request_id": "neg-brb",
    "row_id": "DCM-005-BRB",
    "request_type": "causal_trustreport",
    "decision": "DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "audit_record_id": "audit-neg-brb",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-005-BRB is diagnostic-only; restricted TrustReport dry-run blocked"
  },
  {
    "request_id": "neg-kfold",
    "row_id": "DCM-005-KFOLD",
    "request_type": "causal_trustreport",
    "decision": "DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "audit_record_id": "audit-neg-kfold",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-005-KFOLD is diagnostic-only; restricted TrustReport dry-run blocked"
  },
  {
    "request_id": "neg-placebo",
    "row_id": "DCM-005-PLACEBO",
    "request_type": "causal_trustreport",
    "decision": "DRY_RUN_BLOCKED_NULL_MONITOR_CAUSAL_REUSE",
    "accepted": false,
    "audit_record_id": "audit-neg-placebo",
    "gate_results": {
      "null_monitor_causal_reuse": true
    },
    "reason": "Null-monitor path cannot be reused for causal TrustReport dry-run"
  },
  {
    "request_id": "neg-dcm006-global",
    "row_id": "DCM-006",
    "request_type": "global_claim",
    "decision": "DRY_RUN_BLOCKED_NOT_PROMOTED",
    "accepted": false,
    "audit_record_id": "audit-neg-dcm006-global",
    "gate_results": {
      "multicell_global_blocked": true
    },
    "reason": "DCM-006 global/winner/pooled claims not promoted"
  },
  {
    "request_id": "neg-dcm006-pooled",
    "row_id": "DCM-006",
    "request_type": "pooled_claim",
    "decision": "DRY_RUN_BLOCKED_NOT_PROMOTED",
    "accepted": false,
    "audit_record_id": "audit-neg-dcm006-pooled",
    "gate_results": {
      "multicell_global_blocked": true
    },
    "reason": "DCM-006 global/winner/pooled claims not promoted"
  },
  {
    "request_id": "neg-dcm008-aggregate",
    "row_id": "DCM-008",
    "request_type": "aggregate_stratified",
    "decision": "DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY",
    "accepted": false,
    "audit_record_id": "audit-neg-dcm008-aggregate",
    "gate_results": {
      "diagnostic_only": true
    },
    "reason": "DCM-008 is diagnostic-only; restricted TrustReport dry-run blocked"
  },
  {
    "request_id": "neg-cal-dcm001",
    "row_id": "DCM-001",
    "request_type": "calibration_signal",
    "decision": "DRY_RUN_BLOCKED_CALIBRATION_SIGNAL",
    "accepted": false,
    "audit_record_id": "audit-neg-cal-dcm001",
    "gate_results": {
      "calibration_signal_blocked": true
    },
    "reason": "CalibrationSignal not authorized for any row"
  },
  {
    "request_id": "neg-live-dcm004",
    "row_id": "DCM-004",
    "request_type": "live_api",
    "decision": "DRY_RUN_BLOCKED_LIVE_API",
    "accepted": false,
    "audit_record_id": "audit-neg-live-dcm004",
    "gate_results": {
      "live_api_blocked": true
    },
    "reason": "Live API authorization forbidden in dry-run lane"
  },
  {
    "request_id": "neg-scheduler-dcm001",
    "row_id": "DCM-001",
    "request_type": "scheduler",
    "decision": "DRY_RUN_BLOCKED_SCHEDULER",
    "accepted": false,
    "audit_record_id": "audit-neg-scheduler-dcm001",
    "gate_results": {
      "scheduler_blocked": true
    },
    "reason": "Scheduler authorization forbidden in dry-run lane"
  },
  {
    "request_id": "neg-prod-dcm004",
    "row_id": "DCM-004",
    "request_type": "production",
    "decision": "DRY_RUN_BLOCKED_PRODUCTION_DECISIONING",
    "accepted": false,
    "audit_record_id": "audit-neg-prod-dcm004",
    "gate_results": {
      "production_decisioning_blocked": true
    },
    "reason": "Production decisioning forbidden in dry-run lane"
  },
  {
    "request_id": "neg-budget-dcm001",
    "row_id": "DCM-001",
    "request_type": "budget",
    "decision": "DRY_RUN_BLOCKED_BUDGET_OPTIMIZATION",
    "accepted": false,
    "audit_record_id": "audit-neg-budget-dcm001",
    "gate_results": {
      "budget_optimization_blocked": true
    },
    "reason": "Budget optimization input forbidden in dry-run lane"
  },
  {
    "request_id": "neg-unknown",
    "row_id": "DCM-999",
    "request_type": "unknown",
    "decision": "DRY_RUN_BLOCKED_UNKNOWN_ROW",
    "accepted": false,
    "audit_record_id": "audit-neg-unknown",
    "gate_results": {
      "unknown_row": true
    },
    "reason": "Unknown or unregistered row: DCM-999"
  }
]

## 10. Blocked diagnostic-only rows

DCM-002, DCM-005-BRB, DCM-005-KFOLD, DCM-008 — DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY

## 11. Blocked null-monitor causal reuse

DCM-005-PLACEBO, SCM-PLACEBO causal TrustReport attempts — DRY_RUN_BLOCKED_NULL_MONITOR_CAUSAL_REUSE

## 12. Blocked multi-cell/global claims

DCM-006 global/winner/pooled — DRY_RUN_BLOCKED_NOT_PROMOTED

## 13. Blocked stratified aggregate claims

DCM-008 aggregate — DRY_RUN_BLOCKED_DIAGNOSTIC_ONLY

## 14. CalibrationSignal boundary

{
  "any_calibration_signal_allowed": false,
  "per_row": {
    "DCM-001": false,
    "DCM-004": false
  }
}

## 15. Live API boundary

{
  "live_api_authorized": false,
  "dry_run_only": true,
  "rationale": "Live API blocked in dry-run lane"
}

## 16. Scheduler boundary

{
  "scheduler_authorized": false,
  "dry_run_only": true,
  "rationale": "Scheduler blocked in dry-run lane"
}

## 17. Production decisioning boundary

{
  "any_production_decisioning_allowed": false
}

## 18. Budget optimization boundary

{
  "any_budget_optimization_allowed": false
}

## 19. Audit record verification

Audit records emitted: 22

## 20. Open investigation check

{
  "deferred_investigations": [
    "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
    "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001"
  ],
  "blocking_for_dry_run": [],
  "rationale": "Deferred multicell investigations do not block DCM-001/004 dry-run"
}

## 21. Governance verdict

`trustreport_integration_dry_run_passed`

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

**Revisit trigger:** After TRUSTREPORT_RESEARCH_MODE_RENDERER_001 or contract remediation

**Required decision checkpoint:** TRUSTREPORT_INTEGRATION_DRY_RUN_001

**Next artifact:** TRUSTREPORT_RESEARCH_MODE_RENDERER_001


## Residual Issues and Handoff

Next artifact: `TRUSTREPORT_RESEARCH_MODE_RENDERER_001`
