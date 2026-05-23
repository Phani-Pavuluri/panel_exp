# panel_exp roadmap v2 (post–algorithm audit)

**Status:** living document  
**Last reviewed:** 2026-05-20  
**Supersedes priorities in:** `docs/ROADMAP_REASSESSMENT.md` (architecture/governance lens)  
**Inputs:**

| Document | Role |
|----------|------|
| `docs/ROADMAP_REASSESSMENT.md` | v1 verdict, policy layers, original top-5 PRs |
| `docs/VALIDATION_COVERAGE.md` | Estimator × runner × recovery wiring truth |
| `docs/ALGORITHM_REASSESSMENT.md` | Causal/statistical risks, DGP gaps, must-fix list |

**Package version:** 0.2.1  
**Do not treat this file as modifying estimator code or maturity labels.**

---

## 1. Executive verdict

### Has overall confidence improved or worsened?

**Split verdict — operational confidence up slightly; statistical confidence down.**

| Layer | v1 (ROADMAP_REASSESSMENT) | v2 (after algorithm audit) |
|-------|---------------------------|----------------------------|
| **Auditability** | Improved via maturity, cards, readiness, bundles | **Maintained** — estimand/interference/power contracts and doc-truth tests now exist (`spec.py`, `evidence.py`, `tests/test_estimand_contract.py`, `tests/test_interference_review.py`, `tests/test_power_contract.py`, `tests/test_docs_code_truth.py`) |
| **Claimed validation strength** | “B” recovery framework, incomplete coverage | **Downgraded in practice** — recovery smoke uses `n_simulations=1–6`; SCM/TBR recovery runs `inference=None`, so FPR/coverage/power are often **NaN** (`recovery_metrics.py`, `ALGORITHM_REASSESSMENT` §statistical risks #6–7) |
| **Core estimator trust** | B+ SCM/TBR/DID with expert review | **Unchanged math, sharper limits** — estimand mismatch, spillover in DGP but not models, DID pretrends non-blocking, silent recovery failures |
| **Production readiness** | Expert-review tool; not self-certifying | **Still expert-review** — algorithm audit adds five explicit must-fix gates before “wider production use” |

**Net:** Confidence in **using panel_exp as a disciplined review platform** is slightly **better** (contracts + documented coverage matrix). Confidence in **trusting recovery/calibration readouts or cross-estimator ATT comparability** is **worse** because gaps are now quantified and some were previously assumed covered.

### Did algorithm risks exceed expectations?

**Yes — in severity and in false sense of security, not in “new unknown estimators.”**

Risks that **exceeded** the v1 roadmap assumptions:

1. **Recovery metrics ≠ interval calibration** — v1 implied recovery/calibration could support reviewer trust; audit shows default battery does not exercise inference modes for SCM/TBR, so `false_positive_rate` and `coverage_under_null` are largely unmeasured for the most-used families (`VALIDATION_COVERAGE.md`; `ALGORITHM_REASSESSMENT` risks #6–7).
2. **Truth ↔ score misalignment** — Synthetic truth scalar vs `_path_relative_att` vs pooled DID coefficient are not proven equivalent under heterogeneous effects (`synthetic_world.py`, `runner.py`); recovery “success” may optimize the wrong objective.
3. **DGP honesty** — `fillna(0.0)` on missing outcomes and spillover on controls without estimator adjustment mean scenarios test robustness to **unmodeled** failures, not recovery of declared estimands.
4. **Scenario registry vs battery** — `scm_structural_break` and SDID stagger scenarios exist but are **not** in the active recovery paths wired to CI (`ESTIMATOR_RECOVERY_SCENARIOS` vs full registry; SDID not in `_extended_estimator_configs()`).
5. **Stable-but-wrong regimes** — DID still exports ATT under pretrend violation; SCM/TBR can fit pre-period well with poor post extrapolation; failures become NaN without typed diagnostics (`recovery_runner.py`).

Risks that **matched** expectations (no surprise, but now prioritized): interference metadata-only, skipped estimators (TROP/SDID/Bayesian), research-only maturity, platform-sensitive placebo.

**Bottom line (unchanged positioning, sharper ordering):** panel_exp remains an **internal / expert-review** geo toolkit. v2 prioritizes **statistical validity and measured calibration** over new policy surface or research estimators.

---

## 2. Remove previous assumptions

Items from `ROADMAP_REASSESSMENT.md` §5–6 reassessed against algorithm audit and current repo state.

### Promoted (do sooner than v1 ordering)

| Item | Why promoted |
|------|----------------|
| **Finite-sample recovery at scale (≥100 reps) with production inference modes** | Algorithm must-fix #2; `MIN_REPLICATIONS_FOR_STABLE_CALIBRATION = 100` already in `calibration_report.py` but CI uses 1–6 (`test_recovery_runner.py`). |
| **DGP truth ↔ estimator metric equivalence tests** | Algorithm must-fix #5; without this, expanding scenarios adds false confidence. |
| **Inference-mode stratified recovery (SCM, TBRRidge, DID)** | Closes NaN FPR/coverage gap; directly addresses top statistical risk #6. |
| **Wire `scm_structural_break` + collinearity scenarios into `ESTIMATOR_RECOVERY_SCENARIOS`** | Registered but not in SCM battery; algorithm missing-DGP #1. |
| **DID parallel-trends policy (gate or explicit waiver on ATT export)** | Algorithm correctness #5; metadata-only pretrends insufficient for causal claims. |
| **Recovery failure diagnostics (typed errors, not silent NaN)** | Algorithm correctness #10; affects trust in any calibration fed to readiness. |
| **Optional counterfactual stability hook post-fit (SCM/TBRRidge)** | Stability code exists but is not in `run_analysis`; addresses pre→post drift risk without new estimators. |

### Demoted (still useful, no longer top-tier)

| Item | Why demoted |
|------|-------------|
| **Validation coverage matrix document** | **Done** — `docs/VALIDATION_COVERAGE.md` is source of truth; further work is *execution*, not another matrix. |
| **Estimand / uncertainty prespecification helpers** | **Partially done** — `TargetEstimand`, `UncertaintyContract`, `build_analysis_contract` exist; remaining gap is **enforcement and metric alignment**, not more fields. |
| **Interference / spillover review packet (metadata)** | **Done** — `InterferenceReview`, card sections, bundle attachment; does not fix spillover in DGP/estimators (Tier 3). |
| **Power / MDE user contract** | **Done** — `PowerContract`, `MDE_SEMANTICS`, card separation of rules vs results; remaining gap is **aligning power DGP with recovery DGP** (Tier 1). |
| **Documentation reconciliation (gh-pages vs README)** | **Substantially done** — `tests/test_docs_code_truth.py`, README/user guide banners; maintenance only (Tier 2). |
| **Readiness profile expansion / strict as default** | Artifact layer sufficient; algorithm audit shows readiness inputs (FPR/coverage) are often **missing or unstable** for SCM/TBR — fix inputs before tuning profiles. |

### Removed (stop treating as near-term roadmap work)

| Item | Why removed |
|------|-------------|
| **“Add VALIDATION_COVERAGE.md” as a PR** | Already shipped. |
| **“Publish skip list” as discovery work** | Codified in `runner.py` `SKIPPED_ESTIMATORS` and coverage doc. |
| **More experiment-card / bundle / schema versions** | v1 overbuilt assessment stands; algorithm audit adds no justification for v2 artifact churn. |
| **Promoting estimators via smoke/recovery alone** | Explicitly forbidden by policy tests; algorithm audit proves smoke metrics can be NaN or misaligned. |

### Postponed (explicit deferral)

| Item | Why postponed |
|------|---------------|
| **SyntheticDID / TROP / Bayesian MCMC productionization** | Research-only; partial or broken recovery wiring; staggered SDID tests contradict scenario intent (`ALGORITHM_REASSESSMENT`). |
| **Full spillover estimation** | Tier 3; metadata review now adequate for partial interference workflows. |
| **Automated blocking readiness gates** | Culture remains advisory; blocking without calibrated inputs would be harmful. |
| **`production_safe` catalog promotions** | No estimator meets promotion table in `VALIDATION_COVERAGE.md` §4; algorithm must-fix list unfinished. |
| **Jackknife+ / time Jackknife+** | Still deferred per `uncertainty.md`; recover baseline modes first. |
| **External GeoLift benchmark suite** | Valuable but not prerequisite for *internal* wider use if in-repo calibration gates pass. |

---

## 3. Categorize remaining work

### Tier 1 — directly improves causal/statistical validity

| Workstream | Evidence / outcome |
|------------|-------------------|
| **Estimand contract enforcement + per-family reporting alignment** | Extend prespec helpers to require declared `target_estimand`; map SCM/TBR/DID outputs to that estimand in validation scoring. |
| **Truth ↔ metric equivalence regression suite** | Controlled DGPs where unit-level ATT is known; assert `_path_relative_att`, `summary()`, DID coef agree within tolerance. |
| **Recovery battery upgrade** | ≥100 reps per scenario for calibration jobs; ≥50 for CI nightly subset; inference modes match production defaults. |
| **Interval calibration by estimator × inference mode** | Populate `ci_lower`/`ci_upper`/`significant` in recovery; measure FPR (`MAX_FALSE_POSITIVE_RATE=0.10`) and `MIN_COVERAGE_UNDER_NULL=0.90`. |
| **DGP expansion (wired to CI)** | Collinearity, honest missingness (fix `fillna(0)` policy or document), multi-treated/staggered for TBRRidge, add `scm_structural_break` to SCM battery. |
| **DID pretrend policy** | Block or flag ATT when joint/linear pretrend tests fail; document waiver path on card. |
| **Align power null simulations with recovery null worlds** | Reduce false confidence when comparing `evaluate_aa_calibration` vs `RecoveryRunner` (`recovery_null_effect`). |
| **Counterfactual drift diagnostics in fit path (optional flag)** | `counterfactual_stability_tests.py` on SCM/TBRRidge after fit. |

### Tier 2 — improves operational safety

| Workstream | Notes |
|------------|-------|
| **Doc-truth CI maintenance** | Keep `test_docs_code_truth.py` green when API changes. |
| **Recovery failure surfacing** | Typed error counts in recovery payload; experiment card “validation quality” section. |
| **Reproducibility** | `random_state` required in power + inference examples; seed sensitivity report on recovery jobs. |
| **Evidence consistency** | Single canonical relative-ATT definition in evidence hash inputs when estimand declared. |
| **CVXPY path parity** | `SyntheticControlCVXPY` validation/recovery wiring per coverage matrix (expert_review estimators used in production-like flows). |
| **Platform placebo contract** | Document non-portable goldens; strict placebo mode default for stakeholder exports. |

### Tier 3 — research backlog

| Workstream | Notes |
|------------|-------|
| **Spillover estimation / partial interference adjustment** | Not required for expert-review if Tier 1–2 gates met. |
| **SDID staggered timing end-to-end** | Scenarios + panels + recovery + validation runner. |
| **TROP stable tuning contract + finite metrics** | Or permanent skip with hard error in user API. |
| **BayesianTBR / MTGP MCMC** | Optional-dep CI, convergence policy. |
| **Dynamic causal models / AugSynth recovery** | `unvalidated` today. |
| **External published benchmarks** | Informs `production_safe` discussion only after Tier 1 gates. |

---

## 4. Top 5 implementation PRs

Ordered by **statistical validity per engineering week**. No code in this doc — PR specs only.

### PR 1 — Estimand alignment and truth↔metric equivalence tests

| Dimension | Assessment |
|-----------|------------|
| **Impact** | High — makes all downstream recovery and cards interpretable. |
| **Risk reduced** | Algorithm correctness #1; statistical #2; must-fix #1 and #5. |
| **Expected statistical gain** | Provable comparability across SCM/TBR/DID on synthetic ground truth; ends silent optimization of mismatched metrics. |
| **Implementation complexity** | Medium — mostly validation tests + mapping layer in `runner.py` / evidence, not new estimators. |
| **Validation requirements** | New test module per family; heterogeneous-effect DGP fixtures; fail CI on estimand drift > tolerance. |

### PR 2 — Recovery battery v2 (inference modes + replication scale + failure typing)

| Dimension | Assessment |
|-----------|------------|
| **Impact** | High — turns recovery from smoke into calibration instrument. |
| **Risk reduced** | Statistical #6–7; correctness #10; must-fix #2. |
| **Expected statistical gain** | Measurable FPR/coverage/power for SCM/TBR (not only DID); stable estimates at n≥100. |
| **Implementation complexity** | Medium–high — `EstimatorConfig` matrix, slower CI tier (nightly), metadata on exceptions. |
| **Validation requirements** | Parametrize `n_simulations`; separate fast smoke (n≤5) vs calibration job (n≥100); assert finite metrics or explicit failure codes. |

### PR 3 — Synthetic DGP hardening (scenarios wired + missingness policy)

| Dimension | Assessment |
|-----------|------------|
| **Impact** | High for SCM/TBR/DID stress testing. |
| **Risk reduced** | Missing DGP #1–4; correctness #2, #7; statistical #4–5. |
| **Expected statistical gain** | Detects collinearity/outlier/structural-break failures before real geo panels. |
| **Implementation complexity** | Medium — `synthetic_scenarios.py` + `synthetic_world.py` policy for NaN; add scenarios to `ESTIMATOR_RECOVERY_SCENARIOS`. |
| **Validation requirements** | Each new scenario in recovery smoke; document `fillna(0)` or replace with explicit missingness estimator path. |

### PR 4 — DID pretrend contract (gate or waiver)

| Dimension | Assessment |
|-----------|------------|
| **Impact** | Medium–high for DID users; prevents stable-but-wrong TWFE claims. |
| **Risk reduced** | Correctness #5; statistical #2; must-fix #3. |
| **Expected statistical gain** | Clear causal credibility boundary; pretrend violation scenarios become actionable. |
| **Implementation complexity** | Low–medium — policy flag on `DID.run_analysis` + card/evidence fields. |
| **Validation requirements** | `did_parallel_trends_violation` must trigger gate/warn; bootstrap CI not exported without waiver. |

### PR 5 — Counterfactual stability optional post-fit + CVXPY recovery wiring

| Dimension | Assessment |
|-----------|------------|
| **Impact** | Medium — closes pre→post drift blind spot for SCM family. |
| **Risk reduced** | Correctness #6; donor stability / residual drift risks. |
| **Expected statistical gain** | Surfaces weight instability and residual drift before inference on post period. |
| **Implementation complexity** | Medium — hook existing `counterfactual_stability_tests.py`; add CVXPY configs to recovery runner per `VALIDATION_COVERAGE.md`. |
| **Validation requirements** | Stability flags on `scm_trend_mismatch` / `scm_structural_break`; no change to point estimates unless opt-in. |

**Dropped from v1 top-5 (already delivered):** coverage matrix doc, estimand helpers, interference packet, power contract, gh-pages reconciliation — see §2.

---

## 5. Things NOT to build

Attractive ideas that remain **premature** after the algorithm audit.

| Do not build (yet) | Reason |
|--------------------|--------|
| **Automated go/no-go / blocking readiness** | FPR/coverage inputs unreliable for SCM/TBR; would encode false certainty. |
| **`production_safe` maturity promotions** | Promotion criteria in `VALIDATION_COVERAGE.md` §4 unmet; estimand and calibration gates open. |
| **Stakeholder “MDE guarantee” UI** | Simulation MDE semantics honest but easy to mis-sell; power DGP ≠ recovery DGP. |
| **Default Bayesian / TROP / SDID in design runners** | Skipped in validation; partial recovery; research-only. |
| **Spillover estimation module** | Tier 3; declared metadata sufficient for current positioning. |
| **More readiness profiles or ML readiness** | Threshold tuning without calibrated recovery inputs is noise. |
| **Auto-attach run bundles on every analysis** | Bloat; does not fix statistical gaps. |
| **Additional artifact schema v2** | No external consumer pressure. |
| **Jackknife+ / time Jackknife+** | Baseline jackknife/BRB/placebo not calibrated in recovery. |
| **Multi-estimator “consensus ATT” score** | Estimands not aligned; would amplify stable-but-wrong agreement. |
| **Pretest_analysis revival** | Superseded by `PowerAnalysis` + design validation. |
| **HTML doc pipeline investment** | Tier 2 maintenance only until Tier 1 calibration green. |

---

## 6. Success criteria

**“panel_exp ready for wider production use”** means wider **internal expert-led** deployment (more teams, more studies), **not** unattended automated causal certification or `production_safe` catalog labels.

### 6.1 Estimand and reporting

| Criterion | Target | Evidence |
|-----------|--------|----------|
| Declared estimand on every study artifact | 100% of exported evidence with `build_analysis_contract` | `tests/test_estimand_contract.py` + card |
| Family-level metric matches declared estimand on synthetic ground truth | Bias &lt; policy tolerance on ≥3 scenarios per family | New equivalence test suite (PR 1) |
| No cross-estimator ATT comparison in templates without estimand note | Doc + card lint | User guide / experiment card |

### 6.2 Validation coverage breadth

| Criterion | Target | Evidence |
|-----------|--------|----------|
| Batch validation | SCM, TBRRidge/TBR, DID remain green; skips documented for TROP/SDID/Bayesian/MTGP | `runner.py`, `VALIDATION_COVERAGE.md` |
| Recovery runner wired | SCM, DID, TBR, TBRRidge + **CVXPY SCM** at minimum | `_extended_estimator_configs()` |
| Active scenario count | ≥5 stress scenarios per core family (incl. structural break, null, positive, interference proxy) | `ESTIMATOR_RECOVERY_SCENARIOS` |
| Research estimators | Either fully wired **or** hard `research_only` + runtime guard preventing default selection | Catalog + API |

### 6.3 Finite-sample recovery and calibration

| Criterion | Target | Evidence |
|-----------|--------|----------|
| Calibration jobs | `n_replications ≥ 100` per scenario for null and positive | `MIN_REPLICATIONS_FOR_STABLE_CALIBRATION` |
| CI smoke | May use n≤10 but **must** assert finite metrics or explicit failure code | `recovery_runner.py` |
| Recovery success rate | ≥ `MIN_RECOVERY_SUCCESS_RATE` (0.90) on positive scenarios per family | `calibration_report.py` |
| Failure transparency | &lt;5% NaN estimates without typed error in payload | PR 2 |

### 6.4 Interval calibration quality

| Criterion | Target | Evidence |
|-----------|--------|----------|
| Inference modes in recovery | At least one validated mode per family used in production (e.g. UnitJackknife or BRB for SCM/TBR; bootstrap for DID) | Recovery configs |
| Null FPR | ≤ `MAX_FALSE_POSITIVE_RATE` (0.10) at n≥100 | `build_calibration_report` |
| Null coverage | ≥ `MIN_COVERAGE_UNDER_NULL` (0.90) when intervals claimed | Same |
| Placebo semantics | Placebo bands never labeled as CI in exports | `InferenceResult` + card |
| Power on positive scenarios | ≥ `MIN_POWER_TARGET` (0.80) where effect size ≥ MDE grid point | Calibration report |

### 6.5 Counterfactual and design validity

| Criterion | Target | Evidence |
|-----------|--------|----------|
| DID pretrends | Violation blocks ATT or requires documented waiver on card | PR 4 |
| Optional stability diagnostics | Available for SCM/TBRRidge; WARN surfaced on card when drift flagged | Stability tests hook |
| Interference | Declared + review packet; spillover estimation still optional | `InterferenceReview` |
| Power vs recovery null | Documented relationship or unified null DGP for A/A checks | Tier 1 alignment |

### 6.6 Reproducibility and documentation truth

| Criterion | Target | Evidence |
|-----------|--------|----------|
| Full test suite | Green on supported platform | `poetry run pytest tests/ -q` |
| Doc-truth tests | Pass | `tests/test_docs_code_truth.py` |
| `random_state` | Documented required for power and stochastic inference in examples | README / user guide |
| Seed sensitivity | Recovery metrics stable within tolerance across 3 seeds at n≥100 | New regression |

### 6.7 Explicit non-goals (still not “wider production”)

- `production_safe` in `method_metadata.py` for any estimator  
- Automated business decision gates on readiness status  
- Spillover-adjusted ATT without a dedicated Tier 3 module  
- SDID/TROP/Bayesian as default recommended estimators  

### 6.8 Summary gate checklist

Wider production use is **go** when **all** are true:

1. PR 1 equivalence tests green for SCM, TBRRidge, DID.  
2. PR 2 calibration report at n≥100 shows FPR ≤ 0.10 and coverage ≥ 0.90 for declared inference modes on null scenarios.  
3. PR 3 scenarios active in CI recovery battery including structural break / collinearity.  
4. PR 4 DID pretrend policy shipped.  
5. No silent NaN recovery rate &gt;5% on core family battery.  
6. `VALIDATION_COVERAGE.md` updated to reflect wiring; zero undocumented skips for core paths.  

Until then: **expert-review platform** (v1 positioning holds; v2 adds measurable statistical gates).

---

## Appendix: v1 → v2 priority shift (one table)

| v1 top priority | v2 status |
|-----------------|-----------|
| Validation coverage matrix | **Done** → execute Tier 1 recovery/DGP |
| Estimand helpers | **Done** → enforce + align metrics |
| Interference packet | **Done** → Tier 3 estimation deferred |
| Power contract | **Done** → align null DGPs |
| Docs reconciliation | **Done** → Tier 2 maintenance |
| *(new)* Truth↔metric tests | **Tier 1 PR 1** |
| *(new)* Inference recovery at scale | **Tier 1 PR 2** |
| *(new)* DGP hardening | **Tier 1 PR 3** |
| *(new)* DID pretrend gate | **Tier 1 PR 4** |

---

*Read-only roadmap update. No package code modified.*
