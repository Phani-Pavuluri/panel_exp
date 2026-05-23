"""Synthetic DGP hardening: scenarios, missingness policy, recovery wiring."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from panel_exp.validation.recovery_runner import RecoveryRunner
from panel_exp.validation.synthetic_scenarios import (
    ESTIMATOR_RECOVERY_SCENARIOS,
    RECOVERY_SCENARIO_REGISTRY,
    get_recovery_scenario,
    get_scenario_recovery_support,
    scenarios_for_estimator,
)
from panel_exp.validation.synthetic_world import (
    MISSINGNESS_POLICY_FILL_ZERO,
    PANEL_MISSINGNESS_WARNING,
    SyntheticWorld,
    control_donor_correlation_summary,
)


def test_scm_high_collinearity_generates_correlated_donors():
    high = get_recovery_scenario("scm_high_collinearity")
    low = get_recovery_scenario("scm_low_signal")
    world_high = SyntheticWorld.generate(high)
    world_low = SyntheticWorld.generate(replace(low, random_state=high.random_state))
    summary = world_high.truth["donor_correlation_summary"]
    summary_low = world_low.truth["donor_correlation_summary"]
    assert summary["n_control_units"] >= 2
    assert summary["mean_abs_off_diag_correlation"] > summary_low[
        "mean_abs_off_diag_correlation"
    ]
    assert summary["mean_abs_off_diag_correlation"] > 0.65
    assert summary["max_abs_correlation"] > 0.75
    assert world_high.truth["cross_geo_correlation_param"] == pytest.approx(0.98)


def test_structural_break_scenario_wired_for_scm():
    assert "scm_structural_break" in ESTIMATOR_RECOVERY_SCENARIOS["SCM"]
    assert "scm_structural_break" in RECOVERY_SCENARIO_REGISTRY
    scenario = get_recovery_scenario("scm_structural_break")
    assert scenario.structural_break_shift != 0.0
    world = SyntheticWorld.generate(scenario)
    observed = np.asarray(world.truth["observed"])
    t0 = int(world.truth["treatment_start"])
    pre_mean = float(np.nanmean(observed[:, :t0]))
    post_mean = float(np.nanmean(observed[:, t0:]))
    assert post_mean - pre_mean > scenario.structural_break_shift * 0.25


def test_missingness_scenario_records_policy_and_warning():
    scenario = get_recovery_scenario("scm_missing_outcomes")
    assert scenario.missing_probability > 0.0
    world = SyntheticWorld.generate(scenario)
    meta = world.panel_conversion_metadata()
    assert meta["missingness_policy"] == MISSINGNESS_POLICY_FILL_ZERO
    assert meta["missing_cell_count"] > 0
    assert meta["panel_conversion_warning"] == PANEL_MISSINGNESS_WARNING
    with pytest.warns(UserWarning, match="filled with zero"):
        world.to_panel_dataset()


def test_recovery_missing_outcomes_in_tbrridge_battery():
    tbr_names = scenarios_for_estimator("TBRRidge")
    assert "recovery_missing_outcomes" in tbr_names
    assert "tbrridge_multi_treated" in tbr_names


def test_multi_treated_scenario_metadata():
    scenario = get_recovery_scenario("scm_multi_treated")
    world = SyntheticWorld.generate(scenario)
    meta = world.panel_conversion_metadata()
    assert len(world.truth["treated_units"]) > 1
    assert meta["n_treated_units"] > 1
    assert meta["treatment_timing"] == "simultaneous"
    assert meta["aggregation_mode"] == "relative_att_post_path_mean"


def test_staggered_scenario_explicitly_unsupported_for_recovery():
    support = get_scenario_recovery_support("sdid_staggered_timing")
    assert support["recovery_supported"] is False
    assert support["skip_reason"]
    assert "staggered" in support["skip_reason"].lower()
    scenario = get_recovery_scenario("sdid_staggered_timing")
    assert scenario.treatment_timing == "staggered_declared"
    assert "sdid_staggered_timing" not in ESTIMATOR_RECOVERY_SCENARIOS.get(
        "SCM", ()
    )


def test_recovery_runner_attaches_dgp_metadata():
    payload = RecoveryRunner(
        "SCM",
        "scm_missing_outcomes",
        n_simulations=1,
        random_state=0,
    ).run()
    assert "scenario_dgp_metadata" in payload
    meta = payload["scenario_dgp_metadata"]
    assert meta["missingness_policy"] == MISSINGNESS_POLICY_FILL_ZERO
    assert payload["scenario_recovery_support"]["recovery_supported"] is True


def test_scm_battery_includes_new_scenarios():
    scm = scenarios_for_estimator("SCM")
    for name in (
        "scm_high_collinearity",
        "scm_structural_break",
        "scm_missing_outcomes",
        "scm_multi_treated",
    ):
        assert name in scm


def test_collinearity_helper_stable_with_few_controls():
    summary = control_donor_correlation_summary(
        np.ones((3, 10)),
        ["geo_0"],
        [f"geo_{i}" for i in range(3)],
        treatment_start=5,
    )
    assert np.isnan(summary["mean_abs_off_diag_correlation"])
