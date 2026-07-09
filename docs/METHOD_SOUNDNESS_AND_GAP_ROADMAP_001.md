# METHOD-SOUNDNESS-AND-GAP-ROADMAP-001

**Document ID:** METHOD-SOUNDNESS-AND-GAP-ROADMAP-001  
**Type:** Audit-derived method soundness & development-gap roadmap — **evidence synthesis only**  
**Status:** **complete**  
**Date:** 2026-06-03  
**Verdict:** Inventory what **actually exists** in GeoX/panel_exp, reconcile prior audits, and sequence **development-first** work — **no new eligibility decisions**  
**Supersedes (for sequencing):** ad-hoc OC planning without inventory reconciliation  

**Primary inputs:** [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) · [`TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md`](TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md) · [`TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md`](TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md) · [`TRACK_D_D4_POWER_MDE_AUDIT_001.md`](TRACK_D_D4_POWER_MDE_AUDIT_001.md) · [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md) · [`METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md`](METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md) · [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) · [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) · [`AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md) · [`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md) · [`F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md`](F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md) · [`F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md`](F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md) · [`F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md`](F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md) · [`track_d/D5_INST_COMBO_AUDIT_001_REPORT.md`](track_d/D5_INST_COMBO_AUDIT_001_REPORT.md) · [`audits/AUDIT-010_mmm_readiness_gap.md`](audits/AUDIT-010_mmm_readiness_gap.md)

**Related:** [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) · [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) · [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) · [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) · [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) · [`TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md`](TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md) · [`METHOD_FOUNDATION_SYNTHESIS_001.md`](METHOD_FOUNDATION_SYNTHESIS_001.md) · [`METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md`](METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md) · [`METHOD_STRENGTHENING_LANES_001.md`](METHOD_STRENGTHENING_LANES_001.md) · [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md)

**Geometry controller:** [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) — post-D5 canonical geometry types and bridge requirements (Accepted; no promotion).

**Design audit program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) — Accepted; estimator/inference audit parity incomplete until design ladder completes.

**Parked future estimator:** [`TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md`](TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md) — TROP audit ladder; `research_only` today; not rejected.

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

**Design audit program:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) — Accepted. **Design output contract:** [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) — Accepted. **Design code inventory:** [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) — Accepted (31 rows; 0 contract-complete implementations).

**Metadata gap summary (from inventory):** No design emits `geometry_id`, `forbidden_downstream_claims`, or full unit-universe fields. `DesignEvidence` partial only. Supergeo lacks `supergeo_source_unit_map` in output path. Trim lacks exclusion/target-population metadata. Multi-cell lacks `cell_ids` / shared-control policy in evidence. Power/MDE not linked to design contract envelope.

**Conceptual gaps (from literature alignment):** G-DES-001–014 — thinning semantics ambiguous; shared-control implicit; rerandomization inference not connected; block/pair metadata absent; trim/supergeo bridges undefined; balanced vs complete randomization naming risk. See [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) §21.

**Implementation blockers (from implementation validation):** [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) — Accepted; **0/31 contract-complete**; 4 `adapter_required`; 8 hard blocker classes (IV-DES-001–017): missing `geometry_id`, missing `forbidden_downstream_claims`, missing `concurrent_multi_experiment_compatibility`, adapter-required designs (QuickBlock, MatchedPair, TrimmedMatch, Supergeo), missing trim/supergeo metadata, missing shared-control/cell metadata, no design contract validation tests.

**Statistical validation protocol:** [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) — Accepted; `design_statistical_validation_protocol_defined_not_executed`; **0 designs statistically validated**; tier-1 eligible with contract BLOCK; trim/supergeo/pooled remain bridge-blocked until `D5-DES-STAT-*` execution.

From [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) (supersedes [`TRACK_D_DESIGN_METHOD_INVENTORY_001.md`](TRACK_D_DESIGN_METHOD_INVENTORY_001.md) for enumeration authority) and design registry.

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
| DES-GREEDY | design | greedy_match_markets | stratified_OC | promising_needs_OC | design_geometry_gap | DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001 ✅ | DESIGN-INVENTORY ✅ |
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
| **DESIGN_READOUT_COMPATIBILITY_AUDIT_001** | compatibility study | design_geometry_gap | DESIGN-INVENTORY ✅ · **AugSynth-scoped:** [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md) ✅ P6 |
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
| **4** | Design / readout compatibility | DL-4: design–readout audit ✅ P6 · **DL-1 closed** [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md) | Pooling ADR next |
| **5** | supergeo / trim / multi-cell | DL-5 + DL-4 F-MCELL | Adapter ADRs scoped; no flat SCM claims |
| **6** | TBR aggregate + TBRRidge paths | DL-6 | Aggregate bridge audit complete |
| **7** | Real-panel shadow replay | DL-7 | **`evidence_missing`** until charter + first replay |
| **8** | LLM readiness audit | AUDIT-011 | [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) §6 exit |

**LLM layer remains paused** through phases 0–7.

---

## 9. Immediate next active lane

**Authoritative sequence (2026-06-04):** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md).

| Priority | Artifact | Layer | Status |
|----------|----------|-------|--------|
| **1** | **METHOD_VALIDATION_PROGRAM_001** | program | ✅ active |
| **2** | **METHOD_CODE_INVENTORY_001** | 1 | ✅ [`METHOD_CODE_INVENTORY_001.md`](METHOD_CODE_INVENTORY_001.md) |
| **3** | **METHOD_LITERATURE_ALIGNMENT_001** | 2 | ✅ [`METHOD_LITERATURE_ALIGNMENT_001.md`](METHOD_LITERATURE_ALIGNMENT_001.md) |
| **4** | **METHOD_IMPLEMENTATION_VALIDATION_001** | 3 | ✅ [`METHOD_IMPLEMENTATION_VALIDATION_001.md`](METHOD_IMPLEMENTATION_VALIDATION_001.md) |
| **5** | **METHOD_STATISTICAL_VALIDATION_PROTOCOL_001** | 4 | ✅ [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) |
| **6** | **METHOD_COMBINATION_VALIDATION_MATRIX_001** | 5 | ✅ [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) |
| **7** | **DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001** | post-5 | ✅ [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) |
| **8** | **D5-STAT-SMOKE-CALLABLE-001** | OC execution | ✅ [`docs/track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md`](track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md) |
| **9** | **D5-STAT-SCM-JK-001** | Level B characterization | ✅ [`docs/track_d/D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md) |
| **10** | **D5-STAT-AUGSYNTH-POINT-001** | Level B characterization | ✅ [`docs/track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md) |
| **11** | **D5-STAT-TBR-AGG-001** | Level B characterization | ✅ `characterization_mixed_requires_followup` |
| **12** | **D5-STAT-DID-BOOTSTRAP-001** | Level B characterization | ✅ harness corrected · production readout fixed (`did_bootstrap_cumulative_readout_corrected_requires_reassessment`) |
| **13** | **D5-STAT-MCELL-PERCELL-001** | Level B per-cell execution | ✅ `characterization_pass_with_caveats` |
| **14** | **D5-STAT-TBRRIDGE-INF-001** | Level B characterization | ✅ **Complete** — mixed followup |
| **15** | **INFERENCE_READOUT_SEMANTICS_001** | Readout contract | ✅ **Accepted** — [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) |
| **16** | **GEOMETRY_BRIDGE_REQUIREMENTS_001** | Geometry bridge | ✅ **Accepted** — [`GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md) |
| **17** | **DESIGN_OUTPUT_CONTRACT_001** | Design output contract | ✅ Accepted |
| **18** | **DESIGN_CODE_INVENTORY_001** | Design code inventory | ✅ Accepted — [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) |
| **19** | **DESIGN_LITERATURE_ALIGNMENT_001** | Design literature alignment | ✅ Accepted — [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) |
| **20** | **DESIGN_IMPLEMENTATION_VALIDATION_001** | Design implementation validation | ✅ Accepted — [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) |
| **21** | **DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001** | Design statistical validation | ✅ Accepted — [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) |
| **22** | **DESIGN_COMBINATION_VALIDATION_MATRIX_001** | Design combination matrix | ✅ Accepted — [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) |
| **23** | **DESIGN_GUARDRAILS_001** | Design guardrails | ✅ Accepted — [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) |
| **24** | **DESIGN_SUITABILITY_FRAMEWORK_001** | Design suitability | ✅ Accepted — [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) |
| **25** | **DESIGN_CONTRACT_ENFORCEMENT_PLAN_001** | Contract enforcement planning | ✅ Accepted — [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) |
| **26** | **DESIGN_CONTRACT_SCHEMA_001** | Contract schema | ✅ Accepted — [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) |
| **27** | **DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001** | Tier-1 emission plan | ✅ Accepted — [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) |
| **28** | **DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001** | Contract validation tests | ✅ Accepted — [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) |
| **29** | **DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001** | Validator implementation plan | ✅ Accepted — [`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md`](DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md) |
| **30** | **DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001** | Validator code | ✅ Implemented — `design_contract_validator_001.py` |
| **31** | **DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001** | Tier-1 emission wiring plan | ✅ Accepted |
| **32** | **DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001** | Tier-1 runtime emission code | ✅ Implemented |
| **33** | **DESIGN_CONTRACT_GOLDEN_FIXTURES_001** | Golden contract fixtures | ✅ Accepted |
| **34** | **DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001** | Runtime guardrails | ✅ **Implemented** |
| **35** | **DESIGN_SUITABILITY_REASSESSMENT_001** | Suitability reassessment | ✅ **Accepted** |
| **36** | **D5-DES-STAT-TIER1-001** | Tier-1 design statistical execution | ✅ **Executed** |
| **37** | **D5-DES-STAT-GREEDY-FEASIBILITY-001** | Greedy π exhaustion follow-on | ✅ **Executed** — [`D5_DES_STAT_GREEDY_FEASIBILITY_001_REPORT.md`](track_d/D5_DES_STAT_GREEDY_FEASIBILITY_001_REPORT.md) |
| **38** | **D5-DES-STAT-STRATIFIED-001** | Stratified sparse-strata follow-on | ✅ **Executed** — [`D5_DES_STAT_STRATIFIED_001_REPORT.md`](track_d/D5_DES_STAT_STRATIFIED_001_REPORT.md) |
| **39** | **D5-DES-STAT-MULTICELL-001** | DES-011 multi-cell | ✅ **Executed** — [`D5_DES_STAT_MULTICELL_001_REPORT.md`](track_d/D5_DES_STAT_MULTICELL_001_REPORT.md) |
| **40** | **D5-DES-STAT-TIER1-RECHARACTERIZATION-001** | Post-fix tier-1 baseline | ✅ **Executed** — mixed method-specific restrictions; no promotion — [`D5_DES_STAT_TIER1_RECHARACTERIZATION_001_REPORT.md`](track_d/D5_DES_STAT_TIER1_RECHARACTERIZATION_001_REPORT.md) |
| **41** | **DESIGN_COMBINATION_VALIDATION_EXECUTION_001** | Design × estimator × inference execution | **Next** |
| **42** | **DESIGN_GUARDRAIL_ENFORCEMENT_001** | Runtime guardrail enforcement | Planned |
| **—** | **TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001** | TROP parked audit program | ✅ **Proposed** — [`TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md`](TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md) |
| **15** | **METHOD_ENHANCEMENT_ROADMAP_001** | Post-Level-B synthesis | ✅ [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) |

**Controlling enhancement plan:** [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md) — deferred families (Bayesian, TBRRidge, SARIMAX, supergeo, trim, pooled multi-cell, inference wrappers) and enhancement lanes A–L.

**DL-1 AugSynth lane:** closed — evidence retained; **not** active repo-wide lane.

**Retained evidence (not sequencing authority):** AugSynth P1–P6 · [`METHOD_FOUNDATION_SYNTHESIS_001.md`](METHOD_FOUNDATION_SYNTHESIS_001.md) · Track D/F audits · pooling ADR semantics.

**Paused:** **`D5-INST-AUGSYNTH-MULTICELL-001`** as default next step · TrustReport/F-DECISION/CalibrationSignal/MMM role expansion · TrustReport product-ops (audit log, API, scheduler, platform — frozen per [`ROADMAP_REFOCUS_METHOD_VALIDATION_001.md`](audits/ROADMAP_REFOCUS_METHOD_VALIDATION_001.md)) · LLM layer · promotion audits.

**Active lanes (2026-07-04):** SCM closeout: `SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001` (immediate). **Profiler/diagnostics:** `GEO_KPI_SPEND_DATA_PROFILER_001` ✅ · `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` ✅ · `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001` ✅ · `POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001` ✅ · `POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001` ✅ · `POWER_MDE_DIAGNOSTICS_RUNTIME_001` ✅ · `DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001` ✅ · `DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001` ✅ · `DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001` ✅ · `DESIGN_CELL_STRUCTURE_RUNTIME_001` ✅ · `DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001` ✅ · `DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001` ✅ · `METHOD_SUITABILITY_HANDOFF_CONTRACT_001` ✅ · `METHOD_SUITABILITY_RUNTIME_001` ✅ · `DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001` ✅ · `DESIGN_ASSIGNMENT_RUNTIME_001` ✅ · `READOUT_METHOD_GOVERNANCE_CONTRACT_001` ✅ · `READOUT_PLAN_CONTRACT_001` ✅ · `READOUT_PLAN_RUNTIME_001` ✅ · `ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001` ✅ · `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001` ✅ · `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS` ✅ · `READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001` ✅ · `READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001` ✅ · `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR` ✅ · `READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC` ✅ · `CLAIM_AUTHORIZATION_CONTRACT_001` ✅. **P0 hardening lane (active):** `PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001` ✅ → `DID_INSTRUMENT_ESTIMAND_UNIFICATION_001` ✅ → `METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001` ✅ (docs only; blocklist enforced) → `ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001` ✅ → `STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001` ✅ → `GOVERNED_RANDOMIZATION_RUNTIME_001` ✅ → `SRM_BALANCE_READOUT_DIAGNOSTIC_001` ✅ → `CLAIM_AUTHORIZATION_RUNTIME_001` ✅ → `TRUSTED_READOUT_REPORT_CONTRACT_001` ✅. **Then:** `TRUSTED_READOUT_REPORT_RUNTIME_001` ✅ · `METHOD_PROMOTION_REVIEW_CONTRACT_001` ✅ · `METHOD_PROMOTION_REVIEW_RUNTIME_001` ✅ · `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001` ✅ · `METHOD_PROMOTION_CANDIDATE_AUDIT_001` ✅ · `SOPHISTICATED_METHOD_EVIDENCE_LADDER_001` ✅ · `MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001` ✅ · `MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_RUNTIME_001` ✅ · `TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001` ✅ · `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001` ✅ · `TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001` ✅ · `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001` ✅ · `TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001` ✅ · `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001` ✅ · `TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001` ✅ · `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001` ✅ · `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001` ✅ · `TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001` ✅ · `TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001` ✅ · `TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001` ✅ · `TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001` ✅ · `TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001` ✅ · `TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001` ✅ · `TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001` ✅ · `TBRRIDGE_DIRECTIONAL_ERROR_AUDIT_001` ✅ · `TBRRIDGE_POSITIVE_CONTROL_RECOVERY_AUDIT_001` ✅ · `TBRRIDGE_REGIME_SENSITIVITY_PLAN_001` ✅ · `TBRRIDGE_SENSITIVITY_EVIDENCE_AUDIT_BUNDLE_001` ✅ · `TBRRIDGE_METRIC_ESTIMAND_ALIGNMENT_AUDIT_001` ✅ · `METHOD_INSTRUMENT_CLASSIFICATION_POLICY_001` ✅ · `METHOD_ESTIMATOR_INFERENCE_PAIRING_COVERAGE_AUDIT_001` ✅ · `METHOD_PAIRING_VALUE_PRIORITIZATION_AUDIT_001` ✅. **Next:** `TBRRIDGE_CLAIM_AUTHORIZATION_BOUNDARY_AUDIT_001`. **Alternative:** `AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001`. **Deferred:** `PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001`. **Paused/deferred:** [`METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001`](track_d/METHOD_BLOCKLIST_REMEDIATION_AND_PROMOTION_ROADMAP_001.md). **Assignment-panel integrity:** [`ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001`](track_d/ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001_REPORT.md). **Statistical promotion thresholds:** [`STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001`](track_d/STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001_REPORT.md). **Governed randomization:** [`GOVERNED_RANDOMIZATION_RUNTIME_001`](track_d/GOVERNED_RANDOMIZATION_RUNTIME_001_REPORT.md). **SRM/balance readout diagnostic:** [`SRM_BALANCE_READOUT_DIAGNOSTIC_001`](track_d/SRM_BALANCE_READOUT_DIAGNOSTIC_001_REPORT.md). **Claim authorization runtime:** [`CLAIM_AUTHORIZATION_RUNTIME_001`](track_d/CLAIM_AUTHORIZATION_RUNTIME_001_REPORT.md). **Trusted readout report contract:** [`TRUSTED_READOUT_REPORT_CONTRACT_001`](track_d/TRUSTED_READOUT_REPORT_CONTRACT_001_REPORT.md). **Paused/deferred:** `AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001` · `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_004_BOOTSTRAP_INFERENCE` · advanced estimator production. See [`AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001.md`](track_d/AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001.md). Planned: `PANEL_EXP_AGENT_ANSWERABILITY_AND_RECOVERY_CONTRACT_001`. Downstream paused.

**SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001:** 63-row SCM validation plan (`failed_scenarios: []`). First gated production-candidate lane; point estimate not sufficient. See [`SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`](track_d/SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_REPORT.md).

**MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001:** 78-row multicell validation plan (`failed_scenarios: []`). Cross-family blocker; multiplicity/dependence validation required before any multicell production claim. See [`MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001`](track_d/MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001_REPORT.md).

**PRODUCTION_READINESS_BACKLOG_LEDGER_001:** 46-row production-readiness backlog ledger (`failed_scenarios: []`). Single control-plane backlog tracking all unfinished production-readiness items. See [`PRODUCTION_READINESS_BACKLOG_LEDGER_001`](track_d/PRODUCTION_READINESS_BACKLOG_LEDGER_001_REPORT.md).

**DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001:** 96-row selection gate requirements (`failed_scenarios: []`). Design/estimator/inference eligibility separated; selector not production-authorized. See [`DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001`](track_d/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001_REPORT.md).

**AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001:** 84-row AugSynth remediation validation plan (`failed_scenarios: []`). AugSynth diagnostic/restricted research until remediation evidence; CVXPY solver reliability required. See [`AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001`](track_d/AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001_REPORT.md).

**DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001:** 87-row DID conditional production-candidate validation plan (`failed_scenarios: []`). DID conditional only under eligible designs; production inference unauthorized. See [`DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001`](track_d/DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_REPORT.md).

**SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001:** 114-row Synthetic DID implementation-readiness plan (`failed_scenarios: []`). Implementation-readiness candidate only; unit/time-weight contracts required. See [`SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001`](track_d/SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001_REPORT.md).

**METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001:** 180-row method-family retire/replace execution plan (`failed_scenarios: []`). Retire overclaim paths; retain gated candidates; classic TBR retire/replace required. See [`METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001`](track_d/METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001_REPORT.md).

**MULTICELL_MAX_T_RESEARCH_SCOUT_001:** 50-row multicell max-T research scout (`failed_scenarios: []`). Naive per-cell p-values blocked; pooled/global inference blocked; max-T/stepdown research candidates only. See [`MULTICELL_MAX_T_RESEARCH_SCOUT_001`](track_d/MULTICELL_MAX_T_RESEARCH_SCOUT_001_REPORT.md).

**DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001:** 56-row DID suitability audit (`failed_scenarios: []`). Production inference unauthorized; bootstrap cannot fix invalid assignment. See [`DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001`](track_d/DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001_REPORT.md).

**METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001:** 9-family production compatibility and remediation roadmap (`failed_scenarios: []`). Research-only/diagnostic-only are promotion hypotheses. See [`METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001`](track_d/METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001.md).

**Post-control implementation lanes (not selected until control layer complete):** `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001` · `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001` · `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001` · `MULTICELL_MAX_T_RESEARCH_SCOUT_001` · `AUGSYNTH_ESTIMATOR_BACKED_RANDOMIZATION_CALIBRATION_001` · `SCM_AUGSYNTH_DISAGREEMENT_DIAGNOSTICS_001` · `METHOD_PROMOTION_CRITERIA_BY_FAMILY_001` · `METHOD_REPAIR_REPLACE_RETIRE_DECISION_RULES_001`

**Explicitly not next:** Ad-hoc combo OC without Layer 3–4 coverage · MCELL as method-suitability proof.

### Unresolved design guardrail blockers (DESIGN_GUARDRAILS_001)

Per [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) — **0 downstream PASS** at authoring:

| Blocker class | Guardrail | Affected |
|---------------|-----------|----------|
| Missing `geometry_id` / contract envelope | **BLOCK** | All geo designs (IV-DES-001–003) |
| Adapter-required outputs | **REQUIRES_ADAPTER** → **BLOCK** | QuickBlock, MatchedPair, TrimmedMatch, Supergeo |
| Trim/supergeo population transitions | **REQUIRES_BRIDGE** | DES-005, 009, 010 |
| Pooled multi-cell claims | **BLOCK** | DES-011 / DCM-007 |
| Statistical validation not executed | **REQUIRES_STATISTICAL_VALIDATION** | All 31 designs |
| Future Bayesian / TROP / SARIMAX | **DEFERRED** → **BLOCK** | DCM-017–019 |

**Next:** `D5-DES-STAT-TIER1-001` → executed tier-1 design statistical validation (Phase 3 evidence lane).

### Unresolved gap: schema defined, emission/validation not implemented

Per [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) — schema specified; **no `design_contract` block in `DesignEvidence`**; no validator; fixture unchanged; downstream BLOCK.

### Unresolved implementation gaps (enforcement plan must close)

Per [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) §8:

| Gap | Phase | Resolution |
|-----|-------|------------|
| IV-DES-001 `geometry_id` | 2 | Emit on DesignEvidence contract block |
| IV-DES-002 forbidden claims | 2 | Emit static list per geometry |
| IV-DES-003 concurrency | 2 | Emit compatibility enum |
| IV-DES-004 adapters | 4 | QuickBlock/MatchedPair/Trim/Supergeo |
| IV-DES-005–006 supergeo/trim metadata | 4–5 | Adapter + bridge fields |
| IV-DES-007–009 block/cell/shared-control | 2, 6 | Family-conditional emission |
| IV-DES-010 power linkage | 7 | Join PowerContract |
| IV-DES-011–014 assignment/identity caveats | 2–3 | Emission + tests |
| IV-DES-016 contract tests | 3 | New validator test suite |

### Remaining blockers preventing positive suitability

Per [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) — **0 downstream suitable designs**:

| Blocker | Suitability category | Resolution |
|---------|---------------------|------------|
| 0/31 contract-complete | `contract_blocked` | Tier-1 emission **planned** ([`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md)); **not implemented** |
| Tier-1 emission planned, not implemented | `contract_blocked` | Code emission (Phase 2) |
| Validation test plan defined, tests not implemented | `contract_blocked` | Tests (Phase 3) |
| Tier-1 emission + golden fixtures; guardrails/stat validation not wired | `contract_blocked` | Guardrail runtime (Phase 3) |
| 0/31 statistically validated | `stat_validation_required` | D5-DES-STAT-* execution |
| Adapter-required designs | `adapter_required` | QuickBlock/MatchedPair/Trim/Supergeo adapters |
| Trim/supergeo bridges | `bridge_required` | F-GEO-003/004 |
| Thinning ambiguity | `implementation_ambiguous` | Thinning ADR |
| Multi-cell metadata | `contract_blocked` | cell_ids + shared-control policy |
| Product layers | `blocked` | TrustReport/CalibrationSignal/MMM/LLM gates |

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

**Estimator readout integration (2026-06-18):** Runtime adapter wires native results to inference-boundary guardrails when opted in. TBR (DCM-003) and TBRRidge (DCM-005) remain **blocked at research** per combination registry until additional D5 statistical evidence — adapter routes correctly; guardrail BLOCK is expected, not adapter failure.

**TrustReport eligibility validation (2026-06-17):** [`TRUSTREPORT_ELIGIBILITY_VALIDATION_001_REPORT.md`](track_d/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_REPORT.md) implemented. All production-facing downstream roles remain BLOCKED.

**TrustReport remediation plan (2026-06-17):** [`TRUSTREPORT_ELIGIBILITY_REMEDIATION_PLAN_001.md`](TRUSTREPORT_ELIGIBILITY_REMEDIATION_PLAN_001.md) — SCM+JK reassessed (DCM-001); ✅ **`D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001`** confirms production DID bootstrap miscentering + canonical harness defect; ✅ **`DCM-004-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001`** reassesses DCM-004 `ELIGIBLE_WITH_RESTRICTIONS`; next: DCM-005 TBRRidge validation.

**SCM+JK harness correction (2026-06-17):** [`D5_STAT_SCM_JK_001_HARNESS_CORRECTION_REPORT.md`](track_d/D5_STAT_SCM_JK_001_HARNESS_CORRECTION_REPORT.md) — canonical D5-STAT-SCM-JK-001 archive corrected (`scm_jk_harness_corrected_level_consistent_baseline_established`).

**DCM-004 TrustReport eligibility reassessment (2026-06-18):** [`DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md`](track_d/DCM004_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md) — DCM-004 `ELIGIBLE_WITH_RESTRICTIONS` on corrected bootstrap evidence; supported null type-I ~13%; no authorization.

**D5-TRUST-TBRRIDGE-BRB-001 (2026-06-18):** [`D5_TRUST_TBRRIDGE_BRB_001_REPORT.md`](track_d/D5_TRUST_TBRRIDGE_BRB_001_REPORT.md) — BRB production defect confirmed (interval miscentering); diagnostic-only; no authorization.

**TBRRIDGE-BRB-INTERVAL-CORRECTION-001 (2026-06-18):** [`TBRRIDGE_BRB_INTERVAL_CORRECTION_001_REPORT.md`](track_d/TBRRIDGE_BRB_INTERVAL_CORRECTION_001_REPORT.md) — mean-effect centered-deviation CI; positive coverage improved; null caveat; no authorization.

**INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001 (OPEN):** [`OPEN_INVESTIGATIONS_001.json`](governance/OPEN_INVESTIGATIONS_001.json) — post-correction BRB variance ratio ~11; null coverage ~40.5%; positive coverage ~50.7%; causal-interval eligibility blocked; TrustReport authorization false.

**D5-TRUST-TBRRIDGE-KFOLD-001 (2026-06-18):** [`D5_TRUST_TBRRIDGE_KFOLD_001_REPORT.md`](track_d/D5_TRUST_TBRRIDGE_KFOLD_001_REPORT.md) — KFold not causal-interval eligible; null interval coverage 100% but level point bias ~395; sign accuracy ~1.7%; provisional DIAGNOSTIC_ONLY recommendation for INV-TBRRIDGE-KFOLD-NULL-FPR-001 (OPEN pending DCM-005); no authorization.

**D5-TRUST-TBRRIDGE-PLACEBO-001 (2026-06-22):** [`D5_TRUST_TBRRIDGE_PLACEBO_001_REPORT.md`](track_d/D5_TRUST_TBRRIDGE_PLACEBO_001_REPORT.md) — Placebo null-monitor / falsification only; single-treated restricted; null type-I 0%; power ~24%; provisional NULL_MONITOR_ONLY for INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001 (OPEN pending DCM-005); no authorization.

**DCM-005 TrustReport eligibility reassessment (2026-06-23):** [`DCM005_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md`](track_d/DCM005_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md) — BRB deferred REMEDIATE; KFold DIAGNOSTIC_ONLY; Placebo NULL_MONITOR_ONLY; no authorization.

**D5-TRUST-MULTICELL-PERCELL-INFERENCE-001 (2026-06-03):** [`D5_TRUST_MULTICELL_PERCELL_INFERENCE_001_REPORT.md`](track_d/D5_TRUST_MULTICELL_PERCELL_INFERENCE_001_REPORT.md) — DCM-006 per-cell SCM+JK; multiplicity unresolved (familywise type-I ~27%); PER_CELL_RESTRICTED; pooled blocked; no authorization.

**MULTICELL-CELL-RELATIONSHIP-AND-DECISION-POLICY-CONTRACT-001 (2026-06-03):** [`MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001.md`](MULTICELL_CELL_RELATIONSHIP_AND_DECISION_POLICY_CONTRACT_001.md) — semantic guardrail for cell_relationship × decision_policy; parallel marginal readouts not blocked; selection/pooled/global claims gated.

**D5-TRUST-STRATIFIED-SCM-JK-001 (2026-06-03):** [`D5_TRUST_STRATIFIED_SCM_JK_001_REPORT.md`](track_d/D5_TRUST_STRATIFIED_SCM_JK_001_REPORT.md) — DCM-008 per-stratum SCM+JK; diagnostic_only; aggregate claims blocked; within-stratum donor preferred; no authorization.

**FULL-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001 (2026-06-03):** [`FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md`](track_d/FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md) — matrix reassessment all governed DCM rows; global `trust_report_authorized` false; SCM Placebo and AugSynth JK resolved; BRB/multicell lanes deferred.

**TBRRIDGE-BRB-VARIANCE-CALIBRATION-REMEDIATION-001 (2026-06-03):** [`TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001_REPORT.md`](track_d/TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001_REPORT.md) — BRB variance policies characterized; `tbrridge_brb_variance_remediation_candidate_only`; null gates fail; post-remediation reassessment next.

**DCM005-TBRRIDGE-BRB-POST-REMEDIATION-REASSESSMENT-001 (2026-06-03):** [`DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001_REPORT.md`](track_d/DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001_REPORT.md) — BRB terminally `DIAGNOSTIC_ONLY`; null calibration blocked; regenerate: `poetry run python -m panel_exp.validation.dcm005_tbrridge_brb_post_remediation_reassessment_001 --overwrite`.

**TRUSTREPORT-DOWNSTREAM-PROMOTION-001 (2026-06-03):** [`TRUSTREPORT_DOWNSTREAM_PROMOTION_001_REPORT.md`](track_d/TRUSTREPORT_DOWNSTREAM_PROMOTION_001_REPORT.md) — DCM-001/004 row-level restricted promotion; global platform false; regenerate: `poetry run python -m panel_exp.validation.trustreport_downstream_promotion_001 --overwrite`.

**TRUSTREPORT-INTEGRATION-DRY-RUN-001 (2026-06-03):** [`TRUSTREPORT_INTEGRATION_DRY_RUN_001_REPORT.md`](track_d/TRUSTREPORT_INTEGRATION_DRY_RUN_001_REPORT.md) — dry-run integration check passed; regenerate: `poetry run python -m panel_exp.validation.trustreport_integration_dry_run_001 --overwrite`.

**TRUSTREPORT-RESEARCH-MODE-RENDERER-001 (2026-06-03):** [`TRUSTREPORT_RESEARCH_MODE_RENDERER_001_REPORT.md`](track_d/TRUSTREPORT_RESEARCH_MODE_RENDERER_001_REPORT.md) — research-mode renderer passed; regenerate: `poetry run python -m panel_exp.validation.trustreport_research_mode_renderer_001 --overwrite`.

**TRUSTREPORT-RESEARCH-MODE-ARTIFACT-EXPORT-001 (2026-06-03):** [`TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_REPORT.md`](track_d/TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001_REPORT.md) — sanitized artifact export passed; regenerate: `poetry run python -m panel_exp.validation.trustreport_research_mode_artifact_export_001 --overwrite`.

**TRUSTREPORT-RESEARCH-MODE-REVIEW-WORKFLOW-001 (2026-06-03):** [`TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001_REPORT.md`](track_d/TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001_REPORT.md) — research-mode review workflow passed; regenerate: `poetry run python -m panel_exp.validation.trustreport_research_mode_review_workflow_001 --overwrite`.

**TRUSTREPORT-RESEARCH-MODE-ACCESS-CONTROL-001 (2026-06-03):** [`TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001_REPORT.md`](track_d/TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001_REPORT.md) — research-mode access control passed; regenerate: `poetry run python -m panel_exp.validation.trustreport_research_mode_access_control_001 --overwrite`.

**ROADMAP-REFOCUS-METHOD-VALIDATION-001 (2026-06-03):** [`ROADMAP_REFOCUS_METHOD_VALIDATION_001.md`](audits/ROADMAP_REFOCUS_METHOD_VALIDATION_001.md) — TrustReport ops frozen after access control; `refocus_on_method_validation`; next: `INFERENCE_REPLACEMENT_SCOUT_001`.

**INFERENCE-REPLACEMENT-SCOUT-001 (2026-06-03):** [`INFERENCE_REPLACEMENT_SCOUT_001.md`](audits/INFERENCE_REPLACEMENT_SCOUT_001.md) — inference-family scout completed; primary `DESIGN_AWARE_ASSIGNMENT_GENERATORS_001`; no authorization.

**DESIGN-AWARE-ASSIGNMENT-GENERATORS-001 (2026-06-03):** [`DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_REPORT.md`](track_d/DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_REPORT.md) — assignment generator contract; `design_aware_assignment_generators_defined_no_inference_authorization`; regenerate: `poetry run python -m panel_exp.validation.design_aware_assignment_generators_001 --overwrite`.

**MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001 (2026-06-03):** [`MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001_REPORT.md`](track_d/MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001_REPORT.md) — treated-set placebo framework; `multitreated_treated_set_placebo_framework_defined_no_inference_authorization`; regenerate: `poetry run python -m panel_exp.validation.multitreated_treated_set_placebo_framework_001 --overwrite`.

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
