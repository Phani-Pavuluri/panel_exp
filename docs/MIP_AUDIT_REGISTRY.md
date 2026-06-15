# MIP audit registry

**Program ID:** MIP-PERIODIC-AUDIT  
**Status:** active  
**Last updated:** 2026-06-02 (AUDIT-010A roadmap consistency gate)  

**Template:** [`MIP_PERIODIC_ARCHITECTURE_AND_ROBUSTNESS_AUDIT_TEMPLATE.md`](MIP_PERIODIC_ARCHITECTURE_AND_ROBUSTNESS_AUDIT_TEMPLATE.md)  
**Alignment gate:** [`ROADMAP_ALIGNMENT_GATE.md`](ROADMAP_ALIGNMENT_GATE.md)

Living index of periodic audits. Each row must link to a filled report (or `docs/audits/AUDIT-NNN_*.md`) when complete.

---

## Program summary

| Field | Value |
|-------|--------|
| **Purpose** | Assess whether implemented work, roadmap direction, scientific rigor, architecture, and governance remain aligned to the MIP north star |
| **Cadence** | After every major milestone; before production-promotion decisions |
| **Success criterion** | No untracked gaps, orphan findings, unsupported methods, or roadmap drift |

---

## Audit index

| Audit ID | Date | Milestone / scope | Commit | Overall verdict | Critical gaps (short) | Follow-up | Status |
|----------|------|-------------------|--------|-----------------|----------------------|-----------|--------|
| **AUDIT-001** | 2026-05-28 | B5c + B5d + alignment gate (`f3df38b`) | `f3df38b` | `continue_with_minor_corrections` | M2 not on mainline; no production TrustReport; Track D D1+ not started | Commit M2; run **AUDIT-002**; wire adapter on real GeoX | **closed** (summary below) |
| **AUDIT-002** | 2026-05-28 | M2 dual-write + live adapter compare | `2754c0a` | `continue_with_minor_corrections` | Prod TrustReport; real-bundle adapter hardening; Track D D1+ | Adapter wire-up on GeoX; then Track D D1 | **closed** |
| **AUDIT-003** | 2026-05-28 | M2.1 wire-up gate (before Track D D1) | `5000fc5` | `continue_with_minor_corrections` | GeoX main export hook; M2.2 TrustReport; Track D D1 optional | **M2.2** prod lane; D1 research optional | **closed** |
| **AUDIT-004** | 2026-05-28 | M2.2 TrustReport sidecar gate | `ec2d351` | `continue_with_minor_corrections` | Product UI consumer; `__init__` re-exports; Track D D1+ | Track D D1 research lane | **closed** |
| **AUDIT-005** | 2026-05-28 | Track D D1 design/matching (research lane) | `7af9ef9` | `continue_with_characterization_required` | Pre-period matching risk (D1-FIND-001); D5 OC pending | D5 design OC; D2 | **closed** (research) |
| **AUDIT-006** | 2026-05-28 | Track D D2 estimator/donor (research lane) | `1a31e69` | `continue_with_characterization_required` | `full_model` SCM fit risk (D2-FIND-001); D5 OC pending | INV-D2-001; D3; D5-EST-002a | **closed** (research) |
| **AUDIT-007** | 2026-05-28 | Track D D3 inference (research lane) | `fed7050` | `continue_with_characterization_required` | JK LOO target review (D3-FIND-001); eligibility unchanged | INV-D3-001; D5-INF-002a; D4 | **closed** (research) |
| **AUDIT-008** | 2026-06-01 | Track D D4 power/MDE (research lane) | `24beae8` | `continue_with_characterization_required` | Power ≠ SCM JK readout; aggregation | D5-POW-001a; E1 | **closed** (research) |
| **AUDIT-009** | 2026-06-01 | Track E E1–E7 completion gate | `79c59c4` | `continue` | Live export lacks auto profile assembly (E7-FIND-001) | AUDIT-010A ✅; ~~D5-INST-TBR-001~~ ✅ → AUDIT-010 | **closed** |
| **AUDIT-010A** | 2026-06-02 | Roadmap consistency pre-MMM (post Track F + Kfold OC) | `ebc899c` | `continue_with_minor_corrections` | Stale MCELL next-lines; Track F P0/TBR sequence; DESIGN §13 Kfold | ~~D5-INST-TBR-001~~ ✅ → **AUDIT-010** | **closed** |
| **AUDIT-010** | 2026-06-03 | MMM readiness / gap (not promotion) | `696045a` | **`not_ready_continue_track_f`** | MMM blocked; CS no expansion; 30-tuple Appendix A | **Track F P2 OC** | **closed** |
| **AUDIT-011** | — | Before LLM interface | TBD | — | Blocked on [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md) §6 exit | — | **planned** (LLM paused) |

---

## AUDIT-001 summary (B5c + B5d + alignment gate)

**Scope:** Track B contract discipline through B5d; research lane added to alignment gate.

**Strengths**

1. Fixture-oracle pipeline is executable: composer (B5c) + validator (B5d) + F1–F12 guards.  
2. Trust boundary is test-proven: verdicts only on TrustReport scenarios.  
3. Research lane prevents the gate from blocking Track D while keeping promotion strict.

**Risks**

1. **Fixture–production gap:** Golden slices are authoritative; real GeoX RunBundle dual-write was not yet on mainline at audit time.  
2. **Statistical claims still pre-D1:** Contracts prevent semantic lies; OC/math audits not yet executed.  
3. **Component illusion:** Rich docs/fixtures can feel “done” without product path.

**Missing pieces**

1. M2 dual-write committed and audited (→ AUDIT-002).  
2. `resolve_adapter_output` on production export paths (not only fixture slice).  
3. Track D D1+ under research lane after M2.

**Verdict:** `continue_with_minor_corrections` — stay on production path B5 → M2 → adapter wire-up; keep Track D in research lane.

**Full report:** Use template sections 1–11 when copying to `docs/audits/AUDIT-001_b5_alignment_gate.md` for archival detail.

---

## AUDIT-002 summary (M2 dual-write)

**Report:** [`audits/AUDIT-002_m2_dual_write.md`](audits/AUDIT-002_m2_dual_write.md)

**Verdict:** `continue_with_minor_corrections` — M2 alignment gate stop conditions **met** (313 tests; 14/14 live adapter oracle; legacy bundle schema stable; opt-in sidecar).

**Confirmed**

1. Legacy RunBundle unchanged when `include_track_b_views=False`.  
2. `track_b_views` sidecar-only; no legacy key replacement.  
3. No `alignment_verdict` / `trust_outcome` on adapter or evidence layers.  
4. Unmapped `config_alias` → `export_status: blocked` (no ID guessing).

**Remaining gaps (explicit)**

1. Production TrustReport path not wired.  
2. Track D D1+ robustness audits not started (research lane; do not skip).  
3. Bundle metadata extraction from all real GeoX runs not yet proven.

**Next production-lane item:** M2.2 production TrustReport path (AUDIT-003 gate passed).

---

## AUDIT-003 summary (M2.1 wire-up gate)

**Report:** [`audits/AUDIT-003_m2_1_wire_up_gate.md`](audits/AUDIT-003_m2_1_wire_up_gate.md)

**Verdict:** `continue_with_minor_corrections` — **gate passed**; M2.1 meets AUDIT-002 follow-up.

**Confirmed**

1. Five representative RunBundles (REP-001–005): complete, blocked, partial explicit.  
2. `extract_resolve_input_from_bundle` — no estimand-from-estimator guess; cataloged `estimator+inference_mode` only.  
3. Legacy `build_run_artifact_bundle` default unchanged (`include_track_b_views=False`).  
4. No `alignment_verdict` / `trust_outcome` on adapter or evidence (REP + B5 boundary).  
5. Production TrustReport deferred (M2.2 next); Track D D1+ not started (eligible research-lane parallel).

**Post-gate decision**

| Path | Status |
|------|--------|
| **M2.2** production TrustReport | **Recommended next** (production lane) |
| **Track D D1** | Allowed in parallel (research lane only) |
| **More M2.1 hardening** | Only on new live GeoX shape failures |

---

## AUDIT-004 summary (M2.2 TrustReport sidecar gate)

**Report:** [`audits/AUDIT-004_m2_2_trust_report_gate.md`](audits/AUDIT-004_m2_2_trust_report_gate.md)

**Verdict:** `continue_with_minor_corrections` — **gate passed**; production TrustReport opt-in on `track_b_views`.

**Confirmed**

1. Verdicts only on `trust_report_view.scenarios`; adapter/evidence fact-only.  
2. Missing scenarios → `trust_report_omit_reason: missing_trust_scenarios`.  
3. `export_geo_run_bundle` / `GeoExperimentDesign.export_run_readout_bundle` wired; defaults off.  
4. GOLD-001 export oracle parity; REP blocked/partial TrustReport paths.  
5. No estimator/scoring/eligibility changes; Track D D1+ not started.

**Post-gate decision**

| Path | Status |
|------|--------|
| **Track D D1** | **Eligible** (research lane) |
| **Product TrustReport consumer** | Next integration when ready |
| **Track B `__init__.py` re-exports** | Minor follow-up (uncommitted at audit) |

**Next item:** Track D D1 under research lane, or Track B consumer wiring.

---

## AUDIT-005 summary (Track D D1 — research lane)

**Report:** [`TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md`](TRACK_D_D1_DESIGN_MATCHING_AUDIT_001.md)

**Verdict:** `continue_with_characterization_required` — D1 package complete; **no** production promotion.

**Confirmed**

1. Geo-run designs and MAT-001 audited; matrix statuses updated.  
2. DG-007 validation gate **restricted** (integrity, not matching correctness).  
3. No estimator/inference/eligibility/maturity changes in D1.  
4. TrustReport boundary unchanged.

**Top finding:** D1-FIND-001 — default geo pipeline matched on full panel when `pre_treatment_period` was not passed (fixed `61a174f`).

**Post-fix checkpoint:** D5-DES-001a Jaccard fixed vs pre-only **1.00** — D2 eligible under research lane.

**Next:** D2 estimator/donor audit (→ AUDIT-006).

---

## AUDIT-006 summary (Track D D2 — research lane)

**Report:** [`TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md`](TRACK_D_D2_ESTIMATOR_AND_DONOR_AUDIT_001.md)

**Verdict:** `continue_with_characterization_required` — D2 package complete; **no** production promotion.

**Confirmed**

1. Default SCM CVXPY path fits on pre-period only; treated units excluded from donor pool.  
2. Estimator vs inference separation intact (`ImpactAnalyzer` + inference registry).  
3. MAT-004/005 and EST-001–004 receive explicit robustness statuses.  
4. No estimator/inference/TrustReport/eligibility changes in D2.  
5. CalibrationSignal eligibility **unchanged** (SCM JK null-monitor only).

**Top finding:** D2-FIND-001 — `full_model=True` fits SCM weights on post-period columns → propose **INV-D2-001** (separate governed fix PR).

**Next:** D3 inference audit (→ AUDIT-007).

---

## AUDIT-007 summary (Track D D3 — research lane)

**Report:** [`TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md`](TRACK_D_D3_INFERENCE_METHOD_AUDIT_001.md)

**Verdict:** `continue_with_characterization_required` — D3 package complete; **no** production promotion.

**Confirmed**

1. INF-001–010 audited with explicit governance roles.  
2. Registry `IntervalType` / Track B `interval_semantics` separation intact.  
3. SCM JK **null_monitor_only** — sole `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` member (unchanged).  
4. Placebo **diagnostic_only**, single-treated scope (Phase 15).  
5. No inference/TrustReport/eligibility code changes in D3.

**Top finding:** D3-FIND-001 — Unit JK LOO compares `y_hat` to observed `y` → **INV-D3-001** opened (D5-INF-002a).

**Next:** D5-MCELL ✅ → instrument OC chain (see AUDIT-010A).

---

## AUDIT-008 summary (Track D D4 — research lane)

**Report:** [`TRACK_D_D4_POWER_MDE_AUDIT_001.md`](TRACK_D_D4_POWER_MDE_AUDIT_001.md)

**Verdict:** `continue_with_characterization_required` — D4 complete; **no** production promotion.

**Confirmed**

1. `PowerAnalysis` semantics and `power_contract` are explicit (simulation-coverage, not classical).  
2. Default geo path uses TBRRidge+Kfold on aggregated 2-row panel — **not** SCM JK readout.  
3. POW rows updated; D5-POW-001a–e specified.  
4. No code / TrustReport / eligibility changes in D4.

**Top finding:** D4-FIND-001 — design MDE not aligned to `SCM_UnitJackKnife` instrument.

**Next:** D5-MCELL ✅; ~~D5-INST-TBR-001~~ ✅ → **AUDIT-010**.

---

## ROADMAP-DESIGN-READOUT-UPDATE-001 checkpoint (2026-06-01)

**Doc:** [`ROADMAP_DESIGN_READOUT_UPDATE_001.md`](ROADMAP_DESIGN_READOUT_UPDATE_001.md)

**Corrections before D5-POW-001e:**

- SCM+UnitJackKnife = **reference null-monitor branch** only (not universal readout / platform MDE / lift detection).  
- Power/OC = **design-method × geometry-mode × measurement-instrument** specific.  
- Multi-cell = **geometry mode** (`n_test_grps > 1`), not a design method.  
- **supergeos** / **trimmedmatch** in roadmap (D5-DES-SUPERGEO-001, D5-DES-TRIM-001); not ignored.  
- D5-POW-001e **complete** — see checkpoint below.

---

## Track E E1/E2 checkpoint (2026-06-01)

**Docs:** [`TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md`](TRACK_E_E1_SUITABILITY_DIAGNOSTIC_INVENTORY_001.md) · [`TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md`](TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001.md)

**Verdict:** Documentation contract complete — eight diagnostic families; design/geometry/instrument cards grounded in D5-POW-001a–e. **Next:** E3/E4 (complete — see below).

---

## Track E E3/E4 checkpoint (2026-06-01)

**Docs:** [`TRACK_E_E3_TRIANGULATION_SCHEMA_001.md`](TRACK_E_E3_TRIANGULATION_SCHEMA_001.md) · [`TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md`](TRACK_E_E4_TRUSTREPORT_CONFLICT_FIXTURES_001.md)

**Fixtures:** [`tests/fixtures/track_e_conflicts/`](../../tests/fixtures/track_e_conflicts/) (E4-001 … E4-010)

**Verdict:** Triangulation schema + E4 fixtures complete. **Next:** E5/E6 (complete — see below).

---

## Track E E5/E6 checkpoint (2026-06-01)

**Docs:** [`TRACK_E_E5_CALIBRATIONSIGNAL_ELIGIBILITY_POLICY_001.md`](TRACK_E_E5_CALIBRATIONSIGNAL_ELIGIBILITY_POLICY_001.md)

**Tests:** E6 [`tests/track_e/test_e6_e4_conflict_fixtures.py`](../tests/track_e/test_e6_e4_conflict_fixtures.py) · E7 [`tests/track_b/test_e7_track_e_trust_report.py`](../tests/track_b/test_e7_track_e_trust_report.py) · production [`panel_exp/track_b/triangulation.py`](../panel_exp/track_b/triangulation.py)

**Verdict:** E5 maps E4 dispositions → CalibrationSignal eligibility (conditional weak null-monitor only; fail-closed on conflict/stale/missing uncertainty/pooled multi-cell). E6/E7: contract + production TrustReport composer assert all E4 fixtures — no averaging, no MMM outside CalibrationSignal, no restricted override. **E7 complete.**

---

## AUDIT-009 summary (Track E E1–E7 completion gate)

**Report:** [`audits/AUDIT-009_track_e_completion_gate.md`](audits/AUDIT-009_track_e_completion_gate.md)

**Verdict:** **`continue`** — Track E E1–E7 **complete**; production TrustReport wiring bounded; **no** MMM ingestion or instrument promotion.

**Confirmed**

1. E1/E2 classify design-method × geometry-mode × measurement-instrument (documentation).  
2. E3/E4 schema + 10 golden conflict fixtures with forbidden actions.  
3. E5/E6 policy + tests; production evaluator in `triangulation.py`.  
4. E7: `track_e_triangulation` only when `triangulation_profile` supplied; legacy `_interpret` unchanged.  
5. No changes to estimators, design, inference, or eligibility registry in E7 scope.

**Top finding:** E7-FIND-001 — `export_geo_run_bundle` does not auto-assemble triangulation profiles (product follow-up, not an E1–E7 blocker).

**Next:** ~~D5-INST-TBR-001~~ ✅ → **AUDIT-010** (MMM readiness/gap).

---

## D5-DES-SUPERGEO-001 checkpoint (2026-06-01)

**Artifact:** [`docs/track_d/archives/D5_DES_SUPERGEO_001_results.json`](track_d/archives/D5_DES_SUPERGEO_001_results.json)  
**Report:** [`docs/track_d/D5_DES_SUPERGEO_001_REPORT.md`](track_d/D5_DES_SUPERGEO_001_REPORT.md)  
**Harness:** `panel_exp/validation/track_d_d5_des_supergeo_001.py`

**Verdict:** **`requires_implementation_fix_before_oc`** — separate supergeo geometry confirmed; flat SCM+JK / 001e **blocked**; MILP scope mismatch (largest-cluster combos vs all-market assignment constraints). Track E GEO-003 stays **`characterization_required`**.

**Next:** D5-MCELL ✅; ~~D5-INST-TBR-001~~ ✅ → **AUDIT-010**.

---

## D5-DES-TRIM-001 checkpoint (2026-06-02)

**Artifact:** [`docs/track_d/archives/D5_DES_TRIM_001_results.json`](track_d/archives/D5_DES_TRIM_001_results.json)  
**Report:** [`docs/track_d/D5_DES_TRIM_001_REPORT.md`](track_d/D5_DES_TRIM_001_REPORT.md)  
**Harness:** `panel_exp/validation/track_d_d5_des_trim_001.py`

**Verdict:** **`target_population_shift_severe`** — Tp/Te pair design + trim excludes most markets; classical pair power on Te only; flat SCM+JK / 001e **blocked**. Track E GEO-004 stays **`characterization_required`**.

**Next:** Other instrument OC batteries; not MMM.

---

## D5-MCELL-001 checkpoint (2026-06-02)

**Artifact:** [`docs/track_d/archives/D5_MCELL_001_results.json`](track_d/archives/D5_MCELL_001_results.json)  
**Report:** [`docs/track_d/D5_MCELL_001_REPORT.md`](track_d/D5_MCELL_001_REPORT.md)  
**Harness:** `panel_exp/validation/track_d_d5_mcell_001.py`

**Verdict:** **`acceptable_with_caveats_two_cells`** — k≤2 for most tier-1 methods on n_geos=16 battery; conservative k≤1; k≥3 degrades. Per-cell SCM+JK only; no pooling.

**Next:** ~~D5-INST-TBR-001~~ ✅ → **AUDIT-010** (MMM readiness/gap) → MMM only if gaps closed.

---

---

## AUDIT-010A checkpoint (2026-06-02)

**Report:** [`docs/audits/AUDIT-010A_roadmap_consistency_pre_mmm_gate.md`](audits/AUDIT-010A_roadmap_consistency_pre_mmm_gate.md)

**Verdict:** **`continue_with_minor_corrections`** — roadmaps aligned after doc fixes; stale MCELL next-lines; Track F sequence corrected (TBR-001 → AUDIT-010 → P0 → P2). **Not** MMM approval.

**Next:** ~~D5-INST-TBR-001~~ ✅ → **AUDIT-010**.

---

## D5-INST-TBR-001 checkpoint (2026-06-03)

**Artifact:** [`docs/track_d/archives/D5_INST_TBR_001_results.json`](track_d/archives/D5_INST_TBR_001_results.json)  
**Report:** [`docs/track_d/D5_INST_TBR_001_REPORT.md`](track_d/D5_INST_TBR_001_REPORT.md)

**Verdict:** **`remain_restricted_aggregate_diagnostic`** — class TBR aggregate 1×1 only; point/Kfold callable; JK blocked on agg2; JKP unverified; not TBRRidge; not MMM-eligible.

**Next:** **AUDIT-010** charter → audit close.

---

## AUDIT-010 checkpoint (2026-06-03)

**Report:** [`docs/audits/AUDIT-010_mmm_readiness_gap.md`](audits/AUDIT-010_mmm_readiness_gap.md)

**Verdict:** **`not_ready_continue_track_f`** — MMM **not ready / blocked**; CalibrationSignal **no expansion**; Appendix A primary buckets A01–A30; **not** promotion.

**Next:** ~~Track F P0~~ ✅ → **Track F P2 OC**.

---

## Track F P0 hygiene checkpoint (2026-06-03)

**Code:** [`panel_exp/governance/instrument_contract.py`](../panel_exp/governance/instrument_contract.py) · [`tests/governance/test_track_f_p0_hygiene.py`](../tests/governance/test_track_f_p0_hygiene.py)

**Verdict:** **P0 complete** — F-P0-001…006 guards/tests; no CalibrationSignal expansion; no MMM ingress.

**Next:** ~~Track F P0~~ ✅ → ~~TBRRidge-002~~ ✅ → ~~AugSynth Conformal (003)~~ ✅ — **P2 complete**.

---

## D5-INST-TBRRIDGE-002 checkpoint (2026-06-03)

**Artifact:** [`docs/track_d/archives/D5_INST_TBRRIDGE_002_results.json`](track_d/archives/D5_INST_TBRRIDGE_002_results.json)  
**Report:** [`docs/track_d/D5_INST_TBRRIDGE_002_REPORT.md`](track_d/D5_INST_TBRRIDGE_002_REPORT.md)  
**Harness:** `panel_exp/validation/track_d_d5_inst_tbrridge_002.py`

**Verdict:** **`remain_restricted_no_promotion`** — JK/JKP/Conformal blocked_interface; TimeSeriesKfold callable_unverified; Bayesian INV-015.

**Next:** **D5-INST-AUGSYNTH-003** (Conformal).

---

## D5-INST-AUGSYNTH-003 checkpoint (2026-06-03)

**Artifact:** [`docs/track_d/archives/D5_INST_AUGSYNTH_003_results.json`](track_d/archives/D5_INST_AUGSYNTH_003_results.json)  
**Report:** [`docs/track_d/D5_INST_AUGSYNTH_003_REPORT.md`](track_d/D5_INST_AUGSYNTH_003_REPORT.md)  
**Harness:** `panel_exp/validation/track_d_d5_inst_augsynth_003.py`

**Verdict:** **`callable_unverified_interval_semantics`** — interface-valid on 001e; 100% negative half-width and 100% null interval-exclusion FPR; not governed uncertainty; no promotion.

**Next:** Track F **P2 complete** — [`TRACK_F_P2_CLOSEOUT_001.md`](TRACK_F_P2_CLOSEOUT_001.md) — implementation backlog (F-INF / F-GEO / F-CAT).

---

## TRACK-F-P2-CLOSEOUT-001 checkpoint (2026-06-03)

**Artifact:** [`docs/TRACK_F_P2_CLOSEOUT_001.md`](TRACK_F_P2_CLOSEOUT_001.md)

**Verdict:** **Track F P2 formally closed** — no additional OC batteries scheduled; promotion not authorized.

**Next lane:** ~~TBRRIDGE-003~~ ✅ → **[TRACK-F-IMPLEMENTATION-CHECKPOINT-001](TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md)** (pause default)

---

## F-DECISION-001 checkpoint (2026-06-03)

**Artifact:** [`docs/F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md`](F_DECISION_001_METHOD_ELIGIBILITY_AND_DECISION_POLICY.md)  
**Code:** [`panel_exp/governance/decision_policy.py`](../panel_exp/governance/decision_policy.py) · [`tests/governance/test_f_decision_001_decision_policy.py`](../tests/governance/test_f_decision_001_decision_policy.py)

**Verdict:** Method eligibility resolver + evidence comparison policy complete; consumes F-INF/F-GEO/F-CAT; no promotion/MMM/CS expansion.

**Next:** ~~Governance PR~~ — package with F-BACKLOG-002; TrustReport integration (no new Track F OC).

---

## F-BACKLOG-002 checkpoint (2026-06-03)

**Artifact:** [`docs/F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md`](F_BACKLOG_002_INDUSTRY_RELEVANCE_REVIEW.md)

**Verdict:** Parked estimator/inference/design items re-ranked by external importance × internal readiness × product fit; **external importance does not override** AUDIT-010 / F-DECISION-001 gates.

**Surfaced:** SCM+JK null monitor, characterized diagnostics (A05/A18/A19), placebo falsification, class TBR aggregate diagnostic.

**Blocked/buried:** Registry Bayesian, TROP prod, pooled multi-cell, supergeo/trim SCM+JK without ADR.

**Next program lanes:** design ADRs (F-MCELL-001, F-GEO-003/004, F-CAT-002, F-P0-004); optional OC (A09, per-cell); research charters RTP-001..004; **no promotion candidates**.

**Prerequisites:** TRACK-F-IMPLEMENTATION-CHECKPOINT-001 · F-DECISION-001 · F-BACKLOG-001.

---

## GOVERNANCE-PR-TRACK-F-DECISION-PACKAGE-001 (2026-06-03)

**Artifact:** [`docs/GOVERNANCE_PR_TRACK_F_DECISION_PACKAGE_001.md`](GOVERNANCE_PR_TRACK_F_DECISION_PACKAGE_001.md)

**Verdict:** Governance PR summary **ready** — documents commit spine (F-INF-002 → TBRRIDGE-003 → CHECKPOINT → F-DECISION-001 → F-BACKLOG-002 `97e7acc`); decision-safe layer; guardrails; **TrustReport integration** authorized as **next** engineering step (separate PR).

**Not in this package:** TrustReport wiring, OC, promotion, MMM, CalibrationSignal expansion.

**Next:** ~~TrustReport integration~~ ✅ TRUSTREPORT-F-DECISION-INTEGRATION-001.

---

## TRUSTREPORT-F-DECISION-INTEGRATION-001 (2026-06-03)

**Artifact:** [`docs/TRUSTREPORT_F_DECISION_INTEGRATION_001.md`](TRUSTREPORT_F_DECISION_INTEGRATION_001.md)  
**Code:** [`panel_exp/track_b/f_decision_context.py`](../panel_exp/track_b/f_decision_context.py) · [`panel_exp/track_b/trust_report.py`](../panel_exp/track_b/trust_report.py) · [`tests/track_b/test_trustreport_f_decision_integration_001.py`](../tests/track_b/test_trustreport_f_decision_integration_001.py)

**Verdict:** Optional TrustReport `f_decision_context` from F-DECISION-001; legacy exports unchanged; guardrails enforced; no promotion/MMM/CS/OC.

---

## TRUSTREPORT-DECISION-INPUTS-WIRING-001 (2026-06-03)

**Artifact:** [`docs/TRUSTREPORT_DECISION_INPUTS_WIRING_001.md`](TRUSTREPORT_DECISION_INPUTS_WIRING_001.md)  
**Code:** [`panel_exp/track_b/readout_evidence_wiring.py`](../panel_exp/track_b/readout_evidence_wiring.py) · [`tests/track_b/test_trustreport_decision_inputs_wiring_001.py`](../tests/track_b/test_trustreport_decision_inputs_wiring_001.py)

**Verdict:** `include_trust_report_decision_context` wires bundle metadata → `TrustReportDecisionInputs` → `f_decision_context` on export; default off.

---

## TRUSTREPORT-DECISION-CONTEXT-SMOKE-001 (2026-06-03)

**Artifact:** [`docs/TRUSTREPORT_DECISION_CONTEXT_SMOKE_001.md`](TRUSTREPORT_DECISION_CONTEXT_SMOKE_001.md) · [`docs/track_b/archives/TRUSTREPORT_DECISION_CONTEXT_SMOKE_001_export.json`](track_b/archives/TRUSTREPORT_DECISION_CONTEXT_SMOKE_001_export.json)  
**Tests:** [`tests/track_b/test_trustreport_decision_context_smoke_001.py`](../tests/track_b/test_trustreport_decision_context_smoke_001.py)

**Verdict:** Export smoke passes — opt-in `f_decision_context` on realistic geo bundle; legacy shape when flag off; guardrails + incomplete-metadata warning path.

---

## METHOD-READINESS-AND-COMPATIBILITY-MATRIX-001 (2026-06-03)

**Artifact:** [`docs/METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md`](METHOD_READINESS_AND_COMPATIBILITY_MATRIX_001.md)

**Verdict:** Layered readiness — estimator table, inference table, combination/promotion table; F-BACKLOG-002 as rank input; top strengthen lists + blocked-despite-importance + next-artifact map. **No promotion.**

**Prerequisites:** F-BACKLOG-002 · AUDIT-010 · F-DECISION-001 · CV-001.

---

## METHOD-SELECTION-AND-PROMOTION-FRAMEWORK-001 (2026-06-03)

**Artifact:** [`docs/METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md`](METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001.md)

**Verdict:** Promotion **pipeline** (not freeze) — data-structure routing, candidate selection (L1+L2+L3), benchmark vs A26, role-specific promotion lanes; **METHOD-PROMOTION-AUDIT-TEMPLATE-001** required for future role upgrades; **0** promotions authorized.

**Prerequisites:** METHOD-READINESS-AND-COMPATIBILITY-MATRIX-001 · F-BACKLOG-002 · F-DECISION-001 (baseline until audit).

**Future artifact:** METHOD-PROMOTION-AUDIT-TEMPLATE-001 (placeholder: [`METHOD_PROMOTION_AUDIT_TEMPLATE_001.md`](METHOD_PROMOTION_AUDIT_TEMPLATE_001.md)).

**Downstream:** [`METHOD_STRENGTHENING_LANES_001.md`](METHOD_STRENGTHENING_LANES_001.md) — strengthening work packages; does not duplicate routing.

---

## METHOD-STRENGTHENING-LANES-001 (2026-06-03)

**Artifact:** [`docs/METHOD_STRENGTHENING_LANES_001.md`](METHOD_STRENGTHENING_LANES_001.md)

**Verdict:** Strengthening layer — estimator / inference / combination evidence categories; first lanes AUGSYNTH_ASCM, TBR_AGGREGATE, MULTICELL, TRIM_SUPERGEO, BAYESIAN_TBR_TROP_RTP; entry/exit criteria; next-artifact map. **Not promotion**; no TrustReport / F-DECISION / CS / MMM change.

**Prerequisites:** METHOD-SELECTION-AND-PROMOTION-FRAMEWORK-001 · METHOD-READINESS matrix · F-BACKLOG-002 · F-DECISION-001 (baseline).

---

## AUGSYNTH-ASCM-STRENGTHENING-001 (2026-06-03)

**Artifact:** [`docs/AUGSYNTH_ASCM_STRENGTHENING_001.md`](AUGSYNTH_ASCM_STRENGTHENING_001.md)

**Verdict:** Strengthening **charter** for LANE-ASCM-001 — literature/implementation checklists, pre-OC diagnostics, candidate inference pairings (A05/A01–A03 vs A26), **D5-INST-AUGSYNTH-ASCM-002** executed, promotion-audit entry criteria. **No role change**; CS/MMM/TrustReport/F-DECISION unchanged.

**Prerequisites:** METHOD-STRENGTHENING-LANES-001 §3.1 · D5-INST-AUGSYNTH-001/003/KFOLD · CV-EST-AUGSYNTH.

**Next:** [`SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md) ✅; optional **D5-INST-AUGSYNTH-ASCM-003** (threshold calibration); then P2 design–readout audit.

---

## D5-INST-AUGSYNTH-ASCM-002 checkpoint (2026-06-03)

**Artifact:** [`docs/track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json`](track_d/archives/D5_INST_AUGSYNTH_ASCM_002_results.json)  
**Report:** [`docs/track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md`](track_d/D5_INST_AUGSYNTH_ASCM_002_REPORT.md)  
**Harness:** [`panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py`](../panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py)

**Verdict:** `remain_diagnostic_comparator` — 12 stratified worlds vs A26; partial weak-fit MAE gain (1/2 @ 8%); JK null FPR conservative; Conformal unsafe; **promotion_audit_eligible: false**.

**Prerequisites:** AUGSYNTH-ASCM-STRENGTHENING-001 · D5-INST-AUGSYNTH-001/003/KFOLD.

---

## AUGSYNTH-ASCM-INFERENCE-PAIRING-ADR-001 (2026-06-03)

**Artifact:** [`docs/AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md`](AUGSYNTH_ASCM_INFERENCE_PAIRING_ADR_001.md)

**Verdict:** **Accepted** — post-ASCM-002 inference pairing policy: **no promotion**; Conformal **keep_restricted**; JK diagnostic + optional future OC; A26 unchanged.

**Prerequisites:** ASCM-002 · AUGSYNTH-ASCM-STRENGTHENING-001 · F-INF-001 · F-DECISION-001.

---

## METHOD-FOUNDATION-HARDENING-001 (2026-06-03)

**Artifact:** [`docs/METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md)

**Verdict:** Pre-LLM foundation phase plan — **LLM paused**; gap registry; lanes P0 complete → P1 threshold audit ✅ (calibration via ASCM-003 open). **No production/promotion/CS/MMM/LLM integration.**

**Prerequisites:** METHOD-READINESS matrix · METHOD-SELECTION · METHOD-STRENGTHENING · ADR-001 · F-DECISION-001.

**Next program lane:** P2 design–readout compatibility audit per [`METHOD_FOUNDATION_HARDENING_001.md`](METHOD_FOUNDATION_HARDENING_001.md); optional research OC **D5-INST-AUGSYNTH-ASCM-003** for P1 threshold calibration.

**AUDIT-011 linkage:** LLM interface **planned** until foundation hardening exit criteria met (P1 audit complete; ASCM-003 calibration open).

---

## SCM-AUGSYNTH-DIAGNOSTIC-THRESHOLD-AUDIT-001 (2026-06-03)

**Artifact:** [`docs/SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md`](SCM_AUGSYNTH_DIAGNOSTIC_THRESHOLD_AUDIT_001.md)

**Verdict:** Provisional diagnostic **label vocabulary** and threshold **types** for SCM/A26 and AugSynth/ASCM (fit, hull, sparsity, disagreement, false-confidence). **No promotion**; **no F-DECISION/TrustReport behavior change**.

**Prerequisites:** METHOD-FOUNDATION-HARDENING-001 P1 · ASCM-002 · ADR-001 · AUGSYNTH-ASCM-STRENGTHENING-001 §5 · F-DECISION-001 disagreement policy.

**Next:** **D5-INST-AUGSYNTH-ASCM-003** — fidelity audit ✅ [`AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md`](AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md); uses D5-DIAG diagnostics.

---

## AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001 (2026-06-03)

**Artifact:** [`docs/AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md`](AUGSYNTH_ASCM_IMPLEMENTATION_FIDELITY_AUDIT_001.md)

**Verdict:** **`fidelity_confirmed_with_caveats`** — `AugSynthCVXPY` implements SCM + Ridge-on-residuals ASCM; gaps in diagnostic SCM leg alignment, estimand reporting, D8 grid. **No mandatory fix before OC.**

**Prerequisites:** ASCM-002 · threshold audit · D5-DIAG-SCM-AUGSYNTH-001.

**Next:** **D5-INST-AUGSYNTH-ASCM-003**.

---

## METHOD-SOUNDNESS-AND-GAP-ROADMAP-001 (2026-06-03)

**Artifact:** [`docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md`](METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md)

**Verdict:** Audit-derived **development-first** method soundness inventory, gap taxonomy, scorecard, and sequenced development lanes (DL-0–DL-8). Reconciles Track D audits and 25 OC JSON archives; **no new eligibility decisions**; **`restricted` = development needed**.

**Prerequisites:** TRACK-D inventory · D2/D3/D4 · CV-001 · AUDIT-010 · METHOD-FOUNDATION-HARDENING-001 · threshold audit · F-DECISION-001.

**Next active lane (DL-1):** ✅ development roadmap **materialized** → ✅ D5-DIAG **complete** → ✅ fidelity audit **complete** → **D5-INST-AUGSYNTH-ASCM-003**.

---

## D5-DIAG-SCM-AUGSYNTH-001 (2026-06-03)

**Artifact:** [`docs/track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md`](track_d/D5_DIAG_SCM_AUGSYNTH_001_REPORT.md)  
**Module:** [`panel_exp/validation/scm_augsynth_diagnostics.py`](../panel_exp/validation/scm_augsynth_diagnostics.py)

**Verdict:** Reusable SCM/AugSynth diagnostic helpers (D1–D11 descriptive fields); integrated into ASCM-002 harness. **No threshold finalization**; **no promotion**; **no prod behavior change**.

**Prerequisites:** Threshold audit · ASCM-002 harness · METHOD-SOUNDNESS-ROADMAP-REVIEW-001 · AUGSYNTH-ASCM-DEVELOPMENT-ROADMAP-001.

**Next:** ✅ fidelity audit complete → **D5-INST-AUGSYNTH-ASCM-003**.

**Review checkpoint:** [`METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md) — **`proceed_to_augsynth_development_lane`**.

**Bridge:** Foundation hardening → soundness roadmap → **review checkpoint** → DL-1 execution → AUDIT-011 (LLM paused).

---

## METHOD-VALIDATION-PROGRAM-001 (2026-06-04)

**Artifact:** [`docs/METHOD_VALIDATION_PROGRAM_001.md`](METHOD_VALIDATION_PROGRAM_001.md)

**Status:** **`authoritative_method_foundation_sequence`**

**Verdict:** Layered validation program (code inventory → literature → implementation → statistical OC → combination matrix) **before** trust-framework / method-role expansion. Pauses default MCELL OC and TrustReport/F-DECISION/CalibrationSignal/MMM role growth until layers 1–5 complete.

**Prerequisites:** Prior audits retained as `evidence_input` only.

**Next:** ✅ Layers 1–5 + suitability + smoke + SCM+JK + AugSynth point + TBR aggregate + DID bootstrap + MCELL per-cell + **TBRRidge inference Level B**.

---

## METHOD-ENHANCEMENT-ROADMAP-001 (2026-06-09)

**Artifact:** [`docs/METHOD_ENHANCEMENT_ROADMAP_001.md`](METHOD_ENHANCEMENT_ROADMAP_001.md)

**Status:** **`post_level_b_synthesis_planning`**

**Verdict:** Synthesizes D5-STAT Level B findings (smoke through MCELL per-cell) into twelve enhancement lanes (readout semantics, geometry bridges, SCM/AugSynth/TBR/DID/MCELL fixes, TBRRidge/SARIMAX/Bayesian contracts). **Not** promotion, suitability, or TrustReport wiring.

**Prerequisites:** D5-STAT queue through **`D5-STAT-MCELL-PERCELL-001`** complete.

**Next planning/enhancement:** **`DESIGN_SUITABILITY_REASSESSMENT_001`** (design-side). Guardrail runtime: [`DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001.md`](DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001.md) (**Accepted**; 0/31 contract-complete).

---

## INFERENCE-READOUT-SEMANTICS-001 (2026-06-09)

**Artifact:** [`docs/INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md)

**Status:** **`accepted_post_d5_semantic_contract`**

**Verdict:** Canonical readout semantics for effect scale, point/interval targets, coverage, null vs directional rules, and prediction vs causal uncertainty. **Documentation/governance only** — no code changes, no promotion.

**Prerequisites:** D5-STAT Level B queue complete through **`D5-STAT-TBRRIDGE-INF-001`**.

**Feeds:** `GEOMETRY_BRIDGE_REQUIREMENTS_001` · suitability framework v2 · protocol v2 · matrix v2 · method-family enhancement lanes.

**Next:** **`DESIGN_OUTPUT_CONTRACT_001`**.

---

## GEOMETRY-BRIDGE-REQUIREMENTS-001 (2026-06-09)

**Artifact:** [`docs/GEOMETRY_BRIDGE_REQUIREMENTS_001.md`](GEOMETRY_BRIDGE_REQUIREMENTS_001.md)

**Status:** **`accepted_post_d5_geometry_contract`**

**Verdict:** Canonical geometry types, allowed/blocked/bridge-required transitions, multi-cell/supergeo/trim rules, and D5 geometry backfill. **Documentation/governance only** — no code changes, no promotion.

**Prerequisites:** [`INFERENCE_READOUT_SEMANTICS_001.md`](INFERENCE_READOUT_SEMANTICS_001.md) (**Accepted**); D5 Level B queue complete.

**Feeds:** `DESIGN_OUTPUT_CONTRACT_001` · method-family enhancement lanes · suitability v2 · matrix v2 · protocol v2.

**Next:** **`DESIGN_OUTPUT_CONTRACT_001`**.

---

## TRIPLY-ROBUST-ESTIMATOR-AUDIT-PROGRAM-001 (2026-06-09)

**Artifact:** [`docs/TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md`](TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.md)

**Status:** **`proposed_parked_future_estimator`**

**Verdict:** Parks triply robust / TROP as a **future candidate estimator family** with full audit ladder (literature → implementation gap → validation protocol → combination matrix → suitability extension → optional D5). **Not rejected.** Existing `TROP` code remains `research_only`; validation runner skipped. **No implementation** in this artifact.

**Prerequisites:** Readout semantics + geometry bridge Accepted; `DESIGN_OUTPUT_CONTRACT_001` before TROP audit execution.

**Feeds:** Future TROP audit sequence; does not change immediate enhancement queue.

**Program next (unchanged):** **`DESIGN_SUITABILITY_REASSESSMENT_001`** (design-side).

---

## DESIGN-AUDIT-PROGRAM-001 (2026-06-09)

**Artifact:** [`docs/DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md)

**Status:** **`accepted_design_audit_program`**

**Verdict:** Establishes design-side audit ladder matching estimator/inference rigor. Repository discovery of 10 design implementations + helpers; concurrency/supergeo/trim guardrails. Estimator/inference audit parity **incomplete** until design ladder completes. **Documentation/governance only** — no code changes, no promotion.

**Prerequisites:** Readout semantics + geometry bridge Accepted.

**Feeds:** `DESIGN_OUTPUT_CONTRACT_001` ✅ → `DESIGN_CODE_INVENTORY_001` ✅ → `DESIGN_LITERATURE_ALIGNMENT_001` ✅ → `DESIGN_IMPLEMENTATION_VALIDATION_001` ✅ → statistical protocol → combination matrix → guardrails → design suitability.

**Immediate next:** **`DESIGN_SUITABILITY_REASSESSMENT_001`**.

---

## DESIGN-OUTPUT-CONTRACT-001 (2026-06-09)

**Artifact:** [`docs/DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md)

**Status:** **`accepted_design_output_contract`**

**Verdict:** Governed **DesignOutputContract** schema for all designs (identity, assignment, geometry, multi-cell, trim/supergeo, balance, power/MDE, forbidden claims, PASS/WARN/BLOCK). Operationalizes geometry bridge + readout semantics + design audit program. **No implementation** — current `DesignEvidence` partial only.

**Prerequisites:** [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) Accepted; readout + geometry bridge Accepted.

**Feeds:** ✅ `DESIGN_CODE_INVENTORY_001` → design validation ladder → combination matrix v2 → experiment planning (deferred).

**Next:** **`DESIGN_SUITABILITY_REASSESSMENT_001`**.

---

## DESIGN-CODE-INVENTORY-001 (2026-06-09)

**Artifact:** [`docs/DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md)

**Status:** **`accepted_design_code_inventory`**

**Verdict:** Authoritative design-side code inventory — 31 rows (10 registered designs + wrapper + multi-cell + helpers/output/governance). Maps emitted fields to [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md). **0 contract-complete implementations.** Verdict: `design_code_inventory_complete_contract_gaps_identified`. **Documentation/governance only** — no code changes, no promotion.

**Prerequisites:** [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) Accepted; [`DESIGN_AUDIT_PROGRAM_001.md`](DESIGN_AUDIT_PROGRAM_001.md) Accepted.

**Feeds:** ✅ `DESIGN_IMPLEMENTATION_VALIDATION_001` → ✅ statistical protocol → combination matrix v2 → guardrails → design suitability.

**Next:** ✅ **`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001`**.

---

## DESIGN-LITERATURE-ALIGNMENT-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md)

**Status:** **`accepted_design_literature_alignment`**

**Verdict:** Aligns 31 inventory rows (DES-001–DES-031) to canonical experimental-design methodology (geo/matched-market, randomization, blocking, rerandomization, thinning, trim, supergeo, multi-cell, power/MDE). **14 open conceptual gaps (G-DES-001–014).** **0 validated designs.** Verdict: `design_literature_alignment_complete_with_open_conceptual_gaps`. **Documentation/governance only** — no code changes, no promotion.

**Prerequisites:** [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) Accepted; [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) Accepted.

**Feeds:** `DESIGN_IMPLEMENTATION_VALIDATION_001` → statistical protocol → combination matrix v2 → guardrails → design suitability.

**Next:** ✅ **`DESIGN_IMPLEMENTATION_VALIDATION_001`**.

---

## DESIGN-IMPLEMENTATION-VALIDATION-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md)

**Status:** **`accepted_design_implementation_validation`**

**Verdict:** Validates 31 inventory rows against literature-aligned families and contract. **0 contract-complete.** 4 `adapter_required`. 8 hard blocker classes. **Documentation/governance only** — no code fixes.

**Prerequisites:** [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) Accepted; [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) Accepted.

**Feeds:** `DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001` → combination matrix v2 → guardrails → design suitability.

**Next:** ✅ **`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001`**.

---

## DESIGN-STATISTICAL-VALIDATION-PROTOCOL-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md)

**Status:** **`accepted_design_statistical_validation_protocol`**

**Verdict:** Defines design-side simulation worlds, diagnostics, metrics, pass/warn/block rules, and future `D5-DES-STAT-*` harness requirements for all DES-001–DES-031 rows. Scoped to **observed** implementation behavior from [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md). **0 designs statistically validated.** Verdict: `design_statistical_validation_protocol_defined_not_executed`. **Documentation/governance only** — no harness execution.

**Prerequisites:** [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) Accepted; [`DESIGN_LITERATURE_ALIGNMENT_001.md`](DESIGN_LITERATURE_ALIGNMENT_001.md) Accepted; [`DESIGN_CODE_INVENTORY_001.md`](DESIGN_CODE_INVENTORY_001.md) Accepted.

**Feeds:** `DESIGN_COMBINATION_VALIDATION_MATRIX_001` → guardrails → design suitability.

**Next:** ✅ **`DESIGN_COMBINATION_VALIDATION_MATRIX_001`**.

---

## DESIGN-COMBINATION-VALIDATION-MATRIX-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md)

**Status:** **`accepted_design_combination_validation_matrix`**

**Verdict:** Defines design × geometry × estimator × inference × readout combination statuses and D-COMB-* reason codes for DES-001–DES-031. **0 combinations promoted.** Verdict: `design_combination_matrix_defined_no_combinations_promoted`. **Documentation/governance only**.

**Prerequisites:** [`DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md`](DESIGN_STATISTICAL_VALIDATION_PROTOCOL_001.md) Accepted; [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) Accepted.

**Feeds:** `DESIGN_GUARDRAILS_001` → design suitability.

**Next:** ✅ **`DESIGN_GUARDRAILS_001`**.

---

## DESIGN-GUARDRAILS-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md)

**Status:** **`accepted_design_guardrails`**

**Verdict:** Converts design audit ladder, contract blockers, implementation gaps, statistical protocol eligibility, and combination matrix statuses into PASS/WARN/BLOCK governance policy. **0 downstream PASS.** Verdict: `design_guardrails_defined_no_downstream_pass`. **Documentation/governance only** — no runtime enforcement.

**Prerequisites:** [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) Accepted; [`DESIGN_IMPLEMENTATION_VALIDATION_001.md`](DESIGN_IMPLEMENTATION_VALIDATION_001.md) Accepted.

**Feeds:** `DESIGN_SUITABILITY_FRAMEWORK_001` → experiment planning filters.

**Next:** ✅ **`DESIGN_SUITABILITY_FRAMEWORK_001`**.

---

## DESIGN-SUITABILITY-FRAMEWORK-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md)

**Status:** **`accepted_design_suitability_framework`**

**Verdict:** Classifies design methods and design × estimator × inference combinations for structural suitability after consuming contract, implementation, statistical protocol, combination matrix, and guardrails. **0 downstream suitable designs.** Verdict: `design_suitability_framework_defined_no_downstream_suitable_designs`. **Documentation/governance only** — distinct from [`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md).

**Prerequisites:** [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) Accepted; [`DESIGN_COMBINATION_VALIDATION_MATRIX_001.md`](DESIGN_COMBINATION_VALIDATION_MATRIX_001.md) Accepted.

**Feeds:** `DESIGN_CONTRACT_ENFORCEMENT_PLAN_001` → schema → emission → `D5-DES-STAT-*` → experiment planning.

**Next:** ✅ **`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001`**.

---

## DESIGN-CONTRACT-ENFORCEMENT-PLAN-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md)

**Status:** **`accepted_design_contract_enforcement_plan`**

**Verdict:** Defines phased plan for emitting, validating, and enforcing design output contract fields on `DesignEvidence`, `geo_runner`, and related paths. **Phase 0 only — not implemented.** Verdict: `design_contract_enforcement_plan_defined_not_implemented`. **Documentation/governance only.**

**Prerequisites:** [`DESIGN_SUITABILITY_FRAMEWORK_001.md`](DESIGN_SUITABILITY_FRAMEWORK_001.md) Accepted; [`DESIGN_GUARDRAILS_001.md`](DESIGN_GUARDRAILS_001.md) Accepted.

**Feeds:** `DESIGN_CONTRACT_SCHEMA_001` → tier-1 emission → `DESIGN_GUARDRAIL_ENFORCEMENT_001`.

**Next:** ✅ **`DESIGN_CONTRACT_SCHEMA_001`**.

---

## DESIGN-CONTRACT-SCHEMA-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md)

**Status:** **`accepted_design_contract_schema`**

**Verdict:** Machine-readable schema specification for `design_contract` nested block — field blocks, enums, conditional requirements, validation rules, illustrative examples. **Not implemented in code.** Verdict: `design_contract_schema_defined_not_implemented`. **Documentation/schema-spec only.**

**Prerequisites:** [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) Accepted; [`DESIGN_OUTPUT_CONTRACT_001.md`](DESIGN_OUTPUT_CONTRACT_001.md) Accepted.

**Feeds:** `DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001` → validator → runtime enforcement.

**Next:** ✅ **`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001`**.

---

## DESIGN-TIER1-CONTRACT-EMISSION-PLAN-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md)

**Status:** **`accepted_design_tier1_contract_emission_plan`**

**Verdict:** Phase 2 tier-1 geo-run emission plan for DES-001–004, DES-006, constrained DES-011. Maps schema fields to `geo_runner` / `DesignEvidence` producers. Verdict: `design_tier1_contract_emission_plan_defined_not_implemented`. **Documentation/planning only** — no code emission; no validator; no fixture regeneration; **0/31 contract-complete**; downstream **blocked**; no TrustReport/CalibrationSignal/MMM/LLM authorization.

**Prerequisites:** [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) Accepted; [`DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md`](DESIGN_CONTRACT_ENFORCEMENT_PLAN_001.md) Accepted.

**Feeds:** `DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001` → tier-1 code emission → `D5-DES-STAT-*` → experiment planning.

**Next:** ✅ **`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001`**.

---

## DESIGN-CONTRACT-VALIDATION-TEST-PLAN-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md)

**Status:** **`accepted_design_contract_validation_test_plan`**

**Verdict:** Phase 3 contract validation test plan — positive, negative, conditional, fixture, and CI gating before emission can be trusted. Verdict: `design_contract_validation_test_plan_defined_not_implemented`. **Documentation/test-plan only** — no tests implemented; no validator; no fixture regeneration; **0/31 contract-complete**; downstream **blocked**; no TrustReport/CalibrationSignal/MMM/LLM authorization.

**Prerequisites:** [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) Accepted; [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) Accepted.

**Feeds:** `DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001` → validator module → fixtures → pytest suite → tier-1 code emission.

**Next:** ✅ **`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001`**.

---

## DESIGN-CONTRACT-VALIDATOR-IMPLEMENTATION-PLAN-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md`](DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md)

**Status:** **`accepted_design_contract_validator_implementation_plan`**

**Verdict:** Validator architecture and implementation sequencing for `design_contract` blocks — module target, result object, reason codes, severity rules, tier-1 behavior, guardrail/suitability integration. Verdict: `design_contract_validator_implementation_plan_defined`. **Implementation complete** as DESIGN-CONTRACT-VALIDATOR-IMPLEMENTATION-001.

**Prerequisites:** [`DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md`](DESIGN_CONTRACT_VALIDATION_TEST_PLAN_001.md) Accepted; [`DESIGN_CONTRACT_SCHEMA_001.md`](DESIGN_CONTRACT_SCHEMA_001.md) Accepted.

**Feeds:** ✅ `DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001` → tier-1 emission wiring → pytest on emitted contracts.

**Next:** ✅ **`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001`**.

---

## DESIGN-CONTRACT-VALIDATOR-IMPLEMENTATION-001 (2026-06-10)

**Artifact:** [`panel_exp/validation/design_contract_validator_001.py`](../panel_exp/validation/design_contract_validator_001.py) · [`tests/validation/test_design_contract_validator_001.py`](../tests/validation/test_design_contract_validator_001.py)

**Status:** **`implemented_design_contract_validator`**

**Verdict:** First design-contract validator module — universal + conditional + no-overclaim checks per DESIGN-CONTRACT-SCHEMA-001. `validate_design_contract`, `validate_design_evidence_contract`, `compute_contract_status`; conservative `contract_complete_allowed=False`. **Validator-only scope** — no tier-1 emission wiring; no fixture regeneration; **0/31 contract-complete**; downstream **blocked**; no TrustReport/CalibrationSignal/MMM/LLM authorization.

**Prerequisites:** [`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md`](DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN_001.md) Accepted.

**Feeds:** tier-1 emission wiring → guardrail/suitability integration.

**Next:** ✅ **`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001`**.

---

## DESIGN-TIER1-CONTRACT-EMISSION-IMPLEMENTATION-PLAN-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md)

**Status:** **`accepted_design_tier1_contract_emission_implementation_plan`**

**Verdict:** Decomposes tier-1 `design_contract` emission into concrete wiring steps — builder module, `DesignEvidence` optional fields, `geo_runner` validator invocation, tier-1 tests, backward compatibility. Verdict: `design_tier1_contract_emission_implementation_plan_defined_not_implemented`. **Documentation/planning only** — no runtime emission; no fixture regeneration; **0/31 contract-complete**; downstream **blocked**; no TrustReport/CalibrationSignal/MMM/LLM authorization.

**Prerequisites:** [`DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_PLAN_001.md) Accepted; [`DESIGN_CONTRACT_VALIDATOR_IMPLEMENTATION_001`](../panel_exp/validation/design_contract_validator_001.py) Implemented.

**Feeds:** ✅ `DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001` → golden fixtures → guardrail integration.

**Next:** ✅ **`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001`**.

---

## DESIGN-TIER1-CONTRACT-EMISSION-IMPLEMENTATION-001 (2026-06-10)

**Artifact:** [`panel_exp/validation/design_contract_builder_001.py`](../panel_exp/validation/design_contract_builder_001.py) · [`panel_exp/design/geo_runner.py`](../panel_exp/design/geo_runner.py) · [`tests/validation/test_design_tier1_contract_emission_001.py`](../tests/validation/test_design_tier1_contract_emission_001.py)

**Status:** **`implemented_design_tier1_contract_emission`**

**Verdict:** First tier-1 runtime `design_contract` emission — builder + validator invocation in `geo_runner`; optional `DesignEvidence.design_contract` / `contract_validation`; conservative governance defaults. Verdict: `design_tier1_contract_emission_implemented_conservative`. **0/31 contract-complete**; downstream **blocked**; no TrustReport/CalibrationSignal/MMM/LLM authorization; no `design_evidence_v1.json` overwrite.

**Prerequisites:** [`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md`](DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_PLAN_001.md) Accepted; validator implemented.

**Feeds:** golden fixtures → guardrail runtime → D5-DES-STAT.

**Next:** ✅ **`DESIGN_CONTRACT_GOLDEN_FIXTURES_001`**.

---

## DESIGN-CONTRACT-GOLDEN-FIXTURES-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_CONTRACT_GOLDEN_FIXTURES_001.md`](DESIGN_CONTRACT_GOLDEN_FIXTURES_001.md) · [`tests/fixtures/artifact_schemas/design_contract_golden_001/`](../tests/fixtures/artifact_schemas/design_contract_golden_001/) · [`tests/validation/test_design_contract_golden_fixtures_001.py`](../tests/validation/test_design_contract_golden_fixtures_001.py)

**Status:** **`accepted_design_contract_golden_fixtures`**

**Verdict:** Golden fixtures stabilize tier-1 `design_contract` emitted shape — 9 JSON fixtures, 39 regression tests. Verdict: `design_contract_golden_fixtures_defined_and_tested_no_promotion`. **0/31 contract-complete**; downstream **blocked**; `design_evidence_v1.json` unchanged.

**Prerequisites:** [`DESIGN_TIER1_CONTRACT_EMISSION_IMPLEMENTATION_001`](../panel_exp/validation/design_contract_builder_001.py) Implemented.

**Feeds:** ✅ guardrail runtime integration → suitability reassessment → D5-DES-STAT.

**Next:** ✅ **`DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001`**.

---

## DESIGN-GUARDRAIL-RUNTIME-INTEGRATION-001 (2026-06-10)

**Artifact:** [`docs/DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001.md`](DESIGN_GUARDRAIL_RUNTIME_INTEGRATION_001.md) · [`panel_exp/validation/design_guardrail_runtime_001.py`](../panel_exp/validation/design_guardrail_runtime_001.py) · [`tests/validation/test_design_guardrail_runtime_integration_001.py`](../tests/validation/test_design_guardrail_runtime_integration_001.py)

**Status:** **`design_guardrail_runtime_integration_defined_and_tested_no_promotion`**

**Verdict:** Runtime guardrail evaluator consumes emitted `design_contract` + `contract_validation` metadata — 24 integration tests over golden fixtures. Maps validator state to PASS/WARN/BLOCK; enforces no-overclaim policy. **0/31 contract-complete**; downstream **blocked**; `downstream_may_proceed=False` always; not wired to producers.

**Prerequisites:** [`DESIGN_CONTRACT_GOLDEN_FIXTURES_001`](DESIGN_CONTRACT_GOLDEN_FIXTURES_001.md) Accepted; tier-1 emission implemented.

**Feeds:** suitability reassessment → D5-DES-STAT.

**Next:** **`DESIGN_SUITABILITY_REASSESSMENT_001`** (design-side).

---

## METHOD-CODE-INVENTORY-001 (2026-06-04)

**Artifact:** [`docs/METHOD_CODE_INVENTORY_001.md`](METHOD_CODE_INVENTORY_001.md) · [`docs/track_d/archives/METHOD_CODE_INVENTORY_001.json`](track_d/archives/METHOD_CODE_INVENTORY_001.json)

**Verdict:** Layer 1 **complete** — 44 code-derived items (designs, estimators, inference, orchestration). Generator: `python -m panel_exp.validation.method_code_inventory_001`.

**Next:** ✅ **`METHOD_LITERATURE_ALIGNMENT_001`**.

---

## METHOD-LITERATURE-ALIGNMENT-001 (2026-06-04)

**Artifact:** [`docs/METHOD_LITERATURE_ALIGNMENT_001.md`](METHOD_LITERATURE_ALIGNMENT_001.md) · [`docs/track_d/archives/METHOD_LITERATURE_ALIGNMENT_001.json`](track_d/archives/METHOD_LITERATURE_ALIGNMENT_001.json)

**Verdict:** Layer 2 **complete** — 24 literature families (design, estimator, inference) mapped to code inventory; canonical references and Layer 3/4 question lists; no trust roles.

**Generator:** `python -m panel_exp.validation.method_literature_alignment_001`

**Next:** ✅ **`METHOD_IMPLEMENTATION_VALIDATION_001`**.

---

## METHOD-IMPLEMENTATION-VALIDATION-001 (2026-06-04)

**Artifact:** [`docs/METHOD_IMPLEMENTATION_VALIDATION_001.md`](METHOD_IMPLEMENTATION_VALIDATION_001.md) · [`docs/track_d/archives/METHOD_IMPLEMENTATION_VALIDATION_001.json`](track_d/archives/METHOD_IMPLEMENTATION_VALIDATION_001.json)

**Verdict:** Layer 3 **complete** — 29 rows; identity/estimand/geometry/inference/orchestration fidelity; prior audit reconciliation (D1, G1–G8, F-GEO, F-INF, COMBO); `promotion_allowed` false on all rows.

**Generator:** `python -m panel_exp.validation.method_implementation_validation_001`

**Next:** ✅ **`METHOD_STATISTICAL_VALIDATION_PROTOCOL_001`**.

---

## METHOD-STATISTICAL-VALIDATION-PROTOCOL-001 (2026-06-04)

**Artifact:** [`docs/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md`](METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md) · [`docs/track_d/archives/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json`](track_d/archives/METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.json)

**Verdict:** Layer 4 **complete** — 51 protocol rows; DGP world catalog; metric catalog; acceptance taxonomy; battery A–E; combination cards; blocked-before-OC register; `promotion_allowed` / `trust_role_allowed` / `calibration_signal_allowed` / `mmm_allowed` false on all rows.

**Generator:** `python -m panel_exp.validation.method_statistical_validation_protocol_001`

**Next:** ✅ **`METHOD_COMBINATION_VALIDATION_MATRIX_001`**.

---

## METHOD-COMBINATION-VALIDATION-MATRIX-001 (2026-06-04)

**Artifact:** [`docs/METHOD_COMBINATION_VALIDATION_MATRIX_001.md`](METHOD_COMBINATION_VALIDATION_MATRIX_001.md) · [`docs/track_d/archives/METHOD_COMBINATION_VALIDATION_MATRIX_001.json`](track_d/archives/METHOD_COMBINATION_VALIDATION_MATRIX_001.json)

**Verdict:** Layer 5 **complete** — 30 combination rows; ready-for-OC / blocked / bridge-required / research-only status; D5-STAT execution and blocked queues; forbidden flags false on all rows.

**Generator:** `python -m panel_exp.validation.method_combination_validation_matrix_001`

**Next:** ✅ **`DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001`**.

---

## DESIGN-ESTIMATOR-INFERENCE-SUITABILITY-FRAMEWORK-001 (2026-06-04)

**Artifact:** [`docs/DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md`](DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md) · [`docs/track_d/archives/DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.json`](track_d/archives/DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.json)

**Verdict:** Post-foundation suitability framework **complete** — 30 rows mapped from Layer 5 matrix; non-promotional `suitability_class` only; OC-ready ≠ suitable; `promotion_allowed` / `trust_role_allowed` / `calibration_signal_allowed` / `mmm_allowed` / `llm_recommendation_allowed` false on all rows.

**Generator:** `python -m panel_exp.validation.design_estimator_inference_suitability_framework_001`

**Next:** ✅ **`D5-STAT-SMOKE-CALLABLE-001`** (see below).

---

## D5-STAT-SMOKE-CALLABLE-001 (2026-06-04)

**Artifact:** [`docs/track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md`](track_d/D5_STAT_SMOKE_CALLABLE_001_REPORT.md) · [`docs/track_d/archives/D5_STAT_SMOKE_CALLABLE_001_results.json`](track_d/archives/D5_STAT_SMOKE_CALLABLE_001_results.json)

**Verdict:** First evidence-execution smoke battery **complete** — `smoke_pass_with_caveats`; 11 callable passes; 16 expected blocks; 3 skipped optional TBRRidge mappings; no promotion/trust/CS/MMM/LLM claims.

**Generator:** `python -m panel_exp.validation.track_d_d5_stat_smoke_callable_001`

**Next:** ✅ **`D5-STAT-SCM-JK-001`** (see below).

---

## D5-STAT-SCM-JK-001 (2026-06-04)

**Artifact:** [`docs/track_d/D5_STAT_SCM_JK_001_REPORT.md`](track_d/D5_STAT_SCM_JK_001_REPORT.md) · [`docs/track_d/archives/D5_STAT_SCM_JK_001_results.json`](track_d/archives/D5_STAT_SCM_JK_001_results.json)

**Verdict:** Level B characterization **complete** — `characterization_mixed_requires_followup`; 7 worlds × 15 replicates; interval orientation/half-width checks pass on feasible runs; no promotion/trust/CS/MMM/suitability claims.

**Generator:** `python -m panel_exp.validation.track_d_d5_stat_scm_jk_001`

**Next:** ✅ **`D5-STAT-AUGSYNTH-POINT-001`** (see below).

---

## D5-STAT-AUGSYNTH-POINT-001 (2026-06-04)

**Artifact:** [`docs/track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md`](track_d/D5_STAT_AUGSYNTH_POINT_001_REPORT.md) · [`docs/track_d/archives/D5_STAT_AUGSYNTH_POINT_001_results.json`](track_d/archives/D5_STAT_AUGSYNTH_POINT_001_results.json)

**Verdict:** Level B AugSynthCVXPY **point** characterization **complete** — `characterization_mixed_requires_followup`; injected-truth comparison (not SCM); no interval/inference validation; forbidden flags false.

**Generator:** `python -m panel_exp.validation.track_d_d5_stat_augsynth_point_001`

**Next:** **`D5-STAT-TBRRIDGE-INF-001`**.

---

## METHOD-FOUNDATION-SYNTHESIS-001 (2026-06-03)

**Artifact:** [`docs/METHOD_FOUNDATION_SYNTHESIS_001.md`](METHOD_FOUNDATION_SYNTHESIS_001.md)

**Status:** **complete** · **`superseded_for_sequencing`** (2026-06-04)

**Verdict:** Evidence-input combination map and stable conclusions — **not** sequencing authority. Superseded by **METHOD-VALIDATION-PROGRAM-001**.

**Prerequisites:** DL-1 P1–P6 · lane closeout · design-readout P6.

**Next:** N/A for sequencing — use validation program.

---

## METHOD-SOUNDNESS-ROADMAP-REVIEW-001 (2026-06-03)

**Artifact:** [`docs/METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md`](METHOD_SOUNDNESS_ROADMAP_REVIEW_001.md)

**Verdict:** Confirms AugSynth/ASCM as immediate active lane vs design-readout/inference alternatives; orders next 5 artifacts; first **code** PR = D5-DIAG-SCM-AUGSYNTH-001.

**Prerequisites:** METHOD-SOUNDNESS-AND-GAP-ROADMAP-001 · threshold audit · ASCM-002 · ADR-001.

**Next:** ✅ D5-DIAG **complete** → ✅ fidelity audit **complete** → **D5-INST-AUGSYNTH-ASCM-003**.

---

## AUGSYNTH-ASCM-LANE-CLOSEOUT-001 (2026-06-03)

**Artifact:** [`docs/AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md)

**Verdict:** DL-1 P1–P6 **lane closed**. AugSynth point = promising **diagnostic comparator**; not promoted. JK = diagnostic-only (`jk_unsafe_under_diagnostics`); Conformal = **blocked** (`conformal_blocked_pending_new_design`); design compat = per-cell only + bridges required. Ordered next at closeout: **`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001`** (now ✅) — not `D5-INST-AUGSYNTH-MULTICELL-001` before pooling ADR.

**Prerequisites:** P1–P6 complete · [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md).

**Next ordered (historical):** superseded by **METHOD-VALIDATION-PROGRAM-001** Layer 1–5 sequence.
**Next ordered (post-closeout):** (1) ✅ pooling ADR · (2) **`D5-INST-AUGSYNTH-MULTICELL-001`** · (3) estimand bridge ADR · (4) design-compat OC · (5) diagnostic-only vs repair-lane decision.

---

## MULTICELL-AUGSYNTH-POOLING-RULE-ADR-001 (2026-06-03)

**Artifact:** [`docs/MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md`](MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md)

**Verdict:** **Accepted** — multi-cell AugSynth per-cell diagnostic default (S0); no pooled causal lift; optional descriptive equal-cell mean under `pooling_rule_id=MULTICELL_AUGSYNTH_DESCRIPTIVE_V0` only if all per-cell gates pass; **no pooled uncertainty**. Satisfies P6 / E-DES-MCELL-011 AugSynth specialization.

**Prerequisites:** P6 [`DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md) · lane closeout · D5-MCELL-001 · F-P0-006.

**Next:** **`D5-INST-AUGSYNTH-MULTICELL-001`** (OC — not before this ADR).

---

## DESIGN-READOUT-AUGSYNTH-COMPATIBILITY-001 (2026-06-03)

**Artifact:** [`docs/DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md`](DESIGN_READOUT_AUGSYNTH_COMPATIBILITY_001.md)

**Verdict:** `compatible_per_cell_only_pooling_blocked`; co-verdict `bridge_required_before_broader_use`. Tier-1 geo single-cell unit-panel compatible for AugSynth **point diagnostics** (greedy OC-validated); multi-cell **per-cell only**; JK diagnostic-only (P4); Conformal blocked (P5); supergeo/trim/aggregate require bridges. **No promotion.**

**Prerequisites:** P3 ASCM-003 · P4 JK calibration · P5 Conformal failure · DESIGN-INVENTORY-001.

**Next:** **`METHOD_VALIDATION_PROGRAM_001`** → **`METHOD_CODE_INVENTORY_001`** (pooling ADR = semantic guardrail if merged; MCELL OC paused as default).

---

## AUGSYNTH-ASCM-DEVELOPMENT-ROADMAP-001 (2026-06-03)

**Artifact:** [`docs/AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md`](AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001.md)

**Verdict:** Active DL-1 **execution** plan — P1–P6 ✅; lane **closed** per closeout. **No promotion.**

**Status:** **complete** — execution landed; closeout [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md).

**Prerequisites:** METHOD-SOUNDNESS-ROADMAP-REVIEW-001 · ASCM-002 · threshold audit · ADR-001.

**Next:** **`METHOD_VALIDATION_PROGRAM_001`** — AugSynth lane **paused** for new execution; evidence retained.
**Next:** **`D5-INST-AUGSYNTH-MULTICELL-001`** after ✅ [`MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md`](MULTICELL_AUGSYNTH_POOLING_RULE_ADR_001.md) and [`AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md`](AUGSYNTH_ASCM_LANE_CLOSEOUT_001.md).

---

## TRACK-F-IMPLEMENTATION-CHECKPOINT-001 (2026-06-03)

**Artifact:** [`docs/TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md`](TRACK_F_IMPLEMENTATION_CHECKPOINT_001.md)

**Verdict:** Contract stack + P3+ fixes/OC **complete**; **pause** default implementation; optional **F-INF-004** (A09) on product pull only; promotion/MMM/CS **blocked**; governed uncertainty **empty**.

**Commits (P3+ spine):** `cf128a2` F-INF-003 · `d9afc2a` POSTFIX · `3993ba7` F-INF-002 · `9f1dba0` TBRRIDGE-003.

---

## D5-INST-TBRRIDGE-003 checkpoint (2026-06-03)

**Artifact:** [`docs/track_d/D5_INST_TBRRIDGE_003_REPORT.md`](track_d/D5_INST_TBRRIDGE_003_REPORT.md) · [`D5_INST_TBRRIDGE_003_results.json`](track_d/archives/D5_INST_TBRRIDGE_003_results.json)  
**Harness:** [`panel_exp/validation/track_d_d5_inst_tbrridge_003.py`](../panel_exp/validation/track_d_d5_inst_tbrridge_003.py)

**Verdict:** A16/A21 `callable_unverified_interval_semantics`; **A18** `characterized_restricted`; not governed; promotion blocked.

**Prerequisite:** F-INF-002 (`3993ba7`).

---

## F-INF-002 checkpoint (2026-06-03)

**Artifact:** [`docs/F_INF_002_TBRRIDGE_INTERFACE_FIX.md`](F_INF_002_TBRRIDGE_INTERFACE_FIX.md)  
**Code:** [`panel_exp/inference/_impact_common.py`](../panel_exp/inference/_impact_common.py) · [`panel_exp/inference/modes/impl.py`](../panel_exp/inference/modes/impl.py) · [`panel_exp/inference/unit_jackknife.py`](../panel_exp/inference/unit_jackknife.py) · [`tests/governance/test_f_inf_002_tbrridge_interface.py`](../tests/governance/test_f_inf_002_tbrridge_interface.py)

**Verdict:** A16/A18/A21 no longer `blocked_interface` — pooled-CF multi-treated readout; structurally valid on 001e fixture; **`callable_unverified_interval_semantics`** until TBRRIDGE-003 OC; not governed.

**Next:** ~~**D5-INST-TBRRIDGE-003**~~ ✅.

---

## F-INF-001 checkpoint (2026-06-03)

**Artifact:** [`docs/F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md`](F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md)  
**Code:** [`panel_exp/governance/interval_semantics_contract.py`](../panel_exp/governance/interval_semantics_contract.py) · [`tests/governance/test_f_inf_001_interval_semantics.py`](../tests/governance/test_f_inf_001_interval_semantics.py)

**Verdict:** **Contract complete** — callable invalid intervals classified safely; `GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST` empty; no silent bound fixes.

**Next:** ~~**F-CAT-001**~~ ✅ registry/catalog cleanup.

---

## F-GEO-001 checkpoint (2026-06-03)

**Artifact:** [`docs/F_GEO_001_GEOMETRY_ADAPTER_CONTRACT.md`](F_GEO_001_GEOMETRY_ADAPTER_CONTRACT.md)  
**Code:** [`panel_exp/governance/geometry_adapter_contract.py`](../panel_exp/governance/geometry_adapter_contract.py) · [`tests/governance/test_f_geo_001_geometry_adapter_contract.py`](../tests/governance/test_f_geo_001_geometry_adapter_contract.py)  
**Depends on:** F-INF-001 — geometry blocks before interval semantics; valid intervals do not rescue wrong geometry.

**Verdict:** **Contract complete** — geometry support rules tested; no MMM/promotion.

**Next:** ~~**F-CAT-001**~~ ✅.

---

## F-CAT-001 checkpoint (2026-06-03)

**Artifact:** [`docs/F_CAT_001_REGISTRY_CATALOG_CLEANUP.md`](F_CAT_001_REGISTRY_CATALOG_CLEANUP.md)  
**Code:** [`panel_exp/governance/catalog_contract.py`](../panel_exp/governance/catalog_contract.py) · [`tests/governance/test_f_cat_001_catalog_contract.py`](../tests/governance/test_f_cat_001_catalog_contract.py)  
**Depends on:** F-INF-001 + F-GEO-001 — catalog cannot over-claim geometry, interval semantics, CalibrationSignal, or MMM readiness.

**Verdict:** **Catalog cleanup complete** — taxonomy notes in `method_metadata`; canonical combo records + audits; no method behavior changes.

**Next:** ~~**D5-INF-POSTFIX-001**~~ ✅ → **F-INF-002**.

---

## D5-INF-POSTFIX-001 checkpoint (2026-06-03)

**Artifact:** [`docs/track_d/D5_INF_POSTFIX_001_REPORT.md`](track_d/D5_INF_POSTFIX_001_REPORT.md) · [`D5_INF_POSTFIX_001_results.json`](track_d/archives/D5_INF_POSTFIX_001_results.json)

**Verdict:** A05/A19 structurally valid post F-INF-003; null FPR 0 on 001e battery; **`diagnostic_interval_only`** — not governed; promotion blocked.

**Next:** ~~**F-INF-002**~~ ✅.

---

## F-INF-003 checkpoint (2026-06-03)

**Artifact:** [`docs/F_INF_003_INTERVAL_ORIENTATION_FIX.md`](F_INF_003_INTERVAL_ORIENTATION_FIX.md)  
**Code:** [`panel_exp/inference/modes/impl.py`](../panel_exp/inference/modes/impl.py) · [`panel_exp/inference/_impact_common.py`](../panel_exp/inference/_impact_common.py) · [`tests/governance/test_f_inf_003_interval_orientation.py`](../tests/governance/test_f_inf_003_interval_orientation.py)

**Verdict:** **Orientation fix complete** — Conformal/TimeSeriesKfold map effect bounds via `y_hat + effect`; F-INF-001 unchanged. A05/A19 **structurally_valid_interval_ready_for_OC** — not governed uncertainty.

**Next:** **D5-INF-POSTFIX-001** OC rerun.

---

## F-BACKLOG-001 checkpoint (2026-06-03)

**Artifact:** [`docs/F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md`](F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md)

**Verdict:** **Implementation backlog locked** — contract stack complete; classified queue across F-INF / F-GEO / F-CAT / F-MCELL / R&D / promotion prerequisites.

**Next authorized implementation:** **F-INF-003** (Conformal + TimeSeriesKfold band sign / orientation). OC rerun only after fix per backlog §7.

---

## D5-INST-AUGSYNTH-KFOLD-001 checkpoint (2026-06-02)

**Artifact:** [`docs/track_d/archives/D5_INST_AUGSYNTH_KFOLD_001_results.json`](track_d/archives/D5_INST_AUGSYNTH_KFOLD_001_results.json)  
**Report:** [`docs/track_d/D5_INST_AUGSYNTH_KFOLD_001_REPORT.md`](track_d/D5_INST_AUGSYNTH_KFOLD_001_REPORT.md)

**Verdict:** **`remain_restricted_diagnostic_comparator`** — AugSynthCVXPY+Kfold feasible single-cell + k=2 per-cell; null FPR 0 on battery; **not** CalibrationSignal; COMBO `valid_candidate` → characterized restricted.

---

## TRACK-D-CONCEPTUAL-VALIDITY-AUDIT-001 checkpoint (2026-06-02)

**Artifact:** [`docs/TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md) · [`docs/track_d/archives/TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001_results.json`](track_d/archives/TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001_results.json)

**Verdict:** **`continue_with_restricted_diagnostics_only`** — method-by-method literature fidelity; **0** production-ready paths; synthetic OC ≠ conceptual validity. **AUDIT-010 prerequisite** (with D5-INST-TBR-001). Blockers: `full_model` SCM, registry Bayesian≠MCMC, TBR/TBRRidge conflation, DID relative CI. **Implementation plan:** [`TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md`](TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md).

---

## TRACK-F-ESTIMATOR-INFERENCE-COMPLETION-PLAN-001 (2026-06-02)

**Artifact:** [`docs/TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md`](TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001.md)

**Verdict:** **plan v1** — 30 COMBO tuples dispositioned (FIX/BLOCK/HOLD/R&D); P0 hygiene → TBR-001 → AUDIT-010 → P2 OC. **Planning only** — no code changes in package.

---

## D5-INST-COMBO-AUDIT-001 checkpoint (2026-06-02)

**Artifact:** [`docs/track_d/archives/D5_INST_COMBO_AUDIT_001_results.json`](track_d/archives/D5_INST_COMBO_AUDIT_001_results.json)  
**Report:** [`docs/track_d/D5_INST_COMBO_AUDIT_001_REPORT.md`](track_d/D5_INST_COMBO_AUDIT_001_REPORT.md)

**Verdict:** **30 curated combos** — 9 already_characterized, 6 valid_candidate, 8 invalid/blocked/research_only. No blind Cartesian OC. TBR aggregate-only; AugSynthCVXPY+Kfold candidate; TBRRidge Kfold/BRB characterized.

---

## D5-INST-AUGSYNTH-001 checkpoint (2026-06-02)

**Artifact:** [`docs/track_d/archives/D5_INST_AUGSYNTH_001_results.json`](track_d/archives/D5_INST_AUGSYNTH_001_results.json)  
**Report:** [`docs/track_d/D5_INST_AUGSYNTH_001_REPORT.md`](track_d/D5_INST_AUGSYNTH_001_REPORT.md)

**Verdict:** **`remain_diagnostic_only_no_calibration_signal`** — AugSynthCVXPY 100% feasible single-cell; JK null FPR 0; characterized comparator not CalibrationSignal. INST-004 JK → diagnostic_only. Prerequisite for AUDIT-010 (with TBR-001).

---

## D5-INST-AUDIT-001 checkpoint (2026-06-02)

**Artifact:** [`docs/track_d/archives/D5_INST_AUDIT_001_results.json`](track_d/archives/D5_INST_AUDIT_001_results.json)  
**Report:** [`docs/track_d/D5_INST_AUDIT_001_REPORT.md`](track_d/D5_INST_AUDIT_001_REPORT.md)

**Verdict:** **`inventory_complete_augsynth_tbr_then_mmm_readiness_audit_010`** — 13 estimators × 9 inference modes × 8 geometries (192 matrix rows). **AUDIT-010** = MMM readiness/gap gate **after** AUGSYNTH-001 + TBR-001 (not promotion). TBR aggregate-only; registry Bayesian ≠ BayesianTBR MCMC; DID native bootstrap.

---

## D5-INST-PLACEBO-001 checkpoint (2026-06-02)

**Artifact:** [`docs/track_d/archives/D5_INST_PLACEBO_001_results.json`](track_d/archives/D5_INST_PLACEBO_001_results.json)  
**Report:** [`docs/track_d/D5_INST_PLACEBO_001_REPORT.md`](track_d/D5_INST_PLACEBO_001_REPORT.md)

**Verdict:** **`remain_diagnostic_only_no_promotion`** — single-treated feasible (`placebo_band`); multi-treated natural assignment **100% blocked**; multi-cell k=2 per-cell single-treated only; no CalibrationSignal.

---

## D5-INST-TBRRIDGE-001 checkpoint (2026-06-02)

**Artifact:** [`docs/track_d/archives/D5_INST_TBRRIDGE_001_results.json`](track_d/archives/D5_INST_TBRRIDGE_001_results.json)  
**Report:** [`docs/track_d/D5_INST_TBRRIDGE_001_REPORT.md`](track_d/D5_INST_TBRRIDGE_001_REPORT.md)

**Verdict:** **`remain_restricted_no_promotion`** — TBRRidge Kfold/BRB stay restricted; unit point scale ≠ SCM+JK.

---

## D5-POW-001e checkpoint (2026-06-01)

**Artifact:** [`docs/track_d/archives/D5_POW_001e_results.json`](track_d/archives/D5_POW_001e_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_pow_001e.py`

**Verdict:** **`acceptable_with_caveats`** — fixed-window unit SCM+JK null-monitor reference across six confirmed design methods. **Single_cell:** all methods **acceptable** (mean per-cell null interval-exclusion FPR ≈ 0 on `scm_low_signal`, n=28). **Multi_cell** (`n_test_grps=2`): all **acceptable**; per-cell metrics only (control-only donors); `thinningdesign` test_1 mean null FPR ≈ 3.6%. **Greedy vs `Rerandomization(greedy)`:** identical on this battery. **Track E:** E-DES-MCELL-* + E-SCM-DONOR / E-DES-WIN follow-ons. **Excluded:** supergeos, trimmedmatch, quickblock, matchedpair. Not platform power / MDE / lift promotion.

---

## DESIGN-INVENTORY-001 checkpoint (2026-06-01)

**Artifact:** [`docs/track_d/archives/DESIGN_INVENTORY_001_results.json`](track_d/archives/DESIGN_INVENTORY_001_results.json)  
**Doc:** [`TRACK_D_DESIGN_METHOD_INVENTORY_001.md`](TRACK_D_DESIGN_METHOD_INVENTORY_001.md)

**Confirmed for D5-POW-001e (6):** `greedy_match_markets`, `rerandomization_wrapper`, `completerandomization`, `balancedrandomization`, `stratifiedrandomization`, `thinningdesign`. **Commit:** `e3e6aeb`. **001e:** ✅ complete. No `multi_cell_multi_treated` class — multi-cell = `n_test_grps>1`. **Separate follow-ups:** `supergeos`, `trimmedmatch`. **tier_3:** `quickblock`, `matchedpair`.

---

## D5-POW-001d checkpoint (2026-06-01)

**Artifact:** [`docs/track_d/archives/D5_POW_001d_results.json`](track_d/archives/D5_POW_001d_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_pow_001d.py`

**Verdict:** **`fixed_window_preferred`** — unit SCM+JK readout OC relatively stable across pre/post grid; greedy assignment overlap with baseline (pre28/post8) high when post length varies at fixed pre=28. Prefer **fixed experiment windows** for governed readout; PowerAnalysis **circular sliding** is not SCM+JK readout. Track E diagnostics **E-POW-WIN-001–007** registered in artifact.

---

## D5-POW-001c checkpoint (2026-06-01)

**Artifact:** [`docs/track_d/archives/D5_POW_001c_results.json`](track_d/archives/D5_POW_001c_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_pow_001c.py`

**Verdict:** **`narrow_diagnostics_only`** — greedy pre-period assignment held fixed; unit SCM+JK vs 2-row sum+TBRRidge+Kfold. Injection-grid point correlation ≈1 but effect magnitudes differ ~12× (sum aggregation). SCM+JK **infeasible** on 2-row panel (one control row). 2-row path is **not** an acceptable proxy for governed unit readout; geo power remains diagnostic-only.

**Design-aware:** `design_context_reference` + `design_methods_for_001e` tier table in artifact.

---

## D5-POW-001b checkpoint (2026-06-01)

**Artifact:** [`docs/track_d/archives/D5_POW_001b_results.json`](track_d/archives/D5_POW_001b_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_pow_001b.py`

**Verdict:** **`null_monitor_only`** — D5-POW-001a pooled detection degeneracy is explained by **swapped interval endpoints** in the research harness (`mean(y-y_lower)` vs correct `mean(y-y_upper)` for effect-lo). Under correct PowerAnalysis semantics, null interval-exclusion FPR ≈ **3%** (not 100%); wrong 001a-style FPR = **100%**. SCM+JK does **not** support power/MDE via interval-excludes-zero; use null-monitor cell coverage only.

---

## D5-POW-001a checkpoint (2026-06-01)

**Artifact:** [`docs/track_d/archives/D5_POW_001a_results.json`](track_d/archives/D5_POW_001a_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_pow_001a.py`

**Verdict:** **`optimistic_proxy`** — geo `PowerAnalysis` `mde_percent` (~1.5% mean) is materially lower than pooled SCM+JK interval-detection MDE (~4%) on the same greedy assignment battery (n=24). Pooled interval-detection curves are degenerate (100% exclude zero at all grid points). **Do not** use geo MDE for SCM JK feasibility or MMM planning.

**Governance:** No production, TrustReport, Track B, or eligibility changes.

---

## INV-D3-001 checkpoint (2026-06-01)

**Fix:** `unit_jk` LOO anchor → `y_hat` (shared primitive).  
**Validation:** [D5_INF_002b_results.json](track_d/archives/D5_INF_002b_results.json) — `accepted_deviation`, prod/ref ratio **1.0**, treated post noise Δ **0**.  
**Governance:** `SCM_UnitJackKnife` remains **null_monitor_only**; eligibility unchanged.  
**Track E:** [TRACK_E_METHOD_SUITABILITY_AND_TRIANGULATION_001.md](TRACK_E_METHOD_SUITABILITY_AND_TRIANGULATION_001.md) E0 planning doc added.

---

## How to add an audit

1. Copy [`MIP_PERIODIC_ARCHITECTURE_AND_ROBUSTNESS_AUDIT_TEMPLATE.md`](MIP_PERIODIC_ARCHITECTURE_AND_ROBUSTNESS_AUDIT_TEMPLATE.md).  
2. Fill all sections; do not skip §9 gap discovery.  
3. Add a row to the index table above.  
4. Set status `closed` when follow-ups are ticketed or merged into roadmap.

---

*Registry MIP-AUDIT-REGISTRY v1.0.0*
