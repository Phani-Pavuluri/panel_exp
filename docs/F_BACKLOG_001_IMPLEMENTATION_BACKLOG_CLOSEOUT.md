# F-BACKLOG-001 — Implementation backlog closeout

**Document ID:** F-BACKLOG-001  
**Type:** Governance / planning closeout — **no implementation**  
**Status:** **complete**  
**Date:** 2026-06-03  
**Verdict:** Contract stack locked; **next authorized implementation = F-INF-003**

**Prerequisites:** AUDIT-010 ✅ (`not_ready_continue_track_f`) · Track F P0 ✅ · P2 closeout ✅ · **F-INF-001** ✅ · **F-GEO-001** ✅ · **F-CAT-001** ✅

**Related:** [`TRACK_F_P2_CLOSEOUT_001.md`](TRACK_F_P2_CLOSEOUT_001.md) · [`AUDIT-010_mmm_readiness_gap.md`](audits/AUDIT-010_mmm_readiness_gap.md) · [`F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md`](F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md) · [`F_GEO_001_GEOMETRY_ADAPTER_CONTRACT.md`](F_GEO_001_GEOMETRY_ADAPTER_CONTRACT.md) · [`F_CAT_001_REGISTRY_CATALOG_CLEANUP.md`](F_CAT_001_REGISTRY_CATALOG_CLEANUP.md)

---

## 1. Executive summary

The **governance contract stack** is complete. It prevents:

- Invalid or unverified intervals from being labeled governed uncertainty (F-INF-001)
- Unsupported geometry from being exported even when intervals look valid (F-GEO-001)
- Stale catalog/registry labels implying CalibrationSignal or MMM readiness (F-CAT-001)

**AUDIT-010** remains closed with **MMM ingress blocked** and **CalibrationSignal expansion not authorized** (`SCM_UnitJackKnife` null_monitor_only unchanged).

This document converts P2 OC, Appendix A (30 tuples), and contract findings into a **single prioritized implementation backlog**. It does **not** change estimators, inference paths, TrustReport, Track B schema, or run new OC.

| Layer | Status |
|-------|--------|
| P2 characterization | ✅ Closed |
| Contract stack (F-INF / F-GEO / F-CAT) | ✅ Complete |
| **F-BACKLOG-001** (this doc) | ✅ Complete |
| **Implementation** | **Authorized starting at F-INF-003 only** |

---

## 2. Execution order (binding)

```mermaid
flowchart LR
  CS[Contract stack complete] --> BL[F-BACKLOG-001 classified backlog]
  BL --> IMPL[Implementation fix authorized item]
  IMPL --> OC[D5 OC rerun only if item requires_OC_after_fix]
  OC --> CV[Conceptual validity review if scope changed]
  CV --> PROM[Promotion / MMM audit — not authorized today]
```

| Step | Rule |
|------|------|
| 1 | **Contract stack** (F-INF-001, F-GEO-001, F-CAT-001, F-BACKLOG-001) must be complete before any implementation fix. |
| 2 | **Implementation** runs only on items classified `fix_now` or `fix_later` in §4, in **§5 priority order**. |
| 3 | **No silent reclassification** — band/orientation fixes are implementation (F-INF-003), not catalog-only relabeling. |
| 4 | **OC rerun** only after an implementation fix that lists `requires_OC_after_fix` — **no new P2 batteries by default**. |
| 5 | **Promotion / MMM / CalibrationSignal** audit only after OC + conceptual validity pass — **none authorized** in current AUDIT-010 scope. |

---

## 3. Classification legend

| Tag | Meaning |
|-----|---------|
| `fix_now` | Next implementation lane — do after backlog lock |
| `fix_later` | Worth doing; not first — depends on product priority or prior fixes |
| `keep_blocked` | Policy/geometry/catalog block — do not implement export path |
| `research_only` | R&D estimators — no production path |
| `requires_design_ADR` | Needs design doc before code |
| `requires_OC_after_fix` | Schedule targeted D5 battery only after fix lands |
| `not_worth_fixing_now` | Explicitly deferred — cost/risk vs product need |

**Global (all lanes):** `keep_blocked` — MMM default ingress · CalibrationSignal expansion beyond `SCM_UnitJackKnife` · governed lift promotion · TrustReport rule changes without separate audit.

---

## 4. Prioritized backlog by lane

### 4.1 F-INF fixes

| ID | Item | AUDIT / source | Classification | Notes |
|----|------|----------------|----------------|-------|
| **F-INF-001** | Interval semantics **contract** | D3, P2, A05/A19 | ✅ complete | Classify only; allowlist empty |
| **F-INF-003** | **Band sign / interval orientation** for Conformal + TimeSeriesKfold | A05, A19; AUGSYNTH-003; TBRRIDGE-002 | ~~**`fix_now`**~~ ✅ · `requires_OC_after_fix` | [`F_INF_003_INTERVAL_ORIENTATION_FIX.md`](F_INF_003_INTERVAL_ORIENTATION_FIX.md) — structurally valid; OC pending |
| **F-INF-002** | TBRRidge multi-treated **pooled-CF readout** (JK, JKP, Conformal) | A16, A18, A21; TBRRIDGE-002 | ~~**`fix_later`**~~ ✅ · `requires_OC_after_fix` | [`F_INF_002_TBRRIDGE_INTERFACE_FIX.md`](F_INF_002_TBRRIDGE_INTERFACE_FIX.md) — struct valid; TBRRIDGE-003 OC pending |
| **F-INF-004** | TBR + JKP interval artifacts on aggregate 1×1 | A09; TBR-001 | `fix_later` · `requires_OC_after_fix` | Callable but unverified; may share orientation logic with F-INF-003 |
| **F-P0-004** | DID relative ATT CI policy **enforcement** (DEF-003) | A25; P0 guard | `fix_later` | Guard exists; full enforcement separate from band sign |

### 4.2 F-GEO adapters

| ID | Item | AUDIT / source | Classification | Notes |
|----|------|----------------|----------------|-------|
| **F-GEO-001** | Geometry adapter **contract** | COMBO, CV-001 | ✅ complete | Blocks before F-INF export |
| **F-GEO-002** | Class TBR **aggregate 1×1 adapter hardening** (n_treated/n_control asserts, export messaging) | A07, A12; TBR-001 | `fix_later` | Contract rules exist; runtime adapter messaging optional |
| **F-GEO-003** | **Supergeo** unit readout adapter (`supergeo_adapter_id`) | A29; SUPERGEO design lane | `requires_design_ADR` · `keep_blocked` | D5-DES-SUPERGEO characterization prerequisite |
| **F-GEO-004** | **Trimmed population** estimand bridge (`trim_estimand_bridge_id`) | A30; TRIM design lane | `requires_design_ADR` · `keep_blocked` | D5-DES-TRIM characterization prerequisite |
| — | TBR on unit_panel | A12 | `keep_blocked` | F-GEO-001 — aggregate-only class TBR |
| — | SCM+JK on supergeo/trim without bridge | A29, A30 | `keep_blocked` | No adapter → blocked export |
| — | Placebo multi-treated | A28 | `keep_blocked` | PLACEBO-001 geometry limit |

### 4.3 F-CAT / catalog follow-ups

| ID | Item | AUDIT / source | Classification | Notes |
|----|------|----------------|----------------|-------|
| **F-CAT-001** | Registry/catalog cleanup | COMBO, INV-015, Placebo taxonomy | ✅ complete | Metadata + `catalog_contract.py` |
| **F-CAT-002** | AugSynthCVXPY + **BRB** — explicit BLOCK vs add to `inference_support` | A04; F-OD-002 | `requires_design_ADR` | **Block** preferred until concept doc |
| **F-CAT-003** | Base AugSynth (non-CVXPY) quarantine / parity | P2 closeout §4.3 | `not_worth_fixing_now` | CVXPY path is characterized lane |
| — | Track B `signal_id` on non-SCM aliases | E5; F-CAT-001 overlay | `keep_blocked` | Adapter metadata only — not CS eligibility |
| — | Registry Bayesian vs BayesianTBR MCMC | A20, A22; INV-015 | `keep_blocked` (prod) | Catalog documents split; production block remains |

### 4.4 F-MCELL pooling-rule design

| ID | Item | Classification | Notes |
|----|------|----------------|-------|
| **F-MCELL-001** | `pooling_rule_id` schema + policy for **pooled multi-cell** claims | `requires_design_ADR` · `not_worth_fixing_now` | F-P0-006 + F-GEO block until product requires pooling |
| — | Per-cell multi-cell readout | `fix_later` (characterization) | D5-MCELL research lane — not implementation backlog P0 |

### 4.5 Research-only methods

| Item | Tuple | Classification | Notes |
|------|-------|----------------|-------|
| BayesianTBR native MCMC | A23 | `research_only` | No registry inference mode |
| BayesianTBR + registry Bayesian | A22 | `research_only` | JAX path ≠ paper NUTS |
| TROP point | A24 | `research_only` | No registry inference |
| Registry Bayesian on TBRRidge (prod) | A20 | `keep_blocked` | INV-015 production block |

### 4.6 Promotion-candidate prerequisites (not authorized)

| Prerequisite | Status | Classification |
|--------------|--------|----------------|
| F-INF-003 + targeted OC for A05/A19 | Not started | `requires_OC_after_fix` |
| F-INF-002 interface fix for A16/A18/A21 | ✅ complete (`3993ba7`) | — |
| D5-INST-TBRRIDGE-003 OC for A16/A18/A21 | ✅ complete | A18 → `characterized_restricted`; A16/A21 → `callable_unverified` |
| Conceptual validity re-review for promoted combo | Not scheduled | `fix_later` |
| AUDIT re-open for MMM readiness | Not authorized | `keep_blocked` |
| CalibrationSignal expansion | Not authorized | `keep_blocked` |
| Governed uncertainty allowlist non-empty | Not authorized | `keep_blocked` |

**Promotion verdict today:** **Not authorized** for any Appendix A tuple.

---

## 5. Implementation priority order (after this closeout)

| Rank | ID | Rationale |
|------|-----|-----------|
| ~~**1**~~ | ~~**F-INF-003**~~ ✅ | Orientation fix at source |
| ~~**2**~~ | ~~**D5-INF-POSTFIX-001**~~ ✅ | A05/A19 → `diagnostic_interval_only` / `characterized_restricted`; not governed |
| ~~**1**~~ | ~~**F-INF-002**~~ ✅ · ~~**D5-INST-TBRRIDGE-003**~~ ✅ | A18 characterized_restricted; A16/A21 callable unverified |
| — | **TRACK-F-IMPLEMENTATION-CHECKPOINT-001** | ✅ Pause default; see [`TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md`](TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md) |
| (optional) | **F-INF-004** / TBR JKP | A09 aggregate 1×1 — **not** default queue |
| 4 | F-GEO-002 | Hardening only — contract already blocks wrong geometry |
| 5 | F-P0-004 | DID CI policy — parallel policy lane |
| 6 | F-CAT-002 | ADR-only — no code until decision |
| — | F-MCELL-001, F-GEO-003, F-GEO-004 | Design lanes — **not** implementation queue |

**Do not start** F-INF-002, F-GEO adapter implementation, or new OC **before** F-INF-003 unless an explicit governance PR reprioritizes (this doc is the default authority).

---

## 6. Appendix A quick map (implementation vs hold)

| Bucket | IDs | Backlog action |
|--------|-----|----------------|
| `callable_unverified_interval_semantics` | A16, A21 | **TBRRIDGE-003** ✅ |
| `characterized_restricted` | A03, A05, A07, A10, A18, A19 | **F-INF-003** + POSTFIX / **TBRRIDGE-003** ✅ |
| `implemented_but_unvalidated` | A09 | **F-INF-004** / shared orientation — optional OC |
| `invalid_by_geometry` | A12, A29, A30 | **keep_blocked** / design ADR |
| `invalid_by_interface` | A04, A06, A11, A17, A23 | **keep_blocked** or F-CAT-002 ADR (A04 only) |
| `blocked` | A08, A20, A28 | **keep_blocked** |
| `research_only` | A22, A24 | **research_only** |
| `already_characterized` / `characterized_restricted` | A01–A03, A07, A10, A13–A15, A25–A27 | **HOLD** — no promotion |

Full rows: [`AUDIT-010` Appendix A](audits/AUDIT-010_mmm_readiness_gap.md).

---

## 7. OC schedule (after implementation only)

| Fix | Reopen battery (if fix lands) | Tuple |
|-----|------------------------------|-------|
| F-INF-003 | D5 targeted rerun (Conformal / TimeSeriesKfold semantics) | A05, A19 |
| F-INF-002 | D5-INST-TBRRIDGE-003 or equivalent | A16, A18, A21 |
| F-INF-004 | Optional TBR JKP semantics spot-check | A09 |

**Default:** No new P2-scale batteries until a fix moves a row from `callable_unverified` or `blocked_interface` to a candidate state.

---

## 8. Stop condition (met)

| Criterion | Status |
|-----------|--------|
| Backlog classified across F-INF / F-GEO / F-CAT / F-MCELL / R&D / promotion | ✅ |
| P3+ execution order complete (F-INF-003 → POSTFIX → F-INF-002 → TBRRIDGE-003) | ✅ |
| Implementation checkpoint published | ✅ **TRACK-F-IMPLEMENTATION-CHECKPOINT-001** |
| MMM / CalibrationSignal / promotion remain blocked | ✅ |
| Governed uncertainty allowlist empty | ✅ |

---

## 9. Next authorized task (explicit)

~~**F-INF-003**~~ ✅ · ~~**D5-INF-POSTFIX-001**~~ ✅ · ~~**F-INF-002**~~ ✅ · ~~**D5-INST-TBRRIDGE-003**~~ ✅.

**Default:** **Pause** — see [`TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md`](TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md). Await **governance PR** before reopening impl/OC.

**Optional (product pull only):** **F-INF-004** (A09 TBR JKP). **Design ADR:** F-GEO-003/004, F-MCELL-001, F-CAT-002. Promotion/MMM/CS still blocked.

---

*F-BACKLOG-001 v1.2.0 — P3+ loop closed at TRACK-F-IMPLEMENTATION-CHECKPOINT-001; pause default.*
