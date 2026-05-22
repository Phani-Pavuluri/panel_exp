# Documentation drift audit

**Date:** 2026-05-20  
**Package version:** 0.2.1  
**Scope:** README, hosted user guide, examples, `docs/`, public API vs implementation.

This report informed the documentation truth PR. Hosted HTML under `gh-pages/` is generated from `gh-pages/_sources/user_guide.md.txt`.

---

## Summary

| Severity | Count (approx.) |
|----------|-----------------|
| High | 8 |
| Medium | 12 |
| Low | 6 |

Primary drift: long legacy user-guide body (dashboard / pretest workflows), classical-power wording, and `power_analysis.run_analysis()` shown as returning a results dict.

---

## Mismatch register

| Claim | Location | Actual code behavior | Severity | Fix |
|-------|----------|----------------------|----------|-----|
| `panel_exp.pretest_analysis` usable API | `examples/dev_notebooks/pretest_analysis_example.ipynb`, `examples/test_design_notebooks/fy24q1_test_designs.ipynb` | Module **not shipped** (`tests/test_public_api.py`) | High | Legacy banner in `examples/README.md`; user guide already warns |
| `panel_exp.util` import | Dev notebooks, `scripts/*.ipynb` | **`panel_exp.util` removed**; use `panel_exp.methods.bayesian_regression` or `panel_exp.utils.*` | High | Documented in README / user guide code-truth |
| `create_design_comparison_dashboard` as standard workflow | `user_guide.md.txt` § GeoExperimentDesign, § End-to-End | Lives in **`panel_exp.utils.test_designs_evaluation`** (internal); not wheel quickstart | Medium | Legacy banner on dashboard sections |
| `generate_cv_fit_plots` without context | User guide design comparison block | Utils helper; optional internal tooling | Low | Legacy banner |
| `power_analysis.run_analysis()` returns dict with `mde_percent` | User guide Power Analysis snippet | **`run_analysis()` returns `None`**; MDE on `PowerAnalysis` attributes (`mde_percent`, `mde_semantics`, `power_contract`) | High | Banner + corrected snippet in guide |
| “Determines probability of detecting true effects” (classical power) | User guide Power Analysis metrics | **Simulation coverage** threshold; `classical_power: False` in `MDE_SEMANTICS` | High | Wording aligned to simulation contract |
| “Reliably detected” MDE | Older user-guide phrasing (partially fixed) | MDE is grid coverage threshold, not guarantee | Medium | Already updated in places; banner on legacy blocks |
| All designs via `GeoExperimentDesign.run_design` | User guide implies universal orchestration | Only **5** base randomizers geo-run supported (`GEO_RUN_DESIGN_SUPPORTED`) | Medium | Code-truth table retained at top |
| QuickBlock / MatchedPair via geo-run | Some narrative examples | **`ValueError`** if selected as `base_randomizer_cls` | Medium | Code-truth + legacy banners |
| `from panel_exp.methods import TBRRidge` | User guide snippets | Works via lazy `panel_exp.__getattr__` for SCM/TBR/TBRRidge only; prefer `panel_exp.methods.tbr` | Low | Note in code-truth |
| Production-ready / automated approval | Marketing-style overview prose | **No `production_safe` estimators**; readiness is **advisory** | High | Code-truth “Not implemented” |
| Spillover estimation | Implied by interference fields only | **`spillover_estimation_available: False`** in evidence metadata | Medium | Listed under Not implemented |
| Experiment card always means power was run | User concern (post power-contract work) | Card shows **interpretation rules** vs **power results attached** separately | Low | Documented in user guide |
| Run bundle in decision chain | README partial | **`build_run_artifact_bundle`** exists; not in older guide flow | Low | Add to decision workflow diagram |
| Validation coverage matrix | Not linked from README | **`docs/VALIDATION_COVERAGE.md`** exists | Low | Add doc links |
| Time-varying coefficients / causal drift | Not in API | **Not implemented** | Low | Listed under Not implemented |
| Bayesian inference “production” path | Some examples use `BayesianTBR` casually | Catalog **`research_only`** | Medium | Research-only list in code-truth |

---

## Aligned claims (no change required)

- No estimator rated `production_safe` in catalog (`tests/test_estimator_maturity.py`).
- `PowerAnalysis` simulation MDE and `power_contract` metadata.
- Explicit inference interval types (`InferenceResult` / `IntervalType`).
- `RecoveryRunner`, `build_calibration_report`, `build_readiness_assessment` advisory only.
- `build_experiment_card` / `build_run_artifact_bundle` additive artifacts.

---

## Related documents

- [VALIDATION_COVERAGE.md](./VALIDATION_COVERAGE.md) — estimator validation matrix  
- [ROADMAP_REASSESSMENT.md](./ROADMAP_REASSESSMENT.md) — roadmap and gaps  
- [../examples/README.md](../examples/README.md) — notebook / script index  
