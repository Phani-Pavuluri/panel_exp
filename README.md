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

After `run_analysis()`, `power_contract` records planning semantics (`mde_type: simulation_coverage`, `classical_power: false`). Use for **ranking design alternatives and sensitivity only** — not guaranteed detectability or financial go/no-go thresholds. Review `aa_calibration` on null-effect rows before decision use.

### Interference

`InterferenceAssumption`: `unknown`, `no_interference`, `partial_interference`. Design validation warns when interference is unknown. The package does **not** estimate spillovers automatically.

### Recovery validation (diagnostic)

`panel_exp.validation.RecoveryRunner` and `validation_metadata` on analysis results summarize synthetic recovery metrics (bias, coverage, FPR, power). These are **diagnostic** and do not auto-upgrade maturity ratings.

### Not shipped

- `panel_exp.pretest_analysis` — referenced in some dev notebooks only.
- `panel_exp.util` — removed; import `standardize` from `panel_exp.methods.bayesian_regression`.

---

## Decision Workflow

Advisory readout chain (non-blocking; does not change estimates):

```
Design
↓
Inference
↓
Recovery
↓
Calibration
↓
Maturity Evidence
↓
Readiness
↓
Experiment Card
↓
Run Bundle
```

| Stage | Summary |
|-------|---------|
| **Design** | `DesignSpec`, assignment, `DesignEvidence` |
| **Inference** | Estimators + labeled interval semantics |
| **Recovery** | `RecoveryRunner` diagnostics — see `docs/VALIDATION_COVERAGE.md` |
| **Calibration** | `build_calibration_report` (FPR, coverage, power) |
| **Maturity evidence** | Measured evidence; does not auto-promote catalog labels |
| **Readiness** | `build_readiness_assessment` — advisory only |
| **Experiment card** | `build_experiment_card` (contracts + optional power results) |
| **Run bundle** | `build_run_artifact_bundle` portable export |

Further reading: `docs/ROADMAP_REASSESSMENT.md`, `docs/DOC_DRIFT_AUDIT.md`.

Runnable examples:

- `poetry run python examples/decision_workflow_example.py` — full workflow
- `poetry run python examples/readiness_profile_comparison.py` — same evidence under all profiles

```python
from panel_exp.validation import build_calibration_report, build_maturity_evidence
from panel_exp.policy import build_readiness_assessment, ReadinessProfile
from panel_exp.artifacts import build_experiment_card

report = build_calibration_report(recovery_outputs=recovery_payloads, estimator="DID")
maturity = build_maturity_evidence("TBRRidge", meta, calibration_report=report, recovery_outputs=recovery_payloads)
readiness = build_readiness_assessment(
    inference_metadata=results["inference_metadata"],
    calibration_report=report,
    maturity_evidence=maturity,
    profile=ReadinessProfile.STANDARD,  # default if omitted
)
card = build_experiment_card(evidence)
print(card.to_markdown())
```

## Readiness Policy Profiles

`build_readiness_assessment(..., profile=ReadinessProfile.STANDARD)` evaluates the same evidence under configurable advisory thresholds. **All profiles are non-blocking** — none prove causal truth; readiness summarizes evidence quality for human review.

| Profile | When to use |
|---------|-------------|
| **exploratory** | Research and debugging. Allows missing intervals, `research_only` / unvalidated maturity, and unknown interference. **Not** for budget or go/no-go decisions. |
| **standard** | **Default.** Requires path-level intervals, rejects research-only / unvalidated methods, requires a declared interference assumption. Suitable for normal reviewed readouts. |
| **strict** | Conservative review before high-stakes decisions. Tighter FPR, coverage, power, and recovery-success thresholds. Still advisory — not automatic approval. |

Profile comparison (mocked inputs, no estimator fit): `examples/readiness_profile_comparison.py`.

### Run artifact bundle export

Portable JSON/markdown snapshot of evidence, experiment card, calibration, maturity, and readiness (opt-in; does not auto-attach to estimator results):

```python
from panel_exp.artifacts import build_run_artifact_bundle, write_run_artifact_bundle_json

bundle = build_run_artifact_bundle(
    evidence=evidence,
    experiment_card=card,
    calibration_report=report,
    maturity_evidence=maturity,
    readiness_assessment=readiness,
)
write_run_artifact_bundle_json(bundle, "artifacts/run_bundle.json")
```

---

## Documentation

- **Hosted docs:** Pre-built HTML under `gh-pages/` (open `gh-pages/index.html` locally).
- **Development validation:** `docs/dev_validation_workflow.md` documents the standard container-first `make validate` workflow.
- **User guide source:** `gh-pages/_sources/user_guide.md.txt` (starts with **Current Package Status** / code truth).
- **Uncertainty notes:** `panel_exp/inference/uncertainty.md`
- **Validation matrix:** `docs/VALIDATION_COVERAGE.md`
- **Roadmap / gaps:** `docs/ROADMAP_REASSESSMENT.md`
- **Future package-side agents (deferred):** `docs/FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001.md` — roadmap capture only; no agent implementation
- **Doc drift audit:** `docs/DOC_DRIFT_AUDIT.md`
- **GeoX–MIP production alignment audit:** [`docs/track_d/GEOX_MIP_PRODUCTION_ALIGNMENT_READINESS_AUDIT_001.md`](docs/track_d/GEOX_MIP_PRODUCTION_ALIGNMENT_READINESS_AUDIT_001.md) — committed-state audit; multiple production gates remain blocked
- **Examples index:** `examples/README.md` (legacy notebooks flagged)

---

## Install locally (development)

```bash
git clone <repository-url>
cd panel_exp
make validate
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

`PowerAnalysis` uses **simulation**: sliding train/test windows, injected percent-effect grids, and interval coverage vs a threshold. Reported MDE is **not** classical analytic power or a guaranteed minimum detectable effect. `power_contract` and `mde_semantics` document this; pass `random_state` for reproducibility. Power outputs are **planning diagnostics**, not promised detection probabilities.

---

## Tests

```bash
make validate
```

This container-first command and its host fallback are documented in
`docs/dev_validation_workflow.md`.

---

## Project layout

- `panel_exp/` — library (`design`, `methods`, `inference`, `spec`, `evidence`, …)
- `tests/` — pytest (`tests/fixtures/` for synthetic data)
- `gh-pages/` — published documentation HTML
- `scripts/` — diagnostic scripts (not part of the wheel API)
- `examples/` — notebooks, `decision_workflow_example.py`, `readiness_profile_comparison.py`

---

## Status

Under active development. Version in `pyproject.toml` and `panel_exp.__version__` is the source of truth.

**Not installable from notebooks:** `panel_exp.pretest_analysis` is referenced in some example notebooks but is not shipped in the wheel; use `PowerAnalysis` and `GeoExperimentDesign` instead.
