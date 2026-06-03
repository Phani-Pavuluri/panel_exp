# D5-INST-AUGSYNTH-001 — AugSynth / AugSynthCVXPY geometry characterization

**Artifact:** [`archives/D5_INST_AUGSYNTH_001_results.json`](archives/D5_INST_AUGSYNTH_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_augsynth_001.py`  
**Lane:** Research — no promotion, no CalibrationSignal ingress

**Prior:** [`D5_INST_AUDIT_001_REPORT.md`](D5_INST_AUDIT_001_REPORT.md)

---

## Summary

On **greedy_match_markets**, fixed windows (train=28, test=8), `scm_low_signal` (n_geos=16), **AugSynthCVXPY** is **100% feasible** on **single-cell** unit panels when donors ≥ `min_donors=5`. **UnitJackKnife** runs with **null interval-exclusion FPR = 0** (conservative null-monitor pattern, aligned with Phase 14). **Point-only** path has no intervals by design.

**Overall verdict:** `remain_diagnostic_only_no_calibration_signal`

**Governance headline:** AugSynthCVXPY is the **strongest characterized comparator** for triangulation on this battery — **not** automatic CalibrationSignal or MMM ingress. **Reliable estimator ≠ governed MMM instrument.**

---

## Callable surfaces

| Variant | Callable | Track B | Inference on battery |
|---------|----------|---------|----------------------|
| **AugSynthCVXPY** | ✅ (cvxpy+osqp) | `AugSynthCVXPY_Point` | point, UnitJackKnife |
| **AugSynth** (base) | ✅ probe (inner CVXPY) | — | point probe only |
| **AugSynthCVXPY_UnitJackKnife** | ✅ | characterized in D3; not registry-eligible | JK |

Registry lists **point_only** for Track B export; JK is a separate characterized path (Phase 14 + this D5).

---

## Key results (n_mc=14, single_cell)

| Instrument | Fit / feasibility | Mean point @ null | Null interval-exclusion FPR | Mean JK half-width @ null |
|------------|-------------------|-------------------|----------------------------|---------------------------|
| SCM+JK (reference) | 100% | ~−0.10 | **0.0** | — |
| AugSynthCVXPY point | 100% | ~+0.18 | n/a (no interval) | — |
| AugSynthCVXPY+JK | 100% | ~+0.18 | **0.0** | ~3.7 |

@ 8% injection: AugSynth point mean ~**8.2** vs SCM+JK on relative-att scale — **material scale/path disagreement** with SCM reference (compare as context only; no averaging).

**SCM+JK vs AugSynth @ null:** sign disagreement common; material point mismatch rate **100%** on this battery (different effect path / augmentation).

---

## Multi-cell k=2 (per-cell)

- **AugSynthCVXPY point:** feasible on **per-cell** runs when donors ≥ 5.
- **2 cell-runs** blocked (`insufficient_donors_need_5_got_2`) — thin control in a concurrent cell.
- **No pooled** AugSynth claim across cells (MCELL discipline).

---

## Base AugSynth

- **Callable** via inner `SyntheticControlCVXPY` on this battery (probe matches CVXPY point numerically).
- Remains **unvalidated** as a separate governed instrument — **do not force** dedicated base-AugSynth OC.

---

## Track E status (refined)

| Card | Prior E2 | After D5-INST-AUGSYNTH-001 |
|------|----------|----------------------------|
| **INST-004 point** | diagnostic_only | **`diagnostic_only`** — characterized comparator; not CalibrationSignal |
| **INST-004 JK** | characterization_required | **`diagnostic_only`** — D5 + Phase 14 close geometry gap; null-monitor only |

---

## Gaps before AUDIT-010 (MMM readiness)

1. ✅ AugSynthCVXPY on 001e windows (this artifact).
2. ⏳ **D5-INST-TBR-001** (normal TBR aggregate path).
3. Then **AUDIT-010** readiness/gap audit (not promotion).

P2 follow-ups: TBRRidge-002, BayesianTBR, TROP — block from MMM intake in AUDIT-010 unless explicitly scoped.

---

## Findings

1. **D5-AS-FIND-001:** CVXPY path reliable on tier-1 single-cell geometry; not decision-grade for MMM.
2. **D5-AS-FIND-002:** JK conservative at null — triangulation/diagnostic only.
3. **D5-AS-FIND-003:** k=2 per-cell works with donor floor; occasional thin-cell failure.
4. **D5-AS-FIND-004:** Point scale ≠ SCM+JK at null and under injection — no lift compare without bridge.

**Next:** D5-INST-TBR-001 → AUDIT-010.
