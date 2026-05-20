"""Deep immutability of nested evidence payloads."""

from __future__ import annotations

import pytest

from panel_exp.evidence import DesignEvidence
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design


def _spec():
    return spec_from_geo_design(
        "exp-immut",
        "y",
        "u",
        "t",
        TimePeriod(0, 10),
        TimePeriod(10, 30),
        "balancedrandomization",
    )


def _evidence(**kwargs):
    spec = _spec()
    defaults = dict(
        spec=spec,
        assignment={"control": ["u0"], "test_0": ["u1"]},
        validation_summary={
            "status": "WARN",
            "checks": [{"metric": "min_control_units", "status": "PASS", "message": "ok"}],
        },
        inference_metadata={"interval_type": "confidence_interval", "warnings": ["note"]},
        artifacts={"nested": {"path": "out.json"}},
        created_at="2026-01-01T00:00:00+00:00",
    )
    defaults.update(kwargs)
    return DesignEvidence.from_assignment(**defaults)


def test_assignment_tuple_elements_immutable():
    ev = _evidence()
    with pytest.raises((TypeError, AttributeError)):
        ev.assignment["control"] += ("u9",)  # type: ignore[operator]


def test_validation_summary_nested_mutation_blocked():
    ev = _evidence()
    checks = ev.validation_summary["checks"]
    with pytest.raises(TypeError):
        checks[0]["status"] = "FAIL"  # type: ignore[index]


def test_inference_metadata_nested_list_is_tuple():
    ev = _evidence()
    warnings = ev.inference_metadata.get("warnings")
    assert isinstance(warnings, tuple)
    with pytest.raises((TypeError, AttributeError)):
        warnings.append("x")  # type: ignore[attr-defined]


def test_artifacts_nested_mapping_blocked():
    ev = _evidence()
    nested = ev.artifacts["nested"]
    with pytest.raises(TypeError):
        nested["path"] = "other.json"  # type: ignore[index]


def test_caller_payload_mutation_does_not_affect_evidence():
    spec = _spec()
    assignment = {"control": ["u0"], "test_0": ["u1"]}
    control_list = assignment["control"]
    validation = {"checks": [{"status": "PASS"}]}
    ev = DesignEvidence.from_assignment(
        spec,
        assignment,
        validation_summary=validation,
        created_at="2026-01-01T00:00:00+00:00",
    )
    control_list.append("u9")
    validation["checks"][0]["status"] = "FAIL"
    assert list(ev.assignment["control"]) == ["u0"]
    assert ev.validation_summary["checks"][0]["status"] == "PASS"
