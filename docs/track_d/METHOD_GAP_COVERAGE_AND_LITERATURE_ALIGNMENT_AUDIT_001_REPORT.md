# METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001

**Artifact ID:** METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001  
**Date:** 2026-06-03  
**Validation:** `panel_exp/validation/method_gap_coverage_literature_alignment_audit_001.py`  
**Summary:** [`archives/METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001_summary.json`](archives/METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001_summary.json)

---

## 1. Artifact ID

`METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001`

---

## 2. Purpose

Audit whether the current roadmap covers the full design/estimator/inference gap space and whether each method path should be kept restricted, repaired, replaced, retired, blocked, kept diagnostic-only, scouted as a newer method, or deferred as research-only.

---

## 3. Current evidence base

Consumes repo evidence after `ROADMAP_INFERENCE_AND_METHOD_GAP_CONTROL_REFOCUS_001`, `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`, and `INFERENCE_SUITABILITY_ROADMAP_MERGE_001` on `main` @ `576debb`. Primary inputs: suitability matrix (50 rows), method-readiness matrix v2, null-calibration harnesses, SCM/AugSynth adapter contract, method-accuracy refocus audit, and governance investigations.

---

## 4. Why the suitability matrix is necessary but not sufficient

**Finding 1:** `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001` maps estimator × design × inference combinations, but it does not prove observed-data suitability, centralized simulation DGP coverage, literature alignment, or complete repair/replace/retire decisions. `suitability_matrix_sufficient_alone: false`.

---

## 5. Coverage dimensions

82 audit rows across design families (12), estimator families (9), inference families (17), observed-data conditions (18), simulation DGP conditions (14), and literature-alignment buckets (12).

---

## 6. Design-family coverage

All 12 design families are represented. Most are **partially covered** or **research required** (multicell). Unknown assignment is **blocked**. Greedy matched-market and kernel thinning remain falsification-only diagnostic paths.

---

## 7. Estimator-family coverage

All 9 estimator families represented including `future_method_scout`. SCM/DID partially covered; TBRRidge **gap/repair**; TBR **blocked**; Synthetic DID/TROP **scout**; Bayesian TBR diagnostic-only.

---

## 8. Inference-family coverage

All 17 inference families represented. Placebo/randomization is one family, not the full layer. TBRRidge BRB/KFold are repair/diagnostic gaps. Max-T/stepdown are research gaps. Conformal is blocked with scout warranted.

---

## 9. Observed-data diagnostic gaps

**Finding 2:** All 18 observed-data conditions are **planned** only. Before production-like method selection, the platform must define diagnostics for donor overlap, pre-period fit, small-N structure, sparsity, autocorrelation, outliers, seasonality, spillover, contamination, and heterogeneity. Next: `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`.

---

## 10. Simulation DGP coverage gaps

**Finding 3:** Existing null-calibration harnesses provide partial iid-null evidence only. A master DGP coverage plan is required for unit/time FE, latent factors, heteroskedasticity, autocorrelation, outliers, seasonality, sparse metrics, small-N geo, spillover, heterogeneous effects, and multicell dependence. Next: `SIMULATION_DGP_COVERAGE_PLAN_001`.

---

## 11. Literature-alignment buckets

**Finding 5:** All 12 literature-alignment buckets are registered as requiring formal review before promotion. This audit does not prove literature validity — buckets are internal research agendas only.

---

## 12. Known method-risk themes

TBRRidge inference failures, AugSynth JK retire/replace, TBR aggregate geometry mismatch, multicell global/winner familywise risk, stratified pooled heterogeneity, unknown assignment blocked, deterministic/falsification-only assignment paths.

---

## 13. Repair / replace / retire / scout decisions

**Finding 4:** Failure modes need central registry (`METHOD_FAILURE_MODE_REGISTRY_001`).  
**Finding 6:** New method scouts justified for Synthetic DID/generalized SDID, panel conformal, max-T/stepdown multicell, robust studentized randomization, interference/spillover geo methods, sparse/count outcome geo methods.

Recommended actions include repair (TBRRidge, AugSynth), retire/block (TBR, unknown assignment), scout (Synthetic DID, TROP, conformal, spillover), and defer research (multicell, cluster-robust).

---

## 14. Recommended next artifact sequence

1. `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`
2. `SIMULATION_DGP_COVERAGE_PLAN_001`
3. `METHOD_FAILURE_MODE_REGISTRY_001`
4. `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
5. `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
6. `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
7. `MULTICELL_MAX_T_RESEARCH_SCOUT_001`

Also noted: `METHOD_PROMOTION_CRITERIA_BY_FAMILY_001`, `METHOD_REPAIR_REPLACE_RETIRE_DECISION_RULES_001`, `AUGSYNTH_ESTIMATOR_BACKED_RANDOMIZATION_CALIBRATION_001`, `SCM_AUGSYNTH_DISAGREEMENT_DIAGNOSTICS_001`.

---

## 15. Downstream boundary

**Finding 7:** Downstream remains paused. This audit does not validate production inference. This audit does not authorize p-values or confidence intervals. This audit does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

---

## 16. Summary JSON location

[`archives/METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001_summary.json`](archives/METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001_summary.json) — `row_count: 82`, `failed_scenarios: []`.

---

## 17. Validation

Validation harness: 30+ scenarios, all passed. Governance JSON and roadmap updated. No downstream authorization flags true.

---

## 18. Verdict

**`method_gap_coverage_and_literature_alignment_audit_completed_no_downstream_authorization`**

Immediate next artifact: **`OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`**.
