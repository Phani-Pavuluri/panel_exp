# panel_exp roadmap v3 (post interval/DGP cleanup)

**Status:** frozen (execution order in `docs/ROADMAP_V3_EXECUTION_ORDER.md`)  
**Last reviewed:** 2026-05-20  
**Supersedes:** `docs/ROADMAP_V2.md` (priority ordering and open gates)  
**Inputs:**

| Document | Role |
|----------|------|
| `docs/ROADMAP_V2.md` | Prior tiering, PR list, success criteria |
| `docs/ALGORITHM_REASSESSMENT.md` | Original risk inventory (partially closed) |
| Recent validation work | Commits through `d209f9b` (estimand alignment, interval gating, nominal calibration smoke, DGP semantics) |

**Package version:** 0.2.1  
**Read-only roadmap — no package code in this change.**

---

## 1. Executive verdict

### Has overall confidence improved since v2?

**Yes — statistical confidence is modestly up; operational confidence unchanged.**

v2 correctly flagged a **split verdict**: strong auditability but weak calibration readouts. Since v2, work focused on **measurement honesty** (what is scored, what intervals mean, what the DGP actually does) rather than new estimators or artifact surface.

| Layer | v2 | v3 (now) |
|-------|-----|----------|
| **Estimand ↔ recovery scoring** | Assumed misaligned | **Explicit** — `RELATIVE_ATT_POST` via `_path_relative_att`; tests in `tests/test_estimand_metric_alignment.py` |
| **Inference in recovery** | SCM/TBR mostly `inference=None`; FPR/coverage NaN | **Inference configs wired** (`SCM_UnitJackKnife`, `TBRRidge_Kfold`, `TBRRidge_BlockResidualBootstrap`, `DID_Bootstrap`) with failure typing |
| **Interval ↔ point estimand** | Heuristic DID `treatment_ci` scaling; path bounds mixed | **Gated** — coverage/FPR only when `interval_estimand == relative_att_post`; DID cumulative CI marked mismatch (`recovery_intervals.py`) |
| **Nominal calibration** | None at scale | **Smoke helper** — `run_nominal_calibration_check()`; eligible configs only; documents n&lt;100 as non-production |
| **DGP missingness** | Silent `fillna(0)` | **Explicit policies** (`none`, `fill_zero`, `drop`, `error`); calibration scenarios use `none`; missing scenarios opt into `fill_zero` |
| **Staggered timing** | Fake `staggered_declared`, one `treatment_start` | **Real per-unit starts** for `sdid_staggered_adoption`; renamed misleading scenarios |
| **DID pretrends** | Metadata only | **Contract** on results (`did_pretrend_contract`); warn/fail + waiver path (`tests/test_did_pretrend_contract.py`) |
| **Estimator diagnostics** | N/A | **Opt-in review API** (`build_estimator_review`) — not in default `results` keys |

**Still not true:** unattended production certification, nominal coverage at n≥100 for all core modes, SDID/TROP/Bayesian validation, spillover estimation, or blocking readiness gates.

---

## 2. What risks were reduced

Mapped to `ALGORITHM_REASSESSMENT.md` and v2 must-fix list. **Implemented behavior** (not merely documented).

| Risk area | What changed | Evidence |
|-----------|--------------|----------|
| **Truth ↔ recovery score misalignment (homogeneous / pooled paths)** | Single scored estimand; canonical truth tests; DID pooled path tests | `recovery_runner.SCORED_TARGET_ESTIMAND`, `tests/test_estimand_metric_alignment.py` |
| **Recovery without inference (FPR/coverage unobserved)** | Inference-enabled recovery configs; metrics with `coverage_status` / `false_positive_rate_status` | `recovery_runner._inference_recovery_configs`, `tests/test_recovery_inference_calibration.py` |
| **Silent recovery failures** | Typed `failure_type` / `failure_message` on `SimulationRecord` | `recovery_runner._run_simulation` |
| **Mismatched interval coverage (DID cumulative vs relative ATT)** | No coverage against relative truth when interval estimand mismatches | `recovery_intervals.py`, `tests/test_recovery_estimand_interval_alignment.py` |
| **False calibration from mis-scaled DID intervals** | `DID_Bootstrap` coverage unavailable with explicit reason | Same |
| **Aligned-interval smoke without production claims** | `run_nominal_calibration_check` + small-n warnings | `nominal_calibration.py`, `tests/test_nominal_calibration_check.py` |
| **Silent missingness (`fillna(0)`)** | Explicit policy; calibration scenarios avoid fill-zero; missing scenarios declare `fill_zero` | `synthetic_world.py`, `tests/test_synthetic_dgp_semantics.py` |
| **Fake staggered DGP names** | Per-unit `treatment_start_by_unit`; `staggered_treatment_supported` metadata | `sdid_staggered_adoption`, `tests/test_synthetic_dgp_semantics.py` |
| **DGP stress scenarios unwired** | Collinearity, structural break, missingness, multi-treated in SCM/TBR batteries | `synthetic_scenarios.py`, `tests/test_synthetic_dgp_hardening.py` |
| **DID pretrend violation without reviewer signal** | Pretrend contract + optional waiver | `DID.py`, `tests/test_did_pretrend_contract.py` |
| **Diagnostics polluting legacy result contracts** | `estimator_diagnostics` opt-in only | `build_estimator_review`, commit `c002772` |

### Risks partially reduced (do not over-claim)

| Area | Limit |
|------|--------|
| **Heterogeneous multi-treated truth vs pooled scoring** | Tests document divergence; aggregation rules not unified |
| **Nominal calibration** | Plumbing + eligibility gates; **not** n≥100 threshold enforcement in CI |
| **DID pretrends** | Warn/fail contract — **ATT still exported** unless human applies waiver discipline |
| **SCM post-period extrapolation** | Stability tests exist but **not** default post-fit hook |
| **Power null DGP vs recovery null** | Still separate worlds (`power.py` vs `recovery_null_effect`) |

---

## 3. What remains unresolved

Prioritized for **algorithm/statistical validity** only.

| # | Remaining risk | Why it still matters |
|---|----------------|----------------------|
| 1 | **No production-scale nominal calibration (n≥100)** | Smoke runs use n≈2–6; `MIN_REPLICATIONS_FOR_STABLE_CALIBRATION=100` is advisory only |
| 2 | **DID intervals not aligned with scored relative ATT** | Correctly gated — but DID production inference still not calibratable in recovery until a relative-ATT interval path exists |
| 3 | **Multi-treated / heterogeneous estimand aggregation** | Pooled `_path_relative_att` vs unit×time canonical truth can diverge |
| 4 | **Spillover in DGP, not in estimators** | `scm_donor_contamination` stresses fits; no spillover term in SCM/TBR/DID |
| 5 | **SCM/TBR counterfactual stability not default** | `counterfactual_stability_tests.py` optional; pre→post weight drift unmonitored in normal runs |
| 6 | **SDID / TROP / Bayesian not recovery-validated** | SDID DGP stagger now honest; **RecoveryRunner** still has no SDID config; TROP/Bayesian skipped |
| 7 | **Power analysis null ≠ recovery null** | A/A power readouts and recovery FPR not comparable without unified null world |
| 8 | **Placebo vs CI interpretation** | Semantics documented in inference layer; user misuse still possible when strict mode off |
| 9 | **TBRRidge k-fold / BRB heuristic SEs** | Documented adaptations; not paper-exact; eligible for smoke only when path intervals align |
| 10 | **Structural-break scenario not scored in recovery assertions** | Scenario wired; no bias/recovery failure thresholds tied to break |

---

## 4. Approved execution order (Phases 5–8)

**Frozen:** see [`docs/ROADMAP_V3_EXECUTION_ORDER.md`](ROADMAP_V3_EXECUTION_ORDER.md) for objectives, acceptance criteria, dependencies, CI impact, blockers, and deferred work. **Do not implement** until that sequence is explicitly picked up in a phase-scoped PR.

**Sequence:** Phase 5 (production calibration) → Phase 6 (DID interval policy) → Phase 7 (review flags) → Phase 8 (focused re-audit).

**Phase 5 status:** `run_production_nominal_calibration()` in `panel_exp/validation/production_nominal_calibration.py` — production defaults n=100, seeds (0,1,2); CI uses small n via tests only.

**Scope lock:** no new estimators, inference modes, or artifacts in Phases 5–8.

---

## 4a. Top 3 next PRs (maps to Phases 5–7)

Ordered by **validity per engineering week**. Specs only — no code here.

### PR 1 — Production-scale nominal calibration job (aligned configs only) → **Phase 5**

| Dimension | Detail |
|-----------|--------|
| **Goal** | Run `run_nominal_calibration_check` (or RecoveryRunner) at **n≥100** for `SCM_UnitJackKnife`, `TBRRidge_Kfold`, `TBRRidge_BlockResidualBootstrap` on `recovery_null_effect` and `recovery_positive_effect`; report FPR, coverage, power against `calibration_report.py` thresholds |
| **Risk reduced** | v2 statistical #6–7; must-fix #2 |
| **Out of scope** | `DID_Bootstrap` until relative-ATT intervals exist |
| **Validation** | Nightly or manual job artifact; assert FPR ≤ 0.10, coverage ≥ 0.90 on null **or** explicit “insufficient n / failed” — not NaN silence |

### PR 2 — Relative-ATT interval path for DID (or exclude DID from interval calibration claims) → **Phase 6**

| Dimension | Detail |
|-----------|--------|
| **Goal** | Either (a) export/bootstrap a **relative post-period ATT** interval comparable to `_path_relative_att`, or (b) permanently document DID as **point-estimate-only** in recovery calibration with separate cumulative-ATT reporting |
| **Risk reduced** | Interval estimand mismatch (now gated but blocks DID calibration entirely) |
| **Validation** | `DID_Bootstrap` becomes eligible for nominal check **only if** (a); else card/calibration docs state cumulative scale |

### PR 3 — Default optional counterfactual stability summary (SCM/TBRRidge, point inference only) → **Phase 7**

| Dimension | Detail |
|-----------|--------|
| **Goal** | After `run_analysis`, `build_estimator_review(..., attach=False)` includes pre-period residual drift / donor weight health flags when `inference in {None, self}` — still **no** change to default `results` keys |
| **Risk reduced** | Algorithm correctness #6; pre→post extrapolation blind spot |
| **Validation** | Flags on `scm_structural_break` / `scm_trend_mismatch`; no estimator math change |

**Dropped from v2 “top 5” as standalone PRs (delivered or absorbed):**

- PR 1 v2 (estimand alignment tests) → **shipped**
- PR 2 v2 (inference recovery configs) → **shipped** (scale remains PR 1 above)
- PR 3 v2 (DGP hardening) → **shipped** (missingness + stagger semantics)
- PR 4 v2 (DID pretrend contract) → **shipped**
- PR 5 v2 (stability hook) → **folded into PR 3 v3**

---

## 5. Items removed from roadmap

Stop scheduling these as near-term statistical-validity work.

| Removed item | Reason |
|--------------|--------|
| **“Add estimand alignment tests”** | Done (`test_estimand_metric_alignment.py`) |
| **“Wire inference modes into recovery”** | Done; scale is separate calibration job |
| **“Fix fillna(0) silently”** | Done — explicit `missingness_policy` + metadata |
| **“Rename/fix fake staggered scenarios”** | Done — `sdid_staggered_adoption` + per-unit starts |
| **“Add DID pretrend metadata”** | Done — pretrend contract |
| **“Auto-attach estimator_diagnostics on every run”** | Rejected — opt-in review workflow shipped |
| **“Add VALIDATION_COVERAGE.md”** | Already shipped in v1/v2 |
| **“Inference recovery for DID via scaled cumulative CI”** | Removed as approach — gated as mismatch; needs PR 2 v3 instead |
| **More experiment-card / bundle / readiness schema versions** | Out of scope for validity roadmap |
| **`production_safe` promotions** | Still no estimator meets promotion bar |
| **Automated blocking readiness** | Inputs now honest but not yet at n≥100 calibration |
| **Jackknife+ / time Jackknife+** | Deferred until baseline modes calibrated at scale |
| **Consensus ATT across estimators** | Estimands still not fully unified under heterogeneity |

---

## 6. Success criteria before next audit

**Next algorithm/statistical mini-audit** should run only after these are measurable — not merely coded.

### 6.1 Must pass (gate)

| # | Criterion | Target |
|---|-----------|--------|
| 1 | **Aligned-interval calibration at scale** | For each of `SCM_UnitJackKnife`, `TBRRidge_Kfold`, `TBRRidge_BlockResidualBootstrap`: on `recovery_null_effect` with n≥100, `coverage_status=computed` and coverage ∈ [0.85, 0.95] (or documented simulator misspecification); FPR ≤ 0.10 |
| 2 | **Positive-scenario power** | Same configs on `recovery_positive_effect` at n≥100: `power_status=computed` and power ≥ 0.80 (or explicit failure code) |
| 3 | **No silent interval mismatch coverage** | Zero recovery payloads with finite `coverage` when `interval_estimand != relative_att_post` |
| 4 | **Calibration scenarios clean missingness** | `recovery_null_effect` / `recovery_positive_effect` metadata: `missingness_policy=none`, no fill-zero warning on `to_panel_dataset()` |
| 5 | **Staggered honesty** | No active scenario name implies stagger unless `staggered_treatment_supported=true` and ≥2 distinct `treatment_start_by_unit` values |
| 6 | **Full test suite** | `poetry run pytest tests/ -q` green |

### 6.2 Should pass (strong signal)

| # | Criterion | Target |
|---|-----------|--------|
| 7 | **Heterogeneous-effect documentation** | Test or doc states when pooled scoring ≠ unit-level canonical truth |
| 8 | **DID policy** | Pretrend violation scenario triggers contract `fail` or `warn`; waiver path tested |
| 9 | **Stability review available** | `build_estimator_review` returns drift/donor flags for SCM/TBRRidge on structural-break scenario |
| 10 | **Recovery failure rate** | &lt;5% failed sims without `failure_type` on core battery at n≥50 |

### 6.3 Explicit non-goals (unchanged)

- `production_safe` catalog labels  
- Automated business go/no-go on readiness alone  
- SDID/TROP/Bayesian as default recommended estimators without full recovery wiring  
- Spillover-adjusted ATT in core estimators  
- Unattended “certified causal effect” language in user-facing docs  

### 6.4 Audit questions for v4 → **Phase 8**

When re-running assessment (focused mini-audit only; see execution order doc), answer:

1. Did n≥100 calibration runs happen and get archived?  
2. Is DID either calibratable on relative ATT or explicitly excluded from interval claims?  
3. Did any new code re-introduce silent `fill_zero` on calibration scenarios?  
4. Are FPR/coverage/power still computed from significance flags on mismatched estimands anywhere?  

---

## Appendix: v2 → v3 PR map

| v2 PR | v3 status |
|-------|-----------|
| PR 1 Estimand + equivalence tests | **Done** |
| PR 2 Recovery inference + failure typing | **Done** (scale → v3 PR 1) |
| PR 3 DGP hardening | **Done** (missingness + stagger) |
| PR 4 DID pretrend contract | **Done** |
| PR 5 Stability + CVXPY recovery | **Partial** → v3 PR 3 |
| *(new)* Interval estimand gating | **Done** (`f1a276c`) |
| *(new)* Nominal calibration smoke | **Done** (`458c534`) |
| *(new)* Opt-in diagnostics | **Done** (`c002772`) |

---

*Roadmap frozen for Phases 5–8 execution order. Supersedes v2 priority ordering for statistical work; does not modify estimator code or maturity labels. Implementation: `docs/ROADMAP_V3_EXECUTION_ORDER.md`.*
