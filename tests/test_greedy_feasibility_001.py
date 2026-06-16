"""Production tests for greedy_match_markets feasibility fix (DES-001)."""

from __future__ import annotations

import pytest

from panel_exp.design.assign import greedy_match_markets
from panel_exp.design.greedy_feasibility import compute_greedy_feasibility
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.track_d_d5_des_stat_greedy_feasibility_001 import (
    MIN_CONTROL_THRESHOLD,
    synthesize_panel,
    _world_spec,
)


def test_default_policy_is_control_reservation() -> None:
    design = greedy_match_markets()
    assert design.feasibility_policy == "control_reservation"
    assert design.min_control_units == 1


def test_compute_greedy_feasibility_bounds() -> None:
    contract = compute_greedy_feasibility(
        n_assignable=10,
        treatment_probability=0.35,
        n_test_grps=1,
        pinned_control=0,
        pinned_test=0,
        min_control_units=3,
        policy="control_reservation",
    )
    assert contract.requested_n_treated == 3
    assert contract.max_feasible_n_treated == 7
    assert contract.min_control_units == 3


def test_public_api_backward_compatible_return_type() -> None:
    spec = _world_spec("balanced_feasible", 12, 0.5)
    wide = synthesize_panel(spec, 42)
    panel = PanelDataset(wide.copy())
    design = greedy_match_markets(treatment_probability=0.5, random_state=42)
    result = design.assign(panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1)
    assert isinstance(result, dict)
    assert "control" in result
    assert "test_0" in result
    assert isinstance(result["control"], list)


def test_legacy_policy_available_for_baseline() -> None:
    spec = _world_spec("treatment_pool_exhaustion", 10, 0.35)
    wide = synthesize_panel(spec, 101)
    panel = PanelDataset(wide.copy())
    design = greedy_match_markets(
        treatment_probability=0.35,
        random_state=101,
        feasibility_policy="legacy",
        min_control_units=MIN_CONTROL_THRESHOLD,
    )
    result = design.assign(panel_data=panel, pre_treatment_period=TimePeriod(0, 30), n_test_grps=1)
    assert design.last_feasibility_metadata is None
    assert "control" in result
