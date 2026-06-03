# D5-INST-AUGSYNTH-KFOLD-001 — AugSynthCVXPY + KFold characterization

**Artifact:** [`archives/D5_INST_AUGSYNTH_KFOLD_001_results.json`](archives/D5_INST_AUGSYNTH_KFOLD_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_augsynth_kfold_001.py`  
**Lane:** Research — no promotion, no CalibrationSignal ingress

**Prior:** [`D5_INST_COMBO_AUDIT_001_REPORT.md`](D5_INST_COMBO_AUDIT_001_REPORT.md) · [`D5_INST_AUGSYNTH_001_REPORT.md`](D5_INST_AUGSYNTH_001_REPORT.md) · [`TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md`](../TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001.md)

---

## Summary

**Primary instrument:** `AugSynthCVXPY` + **KFold** inference only (no base AugSynth).

On **greedy_match_markets**, fixed windows (train=28, test=8), `scm_low_signal` (n_geos=16), AugSynthCVXPY+Kfold is **feasible** on unit single-cell panels when donors ≥ `min_donors=5`. **SCM+JK** and **AugSynthCVXPY+JK** are included as **diagnostic context only** — not estimand-equivalence benchmarks.

**Overall verdict:** `remain_restricted_diagnostic_comparator`

| Governance | Value |
|------------|-------|
| CalibrationSignal | **No** |
| MMM ingress | **No** |
| Direct estimand equivalence to SCM+JK | **Forbidden** |
| Track E INST-004 Kfold | **`restricted`** (diagnostic triangulation) |
| COMBO status update | `valid_candidate` → **characterized restricted** |

---

## Callable surface

| Field | Value |
|-------|--------|
| Estimator | `AugSynthCVXPY` only |
| Inference | `Kfold` only |
| Windows | train=28, test=8 (001e / MCELL aligned) |
| Design | `greedy_match_markets` |
| `path_interval_type` | `confidence_interval` |
| Track B alias | None (not in `CONFIG_RESOLUTION`) |

---

## Single-cell results (n_mc=14)

| Instrument @ null | Feasibility | Null interval-exclusion FPR | Mean point @ null | Mean half-width |
|-------------------|------------:|----------------------------:|------------------:|----------------:|
| **AugSynthCVXPY + Kfold** (primary) | **100%** (13/14 reps; 1 thin-donor block) | **0.0** | ~+0.08 | ~8.9 |
| AugSynthCVXPY + JK (context) | 100% (13/14) | 0.0 | ~+0.01 | ~3.4 |
| SCM + JK (context) | 100% | 0.0 | ~−0.03 | — |

@ **8% injection** (context — not promotion evidence):

| Instrument | Mean point | Interval excludes zero rate |
|------------|----------:|-----------------------------:|
| AugSynthCVXPY + Kfold | ~8.14 | 0% on this battery |
| AugSynthCVXPY + JK | ~8.06 | 100% |

**Interpretation:** Kfold intervals are **wider** (~2.6× JK half-width at null) and use **sampling/CV semantics** (`confidence_interval`), not SCM+JK **null-monitor** semantics. Point paths differ from SCM+JK at null (material mismatch vs SCM reference — same pattern as AUGSYNTH-001). **Do not average or equate scales.**

---

## Multi-cell k=2 (per-cell)

| Instrument @ null | Per-cell runs | Feasibility | Null FPR |
|-------------------|--------------:|------------:|---------:|
| AugSynthCVXPY + Kfold | 28 (14 reps × 2 cells) | **100%** | **0.0** |
| AugSynthCVXPY + JK | 28 | **100%** | **0.0** |

**Policy:** Per-cell only; **no pooled** multi-cell Kfold claim. No `insufficient_donors` failures on this battery (unlike AUGSYNTH-001 point probe on one thin cell) — still subject to MCELL k≤2 discipline.

---

## Context comparisons (not equivalence tests)

| Metric | Value |
|--------|------:|
| Null detection disagreement Kfold vs JK | ~0% on feasible runs |
| Null detection disagreement Kfold vs SCM+JK | ~0% at null on this battery |
| Kfold null point seed sensitivity (std across 3 seeds) | low on sampled reps |

---

## Stop-condition answer

| Geometry | Verdict |
|----------|---------|
| **single_cell** | **Remain a valid restricted diagnostic comparator** — feasible, conservative null FPR on this battery, but **not** CalibrationSignal-eligible and **not** estimand-equivalent to SCM+JK |
| **multi_cell k=2 per-cell** | **Same restricted status** when donors ≥ 5; per-cell only |

**Not blocked** — COMBO `valid_candidate` is **closed by this OC** as **characterized restricted**.

**Not promoted** — remains diagnostic triangulation input only until separate governance PRs.

---

## Findings

1. **D5-ASKF-FIND-001:** AugSynthCVXPY+Kfold completes on 001e windows; probe-validated combo is OC'd.
2. **D5-ASKF-FIND-002:** `confidence_interval` semantics differ from JK null-monitor role despite similar null FPR here.
3. **D5-ASKF-FIND-003:** Kfold intervals are materially wider than AugSynth JK on this battery.
4. **D5-ASKF-FIND-004:** No Track B alias / CalibrationSignal path — intentional.

---

## Sequence

**Next:** ~~D5-INST-TBR-001~~ ✅ → **AUDIT-010**. Optional P2: TBRRidge-002; AugSynth Conformal (separate battery).

**Rules acknowledged:** No production, estimator, inference, TrustReport, Track B schema, or MMM changes in this package.
