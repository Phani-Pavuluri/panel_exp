# D5-INST-TBRRIDGE-003 — Post F-INF-002 targeted OC (A16, A18, A21)

**Artifact:** [`archives/D5_INST_TBRRIDGE_003_results.json`](archives/D5_INST_TBRRIDGE_003_results.json)  
**Harness:** [`panel_exp/validation/track_d_d5_inst_tbrridge_003.py`](../../panel_exp/validation/track_d_d5_inst_tbrridge_003.py)  
**Prerequisite:** F-INF-002 (`3993ba7`) pooled-counterfactual interface fix  
**Verdict:** **`remain_restricted_no_promotion`** — interface restored; mixed behavioral null-FPR; **not** governed uncertainty

---

## Scope

| Tuple | Estimator | Inference | Geometry | Prior battery |
|-------|-----------|-----------|----------|---------------|
| **A16** | TBRRidge | UnitJackKnife | 001e single-cell, multi-treated | D5-INST-TBRRIDGE-002 |
| **A18** | TBRRidge | Conformal | 001e single-cell, multi-treated | D5-INST-TBRRIDGE-002 |
| **A21** | TBRRidge | JKP | 001e single-cell, multi-treated | D5-INST-TBRRIDGE-002 |

Also includes a **single-treated** scm_low_signal probe (`n_mc=6`) for regression sanity. No other Appendix A rows. No promotion, MMM, or CalibrationSignal.

---

## Pre-fix vs post-fix (multi-treated null, n_mc=14)

| Metric | A16 pre (002) | A16 post | A18 pre | A18 post | A21 pre | A21 post |
|--------|---------------|----------|---------|----------|---------|----------|
| Feasibility | **0%** | **100%** | **0%** | **100%** | **0%** | **100%** |
| Failure class | interface_shape | — | interface_shape | — | interface_shape | — |
| Negative HW rate | n/a | **0%** | n/a | **0%** | n/a | **0%** |
| Inverted bound rate | n/a | **0%** | n/a | **0%** | n/a | **0%** |
| Null interval-exclusion FPR | n/a | **79%** | n/a | **0%** | n/a | **29%** |

**Interpretation:** F-INF-002 eliminated broadcast/interface failures (0% → 100% feasibility). Structural interval checks pass on all three modes. Behavioral null-FPR is **acceptable only for Conformal** on this battery; UnitJackKnife and JKP remain **callable but unverified**.

---

## Post-OC disposition

| Tuple | TBRRIDGE-003 disposition | AUDIT-010 after OC | Governed uncertainty |
|-------|--------------------------|--------------------|----------------------|
| **A16** | `callable_unverified_interval_semantics` | `callable_unverified_interval_semantics` | No |
| **A18** | `characterized_restricted` | `characterized_restricted` | No |
| **A21** | `callable_unverified_interval_semantics` | `callable_unverified_interval_semantics` | No |

**Safe outcome:** A18 is a **restricted diagnostic** (like A05/A19 post-POSTFIX). A16/A21 are structurally valid but **not** characterized — elevated null interval-exclusion on pooled readout.

---

## AUDIT-010 Appendix A updates

| Row | Prior (post F-INF-002) | Post TBRRIDGE-003 OC | D5 OC |
|-----|------------------------|----------------------|-------|
| **A16** | `callable_unverified_interval_semantics` | **`callable_unverified_interval_semantics`** (unchanged) | **TBRRIDGE-003** ✅ |
| **A18** | `callable_unverified_interval_semantics` | **`characterized_restricted`** | **TBRRIDGE-003** ✅ |
| **A21** | `callable_unverified_interval_semantics` | **`callable_unverified_interval_semantics`** (unchanged) | **TBRRIDGE-003** ✅ |

Roll-up: `blocked_interface` remains **0**. `characterized_restricted` gains **A18** (6 total with A03, A05, A07, A10, A19).

---

## Governance (unchanged)

- **Promotion:** not authorized  
- **CalibrationSignal:** `SCM_UnitJackKnife` only — unchanged  
- **MMM ingress:** blocked (`not_ready_continue_track_f`)  
- **Governed uncertainty:** none

---

## Findings

1. **D5-TBR003-FIND-001:** F-INF-002 restored feasibility (0% → 100%) for JK/JKP/Conformal on 001e multi-treated panels.
2. **D5-TBR003-FIND-002:** Conformal passes structural + null-FPR gates on this battery → **`characterized_restricted`** diagnostic only.
3. **D5-TBR003-FIND-003:** UnitJackKnife (79% null exclusion) and JKP (29%) remain **`callable_unverified_interval_semantics`** — do not promote or treat as governed uncertainty.

---

## Next authorized step

No further inference implementation until governance PR. Optional: deeper behavioral study for A16/A21 null-FPR under pooled-CF readout (research only).
