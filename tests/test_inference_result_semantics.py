"""InferenceResult interval typing and honest unavailable reporting."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from panel_exp.inference_result import InferenceResult, IntervalType
from panel_exp.methods.scm import SyntheticControl
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod
from tests.inference_registry_helpers import make_scm_panel, make_tbr_panel


def test_interval_type_enum_values():
    assert IntervalType.CONFIDENCE_INTERVAL.value == "confidence_interval"
    assert IntervalType.PLACEBO_BAND.value == "placebo_band"
    assert IntervalType.UNAVAILABLE.value == "unavailable"


def test_unavailable_has_no_intervals():
    ir = InferenceResult.unavailable(
        method="Placebo", alpha=0.05, reason="not enough controls"
    )
    assert ir.intervals_available is False
    assert ir.effective_path_interval_type() == IntervalType.UNAVAILABLE
    results: dict = {}
    ir.attach_to_results(results)
    assert results["interval_type"] == "unavailable"
    assert results["intervals_available"] is False
    assert results["inference_metadata"]["confidence_level"] == pytest.approx(0.95)


@pytest.mark.parametrize(
    "inference,expected_path",
    [
        ("UnitJackKnife", IntervalType.CONFIDENCE_INTERVAL),
        pytest.param(
            "Bayesian",
            IntervalType.CREDIBLE_INTERVAL,
            marks=pytest.mark.skipif(
                __import__("importlib").util.find_spec("jax") is None,
                reason="jax not installed",
            ),
        ),
        ("Conformal", IntervalType.CONFORMAL_INTERVAL),
    ],
)
def test_path_interval_type_per_mode(inference: str, expected_path: IntervalType):
    if inference == "Bayesian":
        pytest.importorskip("jax")
    pds = make_scm_panel(n_ctrl=6)
    est = SyntheticControl(inference=inference, alpha=0.05)
    est.run_analysis(pds)
    assert est.results["interval_type"] == expected_path.value
    assert est.results["intervals_available"] is True
    assert est.inference_result.effective_path_interval_type() == expected_path
    assert "inference_metadata" in est.results


def test_placebo_path_band_vs_effect_ci():
    pds = make_scm_panel(n_ctrl=6)
    est = SyntheticControl(inference="Placebo", alpha=0.05)
    est.run_analysis(pds)
    assert est.results["interval_type"] == IntervalType.PLACEBO_BAND.value
    assert est.inference_result.path_interval_type == IntervalType.PLACEBO_BAND
    if est.inference_result.effect_interval_type is not None:
        assert est.results.get("effect_interval_type") == "confidence_interval"
        assert est.inference_result.interval_lower is not None


def test_placebo_unsupported_unavailable():
    wide = pd.DataFrame({"c1": np.arange(20.0), "c2": np.arange(20.0) + 1})
    pds = PanelDataset(wide.T, treated_units=["c1"], treated_periods=[TimePeriod(10)])
    est = SyntheticControl(inference="Placebo", alpha=0.05)
    with pytest.raises(ValueError, match="Placebo inference unavailable"):
        est.run_analysis(pds, placebo_strict=True)


def test_point_estimate_unavailable():
    pds = make_tbr_panel()
    est = TBRRidge(inference=None, alpha=0.05)
    est.run_analysis(pds)
    assert set(est.results.keys()) == {"times", "y", "y_hat"}
    assert est.inference_result.effective_path_interval_type() == IntervalType.UNAVAILABLE
    assert est.inference_result.intervals_available is False
    assert "y_lower" not in est.results


def test_to_dict_includes_path_and_confidence():
    ir = InferenceResult.for_path_intervals(
        method="Kfold",
        alpha=0.1,
        path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
        point_estimate=1.0,
    )
    d = ir.to_dict()
    assert d["path_interval_type"] == "confidence_interval"
    assert d["confidence_level"] == pytest.approx(0.9)
    assert d["interval_label"] == "confidence interval"
