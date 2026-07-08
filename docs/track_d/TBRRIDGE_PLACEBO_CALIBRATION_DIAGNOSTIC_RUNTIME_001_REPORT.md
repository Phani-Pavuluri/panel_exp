# TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001` |
| **Artifact type** | `tbrridge_placebo_calibration_diagnostic_runtime` |
| **Status** | `completed` |
| **Scope** | `tbrridge_placebo_calibration_diagnostic_runtime_implemented_no_placebo_inference_or_uncertainty` |
| **Base commit** | `c1a5137` (Define TBRRidge placebo calibration diagnostic contract) |
| **Final verdict** | `tbrridge_placebo_calibration_diagnostic_runtime_implemented_no_placebo_inference_or_uncertainty` |

**Depends on:** `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001` · `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001` · `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001`

---

## 2. Source files inspected

- `panel_exp/validation/tbrridge_placebo_calibration_diagnostic_contract_001.py`
- `docs/track_d/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001_REPORT.md`
- `panel_exp/validation/tbrridge_kfold_leakage_diagnostic_runtime_001.py`
- `panel_exp/validation/tbrridge_kfold_leakage_diagnostic_contract_001.py`
- `docs/track_d/TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001.md`

---

## 3. Runtime purpose

Implements a narrow, manifest-driven runtime that emits a structured placebo calibration diagnostic packet for `TBRRidge_Placebo`.

**Input:** placebo assignment, null-period, geometry, contamination, rank/tail, directionality, outlier, regularization, and optional KFold leakage diagnostic evidence.

**Output:** placebo calibration status, detected placebo risks, blockers, missing evidence, allowed/prohibited surfaces, failure packet, and deterministic provenance.

**Does not:** compute placebo p-values, significance, CIs, coverage, uncertainty, treatment effects, lift, ROI, promotion, catalog unblock, or production authorization.

---

## 4. Input / output packet

**Public API:** `generate_tbrridge_placebo_calibration_diagnostic(input_data, config=None)`

**Aliases:** `evaluate_tbrridge_placebo_calibration` · `build_tbrridge_placebo_calibration_packet`

Supports dict, dataclass-like, and list inputs. List input returns multiple independent diagnostics without ranking.

**Output packet fields:** `request_id`, `diagnostic_id`, `diagnostic_status`, `method_id`, `instrument_id`, `estimator_family`, `inference_family`, `placebo_scheme`, `null_period_definition`, `placebo_count`, `placebo_risks_evaluated`, `detected_placebo_risks`, `required_evidence`, `missing_evidence`, `blockers`, `restrictions`, `allowed_surfaces`, `prohibited_surfaces`, `failure_packet`, `lineage_manifest`, `provenance_hash`, `policy_version`, `authorization_boundary_report`, `warnings`.

---

## 5. Null construction validation behavior

The runtime inspects `null_period_definition` and blocks with `PLACEBO_CALIBRATION_BLOCKED_BY_INVALID_NULL_CONSTRUCTION` when invalid null periods or invalid placebo construction are declared. Missing placebo assignment or null-period evidence blocks with the contract missing-manifest status before any further diagnostic interpretation.

---

## 6. Placebo contamination behavior

`placebo_contamination_report` drives detection of `PSEUDO_TREATED_CONTAMINATION` and `PLACEBO_DONOR_OVERLAP`. Either condition blocks with `PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION`. The runtime treats contamination as a hard stop for placebo interpretation, not as a score or adjusted inference signal.

---

## 7. Rank / tail / directional instability behavior

`placebo_rank_tail_report` flags `PLACEBO_TAIL_INSTABILITY` and `PLACEBO_RANK_INSTABILITY`. `placebo_directionality_report` flags `DIRECTIONAL_SIGN_INSTABILITY`. Any of these produce `PLACEBO_CALIBRATION_BLOCKED_BY_DIRECTIONAL_INSTABILITY`, with normalized failure codes distinguishing tail, rank, and directional-sign instability.

---

## 8. Outlier / regularization risk behavior

`placebo_outlier_influence_report` blocks with `PLACEBO_CALIBRATION_BLOCKED_BY_OUTLIER_INFLUENCE`. `regularization_sensitivity_report`, `pre_period_fit_overconfidence`, `placebo_metric_mismatch`, and unbalanced placebo geometry remain diagnostic-only restrictions rather than inference surfaces. These produce warnings and restricted-status packets, not numerical confidence outputs.

---

## 9. KFold leakage dependency behavior

When a `kfold_leakage_diagnostic_report` is provided and remains blocked, the runtime propagates that state as a blocker/restriction on placebo interpretation. A blocked KFold dependency upgrades an otherwise clean placebo diagnostic to `PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS`, preserving the diagnostic-only boundary instead of silently ignoring upstream leakage risk.

---

## 10. Allowed / prohibited surfaces

**Allowed:** `DIAGNOSTIC_ONLY` · `RESEARCH_OR_REVIEW_ONLY` · `PLACEBO_CALIBRATION_SUMMARY` · `FALSE_CONFIDENCE_RISK_SUMMARY` · `PLACEBO_GEOMETRY_DIAGNOSTIC`

**Prohibited:** `PLACEBO_P_VALUE_CLAIM` · `STATISTICAL_SIGNIFICANCE_CLAIM` · `CONFIDENCE_INTERVAL_CLAIM` · `COVERAGE_CLAIM` · `CAUSAL_LIFT_CLAIM` · `ROI_CLAIM` · `PRODUCTION_READOUT` · `METHOD_PROMOTION_NOTICE`

Requesting a prohibited surface yields `PLACEBO_SIGNIFICANCE_SURFACE_BLOCKED`.

---

## 11. Failure packet semantics

Runtime normalizes failure semantics to the requested codes:

- `MISSING_PLACEBO_ASSIGNMENT_MANIFEST`
- `MISSING_NULL_PERIOD_DEFINITION`
- `INVALID_NULL_CONSTRUCTION`
- `INSUFFICIENT_PLACEBO_COUNT`
- `PLACEBO_CONTAMINATION_DETECTED`
- `PLACEBO_GEOMETRY_UNBALANCED`
- `PLACEBO_TAIL_INSTABILITY_DETECTED`
- `PLACEBO_RANK_INSTABILITY_DETECTED`
- `DIRECTIONAL_SIGN_INSTABILITY_DETECTED`
- `OUTLIER_PLACEBO_INFLUENCE_DETECTED`
- `PLACEBO_SIGNIFICANCE_SURFACE_BLOCKED`

---

## 12. Authorization boundary

| Flag | Value |
|------|-------|
| `placebo_calibration_runtime_implemented` | true |
| `placebo_calibration_diagnostic_packet_generated` | true |
| `placebo_inference_surfaces_blocked` | true |
| `placebo_inference_implemented` | false |
| `uncertainty_computed` | false |
| `coverage_computed` | false |
| `method_promoted` | false |
| `production_readout_authorized` | false |

---

## 13. Tests added

- `tests/validation/test_tbrridge_placebo_calibration_diagnostic_runtime_001.py`
- `tests/governance/test_tbrridge_placebo_calibration_diagnostic_runtime_001_governance.py`

---

## 14. Validation results

Runtime tests cover missing evidence, invalid null construction, insufficient count, contamination, donor overlap, geometry imbalance, rank/tail/directional instability, outlier influence, pre-period fit overconfidence, regularization masking, metric mismatch, KFold dependency propagation, deterministic IDs, blocked inference surfaces, and forbidden flags.

---

## 15. Known limitations

- The runtime is manifest/report driven and does not recompute placebo statistics.
- It does not synthesize or validate null DGPs beyond declared diagnostic evidence.
- It does not integrate with estimator execution, promotion review, or TrustReport authorization.

---

## 16. Recommended next artifact

**Primary:** `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001`

**Alternative:** `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`
