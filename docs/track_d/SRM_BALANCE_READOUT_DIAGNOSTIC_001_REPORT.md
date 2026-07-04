# SRM_BALANCE_READOUT_DIAGNOSTIC_001 Report

## 1. Artifact ID, status, base commit, and final verdict

| Field | Value |
|-------|-------|
| **Artifact ID** | `SRM_BALANCE_READOUT_DIAGNOSTIC_001` |
| **Artifact type** | `srm_balance_readout_diagnostic_runtime` |
| **Artifact version** | `1.0.0` |
| **Status** | `completed` |
| **Scope** | `srm_balance_readout_diagnostic_implemented_no_inference_or_claim_authorization` |
| **Base commit** | `289bafb` (Add governed randomization runtime) |
| **Final verdict** | `srm_balance_readout_diagnostic_implemented_no_inference_or_claim_authorization` |

---

## 2. Source files inspected

- `panel_exp/validation/governed_randomization_runtime_001.py`
- `panel_exp/validation/assignment_panel_integrity_runtime_001.py`
- `panel_exp/validation/statistical_promotion_thresholds_001.py`
- `panel_exp/validation/readout_diagnostics_sensitivity_runtime_001.py`
- `panel_exp/validation/readout_diagnostics_sensitivity_contract_001.py`
- `panel_exp/validation/readout_did_diagnostics_002.py`
- `panel_exp/validation/readout_plan_runtime_001.py`
- `panel_exp/validation/estimator_inference_execution_runtime_001.py`
- `panel_exp/validation/method_suitability_runtime_001.py`
- Audit and governance docs

---

## 3. Audit finding being addressed

Expanded adversarial audit (`AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001`) identified that a randomized assignment artifact alone is insufficient before readout or claim review. The realized analysis panel must be checked for sample-ratio mismatch, missing units, treatment/control imbalance, and covariate/baseline drift.

---

## 4. Problem statement: realized assignment/readout imbalance risk

Without SRM and balance diagnostics, downstream review could proceed when realized panel counts diverge from assignment expectations, when assigned units are absent from the analysis panel, when unassigned units appear, or when covariates and pre-period outcomes are imbalanced across treatment arms.

---

## 5. Runtime purpose

`evaluate_srm_balance_readout_diagnostic` emits descriptive diagnostic evidence for readout readiness. It validates assignment-vs-panel count alignment, missing/extra units, treatment/control presence, covariate standardized mean differences, and optional pre-period outcome balance. It does not estimate effects, run inference, compute p-values or confidence intervals, authorize claims, or loosen production blocklists.

---

## 6. Input contract

Accepts dict, dataclass-like, or list input (multiple requests, no ranking).

Supported fields include: `request_id`, `assignment_artifact`, `assignment_artifact_id`, `assignment_hash`, `unit_allocations`, `analysis_panel`, `panel_records`, field-name overrides, `expected_cell_counts`, `expected_treatment_counts`, `covariate_fields`, `baseline_fields`, `pre_period_indicator_field`, `pre_period_values`, threshold overrides, `require_assignment_panel_integrity_pass`, `assignment_panel_integrity_report`, and `production_context`.

Panel formats: `list[dict]`, dict with `records` / `panel_records`, or dataclass-like input.

---

## 7. Status taxonomy

- `SRM_BALANCE_DIAGNOSTIC_PASSED`
- `SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS`
- `SRM_BALANCE_DIAGNOSTIC_FAILED`
- `SRM_BALANCE_DIAGNOSTIC_BLOCKED`
- `SRM_BALANCE_DIAGNOSTIC_INCONCLUSIVE`
- `SRM_BALANCE_DIAGNOSTIC_NOT_EVALUATED`

Component statuses: `SRM_CHECK_PASSED`, `SRM_CHECK_FAILED`, `SRM_CHECK_INCONCLUSIVE`, `BALANCE_CHECK_PASSED`, `BALANCE_CHECK_FAILED`, `BALANCE_CHECK_INCONCLUSIVE`.

---

## 8. Issue taxonomy

`ASSIGNMENT_ARTIFACT_MISSING`, `UNIT_ALLOCATIONS_MISSING`, `ANALYSIS_PANEL_MISSING`, `ASSIGNMENT_PANEL_INTEGRITY_FAILED`, `EXPECTED_COUNTS_MISSING`, `REALIZED_CELL_MISSING`, `TREATED_OR_CONTROL_REALIZED_MISSING`, `SAMPLE_RATIO_MISMATCH`, `MISSING_ASSIGNED_UNITS`, `EXTRA_PANEL_UNITS`, `MINIMUM_CELL_COUNT_FAILED`, `COVARIATE_FIELD_MISSING`, `COVARIATE_NON_NUMERIC`, `COVARIATE_BALANCE_FAILED`, `BASELINE_OUTCOME_BALANCE_FAILED`, `NONFINITE_BALANCE_METRIC`.

---

## 9. Retry categories

`FIX_ASSIGNMENT_ARTIFACT`, `FIX_PANEL_DATA_CONTRACT`, `FIX_ASSIGNMENT_PANEL_JOIN`, `RECONCILE_REALIZED_PANEL`, `RERUN_GOVERNED_RANDOMIZATION`, `RERUN_ASSIGNMENT_PANEL_INTEGRITY`, `ADD_BASELINE_COVARIATES`, `ADD_PRE_PERIOD_OUTCOME`, `REDESIGN_EXPERIMENT_STRUCTURE`, `KEEP_RESEARCH_ONLY`, `BLOCK_CLAIM_REVIEW`.

---

## 10. SRM diagnostic logic

Expected cell shares are derived from assignment allocations or supplied `expected_cell_counts`. Realized counts are computed from unique panel units. For each cell:

- `expected_share = expected_count / total_expected`
- `realized_share = realized_count / total_realized`
- `absolute_share_deviation = abs(realized_share - expected_share)`

`max_sample_ratio_deviation` is the maximum absolute share deviation. Threshold default: 0.05. No chi-square tests; count-ratio diagnostics only.

---

## 11. Balance diagnostic logic

Missing assigned units and extra panel units are computed by set difference between allocation unit IDs and panel unit IDs. Rates are compared against production (0.0) or research (0.05) thresholds. Minimum cell count is enforced per expected cell.

---

## 12. Covariate/baseline SMD policy

Standardized mean difference: `(mean_treatment - mean_control) / pooled_standard_deviation`.

- Zero pooled SD with equal means → SMD = 0
- Zero pooled SD with unequal means → non-finite metric / failed balance diagnostic
- Warning threshold: 0.25 SMD; blocking threshold: 0.50 SMD (config-overridable)
- Non-numeric covariates reported as issues, not silently ignored
- Pre-period outcome balance computed when `pre_period_values` or `pre_period_indicator_field` supplied

No p-values. No effect estimates.

---

## 13. Assignment-panel integrity dependency

When `require_assignment_panel_integrity_pass` is true and an integrity report is supplied with failed/blocked status, SRM/balance diagnostic blocks without treating balance as valid.

---

## 14. Diagnostics/sensitivity runtime integration

Integrated into `readout_diagnostics_sensitivity_runtime_001.py` via `_maybe_compute_srm_balance_diagnostic` when `enable_srm_balance_readout_diagnostic=True` (default). Handles requirement types: `SRM_DIAGNOSTIC`, `SAMPLE_RATIO_MISMATCH_DIAGNOSTIC`, `BALANCE_DIAGNOSTIC`, `COVARIATE_BALANCE_DIAGNOSTIC`, `BASELINE_BALANCE_DIAGNOSTIC`, `READOUT_BALANCE_DIAGNOSTIC`.

---

## 15. Readout plan integration

When `add_srm_balance_readout_prerequisites=True` (default) and assignment is randomized (`RANDOMIZED_ASSIGNMENT`, `GOVERNED_RANDOMIZATION`, or `RERANDOMIZED_ASSIGNMENT`), readout plan appends SRM/balance diagnostic prerequisites and adds `srm_balance_readout_diagnostic_required` to execution prerequisites. Planning does not execute diagnostics.

---

## 16. Research-vs-production boundary

Production context applies stricter missing/extra unit rate thresholds (0.0) and blocks on failed SRM and balance by default. Research context may downgrade some balance failures to warnings when `block_on_failed_balance_research=False`.

---

## 17. Claim / production authorization boundary

This artifact does not authorize causal, incremental-lift, ROI, or production claims. `can_support_claim_review` indicates diagnostic evidence readiness only. `can_support_production_readout` remains false. All authorization flags in `claim_boundary_report` are false.

Positive capability flags: `srm_balance_diagnostic_runtime_implemented`, `sample_ratio_mismatch_diagnostic_evaluated`, `realized_assignment_balance_evaluated`, `covariate_balance_smd_evaluated`, `baseline_outcome_balance_evaluated` (when pre-period data supplied).

---

## 18. Tests added

`tests/validation/test_srm_balance_readout_diagnostic_001.py` covers public API, matching counts, SRM deviation, missing/extra units, treated/control missing, integrity block, covariate SMD pass/fail, zero pooled SD, non-numeric covariates, baseline balance, production vs research blocking, diagnostics runtime integration, readout plan prerequisite, list/dataclass input, deterministic trace, and authorization boundary flags.

Integration regressions added to diagnostics/sensitivity and readout plan test modules.

---

## 19. Validation results

Targeted pytest suites pass. Summary JSON validates. Safety grep confirms no unauthorized capability flags. Capability-positive grep confirms diagnostic runtime flags.

---

## 20. Known limitations

- Descriptive count-ratio SRM only; no inferential SRM tests
- Covariate SMD requires numeric fields on panel records
- Baseline outcome balance requires pre-period indicator or value list
- Does not regenerate assignments or optimize balance
- Production readout authorization remains out of scope

---

## 21. Recommended next artifact

**Primary:** `CLAIM_AUTHORIZATION_RUNTIME_001`

**Alternative:** `TRUSTED_READOUT_REPORT_CONTRACT_001`
