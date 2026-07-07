# TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001` |
| **Artifact type** | `tbrridge_placebo_calibration_diagnostic_contract` |
| **Status** | `completed` |
| **Scope** | `tbrridge_placebo_calibration_diagnostic_contract_defined_no_runtime_or_inference` |
| **Base commit** | `4e84702` (Add TBRRidge KFold leakage diagnostic runtime) |
| **Final verdict** | `tbrridge_placebo_calibration_diagnostic_contract_defined_no_runtime_or_inference` |

**Depends on:** `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001` · `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001` · `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001.md`
- `docs/track_d/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001_REPORT.md`
- `docs/track_d/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001_REPORT.md`
- `panel_exp/validation/tbrridge_kfold_leakage_diagnostic_contract_001.py`
- `panel_exp/validation/tbrridge_kfold_leakage_diagnostic_runtime_001.py`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`

---

## 3. Problem statement

`TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001` identified **TBRRidge + Placebo** as an evidence-building diagnostic path with `PLACEBO_SEMANTICS_UNGOVERNED` blocker category. Placebo diagnostics may detect false confidence, but must not be treated as governed inference, significance, or production lift evidence until placebo construction, null semantics, tail/rank behavior, and instability risks are governed.

**Core principle:** Contract only — no placebo runtime, placebo computation, estimator changes, or catalog unblock.

---

## 4. Relationship to false-confidence audit

TBRRidge Placebo remains **STAGE_2 diagnostic-only** per the evidence ladder. This contract defines diagnostic statuses, placebo risk taxonomy, required evidence, and failure semantics before `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001`.

---

## 5. Diagnostic statuses

| Status | Meaning |
|--------|---------|
| `PLACEBO_CALIBRATION_NOT_EVALUATED` | No placebo diagnostic evidence submitted |
| `PLACEBO_CALIBRATION_DIAGNOSTIC_READY` | Placebo calibration diagnostic complete; diagnostic surfaces only |
| `PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS` | Diagnostic summary allowed with caveats |
| `PLACEBO_CALIBRATION_BLOCKED_BY_MISSING_PLACEBO_MANIFEST` | Required placebo manifests/reports missing |
| `PLACEBO_CALIBRATION_BLOCKED_BY_INVALID_NULL_CONSTRUCTION` | Invalid null period or construction |
| `PLACEBO_CALIBRATION_BLOCKED_BY_INSUFFICIENT_PLACEBOS` | Insufficient placebo count |
| `PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION` | Pseudo-treated or donor contamination |
| `PLACEBO_CALIBRATION_BLOCKED_BY_DIRECTIONAL_INSTABILITY` | Rank/tail/sign instability |
| `PLACEBO_CALIBRATION_BLOCKED_BY_OUTLIER_INFLUENCE` | Outlier-driven placebo influence |
| `PLACEBO_CALIBRATION_REQUIRES_METHOD_REVIEW` | Placebo inference surface requested; blocked |

**No status grants production approval or placebo p-value authorization.**

---

## 6. Placebo risk taxonomy

`INVALID_NULL_PERIOD` · `PSEUDO_TREATED_CONTAMINATION` · `PLACEBO_DONOR_OVERLAP` · `INSUFFICIENT_PLACEBO_COUNT` · `UNBALANCED_PLACEBO_GEOMETRY` · `PLACEBO_TAIL_INSTABILITY` · `PLACEBO_RANK_INSTABILITY` · `DIRECTIONAL_SIGN_INSTABILITY` · `OUTLIER_PLACEBO_INFLUENCE` · `PRE_PERIOD_FIT_OVERCONFIDENCE` · `REGULARIZATION_MASKED_PLACEBO_FAILURE` · `PLACEBO_METRIC_MISMATCH`

---

## 7. Required evidence

`placebo_assignment_manifest` · `pseudo_treated_unit_manifest` · `placebo_control_unit_manifest` · `null_period_definition` · `placebo_window_manifest` · `placebo_metric_manifest` · `placebo_geometry_report` · `placebo_contamination_report` · `placebo_count_report` · `placebo_rank_tail_report` · `placebo_directionality_report` · `placebo_outlier_influence_report` · `regularization_sensitivity_report` · `kfold_leakage_diagnostic_report` (when applicable) · `lineage_provenance_manifest`

---

## 8. Null construction rules

- Null period must be pre-treatment or declared counterfactual.
- Pseudo-treated units must not overlap true treated units.
- Placebo window must not include post-treatment outcome leakage.
- Placebo metric must align with estimand under test.
- Multi-treated placebo requires explicit geometry policy.

---

## 9. Placebo contamination / rank-tail / directional rules

**Contamination:** pseudo-treated must not share donors with true treated controls; donor overlap reported; shared-control placebo families require geometry declaration.

**Rank/tail:** rank distribution reported before inference claims; tail instability blocks p-value surfaces; rank instability blocks significance claims.

**Directional:** sign flips across placebos require review; pre-period fit strength must not substitute for placebo pass.

---

## 10. Allowed / prohibited surfaces

**Allowed:** `DIAGNOSTIC_ONLY` · `RESEARCH_OR_REVIEW_ONLY` · `PLACEBO_CALIBRATION_SUMMARY` · `FALSE_CONFIDENCE_RISK_SUMMARY` · `PLACEBO_GEOMETRY_DIAGNOSTIC`

**Prohibited:** `PLACEBO_P_VALUE_CLAIM` · `STATISTICAL_SIGNIFICANCE_CLAIM` · `CONFIDENCE_INTERVAL_CLAIM` · `COVERAGE_CLAIM` · `CAUSAL_LIFT_CLAIM` · `ROI_CLAIM` · `PRODUCTION_READOUT` · `METHOD_PROMOTION_NOTICE`

---

## 11. Failure packet semantics

Fields: `failure_code` · `failure_reason` · `detected_placebo_risks` · `missing_evidence` · `required_remediation` · `retry_category`

Codes include: `MISSING_PLACEBO_ASSIGNMENT_MANIFEST` · `INVALID_NULL_CONSTRUCTION` · `PLACEBO_CONTAMINATION_DETECTED` · `DIRECTIONAL_INSTABILITY_DETECTED` · `PLACEBO_INFERENCE_SURFACE_BLOCKED` · etc.

---

## 12. Future runtime acceptance criteria

- Blocks without placebo assignment manifest
- Blocks without null period definition
- Blocks invalid null construction
- Blocks insufficient placebo count
- Detects placebo contamination
- Detects directional instability
- Detects outlier placebo influence
- Flags pre-period fit overconfidence and regularization-masked failure risks
- Permits diagnostic-only placebo summary when evidence is present
- Blocks placebo p-value/CI/significance/coverage surfaces
- Deterministic diagnostic_id/provenance_hash
- All forbidden computation/authorization flags false

---

## 13. Authorization boundary

| Flag | Value |
|------|-------|
| `placebo_calibration_diagnostic_contract_defined` | true |
| `placebo_risk_taxonomy_defined` | true |
| `placebo_calibration_runtime_implemented` | false |
| `placebo_inference_implemented` | false |
| `p_value_computed` | false |
| `method_promoted` | false |
| `production_readout_authorized` | false |

---

## 14. Validation results

Contract validation and scenario suite pass with `failed_scenarios: []`.

---

## 15. Known limitations

- Manifest schema is contract-oriented; production ingest adapters not implemented.
- Does not compute placebo statistics or ranks.
- Does not integrate with estimator execution.

---

## 16. Recommended next artifact

**Primary:** `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001`

**Alternative:** `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`
