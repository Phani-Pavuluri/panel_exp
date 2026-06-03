# F-CAT-001 — Registry/catalog cleanup

**Document ID:** F-CAT-001  
**Type:** Implementation contract (Track F backlog)  
**Status:** **complete**  
**Date:** 2026-06-03  
**Depends on:** **F-INF-001** ✅ · **F-GEO-001** ✅

**Prior:** [`F_GEO_001_GEOMETRY_ADAPTER_CONTRACT.md`](F_GEO_001_GEOMETRY_ADAPTER_CONTRACT.md) · [`F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md`](F_INF_001_INTERVAL_SEMANTICS_CONTRACT.md)

---

## Goal

Reconcile estimator, inference, geometry, and instrument **catalog/registry metadata** with F-INF interval semantics and F-GEO geometry adapter rules so labels cannot imply unsupported compatibility, governed uncertainty, CalibrationSignal eligibility, or MMM readiness.

**No estimator or inference behavior changes** — policy helpers and `method_metadata` taxonomy notes only.

---

## Code

| Item | Location |
|------|----------|
| Catalog contract | [`panel_exp/governance/catalog_contract.py`](../panel_exp/governance/catalog_contract.py) |
| Metadata notes | [`panel_exp/method_metadata.py`](../panel_exp/method_metadata.py) |
| Tests | [`tests/governance/test_f_cat_001_catalog_contract.py`](../tests/governance/test_f_cat_001_catalog_contract.py) |

---

## Catalog rules (enforced)

| Rule | Source |
|------|--------|
| No `governed_uncertainty` unless F-INF passes **and** allowlist permits | F-INF-001 — allowlist **empty** |
| No geometry support claim unless F-GEO permits | F-GEO-001 — blocked geometry ⇒ `export_tier=blocked` |
| No CalibrationSignal eligibility unless `NOMINAL_CALIBRATION_ELIGIBLE_CONFIGS` | E5 — **`SCM_UnitJackKnife` only** |
| No MMM readiness | AUDIT-010 — `MMM_READINESS_GOVERNED_ALIASES` empty |
| No pooled multi-cell without `pooling_rule_id` | F-P0-006 / F-GEO |
| No supergeo/trim readout without adapter/estimand bridge | F-GEO |
| Placebo = **inference/falsification**, not estimator catalog name | F-P0-005 |

---

## Taxonomy fixes

| Stale label | Correct catalog semantics |
|-------------|---------------------------|
| TBR = TBRRidge | **Distinct** — `CLASS_TBR_NAMES` vs `TBRRIDGE_CLASS_NAMES` |
| Registry `Bayesian` = BayesianTBR NUTS MCMC | **INV-015** — registry JAX bands only |
| Placebo as estimator | **Forbidden** in `estimator_catalog`; inference mode documents falsification layer |
| Conformal callable = governed uncertainty | **F-INF** — `callable_unverified` / `blocked_invalid`; never governed |
| Kfold vs TimeSeriesKfold | Distinct notes in `inference_mode_catalog` |
| UnitJackKnife vs JKP | Distinct assumptions documented in metadata |
| Track B `signal_id` on non-SCM aliases | **Adapter metadata only** — `track_b_alias_governance()` overlay |

---

## Canonical combo records

`canonical_catalog_combo_records()` is the authoritative cross-product overlay for Track F combos (TBR aggregate, TBRRidge unit, AugSynth, SCM+JK, SCM+Placebo, blocked geometries). Each record carries:

- `interval_semantics_tier` (F-INF)
- `geometry_tier` (F-GEO)
- `export_tier` / `catalog_readiness`
- `catalog_layer` (`estimator_readout` vs `inference_falsification` for Placebo)
- `calibration_signal_eligible` / `mmm_ready` / `governed_uncertainty_claim` (all false except SCM+JK alias flag for policy documentation)

`assert_catalog_consistency()` runs estimator catalog, inference mode catalog, canonical record, and optional Track B signal audits.

---

## Stop condition (met)

| Criterion | Status |
|-----------|--------|
| Catalog reflects F-INF + F-GEO | ✅ |
| Tests block stale alias / overclaim patterns | ✅ |
| No MMM / CalibrationSignal expansion / promotion | ✅ |
| No estimator/inference rewrites | ✅ |

**Next decision point:** **F-BACKLOG-001** implementation roadmap closeout **or** **F-INF-003** band sign fix (implementation).

---

*F-CAT-001 v1.0.0 — registry metadata aligned with contract stack; tests prevent misleading readiness claims.*
