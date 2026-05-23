"""Estimator diagnostic classification and post-fit routing."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from panel_exp.diagnostics.estimator_diagnostics import (
    ESTIMATOR_DIAGNOSTIC_PROFILES,
    attach_estimator_diagnostics,
    classify_estimator,
    collect_estimator_diagnostics,
)
from panel_exp.methods.DID import DID
from panel_exp.methods.scm import SyntheticControl
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod


def _simple_panel(n_units: int = 8, n_periods: int = 24, seed: int = 0) -> PanelDataset:
    rng = np.random.default_rng(seed)
    wide = pd.DataFrame(
        rng.normal(100, 10, size=(n_units, n_periods)),
        index=[f"u{i}" for i in range(n_units)],
        columns=pd.date_range("2020-01-01", periods=n_periods, freq="W"),
    )
    t0 = n_periods - 6
    period = TimePeriod(wide.columns[t0], wide.columns[-1])
    return PanelDataset(
        wide,
        treated_periods=[period],
        treated_units=["u0"],
    )


def test_all_listed_estimators_have_profiles():
    expected = {
        "SyntheticControl",
        "SyntheticControlCVXPY",
        "AugSynth",
        "AugSynthCVXPY",
        "TBR",
        "TBRRidge",
        "DID",
        "SyntheticDID",
        "TROP",
        "BayesianTBR",
        "BayesianTBRHorseShoe",
        "MTGP",
    }
    assert expected == set(ESTIMATOR_DIAGNOSTIC_PROFILES)


def test_classify_estimator_unknown_raises():
    with pytest.raises(KeyError, match="Unknown estimator"):
        classify_estimator("NotAnEstimator")


def test_default_run_analysis_omits_estimator_diagnostics():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel)
    assert "estimator_diagnostics" not in scm.results

    model = TBRRidge(inference=None)
    model.run_analysis(panel)
    assert "estimator_diagnostics" not in model.results

    did = DID()
    did.run_analysis(panel, multiple_treated="pooled")
    assert "estimator_diagnostics" not in did.results


def test_run_estimator_diagnostics_true_attaches_sections():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel, run_estimator_diagnostics=True)
    diag = scm.results["estimator_diagnostics"]
    assert diag["estimator"] == "SyntheticControl"
    assert diag["primary_diagnostic"] == "counterfactual_stability"
    assert "counterfactual_stability" in diag["sections"]
    assert "donor_support" in diag["sections"]
    pre = diag["sections"]["counterfactual_stability"]["pre_period_residuals"]
    assert pre["available"] is True
    assert pre["n_pre"] == panel.treated_start_idxs[0]

    model = TBRRidge(inference=None)
    model.run_analysis(panel, run_estimator_diagnostics=True)
    assert "counterfactual_stability" in model.results["estimator_diagnostics"]["sections"]

    did = DID()
    did.run_analysis(
        panel,
        multiple_treated="pooled",
        run_estimator_diagnostics=True,
    )
    diag = did.results["estimator_diagnostics"]
    assert diag["primary_diagnostic"] == "pretrend_contract"
    assert "pretrend_contract" in diag["sections"]
    assert did.results["did_pretrend_contract"] is not None


def test_y_hat_unchanged_with_diagnostics_flag():
    panel = _simple_panel()
    off = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    on = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    off.run_analysis(panel)
    on.run_analysis(panel, run_estimator_diagnostics=True)
    np.testing.assert_allclose(off.results["y"], on.results["y"])
    np.testing.assert_allclose(off.results["y_hat"], on.results["y_hat"])


def test_mtgp_profile_unsupported_collect():
    from panel_exp.methods.mtgp import MTGP

    profile = classify_estimator(MTGP)
    assert profile.primary_diagnostic == "unsupported"
    mtgp = MTGP()
    payload = collect_estimator_diagnostics(mtgp)
    assert payload.get("unsupported_reason")


def test_attach_estimator_diagnostics_explicit():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel)
    assert "estimator_diagnostics" not in scm.results
    first = attach_estimator_diagnostics(scm)
    assert "estimator_diagnostics" in scm.results
    second = attach_estimator_diagnostics(scm)
    assert second == first
