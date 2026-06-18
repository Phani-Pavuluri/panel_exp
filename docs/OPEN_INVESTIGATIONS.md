# Open investigations

**Status:** living backlog for intentionally deferred or unresolved issues  
**Last updated:** 2026-06-18  
**Package version:** 0.2.1  

**Authoritative registry (Track D trust lanes):** [`governance/OPEN_INVESTIGATIONS_001.json`](governance/OPEN_INVESTIGATIONS_001.json) — machine-readable source of truth per [`INVESTIGATION_LIFECYCLE_AND_HANDOFF_CONTRACT_001.md`](INVESTIGATION_LIFECYCLE_AND_HANDOFF_CONTRACT_001.md). This markdown file retains Phase 12 historical context; new unresolved findings must be registered in the JSON ledger with revisit triggers.

**Related:** `docs/ROADMAP_V3.md` (governance), `docs/ROADMAP_V4.md` (Phases 11–15; Tracks A/B/C), `docs/METHOD_VALIDATION_PLAN.md`, `docs/VALIDATION_COVERAGE.md`, `docs/EXPERIMENTATION_PLATFORM_VISION.md`, [`docs/DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md)

---

## OPEN_INVESTIGATIONS vs DEFERRED_WORK_REGISTRY

Two complementary ledgers — not duplicates.

| Document | Question it answers | Typical contents |
|----------|---------------------|------------------|
| **`OPEN_INVESTIGATIONS.md`** (this file) | **What are we still investigating?** | Open questions, active Phase 12 tracks, hypothesis-to-test framing |
| **[`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md)** | **What do we already know is deferred?** | Characterized findings, accepted limitations, deferred fixes, deferred platform capabilities |

**Workflow:** A gap starts as an **investigation** here. When characterized, it receives a **disposition** (Fixed · Deferred · Accepted · Rejected · Escalated) and a **`DEF-xxx`** entry in the deferred registry. Investigations may close; deferred work remains until a revisit trigger fires or the item is fixed.

**Rule (both docs):** No investigation, audit, calibration run, or governance decision may close without a disposition — **no orphan findings**.

---

## Purpose

Track **unresolved gaps, deferred work, and open scientific questions** discovered during development. This is institutional memory for honest governance — not an implementation roadmap and not proof of correctness.

For **known future work** already characterized (e.g. DEF-001 KFold geometry, DEF-002 BRB positive under-coverage, DEF-009 aggregation semantics, **DEF-021 jackknife family alternatives**), see [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md).

**Deferred ≠ abandoned.** Items remain listed until evidence closes them. Passing tests, calibration plumbing, or implemented diagnostics do not close an investigation without archived operating-characteristic evidence.

**Not claimed:** `production_safe` for any estimator; package-wide nominal calibration (only partial SCM null monitoring is evidenced).

---

## Phase 12 investigation program (TBRRidge) — **CLOSED**

**Status:** **Closed** 2026-05-28 by [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md).  
**Framing:** Characterize whether TBRRidge inference can support calibrated expert-review workflows — **not** “fix TBRRidge.” All outcomes are acceptable if evidenced.

| ID | Track | Disposition | Primary artifact | DEF entry |
|----|-------|-------------|------------------|-----------|
| **INV-007** | KFold geometry | **Deferred** | [`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md) | DEF-001 |
| **INV-008** | BRB OC after bound fix | **Deferred** (bounds **Fixed**) | [`CALIBRATION_RUN_002.md`](CALIBRATION_RUN_002.md) | DEF-002 |
| **INV-003** | Multi-treated aggregation | **Deferred** | [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md) | DEF-009, DEF-018 |
| **INV-017** | Calibration governance | **Deferred** | [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) | DEF-008 |

**Phase 13 outcomes:** SCM retain (null monitor); BRB restrict (excluded); Kfold restrict (research-only on default DGP). Eligibility registry **unchanged**.

---

## Active Track D investigations (research lane)

| ID | Track | Status | Primary artifact | Disposition |
|----|-------|--------|------------------|-------------|
| **INV-D1-001** | Pre-period matching leakage | **Fix applied** (`61a174f`) | [`investigations/INV-D1-001_PRE_PERIOD_MATCHING_LEAKAGE.md`](investigations/INV-D1-001_PRE_PERIOD_MATCHING_LEAKAGE.md) · [`track_d/archives/D5_DES_001a_results.json`](track_d/archives/D5_DES_001a_results.json) | **characterization_required** — D5 re-run Jaccard **1.0**; D2 complete |
| **INV-D2-001** | SCM `full_model` post-period weight fit | **Proposed** (D2-FIND-001) | [`TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md`](TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md) §10 | **investigating** — characterize via D5-EST-002b; fix in separate governed PR |
| **INV-D3-001** | Unit JK LOO target (`y` vs `y_hat_{-i}`) | **Fix accepted** | [`investigations/INV-D3-001_UNIT_JACKKNIFE_LOO_TARGET.md`](investigations/INV-D3-001_UNIT_JACKKNIFE_LOO_TARGET.md) · [`D5_INF_002b_results.json`](track_d/archives/D5_INF_002b_results.json) | **fix_accepted** — null_monitor_only unchanged |

**D5-DES-001a headline (post-fix):** `pre_treatment_period` path matches pre-only reference (Jaccard **1.00**). Pre-fix baseline Jaccard **0.27** documented in artifact history.

**D2 headline:** Default geo SCM donor pool and pre-fit path **OK**; `full_model=True` paths flagged — no code fix in D2 package.

**D3 headline:** Inference semantics and Track B alignment **OK**; SCM JK null-monitor only; placebo diagnostic single-treated; eligibility registry **unchanged**.

**D5-INF-002a headline:** Pre-fix JK sensitive to treated post noise (rel Δ **3.0×**). **D5-INF-002b:** post-fix prod=ref (ratio **1.0**), treated noise Δ **0** — **INV-D3-001 fix accepted**.

**D4 headline:** Geo `PowerAnalysis` is **diagnostic_only**; default path **TBRRidge+Kfold** on aggregated panel — **not** aligned to **SCM_UnitJackKnife** readout ([`TRACK_D_D4_POWER_MDE_AUDIT_001.md`](TRACK_D_D4_POWER_MDE_AUDIT_001.md)).

---

## Active Track A investigations (post–Phase 14)

| ID | Track | Status | Primary artifact | DEF entry |
|----|-------|--------|------------------|-----------|
| **INV-030** | Jackknife family characterization | **Investigating** (plan committed) | [`INV030_JACKKNIFE_FAMILY_CHARACTERIZATION_PLAN.md`](INV030_JACKKNIFE_FAMILY_CHARACTERIZATION_PLAN.md) | DEF-013 (refine), **DEF-021** (alternatives backlog) |
| **INV-031** | Inference conservatism synthesis | **Investigating** (plan committed) | [`INV031_INFERENCE_CONSERVATISM_PLAN.md`](INV031_INFERENCE_CONSERVATISM_PLAN.md) | DEF-013, DEF-002, DEF-020, DEF-015 |
| **INV-029** | Placebo OC | **Closed — characterized** | [`PHASE15_PLACEBO_CHARACTERIZATION_001.md`](PHASE15_PLACEBO_CHARACTERIZATION_001.md) | DEF-020 (governance pending) |

### INV-030 — Jackknife family characterization

| Field | Detail |
|-------|--------|
| **Category** | inference / calibration / governance |
| **Status** | **investigating** — plan committed; execution pending |
| **Why open** | Phase 11 + Phase 14 characterized **implemented `UnitJackKnife` only**; shared conservatism (coverage ≈ 1, FPR ≈ 0, power ≈ 0) unexplained at **family** level |
| **Governing question** | Is conservatism expected donor-sensitivity semantics vs geometry/aggregation artifact — and which jackknife **families** merit future OC? |
| **Risk if unresolved** | Track B trust contracts mislabel JK intervals as lift-detection CIs; premature jackknife+ scope |
| **Revisit when** | INV-030 execution archive; Track B uncertainty semantics design |
| **Non-goals** | No variant implementation; no eligibility/maturity/release-gate change |

**Distinction:** Phase 11 (`SCM_JACKKNIFE_CHARACTERIZATION_001.md`) and Phase 14 (`PHASE14_AUGSYNTH_CHARACTERIZATION_001.md` §4) = **implemented path OC**. INV-030 = **family semantics + inventory + explanatory synthesis**.

---

## Future platform investigations (Track C)

**Framing:** User-level experimentation, conversion lift, MMM calibration bridges, and cross-modality trust semantics — **future architecture / governance** only. Gated behind Track A stabilization and Track B shared contracts (`ExperimentSpec`, `ExperimentEvidence`, estimand registry).

**Conceptual reference:** Industry conversion-lift practice (e.g. Google Conversion Lift — ghost ads, opportunity logging, user-randomized designs) informs **governance questions** — not mathematical implementation blueprints.

**No code, API, schema, eligibility, or production behavior in v0.2.1.**

| ID | Title | Category | Status |
|----|-------|----------|--------|
| **INV-020** | Unified experimentation estimand contracts | architecture / causal_validity | intentionally_deferred |
| **INV-021** | User-randomized experiment TrustReport semantics | governance / architecture | intentionally_deferred |
| **INV-022** | Experiment feasibility and viability governance | governance / operational | intentionally_deferred |
| **INV-023** | Experiment-to-MMM compatibility resolver | architecture / calibration | intentionally_deferred |
| **INV-024** | Sequential experimentation governance | governance / statistical_validity | intentionally_deferred |
| **INV-025** | Randomization integrity and SRM diagnostics | operational / causal_validity | intentionally_deferred |
| **INV-026** | Exposure eligibility and opportunity logging semantics | causal_validity / architecture | intentionally_deferred |

### INV-020 — Unified experimentation estimand contracts

| Field | Detail |
|-------|--------|
| **Category** | architecture / causal_validity |
| **Status** | intentionally_deferred |
| **Why deferred** | Geo `relative_att_post` documented; A/B/CLS/MMM estimands not unified |
| **Risk if unresolved** | Silent “lift” labels across modalities; MMM miscalibration |
| **Revisit when** | Track B `Estimand` registry design PR; after Phase 12 aggregation semantics (INV-003) |

### INV-021 — User-randomized experiment TrustReport semantics

| Field | Detail |
|-------|--------|
| **Category** | governance / architecture |
| **Status** | intentionally_deferred |
| **Why deferred** | TrustReport taxonomy conceptual only; no user-level experiments |
| **Risk if unresolved** | `inconclusive` misread as null; binary launch/stop narratives |
| **Revisit when** | TrustReport outcome taxonomy ratified in platform vision + Track B evidence schema |

### INV-022 — Experiment feasibility and viability governance

| Field | Detail |
|-------|--------|
| **Category** | governance / operational |
| **Status** | intentionally_deferred |
| **Why deferred** | Power/MDE exists for design; no cross-modality feasibility engine |
| **Risk if unresolved** | Underpowered CLS/A/B studies run without governed viability assessment |
| **Revisit when** | Shared feasibility contract scoped for A/B, CLS, GeoX, holdouts |

### INV-023 — Experiment-to-MMM compatibility resolver

| Field | Detail |
|-------|--------|
| **Category** | architecture / calibration |
| **Status** | intentionally_deferred |
| **Why deferred** | No MMM API; geo evidence exports only |
| **Risk if unresolved** | Raw lift points fed to MMM as calibrated incrementality |
| **Revisit when** | MMM integration milestone; calibrated contribution estimand defined |

### INV-024 — Sequential experimentation governance

| Field | Detail |
|-------|--------|
| **Category** | governance / statistical_validity |
| **Status** | intentionally_deferred |
| **Why deferred** | No sequential testing product surface |
| **Risk if unresolved** | Peeking and optional stopping without human-governed discipline |
| **Revisit when** | Track C experimentation orchestration design |

### INV-025 — Randomization integrity and SRM diagnostics

| Field | Detail |
|-------|--------|
| **Category** | operational / causal_validity |
| **Status** | intentionally_deferred |
| **Why deferred** | Geo randomization differs from user-level SRM patterns |
| **Risk if unresolved** | Assignment bugs undetected in user-randomized studies |
| **Revisit when** | User/session randomization in `ExperimentSpec`; links to TrustReport |

### INV-026 — Exposure eligibility and opportunity logging semantics

| Field | Detail |
|-------|--------|
| **Category** | causal_validity / architecture |
| **Status** | intentionally_deferred |
| **Why deferred** | Ghost-ad / opportunity concepts are Track C governance only |
| **Risk if unresolved** | Conversion lift estimands misaligned with exposure definition |
| **Revisit when** | Conversion lift `ExperimentSpec` extension; not vendor-specific copy |

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
| **Status** | **closed — accepted** (Phase 13) |
| **Resolution** | Phase 11 + Phase 13: null-monitor role ratified; zero power on positive is expected conservatism |
| **Disposition** | **DEF-013** |
| **Governance** | [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) §3 |

---

## Medium-priority investigations

### Heterogeneous vs pooled recovery scoring

**Phase 12 ID:** INV-003 — **Closed** (Phase 13: governance evolution **deferred**)

| Field | Detail |
|-------|--------|
| **Category** | statistical_validity |
| **Status** | **closed — deferred** |
| **Resolution** | INV-003 archive: A ≈ B on default DGP; drift under heterogeneity; absolute/relative hard mismatch |
| **Disposition** | **DEF-009**, **DEF-018** |
| **Revisit when** | Track B estimand registry; TrustReport rules |

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

**Phase 12 ID:** INV-008 — **Closed** (Phase 13: **restrict**, remain excluded)

| Field | Detail |
|-------|--------|
| **Category** | inference / calibration |
| **Status** | **closed — deferred** |
| **Resolution** | Run 002: bounds fixed; null pass; positive under-coverage. Keep excluded from eligibility. |
| **Disposition** | **DEF-002** in [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) |
| **Governance** | [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) §4 |

### TBRRidge Kfold multi-treated geometry

**Phase 12 ID:** INV-007 — **Closed** (Phase 13: **restrict**, research-only on default DGP)

| Field | Detail |
|-------|--------|
| **Category** | inference / geometry |
| **Status** | **closed — deferred** |
| **Resolution** | n_treated=1 viable; n_treated≥2 100% failure. Skip reason remains valid. |
| **Disposition** | **DEF-001** in [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) |
| **Governance** | [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) §5 |

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

**Superseded in planning by INV-030** — see [`INV030_JACKKNIFE_FAMILY_CHARACTERIZATION_PLAN.md`](INV030_JACKKNIFE_FAMILY_CHARACTERIZATION_PLAN.md) §4 (family inventory) and **DEF-021**.

| Field | Detail |
|-------|--------|
| **Category** | research |
| **Status** | **investigating** (INV-030 plan) |
| **Why deferred** | `uncertainty.md`; only leave-one-donor `UnitJackKnife` OC-archived; `JKP` / time jackknife+ uncharacterized |
| **Risk if unresolved** | Scope creep before OC gates; jackknife+ shipped without properties archive |
| **Revisit when** | INV-030 execution; governance approval for variant OC scope |
| **Disposition** | **DEF-021** |

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

**Phase 14 ID:** INV-028 — **Closed** (characterized)

| Field | Detail |
|-------|--------|
| **Category** | operational / validation |
| **Status** | **closed — characterized** |
| **Resolution** | [`PHASE14_AUGSYNTH_CHARACTERIZATION_001.md`](PHASE14_AUGSYNTH_CHARACTERIZATION_001.md): point expert-review candidate; UnitJackKnife null-monitor only; spillover DGP bias |
| **Disposition** | **DEF-019**, **DEF-017** (wiring still open) |
| **Revisit when** | RecoveryRunner registry wiring PR only |

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
| Phase 12 program (INV-003/007/008/017) | Phase 12 investigation program (**closed** — see Phase 13) |
| Phase 13 governance | [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) |
| Track C platform (INV-020–026) | Future platform investigations |
| Unified estimand contracts (INV-020) | Future platform investigations |
| TrustReport semantics (INV-021) | Future platform investigations |
| Feasibility governance (INV-022) | Future platform investigations |
| MMM compatibility (INV-023) | Future platform investigations |
| Sequential testing governance (INV-024) | Future platform investigations |
| SRM / randomization integrity (INV-025) | Future platform investigations |
| Exposure eligibility (INV-026) | Future platform investigations |
| BRB inference behavior (INV-008) | Inference concerns |
| Kfold multi-treated geometry (INV-007) | Inference concerns |
| Jackknife family semantics (INV-030) | Active Track A investigations |
| Jackknife+ / alternative families (DEF-021) | Inference concerns · INV-030 |
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
| Deferred work registry (DEF-xxx) | [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) |

---

*Update when investigations close, new calibration runs are archived, or Phase 12–15 / Track C evidence arrives. Do not delete entries without resolution evidence. When a finding is characterized, add or update the matching `DEF-xxx` entry in [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md).*
