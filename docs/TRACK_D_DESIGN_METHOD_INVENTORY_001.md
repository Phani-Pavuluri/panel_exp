# Track D — Design method inventory 001 (code-derived)

**Document ID:** TRACK-D-DESIGN-INVENTORY-001  
**Type:** Research-lane inventory (pre D5-POW-001e)  
**Status:** complete @ commit `e3e6aeb`  
**Artifact:** [`track_d/archives/DESIGN_INVENTORY_001_results.json`](track_d/archives/DESIGN_INVENTORY_001_results.json)  
**Generator:** `panel_exp/validation/track_d_design_inventory_001.py`  
**Governance update:** [`ROADMAP_DESIGN_READOUT_UPDATE_001.md`](ROADMAP_DESIGN_READOUT_UPDATE_001.md)

---

## Purpose

Enumerate **actual** design/assignment implementations in `panel_exp/design/` from code (registry + source). Classify eligibility for **D5-POW-001e** under the **SCM+UnitJackKnife reference null-monitor branch**—not as universal platform validation.

**D5-POW-001e:** **not started** (scoped in ROADMAP-DESIGN-READOUT-UPDATE-001).

---

## Discovery summary (code-grounded)

| Category | Count | Notes |
|----------|-------|--------|
| Registry entries | 9 | `get_design_registry().list_names()` |
| Geo-run supported | 5 | Matches `LEGACY_GEO_RUN_DESIGN_SUPPORTED` |
| Production wrapper | 1 | `Rerandomization` in `assign.py` — **not** a registry row |
| Confirmed for D5-POW-001e | 6 | 5 geo bases + `rerandomization_wrapper` |

**Not found:** `multi_cell_multi_treated` as a class. **Multi-cell** = geometry mode: `n_test_grps > 1` on tier-1 geo methods.

### Geo-run-supported registry methods

- `greedy_match_markets`  
- `thinningdesign`  
- `balancedrandomization`  
- `completerandomization`  
- `stratifiedrandomization`  

### Production orchestration

`GeoExperimentDesign.create_design()` → `Rerandomization(base_randomizer_cls=…)` → base `assign()`.

---

## SCM+UnitJackKnife framing (not universal readout)

SCM+UnitJackKnife is the **reference readout** for fixed-window **unit-level null-monitor OC** in D5-POW-001e. It is **not**:

- the universal GeoX readout  
- a platform-wide power/MDE instrument  
- a lift-detection instrument  

Other measurement instruments (TBRRidge+KFold, BRB, DID+bootstrap, AugSynth, placebo, geo `PowerAnalysis`) require **separate** OC batteries before Track E promotion.

---

## Confirmed for D5-POW-001e (design methods)

| method_id | Notes |
|-----------|--------|
| `greedy_match_markets` | Bare baseline; pre-period slice in assign |
| `rerandomization_wrapper` | Production `Rerandomization(greedy)` — **must** compare to bare greedy |
| `completerandomization` | Bernoulli + constraints |
| `balancedrandomization` | Volume-balanced |
| `stratifiedrandomization` | Strata + volume balance |
| `thinningdesign` | Kernel thinning; geo-supported |

**001e question:** Under fixed-window unit-level SCM+JK reference readout, which methods and geometry modes have acceptable null behavior?

**Harness:** unit panel, fixed pre/post (001d), correct null intervals (001b), ≥2 control units, research lane only.

---

## Multi-cell design geometry

Multi-cell = **control vs test_0 / test_1 / … / test_k** (shared control), via **`n_test_grps > 1`** — **not** a separate method.

001e: limited multi_cell runs where safe; **per-cell** metrics only; **no pooled** multi-cell null FPR or lift claims without a governed pooling rule.

See ROADMAP-DESIGN-READOUT-UPDATE-001 §5–6 for required `E-DES-MCELL-*` diagnostics.

---

## Separate-semantics paths (in roadmap, not 001e)

### supergeos

| Field | Value |
|-------|--------|
| Class / registry | `SupergeoModel` / `supergeos` |
| Status | **separate_geometry_design** / characterization_required |
| 001e | **Excluded** — supergeo clusters / MILP pairing; not flat unit dict for SCM+JK |
| Follow-up | **D5-DES-SUPERGEO-001** |

### trimmedmatch

| Field | Value |
|-------|--------|
| Class / registry | `TrimmedMatchDesign` / `trimmedmatch` |
| Status | **separate_population_design** / characterization_required |
| 001e | **Excluded** — Tp/Te split, pair trim, own power semantics |
| Follow-up | **D5-DES-TRIM-001** |

### tier_3_legacy_or_doc_only

`quickblock`, `matchedpair` — registered; not `geo_run_supported`; legacy APIs unless later shown on production geo path.

---

## Tier summary (D5-POW-001e buckets)

| Bucket | Members |
|--------|---------|
| **tier_1_include_in_d5_pow_001e** | Six confirmed methods above |
| **tier_2_separate_characterization** | `trimmedmatch` |
| **blocked_for_scm_jk_oc** (001e contract) | `supergeos` |
| **tier_3_legacy_or_doc_only** | `quickblock`, `matchedpair` |

---

## Entrypoints (production geo path)

```
GeoExperimentDesign.run_design()
  → registry.run → run_geo_experiment_design()
       → Rerandomization.assign → base randomizer
       → validate_design (optional)
       → _calculate_sensitivity_metrics  # 2-row agg + PowerAnalysis (diagnostic; ≠ 001e readout)
```

---

## Related D5 artifacts

| Artifact | Relevance |
|----------|-----------|
| D5-POW-001a | TBRRidge+Kfold vs SCM+JK; optimistic_proxy |
| D5-POW-001b | SCM+JK null-monitor semantics |
| D5-POW-001c | 2-row aggregation narrow_diagnostics_only |
| D5-POW-001d | Fixed windows preferred; E-DES-WIN-* |

---

*DESIGN-INVENTORY-001 — research lane; no production changes.*
