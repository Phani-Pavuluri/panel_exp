# Phase 15 investigation plan — Placebo inference characterization

**Status:** governed investigation plan (pre-execution)  
**Last updated:** 2026-05-28  
**Package version:** 0.2.1  
**Phase:** 15 — Placebo inference operating-characteristic characterization  
**Prerequisite:** Phase 14 plan adopted; Phase 13 governance complete

**Related:** [`ROADMAP_V4.md`](ROADMAP_V4.md) § Phase 15 · [`PHASE12_INVESTIGATION_PLAN.md`](PHASE12_INVESTIGATION_PLAN.md) · [`PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md`](PHASE12_INV017_CALIBRATION_GOVERNANCE_001.md) · [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · [`tests/test_inference_result_semantics.py`](../tests/test_inference_result_semantics.py) · [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) DEF-020

**This document does not:** modify code, change eligibility, run characterization jobs, promote estimators, or implement Track B contracts.

---

## 1. Executive purpose

**Placebo inference** is a core SCM/TBR-family uncertainty mode cataloged for expert review. It provides **randomization-style null envelopes** distinct from jackknife/bootstrap confidence intervals — strategically important for geo experiments where reviewers need honest **null reference distributions**, not mislabeled CIs.

**Why strategically important:**

| Factor | Rationale |
|--------|-----------|
| **Catalog presence** | SCM/TBR list **Placebo** in inference registry (`method_metadata.py`) |
| **Semantic distinction** | Exports use `interval_type = placebo_band`, not standard confidence intervals ([`IntervalType.PLACEBO_BAND`](panel_exp/inference_result.py)) |
| **Expert-review risk** | Placebo bands can be **misread as CIs** ([`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) § Placebo vs CI interpretation) |
| **Track B trust** | TrustReport must distinguish placebo null envelopes from calibrated `relative_att_post` intervals |
| **Characterization gap** | No n≥100 OC archive; not in `RecoveryRunner` inference configs today (only `SCM_UnitJackKnife` wired) |

**Governing question:**

> **Under geo recovery scenarios, does Placebo inference behave as a trustworthy null monitor or expert-review adjunct — and under what geometry constraints — without misrepresenting interval semantics?**

**Scientific posture:** Characterization only. Outcomes may include **trustworthy null monitor**, **expert-review-only with strict export policy**, or **research-only** — if evidence supports it.

**Critical semantic hypothesis (to test, not assume):**

Placebo **`placebo_band`** intervals may **not** align to recovery **`relative_att_post`** interval calibration gates the same way jackknife CIs do. Phase 15 must characterize **both** path-level placebo behavior **and** whether nominal calibration metrics are **meaningful or misleading** for this mode.

**Eligibility (frozen):** No Placebo config in `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS`. This phase does not target eligibility addition without estimand proof.

---

## 2. Questions

### Null calibration

- On `recovery_null_effect`, does Placebo produce **calibrated null envelopes** (expected FPR / coverage under declared semantics)?
- Is null behavior **over-conservative**, **anti-calibrated**, or **unstable across seeds**?

### FPR and coverage

- What are **FPR** and **coverage** when significance is derived from placebo bands vs point relative ATT?
- If recovery interval extraction is **not aligned**, document **policy exclusion** explicitly (DID template).

### Power (positive scenario)

- Under `recovery_positive_effect`, what are **power** and **coverage** when placebo bands are used as uncertainty summaries?
- Is Placebo **ever appropriate for lift detection**, or **null/reference only**?

### Treatment geometry sensitivity

- **Single-treated vs multi-treated** default recovery DGP  
- Failure modes when treated count exceeds control requirements (`Placebo requires >=5 control units` — see inference impl)  

### Donor count sensitivity

- Small donor panels vs medium (20 geos) vs large (40 geos)  
- Relationship between **minimum control count** and usable placebo draws  

### Heterogeneous effects

- Homogeneous vs heterogeneous relative DGP (INV-003 protocol)  
- Does pooled-path placebo aggregation drift from canonical truth?

### Multi-treated behavior

- Default ~4 treated vs explicit 1 / 2 / 4 treated panels  
- Compare to **SCM jackknife** and **TBRRidge BRB** geometry lessons (Phase 11–12)

### Cross-estimator portability

- **SCM + Placebo** (primary)  
- **TBR/TBRRidge + Placebo** where viable (secondary)  
- Document **family-specific** limitations — no silent consensus  

### Export / interpretation discipline

- Are reviewers protected from **placebo_band vs confidence_interval** confusion?  
- Does `placebo_strict` mode change failure surfaces materially?

---

## 3. Experimental design

### Investigation tracks

| Track | ID | Primary config | Focus |
|-------|-----|----------------|-------|
| **A — SCM Placebo OC** | INV-029A | `SCM` + `inference="Placebo"` | Null/positive metrics on scm_* scenarios |
| **B — Interval semantics** | INV-029B | Same | `interval_type`, alignment to `relative_att_post`, recovery_intervals policy |
| **C — Geometry matrix** | INV-029C | SCM Placebo | Treated count × donor tier |
| **D — TBR Placebo** | INV-029D | `TBR`/`TBRRidge` + Placebo where supported | Cross-family comparison (diagnostic) |

### Scenarios

| Scenario | Purpose | Priority |
|----------|---------|----------|
| `recovery_null_effect` | Null OC | **Required** |
| `recovery_positive_effect` | Positive / power | **Required** |
| `scm_*` family scenarios (batch validation) | Broader geometry | Recommended |
| Single-treated explicit panel | Minimum viable geometry | **Required** |
| Heterogeneous-effect variant | Aggregation drift | Recommended |

### Metrics

| Metric | Notes |
|--------|-------|
| Recovery success (point) | Scored estimand `relative_att_post` unchanged |
| Placebo band width / position | Path-level `placebo_band` exports |
| Null FPR / coverage | **Only if estimand alignment documented**; else report as **diagnostic non-calibration** |
| Power, significance rate | Positive scenario |
| `interval_estimand`, `interval_aligned`, `interval_type` | Mandatory metadata per rep |
| Failure rate, `placebo_unsupported` reasons | Control-count gates |
| Seed stability | std across seeds 0–1–2 |

### Simulation counts

| Tier | n_simulations | Seeds | Use |
|------|---------------|-------|-----|
| **Characterization** | 30 | 0, 1, 2 | Geometry matrix, unsupported-rate surface |
| **Production-scale** | **100** | **0, 1, 2** | Primary SCM Placebo config on null + positive — if aligned path exists |

### Archive rules

Per INV-017 lifecycle:

1. This plan committed before execution.  
2. Evidence archive: `PHASE15_PLACEBO_CHARACTERIZATION_001.md`.  
3. Failure analysis if anti-calibration or systematic misalignment discovered.  
4. Governance addendum with **export policy recommendations** (documentation — not code in planning PR).  
5. Dispositions → DEF-020 in deferred registry.

### Execution note (future)

Investigation-only `RecoveryRunner` or custom loop may be required — **no registry change** in characterization PRs unless full promotion chain completes later.

---

## 4. Acceptable outcomes

| Outcome | Meaning |
|---------|---------|
| **Trustworthy null monitor** | Stable null behavior under declared geometry; suitable for expert-review null reference |
| **Expert-review inference (strict export)** | Usable with mandatory `placebo_band` labeling; not interchangeable with jackknife CI |
| **Null monitor only** | Null acceptable; positive power not claimed |
| **Research-only** | Unstable, unsupported on default DGP, or semantically incompatible with recovery calibration |
| **Policy closed on relative-ATT calibration** | Placebo excluded from nominal `relative_att_post` calibration path (like DID cumulative) — **valid if evidenced** |
| **Geometry restricted** | e.g. single-treated-only or minimum donor policy |

All outcomes must be **archived**, not inferred from unit tests alone.

---

## 5. Non-goals

Phase 15 planning and execution **does not**:

- Modify placebo inference implementation (`inference/placebo.py`, mode impl)  
- Change recovery scoring or interval extraction without separate governed PR  
- Promote Placebo to nominal calibration eligibility  
- Change maturity labels or release gates  
- Implement Track B contracts  
- Conflate placebo bands with jackknife/bootstrap CIs in documentation or product copy  
- Auto-enable `placebo_strict` globally  

Phase 15 **does**:

- Characterize a catalog-listed inference mode before Track B trust composition  
- Resolve OPEN_INVESTIGATIONS placebo-vs-CI ambiguity with evidence  
- Inform TrustReport `calibration_unavailable` / `incompatible_estimand` rules for placebo exports  
- Close or narrow DEF-020 when characterized  

---

## Appendix — known constraints from code/tests

| Constraint | Source |
|------------|--------|
| `IntervalType.PLACEBO_BAND` distinct from CI | `inference_result.py`, `test_inference_result_semantics.py` |
| Placebo unavailable with insufficient controls | `inference/modes/impl.py` |
| Single-treated / strict mode limitations | OPEN_INVESTIGATIONS |
| Not in production nominal calibration registry | `nominal_calibration.py` |

---

*Investigation plan INV-029 / Phase 15. No code or registry changes in this document.*
