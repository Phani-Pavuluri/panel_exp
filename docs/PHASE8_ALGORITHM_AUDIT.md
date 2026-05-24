# Phase 8 — Focused algorithm re-audit

**Date:** 2026-05-20  
**Scope:** Statistical validity after Phases 1–7 (estimand alignment through review flags). Read-only; no code changes.  
**Package version:** 0.2.1  
**Inputs:** `docs/ROADMAP_V3.md`, `docs/ALGORITHM_REASSESSMENT.md`, `docs/VALIDATION_COVERAGE.md`, commits on `estimator-maturity-metadata` through `aec27bc`.  
**Test run at audit:** `poetry run pytest tests/ -q` → **651 passed, 2 skipped** (2026-05-20).

This audit answers whether the package is **statistically more trustworthy** for expert-review use—not a module-by-module architecture review.

---

## 1. Executive verdict

**Confidence: improved (narrowly), not production-ready.**

Phases 1–7 materially improved **measurement honesty**: what is scored, what intervals mean, what the DGP does, and what reviewers can see. The package is **more auditable and less likely to silently mis-report calibration** than at the time of `ALGORITHM_REASSESSMENT.md`.

**Why improved**

- Single recovery scoring estimand (`relative_att_post`) with tests; mismatched interval coverage is gated, not scaled.
- Inference-enabled recovery configs exist; failure typing replaced silent NaN-only failures.
- DGP semantics (missingness, stagger) are explicit; calibration scenarios avoid silent fill-zero.
- DID pretrend and interval policies are on-results contracts, not hidden conversions.
- Review flags and diagnostics are opt-in and family-classified.

**Why not “production-ready”**

- **No archived n≥100 nominal calibration run** has been executed in CI or committed as evidence.
- Heterogeneous/multi-treated estimand aggregation, spillover, and research-only estimators (SDID/TROP/Bayesian) remain weak or unwired.
- DID still exports ATT under pretrend violation unless humans enforce waiver discipline.
- Maturity remains `expert_review` / `research_only`; zero `production_safe` labels by policy.

**Operational confidence:** largely **unchanged**—diagnostics and flags require explicit review calls; nothing blocks bad runs automatically.

---

## 2. What risks were actually reduced

Evidence is tied to shipped code and tests (not roadmap text alone).

| Risk (from reassessment / v2) | Reduction | Evidence |
|-------------------------------|-----------|----------|
| Truth ↔ recovery score misalignment (pooled paths) | **Reduced** | `recovery_runner.SCORED_TARGET_ESTIMAND`, `runner._path_relative_att`; `tests/test_estimand_metric_alignment.py` |
| Recovery without inference → FPR/coverage unobserved | **Reduced** | `recovery_runner._inference_recovery_configs`; `tests/test_recovery_inference_calibration.py` |
| Silent recovery failures | **Reduced** | `SimulationRecord.failure_type` / `failure_message`; `tests/test_recovery_inference_calibration.py::test_failed_simulation_records_failure_metadata` |
| DID cumulative CI counted as relative ATT coverage | **Removed** | `recovery_intervals.extract_recovery_interval` → `did_relative_att_interval_unsupported`; `tests/test_recovery_estimand_interval_alignment.py`, `tests/test_did_interval_policy.py` |
| False calibration from scaled DID intervals | **Removed** | No recovery path uses `runner._relative_ci` for DID; `tests/test_did_interval_policy.py::test_no_relative_ci_scaling_used_in_recovery_path` |
| Silent `fillna(0)` on calibration worlds | **Reduced** | `synthetic_world.missingness_policy`; `tests/test_synthetic_dgp_semantics.py` |
| Fake staggered scenario names | **Reduced** | `treatment_start_by_unit`, `sdid_staggered_adoption`; `tests/test_synthetic_dgp_semantics.py` |
| DGP stress scenarios unwired | **Reduced** | Collinearity, structural break, missingness in batteries; `tests/test_synthetic_dgp_hardening.py` |
| DID pretrend invisible to reviewers | **Reduced** | `DID.run_analysis` → `did_pretrend_contract`; `tests/test_did_pretrend_contract.py` |
| Diagnostics breaking legacy result keys | **Avoided** | Opt-in `build_estimator_review`; `tests/test_estimator_diagnostics.py::test_default_run_analysis_omits_estimator_diagnostics` |
| Nominal calibration eligibility ambiguous | **Reduced** | `nominal_calibration.NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`, `run_production_nominal_calibration`; `tests/test_nominal_calibration_production.py` |
| DID interval policy implicit | **Reduced** | `did_interval_policy` on results + `VALIDATION_COVERAGE.md` matrix; `tests/test_did_interval_policy.py` |
| Stability risks passive only | **Partially reduced** | `review_flags.classify_review_flag_support`, `collect_review_flags`; `tests/test_review_flags.py` (structural break → `residual_drift` warn/fail) |

---

## 3. What risks remain

### Statistical risks

| Risk | Status |
|------|--------|
| **No demonstrated nominal calibration at n≥100** | **Open** — harness exists (`production_nominal_calibration.py`); no production-tier artifact |
| **TBRRidge_Kfold on multi-geo `recovery_null_effect`** | **Open** — smoke runs can fail all reps (`interval_not_aligned`); geometry not fully characterized |
| **Heterogeneous effects vs pooled `_path_relative_att`** | **Open** — documented divergence only |
| **Power null DGP ≠ recovery null DGP** | **Open** — separate systems (`power.py` vs `recovery_null_effect`) |
| **Jackknife/BRB SE geometry under few donors** | **Open** — documented; no automated guards at small n_geos |
| **Finite-sample metrics from n=2–6 in CI** | **Open** — unstable FPR/coverage point estimates in smoke |

### Causal risks

| Risk | Status |
|------|--------|
| **DID ATT exported under pretrend violation** | **Open** — contract warns/fails but does not block (`DID.py`) |
| **DID relative ATT intervals unsupported** | **Accepted policy** — cumulative/bootstrap only; not a bug if documented |
| **Spillover in DGP, not in estimators** | **Open** — `scm_donor_contamination` stresses; no spillover estimation |
| **Pooled DID vs unit-level heterogeneous lift** | **Open** |
| **Placebo vs CI misuse** | **Open** — semantics in `inference_result.py`; strict mode optional |

### Implementation risks

| Risk | Status |
|------|--------|
| **SDID / TROP / Bayesian recovery unwired or skipped** | **Open** — `SKIPPED_ESTIMATORS`, no `RecoveryRunner` for SDID |
| **SCM post-period extrapolation unstability** | **Partial** — review flags opt-in; not default |
| **Recovery still swallows some run failures as NaN** | **Reduced** — typed failures when exception path hit; non-finite estimate still a soft fail |
| **TROP sparse panels → NaN recovery metrics** | **Open** — smoke tolerated |

### Operational risks

| Risk | Status |
|------|--------|
| **Review flags/diagnostics require manual opt-in** | **By design** — easy to skip in production workflows |
| **No nightly n≥100 calibration job** | **Open** |
| **No automated go/no-go on calibration thresholds** | **By design** — status rules are advisory (`production_nominal_calibration` pass/warn/fail) |

---

## 4. Evidence quality

### What tests prove (today)

| Claim | Evidence |
|-------|----------|
| Recovery scores `relative_att_post` consistently | `tests/test_estimand_metric_alignment.py` |
| Interval coverage gated on `interval_aligned` / `relative_att_post` | `tests/test_recovery_estimand_interval_alignment.py` |
| DID bootstrap not nominal-eligible; no relative CI in recovery | `tests/test_did_interval_policy.py`, `tests/test_nominal_calibration_check.py` |
| Inference recovery configs produce finite or explicit-unavailable metrics | `tests/test_recovery_inference_calibration.py` |
| DGP missingness/stagger semantics | `tests/test_synthetic_dgp_semantics.py`, `tests/test_synthetic_dgp_hardening.py` |
| DID pretrend contract present and waiver-tested | `tests/test_did_pretrend_contract.py` |
| Production calibration **harness** (aggregation, status rules, eligibility) | `tests/test_nominal_calibration_production.py` (n=3–5, seeds 0–1) |
| Review flags family classification + structural-break signal | `tests/test_review_flags.py` |
| Full regression suite green | **651 passed**, 2 skipped (this audit) |

### What tests do **not** prove

| Claim | Gap |
|-------|-----|
| Nominal FPR ≤ 0.10 and coverage ≥ 0.90 at scale | No n≥100 run archived |
| Power ≥ 0.80 on positive scenarios at scale | Same |
| Seed-stable operating characteristics | Multi-seed tested only at n≤5 |
| TBRRidge_Kfold calibration on default recovery null panel | Known failure mode at small n |
| External/geo benchmark equivalence | Not in repo |
| Bayesian / SDID / TROP production inference validity | Skipped or smoke-only |
| Review flags prevent bad decisions | Flags are non-blocking metadata |

### Has n≥100 calibration actually been run?

**No.** `run_production_nominal_calibration()` defaults to `n_simulations=100` and `random_seeds=(0,1,2)`, but **CI and audit pytest use n=3–5 only** (`tests/test_nominal_calibration_production.py`). No nightly/manual job output is checked into the repo. Phase 5 hard blocker **B1** from `ROADMAP_V3_EXECUTION_ORDER.md` is **not met**.

---

## 5. Audit questions (Phases 1–7)

| # | Question | Verdict |
|---|----------|---------|
| 1 | **Estimand correctness improved?** | **Partial / yes for pooled path** — explicit scoring + tests; heterogeneous aggregation still open |
| 2 | **Interval calibration credibility improved?** | **Partial** — honesty and gating yes; **demonstrated** calibration at scale **no** |
| 3 | **DGP realism improved?** | **Yes (modest)** — explicit missingness/stagger/stress scenarios; still stylized synthetic worlds |
| 4 | **DID causal-safety improved?** | **Partial** — pretrend contract + interval policy; ATT still exported; relative intervals unsupported by policy |
| 5 | **Diagnostics actionable?** | **Partial / yes when opted in** — `review_flags` + `estimator_diagnostics`; not default |
| 6 | **Recovery/calibration too weak for production claims?** | **Yes** — smoke n, missing n≥100 proof, research-only gaps |

---

## 6. Remaining blockers before wider expert-review rollout

These block **strong statistical claims** and **production-style certification**—not necessarily careful expert-review use with human checks.

1. **Execute and archive n≥100 nominal calibration** for `SCM_UnitJackKnife`, `TBRRidge_BlockResidualBootstrap` (and characterize `TBRRidge_Kfold` panel geometry or alternate scenario).
2. **Document heterogeneous-effect limits** where pooled `_path_relative_att` ≠ canonical unit×time truth.
3. **Human workflow** for DID pretrend `fail` / waiver (already on results; needs process, not code).
4. **Clarify TBRRidge k-fold recovery eligibility** on default multi-geo calibration panels.
5. **Keep research-only estimators** (SDID, TROP, Bayesian) out of default recommended paths until wired/skipped policy is explicit in study docs.

---

## 7. Recommended next 3 PRs only

Ordered by validity per engineering week (specs only—no implementation in this audit).

### PR 1 — Run and archive production nominal calibration (n≥100, multi-seed)

- Execute `run_production_nominal_calibration()` at n=100–300, seeds (0,1,2) for aligned configs on null/positive scenarios.
- Store JSON/CSV artifact (nightly or manual); document pass/fail against `calibration_report.py` thresholds.
- **Risk reduced:** reassessment #6–7; Phase 5 blocker B1.

### PR 2 — Heterogeneous / multi-treated estimand documentation + targeted tests

- Document when pooled `_path_relative_att` diverges from `synthetic_world` canonical truth; add controlled DGP tests (no estimator math change).
- **Risk reduced:** reassessment #1; v3 unresolved #3.

### PR 3 — TBRRidge k-fold recovery characterization (or scenario fix)

- Either fix/ document panel requirements for `TBRRidge_Kfold` on `recovery_null_effect`, or add a single-treated calibration scenario wired to k-fold.
- **Risk reduced:** ambiguous calibration eligibility for one of three aligned configs.

---

## 8. Stop list

Do **not** schedule as near-term statistical-validity work (unchanged from `ROADMAP_V3_EXECUTION_ORDER.md` deferred list):

- BayesianTBR / MCMC expansion  
- TROP productionization or validation-runner wiring  
- SyntheticDID / SDID recovery wiring without dedicated design  
- `production_safe` maturity promotions  
- Automated blocking readiness / go-no-go gates  
- Spillover estimation in core estimators  
- New inference modes (Jackknife+, etc.)  
- DID relative-ATT intervals via cumulative-CI scaling  
- More experiment cards, bundles, or readiness schema versions  
- Large architecture/governance re-audit (this doc replaces that for validity)

---

## 9. Updated go/no-go recommendation

| Use case | Recommendation |
|----------|----------------|
| **Internal expert-review experiments** (SCM/TBRRidge/DID with human review of pretrend + review flags) | **Go with caveats** — statistically more trustworthy than pre–Phase 1; use opt-in `build_estimator_review(..., attach_review_flags=True)` |
| **Claiming nominal interval calibration / FPR control** | **No-go** until n≥100 artifacts exist |
| **DID interval calibration on relative ATT** | **No-go** — explicit unsupported policy (`did_relative_att_interval_unsupported`) |
| **Default production / unattended certification** | **No-go** — maturity policy unchanged; no `production_safe` |
| **SDID / TROP / Bayesian as default recommended estimators** | **No-go** |
| **Wider rollout without calibration archive** | **Conditional go** — only if studies document estimand limits, DID pretrend status, and skip research-only methods |

**Summary:** Phases 1–7 improved **trustworthiness of what we measure and report**. They did **not** complete **trustworthiness of operating characteristics at production replication scale**. The next gate is evidence, not more plumbing.

---

*Phase 8 focused audit. Supersedes informal “confidence improved” claims for production calibration until n≥100 artifacts exist.*
