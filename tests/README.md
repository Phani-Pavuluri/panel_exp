# Running tests

Dependencies (including `matplotlib`, required by `panel_exp.panel_data`) are managed with **Poetry** — see [`pyproject.toml`](../pyproject.toml).

## Setup (once per clone)

```bash
cd panel_exp
poetry install --with dev
```

## Run tests (recommended)

```bash
poetry run pytest
poetry run pytest tests/track_b/test_trustreport_decision_context_smoke_001.py -q
```

Or activate the project venv, then use `pytest` / `python -m pytest`:

```bash
source .venv/bin/activate
python -m pytest tests/track_b/ -q
```

## Common failure: `ModuleNotFoundError: No module named 'matplotlib'`

This usually means pytest is using **system Python** without project dependencies installed (e.g. bare `python3 -m pytest` before `poetry install`).

**Fix:** run `poetry install --with dev`, then use `poetry run pytest` or the activated `.venv` interpreter — not an unrelated system `python3`.

Do not add lazy imports in library code to avoid this; install the declared dependencies instead.
