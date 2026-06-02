# D5-INST-TBRRIDGE-001 — TBRRidge + KFold / BRB restricted-instrument characterization

**Artifact:** [`archives/D5_INST_TBRRIDGE_001_results.json`](archives/D5_INST_TBRRIDGE_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_tbrridge_001.py`  
**Lane:** Research — no promotion, no CalibrationSignal ingress

---

## Summary

Under **greedy_match_markets** assignment, fixed windows (train=28, test=8), and `scm_low_signal` (n_geos=16), **TBRRidge+Kfold** and **TBRRidge+BRB** remain **`restricted`** comparators. They are **not** interchangeable with governed **SCM+JK** null-monitor evidence even when null **interval-exclusion FPR** matches on this battery.

**Overall verdict:** `remain_restricted_no_promotion`

---

## Instruments tested

| Path | Panel | Role |
|------|-------|------|
| **scm_jk_unit** | Unit markets + shared-control readout | Reference null-monitor only |
| **tbr_kfold_unit** | Same unit panel | Restricted comparator |
| **tbr_kfold_agg2** | 2-row sum treated/control | Geo power / aggregation sensitivity |
| **tbr_brb_unit** | Unit panel | Restricted; BRB feasible on battery |
| **tbr_brb_agg2** | 2-row aggregate | Aggregation sensitivity |

Optional **k=2 multi-cell** per-cell runs included in artifact (per-cell only, no pooling).

---

## Key results (n_mc=14, null effect)

| Instrument | Null interval-exclusion FPR | Mean point @ null | Mean half-width |
|------------|----------------------------|-------------------|-----------------|
| SCM+JK unit | **0.0** | ~0.07 | ~3.0 |
| TBR+Kfold unit | **0.0** | **~-387** | ~17.9 |
| TBR+Kfold agg2 | **0.0** | ~0.70 | ~6.4 |
| TBR+BRB unit | **0.0** | ~0.85 | ~6.4 |

**Interpretation:** Shared null FPR on the PowerAnalysis-style criterion does **not** imply comparable estimands. Unit-level TBR point effects operate on a **different scale** than SCM+JK relative ATT (consistent with D5-POW-001a/001c). Aggregated 2-row TBR is closer in magnitude to SCM point scale but still not a governed bridge.

@ 8% injection: unit TBR point moves (~-379 vs ~-387 null) but remains non-comparable to SCM injection response.

**Kfold seed sensitivity** at null: negligible on mean point (spread ~0) — stability of *detection flag* not of *economic magnitude*.

**Disagreement rate (detection mismatch SCM vs TBR):** 0% on this battery — both conservative on interval exclusion; conflict fixtures arise from **restricted positive** intervals, not from null FPR alone.

---

## Track E status (unchanged)

| Card | Status |
|------|--------|
| **INST-002** TBRRidge+Kfold | **`restricted`** — diagnostic / TrustReport context only |
| **INST-003** TBRRidge+BRB | **`restricted`** — no CalibrationSignal |
| Governed primary | SCM+JK null-monitor only |

**Narrower wording:** TBRRidge may be cited for **null-viability / exploratory** diagnostics on the **correct panel geometry** (agg2 for power path, unit panel only with explicit scale bridge). Never for lift promotion or MMM.

---

## Governance reminders

- Do **not** use TBRRidge+Kfold geo power output as platform MDE or unit null-monitor (D4-FIND-001).
- Do **not** let restricted TBR positive intervals override null-compatible SCM+JK primary (E4-002, E5-R-002).
- **No** pooled multi-cell TBR claim.

---

## Findings

1. **D5-TBR-FIND-001:** Aggregation geometry changes TBR point scale by orders of magnitude vs unit TBR.
2. **D5-TBR-FIND-002:** Unit TBR vs SCM+JK point effects are not comparable at null or under injection.
3. **D5-TBR-FIND-003:** BRB runs on this battery but does not justify promotion.

**Next:** ~~D5-INST-PLACEBO-001~~ ✅ → D5-INST-DID-001 → AUDIT-010 (not MMM).
