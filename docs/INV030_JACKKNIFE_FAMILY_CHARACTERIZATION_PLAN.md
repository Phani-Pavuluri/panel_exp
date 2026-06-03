# INV-030 — Jackknife family characterization plan

**Investigation ID:** INV-030  
**Status:** governed investigation plan (pre-execution)  
**Last updated:** 2026-05-20  
**Package version:** 0.2.1  
**Phase:** Post–Phase 14 research characterization (Track A adjunct)

**Related:** [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md) · [`PHASE14_AUGSYNTH_CHARACTERIZATION_001.md`](PHASE14_AUGSYNTH_CHARACTERIZATION_001.md) · [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) · [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) · [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`panel_exp/inference/unit_jackknife.py`](../panel_exp/inference/unit_jackknife.py)

**This document does not:** implement jackknife variants, modify `UnitJackKnife`, change inference math, recovery scoring, eligibility, maturity, release gates, or promote any inference method.

---

## 1. Executive purpose

### Why this investigation exists

Phase 11 and Phase 14 archived **operating characteristics of the currently wired `UnitJackKnife` inference mode** on SCM and AugSynthCVXPY respectively. Both archives show the same pattern:

- null coverage ≈ 1, FPR ≈ 0  
- positive-scenario power ≈ 0 despite accurate point estimates  
- width/effect ratio ≈ 8–23× depending on panel geometry  

Phase 13 ratified **`SCM_UnitJackKnife` as a null monitor only** ([`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md) §3; **DEF-013**). Phase 14 extended the same inference-boundary finding to AugSynth ([`PHASE14_AUGSYNTH_CHARACTERIZATION_001.md`](PHASE14_AUGSYNTH_CHARACTERIZATION_001.md) §4).

Those archives answer: **“How does the implemented `UnitJackKnife` behave on recovery worlds?”**

They do **not** answer:

- whether conservatism is an **expected property of this jackknife construction** (leave-one-donor counterfactual sensitivity) vs a defect  
- whether conservatism is driven by **recovery-world geometry**, **multi-treated aggregation**, or **estimator-specific fit**  
- whether **other jackknife families** (time-resampling, cluster, delete-d, jackknife+) would materially differ in GeoX-relevant operating characteristics  
- what **uncertainty quantity** the current intervals approximate for Track B trust contracts  

### Implemented UnitJackKnife characterization vs jackknife family characterization

| Scope | Question | Evidence today | INV-030 goal |
|-------|----------|----------------|--------------|
| **Implemented UnitJackKnife characterization** | How does `inference="UnitJackKnife"` behave on declared recovery scenarios? | Phase 11 (SCM, 144-cell matrix); Phase 14 (AugSynth JK track); Run 001 | **Complete** for wired path — no re-run required unless sensitivity gaps identified |
| **Jackknife family characterization** | What uncertainty is being measured; which resampling unit drives width; would alternative jackknife **families** differ? | Partial read-only code inventory; `uncertainty.md` notes; uncharacterized `JKP` / `time_jackknife_plus` in repo | **Explain** observed conservatism and **inventory** alternatives for **future** experimentation workflows |

**Governing question:**

> **Is UnitJackKnife’s conservative null-monitor behavior expected given its implemented resampling semantics — and which jackknife families (if any) merit future OC before experimentation-platform trust contracts assume lift-detection intervals?**

**Scientific posture:** Investigation and governance planning only. Success is **explanatory**, not promotional. No variant implementation in this investigation.

**Eligibility (frozen):** `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS = {"SCM_UnitJackKnife"}` only. INV-030 does not target eligibility change.

---

## 2. Current evidence

### SCM findings (Phase 11)

Source: [`SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md)

| Dimension | Finding |
|-----------|---------|
| **Execution** | 0% failure across 144 cells; intervals aligned |
| **Null** | coverage = 1.0, FPR = 0.0 in every null cell |
| **Positive** | power = 0.0 in every positive cell (effects 0.05–0.20) |
| **Points** | recovery success = 1.0; point estimates track truth |
| **Treated count** | Width **not** primarily driven by n_treated (slightly narrower at higher n_treated) |
| **Donor / panel geometry** | **Strongest width driver** — width/effect ≈ 8× (small tier) to 23× (large tier) |
| **Noise** | Almost no effect on width or power in matrix |
| **Effect size** | Width scales ~linearly with effect; width/effect ratio ~constant (~15× medium tier) |
| **Classification** | Expected **conservatism + geometry limitation**, not BRB-class defect |

### AugSynth findings (Phase 14)

Source: [`PHASE14_AUGSYNTH_CHARACTERIZATION_001.md`](PHASE14_AUGSYNTH_CHARACTERIZATION_001.md) §4

| Dimension | Finding |
|-----------|---------|
| **Config** | `AugSynthCVXPY_UnitJackKnife` (same `unit_jk` registry path as SCM) |
| **Null** | coverage = 1.0, FPR = 0.0, interval aligned = 1.0 |
| **Positive** | coverage = 1.0, **power = 0.0**, significance rate = 0.0 |
| **Width** | mean width ≈ 1.54 on effect 0.10 → width/effect ≈ **15.4×** |
| **Geometry** | No KFold-style failure surface; multi-treated default DGP supported for **point** path |
| **Classification** | **Null-monitor-style only** — mirrors SCM jackknife pattern |

### Common pattern (cross-estimator)

| Metric | SCM UnitJackKnife | AugSynthCVXPY UnitJackKnife |
|--------|-------------------|-----------------------------|
| Null coverage | ≈ 1 | ≈ 1 |
| Null FPR | ≈ 0 | ≈ 0 |
| Positive power | ≈ 0 | ≈ 0 |
| Point recovery | excellent | excellent |
| Width/effect (medium geometry) | ≈ 15× | ≈ 15× |

**Key inference:** The shared **`unit_jk` implementation** ([`panel_exp/inference/unit_jackknife.py`](../panel_exp/inference/unit_jackknife.py), wired via `run_unit_jackknife`) produces **estimator-agnostic conservatism** on recovery worlds when points are accurate. This is evidence for **procedure-level** (not SCM-specific) behavior.

### Read-only implementation note (no code changes)

The wired path uses **variation 1** (SDID-style): for each **control unit** `i`, drop `i`, re-fit, compare leave-one-out **`y_hat`** to full-sample treated **`y`**, accumulate squared differences, return `norm.ppf(1-α/2) * sqrt(JK)`.

Intervals are therefore centered on **`y_hat` ± error** where error reflects **donor-delete counterfactual instability**, not a declared sampling model for post-period ATT noise alone.

---

## 3. Hypotheses

Each hypothesis is testable using **existing archives**, **read-only code review**, and **planned diagnostic re-analysis** — not new inference implementations.

| ID | Hypothesis | Test strategy | If supported |
|----|------------|---------------|--------------|
| **H1** | Current UnitJackKnife primarily measures **donor-sensitivity** of the counterfactual (leave-one-donor perturbation of `y_hat` vs fixed `y`), not classical sampling uncertainty of the ATT | Code-path audit; correlate Phase 11 width with donor-tier geometry; compare SCM vs AugSynth at matched geometry | Conservatism is **expected** for this variant; null monitor role is coherent |
| **H2** | Conservatism is **not** primarily driven by multi-treated aggregation | Phase 11: power = 0 even at n_treated = 1; AugSynth geometry sweep (n=1,2,4) shows stable JK pattern | Retire “multi-treated pooling causes zero power” as primary explanation |
| **H3** | Conservatism is **partially driven by recovery-world geometry** (donor count, n_geos, pre/post lengths) | Re-analyze Phase 11 donor-tier vs treated-count axes; optional single-geometry deep dives | Document geometry-specific usage boundaries; inform feasibility / TrustReport |
| **H4** | **Alternative jackknife families** would produce materially different OC (width, power, FPR tradeoffs) on the same DGPs | Literature + inventory (§4); map existing uncharacterized modes (`JKP`, `time_jackknife_plus`); **defer** empirical OC until governance approves variant scope | Justify **DEF-021** research backlog; do **not** imply current path is “wrong” |
| **H5** | Width scales with **effect size** because intervals are built from **level** counterfactual gaps that move with treated outcomes, not effect-normalized estimand noise | Phase 11 §4.4 width/effect constancy; recovery interval extraction on relative ATT | Clarify interval scale vs scored estimand (`relative_att_post`) for Track B |
| **H6** | AugSynth–SCM JK similarity implies conservatism is **inference-layer**, not weight-construction defect | Cross-estimator comparison at matched cells (Phase 14 already supports) | Strengthen DEF-013 as **UnitJackKnife-class** boundary, not SCM-only |

**Primary competing explanations to distinguish:**

1. Expected procedure property (H1)  
2. Recovery-world geometry artifact (H3)  
3. Aggregation / estimand extraction artifact (H5)  
4. Evidence that alternatives deserve future study (H4) — **not** evidence that current path should change without governance  

---

## 4. Jackknife family inventory

Conceptual catalog for GeoX panel inference. **No implementation** in INV-030.

| Family | Code status | Conceptual target | Uncertainty quantity measured | Expected advantages (GeoX) | Expected risks | GeoX relevance |
|--------|-------------|-------------------|------------------------------|----------------------------|----------------|----------------|
| **A. Leave-one-donor-out** | **Implemented** — `UnitJackKnife` / `unit_jk` v1 | Stability of synthetic control / ridge counterfactual to donor deletion | Donor-delete sensitivity of **`y_hat`** relative to treated **`y`** | Simple; aligns with “which donor drives the counterfactual?” review questions; conservative null guard | Very wide intervals; **zero lift power** on tested geometries; conflates fit stability with ATT sampling uncertainty | **High** — default wired path; null monitor only |
| **B. Leave-one-treated-out** | Not in recovery registry | Sensitivity to treated-unit composition | Treated-unit resampling / delete-one-treated influence | Useful when n_treated > 1 and reviewers ask about treated-cohort stability | Ill-defined or unstable when n_treated small; interacts with pooled vs unit estimands (DEF-009) | **Medium** — multi-geo incrementality reviews |
| **C. Delete-d jackknife** | Not implemented | Bias reduction for smooth estimators; robustness to outlier donors | Bias-adjusted ATT uncertainty with subset resampling | Can narrow intervals vs full LOO when d chosen well | Requires d selection policy; easy to over-tune; OC gate heavy | **Low–medium** — research / method comparison only |
| **D. Time-block jackknife** | Partial — `jkp()` time-drop logic in repo; **not** RecoveryRunner-calibrated | Temporal stability of counterfactual path | Time-segment perturbation of pre/post fit | Addresses **parallel trends / temporal leverage** questions | Block size choice; misalignment with relative ATT extraction; staggered adoption complexity | **Medium–high** — geo time-series leverage is common reviewer concern |
| **E. Cluster jackknife** | Not implemented | Correlation within clusters (markets, regions) | Cluster-level resampling uncertainty | Needed when donors are not exchangeable | Cluster definition governance; sparse clusters in geo panels | **Medium** — multi-market geo designs |
| **F. Jackknife+** | Partial — `jkp`, `time_jackknife_plus`; `uncertainty.md` says “do not implement; properties unclear” | Distribution-free interval with finite-sample coverage targets | Quantile of leave-one-out residuals (unit or time) | Potentially better calibrated finite-sample coverage than classical JK | Theoretical assumptions; may still be conservative on synthetic controls; **uncharacterized** in this package | **Medium** — future research if governance opens variant OC |

### Implemented vs catalogued-not-calibrated

| Mode | Registry name | RecoveryRunner OC | Notes |
|------|---------------|-------------------|-------|
| Leave-one-donor-out | `UnitJackKnife` | **Yes** (SCM eligible config; AugSynth investigation script) | Phase 11 + 14 archives |
| Jackknife+ (unit/time) | `JKP` (inference registry) | **No** | Exists in code; not promotion path ([`ROADMAP_V4.md`](ROADMAP_V4.md) §5) |
| Time jackknife+ | internal helpers | **No** | Research-only per `uncertainty.md` |

---

## 5. Investigation design

INV-030 execution is **documentation, re-analysis, and governance synthesis** — not new inference code.

### Track 0 — Evidence synthesis (required)

| Step | Activity | Inputs | Output |
|------|----------|--------|--------|
| 0.1 | Merge Phase 11 + Phase 14 JK metrics into comparison table | SCM + AugSynth archives | Cross-estimator conservatism memo section |
| 0.2 | Code-path semantics doc (read-only) | `unit_jk`, `run_unit_jackknife`, recovery interval extraction | Formal statement of measured quantity vs scored `relative_att_post` |
| 0.3 | Hypothesis scoring | H1–H6 vs existing matrices | Supported / refuted / inconclusive table |

### Track 1 — Donor sensitivity vs uncertainty (H1, H3)

Distinguish **donor sensitivity** from **statistical uncertainty**:

| Diagnostic | Method (no new inference) | Distinguishes |
|------------|----------------------------|---------------|
| Donor-tier width gradient | Re-tabulate Phase 11 by donor tier holding effect constant | Geometry / donor pool vs effect |
| Treated-count flatness | Phase 11 §4.1 + AugSynth n_treated sweep | Multi-treated aggregation vs procedure |
| Estimator swap at fixed inference | SCM vs AugSynth JK at medium tier | Estimator fit vs shared `unit_jk` |
| Leave-one-donor ATT spread (optional read-only probe) | Single-panel diagnostic script exporting per-donor-delete gaps **without** changing `unit_jk` | Direct donor-sensitivity visualization — investigation-only, not registry |

### Track 2 — Aggregation and estimand effects (H2, H5)

| Dimension | Variation | Source |
|-----------|-----------|--------|
| Pooled path extraction | How `relative_att_post` CI is derived from path-level `y_lower`/`y_upper` | [`recovery_intervals.py`](../panel_exp/validation/recovery_intervals.py), INV-003 |
| Multi-treated | n_treated 1, 2, 4, 8 (Phase 11) vs default (~4) | Existing archives |
| Heterogeneous effects | AugSynth homogeneous vs heterogeneous (point stable; JK not re-run at scale) | Phase 14 gap — note as **future OC cell**, not INV-030 implementation |
| Effect size ladder | 0.05, 0.10, 0.20 | Phase 11 §4.4 |

### Track 3 — Temporal and alternative-family framing (H4)

**No implementation.** Deliverables:

- Map families A–F to GeoX reviewer questions (donor leverage, time leverage, cluster structure)  
- Identify which families already have **code stubs** vs greenfield  
- Define **future OC battery template** (cells, metrics, tiers) for when governance approves variant characterization — mirror Phase 11 matrix structure  

**Potential future OC dimensions** (for DEF-021 backlog, not INV-030 execution):

| Dimension | Levels |
|-----------|--------|
| Treated count | 1, 2, 4, default |
| Donor tier | small / medium / large |
| Effect size | 0, 0.05, 0.10, 0.20 |
| Noise | low / medium / high |
| Heterogeneity | off / on |
| Spillover | none / contamination DGP |
| Estimator | SCM, AugSynthCVXPY (point-accurate bases) |

### Tiering (if optional diagnostic scripts added later)

| Tier | n_simulations | Purpose |
|------|---------------|---------|
| Characterization | 30, seeds 0–1–2 | Hypothesis discrimination |
| Production | 100, seeds 0–1–2 | Archive comparable to Run 001 / Phase 14 prod cells |

**Frozen constraints:** no recovery scoring changes; no threshold tuning; investigation-only scripts if any.

---

## 6. Success criteria

INV-030 **succeeds** when the program produces a governed archive (planned: `PHASE16_JACKKNIFE_FAMILY_CHARACTERIZATION_001.md` or equivalent) that:

| Criterion | Standard |
|-----------|----------|
| **Explains conservatism** | Primary driver classified among H1–H6 with evidence citations |
| **Distinguishes sensitivity vs uncertainty** | Plain-language statement of what `UnitJackKnife` intervals measure on recovery worlds |
| **Resolves aggregation questions** | Documents whether multi-treated pooling is a primary cause (expected: **no**, per Phase 11) |
| **Geometry boundaries** | Documents donor-tier / panel geometry effect on width and null-monitor suitability |
| **Family inventory complete** | §4 catalog with GeoX relevance and no implementation |
| **Governance alignment** | Confirms Phase 13 null-monitor boundary or recommends **documentation-only** refinement — **not** eligibility or maturity change |
| **No new methods** | Zero inference implementation PRs required for success |

**Does not require:** positive power on default recovery DGP; new eligible configs; jackknife variant shipping.

---

## 7. Deferred-work implications

| Entry | Action | Rationale |
|-------|--------|-----------|
| **DEF-013** | **Keep Accepted** — refine description to **UnitJackKnife-class** (not SCM-only) after INV-030 archive | AugSynth replication of zero-power pattern |
| **DEF-021** | **Add** — jackknife family alternatives research backlog | Justified: family inventory + H4 require institutional memory separate from “current path is null monitor” |
| **DEF-017 / DEF-019** | Cross-link only | AugSynth JK shares SCM inference semantics |
| **INV-027** (roadmap research backlog) | **Superseded in planning by INV-030** for jackknife-family scope | INV-030 is the governed program; INV-027 folded into INV-030 / DEF-021 |

### Proposed DEF-021 (placeholder — registry PR separate)

**Title:** Jackknife family alternatives — research characterization backlog  
**Status:** Investigating → Deferred after INV-030 plan adoption  
**Why deferred:** Only leave-one-donor `UnitJackKnife` is OC-archived; alternatives exist conceptually or as uncalibrated code stubs; implementing variants before OC gates violates roadmap scope lock  
**Future work:** Governance-approved OC of selected families (D, F first candidates for geo time/leverage questions); no eligibility impact without full promotion chain  
**Related investigations:** INV-030  

---

## 8. Relationship to Track B

Understanding jackknife **uncertainty semantics** is a prerequisite for honest Track B contracts ([`TRACK_B_ARCHITECTURE_PLAN.md`](TRACK_B_ARCHITECTURE_PLAN.md)).

| Track B artifact | INV-030 implication |
|------------------|---------------------|
| **`ExperimentEvidence`** | Must record `inference_mode=UnitJackKnife`, interval type (`confidence_interval`), **`uncertainty_semantics=donor_delete_counterfactual_sensitivity`** (proposed label), and geometry class — not generic “CI calibrated” |
| **`CalibrationSignal`** | JK signal is **null-monitor calibrated** on tested null worlds; **not** `lift_detection_calibrated`; positive coverage = 1 reflects interval width, not power |
| **`TrustReport`** | `supported_null_monitor` vs `inconclusive_lift` separation; forbid interpreting zero FPR as lift-detection readiness; cross-link DEF-013 / DEF-021 |
| **Experimentation contracts** | Default geo workflow: point estimate + null monitor JK; lift claims require **different inference mode** or explicit human waiver — future families only after OC archive |

**Track B sequencing:** INV-030 is **planning and explanation** — it **enables** Track B trust vocabulary; it does **not** authorize Track B implementation priority over Phase 15 Placebo OC ([`PHASE15_PLACEBO_INVESTIGATION_PLAN.md`](PHASE15_PLACEBO_INVESTIGATION_PLAN.md)).

---

## 9. Non-goals

INV-030 explicitly **does not**:

| Non-goal | Reason |
|----------|--------|
| Implement new jackknife variants | Roadmap scope lock ([`ROADMAP_V4.md`](ROADMAP_V4.md) §5) |
| Modify `UnitJackKnife` / `unit_jk` | Characterization-only mandate |
| Change inference math or registry wiring | Preserves Phase 11–14 evidentiary baseline |
| Change recovery scoring or thresholds | Avoid retroactive calibration pass |
| Change eligibility, maturity, release gates | Governance frozen unless promotion chain completes |
| Promote SCM, AugSynth, or JK to lift detector | Phase 13 + Phase 14 boundaries stand |
| Claim jackknife+ is safe to ship | Properties uncharacterized |
| Replace DEF-013 with “fixed” | Zero power is **accepted usage boundary**, not defect |

---

## Appendix A — Planned deliverables

| Deliverable | Owner phase | Depends on |
|-------------|-------------|------------|
| This plan | INV-030 | — |
| Evidence synthesis + hypothesis scoring memo | INV-030 execution | Phase 11 + 14 archives |
| `PHASE16_JACKKNIFE_FAMILY_CHARACTERIZATION_001.md` (working title) | Post-plan execution | INV-030 Tracks 0–2 |
| Optional investigation-only diagnostic JSON | Local only | Track 1 probes |
| DEF-021 registry entry | Governance PR | This plan |
| Track B uncertainty semantics note | Track B planning | INV-030 archive |

---

## Appendix B — Investigation disposition (preview)

| Outcome | Likely disposition | Registry |
|---------|-------------------|----------|
| H1 supported — donor-sensitivity semantics | **Accepted** usage clarification | DEF-013 update (wording) |
| H3 supported — geometry drives width | **Accepted** geometry boundary | DEF-013 + validation docs |
| H4 — alternatives may differ materially | **Deferred** research | DEF-021 |
| Request to ship jackknife+ without OC | **Rejected** | Roadmap §5 scope lock |

---

*Investigation plan INV-030. No code, eligibility, maturity, or release-gate changes.*
