# Design golden fixtures

Assignment JSON baselines for registry equivalence tests.

## Format

Each `assignment_*.json` file contains:

- **`group_labels`**: ordered assignment bucket names (e.g. `control`, `test_0`)
- **`assignments`**: map from each label to sorted unit id lists

Registered designs in the registry are not necessarily supported by
`GeoExperimentDesign`; only designs in `GEO_RUN_DESIGN_SUPPORTED` may be used
via `run_design`.

## Regenerate

```bash
MPLCONFIGDIR=/tmp/mpl .venv/bin/python scripts/regenerate_design_golden.py
```

## Requirements

- `seed=42`, panel `12 x 50` from `tests/design_registry_helpers.make_geo_panel`
- `max_iter=8` on rerandomization wrapper
- `random_state=42`
- `n_test_grps=1` → group labels `control`, `test_0`

Power/MDE numeric goldens are not committed (slow / environment-sensitive);
pipeline structure and ordering are tested in `test_design_registry_equivalence.py`.
