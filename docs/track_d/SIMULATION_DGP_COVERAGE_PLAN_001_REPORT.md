# SIMULATION_DGP_COVERAGE_PLAN_001

**Artifact ID:** SIMULATION_DGP_COVERAGE_PLAN_001  
**Date:** 2026-06-03  
**Validation:** `panel_exp/validation/simulation_dgp_coverage_plan_001.py`  
**Summary:** [`archives/SIMULATION_DGP_COVERAGE_PLAN_001_summary.json`](archives/SIMULATION_DGP_COVERAGE_PLAN_001_summary.json)

---

## 1. Artifact ID

`SIMULATION_DGP_COVERAGE_PLAN_001`

---

## 2. Purpose

Define the master scenario universe for future null calibration, estimator remediation, design stress tests, and method promotion reviews. This is a DGP coverage requirements artifact, not a heavy simulation runner.

---

## 3. Current evidence base

Consumes evidence after `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001` (87 diagnostic requirements), `METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001`, and prior null-calibration harnesses (`STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001`, `SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001`). Existing harnesses provide partial IID-null evidence only.

---

## 4. Why shared DGP coverage is required

**Finding 1:** Existing null-calibration artifacts are useful, but future calibration should not expand through disconnected toy grids. A shared DGP coverage plan is required before widening estimator/inference validation.

---

## 5. Relationship to observed-panel diagnostics

**Finding 2:** Observed-panel diagnostics identify real data conditions; the DGP plan converts those conditions into required simulation scenarios. Each DGP row maps to `OPD-*` observed diagnostic requirement IDs.

---

## 6. DGP categories

105 DGP requirements across 12 categories: null baseline (7), noise/variance (7), temporal structure (7), outcome scale (9), treatment effect (9), assignment/design (11), donor/support (7), small-sample panel (8), interference/spillover (6), multicell/multiplicity (9), estimator-specific (11), inference-specific (14).

---

## 7. Null-baseline scenarios

IID normal/non-normal, unit/time/two-way FE, latent factor, and donor-matched latent factor nulls. All required before promotion of design-based inference paths.

---

## 8. Noise and variance scenarios

Homoskedastic through outlier-contaminated errors. Serial correlation and heteroskedasticity block IID bootstrap promotion.

---

## 9. Temporal-structure scenarios

Seasonality, shocks, level shifts, trend breaks, nonstationarity, lagged response, and metric delay mismatch.

---

## 10. Outcome-scale scenarios

**Finding 6:** Continuous through negative/invalid log-scale scenarios. Sparse count, zero-inflated, binary/binomial, and rate metrics require explicit coverage.

---

## 11. Treatment-effect scenarios

Sharp null through partial compliance. Heterogeneous and staggered effects stress DID and synthetic paths.

---

## 12. Assignment/design scenarios

Randomized through degenerate pseudo-assignment. Unknown and deterministic assignment block randomization inference promotion.

---

## 13. Donor/support scenarios

Good overlap through support mismatch. Hull violations and weight degeneracy block SCM/AugSynth promotion.

---

## 14. Small-sample panel scenarios

Small-N geos, few treated/donors, short pre/post, unbalanced panels, missingness, duplicate rows.

---

## 15. Interference/spillover scenarios

**Finding 5:** No-interference baseline plus neighbor spillover, cross-cell contamination, national media, donor contamination, and partial exposure leakage require research handling.

---

## 16. Multicell/multiplicity scenarios

Independent cells through stepdown candidates. Shared-control dependence and winner selection block naive independent-cell promotion.

---

## 17. Estimator-specific scenarios

SCM/AugSynth favorable and poor paths, DID parallel trends, TBRRidge stability, Bayesian TBR prior sensitivity, Synthetic DID, and TROP research-only.

---

## 18. Inference-specific scenarios

**Finding 3:** Null calibration alone is insufficient. Coverage spans randomization through no-valid-inference, including bootstrap under dependence, jackknife sensitivity-only, conformal research, and max-T/stepdown multicell requirements.

---

## 19. Promotion-blocking DGP gaps

**Finding 4:** 24+ DGP rows set `blocks_promotion_if_missing=True`. Estimator/inference combinations should not be promoted if required DGP categories lack validation evidence.

---

## 20. Routing to next artifacts

1. `METHOD_FAILURE_MODE_REGISTRY_001`
2. `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
3. `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
4. `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
5. `MULTICELL_MAX_T_RESEARCH_SCOUT_001`

---

## 21. Downstream boundary

**Finding 7:** This artifact defines DGP coverage requirements only. It does not run production simulations. It does not validate production inference. It does not authorize p-values or confidence intervals. It does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

---

## 22. Summary JSON location

[`archives/SIMULATION_DGP_COVERAGE_PLAN_001_summary.json`](archives/SIMULATION_DGP_COVERAGE_PLAN_001_summary.json) — `dgp_count: 105`, `failed_scenarios: []`.

---

## 23. Validation

Validation harness: all scenarios passed. Governance JSON and roadmap updated. No downstream authorization flags true.

---

## 24. Verdict

**`simulation_dgp_coverage_plan_defined_no_downstream_authorization`**

Immediate next artifact: **`METHOD_FAILURE_MODE_REGISTRY_001`**.
