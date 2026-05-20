# panel_exp

**Panel data modeling and geo-experimentation** — a Python toolkit for designing geo-based experiments, estimating causal effects on panel data, and quantifying uncertainty.

The package is organized around three areas:

| Area | What it covers |
|------|----------------|
| **Design** | Geo experiment design, randomization (`BalancedRandomization`, `CompleteRandomization`, stratified, thinning, rerandomization, greedy matching), power / MDE, validation gates |
| **Methods** | Synthetic control / SCM, TBR, Bayesian regression, multi-task GP, diff-in-diff, synthetic DID, triply robust estimators |
| **Inference** | K-fold and residual-based procedures, placebos, conformal methods, unit jackknife |

**Python:** 3.10+ (see `pyproject.toml` for pinned dependencies).

**Default uncertainty:** Estimators use `alpha=0.05` (95% intervals) unless you set `alpha` explicitly.

---

## Documentation

- **Hosted docs:** Pre-built HTML under `gh-pages/` (open `gh-pages/index.html` locally).
- **User guide source:** `gh-pages/_sources/user_guide.md.txt`
- **Uncertainty notes:** `panel_exp/inference/uncertainty.md`

There is no separate `docs/` Sphinx tree in this repository; use `gh-pages/` or build docs from the published site artifacts.

---

## Install locally (development)

```bash
git clone <repository-url>
cd panel_exp
poetry install
poetry run pytest
```

---

## Quickstart

```python
import pandas as pd
from panel_exp import (
    PanelDataset,
    long_df_to_paneldataset,
    BalancedRandomization,
    SyntheticControl,
    DesignSpec,
    DesignMethod,
    TimePeriod,
)

long_df = pd.read_csv("kansas_parsed.csv")
panel_data = long_df_to_paneldataset(
    long_df, "year_qtr", "state", "lngdp", ["Kansas"], 2012
)

# Volume-balanced geo assignment (not Bernoulli randomization)
design = BalancedRandomization(treatment_probability=0.3, random_state=42)
assignment = design.assign(panel_data=panel_data, n_test_grps=1)

scm = SyntheticControl(inference="Kfold", alpha=0.05)
scm.run_analysis(panel_data)
scm.plot()
```

### Experiment specification

Use `DesignSpec` / `ExperimentSpec` for explicit contracts (periods, alpha, interference assumption, constraints):

```python
from panel_exp import DesignSpec, DesignMethod, InterferenceAssumption, TimePeriod

spec = DesignSpec(
    experiment_id="fy26_us_geo",
    outcome_column="conversions",
    unit_column="geo",
    time_column="date",
    pre_period=TimePeriod(0, 90),
    experiment_period=TimePeriod(90, 120),
    design_method=DesignMethod.BALANCED_RANDOMIZATION,
    random_state=42,
    alpha=0.05,
    interference=InterferenceAssumption.UNKNOWN,
)
```

### Geo experiment orchestration

`GeoExperimentDesign` supports: `greedy_match_markets`, `ThinningDesign`, `BalancedRandomization`, `CompleteRandomization`, `StratifiedRandomization` (via rerandomization). **QuickBlock** and **MatchedPair** must be called directly — not through `run_design`.

---

## Randomization naming

| Class | Behavior |
|-------|----------|
| `BalancedRandomization` | KPI volume–balanced heuristic (shuffled units, greedy share targets) |
| `CompleteRandomization` | Bernoulli assignment of free units with whitelist/blacklist enforcement |
| `StratifiedRandomization` | Strata by pre-period mean KPI, balanced within strata |

---

## Power / MDE

`PowerAnalysis` uses **simulation**: sliding train/test windows, injected effects, and CI coverage vs a power threshold. Reported MDE is **not** a closed-form analytic MDE. Pass `random_state` for reproducibility.

---

## Tests

```bash
poetry run pytest
```

---

## Project layout

- `panel_exp/` — library (`design`, `methods`, `inference`, `spec`, `evidence`, …)
- `tests/` — pytest (`tests/fixtures/` for synthetic data)
- `gh-pages/` — published documentation HTML
- `scripts/` — diagnostic scripts (not part of the wheel API)
- `examples/` — notebooks (some reference dev-only modules)

---

## Status

Under active development. Version in `pyproject.toml` and `panel_exp.__version__` is the source of truth.

**Not installable from notebooks:** `panel_exp.pretest_analysis` is referenced in some example notebooks but is not shipped in the wheel; use `PowerAnalysis` and `GeoExperimentDesign` instead.
