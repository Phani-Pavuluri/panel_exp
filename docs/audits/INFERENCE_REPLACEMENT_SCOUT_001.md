# INFERENCE-REPLACEMENT-SCOUT-001

**Artifact ID:** INFERENCE-REPLACEMENT-SCOUT-001  
**Type:** Scouting / selection / roadmap (governance)  
**Date:** 2026-06-03  
**Branch:** `audit/inference-replacement-scout-001`  
**Summary:** [`docs/track_d/archives/INFERENCE_REPLACEMENT_SCOUT_001_summary.json`](../track_d/archives/INFERENCE_REPLACEMENT_SCOUT_001_summary.json)

---

## 1. Executive summary

Several inference paths in `panel_exp` are **blocked or diagnostic-only** (TBRRidge BRB/KFold/Placebo, SCM single-treated Placebo, AugSynth JK, multicell global claims, stratified aggregate). This scout evaluates candidate inference families against the estimators, designs, geometries, estimands, validation failures, and package constraints already present in the repo.

**Primary recommendation:** `DESIGN_AWARE_ASSIGNMENT_GENERATORS_001`  
**Secondary recommendation:** `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001`  
**Next artifact:** `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001` (assignment generators implemented — see [`DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_REPORT.md`](../track_d/DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_REPORT.md))

Design-valid pseudo-assignment generation is a **prerequisite** for treated-set placebo, permutation/rerandomization inference, and credible falsification across SCM, TBRRidge, AugSynth, and multicell geometries. Further BRB tuning and KFold recovery are **not** justified by current evidence.

**Governance verdict:** `inference_replacement_scout_completed_no_authorization`

> This scout does not authorize any inference method for TrustReport, CalibrationSignal, production decisioning, live API, scheduler, MMM ingestion, or budget optimization. It only selects the next method-validation investment path.

---

## 2. Why this scout exists

[`ROADMAP_REFOCUS_METHOD_VALIDATION_001`](ROADMAP_REFOCUS_METHOD_VALIDATION_001.md) froze TrustReport product-ops and redirected active work to method validity. Before committing implementation effort to a specific inference family, the program needs a governed comparison of:

- What is already implemented and characterized
- What failed statistical or semantic gates
- Which families are blocked by **design** gaps vs **inference** gaps
- Where small geo counts make cluster/bootstrap paths non-credible

Without this scout, the roadmap risked sequencing `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001` before the design bridges required to generate valid null assignments.

---

## 3. Current estimator inventory

| Estimator | Module | Trust lane | Status |
|-----------|--------|------------|--------|
| **SCM** / SyntheticControlCVXPY | `methods/scm.py` | DCM-001 | Restricted research-mode TrustReport (JK) |
| **TBRRidge** | `methods/scm.py` | DCM-005 | All causal inference paths blocked/diagnostic |
| **DID** | `methods/DID.py` | DCM-004 | Restricted research-mode TrustReport (embedded bootstrap) |
| **AugSynthCVXPY** | `methods/scm.py` | DCM-002 | Point/JK diagnostic; no promotion |
| **TBR** | `methods/tbr.py` | DCM-003 | Geometry ineligible (aggregate on unit panel) |
| **BayesianTBR** / HorseShoe | `methods/bayesian_regression.py` | — | Research-only; registry `Bayesian` ≠ NUTS MCMC |
| **SyntheticDID** | `methods/synthetic_did.py` | — | Unvalidated |
| **TROP** | `methods/triply_robust_est.py` | — | Research-only charter |

---

## 4. Current design inventory

| Design family | Implementation | Readout bridge |
|---------------|----------------|----------------|
| Single-treated geo | `greedy_match_markets`, `completerandomization` | Partial — SCM+JK reference |
| Multi-treated geo | greedy, multicell modes | Blocked for causal interval |
| Matched-pair / block | `design/matched_pair.py` | REQUIRES_ADAPTER |
| Stratified | `stratifiedrandomization` | `needs_design_bridge` |
| Rerandomized | `rerandomization_wrapper` in `assign.py` | **Not connected to inference** |
| Greedy matched-market | `greedy_match_markets` | `needs_design_bridge` |
| Kernel thinning | `thinningdesign` | Ambiguous semantics (G-DES) |
| Multicell shared-control | `multicell` feasibility/assign | Per-cell marginal only |
| Fixed / observational | — | Fail-closed for randomization inference |
| Unknown assignment | — | Fail-closed |

Conceptual gaps G-DES-001–014 (thinning, shared-control, rerandomization, trim/supergeo bridges) remain open per [`DESIGN_LITERATURE_ALIGNMENT_001.md`](../DESIGN_LITERATURE_ALIGNMENT_001.md).

---

## 5. Current inference inventory

Registered modes (`inference/modes/__init__.py`):

| Mode | Module | Wired estimators | Governed role |
|------|--------|------------------|---------------|
| **UnitJackKnife** | `unit_jackknife.py` | SCM, AugSynthCVXPY, TBRRidge | SCM restricted TrustReport; TBRRidge fails |
| **BlockResidualBootstrap** | `block_residual_bootstrap.py` | TBRRidge | `BRB_DIAGNOSTIC_ONLY` |
| **Kfold** / **TimeSeriesKfold** | `k_fold.py` | SCM, AugSynth, TBRRidge | Diagnostic only |
| **Placebo** | `placebo.py` | SCM, TBRRidge | Null-monitor; single-treated SCM |
| **Conformal** | `conformal.py` | AugSynth, TBRRidge | Diagnostic; not governed export |
| **Bayesian** | `modes/impl.py` | TBRRidge, BayesianTBR | Research; registry mismatch |
| **JKP** | `modes/impl.py` | TBRRidge | Known failure (~79% null FPR) |
| **DID bootstrap** (embedded) | `methods/DID.py` | DID only | Restricted TrustReport |

---

## 6. Known blocked / diagnostic-only paths

| Path | Verdict | Gate failure |
|------|---------|--------------|
| TBRRidge + BRB | `BRB_DIAGNOSTIC_ONLY` | Null type-I ~50% post-remediation |
| TBRRidge + KFold | `DIAGNOSTIC_ONLY` | Not causal-interval eligible |
| TBRRidge + Placebo | `NULL_MONITOR_ONLY` | Single-treated; falsification only |
| TBRRidge + JK | `known_failure_mode` | Null FPR ~79% |
| SCM + Placebo | `NULL_MONITOR_ONLY` | Single-treated only (A28) |
| AugSynthCVXPY + JK | `DIAGNOSTIC_ONLY` | Estimand/scale gap |
| DCM-006 global/winner/pooled | `PER_CELL_RESTRICTED` | Multiplicity ~27%; correlation ~0.90 |
| DCM-008 aggregate | `DIAGNOSTIC_ONLY` | Pooled estimand undefined |

---

## 7. Candidate inference families

| Family | Classification |
|--------|----------------|
| `design_based_randomization_inference` | `PROMISING_BUT_NEEDS_DESIGN_GENERATORS` |
| `treated_set_placebo_inference` | `PROMISING_BUT_NEEDS_DESIGN_GENERATORS` |
| `studentized_placebo_rank_inference` | `PROMISING_BUT_NEEDS_DESIGN_GENERATORS` |
| `permutation_or_rerandomization_inference` | `PROMISING_BUT_NEEDS_DESIGN_GENERATORS` |
| `jackknife_family` | `DIAGNOSTIC_ONLY` (SCM exception: restricted TrustReport) |
| `crossfit_or_kfold_family` | `DIAGNOSTIC_ONLY` |
| `BRB_family` | `BLOCKED_BY_NULL_CALIBRATION_RISK` |
| `wild_bootstrap_or_residual_bootstrap` | `BLOCKED_BY_NULL_CALIBRATION_RISK` (TBRRidge); DID embedded path separate |
| `conformal_residual_inference` | `DIAGNOSTIC_ONLY` |
| `cluster_or_block_robust_inference` | `BLOCKED_BY_SMALL_GEO_COUNTS` |
| `Bayesian_posterior_predictive_inference` | `PROMISING_BUT_RESEARCH_ONLY` |
| `Bayesian_structural_time_series_inference` | `PROMISING_BUT_RESEARCH_ONLY` |

---

## 8. Evaluation criteria

Each candidate scored 1–5 on:

`method_validity` · `null_calibration_potential` · `coverage_potential` · `small_sample_feasibility` · `multi_treated_support` · `single_treated_support` · `multicell_support` · `stratified_support` · `estimator_agnostic_reuse` · `implementation_complexity_inverse` · `testability` · `governance_clarity` · `alignment_with_existing_designs` · `alignment_with_existing_estimators` · `risk_of_false_authorization_inverse`

Binary flags recorded per candidate: `requires_known_assignment_process`, `requires_design_aware_generators`, `requires_large_number_of_units`, `requires_strong_model_assumptions`, `requires_bayesian_modeling_stack`, `produces_p_value`, `produces_interval`, `produces_diagnostic_only`, `can_support_*` estimator/design scopes.

---

## 9. Candidate scoring matrix

Aggregate scores (mean of 15 criteria, rounded):

| Rank | Family | Score | Classification |
|------|--------|-------|----------------|
| 1 | `design_based_randomization_inference` | **4.1** | `PROMISING_BUT_NEEDS_DESIGN_GENERATORS` |
| 2 | `treated_set_placebo_inference` | **3.9** | `PROMISING_BUT_NEEDS_DESIGN_GENERATORS` |
| 3 | `permutation_or_rerandomization_inference` | **3.8** | `PROMISING_BUT_NEEDS_DESIGN_GENERATORS` |
| 4 | `studentized_placebo_rank_inference` | **3.5** | `PROMISING_BUT_NEEDS_DESIGN_GENERATORS` |
| 5 | `jackknife_family` | **3.2** | `DIAGNOSTIC_ONLY` |
| 6 | `Bayesian_posterior_predictive_inference` | **2.8** | `PROMISING_BUT_RESEARCH_ONLY` |
| 7 | `conformal_residual_inference` | **2.6** | `DIAGNOSTIC_ONLY` |
| 8 | `Bayesian_structural_time_series_inference` | **2.5** | `PROMISING_BUT_RESEARCH_ONLY` |
| 9 | `crossfit_or_kfold_family` | **2.4** | `DIAGNOSTIC_ONLY` |
| 10 | `cluster_or_block_robust_inference` | **2.2** | `BLOCKED_BY_SMALL_GEO_COUNTS` |
| 11 | `BRB_family` | **2.0** | `BLOCKED_BY_NULL_CALIBRATION_RISK` |

Full per-criterion scores: [`INFERENCE_REPLACEMENT_SCOUT_001_summary.json`](../track_d/archives/INFERENCE_REPLACEMENT_SCOUT_001_summary.json).

---

## 10. Estimator compatibility matrix

| Estimator | Best near-term inference investment | Blocked / terminal paths |
|-----------|--------------------------------------|--------------------------|
| **SCM** | JK (existing restricted); future treated-set placebo | Placebo multi-treated blocked |
| **TBRRidge** | Replacement via design-based falsification | BRB, KFold, JK terminal |
| **DID** | Keep embedded bootstrap; add assignment bridge for rerandomization | Relative CI policy open |
| **AugSynthCVXPY** | Disposition + conformal diagnostic scout (deferred) | JK not promoted |
| **TBR** | Not compatible with current unit-panel geometry | — |

---

## 11. Design compatibility matrix

| Design | Randomization / placebo families | Current support |
|--------|----------------------------------|-----------------|
| Single-treated geo | Placebo (SCM), JK | Partial |
| Multi-treated geo | Treated-set placebo, permutation | **Blocked** — no valid pseudo-sets |
| Rerandomized | Permutation / design-based | Wrapper exists; inference disconnected |
| Multicell shared-control | Simultaneous / winner | **No method ready** |
| Stratified | Aggregate causal | **Blocked** — estimand undefined |
| Unknown assignment | All randomization families | Fail-closed |

---

## 12. Small-sample / geo-count constraints

Geo experiments typically have **small-to-moderate** unit counts. Implications:

- **Cluster/block-robust inference** is not credible as a near-term primary path (`BLOCKED_BY_SMALL_GEO_COUNTS`).
- **KFold** lacks stable calibration at observed counts; terminal diagnostic for TBRRidge.
- **BRB** failed null calibration after variance remediation — more resampling tuning is low yield.
- **Design-valid falsification** (placebo/permutation with governed assignment metadata) scales better conceptually because it uses the design structure rather than asymptotic cluster arguments.

---

## 13. Multicell and shared-control constraints

From `D5-TRUST-MULTICELL-PERCELL-INFERENCE-001`:

- Familywise null type-I ~27% (unadjusted)
- Cross-cell estimate correlation ~0.90
- Pooled/winner/global claims blocked 100%

**No candidate inference family** can support multicell winner/global/pooled claims **now**. Marginal per-cell SCM+JK remains available under [`MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001`](../MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001.md). Simultaneous inference requires `MULTICELL_MULTIPLICITY_CALIBRATION_001` and shared-control work — deferred, not scout-selected as next.

---

## 14. Stratified estimand constraints

From `D5-TRUST-STRATIFIED-SCM-JK-001`:

- Per-stratum SCM+JK diagnostic (~86% coverage balanced)
- Aggregate characterization type-I ~26%; aggregate claims blocked

**No method supports stratified aggregate TrustReport now.** `STRATIFIED_POOLED_ESTIMAND_CONTRACT_001` is a prerequisite before any aggregate inference investment.

---

## 15. TrustReport / CalibrationSignal / production boundaries

| Surface | Authorized |
|---------|------------|
| TrustReport (global) | **false** |
| TrustReport (DCM-001/004 research-mode) | restricted only — unchanged |
| CalibrationSignal | **false** |
| Production decisioning | **false** |
| Live API | **false** |
| Scheduler | **false** |
| Budget optimization | **false** |
| MMM ingestion | **false** |

This scout selects the **next method-validation investment path only**.

---

## 16. Recommended primary path

### `DESIGN_AWARE_ASSIGNMENT_GENERATORS_001`

**Why primary (matrix justification):**

1. Highest aggregate score among actionable families (`design_based_randomization_inference` = 4.1).
2. Lowest `alignment_with_existing_designs` (score 2) across all promising families — this is the **binding constraint**, not estimator code.
3. Prerequisite for treated-set placebo, permutation/rerandomization, and valid multi-treated falsification.
4. Unblocks SCM, TBRRidge, AugSynth, and multicell **falsification** lanes without prematurely authorizing causal intervals.
5. Addresses G-DES-001–014 explicitly referenced in method soundness roadmaps.

---

## 17. Recommended secondary path

### `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001`

**Why secondary (not primary):**

- Score 3.9 — strong, but `requires_design_aware_generators: true` on all flags.
- SCM Placebo is single-treated today (A28); multi-treated pseudo-sets need governed generators first.
- Sequencing placebo framework **after** generators avoids building semantics on invalid assignment nulls.

---

## 18. Rejected or deferred paths

### Rejected

| Path | Reason |
|------|--------|
| BRB further tuning | Post-remediation null gates failed; terminal `DIAGNOSTIC_ONLY` |
| KFold as causal interval (TBRRidge) | Terminal diagnostic; not recoverable without new assumptions |
| Cluster/block-robust near-term | Not credible at geo unit counts |

### Deferred

| Path | Reason |
|------|--------|
| `CONFORMAL_INFERENCE_FEASIBILITY_001` | Diagnostic only; multi-treated broadcast failure; not governed |
| `BAYESIAN_POSTERIOR_PREDICTIVE_SCOUT_001` | Research-only; modeling stack + governance gap |
| `TBRRIDGE_INFERENCE_REPLACEMENT_PROTOTYPE_001` | After design generators + treated-set framework |
| `MULTICELL_SHARED_CONTROL_INFERENCE_SCOUT_001` | After multiplicity lane |
| `AUGSYNTH_INFERENCE_DISPOSITION_001` | After design/estimand bridges |
| `STRATIFIED_POOLED_ESTIMAND_CONTRACT_001` | Estimand contract before aggregate inference |

---

## 19. Next implementation artifact

**`DESIGN_AWARE_ASSIGNMENT_GENERATORS_001`**

Deliverables should include: governed pseudo-assignment generation for rerandomization/stratified/multicell geometries; metadata bridge from `design/assign.py` modes to inference null specifications; explicit fail-closed policy for unknown/fixed assignment; OC hooks for placebo/permutation readiness — **without** authorizing TrustReport or production surfaces.

---

## 20. Residual issues and handoff

### Scout comparison answers

| # | Question | Answer |
|---|----------|--------|
| 1 | Multi-treated treated-set placebo next? | **No** — design generators first |
| 2 | Design-aware assignment generators first? | **Yes** — primary path |
| 3 | Abandon further BRB tuning? | **Yes** |
| 4 | KFold recoverable? | **No** — diagnostic only |
| 5 | Conformal promising for TBRRidge/AugSynth? | **Diagnostic only** — deferred feasibility scout |
| 6 | Bayesian posterior predictive near-term? | **No** — research lane |
| 7 | Cluster/block robust credible? | **No** at geo counts |
| 8 | Multicell winner/global now? | **No** |
| 9 | Stratified aggregate TrustReport now? | **No** |
| 10 | Next artifact? | `DESIGN_AWARE_ASSIGNMENT_GENERATORS_001` |

### Unchanged investigations

- `INV-MULTICELL-MULTIPLICITY-CALIBRATION-001` — deferred; clearer target after design lane
- `INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001` — deferred

**Next artifact:** `MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001` (assignment generators implemented — see [`DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_REPORT.md`](../track_d/DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_REPORT.md))
