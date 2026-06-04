# AUGSYNTH-ASCM-DEVELOPMENT-ROADMAP-001

**Document ID:** AUGSYNTH-ASCM-DEVELOPMENT-ROADMAP-001  
**Type:** Focused execution roadmap — **AugSynth/ASCM active lane only**  
**Status:** **complete** — P1–P6 execution ✅; lane **closed** per [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md)  
**Date:** 2026-06-03  
**Verdict:** Convert audit/review findings into a **concrete PR sequence** — diagnostics → fidelity audit → stratified OC → inference calibration → design compatibility  
**Decision context:** [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md) — **`proceed_to_augsynth_development_lane`**

**Primary inputs:** [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) · [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) · [`AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md) · [`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md) · [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) · [`track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md) · [`track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json`](track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json)

**Code references:** [`panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py`](../panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py) · [`tests/track_d/test_d5_inst_augsynth_ascm_002.py`](../tests/track_d/test_d5_inst_augsynth_ascm_002.py)

---

## 1. Purpose

This is the **active AugSynth/ASCM development roadmap** — the first execution lane selected after [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md).

It converts prior audit, threshold, and OC evidence into **named PRs** with code, tests, archives, or audit procedures.

**This document is not:**

| Not | Meaning |
|-----|---------|
| A **promotion document** | No role upgrades; A26 unchanged |
| An **eligibility framework** | F-DECISION-001 and AUDIT-010 remain authoritative |
| An **LLM-layer plan** | LLM paused per foundation hardening |
| A **replacement for code-backed evidence** | Each PR must produce runnable artifacts |

**Next step (2026-06-04):** AugSynth-specific execution **paused** under [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md). P1–P6 + [`METHOD_FOUNDATION_SYNTHESIS_001.md`](METHOD_FOUNDATION_SYNTHESIS_001.md) remain **evidence inputs** only. **`D5-INST-AUGSYNTH-MULTICELL-001`** is **not** the default next step (optional later: narrow ADR metadata gate regression only). Repo-wide next: **`METHOD_CODE_INVENTORY_001`**.
**Next step after lane closeout:** ✅ [`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md`](MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md) **accepted** (see [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md)) → **`D5-INST-AUGSYNTH-MULTICELL-001`** (OC). Then [`AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md) · optional **`D5-INST-AUGSYNTH-DESIGN-COMPAT-001`**. P1–P6 ✅.

---

## 2. Current evidence state

Reconciled from ASCM-002, ADR-001, threshold audit, and AUDIT-010 — **no new decisions**.

| Topic | Current state |
|-------|---------------|
| **A26 (SCM + UnitJackKnife)** | Current governed **null-monitor baseline**; `ready_limited_governed_use`; CalibrationSignal `null_monitor_only` only |
| **AugSynthCVXPY point (A01)** | **`diagnostic_comparator`**; material scale/path disagreement vs A26 at null (D5-AS-FIND-004) |
| **AugSynthCVXPY + UnitJackKnife (A02/A03)** | **`diagnostic_comparator`**; JK null FPR **0.0** on ASCM-002 W2/W3; estimand ≠ A26 JK; **more OC needed** (ADR-001) |
| **AugSynthCVXPY + Conformal (A05)** | **`characterized_restricted`**; **not governed uncertainty**; keep_restricted (ADR-001) |
| **AugSynthCVXPY + Kfold (A03 path)** | **`diagnostic_comparator`** / restricted robustness only (KFOLD-001, ADR-001) |
| **ASCM-002 weak-fit recovery** | AugSynth point beats A26 MAE on **1/2** weak-fit worlds @ 8% injection |
| **Inside hull (W2)** | Promising — AugSynth beats A26 MAE @ 8% |
| **Outside hull (W3)** | **Does not** reliably beat A26 — AugSynth MAE worse @ 8% |
| **JK null FPR (W2/W3)** | **0.0** for A26 and AugSynth+JK (conservative on available slice) |
| **Threshold labels** | **Provisional** — vocabulary in threshold audit; numeric cutoffs need ASCM-003 |
| **Diagnostics D8/D10/D11** | **Missing or incomplete** in ASCM-002 JSON (outcome-model sensitivity, scale bridge, false-confidence flag) |
| **Promotion audit** | **Not open** — `promotion_audit_eligible: false` (ASCM-002) |

**Harness reuse:** `track_d_d5_inst_augsynth_ascm_002.py` + `tests/track_d/test_d5_inst_augsynth_ascm_002.py` (n_mc=4 archive committed).

---

## 3. Development gaps

| gap_id | layer | description | current evidence | risk if unresolved | next artifact | priority |
|--------|-------|-------------|------------------|-------------------|---------------|----------|
| **GAP-ASCM-FID-001** | estimator | Implementation fidelity vs intended AugSynth/ASCM (objective, ridge, weights) | Charter §4 I4–I8 partial; CV-EST-AUGSYNTH | Wrong OC conclusions | **AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001** | **P2** |
| **GAP-ASCM-HULL-002** | diagnostics | Outside-hull behavior unresolved (W3 no MAE win) | ASCM-002 W3 | Over-trust augmentation under extrapolation | **D5-INST-AUGSYNTH-ASCM-003** | **P3** |
| **GAP-ASCM-WFIT-001** | OC | Weak-fit severity not calibrated; world labels ≠ RMSE monotonicity | ASCM-002 n_mc=4 | Wrong threshold cutoffs | **D5-INST-AUGSYNTH-ASCM-003** | **P3** |
| **GAP-ASCM-HULL-001** | diagnostics | Donor-hull / extrapolation diagnostics incomplete for product labels | D6 in JSON; labels provisional | Silent extrapolation in narratives | **D5-DIAG-SCM-AUGSYNTH-001** + ASCM-003 | **P1** / P3 |
| **GAP-ASCM-META-001** | metadata | Weight concentration / effective donor count need stable emission | D4/D5 partial; NaN on blocked runs | Cannot label `weight_concentration_high` | **D5-DIAG-SCM-AUGSYNTH-001** | **P1** |
| **GAP-ASCM-FC-001** | diagnostics | False-confidence flags missing (D11) | Not in ASCM-002 JSON | False-confidence narratives | **D5-DIAG-SCM-AUGSYNTH-001** | **P1** |
| **GAP-ASCM-SCALE-001** | metadata | Scale bridge diagnostics missing (D10) | `conflict_vs_a26` aggregate only | Lift compare without bridge | **D5-DIAG-SCM-AUGSYNTH-001** | **P1** |
| **GAP-ASCM-DISC-001** | diagnostics | AugSynth vs SCM disagreement labels need calibration | 100% material point mismatch @ null | LLM may smooth disagreement | **D5-INST-AUGSYNTH-ASCM-003** | **P3** |
| **GAP-ASCM-JK-001** | inference | AugSynth+JK FPR/coverage needs larger OC | 0.0 on W2/W3 only; n_mc=4 | Premature JK promotion narrative | **D5-INF-AUGSYNTH-JK-CALIBRATION-001** | **P4** |
| **GAP-ASCM-CONF-001** | inference | Conformal failure mode needs isolation | D5-AUGSYNTH-003 + POSTFIX; not governed | Role creep to uncertainty | **D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001** | **P5** |
| **GAP-ASCM-KF-001** | inference | Kfold semantics remain diagnostic only | KFOLD-001; ADR-001 | Mislabeled as null monitor | ADR-001 (done); no promotion OC | **defer** |
| **GAP-ASCM-MT-001** | design_compatibility | Multi-treated / per-cell compatibility needs explicit validation | W11 in ASCM-002; A28 placebo block | Pooled or wrong geometry claims | ✅ P6 · pooling ADR (semantics) | **paused** → [`METHOD_VALIDATION_PROGRAM_001`](METHOD_VALIDATION_PROGRAM_001.md) Layer 4–5 |
| **GAP-ASCM-POW-001** | design_compatibility | Power/MDE path (TBRRidge agg2) vs AugSynth readout mismatch | D5-POW-001a | Planning vs readout confusion | **DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001** | **P6** |
| **GAP-ASCM-D8-001** | diagnostics | Outcome-model sensitivity (D8) not archived | Charter gap | Ridge misspecification hidden | **D5-DIAG-SCM-AUGSYNTH-001** + ASCM-003 grid | **P1** / P3 |

---

## 4. Workstreams

Concrete workstreams only — each maps to one or more PRs in §5.

### A. Diagnostics implementation

| Field | Value |
|-------|--------|
| **Deliverable** | **D5-DIAG-SCM-AUGSYNTH-001** |
| **Goal** | Implement and emit diagnostics required by [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) and ASCM-003: D8/D10/D11, normalized fields, blocked-run handling |
| **Scope** | Shared **SCM + AugSynthCVXPY** legs on unit-panel geo; extends or wraps ASCM-002 harness |
| **Out of scope** | Final threshold numeric cutoffs; TrustReport wiring |

### B. Estimator fidelity audit

| Field | Value |
|-------|--------|
| **Deliverable** | **AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001** |
| **Goal** | Audit objective, loss, regularization, weight constraints, donor eligibility, multi-treated handling, estimand, metadata vs `panel_exp/methods/scm.py` |
| **Out of scope** | Silent estimator behavior changes; promotion |

### C. Larger stratified OC

| Field | Value |
|-------|--------|
| **Deliverable** | **D5-INST-AUGSYNTH-ASCM-003** |
| **Goal** | Larger n_mc (≥ 14); weak-fit severity grid; inside/outside hull; sparse/rich donors; shock/noise/outlier; ridge sensitivity; **calibrate provisional threshold cutoffs** |
| **Depends on** | P1 diagnostics schema stable |

### D. Inference calibration

| Deliverable | Goal |
|-------------|------|
| **D5-INF-AUGSYNTH-JK-CALIBRATION-001** | FPR, coverage, interval width, false-confidence on null/effect worlds — **do not promote JK** |
| **D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001** | Isolate invalid/unsafe Conformal behavior — repairable vs permanently restricted; **no governed uncertainty change** |

### E. Design / readout compatibility

| Field | Value |
|-------|--------|
| **Deliverable** | **DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001** |
| **Goal** | Map **actual repo-supported** design/geometries compatible with AugSynthCVXPY readout (single-cell, multi-treated per-unit, per-cell multi-cell if harness supports); **exclude** unsupported geometries explicitly |
| **Parallel** | Foundation P2 `DESIGN_READOUT_COMPATIBILITY_AUDIT_001` may subsume partially — this artifact is **AugSynth-scoped** |

---

## 5. Proposed PR sequence

| PR | Artifact | Type | Notes |
|----|----------|------|-------|
| **P1** | **D5-DIAG-SCM-AUGSYNTH-001** | code + tests | Diagnostic implementation; optional refresh of diagnostic slice in ASCM-002 archive/report — **no threshold finalization** |
| **P2** | **AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001** | audit doc | May list implementation fixes; **no silent code change** in audit PR |
| **P3** | **D5-INST-AUGSYNTH-ASCM-003** | OC harness + JSON + report + tests | Weak-fit grid, hull/sparsity/shock variants, n_mc for calibration |
| **P4** | **D5-INF-AUGSYNTH-JK-CALIBRATION-001** | OC | Null/effect worlds; FPR/coverage/width; no JK promotion |
| **P5** | **D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001** | OC / failure doc | Isolate Conformal unsafe modes; no CS/MMM |
| **P6** | **DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001** | compatibility audit | ✅ [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md) — verdict `compatible_per_cell_only_pooling_blocked` |

```text
P1 diagnostics (code) → P2 fidelity audit → P3 stratified OC → P4 JK OC → P5 Conformal OC → P6 design compat (docs)
```

**Deferred after P3–P4:** `AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001` (estimand bridge ADR).

---

## 6. Evidence standards

Every PR in §5 must include:

| Requirement | Applies to |
|-------------|------------|
| Runnable **code**, **audit procedure**, or **OC harness** | P1–P5 |
| **Tests** (pytest) | P1, P3–P5 |
| **Archived JSON** when OC is executed | P3–P5 |
| **Report** with scientific conclusion + **limitations** | P2–P6 |
| **Exact repo method names** (AugSynthCVXPY, UnitJackKnife, …) | All |
| **Guardrails block**: no promotion · no CS/MMM · no TrustReport/F-DECISION change · no LLM | All |

---

## 7. Stop/go criteria

### A. Continue diagnostic only (default posture)

Trigger when **any** of:

- Partial weak-fit recovery persists (≤ 50% worlds beat A26 @ agreed effect grid)
- Outside-hull (W3-class) behavior remains poor
- Threshold labels unstable across ASCM-003 n_mc repeats
- AugSynth+JK/Conformal remain uncalibrated for promotion narrative

**Action:** Maintain `diagnostic_comparator`; refresh Track E cards; **no F-DECISION amendment**.

### B. Run additional OC

Trigger when:

- Promising but noisy inside-hull improvement
- Threshold label precision/recall unclear on ASCM-003
- Weak-fit severity grid needs refinement

**Action:** ASCM-004 or targeted slice OC — **charter amendment required** before execution.

### C. Open implementation fix

Trigger when:

- Fidelity audit (P2) finds mismatch vs intended ASCM algorithm (objective, ridge, weights, donor rules)

**Action:** Separate governed fix PR with tests — **not** bundled into audit doc PR.

### D. Open inference calibration

Trigger when:

- JK remains conservative but coverage/width characterization incomplete (P4)
- Conformal failure isolated and potentially repairable (P5)

**Action:** Fix or restriction ADR — **still no governed uncertainty export** without F-INF amendment.

### E. Consider future promotion audit (not opened here)

**All** required before **scoping** [`METHOD_PROMOTION_AUDIT_TEMPLATE_001.md`](METHOD_PROMOTION_AUDIT_TEMPLATE_001.md):

- Stable improvement in **targeted** weak-fit worlds (inside hull)
- No unsafe null FPR on nominated inference arm
- Calibrated diagnostics (D1–D11 + labels)
- Closed estimand bridge + inference semantics
- Design/readout compatibility for claimed geometry
- Explicit F-DECISION amendment path

**This roadmap does not open a promotion audit.**

---

## 8. Relationship to broader roadmap

| Relationship | Detail |
|--------------|--------|
| **Parent** | Active lane **DL-1** under [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) |
| **Checkpoint** | Selected by [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md) |
| **Foundation** | Implements foundation P1 calibration path; **does not replace** foundation P2–P5 |
| **Deferred families** | TBR aggregate strengthening, TBRRidge JK doc, supergeo/trim, BayesianTBR/TROP — until this lane hits stop/go or parallel docs complete |
| **Parallel (non-blocking)** | `DESIGN_READOUT_COMPATIBILITY_AUDIT_001` (foundation P2) · `INFERENCE_ROLE_TAXONOMY_ADR_001` (foundation P2) |
| **SCM coupling** | P1 diagnostics serve **A26 + AugSynth** — SCM hardening is not a separate competing lane |

---

## 9. Stop condition (this document)

| Criterion | Status |
|-----------|--------|
| Focused execution roadmap for AugSynth/ASCM lane | ✅ |
| Gap table with concrete next artifacts | ✅ §3 |
| Workstreams A–E | ✅ §4 |
| PR sequence P1–P6 | ✅ §5 — **lane closed** [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md) |
| Evidence standards + stop/go | ✅ §6–§7 |
| No promotion / eligibility / prod change | ✅ §1, §10 |
| Next workstream chosen (pooling ADR) | ✅ closeout §6 |

---

## 10. Guardrails

- **Docs/planning only** in this PR — no estimator code, inference code, or OC execution here.
- **No new eligibility decisions** — AUDIT-010 and F-DECISION-001 unchanged.
- **No promotion or demotion** — A26 baseline; AugSynth `diagnostic_comparator`.
- **No TrustReport / F-DECISION behavior change.**
- **No CalibrationSignal / MMM changes.**
- **No LLM integration.**
- **Every item in §5 maps to a concrete development PR.**

---

*AUGSYNTH-ASCM-DEVELOPMENT-ROADMAP-001 v1.0.0 — P1 complete; execute P2 next.*
