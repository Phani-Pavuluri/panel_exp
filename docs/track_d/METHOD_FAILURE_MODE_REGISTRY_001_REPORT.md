# METHOD_FAILURE_MODE_REGISTRY_001

**Artifact ID:** METHOD_FAILURE_MODE_REGISTRY_001  
**Date:** 2026-06-03  
**Validation:** `panel_exp/validation/method_failure_mode_registry_001.py`  
**Summary:** [`archives/METHOD_FAILURE_MODE_REGISTRY_001_summary.json`](archives/METHOD_FAILURE_MODE_REGISTRY_001_summary.json)

---

## 1. Artifact ID

`METHOD_FAILURE_MODE_REGISTRY_001`

---

## 2. Purpose

Centralize known and expected failure modes across design, estimator, inference, observed-panel diagnostics, and simulation DGP requirements before future promotion. This is a registry/control artifact, not a production validator.

---

## 3. Current evidence base

Consumes evidence after `SIMULATION_DGP_COVERAGE_PLAN_001` (105 DGPs), `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001` (87 diagnostics), `METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001`, `ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`, and prior calibration/adapter artifacts (studentized randomization, SCM placebo, AugSynth adapter, method readiness v2, CalibrationSignal gate draft, TBRRidge/multicell/stratified reports).

---

## 4. Why a central failure-mode registry is required

**Finding 1:** The platform now has method suitability, gap coverage, observed diagnostics, and DGP coverage. Without a central failure-mode registry, later artifacts may rediscover the same failures or accidentally promote known weak paths.

---

## 5. Relationship to method suitability, observed diagnostics, and DGP coverage

Each registry row links `observed_diagnostic_triggers` (OPD-*) and `dgp_triggers` (DGP-*) to affected design/estimator/inference families, severity, required actions, and promotion impact.

---

## 6. Registry schema

`MethodFailureMode` rows connect failure mode → diagnostic/DGP triggers → affected families → severity → required actions → promotion/downstream blocking → recommended next artifact.

---

## 7. Failure-mode categories

100 failure modes across 11 categories: design/assignment (10), panel structure (10), donor/support (8), pre-period fit/trends (7), temporal dependence/shocks (7), outcome/metric (9), treatment exposure/interference (9), estimator-specific (10), inference-specific (11), calibration/promotion (9), downstream boundary (10).

---

## 8. Design/assignment failures

Unknown assignment, deterministic-as-randomized, rerandomization gaps, matched-pair/block failures, stratification integrity, small/degenerate support, shared-control dependence ignored, multicell winner-selection ignored.

---

## 9. Panel-structure failures

Duplicate rows, missing keys, unbalanced panels, short pre/post, few treated/donors, small-N overclaim, high missingness, index leakage.

---

## 10. Donor/support failures

Small donor pool, invalid eligibility, hull violation, treated outside range, weak overlap, SCM weight degeneracy, AugSynth extrapolation, support mismatch ignored.

---

## 11. Pre-period fit and trend failures

Poor fit, residual bias, parallel-trends violation, trend breaks, nonstationarity, shock sensitivity, leave-last-pre-period instability.

---

## 12. Temporal dependence and shock failures

Autocorrelation, seasonality, holiday/promo shocks, outlier weeks, level shifts, time-varying variance, metric lag mismatch.

---

## 13. Outcome/metric failures

Invalid log transform, negative values, sparse count as Gaussian, zero inflation, binary without diagnostic, missing denominator, heavy tails, scale mismatch, metric drift.

---

## 14. Treatment exposure and interference failures

Timing inconsistency, partial compliance, dose/stagger ignored, cross-cell contamination, donor contamination, national media spillover, neighbor spillover, exposure leakage.

---

## 15. Estimator-specific failures

SCM/AugSynth/DID/TBRRidge/TBR/Bayesian TBR/Synthetic DID/TROP promotion failures including poor support, uncalibrated inference, trend violations, regularization masking, aggregate overclaim, research-only paths treated as production.

---

## 16. Inference-specific failures

Placebo as p-value, uncalibrated studentized placebo, bootstrap under dependence, BRB without validation, jackknife as CI, cluster-robust with few clusters, conformal without panel review, posterior as causal CI, max-T/stepdown ignored, no-valid-inference promoted.

---

## 17. Calibration and promotion failures

Missing null calibration, DGP coverage, observed diagnostics, registry consultation, literature alignment, method adapter; promotion from diagnostic/research/blocked status.

---

## 18. Downstream-boundary failures

TrustReport, CalibrationSignal, MMM, LLM, production decisioning, live API, scheduler, budget optimization, production p-value, and causal CI authorization attempts.

---

## 19. Hard blockers vs diagnostic/sensitivity/research paths

**Finding 2 — Hard blockers:** Unknown assignment for design-based inference, support mismatch ignored, invalid log scale, shared-control dependence ignored, posterior as causal CI, production authorization attempts.

**Finding 3 — Diagnostic/sensitivity paths:** SCM placebo without production semantics, jackknife sensitivity-only, AugSynth point without calibrated inference, Bayesian posterior diagnostic-only, weak pre-fit, mild autocorrelation.

---

## 20. Remediation, retirement, and replacement paths

**Finding 4:** TBR aggregate overclaim, TBRRidge instability masked by regularization, bootstrap under dependence, cluster-robust with few clusters, TROP research-only treated as production — route to remediate, retire/replace, or scout new methods.

---

## 21. How future promotion must consult this registry

**Finding 5:** No design/estimator/inference path should be promoted without checking observed-panel diagnostics, DGP coverage plan, and this failure-mode registry.

---

## 22. Routing to next artifacts

1. `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
2. `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
3. `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
4. `MULTICELL_MAX_T_RESEARCH_SCOUT_001`

---

## 23. Downstream boundary

**Finding 6:** This artifact defines a failure-mode registry only. It does not run production diagnostics. It does not validate production inference. It does not authorize p-values or confidence intervals. It does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

---

## 24. Summary JSON location

[`archives/METHOD_FAILURE_MODE_REGISTRY_001_summary.json`](archives/METHOD_FAILURE_MODE_REGISTRY_001_summary.json) — `failure_mode_count: 100`, `failed_scenarios: []`.

---

## 25. Validation

Validation harness: all scenarios passed. Governance JSON and roadmap updated. No downstream authorization flags true.

---

## 26. Verdict

**`method_failure_mode_registry_defined_no_downstream_authorization`**

Immediate next artifact: **`DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`**.
