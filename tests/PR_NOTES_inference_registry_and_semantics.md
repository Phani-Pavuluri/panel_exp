# PR notes: inference registry + interval semantics

Commit `a40ebe3` bundles two related but distinct changes. Review and release notes should treat them separately even though they land together.

---

## Architecture (refactor)

**ImpactAnalyzer inference dispatch moved to a registry.**

- `panel_exp.inference.registry.InferenceRegistry` registers modes by name/alias with declarative metadata (`output_keys`, `interval_keys`, `path_interval_type`, failure behavior).
- `ImpactAnalyzer.run_analysis()` delegates to `get_inference_registry().run(...)` instead of a monolithic `if/elif` chain in `impact.py`.
- Mode implementations live in `panel_exp/inference/modes/impl.py` (migrated from legacy `impact.py` branches).
- Golden equivalence tests: `tests/test_inference_registry_equivalence.py`, fixtures under `tests/fixtures/inference_golden/`.

**Intent:** Same inference math and defaults; centralized dispatch, easier to add modes and test parity.

---

## Semantics (metadata only)

**Interval outputs now carry explicit `interval_type` metadata.**

- `InferenceResult` + `IntervalType` enum: `confidence_interval`, `credible_interval`, `conformal_interval`, `placebo_band`, `unavailable`.
- `path_interval_type` describes `results['y_lower']` / `results['y_upper']`; `effect_interval_type` used when scalar effect CI differs (e.g. placebo inversion).
- `sync_inference_metadata()` runs after each mode; `attach_to_results()` sets `interval_type`, `intervals_available`, and nested `inference_metadata` (alpha, confidence_level, labels).
- Placebo: path bands labeled `placebo_band`; inversion cumulative bounds labeled `confidence_interval` when finite—not mislabeled as generic CIs on the path.

**Intent:** Honest reporting; no fake precision. Does not alter how intervals are computed.

---

## Behavior (unchanged)

- **`y_hat`, `y_lower`, `y_upper` numeric values unchanged** (golden npz equivalence).
- Estimator calculations, conformal null grid, BRB/Kfold/placebo algorithms, and inference defaults unchanged.
- Point-estimate mode: `results` keys remain `{times, y, y_hat}` only; semantics live on `analyzer.inference_result`.

---

## Testing

- `tests/test_inference_result_semantics.py` — typing and placebo band vs CI distinction.
- `tests/test_inference_registry.py`, `tests/test_inference_registry_equivalence.py` — dispatch and golden parity.
- Assignment hardening suite unaffected; see `tests/REGRESSION_NOTE_assignment_hardening.md` for full-suite boundary.

## Suggested PR title

`Inference registry dispatch + explicit interval semantics`

## Suggested PR summary (paste into GitHub)

### Architecture
- ImpactAnalyzer inference dispatch moved to registry.

### Semantics
- Interval outputs now carry explicit `interval_type` metadata.

### Behavior
- `y_hat`, `y_lower`, `y_upper` unchanged.
