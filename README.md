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

## Current package status (code truth)

### Geo design orchestration

| Via `GeoExperimentDesign.run_design` | Lower-level only (registered, not geo-run supported) |
|--------------------------------------|------------------------------------------------------|
| `greedy_match_markets` | `QuickBlock` |
| `ThinningDesign` | `MatchedPair` |
| `BalancedRandomization` | `TrimmedMatchDesign` |
| `CompleteRandomization` | `SupergeoModel` (`supergeos`) |
| `StratifiedRandomization` | |

Unsupported designs raise `ValueError` at `GeoExperimentDesign` construction if selected as `base_randomizer_cls`. Use the design class `.assign(...)` API directly for lower-level tools.

Registry helpers: `get_design_registry()`, `GEO_RUN_DESIGN_SUPPORTED`.

### Evidence and readouts

- **`DesignEvidence` / `ExperimentEvidence` / `InferenceEvidence`** — immutable-friendly artifacts with `spec_hash`, `assignment_hash`, `input_structure_hash`, warnings, errors, `validation_summary`.
- **Experiment card** — `build_experiment_card(evidence)` and `attach_experiment_card_markdown(artifacts, evidence)` for human-readable markdown (does not change estimates).

### Estimator maturity (conservative)

- **`EstimatorMaturity`** and **`get_method_registry()`** — operational readiness labels, not statistical superiority.
- No estimator or inference mode is rated **`production_safe`** in the current catalog; smoke/recovery tests alone do not promote maturity.

### Inference interval semantics

Path bands in `results` are labeled explicitly: `confidence_interval`, `credible_interval`, `conformal_interval`, `placebo_band`, or `unavailable`. Placebo outputs are **placebo bands**, not generic confidence intervals. Point-estimate-only runs report `unavailable`.

### Power / MDE

`PowerAnalysis` is **simulation-based** (coverage vs injected effects), not a closed-form analytic MDE. Pass `random_state` for reproducibility; parallel `n_jobs` behavior depends on the backing estimator.

### Interference

`InterferenceAssumption`: `unknown`, `no_interference`, `partial_interference`. Design validation warns when interference is unknown. The package does **not** estimate spillovers automatically.

### Recovery validation (diagnostic)

`panel_exp.validation.RecoveryRunner` and `validation_metadata` on analysis results summarize synthetic recovery metrics (bias, coverage, FPR, power). These are **diagnostic** and do not auto-upgrade maturity ratings.

### Not shipped

- `panel_exp.pretest_analysis` — referenced in some dev notebooks only.
- `panel_exp.util` — removed; import `standardize` from `panel_exp.methods.bayesian_regression`.

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

See **Current package status** above for the geo-supported allowlist vs registered-only designs.

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
