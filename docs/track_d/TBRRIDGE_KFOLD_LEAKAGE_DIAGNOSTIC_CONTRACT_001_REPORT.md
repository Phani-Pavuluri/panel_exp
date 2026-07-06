# TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001` |
| **Artifact type** | `tbrridge_kfold_leakage_diagnostic_contract` |
| **Status** | `completed` |
| **Scope** | `tbrridge_kfold_leakage_diagnostic_contract_defined_no_runtime_or_inference` |
| **Base commit** | `9059e3e` (Add TBRRidge false confidence diagnostic audit) |
| **Final verdict** | `tbrridge_kfold_leakage_diagnostic_contract_defined_no_runtime_or_inference` |

**Depends on:** `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001` · `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001` · `MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001`

---

## 2. Source files inspected

- `docs/track_d/TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001.md`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`
- `docs/GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md`
- `docs/TRACK_B_CALIBRATION_SIGNAL_001.md`
- `docs/TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md`
- `panel_exp/validation/recovery_runner.py`
- `panel_exp/validation/multicell_experiment_family_contrast_runtime_001.py`
- `tests/governance/test_f_inf_002_tbrridge_interface.py`

---

## 3. Problem statement

`TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001` identified **TBRRidge + KFold** as the dominant false-confidence surface:

- Readiness: `TBRRIDGE_UNCERTAINTY_EVIDENCE_BUILDING`
- Blocker: `kfold_multi_treated_unsupported_run001`
- Evidence: Run 001 100% failure
- Primary mechanism: geometry + fold/temporal leakage

KFold can only support future uncertainty review if fold construction is **proven non-leaky**, compatible with treated/control geometry, temporally valid, and not silently converting predictive stability into causal confidence.

**Core principle:** Contract only — no KFold inference, estimator changes, or catalog unblock.

---

## 4. Relationship to TBRRidge false-confidence audit

This contract is the **smallest named follow-on** from `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001`. It defines diagnostic statuses, leakage taxonomy, required evidence, and failure semantics before `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001`.

---

## 5. Diagnostic statuses

| Status | Meaning |
|--------|---------|
| `KFOLD_LEAKAGE_NOT_EVALUATED` | No diagnostic evidence submitted |
| `KFOLD_LEAKAGE_DIAGNOSTIC_READY` | Leakage diagnostic complete; diagnostic surfaces only |
| `KFOLD_LEAKAGE_DIAGNOSTIC_READY_WITH_RESTRICTIONS` | Diagnostic summary allowed with caveats |
| `KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY` | Multi-treated or unsupported geometry |
| `KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE` | Pre/post or future-information leakage |
| `KFOLD_LEAKAGE_BLOCKED_BY_FOLD_OVERLAP` | Fold overlap or shared-control fold leakage |
| `KFOLD_LEAKAGE_BLOCKED_BY_TREATED_CONTROL_CONTAMINATION` | Treated/control contamination |
| `KFOLD_LEAKAGE_BLOCKED_BY_SMALL_SAMPLE_GEOMETRY` | Fold degeneracy |
| `KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE` | Required manifests/reports missing |
| `KFOLD_LEAKAGE_REQUIRES_METHOD_REVIEW` | Uncertainty surface requested; blocked |

**No status grants production approval or KFold uncertainty authorization.**

---

## 6. Leakage type taxonomy

`TEMPORAL_LEAKAGE` · `POST_PERIOD_LEAKAGE` · `PRE_POST_BOUNDARY_LEAKAGE` · `TREATED_CONTROL_CONTAMINATION` · `UNIT_OVERLAP_LEAKAGE` · `SHARED_CONTROL_FOLD_LEAKAGE` · `MULTI_TREATED_GEOMETRY_UNSUPPORTED` · `FOLD_ASSIGNMENT_INSTABILITY` · `SMALL_SAMPLE_FOLD_DEGENERACY` · `FEATURE_CONSTRUCTION_LEAKAGE` · `HYPERPARAMETER_SELECTION_LEAKAGE` · `OUTLIER_INFLUENCE_LEAKAGE`

---

## 7. Required evidence

`fold_assignment_manifest` · `treated_unit_manifest` · `control_unit_manifest` · `pre_period_window` · `post_period_window` · `feature_construction_manifest` · `hyperparameter_selection_manifest` · `geometry_support_report` · `temporal_split_report` · `fold_overlap_report` · `treated_control_separation_report` · `sample_size_by_fold` · `shared_control_family_report` (when applicable) · `multicell_family_contrast_packet` (when applicable) · `lineage_provenance_manifest`

---

## 8. Unsupported geometry rules

- Multi-treated geometry requires explicit policy or block (`kfold_multi_treated_unsupported_run001` lineage).
- Shared-control folds require `shared_control_family_report`.
- Multicell KFold requires `multicell_family_contrast_packet` from contrast runtime.
- Single-treated default only after geometry support passes.

---

## 9. Temporal / fold leakage rules

**Temporal:**
- Post-period features must not enter pre-period folds.
- Pre/post boundary declared in `temporal_split_report`.
- Hyperparameter selection must not use post-period outcomes.

**Fold overlap:**
- Treated/control separation reported in `treated_control_separation_report`.
- Unit overlap across folds reported in `fold_overlap_report`.
- Fold assignment instability blocks uncertainty surfaces.

---

## 10. Allowed / prohibited surfaces

**Allowed:** `DIAGNOSTIC_ONLY` · `RESEARCH_OR_REVIEW_ONLY` · `FOLD_GEOMETRY_DIAGNOSTIC` · `LEAKAGE_RISK_SUMMARY`

**Prohibited:** `KFOLD_UNCERTAINTY_CLAIM` · `CONFIDENCE_INTERVAL_CLAIM` · `STATISTICAL_SIGNIFICANCE_CLAIM` · `COVERAGE_CLAIM` · `CAUSAL_LIFT_CLAIM` · `PRODUCTION_READOUT` · `METHOD_PROMOTION_NOTICE`

---

## 11. Failure packet semantics

Fields: `failure_code` · `failure_reason` · `detected_leakage_types` · `unsupported_geometries` · `missing_evidence` · `required_remediation` · `retry_category`

Codes include: `MISSING_FOLD_ASSIGNMENT_MANIFEST` · `TEMPORAL_LEAKAGE_DETECTED` · `MULTI_TREATED_GEOMETRY_UNSUPPORTED` · `KFOLD_UNCERTAINTY_SURFACE_BLOCKED` · etc.

---

## 12. Future runtime acceptance criteria

- Blocks without fold assignment manifest or temporal split report
- Blocks unsupported multi-treated geometry
- Detects pre/post boundary leakage, treated/control contamination, fold overlap
- Blocks small-sample fold degeneracy
- Flags feature/hyperparameter leakage risks
- Permits diagnostic-only leakage summary when evidence present
- Blocks KFold uncertainty/CI/significance/coverage surfaces
- Deterministic `diagnostic_id` / `provenance_hash`
- All forbidden computation/authorization flags remain false

---

## 13. Authorization boundary

| Flag | Value |
|------|-------|
| `kfold_leakage_diagnostic_contract_defined` | true |
| `kfold_leakage_runtime_implemented` | false |
| `kfold_inference_implemented` | false |
| `method_promoted` | false |
| `production_catalog_unblocked` | false |

---

## 14. Validation results

- Contract module validates taxonomies and gate scenarios
- Governance tests assert registry reference and forbidden flags
- Safety grep: no forbidden `true` flags

---

## 15. Known limitations

- Contract-only; does not execute fold assignment analysis.
- Does not remediate `kfold_multi_treated_unsupported_run001` — documents requirements only.
- BRB inverted bounds remain separate blocker.

---

## 16. Recommended next artifact

**`TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001`**

**Alternative:** `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`
