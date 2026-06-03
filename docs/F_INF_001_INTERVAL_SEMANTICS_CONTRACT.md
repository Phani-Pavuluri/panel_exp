# F-INF-001 — Interval semantics and inference wrapper contract

**Document ID:** F-INF-001  
**Type:** Implementation contract (Track F backlog)  
**Status:** **complete**  
**Date:** 2026-06-03  
**Lane:** Governance / validation — no production inference redesign

**Prior:** [`TRACK_F_P2_CLOSEOUT_001.md`](TRACK_F_P2_CLOSEOUT_001.md) · D5-INST-TBRRIDGE-002 · D5-INST-AUGSYNTH-003

---

## Goal

Define a governed interval semantics contract so **callable inference wrappers cannot be treated as governed uncertainty** unless band semantics are valid (positive width, ordered bounds, declared type/units/estimand/geometry) and explicitly allowlisted.

---

## Code

| Item | Location |
|------|----------|
| Contract module | [`panel_exp/governance/interval_semantics_contract.py`](../panel_exp/governance/interval_semantics_contract.py) |
| Tests | [`tests/governance/test_f_inf_001_interval_semantics.py`](../tests/governance/test_f_inf_001_interval_semantics.py) |

---

## Classification tiers

| Tier | Meaning |
|------|---------|
| `governed_uncertainty` | Semantics pass **and** on `GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST` (currently **empty**) |
| `diagnostic_interval_only` | Callable; semantically valid or policy-restricted diagnostic (Kfold, JK, BRB, etc.) |
| `callable_unverified_interval_semantics` | Callable; null FPR / metadata gaps / behavioral semantics fail |
| `blocked_invalid_interval` | Callable but structurally invalid band (negative HW, inverted bounds) |
| `blocked_interface` | Inference did not complete (interface / policy block) |

**Separation enforced:**

| Concept | Rule |
|---------|------|
| Callable inference | `callable=True` and no `blocked_interface_reason` |
| Diagnostic interval | Valid or policy-restricted; **not** governed export |
| Ungoverned / unverified | Callable with failed semantics checks |
| Governed uncertainty | Requires allowlist + passing checks — **no Track F combo qualifies today** |

---

## Validation helpers

| Check | Issue code |
|-------|------------|
| Negative mean half-width | `negative_half_width` |
| `y_lower > y_upper` | `inverted_lower_upper_bounds` |
| Null interval-exclusion FPR ≥ 0.35 | `null_interval_exclusion_fpr` |
| Missing `path_interval_type` | `missing_interval_type` |
| Missing `interval_units` | `missing_interval_units` |
| Missing / unknown `target_estimand` | `missing_estimand_binding` |
| Missing `geometry_mode` | `missing_geometry_binding` |
| Interface block | `blocked_interface` |

**Non-goals (explicit):** no `abs()` on half-width; no silent swap of bounds; no upgrading callable output to governed uncertainty.

---

## Track F P2 mappings (registry)

| Combo | Expected classification |
|-------|-------------------------|
| TBRRidge + TimeSeriesKfold + single_cell | `callable_unverified_interval_semantics` |
| AugSynthCVXPY + Conformal + single_cell | `callable_unverified_interval_semantics` (live negative HW → `blocked_invalid_interval`) |
| TBR + JKP + aggregate_two_series | `callable_unverified_interval_semantics` |
| TBRRidge + UnitJackKnife / Conformal / JKP + single_cell | `blocked_interface` |
| TBRRidge + Kfold / BRB + single_cell | `diagnostic_interval_only` |
| AugSynthCVXPY + UnitJackKnife / Kfold + single_cell | `diagnostic_interval_only` |

---

## Stop condition (met)

| Criterion | Status |
|-----------|--------|
| Shared contract module | ✅ |
| Classification tiers defined | ✅ |
| Validation helpers + tests | ✅ |
| Callable invalid paths cannot become governed | ✅ |
| Track F P2 findings mapped | ✅ |
| No MMM / CalibrationSignal / promotion | ✅ |

**Next lane:** **F-GEO-001** geometry adapter hardening · then **F-CAT-001** registry/catalog cleanup.

---

*F-INF-001 v1.0.0 — contract-first; fix intervals in implementation lanes, not by silent reclassification.*
