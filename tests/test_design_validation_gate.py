"""Post-assignment validation gate behavior."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from panel_exp.design.assign import BalancedRandomization
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.design.validation import ValidationStatus, validate_design
from tests.design_registry_helpers import make_geo_panel


def test_duplicate_assignment_fails():
    panel = make_geo_panel(seed=1, n_units=6)
    assignment = {"control": ["u0", "u1"], "test_0": ["u1", "u2"]}
    with pytest.raises(ValueError, match="blocking"):
        validate_design(panel.wide_data, assignment, block_on_fail=True)


def test_overlapping_arms_fail():
    panel = make_geo_panel(seed=2, n_units=6)
    assignment = {"control": ["u0", "u1"], "test_0": ["u1"]}
    with pytest.raises(ValueError, match="blocking"):
        validate_design(panel.wide_data, assignment, block_on_fail=True)


def test_unknown_assigned_geo_fails():
    panel = make_geo_panel(seed=3, n_units=6)
    assignment = {"control": ["u0", "ghost"], "test_0": ["u1"]}
    with pytest.raises(ValueError, match="blocking"):
        validate_design(panel.wide_data, assignment, block_on_fail=True)


def test_imbalance_warn_without_block():
    panel = make_geo_panel(seed=4, n_units=8)
    assignment = {"control": ["u0", "u1", "u2", "u3"], "test_0": ["u4", "u5"]}
    result = validate_design(
        panel.wide_data,
        assignment,
        treatment_probability=0.9,
        srm_tolerance=0.01,
        block_on_fail=False,
    )
    assert any(
        c.metric == "srm_unit_share" and c.status == ValidationStatus.WARN
        for c in result.checks
    )


def test_blocking_validation_stops_geo_pipeline(monkeypatch):
    import panel_exp.design.geo_runner as geo_runner

    panel = make_geo_panel(seed=5, n_units=8)
    geo = GeoExperimentDesign(
        panel_data=panel,
        base_randomizer_cls=BalancedRandomization,
        random_state=1,
        validate_after_assign=True,
        block_on_validation_fail=True,
        test_lengths=[28],
    )
    order: list[str] = []

    def _assign(self, panel_data=None, **kwargs):
        order.append("assign")
        return {"control": ["u0"], "test_0": ["u1"]}

    def _validate(*args, **kwargs):
        order.append("validate")
        raise ValueError("Design validation failed (blocking): min_control_units")

    def _evidence(*args, **kwargs):
        order.append("evidence")
        return MagicMock()

    def _mde(self, *args, **kwargs):
        order.append("mde")
        raise AssertionError("MDE must not run after blocking validation failure")

    monkeypatch.setattr(BalancedRandomization, "assign", _assign)
    monkeypatch.setattr(geo_runner, "validate_design", _validate)
    monkeypatch.setattr(geo_runner.ExperimentEvidence, "build", _evidence)
    monkeypatch.setattr(GeoExperimentDesign, "_calculate_sensitivity_metrics", _mde)

    with pytest.raises(ValueError, match="blocking"):
        geo.run_design()
    assert order == ["assign", "validate"]
    assert geo.last_evidence is None
