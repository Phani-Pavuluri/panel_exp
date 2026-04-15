# panel_exp

**Panel data modeling and geo-experimentation** — a Python toolkit for designing geo-based experiments, estimating causal effects on panel data, and quantifying uncertainty.

The package is organized around three areas:

| Area | What it covers |
|------|----------------|
| **Design** | Geo experiment design, randomization (complete, stratified, thinning, rerandomization, QuickBlock, matched pairs, greedy matching), power / MDE, assignment helpers |
| **Methods** | Synthetic control / SCM, TBR, Bayesian regression, multi-task GP, diff-in-diff, synthetic DID, triply robust estimators, and related panel estimators |
| **Inference** | K-fold and residual-based procedures, placebos, conformal methods, unit jackknife, and other uncertainty tools |

**Python:** 3.10+ (see `pyproject.toml` for pinned dependencies).

---

## Documentation

- **Hosted docs:** If your fork enables GitLab Pages (or similar), publish from the default branch using `.gitlab-ci.yml` and use the resulting site URL.

- **Local build:** from the repo root, with docs extras installed:

  ```bash
  poetry install --with docs
  poetry run make -C docs clean html
  ```

  Open `docs/build/html/index.html` in a browser.

- **Long-form guide:** `docs/source/user_guide.md` (architecture, APIs, and workflows).

Sphinx also pulls a short intro from `docs/README.rst`; keep that file aligned with major version or install changes if you maintain both.

---

## Install locally (development)

This project uses [Poetry](https://python-poetry.org/) (see CircleCI for a pinned version, e.g. 1.7.1).

```bash
git clone <repository-url>
cd panel_exp
poetry install
```

For documentation tooling as well:

```bash
poetry install --with docs
```

Activate the virtualenv (`poetry shell`) or prefix commands with `poetry run`.

---

## Quickstart

```python
import pandas as pd
from panel_exp.panel_data import long_df_to_paneldataset
from panel_exp.methods.scm import SyntheticControl

long_df = pd.read_csv("kansas_parsed.csv")
panel_data = long_df_to_paneldataset(
    long_df, "year_qtr", "state", "lngdp", ["Kansas"], 2012
)

scm = SyntheticControl()
scm.run_analysis(panel_data)
scm.plot()
```

For geo design workflows, see `docs/source/user_guide.md` (e.g. `GeoExperimentDesign` and `long_df_to_paneldataset`).

---

## Tests

Tests use [pytest](https://docs.pytest.org/en/stable/getting-started.html).

```bash
poetry install
poetry run pytest
```

**Before opening a pull request:** run the full test suite locally and ensure it passes. (This repo uses Poetry; there is no `setup.py`. Prefer `poetry run pytest` rather than `python setup.py pytest`.)

---

## Project layout (high level)

- `panel_exp/` — library code (`design`, `methods`, `inference`, `panel_data`, `utils`, …)
- `tests/` — pytest tests
- `docs/` — Sphinx sources and Makefile
- `scripts/` — analysis and diagnostic scripts (not part of the wheel API)
- `examples/` — notebooks and examples

---

## Status

Under active development. Version in `pyproject.toml` is the source of truth for the current release line.
