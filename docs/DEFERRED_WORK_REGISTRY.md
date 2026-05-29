# Deferred work registry

**Status:** active governance artifact  
**Last updated:** 2026-05-28  
**Package version:** 0.2.1  

**Related:** [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) (active questions) · [`ROADMAP_V4.md`](ROADMAP_V4.md) (phase sequencing) · [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) (archive lifecycle) · [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) (Phase 12 closure)

---

## 1. Purpose and lifecycle

### Purpose

This registry is **institutional memory** for findings that emerge from investigations, audits, operating-characteristic studies, calibration runs, failure analyses, roadmap reviews, algorithm reassessments, and governance decisions.

It prevents known issues, limitations, deferred fixes, and strategic capabilities from being **discovered once, documented once, and lost** as the platform grows.

| Document | Role |
|----------|------|
| [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) | **Active questions** — what we are still trying to understand or decide |
| **`DEFERRED_WORK_REGISTRY.md`** | **Known future work** — characterized findings, accepted limitations, and deferred capabilities awaiting a revisit trigger |

**Deferred ≠ abandoned.** **Accepted ≠ fixed.** Every entry must remain traceable to evidence.

### Dispositions

Every investigation, audit, calibration run, or governance decision **must close with exactly one disposition** for each material finding:

| Disposition | Meaning | Registry action |
|-------------|---------|-----------------|
| **Fixed** | Root cause addressed; evidence archived | Move entry to **Resolved** appendix or mark **Fixed** with fix artifact |
| **Deferred** | Known gap or capability; fix/work intentionally postponed | **Active registry entry** with revisit trigger |
| **Accepted** | Known limitation documented; no near-term fix planned | **Active registry entry**; may be permanent policy boundary |
| **Rejected** | Proposed approach evaluated and declined | **Active or retired entry** with rejection rationale |
| **Investigating** | Question open; evidence incomplete | Cross-link [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md); promote to Deferred when characterized |
| **Escalated** | Requires governance decision, product policy, or phase gate | Cross-link roadmap phase; block silent implementation |

**Rule:** No investigation, audit, calibration run, or governance decision may close **without a disposition** for each material finding. **No orphan findings.**

### Entry lifecycle

```
Finding emerges → Investigating (OPEN_INVESTIGATIONS)
              → Characterized → Deferred / Accepted / Rejected / Escalated (this registry)
              → Work completed → Fixed (resolved appendix)
              → Trigger obsolete → Retired (resolved appendix)
```

Updates require: disposition change, new evidence citation, or explicit retirement rationale — not silent deletion.

---

## 2. Registry schema

Each entry uses this schema:

| Field | Required | Description |
|-------|----------|-------------|
| **ID** | Yes | `DEF-xxx` — stable identifier |
| **Title** | Yes | Short human-readable name |
| **Category** | Yes | e.g. inference, calibration, causal_validity, architecture, platform, governance |
| **Source artifact(s)** | Yes | Investigation doc, calibration run, audit, policy file |
| **Status** | Yes | Fixed · Deferred · Accepted · Rejected · Investigating · Escalated |
| **Why deferred** | Yes | Honest rationale — not a placeholder |
| **Risk if not addressed** | Yes | What breaks if forgotten |
| **Revisit trigger** | Yes | Explicit event that should reopen the item |
| **Future work** | Yes | What would be done when triggered (not a priority rank) |
| **Related investigations** | Yes | `INV-xxx` cross-links |
| **Related roadmap area** | Yes | Phase, Track A/B/C, or validation path |

Optional: **Resolution date**, **Resolution artifact**, **Supersedes**.

---

## 3. Initial registry population

### DEF-001 — Multi-treated KFold support

| Field | Value |
|-------|--------|
| **Category** | inference / geometry |
| **Source artifact(s)** | [`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md) · [`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) §2.3 · Run 001 |
| **Status** | **Deferred** |
| **Why deferred** | INV-007 characterized 100% `ValueError` broadcast `(n_pre, n_treated)` vs `(n_pre,)` for n_treated ≥ 2. Fix requires inference geometry redesign or explicit single-treated-only contract — not characterized as a one-line patch. |
| **Risk if not addressed** | Users enabling Kfold on multi-geo panels get hard failures; eligibility reconsideration without geometry contract repeats Run 001 failure surface. |
| **Revisit trigger** | Need for multi-treated TBRRidge inference; Phase 13 governance decision; explicit product requirement for Kfold on pooled treated paths |
| **Future work** | Either implement multi-treated k-fold path geometry with OC archive, or ratify **single-treated-only** contract in validation docs and registry skip reason |
| **Related investigations** | INV-007 · INV-003 (aggregation interacts with pooled paths) |
| **Related roadmap area** | Phase 12 → Phase 13 TBRRidge decision · Track A |

---

### DEF-002 — BRB positive-scenario undercoverage

| Field | Value |
|-------|--------|
| **Category** | calibration / inference |
| **Source artifact(s)** | [`CALIBRATION_RUN_002.md`](CALIBRATION_RUN_002.md) · [`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) §2.2 |
| **Status** | **Deferred** |
| **Why deferred** | Run 002 fixed bound-ordering (null FPR = 0, coverage = 1) but positive scenario shows **coverage = 0**, **power = 0** with accurate points — intervals too narrow to contain truth 0.10 (width ≈ 0.043). Not a threshold-tuning problem; mechanism requires inference/OC redesign or governed usage boundary. |
| **Risk if not addressed** | Re-eligibility without positive OC → false lift-detection or false calibration claims; TrustReport may overstate interval validity. |
| **Revisit trigger** | Phase 13 eligibility reconsideration; TBRRidge promotion decision; need for positive-scenario nominal calibration claims |
| **Future work** | OC characterization of width mechanism; optional geometry sensitivity; failure analysis for positive under-coverage; governance decision (monitor-only vs redesign vs research-only) |
| **Related investigations** | INV-008 · INV-017 |
| **Related roadmap area** | Phase 12 → Phase 13 · Track A calibration honesty |

---

### DEF-003 — DID relative-ATT interval support

| Field | Value |
|-------|--------|
| **Category** | inference / estimand |
| **Source artifact(s)** | `did_interval_policy.py` · [`PHASE8_ALGORITHM_AUDIT.md`](PHASE8_ALGORITHM_AUDIT.md) §3 · [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · `tests/test_did_interval_policy.py` |
| **Status** | **Accepted** (policy) · relative-path work **Deferred** |
| **Why deferred** | Phase 6 policy: cumulative bootstrap intervals only; scaling cumulative CIs to relative ATT **rejected** as false calibration. Relative-ATT interval design deferred pending estimand proof and new interval construction. |
| **Risk if not addressed** | Users expect DID relative-ATT calibration comparable to SCM/TBR recovery; cross-family false agreement. |
| **Revisit trigger** | New relative-ATT interval design with estimand proof; Phase 14 DID OC; explicit product requirement for relative DID CIs |
| **Future work** | Design aligned relative interval path; recovery wiring only after OC + failure analysis; do not rescale cumulative bootstrap |
| **Related investigations** | INV-005 · INV-006 · INV-032 (DID pretrend / timing) |
| **Related roadmap area** | Phase 14 DID OC · Track A estimand discipline |

---

### DEF-004 — Spillover estimation and interference modeling

| Field | Value |
|-------|--------|
| **Category** | causal_validity / research |
| **Source artifact(s)** | [`PHASE8_ALGORITHM_AUDIT.md`](PHASE8_ALGORITHM_AUDIT.md) §3 · [`ROADMAP_V4.md`](ROADMAP_V4.md) · DGP `scm_donor_contamination` · [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) § Spillover |
| **Status** | **Deferred** |
| **Why deferred** | DGP stress exists; core SCM/TBR/DID estimators have **no spillover term**. Partial-interference product requirement not scoped. |
| **Risk if not addressed** | Overconfident geo incrementality under interference; TrustReport cannot emit `interference_detected` with estimator backing. |
| **Revisit trigger** | Partial-interference product requirement; GeoX design with explicit spillover review; Track C exposure-eligibility work (INV-026) |
| **Future work** | Research spike on spillover-adjusted estimands; DGP + recovery characterization before any promotion |
| **Related investigations** | INV-009 (spillover) · INV-026 (exposure eligibility) |
| **Related roadmap area** | Research backlog · Track C (interference semantics) |

---

### DEF-005 — SyntheticDID maturation

| Field | Value |
|-------|--------|
| **Category** | estimator / validation |
| **Source artifact(s)** | [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) (path D/E) · [`GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md`](GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md) · [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) |
| **Status** | **Deferred** |
| **Why deferred** | Staggered DGP metadata honest; `RecoveryRunner` **unwired**; `research_only`; skipped in batch calibration. |
| **Risk if not addressed** | SDID used in comparisons without recovery or OC backing; maturity labels misread as validated. |
| **Revisit trigger** | Recovery config wired; staggered OC smoke; explicit decision to pursue path D vs permanent research-only guard |
| **Future work** | Wire `RecoveryRunner` config; staggered adoption OC; METHOD_VALIDATION_PLAN path decision |
| **Related investigations** | INV-011 · INV-019 |
| **Related roadmap area** | Research backlog · Phase 15 adjacent |

---

### DEF-006 — BayesianTBR validation program

| Field | Value |
|-------|--------|
| **Category** | inference / validation |
| **Source artifact(s)** | [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · [`PHASE8_ALGORITHM_AUDIT.md`](PHASE8_ALGORITHM_AUDIT.md) §3 · [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) § Bayesian inference paths |
| **Status** | **Deferred** |
| **Why deferred** | Registry `Bayesian` on SCM/TBR ≠ `BayesianTBR` NUTS path; JAX optional deps; no recovery calibration program; path E/D skip. |
| **Risk if not addressed** | Wrong uncertainty claims in notebooks; MCMC outputs treated as frequentist CIs. |
| **Revisit trigger** | Optional-dep CI matrix; convergence policy defined; recovery wiring decision |
| **Future work** | Disambiguation table; convergence diagnostics policy; recovery + OC only after wiring |
| **Related investigations** | INV-015 |
| **Related roadmap area** | Research backlog · METHOD_VALIDATION_PLAN path D/E |

---

### DEF-007 — MTGP validation program

| Field | Value |
|-------|--------|
| **Category** | estimator / validation |
| **Source artifact(s)** | [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · [`GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md`](GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md) · [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) |
| **Status** | **Deferred** |
| **Why deferred** | Skipped batch; no recovery; MCMC cost; `research_only`. |
| **Risk if not addressed** | Experimental runtime in production-like flows; unvalidated GP uncertainty in comparisons. |
| **Revisit trigger** | Performance budget defined; optional-dep CI matrix; product interest in MTGP orchestration |
| **Future work** | Stability + performance characterization; recovery config or permanent skip guard |
| **Related investigations** | INV-011 (research estimators) |
| **Related roadmap area** | Research backlog · Phase 15 adjacent |

---

### DEF-008 — Calibration scaling and TrustReport evolution

| Field | Value |
|-------|--------|
| **Category** | governance / architecture |
| **Source artifact(s)** | [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) · [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) · [`CALIBRATION_RUN_002.md`](CALIBRATION_RUN_002.md) · [`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md) |
| **Status** | **Deferred** (governance partially **Investigating** via INV-017 archives) |
| **Why deferred** | CI smoke uses n ≪ production n=100; no nightly archival job; TrustReport / `CalibrationSignal` conceptual only — no calibrated trust model. |
| **Risk if not addressed** | Green smoke tests mistaken for production calibration; readiness misread as certification. |
| **Revisit trigger** | TrustReport implementation; nightly/production-tier archival job; Track B activation; eligibility reconsideration |
| **Future work** | Smoke vs production tier tags; archive schema enforcement; trust formation rules grounded in OC docs |
| **Related investigations** | INV-017 · INV-021 (TrustReport semantics) |
| **Related roadmap area** | Phase 12 governance · Track B · Track C |

---

### DEF-009 — Multi-treated aggregation semantics evolution

| Field | Value |
|-------|--------|
| **Category** | causal_validity / statistical_validity |
| **Source artifact(s)** | [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md) · `recovery_runner.py` · `tests/test_estimand_metric_alignment.py` |
| **Status** | **Deferred** (characterized — **Escalated** to Phase 13) |
| **Why deferred** | INV-003 showed A (canonical cell relative) ≈ B (pooled-path relative) under homogeneous default DGP, but B ≠ A under multi-treated heterogeneity (max |B−A| ≈ 0.00072 on 0.10 lift). Absolute DGP + relative scoring is hard incompatibility. Formal estimand registry and scoring contract evolution deferred to Phase 13 / Track B. |
| **Risk if not addressed** | Silent ATT labels across geo panels; structured recovery residuals under heterogeneity; MMM miscalibration from wrong aggregation contract. |
| **Revisit trigger** | Phase 13 governance decision; Track B `Estimand` registry design; heterogeneous DGP scenario catalog; TrustReport `incompatible_estimand` rules |
| **Future work** | Formal A vs B registry entry; single-treated scenario catalog; alternate scoring path evaluation; no silent change to `_path_relative_att` without policy chain |
| **Related investigations** | INV-003 · INV-020 · INV-001 · INV-002 |
| **Related roadmap area** | Phase 13 · Track B estimand contracts · Track C |

---

### DEF-010 — User-level experimentation feasibility engine

| Field | Value |
|-------|--------|
| **Category** | platform / governance |
| **Source artifact(s)** | [`ROADMAP_V4.md`](ROADMAP_V4.md) Track C · [`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md) § Experiment feasibility · [`GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md`](GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md) |
| **Status** | **Deferred** |
| **Why deferred** | Power/MDE exists for geo design; no cross-modality feasibility engine for A/B, conversion lift, GeoX, holdouts. Track C gated behind Track A + Track B contracts. |
| **Risk if not addressed** | Underpowered CLS/A/B studies run without governed viability assessment; TrustReport cannot emit `underpowered` with shared contract. |
| **Revisit trigger** | Track C activation; shared `ExperimentSpec` feasibility extension; conversion-lift product scoping |
| **Future work** | Governed feasibility contract across modalities; links to TrustReport and ExperimentSpec constraints — not a standalone calculator |
| **Related investigations** | INV-022 |
| **Related roadmap area** | Track C · after Track B |

---

### DEF-011 — Unified experimentation estimand contracts

| Field | Value |
|-------|--------|
| **Category** | architecture / causal_validity |
| **Source artifact(s)** | [`ROADMAP_V4.md`](ROADMAP_V4.md) § Unified estimand philosophy · [`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md) · [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md) |
| **Status** | **Deferred** |
| **Why deferred** | Geo `relative_att_post` best documented; A/B, CLS, MMM estimands not unified in a registry. INV-003 characterized geo aggregation; cross-modality contract not implemented. |
| **Risk if not addressed** | Silent “lift” labels across modalities; incompatible exports fed to MMM or TrustReport. |
| **Revisit trigger** | Track B `Estimand` registry design PR; after Phase 13 aggregation governance decision |
| **Future work** | Single estimand registry consumed by design, measurement, calibration, feasibility, trust layers |
| **Related investigations** | INV-020 · INV-003 |
| **Related roadmap area** | Track B · Track C |

---

### DEF-012 — Experiment-to-MMM compatibility resolver

| Field | Value |
|-------|--------|
| **Category** | architecture / calibration |
| **Source artifact(s)** | [`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md) § MMM calibration · [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md) §6 |
| **Status** | **Deferred** |
| **Why deferred** | No MMM API; geo evidence exports only; raw relative path lift ≠ calibrated MMM increment without explicit transform contract. |
| **Risk if not addressed** | Raw lift points fed to MMM as calibrated incrementality; iROAS claims without OC-backed bridge. |
| **Revisit trigger** | MMM integration milestone; calibrated contribution estimand defined; Track C holdout governance (INV-023) |
| **Future work** | Compatibility resolver mapping experiment estimand → MMM input; calibration transfer from archived OC, not single runs |
| **Related investigations** | INV-023 |
| **Related roadmap area** | Track C · Track B `ExperimentEvidence` |

---

### Additional evidenced entries

#### DEF-013 — SCM UnitJackKnife positive-scenario zero power

| Field | Value |
|-------|--------|
| **Category** | calibration / inference |
| **Source artifact(s)** | [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) · [`CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) §2.1 · `SCM_JACKKNIFE_CHARACTERIZATION_001.md` |
| **Status** | **Accepted** (usage boundary) · redesign **Deferred** |
| **Why deferred** | Phase 11 / Run 001: null pass with over-conservative intervals; power = 0 on positive despite accurate points — geometry/conservatism, not implementation defect. Role bounded to **null monitor**. |
| **Risk if not addressed** | SCM jackknife promoted as lift detector; false confidence in positive-scenario detection. |
| **Revisit trigger** | Product requires power claims; eligibility or maturity discussion; inference redesign proposal |
| **Future work** | Maintain null-monitor-only boundary; optional single-treated power benchmarking scenario (documentation) |
| **Related investigations** | INV-004 · INV-039 |
| **Related roadmap area** | Phase 11 (complete) · Phase 13 · Track A |

#### DEF-014 — Cross-estimator estimand enforcement

| Field | Value |
|-------|--------|
| **Category** | causal_validity |
| **Source artifact(s)** | [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) § Cross-estimator · [`PHASE8_ALGORITHM_AUDIT.md`](PHASE8_ALGORITHM_AUDIT.md) · [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md) |
| **Status** | **Deferred** |
| **Why deferred** | Requires per-family contract layer; SCM/TBR/DID exports not interchangeable as “the ATT” without declared estimand. |
| **Risk if not addressed** | False agreement across estimators on experiment cards. |
| **Revisit trigger** | Estimand matrix in validation docs; Track B registry; equivalence tests vs DGP truth |
| **Future work** | Per-family estimand declarations; reviewer-facing incompatibility flags |
| **Related investigations** | INV-001 · INV-002 · INV-036 · INV-003 |
| **Related roadmap area** | Track B · ongoing documentation |

#### DEF-015 — Package demonstrated nominal calibration gap

| Field | Value |
|-------|--------|
| **Category** | calibration |
| **Source artifact(s)** | [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) · [`CALIBRATION_RUN_002.md`](CALIBRATION_RUN_002.md) · [`PHASE8_ALGORITHM_AUDIT.md`](PHASE8_ALGORITHM_AUDIT.md) §3 · `nominal_calibration.py` |
| **Status** | **Accepted** (current claim boundary) · closure **Deferred** |
| **Why deferred** | Only `SCM_UnitJackKnife` eligible; BRB/Kfold excluded; SCM zero power on positive; no package-wide nominal calibration demonstrated. |
| **Risk if not addressed** | Over-claiming calibration or expert-review expansion without evidence. |
| **Revisit trigger** | Phase 13 governance decision; explicit package-level null-monitor-only statement ratified; new eligible configs with full OC chain |
| **Future work** | Document honest package calibration scope; update only via promotion policy chain |
| **Related investigations** | INV-039 · INV-008 · INV-007 |
| **Related roadmap area** | Phase 11–13 · Track A |

#### DEF-016 — DID operating-characteristic characterization

| Field | Value |
|-------|--------|
| **Category** | causal_validity / calibration |
| **Source artifact(s)** | [`ROADMAP_V4.md`](ROADMAP_V4.md) Phase 14 · [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · [`PHASE8_ALGORITHM_AUDIT.md`](PHASE8_ALGORITHM_AUDIT.md) |
| **Status** | **Deferred** |
| **Why deferred** | Phase 14 not executed; cumulative-scale FPR/coverage meaning for reviewers not archived; pretrend waiver discipline relies on humans. |
| **Risk if not addressed** | Unclear what DID cumulative CIs mean for calibration; credible results under pretrend violation. |
| **Revisit trigger** | Phase 14 activation; DID OC appendix scoped |
| **Future work** | OC on `did_parallel_trends_*`; strengthen reviewer contract; confirm DEF-003 policy remains |
| **Related investigations** | INV-005 · INV-006 · INV-032 |
| **Related roadmap area** | Phase 14 · Track A |

#### DEF-017 — AugSynth / CVXPY validation wiring

| Field | Value |
|-------|--------|
| **Category** | validation / operational |
| **Source artifact(s)** | [`ROADMAP_V4.md`](ROADMAP_V4.md) Phase 14 · [`PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md`](PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md) · [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) |
| **Status** | **Investigating** → execution via Phase 14 |
| **Why deferred** | Unit tests only; no `RecoveryRunner` configs or permanent research-only guard finalized. OC program: [`PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md`](PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md). |
| **Risk if not addressed** | Expert-review maturity overstates automated evidence for CVXPY variants. |
| **Revisit trigger** | Phase 14 execution; `PHASE14_AUGSYNTH_CHARACTERIZATION_001.md` archive; collinearity scenario (INV-037) |
| **Future work** | Execute INV-028; recovery wiring per OC outcome; VALIDATION_COVERAGE update |
| **Related investigations** | INV-018 · INV-037 · **INV-028** |
| **Related roadmap area** | Phase 14 · Track A |

#### DEF-018 — Absolute-effect DGP vs relative recovery scoring

| Field | Value |
|-------|--------|
| **Category** | statistical_validity / estimand |
| **Source artifact(s)** | [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md) §4 · `recovery_runner.py` |
| **Status** | **Accepted** (incompatibility) · alternate path **Deferred** |
| **Why deferred** | Recovery scores `_path_relative_att` against canonical truth; on absolute-effect DGPs truth and path differ by orders of magnitude — hard scale mismatch, not tuning. |
| **Risk if not addressed** | Absolute business questions scored with relative recovery metrics; TrustReport false passes. |
| **Revisit trigger** | Absolute-effect scenario catalog; alternate scoring path proposal; `incompatible_estimand` TrustReport rules |
| **Future work** | Exclude absolute DGPs from relative recovery battery or add declared alternate scoring contract |
| **Related investigations** | INV-003 · INV-020 |
| **Related roadmap area** | Phase 13 · Track B |

#### DEF-019 — AugSynth OC characterization (Phase 14)

| Field | Value |
|-------|--------|
| **Category** | validation / calibration |
| **Source artifact(s)** | [`PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md`](PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md) · [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) AugSynthCVXPY row |
| **Status** | **Investigating** (plan committed; execution pending) |
| **Why deferred** | AugSynthCVXPY is expert-review tier without n≥100 OC archive; no recovery runner wiring; strategic core-instrument candidate uncharacterized. |
| **Risk if not addressed** | Track B trust contracts cite immature instrument; GeoX over-claims AugSynth validity. |
| **Revisit trigger** | Phase 14 execution; `PHASE14_AUGSYNTH_CHARACTERIZATION_001.md` archive; Track B implementation prioritization |
| **Future work** | INV-028 geometry + null/positive OC; failure analysis if anti-calibration; governance disposition (expert-review / research-only / restrict) |
| **Related investigations** | INV-028 · INV-018 · INV-037 · DEF-017 |
| **Related roadmap area** | Phase 14 · Track A · Track B gate |

#### DEF-020 — Placebo inference OC characterization (Phase 15)

| Field | Value |
|-------|--------|
| **Category** | inference / calibration |
| **Source artifact(s)** | [`PHASE15_PLACEBO_INVESTIGATION_PLAN.md`](PHASE15_PLACEBO_INVESTIGATION_PLAN.md) · [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) § Placebo vs CI · `IntervalType.PLACEBO_BAND` |
| **Status** | **Investigating** (plan committed; execution pending) |
| **Why deferred** | Placebo catalog-listed for SCM/TBR but no OC archive; `placebo_band` vs CI semantic gap; not in nominal calibration registry. |
| **Risk if not addressed** | Placebo bands misread as confidence intervals; TrustReport mis-calibration claims; wrong null-monitor trust. |
| **Revisit trigger** | Phase 15 execution; `PHASE15_PLACEBO_CHARACTERIZATION_001.md` archive; TrustReport placebo export policy |
| **Future work** | INV-029 null/positive OC; interval-alignment policy decision; export discipline recommendations |
| **Related investigations** | INV-029 · placebo vs CI (OPEN_INVESTIGATIONS) |
| **Related roadmap area** | Phase 15 · Track A · Track B gate |

---

## 4. Revisit-trigger policy

Every deferred or accepted entry **must** have an explicit revisit trigger. Triggers are **events**, not dates.

### Standard trigger catalog

| Trigger | Typical entries reopened |
|---------|-------------------------|
| **Need for multi-treated inference** | DEF-001, DEF-009 |
| **Eligibility reconsideration** | DEF-001, DEF-002, DEF-015 |
| **Phase gate (13 / 14 / 15)** | DEF-002, DEF-009, DEF-016, DEF-017, **DEF-019**, **DEF-020** |
| **Track B implementation prioritization** | DEF-019, DEF-020 (core instrument OC) |
| **Track B activation** | DEF-008, DEF-011, DEF-014 |
| **Track C activation** | DEF-010, DEF-011, DEF-012, DEF-004 |
| **MMM integration work** | DEF-012, DEF-011 |
| **TrustReport implementation** | DEF-008, DEF-009, DEF-010, DEF-018 |
| **Release-gate expansion** | DEF-008, DEF-015 |
| **Recovery wiring decision** | DEF-005, DEF-006, DEF-007, DEF-017, **DEF-019** |
| **Product interference / spillover requirement** | DEF-004 |
| **New relative-ATT interval design (DID)** | DEF-003 |

### Trigger discipline

1. **No silent reopen** — log disposition change and evidence in this registry or resolved appendix.  
2. **Investigation first** — if trigger fires but question is open, use **Investigating** in OPEN_INVESTIGATIONS before changing Deferred → Fixed.  
3. **Escalation** — if trigger requires governance decision (e.g. eligibility), mark **Escalated** and cite phase doc — do not implement in evidence-only PRs.

---

## 5. Governance integration

### Closure requirement

Every future:

| Activity | Must produce |
|----------|--------------|
| Investigation (INV-xxx) | Disposition per finding → registry entry or resolved appendix |
| Audit | Disposition per material risk |
| OC characterization | Disposition per config/scenario outcome |
| Calibration study (Run xxx) | Disposition per config × scenario headline |
| Governance decision (Phase xx) | Disposition per config/policy outcome |

**Acceptable closures:**

- **Fixed item** — with fix artifact and verification evidence  
- **Deferred item** — with revisit trigger and risk statement  
- **Rejected item** — with rationale (e.g. cumulative-to-relative scaling)  
- **Accepted limitation** — with usage boundary (e.g. SCM null monitor, DID relative CIs unsupported)

**Unacceptable:** findings mentioned only in PR comments, Slack, or unlinked local JSON.

### Archive chain (calibration example)

Per [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md):

```
Run archive → Failure analysis (if fail) → OC / investigation doc → Registry disposition → Phase governance decision → Eligibility change (optional, last)
```

Registry entries **DEF-001**, **DEF-002**, **DEF-009**, **DEF-013**, **DEF-015** trace this chain for Phase 12.

### Cross-reference maintenance

When [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) closes or characterizes an item, add or update the corresponding **DEF-xxx** entry here. When disposition becomes **Fixed**, move to §8 Resolved appendix.

---

## 6. Roadmap integration

Roadmap reviews ([`ROADMAP_V4.md`](ROADMAP_V4.md) and successors) **must** include a deferred-work pass:

| Review action | Registry operation |
|---------------|-------------------|
| New finding from phase work | Add DEF-xxx or update Investigating → Deferred |
| Work completed in phase | Mark **Fixed**; move to resolved appendix |
| Trigger fired | Reopen or escalate; link new evidence |
| Scope permanently out of product | Mark **Rejected** or **Retired** with rationale |
| Accepted policy boundary | Mark **Accepted**; ensure usage docs cite DEF-xxx |

**Roadmap sequencing is unchanged by this registry.** The registry records **what is known and deferred** — it does not reprioritize phases or promote estimators.

Companion at re-audit: update [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) for active questions; update this file for institutional memory.

---

## 7. Non-goals

This registry is **not**:

| Not this | Why |
|----------|-----|
| Backlog prioritization | No rank ordering; triggers drive reopen |
| Estimator ranking | Maturity lives in validation docs and policy chain |
| Release planning | Phases remain in ROADMAP_v4 |
| Maturity scoring | Promotion policy unchanged |
| Implementation tracker | No sprint tasks or assignees |

This registry **is**:

- **Institutional memory** for characterized gaps and deferred capabilities  
- **Disposition enforcement** so findings do not become orphans  
- **Revisit-trigger catalog** for honest reactivation  
- **Bridge** between investigations (questions) and roadmap (sequencing)

---

### Phase 12–13 closure (2026-05-28)

Phase 12 investigation tracks closed by [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md). Corresponding dispositions:

| Investigation | Disposition | DEF entry |
|---------------|-------------|-----------|
| INV-003 | Escalated → Deferred | DEF-009, DEF-018 |
| INV-007 | Deferred | DEF-001 |
| INV-008 | Deferred (partial fix: bounds) | DEF-002 |
| INV-017 | Deferred | DEF-008 |
| Phase 11 SCM OC | Accepted | DEF-013 |
| INV-028 (AugSynth OC) | Investigating | DEF-019, DEF-017 |
| INV-029 (Placebo OC) | Investigating | DEF-020 |

**Phase 14–15 (planned):** AugSynth and Placebo characterization plans committed — execution pending ([`PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md`](PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md), [`PHASE15_PLACEBO_INVESTIGATION_PLAN.md`](PHASE15_PLACEBO_INVESTIGATION_PLAN.md)).

**Eligibility unchanged:** `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = {"SCM_UnitJackKnife"}`.

---

## 8. Resolved appendix

Entries moved here when **Fixed** or **Retired**. None at initial publication (2026-05-28).

| ID | Title | Resolution | Date | Artifact |
|----|-------|------------|------|----------|
| — | — | — | — | — |

### Partial fixes (documented, work remains deferred)

| Finding | Fix scope | Remaining deferred ID |
|---------|-----------|------------------------|
| BRB inverted bounds (Run 001) | Bound-ordering guard + fix; null OC sane (Run 002) | **DEF-002** (positive under-coverage) |
| INV-003 aggregation characterization | Semantic archive; A ≈ B on default DGP | **DEF-009** (governance evolution) |
| INV-007 KFold geometry | Failure surface archived | **DEF-001** (support or contract) |

---

## Index by category

| Category | IDs |
|----------|-----|
| inference / geometry | DEF-001, DEF-002, DEF-003, DEF-006, **DEF-020** |
| calibration | DEF-002, DEF-008, DEF-013, DEF-015, DEF-016, **DEF-019**, **DEF-020** |
| causal_validity / estimand | DEF-003, DEF-004, DEF-009, DEF-014, DEF-018 |
| validation / estimators | DEF-005, DEF-006, DEF-007, DEF-017, **DEF-019** |
| platform / Track C | DEF-010, DEF-011, DEF-012 |
| governance / architecture | DEF-008, DEF-011 |

---

*Update when dispositions change, phases complete, or new evidence archives close investigations. Do not delete entries without resolution or retirement rationale.*
