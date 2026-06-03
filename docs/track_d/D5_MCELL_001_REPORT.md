# D5-MCELL-001 — Optimal concurrent cell-count characterization

**Artifact:** [`archives/D5_MCELL_001_results.json`](archives/D5_MCELL_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_mcell_001.py`  
**Lane:** Research (extends D5-POW-001e; per-cell only)

---

## Summary

Multi-cell is a **geometry mode** (`n_test_grps > 1`), not a separate design method. This battery sweeps **k ∈ {1,…,5}** for all six tier-1 geo-run designs on `scm_low_signal` (n_geos=16) with the same fixed-window **SCM+JK null-monitor** readout as D5-POW-001e.

**Overall verdict:** `acceptable_with_caveats_two_cells` — most methods support **k=2**; **k≥3** degrades; conservative **k≤1** if every method must pass (e.g. `balancedrandomization` degrades at k=2).

---

## Rule of thumb (this battery)

| Setting | Guidance |
|---------|----------|
| **Majority of tier-1 methods** | **≤ 2 concurrent test cells** |
| **Conservative (all six methods)** | **≤ 1 cell** |
| **k ≥ 3** | Degraded — ~1 treated market per cell, shared-control stress, higher per-cell null FPR |
| **k = 4–5** | Further degradation / multiple-comparison warnings |
| **Claims** | **Per-cell only** — no pooled multi-cell null FPR or lift |

Scale with **n_geos** and **treatment_probability**: larger panels may support higher k; re-run harness before product defaults change.

---

## Readout contract (unchanged from 001e)

- **Donors:** shared `control` arm only per cell (other test cells excluded from donor pool).
- **SCM+JK:** null-monitor reference — not lift detection or MMM ingress.
- **Excluded:** supergeos, trimmedmatch, quickblock, matchedpair.

---

## Per-method snapshot (n_mc=14)

See artifact `recommendations.per_method` for full tables. Typical pattern:

| Method | recommended_max_cells | degraded_at | notes |
|--------|----------------------|-------------|--------|
| greedy_match_markets | 2 | 3+ | Aligns with 001e |
| rerandomization_wrapper | 2 | 3+ | Aligns with 001e |
| completerandomization | 2 | 3+ | |
| balancedrandomization | 1 | 2 | Stricter — drives conservative k=1 |
| stratifiedrandomization | 3 | 4+ | Slightly more k on this battery |
| thinningdesign | 2 | 3+ | 001e: test_1 null FPR slightly elevated |

---

## Track E (E-DES-MCELL-012)

- **E-DES-MCELL-012:** characterized ✅  
- **GEO-002:** remains **`suitable_with_caveats`** with explicit **k≤2** product guidance (k≤1 conservative).  
- **E-DES-MCELL-011:** no pooled multi-cell claim without `pooling_rule_id`.

---

## Findings

1. **D5-MCELL-FIND-001:** Shared control is subdivided across k cells — typical panel yields ~1 treated market per cell when k≥3.  
2. **D5-MCELL-FIND-002:** Per-cell null FPR and multiple-comparison warnings increase with k.  
3. **D5-MCELL-FIND-003:** k=2 matches D5-POW-001e multi_cell acceptance; k≥3 is research-only without re-characterization.

**Next:** Other instrument OC batteries; not MMM integration.
