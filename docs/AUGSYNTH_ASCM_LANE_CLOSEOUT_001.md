# AUGSYNTH-ASCM-LANE-CLOSEOUT-001

**Document ID:** AUGSYNTH-ASCM-LANE-CLOSEOUT-001  
**Type:** Lane closeout / decision checkpoint — **not a new framework**  
**Status:** **complete** (docs-only)  
**Date:** 2026-06-03  
**Lane:** DL-1 AugSynth/ASCM active development (`AUGSYNTH-ASCM-DEVELOPMENT-ROADMAP-001` P1–P6)

**Decision:** **Lane closed** at planned P6 stop. **Next workstream:** open **`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001`** before any multi-cell OC or pooled readout work.

**Primary inputs:** [`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md) · [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md) · [`AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md`](AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md) · P1–P5 Track D reports · [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md) · [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md)

---

## 1. Purpose

Close the **AugSynth/ASCM P1–P6 development lane** selected by [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md) and executed under [`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md).

This memo:

1. Summarizes what P1–P6 **proved** and what remains **blocked**
2. Records the **current decision posture** (no promotion)
3. Compares candidate **next workstreams**
4. Chooses the **next branch of work** — a conceptual ADR, not another OC battery

**This is a decision checkpoint, not a new framework.** F-DECISION-001, AUDIT-010, ADR-001, and governed-uncertainty policy remain authoritative.

---

## 2. Evidence summary

| PR | Artifact | Type | Verdict | What it proved |
|----|----------|------|---------|----------------|
| **P1** | [`D5_DIAG_SCM_AUGSYNTH_001`](track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md) | code + tests | Diagnostics implemented | Reusable D5-DIAG fields (`scm_pre_rmse`, hull distance, weight concentration, scale bridge, disagreement, instrument flags) in [`scm_augsynth_diagnostics.py`](../panel_exp/validation/scm_augsynth_diagnostics.py); wired into validation harnesses; **no threshold finalization** |
| **P2** | [`AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001`](AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md) | audit doc | `fidelity_confirmed_with_caveats` | AugSynth/ASCM implementation matches intended algorithm **with documented gaps** (G4 SciPy vs CVXPY SCM leg, G7 level vs relative estimand, G8 hull proxy); ASCM-003 cleared to proceed |
| **P3** | [`D5_INST_AUGSYNTH_ASCM_003`](track_d/D5_INST_AUGSYNTH_ASCM_003_REPORT.md) | OC harness + archive | `promising_needs_inference_calibration` | 19-world stratified OC on `greedy_match_markets` unit panels; partial weak-fit MAE gains inside hull; outside-hull unreliable; D5-DIAG fields useful; **promotion audit not opened** |
| **P4** | [`D5_INF_AUGSYNTH_JK_CALIBRATION_001`](track_d/D5_INF_AUGSYNTH_JK_CALIBRATION_001_REPORT.md) | inference OC | `jk_unsafe_under_diagnostics` | AugSynth+UnitJackKnife callable but **not safe for promotion**; elevated null FPR on `W8_post_period_shock`; remains **diagnostic comparator only** |
| **P5** | [`D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001`](track_d/D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_REPORT.md) | failure analysis | `conformal_blocked_pending_new_design` | Primary failure is interval miscalibration/degeneracy (over-wide bands ~21–60× A26; mechanisms: band construction mismatch, residual exchangeability failure); **not governed uncertainty** |
| **P6** | [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md) | compatibility audit | `compatible_per_cell_only_pooling_blocked` + `bridge_required_before_broader_use` | Tier-1 geo methods structurally compatible for unit-panel **point diagnostics**; multi-cell **per-cell only**; aggregate/supergeo/trim require bridges; only **greedy** OC-validated for AugSynth |

**Lane outcome:** AugSynth point is **promising as a diagnostic comparator** on validated unit-panel geometry, but **inference calibration is unresolved**, **Conformal is blocked**, and **broader design/readout claims require ADRs before more OC**.

---

## 3. Current decision posture

| Topic | Posture |
|-------|---------|
| **AugSynth point** | **Promising diagnostic comparator** on unit-panel single-cell geometry (partial weak-fit gains in ASCM-003); not promoted |
| **AugSynth role** | **`diagnostic_comparator`** — unchanged; A26 remains governed null-monitor baseline |
| **AugSynth + UnitJackKnife** | **Diagnostic-only**; P4 found **unsafe diagnostic strata** (`W8_post_period_shock`); not governed uncertainty |
| **AugSynth + Conformal** | **Blocked** (`conformal_blocked_pending_new_design`); needs new interval design, not geometry-only fix |
| **Unit-panel single-cell / per-cell** | **Structurally valid** for diagnostic readout when donors ≥ 5 |
| **Pooled multi-cell claims** | **Blocked** without a governed pooling rule |
| **Aggregate (agg2/TBR), supergeo, trimmed designs** | **Require explicit bridge charters/ADRs** before AugSynth claims |
| **MMM / CalibrationSignal** | **No claim** from this lane — scale and estimand mismatch vs A26 |
| **TrustReport / F-DECISION** | **No change** |
| **Promotion audit** | **Not opened** |

---

## 4. Blockers

These blockers remain **after P1–P6**. None are resolved by running another OC immediately.

| Blocker ID | Description | Source |
|------------|-------------|--------|
| **BLK-INF-001** | Inference calibration unresolved — point promising but JK/Conformal not product-ready | P3 → P4/P5 chain |
| **BLK-JK-001** | JK unsafe under diagnostic strata (post-period shock) | P4 `jk_unsafe_under_diagnostics` |
| **BLK-CONF-001** | Conformal needs **new interval design** (construction + exchangeability) | P5 `conformal_blocked_pending_new_design` |
| **BLK-MCELL-001** | No governed **multi-cell pooling rule** | P6; `F-MCELL-001` not materialized |
| **BLK-EST-001** | **Estimand bridge unresolved** (level vs relative; aggregate vs unit) | P2 G7; P6 `AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001` |
| **BLK-GEO-001** | **Supergeo / trim bridges unresolved** | P6; separate geometry/population semantics |
| **BLK-OC-001** | Only **`greedy_match_markets`** OC-validated for AugSynth — other tier-1 geo methods structurally compatible but **not OC-validated** | P6 compatibility table |

---

## 5. Candidate next workstreams

| Candidate | Type | Addresses | Pros | Cons / defer reason |
|-----------|------|-----------|------|---------------------|
| **`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001`** | ADR | BLK-MCELL-001 | Unblocks meaningful multi-cell semantics before OC; P6 explicit prerequisite | Docs-only; no numeric OC yet |
| **`AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001`** | ADR | BLK-EST-001 | Closes level/relative and aggregate/unit gap (G7) | Does not fix inference |
| **`D5-INST-AUGSYNTH-MULTICELL-001`** | OC battery | Per-cell multi-cell characterization | Extends ASCM-003 depth to `n_test_grps>1` | **Premature without pooling ADR** — pooled claims still blocked; numbers without governed estimand |
| **`D5-INST-AUGSYNTH-DESIGN-COMPAT-001`** | OC battery | BLK-OC-001 | Validates non-greedy tier-1 geo on AugSynth path | Lower priority than pooling + estimand ADRs |
| **`SUPERGEO_AUGSYNTH_BRIDGE_CHARTER_001`** | charter | BLK-GEO-001 (supergeo) | Required before supergeo AugSynth claims | Niche until unit-panel lane stable |
| **`TRIMMED_DESIGN_AUGSYNTH_BRIDGE_CHARTER_001`** | charter | BLK-GEO-001 (trim) | Required before trimmed-match AugSynth claims | Same |
| **Pause AugSynth; move to another method lane** | lane switch | Foundation P2/P3 (TBR, design-readout, inference taxonomy) | Parallel non-blocking work exists | Leaves DL-1 mid-bridge; P6 already ordered next ADRs |

### Why not jump straight to `D5-INST-AUGSYNTH-MULTICELL-001`?

P6 found multi-cell is **per-cell only** and **pooled claims are blocked**. Running multi-cell OC before defining pooling semantics would produce **numbers without a governed estimand** — the same failure mode P6 guardrailed against. The clean next move is the **pooling ADR first**.

---

## 6. Recommended next step

**Open `MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001` first.**

**Reason:** P6 verdict `compatible_per_cell_only_pooling_blocked` makes multi-cell pooling the **conceptual prerequisite** for:

- any pooled multi-cell AugSynth readout claim
- meaningful design of `D5-INST-AUGSYNTH-MULTICELL-001`
- alignment with foundation lane `F-MCELL-001` / `POWER_READOUT_ALIGNMENT_ADR_001`

This ADR should define: per-cell estimand, allowed aggregation, null-monitor semantics, and explicit **block** conditions — **without** promotion or governed-uncertainty change.

---

## 7. Ordered next roadmap

Recommended sequence after this closeout:

| Order | Artifact | Rationale |
|-------|----------|-----------|
| **1** | **`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001`** | Prerequisite for multi-cell semantics (P6) |
| **2** | **`AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001`** | Level/relative + aggregate/unit (P2 G7, P6) |
| **3** | **`D5-INST-AUGSYNTH-MULTICELL-001`** | Per-cell multi-cell OC **after** pooling ADR scopes estimand |
| **4** | **`D5-INST-AUGSYNTH-DESIGN-COMPAT-001`** | OC parity for non-greedy tier-1 geo methods |
| **5** | **Decision checkpoint** | After ADRs + targeted OC: remain **diagnostic-only** vs open **Conformal repair lane** (separate inference design — not P5 rerun) |

**Deferred (parallel foundation, not DL-1 immediate):**

- `SUPERGEO_AUGSYNTH_BRIDGE_CHARTER_001` · `TRIMMED_DESIGN_AUGSYNTH_BRIDGE_CHARTER_001` — after unit-panel + multi-cell ADRs
- Foundation P2 `DESIGN_READOUT_COMPATIBILITY_AUDIT_001` (all readouts) — not duplicated here
- Promotion audit — **not opened**; exit criteria in development roadmap §7E still unmet

---

## 8. Guardrails

This closeout and all follow-on work must **not**:

- Promote AugSynth or change method roles
- Change F-DECISION-001 eligibility or TrustReport behavior
- Add AugSynth inference arms to governed-uncertainty allowlist
- Wire AugSynth into CalibrationSignal or MMM
- Integrate LLM layer (AUDIT-011 remains paused)
- Make **pooled multi-cell** AugSynth claims until `MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001` exists
- Launch **D5-INST-AUGSYNTH-MULTICELL-001** before pooling ADR

**Stop condition met:** Repo has a closeout memo for the AugSynth/ASCM P1–P6 lane and a clear next workstream decision.

---

## 9. Lane status

| Field | Value |
|-------|--------|
| **Lane** | DL-1 AugSynth/ASCM development |
| **Planned sequence** | P1–P6 ✅ **complete** |
| **Lane status** | **closed** at planned stop |
| **Next workstream** | **`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001`** |
| **Promotion** | **Not opened** |
