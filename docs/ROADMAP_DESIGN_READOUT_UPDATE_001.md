# ROADMAP-DESIGN-READOUT-UPDATE-001

**Document ID:** ROADMAP-DESIGN-READOUT-UPDATE-001  
**Type:** Governance / roadmap correction (research lane)  
**Status:** **complete**  
**Date:** 2026-06-01  
**Baseline:** DESIGN-INVENTORY-001 @ `e3e6aeb`; D5-POW-001a–d complete  

---

## Purpose

Correct roadmap and governance framing **before** D5-POW-001e implementation. Power/OC and design-readout evidence are **design-method × geometry-mode × measurement-instrument** specific. SCM+UnitJackKnife is the **reference null-monitor branch** for fixed-window unit-level OC—not the universal GeoX readout.

---

## 1. DESIGN-INVENTORY-001 status

| Item | Status |
|------|--------|
| **DESIGN-INVENTORY-001** | ✅ Complete @ commit `e3e6aeb` |
| **D5-POW-001e** | ✅ Complete — [`D5_POW_001e_results.json`](track_d/archives/D5_POW_001e_results.json) |
| **Discovery** | Code-grounded via `get_design_registry()`, not roadmap-assumed names |

**Registry:** 9 entries. **Geo-run supported (5):** `greedy_match_markets`, `thinningdesign`, `balancedrandomization`, `completerandomization`, `stratifiedrandomization` — matches `LEGACY_GEO_RUN_DESIGN_SUPPORTED`.

**Orchestration:** `Rerandomization` in `panel_exp/design/assign.py`; used via `GeoExperimentDesign.create_design()`; **not** a registry row.

**Not found:** `multi_cell_multi_treated` as a class or method. Multi-cell = **`n_test_grps > 1`** on supported geo design methods (geometry mode, not a method).

**Artifacts:** [`TRACK_D_DESIGN_METHOD_INVENTORY_001.md`](TRACK_D_DESIGN_METHOD_INVENTORY_001.md) · [`track_d/archives/DESIGN_INVENTORY_001_results.json`](track_d/archives/DESIGN_INVENTORY_001_results.json)

---

## 2. Reframe SCM+UnitJackKnife

**SCM+UnitJackKnife** is the current **reference readout** for fixed-window **unit-level null-monitor OC**. It is **not**:

- the universal GeoX readout  
- a platform-wide power/MDE instrument  
- a lift-detection instrument  

**D5-POW-001e interprets as:**

- SCM+JK **reference null-behavior** across confirmed design methods and supported geometry modes  

**D5-POW-001e does not interpret as:**

- full platform power validation  
- general MDE validation  
- validation of all estimators/inference methods  
- validation of MMM-ready lift evidence  

**Track E E1/E2 expansion (required):** suitability cards for the broader measurement-instrument panel, each with its own OC evidence before promotion:

- SCM + UnitJackKnife (reference null-monitor branch)  
- TBRRidge + KFold  
- TBRRidge + BlockResidualBootstrap  
- AugSynth point / JK (where available)  
- DID + bootstrap  
- SCM Placebo (where geometry supports)  
- Geo `PowerAnalysis` diagnostic path (aggregated; not governed readout)  

---

## 3. OC framing: design × geometry × instrument

| Layer | Examples |
|-------|----------|
| **Design method** | `greedy_match_markets`, `completerandomization`, `Rerandomization` wrapper, … |
| **Geometry mode** | `single_cell` (`n_test_grps=1`), `multi_cell` (`n_test_grps>1`), `supergeo`, `trimmed_population` |
| **Measurement instrument** | `SCM_UnitJackKnife`, `TBRRidge_Kfold`, geo `PowerAnalysis`, … |

No naive averaging across frameworks. No pooled multi-cell claim without a governed pooling rule.

---

## 4. D5-POW-001e scope (pre-implementation)

**Question:** Under fixed-window unit-level **SCM+JK reference readout**, which confirmed design methods and supported geometry modes have acceptable null behavior?

**Eligible design methods only** ([DESIGN-INVENTORY-001](TRACK_D_DESIGN_METHOD_INVENTORY_001.md)):

1. `greedy_match_markets` (bare baseline)  
2. `rerandomization_wrapper` + `greedy_match_markets` (production path)  
3. `completerandomization`  
4. `balancedrandomization`  
5. `stratifiedrandomization`  
6. `thinningdesign`  

**Required:** single-cell null FPR across all six (compare bare greedy vs `Rerandomization(greedy)` explicitly).

**Where safely supported:** limited **multi_cell** runs (`n_test_grps > 1`); **per-cell** metrics only; **no pooling** unless a governed pooling rule exists.

**Harness contract:** fixed chronological pre/post (D5-POW-001d); correct effect interval semantics (D5-POW-001b); unit-level markets (D5-POW-001c); research lane only.

---

## 5. Multi-cell design geometry

**Multi-cell** = multiple concurrent test cells (e.g. channels or strategies) against one **shared control**. It is a **geometry/design mode**, not a separate design method.

| Single-cell | Multi-cell |
|-------------|------------|
| control vs test | control vs test_0 / test_1 / … / test_k |

**Roadmap implication:** Design stage should not blindly accept `n_test_grps`; eventually diagnose whether requested cell count degrades per-cell performance and recommend feasible/optimal **k**.

**Required diagnostics (Track E `E-DES-MCELL-*`):** per-cell balance; shared-control adequacy; per-cell donor/control count; per-cell SCM+JK feasibility; per-cell null FPR / null-monitor coverage; treatment-cell conflict; multiple-comparison warning; minimum viable controls per cell; **no pooled multi-cell claim** without governed pooling rule; recommended/maximum feasible cell count.

---

## 6. D5-POW-001e method × geometry contract

Per **method × geometry_mode** row, record at minimum:

`method_id`, `entrypoint`, `geometry_mode`, `n_test_grps`, assignment geometry, control count, test count per cell, pre/post windows, per-cell pre-balance, shared-control adequacy, per-cell donor/control count, per-cell UnitJackKnife feasibility, per-cell null interval-exclusion FPR, per-cell null-monitor coverage, point null drift, skip/failure reason, Track E candidate flags.

**Rules:** no pooled multi-cell estimate; no pooled lift claim; no MMM/planning feed; no SCM+JK MDE or lift-detection promotion; research lane only.

---

## 7. Supergeos, trimmedmatch, legacy paths

| ID | Status | Future |
|----|--------|--------|
| **supergeos** | `SupergeoModel` / registry `supergeos`. **Excluded from 001e** — supergeo clusters / MILP pairing; not flat unit-level SCM+JK contract. **separate_geometry_design** / characterization_required. | **D5-DES-SUPERGEO-001** |
| **trimmedmatch** | `TrimmedMatchDesign` / registry `trimmedmatch`. **Excluded from 001e** — pair trim, Tp/Te split, own power semantics; may shift population/estimand. **separate_population_design** / characterization_required. | **D5-DES-TRIM-001** |
| **quickblock**, **matchedpair** | Registered; **tier_3_legacy_or_doc_only** unless shown active in production geo path | — |

**Not ignored** — separate follow-ups with distinct semantics.

---

## 8. Track E diagnostic families (preserve + extend)

| Family | IDs | Focus |
|--------|-----|--------|
| **E-DES-WIN** | assignment/pre-balance stability; readout FPR vs window; post-length adequacy; fixed-window requirement | D5-POW-001d |
| **E-SCM-DONOR** | min donors; concentration; LOO stability; pool overlap; constraint feasibility; regional/spend sensitivity | D2 + 001e |
| **E-DES-MCELL** | cell-count feasibility; per-cell balance; shared control; per-cell JK feasibility/FPR; conflict; multi-comparison; optimal **k** | 001e multi_cell |

---

## 9. Track E E1/E2 (target)

**E1:** formal suitability diagnostic inventory (families above).  
**E2:** design-method and measurement-instrument **cards** with: design identity; geometry mode; compatible/incompatible readouts; window requirements; donor/pre-period diagnostics; D5 OC evidence; CalibrationSignal / TrustReport / diagnostic / restricted / blocked; MMM implication.

**Explicit:** SCM+JK is **one card**, not the whole system. Other instruments need own OC before promotion.

---

## 10. Updated next-step sequence

1. ✅ **ROADMAP-DESIGN-READOUT-UPDATE-001** (this document)  
2. ✅ **D5-POW-001e** — six confirmed methods; SCM+JK reference branch; per-cell single/multi_cell; no pooling  
3. ✅ **Track E E1/E2** — [`TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md`](TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md) · [`TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md`](TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md)  
4. ✅ **Track E E3/E4** — [`TRACK_E_E3_TRIANGULATION_SCHEMA_001.md`](TRACK_E_E3_TRIANGULATION_SCHEMA_001.md) · [`TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md`](TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md)  
5. ✅ **Track E E5/E6** — CalibrationSignal eligibility policy + E4 fixture contract tests  
6. **Track E E7** — production triangulation / TrustReport integration  
7. **Later:** D5-DES-SUPERGEO-001 · D5-DES-TRIM-001 · D5-MCELL · other instrument OC batteries  

---

## 11. Governance constraints (unchanged)

- Research lane only  
- No production design/power/estimator/inference changes  
- No Track B / TrustReport changes  
- No MMM/planning feed  
- No SCM+JK lift-detection or MDE promotion  
- D5-POW-001e = OC evidence only; Track E converts to suitability cards and rules  

---

## 12. D5-POW-001e results (2026-06-01)

**Artifact:** [`D5_POW_001e_results.json`](track_d/archives/D5_POW_001e_results.json) · harness `panel_exp/validation/track_d_d5_pow_001e.py`

| Finding | Detail |
|---------|--------|
| **Overall** | `acceptable_with_caveats` — SCM+JK **null-monitor reference** only |
| **Single-cell** | All six methods **acceptable** (mean per-cell null interval-exclusion FPR ≈ 0 on `scm_low_signal` battery) |
| **Multi-cell** | All six **acceptable**; `thinningdesign` test_1 mean null FPR ≈ 3.6%; no pooled multi-cell claim |
| **Greedy vs wrapper** | `Rerandomization(greedy)` matches bare greedy on this battery (Δ FPR 0) |
| **Track E** | Register **E-DES-MCELL-*** for multi-cell suitability; **E-SCM-DONOR-*** / **E-DES-WIN-*** as follow-ons |

---

## 13. Combo compatibility audit (D5-INST-COMBO-AUDIT-001)

**Status:** ✅ [`D5_INST_COMBO_AUDIT_001_REPORT.md`](track_d/D5_INST_COMBO_AUDIT_001_REPORT.md)

30 **curated** estimator × inference × geometry tuples (not a blind Cartesian product). Key gates:

- **TBR** — valid only on **aggregate 1×1**; invalid on unit multi-control.
- **AugSynthCVXPY + Kfold** — valid OC candidate; **BRB/Placebo** blocked at catalog interface until clarified.
- **TBRRidge + Kfold/BRB** — already characterized; other inference modes unvalidated.
- **AUDIT-010** — MMM readiness/gap audit blocks invalid combos from intake.

---

## 14. Conceptual validity audit (TRACK-D-CONCEPTUAL-VALIDITY-AUDIT-001)

**Status:** ✅ [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md)

Literature/method fidelity audit for all estimator and inference families. **Synthetic OC ≠ paper validity.** Verdict: **`continue_with_restricted_diagnostics_only`** — **0** production/MMM-ready paths.

**AUDIT-010 prerequisites:** this audit ✅ + **D5-INST-TBR-001** (aggregate class TBR).

**Blocking conceptual gaps:** `full_model` SCM/AugSynth; registry `Bayesian` ≠ BayesianTBR MCMC; TBR/TBRRidge conflation; DID relative ATT CI vs SCM.

---

*ROADMAP-DESIGN-READOUT-UPDATE-001 v1.0.3 — TRACK-D-CONCEPTUAL-VALIDITY-AUDIT-001 complete*
