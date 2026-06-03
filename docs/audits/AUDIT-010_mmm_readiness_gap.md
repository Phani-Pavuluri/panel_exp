# AUDIT-010 — MMM readiness / gap audit

**Audit ID:** AUDIT-010  
**Type:** MMM **readiness / gap** audit — **not** a promotion gate  
**Status:** **closed** — readiness/gap gate (not promotion)  
**Verdict:** **`not_ready_continue_track_f`** — MMM **not ready / blocked**; CalibrationSignal **no expansion**  
**Next:** **Track F P0 hygiene** (then P2 OC; promotion lane **not** authorized)  
**Branch / baseline:** `fix-kfold-multitreated-geometry` @ post `D5-INST-TBR-001` (`4cfa77b`)  
**Prerequisites:** AUDIT-010A ✅ · TRACK-D-CONCEPTUAL-VALIDITY-AUDIT-001 ✅ · D5-INST-TBR-001 ✅  

**Related:** [`AUDIT-010A`](AUDIT-010A_roadmap_consistency_pre_mmm_gate.md) · [`TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md`](../TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md) · [`D5_INST_COMBO_AUDIT_001_REPORT.md`](../track_d/D5_INST_COMBO_AUDIT_001_REPORT.md)

**Date:** 2026-06-03

---

## Taxonomy (binding for intake and Track F P0)

| Layer | Examples | Not examples |
|-------|----------|--------------|
| **Estimator / readout** | SCM, AugSynthCVXPY, class TBR, TBRRidge, DID, TROP, BayesianTBR | **Placebo** — Placebo is **inference / falsification**, never a standalone estimator |
| **Inference / falsification** | point_estimate, UnitJackKnife, Kfold, JKP, Conformal, BlockResidualBootstrap, **Placebo**, native_bootstrap | Estimator names used as if they were inference modes |
| **Geometry** | single_cell_unit, aggregate_two_series, single_treated, multi_treated, supergeo, trimmed, **multi_cell** | Pooled cross-cell panels without `pooling_rule_id` |

**Global multi-cell rule:** Applies to **all** estimator × inference combinations. Multi-cell runs must be **per-cell only** (one cell’s treated/control assignment per panel). **Pooled** multi-cell lift, null FPR, or CIs are **blocked** unless a governed **`pooling_rule_id`** is defined. When geometry mode is multi-cell, disposition for each cell follows the matching single-cell / single-treated Appendix A row.

---

## Mandatory audit structure

AUDIT-010 **must** ship two levels of evidence. The executive summary is for readability only; **Appendix A is authoritative** for tuple coverage.

1. **Executive summary table** — short; major evidence families only (§2 below).
2. **Appendix A: Full estimator × inference × geometry disposition matrix** — **all 30** curated COMBO tuples from D5-INST-COMBO-AUDIT-001, reconciled against:
   - COMBO compatibility result ([`D5_INST_COMBO_AUDIT_001`](../track_d/D5_INST_COMBO_AUDIT_001_REPORT.md) / [`D5_INST_COMBO_AUDIT_001_results.json`](../track_d/archives/D5_INST_COMBO_AUDIT_001_results.json))
   - Conceptual validity result ([`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001`](../TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md))
   - D5 OC result, if available (D5-INST-* reports)
   - Track F disposition ([`TRACK_F` §3](../TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md))
   - Track B / Track E status ([`TRACK_E_E2`](../TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md))
   - CalibrationSignal eligibility (E5 policy)
   - MMM readiness (approved intake vs blocked)
   - Blocking reason or next action

**Coverage rule:** The executive summary may **group** combinations for narrative clarity, but **no tuple may disappear** from Appendix A. Every known candidate tuple must map to exactly one disposition bucket:

| Disposition bucket | Meaning |
|--------------------|---------|
| `already_characterized` | COMBO + D5 OC complete; governed role defined |
| `characterized_restricted` | OC complete; restricted diagnostic only |
| `valid_candidate_pending_OC` | COMBO valid_candidate; battery not yet run |
| `invalid_by_interface` | Catalog / `impl.py` / runner blocks combo |
| `invalid_by_geometry` | Estimator asserts or geometry contract fails |
| `implemented_but_unvalidated` | Wired; probe failed or semantics unverified |
| `research_only` | R&D lane; no production instrument |
| `blocked` | Policy block (Track F BLOCK / permanent) |

**Verdict section (to complete at audit close):** `mmm_intake_blocked` | `mmm_intake_conditional` | `mmm_intake_approved_subset` — with explicit **approved MMM intake list** (expected: **empty or null_monitor-only** per E5) and **P0 gap list** for Track F.

---

## 1. Scope and non-goals

| In scope | Out of scope |
|----------|--------------|
| Reconcile 30 COMBO tuples → MMM / CalibrationSignal / Track B intake | Production code changes in this audit |
| Confirm zero silent tuple gaps vs COMBO + Track F + CV-001 | Estimator / inference implementation |
| Publish MMM block list + approved intake set (documentation) | TrustReport schema changes |
| Encode P0 hygiene gaps for post-audit Track F work | Promotion to MMM feed |

---

## 2. Executive summary (illustrative only)

> **Authoritative coverage:** Appendix A (30 rows). This table groups major evidence families; it does **not** replace per-tuple accounting.

| Evidence family | Governed role | CalibrationSignal | MMM readiness |
|-----------------|---------------|-------------------|---------------|
| **SCM + UnitJackKnife** | **Governed null-monitor only** (`null_monitor_only`) | **Eligible** (nominal registry) | **Not MMM lift** — null-monitor reference only |
| **SCM + Placebo (inference)** | **Diagnostic falsification** — estimator=SCM, inference=Placebo, single-treated only | neither | **Blocked** MMM |
| **AugSynthCVXPY + point / JK / KFold** | **Diagnostic / restricted comparator** | neither | **Blocked** MMM |
| **Class TBR + point / KFold** | **Restricted aggregate diagnostic only** (1×1 agg) | neither | **Blocked** MMM |
| **Class TBR + JKP** | **Callable; unverified / not governed** | neither | **Blocked** MMM |
| **Class TBR + UnitJackKnife** | **Blocked** on aggregate 1×1 (1 control row) | neither | **Blocked** |
| **TBRRidge + KFold / BRB** | **Restricted diagnostic** (unit + geo-power agg2) | neither | **Blocked** MMM |
| **TBRRidge + JK / Conformal / JKP / Bayesian** | **Implemented but unvalidated** or **BLOCK** prod (Bayesian) | neither | **Blocked** until TBRRIDGE-002 + hygiene |
| **BayesianTBR / TROP** | **Research-only** | neither | **Blocked** production |
| **DID + native bootstrap** | **Restricted** — cumulative ATT; DEF-003 CI policy | neither | **Blocked** MMM pending policy |
| **Multi-cell (all estimator × inference)** | **Per-cell only** — no pooling without `pooling_rule_id` | neither (pooled) | **Blocked** pooled; each cell follows Appendix A row for its geometry |

**Global gaps (Track F P0 — listed for close checklist):** `full_model` SCM/AugSynth guard · recovery_runner TBR→TBRRidge mislabel · registry `Bayesian` ≠ BayesianTBR MCMC · DID relative ATT CI policy · Placebo taxonomy · multi-cell pooling rule.

---

## Appendix A — Full 30-tuple disposition matrix (authoritative)

**Sources reconciled:** COMBO-AUDIT-001 (2026-06-02) · CONCEPTUAL-VALIDITY-001 · D5-INST OC chain · Track F §3 · Track E E2 cards · E5 CalibrationSignal policy.

**Row ID** = stable tuple key for AUDIT-010 traceability (matches Track F §3 order).

| ID | Primary bucket | Estimator / readout | Inference / falsification | Geometry | COMBO status | Conceptual validity | D5 OC status | Track E / B status | Track F disposition | CalibrationSignal | MMM readiness | Reason / next action |
|----|----------------|---------------------|---------------------------|----------|--------------|---------------------|--------------|-------------------|---------------------|-------------------|---------------|----------------------|
| A01 | `already_characterized` | AugSynthCVXPY | point_estimate | single_cell_unit | already_characterized | aligned_with_deviation | **AUGSYNTH-001** ✅ | INST-004 diagnostic | **HOLD** | neither | **blocked** | Diagnostic comparator; not MMM |
| A02 | `already_characterized` | AugSynthCVXPY | UnitJackKnife | single_cell_unit | already_characterized | aligned_with_deviation | **AUGSYNTH-001** ✅ | INST-004 diagnostic | **HOLD** | neither | **blocked** | JK null FPR 0 on battery; not CalibrationSignal |
| A03 | `characterized_restricted` | AugSynthCVXPY | Kfold | single_cell_unit | already_characterized | restricted | **AUGSYNTH-KFOLD-001** ✅ | INST-004 restricted | **HOLD** | neither | **blocked** | Restricted diagnostic; COMBO was valid_candidate |
| A04 | `invalid_by_interface` | AugSynthCVXPY | BlockResidualBootstrap | single_cell_unit | invalid_by_interface | n/a | not OC'd | — | **CLEAN-I** | neither | **blocked** | Not in `inference_support`; block or catalog ADR (F-OD-002) |
| A05 | `callable_unverified_interval_semantics` | AugSynthCVXPY | Conformal | single_cell_unit | valid_candidate | restricted | pending | — | **FIX** + OC | neither | **blocked** | D5-AUGSYNTH-003 ✅ — negative HW; 100% null exclude; not governed |
| A06 | `invalid_by_interface` | AugSynthCVXPY | Placebo | single_treated | invalid_by_interface | n/a | not OC'd | — | **BLOCK** | neither | **blocked** | Placebo inference not in AugSynth catalog |
| A07 | `characterized_restricted` | TBR (class) | point_estimate | aggregate_two_series | valid_candidate → OC | aggregate-only | **TBR-001** ✅ | INST-008 restricted | **HOLD** | neither | **blocked** | ~0.99 scale @ 8%; not MMM |
| A08 | `blocked` | TBR (class) | UnitJackKnife | aggregate_two_series | implemented_but_unvalidated | aggregate-only | **TBR-001** blocked | INST-008 | **BLOCK** | neither | **blocked** | 1 control row; geometry block |
| A09 | `implemented_but_unvalidated` | TBR (class) | JKP | aggregate_two_series | valid_candidate | aggregate-only | **TBR-001** unverified | INST-008 | **HOLD** unverified | neither | **blocked** | Callable; interval semantics not governed |
| A10 | `characterized_restricted` | TBR (class) | Kfold | aggregate_two_series | valid_candidate → OC | restricted | **TBR-001** ✅ | INST-008 restricted | **HOLD** | neither | **blocked** | Null FPR 0; restricted diagnostic |
| A11 | `invalid_by_interface` | TBR (class) | Placebo | aggregate_two_series | invalid_by_interface | n/a | blocked probe | — | **BLOCK** | neither | **blocked** | `run_placebo` blocks TBR class |
| A12 | `invalid_by_geometry` | TBR (class) | point_estimate | single_cell_unit | invalid_by_geometry | blocked unit | blocked assert | — | **BLOCK** | neither | **blocked** | Unit panel fails 1×1 assert |
| A13 | `already_characterized` | TBRRidge | Kfold | single_cell_unit | already_characterized | restricted | **TBRRIDGE-001** ✅ | INST-002 restricted | **HOLD** | neither | **blocked** | Unit scale ≠ SCM+JK |
| A14 | `already_characterized` | TBRRidge | BlockResidualBootstrap | single_cell_unit | already_characterized | restricted | **TBRRIDGE-001** ✅ | INST-003 restricted | **HOLD** | neither | **blocked** | Restricted diagnostic |
| A15 | `already_characterized` | TBRRidge | Kfold | aggregate_two_series | already_characterized | restricted | **TBRRIDGE-001** ✅ | INST-007 geo-power | **HOLD** | neither | **blocked** | Geo power path; not class TBR |
| A16 | `implemented_but_unvalidated` | TBRRidge | UnitJackKnife | single_cell_unit | implemented_but_unvalidated | restricted | probe failed | — | **FIX** TBRRIDGE-002 | neither | **blocked** | TBRRIDGE-002 OC |
| A17 | `invalid_by_interface` | TBRRidge | Placebo | single_treated | invalid_by_interface | n/a | probe failed | — | **BLOCK** | neither | **blocked** | Not SCM placebo-in-space |
| A18 | `implemented_but_unvalidated` | TBRRidge | Conformal | single_cell_unit | implemented_but_unvalidated | restricted | probe failed | — | **FIX** TBRRIDGE-002 | neither | **blocked** | Exchangeability review |
| A19 | `valid_candidate_pending_OC` | TBRRidge | TimeSeriesKfold | single_cell_unit | valid_candidate | restricted | pending | — | **FIX** TBRRIDGE-002 | neither | **blocked** | OC missing |
| A20 | `blocked` | TBRRidge | Bayesian (registry) | single_cell_unit | implemented_but_unvalidated | **BLOCK** prod | not governed | — | **BLOCK** prod | neither | **blocked** | INV-015 |
| A21 | `implemented_but_unvalidated` | TBRRidge | JKP | single_cell_unit | implemented_but_unvalidated | restricted | probe failed | — | **FIX** TBRRIDGE-002 | neither | **blocked** | JKP vs JK at ridge scale |
| A22 | `research_only` | BayesianTBR | Bayesian (registry) | single_cell_unit | research_only | research_only | R&D | — | **R&D** | neither | **blocked** | JAX ≠ paper MCMC |
| A23 | `invalid_by_interface` | BayesianTBR | mcmc_native | single_cell_unit | invalid_by_interface | research_only | R&D | — | **R&D** | neither | **blocked** | No registry mode |
| A24 | `research_only` | TROP | point_estimate | single_cell_unit | research_only | research_only | none | — | **R&D** | neither | **blocked** | No registry inference |
| A25 | `already_characterized` | DID | native_bootstrap | single_cell_unit | already_characterized | restricted | partial / DEF-003 | INST-005 restricted | **HOLD** + guard | neither | **blocked** | Relative ATT CI deferred |
| A26 | `already_characterized` | SCM | UnitJackKnife | single_cell_unit | already_characterized | aligned (caveats) | **001e** ✅ | INST-001 null_monitor | **HOLD** | **null_monitor_only** | **not MMM lift** | Only CS-eligible tuple |
| A27 | `already_characterized` | SCM | Placebo | single_treated | already_characterized | diagnostic | **PLACEBO-001** ✅ | INST-006 diagnostic | **HOLD** | neither | **blocked** | Falsification only |
| A28 | `blocked` | SCM | Placebo | multi_treated | already_characterized | blocked | **PLACEBO-001** 100% block | INST-006 blocked | **BLOCK** | neither | **blocked** | Multi-treated placebo invalid |
| A29 | `invalid_by_geometry` | SCM | UnitJackKnife | supergeo | invalid_by_geometry | blocked readout | **SUPERGEO-001** | GEO-003 char req | **BLOCK** | neither | **blocked** | Design-only |
| A30 | `invalid_by_geometry` | SCM | UnitJackKnife | trimmed | invalid_by_geometry | blocked readout | **TRIM-001** | GEO-004 char req | **BLOCK** | neither | **blocked** | Design-only |

### Appendix A — disposition bucket roll-up (closed)

| Bucket | Tuple IDs | Count |
|--------|-----------|------:|
| `already_characterized` | A01, A02, A13, A14, A15, A25, A26, A27 | 8 |
| `characterized_restricted` | A03, A07, A10 | 3 |
| `valid_candidate_pending_OC` | A05, A19 | 2 |
| `invalid_by_interface` | A04, A06, A11, A17, A23 | 5 |
| `invalid_by_geometry` | A12, A29, A30 | 3 |
| `implemented_but_unvalidated` | A09, A16, A18, A21 | 4 |
| `research_only` | A22, A24 | 2 |
| `blocked` | A08, A20, A28 | 3 |

**Total:** 30 tuples — each row has exactly one primary bucket.

---

## 3. AUDIT-010 checklist (executed at close)

| # | Check | Status |
|---|-------|--------|
| 1 | All 30 Appendix A rows reviewed; no missing tuple vs COMBO JSON | ✅ |
| 2 | Executive summary groups match Appendix A (no contradictions) | ✅ |
| 3 | CalibrationSignal intake = `SCM_UnitJackKnife` only (E5) | ✅ |
| 4 | MMM default ingress **blocked**; approved subset documented | ✅ |
| 5 | P0 hygiene gaps listed with owners (Track F §4) | ✅ |
| 6 | TBR ≠ TBRRidge documented in intake validator spec | ✅ |
| 7 | Multi-cell: per-cell only unless `pooling_rule_id` (global) | ✅ |
| 8 | Class TBR JKP marked **not governed** despite callable | ✅ |
| 9 | Placebo classified as inference/falsification, not estimator | ✅ |
| 10 | MIP registry + ROADMAP_V4 updated at close | ✅ |

---

## 4. Audit outcomes (closed)

| Outcome | Result |
|---------|--------|
| **Final verdict** | **`not_ready_continue_track_f`** |
| **MMM readiness** | **Not ready / blocked** — no default MMM ingress |
| **CalibrationSignal expansion** | **No** — `SCM_UnitJackKnife` null_monitor_only unchanged |
| **Approved MMM intake list** | **Empty** (null-monitor ≠ MMM lift) |
| **Promotion** | **Not authorized** |
| **Next lane** | **Track F P0 hygiene** → P2 OC |

**P0 gap list (Track F):** F-P0-001 `full_model` · F-P0-002 TBR label · F-P0-003 INV-015 · F-P0-004 DID CI · F-P0-005 Placebo taxonomy · F-P0-006 multi-cell pooling.

**Final verdict:** **`not_ready_continue_track_f`**

---

## 5. Traceability

| Artifact | Role in AUDIT-010 |
|----------|-------------------|
| [`D5_INST_COMBO_AUDIT_001_results.json`](../track_d/archives/D5_INST_COMBO_AUDIT_001_results.json) | COMBO status per tuple |
| [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001`](../TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md) | Literature / blocking deviations |
| [`TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001`](../TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md) | FIX/BLOCK/HOLD/R&D disposition |
| [`TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001`](../TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md) | INST-* cards |
| D5-INST-TBR-001 / AUGSYNTH-* / TBRRIDGE-001 / PLACEBO-001 / 001e | OC evidence columns |

---

*AUDIT-010 v1.0.0 closed — `not_ready_continue_track_f`; Appendix A authoritative (30 tuples); next: Track F P0.*
