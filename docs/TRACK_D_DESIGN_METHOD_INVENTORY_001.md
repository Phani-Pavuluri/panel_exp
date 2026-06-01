# Track D — Design method inventory 001 (code-derived)

**Document ID:** TRACK-D-DESIGN-INVENTORY-001  
**Type:** Research-lane inventory (pre D5-POW-001e)  
**Status:** complete  
**Artifact:** [`track_d/archives/DESIGN_INVENTORY_001_results.json`](track_d/archives/DESIGN_INVENTORY_001_results.json)  
**Generator:** `panel_exp/validation/track_d_design_inventory_001.py`

---

## Purpose

Enumerate **actual** design/assignment implementations in `panel_exp/design/` and classify which may enter **D5-POW-001e** (null FPR at scale on unit-level SCM+UnitJackKnife with fixed windows). Names come from the **registry and source**, not prior roadmap placeholders.

---

## Discovery summary

| Category | Count | Notes |
|----------|-------|--------|
| Registry entries | 9 | `get_design_registry().list_names()` |
| Geo-run supported | 5 | `geo_run_supported=True`; matches `LEGACY_GEO_RUN_DESIGN_SUPPORTED` |
| Production orchestration wrapper | 1 | `Rerandomization` (not a registry row) |
| Confirmed for D5-POW-001e | 6 | 5 geo bases + rerandomization wrapper |

There is **no** separate class named `multi_cell_multi_treated`. Multi-cell designs use `n_test_grps > 1` on geo tier-1 methods.

---

## Confirmed for D5-POW-001e

| method_id | Class | Pre-period matching in assign | SCM+JK |
|-----------|-------|------------------------------|--------|
| `greedy_match_markets` | `greedy_match_markets` | **Yes** (slices wide) | ✅ |
| `rerandomization_wrapper` | `Rerandomization` | Via base + imbalance on pre slice | ✅ |
| `completerandomization` | `CompleteRandomization` | No (full wide for assign) | ✅ |
| `balancedrandomization` | `BalancedRandomization` | No | ✅ |
| `stratifiedrandomization` | `StratifiedRandomization` | No | ✅ |
| `thinningdesign` | `ThinningDesign` | No | ✅ |

**001e harness contract** (from D5-POW-001b/d): unit panel, fixed pre/post windows, `pre_treatment_period=TimePeriod(0, train_length-1)`, correct interval null FPR semantics, ≥2 control units.

**Production note:** `GeoExperimentDesign` default is `Rerandomization(greedy_match_markets)`, not bare greedy. 001e should test **both** bare greedy (D5 baseline) and rerandomization+greedy.

---

## Tier 2 — separate characterization (not 001e null FPR)

| method_id | Reason |
|-----------|--------|
| `trimmedmatch` | Pair-trimmed design; `run_design()` API; classical power semantics |

---

## Blocked for SCM+JK OC

| method_id | Reason |
|-----------|--------|
| `supergeos` | Supergeo aggregation; no `control`/`test_*` unit dict |

---

## Tier 3 — legacy / doc only

| method_id | Reason |
|-----------|--------|
| `quickblock` | Registered; not `geo_run_supported`; `assign_all` API |
| `matchedpair` | `assign(X)` matrix API; not geo pipeline |

---

## Entrypoints (production geo path)

```
GeoExperimentDesign.run_design()
  → get_design_registry().run(base_randomizer_cls, geo)
  → run_geo_experiment_design()
       → create_design().assign(...)   # Rerandomization → base
       → validate_design (optional)
       → _calculate_sensitivity_metrics  # 2-row agg + PowerAnalysis (not 001e readout)
```

Direct assignment (D5 harness style):

```python
greedy_match_markets(...).assign(
    panel_data,
    pre_treatment_period=TimePeriod(0, train_length - 1),
    n_test_grps=1,
)
```

---

## Track E forward

Use **E-POW-WIN-001–007** (from D5-POW-001d) plus per-method null FPR from 001e when building E1/E2 suitability cards. Do not audit every design algorithm now—expand only when D5/E evidence requires.

---

## Related D5 artifacts

| Artifact | Relevance |
|----------|-----------|
| D5-POW-001c | Aggregation not valid proxy |
| D5-POW-001d | Fixed windows preferred |
| D5-POW-001b | SCM+JK null-monitor semantics |

---

*DESIGN-INVENTORY-001 — research lane; no production changes.*
