# TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001` |
| **Artifact type** | `tbrridge_kfold_leakage_diagnostic_runtime` |
| **Status** | `completed` |
| **Scope** | `tbrridge_kfold_leakage_diagnostic_runtime_implemented_no_kfold_inference_or_uncertainty` |
| **Base commit** | `2ba3d8d` (Define TBRRidge KFold leakage diagnostic contract) |
| **Final verdict** | `tbrridge_kfold_leakage_diagnostic_runtime_implemented_no_kfold_inference_or_uncertainty` |

**Depends on:** `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001` · `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001`

---

## 2. Source files inspected

- `panel_exp/validation/tbrridge_kfold_leakage_diagnostic_contract_001.py`
- `docs/track_d/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001_REPORT.md`
- `docs/track_d/TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001.md`
- `panel_exp/validation/multicell_experiment_family_contrast_runtime_001.py`
- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`

---

## 3. Runtime purpose

Implements a **narrow diagnostic runtime** that consumes fold/geometry/temporal manifests and emits a structured KFold leakage diagnostic packet for `TBRRidge_Kfold`.

**Input:** fold assignment, treated/control, temporal, geometry, and separation manifests/reports.

**Output:** diagnostic status, detected leakage types, blockers, missing evidence, allowed/prohibited surfaces, failure packet.

**Does not:** run KFold inference, estimate lift, compute uncertainty, coverage, p-values, CIs, promote TBRRidge, unblock catalog, or authorize production readouts.

---

## 4. Input / output packet

**Public API:** `generate_tbrridge_kfold_leakage_diagnostic(input_data, config=None)`

**Aliases:** `evaluate_tbrridge_kfold_leakage` · `build_tbrridge_kfold_leakage_packet`

**Input fields:** `request_id`, `method_id`, `instrument_id`, `estimator_family`, `inference_family`, `fold_scheme`, manifest/report fields per contract, optional `requested_surface`, `lineage_manifest`.

**Output packet fields:** `request_id`, `diagnostic_id`, `diagnostic_status`, method/instrument metadata, `treated_geometry`, `control_geometry`, `leakage_types_evaluated`, `detected_leakage_types`, `unsupported_geometries`, `required_evidence`, `missing_evidence`, `blockers`, `restrictions`, `allowed_surfaces`, `prohibited_surfaces`, `failure_packet`, `lineage_manifest`, `provenance_hash`, `policy_version`, `authorization_boundary_report`, `warnings`.

Supports dict, dataclass-like, and list inputs (list returns multiple independent diagnostics without ranking).

---

## 5. Leakage detection behavior

Runtime scans manifest/report content and flags:

- `TEMPORAL_LEAKAGE` / `POST_PERIOD_LEAKAGE` / `PRE_POST_BOUNDARY_LEAKAGE` from `temporal_split_report`
- `TREATED_CONTROL_CONTAMINATION` from `treated_control_separation_report`
- `UNIT_OVERLAP_LEAKAGE` / `FOLD_ASSIGNMENT_INSTABILITY` from `fold_overlap_report`
- `SHARED_CONTROL_FOLD_LEAKAGE` from `shared_control_family_report`
- `MULTI_TREATED_GEOMETRY_UNSUPPORTED` from geometry manifests
- `SMALL_SAMPLE_FOLD_DEGENERACY` from `sample_size_by_fold`
- `FEATURE_CONSTRUCTION_LEAKAGE` / `HYPERPARAMETER_SELECTION_LEAKAGE` as risk flags
- `OUTLIER_INFLUENCE_LEAKAGE` when outlier evidence is present

Evaluation delegates status resolution to `evaluate_kfold_leakage_diagnostic()` from the contract.

---

## 6. Unsupported geometry behavior

Multi-treated geometry without explicit policy blocks with `KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY` and `MULTI_TREATED_GEOMETRY_UNSUPPORTED`. Shared-control contexts require `shared_control_family_report`; multicell contexts may require `multicell_family_contrast_packet`.

---

## 7. Temporal / fold overlap behavior

Missing `temporal_split_report` blocks before leakage evaluation. Temporal leakage types block uncertainty surfaces. Fold overlap and assignment instability map to `KFOLD_LEAKAGE_BLOCKED_BY_FOLD_OVERLAP`.

---

## 8. Allowed / prohibited surfaces

**Allowed:** `DIAGNOSTIC_ONLY` · `RESEARCH_OR_REVIEW_ONLY` · `FOLD_GEOMETRY_DIAGNOSTIC` · `LEAKAGE_RISK_SUMMARY`

**Prohibited:** `KFOLD_UNCERTAINTY_CLAIM` · `CONFIDENCE_INTERVAL_CLAIM` · `STATISTICAL_SIGNIFICANCE_CLAIM` · `COVERAGE_CLAIM` · `CAUSAL_LIFT_CLAIM` · `PRODUCTION_READOUT` · `METHOD_PROMOTION_NOTICE`

Requesting a prohibited surface yields `KFOLD_UNCERTAINTY_SURFACE_BLOCKED`.

---

## 9. Failure packet semantics

Failure codes from contract: `MISSING_FOLD_ASSIGNMENT_MANIFEST`, `MISSING_TEMPORAL_SPLIT_REPORT`, `MISSING_GEOMETRY_SUPPORT_REPORT`, `TEMPORAL_LEAKAGE_DETECTED`, `TREATED_CONTROL_CONTAMINATION_DETECTED`, `FOLD_OVERLAP_DETECTED`, `MULTI_TREATED_GEOMETRY_UNSUPPORTED`, `SMALL_SAMPLE_FOLD_DEGENERACY`, `FEATURE_CONSTRUCTION_LEAKAGE_RISK`, `HYPERPARAMETER_SELECTION_LEAKAGE_RISK`, `KFOLD_UNCERTAINTY_SURFACE_BLOCKED`.

---

## 10. Authorization boundary

| Flag | Value |
|------|-------|
| `kfold_leakage_runtime_implemented` | true |
| `kfold_leakage_diagnostic_packet_generated` | true |
| `kfold_uncertainty_surface_blocked` | true |
| `kfold_inference_implemented` | false |
| `uncertainty_computed` | false |
| `coverage_computed` | false |
| `method_promoted` | false |
| `production_readout_authorized` | false |

---

## 11. Tests added

- `tests/validation/test_tbrridge_kfold_leakage_diagnostic_runtime_001.py`
- `tests/governance/test_tbrridge_kfold_leakage_diagnostic_runtime_001_governance.py`

---

## 12. Validation results

Contract tests remain green. Runtime tests cover manifest blocking, leakage detection, diagnostic-ready path, prohibited surfaces, deterministic IDs, and forbidden flags.

---

## 13. Known limitations

- Manifest schema is contract-oriented; production ingest adapters are not implemented.
- Leakage detection is manifest-flag driven, not statistical recomputation of folds.
- Does not integrate with estimator execution or TrustReport generation.

---

## 14. Recommended next artifact

**Primary:** `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001`

**Alternative:** `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`
