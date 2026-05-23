"""Estimator diagnostic classification and explicit review workflow."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from panel_exp.diagnostics import (
    attach_estimator_diagnostics,
    build_estimator_review,
    collect_estimator_diagnostics,
)
from panel_exp.diagnostics.estimator_diagnostics import (
    ESTIMATOR_DIAGNOSTIC_PROFILES,
    classify_estimator,
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
    assert "did_pretrend_contract" in did.results


def test_collect_estimator_diagnostics_scm_family_sections():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    results = scm.run_analysis(panel)
    diagnostics = collect_estimator_diagnostics(scm, results)
    assert diagnostics["estimator"] == "SyntheticControl"
    assert diagnostics["primary_diagnostic"] == "counterfactual_stability"
    assert "counterfactual_stability" in diagnostics["sections"]
    assert "donor_support" in diagnostics["sections"]
    pre = diagnostics["sections"]["counterfactual_stability"]["pre_period_residuals"]
    assert pre["available"] is True
    assert pre["n_pre"] == panel.treated_start_idxs[0]
    assert "estimator_diagnostics" not in results


def test_collect_and_attach_explicit_results_dict():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    results = scm.run_analysis(panel)
    diagnostics = collect_estimator_diagnostics(scm, results)
    attach_estimator_diagnostics(results, diagnostics)
    assert results["estimator_diagnostics"] == diagnostics


def test_build_estimator_review_attach_false_does_not_mutate():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel)
    keys_before = set(scm.results.keys())
    y_before = np.asarray(scm.results["y"]).copy()
    y_hat_before = np.asarray(scm.results["y_hat"]).copy()
    review = build_estimator_review(scm, attach=False)
    assert review["diagnostics_version"] == "1.0"
    assert "estimator_diagnostics" in review
    assert set(scm.results.keys()) == keys_before
    assert "estimator_diagnostics" not in scm.results
    np.testing.assert_allclose(scm.results["y"], y_before)
    np.testing.assert_allclose(scm.results["y_hat"], y_hat_before)


def test_build_estimator_review_attach_true_mutates_results():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel)
    review = build_estimator_review(scm, attach=True)
    assert scm.results["estimator_diagnostics"] == review["estimator_diagnostics"]


def test_did_collect_includes_pretrend_contract_section():
    panel = _simple_panel(n_units=6)
    did = DID()
    results = did.run_analysis(panel, multiple_treated="pooled")
    diagnostics = collect_estimator_diagnostics(did, results)
    assert diagnostics["primary_diagnostic"] == "pretrend_contract"
    assert "pretrend_contract" in diagnostics["sections"]
    assert results["did_pretrend_contract"] is not None
    assert (
        diagnostics["sections"]["pretrend_contract"]["contract"]
        == results["did_pretrend_contract"]
    )


def test_y_hat_unchanged_when_collecting_diagnostics():
    panel = _simple_panel()
    base = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    review_est = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    base_results = base.run_analysis(panel)
    review_results = review_est.run_analysis(panel)
    collect_estimator_diagnostics(review_est, review_results)
    np.testing.assert_allclose(base_results["y"], review_results["y"])
    np.testing.assert_allclose(base_results["y_hat"], review_results["y_hat"])


def test_tbrridge_collect_pre_period_residuals():
    panel = _simple_panel()
    model = TBRRidge(inference=None)
    results = model.run_analysis(panel)
    diagnostics = collect_estimator_diagnostics(model, results)
    assert "counterfactual_stability" in diagnostics["sections"]


def test_mtgp_profile_unsupported_collect():
    from panel_exp.methods.mtgp import MTGP

    profile = classify_estimator(MTGP)
    assert profile.primary_diagnostic == "unsupported"
    mtgp = MTGP()
    payload = collect_estimator_diagnostics(mtgp)
    assert payload.get("unsupported_reason")
