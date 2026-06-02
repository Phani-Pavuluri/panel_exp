# Track E E2 — Method & Design Suitability Cards 001

**Document ID:** TRACK-E-E2-METHOD-DESIGN-SUITABILITY-CARDS-001  
**Type:** Governance contract (suitability cards)  
**Status:** **complete** (documentation only)  
**Date:** 2026-06-01  
**Lane:** Research / governance bridge  
**Diagnostic inventory:** [`TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md`](TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md)

**Related:** [`TRACK_E_METHOD_SUITABILITY_AND_TRIANGULATION_001.md`](TRACK_E_METHOD_SUITABILITY_AND_TRIANGULATION_001.md) · [`TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`](TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md) · [`TRACK_D_DESIGN_METHOD_INVENTORY_001.md`](TRACK_D_DESIGN_METHOD_INVENTORY_001.md)

---

## 1. Canonical governance (read first)

| Rule | Statement |
|------|-----------|
| **SCM+JK scope** | **One reference null-monitor card** — not the universal GeoX readout, platform MDE, lift detection, or MMM-ready lift evidence. |
| **D5-POW-001e** | Supplies **Track E suitability evidence only** for design × geometry under SCM+JK; overall **`acceptable_with_caveats`** on `scm_low_signal` battery (n=28). |
| **Multi-cell** | **Per-cell** evidence only; **no pooled** null or lift claim without governed pooling rule. |
| **supergeos / trimmedmatch** | **Not ignored** — `characterization_required` on separate semantics paths. |
| **Geo PowerAnalysis** | **Diagnostic / narrow planning** — not governed readout MDE ([D5-POW-001a](track_d/archives/D5_POW_001a_results.json)). |
| **MMM** | **CalibrationSignal** = only MMM ingress. |
| **Trust** | **TrustReport** = only trust-verdict layer. |

### Card template fields

Each card includes: **purpose** · **compatible design geometry** · **compatible measurement instruments** · **incompatible / blocked** · **required diagnostics** · **OC evidence** · **known restrictions** · **allowed claims** · **disallowed claims** · **Track B / CalibrationSignal** · **Track E status**

### Status vocabulary

| Status | Meaning |
|--------|---------|
| `suitable` | May support governed claim class with diagnostics passing |
| `suitable_with_caveats` | Usable with documented limits (most SCM+JK design×geometry today) |
| `diagnostic_only` | TrustReport / research only; no MMM lift |
| `restricted` | Runnable; not decision-grade / not calibration-eligible |
| `blocked` | Do not use for governed claims on this geometry |
| `characterization_required` | In roadmap; OC not complete for this tensor slice |

---

## Part A — Geometry mode cards

### GEO-001 — `single_cell` geometry

| Field | Value |
|-------|--------|
| **Purpose** | One test arm (`test_0`) vs shared control (`n_test_grps = 1`). |
| **Compatible design geometry** | Unit-level `dict[control, test_0]` from tier-1 geo methods. |
| **Compatible measurement instruments** | `SCM_UnitJackKnife` (reference null-monitor); others per instrument cards with own OC. |
| **Incompatible / blocked** | 2-row aggregated geo power panel as **governed** SCM readout ([001c](track_d/archives/D5_POW_001c_results.json)). |
| **Required diagnostics** | E-DES-WIN-005; E-SCM-DONOR-001; E-DES-GEO-001–003; E-INST-OC-003 (per design method). |
| **OC evidence** | D5-POW-001e all six methods **acceptable** single_cell. |
| **Known restrictions** | Fixed pre/post windows required for governed SCM+JK OC (001d). |
| **Allowed claims** | Null-monitor interval semantics; per-method suitability input to TrustReport. |
| **Disallowed claims** | Platform MDE; lift detection; MMM lift without CalibrationSignal governance. |
| **Track B / CalibrationSignal** | SCM+JK: `null_monitor_only` calibration-eligible when instrument card passes. |
| **Track E status** | **`suitable_with_caveats`** (under SCM+JK reference branch) |

---

### GEO-002 — `multi_cell` geometry

| Field | Value |
|-------|--------|
| **Purpose** | Multiple concurrent test cells (`test_0`…`test_{k-1}`) vs **one shared control** (`n_test_grps > 1`). |
| **Compatible design geometry** | Same tier-1 assign APIs with `n_test_grps > 1`; readout uses **control-only donors per cell** (exclude other test cells). |
| **Compatible measurement instruments** | `SCM_UnitJackKnife` per-cell only (001e contract). |
| **Incompatible / blocked** | Pooled multi-cell SCM+JK null FPR or lift; supergeo without D5-DES-SUPERGEO-001. |
| **Required diagnostics** | E-DES-MCELL-001–012 (especially 004–007, 011); E-SCM-DONOR-001 per cell. |
| **OC evidence** | D5-POW-001e + **D5-MCELL-001** ✅ [`D5_MCELL_001_results.json`](track_d/archives/D5_MCELL_001_results.json): k≤2 typical; k≥3 degrades; `thinningdesign` test_1 slightly elevated at k=2. |
| **Known restrictions** | Multiple-comparison risk; shared-control stress when k≥3; conservative k≤1 if all methods required. |
| **Allowed claims** | Per-cell null-monitor; per-cell balance/donor diagnostics to TrustReport. |
| **Disallowed claims** | Pooled multi-cell lift; single headline FPR across cells; MMM pooled cell evidence. |
| **Track B / CalibrationSignal** | Per-cell signals only if future policy defines cell-level CalibrationSignal keys (not default today). |
| **Track E status** | **`suitable_with_caveats`** |

---

### GEO-003 — `supergeo` geometry

| Field | Value |
|-------|--------|
| **Purpose** | Supergeo clusters / MILP pairing — distinct unit geometry from flat markets. |
| **Compatible design geometry** | `SupergeoModel` / registry `supergeos`. |
| **Compatible measurement instruments** | **None** for flat unit-level SCM+JK contract until D5-DES-SUPERGEO-001. |
| **Incompatible / blocked** | SCM+JK on flat unit dict assumed by 001e; standard geo tier-1 cards without supergeo OC. |
| **Required diagnostics** | E-DES-GEO-006; full E-DES-GEO + E-INST-OC battery on supergeo panel. |
| **OC evidence** | DESIGN-INVENTORY-001; **D5-DES-SUPERGEO-001** ✅ [`D5_DES_SUPERGEO_001_results.json`](track_d/archives/D5_DES_SUPERGEO_001_results.json); excluded from D5-POW-001e. |
| **Known restrictions** | Separate geometry semantics; MILP pair output (not control/test dict); MILP scope mismatch (largest cluster only). |
| **Allowed claims** | None governed — flat market SCM+JK blocked; supergeo-unit readout uncharacterized. |
| **Disallowed claims** | Any claim transferring tier-1 001e results to supergeo tests. |
| **Track B / CalibrationSignal** | No ingress. |
| **Track E status** | **`characterization_required`** (`separate_geometry_design`) |

---

### GEO-004 — `trimmed_population` geometry

| Field | Value |
|-------|--------|
| **Purpose** | TrimmedMatchDesign — pair trimming, Tp/Te split; may shift target population / estimand. |
| **Compatible design geometry** | `TrimmedMatchDesign` / registry `trimmedmatch`. |
| **Compatible measurement instruments** | Native pair-lift CI (**diagnostic only**); no governed SCM+JK. |
| **Incompatible / blocked** | Standard geo ATT cards without population bridge; SCM+JK 001e tensor. |
| **Required diagnostics** | E-DES-GEO-007; E-ESTIMAND-007. |
| **OC evidence** | DESIGN-INVENTORY-001; **D5-DES-TRIM-001** ✅ [`D5_DES_TRIM_001_results.json`](track_d/archives/D5_DES_TRIM_001_results.json); excluded from 001e. |
| **Known restrictions** | Tp/Te split; pair trim; **severe target-population shift** on battery; classical pair power. |
| **Allowed claims** | Diagnostic-only — `power_analysis_with_cross_validation` on retained pairs. |
| **Disallowed claims** | MMM geo relative ATT without estimand bridge. |
| **Track B / CalibrationSignal** | No ingress. |
| **Track E status** | **`characterization_required`** (`separate_population_design`) |

---

## Part B — Design method cards (tier-1 geo + wrapper)

*All tier-1 cards below share: unit-level assignment, fixed-window SCM+JK OC from 001e, pre-period `TimePeriod(0, train_length-1)` where applicable. **Track E status** for SCM+JK null-monitor tensor: **`suitable_with_caveats`** unless noted.*

### DES-001 — `greedy_match_markets`

| Field | Value |
|-------|--------|
| **Purpose** | Production default base randomizer; greedy pre-period correlation matching. |
| **Compatible design geometry** | `single_cell`, `multi_cell` (`n_test_grps`). |
| **Compatible measurement instruments** | `SCM_UnitJackKnife` (001e ✅); geo `PowerAnalysis` diagnostic on agg panel only. |
| **Incompatible / blocked** | Governed SCM+JK on 2-row sum panel; supergeo flat mapping. |
| **Required diagnostics** | E-DES-WIN-*; E-SCM-DONOR-*; E-DES-GEO-003; E-DES-MCELL-* if multi_cell; E-INST-OC-003. |
| **OC evidence** | 001e single_cell + multi_cell **acceptable**; 001c/d baseline; 001a–b readout semantics. |
| **Known restrictions** | Bare greedy vs rerandomization wrapper compared in 001e (Δ FPR 0 on battery). |
| **Allowed claims** | Null-monitor suitability evidence; design quality diagnostics. |
| **Disallowed claims** | MDE; lift detection; MMM-ready without CalibrationSignal. |
| **Track B / CalibrationSignal** | Indirect via instrument + evidence; design method not a CalibrationSignal key. |
| **Track E status** | **`suitable_with_caveats`** |

---

### DES-002 — `rerandomization_wrapper`

| Field | Value |
|-------|--------|
| **Purpose** | Production `GeoExperimentDesign.create_design()` path: `Rerandomization(base_randomizer_cls=greedy_match_markets)`. |
| **Compatible design geometry** | `single_cell`, `multi_cell`. |
| **Compatible measurement instruments** | Same as DES-001 for SCM+JK. |
| **Incompatible / blocked** | Same as DES-001. |
| **Required diagnostics** | E-DES-GEO-005 + DES-001 set. |
| **OC evidence** | 001e **acceptable**; greedy vs wrapper **identical** null FPR on `scm_low_signal` battery. |
| **Known restrictions** | Not a registry row; always interpreted with declared base. |
| **Allowed / disallowed claims** | Same as DES-001. |
| **Track B / CalibrationSignal** | Same as DES-001. |
| **Track E status** | **`suitable_with_caveats`** |

---

### DES-003 — `completerandomization`

| Field | Value |
|-------|--------|
| **Purpose** | Bernoulli complete randomization with constraint enforcement. |
| **Compatible design geometry** | `single_cell`, `multi_cell`. |
| **Compatible measurement instruments** | `SCM_UnitJackKnife` (001e ✅). |
| **Incompatible / blocked** | 2-row governed SCM+JK; supergeo/trimmed without OC. |
| **Required diagnostics** | E-DES-GEO-004; E-INST-OC-003; E-DES-MCELL-* if multi_cell. |
| **OC evidence** | 001e **acceptable** both geometries. |
| **Known restrictions** | No pre-period-only matching in base assign (imbalance via rerandomization wrapper in production). |
| **Track E status** | **`suitable_with_caveats`** |

---

### DES-004 — `balancedrandomization`

| Field | Value |
|-------|--------|
| **Purpose** | KPI volume-share balancing across arms. |
| **Compatible design geometry** | `single_cell`, `multi_cell`. |
| **Compatible measurement instruments** | `SCM_UnitJackKnife` (001e ✅). |
| **OC evidence** | 001e **acceptable** both geometries. |
| **Required diagnostics** | DES-003 set + E-DES-GEO-008. |
| **Track E status** | **`suitable_with_caveats`** |

---

### DES-005 — `stratifiedrandomization`

| Field | Value |
|-------|--------|
| **Purpose** | Percentile strata + volume balancing within strata. |
| **Compatible design geometry** | `single_cell`, `multi_cell`. |
| **Compatible measurement instruments** | `SCM_UnitJackKnife` (001e ✅). |
| **OC evidence** | 001e **acceptable** both geometries. |
| **Track E status** | **`suitable_with_caveats`** |

---

### DES-006 — `thinningdesign`

| Field | Value |
|-------|--------|
| **Purpose** | Kernel thinning design (ThinningDesign). |
| **Compatible design geometry** | `single_cell`, `multi_cell`. |
| **Compatible measurement instruments** | `SCM_UnitJackKnife` (001e ✅). |
| **OC evidence** | 001e **acceptable**; multi_cell `test_1` slightly higher mean null FPR (~3.6%) vs 0% other cells/methods. |
| **Known restrictions** | Watch E-DES-MCELL-007 / 009 for multi_cell. |
| **Track E status** | **`suitable_with_caveats`** (multi_cell: monitor per-cell FPR) |

---

## Part C — Measurement instrument cards

### INST-001 — `SCM_UnitJackKnife` (SCM + Unit Jackknife)

| Field | Value |
|-------|--------|
| **Purpose** | **Reference null-monitor** for fixed-window unit-level design×geometry OC — **not** platform readout. |
| **Compatible design geometry** | `single_cell`, `multi_cell` (per-cell); unit-level markets only. |
| **Compatible design methods** | Six confirmed tier-1 methods (001e); not supergeo/trimmed without separate OC. |
| **Incompatible / blocked** | 2-row aggregated panel; interval-excludes-zero as power/MDE; pooled multi_cell claims. |
| **Required diagnostics** | E-DES-WIN-005; E-SCM-DONOR-001–005; E-INST-OC-001–003; E-DES-MCELL-* if multi_cell; E-MMM-005. |
| **OC evidence** | 001b `null_monitor_only`; 001d `fixed_window_preferred`; 001e `acceptable_with_caveats`; INV-D3-001 fix. |
| **Known restrictions** | Cell coverage ~63% null monitor on 001e battery; not lift detection. |
| **Allowed claims** | Null-monitor interval exclusion; cell covers-zero rate; suitability input to TrustReport. |
| **Disallowed claims** | MDE planning; lift detection; MMM causal lift; platform-wide power module. |
| **Track B / CalibrationSignal** | **`null_monitor_only`** — calibration-eligible for null-monitor role only. |
| **Track E status** | **`suitable_with_caveats`** |

---

### INST-002 — `TBRRidge_Kfold` (TBRRidge + KFold)

| Field | Value |
|-------|--------|
| **Purpose** | Geo default readout path on aggregated panel; seasonal panels. |
| **Compatible design geometry** | Aggregated 2-row / geo power panel; multi_treated with geometry fix validation. |
| **Compatible design methods** | Geo orchestrator default; **not** interchangeable with unit SCM+JK 001e tensor. |
| **Incompatible / blocked** | Governed compare to SCM+JK relative ATT CI without estimand bridge; multi-treated pre-fix geometry. |
| **Required diagnostics** | E-INST-OC-006; E-ESTIMAND-003; DEF-001. |
| **OC evidence** | 001c: point correlation high but ~12× magnitude vs unit SCM; Track D D3. |
| **Allowed claims** | Diagnostic / exploratory; TrustReport restricted role. |
| **Disallowed claims** | CalibrationSignal; MMM; primary null-monitor for unit geo tests. |
| **Track B / CalibrationSignal** | **Excluded**. |
| **Track E status** | **`restricted`** |

---

### INST-003 — `TBRRidge_BlockResidualBootstrap` (TBRRidge + BRB)

| Field | Value |
|-------|--------|
| **Purpose** | Block residual bootstrap uncertainty on TBR path. |
| **Compatible design geometry** | Geo aggregated / multi_treated per DEF-002 scope. |
| **Required diagnostics** | E-INST-OC-007; DEF-002. |
| **OC evidence** | Track D D3; Phase 12 characterization tiers. |
| **Allowed claims** | Null-viability characterization tier only. |
| **Disallowed claims** | CalibrationSignal; governed lift without separate D5 promotion. |
| **Track E status** | **`restricted`** |

---

### INST-004 — `AugSynthCVXPY_Point` / AugSynth JK

| Field | Value |
|-------|--------|
| **Purpose** | Augmented synthetic control point path; JK mirrors SCM conservatism when available. |
| **Compatible design geometry** | Unit panels per Phase 14 scope; spillover-sensitive DGPs risky. |
| **Required diagnostics** | E-INST-OC-010; Phase 14 archive. |
| **OC evidence** | Phase 14 characterization — point bias under spillover. |
| **Allowed claims** | Point triangulation diagnostic only (point card). |
| **Disallowed claims** | CalibrationSignal for JK without separate instrument OC. |
| **Track E status** | Point: **`diagnostic_only`**; JK: **`characterization_required`** |

---

### INST-005 — `DID_Bootstrap` (DID + bootstrap)

| Field | Value |
|-------|--------|
| **Purpose** | Panel DID with bootstrap intervals. |
| **Compatible design geometry** | Panel DID structure; parallel trends assumed. |
| **Incompatible / blocked** | Relative ATT post CI claims (DEF-003 cumulative intervals). |
| **Required diagnostics** | E-INST-OC-008; E-ESTIMAND-002. |
| **Allowed claims** | Point directional diagnostic on relative path if declared. |
| **Disallowed claims** | Interval compare to SCM relative ATT; CalibrationSignal. |
| **Track E status** | **`restricted`** |

---

### INST-006 — `SCM_Placebo` (SCM + Placebo)

| Field | Value |
|-------|--------|
| **Purpose** | Placebo-band null reference — **not** a confidence interval. |
| **Compatible design geometry** | **`single_treated_only`** — multi-treated default blocked. |
| **Required diagnostics** | E-INST-OC-009; E-ESTIMAND-004; E-CONFLICT-005. |
| **OC evidence** | Phase 15 (single-treated); geometry matrix. |
| **Allowed claims** | Null-reference diagnostic; TrustReport diagnostic role. |
| **Disallowed claims** | Lift detection; CalibrationSignal without single-treated OC. |
| **Track E status** | **`diagnostic_only`** (single-treated); **`blocked`** (multi-treated default) |

---

### INST-007 — Geo `PowerAnalysis` (diagnostic path)

| Field | Value |
|-------|--------|
| **Purpose** | Simulation-coverage MDE / power on **aggregated** geo panel — planning diagnostic. |
| **Compatible design geometry** | 2-row treated/control sum; circular sliding windows in product (not SCM+JK readout). |
| **Compatible design methods** | GeoExperimentDesign orchestration — not unit SCM tensor. |
| **Incompatible / blocked** | Governed SCM+JK MDE; MMM planning feed ([001a](track_d/archives/D5_POW_001a_results.json)). |
| **Required diagnostics** | E-INST-OC-004–005; E-ESTIMAND-006; E-MMM-010. |
| **OC evidence** | 001a **`optimistic_proxy`** (~1.5% geo vs ~4% SCM detection MDE); 001c geometry loss. |
| **Allowed claims** | Narrow planning diagnostic; AA calibration helper (not production gate). |
| **Disallowed claims** | Governed readout MDE; SCM feasibility; MMM CalibrationSignal. |
| **Track B / CalibrationSignal** | **Excluded** from MMM. |
| **Track E status** | **`diagnostic_only`** |

---

## Part D — Combination matrix (quick reference)

**Legend:** ✅ = suitable_with_caveats (SCM+JK null-monitor) · ⚠️ = diagnostic_only / restricted · ⛔ = blocked / characterization_required · — = not evaluated

### Design method × geometry × SCM_UnitJackKnife

| Design method | single_cell | multi_cell |
|---------------|-------------|------------|
| greedy_match_markets | ✅ | ✅ |
| rerandomization_wrapper | ✅ | ✅ |
| completerandomization | ✅ | ✅ |
| balancedrandomization | ✅ | ✅ |
| stratifiedrandomization | ✅ | ✅ |
| thinningdesign | ✅ | ✅ (monitor test_1 FPR) |
| supergeos | ⛔ | ⛔ |
| trimmedmatch | ⛔ | ⛔ |

### Measurement instrument × MMM / Trust

| Instrument | TrustReport | CalibrationSignal / MMM |
|------------|-------------|---------------------------|
| SCM_UnitJackKnife | null_monitor | Eligible **null_monitor_only** |
| SCM_Placebo | diagnostic | Excluded |
| TBRRidge_Kfold | restricted | Excluded |
| TBRRidge_BRB | restricted | Excluded |
| DID_Bootstrap | restricted | Excluded |
| AugSynth point | diagnostic | Excluded |
| Geo PowerAnalysis | diagnostic | **Forbidden** (E-MMM-010) |

---

## Part E — Decision rules (E3+ input)

1. **Suitability** for a production geo test requires passing **all required diagnostics** for the `(design, geometry, instrument)` tuple.  
2. **SCM+JK + tier-1 design + single_cell/multi_cell** → `suitable_with_caveats` for **null-monitor evidence only** (001e).  
3. **Lift / MMM** requires instrument card ≠ `diagnostic_only` / `restricted`, plus E-MMM-* gates and TrustReport alignment.  
4. **Triangulation** across instruments uses E-CONFLICT-* — no averaging.  
5. **Promotion** of any instrument beyond current status requires **new D5 OC** — E2 does not promote.

---

## Part F — Sign-off

| Deliverable | Status |
|-------------|--------|
| E1 diagnostic inventory | ✅ [`TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md`](TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md) |
| E2 cards (this document) | ✅ |
| E3 triangulation schema | Planned |
| D5-DES-SUPERGEO-001 / D5-DES-TRIM-001 | Planned |

---

*TRACK-E-E2-METHOD-DESIGN-SUITABILITY-CARDS-001 v1.0.0 — 2026-06-01*
