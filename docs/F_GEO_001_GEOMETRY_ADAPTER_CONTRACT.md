# F-GEO-001 — Geometry adapter contract

**Document ID:** F-GEO-001  
**Type:** Implementation contract (Track F backlog)  
**Status:** **complete**  
**Date:** 2026-06-03  
**Depends on:** **F-INF-001** ✅ — interval semantics never override geometry blocking

**Prior:** [`TRACK_F_P2_CLOSEOUT_001.md`](TRACK_F_P2_CLOSEOUT_001.md) · [`F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md`](F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md)

---

## Goal

Define governed geometry adapter rules so estimator × inference readouts cannot be used on unsupported unit, aggregate, multi-cell, supergeo, or trimmed-population geometries — **even when the path is callable or intervals look valid**.

---

## Code

| Item | Location |
|------|----------|
| Contract module | [`panel_exp/governance/geometry_adapter_contract.py`](../panel_exp/governance/geometry_adapter_contract.py) |
| Tests | [`tests/governance/test_f_geo_001_geometry_adapter_contract.py`](../tests/governance/test_f_geo_001_geometry_adapter_contract.py) |

---

## Governed geometry types

| Type | Role |
|------|------|
| `unit_panel` | Unit-level donors/treated (001e, TBRRidge, SCM, AugSynth) |
| `aggregate_two_series_1x1` | Class TBR 1 treated + 1 control row |
| `aggregate_two_series_per_cell` | Per-cell 1×1 aggregate (no pooling) |
| `multi_cell_per_cell` | k≥2 cells analyzed separately |
| `pooled_multi_cell` | Requires `pooling_rule_id` |
| `supergeo_unit` | Requires `supergeo_adapter_id` |
| `trimmed_population` | Requires `trim_estimand_bridge_id` |

---

## Classification outputs

| Classification | Meaning |
|----------------|---------|
| `geometry_supported` | Geometry valid for readout family |
| `geometry_supported_with_caveats` | Valid but restricted / diagnostic / per-cell only |
| `blocked_geometry` | Wrong geometry for estimator (e.g. TBR on unit_panel) |
| `blocked_missing_pooling_rule` | Pooled multi-cell without `pooling_rule_id` |
| `blocked_missing_estimand_bridge` | Trimmed population without bridge |
| `blocked_missing_adapter` | Supergeo without adapter |
| `blocked_unsupported_inference_geometry` | Inference/geometry combo not supported (e.g. placebo multi-treated) |

**Export tiers:** `restricted` · `diagnostic_only` · `blocked` · `future_calibration_signal_eligible` (SCM+JK unit null-monitor policy slot — no expansion authorized)

---

## Readout family rules (summary)

| Family | Geometry rule |
|--------|-----------------|
| **Class TBR** | `aggregate_two_series_1x1` only; unit_panel **blocked** |
| **TBR per-cell** | `aggregate_two_series_per_cell` — restricted; no pooling |
| **TBRRidge** | `unit_panel` restricted diagnostics only |
| **SCM** | `unit_panel` / `multi_cell_per_cell` diagnostic; supergeo/trim **blocked** without bridge/adapter |
| **AugSynthCVXPY** | `unit_panel` / `multi_cell_per_cell` restricted diagnostic |
| **DID** | Restricted/deferred — estimand policy separate (DEF-003) |
| **Placebo** | Inference/falsification; single-treated only |
| **Multi-cell** | Per-cell only unless governed `pooling_rule_id` |

---

## F-INF interaction (binding)

`classify_combined_readout()` applies **geometry first**:

> **F-INF interval status does not override geometry blocking.**  
> A method can produce valid-looking intervals and still be **blocked** on wrong geometry.

Interval band sign fixes remain **F-INF-003** — out of scope for F-GEO-001.

---

## Stop condition (met)

| Criterion | Status |
|-----------|--------|
| Geometry types + classifications defined | ✅ |
| Readout family rules encoded | ✅ |
| Tests: callable ≠ geometry support | ✅ |
| Tests: interval cannot rescue geometry block | ✅ |
| No MMM / CalibrationSignal / promotion | ✅ |

**Next lane:** ~~**F-BACKLOG-001**~~ ✅ · **F-INF-003** (implementation).

---

*F-GEO-001 v1.0.0 — geometry blocks before interval semantics; no silent estimand equivalence.*
