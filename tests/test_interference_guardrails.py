"""Interference / spillover assumption guardrails (metadata only, no estimation)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from panel_exp.design.assign import BalancedRandomization
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.design.validation import ValidationStatus, validate_design
from panel_exp.evidence import DesignEvidence, ExperimentEvidence
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import (
    InterferenceAssumption,
    interference_evidence_metadata,
    spec_from_geo_design,
    spillover_metadata_available,
)
from tests.design_registry_helpers import make_geo_panel


def _assignment(panel):
    n = len(panel.units)
    return {"control": list(panel.units[: n // 2]), "test_0": list(panel.units[n // 2 :])}


def test_default_unknown_produces_warn():
    panel = make_geo_panel(seed=1, n_units=8)
    result = validate_design(
        panel.wide_data,
        _assignment(panel),
        interference=InterferenceAssumption.UNKNOWN,
        block_on_fail=False,
    )
    check = next(c for c in result.checks if c.metric == "interference_assumption")
    assert check.status == ValidationStatus.WARN
    assert "does not estimate spillovers" in check.message


def test_explicit_no_interference_records_pass_not_warn():
    panel = make_geo_panel(seed=2, n_units=8)
    result = validate_design(
        panel.wide_data,
        _assignment(panel),
        interference=InterferenceAssumption.NO_INTERFERENCE,
        block_on_fail=False,
    )
    check = next(c for c in result.checks if c.metric == "interference_assumption")
    assert check.status == ValidationStatus.PASS
    assert "User declared" in check.message


def test_partial_interference_without_metadata_warns():
    panel = make_geo_panel(seed=3, n_units=8)
    result = validate_design(
        panel.wide_data,
        _assignment(panel),
        interference=InterferenceAssumption.PARTIAL_INTERFERENCE,
        spillover_metadata_available=False,
        block_on_fail=False,
    )
    check = next(c for c in result.checks if c.metric == "interference_assumption")
    assert check.status == ValidationStatus.WARN
    assert "no spillover metadata" in check.message


def test_partial_interference_with_metadata_passes_check():
    panel = make_geo_panel(seed=4, n_units=8)
    result = validate_design(
        panel.wide_data,
        _assignment(panel),
        interference=InterferenceAssumption.PARTIAL_INTERFERENCE,
        spillover_metadata_available=True,
        block_on_fail=False,
    )
    check = next(c for c in result.checks if c.metric == "interference_assumption")
    assert check.status == ValidationStatus.PASS


def test_evidence_includes_interference_metadata():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 10),
        TimePeriod(10, 30),
        "balancedrandomization",
        interference=InterferenceAssumption.UNKNOWN,
        random_state=1,
    )
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["a", "b"], "test_0": ["c"]},
        warnings=["Interference assumption is unknown."],
    )
    meta = dict(ev.inference_metadata)
    assert meta["interference_assumption"] == "unknown"
    assert meta["spillover_metadata_available"] is False
    assert meta["spillover_estimation_available"] is False


def test_spillover_metadata_available_from_optional_fields():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 10),
        TimePeriod(10, 30),
        "balancedrandomization",
        interference=InterferenceAssumption.PARTIAL_INTERFERENCE,
        spillover_notes="DMA adjacency documented offline",
    )
    assert spillover_metadata_available(spec) is True


def test_blocking_validation_still_blocks(monkeypatch):
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

    def _assign(self, panel_data=None, **kwargs):
        return {"control": ["u0"], "test_0": ["u1"]}

    def _validate(*args, **kwargs):
        raise ValueError("Design validation failed (blocking): min_control_units")

    monkeypatch.setattr(BalancedRandomization, "assign", _assign)
    monkeypatch.setattr(geo_runner, "validate_design", _validate)
    monkeypatch.setattr(geo_runner.ExperimentEvidence, "build", MagicMock())

    with pytest.raises(ValueError, match="blocking"):
        geo.run_design()
    assert geo.last_evidence is None


def test_design_outputs_unchanged_assignment_keys():
    panel = make_geo_panel(seed=6, n_units=8)
    design = BalancedRandomization(treatment_probability=0.33, random_state=0)
    out = design.assign(panel_data=panel, n_test_grps=1)
    assert "control" in out and "test_0" in out


def test_interference_evidence_metadata_unknown_note():
    spec = spec_from_geo_design(
        "e1",
        "y",
        "u",
        "t",
        TimePeriod(0, 5),
        TimePeriod(5, 10),
        "balancedrandomization",
        interference=InterferenceAssumption.UNKNOWN,
    )
    meta = interference_evidence_metadata(spec)
    assert meta["interference_assumption"] == "unknown"
    assert "unknown" in meta["interference_note"].lower()
