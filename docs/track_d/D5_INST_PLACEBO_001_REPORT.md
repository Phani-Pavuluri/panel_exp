# D5-INST-PLACEBO-001 — SCM placebo geometry characterization

**Artifact:** [`archives/D5_INST_PLACEBO_001_results.json`](archives/D5_INST_PLACEBO_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_inst_placebo_001.py`  
**Lane:** Research — no promotion, no CalibrationSignal ingress

---

## Summary

Under **greedy_match_markets**, fixed windows (train=28, test=8), and `scm_low_signal` (n_geos=16), **SCM+Placebo** remains a **geometry-limited diagnostic** instrument. **Single-treated** panels run with **100%** `placebo_band` path semantics; **multi-treated** assignment (~5 treated in test_0) is **100% blocked** before inference (`placebo_in_space_single_treated_only`). **Multi-cell k=2** is supported only as **per-cell single-treated** runs — no pooled placebo.

**Overall verdict:** `remain_diagnostic_only_no_promotion`

---

## Geometry matrix

| Geometry case | Treated units | Feasibility | Failure mode |
|---------------|---------------|-------------|--------------|
| **single_treated_forced** | 1 | **100%** | Supported |
| **multi_treated_natural** | ~4.9 mean | **0%** | Blocked — implementation requires exactly one treated unit |
| **multi_cell_k2_per_cell_single** | 1 per cell | **100%** (28/28 cell-runs) | Per-cell only; do not pool |

---

## Key metrics (n_mc=14, null effect)

| Case | Control donors | Placebo pseudo-treated | Mean placebo p-value | placebo_band rate | Inversion CI excludes zero |
|------|----------------|------------------------|----------------------|-------------------|----------------------------|
| Single-treated | ~7.9 | ~7.9 | ~0.61 | **1.0** | **0.0** |
| Multi-treated natural | ~7.9 | n/a (blocked) | n/a | 0.0 | n/a |
| Multi-cell k=2 (per cell) | ~7.8 | ~7.8 | ~0.62 | **1.0** | **0.0** |

**SCM+JK null-monitor context (single-treated only):** mean interval-exclusion FPR ~**7%** vs placebo inversion exclusion **0%** on this battery — **not comparable estimands** (same lesson as D5-INST-TBRRIDGE-001).

---

## Implementation limits (confirmed)

1. `panel_exp/inference/placebo.py` — `placebo()` raises when `len(treated_units) != 1`.
2. Track B registry — `instrument_geometry_scope="single_treated_only"` for `SCM_Placebo`.
3. Harness pre-check mirrors implementation for multi-treated natural assignment (no silent partial run).

---

## Track E status (unchanged)

| Card | Status |
|------|--------|
| **INST-006** single-treated | **`diagnostic_only`** — TrustReport null-reference; not lift |
| **INST-006** multi-treated default | **`blocked`** — E4-006 fixture remains valid |
| **CalibrationSignal / MMM** | **Excluded** |

**Narrower wording:** Placebo output is **placebo_band** semantics only; inversion CI is a separate display layer — never treat as governed lift interval or JK-comparable detection.

---

## Governance reminders

- Do **not** promote placebo p-values or bands to lift evidence or MMM ingress.
- Do **not** generalize single-treated placebo behavior to multi-treated geo tests.
- Do **not** pool placebo diagnostics across concurrent cells (MCELL k≤2 discipline applies).
- Compare to SCM+JK null-monitor **as context only** — different estimand and interval semantics.

---

## Findings

1. **D5-PLAC-FIND-001:** Multi-treated greedy assignment (~5 units) is incompatible with placebo-in-space; block is deterministic.
2. **D5-PLAC-FIND-002:** `placebo_band` is always emitted on feasible runs; not a confidence interval for lift.
3. **D5-PLAC-FIND-003:** k=2 multi-cell requires per-cell single-treated restriction; pooling pseudo-treated counts is invalid.

**Next:** D5-INST-DID-001 → AUDIT-010 (not MMM).
