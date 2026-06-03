# METHOD-SOUNDNESS-AND-GAP-ROADMAP-001

**Document ID:** METHOD-SOUNDNESS-AND-GAP-ROADMAP-001  
**Type:** Audit-derived method soundness & development-gap roadmap — **evidence synthesis only**  
**Status:** **complete**  
**Date:** 2026-06-03  
**Verdict:** Inventory what **actually exists** in GeoX/panel_exp, reconcile prior audits, and sequence **development-first** work — **no new eligibility decisions**  
**Supersedes (for sequencing):** ad-hoc OC planning without inventory reconciliation  

**Primary inputs:** [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) · [`TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md`](TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md) · [`TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md`](TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md) · [`TRACK_D_D4_POWER_MDE_AUDIT_001.md`](TRACK_D_D4_POWER_MDE_AUDIT_001.md) · [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md) · [`METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md`](METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md) · [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) · [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) · [`AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md) · [`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md) · [`F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md`](F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md) · [`F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md`](F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md) · [`F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md`](F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md) · [`track_d/D5_INST_COMBO_AUDIT_001_REPORT.md`](track_d/D5_INST_COMBO_AUDIT_001_REPORT.md) · [`audits/AUDIT-010_mmm_readiness_gap.md`](audits/AUDIT-010_mmm_readiness_gap.md)

**Related:** [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) · [`METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md`](METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md) · [`METHOD_STRENGTHENING_LANES_001.md`](METHOD_STRENGTHENING_LANES_001.md) · [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md)

**Guardrails:** Docs/evidence synthesis only. No new eligibility decisions. No promotion/demotion. No TrustReport/F-DECISION/CalibrationSignal/MMM behavior change. No LLM integration. Missing evidence labeled **`evidence_missing`**.

---

## 1. Purpose and correction

Prior governance work (F-INF, F-GEO, F-CAT, AUDIT-010, F-DECISION-001, METHOD-SELECTION) made the platform **decision-safe** by recording evidence and blocking unsafe promotion. That stack was necessary but risked being read as a **top-down hierarchy** that decides which methods may exist before they are fully developed and characterized.

**This roadmap corrects that risk:**

| Prior risk | Correction |
|------------|------------|
| Governance read as final method ranking | Governance records **evidence** and **prevents unsafe promotion** — it does not replace method development |
| Matrix buckets mistaken for permanent rejection | **`restricted`** and **`characterized_restricted`** mean **development needed**, not discard |
| OC pass mistaken for paper fidelity | D5 batteries prove **operating characteristics under synthetic DGPs** (CV-001); conceptual validity is separate |
| LLM layer deciding validity | LLM layer **paused** ([`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md)); future LLM may **summarize labeled evidence only** |

**This document is:**

- **Audit-derived** — every row traces to code, tests, Track D audits, or archived OC JSON  
- **Development-first** — gaps convert to concrete deliverables (harness, OC, fidelity audit, metadata)  
- **Evidence-first** — uses development language (`needs_OC`, `known_failure_mode`) not winner/loser framing  

**This document is not:** a new eligibility resolver, a promotion list, or permission to change production roles without a separate governance PR.

---

## 2. Source-of-truth inventory

**Code authority:** [`panel_exp/method_metadata.py`](../panel_exp/method_metadata.py) · [`panel_exp/methods/`](../panel_exp/methods/) · [`panel_exp/inference/`](../panel_exp/inference/) · [`panel_exp/design/`](../panel_exp/design/) · [`panel_exp/validation/`](../panel_exp/validation/) · [`tests/`](../tests/)

**OC archive authority:** [`docs/track_d/archives/`](track_d/archives/) (25 JSON artifacts as of 2026-06-03)

### 2.A Estimators / readout methods

Catalog names from `_ESTIMATOR_CATALOG` ([`method_metadata.py`](../panel_exp/method_metadata.py)). Track B alias `SCM` maps to `SyntheticControl` / `SyntheticControlCVXPY` paths in production configs.

| Repo name | Code path | Tests (representative) | Audits / reports | OC evidence | Conceptual gaps | Implementation gaps | Diagnostic gaps | Development status |
|-----------|-----------|------------------------|------------------|-------------|-----------------|----------------------|-----------------|-------------------|
| **SCM** (`SyntheticControl`) | `panel_exp/methods/scm.py` | `tests/test_scm.py` | D2 ✅ · CV-001 `CV-EST-SCM` | D5-POW-001b/e (JK null-monitor framing) | `full_model=True` post-fit leakage (INV-D2-001) | scipy path less exercised than CVXPY | Pre-fit RMSE archived in ASCM-002 via inner leg | **`evidence_sufficient_for_current_role`** (A26 point/weight leg) |
| **SyntheticControlCVXPY** | `panel_exp/methods/scm.py` | `tests/test_scm.py` | D2 ✅ | Same family as SCM | Same `full_model` risk | Default pre-period path aligned (D2 pass) | D1–D7 in ASCM-002 JSON | **`evidence_sufficient_for_current_role`** for default geo path |
| **AugSynth** | `panel_exp/methods/scm.py` | `tests/test_scm.py` (limited) | D2 ✅ · CV-001 deprioritized | D5-INST-AUGSYNTH-001 probe context | Non-CVXPY path not product focus (F-CAT-003) | UNVALIDATED maturity | Not in ASCM-002 primary arms | **`known_failure_mode`** for production — probe-only |
| **AugSynthCVXPY** | `panel_exp/methods/scm.py` | `tests/test_scm.py` | D2 ✅ · CV-001 `CV-EST-AUGSYNTH` · ASCM charter | D5-INST-AUGSYNTH-001/003/KFOLD · **ASCM-002** stratified | Scale/path vs A26 at null (D5-AS-FIND-004); outside-hull W3 no MAE win | I4 partial weights; D8/D11 not emitted | Threshold labels provisional ([`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md)) | **`promising_needs_OC`** — active development lane |
| **TBR** | `panel_exp/methods/tbr.py` | `tests/track_d/test_d5_inst_tbr_001.py` | D2 skim · CV-001 `CV-EST-TBR` | **D5-INST-TBR-001** aggregate 1×1 | Aggregate estimand ≠ unit SCM (CV-EST-TBR) | Strict 1 treated + 1 control assert | Ratio/scale @ 8% (~0.99) in TBR-001 | **`needs_OC`** on aggregate geometry only; **`blocked_by_unresolved_geometry`** on unit panel |
| **TBRRidge** | `panel_exp/methods/tbr.py` | recovery/registry tests | D2 skim · CV-001 | **D5-INST-TBRRIDGE-001/002/003** | Pooled-CF semantics for JK/JKP (D5-TBRRIDGE-003) | Placebo-in-space invalid (COMBO) | Scale ≠ SCM+JK | **`needs_inference_calibration`** for JK/JKP; **`evidence_sufficient_for_current_role`** as restricted diagnostic (Kfold/BRB) |
| **TBRAutoSARIMAX** | `panel_exp/methods/tbr.py` | limited | D2 inventory | **evidence_missing** | ARIMA search stability | Not in validation runner | No D5 archive | **`unclear`** — needs fidelity audit before OC |
| **BayesianTBR** | `panel_exp/methods/bayesian_regression.py` | `tests/jax_test_helpers.py` · optional | CV-001 · INV-015 | none governed | Registry `Bayesian` ≠ NUTS MCMC (A22) | JAX optional-deps path | No production metadata | **`research_only`** — RTP-001 charter path |
| **BayesianTBRHorseShoe** | `panel_exp/methods/bayesian_regression.py` | optional JAX | CV-001 | none | Same as BayesianTBR | Research-only | — | **`research_only`** |
| **DID** | `panel_exp/methods/DID.py` | `tests/test_did_*` | D2 · CV-001 | A25 characterized (native bootstrap) | Relative ATT CI deferred (DEF-003) | Embedded bootstrap only | Cumulative interval semantics | **`needs_inference_calibration`** for relative CI policy |
| **SyntheticDID** | `panel_exp/methods/synthetic_did.py` | `tests/synthetic_did_test.py` | D2 · CV-001 | **evidence_missing** | SDID factor model fidelity | Skipped in validation runner | — | **`research_only`** |
| **TROP** | `panel_exp/methods/triply_robust_est.py` | `tests/trop_test.py` | D2 · CV-001 | A24 research_only | No registry inference surface | Expert tuning space | — | **`research_only`** — RTP-002 |
| **MTGP** | `panel_exp/methods/mtgp.py` | limited | D2 inventory | **evidence_missing** | GP prior fidelity | MCMC runtime | — | **`research_only`** |

### 2.B Inference methods

From `_INFERENCE_MODE_CATALOG` and D3 INF-* rows. DID native bootstrap is **estimator-embedded** (INF-010), not a separate registry mode.

| Repo name | Code path | Compatible estimators (observed in repo) | Claimed role (governance) | Interval semantics | Audits / reports | OC / FPR evidence | Failure modes | Development status |
|-----------|-----------|----------------------------------------|---------------------------|-------------------|------------------|-------------------|---------------|-------------------|
| **point_estimate** | `inference/` dispatch | All estimators | Point diagnostic | `none` | D3 INF-001 | N/A | No uncertainty path | **`evidence_sufficient_for_current_role`** as diagnostic |
| **UnitJackKnife** | `inference/unit_jackknife.py` | SCM, AugSynthCVXPY, TBRRidge (wired) | **Null monitor** with SCM (A26); diagnostic on AugSynth | `confidence_interval` (JK path) | D3 ✅ · D5-INF-002a/b | SCM JK FPR≈0 on 001e/ASCM-002 W2/W3 | Invalid on aggregate 2-row SCM/AugSynth | SCM+JK **`evidence_sufficient_for_current_role`**; TBRRidge+JK **`known_failure_mode`** (A16 ~79% null FPR) |
| **JKP** | registry → impl | SCM, TBR, TBRRidge | Restricted CI | `confidence_interval` | D3 · TBRRIDGE-003 | TBRRidge A21 ~29% null FPR | Pooled-CF pivot semantics | **`needs_inference_calibration`** |
| **Kfold** | `inference/k_fold.py` | SCM, AugSynthCVXPY, TBRRidge, TBR | **Diagnostic band** | `confidence_interval` | D3 · D5-KFOLD · AUGSYNTH-KFOLD-001 | 0% null FPR many batteries | Not null-monitor substitute | **`evidence_sufficient_for_current_role`** as restricted diagnostic |
| **BlockResidualBootstrap** | `inference/block_residual_bootstrap.py` | TBRRidge (primary OC) | Diagnostic band | `confidence_interval` | D3 · TBRRIDGE-001 | DEF-002 positive OC | Not AugSynth catalog (A04) | **`evidence_sufficient_for_current_role`** (TBRRidge restricted) |
| **Placebo** | `inference/placebo.py` | **SCM** (A27); not AugSynth/TBR | **Falsification** | `placebo_band` | D3 · **D5-INST-PLACEBO-001** | Single-treated scope | Multi-treated blocked (A28) | **`evidence_sufficient_for_current_role`** (falsification scope) |
| **Conformal** | `inference/conformal.py` | AugSynthCVXPY, TBRRidge | Diagnostic band (not governed) | `conformal_interval` | D3 · D5-AUGSYNTH-003 · F-INF-003 POSTFIX | POSTFIX fixed sign; null FPR 0 on battery; **not governed export** | 100% null exclude pre-POSTFIX on AugSynth | **`needs_inference_calibration`** for role taxonomy; structurally callable post-POSTFIX |
| **TimeSeriesKfold** | registry impl | TBRRidge (A19) | Diagnostic band | `confidence_interval` | D3 · POSTFIX | A19 null FPR 0 post-POSTFIX | Scale ≠ SCM+JK | **`evidence_sufficient_for_current_role`** as restricted diagnostic |
| **Bayesian** (registry) | registry impl | TBRRidge, BayesianTBR | Research / blocked prod | `credible_interval` | D3 · INV-015 | Not NUTS MCMC | Registry misuse vs BayesianTBR | **`known_failure_mode`** on prod path (A20 blocked) |
| **DID bootstrap** (native) | `panel_exp/methods/DID.py` | DID only | Restricted diagnostic | cumulative ATT (DEF-003) | D3 INF-010 | A25 partial | Relative CI unsupported | **`needs_inference_calibration`** |

### 2.C Designs / geometries / assignment modes

From [`TRACK_D_DESIGN_METHOD_INVENTORY_001.md`](TRACK_D_DESIGN_METHOD_INVENTORY_001.md) and design registry.

| Repo name | Code path | Compatible readouts observed | Power/MDE evidence | Geometry / estimand assumptions | Design–readout gaps | Development status |
|-----------|-----------|------------------------------|--------------------|---------------------------------|---------------------|-------------------|
| **greedy_match_markets** | `design/assign.py` | SCM+JK (001e reference); AugSynth diagnostic | **D5-POW-001e** tier-1 | Unit panel; pre-period matching (INV-D1-001 fixed) | Matching stage ≠ SCM donor pool (MAT-004) | **`needs_design_bridge`** vs readout audit |
| **rerandomization_wrapper** | `design/assign.py` | Same as base randomizer | D5-POW-001e | Production wraps base design | Must compare to bare greedy | **`needs_OC`** sensitivity vs bare DES-001 |
| **completerandomization** | `design/modes/` | SCM+JK 001e | D5-POW-001e | Bernoulli + constraints | Same readout alignment gap | **`needs_design_bridge`** |
| **balancedrandomization** | `design/modes/` | SCM+JK 001e | D5-POW-001e | Volume-balanced | Same | **`needs_design_bridge`** |
| **stratifiedrandomization** | `design/modes/` | SCM+JK 001e | D5-POW-001e | Strata + balance | Same | **`needs_design_bridge`** |
| **thinningdesign** | `design/modes/` | SCM+JK 001e | D5-POW-001e | Kernel thinning | Same | **`needs_design_bridge`** |
| **trimmedmatch** | `design/trimmed_match.py` | **No** flat SCM+JK (A30) | **D5-DES-TRIM-001** | Tp/Te pair population | **`needs_design_bridge`** (F-GEO-004) | **`blocked_by_unresolved_geometry`** for SCM readout |
| **supergeos** | `design/supergeos.py` | **No** flat SCM+JK (A29) | **D5-DES-SUPERGEO-001** | MILP cluster geometry | **`needs_design_bridge`** (F-GEO-003) | **`blocked_by_unresolved_geometry`** for SCM readout |
| **quickblock** | `design/quickblock.py` | not geo-run | **evidence_missing** | Legacy API | Not on production geo path | **`unclear`** — defer |
| **matchedpair** | `design/matched_pair.py` | not geo-run | **evidence_missing** | Legacy API | Defer | **`unclear`** |
| **multi_cell** (geometry mode) | `n_test_grps > 1` | Per-cell SCM+JK; AugSynth per cell | **D5-MCELL-001** | Per-cell only; pooled blocked | F-MCELL-001 pooling ADR open | **`needs_design_bridge`** for pooled claims |

**Aggregate geometry `aggregate_two_series`:** Class **TBR** readout only (D5-TBR-001); PowerAnalysis 2-row path uses **TBRRidge** agg2 — **D5-POW-001a** documents mismatch vs SCM+JK final readout.

### 2.D Existing combinations (AUDIT-010 Appendix A)

Authoritative tuple IDs **A01–A30** in [`audits/AUDIT-010_mmm_readiness_gap.md`](audits/AUDIT-010_mmm_readiness_gap.md). Summary by disposition (reconciled, not re-litigated):

| Combo IDs | Estimator | Inference | Geometry | Evidence source | Known issues | Next development task |
|-----------|-----------|-----------|----------|-----------------|--------------|----------------------|
| **A26** | SCM | UnitJackKnife | single_cell_unit | 001e · D5-POW-001b/e · CV-001 | Conservative null monitor; not lift/MDE | SCM failure-mode metadata hardening; diagnostic labels |
| **A27** | SCM | Placebo | single_treated | PLACEBO-001 | Falsification only | Placebo taxonomy ADR (F-P0-005 backlog) |
| **A28** | SCM | Placebo | multi_treated | PLACEBO-001 | 100% block rate | Keep scope documentation |
| **A01–A03** | AugSynthCVXPY | point / JK / Kfold | single_cell_unit | AUGSYNTH-001 · KFOLD-001 · **ASCM-002** | Scale bridge; outside-hull W3 | **D5-INST-AUGSYNTH-ASCM-003**; estimand bridge ADR |
| **A05** | AugSynthCVXPY | Conformal | single_cell_unit | AUGSYNTH-003 · POSTFIX | Not governed uncertainty (ADR-001) | Inference role taxonomy; no promotion OC |
| **A07, A10** | TBR | point / Kfold | aggregate_two_series | TBR-001 | Aggregate-only; scale ratio | TBR aggregate strengthening charter |
| **A13–A15, A18–A19** | TBRRidge | Kfold / BRB / Conformal / TS-Kfold | unit / agg2 | TBRRIDGE-001/003 · POSTFIX | Scale ≠ SCM+JK | JK/JKP calibration doc |
| **A16, A21** | TBRRidge | UnitJackKnife / JKP | single_cell_unit | TBRRIDGE-003 | High null FPR | **`needs_inference_calibration`** |
| **A25** | DID | native_bootstrap | single_cell_unit | COMBO · DEF-003 | Relative CI deferred | DID interval policy completion |
| **A29, A30** | SCM | UnitJackKnife | supergeo / trimmed | SUPERGEO-001 · TRIM-001 | Invalid flat readout | F-GEO-003/004 adapter ADRs |
| **A04, A06, A11, A17** | various | BRB/Placebo mismatches | — | COMBO-001 | invalid_by_interface | Catalog clarity only — no OC until ADR |
| **A22–A24** | BayesianTBR / TROP | registry paths | unit | COMBO | research_only | RTP charters — not production lane |

Full 30-row matrix: AUDIT-010 Appendix A + [`D5_INST_COMBO_AUDIT_001_results.json`](track_d/archives/D5_INST_COMBO_AUDIT_001_results.json).

---

## 3. Evidence reconciliation

Prior audits **already established** the following (reconciled here; no re-litigation):

| Audit | Established finding | Development implication |
|-------|---------------------|-------------------------|
| **D1 / INV-D1-001** | Pre-period design matching leakage fixed (`61a174f`) | Design OC baseline trustworthy for pre-period assignment |
| **D2** | Default SCM CVXPY pre-period path aligned; `full_model=True` **fail-risk** | **`known_failure_mode`** — monitor/block `full_model` misuse |
| **D3** | SCM+JK = conservative **null monitor**; placebo = falsification; no lift-grade inference promoted | Roles stable; taxonomy docs still needed for Kfold/Conformal |
| **D4** | PowerAnalysis agg2 ≠ SCM+JK readout; fixed-window preferred | **`needs_design_bridge`** POW vs readout |
| **CV-001** | 0 production-ready methods for MMM; A26 only CS-eligible | Development continues under **`restricted`** semantics |
| **COMBO / AUDIT-010** | 30 tuples dispositioned; TBR≠TBRRidge; pooled multi-cell blocked | Combination work is **targeted OC**, not Cartesian expansion |
| **ASCM-002** | AugSynth beats A26 MAE **1/2** weak-fit @ 8%; W3 outside hull **no** win; JK null FPR 0 | **`promising_needs_OC`** — not promotion |
| **ADR-001** | No AugSynth inference pairing promoted | JK remains diagnostic comparator style |
| **Threshold audit** | Provisional diagnostic labels; D8/D10/D11 missing in JSON | **`needs_inference_calibration`** via ASCM-003 |
| **F-DECISION-001** | Baseline roles assigned; disagreement policy exists | No change from this roadmap |

**Evidence language used below:** `evidence_sufficient_for_current_role` · `needs_OC` · `needs_fidelity_audit` · `needs_inference_calibration` · `needs_design_bridge` · `known_failure_mode` · `evidence_missing` · `blocked_by_unresolved_geometry`

---

## 4. Soundness dimensions

### 4.1 Estimator / readout soundness

| Dimension | Strongest repo evidence | Weakest repo evidence |
|-----------|-------------------------|----------------------|
| Estimand clarity | SCM default ATT path (CV-EST-SCM) | TBR aggregate vs unit SCM conflation |
| Assumption clarity | D2 donor exclusion documented | AugSynth spillover sensitivity partial |
| Donor/control construction | MAT-004/005 audited | Design matcher vs SCM donor pool not unified |
| Treatment geometry support | Unit panel SCM+JK (A26) | supergeo/trim flat tensor |
| Implementation fidelity | SyntheticControlCVXPY tests | AugSynth non-CVXPY UNVALIDATED |
| Failure-mode detectability | ASCM-002 D1–D7 partial | D11 `false_confidence_flag` not emitted |

### 4.2 Inference soundness

| Dimension | Strongest repo evidence | Weakest repo evidence |
|-----------|-------------------------|----------------------|
| Uncertainty source clarity | SCM donor LOO (D3) | TBRRidge JK pooled-CF |
| Interval semantics | F-INF-001 contracts | Conformal role creep risk |
| Null FPR evidence | SCM JK, AugSynth+JK on ASCM-002 W2/W3 | TBRRidge+JK (A16) |
| Coverage evidence | Limited vs power | **evidence_missing** for most bands |
| Power/MDE interpretation | D5-POW-001b null-monitor framing | 001a TBRRidge proxy optimism |
| Diagnostic vs decision separation | D3 + F-DECISION roles | Product narrative conflation risk (backlog) |

### 4.3 Design soundness

| Dimension | Strongest repo evidence | Weakest repo evidence |
|-----------|-------------------------|----------------------|
| Assignment geometry clarity | DESIGN-INVENTORY-001 | multi_cell pooling rule |
| Design estimand clarity | trim/supergeo separate populations | greedy_match vs SCM readout |
| Readout compatibility | 001e tier-1 + SCM+JK | supergeo/trim with SCM+JK |
| Power/MDE/readout alignment | 001e contract explicit | agg2 PowerAnalysis vs unit SCM |
| Interference/spillover | Phase 14 / CV spillover notes | Not standardized in D5 design OC |
| Donor/control compatibility | D1 fix + MAT-004 | Outside-hull stress partial |

### 4.4 Compatibility soundness

| Pairing | Status (reconciled) |
|---------|----------------------|
| Estimator × inference | AUDIT-010 A01–A30; COMBO rules |
| Estimator × design | A29/A30 **`blocked_by_unresolved_geometry`** |
| Inference × design | Placebo requires single-treated geometry |
| Estimand compatibility | AugSynth vs A26 scale bridge open |
| Interval semantics compatibility | F-INF-001 + POSTFIX for A05/A19 |
| Reporting/diagnostic compatibility | TrustReport `f_decision_context` visibility only |

### 4.5 Operational soundness

| Dimension | Evidence |
|-----------|----------|
| Reproducible tests | 119+ test modules; track_d harness tests per D5 artifact |
| Archive generation | 25 JSON archives under `docs/track_d/archives/` |
| Metadata emitted | ASCM-002 D1–D7; gaps D8/D10/D11 |
| Failure diagnostics | Threshold vocabulary defined; numeric calibration open |
| Runtime/failure handling | `min_donors=5` blocks recorded in ASCM-002 |
| Real-panel readiness | **evidence_missing** — no shadow replay archive in repo |

---

## 5. Gap taxonomy

| Category | Definition | Example in repo |
|----------|------------|-----------------|
| **conceptual_gap** | Literature/estimand mismatch undocumented | TBR vs TBRRidge (CV-EST-TBR) |
| **algorithm_fidelity_gap** | Implementation may deviate from cited algorithm | Registry Bayesian vs BayesianTBR MCMC |
| **implementation_gap** | Code incomplete vs charter | ASCM D11 boolean not in harness |
| **inference_semantics_gap** | Role of interval unclear | Conformal as diagnostic vs null monitor |
| **design_geometry_gap** | Design output incompatible with readout tensor | supergeos + flat SCM+JK |
| **estimand_gap** | Target quantity differs across arms | AugSynth point vs A26 JK path |
| **OC_evidence_gap** | No stratified battery for claim | Weak-fit before ASCM-002 |
| **diagnostic_gap** | Failure modes not measurable | Provisional RMSE/hull cutoffs |
| **metadata_gap** | JSON/archive missing fields | `false_confidence_flag`, scale ratio |
| **real_panel_validation_gap** | No production replay evidence | **evidence_missing** |
| **documentation_gap** | Product narrative may misread role | Placebo vs CI (F-P0-005) |

---

## 6. Soundness scorecard

Evidence levels: `none` · `docs_only` · `unit_tests` · `small_OC` · `stratified_OC` · `real_panel_shadow` · `production_candidate`  
Soundness status: `sound_for_current_role` · `promising_needs_OC` · `unclear` · `known_failure_mode` · `blocked_by_geometry` · `implementation_gap`

### 6.1 Estimators / readouts (selected)

| item_id | item_type | exact repo name | evidence level | soundness status | highest-priority gap | next development artifact | not-before |
|---------|-----------|-----------------|----------------|------------------|----------------------|---------------------------|------------|
| EST-SCM | estimator | SCM / SyntheticControlCVXPY | stratified_OC | sound_for_current_role | diagnostic_gap | D5-DIAG-SCM-AUGSYNTH-001 metadata spec | threshold labels |
| EST-ASCM | estimator | AugSynthCVXPY | stratified_OC | promising_needs_OC | OC_evidence_gap + estimand_gap | **D5-INST-AUGSYNTH-ASCM-003** | ADR-001 ✅ |
| EST-TBR | estimator | TBR | small_OC | sound_for_current_role (agg only) | conceptual_gap | TBR_AGGREGATE_STRENGTHENING_001 | unit panel block documented |
| EST-TBRR | estimator | TBRRidge | small_OC | promising_needs_OC | inference_semantics_gap | TBRRIDGE_JK_JKP_STRENGTHENING_001 | TBRRIDGE-003 ✅ |
| EST-DID | estimator | DID | small_OC | promising_needs_OC | inference_semantics_gap | DEF-003 relative CI policy | F-P0-004 |
| EST-AUG | estimator | AugSynth (non-CVXPY) | unit_tests | known_failure_mode | algorithm_fidelity_gap | none (deprioritized F-CAT-003) | — |
| EST-BTBR | estimator | BayesianTBR | unit_tests | unclear | algorithm_fidelity_gap | RTP-001 charter | product pull |
| EST-TROP | estimator | TROP | unit_tests | unclear | OC_evidence_gap | RTP-002 charter | product pull |

### 6.2 Inference (selected)

| item_id | item_type | exact repo name | evidence level | soundness status | highest-priority gap | next development artifact | not-before |
|---------|-----------|-----------------|----------------|------------------|----------------------|---------------------------|------------|
| INF-JK-SCM | inference | UnitJackKnife + SCM | stratified_OC | sound_for_current_role | diagnostic_gap | SCM diagnostic metadata wiring proposal | ASCM-003 calibration |
| INF-JK-AS | inference | UnitJackKnife + AugSynthCVXPY | stratified_OC | promising_needs_OC | estimand_gap | AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001 | ASCM-003 |
| INF-PLAC | inference | Placebo | small_OC | sound_for_current_role | documentation_gap | PLACEBO_FALSIFICATION_TAXONOMY_ADR_001 | — |
| INF-CONF | inference | Conformal | small_OC | promising_needs_OC | inference_semantics_gap | INFERENCE_ROLE_TAXONOMY_ADR_001 | POSTFIX ✅ |
| INF-JK-TBRR | inference | UnitJackKnife + TBRRidge | small_OC | known_failure_mode | inference_semantics_gap | TBRRIDGE_JK_JKP_STRENGTHENING_001 | F-INF-002 ✅ |
| INF-KF | inference | Kfold | small_OC | sound_for_current_role | inference_semantics_gap | INFERENCE_ROLE_TAXONOMY_ADR_001 | KFOLD-001 ✅ |

### 6.3 Designs / geometries (selected)

| item_id | item_type | exact repo name | evidence level | soundness status | highest-priority gap | next development artifact | not-before |
|---------|-----------|-----------------|----------------|------------------|----------------------|---------------------------|------------|
| DES-GREEDY | design | greedy_match_markets | stratified_OC | promising_needs_OC | design_geometry_gap | DESIGN_READOUT_COMPATIBILITY_AUDIT_001 | DESIGN-INVENTORY ✅ |
| DES-MCELL | geometry | multi_cell (n_test_grps>1) | small_OC | promising_needs_OC | estimand_gap | F-MCELL-001 pooling ADR | D5-MCELL-001 ✅ |
| DES-SGEO | design | supergeos | small_OC | blocked_by_geometry | design_geometry_gap | TRIM_SUPERGEO_STRENGTHENING_001 / F-GEO-003 | D5-DES-SUPERGEO-001 ✅ |
| DES-TRIM | design | trimmedmatch | small_OC | blocked_by_geometry | design_geometry_gap | TRIM_SUPERGEO_STRENGTHENING_001 / F-GEO-004 | D5-DES-TRIM-001 ✅ |
| GEO-AGG2 | geometry | aggregate_two_series | small_OC | promising_needs_OC | design_geometry_gap | POWER_READOUT_ALIGNMENT_ADR_001 | D5-POW-001a ✅ |

### 6.4 Combinations (headline)

| item_id | item_type | exact repo name | evidence level | soundness status | highest-priority gap | next development artifact | not-before |
|---------|-----------|-----------------|----------------|------------------|----------------------|---------------------------|------------|
| A26 | combination | SCM+UnitJackKnife+single_cell_unit | stratified_OC | sound_for_current_role | diagnostic_gap | D5-DIAG-SCM-AUGSYNTH-001 | — |
| A01-A03 | combination | AugSynthCVXPY arms | stratified_OC | promising_needs_OC | OC_evidence_gap | D5-INST-AUGSYNTH-ASCM-003 | threshold audit ✅ |
| A05 | combination | AugSynthCVXPY+Conformal | small_OC | promising_needs_OC | inference_semantics_gap | keep_restricted policy note | ADR-001 ✅ |
| A16 | combination | TBRRidge+UnitJackKnife | small_OC | known_failure_mode | inference_semantics_gap | TBRRIDGE_JK_JKP_STRENGTHENING_001 | TBRRIDGE-003 ✅ |
| A29-A30 | combination | SCM+JK on supergeo/trim | docs_only | blocked_by_geometry | design_geometry_gap | F-GEO-003/004 ADRs | DES OC ✅ |

---

## 7. Development roadmap

Lanes convert gaps to **concrete deliverables**. Priority: scientific importance × evidence weakness × reuse × production relevance × LLM-readiness blockers.

### Lane DL-0 — Inventory reconciliation (this document)

| Deliverable | Type | Unlocks |
|-------------|------|---------|
| **METHOD-SOUNDNESS-AND-GAP-ROADMAP-001** (this doc) | docs | Sequenced development; scorecard baseline |

### Lane DL-1 — Active AugSynth/ASCM development (highest priority)

| Deliverable | Type | Gap categories | Depends on |
|-------------|------|----------------|------------|
| **AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001** | docs | documentation_gap | ASCM-002 ✅ · threshold audit ✅ · review ✅ |
| **D5-DIAG-SCM-AUGSYNTH-001** | diagnostic implementation | metadata_gap · diagnostic_gap | Threshold audit §2 |
| **D5-INST-AUGSYNTH-ASCM-003** | OC battery | OC_evidence_gap · diagnostic_gap | ASCM-002 harness |
| **AUGSYNTH_SCM_ESTIMAND_BRIDGE_ADR_001** | ADR | estimand_gap | D5-AS-FIND-004 · ASCM-002 conflict metrics |

### Lane DL-2 — SCM baseline / failure-mode hardening

| Deliverable | Type | Gap categories | Depends on |
|-------------|------|----------------|------------|
| Emit D11 + normalized RMSE in harness | metadata/reporting hardening | metadata_gap | D5-DIAG-SCM-AUGSYNTH-001 |
| INV-D2-001 monitoring for `full_model=True` | implementation fidelity audit | known_failure_mode | D2 finding |
| TrustReport diagnostic label **proposal** (no prod change) | docs | diagnostic_gap | ASCM-003 calibration |

### Lane DL-3 — Inference calibration (cross-cutting)

| Deliverable | Type | Gap categories | Depends on |
|-------------|------|----------------|------------|
| **INFERENCE_ROLE_TAXONOMY_ADR_001** | ADR | inference_semantics_gap | ADR-001 · D3 |
| **TBRRIDGE_JK_JKP_STRENGTHENING_001** | failure-mode doc | inference_semantics_gap | TBRRIDGE-003 |
| **PLACEBO_FALSIFICATION_TAXONOMY_ADR_001** | ADR | documentation_gap | PLACEBO-001 |
| DEF-003 / DID relative CI policy | inference calibration | inference_semantics_gap | A25 |

### Lane DL-4 — Design / readout compatibility

| Deliverable | Type | Gap categories | Depends on |
|-------------|------|----------------|------------|
| **DESIGN_READOUT_COMPATIBILITY_AUDIT_001** | compatibility study | design_geometry_gap | DESIGN-INVENTORY ✅ |
| **POWER_READOUT_ALIGNMENT_ADR_001** | ADR | design_geometry_gap | D5-POW-001a–e |
| **F-MCELL-001** pooling ADR | ADR | estimand_gap | D5-MCELL-001 |

### Lane DL-5 — supergeo / trim (repo artifacts exist)

| Deliverable | Type | Gap categories | Depends on |
|-------------|------|----------------|------------|
| **TRIM_SUPERGEO_STRENGTHENING_001** | charter | design_geometry_gap | D5-DES-SUPERGEO/TRIM ✅ |
| F-GEO-003 / F-GEO-004 adapter scope | ADR | design_geometry_gap | RTP-003/004 backlog |

### Lane DL-6 — TBR aggregate / TBRRidge product paths

| Deliverable | Type | Gap categories | Depends on |
|-------------|------|----------------|------------|
| **TBR_AGGREGATE_STRENGTHENING_001** | charter | conceptual_gap | TBR-001 ✅ |
| Optional TBR+JKP OC (A09) | OC battery | OC_evidence_gap | TBR-001 |

### Lane DL-7 — Real-panel replay / shadow validation

| Deliverable | Type | Gap categories | Depends on |
|-------------|------|----------------|------------|
| Real-panel shadow replay charter | docs + harness | real_panel_validation_gap | DL-1–4 metadata stable |
| **evidence_missing** today | — | — | No archive in repo |

### Lane DL-8 — Research-only (product pull)

| Deliverable | Type | Items |
|-------------|------|-------|
| RTP-001 / RTP-002 charters | research | BayesianTBR MCMC · TROP |
| MTGP / SyntheticDID | defer | evidence_missing OC |

---

## 8. Recommended phase sequence

Phases derived from repo evidence and [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) lanes. **No new eligibility decisions.**

| Phase | Name | Scope | Exit signal |
|-------|------|-------|-------------|
| **0** | Inventory reconciliation & scorecard | This doc + cross-ref updates | Scorecard rows for all headline items |
| **1** | Active AugSynth/ASCM development | DL-1: development roadmap, D5-DIAG, ASCM-003, estimand bridge ADR | ASCM-003 calibrates threshold cutoffs; D8/D10/D11 in JSON |
| **2** | SCM baseline / failure-mode hardening | DL-2: metadata, `full_model` monitoring, diagnostic label proposal | Stable diagnostic facets documented |
| **3** | Inference calibration | DL-3: role taxonomy, TBRRidge JK/JKP, placebo taxonomy, DID CI | Inference roles documented per F-INF + ADRs |
| **4** | Design / readout compatibility | DL-4: design–readout audit, POW alignment, F-MCELL | Compatibility table for tier-1 designs × readouts |
| **5** | supergeo / trim / multi-cell | DL-5 + DL-4 F-MCELL | Adapter ADRs scoped; no flat SCM claims |
| **6** | TBR aggregate + TBRRidge paths | DL-6 | Aggregate bridge audit complete |
| **7** | Real-panel shadow replay | DL-7 | **`evidence_missing`** until charter + first replay |
| **8** | LLM readiness audit | AUDIT-011 | [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) §6 exit |

**LLM layer remains paused** through phases 0–7.

---

## 9. Immediate next active lane

**Checkpoint:** [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md) — verdict **`proceed_to_augsynth_development_lane`** (DL-1 + coupled DL-2; design-readout parallel docs). **Review complete.**

**Execution plan:** [`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md) — **materialized**. **D5-DIAG-SCM-AUGSYNTH-001** ✅ complete ([`D5_DIAG_SCM_AUGSYNTH_001_REPORT.md`](track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md)). **Next:** **AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001** (P2).


**AugSynth/ASCM** is the **active method-development lane** because recent stratified evidence ([`D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md)) is the richest weak-fit/hull dataset in the repo, and foundation docs ([`AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md), ADR-001, threshold audit) already frame gaps — without promoting AugSynth or demoting SCM/A26.

| Priority | Artifact | Type | Rationale |
|----------|----------|------|-----------|
| **1** | **AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001** | docs | ✅ Materialized — sequences DL-1/DL-2 deliverables ([`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md)) |
| **2** | **D5-DIAG-SCM-AUGSYNTH-001** | diagnostic implementation | ✅ [`D5_DIAG_SCM_AUGSYNTH_001_REPORT.md`](track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md) — [`scm_augsynth_diagnostics.py`](../panel_exp/validation/scm_augsynth_diagnostics.py) |
| **3** | **AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001** | fidelity audit | **Next** — charter §4 I4–I8 vs implementation |
| **4** | **D5-INST-AUGSYNTH-ASCM-003** | OC battery | Uses D5-DIAG fields; calibrates provisional threshold cutoffs (n_mc ≥ 14) |

**Parallel (non-blocking):** DESIGN_READOUT_COMPATIBILITY_AUDIT_001 (foundation P2) — design-stage work, not AugSynth algorithm work.

**Explicitly not next:** LLM integration · method promotion · F-DECISION amendment · CalibrationSignal expansion.

---

## 10. Anti-bureaucracy rules

1. **No broad eligibility decisions without new evidence** — F-DECISION-001 and AUDIT-010 remain authoritative; this roadmap does not amend them.  
2. **No more roadmap docs unless they unlock code, audit, OC, or replay work** — the next doc in DL-1 must point to D5-DIAG or ASCM-003 execution.  
3. **`restricted` / `characterized_restricted` means development needed** — not permanent rejection.  
4. **Every roadmap item must point to a concrete deliverable** — see §7 tables.  
5. **LLM cannot infer validity** — it may only summarize **labeled** evidence ([`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) §6; foundation hardening §6).  
6. **If evidence is missing, say so** — do not substitute literature or product narrative for OC archives.  
7. **Governance prevents unsafe promotion; development closes gaps** — both are required, neither replaces the other.

---

## 11. Stop condition

| Criterion | Status |
|-----------|--------|
| Inventories actual implemented/documented methods (§2) | ✅ |
| Reconciles existing audits without re-litigation (§3) | ✅ |
| Identifies conceptual/algorithmic/operational gaps (§4–§5) | ✅ |
| Scorecard for headline items (§6) | ✅ |
| Development-first sequenced lanes (§7–§8) | ✅ |
| Active lane identified with concrete next artifacts (§9) | ✅ |
| Anti-bureaucracy rules (§10) | ✅ |
| No new eligibility / promotion / prod behavior change | ✅ |

---

*METHOD-SOUNDNESS-AND-GAP-ROADMAP-001 v1.0.0 — evidence synthesis; execution via DL-1+ deliverables.*
