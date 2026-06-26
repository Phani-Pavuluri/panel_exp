# panel_exp roadmap v4 (post Phase 8 / Run 001)

**Status:** active (Phases 11–15 scoped; priorities frozen; Tracks A / B / C)  
**Last reviewed:** 2026-06-03  
**Supersedes:** `docs/ROADMAP_V3.md` (Phases 5–8 execution and v3 priority ordering)  
**Package version:** 0.2.1  

**Companion documents:**

| Document | Role |
|----------|------|
| [`docs/OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) | Phase 12 historical investigations ledger; Track C IDs INV-020–026 |
| [`docs/governance/OPEN_INVESTIGATIONS_001.json`](governance/OPEN_INVESTIGATIONS_001.json) | **Authoritative machine-readable open investigations** (Track D trust lanes) |
| [`docs/INVESTIGATION_LIFECYCLE_AND_HANDOFF_CONTRACT_001.md`](INVESTIGATION_LIFECYCLE_AND_HANDOFF_CONTRACT_001.md) | Investigation lifecycle, artifact handoff schema, CI enforcement |
| [`docs/ROADMAP_V3.md`](ROADMAP_V3.md) | Phases 5–8 history and shipped measurement-honesty work |
| [`docs/ROADMAP_V3_EXECUTION_ORDER.md`](ROADMAP_V3_EXECUTION_ORDER.md) | Frozen execution spec for Phases 5–8 |
| [`docs/CALIBRATION_RUN_001.md`](CALIBRATION_RUN_001.md) | Production nominal calibration evidence (n=100) |
| [`docs/CALIBRATION_FAILURE_ANALYSIS_001.md`](CALIBRATION_FAILURE_ANALYSIS_001.md) | Run 001 diagnosis and eligibility tightening |
| [`docs/METHOD_VALIDATION_PLAN.md`](METHOD_VALIDATION_PLAN.md) | Per-estimator validation paths A–E |
| [`docs/VALIDATION_COVERAGE.md`](VALIDATION_COVERAGE.md) | Estimator × scenario × inference matrix |
| [`docs/PHASE8_ALGORITHM_AUDIT.md`](PHASE8_ALGORITHM_AUDIT.md) | Focused mini-audit (superseded in part by Run 001 archive) |
| [`docs/GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md`](GEOX_PANEL_EXP_STRATEGIC_CHECKPOINT.md) | Architecture milestone snapshot; Track A/B framing |
| [`docs/SCM_JACKKNIFE_CHARACTERIZATION_001.md`](SCM_JACKKNIFE_CHARACTERIZATION_001.md) | Phase 11 OC archive (complete) |

| [`docs/PHASE12_INVESTIGATION_PLAN.md`](PHASE12_INVESTIGATION_PLAN.md) | Phase 12 governed investigation plan (pre-execution) |
| [`docs/ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) | **Alignment gate** — north star, six questions, stop conditions per item |
| [`docs/MIP_PERIODIC_ARCHITECTURE_AND_ROBUSTNESS_AUDIT_TEMPLATE.md`](MIP_PERIODIC_ARCHITECTURE_AND_ROBUSTNESS_AUDIT_TEMPLATE.md) | **Periodic audit** — “building the right thing, correctly?” |
| [`docs/MIP_AUDIT_REGISTRY.md`](MIP_AUDIT_REGISTRY.md) | Audit index and follow-ups |

**Read-only roadmap — no package code in this document.**

**Alignment:** Every active execution item must satisfy [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) before start and at completion.

**Periodic audit (MIP-PERIODIC-AUDIT):** After major milestones and before production-promotion, run the [audit template](MIP_PERIODIC_ARCHITECTURE_AND_ROBUSTNESS_AUDIT_TEMPLATE.md) and update the [audit registry](MIP_AUDIT_REGISTRY.md). Cadence: after B5d, after M2, after Track D D1/D2/D3, **before MMM intake readiness/gap audit (AUDIT-010)**, before planning/optimizer, before LLM interface. Not a substitute for tests or Track D OC.

**Conceptual reference (not implementation blueprint):** Industry conversion-lift and user-level incrementality practice (e.g. Google Conversion Lift methodology — ghost ads, exposure-opportunity logging, user-randomized designs) informs **Track C governance semantics only**. Do not copy external estimators or certify parity without archived OC.

---

## Multi-track roadmap (post checkpoint)

The roadmap **bifurcates and extends** after the GeoX strategic checkpoint. **Not in scope:** random estimator expansion.

### Track A — evidence / governance stabilization

**Objective:** Make causal claims honest, bounded, and auditable.

| Work | Examples |
|------|----------|
| Operating-characteristic characterization | Phase 11 SCM (done); Phase 12 TBRRidge investigation program; Phase 14 DID |
| Calibration archives | Run 001; Run 002 (post–BRB merge) |
| Failure analysis + eligibility | Registry skip reasons; no threshold tuning |
| Investigation ledger | `OPEN_INVESTIGATIONS.md` — deferred ≠ abandoned |
| Correctness preservation | **Merge BRB bound-ordering fix** (not re-promotion) |
| Governed measurement instruments | Per-estimator: estimand, interval, OC, failure analysis, usage boundary |

**Moat here:** evidence lineage, calibration honesty, estimator governance, explainable trust.

### Track B — experimentation-platform evolution

**Objective:** Unified experimentation architecture inside MIP (mid-term, after Phase 12 stabilizes).

| Work | Examples |
|------|----------|
| Shared abstractions (future) | `ExperimentSpec`, `ExperimentEvidence`, `Estimand`, `DiagnosticSummary`, `CalibrationSignal`, `TrustReport`, `RecommendationContext`, `ReleaseGate` |
| GeoX + A/B + MMM convergence | Shared contracts across geo, conversion lift, budget optimization |
| Experiment memory + calibration exchange | Cross-study reuse; trust-aware recommendations |
| LLM orchestration reference | Grounded in investigations + runs; no unsourced promotion |

Detail: [`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md).

**Track A is gate for Track B** — do not build unified abstractions before TBRRidge OC and governance stabilize.

#### Track B execution status (2026-05-20)

Architecture contracts and test discipline (planning + fixtures; implementation in progress):

| Artifact | Doc | Status |
|----------|-----|--------|
| B3a Measurement Instrument Catalog | [`TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`](TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md) | Complete |
| B3b Estimand Registry | [`TRACK_B_ESTIMAND_REGISTRY_001.md`](TRACK_B_ESTIMAND_REGISTRY_001.md) | Complete |
| B2 Contract Schema Draft | [`TRACK_B_CONTRACT_SCHEMA_DRAFT_001.md`](TRACK_B_CONTRACT_SCHEMA_DRAFT_001.md) | Complete |
| B4 Adapter ID Resolution | [`TRACK_B_ADAPTER_ID_RESOLUTION_001.md`](TRACK_B_ADAPTER_ID_RESOLUTION_001.md) | Complete |
| B5 Contract Test Plan | [`TRACK_B_CONTRACT_TEST_PLAN_001.md`](TRACK_B_CONTRACT_TEST_PLAN_001.md) | Complete |
| B5a Golden fixtures | [`tests/fixtures/track_b_contracts/`](../tests/fixtures/track_b_contracts/) | Complete |
| B5b Pytest loader | [`tests/track_b/`](../tests/track_b/) | Complete |
| B5c TrustReport composer tests | [`tests/track_b/trust_report_composer.py`](../tests/track_b/trust_report_composer.py) | **Complete** |
| B5d Contract validator | [`tests/track_b/contract_validator.py`](../tests/track_b/contract_validator.py) | **Complete** |
| M2 Dual-write | [`panel_exp/track_b/`](../panel_exp/track_b/) · [`TRACK_B_ARTIFACT_CONSOLIDATION_001.md`](TRACK_B_ARTIFACT_CONSOLIDATION_001.md) | **Complete** (AUDIT-002 `2754c0a`) |
| M2.1 Adapter production wire-up | [`panel_exp/track_b/bundle_extract.py`](../panel_exp/track_b/bundle_extract.py) · [`export.py`](../panel_exp/track_b/export.py) | **Complete** ([AUDIT-003](audits/AUDIT-003_m2_1_wire_up_gate.md) `5000fc5`) |
| M2.2 Production TrustReport path | [`trust_report.py`](../panel_exp/track_b/trust_report.py) · [`geo_run_export.py`](../panel_exp/artifacts/geo_run_export.py) | **Complete** ([AUDIT-004](audits/AUDIT-004_m2_2_trust_report_gate.md) `ec2d351`) |

**Near-term sequence:** … **Track E E3/E4** **complete** · **Track E E5/E6** **complete** · **Track E E7** **complete** · not MMM yet.

**Alignment registry:** [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) § Track B — per-item capability, risk, artifacts, stop conditions.

### Track D — statistical robustness, method coverage, literature cross-check

**Roadmap ID:** `TRACK-D-STATISTICAL-ROBUSTNESS`  
**Status:** planned (D0/D0b architecture started)  
**Trigger:** Begin D1+ execution after **M2 adapter wire-up** on representative real GeoX RunBundles (M2 dual-write complete per [AUDIT-002](audits/AUDIT-002_m2_dual_write.md)). D0 inventory may proceed in parallel — **do not skip AUDIT-002 gate before D1**.

**Alignment registry:** [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) § Track D.

**Purpose:** Harden the **scientific core** — every design method, matching algorithm, estimator, inference mode, power/MDE method, diagnostic, and validation gate is inventoried, literature-checked, implementation-audited, simulation-characterized, mapped to Track B identity, and assigned a governed robustness status before calibration or decision-grade claims.

**Core principle:** Contracts prevent semantic lies (Track B). Track D prevents statistical and mathematical lies.

**Lane:** Track D execution is **research / robustness** by default — ambitious literature-backed and statistical work is encouraged under [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) § Research / robustness lane. Outputs are not production-, calibration-, or decision-eligible until the promotion bridge completes.

| Package | Document | Status |
|---------|----------|--------|
| **D0** | [`TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md`](TRACK_D_METHOD_INVENTORY_AND_ROBUSTNESS_MATRIX_001.md) | Complete (planning) |
| **D0b** | [`TRACK_D_LITERATURE_CROSSCHECK_001.md`](TRACK_D_LITERATURE_CROSSCHECK_001.md) | Complete (template) |
| D1 | Design + matching audit | **Complete** ([`TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md`](TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md)) |
| D2 | Estimator + SCM donor audit | **Complete** ([`TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md`](TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md)) |
| D3 | Inference method audit | **Complete** ([`TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md`](TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md)) |
| D4 | Power / MDE audit | **Complete** ([`TRACK_D_D4_POWER_MDE_AUDIT_001.md`](TRACK_D_D4_POWER_MDE_AUDIT_001.md)) |
| D5 | OC simulation harness | In progress (001a–e ✅; DESIGN-INVENTORY-001 ✅; readout update ✅) |
| D6 | Runtime monitoring | Planned |
| D7 | Promotion / demotion framework | Planned |
| D8 | Cross-method triangulation | Superseded by **Track E** (governance layer) |

**Non-goals:** No new estimator promotion without OC; no eligibility/maturity changes without governance; no silent averaging of conflicting methods; no paper-based trust without implementation validation; no Track B identity rule changes without explicit ADR.

**Success criteria:** Every method explicitly inventoried, literature-checked, audited, characterized where needed, mapped to `estimand_id` / `measurement_instrument_id`, and status-governed before decision-grade claims.

#### Design-readout OC framing ([ROADMAP-DESIGN-READOUT-UPDATE-001](ROADMAP_DESIGN_READOUT_UPDATE_001.md))

Power/OC evidence is **design-method × geometry-mode × measurement-instrument** specific—not one universal readout.

| Concept | Governance |
|---------|------------|
| **SCM+UnitJackKnife** | **Reference** null-monitor branch for fixed-window unit-level OC (D5-POW-001b/d); **not** universal GeoX readout, platform MDE, or lift detection |
| **Multi-cell** | **Geometry mode** (`n_test_grps > 1`); not a design method class |
| **supergeos** | **D5-DES-SUPERGEO-001** ✅ [`D5_DES_SUPERGEO_001_results.json`](track_d/archives/D5_DES_SUPERGEO_001_results.json) — separate geometry; blocked for 001e |
| **trimmedmatch** | **D5-DES-TRIM-001** ✅ [`D5_DES_TRIM_001_results.json`](track_d/archives/D5_DES_TRIM_001_results.json) — separate population; blocked for 001e |
| **Multi-cell k** | **D5-MCELL-001** ✅ [`D5_MCELL_001_results.json`](track_d/archives/D5_MCELL_001_results.json) — k≤2 typical; k≥3 degrades |
| **TBRRidge OC** | **D5-INST-TBRRIDGE-001** ✅ [`D5_INST_TBRRIDGE_001_results.json`](track_d/archives/D5_INST_TBRRIDGE_001_results.json) — remain restricted |
| **Placebo OC** | **D5-INST-PLACEBO-001** ✅ [`D5_INST_PLACEBO_001_results.json`](track_d/archives/D5_INST_PLACEBO_001_results.json) — remain diagnostic_only |
| **Instrument inventory** | **D5-INST-AUDIT-001** ✅ [`D5_INST_AUDIT_001_results.json`](track_d/archives/D5_INST_AUDIT_001_results.json) — estimator × inference × geometry matrix |
| **AugSynth OC** | **D5-INST-AUGSYNTH-001** ✅ [`D5_INST_AUGSYNTH_001_results.json`](track_d/archives/D5_INST_AUGSYNTH_001_results.json) — diagnostic_only; characterized comparator |
| **Combo compatibility** | **D5-INST-COMBO-AUDIT-001** ✅ [`D5_INST_COMBO_AUDIT_001_results.json`](track_d/archives/D5_INST_COMBO_AUDIT_001_results.json) — curated matrix; no Cartesian OC |
| **Conceptual validity** | **TRACK-D-CONCEPTUAL-VALIDITY-AUDIT-001** ✅ [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md) — literature/method fidelity; synthetic OC ≠ paper validity; prerequisite for AUDIT-010 |
| **AugSynth Kfold OC** | **D5-INST-AUGSYNTH-KFOLD-001** ✅ [`D5_INST_AUGSYNTH_KFOLD_001_results.json`](track_d/archives/D5_INST_AUGSYNTH_KFOLD_001_results.json) — restricted diagnostic comparator |
| **AugSynth Conformal OC** | **D5-INST-AUGSYNTH-003** ✅ [`D5_INST_AUGSYNTH_003_results.json`](track_d/archives/D5_INST_AUGSYNTH_003_results.json) — callable; interval semantics unverified |
| **Track F P2 closeout** | **TRACK-F-P2-CLOSEOUT-001** ✅ [`TRACK_F_P2_CLOSEOUT_001.md`](TRACK_F_P2_CLOSEOUT_001.md) — P2 closed; implementation backlog active |
| **F-INF-001 contract** | ✅ [`F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md`](F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md) — interval semantics classification |
| **F-GEO-001 contract** | ✅ [`F_GEO_001_GEOMETRY_ADAPTER_CONTRACT.md`](F_GEO_001_GEOMETRY_ADAPTER_CONTRACT.md) — geometry adapter rules; depends on F-INF-001 |
| **F-CAT-001 catalog** | ✅ [`F_CAT_001_REGISTRY_CATALOG_CLEANUP.md`](F_CAT_001_REGISTRY_CATALOG_CLEANUP.md) — registry/catalog metadata aligned with F-INF + F-GEO |
| **F-BACKLOG-001 closeout** | ✅ [`F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md`](F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md) — prioritized implementation queue |
| **F-BACKLOG-002 relevance** | ✅ [`F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md`](F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md) — industry/literature re-rank; investigation only (no promotion) |
| **F-INF-003 fix** | ✅ [`F_INF_003_INTERVAL_ORIENTATION_FIX.md`](F_INF_003_INTERVAL_ORIENTATION_FIX.md) — Conformal/TimeSeriesKfold orientation |
| **D5-INF-POSTFIX-001** | ✅ [`D5_INF_POSTFIX_001_REPORT.md`](track_d/D5_INF_POSTFIX_001_REPORT.md) — A05/A19 targeted OC post-fix |
| **Class TBR OC** | **D5-INST-TBR-001** ✅ [`D5_INST_TBR_001_results.json`](track_d/archives/D5_INST_TBR_001_results.json) — aggregate 1×1 restricted diagnostic |
| **Roadmap consistency** | **AUDIT-010A** ✅ [`audits/AUDIT-010A_roadmap_consistency_pre_mmm_gate.md`](audits/AUDIT-010A_roadmap_consistency_pre_mmm_gate.md) — pre-MMM sanity check |
| **MMM readiness / gap** | **AUDIT-010** ✅ [`audits/AUDIT-010_mmm_readiness_gap.md`](audits/AUDIT-010_mmm_readiness_gap.md) — `not_ready_continue_track_f`; Appendix A = 30 tuples |
| **D5-POW-001e** | ✅ Six confirmed methods; SCM+JK reference null FPR; [`D5_POW_001e_results.json`](track_d/archives/D5_POW_001e_results.json) — `acceptable_with_caveats` |

**Next steps:** … → ~~**GOVERNANCE-PR-TRACK-F-DECISION-PACKAGE-001**~~ ✅ → ~~**TRUSTREPORT-F-DECISION-INTEGRATION-001**~~ ✅ → promotion **only if** future governance PR allows (not authorized).

### Track F — implementation checkpoint (2026-06-03)

**Document:** [`TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md`](TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md)  
**Verdict:** Active fix→OC loop **paused**; contracts + F-INF-003/002 + POSTFIX/TBRRIDGE-003 complete; governed uncertainty ∅; optional **F-INF-004** only on product pull.

### F-DECISION-001 — method eligibility and evidence decision policy

**Document:** [`F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md`](F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md)  
**Code:** [`panel_exp/governance/decision_policy.py`](../panel_exp/governance/decision_policy.py)  
**Verdict:** Resolver assigns roles (null monitor / diagnostic / falsification / excluded) and evidence posture **without** promotion, MMM, or CalibrationSignal expansion.

### GOVERNANCE-PR-TRACK-F-DECISION-PACKAGE-001 — governance PR summary

**Document:** [`GOVERNANCE_PR_TRACK_F_DECISION_PACKAGE_001.md`](GOVERNANCE_PR_TRACK_F_DECISION_PACKAGE_001.md)  
**Verdict:** Packages checkpoint + F-DECISION-001 + F-BACKLOG-002; confirms production-safe decision posture; **next authorized step = TrustReport integration** (separate PR; no wiring in this package).

### TRUSTREPORT-F-DECISION-INTEGRATION-001

**Document:** [`TRUSTREPORT_F_DECISION_INTEGRATION_001.md`](TRUSTREPORT_F_DECISION_INTEGRATION_001.md)  
**Code:** [`panel_exp/track_b/f_decision_context.py`](../panel_exp/track_b/f_decision_context.py) · [`trust_report.py`](../panel_exp/track_b/trust_report.py)  
**Verdict:** Optional `f_decision_context` on TrustReport; backward compatible; guardrails asserted at build; no promotion/MMM/CS expansion.

### TRUSTREPORT-DECISION-INPUTS-WIRING-001

**Document:** [`TRUSTREPORT_DECISION_INPUTS_WIRING_001.md`](TRUSTREPORT_DECISION_INPUTS_WIRING_001.md)  
**Code:** [`readout_evidence_wiring.py`](../panel_exp/track_b/readout_evidence_wiring.py)  
**Verdict:** Opt-in `include_trust_report_decision_context` on Geo RunBundle export; builds readout evidence from bundle metadata; default off.

### TRUSTREPORT-DECISION-CONTEXT-SMOKE-001

**Document:** [`TRUSTREPORT_DECISION_CONTEXT_SMOKE_001.md`](TRUSTREPORT_DECISION_CONTEXT_SMOKE_001.md)  
**Artifact:** [`track_b/archives/TRUSTREPORT_DECISION_CONTEXT_SMOKE_001_export.json`](track_b/archives/TRUSTREPORT_DECISION_CONTEXT_SMOKE_001_export.json)  
**Verdict:** End-to-end export smoke — `f_decision_context` present when opted in, absent when off; guardrails on representative fixture.

### METHOD-READINESS-AND-COMPATIBILITY-MATRIX-001

**Document:** [`METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md`](METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md)  
**Verdict:** Layered L1 estimator · L2 inference · L3 combination matrix; input F-BACKLOG-002; **0** promotion-ready combinations; separates conceptual strength from combination validity.

### Method selection / promotion layer

**Document:** [`METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md`](METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md)  
**Verdict:** Positive promotion pipeline on top of L1/L2/L3 matrix; A26 = conservative baseline (not permanent winner); benchmark + **METHOD-PROMOTION-AUDIT-TEMPLATE-001** required for role upgrades; **0** promotions in v1.

**Future:** [`METHOD_PROMOTION_AUDIT_TEMPLATE_001`](METHOD_PROMOTION_AUDIT_TEMPLATE_001.md) (placeholder) — required gate per role × data structure.

### METHOD-STRENGTHENING-LANES-001

**Document:** [`METHOD_STRENGTHENING_LANES_001.md`](METHOD_STRENGTHENING_LANES_001.md)  
**Verdict:** Evidence-building lanes between [`METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001`](METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md) and future OC/ADR/promotion audits; five first lanes (AugSynth/ASCM, TBR aggregate, multi-cell, trim/supergeo, BayesianTBR/TROP); **no** production role change.

**Bridge:** METHOD-SELECTION (pipeline) → **METHOD-STRENGTHENING** (this doc) → OC / ADR / charter → METHOD-PROMOTION-AUDIT-TEMPLATE-001 → F-DECISION amendment.

### AUGSYNTH-ASCM-STRENGTHENING-001

**Document:** [`AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md)  
**Verdict:** First strengthening charter — when AugSynth/ASCM may challenge A26 on unit-panel geo; diagnostics §5; **D5-INST-AUGSYNTH-ASCM-002** executed. **No promotion**; AugSynth not primary.

**Prior OC (inputs):** D5-INST-AUGSYNTH-001 · 003 · KFOLD — do not satisfy weak-fit stratification alone.

### D5-INST-AUGSYNTH-ASCM-002

**Report:** [`track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md)  
**Artifact:** [`track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json`](track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json)  
**Harness:** [`track_d_d5_inst_augsynth_ascm_002.py`](../panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py)  
**Verdict:** `remain_diagnostic_comparator` — stratified OC complete; AugSynth point MAE beats A26 on **1/2** weak-fit worlds @ 8%; JK null FPR 0 on battery; **no** promotion.

### AUGSYNTH-ASCM-INFERENCE-PAIRING-ADR-001

**Document:** [`AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md)  
**Verdict:** **Accepted** — no AugSynth inference pairing promoted; Conformal **keep_restricted**; JK **more OC only**; KFold diagnostic; Placebo falsification-only; A26 baseline unchanged.

### METHOD-FOUNDATION-HARDENING-001

**Document:** [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md)  
**Verdict:** Pre-LLM scientific hardening phase — **LLM layer paused**; gap table; lanes P0 ✅ → P1 threshold audit ✅ (calibration via ASCM-003) → P2–P5. **No promotion.**

**Bridge:** METHOD-STRENGTHENING + Track D OC → **FOUNDATION HARDENING** → **METHOD-SOUNDNESS-AND-GAP-ROADMAP-001** → **METHOD-VALIDATION-PROGRAM-001** (authoritative) → suitability framework → AUDIT-011 / LLM (future).

### METHOD-VALIDATION-PROGRAM-001

**Document:** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md)  
**Status:** **active** — authoritative method-foundation sequence  
**Verdict:** **Pauses** trust-framework / method-role expansion until layers 1–5 complete (code inventory → literature → implementation → statistical OC → combination matrix). Prior synthesis and MCELL-first chains are **evidence only**, not sequencing authority.

**Combination-validation scopes (do not conflate):**

| Scope | Artifact | Role |
|-------|----------|------|
| **DCM-001–019** | [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) | Design-side compatibility and geometry matrix |
| **Layer-5 (30 rows)** | [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) | Estimator × inference validation with reference designs |
| **DCM-001–008** | [`TRUSTREPORT_ELIGIBILITY_VALIDATION_001_REPORT.md`](track_d/TRUSTREPORT_ELIGIBILITY_VALIDATION_001_REPORT.md) | Deliberately narrower TrustReport eligibility / promotion subset |

**TrustReport qualification spine (active):**

```
Foundation and compatibility audits ✅
  → DCM-001 SCM-JK correction + partial reassessment ✅
  → governance scope reconciliation ✅
  → DCM-004 DID remediation (`D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001`) ✅
  → D5-STAT-DID-BOOTSTRAP-001 harness correction ✅
  → DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001 ✅
  → DCM-004 eligibility reassessment (post-production correction) ✅
  → D5-TRUST-TBRRIDGE-BRB-001 ✅
  → TBRRIDGE_BRB_INTERVAL_CORRECTION_001 ✅
  → INV-TBRRIDGE-BRB-VARIANCE-CALIBRATION-001 (DEFERRED_WITH_TRIGGER) ✅
  → D5-TRUST-TBRRIDGE-KFOLD-001 ✅
  → D5-TRUST-TBRRIDGE-PLACEBO-001 ✅
  → DCM-005 eligibility reassessment ✅
  → DCM-006 multi-cell per-cell inference validation ✅
  → MULTICELL cell-relationship decision-policy contract ✅
  → D5-TRUST-STRATIFIED-SCM-JK-001 ✅
  → FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT (all DCM-001–008 rows) ✅
  → TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001 ✅
  → DCM005_TBRRIDGE_BRB_POST_REMEDIATION_REASSESSMENT_001 ✅
  → TRUSTREPORT_DOWNSTREAM_PROMOTION_001 ✅
  → TRUSTREPORT_INTEGRATION_DRY_RUN_001 ✅
  → TRUSTREPORT_RESEARCH_MODE_RENDERER_001 ✅
  → TRUSTREPORT_RESEARCH_MODE_ARTIFACT_EXPORT_001 ✅
  → TRUSTREPORT_RESEARCH_MODE_REVIEW_WORKFLOW_001 ✅
  → TRUSTREPORT_RESEARCH_MODE_ACCESS_CONTROL_001 ✅
  → ROADMAP_REFOCUS_METHOD_VALIDATION_001 ✅ (TrustReport ops **frozen**; method validation active)
  → INFERENCE_REPLACEMENT_SCOUT_001 ✅ (design generators primary; placebo secondary)
  → DESIGN_AWARE_ASSIGNMENT_GENERATORS_001 ✅
  → MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001 ✅
  → SCM_PLACEBO_GOVERNED_SEMANTICS_001 ✅
  → METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001 ✅
  → SCM_TREATED_SET_PLACEBO_INTEGRATION_001 ✅
  → STUDENTIZED_PLACEBO_RANK_INFERENCE_001 ✅
  → SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001 ✅
  → MULTICELL_SHARED_CONTROL_MULTIPLICITY_001 ✅
  → STRATIFIED_POOLED_ESTIMAND_CONTRACT_001 ✅
  → AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001 ✅
  → METHOD_READINESS_MATRIX_V2_001 ✅
  → CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001 ✅
  → METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001 ✅
  → STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001 ✅
  → SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001 ✅
  → SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001 ✅
  → ROADMAP_INFERENCE_AND_METHOD_GAP_CONTROL_REFOCUS_001 ✅
  → ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001 ✅
  → METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001 ✅
  → OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001 ✅
  → SIMULATION_DGP_COVERAGE_PLAN_001 ✅
  → METHOD_FAILURE_MODE_REGISTRY_001 ✅
  → DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001 ✅
  → TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001 ✅
  → DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001 ✅
  → METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001 ✅
  → MULTICELL_MAX_T_RESEARCH_SCOUT_001 ✅
  → SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001 ✅
  → SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001 ✅
  → BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001 ✅
  → TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001 ✅
  → METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001 ✅
  → PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001 ✅
  → SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001 ✅
  → MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001 ✅
  → PRODUCTION_READINESS_BACKLOG_LEDGER_001 ✅
  → DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001 ✅
  → AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001 ✅
  → DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001 ✅
  → SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001 ✅
  → METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001 ✅
  → DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001 ✅
  → PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001 ✅
  → SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001 ✅
  → SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001 ✅
  → SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001 ✅
  → SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001 ✅
  → SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001 ✅
  → SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001 ✅
  → SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001 (active method lane)
  → implementation lanes (not selected until control layer complete)
```

**ROADMAP_INFERENCE_AND_METHOD_GAP_CONTROL_REFOCUS_001 (2026-06-03):** Corrects the active method-accuracy lane after `SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001`. The roadmap must not treat placebo/randomization as the full inference layer or select inference by estimator name alone. **Immediate next control artifact:** `OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001` (after gap/literature audit completion). `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001` remains important but moves after the suitability/gap-control layer unless the matrix explicitly reprioritizes it.

**METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001 (2026-06-03):** Audits design/estimator/inference gap coverage and literature-alignment buckets (**82 rows**; `failed_scenarios: []`). Suitability matrix is necessary but not sufficient. Observed-panel diagnostics, simulation DGP plan, and failure-mode registry are required next control layers. See [`track_d/METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001_REPORT.md`](track_d/METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001_REPORT.md).

**OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001 (2026-06-03):** Defines **87** observed-panel diagnostic requirements before method selection (`failed_scenarios: []`). Hard blockers, warnings, estimator/inference routing impacts, and artifact routing defined. See [`track_d/OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001_REPORT.md`](track_d/OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001_REPORT.md).

**SIMULATION_DGP_COVERAGE_PLAN_001 (2026-06-03):** Defines **105** simulation DGP coverage requirements for shared calibration universe (`failed_scenarios: []`). See [`track_d/SIMULATION_DGP_COVERAGE_PLAN_001_REPORT.md`](track_d/SIMULATION_DGP_COVERAGE_PLAN_001_REPORT.md).

**METHOD_FAILURE_MODE_REGISTRY_001 (2026-06-03):** Defines **100** centralized failure modes (`failed_scenarios: []`). See [`track_d/METHOD_FAILURE_MODE_REGISTRY_001_REPORT.md`](track_d/METHOD_FAILURE_MODE_REGISTRY_001_REPORT.md).

**DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001 (2026-06-03):** Defines **91** assignment-generator stress tests (`failed_scenarios: []`). Links FM/OPD/DGP triggers to inference feasibility gates. See [`track_d/DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001_REPORT.md`](track_d/DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001_REPORT.md).

**TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001 (2026-06-03):** Audits **52** TBRRidge inference paths (`failed_scenarios: []`). Point diagnostic allowed; BRB/KFold/placebo/jackknife not production-valid; aggregate/global overclaims blocked. See [`track_d/TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001_REPORT.md`](track_d/TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001_REPORT.md).

**DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001 (2026-06-03):** Audits **56** DID randomization/bootstrap paths (`failed_scenarios: []`). Point diagnostic allowed; randomization/permutation/bootstrap not production-valid; bootstrap cannot fix invalid assignment. See [`track_d/DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001_REPORT.md`](track_d/DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001_REPORT.md).

**METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001 (2026-06-03):** Defines per-family production compatibility and remediation paths for **9** estimator families (`failed_scenarios: []`). Research-only and diagnostic-only are promotion hypotheses, not abandonment. See [`track_d/METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001.md`](track_d/METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001.md).

**MULTICELL_MAX_T_RESEARCH_SCOUT_001 (2026-06-03):** Scouts **50** multicell/shared-control multiplicity paths (`failed_scenarios: []`). Naive per-cell p-values blocked; pooled/global inference blocked; max-T/stepdown research candidates only. See [`track_d/MULTICELL_MAX_T_RESEARCH_SCOUT_001_REPORT.md`](track_d/MULTICELL_MAX_T_RESEARCH_SCOUT_001_REPORT.md).

**SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001 (2026-06-03):** Audits **60** SCM/AugSynth inference promotion gates (`failed_scenarios: []`). SCM strongest near-term candidate; production inference unauthorized. See [`track_d/SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001_REPORT.md`](track_d/SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001_REPORT.md).

**SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001 (2026-06-03):** Scouts **55** Synthetic DID method paths (`failed_scenarios: []`). Research/scout candidate; production inference unauthorized. See [`track_d/SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001_REPORT.md`](track_d/SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001_REPORT.md).

**BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001 (2026-06-03):** Audits **48** TBR/Bayesian TBR boundary paths (`failed_scenarios: []`). Posterior intervals not causal CIs; classic aggregate overclaim blocked. See [`track_d/BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001_REPORT.md`](track_d/BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001_REPORT.md).

**TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001 (2026-06-03):** Audits **40** TROP boundary paths (`failed_scenarios: []`). TROP remains research-only; production inference/recommendations/decisioning unauthorized. See [`track_d/TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001_REPORT.md`](track_d/TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001_REPORT.md).

**METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001 (2026-06-03):** Defines **178** promotion criteria rows across **9** method families (`failed_scenarios: []`). SCM strongest gated candidate; all families require explicit evidence gates. See [`track_d/METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001_REPORT.md`](track_d/METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001_REPORT.md).

**PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001 (2026-06-03):** Defines **10** execution lanes sequencing family validation, remediation, research, retire/replace, and release-gate plans (`failed_scenarios: []`). See [`track_d/PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001.md`](track_d/PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001.md).

**SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001 (2026-06-03):** Defines **63** SCM validation rows across **21** validation areas (`failed_scenarios: []`). SCM first gated production-candidate lane; point estimate not sufficient. See [`track_d/SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_REPORT.md`](track_d/SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_REPORT.md).

**MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001 (2026-06-03):** Defines **78** multicell validation rows across **26** validation areas (`failed_scenarios: []`). Multicell/shared-control cross-family blocker; naive per-cell p-values and pooled/global overclaim blocked. See [`track_d/MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001_REPORT.md`](track_d/MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001_REPORT.md).

**PRODUCTION_READINESS_BACKLOG_LEDGER_001 (2026-06-03):** Single control-plane backlog ledger with **46** rows across **12** domains (`failed_scenarios: []`). Tracks all non-production-ready design, estimator, inference, multicell, router, remediation, retire/replace, and release-gate items. See [`track_d/PRODUCTION_READINESS_BACKLOG_LEDGER_001_REPORT.md`](track_d/PRODUCTION_READINESS_BACKLOG_LEDGER_001_REPORT.md).

**DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001 (2026-06-03):** Defines **96** selection-gate requirement rows across **14** selection layers (`failed_scenarios: []`). Separates design, estimator, and inference eligibility; reconciles prior audits without duplicating resolved work. See [`track_d/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001_REPORT.md`](track_d/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001_REPORT.md).

**AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001 (2026-06-03):** Defines **84** AugSynth validation rows across **28** remediation/validation areas (`failed_scenarios: []`). AugSynth diagnostic/restricted research until remediation; CVXPY solver reliability required. See [`track_d/AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001_REPORT.md`](track_d/AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001_REPORT.md).

**DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001 (2026-06-03):** Defines **87** DID validation rows across **29** validation areas (`failed_scenarios: []`). DID conditional production-candidate only under eligible designs; point estimate not sufficient. See [`track_d/DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_REPORT.md`](track_d/DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_REPORT.md).

**SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001 (2026-06-03):** Defines **114** Synthetic DID readiness rows across **38** readiness areas (`failed_scenarios: []`). Implementation-readiness candidate only; unit/time-weight and adapter contracts required. See [`track_d/SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001_REPORT.md`](track_d/SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001_REPORT.md).

**METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001 (2026-06-03):** Defines **180** retire/replace execution rows across **12** method families and **15** execution areas (`failed_scenarios: []`). Retire/replace overclaim paths; retain gated candidates; classic TBR retire/replace required. See [`track_d/METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001_REPORT.md`](track_d/METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001_REPORT.md).

**DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001 (2026-06-03):** Defines **127** implementation-plan rows for future deterministic selector (`failed_scenarios: []`). `ExperimentSelectionInput`/`ExperimentSelectionDecision` contracts, 14-layer rule ordering, 7 staged phases. **Implementation plan only; no runtime router.** See [`track_d/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001_REPORT.md`](track_d/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001_REPORT.md).

**PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001 (2026-06-03):** Defines **117** release-gate plan rows across **15** authorization domains, **15** evidence prerequisites, and **8** staged phases (`failed_scenarios: []`). `ProductionAuthorizationDecision` contract; scoped/revocable authorization model. **Release-gate plan only; no runtime gate; no production authorization granted.** See [`track_d/PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001_REPORT.md`](track_d/PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001_REPORT.md).

**SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001 (2026-06-03):** Defines **144** SCM validation implementation-plan rows across **31** validation areas and **10** staged phases (`failed_scenarios: []`). `SCMValidationInput`/`SCMValidationEvidence` contracts. SCM remains gated production-candidate; production inference unauthorized. **Implementation plan only; no validation runtime.** See [`track_d/SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001_REPORT.md`](track_d/SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001_REPORT.md).

**SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001 (2026-06-03):** Implements **31** SCM validation area registry rows and deterministic `build_scm_validation_evidence()` metadata scaffolding (`failed_scenarios: []`). `SCMValidationInput`/`SCMValidationEvidence` contracts realized. SCM remains gated production-candidate; production inference unauthorized. **Metadata scaffolding only; no SCM fitting, p-values, or causal CIs.** See [`track_d/SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001_REPORT.md`](track_d/SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001_REPORT.md).

**SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001 (2026-06-03):** Defines **147** SCM null calibration implementation-plan rows across **30** calibration areas and **10** staged phases (`failed_scenarios: []`). `SCMNullCalibrationInput`/`SCMNullCalibrationEvidence` contracts. SCM remains gated production-candidate; production inference unauthorized. **Implementation plan only; no null calibration runtime.** See [`track_d/SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001_REPORT.md`](track_d/SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001_REPORT.md).

**SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001 (2026-06-03):** Implements **30** SCM null calibration area registry rows and deterministic `build_scm_null_calibration_evidence()` metadata scaffolding (`failed_scenarios: []`). `SCMNullCalibrationInput`/`SCMNullCalibrationEvidence` contracts realized. SCM remains gated production-candidate; null calibration not completed. **Metadata scaffolding only; no placebo computation, p-values, or causal CIs.** See [`track_d/SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001_REPORT.md`](track_d/SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001_REPORT.md).

**SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001 (2026-06-03):** Defines **159** SCM jackknife sensitivity implementation-plan rows across **37** sensitivity areas and **10** staged phases (`failed_scenarios: []`). `SCMJackknifeSensitivityInput`/`SCMJackknifeSensitivityEvidence` contracts. SCM remains gated production-candidate; jackknife sensitivity not implemented. **Implementation plan only; no jackknife runtime.** See [`track_d/SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001_REPORT.md`](track_d/SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001_REPORT.md).

**SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001 (2026-06-03):** Implements **37** SCM jackknife sensitivity area registry rows and deterministic `build_scm_jackknife_sensitivity_evidence()` metadata scaffolding (`failed_scenarios: []`). `SCMJackknifeSensitivityInput`/`SCMJackknifeSensitivityEvidence` contracts realized. SCM remains gated production-candidate; jackknife sensitivity not completed. **Metadata scaffolding only; no jackknife refits, p-values, or causal CIs.** **Immediate next artifact:** `SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001`. See [`track_d/SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001_REPORT.md`](track_d/SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001_REPORT.md).

**ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001 (2026-06-03):** First cross-estimator × design × inference suitability matrix (**50 rows**; `failed_scenarios: []`). Placebo/randomization is **one inference family**, not the full inference layer. No estimator receives a universal default inference. See [`track_d/ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001_REPORT.md`](track_d/ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001_REPORT.md).

**Method-control layers (first-class):** Observed-data conditions · design validity · estimator suitability · inference suitability · simulation coverage · literature alignment · failure modes · repair/replace/retire decisions.

**Control artifact definitions:**
- **`ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001`** — Map estimator × design × inference × estimand × geometry to supported, candidate-after-calibration, requires-adapter, diagnostic-only, sensitivity-only, research-deferred, retire/replace, or blocked. Governs jackknife, bootstrap, placebo/studentized placebo, permutation/randomization, conformal, Bayesian posterior diagnostics, DID analytic inference, max-T/stepdown.
- **`METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001`** — Compare observed repo behavior, simulation/null-calibration evidence, design validity, estimator/inference suitability, literature alignment, and new-method scouting needs before repair/replace/retire/scout decisions.
- **`OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001`** — Required diagnostics on the actual observed panel (pre/post length, small-N structure, donor overlap, imbalance, outliers, seasonality, autocorrelation, heteroskedasticity, sparsity, zero inflation, spillover/contamination risk, treatment heterogeneity) before design/estimator/inference selection.
- **`SIMULATION_DGP_COVERAGE_PLAN_001`** — Master simulation DGP grid (iid null, unit/time FE, latent factor, heteroskedasticity, autocorrelation, outliers, seasonality, sparse metrics, small-N geo, spillover, heterogeneous effects, multicell shared-control dependence) so calibration harnesses do not use inconsistent toy nulls.
- **`METHOD_FAILURE_MODE_REGISTRY_001`** — Central registry of known failures (TBR aggregate geometry mismatch, TBRRidge BRB/KFold/placebo diagnostic-only, TBRRidge JK blocked, AugSynth JK diagnostic/retire, SCM single-treated placebo null-monitor-only, multicell global/winner familywise risk, stratified pooled heterogeneity gap, unknown assignment blocked, deterministic/falsification-only paths).

**Explicit decisions:** Placebo/randomization is one inference family, not the full layer. No universal default inference per estimator. Suitability depends on estimator, design, assignment mechanism, estimand, geometry, statistic adapter, observed-data diagnostics, null calibration, multiplicity, and dependence. Observed-panel diagnostics and literature alignment are required before production-like method selection. Simulation DGP coverage must be centralized. Known failure modes must be registered centrally.

**Post-control implementation lanes (candidates, not final):** `TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001` · `DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001` · `DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001` · `MULTICELL_MAX_T_RESEARCH_SCOUT_001` · `AUGSYNTH_ESTIMATOR_BACKED_RANDOMIZATION_CALIBRATION_001` · `SCM_AUGSYNTH_DISAGREEMENT_DIAGNOSTICS_001` · `METHOD_PROMOTION_CRITERIA_BY_FAMILY_001` · `METHOD_REPAIR_REPLACE_RETIRE_DECISION_RULES_001`

**Downstream authorization:** No production p-values, causal confidence intervals, TrustReport, CalibrationSignal, MMM ingestion, LLM decisioning, production decisioning, live API, scheduler, or budget optimization. Downstream work remains paused until method suitability, observed-data diagnostics, literature alignment, simulation coverage, failure registry, and repair/replace/retire rules are completed or explicitly waived by a later audit.

**TrustReport ops freeze (2026-06-03):** Research-mode operationalization is complete enough for package-level governance. Audit log, review queue, UI, API, scheduler, and platform rollout are **deferred to the MIP application/orchestration layer**. Active lane is **method validation** — see [`ROADMAP_REFOCUS_METHOD_VALIDATION_001.md`](audits/ROADMAP_REFOCUS_METHOD_VALIDATION_001.md).

**Downstream pause (2026-06-03):** CalibrationSignal schema alignment, TrustReport expansion, MMM ingestion, and LLM decisioning are **paused** per [`METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001.md`](audits/METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001.md) until P0 null calibration and adapter checkpoints pass.

**Parallel later lane (not blocking core TrustReport qualification):** DCM-009–019 adapter lanes → full design × estimator × inference **matrix v2** → broader product-surface qualification.

**Naming distinction:** [`TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001`](track_d/TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md) reassessed **DCM-001 only** (SCM + UnitJackknife). [`FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001`](track_d/FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001_REPORT.md) (2026-06-03) reassessed **all governed DCM rows**; global TrustReport authorization remains false.

**Ordered next:** ✅ … → ✅ **`SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001`** → ✅ **`SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001`** → ✅ **`SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001`** → **`SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001`**.

**Design implementation validation:** [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) — ✅ Accepted; 0/31 contract-complete; 8 hard blocker classes.

**Design code inventory:** [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) — ✅ Accepted; authoritative design-side enumeration (31 rows).

**Design literature alignment:** [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) — ✅ Accepted; 31 rows aligned; 14 open conceptual gaps (G-DES-001–014).

**Design output contract:** [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) — ✅ Accepted. [`TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md`](TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md) — TROP; follows design-output contract; not implementation.

**Design statistical validation protocol:** [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) — ✅ Accepted; **tier-1 execution complete** [`D5_DES_STAT_TIER1_001_REPORT.md`](track_d/D5_DES_STAT_TIER1_001_REPORT.md); no promotion.

**Design audit lane:** D5-DES-STAT-STRATIFIED-001 ✅ · D5-DES-STAT-MULTICELL-001 ✅ · D5-DES-STAT-TIER1-RECHARACTERIZATION-001 ✅ · DESIGN-COMBINATION-VALIDATION-EXECUTION-001 ✅ · DESIGN-GUARDRAIL-ENFORCEMENT-001 ✅ · INFERENCE-BOUNDARY-GUARDRAIL-ENFORCEMENT-001 ✅ · ESTIMATOR-READOUT-GUARDRAIL-INTEGRATION-001 ✅. **0 contract-complete; downstream blocked.**

### METHOD-ENHANCEMENT-ROADMAP-001 (post-Level-B synthesis)

**Document:** [`METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md)  
**Status:** **active planning** — converts completed D5-STAT Level B evidence into targeted enhancement lanes (readout semantics, geometry bridges, TBRRidge/SARIMAX/Bayesian contracts).  
**Verdict:** Enhancement starts **after** D5 baseline; no method changes implied without rerun validation. Suitability v2 and TrustReport roles remain gated.

**Paused:** TrustReport / F-DECISION / CalibrationSignal / MMM role expansion · default **`D5-INST-AUGSYNTH-MULTICELL-001`** (optional narrow gate test later only).

### METHOD-CODE-INVENTORY-001 (Layer 1)

**Document:** [`METHOD_CODE_INVENTORY_001.md`](METHOD_CODE_INVENTORY_001.md)  
**Archive:** [`track_d/archives/METHOD_CODE_INVENTORY_001.json`](track_d/archives/METHOD_CODE_INVENTORY_001.json)  
**Generator:** [`panel_exp/validation/method_code_inventory_001.py`](../panel_exp/validation/method_code_inventory_001.py)  
**Status:** **complete** — 44 code-derived items; no trust roles  
**Next:** ✅ Layer 2 complete (see below)

### METHOD-LITERATURE-ALIGNMENT-001 (Layer 2)

**Document:** [`METHOD_LITERATURE_ALIGNMENT_001.md`](METHOD_LITERATURE_ALIGNMENT_001.md)  
**Archive:** [`track_d/archives/METHOD_LITERATURE_ALIGNMENT_001.json`](track_d/archives/METHOD_LITERATURE_ALIGNMENT_001.json)  
**Generator:** [`panel_exp/validation/method_literature_alignment_001.py`](../panel_exp/validation/method_literature_alignment_001.py)  
**Status:** **complete** — 24 literature families mapped to Layer 1 inventory; no trust roles  
**Next:** ✅ Layer 3 complete (see below)

### METHOD-IMPLEMENTATION-VALIDATION-001 (Layer 3)

**Document:** [`METHOD_IMPLEMENTATION_VALIDATION_001.md`](METHOD_IMPLEMENTATION_VALIDATION_001.md)  
**Archive:** [`track_d/archives/METHOD_IMPLEMENTATION_VALIDATION_001.json`](track_d/archives/METHOD_IMPLEMENTATION_VALIDATION_001.json)  
**Generator:** [`panel_exp/validation/method_implementation_validation_001.py`](../panel_exp/validation/method_implementation_validation_001.py)  
**Status:** **complete** — 29 implementation-validation rows; code inspection + audit reconciliation  
**Next:** ✅ Layer 4 complete (see below)

### METHOD-STATISTICAL-VALIDATION-PROTOCOL-001 (Layer 4)

**Document:** [`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md)  
**Archive:** [`track_d/archives/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json`](track_d/archives/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json)  
**Generator:** [`panel_exp/validation/method_statistical_validation_protocol_001.py`](../panel_exp/validation/method_statistical_validation_protocol_001.py)  
**Status:** **complete** — 51 protocol rows (29 family + 22 combination); DGP/metric catalogs; battery A–E; no heavy OC  
**Next:** ✅ Layer 5 complete (see below)

### METHOD-COMBINATION-VALIDATION-MATRIX-001 (Layer 5)

**Document:** [`METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md)  
**Archive:** [`track_d/archives/METHOD_COMBINATION_VALIDATION_MATRIX_001.json`](track_d/archives/METHOD_COMBINATION_VALIDATION_MATRIX_001.json)  
**Generator:** [`panel_exp/validation/method_combination_validation_matrix_001.py`](../panel_exp/validation/method_combination_validation_matrix_001.py)  
**Status:** **complete** — 30 combination rows; ready-for-OC / blocked / bridge queues; no suitability roles  
**Next:** ✅ Suitability framework complete (see below)

### DESIGN-ESTIMATOR-INFERENCE-SUITABILITY-FRAMEWORK-001

**Document:** [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md)  
**Archive:** [`track_d/archives/DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.json`](track_d/archives/DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.json)  
**Generator:** [`panel_exp/validation/design_estimator_inference_suitability_framework_001.py`](../panel_exp/validation/design_estimator_inference_suitability_framework_001.py)  
**Status:** **complete** — 30 suitability rows; non-promotional classes only; forbidden flags false  
**Next:** ✅ Smoke + SCM+JK Level B complete (see below)

### D5-STAT-SMOKE-CALLABLE-001

**Report:** [`track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md`](track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md)  
**Archive:** [`track_d/archives/D5_STAT_SMOKE_CALLABLE_001_results.json`](track_d/archives/D5_STAT_SMOKE_CALLABLE_001_results.json)  
**Generator:** [`panel_exp/validation/track_d_d5_stat_smoke_callable_001.py`](../panel_exp/validation/track_d_d5_stat_smoke_callable_001.py)  
**Status:** **complete** — smoke/schema/callability/orientation/guards; `smoke_pass_with_caveats`  
**Next:** ✅ **`D5-STAT-SCM-JK-001`** (see below)

### D5-STAT-SCM-JK-001

**Report:** [`track_d/D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md)  
**Harness correction:** [`track_d/D5_STAT_SCM_JK_001_HARNESS_CORRECTION_REPORT.md`](track_d/D5_STAT_SCM_JK_001_HARNESS_CORRECTION_REPORT.md)  
**Archive:** [`track_d/archives/D5_STAT_SCM_JK_001_results.json`](track_d/archives/D5_STAT_SCM_JK_001_results.json) (historical pre-correction: [`D5_STAT_SCM_JK_001_results_historical_pre_harness_correction.json`](track_d/archives/D5_STAT_SCM_JK_001_results_historical_pre_harness_correction.json))  
**Generator:** [`panel_exp/validation/track_d_d5_stat_scm_jk_001.py`](../panel_exp/validation/track_d_d5_stat_scm_jk_001.py)  
**Status:** **complete** — Level B characterization; harness corrected 2026-06-17; `characterization_pass_with_caveats` / `scm_jk_harness_corrected_level_consistent_baseline_established`  
**Next:** ✅ **`TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001`** (DCM-001 only) → **`D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001`**

### D5-STAT-AUGSYNTH-POINT-001

**Report:** [`track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md)  
**Archive:** [`track_d/archives/D5_STAT_AUGSYNTH_POINT_001_results.json`](track_d/archives/D5_STAT_AUGSYNTH_POINT_001_results.json)  
**Generator:** [`panel_exp/validation/track_d_d5_stat_augsynth_point_001.py`](../panel_exp/validation/track_d_d5_stat_augsynth_point_001.py)  
**Status:** **complete** — AugSynthCVXPY point only; `characterization_mixed_requires_followup`  
**Next:** ✅ **`DESIGN_GUARDRAIL_ENFORCEMENT_001`** (combination execution ✅ [`DESIGN_COMBINATION_VALIDATION_EXECUTION_001_REPORT.md`](track_d/DESIGN_COMBINATION_VALIDATION_EXECUTION_001_REPORT.md))

### METHOD-SOUNDNESS-AND-GAP-ROADMAP-001

**Document:** [`METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md)  
**Status:** **complete**  
**Verdict:** Audit-derived inventory and DL lanes — **reconciled under** [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md). **No new eligibility decisions.**

**Inputs:** Track D D1–D5 · CV-001 · AUDIT-010 · foundation hardening · validation program.

**Ordered next:** See **METHOD-ENHANCEMENT-ROADMAP-001** (`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001`).

### METHOD-SOUNDNESS-ROADMAP-REVIEW-001

**Document:** [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md)  
**Status:** **complete** · **superseded_for_sequencing**  
**Verdict:** Historical checkpoint — DL-1 AugSynth lane selection; superseded by validation program.

**Ordered next:** See **METHOD-VALIDATION-PROGRAM-001** (authoritative).

### METHOD-FOUNDATION-SYNTHESIS-001

**Document:** [`METHOD_FOUNDATION_SYNTHESIS_001.md`](METHOD_FOUNDATION_SYNTHESIS_001.md)  
**Status:** **complete** · **superseded_for_sequencing** — retained as **evidence-input** combination map only  
**Verdict:** Useful consolidation of prior audits; **not** authoritative for next OC or trust roles. See **METHOD-VALIDATION-PROGRAM-001**.

### AUGSYNTH-ASCM-DEVELOPMENT-ROADMAP-001

**Document:** [`AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md)  
**Status:** **complete** — P1–P6 execution landed  
**Verdict:** DL-1 lane **P6 complete** — [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md) verdict `compatible_per_cell_only_pooling_blocked` + `bridge_required_before_broader_use`. **Not promotion.**

**P1–P6:** ✅ complete · **Lane:** **closed**. AugSynth-specific execution **paused** under [`METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md) unless narrowly scoped (e.g. optional ADR metadata gate test later).

### AUGSYNTH-ASCM-LANE-CLOSEOUT-001

**Document:** [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md)  
**Status:** **complete** — decision checkpoint; no production behavior change  
**Verdict:** DL-1 lane **closed** at P6; ordered next was **`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001`** (now ✅). AugSynth point promising diagnostic-only; JK diagnostic-only (unsafe strata); Conformal blocked; no promotion.

### MULTICELL-AUGSYNTH-POOLING-RULE-ADR-001

**Document:** [`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md`](MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md)  
**Status:** **accepted** — docs-only; no production behavior change  
**Verdict:** Multi-cell AugSynth **per-cell diagnostic by default**; **no pooled lift**; optional **`MULTICELL_AUGSYNTH_DESCRIPTIVE_V0`** descriptive mean under gates; **no pooled uncertainty**. **Semantic guardrail only** — statistical validation deferred to validation program. **MCELL OC:** paused as default next step.

### DESIGN-READOUT-AUGSYNTH-COMPATIBILITY-001 (P6)

**Document:** [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md)  
**Status:** **complete** — docs-only; no production behavior change  
**Verdict:** `compatible_per_cell_only_pooling_blocked`; co-verdict `bridge_required_before_broader_use`. Tier-1 unit-panel single-cell structurally compatible (greedy OC-validated); multi-cell per-cell only; Conformal blocked; JK diagnostic-only.

### D5-DIAG-SCM-AUGSYNTH-001

**Document:** [`track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md`](track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md)  
**Module:** [`panel_exp/validation/scm_augsynth_diagnostics.py`](../panel_exp/validation/scm_augsynth_diagnostics.py)  
**Status:** **complete** — validation-layer diagnostics only; no production behavior change.  
**Next:** ASCM-003 OC uses these diagnostics.

### AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001

**Document:** [`AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md`](AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md)  
**Status:** **complete** — docs/inspection only; no estimator behavior change  
**Verdict:** **`fidelity_confirmed_with_caveats`** — ASCM-003 may proceed with documented gaps (G4/G7/G8).  
**Next:** **D5-INST-AUGSYNTH-ASCM-003**.


### SCM-AUGSYNTH-DIAGNOSTIC-THRESHOLD-AUDIT-001

**Document:** [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md)  
**Verdict:** Provisional SCM/A26 and AugSynth/ASCM failure-mode **labels** and threshold **categories** (block / caution / diagnostic-only / insufficient-evidence). **No promotion**; **no TrustReport/F-DECISION change**. ASCM-003 recommended for numeric calibration.

**Inputs:** METHOD-FOUNDATION-HARDENING-001 P1 · ASCM-002 · ADR-001 · AUGSYNTH-ASCM-STRENGTHENING-001 §5.

### Track F — estimator / inference completion (implementation planning)

**Roadmap ID:** `TRACK-F-ESTIMATOR-INFERENCE-COMPLETION`  
**Status:** **plan v1** — converts Track D compatibility + conceptual validity + OC into fix roadmap  
**Document:** [`TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md`](TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md)

| Phase | Scope |
|-------|--------|
| **P1** | ~~D5-INST-TBR-001~~ ✅ — aggregate class TBR OC |
| **P1.5** | ~~AUDIT-010~~ ✅ — `not_ready_continue_track_f` |
| **P0 (post AUDIT-010)** | ~~Blocking hygiene~~ ✅ — [`instrument_contract.py`](../panel_exp/governance/instrument_contract.py) |
| **P2** | ~~D5-INST-TBRRIDGE-002~~ ✅ · ~~D5-INST-AUGSYNTH-003~~ ✅ · [`TRACK_F_P2_CLOSEOUT_001`](TRACK_F_P2_CLOSEOUT_001.md) ✅ | P2 closed — no more OC batteries unless fix reopens |
| **P3+** | ~~F-INF-003~~ ✅ · ~~POSTFIX~~ ✅ · ~~F-INF-002~~ ✅ · ~~TBRRIDGE-003~~ ✅ | **CHECKPOINT-001** ✅ — **pause** (default) |

**Non-goals:** No fixes in planning doc; no MMM ingestion; no CalibrationSignal expansion without separate governance PR.

### Track E — method suitability & triangulation

**Roadmap ID:** `TRACK-E-SUITABILITY-TRIANGULATION`  
**Status:** **E0–E7 complete** ([AUDIT-009](audits/AUDIT-009_track_e_completion_gate.md) `79c59c4`) — documentation, contract tests, production TrustReport wiring  
**Purpose:** Govern **design-method × geometry × measurement-instrument** suitability, triangulation, conflict taxonomy, and MMM-readiness — bridge between Track D OC evidence and Track B TrustReport / CalibrationSignal. **SCM+JK is one instrument card, not the whole system** ([ROADMAP-DESIGN-READOUT-UPDATE-001](ROADMAP_DESIGN_READOUT_UPDATE_001.md)).

| Phase | Document | Status |
|-------|----------|--------|
| **E0** | [`TRACK_E_METHOD_SUITABILITY_AND_TRIANGULATION_001.md`](TRACK_E_METHOD_SUITABILITY_AND_TRIANGULATION_001.md) | **E0–E7 complete** |
| E1 | Suitability diagnostic inventory | ✅ [`TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md`](TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md) |
| E2 | Method suitability cards | ✅ [`TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md`](TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md) |
| E3 | Triangulation schema | ✅ [`TRACK_E_E3_TRIANGULATION_SCHEMA_001.md`](TRACK_E_E3_TRIANGULATION_SCHEMA_001.md) |
| E4 | TrustReport conflict fixtures | ✅ [`TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md`](TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md) · [`tests/fixtures/track_e_conflicts/`](../tests/fixtures/track_e_conflicts/) |
| E5 | CalibrationSignal eligibility policy | ✅ [`TRACK_E_E5_CALIBRATIONSIGNAL_ELIGIBILITY_POLICY_001.md`](TRACK_E_E5_CALIBRATIONSIGNAL_ELIGIBILITY_POLICY_001.md) |
| E6 | TrustReport contract tests (E4 fixtures) | ✅ [`tests/track_e/test_e6_e4_conflict_fixtures.py`](../tests/track_e/test_e6_e4_conflict_fixtures.py) |
| E7 | Production triangulation integration | ✅ [`panel_exp/track_b/triangulation.py`](../panel_exp/track_b/triangulation.py) · [`tests/track_b/test_e7_track_e_trust_report.py`](../tests/track_b/test_e7_track_e_trust_report.py) |

**Non-goals (program):** No MMM ingestion, optimizer/planning feed, instrument promotion, or estimator/design/inference changes. E7 adds opt-in TrustReport triangulation only.

### Track C — unified user-level experimentation & conversion lift

**Objective:** Extend governed experimentation architecture from **geo-level** experiments to **user-randomized incrementality** systems (A/B, conversion lift, holdouts) — as a **future architecture track**, not immediate implementation.

| Future scope (examples) | Role |
|-------------------------|------|
| `ExperimentSpec` for user-randomized studies | Declared design, estimand, randomization unit |
| Ghost Ads / opportunity-logging abstractions | Exposure-eligibility semantics (conceptual; not copied from vendors) |
| CUPED / variance-reduction governance | Allowed transforms with estimand compatibility rules |
| Experiment feasibility engine | Governed viability assessment across A/B, CLS, GeoX, holdouts |
| Sequential experimentation governance | Human-governed stopping; no auto-promotion from peeking |
| SRM / randomization-integrity diagnostics | Sample-ratio mismatch and assignment-integrity signals |
| Unified `TrustReport` semantics | Cross-modality outcome taxonomy (see platform vision) |
| Experiment-to-MMM calibration contracts | Calibrated contribution inputs, not raw lift points |
| Holdout governance | Cohort/holdout randomization semantics and replay rules |
| Experiment replay & evidence freshness | Stale / superseded evidence boundaries |

**Explicit:**

- **Future architecture work** — no API, schema, or production behavior in v0.2.1  
- **Gated behind Track A stabilization** (Phases 11–15 evidence) **and Track B contract foundations** (`ExperimentSpec`, `ExperimentEvidence`, estimand registry)  
- **Conceptual reference only** — conversion-lift industry practice informs governance; it is **not** a mathematical blueprint to copy  

Detail: [`EXPERIMENTATION_PLATFORM_VISION.md`](EXPERIMENTATION_PLATFORM_VISION.md) § Track C · investigations **INV-020–INV-026** in [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md).

**Track sequencing:** A → B → C. Do not implement user-level experimentation surfaces before geo governance and shared contracts stabilize.

**Alignment registry:** [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md) § Track C · MMM · LLM — gated; stop conditions documented.

### Future GeoX / experiment package-side agents (deferred)

**Document:** [`FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001.md`](FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001.md)  
**Status:** **roadmap capture only** — agents are **not** implemented, scheduled, or authorized.

GeoX / `panel_exp` remains the deterministic experiment engine (design, power/MDE/matchability diagnostics, assignment, inference, readouts). MIP owns orchestration, TrustReport governance, CalibrationSignal mapping, and user-facing agent routing. Future **package-side** support agents may interpret typed diagnostics and failure packets **only after** run manifests, failure packets, method governance, and safe retry boundaries are stable.

**Do not prioritize package-side agents before:** stable design/readout interfaces, typed diagnostics, auditable assignment constraints, standardized readout fields, MIP agent contracts, and package adapter allowed/blocked actions (see roadmap doc for full prerequisite list).

**Near-term package priority:** deterministic diagnostics-first work (selection-gate implementation, typed manifests/failure packets, method-governance outputs) — not LLM/agent runtime.

---

## Governed measurement instruments (mindset)

Treat estimators as **governed measurement instruments**, not interchangeable ML models.

Every estimator should eventually have:

| Artifact | Purpose |
|----------|---------|
| Estimand contract | What is estimated, on whom, when |
| Interval contract | Scale, alignment, unsupported paths |
| Calibration evidence | n≥100 archives where claimed |
| OC archive | Width, power, geometry sensitivity |
| Failure analysis | Mechanism when calibration fails |
| Investigation registry entry | Open/deferred gaps |
| Governance status | Supported / expert-review / research / deferred |
| Intended usage boundary | e.g. SCM jackknife = null monitor only |

This is mature scientific infrastructure — rare among experimentation platforms.

---

## Unified experimentation estimand philosophy

GeoX, conversion lift, A/B tests, MMM replay/calibration, and budget optimization must eventually share **governed estimand semantics** — not silent “lift” labels.

### Canonical estimand examples (cross-modality)

| Estimand (conceptual) | Typical modality | Notes |
|----------------------|------------------|-------|
| Absolute incremental lift | A/B, CLS | Δ on outcome scale |
| Relative lift / relative ATT | GeoX, some A/B | Ratio or percent change |
| ATT | GeoX, DID | Treatment effect on treated |
| iROAS | MMM + lift calibration | Incremental return on ad spend |
| Incremental conversions | CLS, A/B | Count scale; lag-sensitive |
| Incremental revenue | CLS, geo revenue tests | Currency scale |
| Calibrated contribution | MMM replay | Posterior/prior informed by experiment OC |
| Δμ (mean shift) | A/B frequentist | Must map to business estimand explicitly |

### Governance rules (future contracts)

| Rule | Intent |
|------|--------|
| **Allowed transformations** | CUPED, variance reduction, aggregation — only when estimand contract preserved and documented |
| **Aggregation semantics** | Pooled vs unit-level vs geo-level — explicit; no implicit consensus ATT (INV-003, INV-020) |
| **Compatibility rules** | Which estimands may feed MMM calibration, TrustReport, or eligibility registry |
| **Calibration eligibility** | Nominal calibration claims only on aligned intervals at n≥100 with archived OC |
| **Trust boundaries** | `TrustReport` states what is supported, inconclusive, incompatible, or stale |

**Today:** geo `relative_att_post` path is the best-documented contract. User-level and MMM estimands are **Track C investigations** — not implemented claims.

---

## Immediate next step (before Phase 12 / Run 002)

**Merge `brb-bound-ordering-fix` into integration mainline** (`estimator-maturity-metadata` → PR to `main`).

| Does | Does not |
|------|----------|
| Remove known BRB bound-ordering defect | Re-promote BRB to nominal eligibility |
| Improve inference hygiene (`apply_bounds_to_results`, guard) | Change `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` |
| Preserve future rehabilitation options | Make calibration claims |
| Enable honest Run 002 characterization | Imply TBRRidge production-ready |

**Classification:** correctness preservation only. BRB remains skipped with `brb_bounds_inverted_run001` until Run 002 + failure analysis + OC pass.

---

## Promotion policy (non-negotiable)

**No estimator advancement** (maturity label change, nominal-calibration eligibility, expert-review expansion, or “recommended for production-like workflows”) without completing this chain **in order**, with archived evidence at each step:

1. **Estimand definition** — what quantity is estimated, on what units and time window, and how it maps to recovery scoring (`relative_att_post` or an explicitly declared alternate).
2. **Recovery evidence** — finite metrics or typed failures on the standard recovery battery (`RecoveryRunner`, documented scenarios).
3. **Calibration evidence** — null-scenario FPR and coverage (and positive-scenario power when claimed) at **n≥100** on aligned configs, archived like Run 001.
4. **Failure analysis** — when calibration fails, root-cause doc (mechanism, not threshold tuning) before re-eligibility.
5. **Operating-characteristic characterization** — width, power, geometry sensitivity, and known failure modes documented for reviewers.

Skipping a step is **roadmap drift**. Plumbing-only changes, passing smoke tests, or documentation without archived OC do **not** satisfy this policy.

Investigation IDs in [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) map to gaps; this roadmap assigns **phases** to close them. Do not re-prioritize ad hoc — update investigations first, then amend v4.

---

## Recommended document sequence

| Step | Action | Status |
|------|--------|--------|
| 1 | Create/update **`docs/ROADMAP_V4.md`** (this file) | **Done** |
| 2 | Add/maintain **`docs/OPEN_INVESTIGATIONS.md`** | **Done** — single source of truth for unresolved gaps |
| 3 | **Freeze priorities** | **Done** — top investigations and phase order locked here + OPEN_INVESTIGATIONS §1 |
| 4 | **Phase 11** — SCM UnitJackKnife OC | **Done** — `SCM_JACKKNIFE_CHARACTERIZATION_001.md` |
| 5 | **Merge BRB bound-ordering fix** | **Ready** — on `estimator-maturity-metadata`; PR to `main` pending |
| 6 | **Phase 12** — TBRRidge inference investigation program | After BRB merge — characterize, do not “fix”; all outcomes acceptable |
| 7 | **Re-audit** after Phases 11–15 | Mini-audit; update investigations |
| 8 | Create **`docs/ROADMAP_V5.md`** | After re-audit |
| 9 | **Track B** — unified experimentation abstractions | After Phase 12 stabilizes |
| 10 | **Track C** — user-level / conversion-lift architecture | After Track B contracts; investigations INV-020–026 |

---

## 1. Completed (Phases 5–10 and foundations)

Shipped behavior and evidence. **Do not re-open** unless new evidence contradicts archived runs.

| Deliverable | What it established | Evidence |
|-------------|---------------------|----------|
| **Estimand alignment** | Recovery scores `relative_att_post` via `_path_relative_att`; canonical truth tests | `recovery_runner.SCORED_TARGET_ESTIMAND`, `tests/test_estimand_metric_alignment.py` |
| **Interval alignment** | Coverage/FPR only when `interval_estimand == relative_att_post` | `recovery_intervals.py`, `tests/test_recovery_estimand_interval_alignment.py` |
| **Production calibration harness** | `run_production_nominal_calibration()`, replication thresholds, advisory status | `production_nominal_calibration.py`, `nominal_calibration.py` |
| **DGP semantics** | Explicit missingness policies; honest stagger metadata; calibration scenarios `missingness_policy=none` | `synthetic_world.py`, `tests/test_synthetic_dgp_semantics.py` |
| **DID contracts** | Pretrend warn/fail + waiver; relative-ATT interval calibration **unsupported** by policy | `did_interval_policy.py`, `tests/test_did_interval_policy.py` |
| **BRB bound fix** | Correct `apply_bounds_to_results` mapping; `PATH_INTERVAL_BOUNDS_INVERTED` guard | `inference/_impact_common.py`, `recovery_intervals.py`, branch `brb-bound-ordering-fix` |
| **Eligibility tightening** | `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` = **`SCM_UnitJackKnife` only** | `nominal_calibration.py`, `VALIDATION_COVERAGE.md` |
| **Phase 8 audit** | Focused algorithm/statistical mini-audit | `docs/PHASE8_ALGORITHM_AUDIT.md` |
| **Run 001 evidence archive** | n=100, 3 seeds; SCM null pass / zero power; BRB/Kfold failures documented | `docs/CALIBRATION_RUN_001.md`, `docs/CALIBRATION_FAILURE_ANALYSIS_001.md` |

**Also shipped (supporting):** inference recovery configs, typed recovery failures, opt-in review flags (`build_estimator_review`), method validation plan, validation coverage matrix.

**Not completed by design:** package-level nominal calibration for TBRRidge modes; DID relative-ATT intervals; `production_safe` promotions; automated blocking readiness.

---

## 2. Current positioning

| Statement | Detail |
|-----------|--------|
| **Expert-review platform** | Disciplined contracts, evidence exports, and calibration **instrumentation** for human reviewers — not unattended certification. |
| **Not production-safe** | No estimator carries `production_safe` in the maturity catalog; policy tests enforce this. |
| **No automated decisioning** | Readiness, calibration status, and experiment cards are **advisory**; they do not block runs or approve business decisions. |
| **No estimator promotions** | `expert_review` / `research_only` labels unchanged until promotion policy chain is satisfied per method. |

**Frozen priority themes** (from [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md)):

1. Close **calibration honesty** (INV-039, INV-004, INV-008, INV-007) before breadth.  
2. Preserve **estimand discipline** (INV-001, INV-002, INV-036) — document and test, not silent consensus ATT.  
3. **Research estimators** (INV-011) stay off the promotion path until wired and characterized.  

---

## 3. Approved execution order (Phases 11–15)

One phase per scoped PR (or PR series). **No new estimators, inference modes, artifact schema versions, or maturity promotions** unless this document is amended after re-audit.

### Phase 11 — SCM UnitJackKnife characterization

| Field | Detail |
|-------|--------|
| **Goal** | Explain Run 001 outcomes: null pass with **zero power** on positive DGP; characterize interval width vs donor/treated geometry. |
| **Investigations** | INV-004, INV-003 (partial), INV-039 (SCM-only path) |
| **In scope** | Read-only analysis + archived notes; optional single-treated calibration scenario **documented**; width/power tables |
| **Out of scope** | DGP tuning to force power pass; re-adding TBRRidge to eligibility; threshold changes |
| **Promotion policy steps** | Estimand (already defined) → recovery (exists) → Run 001 calibration (exists) → **failure analysis for power** → **OC characterization** |
| **Exit** | Written OC doc: when SCM jackknife is suitable for null monitoring only vs lift detection; update OPEN_INVESTIGATIONS INV-004 status |

---

### Phase 12 — TBRRidge inference investigation program

**Framing:** This is **not** “fix TBRRidge” or “make TBRRidge production-ready.” It is an **investigation program** to characterize whether TBRRidge inference can support **calibrated expert-review workflows**.

**Scientific posture:** You are not trying to “win.” You are trying to **characterize reality honestly.** All outcomes are acceptable — including “TBRRidge BRB remains research-only” if the evidence supports it. That discipline is rare and valuable.

| Field | Detail |
|-------|--------|
| **Prerequisite** | BRB bound-ordering fix merged to `main` (correctness only — eligibility unchanged until evidence closes investigations) |
| **Program goal** | Archived operating characteristics, interval validity, failure surfaces, and governance inputs for Phase 13 decision |
| **In scope** | Run 002 (n≥100), geometry matrices, OC archives, guards, recovery tests; registry update **only** after full advancement policy chain |
| **Out of scope** | “Fix TBRRidge” narrative; production-ready claims; automatic eligibility; threshold tuning; new inference modes |
| **Acceptable outcomes** | Partially re-enable · restrict to single-treated · null-monitoring-only · remain expert-review · permanently research-only — **all valid if evidenced** |
| **Exit** | Phase 12 evidence archive + investigation resolutions → Phase 13 governance decision; eligibility unchanged unless OC + policy chain pass |

#### Investigation tracks

Each track produces an **archived evidence artifact** (OC tables, Run 002 slice, or governance note). Tracks may close independently.

**INV-007 — KFold geometry characterization**

| | |
|---|---|
| **Questions** | Single-treated only? Donor-count sensitivity? Treated-count failure surface? Fundamentally incompatible with pooled geometry? |
| **Work** | Geometry matrix on default recovery vs single-treated panels; document hard-failure modes |
| **Possible outcome** | Permanently restricted (single-treated-only contract or research-only) |

**INV-008 — BRB operating characteristics after bound fix**

| | |
|---|---|
| **Questions** | Did inversion fix restore sane intervals? Behavior at n≥100? Coverage vs power tradeoff? Interval width? Seed stability? Geometry sensitivity? |
| **Work** | Calibration Run 002 at n≥100 post-merge; failure analysis vs Run 001; OC archive |
| **Possible outcome** | Partially re-enable within expert-review · or permanently remove from nominal path |

**INV-003 — Multi-treated aggregation semantics** *(broader than TBRRidge)*

| | |
|---|---|
| **Questions** | Pooled relative ATT behavior? Heterogeneous treated effects? Aggregation stability? Relative vs pooled estimands? |
| **Work** | Document scoring contract; optional heterogeneous DGP equivalence probes; tie to recovery runner `_path_relative_att` |
| **Possible outcome** | Documented contract only · alternate scoring path · calibration scenario catalog (single- vs multi-treated) |

**INV-017 — Calibration scaling and governance** *(foundational for Track B)*

| | |
|---|---|
| **Questions** | When is nominal calibration meaningful? How should operating characteristics be archived? How should eligibility evolve? How should trust signals eventually form? |
| **Work** | Run 002 archival conventions; smoke vs production tier tags; eligibility evolution rules; inputs to future `CalibrationSignal` / `TrustReport` |
| **Possible outcome** | Governance playbook for calibration archives and trust formation — not estimator promotion |

See [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) § Phase 12 program for cross-links to living backlog entries.

---

### Phase 13 — TBRRidge promotion decision

| Field | Detail |
|-------|--------|
| **Goal** | **Decision only** — record governance outcome from Phase 12 investigation program (per config: go / no-go / monitor-only / research-only) within **expert_review** — not `production_safe` |
| **Investigations** | INV-039 (partial), METHOD_VALIDATION_PLAN paths |
| **In scope** | Governance doc / validation plan update; explicit “go / no-go / monitor-only” per config |
| **Out of scope** | `production_safe` label; catalog auto-promotion; blocking gates |
| **Exit** | Recorded decision with citations to Run 002 and OC characterization; no promotion without passing promotion policy |
| **Status** | **Complete (historical)** — [`PHASE13_GOVERNANCE_DECISION_001.md`](PHASE13_GOVERNANCE_DECISION_001.md). **Not** the current MMM or instrument promotion path; superseded by Track D/E/F characterization + **AUDIT-010** readiness/gap. |

---

### Track A governance vs characterization (roadmap clarification)

**Track A governance foundation is complete** (estimand alignment, recovery interval gates, nominal calibration framework, DGP hardening, diagnostics separation, review flags, Phase 12–13 investigations, deferred work registry, [`TRACK_B_ARCHITECTURE_PLAN.md`](TRACK_B_ARCHITECTURE_PLAN.md) planning input).

**Track A estimator characterization remains open** for core long-term expert-review instruments **not yet OC-archived**:

| Phase | Focus | Plan |
|-------|-------|------|
| **Phase 14** | AugSynth / AugSynthCVXPY OC | [`PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md`](PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md) |
| **Phase 15** | Placebo inference OC | [`PHASE15_PLACEBO_INVESTIGATION_PLAN.md`](PHASE15_PLACEBO_INVESTIGATION_PLAN.md) |

**Track B:** Planning may proceed **in parallel** ([`TRACK_B_ARCHITECTURE_PLAN.md`](TRACK_B_ARCHITECTURE_PLAN.md)). **Track B implementation** should not become the **primary** roadmap focus until Phase 14–15 produce archived OC evidence for the intended core instrument set (AugSynth + Placebo).

**Re-scoped from earlier v4 draft:** DID operating-characteristic characterization (formerly listed as Phase 14) remains **deferred** — policy closure on relative-ATT intervals exists; full DID OC is tracked in [`DEFERRED_WORK_REGISTRY.md`](DEFERRED_WORK_REGISTRY.md) **DEF-016** and may run at low intensity in parallel or after Phase 15.

---

### Phase 14 — AugSynth operating-characteristic characterization

| Field | Detail |
|-------|--------|
| **Goal** | Characterize **AugSynthCVXPY** (and `AugSynth` where viable) point recovery, null/positive OC, geometry sensitivity, and inference viability — before Track B implementation prioritization |
| **Investigations** | INV-028 (AugSynth OC), INV-018 / INV-037 (collinearity; partial) |
| **In scope** | Governed investigation per [`PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md`](PHASE14_AUGSYNTH_INVESTIGATION_PLAN.md); characterization-tier + optional n≥100 archive; failure analysis if needed |
| **Out of scope** | Promotion; eligibility changes; estimator math changes; Track B schema/API work |
| **Acceptable outcomes** | Expert-review point-only · null monitor only · research-only · deferred wiring |
| **Exit** | `PHASE14_AUGSYNTH_CHARACTERIZATION_001.md` + DEF-019 disposition update |

---

### Phase 15 — Placebo inference operating-characteristic characterization

| Field | Detail |
|-------|--------|
| **Goal** | Characterize **Placebo** inference (`placebo_band` semantics) on SCM/TBR-family paths: null behavior, geometry limits, export discipline — core expert-review null-reference mode |
| **Investigations** | INV-029 (Placebo OC); placebo vs CI interpretation ([`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md)) |
| **In scope** | Governed investigation per [`PHASE15_PLACEBO_INVESTIGATION_PLAN.md`](PHASE15_PLACEBO_INVESTIGATION_PLAN.md); interval-semantics track; geometry matrix |
| **Out of scope** | Implementation changes; promotion; nominal eligibility without estimand alignment proof |
| **Acceptable outcomes** | Trustworthy null monitor · expert-review strict export · research-only · policy exclude from relative-ATT calibration |
| **Exit** | `PHASE15_PLACEBO_CHARACTERIZATION_001.md` + DEF-020 disposition update |

---

## 3b. Track B — after Phase 12 (medium-term platform)

**Track A governance is complete;** Phase 14–15 characterization of AugSynth and Placebo remains before Track B should become the **primary implementation** focus. **Track B planning may proceed in parallel** — see [`TRACK_B_ARCHITECTURE_PLAN.md`](TRACK_B_ARCHITECTURE_PLAN.md).

Start **unified experimentation abstractions** when shared contracts are defined **and** core geo instrument OC archives exist for AugSynth and Placebo (Phase 14–15 exit artifacts).

| Future abstraction | Role |
|--------------------|------|
| `ExperimentSpec` | Declared design + estimand + interference |
| `ExperimentExecution` | Runnable measurement invocation |
| `ExperimentEvidence` | Portable evidence object (estimand, intervals, run refs, flags) |
| `Estimand` | Registry entry with family mapping |
| `DiagnosticSummary` | Reviewer-facing diagnostics aggregate |
| `CalibrationSignal` | Lifecycle state from recovery → OC → eligibility |
| `TrustReport` | Honest trust narrative (passes, limits, deferrals) |
| `RecommendationContext` | Inputs for budget / lift recommendations |
| `ReleaseGate` | Human-governed promotion checkpoint (not auto-block) |

**Shared across:** GeoX, A/B, conversion lift, MMM replay/calibration, budget optimization, future causal agents.

**Not in v0.2.1:** new schema versions or implementation — vision and sequencing only.

---

## 3c. Track C — experimentation outcome taxonomy & feasibility (future)

These concepts inform **TrustReport** and conversational orchestration — not current product behavior.

### Experiment outcome taxonomy (future `TrustReport` semantics)

| Outcome | Meaning |
|---------|---------|
| `supported_positive` | Evidence supports positive incremental effect within declared estimand |
| `supported_negative` | Evidence supports negative incremental effect |
| `inconclusive` | Insufficient evidence — **does not imply “no effect”** |
| `underpowered` | Design/feasibility inputs indicate low power at planned duration |
| `incompatible_estimand` | Measurement export does not match declared estimand contract |
| `stale` | Evidence superseded or outside freshness policy |
| `interference_detected` | Interference / spillover diagnostics exceed review threshold |
| `calibration_unavailable` | No archived calibration path for claimed modality |

All outcomes are **advisory** — human governance retains decision authority.

### Experiment feasibility governance (future shared engine)

**Purpose:** Governed experiment **viability assessment** — not just a power calculator.

| Inputs (examples) | Outputs (examples) |
|-------------------|-------------------|
| Baseline conversion rate, expected lift, variance | Feasibility score (advisory) |
| Spend, duration, traffic, conversion lag | Expected CI width / MDE |
| Randomization unit, clustering, interference assumptions | Power estimate |
| Modality (A/B, CLS, GeoX, holdout) | Operational recommendation (run / extend / redesign / do not run) |

Applies across **A/B**, **conversion lift**, **GeoX**, and **holdouts** with modality-specific constraints documented in `ExperimentSpec`.

### Randomization-unit semantics (future architecture)

| Unit | Modality | Connects to |
|------|----------|-------------|
| User / session randomization | A/B, CLS | `ExperimentSpec`, exposure eligibility |
| Exposure-opportunity randomization | Ghost-ad / opportunity logging (conceptual) | INV-026; not vendor-specific implementation |
| Geo randomization | GeoX | Current panel_exp strength |
| Cohort / holdout randomization | MMM calibration, incrementality holdouts | INV-023 replay contracts |
| Aggregate replay calibration | MMM posterior update | Calibrated contribution estimand |

Each unit carries **calibration compatibility rules** and **TrustReport** boundaries — see INV-020–INV-026.

---

## 4. Research backlog (post Phase 15)

Explicitly **not** in Phases 11–15. Each item requires the **promotion policy** chain before any maturity movement.

| Area | Estimators / topics | Notes |
|------|---------------------|--------|
| **SDID** | `SyntheticDID` | Staggered DGP honest; recovery unwired (INV-019, INV-011) |
| **TROP** | `TROP` | Recovery smoke tolerates NaN; skipped in batch validation (see OPEN_INVESTIGATIONS — TROP) |
| **BayesianTBR** | `BayesianTBR`, `BayesianTBRHorseShoe` | JAX optional deps; registry `Bayesian` ≠ MCMC path (INV-015) |
| **MTGP** | `MTGP` | Not validated; Bayesian GP MCMC |
| **Spillover estimation** | Core SCM/TBR/DID | DGP stress only; no spillover term (INV-009) |
| **Dynamic causal models** | Time-varying coefficients, AugSynth full productionization | Not in API; strategic research |

See [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) §8 and roadmap execution deferred register (v3 D1–D12) for investigation cross-links.

---

## 5. Do not build (scope lock)

Stop scheduling these unless **ROADMAP_V5** explicitly reopens after re-audit.

| Item | Reason |
|------|--------|
| **`production_safe` labels** | No estimator meets bar; promotion policy does not allow skip to label |
| **More inference variants** | Jackknife+, time JK+, etc. — baseline modes not calibrated (INV-027) |
| **Consensus ATT** | Cross-estimator single estimand without proof (INV-001) |
| **Automatic blocking gates** | Advisory culture; weak calibration inputs make blocking harmful (INV-035) |
| **Artifact churn** | New card/bundle/readiness schema versions without external consumers (INV-034) |

**Also unchanged:** unattended “certified causal effect” marketing; spillover-adjusted ATT in core estimators; DID relative-ATT intervals via cumulative scaling; threshold tuning to pass calibration without mechanism docs.

---

## 6. Re-audit trigger (after Phase 15)

Run a **focused mini-audit** (same spirit as Phase 8, not a full governance re-audit). Inputs:

- Phases 11–15 evidence archives (SCM OC, Run 002, TBRRidge decision memo, DID OC, CVXPY validation outcome)
- Updated [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) statuses
- Latest `VALIDATION_COVERAGE.md` and `METHOD_VALIDATION_PLAN.md`

**Audit questions:**

1. Did any config re-enter nominal eligibility without Run 002–class evidence?  
2. Is SCM jackknife’s role (null monitor vs lift detector) explicitly bounded?  
3. Are TBRRidge BRB/Kfold either calibrated or permanently skipped with failure analysis?  
4. Is DID still excluded from relative-ATT calibration claims?  
5. Did Phases 11–15 introduce artifact surface or inference modes against §5?  

**Output:** `docs/ROADMAP_V5.md` — new positioning, completed table, and Phases 16+ only if evidence supports.

Suggested audit triggers also listed in [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md) §12.

---

## 7. Phase map (v3 → v4)

| v3 phase | Status | v4 continuation |
|----------|--------|-----------------|
| Phases 5–8 | **Complete / frozen** | See §1 Completed |
| Phase 9 | Run 001 archive | Evidence input to Phases 11–12 |
| Phase 10 | Failure analysis + eligibility tighten | BRB fix shipped; registry SCM-only |
| **Phase 11** | **Complete** | SCM UnitJackKnife OC — `SCM_JACKKNIFE_CHARACTERIZATION_001.md` |
| **Phase 12** | **Complete** | TBRRidge inference investigation program |
| **Phase 13** | **Complete** | TBRRidge governance decision — `PHASE13_GOVERNANCE_DECISION_001.md` |
| **Phase 14** | **Complete** | AugSynth OC — [`PHASE14_AUGSYNTH_CHARACTERIZATION_001.md`](PHASE14_AUGSYNTH_CHARACTERIZATION_001.md) |
| **Phase 15** | Planned | Placebo inference OC — `PHASE15_PLACEBO_INVESTIGATION_PLAN.md` |
| Track B contracts + B5 | **In progress** | B0–M2 complete; **adapter production wire-up next** — [AUDIT-002](audits/AUDIT-002_m2_dual_write.md) |
| Track D robustness | **In progress** | D0/D0b + **D1–D4** complete; D5 OC research lane |
| Re-audit | After 15 | → ROADMAP_V5 |

---

## Appendix: Investigation → phase map

| Investigation | Title (short) | Phase |
|---------------|---------------|-------|
| INV-004 | SCM jackknife zero power | 11 |
| INV-003 | Multi-treated aggregation semantics | 12 |
| INV-008 | BRB OC after bound fix / Run 002 | 12 |
| INV-007 | KFold geometry characterization | 12 |
| INV-017 | Calibration scaling and governance | 12 |
| INV-039 | Package calibration claim | 11–13 |
| INV-005, INV-006, INV-032 | DID pretrend / intervals / timing | Deferred (DEF-016); was v4 draft Phase 14 |
| INV-028 | AugSynth OC characterization | 14 (complete) |
| INV-029 | Placebo inference OC | 15 |
| INV-018, INV-037 | CVXPY / collinearity | 14 (partial — AugSynth stress) |
| INV-011, INV-019 | SDID staggered validation | Research backlog |
| INV-009 | Spillover | Research backlog |
| INV-001, INV-002, INV-036 | Estimand / pooling / truth | Ongoing documentation; not a promotion shortcut |
| INV-020 | Unified experimentation estimand contracts | Track C |
| INV-021 | User-randomized TrustReport semantics | Track C |
| INV-022 | Experiment feasibility & viability governance | Track C |
| INV-023 | Experiment-to-MMM compatibility resolver | Track C |
| INV-024 | Sequential experimentation governance | Track C |
| INV-025 | Randomization integrity & SRM diagnostics | Track C |
| INV-026 | Exposure eligibility & opportunity logging | Track C |

---

*Roadmap v4 active for Phases 11–15. Priorities frozen via [`OPEN_INVESTIGATIONS.md`](OPEN_INVESTIGATIONS.md). Supersedes v3 for forward execution order only; v3 remains historical record for Phases 5–8.*
