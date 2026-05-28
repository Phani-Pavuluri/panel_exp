# panel_exp roadmap v4 (post Phase 8 / Run 001)

**Status:** active (Phases 11–15 scoped; priorities frozen; dual-track)  
**Last reviewed:** 2026-05-26  
**Supersedes:** `docs/ROADMAP_V3.md` (Phases 5–8 execution and v3 priority ordering)  
**Package version:** 0.2.1  

**Companion documents:**

| Document | Role |
|----------|------|
| [`docs/OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) | **Frozen priority backlog** — 38 investigations, scored and deduplicated |
| [`docs/ROADMAP_V3.md`](ROADMAP_V3.md) | Phases 5–8 history and shipped measurement-honesty work |
| [`docs/ROADMAP_V3_EXECUTION_ORDER.md`](ROADMAP_V3_EXECUTION_ORDER.md) | Frozen execution spec for Phases 5–8 |
| [`docs/CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) | Production nominal calibration evidence (n=100) |
| [`docs/CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) | Run 001 diagnosis and eligibility tightening |
| [`docs/METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) | Per-estimator validation paths A–E |
| [`docs/VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) | Estimator × scenario × inference matrix |
| [`docs/PHASE8_ALGORITHM_AUDIT.md`](PHASE8_ALGORITHM_AUDIT.md) | Focused mini-audit (superseded in part by Run 001 archive) |
| [`docs/GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md`](GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md) | Architecture milestone snapshot; Track A/B framing |
| [`docs/SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md) | Phase 11 OC archive (complete) |

**Read-only roadmap — no package code in this document.**

---

## Dual-track roadmap (post checkpoint)

The roadmap **bifurcates** after the GeoX strategic checkpoint. **Not in scope:** random estimator expansion.

### Track A — evidence / governance stabilization

**Objective:** Make causal claims honest, bounded, and auditable.

| Work | Examples |
|------|----------|
| Operating-characteristic characterization | Phase 11 SCM (done); Phase 12 TBRRidge; Phase 14 DID |
| Calibration archives | Run 001; Run 002 (post–BRB merge) |
| Failure analysis + eligibility | Registry skip reasons; no threshold tuning |
| Investigation ledger | `OPEN_INVESTIGATIONS.md` — deferred ≠ abandoned |
| Correctness preservation | **Merge BRB bound-ordering fix** (not re-promotion) |
| Governed measurement instruments | Per-estimator: estimand, interval, OC, failure analysis, usage boundary |

**Moat here:** evidence lineage, calibration honesty, estimator governance, explainable trust.

### Track B — experimentation-platform evolution

**Objective:** Unified experimentation architecture inside MIP (mid-term, after Phase 12 stabilizes).

| Work | Examples |
|------|----------|
| Shared abstractions (future) | `ExperimentSpec`, `ExperimentEvidence`, `Estimand`, `DiagnosticSummary`, `CalibrationSignal`, `TrustReport`, `RecommendationContext`, `ReleaseGate` |
| GeoX + A/B + MMM convergence | Shared contracts across geo, conversion lift, budget optimization |
| Experiment memory + calibration exchange | Cross-study reuse; trust-aware recommendations |
| LLM orchestration reference | Grounded in investigations + runs; no unsourced promotion |

Detail: [`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md).

**Track A is gate for Track B** — do not build unified abstractions before TBRRidge OC and governance stabilize.

---

## Governed measurement instruments (mindset)

Treat estimators as **governed measurement instruments**, not interchangeable ML models.

Every estimator should eventually have:

| Artifact | Purpose |
|----------|---------|
| Estimand contract | What is estimated, on whom, when |
| Interval contract | Scale, alignment, unsupported paths |
| Calibration evidence | n≥100 archives where claimed |
| OC archive | Width, power, geometry sensitivity |
| Failure analysis | Mechanism when calibration fails |
| Investigation registry entry | Open/deferred gaps |
| Governance status | Supported / expert-review / research / deferred |
| Intended usage boundary | e.g. SCM jackknife = null monitor only |

This is mature scientific infrastructure — rare among experimentation platforms.

---

## Immediate next step (before Phase 12 / Run 002)

**Merge `brb-bound-ordering-fix` into integration mainline** (`estimator-maturity-metadata` → PR to `main`).

| Does | Does not |
|------|----------|
| Remove known BRB bound-ordering defect | Re-promote BRB to nominal eligibility |
| Improve inference hygiene (`apply_bounds_to_results`, guard) | Change `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` |
| Preserve future rehabilitation options | Make calibration claims |
| Enable honest Run 002 characterization | Imply TBRRidge production-ready |

**Classification:** correctness preservation only. BRB remains skipped with `brb_bounds_inverted_run001` until Run 002 + failure analysis + OC pass.

---

## Promotion policy (non-negotiable)

**No estimator advancement** (maturity label change, nominal-calibration eligibility, expert-review expansion, or “recommended for production-like workflows”) without completing this chain **in order**, with archived evidence at each step:

1. **Estimand definition** — what quantity is estimated, on what units and time window, and how it maps to recovery scoring (`relative_att_post` or an explicitly declared alternate).
2. **Recovery evidence** — finite metrics or typed failures on the standard recovery battery (`RecoveryRunner`, documented scenarios).
3. **Calibration evidence** — null-scenario FPR and coverage (and positive-scenario power when claimed) at **n≥100** on aligned configs, archived like Run 001.
4. **Failure analysis** — when calibration fails, root-cause doc (mechanism, not threshold tuning) before re-eligibility.
5. **Operating-characteristic characterization** — width, power, geometry sensitivity, and known failure modes documented for reviewers.

Skipping a step is **roadmap drift**. Plumbing-only changes, passing smoke tests, or documentation without archived OC do **not** satisfy this policy.

Investigation IDs in [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) map to gaps; this roadmap assigns **phases** to close them. Do not re-prioritize ad hoc — update investigations first, then amend v4.

---

## Recommended document sequence

| Step | Action | Status |
|------|--------|--------|
| 1 | Create/update **`docs/ROADMAP_V4.md`** (this file) | **Done** |
| 2 | Add/maintain **`docs/OPEN_INVESTIGATIONS.md`** | **Done** — single source of truth for unresolved gaps |
| 3 | **Freeze priorities** | **Done** — top investigations and phase order locked here + OPEN_INVESTIGATIONS §1 |
| 4 | **Phase 11** — SCM UnitJackKnife OC | **Done** — `SCM_JACKKNIFE_CHARACTERIZATION_001.md` |
| 5 | **Merge BRB bound-ordering fix** | **Next** — correctness preservation; not re-promotion |
| 6 | **Phase 12** — TBRRidge inference rehabilitation | After BRB merge — Run 002 + OC; all outcomes acceptable |
| 7 | **Re-audit** after Phases 11–15 | Mini-audit; update investigations |
| 8 | Create **`docs/ROADMAP_V5.md`** | After re-audit |
| 9 | **Track B** — unified experimentation abstractions | After Phase 12 stabilizes |

---

## 1. Completed (Phases 5–10 and foundations)

Shipped behavior and evidence. **Do not re-open** unless new evidence contradicts archived runs.

| Deliverable | What it established | Evidence |
|-------------|---------------------|----------|
| **Estimand alignment** | Recovery scores `relative_att_post` via `_path_relative_att`; canonical truth tests | `recovery_runner.SCORED_TARGET_ESTIMAND`, `tests/test_estimand_metric_alignment.py` |
| **Interval alignment** | Coverage/FPR only when `interval_estimand == relative_att_post` | `recovery_intervals.py`, `tests/test_recovery_estimand_interval_alignment.py` |
| **Production calibration harness** | `run_production_nominal_calibration()`, replication thresholds, advisory status | `production_nominal_calibration.py`, `nominal_calibration.py` |
| **DGP semantics** | Explicit missingness policies; honest stagger metadata; calibration scenarios `missingness_policy=none` | `synthetic_world.py`, `tests/test_synthetic_dgp_semantics.py` |
| **DID contracts** | Pretrend warn/fail + waiver; relative-ATT interval calibration **unsupported** by policy | `did_interval_policy.py`, `tests/test_did_interval_policy.py` |
| **BRB bound fix** | Correct `apply_bounds_to_results` mapping; `PATH_INTERVAL_BOUNDS_INVERTED` guard | `inference/_impact_common.py`, `recovery_intervals.py`, branch `brb-bound-ordering-fix` |
| **Eligibility tightening** | `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` = **`SCM_UnitJackKnife` only** | `nominal_calibration.py`, `VALIDATION_COVERAGE.md` |
| **Phase 8 audit** | Focused algorithm/statistical mini-audit | `docs/PHASE8_ALGORITHM_AUDIT.md` |
| **Run 001 evidence archive** | n=100, 3 seeds; SCM null pass / zero power; BRB/Kfold failures documented | `docs/CALIBRATION_RUN_001.md`, `docs/CALIBRATION_FAILURE_ANALYSIS_001.md` |

**Also shipped (supporting):** inference recovery configs, typed recovery failures, opt-in review flags (`build_estimator_review`), method validation plan, validation coverage matrix.

**Not completed by design:** package-level nominal calibration for TBRRidge modes; DID relative-ATT intervals; `production_safe` promotions; automated blocking readiness.

---

## 2. Current positioning

| Statement | Detail |
|-----------|--------|
| **Expert-review platform** | Disciplined contracts, evidence exports, and calibration **instrumentation** for human reviewers — not unattended certification. |
| **Not production-safe** | No estimator carries `production_safe` in the maturity catalog; policy tests enforce this. |
| **No automated decisioning** | Readiness, calibration status, and experiment cards are **advisory**; they do not block runs or approve business decisions. |
| **No estimator promotions** | `expert_review` / `research_only` labels unchanged until promotion policy chain is satisfied per method. |

**Frozen priority themes** (from [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md)):

1. Close **calibration honesty** (INV-039, INV-004, INV-008, INV-007) before breadth.  
2. Preserve **estimand discipline** (INV-001, INV-002, INV-036) — document and test, not silent consensus ATT.  
3. **Research estimators** (INV-011) stay off the promotion path until wired and characterized.  

---

## 3. Approved execution order (Phases 11–15)

One phase per scoped PR (or PR series). **No new estimators, inference modes, artifact schema versions, or maturity promotions** unless this document is amended after re-audit.

### Phase 11 — SCM UnitJackKnife characterization

| Field | Detail |
|-------|--------|
| **Goal** | Explain Run 001 outcomes: null pass with **zero power** on positive DGP; characterize interval width vs donor/treated geometry. |
| **Investigations** | INV-004, INV-003 (partial), INV-039 (SCM-only path) |
| **In scope** | Read-only analysis + archived notes; optional single-treated calibration scenario **documented**; width/power tables |
| **Out of scope** | DGP tuning to force power pass; re-adding TBRRidge to eligibility; threshold changes |
| **Promotion policy steps** | Estimand (already defined) → recovery (exists) → Run 001 calibration (exists) → **failure analysis for power** → **OC characterization** |
| **Exit** | Written OC doc: when SCM jackknife is suitable for null monitoring only vs lift detection; update OPEN_INVESTIGATIONS INV-004 status |

---

### Phase 12 — TBRRidge inference rehabilitation

**Framing:** This is **not** “make TBRRidge production-ready.” It is: **determine whether TBRRidge inference can become trustworthy enough for calibrated expert-review workflows.**

| Field | Detail |
|-------|--------|
| **Prerequisite** | BRB bound-ordering fix merged (correctness only — still ineligible until Run 002) |
| **Goal** | Characterize BRB post-fix, Kfold geometry, single- vs multi-treated behavior, interval validity, OC, failure surfaces |
| **Workstreams** | **BRB** — Run 002 at n≥100 after merge; failure analysis. **Kfold** — multi-treated fix **or** single-treated-only contract. **Geometry matrix** — default recovery vs single-treated panels |
| **Investigations** | INV-008, INV-007, INV-003, INV-017 |
| **In scope** | OC archives, Run 002, guards, recovery tests; registry update **only** after full advancement policy chain |
| **Out of scope** | “Production-ready” narrative; automatic eligibility; new inference modes |
| **Acceptable outcomes** | Re-enable partially · restrict to single-treated · null-monitoring-only · remain expert-review · permanently research-only — **all are valid** |
| **Exit** | Governance decision doc (→ Phase 13) with Run 002 + OC evidence; eligibility unchanged unless OC passes |

---

### Phase 13 — TBRRidge promotion decision

| Field | Detail |
|-------|--------|
| **Goal** | **Decision only** — whether any TBRRidge inference config may advance within **expert_review** (not `production_safe`) based on Phase 12 evidence. |
| **Investigations** | INV-039 (partial), METHOD_VALIDATION_PLAN paths |
| **In scope** | Governance doc / validation plan update; explicit “go / no-go / monitor-only” per config |
| **Out of scope** | `production_safe` label; catalog auto-promotion; blocking gates |
| **Exit** | Recorded decision with citations to Run 002 and OC characterization; no promotion without passing promotion policy |

---

### Phase 14 — DID operating-characteristic characterization

| Field | Detail |
|-------|--------|
| **Goal** | Characterize DID **point and cumulative** inference under recovery scenarios: pretrend violation behavior, interval scale, and what can be claimed without relative-ATT intervals. |
| **Investigations** | INV-005, INV-006, INV-032 |
| **In scope** | OC study on `did_parallel_trends_*`; strengthen reviewer-facing contract docs; confirm `did_relative_att_interval_unsupported` remains |
| **Out of scope** | Cumulative-CI scaling to relative ATT; nominal calibration eligibility for `DID_Bootstrap` on relative ATT |
| **Promotion policy steps** | Estimand documentation for DID vs recovery score; recovery evidence; **no** relative-ATT calibration claim unless new interval design (deferred) |
| **Exit** | DID OC appendix: what FPR/coverage mean on cumulative scale; pretrend waiver discipline |

---

### Phase 15 — AugSynth / CVXPY validation

| Field | Detail |
|-------|--------|
| **Goal** | Close the **validation wiring gap** for CVXPY SCM variants: recovery configs or permanent research-only guard. |
| **Investigations** | INV-018, INV-037 (collinearity scenario) |
| **In scope** | `RecoveryRunner` configs and/or `SKIPPED_ESTIMATORS` hardening; METHOD_VALIDATION_PLAN path B vs E decision |
| **Out of scope** | `production_safe`; full OSQP cross-platform golden refresh (see INV-040) |
| **Exit** | VALIDATION_COVERAGE row updated with honest maturity evidence path |

---

## 3b. Track B — after Phase 12 (medium-term platform)

Start **unified experimentation abstractions** only after TBRRidge characterization stabilizes.

| Future abstraction | Role |
|--------------------|------|
| `ExperimentSpec` | Declared design + estimand + interference |
| `ExperimentExecution` | Runnable measurement invocation |
| `ExperimentEvidence` | Portable evidence object (estimand, intervals, run refs, flags) |
| `Estimand` | Registry entry with family mapping |
| `DiagnosticSummary` | Reviewer-facing diagnostics aggregate |
| `CalibrationSignal` | Lifecycle state from recovery → OC → eligibility |
| `TrustReport` | Honest trust narrative (passes, limits, deferrals) |
| `RecommendationContext` | Inputs for budget / lift recommendations |
| `ReleaseGate` | Human-governed promotion checkpoint (not auto-block) |

**Shared across:** GeoX, A/B, conversion lift, MMM replay/calibration, budget optimization, future causal agents.

**Not in v0.2.1:** new schema versions or implementation — vision and sequencing only.

---

## 4. Research backlog (post Phase 15)

Explicitly **not** in Phases 11–15. Each item requires the **promotion policy** chain before any maturity movement.

| Area | Estimators / topics | Notes |
|------|---------------------|--------|
| **SDID** | `SyntheticDID` | Staggered DGP honest; recovery unwired (INV-019, INV-011) |
| **TROP** | `TROP` | Recovery smoke tolerates NaN; skipped in batch validation (INV-020) |
| **BayesianTBR** | `BayesianTBR`, `BayesianTBRHorseShoe` | JAX optional deps; registry `Bayesian` ≠ MCMC path (INV-015) |
| **MTGP** | `MTGP` | Not validated; Bayesian GP MCMC |
| **Spillover estimation** | Core SCM/TBR/DID | DGP stress only; no spillover term (INV-009) |
| **Dynamic causal models** | Time-varying coefficients, AugSynth full productionization | Not in API; strategic research |

See [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) §8 and roadmap execution deferred register (v3 D1–D12) for investigation cross-links.

---

## 5. Do not build (scope lock)

Stop scheduling these unless **ROADMAP_V5** explicitly reopens after re-audit.

| Item | Reason |
|------|--------|
| **`production_safe` labels** | No estimator meets bar; promotion policy does not allow skip to label |
| **More inference variants** | Jackknife+, time JK+, etc. — baseline modes not calibrated (INV-026) |
| **Consensus ATT** | Cross-estimator single estimand without proof (INV-001) |
| **Automatic blocking gates** | Advisory culture; weak calibration inputs make blocking harmful (INV-035) |
| **Artifact churn** | New card/bundle/readiness schema versions without external consumers (INV-034) |

**Also unchanged:** unattended “certified causal effect” marketing; spillover-adjusted ATT in core estimators; DID relative-ATT intervals via cumulative scaling; threshold tuning to pass calibration without mechanism docs.

---

## 6. Re-audit trigger (after Phase 15)

Run a **focused mini-audit** (same spirit as Phase 8, not a full governance re-audit). Inputs:

- Phases 11–15 evidence archives (SCM OC, Run 002, TBRRidge decision memo, DID OC, CVXPY validation outcome)
- Updated [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) statuses
- Latest `VALIDATION_COVERAGE.md` and `METHOD_VALIDATION_PLAN.md`

**Audit questions:**

1. Did any config re-enter nominal eligibility without Run 002–class evidence?  
2. Is SCM jackknife’s role (null monitor vs lift detector) explicitly bounded?  
3. Are TBRRidge BRB/Kfold either calibrated or permanently skipped with failure analysis?  
4. Is DID still excluded from relative-ATT calibration claims?  
5. Did Phases 11–15 introduce artifact surface or inference modes against §5?  

**Output:** `docs/ROADMAP_V5.md` — new positioning, completed table, and Phases 16+ only if evidence supports.

Suggested audit triggers also listed in [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) §12.

---

## 7. Phase map (v3 → v4)

| v3 phase | Status | v4 continuation |
|----------|--------|-----------------|
| Phases 5–8 | **Complete / frozen** | See §1 Completed |
| Phase 9 | Run 001 archive | Evidence input to Phases 11–12 |
| Phase 10 | Failure analysis + eligibility tighten | BRB fix shipped; registry SCM-only |
| **Phase 11** | **Next** | SCM UnitJackKnife OC |
| **Phase 12** | Planned | TBRRidge inference rehabilitation |
| **Phase 13** | Planned | TBRRidge promotion **decision** |
| **Phase 14** | Planned | DID OC characterization |
| **Phase 15** | Planned | AugSynth/CVXPY validation |
| Re-audit | After 15 | → ROADMAP_V5 |

---

## Appendix: Investigation → phase map

| Investigation | Title (short) | Phase |
|---------------|---------------|-------|
| INV-004 | SCM jackknife zero power | 11 |
| INV-003 | Multi-treated default DGP | 11–12 |
| INV-008 | BRB bound ordering / Run 002 | 12 |
| INV-007 | Kfold multi-treated failure | 12 |
| INV-017 | Few-donor inference geometry | 12 |
| INV-039 | Package calibration claim | 11–13 |
| INV-005, INV-006, INV-032 | DID pretrend / intervals / timing | 14 |
| INV-018, INV-037 | CVXPY / collinearity | 15 |
| INV-011, INV-019, INV-020 | SDID/TROP/Bayesian | Research backlog |
| INV-009 | Spillover | Research backlog |
| INV-001, INV-002, INV-036 | Estimand / pooling / truth | Ongoing documentation; not a promotion shortcut |

---

*Roadmap v4 active for Phases 11–15. Priorities frozen via [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md). Supersedes v3 for forward execution order only; v3 remains historical record for Phases 5–8.*
