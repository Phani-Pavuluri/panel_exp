# MIP audit registry

**Program ID:** MIP-PERIODIC-AUDIT  
**Status:** active  
**Last updated:** 2026-06-01 (Track D D4 package)  

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
| **AUDIT-009** | — | Before MMM intake promotion | TBD | — | — | — | planned |
| **AUDIT-010** | — | Before planning / optimizer | TBD | — | — | — | planned |
| **AUDIT-011** | — | Before LLM interface | TBD | — | — | — | planned |

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

**Next:** Track E E5/E6.

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

**Next:** Track E E5/E6; not MMM integration.

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

**Verdict:** Triangulation schema defines multi-instrument `TriangulationProfile` + agreement states; E4 golden fixtures specify TrustReport dispositions and forbidden actions (no averaging, no pooled multi-cell, no MMM outside CalibrationSignal). **Next:** E5 CalibrationSignal policy, E6 composer tests.

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
