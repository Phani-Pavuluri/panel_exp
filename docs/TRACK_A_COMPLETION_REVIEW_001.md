# Track A completion review 001

**Review ID:** TRACK-A-REVIEW-001  
**Status:** active roadmap checkpoint  
**Last updated:** 2026-05-20  
**Package version:** 0.2.1  

**Related:** [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) · [`PHASE15_GOVERNANCE_DECISION_001.md`](PHASE15_GOVERNANCE_DECISION_001.md) · [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) · [`TRACK_B_ARCHITECTURE_PLAN.md`](TRACK_B_ARCHITECTURE_PLAN.md) · [`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md) · [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md)

**Scope:** Assess whether Track A (estimator/inference governance and characterization) has accomplished its purpose and whether Track B may become the **primary** roadmap focus. **No code, registry, maturity, eligibility, or release-gate changes** in this review.

---

## 1. Executive verdict

### Classification: **Substantially complete**

Track A has accomplished its **primary purpose**: the core geo experimentation **measurement instrument** is characterized under governed recovery worlds, inference modes have **honest trust boundaries**, eligibility is **evidence-backed and frozen**, and governance decisions record what may and may not be claimed through Phase 15.

| Criterion | Status |
|-----------|--------|
| **Core geo estimators (SCM, TBRRidge, AugSynthCVXPY)** | OC-archived with governed roles |
| **Core inference modes (UnitJackKnife, BRB, KFold, Placebo)** | OC-archived or reconciled with trust boundaries |
| **Calibration governance framework** | Archived (INV-017); Run 001/002 baseline |
| **Estimand / aggregation semantics** | Characterized (INV-003) |
| **Formal governance decisions** | Phase 13 + Phase 15 + KFold reconciliation addendum |
| **Research backlog** | Registered (DEF-xxx; INV-030/031 as plans) |

### Rationale

**Why not “complete”:** Secondary estimators (SyntheticDID, BayesianTBR, MTGP, TROP), full DID OC (DEF-016), Track C platform investigations (INV-020–026), and synthesis investigations (INV-030 execution, INV-031 execution) remain **open or deferred**. Track A was never scoped to characterize every catalog estimator to production tier.

**Why not “incomplete”:** The **intended Track A gate** for Track B ([`ROADMAP_V4.md`](ROADMAP_V4.md) §3b) required core instrument OC for AugSynth and Placebo plus TBRRidge/SCM inference governance — **all delivered**. Remaining gaps are **explicitly deferred** with revisit triggers, not unknown blockers.

### Recommended conclusion

> **Track A is substantially complete. Track B may become the primary roadmap focus while Track A continues through governed investigations (INV-030, INV-031) and deferred registry items in parallel — not as blockers.**

---

## 2. Characterized estimator inventory

Classification key:

| Label | Meaning |
|-------|---------|
| **Characterized** | Production- or characterization-tier OC archive + governed role on recovery battery |
| **Partially characterized** | Some OC or policy closure; material gaps remain |
| **Uncharacterized** | No OC archive; smoke/unit tests or catalog only |

| Estimator | Status | Primary evidence | Governed role (summary) |
|-----------|--------|------------------|-------------------------|
| **SCM** (`SyntheticControl`) | **Characterized** | Phase 11 JK; Run 001; Phase 15 Placebo; extensive recovery scenarios | **Expert-review** — point + null-monitor JK eligible; Placebo null-reference (single-treated) |
| **TBRRidge** | **Characterized** | Run 001/002; Phase 12 program; KFold fix validation; shares TBR factory | **Expert-review** — point excellent; BRB null-viable; KFold runnable-not-trusted; not lift-calibrated |
| **AugSynth** (`AugSynthCVXPY` primary) | **Characterized** | [`PHASE14_AUGSYNTH_CHARACTERIZATION_001.md`](PHASE14_AUGSYNTH_CHARACTERIZATION_001.md) | **Expert-review point-only**; JK null-monitor only; spillover DGP bias documented |
| **AugSynth** (non-CVXPY) | **Partially characterized** | Phase 14 probe (10 reps) | **Research / probe** — not primary instrument |
| **DID** | **Partially characterized** | Recovery scenarios; pretrend contract; interval policy closed | **Expert-review** point path; **relative-ATT interval calibration unsupported** (DEF-003) |
| **SyntheticDID** | **Uncharacterized** | Staggered DGP metadata; runner unwired (DEF-005) | **Research-only** |
| **BayesianTBR** / **HorseShoe** | **Uncharacterized** | Catalog `research_only`; JAX optional (DEF-006) | **Research-only** — registry `Bayesian` ≠ MCMC path |
| **TROP** | **Partially characterized** | Recovery smoke only; skipped batch validation (DEF-007) | **Research-only** — NaN-tolerant smoke, no OC archive |
| **MTGP** | **Uncharacterized** | Skipped batch; no recovery OC (DEF-007) | **Research-only** |

**Track A scope note:** Characterization of **SCM + TBRRidge + AugSynthCVXPY** on default recovery DGP was the **core instrument maturation** objective. Secondary estimators were **explicitly out of scope** for Phase 11–15 exit.

---

## 3. Characterized inference inventory

| Mode | Evidence quality | Trust boundary | Governed role |
|------|------------------|----------------|---------------|
| **UnitJackKnife** | **High** — Phase 11 144-cell matrix; Run 001 n=100; Phase 14 AugSynth replication | Null FPR=0, coverage≈1; **power=0** on positive; width/effect ~8–23× (geometry-driven) | **Null monitor only** — sole **eligible** config (`SCM_UnitJackKnife`); not lift detector (Phase 13, DEF-013) |
| **BlockResidualBootstrap (BRB)** | **High** — Run 001 + Run 002 n=100 post bound-fix | Null sane post-fix; positive **coverage=0**, power=0 (narrow intervals) | **Expert-review** — null-viable; **excluded** from eligibility (DEF-002) |
| **KFold** | **High (post-fix)** — INV-007 pre/post archives n=30/n=100; reconciliation addendum | **Runnable** multi-treated after `391c64c`; positive OC fails; skip reason unchanged | **Restrict / defer** — runnable ≠ trusted; research-only on default DGP (Phase 13 + reconciliation) |
| **Placebo** | **High (single-treated SCM)** — Phase 15 n=100 + 22-cell matrix | `placebo_band` semantics; FPR=0; **power=0**; multi-treated **100% failure** | **Expert-review null-reference / diagnostic** — single-treated only (Phase 15); not CI; not eligible |

**Cross-mode pattern** ([`INV031_INFERENCE_CONSERVATISM_PLAN.md`](INV031_INFERENCE_CONSERVATISM_PLAN.md)): **Zero lift-detection power is universal** on the recovery battery among characterized modes where runs complete. **Null FPR=0 is common** where intervals align. This is **expected procedure behavior**, not a single defect — mechanisms differ (JK over-width, BRB under-width, placebo null-envelope).

---

## 4. Known trust boundaries

### Null-monitor patterns

| Pattern | Modes | Evidence |
|---------|-------|----------|
| **Conservative null pass** | UnitJackKnife, Placebo (single-treated), BRB (post-fix) | FPR=0, coverage=1 on null cells |
| **Eligible null monitoring** | **`SCM_UnitJackKnife` only** in registry | Run 001 + Phase 11 |
| **Expert-review null reference** | Placebo (`placebo_band`) | Phase 15 — distinct from CI |

### Lift-detection limitations

| Finding | Implication |
|---------|-------------|
| **Power ≈ 0** on `recovery_positive_effect` for all characterized inference | **No mode is a lift detector** on default battery at α=0.05 |
| **Accurate points** across SCM, TBRRidge, AugSynth | Point recovery ≠ interval lift detection |
| **Package claim** | **Null-monitor-only** nominal calibration boundary (DEF-015) |

### Spillover limitations

| Source | Finding |
|--------|---------|
| Phase 14 AugSynth | `scm_donor_contamination`: material point bias (~−0.034 vs 0.10) — **not modeled** |
| DEF-004 | No spillover term in core estimators — **research deferred** |
| Trust | **`interference_detected`** requires future estimator backing |

### Geometry limitations

| Boundary | Modes affected |
|----------|----------------|
| **Single-treated-only** | Placebo (implementation); optional conservative claims for KFold OC |
| **Multi-treated default DGP** | Placebo fails; KFold runnable but not trusted/eligible |
| **Donor pool / n_geos** | UnitJackKnife width scales with donor tier (Phase 11) |
| **Minimum controls** | Placebo requires ≥5 controls (policy); characterized on successful cells |

### Aggregation limitations

| Source | Finding |
|--------|---------|
| INV-003 | A ≈ B on homogeneous default DGP; **heterogeneous multi-treated drift** |
| Recovery scoring | **B-like prediction** vs **A-like truth** — coherent on default relative DGP |
| Absolute DGP | **Hard incompatibility** with relative recovery scoring (DEF-018) |

### Estimand constraints

| Constraint | Source |
|------------|--------|
| **Scored estimand** | `relative_att_post` (path mean) |
| **Interval alignment** | Required for calibration metrics; DID cumulative excluded |
| **Placebo** | Path `placebo_band`; recovery extraction aligned but **not CI semantics** |
| **Cross-estimator ATT** | Not interchangeable without declared estimand (DEF-014) |

---

## 5. Remaining active investigations

| ID | Status | Blocker? | Role |
|----|--------|----------|------|
| **INV-030** — Jackknife family characterization | Plan committed; execution pending | **Non-blocking research** | Explain JK conservatism; inventory alternative families — **no implementation required** for Track B start |
| **INV-031** — Inference conservatism synthesis | Plan committed; execution pending | **Non-blocking** for Track B **planning**; **recommended before CalibrationSignal implementation** | Cross-mode synthesis; feeds TrustReport vocabulary |

### Classification summary

| Category | Investigations |
|----------|----------------|
| **Blockers to Track B primary focus** | **None** — core OC and governance decisions exist |
| **Non-blocking research (parallel)** | INV-030, INV-031 |
| **Future architecture inputs** | INV-020–026 (Track C); DEF-009/011/012 (estimand registry, MMM) |

**INV-031 should complete before implementing `CalibrationSignal` semantics in code** — not before drafting `ExperimentSpec` / `ExperimentEvidence` schemas.

---

## 6. Deferred work review

| Priority | IDs | Theme |
|----------|-----|-------|
| **Critical (platform honesty — not Track B blockers)** | DEF-013, DEF-015, DEF-018 | Zero power boundary; package calibration scope; absolute/relative mismatch |
| **Critical (instrument gaps — parallel Track A)** | DEF-002, DEF-001 (post-fix), DEF-020 (wiring) | BRB positive OC; KFold post-fix OC/eligibility; Placebo multi-treated + RecoveryRunner wiring |
| **Medium (Track B inputs)** | DEF-008, DEF-009, DEF-011, DEF-014, DEF-019 | TrustReport scaling; aggregation registry; cross-estimator contracts; AugSynth wiring |
| **Medium (validation expansion)** | DEF-016, DEF-017, DEF-005, DEF-006, DEF-007 | DID OC; AugSynth/SDID/Bayesian/TROP/MTGP maturation |
| **Long-term research / Track C** | DEF-004, DEF-010, DEF-012, DEF-021, INV-020–026 | Spillover; feasibility engine; MMM bridge; jackknife alternatives; cross-modality platform |

**Registry hygiene (recommended editorial PRs, not blockers):** Update DEF-001 post-KFold fix; DEF-020 post-Phase 15; `ROADMAP_V4` Phase 15 status → Complete.

---

## 7. Track B readiness

Assessment against [`TRACK_B_ARCHITECTURE_PLAN.md`](TRACK_B_ARCHITECTURE_PLAN.md) and [`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md):

| Abstraction | Readiness | Prerequisites met | Remaining prerequisites |
|-------------|-----------|-------------------|-------------------------|
| **ExperimentSpec** | **Ready to implement (draft)** | INV-003 estimand semantics; geometry classes documented; Phase 13/15 governed roles | Formal estimand registry (DEF-011) — can start with geo subset |
| **ExperimentEvidence** | **Ready to implement (draft)** | OC archives cite estimand, interval type, geometry; inference_result semantics tests | Schema must encode `placebo_band` vs `confidence_interval`; `lift_detection_calibrated: false` default |
| **DiagnosticSummary** | **Ready to plan** | Review flags, pretrend contract, estimator diagnostics exist in code | Aggregation of characterized limits into summary contract |
| **CalibrationSignal** | **Plan-ready; implement after INV-031** | Run 001/002, Phase 11–15 null/positive matrices | INV-031 synthesis archive; split null-monitor vs power signals |
| **TrustReport** | **Plan-ready** | Phase 13/15 trust vocabulary; DEF-008 conceptual framework | INV-031 for cross-mode conservatism narrative; Track C taxonomy (INV-021) later |

**Overall:** Track B **contract design and prioritized implementation** may begin. **`CalibrationSignal` and `TrustReport` runtime logic** should consume INV-031 synthesis when available — not block schema work.

---

## 8. Recommended roadmap transition

| Question | Answer |
|----------|--------|
| **Can Track B become the primary focus?** | **Yes** — with this review as the formal checkpoint |
| **What Track A work continues in parallel?** | INV-031 synthesis (priority); INV-030 execution; DEF-016 DID OC (low intensity); registry editorial updates; optional AugSynth/Placebo RecoveryRunner wiring (DEF-019/020) |
| **What remains explicitly deferred?** | SyntheticDID/BayesianTBR/MTGP maturation; spillover modeling; Track C (INV-020–026); jackknife+ implementation; eligibility expansion; `production_safe` labels; MMM bridge (DEF-012) |
| **Next roadmap artifact** | **`ROADMAP_V5.md`** via re-audit ([`ROADMAP_V4.md`](ROADMAP_V4.md) §6) — after Track B schema MVP, not before |

### Suggested implementation priority (Track B)

1. **ExperimentSpec** — geometry class, estimand, inference mode, maturity boundary  
2. **ExperimentEvidence** — portable OC metadata, archive refs, interval types  
3. **DiagnosticSummary** — reviewer-facing aggregate from existing diagnostics  
4. **CalibrationSignal** — after INV-031 archive  
5. **TrustReport** — composes above with deferred-work citations  

---

## 9. Non-claims

This review **does not**:

- Assign **`production_safe`** to any estimator or config  
- Certify estimators as nominally calibrated for lift detection  
- Advance **maturity labels** in [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md)  
- Expand **release gates** or automated blocking  
- Add configs to **`NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`**  
- Imply **package-wide** inference trust  
- Close **Track C** or **research backlog** items  
- Declare INV-030/031 **complete**  

This review **does**:

- Record that **Track A core objectives are met**  
- Authorize **Track B as primary roadmap focus** (implementation planning + contract work)  
- Preserve **parallel governed research** without blocking platform evolution  

---

## 10. Final recommendation table

| Area | Status | Evidence quality | Remaining risk |
|------|--------|------------------|----------------|
| **Track A governance** | **Substantially complete** | Phase 12–15 decisions + INV-017 framework | Stale Phase 13 KFold wording until registry editorial PR |
| **SCM instrument** | **Characterized** | Phase 11, Run 001, Phase 15 Placebo | Placebo multi-treated unsupported |
| **TBRRidge instrument** | **Characterized** | Run 001/002, Phase 12, KFold fix | Positive OC failure all inference modes |
| **AugSynth instrument** | **Characterized (CVXPY point)** | Phase 14 production + matrix | Spillover DGP; RecoveryRunner unwired |
| **DID instrument** | **Partially characterized** | Policy + recovery smoke | DEF-016 OC gap; relative CI unsupported |
| **SyntheticDID / Bayesian / MTGP / TROP** | **Uncharacterized / partial** | Catalog + smoke only | Misuse if promoted without OC |
| **UnitJackKnife inference** | **Characterized** | Phase 11 + 14 + Run 001 | Zero power; donor-sensitivity semantics (INV-030) |
| **BRB inference** | **Characterized** | Run 002 n=100 | Positive under-coverage (DEF-002) |
| **KFold inference** | **Characterized (post-fix)** | Fix validation n=100 | Eligibility unchanged; positive OC fails |
| **Placebo inference** | **Characterized (single-treated)** | Phase 15 n=100 | Multi-treated NotImplemented; export discipline |
| **Estimand / aggregation** | **Characterized** | INV-003 | Heterogeneity + absolute DGP (DEF-009/018) |
| **Nominal calibration registry** | **Frozen** | Run 001 + Phase 13 | Over-claiming lift from null pass |
| **INV-030 / INV-031** | **Planned, not executed** | Plans committed | CalibrationSignal narrative incomplete until INV-031 runs |
| **Track B contracts** | **Ready for primary focus** | Vision + architecture plan + this review | Implement CalibrationSignal after INV-031 |
| **Track C platform** | **Deferred** | INV-020–026 registered | Out of scope for Track A closure |

---

## Appendix — Track A phase closure matrix

| Phase | Artifact | Status |
|-------|----------|--------|
| **11** | SCM UnitJackKnife OC | ✅ Complete |
| **12** | TBRRidge investigation + Run 002 | ✅ Complete |
| **13** | Governance decision | ✅ Complete |
| **14** | AugSynth OC | ✅ Complete |
| **15** | Placebo OC + governance | ✅ Complete |
| **KFold reconciliation** | Post-fix addendum | ✅ Complete |
| **Track A completion review** | This document | ✅ Complete |
| **ROADMAP_V5 re-audit** | Planned | ☐ After Track B schema MVP |

---

## Appendix — Evidence index (Track A core)

| Category | Documents reviewed |
|----------|-------------------|
| **Governance** | [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md), [`PHASE15_GOVERNANCE_DECISION_001.md`](PHASE15_GOVERNANCE_DECISION_001.md), [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md), [`KFOLD_GOVERNANCE_RECONCILIATION_001.md`](KFOLD_GOVERNANCE_RECONCILIATION_001.md) |
| **Estimator / inference OC** | [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md), [`PHASE14_AUGSYNTH_CHARACTERIZATION_001.md`](PHASE14_AUGSYNTH_CHARACTERIZATION_001.md), [`CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md), [`CALIBRATION_RUN_002.md`](CALIBRATION_RUN_002.md), [`PHASE12_INV007_KFOLD_GEOMETRY_001.md`](PHASE12_INV007_KFOLD_GEOMETRY_001.md), [`PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md`](PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md), [`PHASE12_INV003_AGGREGATION_SEMANTICS_001.md`](PHASE12_INV003_AGGREGATION_SEMANTICS_001.md), [`PHASE15_PLACEBO_CHARACTERIZATION_001.md`](PHASE15_PLACEBO_CHARACTERIZATION_001.md) |
| **Roadmap / vision** | [`ROADMAP_V4.md`](ROADMAP_V4.md), [`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md) |
| **Registries** | [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md), [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) |

---

*Review TRACK-A-REVIEW-001. Track A substantially complete; Track B may become primary focus.*
