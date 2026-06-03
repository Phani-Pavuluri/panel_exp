# D5-INST-TBRRIDGE-002 — TBRRidge remaining inference characterization

**Artifact:** [`archives/D5_INST_TBRRIDGE_002_results.json`](archives/D5_INST_TBRRIDGE_002_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_tbrridge_002.py`  
**Lane:** Research — no promotion, no CalibrationSignal ingress

**Prior:** [`D5_INST_TBRRIDGE_001_REPORT.md`](D5_INST_TBRRIDGE_001_REPORT.md) · [`AUDIT-010_mmm_readiness_gap.md`](../audits/AUDIT-010_mmm_readiness_gap.md) · Track F P0 ✅

---

## Summary

After **AUDIT-010** (`not_ready_continue_track_f`) and **Track F P0** hygiene, this battery characterizes **remaining TBRRidge inference wrappers** on **001e unit panels** (train=28, test=8, `scm_low_signal`). **TBRRidge+Kfold/BRB** are **context only** (001). **Class TBR** is out of scope.

**Overall verdict:** `remain_restricted_no_promotion`

| Governance | Value |
|------------|-------|
| TBRRidge ≠ class TBR | ✅ P0 recovery_runner label audit passes |
| CalibrationSignal | **No** |
| MMM ingress | **No** |
| Track B alias expansion | **No** |

---

## P2 target dispositions

| Inference | Disposition | Feasibility @ null (001e) | Notes |
|-------------|-------------|--------------------------:|-------|
| **UnitJackKnife** | **blocked_interface** | 0% | Broadcast shape error on multi-treated TBRRidge path |
| **JKP** | **blocked_interface** | 0% | Same interface failure as COMBO probe |
| **Conformal** | **blocked_interface** | 0% | Same interface failure |
| **TimeSeriesKfold** | **callable_unverified_interval_semantics** | 100% | Runs; **100% negative half-width** @ null; **100% null interval-exclusion FPR** — not governed |
| **Bayesian (registry)** | **blocked_production_policy** | 0% | **INV-015** — not BayesianTBR MCMC; blocked before run |
| **Kfold** (context) | **already_characterized_restricted** | 100% | TBRRIDGE-001 — null FPR 0 |
| **BRB** (context) | **already_characterized_restricted** | 100% | TBRRIDGE-001 |

---

## Key metrics (n_mc=14, null)

| Path | Null FPR | Mean point @ null | Mean half-width |
|------|---------:|------------------:|----------------:|
| SCM+JK (reference) | 0.0 | ~0.07 | ~3.0 |
| TBRRidge+Kfold | 0.0 | ~-401 | ~15.9 |
| TBRRidge+BRB | 0.0 | ~0.57 | ~6.2 |
| TBRRidge+TimeSeriesKfold | **1.0** | ~-401 | **~-21.6** (invalid band sign) |

**TimeSeriesKfold vs Kfold:** Both feasible on 001e panel; point means align (~0.03 delta) but **fold geometry differs** (horizon-blocked vs panel K-fold). **Not interchangeable.** TSKF intervals are **not** governed uncertainty on this battery.

**Combo-scale probes** (train=20, test=6, COMBO panel): JK/JKP/Conformal/Bayesian **probe_failed**; TimeSeriesKfold/Kfold/BRB **probe_success** — consistent with COMBO-AUDIT-001.

---

## Blocked / deferred (explicit)

| Combo | Block reason |
|-------|----------------|
| TBRRidge + UnitJackKnife + unit | Interface — treated path 2D vs 1D broadcast |
| TBRRidge + JKP + unit | Interface |
| TBRRidge + Conformal + unit | Interface |
| TBRRidge + Bayesian + unit | **INV-015** production policy + probe failure |
| TBRRidge + Placebo | Not in scope (invalid_by_interface per COMBO) |

**Deferred:** Interface fix for JK/JKP/Conformal on TBRRidge multi-treated residuals is **out of P2 OC scope** (would be implementation lane, not characterization).

---

## Findings

1. **D5-TBR2-FIND-001:** JK/JKP/Conformal **blocked_interface** on unit TBRRidge — do not schedule promotion OC.
2. **D5-TBR2-FIND-002:** TimeSeriesKfold **callable** but interval semantics **unverified** (negative HW, 100% null exclude).
3. **D5-TBR2-FIND-003:** Registry **Bayesian** remains **blocked_production_policy** (INV-015).
4. **D5-TBR2-FIND-004:** TBRRidge vs class TBR separation confirmed post P0.

---

## Track F / AUDIT-010 alignment

| AUDIT-010 row | Post TBRRIDGE-002 primary bucket |
|---------------|----------------------------------|
| A16 UnitJackKnife | `implemented_but_unvalidated` → **blocked_interface** (OC) |
| A18 Conformal | **blocked_interface** (OC) |
| A19 TimeSeriesKfold | `valid_candidate_pending_OC` → **callable_unverified** |
| A20 Bayesian | **blocked** (unchanged) |
| A21 JKP | **blocked_interface** (OC) |

**Next P2 battery:** **D5-INST-AUGSYNTH-003** (AugSynth Conformal) — separate estimator family.

**Not authorized:** MMM ingress · CalibrationSignal expansion · promotion · TrustReport schema changes.
