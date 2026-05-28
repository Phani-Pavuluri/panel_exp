# Open investigations

**Status:** living backlog for intentionally deferred or unresolved issues  
**Last updated:** 2026-05-28  
**Package version:** 0.2.1  

**Related:** `docs/ROADMAP_V3.md` (governance), `docs/ROADMAP_V4.md` (Phases 11–15), `docs/METHOD_VALIDATION_PLAN.md`, `docs/VALIDATION_COVERAGE.md`

---

## Purpose

Track **unresolved gaps, deferred work, and open scientific questions** discovered during development. This is institutional memory for honest governance — not an implementation roadmap and not proof of correctness.

**Deferred ≠ abandoned.** Items remain listed until evidence closes them. Passing tests, calibration plumbing, or implemented diagnostics do not close an investigation without archived operating-characteristic evidence.

**Not claimed:** `production_safe` for any estimator; package-wide nominal calibration (only partial SCM null monitoring is evidenced).

---

## Phase 12 investigation program (TBRRidge)

**Framing:** Characterize whether TBRRidge inference can support calibrated expert-review workflows — **not** “fix TBRRidge.” All outcomes are acceptable if evidenced.

| ID | Track | Backlog cross-link | Primary artifact |
|----|-------|-------------------|------------------|
| **INV-007** | KFold geometry characterization | [TBRRidge Kfold multi-treated geometry](#tbrridge-kfold-multi-treated-geometry) | Geometry OC matrix; single-treated vs pooled failure surface |
| **INV-008** | BRB operating characteristics after bound fix | [TBRRidge BRB inference behavior](#tbrridge-brb-inference-behavior) | Run 002 archive (n≥100); width/coverage/power/seed stability |
| **INV-003** | Multi-treated aggregation semantics | [Multi-treated default recovery DGP](#multi-treated-default-recovery-dgp), [Heterogeneous vs pooled recovery scoring](#heterogeneous-vs-pooled-recovery-scoring) | Estimand/aggregation contract doc; optional heterogeneous probes |
| **INV-017** | Calibration scaling and governance | [Calibration scaling (CI n ≪ production n)](#calibration-scaling-ci-n--production-n), [Trust-score / TrustReport evolution](#trust-score--trustreport-evolution) | Archival conventions; eligibility evolution rules; trust-signal inputs |

**Successful Phase 12 examples:** “BRB remains research-only”; “Kfold permanently single-treated-only”; “no TBRRidge config re-enters nominal eligibility.” These are **successful** if evidence supports them.

Execution detail: [`ROADMAP_V4.md`](ROADMAP_V4.md) § Phase 12.

---

## Critical investigations

### Cross-estimator estimand not enforced

| Field | Detail |
|-------|--------|
| **Category** | causal_validity |
| **Status** | open |
| **Why deferred** | Requires per-family contract layer, not a single estimator patch; heterogeneous aggregation unresolved |
| **Risk if unresolved** | False agreement across SCM/TBR/DID; wrong experiment-card conclusions |
| **Revisit when** | Estimand matrix published in validation docs + equivalence tests vs DGP truth |

### Package lacks demonstrated nominal calibration

| Field | Detail |
|-------|--------|
| **Category** | calibration |
| **Status** | open |
| **Why deferred** | Only `SCM_UnitJackKnife` eligible; BRB/Kfold removed; SCM zero power on positive DGP |
| **Risk if unresolved** | Over-claiming calibration or expert-review expansion without evidence |
| **Revisit when** | Phase 12 Run 002 (BRB) + full OC archive, or explicit package-level null-monitor-only statement ratified |

### SCM UnitJackKnife over-coverage and zero power

| Field | Detail |
|-------|--------|
| **Category** | calibration / inference |
| **Status** | characterized, not closed |
| **Why deferred** | Phase 11 shows **expected conservatism + geometry limitation**, not implementation defect — no math change warranted yet |
| **Risk if unresolved** | Misuse as lift detector; false confidence in positive-scenario detection |
| **Revisit when** | Product requires power claims → inference redesign or geometry-specific policy (`SCM_JACKKNIFE_CHARACTERIZATION_001.md`) |

---

## Medium-priority investigations

### Heterogeneous vs pooled recovery scoring

**Phase 12 ID:** INV-003

| Field | Detail |
|-------|--------|
| **Category** | statistical_validity |
| **Status** | open |
| **Why deferred** | Pooled `_path_relative_att` contract in recovery runner; documentation-first |
| **Risk if unresolved** | High recovery success while unit-level truth diverges |
| **Revisit when** | Heterogeneous DGP equivalence tests or alternate scoring path defined |

### DID ATT exported under pretrend violation

| Field | Detail |
|-------|--------|
| **Category** | causal_validity |
| **Status** | open |
| **Why deferred** | Warn/fail contract shipped; blocking export is product policy |
| **Risk if unresolved** | Credible-looking DID results when parallel trends fail |
| **Revisit when** | Experiment-card / workflow audit for pretrend fail visibility |

### Multi-treated default recovery DGP

**Phase 12 ID:** INV-003 (partial — aggregation semantics broader than DGP default)

| Field | Detail |
|-------|--------|
| **Category** | DGP_realism |
| **Status** | open |
| **Why deferred** | Run 001 comparability; changing default affects historical archives |
| **Risk if unresolved** | Calibration evidence may not transfer to single-geo workflows |
| **Revisit when** | Single- vs multi-treated calibration scenario catalog documented |

### Power null DGP ≠ recovery null DGP

| Field | Detail |
|-------|--------|
| **Category** | DGP_realism |
| **Status** | open |
| **Why deferred** | Unified null world is large scope (execution order D10) |
| **Risk if unresolved** | Incomparable A/A power vs recovery FPR |
| **Revisit when** | Design/power doc cross-links recovery worlds |

### Documentation drift (user guide vs code truth)

| Field | Detail |
|-------|--------|
| **Category** | documentation |
| **Status** | open |
| **Why deferred** | Maintenance; not a statistical defect |
| **Risk if unresolved** | Misconfigured studies despite correct code |
| **Revisit when** | DOC_DRIFT high-severity rows cleared |

### Six overlapping artifact summary layers

| Field | Detail |
|-------|--------|
| **Category** | architecture |
| **Status** | open |
| **Why deferred** | Individual artifacts not wrong; consolidation is UX/product |
| **Risk if unresolved** | Reviewer fatigue; conflicting narratives |
| **Revisit when** | Primary vs supplementary artifact roles documented in README |

---

## Research backlog

### Spillover estimation

| Field | Detail |
|-------|--------|
| **Category** | causal_validity / research |
| **Status** | intentionally_deferred |
| **Why deferred** | DGP stress only; no spillover term in core estimators (D6) |
| **Risk if unresolved** | Overconfident geo incrementality under interference |
| **Revisit when** | Partial-interference product requirement + research spike |

### SDID staggered validation

| Field | Detail |
|-------|--------|
| **Category** | research |
| **Status** | open |
| **Why deferred** | Staggered DGP honest; `RecoveryRunner` unwired; `research_only` |
| **Risk if unresolved** | SDID used without recovery backing |
| **Revisit when** | Recovery config + staggered OC smoke |

### TROP stable validation contract

| Field | Detail |
|-------|--------|
| **Category** | research |
| **Status** | open |
| **Why deferred** | Skipped batch; smoke tolerates NaN |
| **Risk if unresolved** | Unreliable comparative rankings |
| **Revisit when** | Path D vs permanent skip decision |

### Dynamic causal models / MMM platform scope

| Field | Detail |
|-------|--------|
| **Category** | research |
| **Status** | open |
| **Why deferred** | Geo-experiment-centric v0.2.1 scope |
| **Risk if unresolved** | Expectation mismatch vs platform vision |
| **Revisit when** | `EXPERIMENTATION_PLATFORM_VISION.md` architecture phase picked up |

### External geo-lift benchmarks

| Field | Detail |
|-------|--------|
| **Category** | research |
| **Status** | open |
| **Why deferred** | In-repo synthetic worlds only today |
| **Risk if unresolved** | External credibility gap |
| **Revisit when** | One reference implementation equivalence study scoped |

---

## Deferred architecture work

### Unified experimentation layer (geo + A/B)

| Field | Detail |
|-------|--------|
| **Category** | architecture |
| **Status** | intentionally_deferred |
| **Why deferred** | Mid-term vision; no API surface yet |
| **Risk if unresolved** | Fragmented evidence across experiment types |
| **Revisit when** | Shared `ExperimentEvidence` contract design PR |

### Trust-score / TrustReport evolution

**Phase 12 ID:** INV-017 (partial — trust formation rules depend on calibration archives)

| Field | Detail |
|-------|--------|
| **Category** | architecture / governance |
| **Status** | intentionally_deferred |
| **Why deferred** | Readiness advisory only; no calibrated trust model |
| **Risk if unresolved** | Misread readiness as certification |
| **Revisit when** | Calibration exchange + OC archives exist per estimator |

### Automated blocking readiness gates

| Field | Detail |
|-------|--------|
| **Category** | governance |
| **Status** | intentionally_deferred |
| **Why deferred** | Weak calibration inputs make blocking harmful (D11) |
| **Risk if unresolved** | Process relies on humans; some enterprises expect software gates |
| **Revisit when** | Post–Phase 15 re-audit + product decision |

### Artifact schema churn (cards, bundles v2)

| Field | Detail |
|-------|--------|
| **Category** | architecture |
| **Status** | intentionally_deferred |
| **Why deferred** | No external consumers; v1 sufficient |
| **Risk if unresolved** | Premature versioning cost |
| **Revisit when** | External consumer or unified experimentation layer requires it |

---

## Inference concerns

### TBRRidge BRB inference behavior

**Phase 12 ID:** INV-008

| Field | Detail |
|-------|--------|
| **Category** | inference / calibration |
| **Status** | investigating |
| **Why deferred** | Removed from eligibility (`brb_bounds_inverted_run001`); bound-ordering fix on branch; Run 002 not archived |
| **Risk if unresolved** | Re-eligibility without OC → repeat Run 001 anti-calibration |
| **Revisit when** | Run 002 at n≥100 + failure analysis (Phase 12) |

### TBRRidge Kfold multi-treated geometry

**Phase 12 ID:** INV-007

| Field | Detail |
|-------|--------|
| **Category** | inference / bug |
| **Status** | open |
| **Why deferred** | Removed from eligibility; fix or single-treated-only contract pending |
| **Risk if unresolved** | Hard failures on multi-geo panels if users enable Kfold |
| **Revisit when** | Multi-treated fix or documented single-treated-only policy (Phase 12) |

### DID interval semantics (relative ATT unsupported)

| Field | Detail |
|-------|--------|
| **Category** | inference |
| **Status** | policy closed; investigation open for relative path |
| **Why deferred** | Phase 6 policy: cumulative bootstrap only; scaling rejected |
| **Risk if unresolved** | Users expect relative-ATT calibration on DID |
| **Revisit when** | New relative-ATT interval design with estimand proof (D8) |

### Bayesian inference paths (registry vs MCMC)

| Field | Detail |
|-------|--------|
| **Category** | inference / documentation |
| **Status** | open |
| **Why deferred** | Registry `Bayesian` on SCM/TBR ≠ `BayesianTBR` NUTS |
| **Risk if unresolved** | Wrong uncertainty claims in notebooks |
| **Revisit when** | Disambiguation table in user-facing index |

### Placebo vs CI interpretation

| Field | Detail |
|-------|--------|
| **Category** | inference |
| **Status** | open |
| **Why deferred** | Strict mode optional; single-treated limitation |
| **Risk if unresolved** | Placebo bands misread as confidence intervals |
| **Revisit when** | Stakeholder export policy for strict placebo default |

### Jackknife+ / new inference variants

| Field | Detail |
|-------|--------|
| **Category** | research |
| **Status** | intentionally_deferred |
| **Why deferred** | `uncertainty.md`; baseline modes not fully characterized |
| **Risk if unresolved** | Scope creep before OC gates |
| **Revisit when** | SCM/TBRRidge baseline calibration evidence improves |

---

## DGP realism concerns

### Donor collinearity characterization

| Field | Detail |
|-------|--------|
| **Category** | DGP_realism |
| **Status** | open |
| **Why deferred** | `scm_high_collinearity` exists but not in routine SCM recovery battery |
| **Risk if unresolved** | Undetected weight instability in standard CI |
| **Revisit when** | Add to battery or document permanent exclusion |

### Missingness realism (`fill_zero` on non-calibration paths)

| Field | Detail |
|-------|--------|
| **Category** | DGP_realism |
| **Status** | open |
| **Why deferred** | Calibration scenarios use `missingness_policy=none`; other scenarios may still fill |
| **Risk if unresolved** | Optimistic fits under missing data |
| **Revisit when** | Per-scenario missingness policy audit |

### Calibration scaling (CI n ≪ production n)

**Phase 12 ID:** INV-017 (partial — governance playbook is foundational)

| Field | Detail |
|-------|--------|
| **Category** | calibration / operational |
| **Status** | open |
| **Why deferred** | CI runtime; production harness defaults n=100 |
| **Risk if unresolved** | False sense of calibration from green smoke tests |
| **Revisit when** | Nightly archival job or explicit smoke vs production tier tags |

---

## Estimator-specific investigations

### SCM — conservatism and geometry (Phase 11)

| Field | Detail |
|-------|--------|
| **Category** | calibration |
| **Status** | characterized |
| **Why deferred** | No defect evidence; role bounded to null monitoring |
| **Risk if unresolved** | Promotion beyond null monitor without redesign |
| **Revisit when** | Any eligibility or maturity discussion |

### TBRRidge — inference investigation program

**Phase 12 IDs:** INV-007, INV-008 (+ INV-003, INV-017 where aggregation/governance intersect)

| Field | Detail |
|-------|--------|
| **Category** | calibration |
| **Status** | open |
| **Why deferred** | Phase 12 scope |
| **Risk if unresolved** | No evidenced relative-ATT calibration for TBRRidge modes |
| **Revisit when** | Phase 12 Run 002 + Kfold geometry decision |

### DID — operating-characteristic characterization

| Field | Detail |
|-------|--------|
| **Category** | causal_validity |
| **Status** | open |
| **Why deferred** | Phase 14 scope |
| **Risk if unresolved** | Unclear what cumulative-scale FPR/coverage mean for reviewers |
| **Revisit when** | Phase 14 DID OC appendix |

### AugSynth / CVXPY — validation wiring

| Field | Detail |
|-------|--------|
| **Category** | operational |
| **Status** | open |
| **Why deferred** | Phase 15 scope; unit tests only today |
| **Risk if unresolved** | Expert-review maturity overstates automated evidence |
| **Revisit when** | Recovery configs or permanent research-only guard |

### MTGP orchestration

| Field | Detail |
|-------|--------|
| **Category** | research |
| **Status** | open |
| **Why deferred** | Skipped; no recovery; MCMC cost |
| **Risk if unresolved** | Experimental runtime in production-like flows |
| **Revisit when** | Performance budget + optional-dep CI matrix |

### TROP — NaN-tolerant recovery smoke

| Field | Detail |
|-------|--------|
| **Category** | estimator_behavior |
| **Status** | open |
| **Why deferred** | Research-only; skipped batch |
| **Risk if unresolved** | Silent non-finite metrics in comparisons |
| **Revisit when** | Path D characterization or hard skip |

---

## Index by topic (quick lookup)

| Topic | Section |
|-------|---------|
| Phase 12 program (INV-003/007/008/017) | Phase 12 investigation program |
| BRB inference behavior (INV-008) | Inference concerns |
| Kfold multi-treated geometry (INV-007) | Inference concerns |
| SCM over-coverage | Critical investigations |
| DID interval semantics | Inference concerns |
| Spillover estimation | Research backlog |
| SDID staggered validation | Research backlog |
| Bayesian inference paths | Inference concerns |
| MTGP orchestration | Estimator-specific |
| Dynamic causal models | Research backlog |
| Donor collinearity | DGP realism |
| Missingness realism | DGP realism |
| Calibration scaling (INV-017) | DGP realism / Phase 12 program |
| Trust-score evolution (INV-017) | Deferred architecture / Phase 12 program |

---

*Update when investigations close, new calibration runs are archived, or Phase 12–15 evidence arrives. Do not delete entries without resolution evidence.*
