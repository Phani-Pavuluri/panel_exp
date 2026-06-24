# OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001

**Artifact ID:** OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001  
**Date:** 2026-06-03  
**Validation:** `panel_exp/validation/observed_panel_diagnostic_requirements_001.py`  
**Summary:** [`archives/OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001_summary.json`](archives/OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001_summary.json)

---

## 1. Artifact ID

`OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`

---

## 2. Purpose

Define required diagnostics on an observed geo/panel experiment dataset before selecting an estimator, inference method, calibration path, or downstream evidence route. This is a diagnostic-requirements artifact, not a production diagnostic runner.

---

## 3. Current evidence base

Consumes repo evidence after `METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001`, `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`, and `ROADMAP_INFERENCE_AND_METHOD_GAP_CONTROL_REFOCUS_001`. The gap audit identified 18 observed-data conditions as **planned** only; this artifact operationalizes those into 87 requirement rows with severity, routing impacts, and method-family bindings.

---

## 4. Why observed-panel diagnostics are required before method selection

**Finding 1:** Estimator/inference suitability cannot be determined from method family alone. The observed panel must first be diagnosed for panel structure, assignment validity, donor support, pre-period behavior, outcome scale, temporal dependence, exposure integrity, and multicell dependence.

---

## 5. Diagnostic categories

Ten categories: panel structure (11), assignment/design validity (10), donor/support/overlap (8), pre-period fit/trends (7), temporal dependence/shocks (7), outcome/metric (10), treatment exposure (8), multicell/multiplicity (7), estimator routing (9), inference routing (10).

---

## 6. Panel-structure requirements

Index uniqueness, required columns, balance, missingness, duplicates, pre/post length, treated/control counts, time periods, and small-N flags. Hard blockers include duplicate keys and insufficient pre-period length.

---

## 7. Assignment/design-validity requirements

Assignment mechanism known/unknown, randomized vs deterministic, matched-pair/block integrity, stratification, rerandomization rules, treatment timing, shared-control multicell structure, support size, and pseudo-assignment feasibility.

---

## 8. Donor/support/overlap requirements

Donor pool size, eligibility, hull support, covariate overlap, metric overlap, SCM weight degeneracy, AugSynth extrapolation risk, and support mismatch blockers.

---

## 9. Pre-period fit and trend requirements

Pre-period fit quality, residual bias, parallel-trend plausibility, trend breaks, nonstationarity, shock sensitivity, and leave-last-pre-period stability.

---

## 10. Temporal dependence and shock requirements

Autocorrelation, seasonality, holiday/promo shocks, outlier weeks, level shifts, time-varying variance, and metric delay/lag mismatch.

---

## 11. Outcome/metric requirements

Sparsity, zero inflation, count/binary flags, heavy tails, variance instability, scale compatibility, log-transform validity, denominator availability, and rate metric consistency.

---

## 12. Treatment exposure requirements

Intensity variation, dose availability, on/off consistency, partial compliance, staggered activation, contamination, spillover/interference, and cross-cell leakage.

---

## 13. Multicell/multiplicity requirements

Shared-control dependence, multiple arms, winner selection risk, familywise error risk, cell independence, cell-specific estimand clarity, and pooled/global estimand ambiguity.

---

## 14. Estimator-routing implications

Per-family suitability gates for SCM, AugSynth, DID, TBRRidge, TBR, Bayesian TBR, Synthetic DID, TROP, and new-method scout triggers. TBR and Bayesian TBR remain diagnostic-only; Synthetic DID and TROP require research scouts.

---

## 15. Inference-routing implications

Randomization, placebo rank, studentized statistics, bootstrap, jackknife, cluster-robust, conformal, posterior diagnostic-only boundary, max-T/stepdown need, and no-valid-inference blocker.

---

## 16. Hard blockers vs warnings

**Finding 2 — Hard blockers:** Unknown assignment, support mismatch, insufficient pre-period, invalid outcome scale, shared-control multicell dependence without contract, contamination/spillover, and no-valid-inference paths.

**Finding 3 — Warnings:** Mild autocorrelation, moderate outliers, partial missingness, weak but not failed pre-fit, metric sparsity, and possible heterogeneity route to sensitivity analysis, simulation DGP coverage, or diagnostic-only status.

---

## 17. Routing to next artifacts

**Finding 4:** Requirements explicitly route to:

1. `SIMULATION_DGP_COVERAGE_PLAN_001`
2. `METHOD_FAILURE_MODE_REGISTRY_001`
3. `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
4. `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
5. `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
6. `MULTICELL_MAX_T_RESEARCH_SCOUT_001`

---

## 18. Downstream boundary

**Finding 5 — No downstream authorization:** This artifact defines diagnostic requirements only. It does not compute production diagnostics. It does not validate production inference. It does not authorize p-values or confidence intervals. It does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

---

## 19. Summary JSON location

[`archives/OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001_summary.json`](archives/OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001_summary.json) — `requirement_count: 87`, `failed_scenarios: []`.

---

## 20. Validation

Validation harness: all scenarios passed. Governance JSON and roadmap updated. No downstream authorization flags true.

---

## 21. Verdict

**`observed_panel_diagnostic_requirements_defined_no_downstream_authorization`**

Immediate next artifact: **`SIMULATION_DGP_COVERAGE_PLAN_001`**.
