# D5-INST-AUDIT-001 — GeoX estimator × inference × geometry inventory

**Artifact:** [`archives/D5_INST_AUDIT_001_results.json`](archives/D5_INST_AUDIT_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_audit_001.py`  
**Lane:** Research — inventory only; no promotion

---

## Summary

Code-grounded inventory of **13 estimator classes**, **9 registry inference modes**, and **8 geometry modes** (including design-only supergeo/trim). Live probes on a fixed `scm_low_signal` panel (train=20, test=6, n_geos=12) produced **192** matrix rows (**128** `probe_success`).

**Overall verdict:** `inventory_complete_augsynth_tbr_then_mmm_readiness_audit_010`

---

## Estimators in repo (catalog)

| Registry | Class | Maturity | Default validation runner | D5 OC |
|----------|-------|----------|---------------------------|-------|
| SCM | SyntheticControl | expert_review | ✅ | 001b/e, D3 |
| SCM CVXPY | SyntheticControlCVXPY | expert_review | — | D2, test_scm |
| AugSynth | AugSynth | unvalidated | — | D2 only |
| AugSynth CVXPY | AugSynthCVXPY | expert_review | — | Phase 14 |
| TBR | TBR | expert_review | — (mislabeled TBRRidge in recovery) | **None** |
| TBRRidge | TBRRidge | expert_review | ✅ (as "TBR") | 001a/c, D5-INST-TBRRIDGE-001 |
| TBRAutoSARIMAX | TBRAutoSARIMAX | expert_review | — | None |
| BayesianTBR | BayesianTBR | research_only | skipped (jax) | INV-015 |
| BayesianTBRHorseShoe | BayesianTBRHorseShoe | research_only | skipped | INV-015 |
| DID | DID | expert_review | ✅ | D3, DEF-003 |
| SyntheticDID | SyntheticDID | research_only | skipped | tests only |
| TROP | TROP | research_only | skipped | trop_test.py |
| MTGP | MTGP | research_only | skipped | — |

---

## Inference modes (registry)

| Mode | Path interval type | Maturity |
|------|-------------------|----------|
| point_estimate | unavailable | expert_review |
| UnitJackKnife | confidence_interval | expert_review |
| JKP | confidence_interval | expert_review |
| Bayesian | credible_interval | research_only |
| BlockResidualBootstrap | confidence_interval | expert_review |
| Conformal | conformal_interval | expert_review |
| Kfold | confidence_interval | expert_review |
| Placebo | placebo_band | expert_review |
| TimeSeriesKfold | confidence_interval | expert_review |

**Not in registry:** DID moving-block bootstrap (estimator-native in `DID.run_analysis`).

---

## Readout paths (production vs research)

| Path | Panel geometry | Estimator | Inference | Governed role |
|------|----------------|-----------|-----------|---------------|
| **Null monitor** | Unit-level multi-market | SyntheticControl | UnitJackKnife | Reference (001e) |
| **Geo power / MDE** | Aggregate 2-row sum | TBRRidge | Kfold | Diagnostic / restricted |
| **Placebo null** | Unit single-treated | SyntheticControl | Placebo | diagnostic_only |
| **DID** | Unit pooled TWFE | DID | native bootstrap | restricted (cumulative ATT) |
| **Track B cards** | Per config | See `CONFIG_RESOLUTION` | See alias | No MMM except SCM JK null_monitor |

---

## Explicit answers

### Normal TBR

- **Where it runs:** `panel_exp.methods.tbr.TBR` via `ImpactAnalyzer.run_analysis` when the panel has **exactly one treated series and one control series** (`tbr.py` asserts).
- **Unit-level vs aggregate:** **Aggregate only** for class `TBR`. Unit panels with multiple controls **fail asserts**; use **TBRRidge** for de-aggregated controls.
- **Inference wired:** Catalog lists point_estimate, UnitJackKnife, JKP, Kfold. **Placebo blocked** for `TBR` in `inference/modes/impl.py`.
- **Product note:** `GeoExperimentDesign` power uses **TBRRidge** on aggregated panels, **not** class `TBR`.
- **Audit finding:** `recovery_runner` key `"TBR"` uses **TBRRidge** factory — not true TBR.

### BayesianTBR

- **Where:** `bayesian_regression.BayesianTBR` / `BayesianTBRHorseShoe`; optional JAX stack.
- **Geometry:** Supports **multi-control unit-level** panels in `fit_data`; docstring allows aggregated or de-aggregated controls.
- **Uncertainty:** Registry **`Bayesian`** mode → `credible_interval` via JAX quantiles on `predict()` — **≠** full NUTS MCMC from `fit_model()` unless used directly (INV-015).
- **Status:** **research_only**; skipped in `EstimatorValidationRunner`.

### AugSynth

- **AugSynth:** Implemented; point/Kfold/Conformal; **unvalidated**; few tests.
- **AugSynthCVXPY:** Requires cvxpy+osqp; Phase 14 OC; Track B `AugSynthCVXPY_Point` + characterized JK (not CalibrationSignal-eligible).

### TROP

- **Active code** in `triply_robust_est.py`; **research_only**; validation runner **skipped**; `tests/trop_test.py` only.

### Tested today (D5 instrument batteries)

- ✅ SCM+JK (001b/e), TBRRidge+Kfold/BRB (001a/c, D5-INST-TBRRIDGE-001), SCM+Placebo (D5-INST-PLACEBO-001)
- ❌ Normal TBR class, BayesianTBR MCMC, TROP, SyntheticDID recovery, MTGP, AugSynth base D5 harness

---

## Proposed OC battery roadmap

| Priority | Battery | Rationale |
|----------|---------|-----------|
| **P1** | ~~D5-INST-AUGSYNTH-001~~ ✅ | [`D5_INST_AUGSYNTH_001_REPORT.md`](D5_INST_AUGSYNTH_001_REPORT.md) |
| **P1** | D5-INST-TBR-001 | Distinct aggregate-only TBR vs TBRRidge — **before MMM readiness audit** |
| **P0 (after P1)** | **AUDIT-010** | **MMM readiness / gap audit** — not a promotion gate until AugSynth + normal TBR characterized |
| **P2** | D5-INST-TBRRIDGE-002 | JK, Conformal, TimeSeriesKfold, registry Bayesian on TBRRidge |
| **P2** | D5-INST-BAYESIANTBR-001 | Registry vs NUTS; research-only; block from MMM intake in AUDIT-010 |
| **P3** | D5-INST-TROP-001 | Research-only follow-up; block from MMM intake in AUDIT-010 |
| **deferred** | D5-INST-DID-001 | DEF-016; policy closed on relative ATT |

---

## Findings

1. **D5-AUD-FIND-001:** TBR requires 1×1 aggregated series; TBRRidge is the multi-control / unit path.
2. **D5-AUD-FIND-002:** Registry `Bayesian` ≠ BayesianTBR NUTS MCMC.
3. **D5-AUD-FIND-003:** DID bootstrap is native, not registry `bootstrap`.
4. **D5-AUD-FIND-004:** recovery_runner `TBR` config points at TBRRidge factory.

**Sequence:** ~~D5-INST-AUGSYNTH-001~~ ✅ → D5-INST-TBR-001 → **AUDIT-010** (readiness/gap) → P2/P3 follow-ups. **Combo audit:** [`D5_INST_COMBO_AUDIT_001_REPORT.md`](D5_INST_COMBO_AUDIT_001_REPORT.md). MMM intake only after AUDIT-010 gaps closed.
