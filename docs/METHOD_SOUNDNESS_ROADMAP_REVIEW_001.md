# METHOD-SOUNDNESS-ROADMAP-REVIEW-001

**Document ID:** METHOD-SOUNDNESS-ROADMAP-REVIEW-001  
**Type:** Execution checkpoint review — **docs only**  
**Status:** **complete**  
**Date:** 2026-06-03  
**Verdict:** **`proceed_to_augsynth_development_lane`** — confirmed with DL-2 coupling; design-readout and inference taxonomy run **parallel docs**, not as blockers  
**Primary input:** [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md)

**Also reviewed:** [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) · [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) · [`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md) · [`AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md) · [`track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md)

**Guardrails:** No new eligibility decisions. No promotion/demotion. No TrustReport/F-DECISION/CalibrationSignal/MMM/LLM changes.

---

## 1. Review purpose

This memo is a **checkpoint after** [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) (DL-0 inventory reconciliation) and **before** launching method-specific development work.

It answers one question only:

> **Is AugSynth/ASCM truly the right immediate active lane, or should another gap (design, inference, SCM-only) come first?**

The review uses **only** the soundness roadmap inventory, scorecard (§6), development lanes (§7), and phase sequence (§8). It does **not** introduce new methods, gaps, or eligibility outcomes.

**Output:** an explicit next-lane decision and an ordered list of **3–5 concrete artifacts** where the next PR after this review should produce diagnostics, OC, code, or fidelity evidence — not another planning layer.

---

## 2. Audit-derived top gaps

Top gaps taken from soundness roadmap §6 scorecard and §7 lanes (highest reuse × evidence weakness × LLM-readiness impact).

| gap / lane ID | affected item | evidence level | why it matters | blocks LLM readiness? | proposed next artifact |
|---------------|---------------|----------------|----------------|----------------------|------------------------|
| **DL-1 / EST-ASCM** | **AugSynthCVXPY** | stratified_OC | Only headline estimator with `promising_needs_OC`; ASCM-002 stratified weak-fit/hull; outside-hull W3 failure documented | **Partial** — L3 diagnostics for comparator disagreement | **D5-INST-AUGSYNTH-ASCM-003** |
| **DL-1 / A01–A03** | AugSynthCVXPY + point/JK/Kfold | stratified_OC | Richest unit-panel comparator tuple evidence; scale bridge still open | **Yes** — L4 disagreement labels need calibrated diagnostics | **AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001** (after ASCM-003) |
| **DL-1 + DL-2 / diagnostic_gap** | SCM + AugSynthCVXPY (A26 + A01–A03) | stratified_OC (partial metadata) | Threshold audit labels provisional; D8/D10/D11 **not** in ASCM-002 JSON | **Yes** — foundation §6 L3 | **D5-DIAG-SCM-AUGSYNTH-001** |
| **GAP-SCM-DIAG / EST-SCM** | SCM / SyntheticControlCVXPY (A26) | stratified_OC | A26 `sound_for_current_role` but failure-mode labels not code-backed | **Yes** — same L3 criterion | **D5-DIAG-SCM-AUGSYNTH-001** (shared harness) |
| **DL-4 / DES-GREEDY** | greedy_match_markets (+ tier-1 designs) | stratified_OC | Design matcher ≠ SCM donor pool; POW vs readout mismatch (D5-POW-001a) | **Yes** — foundation §6 L2 design compatibility | **DESIGN_READOUT_COMPATIBILITY_AUDIT_001** |
| **DL-3 / INF-CONF + INF-KF** | Conformal, Kfold (cross-estimator) | small_OC | Role taxonomy incomplete vs null-monitor (foundation GAP-KFOLD-001) | **Yes** — foundation §6 L8 | **INFERENCE_ROLE_TAXONOMY_ADR_001** |
| **DL-3 / A16 INF-JK-TBRR** | TBRRidge + UnitJackKnife | small_OC | `known_failure_mode` (~79% null FPR); already characterized | **No** — documented restricted; not primary path | **TBRRIDGE_JK_JKP_STRENGTHENING_001** |
| **DL-5 / A29–A30** | supergeos, trimmedmatch | small_OC / docs_only | `blocked_by_geometry` for flat SCM+JK | **No** for unit-panel LLM slice | **TRIM_SUPERGEO_STRENGTHENING_001** / F-GEO ADRs |

**Not top immediate gaps (defer):** BayesianTBR, TROP, MTGP (`research_only` / `evidence_missing`); TBR aggregate (`sound_for_current_role` on agg geometry); real-panel replay (**evidence_missing**).

---

## 3. Candidate next lanes

### 3.1 AugSynth/ASCM development (DL-1 + coupled DL-2)

| Field | Assessment |
|-------|------------|
| **Reason to do now** | Sole headline estimator at `promising_needs_OC` with **stratified_OC**; ASCM-002 executed; threshold audit + ADR-001 complete; existing harness (`track_d_d5_inst_augsynth_ascm_002.py`); clear follow-up OC (ASCM-003) and **code** deliverable (D5-DIAG) |
| **Reason to defer** | Does not resolve design-stage compatibility alone; estimand bridge still open; no promotion path |
| **Dependency status** | ADR-001 ✅ · threshold audit ✅ · ASCM-002 ✅ · charter ✅ |
| **Expected evidence output** | JSON with D8/D10/D11; calibrated threshold table; optional fidelity checklist |

### 3.2 SCM baseline / failure-mode hardening (DL-2)

| Field | Assessment |
|-------|------------|
| **Reason to do now** | A26 remains primary null-monitor; diagnostic labels needed for LLM L3; **`full_model=True` risk** (INV-D2-001) |
| **Reason to defer** | SCM already `sound_for_current_role`; no new estimator OC required before comparator diagnostics |
| **Dependency status** | Threshold vocabulary ✅; numeric calibration waits on ASCM-003 |
| **Expected evidence output** | Shared diagnostic harness fields for SCM leg; monitoring notes for `full_model` |

**Review note:** DL-2 is **not a competing lane** — D5-DIAG-SCM-AUGSYNTH-001 is the shared entry point for DL-1 and DL-2.

### 3.3 Inference calibration (DL-3)

| Field | Assessment |
|-------|------------|
| **Reason to do now** | Cross-cutting LLM L8; Conformal/Kfold role creep risk; TBRRidge JK/JKP semantics |
| **Reason to defer** | AugSynth pairing policy **closed** in ADR-001; TBRRidge JK is `known_failure_mode` already documented; taxonomy is **docs/ADR** not blocking diagnostic code |
| **Dependency status** | POSTFIX ✅ · ADR-001 ✅ · TBRRIDGE-003 ✅ |
| **Expected evidence output** | ADR documents; no immediate OC required for AugSynth lane |

### 3.4 Design / readout compatibility (DL-4 / foundation P2)

| Field | Assessment |
|-------|------------|
| **Reason to do now** | Six tier-1 designs characterized under SCM+JK 001e framing; greedy_match used in ASCM-002; LLM L2 gap | 
| **Reason to defer** | Next artifact is **compatibility audit (docs)** — no harness spec ready; does **not** block D5-DIAG or ASCM-003 on unit-panel greedy_match worlds already exercised |
| **Dependency status** | DESIGN-INVENTORY-001 ✅ · D5-POW-001a–e ✅ |
| **Expected evidence output** | Design×readout table; POW alignment ADR charter |

### 3.5 Inventory cleanup (DL-0)

| Field | Assessment |
|-------|------------|
| **Reason to do now** | — |
| **Reason to defer** | **Complete** — soundness roadmap + this review |
| **Dependency status** | ✅ |
| **Expected evidence output** | N/A |

### 3.6 Pause for missing evidence

| Field | Assessment |
|-------|------------|
| **Applicable?** | **No** — ASCM-002 archive, 25 OC JSONs, and scorecard rows exist; gaps are **calibration/metadata**, not absence of baseline OC |

---

## 4. Decision

### Decision code: **`proceed_to_augsynth_development_lane`**

**Not selected:**

| Outcome | Why not |
|---------|---------|
| `proceed_to_design_readout_compatibility_first` | Important for LLM L2, but next step is **docs-only**; does not unlock code/OC; ASCM-002 already runs on tier-1 design geometry |
| `proceed_to_inference_calibration_first` | Cross-cutting ADR work; AugSynth pairing already in ADR-001; does not address open **diagnostic/metadata** gaps blocking L3 |
| `proceed_to_inventory_cleanup_first` | DL-0 complete |
| `pause_for_missing_evidence` | Stratified OC + harness exist; missing pieces are named (D8/D10/D11, threshold numeric calibration) |

### Justification (audit-derived)

AugSynth/ASCM is the correct **immediate active development lane** because the soundness roadmap scorecard shows a unique combination:

1. **Recent stratified OC** — [`D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md): 12 worlds, weak-fit split, `remain_diagnostic_comparator` (evidence level `stratified_OC`).
2. **Known unresolved diagnostics** — threshold audit §3: D8/D10/D11 missing; provisional labels; W3 outside-hull stress case.
3. **Defined threshold policy** — [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) vocabulary ready; ASCM-003 recommended for numeric calibration.
4. **Candidate follow-up OC** — ASCM-003 scoped in charter §7, threshold audit §7, foundation P1.
5. **Concrete docs→code path** — existing validation harness and tests (`tests/track_d/test_d5_inst_augsynth_ascm_002.py`); next step **D5-DIAG-SCM-AUGSYNTH-001** is implementation, not another governance freeze.

**Coupling:** The lane is **AugSynth development + shared SCM/AugSynth diagnostics**, not “replace A26.” ADR-001 and F-DECISION baseline unchanged.

**Parallel (non-blocking):** `DESIGN_READOUT_COMPATIBILITY_AUDIT_001` as foundation P2 docs; `INFERENCE_ROLE_TAXONOMY_ADR_001` when DL-3 bandwidth allows.

---

## 5. Ordered next roadmap

Next **3–5 execution artifacts** after this review. Artifacts **#1–#2 complete**; **next is #3** (fidelity audit).

| Order | Artifact | Type | Lane | Rationale |
|-------|----------|------|------|-----------|
| **1** | **AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001** | docs (short) | DL-1 | ✅ Materialized — [`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md) |
| **2** | **D5-DIAG-SCM-AUGSYNTH-001** | diagnostic harness + tests | DL-1 + DL-2 | ✅ Complete — [`D5_DIAG_SCM_AUGSYNTH_001_REPORT.md`](track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md) |
| **3** | **AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001** | fidelity audit | DL-1 | **Next** — charter §4 I4–I8 |
| **4** | **D5-INST-AUGSYNTH-ASCM-003** | OC battery | DL-1 | Uses D5-DIAG diagnostics; calibrates threshold cutoffs |
| **5** | **DESIGN_READOUT_COMPATIBILITY_AUDIT_001** | compatibility audit (docs) | DL-4 | Foundation P2; **parallel** — does not block #3–#4 |

**Deferred to after #3–#4:** `AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001` (needs ASCM-003 + fidelity audit inputs).

**Explicitly not next:** LLM integration · promotion audit · TrustReport wiring · CalibrationSignal expansion.

**Next PR:** **P2 `AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001`** per [`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md). P1 D5-DIAG ✅.

---

## 6. Anti-bureaucracy check

| Rule | Status |
|------|--------|
| This review does **not** create new eligibility decisions | ✅ — F-DECISION-001 and AUDIT-010 unchanged |
| This review does **not** promote or demote methods | ✅ — `proceed_to_augsynth_development_lane` is development sequencing only |
| This review **only** chooses the next development lane | ✅ |
| Next PR after artifact #1 should produce **concrete** diagnostics, OC, code, or fidelity evidence | ✅ — **#1–#2 complete**; **#3 fidelity audit** is next |
| No further roadmap docs unless they unlock execution | ✅ — P1 code complete; next is P2 fidelity audit |

---

## 7. Stop condition

| Criterion | Status |
|-----------|--------|
| Interprets METHOD-SOUNDNESS-AND-GAP-ROADMAP-001 | ✅ §2–§3 |
| Explicit next-lane decision | ✅ §4 `proceed_to_augsynth_development_lane` |
| Ordered 3–5 artifacts | ✅ §5 |
| Anti-bureaucracy affirmed | ✅ §6 |
| No eligibility / prod behavior change | ✅ |

---

*METHOD-SOUNDNESS-ROADMAP-REVIEW-001 v1.0.0 — checkpoint complete; execute §5 from #3.*
