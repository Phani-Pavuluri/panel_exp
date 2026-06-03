# INV-031 — Inference conservatism investigation plan

**Investigation ID:** INV-031  
**Status:** governed investigation plan (pre-execution)  
**Last updated:** 2026-05-20  
**Package version:** 0.2.1  

**Related:** [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md) · [`CALIBRATION_RUN_002.md`](CALIBRATION_RUN_002.md) · [`PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md`](PHASE12_INV007_KFOLD_FIX_VALIDATION_001.md) · [`PHASE14_AUGSYNTH_CHARACTERIZATION_001.md`](PHASE14_AUGSYNTH_CHARACTERIZATION_001.md) · [`PHASE15_PLACEBO_CHARACTERIZATION_001.md`](PHASE15_PLACEBO_CHARACTERIZATION_001.md) · [`INV030_JACKKNIFE_FAMILY_CHARACTERIZATION_PLAN.md`](INV030_JACKKNIFE_FAMILY_CHARACTERIZATION_PLAN.md) · [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md)

**This document does not:** run new experiments, modify inference implementations, change recovery scoring, eligibility, maturity, or release gates, or promote any inference method.

---

## 1. Executive purpose

Multiple inference modes on geo recovery worlds exhibit a **shared conservative operating pattern**:

| Mode | Null coverage | Null FPR | Positive power | Point recovery |
|------|---------------|----------|----------------|----------------|
| **SCM UnitJackKnife** (Phase 11) | ≈ 1 | ≈ 0 | ≈ 0 | excellent |
| **AugSynth UnitJackKnife** (Phase 14) | ≈ 1 | ≈ 0 | ≈ 0 | excellent |
| **TBRRidge BRB** (Run 002) | 1 | 0 | 0 | excellent |
| **TBRRidge KFold** (post-fix, n=100) | 1 (null cells) | 0 | 0 (positive) | varies |
| **SCM Placebo** (Phase 15, single-treated) | 1 | 0 | 0 | excellent |

**Governing question:**

> **Is this cross-mode pattern evidence of a shared statistical mechanism, recovery-world geometry, aggregation/scoring artifact, or expected behavior of the uncertainty quantities these methods actually estimate?**

INV-031 is a **synthesis and hypothesis-testing plan** — not a request to tune thresholds or ship new inference variants.

**Relationship to INV-030:** INV-030 focuses on **jackknife family** semantics and alternatives. INV-031 spans **all characterized inference modes** and asks why **lift detection uniformly fails** while **null monitoring often passes**.

**Eligibility (frozen):** `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = {"SCM_UnitJackKnife"}` only.

---

## 2. Evidence inventory

### Phase 11 — SCM UnitJackKnife

- 144-cell matrix: null coverage = 1, FPR = 0 everywhere; power = 0 on all positive cells  
- Width/effect ≈ 8–23×; donor tier dominates width  
- Classified: **expected conservatism + geometry**, not defect  

### Run 002 — TBRRidge BlockResidualBootstrap

- Post bound-fix: null coverage = 1, FPR = 0  
- Positive: coverage = 0, power = 0 — intervals **too narrow** to contain truth (distinct mechanism from jackknife **over**-coverage)  
- Points accurate; aligned `relative_att_post`  

### KFold post-fix validation (`391c64c`)

- 0% failure multi-treated; null FPR = 0; positive coverage = 0, power = 0  
- Parallel to BRB **positive under-coverage**, not jackknife over-conservatism  

### Phase 14 — AugSynth UnitJackKnife

- Replicates SCM jackknife: coverage = 1, FPR = 0, power = 0  
- Shared `unit_jk` path → **procedure-level** pattern  

### Phase 15 — SCM Placebo (single-treated)

- coverage = 1 on **both** null and positive; power = 0  
- Intervals include zero **and** true effect on positive — **null-reference semantics**, not narrow CI failure  

**Cross-cutting observation:** **Zero positive power is universal** on default recovery battery among characterized modes; **null FPR = 0 is common** where runs complete and intervals align.

---

## 3. Hypotheses

| ID | Hypothesis | Primary evidence | INV-031 test (no new code) |
|----|------------|------------------|----------------------------|
| **H1** | **UnitJackKnife measures donor-sensitivity** (leave-one-donor counterfactual perturbation) **rather than ATT sampling uncertainty** | `unit_jk` compares `y_hat_{-i}` to fixed `y`; Phase 14 cross-estimator replication | Read-only code audit + Phase 11/14 width vs donor tier tables |
| **H2** | **Recovery-world geometry drives conservatism** (donor count, n_geos, pre/post length) | Phase 11 donor-tier width gradient; placebo donor-tier widths | Re-tabulate archived matrices; document geometry classes |
| **H3** | **Multi-treated aggregation contributes** to interval width / power | Phase 11: power = 0 even at n_treated = 1 | **Refute as primary cause** for jackknife; assess placebo/KFold multi-treated **failure** separately |
| **H4** | **Configured effect sizes are small relative to the uncertainty quantity being estimated** (width/effect ratios ≫ 1 for JK; placebo ~2–3× on single-treated) | Phase 11 constant width/effect ~15×; Phase 15 placebo ~2.3× medium tier | Compare scored estimand (`relative_att_post` ~0.10) to constructed interval widths per mode |
| **H5** | **Conservatism is expected and not a software defect** (distinct from Run 001 BRB inversion) | Stable seeds; aligned metadata; Phase 13 accepted DEF-013 | Synthesis memo: defect vs expected procedure classification per mode |

### Secondary hypotheses (mode-specific)

| ID | Hypothesis | Modes |
|----|------------|-------|
| **H6** | BRB/KFold positive **under-coverage** is a **narrow-interval** failure, not the same as jackknife **over-conservatism** | BRB, KFold |
| **H7** | Placebo zero power reflects **null-envelope semantics** (intervals include zero by construction on positive DGP) | Placebo |
| **H8** | Recovery interval extraction maps path-level bounds to `relative_att_post` in ways that **homogenize** mode-specific semantics in OC metrics | All aligned modes |

---

## 4. Investigation design (planning-only tracks)

**No new simulations in INV-031 planning phase.** Execution draws on existing archives + read-only analysis.

### Track A — Cross-mode OC synthesis

| Deliverable | Inputs |
|-------------|--------|
| Unified comparison table | Phase 11, Run 002, KFold fix validation, Phase 14 JK, Phase 15 Placebo |
| Mode taxonomy | **Null-monitor-viable** vs **lift-detection-failed** vs **execution-blocked** |
| Defect registry cross-check | BRB inversion = **fixed**; KFold broadcast = **fixed**; placebo multi-treated = **unsupported by design** |

### Track B — Uncertainty-quantity mapping

| Mode | Constructed quantity (read-only) | OC expectation |
|------|----------------------------------|----------------|
| UnitJackKnife | Donor-delete counterfactual stability | Wide intervals; zero power |
| BRB | Block residual bootstrap of path | Null pass post-fix; positive narrow |
| KFold | Cross-fold ATT variance | Similar positive failure post-fix |
| Placebo | Randomization null envelope + inversion | Coverage 1 on positive; power 0 |

### Track C — Geometry and aggregation attribution

| Analysis | Source | Resolves |
|----------|--------|----------|
| Donor tier vs treated count | Phase 11 | H2 vs H3 |
| Single-treated-only cells | Phase 11 n=1; Phase 15 prod | H3 refutation |
| Width/effect vs effect ladder | Phase 11 §4.4 | H4 |
| Pooled path CI extraction | `recovery_intervals.py` read-only | H8 |

### Track D — Governance synthesis

| Output | Audience |
|--------|----------|
| Plain-language **“what zero power means”** per mode | Expert reviewers |
| Track B **`CalibrationSignal` semantics** draft | [`TRACK_B_ARCHITECTURE_PLAN.md`](TRACK_B_ARCHITECTURE_PLAN.md) |
| Disposition recommendations | DEF-013, DEF-002, DEF-020, DEF-021 — **documentation only** |

---

## 5. Success criteria

INV-031 **succeeds** when a governed archive (planned: `INV031_INFERENCE_CONSERVATISM_SYNTHESIS_001.md`) provides:

| Criterion | Standard |
|-----------|----------|
| **Explains zero power** | Mode-specific mechanisms documented; shared vs distinct causes separated |
| **H1–H5 scored** | Each hypothesis marked supported / refuted / partial with citations |
| **Geometry boundaries** | Documented which OC claims require single-treated vs default DGP |
| **Defect vs expected** | BRB/KFold fixes distinguished from procedural conservatism |
| **Track B input** | Draft trust labels: `null_monitor_viable`, `lift_detection_not_calibrated`, `incompatible_geometry` |
| **No implementation** | Zero inference code changes required for success |

**Does not require:** achieving positive power on default recovery DGP; eligibility changes.

---

## 6. Deferred-work implications

| Entry | INV-031 interaction |
|-------|---------------------|
| **DEF-013** | Refine wording: zero power is **cross-mode on recovery battery**, not SCM-only surprise |
| **DEF-002** | BRB positive under-coverage remains **distinct mechanism** from jackknife over-width |
| **DEF-020** | Placebo role informed by Phase 15 archive; governance decision follows separately |
| **DEF-021** | Jackknife alternatives remain research — INV-031 does not justify implementation |
| **DEF-015** | Package-wide calibration gap **expected** given universal lift-detection failure |

**Proposed disposition (preview):** INV-031 closes as **Accepted** cross-mode conservatism explanation — not **Fixed** (no code change intended).

---

## 7. Relationship to Track B

| Artifact | INV-031 implication |
|----------|-------------------|
| **`ExperimentEvidence`** | Must store per-mode **`uncertainty_semantics`** and **`lift_detection_calibrated: false`** for characterized modes |
| **`CalibrationSignal`** | Split **null_monitor_signal** from **power_signal** — do not aggregate into single “calibrated” boolean |
| **`TrustReport`** | Default stance: **accurate points + conservative or mis-scaled intervals** until mode-specific evidence says otherwise |
| **`ExperimentSpec`** | Declare **geometry class** (single- vs multi-treated) and **inference mode** before trust composition |

**Sequencing:** INV-031 synthesis should complete **before** Track B implementation claims inference trust — can proceed **in parallel** with INV-030 jackknife family work.

---

## 8. Non-goals

INV-031 explicitly **does not**:

| Non-goal | Reason |
|----------|--------|
| Run new OC batteries | Planning phase only |
| Implement jackknife+ / placebo fixes | Out of scope |
| Tune thresholds to achieve power | Forbidden by governance |
| Change eligibility or maturity | Phase 13 boundary preserved |
| Promote any mode to lift detector | Evidence contradicts |
| Replace INV-030 | Complementary — INV-030 is jackknife-family deep dive |

---

## Appendix — Hypothesis decision preview (from existing evidence)

| Hypothesis | Preliminary assessment (planning) | Confidence |
|------------|-----------------------------------|------------|
| **H1** | **Supported** for UnitJackKnife | High |
| **H2** | **Supported** for jackknife width; partial for placebo | High (JK), medium (Placebo) |
| **H3** | **Refuted** as primary jackknife cause | High |
| **H4** | **Partial** — effect-size scaling visible; not sole cause | Medium |
| **H5** | **Supported** for JK/Placebo; **partial** for BRB/KFold (mixed null/positive) | High |

*Preliminary assessments are planning inputs only — formal scoring belongs in the execution archive.*

---

*Investigation plan INV-031. No experiments executed in this document.*
