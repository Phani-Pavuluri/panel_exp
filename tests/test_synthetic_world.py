"""Tests for synthetic world generation."""

import numpy as np
import pytest

from panel_exp.validation.scenarios import get_scenario
from panel_exp.validation.synthetic_world import (
    OUTCOME_COL,
    TIME_COL,
    UNIT_COL,
    SyntheticScenario,
    SyntheticWorld,
)


def test_same_seed_same_panel():
    scenario = get_scenario("positive_relative_lift")
    w1 = SyntheticWorld.generate(scenario)
    w2 = SyntheticWorld.generate(scenario)
    pd1 = w1.panel_data.sort_values([UNIT_COL, TIME_COL]).reset_index(drop=True)
    pd2 = w2.panel_data.sort_values([UNIT_COL, TIME_COL]).reset_index(drop=True)
    np.testing.assert_array_equal(
        pd1[OUTCOME_COL].fillna(-999).to_numpy(),
        pd2[OUTCOME_COL].fillna(-999).to_numpy(),
    )


def test_different_seed_changes_noise():
    from dataclasses import replace

    s1 = get_scenario("positive_relative_lift")
    s2 = replace(s1, random_state=99)
    w1 = SyntheticWorld.generate(s1)
    w2 = SyntheticWorld.generate(s2)
    assert not np.allclose(
        w1.panel_data[OUTCOME_COL].fillna(0).to_numpy(),
        w2.panel_data[OUTCOME_COL].fillna(0).to_numpy(),
    )


def test_aa_truth_is_zero():
    world = SyntheticWorld.generate(get_scenario("aa_null"))
    assert abs(float(world.truth["true_effect"])) < 1e-10


def test_positive_scenario_injects_effect():
    world = SyntheticWorld.generate(get_scenario("positive_relative_lift"))
    assert float(world.truth["true_effect"]) > 0.05
    treated = world.panel_data[world.panel_data["treated"] == 1]
    post = treated[treated["post"] == 1][OUTCOME_COL].mean()
    pre = treated[treated["post"] == 0][OUTCOME_COL].mean()
    assert post > pre


def test_heterogeneous_unit_effects():
    world = SyntheticWorld.generate(get_scenario("heterogeneous_positive_lift"))
    effects = [
        v
        for u, v in world.truth["effect_by_unit"].items()
        if u in world.truth["treated_units"]
    ]
    assert len(effects) >= 2
    assert len(set(round(e, 6) for e in effects)) > 1


def test_panel_columns_present():
    world = SyntheticWorld.generate(get_scenario("aa_null"))
    for col in (UNIT_COL, TIME_COL, OUTCOME_COL, "treated", "post"):
        assert col in world.panel_data.columns


def test_truth_dict_fields():
    world = SyntheticWorld.generate(get_scenario("positive_relative_lift"))
    for key in (
        "true_effect",
        "treatment_start",
        "treated_units",
        "control_units",
        "effect_by_unit",
        "scenario_name",
    ):
        assert key in world.truth


def test_scenario_validation_errors():
    with pytest.raises(ValueError):
        SyntheticScenario(
            name="bad",
            n_geos=1,
            n_periods=10,
            treatment_start=5,
        )
