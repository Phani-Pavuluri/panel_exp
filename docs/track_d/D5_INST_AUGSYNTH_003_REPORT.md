# D5-INST-AUGSYNTH-003 — AugSynthCVXPY + Conformal characterization

**Artifact:** [`archives/D5_INST_AUGSYNTH_003_results.json`](archives/D5_INST_AUGSYNTH_003_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_augsynth_003.py`  
**Lane:** Research — no promotion, no CalibrationSignal ingress

**Prior:** [`D5_INST_AUGSYNTH_001_REPORT.md`](D5_INST_AUGSYNTH_001_REPORT.md) · [`D5_INST_AUGSYNTH_KFOLD_001_REPORT.md`](D5_INST_AUGSYNTH_KFOLD_001_REPORT.md) · [`D5_INST_TBRRIDGE_002_REPORT.md`](D5_INST_TBRRIDGE_002_REPORT.md) · [`AUDIT-010_mmm_readiness_gap.md`](../audits/AUDIT-010_mmm_readiness_gap.md) · Track F P0 ✅

---

## Summary

**Primary instrument:** `AugSynthCVXPY` + **Conformal** inference only (no base AugSynth).

On **greedy_match_markets**, fixed windows (train=28, test=8), `scm_low_signal` (n_geos=16), AugSynthCVXPY+Conformal is **interface-valid** on unit single-cell panels when donors ≥ `min_donors=5`. **AugSynth point/JK/Kfold** and **SCM+JK** are **diagnostic context only**.

**Primary disposition:** `callable_unverified_interval_semantics`  
**Overall verdict:** `remain_restricted_no_promotion`

| Governance | Value |
|------------|-------|
| CalibrationSignal | **No** |
| MMM ingress | **No** |
| Governed uncertainty | **No** — interval semantics fail on battery |
| Track F P2 | **Complete** — no further P2 batteries scheduled |
| COMBO status update | `valid_candidate_pending_OC` → **callable_unverified_interval_semantics** |

---

## Conformal interval semantics (recorded)

| Field | Value |
|-------|--------|
| **Score definition** | Pre-period absolute residuals `\|Y_{j,t} - \hat{Y}_{j,t}\|` vs treated-period `\|Y_{j,T} - \hat{Y}_{j,T}\|`; one-sided p-value via rank in pre-period empirical CDF (`conformal.py`) |
| **Exchangeability assumption** | Pre-treatment residual magnitudes exchangeable with treated-period under null — fragile under spillover / structural breaks |
| **Residual / source units** | Level outcomes on treated path (same y/ŷ scale as AugSynthCVXPY after percent-effect injection) |
| **`path_interval_type`** | `conformal_interval` |
| **Diagnostic-only** | **Yes** — not governed uncertainty unless band semantics pass |
| **Code refs** | `panel_exp/inference/conformal.py` · `run_conformal` in `modes/impl.py` |

**Do not treat conformal band as governed uncertainty on this battery** — 100% negative half-width and 100% null interval-exclusion FPR on feasible runs.

---

## Callable surface

| Field | Value |
|-------|--------|
| Estimator | `AugSynthCVXPY` only |
| Inference | `Conformal` only |
| Windows | train=28, test=8 (001e / MCELL aligned) |
| Design | `greedy_match_markets` |
| Combo-scale probe (train=20, test=6) | **probe_success** — consistent with COMBO-AUDIT-001 |
| Track B alias | None |

---

## Single-cell results (n_mc=14)

| Instrument @ null | Feasibility | Null interval-exclusion FPR | Mean point @ null | Mean half-width | Negative HW rate |
|-------------------|------------:|----------------------------:|------------------:|----------------:|-----------------:|
| **AugSynthCVXPY + Conformal** (primary) | **100%** (13/14 reps; 1 thin-donor block) | **1.0** | ~−0.08 | **~−8.2** | **100%** |
| AugSynthCVXPY + Kfold (context) | 100% (13/14) | 0.0 | ~+0.08 | ~8.9 | 0% |
| AugSynthCVXPY + JK (context) | 100% (13/14) | 0.0 | ~+0.01 | ~3.4 | — |
| SCM + JK (context) | 100% | 0.0 | ~−0.01 | — | — |

@ **8% injection** (context — not promotion evidence):

| Instrument | Mean point | Null-exclusion rate | Mean half-width |
|------------|----------:|--------------------:|----------------:|
| AugSynthCVXPY + Conformal | ~7.97 | 100% | ~−73.9 |
| AugSynthCVXPY + Kfold | ~8.14 | 0% | ~8.9 |
| AugSynthCVXPY + JK | ~8.06 | 100% | ~3.4 |

**Interpretation:** Conformal **runs** and emits `conformal_interval`, but **band sign is invalid** (negative half-width) and **always excludes zero at null** on feasible runs — opposite of JK/Kfold null behavior on this battery. **Not interchangeable** with SCM+JK null-monitor or Kfold CI. Point path remains on AugSynth scale (material mismatch vs SCM+JK reference).

---

## Multi-cell k=2 (per-cell)

| Instrument @ null | Per-cell runs | Feasibility | Null FPR | Negative HW rate |
|-------------------|--------------:|------------:|---------:|-----------------:|
| AugSynthCVXPY + Conformal | 28 (14 reps × 2 cells) | **100%** | **1.0** | **100%** |
| AugSynthCVXPY + JK (context) | 28 | **100%** | **0.0** | — |

**Policy:** Per-cell only; **no pooled** multi-cell Conformal claim.

---

## Explicit blocks (out of scope)

| Combo / path | Block reason |
|--------------|--------------|
| AugSynthCVXPY + Placebo | Not in `inference_support` — F-P0-005 inference/falsification only |
| AugSynthCVXPY + BRB | Not in catalog — P3 clarification |
| `full_model=True` | **INV-D2-001** / F-P0-001 governed export block |
| Pooled multi-cell | Per-cell only unless `pooling_rule_id` |
| Base AugSynth (non-CVXPY) | Out of battery scope |

---

## Context comparisons (not equivalence tests)

| Metric | Value |
|--------|------:|
| Null detection disagreement Conformal vs JK | ~100% on feasible runs |
| Null detection disagreement Conformal vs Kfold | ~100% |
| Null detection disagreement Conformal vs SCM+JK | ~100% |
| Conformal negative half-width cell rate | **100%** |

---

## Stop-condition answer

| Geometry | Disposition |
|----------|-------------|
| **single_cell** | **`callable_unverified_interval_semantics`** — interface-valid; interval semantics **fail** OC (negative HW, 100% null exclude) |
| **multi_cell k=2 per-cell** | **Same disposition** — per-cell only; not governed uncertainty |

**Not promoted** — remain restricted diagnostic; no CalibrationSignal or MMM path.

**Track F P2 complete** — TBRRidge-002 ✅ + AugSynth Conformal ✅; promotion **not authorized**.

---

## Findings

1. **D5-ASCF-FIND-001:** AugSynthCVXPY+Conformal completes on 001e windows when donors ≥ 5; COMBO probe_success confirmed at combo scale.
2. **D5-ASCF-FIND-002:** `conformal_interval` semantics differ from JK null-monitor and Kfold `confidence_interval`.
3. **D5-ASCF-FIND-003:** **100% negative half-width** and **100% null interval-exclusion FPR** — not governed uncertainty (parallel to TBRRidge TimeSeriesKfold pattern).
4. **D5-ASCF-FIND-004:** Placebo/BRB/full_model/pooled multi-cell explicitly blocked; no Track B / CalibrationSignal expansion.

---

## AUDIT-010 alignment

| Row | Post AUGSYNTH-003 primary bucket |
|-----|----------------------------------|
| **A05** AugSynthCVXPY + Conformal | `valid_candidate_pending_OC` → **`callable_unverified_interval_semantics`** |

---

## Sequence

**Prior:** ~~TBRRidge-002~~ ✅ · ~~AugSynth Kfold~~ ✅ · ~~AUDIT-010~~ ✅ · ~~Track F P0~~ ✅

**Next:** Track F **P2 complete**. Further work requires separate governance PR — **not promotion**.

**Rules acknowledged:** No production, estimator, inference, TrustReport, Track B schema, or MMM changes in this package.
