# Algorithm and statistical reassessment

**Scope:** Estimators, synthetic DGPs, recovery/calibration metrics, counterfactual stability diagnostics, and inference semantics.  
**Excluded:** Docs/cards/bundles/readiness artifacts, maturity metadata, CI layout, API exports.  
**Package version:** 0.2.1  
**Evidence basis:** `panel_exp/methods/*`, `panel_exp/validation/*`, `panel_exp/utils/counterfactual_stability_tests.py`, `panel_exp/inference/*`, `tests/test_*`, `tests/trop_test.py`, `tests/synthetic_did_test.py`.

---

## Top 10 algorithm correctness risks

| # | Risk | Code evidence |
|---|------|----------------|
| 1 | **Validation truth metric may not match estimator estimands.** Scalar truth is mean post-period relative lift vs stored counterfactual baseline (`_scalar_truth_effect` in `synthetic_world.py`); recovery scoring uses path-based mean relative ATT (`_path_relative_att` in `runner.py`) with fallbacks to `summary()`. Heterogeneous effects (`heterogeneous_effects=True`) change per-unit lifts but aggregation rules differ from TWFE/SCM weighting. | `synthetic_world.py` L238–272; `runner.py` L63–103 |
| 2 | **DGP spillover contaminates controls without estimator correction.** `spillover_strength` scales control post-period outcomes (`synthetic_world.py` L165–178) while estimators assume no spillover. `scm_donor_contamination` tests this, but default fits ignore spillover metadata. | `synthetic_scenarios.py` L85–89; `method_metadata.py` interference notes |
| 3 | **TBR path requires degenerate panel geometry.** `TBR.fit_data` asserts exactly one treated unit and one control aggregate (`tbr.py` L116–120). Mis-specified panels fail hard rather than routing to `TBRRidge`. | `tbr.py` L105–120 |
| 4 | **DID requires simultaneous adoption.** `DID.fit_data` asserts a single `treated_start_idxs` and end (`DID.py` L46–47). Staggered or geo-specific timing breaks pooled TWFE; SDID scenarios are not recovery-wired. | `DID.py` L46–47; `recovery_runner.py` `_extended_estimator_configs` |
| 5 | **DID parallel-trends violations do not block ATT export.** Pretrend diagnostics (`_run_event_study_pretrend_test`, `_run_linear_pretrend_test`) populate results metadata, but `fit_model` still returns a pooled `treated_post` coefficient and bootstrap CIs. | `DID.py` L401–736 |
| 6 | **SCM counterfactual weights are pre-period fit; post-period extrapolation unstability is not part of the estimator.** Weights from `SyntheticControl` / OSQP solve (`scm.py`); stability tooling is separate (`counterfactual_stability_tests.py`) and not invoked in `run_analysis`. | `scm.py` L289+; `counterfactual_stability_tests.py` L1–7 |
| 7 | **TBRRidge extrapolates linearly from normalized pre-period ridge fit.** `NormalisedModel.predict` applies pre-period mean scaling then ridge extrapolation (`tbr.py` L224–270). Structural breaks/outliers in scenarios (`tbr_outliers`, `scm_structural_break` in registry) are not modeled in the fit. | `tbr.py` L202–272; `synthetic_scenarios.py` |
| 8 | **TROP can return unstable/empty fits on sparse panels.** `min_donor_support`, weak-donor warnings, and stability-first tuning discard “flat” counterfactuals (`triply_robust_est.py` L1707–1718, L2108+). Recovery smoke tolerates NaN means (`recovery_metrics.py` L78–79; `test_recovery_runner.py::test_trop_recovery_smoke`). | `triply_robust_est.py`; `recovery_runner.py` |
| 9 | **Registry “Bayesian” inference on SCM/TBR ≠ `BayesianTBR` MCMC.** Catalog documents divergence (`method_metadata.py` TBRRidge rationale); MCMC estimators are separate classes with `research_only` maturity and no recovery wiring. | `method_metadata.py`; `validation/runner.py` `SKIPPED_ESTIMATORS` |
| 10 | **Recovery failures are swallowed.** `_run_simulation` catches all exceptions and returns `predicted_effect=nan` without surfacing error class to callers (`recovery_runner.py` L84–92). Production paths do not run recovery, but calibration/readiness can inherit silent gaps if fed recovery outputs. | `recovery_runner.py` L77–92 |

---

## Top 10 statistical / causal risks

| # | Risk | Code evidence |
|---|------|----------------|
| 1 | **Single treated geo + simultaneous treatment in most synthetic worlds.** Default draws ~20% of geos as treated, one `treatment_start` (`synthetic_world.py` L104–106, L151–163). Staggered adoption and multi-treated ATT definitions remain open in `inference/uncertainty.md`. | `uncertainty.md` L5–15; `synthetic_world.py` |
| 2 | **Pooled DID estimand ≠ unit-level geo lift when geos are heterogeneous.** `multiple_treated="pooled"` in validation config (`runner.py` L57–58) with TWFE `treated_post` (`DID.py` L59–61). `did_parallel_trends_violation` turns on `heterogeneous_effects` in DGP but not in estimator. | `synthetic_scenarios.py` L101–107; `runner.py` |
| 3 | **Placebo bands vs confidence intervals.** `InferenceResult` distinguishes `placebo_band` from `confidence_interval` (`inference_result.py`); placebo misuse remains a causal interpretation risk where strict mode is off. | `inference_result.py`; `test_audit_fixes.py::test_placebo_unsupported_no_fake_ci` |
| 4 | **SCM simplex weights: donor collinearity and concentration.** High `cross_geo_correlation` (default 0.4) plus optional correlation filter (`scm.py` L252–263). No dedicated collinearity stress scenario in `ESTIMATOR_RECOVERY_SCENARIOS`. Low-signal scenario weakens donor match (`scm_low_signal`). | `synthetic_scenarios.py`; `scm.py` |
| 5 | **Jackknife / bootstrap geometry under few donors.** Unit jackknife documented for donor removal (`inference/unit_jackknife.py`); BRB documents donor-pooling as experimental (`block_residual_bootstrap.py` L20–30). No automated guard in recovery runs when `n_geos` is small (e.g. `trop_sparse_donors` n_geos=10). | `validation/synthetic_scenarios.py` L154–161 |
| 6 | **Interval coverage in recovery is mostly unobserved for SCM/TBR.** Default recovery configs use `inference=None` (`recovery_runner.py` via `default_estimator_configs` / extended specs). `aggregate_recovery_metrics` sets `coverage`, `false_positive_rate`, `power` to NaN without CIs/significance (`recovery_metrics.py` L90–111). | `recovery_runner.py` L37–50; `recovery_metrics.py` |
| 7 | **Finite-sample calibration uses tiny replication counts.** Recovery tests commonly use `n_simulations=2–6` (`test_recovery_runner.py`), so FPR/coverage/power are unstable estimates, not operating characteristics. | `test_recovery_runner.py` |
| 8 | **Power analysis DGP ≠ recovery DGP.** `PowerAnalysis` uses sliding train/test windows and percent grids (`power.py`); recovery uses stationary factor+seasonality worlds. `aa_calibration` on power output is separate from `RecoveryRunner` null scenarios (`recovery_null_effect`). | `power.py`; `synthetic_scenarios.py` |
| 9 | **SDID staggered scenarios misaligned with estimator tests.** Registry lists `sdid_staggered_timing` / `sdid_varying_timing`, but unit tests repeat identical `TimePeriod` per treated geo (“no stagger”) (`synthetic_did_test.py` L33–36). Recovery not wired (`VALIDATION_COVERAGE.md`). | `synthetic_scenarios.py` L138–153; `synthetic_did_test.py` |
| 10 | **Interference declared but not estimated.** Spillover enters DGP and design metadata only; no spillover term in SCM/TBR/DID likelihoods. Partial interference with missing adjacent-geo metadata still yields finite estimates (`build_interference_review` warnings only). | `synthetic_world.py` L165–178; `spec.py` `spillover_estimation_available: False` in evidence helpers |

---

## Top 5 missing synthetic DGP tests

| # | Missing test | Why it matters | Code gap |
|---|--------------|----------------|----------|
| 1 | **High donor collinearity / rank-deficient SCM donor matrix** | Weights and OSQP solves become unstable; geo panels often have near-duplicate donors. | No scenario with `cross_geo_correlation→1` or explicit rank collapse; `scm_structural_break` exists but is **not** in `ESTIMATOR_RECOVERY_SCENARIOS` (only in `RECOVERY_SCENARIO_REGISTRY`) |
| 2 | **Missing-at-random vs fill-zero panel handling** | `SyntheticWorld` can emit NaN outcomes (`missing_probability`), but `to_panel_dataset()` uses `fillna(0.0)` (`synthetic_world.py` L77), masking missingness mechanics. | `synthetic_world.py` L198–200, L69–77 |
| 3 | **Null + placebo behavior by inference mode (SCM/TBR)** | Cannot calibrate FPR/coverage for jackknife/placebo/conformal on synthetic truth because recovery runs `inference=None`. | `runner.py` L41–45; `recovery_metrics.py` L101–111 |
| 4 | **Multi-treated / staggered timing for SCM and TBRRidge** | Real geo tests often have multiple treated markets; package open questions in `uncertainty.md`. | Worlds default to one treated start; no `ESTIMATOR_RECOVERY_SCENARIOS` entries for multi-treated |
| 5 | **Estimator-specific estimand equivalence checks** | Need regression of known unit-level ATT vs `_path_relative_att` and vs DID coefficient under controlled DGPs. | No test module asserts truth↔metric alignment per estimator family |

---

## Top 5 estimator improvements

| # | Improvement | Target | Code touchpoints (for future work) |
|---|-------------|--------|-----------------------------------|
| 1 | **Wire `SyntheticDID` into `RecoveryRunner` with panel construction that matches staggered DGP** | SDID | `synthetic_scenarios.py` L36–39; `recovery_runner.py` `_extended_estimator_configs`; align with `synthetic_did_test.py` panel builder |
| 2 | **Run recovery with declared inference modes per estimator** | SCM, TBRRidge, DID | Extend `EstimatorConfig` in recovery battery; populate `ci_lower`/`ci_upper`/`significant` so `aggregate_recovery_metrics` FPR/coverage are finite |
| 3 | **Surface recovery failure diagnostics** | All wired estimators | Replace bare `except Exception` in `_run_simulation` with typed error counts in metadata (still non-blocking) |
| 4 | **Attach counterfactual stability summaries to fit outputs (optional)** | SCM, TBRRidge | `counterfactual_stability_tests.py` already separates stability from inference; hook as optional post-fit diagnostic |
| 5 | **TROP: stable recovery contract** | TROP | Pin tuning in validation (`recovery_runner.py` L55–61) and enforce finite `predicted_effect` or explicit failure reason in metrics export |

---

## Top 5 must-fix before wider production use

| # | Item | Rationale | Evidence |
|---|------|-----------|----------|
| 1 | **Publish and enforce a single target estimand per estimator family** | Without this, ATT paths, DID coefficients, and SCM relative lifts are not comparable across methods or to synthetic truth. | `uncertainty.md` L9–15; `_path_relative_att` vs `DID.treatment_effect` vs catalog text |
| 2 | **Recovery/calibration at scale (≥100 replications) with interval modes used in production** | Current smoke/replication counts cannot support FPR/coverage claims; SCM/TBR recovery lacks inference in default configs. | `test_recovery_runner.py`; `recovery_metrics.py`; `calibration_report.py` consumers |
| 3 | **Close the loop on parallel trends for DID** | Reporting ATT under clear pretrend violation without explicit waiver misstates causal credibility. | `DID.py` pretrend block vs unconditional `treatment_effect` |
| 4 | **Research-only estimators (TROP, SDID, Bayesian\*) excluded or fully validated** | Batch validation skips them (`SKIPPED_ESTIMATORS`); partial wiring invites misuse. | `runner.py` L22; `VALIDATION_COVERAGE.md` |
| 5 | **Validate DGP truth ↔ reported metrics on each family** | Until aligned, internal recovery “success” rates optimize the wrong objective. | `synthetic_world.py` truth; `runner.py` metrics; heterogeneous effect scenarios |

---

## Appendix: counterfactual validity snapshot

| Family | Pre→post stability | Donor / coefficient stability | Parallel trends / drift |
|--------|-------------------|------------------------------|------------------------|
| **SCM** | Pre-period weights; post extrapolation | Donor filter + simplex (`scm.py`); stability tests optional | N/A (not trend-based) |
| **TBR/TBRRidge** | Linear extrapolation of normalized ridge | `RidgeCV` on pre-period (`tbr.py`) | Residual drift test available separately (`run_residual_drift_test`) |
| **DID** | TWFE levels | N/A | Pretrend joint tests + fallback (`DID.py` L401+) |
| **SyntheticDID** | Factor model | Time weights `lam` | Tests assume non-staggered panels |
| **TROP** | Regularized CF surface | Unit/time weights + nuclear penalty | Weak-donor warnings only |

## Appendix: recoverable truths today

| Truth in DGP | Recoverable when | Limits |
|--------------|------------------|--------|
| Configured relative lift on treated unit(s) | Noise moderate; SCM/TBR/DID wired | Misalignment with `_path_relative_att` under heterogeneity |
| Null effect (`recovery_null_effect`) | DID significance path only (partial FPR) | SCM/TBR: `significant=None` |
| Parallel trends hold/violate | DID bias direction in 2 scenarios | Not used to gate estimates |
| Low signal / outliers / seasonality | Family scenarios exist | Low `n_simulations` in tests |
| Sparse donors (TROP) | Sometimes NaN | Not a reliability claim |
| Staggered timing (SDID) | Unit tests only | Recovery not wired; panels not staggered in tests |
