# Phase 14 investigation plan — AugSynth characterization

**Status:** governed investigation plan (pre-execution)  
**Last updated:** 2026-05-28  
**Package version:** 0.2.1  
**Phase:** 14 — AugSynth operating-characteristic characterization  
**Prerequisite:** Phase 13 governance decision complete ([`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md))

**Related:** [`ROADMAP_V4.md`](ROADMAP_V4.md) § Phase 14 · [`PHASE12_INVESTIGATION_PLAN.md`](PHASE12_INVESTIGATION_PLAN.md) (template) · [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) · [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) · [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) DEF-017 · DEF-019

**This document does not:** modify code, change eligibility, run characterization jobs, tune thresholds, promote estimators, or implement Track B contracts.

---

## 1. Executive purpose

AugSynth (`AugSynthCVXPY`, and non-CVXPY `AugSynth` where applicable) is among the strongest **long-term expert-review instrumentation** candidates for geo incrementality — especially multi-treated and augmentation-heavy panels where classical SCM weighting is fragile.

**Why strategically important:**

| Factor | Rationale |
|--------|-----------|
| **GeoX relevance** | Augmentation addresses donor-fit limitations common in market tests |
| **Expert-review tier** | `AugSynthCVXPY` is `expert_review` in maturity catalog but **lacks recovery/OC archives** |
| **Track B foundation** | Core instrument set must be characterized before platform contracts claim trustworthy measurement |
| **Governance gap** | VALIDATION_COVERAGE lists “no automated synthetic recovery” — maturity may overstate evidence ([`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) DEF-017) |

**Governing question:**

> **Under declared geo recovery scenarios, what operating characteristics does AugSynth exhibit for point recovery, null behavior, and inference-enabled paths — and what usage boundary is evidence-supported?**

**Scientific posture:** Characterization only. A successful Phase 14 may conclude **research-only**, **point-recovery-only**, **null-monitor-only**, or **deferred** — if evidence supports it.

**Current state (frozen for planning):**

| Estimator | Maturity | Recovery runner | Nominal calibration |
|-----------|----------|-----------------|---------------------|
| **AugSynthCVXPY** | `expert_review` | **No** | **Not eligible** |
| **AugSynth** | `unvalidated` | **No** | **Not eligible** |

**Eligibility (frozen):** `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = {"SCM_UnitJackKnife"}` only.

---

## 2. Questions

### Point recovery and estimand alignment

- What is **recovery success rate** and **point bias** vs canonical truth on `relative_att_post`?
- Does AugSynth point recovery **degrade under multi-treated** default recovery DGP (~4 treated)?
- How does AugSynth compare to **SCM point recovery** on the same scenarios (diagnostic, not ranking)?

### Null behavior

- Under `recovery_null_effect`, what are **FPR**, **coverage**, and **significance rate** when inference is enabled?
- Are null intervals **over-conservative** (SCM jackknife pattern) or **anti-calibrated** (Run 001 BRB pattern)?
- Does null behavior **vary by donor count / treated count**?

### Positive-effect behavior

- Under `recovery_positive_effect` (`true_effect = 0.10`), what are **power**, **coverage**, and **interval width / effect ratio**?
- Is positive-scenario behavior **usable for lift review** or **mechanically zero power**?

### Inference / interval semantics

- Which inference modes are **viable** on AugSynth exports (Kfold, Conformal, point-only)?
- Is `interval_estimand` **alignable** to `relative_att_post` on recovery paths, or policy-blocked like DID cumulative?
- Are intervals **ordered** (`ci_lower ≤ ci_upper`) on post periods?

### Geometry sensitivity

- **Treated count:** 1 vs 2 vs 4 vs default ~4 sampled  
- **Donor tier:** small / medium / large panels (Phase 11 template)  
- **Pre/post length:** default recovery vs shortened panels  

### Heterogeneity sensitivity

- Homogeneous vs **heterogeneous relative effects** (INV-003 template)  
- Does pooled-path scoring vs canonical truth drift beyond documented INV-003 bounds?

### Spillover / interference stress

- Behavior on **`scm_donor_contamination`** or spillover-stress DGP (estimator does not model spillover — characterize **failure to adjust**, not fix)  
- Links to DEF-004 (spillover estimation deferred)

### Stability under donor perturbation

- Weight health metrics (`check_AugSynthCVXPY_weight_health`) vs recovery outcomes  
- **Collinearity stress** (`scm_high_collinearity`) — INV-037 cross-link  
- Solver failures, infeasibility, or silent fallback patterns (CVXPY/OSQP)

### Execution reliability

- **Failure rate** and **failure types** (`ValueError`, solver errors, non-finite outputs)  
- Seed stability on headline metrics  

---

## 3. Experimental design

### Investigation tracks

| Track | ID | Primary configs | Focus |
|-------|-----|-----------------|-------|
| **A — Point recovery** | INV-028A | `AugSynthCVXPY` (`inference=None`) | Bias, recovery success, geometry matrix |
| **B — Inference OC** | INV-028B | `AugSynthCVXPY` + declared inference mode(s) | Null FPR/coverage; positive power; interval alignment |
| **C — Non-CVXPY AugSynth** | INV-028C | `AugSynth` if execution viable | Wiring gap vs CVXPY path |
| **D — Stress scenarios** | INV-028D | AugSynthCVXPY on collinearity / contamination DGPs | Robustness characterization |

### Scenarios (minimum battery)

| Scenario | Purpose | Priority |
|----------|---------|----------|
| `recovery_null_effect` | Null OC baseline | **Required** |
| `recovery_positive_effect` | Positive OC baseline | **Required** |
| `scm_high_collinearity` | Donor instability | Recommended |
| `scm_donor_contamination` | Interference stress (DGP only) | Optional |
| Heterogeneous-effect variant (INV-003 protocol) | Aggregation drift | Recommended |
| Single-treated explicit panel | Geometry contrast | Recommended |

### Geometry matrix (characterization tier)

| Dimension | Levels |
|-----------|--------|
| `n_treated` | 1, 2, 4, default sampled (~4) |
| Donor tier | small (+5 donors), medium (20 geos), large (40 geos) — Phase 11 definition |
| Effect | 0.00 (null), 0.10 (positive); optional 0.05, 0.20 in extended matrix |

### Seeds and simulation counts

| Tier | n_simulations | Seeds | Use |
|------|---------------|-------|-----|
| **Characterization** | 30 | 0, 1, 2 | Geometry matrix, failure surface (INV-007 template) |
| **Production-scale** | **100** | **0, 1, 2** | Headline null/positive OC on **declared primary config** only — if execution viable |

**Do not tune** `true_effect`, noise, or thresholds to pass targets.

### Metrics (per replication)

| Metric | Notes |
|--------|-------|
| Recovery success rate | \|predicted − truth\| within tolerance |
| Point bias / MAE | vs canonical truth |
| Coverage, FPR, power | Only when interval path aligned to declared estimand |
| Mean interval width, width/effect | When intervals exist |
| Significance rate | CI-based or mode-specific |
| Failure rate, failure types | Typed metadata |
| `interval_estimand`, `interval_aligned` | Per recovery_intervals contract |
| Weight health / solver status | AugSynth-specific diagnostics |

### Shared constants (from Run 001 / INV-017)

| Parameter | Value |
|-----------|-------|
| Nominal α | 0.05 |
| Null thresholds (when applicable) | coverage ≥ 0.90, FPR ≤ 0.10, failure_rate < 0.05 |
| Power target (informative) | 0.80 on positive |
| Scored estimand | `relative_att_post` |
| DGP missingness | `missingness_policy=none` on calibration scenarios |

### Archive rules

Per [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md):

1. **Pre-execution:** this plan committed.  
2. **Post-execution:** `PHASE14_AUGSYNTH_CHARACTERIZATION_001.md` (evidence archive) + optional local JSON (not committed unless policy changes).  
3. **Failure analysis:** required if production-tier null FPR/coverage fail or anti-calibration detected.  
4. **Governance decision:** Phase 14 decision memo or Phase 13-style addendum — **no eligibility change** without full promotion chain.  
5. **Disposition:** every material finding → [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) (DEF-019 update).

### Execution note (future — not in this plan PR)

If `RecoveryRunner` lacks AugSynth configs, investigation may use **investigation-only loops** (Run 002 pattern) without registry or eligibility changes.

---

## 4. Acceptable outcomes

All evidence-supported outcomes are **valid**. Phase 14 does not presuppose promotion.

| Outcome | Meaning | Example disposition |
|---------|---------|-------------------|
| **Expert-review candidate (point only)** | Stable point recovery; inference deferred | Path B in METHOD_VALIDATION_PLAN |
| **Expert-review candidate (inference)** | Aligned intervals with acceptable null OC | Requires production-tier archive + failure analysis |
| **Null monitor only** | Null pass; zero or unusable positive power | Analogous to SCM jackknife role |
| **Research-only** | Unreliable failure surface or unaligned intervals | Permanent skip reason optional |
| **Deferred** | Insufficient execution viability (solver/wiring) | DEF-019 remains; wiring sub-track |
| **Restrict geometry** | e.g. single-treated-only or minimum donor count | Documented usage boundary |

**Invalid outcomes:** promotion without archives; eligibility change without Phase 13+ policy chain; `production_safe` claims.

---

## 5. Non-goals

Phase 14 planning and execution **does not**:

- Promote AugSynth or AugSynthCVXPY maturity labels  
- Add configs to `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`  
- Modify AugSynth estimator math, CVXPY formulations, or solver settings for calibration pass  
- Modify inference implementations or recovery scoring  
- Change release gates or automated blocking  
- Implement Track B contracts (`ExperimentSpec`, `ExperimentEvidence`, etc.)  
- Replace spillover modeling (DEF-004)  
- Certify package-wide nominal calibration  

Phase 14 **does**:

- Define governed OC questions before Track B becomes primary implementation focus  
- Produce archived evidence for a core long-term geo instrument candidate  
- Inform VALIDATION_COVERAGE and METHOD_VALIDATION_PLAN path decisions  
- Close or narrow DEF-019 when characterized  

---

## Appendix — evidence gaps today

| Gap | Source |
|-----|--------|
| No `RecoveryRunner` config for AugSynthCVXPY | `VALIDATION_COVERAGE.md` |
| Unit tests only; stability smoke | `tests/test_scm.py`, `tests/test_counterfactual_stability.py` |
| METHOD_VALIDATION_PLAN path **E → B** pending wiring | Part A SCM family |
| Expert-review label without OC archive | Phase 13 Track A partial closure |

---

*Investigation plan INV-028 / Phase 14. No code or registry changes in this document.*
