"""Synthetic DGP missingness policies and staggered treatment semantics."""

from __future__ import annotations

import warnings

import pytest

from panel_exp.validation.recovery_runner import RecoveryRunner
from panel_exp.validation.synthetic_scenarios import (
    get_recovery_scenario,
    get_scenario_recovery_support,
)
from panel_exp.validation.synthetic_world import (
    MISSINGNESS_POLICY_DROP,
    MISSINGNESS_POLICY_ERROR,
    MISSINGNESS_POLICY_FILL_ZERO,
    MISSINGNESS_POLICY_NONE,
    PANEL_MISSINGNESS_WARNING,
    SyntheticScenario,
    SyntheticWorld,
)


def test_missingness_policy_error_raises_on_conversion():
    scenario = SyntheticScenario(
        name="missing_error",
        n_geos=10,
        n_periods=30,
        treatment_start=22,
        missing_probability=0.2,
        missingness_policy="error",
        random_state=0,
    )
    world = SyntheticWorld.generate(scenario)
    assert world.panel_conversion_metadata()["missingness_policy"] == MISSINGNESS_POLICY_ERROR
    with pytest.raises(ValueError, match="missingness_policy='error'"):
        world.to_panel_dataset()


def test_missingness_policy_fill_zero_warns_and_metadata():
    scenario = get_recovery_scenario("scm_missing_outcomes")
    assert scenario.missingness_policy == MISSINGNESS_POLICY_FILL_ZERO
    world = SyntheticWorld.generate(scenario)
    meta = world.panel_conversion_metadata()
    assert meta["missingness_policy"] == MISSINGNESS_POLICY_FILL_ZERO
    assert meta["missing_cell_count"] > 0
    assert meta["panel_conversion_warning"] == PANEL_MISSINGNESS_WARNING
    with pytest.warns(UserWarning, match="filled with zero"):
        world.to_panel_dataset()


def test_missingness_policy_drop_documented_behavior():
    scenario = SyntheticScenario(
        name="missing_drop",
        n_geos=10,
        n_periods=30,
        treatment_start=22,
        treated_units=("geo_0", "geo_1"),
        missing_probability=0.08,
        missingness_policy="drop",
        random_state=1,
    )
    world = SyntheticWorld.generate(scenario)
    meta = world.panel_conversion_metadata()
    assert meta["missingness_policy"] == MISSINGNESS_POLICY_DROP
    with pytest.warns(UserWarning, match="dropped"):
        pds = world.to_panel_dataset()
    assert pds.wide_data.isna().sum().sum() == 0
    assert "geo_0" in pds.wide_data.index


def test_calibration_scenarios_do_not_use_fill_zero():
    for name in ("recovery_null_effect", "recovery_positive_effect"):
        scenario = get_recovery_scenario(name)
        assert scenario.missing_probability == 0.0
        assert scenario.missingness_policy == MISSINGNESS_POLICY_NONE
        world = SyntheticWorld.generate(scenario)
        meta = world.panel_conversion_metadata()
        assert meta["missingness_policy"] == MISSINGNESS_POLICY_NONE
        assert meta["missing_cell_count"] == 0
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            world.to_panel_dataset()
        assert not any(
            "filled with zero" in str(item.message) for item in caught
        )


def test_staggered_adoption_has_distinct_treatment_starts():
    scenario = get_recovery_scenario("sdid_staggered_adoption")
    assert scenario.treatment_timing == "staggered"
    world = SyntheticWorld.generate(scenario)
    starts = world.truth["treatment_start_by_unit"]
    treated = list(world.truth["treated_units"])
    assert len({starts[u] for u in treated}) > 1
    meta = world.panel_conversion_metadata()
    assert meta["staggered_treatment_supported"] is True
    assert meta["treatment_start_by_unit"] == starts


def test_simultaneous_scenario_does_not_claim_staggered_support():
    world = SyntheticWorld.generate(get_recovery_scenario("recovery_positive_effect"))
    meta = world.panel_conversion_metadata()
    assert meta["treatment_timing"] == "simultaneous"
    assert meta["staggered_treatment_supported"] is False
    starts = meta["treatment_start_by_unit"]
    treated = list(world.truth["treated_units"])
    assert len({starts[u] for u in treated}) == 1


def test_recovery_runner_exposes_dgp_semantics_metadata():
    payload = RecoveryRunner(
        "SCM",
        "recovery_positive_effect",
        n_simulations=1,
        random_state=0,
    ).run()
    meta = payload["scenario_dgp_metadata"]
    assert meta["missingness_policy"] == MISSINGNESS_POLICY_NONE
    assert "staggered_treatment_supported" in meta
    assert "treatment_start_by_unit" in meta
    assert meta["staggered_treatment_supported"] is False


def test_staggered_scenario_recovery_support_documents_sdid_gap():
    support = get_scenario_recovery_support("sdid_staggered_adoption")
    assert support["recovery_supported"] is False
    scenario = get_recovery_scenario("sdid_staggered_adoption")
    world = SyntheticWorld.generate(scenario)
    assert world.panel_conversion_metadata()["staggered_treatment_supported"] is True
