# TRUSTREPORT-DOWNSTREAM-PROMOTION-001 Report

## 1. Executive summary

Governance verdict: `trustreport_downstream_restricted_row_promotion_approved`. Promoted rows: ['DCM-001', 'DCM-004']. Global platform, live API, and scheduler authorization remain false.

## 2. Scope

Restricted downstream promotion review for DCM-001 and DCM-004 only.

## 3. Non-goals

- No new statistical simulations
- No estimator/inference remediation
- No live API or scheduler authorization
- No global TrustReport platform rollout

## 4. Input artifacts

{
  "full_reassessment": "/workspace/panel_exp/docs/track_d/archives/FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
  "brb_post_remediation": "/workspace/panel_exp/docs/track_d/archives/DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001_summary.json",
  "dcm001_reassessment": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
  "dcm004_reassessment": "/workspace/panel_exp/docs/track_d/archives/DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_summary.json",
  "prior_validation": "/workspace/panel_exp/docs/track_d/archives/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_summary.json"
}

## 5. Candidate universe

[
  "DCM-001",
  "DCM-004"
]

## 6. Promotion gates

{
  "gate_definitions": [
    "full_reassessment_eligible",
    "no_blocking_investigations",
    "evidence_artifacts_present",
    "restrictions_present",
    "restriction_contract_complete",
    "interval_semantics_supported",
    "calibration_signal_not_requested_or_explicit",
    "not_live_platform_authorization"
  ],
  "global_live_authorization_forbidden": true
}

## 7. DCM-001 review

{
  "row_id": "DCM-001",
  "decision": "PROMOTE_RESTRICTED_TRUSTREPORT",
  "trustreport_eligibility": "ELIGIBLE_WITH_RESTRICTIONS",
  "evidence_artifacts": [
    "TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
    "D5-STAT-SCM-JK-001"
  ],
  "gate_results": {
    "full_reassessment_eligible": true,
    "no_blocking_investigations": true,
    "evidence_artifacts_present": true,
    "restrictions_present": true,
    "restriction_contract_complete": true,
    "interval_semantics_supported": true,
    "calibration_signal_not_requested_or_explicit": true,
    "not_live_platform_authorization": true
  },
  "gates_pass": true,
  "restriction_contract": {
    "allowed_design_family": "single_cell",
    "allowed_estimator": "scm",
    "allowed_inference_method": "unit_jackknife",
    "allowed_estimand": "treated_unit_effect_level",
    "allowed_geometry": "unit_panel_single_cell",
    "allowed_readout_scope": "restricted_causal_interval",
    "minimum_pre_period": "provisional_for_trustreport_reassessment_only",
    "minimum_post_period": "provisional_for_trustreport_reassessment_only",
    "required_fit_diagnostics": [
      "prefit_warning_required",
      "donor_support_gate"
    ],
    "required_interval_semantics": "restricted_causal_interval_level_scale",
    "required_warnings": [
      "noisy_world_coverage_caveat",
      "type_i_caveat"
    ],
    "blocked_geometries": [
      "aggregate_1x1",
      "multi_cell_pooled",
      "staggered_timing"
    ],
    "blocked_downstream_uses": [
      "budget_optimization_input",
      "calibration_signal",
      "global_trustreport_platform",
      "live_api",
      "production_automation",
      "scheduler"
    ],
    "calibration_signal_allowed": false,
    "trustreport_role": "restricted_trustreport_research_only"
  },
  "exclusion_reason": "",
  "blocking_investigations": [],
  "required_warnings": [
    "noisy_world_coverage_caveat",
    "type_i_caveat"
  ],
  "required_restrictions": [
    "support_gated",
    "prefit_warning_required",
    "population_ate_blocked",
    "no_trustreport_authorization"
  ],
  "calibration_signal_allowed": false,
  "trustreport_role": "restricted_trustreport_research_only",
  "row_level_restricted_promotion_allowed": true
}

## 8. DCM-004 review

{
  "row_id": "DCM-004",
  "decision": "PROMOTE_RESTRICTED_TRUSTREPORT",
  "trustreport_eligibility": "ELIGIBLE_WITH_RESTRICTIONS",
  "evidence_artifacts": [
    "DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001",
    "D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001"
  ],
  "gate_results": {
    "full_reassessment_eligible": true,
    "no_blocking_investigations": true,
    "evidence_artifacts_present": true,
    "restrictions_present": true,
    "restriction_contract_complete": true,
    "interval_semantics_supported": true,
    "calibration_signal_not_requested_or_explicit": true,
    "not_live_platform_authorization": true
  },
  "gates_pass": true,
  "restriction_contract": {
    "allowed_design_family": "single_cell",
    "allowed_estimator": "did",
    "allowed_inference_method": "bootstrap",
    "allowed_estimand": "cumulative_att_level",
    "allowed_geometry": "unit_panel_single_cell",
    "allowed_readout_scope": "restricted_causal_interval",
    "minimum_pre_period": 4,
    "minimum_post_period": "support_gated",
    "required_fit_diagnostics": [
      "parallel_trends_diagnostic_required",
      "pretrend_diagnostic_required"
    ],
    "required_interval_semantics": "restricted_causal_interval",
    "required_warnings": [
      "unsupported_worlds_excluded"
    ],
    "blocked_geometries": [
      "parallel_trends_violation",
      "stress_or_outlier",
      "staggered_timing",
      "staggered_pooled",
      "aggregate_1x1"
    ],
    "blocked_downstream_uses": [
      "budget_optimization_input",
      "calibration_signal",
      "global_trustreport_platform",
      "live_api",
      "production_automation",
      "scheduler"
    ],
    "calibration_signal_allowed": false,
    "trustreport_role": "restricted_trustreport_research_only",
    "timing_regime": "common_simultaneous_adoption"
  },
  "exclusion_reason": "",
  "blocking_investigations": [],
  "required_warnings": [
    "unsupported_worlds_excluded"
  ],
  "required_restrictions": [
    "common_simultaneous_adoption_only",
    "parallel_trends_violation_excluded",
    "staggered_pooled_blocked",
    "no_trustreport_authorization"
  ],
  "calibration_signal_allowed": false,
  "trustreport_role": "restricted_trustreport_research_only",
  "row_level_restricted_promotion_allowed": true
}

## 9. Excluded DCM-005 paths

BRB: `BRB_DIAGNOSTIC_ONLY` — TBRRidge + BRB is excluded because post-remediation reassessment terminally marked it diagnostic-only after failed null calibration. It is not eligible for TrustReport, CalibrationSignal, production decisioning, or budget optimization input.
KFold: diagnostic-only — excluded.
Placebo: null-monitor-only — excluded from causal TrustReport promotion.

## 10. Excluded DCM-006 paths

DCM-006 remains limited to governed marginal per-cell readouts under PARALLEL_MARGINAL_CELLS + REPORT_EACH_CELL_ONLY. This artifact does not promote any-cell success, winner/ranking selection, pooled multi-cell causal readout, or global TrustReport decisioning.

## 11. Excluded DCM-008 paths

DCM-008 stratified SCM+JK remains diagnostic-only. Aggregate stratified readout is characterization only, not a governed pooled causal estimand.

## 12. Other excluded/deferred paths

[
  "DCM-005-BRB",
  "DCM-005-KFOLD",
  "DCM-005-PLACEBO",
  "DCM-006",
  "DCM-008",
  "DCM-002",
  "SCM-PLACEBO",
  "DCM-003",
  "DCM-007",
  "DCM-009",
  "DCM-010",
  "DCM-011",
  "DCM-012",
  "DCM-013",
  "DCM-014",
  "DCM-015",
  "DCM-016",
  "DCM-017",
  "DCM-018",
  "DCM-019"
]

## 13. Row-level authorization matrix

{
  "DCM-001": {
    "decision": "PROMOTE_RESTRICTED_TRUSTREPORT",
    "row_level_restricted_promotion_allowed": true,
    "trustreport_role": "restricted_trustreport_research_only",
    "calibration_signal_allowed": false
  },
  "DCM-004": {
    "decision": "PROMOTE_RESTRICTED_TRUSTREPORT",
    "row_level_restricted_promotion_allowed": true,
    "trustreport_role": "restricted_trustreport_research_only",
    "calibration_signal_allowed": false
  },
  "DCM-005-BRB": {
    "decision": "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-005-KFOLD": {
    "decision": "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-005-PLACEBO": {
    "decision": "PROMOTE_NULL_MONITOR_ONLY",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-006": {
    "decision": "DO_NOT_PROMOTE_NOT_IN_SCOPE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-008": {
    "decision": "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-002": {
    "decision": "DO_NOT_PROMOTE_DIAGNOSTIC_ONLY",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "SCM-PLACEBO": {
    "decision": "PROMOTE_NULL_MONITOR_ONLY",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-003": {
    "decision": "DO_NOT_PROMOTE_INELIGIBLE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-007": {
    "decision": "DO_NOT_PROMOTE_INELIGIBLE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-009": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-010": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-011": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-012": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-013": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-014": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-015": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-016": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-017": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-018": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  },
  "DCM-019": {
    "decision": "DO_NOT_PROMOTE_INSUFFICIENT_EVIDENCE",
    "row_level_restricted_promotion_allowed": false,
    "trustreport_role": "blocked",
    "calibration_signal_allowed": false
  }
}

## 14. CalibrationSignal implications

CalibrationSignal remains false for all rows. No CalibrationSignal promotion.

{
  "DCM-001": false,
  "DCM-004": false,
  "DCM-005-BRB": false,
  "DCM-005-KFOLD": false,
  "DCM-005-PLACEBO": false,
  "DCM-006": false,
  "DCM-008": false,
  "DCM-002": false,
  "SCM-PLACEBO": false,
  "DCM-003": false,
  "DCM-007": false,
  "DCM-009": false,
  "DCM-010": false,
  "DCM-011": false,
  "DCM-012": false,
  "DCM-013": false,
  "DCM-014": false,
  "DCM-015": false,
  "DCM-016": false,
  "DCM-017": false,
  "DCM-018": false,
  "DCM-019": false
}

## 15. Downstream role matrix

{
  "DCM-001": {
    "trustreport_restricted": true,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-004": {
    "trustreport_restricted": true,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-005-BRB": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-005-KFOLD": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-005-PLACEBO": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-006": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-008": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-002": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "SCM-PLACEBO": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-003": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-007": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-009": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-010": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-011": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-012": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-013": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-014": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-015": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-016": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-017": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-018": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  },
  "DCM-019": {
    "trustreport_restricted": false,
    "production_decisioning": false,
    "live_api": false,
    "scheduler": false
  }
}

## 16. Required warnings and restrictions

{
  "required_warnings": [
    "common_simultaneous_adoption_only",
    "no_trustreport_authorization",
    "noisy_world_coverage_caveat",
    "parallel_trends_violation_excluded",
    "population_ate_blocked",
    "prefit_warning_required",
    "staggered_pooled_blocked",
    "support_gated",
    "type_i_caveat",
    "unsupported_worlds_excluded"
  ],
  "required_restrictions": [
    "common_simultaneous_adoption_only",
    "no_trustreport_authorization",
    "parallel_trends_violation_excluded",
    "population_ate_blocked",
    "prefit_warning_required",
    "staggered_pooled_blocked",
    "support_gated"
  ]
}

## 17. Global TrustReport authorization boundary

{
  "trust_report_platform_authorized": false,
  "live_api_authorized": false,
  "scheduler_authorized": false
}

## 18. Live API and scheduler boundary

{
  "live_api": {
    "live_api_authorized": false,
    "rationale": "Promotion gate artifact approves row-level restricted research roles only."
  },
  "scheduler": {
    "scheduler_authorized": false,
    "rationale": "No scheduler or production automation authorized."
  }
}

## 19. Open investigation check

{
  "open_investigations": [
    "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
    "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001"
  ],
  "deferred_investigations": [
    "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
    "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001"
  ],
  "blocking_for_promotion": [
    "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
    "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001"
  ]
}

## 20. Governance verdict

`trustreport_downstream_restricted_row_promotion_approved`

## Residual Issues and Handoff

**Resolved in this artifact:** none

**New investigations opened:** none

**Existing investigations updated:** none

**Deferred issues:**
- INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001
- INV-MULTICELL-MULTIPLICITY-CALIBRATION-001

**Explicit exclusions:** none

**Revisit trigger:** After TRUSTREPORT_RESTRICTED_ROW_CONTRACTS_001 or integration dry-run

**Required decision checkpoint:** TRUSTREPORT_DOWNSTREAM_PROMOTION_001

**Next artifact:** TRUSTREPORT_INTEGRATION_DRY_RUN_001


## Residual Issues and Handoff

Next artifact: `TRUSTREPORT_INTEGRATION_DRY_RUN_001`
