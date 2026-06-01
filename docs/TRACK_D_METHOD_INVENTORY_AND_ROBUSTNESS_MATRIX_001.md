# Track D — method inventory and robustness matrix 001

**Document ID:** TRACK-D-METHOD-INVENTORY-001  
**Status:** architecture design — D0 deliverable  
**Last updated:** 2026-05-28 (D1 design/matching audit)  
**Package version:** 0.2.1 (current implementation)  

**Related:** [`TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`](TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md) · [`TRACK_B_ESTIMAND_REGISTRY_001.md`](TRACK_B_ESTIMAND_REGISTRY_001.md) · [`TRACK_B_CONTRACT_TEST_PLAN_001.md`](TRACK_B_CONTRACT_TEST_PLAN_001.md) · [`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md) · [`ROADMAP_V4.md`](ROADMAP_V4.md) · [`VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) · [`METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) · [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md)

This document defines **Track D** — the statistical robustness, estimator correctness, method coverage, and literature cross-check program. **Planning and inventory only.** No estimator fixes, eligibility changes, maturity changes, release-gate changes, or instrument promotion/demotion in this phase.

---

## 1. Purpose and core principle

### Why Track D exists

Track B establishes **identity and trust contracts**:

| Track B answers | Mechanism |
|-----------------|-----------|
| What is measured? | `estimand_id` |
| How is it measured? | `measurement_instrument_id` |
| Where does identity travel? | Spec → Evidence → DiagnosticSummary → CalibrationSignal → TrustReport |
| Where is interpretation? | TrustReport only |

Track B does **not** prove that design algorithms, matching logic, estimators, inference procedures, or power methods are **mathematically correct**, **literature-aligned**, or **robust** under geo/media data generating processes.

> **Contracts prevent semantic lies.**  
> **Track D prevents statistical and mathematical lies.**

A method can pass B5 contract tests (correct IDs, no placebo-as-CI) and still be wrong, weak, or misapplied.

### Track D success criterion

Every design method, matching algorithm, estimator, inference mode, power/MDE method, diagnostic, and validation gate is:

1. **Explicitly inventoried** (no implicit coverage)  
2. **Mapped to Track B** where applicable  
3. **Literature cross-checked** ([`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md))  
4. **Audited** for math and implementation (D1–D4)  
5. **Characterized** via OC simulation (D5) when promotion is considered  
6. **Assigned a governed robustness status** before decision-grade claims  

---

## 2. Placement in roadmap

### Near-term sequence (unchanged Track B first)

| Step | Deliverable | Status (2026-05-20) |
|------|-------------|---------------------|
| B3a | Measurement Instrument Catalog | **Complete** |
| B3b | Estimand Registry | **Complete** |
| B2 | Contract Schema Draft | **Complete** |
| B4 | Adapter ID Resolution | **Complete** |
| B5 | Contract Test Plan | **Complete** |
| B5a | Golden fixture JSON | **Complete** |
| B5b | Pytest fixture loader | **Complete** |
| **B5c** | TrustReport composer contract tests | **Complete** |
| **B5d** | Track B contract validator | **Complete** |
| **M2** | Dual-write GeoX → Track B views | Planned |
| **Track D** | Statistical robustness program | **This document (D0)** |

**Trigger:** Begin D1+ execution **after** M2 dual-write so real GeoX outputs flow through governed contracts during audits (B5c/B5d complete on golden fixtures).

**D0 (this doc):** Complete. Inventory and literature templates do not require dual-write.

**Alignment:** [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) — Track D uses the **Research / robustness lane** (literature, audits, OC, negative findings allowed; not decision-eligible until promotion bridge). D1+ closes with a terminal outcome and matrix row update; promotion is a separate governed milestone.

---

## 3. Robustness status taxonomy

Every inventoried row receives exactly one **robustness status** (orthogonal to VALIDATION_COVERAGE maturity labels):

| Status | Meaning |
|--------|---------|
| **unreviewed** | Present in code/docs; no D audit started |
| **math_review_required** | Literature or implementation suspicion; needs D2 |
| **implementation_review_required** | Code path exists; correctness not verified |
| **characterization_required** | Needs D5 OC before any promotion discussion |
| **restricted** | Usable with explicit boundary (mirrors Track A/B) |
| **diagnostic_only** | Null-reference, placebo, or expert-review — not lift/decision |
| **calibration_eligible** | May support CalibrationSignal after OC + governance |
| **decision_eligible** | May support decision-grade TrustReport claims (rare; geo today: none for lift) |
| **deprecated** | Superseded; do not use for new studies |
| **blocked** | Do not use; known failure or policy closure |

**Promotion rule (D7):** Status may only advance via explicit evidence chain — no silent promotion.

---

## 4. Track B integration columns

Where applicable, each inventory row records:

| Column | Source |
|--------|--------|
| `estimand_id` | [`TRACK_B_ESTIMAND_REGISTRY_001.md`](TRACK_B_ESTIMAND_REGISTRY_001.md) |
| `measurement_instrument_id` | [`TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`](TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md) |
| `interval_semantics` | `confidence_interval` · `placebo_band` · `cumulative_att_interval` · `none` · … |
| `geometry` | `single_treated_only` · `multi_treated_default` · … |
| `supported_claim_types` | null_monitor · null_reference · point_read · lift_detection · … |
| `calibration_signal_ref` | Planning ID or archive doc |
| `trust_usage_boundary` | Mirrors signal `usage_boundary` |
| `b5_fixture_ref` | e.g. GOLD-001 |

**Gap:** Methods without a characterized instrument (e.g. unregistered QuickBlock design) still appear in inventory with `measurement_instrument_id: TBD`.

---

## 5. Design and assignment methods

**Code authority:** `panel_exp/design/` · [`design/registry.py`](../panel_exp/design/registry.py) · [`design/modes/__init__.py`](../panel_exp/design/modes/__init__.py)

| Method ID | Implementation | Geo run supported | Robustness status | Track B | Literature (D0b) | Next action |
|-----------|----------------|-------------------|-------------------|---------|------------------|-------------|
| **DES-001** | `greedy_match_markets` | Yes | **characterization_required** | Spec `design_method`; DG-007 | TBR / matched markets ([INV-D1-001](investigations/INV-D1-001_PRE_PERIOD_MATCHING_LEAKAGE.md) fix `61a174f`) | D5-DES-001a ✅; broader OC |
| **DES-002** | `thinningdesign` | Yes | implementation_review_required | TBD | Geo design | D1b / D5 |
| **DES-003** | `balancedrandomization` | Yes | implementation_review_required | TBD | Randomization inference | D5 |
| **DES-004** | `completerandomization` | Yes | implementation_review_required | TBD | Randomization | D5 |
| **DES-005** | `stratifiedrandomization` | Yes | unreviewed | TBD | Stratified experiments | D1b |
| **DES-006** | `quickblock` | No | unreviewed | TBD | Blocking designs | Defer |
| **DES-007** | `matchedpair` | No | unreviewed | TBD | Paired designs | Defer |
| **DES-008** | `trimmedmatch` | No | unreviewed | TBD | Trimmed match | Defer |
| **DES-009** | `supergeos` | No | unreviewed | TBD | Cluster/supergeo | Defer |
| **DES-010** | Rerandomization (capability on geo designs) | Partial | **characterization_required** | Spec field | Rerandomization tests ([D1](TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md)) | D5-DES-010a |
| **DES-011** | Whitelist / blacklist constraints | Partial | **restricted** | Spec + design validation | Constraint validity ([D1](TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md)) | D0b record |
| **DES-012** | Treatment–control ratio optimization | Docs/product | unreviewed | Feasibility (DEF-010) | Power literature | D4 |
| **DES-013** | Geo eligibility filtering | `design/validation.py` | **restricted** | Spec + validation_summary | Eligibility ([D1](TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md)) | D1-FIND-003 |
| **DES-014** | Heavy-up / go-dark assignment | Planned/product | unreviewed | Track C | Media experiments | Defer |
| **DES-015** | Multi-cell assignment | Product | unreviewed | Track C | Multi-arm geo | Defer |

**D1 audit questions (all design rows):** Assignment valid? Seeds reproducible? Pre-treatment-only matching? Balance metrics meaningful? Constraints enforced? Spillover/adjacency reviewed?

---

## 6. Matching algorithms

**Code authority:** `greedy_match_markets`, `design_metrics.py`, donor logic inside SCM/TBR estimators

| Match ID | Description | Used by | Robustness status | Next action |
|----------|-------------|---------|-------------------|-------------|
| **MAT-001** | Greedy market matching | DES-001 | **characterization_required** | [INV-D1-001](investigations/INV-D1-001_PRE_PERIOD_MATCHING_LEAKAGE.md) fix verified |
| **MAT-002** | Distance-based pairing (trimmed match) | DES-008 | unreviewed | Defer (not geo-run) |
| **MAT-003** | Correlation / pre-period KPI matching | Product + tests | implementation_review_required | D1b / D0b §3.3 |
| **MAT-004** | Donor pool construction (SCM) | SCM estimators | characterization_required | **D2** ✅ + D0b SCM |
| **MAT-005** | Synthetic donor eligibility / weight constraints | SCM CVXPY | characterization_required | **D2** ✅ |
| **MAT-006** | Supergeo cluster matching | DES-009 | unreviewed | Defer |
| **MAT-007** | Spend/outcome covariate matching | Docs | unreviewed | Product / D1b |

---

## 7. Estimators

**Code authority:** [`panel_exp/method_metadata.py`](../panel_exp/method_metadata.py) · `panel_exp/methods/`

| Est ID | Catalog name | Class | Maturity (today) | Robustness status | Primary instrument(s) | Next action |
|--------|--------------|-------|------------------|-------------------|----------------------|-------------|
| **EST-001** | SCM | SyntheticControl | EXPERT_REVIEW | restricted | SCM JK, Placebo | **D2** ✅ + GOLD-001/005 |
| **EST-002** | SCM CVXPY | SyntheticControlCVXPY | EXPERT_REVIEW | characterization_required | — | **D2** ✅ |
| **EST-003** | AugSynth | AugSynth | UNVALIDATED | blocked | — | **D2** ✅ |
| **EST-004** | AugSynthCVXPY | AugSynthCVXPY | EXPERT_REVIEW | restricted | AS point, AS JK | **D2** ✅ + GOLD-003 |
| **EST-005** | TBR | TBR | EXPERT_REVIEW | characterization_required | — | D2 + D0b TBR |
| **EST-006** | TBRRidge | TBRRidge | EXPERT_REVIEW | restricted | BRB, KFold, Placebo | D2 + GOLD-002 |
| **EST-007** | TBRAutoSARIMAX | TBRAutoSARIMAX | EXPERT_REVIEW | unreviewed | — | D2 |
| **EST-008** | BayesianTBR | BayesianTBR | RESEARCH_ONLY | blocked | — | D2 if revived |
| **EST-009** | BayesianTBRHorseShoe | BayesianTBRHorseShoe | RESEARCH_ONLY | blocked | — | D2 if revived |
| **EST-010** | DID | DID | EXPERT_REVIEW | restricted | DID bootstrap | D2 + GOLD-008 |
| **EST-011** | SyntheticDID | SyntheticDID | RESEARCH_ONLY | blocked | — | D2 + D0b SDID |
| **EST-012** | TROP | TROP | RESEARCH_ONLY | blocked | — | D2 |
| **EST-013** | MTGP | MTGP | RESEARCH_ONLY | blocked | — | D2 |
| **EST-014** | Naive difference / benchmark | Tests, notebooks | unreviewed | diagnostic_only | — | D2 |

---

## 8. Inference methods

**Code authority:** [`panel_exp/inference/`](../panel_exp/inference/) · inference registry

| Inf ID | Mode | Interval semantics | Robustness status | Characterized instrument | Known issues |
|--------|------|-------------------|-------------------|-------------------------|--------------|
| **INF-001** | point_estimate | none | diagnostic_only | AugSynth point, many | No uncertainty |
| **INF-002** | UnitJackKnife | confidence_interval | null_monitor_characterized | SCM JK, AugSynth JK | **INV-D3-001 fix accepted** (D5-INF-002b); FPR≈0, power≈0 |
| **INF-003** | JKP | confidence_interval | characterization_required | — | Registry tests only |
| **INF-004** | Kfold | confidence_interval | restricted | TBRRidge KFold | DEF-001; not calibration-eligible |
| **INF-005** | BlockResidualBootstrap | confidence_interval | restricted | TBRRidge BRB | DEF-002 positive OC |
| **INF-006** | Placebo | placebo_band | diagnostic_characterized | SCM/TBR Placebo | Not CI; single-treated; DEF-020 |
| **INF-007** | Conformal | conformal_interval | characterization_required | — | **D3** ✅ assumption audit pending D5 |
| **INF-008** | Bayesian (registry) | credible_interval | blocked | — | Not full BayesianTBR |
| **INF-009** | TimeSeriesKfold | confidence_interval | characterization_required | — | **D3** ✅ temporal blocking |
| **INF-010** | DID bootstrap | cumulative_att_interval | restricted | DID | DEF-003 relative unsupported |

---

## 9. Power and MDE methods

**Code authority:** `panel_exp/design/power.py` · notebooks · product docs

| Pow ID | Method | Robustness status | Track B link | Next action |
|--------|--------|-------------------|--------------|-------------|
| **POW-001** | Simulation-based power (design) | diagnostic_only | Feasibility DEF-010; D5-POW-001a **optimistic_proxy** vs SCM JK | **D4** ✅ **D5-POW-001a** ✅ |
| **POW-002** | Formula MDE (variance-based) | diagnostic_only | Spec `mde_target` (not wired) | **D4** ✅ |
| **POW-003** | Geo-level power (aggregated panel) | restricted | TBRRidge+Kfold ≠ SCM JK readout; D5-POW-001a confirms optimistic_proxy | **D4** ✅ **D5-POW-001a** ✅ |
| **POW-004** | Multi-cell power | blocked | Track C | Defer |
| **POW-005** | Business ROI detectability | diagnostic_only | TrustReport profile | **D4** ✅ |
| **POW-006** | Long-term holdout power | blocked | Holdout Track C | Defer |

**D4 principle:** Power method must match **readout estimator + estimand_id**, not a generic “lift %.”

---

## 10. Diagnostics and validation gates

| Diag ID | Diagnostic / gate | Location | Robustness status | Track B facet |
|---------|-------------------|----------|-------------------|---------------|
| **DG-001** | Pre-period fit / residual drift | `review_flags` | implementation_review_required | DiagnosticSummary |
| **DG-002** | Donor concentration / instability | `review_flags` | implementation_review_required | DiagnosticSummary |
| **DG-003** | Pretrend (DID) | `did_pretrend_contract` | implementation_review_required | DiagnosticSummary |
| **DG-004** | Fold instability | `review_flags` | implementation_review_required | KFold facet |
| **DG-005** | Placebo / null-reference | inference + flags | restricted | GOLD-005 |
| **DG-006** | Spillover / interference | `build_interference_review` | characterization_required | DEF-004 |
| **DG-007** | Design validation gate | `design/validation.py` | implementation_review_required | ExperimentSpec |
| **DG-008** | Readiness assessment | `policy/readiness.py` | diagnostic_only | **Not** TrustReport |
| **DG-009** | Nominal calibration check | `nominal_calibration.py` | calibration_eligible | SCM JK only |
| **DG-010** | Recovery / OC batteries | `recovery_runner.py` | characterization_required | CalibrationSignal |
| **DG-011** | Maturity evidence | `maturity_evidence.py` | diagnostic_only | Advisory only |
| **DG-012** | SRM-style checks | Planned Track C | unreviewed | INV-025 |
| **DG-013** | KPI missingness / freshness | Product | unreviewed | D6 runtime |

---

## 11. Measurement instruments (Track B catalog cross-reference)

Full instrument rows live in [`TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`](TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md). Track D adds **robustness overlay**:

| Instrument ID | Catalog tier | Track D robustness | D5 OC required for promotion? |
|---------------|--------------|--------------------|---------------------------------|
| SCM + UnitJackKnife | Governed | diagnostic_only (null monitor) | Already archived; maintain |
| SCM + Placebo | Governed | diagnostic_only | Phase 15 archive |
| TBRRidge + BRB | Restricted | restricted | Run 002 + repair backlog |
| TBRRidge + KFold | Restricted | restricted | INV-007 |
| AugSynthCVXPY + Point | Restricted | restricted | Phase 14 |
| AugSynthCVXPY + JK | Characterized | diagnostic_only | Phase 14 |
| DID + Bootstrap | Characterized | restricted | DEF-016 |

---

## 12. Track D work packages (D1–D8)

| ID | Package | Output doc (planned) |
|----|---------|-------------------|
| **D0** | Inventory + matrix (this doc) | TRACK-D-METHOD-INVENTORY-001 |
| **D0b** | Literature cross-check | [`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md) |
| **D1** | Design + matching correctness | [`TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md`](TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md) ✅ |
| **D2** | Estimator math audit | `TRACK_D_ESTIMATOR_MATH_AUDIT_001.md` |
| **D3** | Inference audit + repair backlog | `TRACK_D_INFERENCE_AUDIT_001.md` |
| **D4** | Power / MDE audit | [`TRACK_D_D4_POWER_MDE_AUDIT_001.md`](TRACK_D_D4_POWER_MDE_AUDIT_001.md) ✅ |
| **D5** | OC simulation harness | `TRACK_D_OC_SIMULATION_SPEC_001.md` |
| **D6** | Runtime monitoring gates | `TRACK_D_RUNTIME_DIAGNOSTICS_001.md` |
| **D7** | Promotion / demotion framework | `TRACK_D_INSTRUMENT_PROMOTION_001.md` |
| **D8** | Cross-method triangulation | `TRACK_D_CONFLICT_POLICY_001.md` |

---

## 13. Finding governance (no orphan findings)

Every Track D finding must resolve to:

| Disposition | DEF / INV update |
|-------------|------------------|
| **fixed** | Close or reference fix commit |
| **deferred** | New or updated DEF-xxx |
| **accepted_deviation** | Document in literature cross-check |
| **rejected** | Blocked status on inventory row |
| **escalated** | OPEN_INVESTIGATIONS entry |
| **investigating** | INV-xxx open |
| **deprecated** | Inventory status + catalog |
| **blocked** | Inventory status + TrustReport boundary |

Track D updates **feed** Track B artifacts — not replace identity rules.

---

## 14. Non-goals (D0)

| Non-goal | Notes |
|----------|-------|
| Implement fixes | D1+ execution |
| Change estimator behavior | Out of scope |
| Change eligibility / maturity / release gates | Out of scope |
| Promote or demote instruments | D7 only after evidence |
| Replace Track B contracts | Complementary layer |
| Certify from papers alone | D0b requires implementation + OC |

---

## Appendix A — Coverage matrix summary

| Family | Count (inventoried) | Reviewed | Characterized | Decision-eligible |
|--------|---------------------|----------|---------------|-------------------|
| Design | 15 | 9 (D1 geo scope) | 0 | 0 |
| Matching | 7 | 4 (D1 scope) | 0 | 0 |
| Estimators | 14 | Partial (Track A) | Partial | 0 |
| Inference | 10 | Partial | Partial | 0 |
| Power/MDE | 6 | 0 | 0 | 0 |
| Diagnostics | 13 | Partial | Partial | 0 |

**Headline:** Platform has **clean contracts** (Track B) and **partial OC** (Track A) but **no comprehensive D audit** across all methods — Track D closes that gap.

---

## Appendix B — Risk classification

| Risk class | Examples | Track D response |
|------------|----------|------------------|
| **R1 Semantic** | Placebo as CI, cumulative vs relative | Track B + B5 fixtures |
| **R2 Estimand** | A vs B aggregation | B3b + GOLD-009 |
| **R3 Math** | Wrong weights, wrong window | D2 |
| **R4 Inference** | Zero power, wrong coverage | D3 + D5 |
| **R5 Design** | Invalid assignment | D1 |
| **R6 Power** | MDE ≠ readout | D4 |
| **R7 Runtime** | Spend drift, SRM | D6 |
| **R8 Conflict** | Averaging SCM + TBR | D8 |

---

*Planning artifact TRACK-D-METHOD-INVENTORY-001. D0 complete. Begin D0b literature records per method family.*
