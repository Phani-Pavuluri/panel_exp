"""Tests for synthetic world generation."""

import json

import numpy as np
import pytest

from panel_exp.validation.scenarios import get_scenario
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld


def test_aa_world_truth_is_zero():
    scenario = get_scenario("aa_zero_effect")
    world = SyntheticWorld.generate(scenario)
    assert abs(world.truth_mean_relative_att) < 1e-10


def test_positive_effect_truth_near_10pct():
    scenario = get_scenario("constant_positive_10pct")
    world = SyntheticWorld.generate(scenario)
    assert 0.08 <= world.truth_mean_relative_att <= 0.12


def test_deterministic_with_seed():
    scenario = get_scenario("constant_positive_10pct")
    w1 = SyntheticWorld.generate(scenario)
    w2 = SyntheticWorld.generate(scenario)
    np.testing.assert_array_equal(
        w1.wide_data.to_numpy(), w2.wide_data.to_numpy()
    )
    assert w1.truth_mean_relative_att == w2.truth_mean_relative_att


def test_heterogeneous_effects_vary_by_unit():
    scenario = get_scenario("heterogeneous_effects")
    world = SyntheticWorld.generate(scenario)
    effects = list(world.unit_effects.values())
    assert len(effects) >= 2
    assert len(set(round(e, 6) for e in effects)) > 1


def test_scenario_validation_errors():
    with pytest.raises(ValueError):
        SyntheticScenario(
            scenario_name="bad",
            n_geos=1,
            n_periods=10,
            treatment_start=5,
        )
