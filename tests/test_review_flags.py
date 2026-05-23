"""Review-only stability flags — per-family classification, opt-in attach."""

from __future__ import annotations

import numpy as np
import pytest

from panel_exp.diagnostics import (
    build_estimator_review,
    classify_review_flag_support,
    collect_review_flags,
)
from panel_exp.diagnostics.estimator_diagnostics import ESTIMATOR_DIAGNOSTIC_PROFILES
from panel_exp.methods.DID import DID
from panel_exp.methods.scm import SyntheticControl
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import get_recovery_scenario
from panel_exp.validation.synthetic_world import SyntheticWorld


def _simple_panel(n_units: int = 8, n_periods: int = 24, seed: int = 0) -> PanelDataset:
    import pandas as pd

    rng = np.random.default_rng(seed)
    wide = pd.DataFrame(
        rng.normal(100, 10, size=(n_units, n_periods)),
        index=[f"u{i}" for i in range(n_units)],
        columns=pd.date_range("2020-01-01", periods=n_periods, freq="W"),
    )
    t0 = n_periods - 6
    return PanelDataset(
        wide,
        treated_periods=[TimePeriod(wide.columns[t0], wide.columns[-1])],
        treated_units=["u0"],
    )


def test_default_run_analysis_omits_review_flags():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel)
    assert "review_flags" not in scm.results
    assert "review_flag_support" not in scm.results


def test_all_estimator_families_have_flag_classification():
    for name in ESTIMATOR_DIAGNOSTIC_PROFILES:
        support = classify_review_flag_support(name)
        assert support["estimator"] == name
        assert "classification" in support
        assert isinstance(support["supported"], list)
        assert isinstance(support["unsupported"], dict)


def test_scm_support_includes_donor_and_residual_flags():
    support = classify_review_flag_support("SyntheticControl")
    assert "residual_drift" in support["supported"]
    assert "high_donor_concentration" in support["supported"]
    assert "pretrend_violation" in support["unsupported"]


def test_did_support_pretrend_not_donor():
    support = classify_review_flag_support("DID")
    assert "pretrend_violation" in support["supported"]
    assert "high_donor_concentration" in support["unsupported"]
    assert support["unsupported"]["high_donor_concentration"] == "estimator_has_no_donor_weight_vector"


def test_tbrridge_support_coefficient_and_optional_fold():
    support = classify_review_flag_support("TBRRidge")
    assert "coefficient_instability" in support["supported"]
    assert "fold_instability" in support["supported"]
    assert "high_donor_concentration" in support["unsupported"]


def test_mtgp_all_flags_unsupported():
    support = classify_review_flag_support("MTGP")
    assert support["supported"] == []
    assert "residual_drift" in support["unsupported"]


def test_collect_review_flags_scm_after_fit():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel)
    payload = collect_review_flags(scm)
    assert payload["estimator"] == "SyntheticControl"
    assert "residual_drift" in payload["review_flags"]
    assert payload["review_flags"]["residual_drift"] in ("ok", "warn", "fail", "unavailable")
    assert "high_donor_concentration" in payload["review_flags"]


def test_build_estimator_review_includes_flags_without_attach():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel)
    review = build_estimator_review(scm, attach=False)
    assert "review_flags" in review
    assert "review_flag_support" in review
    assert "review_flags" not in scm.results


def test_attach_review_flags_opt_in():
    panel = _simple_panel()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel)
    build_estimator_review(scm, attach=True, attach_review_flags=True)
    assert "review_flags" in scm.results
    assert "review_flag_support" in scm.results


def test_estimates_unchanged_when_collecting_flags():
    panel = _simple_panel()
    base = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    other = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    base_results = base.run_analysis(panel)
    other_results = other.run_analysis(panel)
    collect_review_flags(other, other_results)
    np.testing.assert_allclose(base_results["y"], other_results["y"])
    np.testing.assert_allclose(base_results["y_hat"], other_results["y_hat"])


@pytest.mark.slow
def test_structural_break_scenario_residual_drift_warn_or_fail():
    world = SyntheticWorld.generate(get_recovery_scenario("scm_structural_break"))
    panel = world.to_panel_dataset()
    scm = SyntheticControl(inference=None, penalty="none", penalty_strength=0.0)
    scm.run_analysis(panel)
    flags = collect_review_flags(scm)["review_flags"]
    assert flags["residual_drift"] in ("warn", "fail")


def test_did_pretrend_flags_from_contract():
    panel = _simple_panel(n_units=6)
    did = DID()
    did.run_analysis(panel, multiple_treated="pooled")
    flags = collect_review_flags(did)["review_flags"]
    assert flags["pretrend_violation"] in ("ok", "warn", "fail", "unavailable")
    assert isinstance(flags["pretrend_assessment_unavailable"], bool)


def test_augsynth_donor_flags_unsupported_reason():
    support = classify_review_flag_support("AugSynth")
    assert "high_donor_concentration" in support["unsupported"]
    assert "simplex" in support["unsupported"]["high_donor_concentration"].lower()


def test_trop_weak_donor_supported_not_simplex_donor():
    support = classify_review_flag_support("TROP")
    assert "weak_donor_pool" in support["supported"]
    assert "high_donor_concentration" in support["unsupported"]
