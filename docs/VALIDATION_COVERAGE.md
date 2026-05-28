# Estimator validation coverage matrix

This document is the **source of truth** for which estimators are exercised by in-repo synthetic validation, which are skipped, and what would be required before any `production_safe` promotion. It reflects the code as of package version **0.2.1**.

**Governance:** No estimator is `production_safe`. Nominal calibration eligibility is separate from maturity labels — see registry below and `METHOD_VALIDATION_PLAN.md`.

**Code references:**

| Mechanism | Module |
|-----------|--------|
| Maturity catalog | `panel_exp/method_metadata.py` |
| Batch validation (`EstimatorValidationRunner`) | `panel_exp/validation/runner.py` |
| Monte Carlo recovery (`RecoveryRunner`) | `panel_exp/validation/recovery_runner.py`, `panel_exp/validation/synthetic_scenarios.py` |
| Maturity policy tests | `tests/test_estimator_maturity.py` |
| Recovery tests | `tests/test_recovery_runner.py`, `tests/test_estimator_recovery_smoke.py` |

---

## Coverage matrix

| Estimator | Category | Current maturity | Validation runner support | Recovery runner support | Inference support (catalog) | Optional deps | Known gaps | Required before promotion |
|-----------|----------|------------------|---------------------------|-------------------------|----------------------------|---------------|------------|---------------------------|
| **TBRRidge** | Partially validated | `expert_review` | No (runner uses **`TBR`** config; same `TBRRidge` factory) | Yes — 3 family scenarios (`tbrridge_*`) | point_estimate, UnitJackKnife, JKP, Bayesian†, BlockResidualBootstrap, Conformal, Kfold, TimeSeriesKfold | — | Registry `Bayesian` ≠ full `BayesianTBR` MCMC; smoke/recovery alone insufficient per catalog rationale | Broad recovery battery (≥2 scenarios × ≥50 reps); null FPR/coverage calibration; interval path validated for declared inference mode; full-suite green; external geo benchmark |
| **TBR** | Partially validated | `expert_review` | **Yes** — `default_estimator_configs()` | Yes — 3 scenarios (`tbr_*`; same ridge implementation as TBRRidge) | point_estimate, UnitJackKnife, JKP, Kfold | — | Less in-repo coverage than TBRRidge; prefer TBRRidge for defaults | Same as TBRRidge; align validation runner label with `TBRRidge` or document equivalence |
| **SCM** | Validated | `expert_review` | **Yes** | **Yes** — 3 scenarios (`scm_*`) | point_estimate, UnitJackKnife, JKP, Bayesian†, BlockResidualBootstrap, Conformal, Kfold, Placebo, TimeSeriesKfold | — | scipy optimizer sensitivity; donor count; placebo portability across platforms | Multi-scenario recovery at scale; stable placebo/jackknife CIs; donor diagnostics in review packet |
| **SyntheticControlCVXPY** | Partially validated | `expert_review` | No | No | point_estimate, Kfold, Conformal, BlockResidualBootstrap | **cvxpy**, osqp (transitive) | Not in `EstimatorValidationRunner` or `RecoveryRunner` configs; solver-dependent | Add validation + recovery configs; CVXPY CI path; correlation-filter regression tests extended to recovery |
| **AugSynthCVXPY** | Partially validated | `expert_review` | No | No | point_estimate, Kfold, Conformal | **cvxpy**, osqp (transitive) | No automated synthetic recovery; multi-treated complexity | Recovery scenario family + runner config; stability tests tied to recovery metrics |
| **DID** | Partially validated | `expert_review` | **Yes** — pooled timing (`multiple_treated="pooled"`) | **Yes** — 2 scenarios (`did_parallel_trends_*`); `DID_Bootstrap` recovery config | point_estimate; bootstrap cumulative CI (`DID_Bootstrap`) | — | **Relative ATT interval calibration unsupported** — see DID support matrix below; recovery scores path `relative_att_post` only | Recovery smoke + pretrend contract; bootstrap/cumulative intervals on results; no relative-ATT nominal calibration |
| **SyntheticDID** | Research-only (partial scenarios) | `research_only` | **Skipped** (`SKIPPED_ESTIMATORS`) | **No** — scenarios exist in `ESTIMATOR_RECOVERY_SCENARIOS` but **not** in `_extended_estimator_configs()` | point_estimate | — | Fixture/window limitations in unit tests; calling `RecoveryRunner("SyntheticDID", …)` raises `KeyError` today | Wire recovery + validation configs; stable CI smoke; staggered-timing recovery metrics |
| **AugSynth** | Not validated | `unvalidated` | No | No | point_estimate, Kfold, Conformal | — | No dedicated recovery or validation-runner coverage | Scenario registry + runner config + unit tests comparable to SCM family |
| **BayesianTBR** | Research-only | `research_only` | **Skipped** (listed in `SKIPPED_ESTIMATORS` as `"Bayesian"` if ever added to configs) | No | **Bayesian** (MCMC) | **jax**, **jaxlib**, **numpyro**, **arviz** | Omitted from `EstimatorValidationRunner`; JAX pin required; MCMC cost/convergence | Optional-dep CI matrix; validation runner config; recovery scenarios; convergence diagnostics policy |
| **BayesianTBRHorseShoe** | Research-only | `research_only` | Skipped | No | Bayesian | jax, jaxlib, numpyro, arviz | Same gaps as BayesianTBR | Same as BayesianTBR |
| **TROP** | Research-only (recovery smoke only) | `research_only` | **Skipped** | **Yes** — 2 scenarios (`trop_*`); minimal grid in tests | point_estimate | — | Skipped in batch validation; weak donor warnings; smoke often NaN metrics (`tests/test_recovery_runner.py::test_trop_recovery_smoke`) | Add to validation runner or document permanent skip; stable finite recovery metrics; tuning contract for validation |
| **MTGP** | Not validated | `research_only` | **Skipped** | No | Bayesian | jax, jaxlib, numpyro | Bayesian GP MCMC; experimental runtime | Full validation/recovery wiring + performance budget |

† **Bayesian** on TBRRidge/SCM via inference registry is **not** the same as running `BayesianTBR` / `BayesianTBRHorseShoe` MCMC estimators.

### Also in catalog (not in minimum table above)

| Estimator | Category | Current maturity | Validation runner | Recovery runner |
|-----------|----------|------------------|-------------------|-------------------|
| **TBRAutoSARIMAX** | Not validated | `expert_review` | No | No |

---

## DID interval support matrix

Explicit contract (`did_interval_policy` on `DID.run_analysis` results; `panel_exp/validation/did_interval_policy.py`):

| Capability | Supported |
|------------|-----------|
| Point estimate (recovery path `relative_att_post` via `y` / `y_hat`) | **Yes** |
| Pretrend contract (`did_pretrend_contract`) | **Yes** |
| Bootstrap / cumulative interval (`treatment_ci`, `cumulative_ci`, `cumulative_att`) | **Yes** (absolute / cumulative scale) |
| Relative ATT interval calibration (`relative_att_post` coverage in recovery) | **No** — `did_relative_att_interval_unsupported` |

`DID_Bootstrap` in `RecoveryRunner` remains **ineligible** for `run_nominal_calibration_check` / production nominal calibration. No heuristic scaling of cumulative CIs to relative ATT.

---

## Nominal calibration eligibility (Run 001, post-tightening)

Registry: `panel_exp/validation/nominal_calibration.py` → `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`.

| Config | Relative-ATT nominal calibration | `skip_reason` when requested |
|--------|----------------------------------|------------------------------|
| **SCM_UnitJackKnife** | **Eligible** — null FPR/coverage monitoring only (Run 001); not full operating-characteristic proof (zero power on positive scenario) | — |
| **TBRRidge_BlockResidualBootstrap** | **Removed** — pending bound-ordering fix (inverted `y_lower`/`y_upper` on multi-treated panels) | `brb_bounds_inverted_run001` |
| **TBRRidge_Kfold** | **Removed** — pending multi-treated k-fold support on default `recovery_*` scenarios | `kfold_multi_treated_unsupported_run001` |
| **DID_Bootstrap** | **Ineligible** (policy) | `did_relative_att_interval_unsupported` |

Evidence: `docs/CALIBRATION_RUN_001.md`, `docs/CALIBRATION_FAILURE_ANALYSIS_001.md`, `docs/METHOD_VALIDATION_PLAN.md`.

**SCM advisory notes** (attached to eligible runs): passed null FPR/coverage in Run 001; zero power on positive scenario; Phase 11 (`SCM_JACKKNIFE_CHARACTERIZATION_001.md`) confirms persistent over-coverage and zero power across 144-cell matrix — **null monitoring only**, not lift detection.

**Removed configs (Run 001 + Phase 10):**

| Config | `skip_reason` | Reason (short) |
|--------|---------------|----------------|
| `TBRRidge_BlockResidualBootstrap` | `brb_bounds_inverted_run001` | Inverted path bounds → FPR=1.0 on null |
| `TBRRidge_Kfold` | `kfold_multi_treated_unsupported_run001` | Multi-treated broadcast failure on default `recovery_*` |
| `DID_Bootstrap` | `did_relative_att_interval_unsupported` | Policy: no relative-ATT interval path |

`TBRRidge` point-estimate recovery (`inference=None`) remains available; only **relative-ATT nominal calibration** claims are restricted.

### Unsupported / research estimators (batch validation)

| Estimator | Batch runner | Recovery runner | Notes |
|-----------|--------------|-----------------|-------|
| **SyntheticDID** | Skipped (`SKIPPED_ESTIMATORS`) | No config — `KeyError` | Staggered DGP exists; runner unwired |
| **TROP** | Skipped | Smoke only (`trop_*`) | Often NaN metrics |
| **BayesianTBR / HorseShoe** | Skipped | No | JAX MCMC; `research_only` |
| **MTGP** | Skipped | No | GP MCMC; `research_only` |

---

## 1. What “validated” means in this repo

**Validated** (this document) means **all** of the following:

1. **Listed in the maturity catalog** with explicit assumptions and limitations (`panel_exp/method_metadata.py`).
2. **Included in `EstimatorValidationRunner`** *or* covered by an equivalent, documented alias (e.g. TBR vs TBRRidge factory).
3. **Recovery scenarios** registered in `ESTIMATOR_RECOVERY_SCENARIOS` **and** a working `EstimatorConfig` in `_extended_estimator_configs()` so `RecoveryRunner` can run.
4. **Automated tests** exercise synthetic truth at least at smoke level (`tests/test_estimator_recovery_smoke.py`, `tests/test_recovery_runner.py`, and/or estimator-specific unit tests).
5. Results are **diagnostic only** — they do **not** change catalog maturity labels automatically (`tests/test_estimator_maturity.py::test_production_safe_not_from_smoke_tests_alone`).

**Partially validated** means one or more gaps remain (e.g. unit tests only, recovery without batch validation, or scenarios without runner wiring).

**Research-only** / **not validated** follows catalog `maturity` and the gaps column above.

---

## 2. What is explicitly not validated

The following are **out of scope** for automated in-repo synthetic validation today:

| Item | Reason |
|------|--------|
| **TROP, MTGP, SDID in batch validation** | Hard-coded skip: `SKIPPED_ESTIMATORS = {"TROP", "Bayesian", "MTGP", "SDID"}` in `panel_exp/validation/runner.py` |
| **BayesianTBR / BayesianTBRHorseShoe** | Not in `default_estimator_configs()`; maturity `research_only`; JAX stack optional |
| **AugSynth** | Maturity `unvalidated`; no recovery scenario family |
| **SyntheticControlCVXPY / AugSynthCVXPY** | Strong unit tests (`tests/test_scm.py`, counterfactual stability) but **no** `EstimatorValidationRunner` / `RecoveryRunner` factory entries |
| **SyntheticDID recovery API** | Scenario names exist; **no** `RecoveryRunner` config — not runnable without new wiring |
| **Production decision gates** | Readiness and calibration are **advisory** (`panel_exp/policy/readiness.py`); they do not block runs |
| **Spillover / interference estimation** | Declared in `DesignSpec` only; not empirically estimated |
| **Classical analytic MDE** | `PowerAnalysis` is simulation-coverage-based (`MDE_SEMANTICS` in `panel_exp/design/power.py`) |

---

## 3. Why no estimator is currently `production_safe`

1. **Catalog policy** — `tests/test_estimator_maturity.py` requires **zero** estimators and **zero** inference modes rated `production_safe`; smoke and recovery alone cannot promote maturity.
2. **Explicit catalog text** — e.g. TBRRidge rationale states production-safe status needs broader coverage/FPR/power validation than existing smoke/recovery tests.
3. **Incomplete batch validation** — four registry names are skipped in `EstimatorValidationRunner`; several expert-review estimators never enter the default validation battery.
4. **Inference gaps** — DID and TROP validation wiring use **point_estimate** only; many catalog inference modes are not validated per estimator under synthetic worlds.
5. **Platform and dependency risk** — CVXPY/OSQP and JAX paths have optional-dependency guards but not full recovery matrices.
6. **No external benchmark** — In-repo synthetic worlds are stylized; no committed equivalence study vs published geo-lift reference implementations.

---

## 4. Promotion criteria

Promotion from `expert_review` or `research_only` to **`production_safe`** requires **all** items below (human review still required; maturity is not auto-updated by tests):

| Criterion | Evidence expected |
|-----------|-------------------|
| **Synthetic recovery across scenarios** | Registered scenarios in `ESTIMATOR_RECOVERY_SCENARIOS` **and** working `RecoveryRunner` / validation configs; bias/ATT directionally correct on positive-effect scenarios; acceptable `recovery_success_rate` on family scenarios |
| **Null FPR calibration** | `build_calibration_report` / `RecoveryRunner` on null-effect scenarios; FPR at or below policy thresholds (see `MAX_FALSE_POSITIVE_RATE` in `calibration_report.py` for diagnostics, not gates) with sufficient replications (≥100 recommended for stable calibration) |
| **Interval coverage** | When inference is claimed: `coverage_under_null` and lift-scenario **power** reported; path intervals labeled per `InferenceResult` semantics (not placebo bands mislabeled as CIs) |
| **Documented assumptions** | Catalog `assumptions` and `known_limitations` updated; experiment card / maturity evidence attached for real studies |
| **Stable optional dependency path** | If cvxpy or jax required: pinned versions in `pyproject.toml`, CI job runs `tests/test_jax_optional_deps.py` / CVXPY tests, skip helpers documented |
| **Full-suite regression tests** | `poetry run pytest tests/ -q` green on supported platform; estimator-specific module tests (`test_scm.py`, `trop_test.py`, etc.) maintained |

**Explicit non-criteria:** Passing `RecoveryRunner` with `n_simulations=1`, readiness `ready_with_review`, or a single smoke test is **not** sufficient (`test_production_safe_not_from_smoke_tests_alone`).

---

## Quick reference: runner wiring

### `default_estimator_configs()` (validation runner)

| Config name | Implementation |
|-------------|----------------|
| SCM | `SyntheticControl(inference=None)` |
| TBR | `TBRRidge(inference=None)` |
| DID | `DID()` with `multiple_treated="pooled"` |

### `_extended_estimator_configs()` (recovery runner)

Above **plus** `TBRRidge` (explicit), `TROP` (minimal tuning kwargs in tests).

### `SKIPPED_ESTIMATORS` (validation runner only)

`TROP`, `Bayesian`, `MTGP`, `SDID`

### `ESTIMATOR_RECOVERY_SCENARIOS` keys

`SCM`, `DID`, `TBR`, `TBRRidge`, `SyntheticDID`, `TROP`

---

*Maturity labels remain authoritative in `panel_exp/method_metadata.py`. This matrix only describes validation machinery and tests.*
