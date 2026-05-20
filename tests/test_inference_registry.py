"""Tests for ImpactAnalyzer inference registry dispatch."""

import numpy as np
import pandas as pd
import pytest

from panel_exp.inference.modes import register_builtin_inference_modes
from panel_exp.inference.registry import InferenceRegistry, get_inference_registry
from panel_exp.panel_data import PanelDataset, TimePeriod


def test_registry_resolves_all_builtin_modes():
    reg = InferenceRegistry()
    register_builtin_inference_modes(reg)
    for key in (
        None,
        "UnitJackKnife",
        "JKP",
        "Bayesian",
        "BlockResidualBootstrap",
        "Conformal",
        "Kfold",
        "Placebo",
        "TimeSeriesKfold",
    ):
        spec = reg.resolve(key)
        assert spec.run is not None


def test_registry_unknown_raises():
    reg = get_inference_registry()
    with pytest.raises(NotImplementedError, match="not a supported inference method"):
        reg.resolve("NotAMode")


def test_unit_jackknife_requires_two_controls():
    pytest.importorskip("cvxpy")
    from panel_exp.methods.scm import SyntheticControl

    wide = pd.DataFrame({"c1": np.arange(20.0)})
    pds = PanelDataset(wide.T, treated_units=["c1"], treated_periods=[TimePeriod(10)])
    scm = SyntheticControl(inference="UnitJackKnife", alpha=0.05)
    with pytest.raises(ValueError, match="at least 2 control units"):
        scm.run_analysis(pds)


def test_placebo_strict_raises_on_unsupported():
    pytest.importorskip("cvxpy")
    from panel_exp.methods.scm import SyntheticControl

    wide = pd.DataFrame({"c1": np.arange(20.0), "c2": np.arange(20.0) + 1})
    pds = PanelDataset(wide.T, treated_units=["c1"], treated_periods=[TimePeriod(10)])
    scm = SyntheticControl(inference="Placebo", alpha=0.05)
    with pytest.raises(ValueError, match="Placebo inference unavailable"):
        scm.run_analysis(pds, placebo_strict=True)
