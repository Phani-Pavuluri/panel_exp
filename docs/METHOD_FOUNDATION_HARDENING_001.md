# METHOD-FOUNDATION-HARDENING-001

**Document ID:** METHOD-FOUNDATION-HARDENING-001  
**Type:** Pre-LLM scientific foundation phase plan — **governance / research planning only**  
**Status:** **complete**  
**Date:** 2026-06-03  
**Verdict:** Define the next phase of **estimator / inference / design / compatibility hardening** before any LLM decision-layer integration  
**Supersedes (for sequencing):** ad-hoc “next OC” without foundation framing  

**Primary inputs:** [`METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md`](METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md) · [`METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md`](METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md) · [`METHOD_STRENGTHENING_LANES_001.md`](METHOD_STRENGTHENING_LANES_001.md) · [`AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md) · [`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md) · [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) · [`track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md) (validation PR) · [`F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md`](F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md) · [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) · [`F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md`](F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md)

**Related:** [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) · [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md) · [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) · [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) § LLM interface

---

## 1. Phase statement

| Statement | Meaning |
|-----------|---------|
| **LLM layer is paused** | No LLM orchestration, synthesis, or operator-facing “best method” narratives until this phase’s exit criteria (§6) are met. AUDIT-011 (before LLM interface) remains **planned**, not started. |
| **Estimator / design / inference hardening comes first** | Work prioritizes **conceptual clarity**, diagnostics, and compatibility labeling — not promotion or production behavior change. |
| **Goal is not perfection** | Enough stable, **labeled**, scientifically meaningful evidence that an LLM layer can **summarize without inferring hidden validity**. |
| **Governance stack is sufficient** | Track B contracts, Track D OC, Track E suitability, Track F decision policy, method selection/strengthening, and AugSynth ASCM-002 **prevent unsafe promotion** — they do not replace foundation hardening. |

```text
Governance (safe)  →  Foundation hardening (this phase)  →  Method development roadmap  →  LLM decision layer (paused)
                              ↑ you are here                    ↑ METHOD-SOUNDNESS-AND-GAP-ROADMAP-001
```

**Non-goals:** Method promotion, CS/MMM expansion, TrustReport/F-DECISION changes, governed-uncertainty allowlist expansion, budget recommendation layer.

---

## 2. Current foundation status

Summary by layer (authoritative decomposition: METHOD-READINESS matrix L1/L2/L3).

| Layer | Status | Evidence base | Foundation gap |
|-------|--------|---------------|----------------|
| **Estimators (L1)** | SCM **strong** on 001e; AugSynth **strong diagnostic**; TBR **niche** on 1×1; TBRRidge **moderate**; supergeo/trim **blocked**; TROP/BayesianTBR **research_only** | CV-001 · D2 · D5-INST · Track E E2 | Failure-mode thresholds, outside-hull behavior, design bridges |
| **Inference (L2)** | SCM+JK **strong null-monitor**; Conformal/Kfold **strong diagnostic** bands; Placebo **falsification**; JKP **unverified** on some families | D3 · F-INF-001 · D5-INF/INST | Role confusion (band vs null-monitor vs falsification); JKP semantics |
| **Designs / geometries (F-GEO)** | Unit panel **supported**; aggregate 1×1 **partial**; multi-cell per-cell **partial**; supergeo/trim **blocked** | F-GEO-001 · D5-DES · design inventory | Adapter/estimand bridges; design-stage vs readout-stage alignment |
| **Estimator × inference (L3)** | **A26 only** `ready_limited_governed_use`; A05/A18/A19 **characterized_restricted**; A16/A21 **callable_unverified** | AUDIT-010 · COMBO audit · ASCM-002 | AugSynth pairing policy closed in ADR; many tuples still diagnostic-only |
| **Design × readout compatibility** | Partial — power/MDE paths use TBRRidge agg2; matching vs SCM readout not unified | D5-POW · D5-DES · DESIGN-INVENTORY | POW vs final estimator mismatch; greedy_match vs readout estimator |
| **Diagnostics** | D5 batteries + ASCM-002 D1–D7 **partially** archived; threshold **vocabulary** defined | ASCM-002 JSON · [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) | Numeric cutoffs **provisional**; ASCM-003 calibration pending |
| **Promotion readiness** | **0** promotion-ready combinations | METHOD-SELECTION framework | By design until foundation + audit gates |

**AugSynth lane snapshot:** ASCM-002 → `remain_diagnostic_comparator`; [`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md) accepted — **no pairing promoted**.

---

## 3. Known conceptual gaps

| gap_id | layer | affected methods | why it matters | current evidence | risk if unresolved | recommended next artifact | priority |
|--------|-------|------------------|----------------|------------------|-------------------|---------------------------|----------|
| **GAP-ASCM-INF-001** | compatibility / inference | AugSynthCVXPY + JK / Conformal / Kfold | LLM cannot label which uncertainty layer applies to AugSynth | ADR-001 + ASCM-002 | Wrong null-monitor or lift claims | ✅ [`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md) | **P0 done** |
| **GAP-ASCM-HULL-001** | estimator / diagnostics | AugSynthCVXPY vs SCM | Outside-hull weak-fit: AugSynth **did not** beat A26 @ 8% (W3) | ASCM-002 + threshold audit | Over-trust augmentation under extrapolation | ✅ [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md); **ASCM-003** for calibration | **P1 audit done** · calibration open |
| **GAP-SCM-DIAG-001** | diagnostics | SCM / A26 | Weak pretreatment fit trigger not operational for product/LLM | Charter D1–D11 partial + audit §2 | SCM used when diagnostics say challenge | ✅ [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md); **ASCM-003** for numeric cutoffs | **P1 audit done** · calibration open |
| **GAP-CONF-001** | inference | Conformal (A05, A18, A19) | 100% null FPR / invalid bands on batteries — not governed uncertainty | D5-003 · F-INF-003 POSTFIX | LLM treats bands as decision-grade | F-INF policy note + **keep_restricted** (no promotion OC) | **P1** |
| **GAP-KFOLD-001** | inference | Kfold on AugSynth/TBRRidge | Diagnostic CI vs governed uncertainty role unclear | KFOLD-001 · ASCM-002 | Role creep to null-monitor | `INFERENCE_ROLE_TAXONOMY_ADR_001` (Kfold/Conformal/Placebo) | **P2** |
| **GAP-DES-READ-001** | compatibility | Design methods × readout estimators | Design-stage assignment (greedy, stratified, …) vs SCM/AugSynth readout not audited as pairs | DESIGN-INVENTORY · D5-DES | LLM recommends design incompatible with readout | `DESIGN_READOUT_COMPATIBILITY_AUDIT_001` | **P2** |
| **GAP-POW-EST-001** | compatibility | PowerAnalysis / MDE vs SCM+JK | Power path uses TBRRidge agg2; final readout often SCM+JK | D5-POW-001a–e | Planning vs decision evidence mismatch | `POWER_READOUT_ALIGNMENT_ADR_001` | **P2** |
| **GAP-MCELL-001** | design / compatibility | Multi-cell geo | Per-cell vs pooled estimand and conflict policy incomplete | D5-MCELL · F-MCELL backlog | Pooled lift claims without bridge | `F-MCELL-001` pooling ADR | **P3** |
| **GAP-TBR-AGG-001** | estimator / compatibility | Class TBR 1×1 | Aggregate estimand vs unit-panel methods unresolved | D5-TBR-001 · matrix | Wrong geometry promotion | `TBR_AGGREGATE_STRENGTHENING_001` / bridge audit | **P4** |
| **GAP-TBR-TBRR-001** | estimator | TBR vs TBRRidge | Audit trail and product language conflation | CV-EST-TBR · D2 | Incorrect competitor comparisons | Maintain in conceptual validity; cite in LLM labels | **P2** |
| **GAP-SGEO-001** | design | Supergeo | No F-GEO-003 adapter; flat SCM tensor invalid | D5-DES-SUPERGEO · RTP-003 | GeoLift-style designs with wrong readout | `TRIM_SUPERGEO_STRENGTHENING_001` / F-GEO-003 ADR | **P5** |
| **GAP-TRIM-001** | design | TrimmedMatch | Population estimand bridge missing | D5-DES-TRIM · F-GEO-004 | Trim design with SCM readout | `TRIM_SUPERGEO_STRENGTHENING_001` / F-GEO-004 ADR | **P5** |
| **GAP-PLACEBO-001** | inference | Placebo (A27) | Falsification vs lift uncertainty conflated in product narratives | D5-PLACEBO · F-P0-005 backlog | LLM uses placebo as primary uncertainty | `PLACEBO_FALSIFICATION_TAXONOMY_ADR_001` | **P2** |
| **GAP-JKP-001** | inference | JKP on TBRRidge (A16/A21) | Pooled-CF semantics; high null FPR in characterization | D5-TBRRIDGE-003 · F-INF-002 | Unsafe comparator promotion | `TBRRIDGE_JK_JKP_STRENGTHENING_001` failure-mode doc | **P2** |
| **GAP-DISC-001** | diagnostics | All unit-panel readouts | Disagreement policy exists in F-DECISION but not LLM-ready facet labels | F-DECISION-001 · TrustReport context | LLM averages conflicting readouts | `METHOD_DISAGREEMENT_POLICY_FOR_LLM_001` | **P2** |
| **GAP-HULL-001** | diagnostics | SCM / AugSynth | Donor hull / extrapolation metrics not stable product thresholds | ASCM-002 + audit §2.4 | Silent extrapolation | ✅ Labels in threshold audit; **ASCM-003** for stable cutoffs | **P1 audit done** · calibration open |
| **GAP-EST-BRIDGE-001** | compatibility | AugSynth point vs A26 | Scale/path mismatch at null (D5-AS-FIND-004) | D5-001 · ASCM-002 | Lift compare without bridge | `AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001` | **P2** |

---

## 4. Prioritized lanes (next 4–6)

Lanes are **execution order** for foundation hardening. They **do not** change production roles.

### Lane P0 — AugSynth/ASCM inference pairing ADR ✅ **complete**

| Field | Content |
|-------|---------|
| **Goal** | Policy for each AugSynth inference pairing post-ASCM-002 |
| **Why now** | ASCM-002 completed; pairing was open |
| **Deliverables** | [`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md) |
| **Stop condition** | ADR accepted; no pairing promoted | **Met** |
| **Guardrails** | No F-DECISION/TrustReport change | **Met** |

### Lane P1 — SCM / AugSynth diagnostic threshold audit ✅ **audit complete** (calibration open)

| Field | Content |
|-------|---------|
| **Goal** | Operational thresholds for weak SCM fit, hull/extrapolation, false-confidence flags (charter D1–D11) consumable by Track B / future LLM |
| **Why now** | ASCM-002 showed inside-hull vs outside-hull split; thresholds not product-stable |
| **Deliverables** | ✅ [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md); **next:** `D5-INST-AUGSYNTH-ASCM-003` (research OC, larger n_mc, label calibration) |
| **Stop condition** | Threshold definitions + evidence table + “when to surface blocker” rules documented | **Met** (numeric cutoffs provisional) |
| **Guardrails** | No promotion; no SCM demotion; diagnostics labels only | **Met** |

### Lane P2 — Design–readout compatibility audit

| Field | Content |
|-------|---------|
| **Goal** | Map each **design method** (DES-INV) to allowed **readout estimator × inference** tuples; flag POW/MDE vs final-readout mismatches |
| **Why now** | DESIGN-INVENTORY complete; compatibility matrix L3 silent on design stage |
| **Deliverables** | `DESIGN_READOUT_COMPATIBILITY_AUDIT_001.md`; updates to robustness matrix crosswalk |
| **Stop condition** | Compatibility table with explicit **allowed / diagnostic-only / blocked** per design×readout pair |
| **Guardrails** | No new production paths; no MMM |

### Lane P3 — Multi-cell pooling / per-cell decision ADR

| Field | Content |
|-------|---------|
| **Goal** | F-MCELL-001: per-cell primary path vs pooled claims; conflict policy for LLM labels |
| **Why now** | Product k=2 tests; pooled blocked in AUDIT-010 |
| **Deliverables** | `F-MCELL-001` ADR; D5-MCELL refresh charter (OC optional, separate PR) |
| **Stop condition** | Pooled estimand bridge documented or permanently blocked with explicit label |
| **Guardrails** | No pooled promotion without ADR |

### Lane P4 — TBR aggregate 1×1 bridge audit

| Field | Content |
|-------|---------|
| **Goal** | Class TBR aggregate estimand, geometry contract, inference semantics vs unit-panel SCM |
| **Why now** | High product ask; D5-TBR-001 maintained; matrix niche strong |
| **Deliverables** | `TBR_AGGREGATE_STRENGTHENING_001` (extend METHOD-STRENGTHENING lane) |
| **Stop condition** | Bridge audit complete; `aggregate_only_primary` still **not** granted without promotion audit |
| **Guardrails** | Never on unit panel |

### Lane P5 — Supergeo / trim conceptual bridge charters

| Field | Content |
|-------|---------|
| **Goal** | F-GEO-003/004 ADR scope + RTP charters; no flat-panel SCM readout |
| **Why now** | Blocked despite high external importance (F-BACKLOG-002) |
| **Deliverables** | `TRIM_SUPERGEO_STRENGTHENING_001` (existing lane registry) |
| **Stop condition** | Adapter/estimand bridges specified; OC batteries scoped — not executed in planning doc |
| **Guardrails** | keep_blocked until bridge + OC |

**Parallel P2 tracks (same priority band):** inference role taxonomy (GAP-KFOLD, GAP-PLACEBO), method disagreement policy for LLM (GAP-DISC), AugSynth–SCM estimand bridge (GAP-EST-BRIDGE).

---

## 5. What is explicitly not next

| Not next | Rationale |
|----------|-----------|
| **LLM-layer synthesis / orchestration** | Paused until §6 |
| **MMM ingestion expansion** | AUDIT-010 `not_ready_continue_track_f` |
| **CalibrationSignal expansion** | A26 only |
| **Method promotion / F-DECISION role upgrades** | 0 promotion candidates; foundation first |
| **Governed uncertainty allowlist expansion** | F-INF allowlist **empty** |
| **Budget recommendation / optimizer layer** | Track C gated |
| **Operator “best method” narrative** | Violates selection framework + this phase |
| **Reopening completed governance** | Unless a gap table row requires a cross-reference only |

---

## 6. LLM readiness criteria

Before **AUDIT-011** / LLM interface work resumes, **all** must hold:

| # | Criterion | Foundation action |
|---|-----------|-------------------|
| L1 | Every evidence object has **stable method identity** (estimator × inference × geometry × estimand IDs) | Track B catalog + matrix rows wired in labels |
| L2 | Estimator / inference / design **compatibility labeled** (allowed / diagnostic / blocked / research) | P2 design–readout audit + matrix refresh |
| L3 | **Diagnostics distinguish failure modes** (weak fit, hull, sparsity, scale bridge) | P1 threshold audit ✅ vocabulary; ASCM-003 for calibrated cutoffs |
| L4 | **Method disagreement policy** is explicit and facet-labeled | P2 GAP-DISC artifact |
| L5 | LLM may **only summarize labeled evidence** — not infer hidden validity | Prompt/contract requirement in future AUDIT-011 |
| L6 | **Research-only** results cannot be described as decision-grade | F-DECISION roles + E5 policy enforced in labels |
| L7 | **Unresolved gaps surface as blockers**, not smoothed | Gap table §3 maintained in registry |
| L8 | **Inference role taxonomy** clear (null-monitor vs diagnostic band vs falsification) | P2 ADR + ADR-001 for AugSynth |
| L9 | **No pairing promoted** without promotion audit | METHOD-SELECTION pipeline unchanged |

**Exit from METHOD-FOUNDATION-HARDENING-001:** Lanes P1–P5 deliverables complete **or** explicitly deferred with blocker labels; gap table has no **P1 audit** rows open (P1 **numeric calibration** via ASCM-003 may remain open); ROADMAP marks LLM layer **unblocked for planning** only after P2–P5 + calibration (not auto-implemented).

---

## 7. Relationship to existing program layers

```text
METHOD-READINESS (L1/L2/L3 status)
  → METHOD-SELECTION (promotion pipeline — paused at 0 promotions)
  → METHOD-STRENGTHENING (evidence lanes — AugSynth in progress)
  → METHOD-FOUNDATION-HARDENING (this doc — pre-LLM scientific clarity)
  → AUDIT-011 / LLM interface (future)
```

| Layer | Role during foundation hardening |
|-------|----------------------------------|
| **F-DECISION-001** | Baseline unchanged |
| **TrustReport `f_decision_context`** | Visibility only |
| **Track D OC** | Research lane; feeds gap closure |
| **Track E cards** | Updated when audits complete — not promotion |

---

## 8. Stop condition (met)

| Criterion | Status |
|-----------|--------|
| Phase statement (LLM paused; hardening first) | ✅ §1 |
| Foundation status by layer | ✅ §2 |
| Gap table with required items | ✅ §3 |
| 4–6 prioritized lanes with deliverables | ✅ §4 (P0–P5) |
| Explicit not-next list | ✅ §5 |
| LLM readiness criteria | ✅ §6 |
| No production / promotion / CS / MMM / LLM change | ✅ |

---

*METHOD-FOUNDATION-HARDENING-001 v1.0.0 — planning only; execution via P1–P5 lanes.*
