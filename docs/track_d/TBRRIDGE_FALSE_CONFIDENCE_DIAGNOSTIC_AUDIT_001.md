# TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **Artifact ID** | `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001` |
| **Artifact type** | `tbrridge_false_confidence_diagnostic_audit` |
| **Status** | `completed` |
| **Scope** | `tbrridge_false_confidence_risks_audited_no_inference_or_promotion` |
| **Base commit** | `8da577d` (Add multicell experiment family and contrast runtime) |
| **Final verdict** | `tbrridge_false_confidence_risks_audited_no_inference_or_promotion` |

**Depends on:** `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001` · `MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001` · `METHOD_PROMOTION_CANDIDATE_AUDIT_001`

---

## 2. Source files inspected

- `docs/track_d/SOPHISTICATED_METHOD_EVIDENCE_LADDER_001.md`
- `docs/track_d/METHOD_PROMOTION_CANDIDATE_AUDIT_001.md`
- `docs/track_d/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001_REPORT.md`
- `docs/GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md`
- `docs/TRACK_B_CALIBRATION_SIGNAL_001.md`
- `docs/TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md`
- `docs/TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md`
- `docs/PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`
- `panel_exp/validation/recovery_runner.py`
- `panel_exp/validation/nominal_calibration.py`
- `panel_exp/validation/production_catalog_blocklist_001.py`
- `tests/governance/test_f_inf_002_tbrridge_interface.py`
- `tests/test_recovery_estimand_interval_alignment.py`

---

## 3. Problem statement

TBRRidge may be useful for **regularized geo prediction and diagnostics**, but regularization, fold design, placebo behavior, donor/control extrapolation, and pooled summaries can produce **false confidence** — intervals or lift claims that look precise without valid inference backing.

`SOPHISTICATED_METHOD_EVIDENCE_LADDER_001` places TBRRidge BRB/KFold/Placebo at **STAGE_2_DIAGNOSTIC_ONLY**, targeting STAGE_4 only after false-confidence risks are characterized. This audit inventories variants, documents where false confidence arises, and names minimum validation before any TBRRidge path moves toward uncertainty-candidate review.

**Core principle:** Characterize before governed uncertainty or production-facing lift claims. No estimator, inference, or catalog changes in this artifact.

---

## 4. Current TBRRidge posture

| Layer | Posture |
|-------|---------|
| **Evidence ladder** | STAGE_2 diagnostic-only (BRB/KFold/Placebo); STAGE_0 for TBR aggregate/pooled |
| **Promotion audit** | BRB/KFold RANK_0 blocked; Placebo RANK_2 evidence-building |
| **Calibration** | BRB excluded — `brb_bounds_inverted_run001`; KFold excluded — `kfold_multi_treated_unsupported_run001` |
| **Run 001** | SCM null pass; BRB anti-calibration; KFold 100% failure on default `recovery_*` |
| **Production catalog** | BRB/KFold blocked; Placebo diagnostic/restricted; aggregate paths blocked |

---

## 5. Diagnostic readiness taxonomy

| Status | Meaning |
|--------|---------|
| `TBRRIDGE_DIAGNOSTIC_BLOCKED` | Hard inference defects or unresolved estimand; no governed readout |
| `TBRRIDGE_RESEARCH_SANDBOX` | Offline replay/characterization only |
| `TBRRIDGE_DIAGNOSTIC_ONLY` | Falsification/comparator surfaces with explicit no-promotion boundary |
| `TBRRIDGE_POINT_ESTIMATE_REVIEW_ONLY` | Restricted point readout with no uncertainty (not current for BRB/KFold) |
| `TBRRIDGE_UNCERTAINTY_EVIDENCE_BUILDING` | Targeted diagnostic contracts/OC before uncertainty candidacy |
| `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW` | May enter restricted uncertainty review packet — **not production approval** |

**No status grants production approval.**

---

## 6. TBRRidge variant inventory

| Variant | instrument_id | Readiness status | Ladder stage |
|---------|---------------|------------------|--------------|
| TBRRidge + BRB | `TBRRidge_BlockResidualBootstrap` | `TBRRIDGE_DIAGNOSTIC_BLOCKED` | STAGE_2 (blocked inference) |
| TBRRidge + KFold | `TBRRidge_Kfold` | `TBRRIDGE_UNCERTAINTY_EVIDENCE_BUILDING` | STAGE_2 |
| TBRRidge + Placebo | `TBRRidge_Placebo` | `TBRRIDGE_DIAGNOSTIC_ONLY` | STAGE_2 |
| TBR aggregate / pooled | `TBR` aggregate paths | `TBRRIDGE_DIAGNOSTIC_BLOCKED` | STAGE_0 |
| TBRRidge point (research) | `TBRRidge` core | `TBRRIDGE_RESEARCH_SANDBOX` | research lineage |

---

## 7. Per-variant audit

### 7.1 TBRRidge + BRB

| Field | Value |
|-------|-------|
| **Readiness** | `TBRRIDGE_DIAGNOSTIC_BLOCKED` |
| **Allowed surfaces** | Offline BRB replay; bound-orientation diagnostics; research OC |
| **Prohibited surfaces** | Governed CI; catalog unblock; trusted lift/significance; production readout |
| **Evidence present** | `brb_bounds_inverted_run001`; Run 001 anti-calibration; adapter IDs documented; F-INF pooled-CF fix lineage |
| **Evidence missing** | Bounds remediation or retirement decision; coverage on null DGP; regularization sensitivity battery; BRB uncertainty semantics contract |
| **False-confidence risks** | Inverted CI bounds; regularization hiding misspecification; residual autocorrelation; prediction-quality vs inference mismatch |
| **Blocker category** | `INFERENCE_DEFECT` + `COVERAGE_UNVALIDATED` |
| **Required next diagnostic** | BRB bounds remediation audit (after KFold/leakage contract) |
| **Stop/go** | **Stop:** any CI surfacing. **Go:** bounds orientation validated on null DGP |
| **Do not build yet** | Production BRB runtime; catalog unblock |

### 7.2 TBRRidge + KFold

| Field | Value |
|-------|-------|
| **Readiness** | `TBRRIDGE_UNCERTAINTY_EVIDENCE_BUILDING` |
| **Allowed surfaces** | Offline KFold replay; fold-assignment diagnostics; geometry-class documentation |
| **Prohibited surfaces** | Multi-treated KFold CI; production catalog unblock; governed uncertainty |
| **Evidence present** | `kfold_multi_treated_unsupported_run001`; Run 001 100% failure; Track E suitability card; gold fixture restrictions |
| **Evidence missing** | Fold/temporal leakage audit; geometry policy for multi-treated; coverage calibration; lambda stability sweeps |
| **False-confidence risks** | Fold leakage; temporal leakage; multi-treated geometry failure; small donor pools; outlier-week influence |
| **Blocker category** | `GEOMETRY_MISSPECIFICATION` + `FOLD_LEAKAGE` + `COVERAGE_UNVALIDATED` |
| **Required next diagnostic** | `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001` |
| **Stop/go** | **Stop:** KFold CI on multi-treated until geometry + leakage governed. **Go:** leakage contract + explicit geometry class |
| **Do not build yet** | KFold production inference; ensemble promotion |

### 7.3 TBRRidge + Placebo

| Field | Value |
|-------|-------|
| **Readiness** | `TBRRIDGE_DIAGNOSTIC_ONLY` |
| **Allowed surfaces** | Placebo falsification replay (restricted); diagnostic comparator |
| **Prohibited surfaces** | Causal lift from placebo; promotion; production placebo inference on unsupported geometry |
| **Evidence present** | Track B placebo characterization (partial); Phase 15 geometry docs; weaker archive than SCM placebo |
| **Evidence missing** | Governed placebo calibration against null DGP; treated/control geometry gates; pre-period fit vs causal validity separation |
| **False-confidence risks** | Placebo calibration failure; pre-period fit mistaken for causal validity; multi-treated placebo misuse |
| **Blocker category** | `PLACEBO_SEMANTICS_UNGOVERNED` |
| **Required next diagnostic** | `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001` (parallel after leakage) |
| **Stop/go** | **Stop:** placebo as promotion evidence. **Go:** null DGP calibration contract |
| **Do not build yet** | Governed placebo production path |

### 7.4 TBR aggregate / pooled

| Field | Value |
|-------|-------|
| **Readiness** | `TBRRIDGE_DIAGNOSTIC_BLOCKED` |
| **Allowed surfaces** | Research sandbox; heterogeneity documentation |
| **Prohibited surfaces** | Aggregate/pooled lift; global winner claims; production CI |
| **Evidence present** | `BLOCKER_AGGREGATE_MISMATCH`; multicell contrast runtime; sophisticated ladder STAGE_0 |
| **Evidence missing** | Pooled estimand contract; heterogeneity diagnostics; multicell contrast semantics for pooled TBRRidge summaries |
| **False-confidence risks** | Heterogeneity collapse; pooled misuse across shared-control cells; aggregate lift false-confidence |
| **Blocker category** | `ESTIMAND_UNRESOLVED` + `MULTICELL_POOLED_BLOCKED` |
| **Required next diagnostic** | Multicell/pooled estimand contracts (upstream); not TBRRidge-specific unblock |
| **Stop/go** | **Stop:** pooled TBRRidge summaries. **Go:** multicell family + pooling evidence |
| **Do not build yet** | Aggregate production executor |

---

## 8. False-confidence risk matrix

| Risk | BRB | KFold | Placebo | Aggregate/pooled |
|------|-----|-------|---------|------------------|
| Regularization sensitivity | ● | ● | ○ | ○ |
| Lambda/penalty instability | ● | ● | ○ | ○ |
| Fold / temporal leakage | ○ | ● | ○ | ○ |
| Placebo calibration failure | ○ | ○ | ● | ○ |
| Pre-period fit ≠ causal validity | ○ | ○ | ● | ○ |
| Donor/control extrapolation | ● | ● | ● | ● |
| Small donor/control pools | ● | ● | ○ | ● |
| Outlier weeks / influence | ● | ● | ○ | ○ |
| Residual autocorrelation | ● | ● | ○ | ○ |
| Heterogeneity collapse (pooled) | ○ | ○ | ○ | ● |
| KFold/BRB uncertainty ungoverned | ● | ● | ○ | ○ |
| Coverage not established | ● | ● | ○ | ● |
| Prediction quality ≠ valid inference | ● | ● | ○ | ● |
| Multicell / shared-control misuse | ○ | ● | ○ | ● |

● = primary risk for variant · ○ = secondary or N/A

---

## 9. Relationship to multicell contrast runtime

`MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001` gates pooled/global and shared-control comparative surfaces. TBRRidge pooled summaries must not bypass experiment-family classification. Any TBRRidge cross-cell or pooled lift claim requires `SHARED_CONTROL_MULTI_ARM` or `POOLED_AGGREGATE_FAMILY` evidence — currently blocked for aggregate paths.

---

## 10. Relationship to method promotion review

TBRRidge variants remain **ineligible** for method promotion review packets except as **gap evidence**. BRB/KFold are RANK_0; Placebo is evidence-building only. This audit does not change promotion posture.

---

## 11. Recommended next smallest artifact

**`TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001`**

Rationale: Local evidence shows **KFold as the dominant TBRRidge false-confidence surface** — Run 001 100% failure, `kfold_multi_treated_unsupported_run001`, and fold/temporal leakage as the primary mechanism by which regularized prediction masquerades as valid uncertainty. A leakage diagnostic contract is smaller than BRB remediation or full coverage OC and unlocks geometry-class policy required before any KFold uncertainty revival.

**Parallel:** `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001` — falsification baseline for Placebo and null-reference for BRB/KFold calibration.

**Alternative:** `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001`

**Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`

---

## 12. Authorization boundary

| Flag | Value |
|------|-------|
| `tbrridge_inventory_completed` | true |
| `false_confidence_risks_documented` | true |
| `coverage_gap_documented` | true |
| `estimator_implemented` | false |
| `inference_implemented` | false |
| `method_promoted` | false |
| `production_catalog_unblocked` | false |
| `production_authorization_granted` | false |

---

## 13. Validation results

- Summary JSON valid
- Governance tests assert inventory, risks, taxonomy, forbidden flags
- Safety grep: no forbidden `true` promotion/computation flags

---

## 14. Known limitations

- Audit reflects documented repo state at base commit; does not re-run Run 001 OC batteries.
- Does not prescribe specific lambda grids or fold counts — deferred to diagnostic contracts.
- BRB inverted bounds may require retirement rather than remediation; decision deferred to follow-on artifact.
