# F-INF-002 — TBRRidge multi-treated inference interface fix

**Status:** Complete (interface validation). **OC:** `requires_OC_after_fix` — D5-INST-TBRRIDGE-003 or equivalent for A16, A18, A21.

**Scope:** AUDIT-010 tuples **A16** (TBRRidge + UnitJackKnife), **A18** (TBRRidge + Conformal), **A21** (TBRRidge + JKP) on 001e-style unit panels (multi-treated, pooled counterfactual).

**Not in scope:** Governed uncertainty, CalibrationSignal expansion, MMM ingress, promotion.

---

## Root cause (D5-INST-TBRRIDGE-002)

TBRRidge fits a **single pooled counterfactual** per time (`y_hat` shape `(n_time,)`), while treated outcomes remain **per unit** (`y` shape `(n_time, n_treated)`). After NumPy 2.x, implicit broadcast `(n_time, n_treated) - (n_time,)` fails. Failures surfaced in:

1. `treatment_window_point_effect` metadata (`sync_inference_metadata`)
2. JKP inner loop residual construction
3. Conformal null-grid calibration (pooled-sum residual scale blew up null range → all-NaN bounds)
4. `apply_effect_bounds_to_results` when effect bounds are 2-D and `y_hat` is 1-D

This is **not** unsupported geometry (F-GEO-001 unit-panel remains valid with caveats). It is a **readout alignment** issue, analogous to Kfold’s `_aggregate_treatment_residuals` pooled semantics.

---

## Fix (narrow)

| Layer | Change |
|-------|--------|
| `panel_exp/inference/_impact_common.py` | `is_tbrridge_multi_treated`, `prepare_y_and_y_hat` readout tag `tbrridge_pooled_counterfactual_multi_treated`, `treatment_window_residuals`, `apply_jkp_bounds_to_results`, 2-D effect + 1-D `y_hat` branch in `apply_effect_bounds_to_results` |
| `panel_exp/inference/_metadata.py` | Point-effect metadata uses `treatment_window_residuals` |
| `panel_exp/inference/unit_jackknife.py` | `_jkp_residual_matrix` — explicit `y_hat[:, None]` broadcast |
| `panel_exp/inference/modes/impl.py` | Per-unit JK bands; JKP 2-D bounds via `apply_jkp_bounds_to_results`; Conformal null scale from per-unit vs pooled CF residuals |

**Estimand policy:** Multi-treated TBRRidge inference uses **pooled counterfactual + per-unit outcome paths** for intervals. We do **not** claim independent per-unit SCM counterfactuals. Same family as existing Kfold multi-treated handling.

---

## Stop condition (this item)

| Tuple | Post F-INF-002 | OC |
|-------|----------------|-----|
| A16 UnitJackKnife | Structurally valid; `callable_unverified_interval_semantics` | **Pending** targeted OC |
| A18 Conformal | Structurally valid; `callable_unverified_interval_semantics` | **Pending** targeted OC |
| A21 JKP | Structurally valid; `callable_unverified_interval_semantics` | **Pending** targeted OC |

- **Not** `blocked_interface`
- **Not** `governed_uncertainty`
- **Not** `characterized_restricted` until OC battery passes (mirror A05/A19 POSTFIX pattern)

---

## Tests

`tests/governance/test_f_inf_002_tbrridge_interface.py` — 001e multi-treated panel: no broadcast failure, finite ordered post-window bounds, F-INF-001 not weakened.

Governance registry: `TRACK_F_KNOWN_INTERVAL_DISPOSITIONS` and F-GEO TBRRidge JK/JKP/Conformal unit-panel → supported with caveats / callable unverified.

---

## Next authorized step

**D5-INST-TBRRIDGE-003** (or equivalent): targeted OC for A16/A18/A21 only after this fix. Do not rerun full P2 battery unless governance PR requires it.
