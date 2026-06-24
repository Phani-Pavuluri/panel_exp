# DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001

**Artifact ID:** DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001  
**Date:** 2026-06-03  
**Validation:** `panel_exp/validation/design_assignment_generator_stress_tests_001.py`  
**Summary:** [`archives/DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001_summary.json`](archives/DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001_summary.json)

---

## 1. Artifact ID

`DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`

---

## 2. Purpose

Define stress-test requirements for assignment generators and pseudo-assignment spaces used by randomization, placebo, permutation, and design-based inference paths. This is a stress-test requirements/control artifact, not a production inference engine.

---

## 3. Current evidence base

Consumes `METHOD_FAILURE_MODE_REGISTRY_001` (100 failure modes), `SIMULATION_DGP_COVERAGE_PLAN_001` (105 DGPs), `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001` (87 diagnostics), suitability matrix, and prior assignment/placebo/randomization artifacts (design-aware generators, treated-set placebo framework, null calibrations, governed semantics, statistic adapter contract).

---

## 4. Why assignment generators are not inference engines

**Finding 1:** A generator that can produce alternative assignments is not sufficient to authorize randomization or placebo inference. Generated support must respect the original design, assignment constraints, treatment counts, cell structure, and feasibility rules.

---

## 5. Relationship to failure-mode registry, observed diagnostics, and DGP coverage

Each stress-test row links `failure_registry_links` (FM-*), `observed_diagnostic_links` (OPD-*), and `dgp_links` (DGP-*) to affected assignment families, inference paths, severity, and required actions.

---

## 6. Stress-test schema

`AssignmentGeneratorStressTest` rows connect stress ID → category → severity → assignment/inference families → triggers → actions → blocking flags → recommended next artifact.

---

## 7. Stress-test categories

91 stress tests across 11 categories: assignment support integrity (12), randomized validity (8), matched-pair (8), matched-block/stratified (8), rerandomization (8), greedy/deterministic (7), kernel thinning (6), multi-treated placebo (7), multicell shared-control (9), inference feasibility (12), failure-registry linkage (6).

---

## 8. Assignment support integrity

Support size, degeneracy, observed assignment inclusion, treatment/treated-set counts, cell constraints, impossible assignment exclusion, seed reproducibility.

---

## 9. Randomized assignment validity

Complete randomization, small support, assignment probabilities, unknown-probability blocking, unit mismatch, treatment drift, timing mismatch.

---

## 10. Matched-pair stress tests

Pair membership, one-treated-per-pair, imbalance, missing pair IDs, swap feasibility, support size, spillover risk.

---

## 11. Matched-block and stratified stress tests

Block/stratum membership, treatment quotas, non-degenerate support, imbalance.

---

## 12. Rerandomization stress tests

Acceptance rule/statistic/threshold, accepted support, reproducibility, balance preservation, unknown-rule blocking.

---

## 13. Greedy/deterministic design stress tests

**Finding 2:** Deterministic and unknown assignment remain blockers unless governed reconstruction exists. Pseudo-assignment cannot be treated as true randomization.

---

## 14. Kernel thinning stress tests

Support availability, seed reproducibility, balance constraints, non-degenerate support, documented assignment probabilities.

---

## 15. Multi-treated and treated-set placebo stress tests

Treated-set size, placebo support, overlap constraints, leave-one-treated-out, placebo rank not production p-value, SCM geometry compatibility.

---

## 16. Multicell shared-control stress tests

**Finding 4:** Shared-control dependence, cell constraints, cross-cell exclusions, winner-selection risk, max-T/stepdown need, pooled estimand ambiguity, invalid independent-cell assumption.

---

## 17. Inference feasibility stress tests

**Finding 3:** Small/degenerate support blocks rank inference. **Finding 5:** Studentized adapters and null calibration required before promotion.

Randomization, permutation, placebo rank (diagnostic-only), studentized adapter, bootstrap not substituted, no-valid-inference routes.

---

## 18. Failure-registry linkage stress tests

**Finding 6:** Unknown assignment, deterministic-as-randomized, small support, degenerate pseudo-support, shared-control ignored, winner-selection ignored — all map to FM-* registry entries.

---

## 19. Hard blockers vs diagnostic/sensitivity/research paths

Hard blockers: unknown assignment, deterministic-as-randomized, degenerate support, multicell dependence ignored. Diagnostic/sensitivity: placebo rank, greedy/kernel falsification, marginal support. Research: multicell max-T/stepdown, multi-treated geometry.

---

## 20. Routing to next artifacts

1. `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
2. `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
3. `MULTICELL_MAX_T_RESEARCH_SCOUT_001`

---

## 21. Downstream boundary

**Finding 7:** This artifact defines assignment-generator stress-test requirements only. It does not run production inference. It does not validate production p-values or confidence intervals. It does not authorize TrustReport, CalibrationSignal, MMM, LLM, live API, scheduler, or budget optimization.

---

## 22. Summary JSON location

[`archives/DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001_summary.json`](archives/DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001_summary.json) — `stress_test_count: 91`, `failed_scenarios: []`.

---

## 23. Validation

Validation harness: all scenarios passed. Governance JSON and roadmap updated. `inference_authorized: false`; all authorization flags false.

---

## 24. Verdict

**`design_assignment_generator_stress_tests_defined_no_downstream_authorization`**

Immediate next artifact: **`TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`**.
