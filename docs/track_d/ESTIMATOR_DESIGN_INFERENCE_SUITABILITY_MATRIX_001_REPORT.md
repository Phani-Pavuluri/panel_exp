# ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001

**Artifact ID:** ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001  
**Date:** 2026-06-03  
**Module:** `panel_exp/inference/estimator_design_inference_suitability.py`  
**Validation:** `panel_exp/validation/estimator_design_inference_suitability_matrix_001.py`  
**Summary:** [`archives/ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001_summary.json`](archives/ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001_summary.json)

---

## 1. Artifact ID

`ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`

---

## 2. Purpose

Define the first cross-estimator, cross-design, cross-inference suitability matrix governing which inference paths are supported, candidate-after-calibration, diagnostic-only, sensitivity-only, adapter-required, null-calibration-required, research-deferred, or blocked for each estimator × design × inference × estimand × geometry combination.

---

## 3. Why this matrix is needed

The method-accuracy lane accumulated placebo/randomization calibration and SCM/AugSynth adapter contracts. Without an explicit suitability matrix, narrow implementation work risks treating placebo/randomization as the entire inference layer. This artifact prevents roadmap overfitting to placebo inference or SCM/AugSynth only.

---

## 4. Prior method-accuracy context

Spine inputs: `METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001` → `STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001` → `SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001` → `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`. Prior readiness work (`METHOD_READINESS_MATRIX_V2_001`) indexed method rows but did not govern full estimator × design × inference selection across all families.

---

## 5. Why placebo/randomization is not the full inference layer

Placebo rank, studentized placebo rank, design-based randomization, and permutation are **one inference family cluster** among many. The matrix also encodes unit jackknife, DID bootstrap, block residual bootstrap, K-fold cross-fit, conformal (blocked), Bayesian posterior intervals, cluster-robust analytic, max-T/stepdown multiplicity, and leave-one-treated-out sensitivity. **Placebo/randomization is one inference family, not the full inference layer.**

---

## 6. Estimator families

SCM · AugSynth CVXPY · DID · TBRRidge · TBR · Bayesian TBR · Synthetic DID · TROP

---

## 7. Design families

Single-treated geo · multi-treated geo · matched pair · matched block · stratified · rerandomized · greedy matched market · kernel thinning · fixed deterministic · multicell shared-control · multicell independent cells · unknown assignment

---

## 8. Inference families

Unit jackknife · leave-one-treated-out sensitivity · treated-set placebo rank · studentized placebo rank · design-based randomization · permutation · bootstrap · block residual bootstrap · K-fold cross-fit · conformal · Bayesian posterior interval · Bayesian posterior predictive check · cluster-robust analytic · DID bootstrap · max-T multiplicity · stepdown multiplicity · no valid inference

---

## 9. Suitability statuses

Supported restricted research · candidate after null calibration · candidate requires adapter · candidate requires design stress test · diagnostic-only · sensitivity-only · posterior diagnostic-only · multiplicity research required · dependence research required · geometry mismatch blocked · assignment unknown blocked · known failure blocked · research deferred · retire or replace · blocked

---

## 10. Suitability matrix

50 governed rows in `build_estimator_design_inference_suitability_matrix()`. Each row specifies estimator family, design family, inference family, estimand scope, geometry, assignment/adapter/null-calibration/multiplicity requirements, suitability status, usage boundary, known failure modes, required evidence, recommended next artifact (when applicable), and forbidden outputs.

---

## 11. SCM findings

- Unit jackknife on single-treated geo: **supported restricted research** (not production).
- Single-treated placebo rank: **diagnostic-only** null-monitor/falsification.
- Multi-treated treated-set and studentized placebo: **candidate after null calibration** (requires prior calibration artifacts + shared adapter).
- Leave-one-treated-out: **sensitivity-only**.
- Unknown assignment + randomization: **assignment unknown blocked**.
- Stratified per-stratum: candidate after calibration; pooled aggregate without heterogeneity policy: **geometry mismatch blocked**.

---

## 12. AugSynth findings

- Multi-treated design-based randomization: **candidate requires adapter** (`SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`).
- Point randomization + studentized placebo: **candidate after null calibration**.
- Jackknife: **retire or replace** (`jk_unsafe_under_diagnostics`).
- Unknown assignment: **blocked**.
- Stratified pooled: **candidate requires adapter** + pooling policy.

---

## 13. DID findings

- Matched/stratified DID bootstrap: **supported restricted research** or **candidate after null calibration** (stratum level).
- Cluster-robust analytic: **candidate requires design stress test** (not credible at geo counts).
- Permutation/randomization: **candidate after null calibration**.
- Unknown assignment: **blocked**.

---

## 14. TBRRidge findings

- BRB: **known failure blocked** (estimand mismatch, variance miscalibration).
- K-fold: **diagnostic-only** (elevated null FPR).
- Placebo rank: **diagnostic-only** until remediation.
- Jackknife: **known failure blocked**.
- Remediation path: **retire or replace** — no valid production inference until audit.

---

## 15. TBR / Bayesian TBR findings

- TBR aggregate geometry: **geometry mismatch blocked**.
- Bayesian posterior interval and predictive check: **posterior diagnostic-only** / research.
- Bayesian placebo rank: **diagnostic-only** without adapter/null calibration.

---

## 16. Synthetic DID / TROP findings

- Synthetic DID bootstrap/permutation: **research deferred** (not implemented).
- Synthetic DID placebo/randomization: **candidate requires adapter**.
- TROP permutation/randomization: **research deferred**.
- TROP unknown assignment: **blocked**.

---

## 17. Multicell findings

- Shared-control + max-T: **dependence research required** (per-cell marginal only).
- Independent cells + stepdown: **multiplicity research required**.
- Global winner selection: **blocked**.
- Pooled multicell effect: **geometry mismatch blocked**.

---

## 18. Stratified findings

- SCM/AugSynth/DID per-stratum inference: candidate after calibration or restricted research.
- Stratified pooled aggregate without heterogeneity policy: **blocked** or geometry mismatch.
- Aggregate claims require explicit heterogeneity and pooling policy.

---

## 19. Unknown / deterministic / falsification-only findings

- Unknown assignment + any design-based inference: **assignment unknown blocked**.
- Fixed deterministic, greedy matched market, kernel thinning + placebo/randomization: **diagnostic-only** falsification/null-monitor only — not valid randomization inference.

---

## 20. Reusable inference engines through statistic adapters

SCM/AugSynth treated-set placebo, studentized placebo, and design-based randomization can share reusable inference engines when `scm_augsynth_shared_adapter` contract is satisfied. Synthetic DID and stratified pooling require future adapters.

---

## 21. Estimator-specific inference requirements

TBRRidge requires remediation before any inference promotion. Bayesian TBR requires separate decision-safe validation. DID bootstrap/cluster paths require design stress tests. AugSynth jackknife should be retired or replaced.

---

## 22. Recommended next artifacts

1. `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001`
2. `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`
3. `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001`
4. `MULTICELL_MAX_T_RESEARCH_SCOUT_001`

Also noted: `AUGSYNTH_ESTIMATOR_BACKED_RANDOMIZATION_CALIBRATION_001` · `SCM_AUGSYNTH_DISAGREEMENT_DIAGNOSTICS_001`

**No downstream schema or TrustReport work recommended.**

---

## 23. Downstream authorization boundary

**No production p-values. No causal confidence intervals. No TrustReport expansion. No CalibrationSignal. No MMM ingestion. No LLM decisioning. No production decisioning. No live API. No scheduler. No budget optimization.** Downstream work remains paused until method suitability, calibration, adapter, and remediation gates are complete.

---

## 24. Safety checks

Validation harness: 50 scenarios, `failed_scenarios: []`. All rows carry forbidden outputs. All authorization flags false. `placebo_is_only_inference_layer: false`. `downstream_work_paused: true`.

---

## 25. Final verdict

**`estimator_design_inference_suitability_matrix_defined_no_downstream_authorization`**

Placebo/randomization is one inference family, not the full inference layer. No estimator receives a universal default inference. Inference suitability depends on estimator, design, assignment mechanism, estimand, geometry, statistic adapter, and null calibration. This artifact does not authorize production p-values or causal confidence intervals. This artifact does not authorize TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization.
