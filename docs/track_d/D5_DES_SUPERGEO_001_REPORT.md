# D5-DES-SUPERGEO-001 — Supergeos separate-geometry characterization

**Artifact:** [`archives/D5_DES_SUPERGEO_001_results.json`](archives/D5_DES_SUPERGEO_001_results.json)  
**Harness:** `panel_exp/validation/track_d_d5_des_supergeo_001.py`  
**Lane:** Research (no production, estimator, TrustReport, or MMM changes)

---

## Summary

`supergeos` (`SupergeoModel`) is a **registered, geo-run-unsupported** design that transforms **market-level** input panels into **supergeo aggregate** candidates via KMeans partitioning, combinatorial supergeo generation, and MILP pair selection. It does **not** produce the `control` / `test_*` assignment dict used by tier-1 geo designs and **must not** be evaluated under D5-POW-001e flat SCM+JK semantics.

**Overall verdict:** `requires_implementation_fix_before_oc` (structural MILP scope mismatch) with **Track E status unchanged:** `characterization_required` / `separate_geometry_design`.

---

## What supergeos produces

| Stage | Output |
|-------|--------|
| Input | `pd.DataFrame` — rows = markets/DMAs, columns = time periods |
| Partitioning | KMeans (`n_clusters`, default 5) → cluster index → market indices |
| Combos | All combinations of markets in **largest cluster only**, sizes 2–5 (hardcoded in `run_design`) |
| MILP | Minimize weighted pair objective; binary pair + supergeo selection variables |
| Return | `DataFrame` columns: `Supergeo_1`, `Supergeo_2`, `Total_Sales_1`, `Total_Sales_2` (selected pairs) |

**Not produced:** `dict[str, list[unit_id]]` with `control`, `test_0`, …; per-market treatment labels; multi-cell geometry.

---

## Geometry & estimand

- **Population:** Markets are merged into supergeo aggregates; the estimand is **not** the standard `geo.relative_att_post` market-level ATT without an explicit bridge.
- **Candidate estimands:** (1) contrast between two MILP-selected supergeo sales trajectories; (2) future supergeo-unit ATT after a panel builder defines arms — both require governance before Track B/CalibrationSignal use.
- **OC tensor:** Valid tuple is `supergeos` × `supergeo` × `TBD_instrument` — **not** characterizable on the 001e instrument column today.

---

## Readout compatibility (governed)

| Path | Status |
|------|--------|
| SCM+JK @ market level | **Blocked** |
| SCM+JK @ supergeo-unit level | **Uncharacterized** (no panel builder) |
| TBRRidge / 2-row PowerAnalysis | **Not supergeo geometry** |
| D5-POW-001e | **Excluded** |

---

## Top findings

1. **D5-SUPERGEO-FIND-001:** MILP constraints require every market index `0..N-1` assigned to exactly one supergeo combo, but combos are generated only from the **largest KMeans cluster** (~40% of markets on the battery). Remaining markets are outside combo scope → over-constrained / empty pair output.
2. **D5-SUPERGEO-FIND-002:** Output schema is **pair selection**, not geo experiment assignment — blocks flat unit readout and 001e null FPR tensor.
3. **D5-SUPERGEO-FIND-003:** `run_design` hardcodes combo sizes `[2, 5]` and ignores full-market clustering intent in the module docstring.

On the synthetic battery (`scm_low_signal`, N ∈ {12, 16, 20}), MILP completed but **`n_selected_pairs = 0`** for all sizes.

---

## Track E recommendation

Keep **GEO-003** at **`characterization_required`** (`separate_geometry_design`). Do **not** promote to `suitable` or enable CalibrationSignal ingress. E4-008 remains valid; fixtures may reference this artifact.

**Next lane:** D5-DES-TRIM-001 → D5-MCELL — not MMM integration.
