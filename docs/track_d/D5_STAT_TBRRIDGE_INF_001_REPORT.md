# D5-STAT-TBRRIDGE-INF-001 — Level B characterization (TBRRidge inference)

**Artifact ID:** D5-STAT-TBRRIDGE-INF-001  
**Type:** Level B inference-path characterization — **not** operator contract, **not** promotion  
**Overall verdict:** `characterization_mixed_requires_followup`

**Archive:** [`archives/D5_STAT_TBRRIDGE_INF_001_results.json`](archives/D5_STAT_TBRRIDGE_INF_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_stat_tbrridge_inf_001.py`  
**Regenerate:** `poetry run python -m panel_exp.validation.track_d_d5_stat_tbrridge_inf_001`

## 1. Purpose

Characterize **existing** TBRRidge inference wrappers on **unit-panel single-cell** geometry under deterministic synthetic worlds. Record callable status, interval orientation, leakage/split caveats, and readout-scale ambiguity. This artifact does **not** upgrade TBRRidge, redesign inference, or assign production roles.

## 2. Relationship to D5 queue

Follows **`D5-STAT-SMOKE-CALLABLE-001`**, **`D5-STAT-SCM-JK-001`**, **`D5-STAT-AUGSYNTH-POINT-001`**, **`D5-STAT-TBR-AGG-001`**, **`D5-STAT-DID-BOOTSTRAP-001`**, and **`D5-STAT-MCELL-PERCELL-001`**. TBRRidge inference was deferred in the enhancement roadmap because wrappers require careful readout, time-split, leakage, and uncertainty-target semantics — this artifact supplies characterization-only evidence for that gap.

## 3. Relationship to METHOD_ENHANCEMENT_ROADMAP_001

Per **`METHOD-ENHANCEMENT-ROADMAP-001`**, post-Level-B enhancement begins with **`INFERENCE_READOUT_SEMANTICS_001`** unless a severe geometry-definition failure blocks readout work. Results here show **no geometry-bridge blocker** (unit-panel identity holds); Conformal is blocked by **implementation readout shape**, not geometry definition.

## 4. Scope and exclusions

**In scope:** TBRRidge + KFold, TimeSeriesKFold, BlockResidualBootstrap (BRB); Conformal probed and blocked with explicit reason. Unit-panel single-cell geometry; seven worlds; 12 replicates (KFold/TSKFold), 6 replicates (BRB/Conformal attempted).

**Out of scope:** SARIMAX; Auto-SARIMAX; Bayesian; TBRRidge+JK; aggregate 2-row TBR; SCM/AugSynth unit paths; multi-cell pooled; supergeo; trim; estimator/inference code changes; TrustReport; CalibrationSignal; MMM; LLM; primary/secondary evidence labels; governed-readout claims.

## 5. TBRRidge geometry and method identity

- **Geometry:** `single_cell_unit_level` — shared control donors + multiple treated unit rows; **not** 2-row aggregate (`TBR-AGG` scope).
- **Assignment:** `greedy_match_markets` with internal assignment-seed retry until ≥3 control units.
- **Method identity guard:** `TBRRidge` class enforced before readout.
- **Panel guard:** rejects ≤2-row panels (aggregate geometry).

## 6. Inference paths characterized

| Path | Level B status | Replicates/world | Callable |
|------|----------------|------------------|----------|
| `TBRRIDGE-KFOLD` | characterized | 12 | 84/84 pass |
| `TBRRIDGE-TSKFOLD` | characterized | 12 | 84/84 pass |
| `TBRRIDGE-BRB` | characterized | 6 | 42/42 pass |

All three paths produce finite point estimates and intervals on tested worlds. Structural checks: **0** interval orientation failures, **0** negative half-widths, **0** non-finite outputs on characterized paths.

## 7. Inference paths skipped or blocked

| Path | Smoke status | Level B status | Skip / block reason |
|------|--------------|----------------|---------------------|
| `TBRRIDGE-TSKFOLD` | skipped (`no_smoke_probe_mapping`) | **characterized** | Smoke gap only |
| `TBRRIDGE-BRB` | skipped (`no_smoke_probe_mapping`) | **characterized** | Smoke gap only |
| `TBRRIDGE-CONFORMAL` | skipped (`no_smoke_probe_mapping`) | **blocked** | `multi_treated_unit_panel_broadcast_failure` — `ValueError` broadcast `(8,n_treated)` vs `(8,)` |

Conformal: **42/42 runs skipped** (6 replicates × 7 worlds). No silent fallback.

## 8. Fixture world design

Fixed seeds; `random_state_base=20260612`. Worlds: `clean_null`, `clean_positive_lift`, `weak_signal_null`, `noisy_positive_lift`, `trend_mismatch_null`, `post_shock_null`, `short_pre_or_short_post` (22 pre / 4 post). Percent post-period injection on treated units; `true_effect` records injection parameter (not outcome-scale cumulative).

## 9. Split and leakage policy checks

| Path | Split policy | Leakage / target caveat |
|------|--------------|-------------------------|
| KFold | panel K-fold (random/blocked) | Temporal leakage possible; **prediction-stability**, not causal-uncertainty validated |
| TimeSeriesKFold | chronological horizon-blocked folds | Forecast-stability target; causal interval semantics not established |
| BRB | block residual bootstrap (block=3, n=8) | Interval target ambiguous without readout contract |
| Conformal | blocked before calibration split | Exchangeability / time-dependence caveat moot — not callable |

Full register in JSON `leakage_register`.

## 10. Results by inference path

**KFold / TimeSeriesKFold (parallel behavior):**

| world | feasible | orient fail | null interval FPR | directional FPR | coverage (lift) | sign err (lift) |
|-------|----------|-------------|-------------------|-----------------|-----------------|-----------------|
| clean_null | 12/12 | 0 | 0.00 | 1.00 | — | — |
| clean_positive_lift | 12/12 | 0 | — | — | 1.00 | 1.00 |
| weak_signal_null | 12/12 | 0 | 0.00 | 1.00 | — | — |
| noisy_positive_lift | 12/12 | 0 | — | — | 1.00 | 1.00 |
| trend_mismatch_null | 12/12 | 0 | 0.00 | 1.00 | — | — |
| post_shock_null | 12/12 | 0 | 0.00 | 0.92 | — | — |
| short_pre_or_short_post | 12/12 | 0 | — | — | 1.00 | 1.00 |

**BRB:**

| world | feasible | orient fail | null interval FPR | directional FPR | coverage (lift) | sign err (lift) |
|-------|----------|-------------|-------------------|-----------------|-----------------|-----------------|
| clean_null | 6/6 | 0 | 0.00 | 0.00 | — | — |
| clean_positive_lift | 6/6 | 0 | — | — | 1.00 | 0.00 |
| weak_signal_null | 6/6 | 0 | 0.00 | 0.00 | — | — |
| noisy_positive_lift | 6/6 | 0 | — | — | 1.00 | 0.00 |
| trend_mismatch_null | 6/6 | 0 | 0.00 | 0.00 | — | — |
| post_shock_null | 6/6 | 0 | 0.00 | 0.00 | — | — |
| short_pre_or_short_post | 6/6 | 0 | — | — | 1.00 | 0.00 |

## 11. Null behavior

KFold/TSKFold: interval mean covers zero on all null worlds (null interval FPR **0**), but **directional false-signal rate ~1.0** on outcome-scale point readout (large |point| vs threshold 500). BRB: both interval and directional null signals **0** on tested null worlds — paths diverge materially at null.

## 12. Injected lift recovery

Outcome-scale point estimates do **not** align with percent injection parameter (documented readout-scale caveat). KFold/TSKFold show **sign_error_rate = 1.0** on lift worlds when comparing point sign to percent injection sign. BRB shows **sign_error_rate = 0.0** on lift worlds under the same comparison — further evidence that readout semantics differ by path and require explicit contract.

## 13. Interval orientation and width checks

**0** orientation failures and **0** negative half-width detections across **210** characterized callable runs. Intervals present on all callable runs for KFold, TSKFold, and BRB.

## 14. Coverage and interval target caveats

Reported coverage vs percent injection is **1.0** on lift worlds for characterized paths — this reflects wide outcome-scale intervals vs a percent truth target, **not** validated causal coverage. Interval targets remain **ambiguous** (prediction stability vs ATT) per leakage register.

## 15. Prediction uncertainty vs causal uncertainty caveat

All characterized intervals reflect **wrapper output dispersion** under split/bootstrap designs documented in the leakage register. None constitute validated causal interval semantics without **`INFERENCE_READOUT_SEMANTICS_001`**. KFold in particular may leak post-treatment information across random folds — flagged explicitly.

## 16. Failure / skip / leakage registers

- **failure_register:** empty (0 hard failures on characterized paths).
- **skip_register:** Conformal blocked (`multi_treated_unit_panel_broadcast_failure`); TSKFold/BRB smoke gaps resolved at Level B.
- **leakage_register:** four entries with split policies and prediction-vs-causal notes.

## 17. Overall verdict

**`characterization_mixed_requires_followup`**

Structural interval checks pass on callable paths. Mixed verdict driven by: (1) KFold/TSKFold high null directional signal on outcome-scale points; (2) readout-scale mismatch vs percent injection; (3) ambiguous interval targets and KFold leakage risk; (4) Conformal blocked on multi-treated unit panel.

## 18. What this artifact does not authorize

No promotion; no trust role; no CalibrationSignal or MMM wiring; no LLM recommendation; no governed readout claim; no geometry generalization to aggregate TBR, MCELL pooled, supergeo, or trim; no claim that Level B equals statistical validation; no production readiness.

## 19. Recommended next artifacts

1. **`INFERENCE_READOUT_SEMANTICS_001`** — primary next (Conformal broadcast + KFold/TSKFold vs BRB null divergence + outcome vs percent readout).
2. Geometry bridge **not** recommended first — unit-panel identity held; block is readout semantics.

## 20. Roadmap and audit updates checked

| Document | Update |
|----------|--------|
| `METHOD_ENHANCEMENT_ROADMAP_001.md` | D5-STAT-TBRRIDGE-INF-001 marked complete; next = INFERENCE_READOUT_SEMANTICS_001 |
| `METHOD_VALIDATION_PROGRAM_001.md` | TBRRidge Level B complete; next planning artifact named |
| `ROADMAP_V4.md` | Layer 5 TBRRidge INF complete |
| `MIP_AUDIT_REGISTRY.md` | D5 queue advanced |
| `METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md` | Item 14 complete |
| `DESIGN_ESTIMATOR_INFERENCE_SUITABILITY_FRAMEWORK_001.md` | Evidence posture updated; no tier advance |
| `METHOD_COMBINATION_VALIDATION_MATRIX_001.md` | TBRRidge INF row characterized |
| `METHOD_STATISTICAL_VALIDATION_PROTOCOL_001.md` | Level B archive reference added |
| `D5_STAT_MCELL_PERCELL_001_REPORT.md` | Next-artifact pointer updated |

## 21. Guardrails

`tbrridge_inference_only`, `single_cell_unit_level_geometry`, `level_b_characterization_only`, `no_governed_uncertainty_claim`, `no_promotion`, `no_sarimax`, `no_bayesian`, `outcome_scale_readout_vs_percent_injection_caveat`. All `forbidden_flags` in JSON are **false**.
