"""Reproducibility contract for simulation-based power analysis."""

from __future__ import annotations

import pandas as pd

from panel_exp.design.power import PowerAnalysis
from panel_exp.methods.tbr import TBRRidge
from tests.power_helpers import make_synthetic_power_panel


def _run_power(seed: int):
    panel = make_synthetic_power_panel(seed=0, n_time=20, treat_start=14)
    pa = PowerAnalysis(
        panel,
        TBRRidge,
        "Kfold",
        test_length=4,
        train_length=8,
        mx_effect=0.1,
        n_sample_prc=0.3,
        n_jobs=1,
        ci_version=2,
        random_state=seed,
    )
    pa.run_analysis()
    return pa


def test_same_random_state_identical_power_output():
    pa1 = _run_power(42)
    pa2 = _run_power(42)
    pd.testing.assert_frame_equal(pa1.output_df, pa2.output_df)
    assert pa1.mde_kpi_cumulative == pa2.mde_kpi_cumulative
    assert pa1.mde_percent == pa2.mde_percent


def test_different_seed_does_not_assert_equality():
    pa1 = _run_power(1)
    pa2 = _run_power(2)
    assert pa1.random_state != pa2.random_state


def test_random_state_none_uses_unseeded_generator():
    pa = PowerAnalysis(
        make_synthetic_power_panel(),
        TBRRidge,
        "Kfold",
        4,
        train_length=8,
        random_state=None,
    )
    assert pa.random_state is None


def test_inference_seed_derivation_is_deterministic():
    pa = PowerAnalysis(
        make_synthetic_power_panel(),
        TBRRidge,
        "Kfold",
        4,
        train_length=8,
        random_state=10,
    )
    assert pa._inference_seed(0) == 10
    assert pa._inference_seed(3) == 13
    assert pa._inference_kwargs(1).get("random_state") == 11
