# Track E E1 — Suitability Diagnostic Inventory 001

**Document ID:** TRACK-E-E1-SUITABILITY-DIAGNOSTIC-INVENTORY-001  
**Type:** Governance contract (diagnostic inventory)  
**Status:** **complete** (documentation only)  
**Date:** 2026-06-01  
**Lane:** Research / governance bridge (pre-implementation E3–E7)  
**Baseline:** D5-POW-001a–e ✅ · DESIGN-INVENTORY-001 `e3e6aeb` · ROADMAP-DESIGN-READOUT-UPDATE-001 ✅ · D5-POW-001e `7f51446`

**Related:** [`TRACK_E_METHOD_SUITABILITY_AND_TRIANGULATION_001.md`](TRACK_E_METHOD_SUITABILITY_AND_TRIANGULATION_001.md) (E0) · [`TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md`](TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md) (E2) · [`ROADMAP_DESIGN_READOUT_UPDATE_001.md`](ROADMAP_DESIGN_READOUT_UPDATE_001.md) · Track D D5 archives

---

## 1. Purpose

E1 defines the **governed diagnostic inventory** used to assess whether a **design-method × geometry-mode × measurement-instrument** combination is suitable for a given claim class.

Diagnostics **inform** suitability; they **do not** auto-promote trust, MMM ingress, or lift detection.

### Canonical governance statements

| Statement | Meaning |
|-----------|---------|
| **SCM+JK is one card** | `SCM_UnitJackKnife` is the **reference null-monitor** instrument for fixed-window unit-level OC—not the whole platform. |
| **D5-POW-001e → Track E only** | 001e supplies **suitability evidence** for design × geometry under SCM+JK; it does **not** promote SCM+JK to MDE, lift detection, or MMM-ready evidence. |
| **Multi-cell per-cell** | Multi-cell geometry yields **per-cell** evidence only; **no pooled** null FPR or lift claim without a governed pooling rule (`E-DES-MCELL-011`). |
| **Separate semantics** | **supergeos** and **trimmedmatch** are **not ignored**; they require separate characterization (D5-DES-SUPERGEO-001, D5-DES-TRIM-001). |
| **Geo PowerAnalysis** | Remains **diagnostic / narrow planning** support on aggregated geometry—not governed readout MDE. |
| **MMM ingress** | **CalibrationSignal** is the **only** MMM ingress path. |
| **Trust** | **TrustReport** is the **only** trust-verdict layer. |

---

## 2. Suitability tensor

Every diagnostic evaluation is scoped to:

```
(design_method_id, geometry_mode, measurement_instrument_id) → diagnostic_results → suitability_status
```

| Layer | Examples |
|-------|----------|
| **Design method** | `greedy_match_markets`, `rerandomization_wrapper`, `completerandomization`, … |
| **Geometry mode** | `single_cell`, `multi_cell`, `supergeo`, `trimmed_population` |
| **Measurement instrument** | `SCM_UnitJackKnife`, `TBRRidge_Kfold`, geo `PowerAnalysis`, … |

**Status vocabulary (E2 cards):** `suitable` · `suitable_with_caveats` · `diagnostic_only` · `restricted` · `blocked` · `characterization_required`

---

## 3. Diagnostic families

### 3.1 E-DES-WIN — pre-period / window stability

**Purpose:** Ensure assignment and readout OC are evaluated on **fixed, documented** chronological windows—not circular sliding power windows alone.

| ID | Diagnostic | Measures | Typical failure | D5 / Track D evidence |
|----|------------|----------|-----------------|------------------------|
| E-DES-WIN-001 | Assignment stability across pre-period lengths | Jaccard overlap of treated set vs baseline window | Assignment is a strong function of pre length | D5-POW-001d (`assignment_jaccard_vs_baseline`) |
| E-DES-WIN-002 | Pre-balance stability across windows | Pre-period treated vs control KPI correlation | Balance degrades when pre shortens/lengthens | D5-POW-001d, 001e (`pre_period_balance_corr`) |
| E-DES-WIN-003 | Readout FPR stability across windows | SCM+JK null interval-exclusion FPR vs window grid | Null-monitor OC not portable across windows | D5-POW-001d (`null_fpr` by window) |
| E-DES-WIN-004 | Post-period length adequacy | Post length vs JK cell count / power proxy | Too few post periods for stable JK | D5-POW-001d grid |
| E-DES-WIN-005 | Fixed-window requirement for governed readout OC | Fixed experiment slice vs circular sliding sample | PowerAnalysis-style sliding ≠ SCM+JK readout | D5-POW-001d verdict **`fixed_window_preferred`** |

**Gate rule:** Governed SCM+JK suitability requires **E-DES-WIN-005 satisfied** (fixed pre/post documented on design spec).

---

### 3.2 E-SCM-DONOR — donor / control adequacy and sensitivity

**Purpose:** SCM+JK branch requires sufficient **control units as donors**; donor concentration and constraint feasibility affect null-monitor stability.

| ID | Diagnostic | Measures | Typical failure | D5 / Track D evidence |
|----|------------|----------|-----------------|------------------------|
| E-SCM-DONOR-001 | Minimum donor/control count | `n_control >= 2` for UnitJackKnife | JK infeasible (001c 2-row panel) | D5-POW-001c, 001e |
| E-SCM-DONOR-002 | Donor concentration / max donor weight | Weight concentration on few donors | Unstable JK / wide intervals | Track D D2 audit |
| E-SCM-DONOR-003 | Leave-one-donor-out stability | LOO point/interval shift | Single-donor dominance | D5-INF-002b post INV-D3-001 |
| E-SCM-DONOR-004 | Donor pool overlap with treated | Treated markets in donor pool incorrectly | Leakage / invalid counterfactual | D2 audit |
| E-SCM-DONOR-005 | Donor feasibility after constraints | Whitelist/blacklist leaves ≥2 controls | Assignment succeeds but readout blocked | Design inventory |
| E-SCM-DONOR-006 | Donor sensitivity by region/spend/channel | Constraint-induced donor pool shift | Regional bias in null monitor | Planned D5 follow-on |

**Gate rule:** SCM+JK **blocked** when E-SCM-DONOR-001 fails on unit-level panel.

---

### 3.3 E-DES-MCELL — multi-cell / shared-control geometry

**Purpose:** Multi-cell is a **geometry mode** (`n_test_grps > 1`), not a design method. Shared control must be diagnosed **per test cell**.

| ID | Diagnostic | Measures | Typical failure | D5 / Track D evidence |
|----|------------|----------|-----------------|------------------------|
| E-DES-MCELL-001 | Method supports `n_test_grps > 1` | Registry / assign API | Method single-cell only | DESIGN-INVENTORY-001 |
| E-DES-MCELL-002 | Requested cell-count feasibility | Assignment succeeds for requested k | Cannot fill k cells with constraints | 001e skip reasons |
| E-DES-MCELL-003 | Per-cell balance quality | Pre-balance corr per `test_i` | One cell poorly matched | D5-POW-001e per_cell |
| E-DES-MCELL-004 | Shared-control adequacy | Control count vs k × min controls heuristic | Control pool over-subscribed | 001e `shared_control_adequacy` |
| E-DES-MCELL-005 | Per-cell donor/control count | Donors = shared control only (exclude other test cells) | Other test cells in donor pool | 001e harness contract |
| E-DES-MCELL-006 | Per-cell UnitJackKnife feasibility | JK runs per cell | Cell empty or <2 donors | 001e per_cell |
| E-DES-MCELL-007 | Per-cell null FPR / null-monitor coverage | Interval-exclusion FPR; cell covers-zero rate | Elevated FPR one cell only | D5-POW-001e |
| E-DES-MCELL-008 | Treatment-cell conflict | Directional disagreement across cells at null | Cells disagree on drift sign | 001e `treatment_cell_conflict` |
| E-DES-MCELL-009 | Multiple-comparison warning | Any cell FPR above concern threshold | k cells inflate family-wise error | 001e flag |
| E-DES-MCELL-010 | Minimum viable controls per cell | Per-cell control adequacy | Cell cannot support JK | 001e |
| E-DES-MCELL-011 | No pooled multi-cell claim without governed pooling rule | Explicit ban on pooled multi-cell lift/null | Implied platform claim from pooled metric | Governance |
| E-DES-MCELL-012 | Recommended / maximum feasible cell count | Optimal k vs degradation | k too large degrades per-cell OC | **Characterized** — D5-MCELL-001 ✅ (k≤2 typical) |

**Gate rule:** Multi-cell **suitability_with_caveats** at best until E-DES-MCELL-012 characterized; **never** pool cells without rule.

---

### 3.4 E-DES-GEO — design geometry and assignment feasibility

**Purpose:** Separate **unit-level market assignment** from **aggregated / supergeo / trimmed** geometries.

| ID | Diagnostic | Measures | Typical failure | D5 / Track D evidence |
|----|------------|----------|-----------------|------------------------|
| E-DES-GEO-001 | Assignment output geometry | `dict[control, test_*]` unit lists | Wrong shape for readout | DESIGN-INVENTORY-001 |
| E-DES-GEO-002 | Unit-level vs aggregated panel | Row count preserved vs 2-row sum | 2-row breaks SCM+JK | D5-POW-001c **`narrow_diagnostics_only`** |
| E-DES-GEO-003 | Pre-period-only matching | `pre_treatment_period` honored in assign | Post-period leakage in matching | INV-D1-001 / D5-DES-001a |
| E-DES-GEO-004 | Constraint satisfaction | Whitelist/blacklist valid assignment | Infeasible assignment | assign.py validation |
| E-DES-GEO-005 | Rerandomization wrapper vs bare base | Null OC delta rerandom vs greedy | Wrapper materially changes null behavior | D5-POW-001e greedy vs wrapper |
| E-DES-GEO-006 | Supergeo cluster geometry | MILP / supergeo unit aggregation | Flat unit SCM+JK contract invalid | **Characterized** — D5-DES-SUPERGEO-001 ✅; Track E `characterization_required` |
| E-DES-GEO-007 | Trimmed population geometry | Pair trim / Tp–Te split | Estimand population shift | **Characterized** — D5-DES-TRIM-001 ✅; Track E `characterization_required` |
| E-DES-GEO-008 | Treatment probability / volume targets | Realized test share vs target | Severe imbalance | 001e balance metrics |

---

### 3.5 E-INST-OC — measurement-instrument operating characteristics

**Purpose:** Link each **measurement instrument** to archived D5 / Phase OC evidence. OC is **instrument-specific**—not transferable from SCM+JK to TBRRidge or geo power.

| ID | Diagnostic | Measures | Typical failure | D5 / Phase evidence |
|----|------------|----------|-----------------|---------------------|
| E-INST-OC-001 | Null-monitor interval semantics | Correct `effect_lo = y - y_upper` | Swapped endpoints → 100% FPR | D5-POW-001b **`null_monitor_only`** |
| E-INST-OC-002 | Interval-excludes-zero as detection | Pooled detection rate at null | Invalid power/MDE interpretation | 001b — **not** lift detection |
| E-INST-OC-003 | Design-method null FPR battery | Per-method × geometry null FPR | Method-specific anti-conservatism | D5-POW-001e |
| E-INST-OC-004 | Geo PowerAnalysis MDE vs SCM+JK | `mde_percent` vs JK detection MDE | Optimistic planning MDE | D5-POW-001a **`optimistic_proxy`** |
| E-INST-OC-005 | Aggregated-panel readout proxy | Unit vs 2-row sum readout | Magnitude / infeasibility mismatch | D5-POW-001c |
| E-INST-OC-006 | KFold geometry / multi-treated | Fold scope vs treated units | DEF-001 geometry failure | Track D D3 |
| E-INST-OC-007 | BRB null viability | Block bootstrap null behavior | DEF-002 | Track D D3 |
| E-INST-OC-008 | DID interval estimand | Cumulative vs relative ATT | DEF-003 compare error | Track D D3 |
| E-INST-OC-009 | Placebo band semantics | `placebo_band` ≠ CI | Lift compare invalid | Phase 15 |
| E-INST-OC-010 | AugSynth point / spillover | Point bias under spillover DGP | Phase 14 characterization | Phase 14 archive |
| E-INST-OC-011 | Evidence freshness / archive link | Committed JSON + doc ID | Stale or missing OC | MIP registry |

**Gate rule:** Instrument promotion beyond `diagnostic_only` requires **E-INST-OC-011** + instrument-specific OC row satisfied.

---

### 3.6 E-ESTIMAND — estimand alignment / incompatibility

**Purpose:** Prevent comparing or feeding MMM with mismatched **point path**, **interval target**, or **geometry scope**.

| ID | Diagnostic | Measures | Typical failure | Track B / D evidence |
|----|------------|----------|-----------------|----------------------|
| E-ESTIMAND-001 | Declared vs exported estimand | Registry ID match | Wrong estimand in export | EST registry |
| E-ESTIMAND-002 | Relative ATT post vs cumulative ATT | Interval scale | DID vs SCM compare | DEF-003 |
| E-ESTIMAND-003 | Pooled vs cell-mean path | Multi-treated aggregation mode | KFold/JK scope error | DEF-001 |
| E-ESTIMAND-004 | Placebo band vs confidence interval | `interval_semantics` | Treat placebo as CI | Phase 15 |
| E-ESTIMAND-005 | Point-only vs interval claims | `inference=none` | Interval claim without uncertainty | Catalog |
| E-ESTIMAND-006 | Geo power `mde_percent` vs relative ATT | Power contract bridge | MDE planning on wrong estimand | D4-FIND-003 |
| E-ESTIMAND-007 | Trimmed-match population estimand | Tp/Te target population | Population shift vs geo ATT | trimmedmatch card |

---

### 3.7 E-CONFLICT — method disagreement and classification

**Purpose:** Classify disagreements when multiple instruments run on the same test; **no naive averaging**.

| ID | Diagnostic | Maps to conflict class | Action |
|----|------------|------------------------|--------|
| E-CONFLICT-001 | Same estimand, noise-level point spread | `benign_disagreement` | Note in TrustReport |
| E-CONFLICT-002 | All intervals wide / underpowered | `power_disagreement` | `inconclusive` profile |
| E-CONFLICT-003 | Relative vs cumulative vs cell-mean | `estimand_disagreement` | **Block compare** |
| E-CONFLICT-004 | Single- vs multi-treated scope | `geometry_disagreement` | Partial export |
| E-CONFLICT-005 | Placebo vs CI semantics | `diagnostic_only_disagreement` | No lift compare |
| E-CONFLICT-006 | Outlier-driven split | `outlier_sensitive_disagreement` | Robustness flag |
| E-CONFLICT-007 | Pre-trend / break split | `trend_break_disagreement` | Design follow-up |
| E-CONFLICT-008 | Governed instruments opposite sign | `high_trust_directional_conflict` | Expert review |
| E-CONFLICT-009 | Incompatible estimand + opposite signs | `severe_conflict` | Exclude from MMM |

**Rule:** E-CONFLICT diagnostics feed **TrustReport only** until E4 fixtures exist; they do not change production composer in E1/E2.

---

### 3.8 E-MMM — CalibrationSignal / TrustReport / MMM eligibility

**Purpose:** Encode what may cross the **MMM boundary** vs remain diagnostic.

| ID | Diagnostic | Gate |
|----|------------|------|
| E-MMM-001 | Instrument governed + in catalog | Required for CalibrationSignal consideration |
| E-MMM-002 | Estimand + interval semantics match signal | Required |
| E-MMM-003 | D5 OC archived for instrument | Required for expansion beyond null_monitor |
| E-MMM-004 | Conflict rules pass (E-CONFLICT) | Required |
| E-MMM-005 | TrustReport role allows claim type | `null_monitor_only` → no lift in MMM |
| E-MMM-006 | Evidence freshness | Stale → `not_assessable` |
| E-MMM-007 | Direct Track D JSON feed forbidden | Must pass promotion bridge |
| E-MMM-008 | Averaging conflicting estimates forbidden | No governed rule → block |
| E-MMM-009 | Multi-cell pooled lift to MMM forbidden | Per E-DES-MCELL-011 |
| E-MMM-010 | Geo PowerAnalysis MDE to MMM forbidden | D5-POW-001a governance |

**Canonical:** Only **CalibrationSignal** may ingress MMM. **TrustReport** is the sole trust-verdict layer.

---

## 4. Diagnostic → D5 artifact map

| Artifact | Primary families | Verdict / use in E2 |
|----------|------------------|---------------------|
| [`D5_POW_001a_results.json`](track_d/archives/D5_POW_001a_results.json) | E-INST-OC-004, E-ESTIMAND-006 | `optimistic_proxy` — geo MDE not SCM MDE |
| [`D5_POW_001b_results.json`](track_d/archives/D5_POW_001b_results.json) | E-INST-OC-001–002 | `null_monitor_only` |
| [`D5_POW_001c_results.json`](track_d/archives/D5_POW_001c_results.json) | E-DES-GEO-002, E-INST-OC-005 | `narrow_diagnostics_only` |
| [`D5_POW_001d_results.json`](track_d/archives/D5_POW_001d_results.json) | E-DES-WIN-* | `fixed_window_preferred` |
| [`D5_POW_001e_results.json`](track_d/archives/D5_POW_001e_results.json) | E-DES-MCELL-*, E-DES-GEO-005, E-INST-OC-003 | `acceptable_with_caveats` (SCM+JK design×geometry) |
| [`DESIGN_INVENTORY_001_results.json`](track_d/archives/DESIGN_INVENTORY_001_results.json) | E-DES-GEO-001, E-DES-MCELL-001 | Code-grounded method list |

---

## 5. Severity and recording contract (E3 input)

| Severity | Meaning | Affects suitability |
|----------|---------|---------------------|
| **info** | Recorded; no gate | No |
| **warn** | Suitable with caveats | `suitable_with_caveats` |
| **fail** | Blocked or restricted | `restricted` / `blocked` |
| **unknown** | Not yet characterized | `characterization_required` |

Per-test diagnostic record (future E3 schema) must include: `diagnostic_id`, `family`, `severity`, `value`, `threshold`, `evidence_ref` (archive path + commit).

---

## 6. Non-goals (E1)

- No production code, estimator, inference, or design algorithm changes  
- No TrustReport composer changes  
- No Track B schema changes  
- No MMM feed or instrument promotion  
- No automatic suitability scoring ML (see E-OQ-1 in E0)

---

## 7. Sign-off

| Role | Statement |
|------|-----------|
| **E1** | Diagnostic inventory complete; links to D5 a–e |
| **E2** | Cards in [`TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md`](TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md) |
| **Next** | E3 triangulation schema · E4 TrustReport fixtures · D5-DES-SUPERGEO-001 / D5-DES-TRIM-001 |

---

*TRACK-E-E1-SUITABILITY-DIAGNOSTIC-INVENTORY-001 v1.0.0 — 2026-06-01*
