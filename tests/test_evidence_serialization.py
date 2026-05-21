"""Evidence JSON round-trip, legacy keys, and versioning."""

from __future__ import annotations

import json


from panel_exp.evidence import EVIDENCE_VERSION, DesignEvidence, ExperimentEvidence
from panel_exp.evidence_hash import assignment_hash
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design


def _spec():
    return spec_from_geo_design(
        "exp-rt",
        "y",
        "u",
        "t",
        TimePeriod(0, 10),
        TimePeriod(10, 30),
        "balancedrandomization",
        random_state=3,
    )


def test_evidence_version_is_1_0():
    assert EVIDENCE_VERSION == "1.0"


def test_legacy_keys_in_to_dict():
    spec = _spec()
    ev = DesignEvidence.from_assignment(
        spec,
        {"control": ["a"], "test_0": ["b"]},
        created_at="2026-01-01T00:00:00+00:00",
        input_data_hash="abc123",
    )
    d = ev.to_dict()
    assert d["timestamp"] == d["created_at"]
    assert d["design_method"] == d["design_name"]
    assert "diagnostics" in d
    assert d["input_data_hash"] == "abc123"
    assert d["input_structure_hash"] == "abc123"


def test_json_round_trip_design_evidence():
    spec = _spec()
    assignment = {"control": ["u0", "u1"], "test_0": ["u2"]}
    created = "2026-05-01T12:00:00+00:00"
    original = DesignEvidence.from_assignment(
        spec,
        assignment,
        validation_summary={"status": "PASS", "checks": [{"metric": "x", "status": "PASS"}]},
        inference_metadata={"interval_type": "unavailable"},
        warnings=["w1"],
        errors=[],
        artifacts={"report": "path.json"},
        input_data_hash="struct01",
        created_at=created,
    )
    j1 = original.to_json()
    restored = DesignEvidence.from_json(j1)
    j2 = restored.to_json()
    assert j1 == j2
    assert restored.created_at == created
    assert restored.spec_hash == original.spec_hash
    assert restored.assignment_hash == original.assignment_hash
    assert restored.assignment_hash == assignment_hash(assignment)
    parsed = json.loads(j1)
    assert "numpy" not in j1
    assert isinstance(parsed["validation_summary"]["checks"], list)


def test_json_round_trip_experiment_evidence():
    from panel_exp.inference_result import InferenceResult, IntervalType

    spec = _spec()
    assignment = {"control": ["u0"], "test_0": ["u1"]}
    created = "2026-05-01T12:00:00+00:00"
    ir = InferenceResult.for_path_intervals(
        method="Kfold",
        alpha=0.05,
        path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
    )
    original = ExperimentEvidence.build(
        spec,
        assignment,
        inference_result=ir,
        inference_method="Kfold",
        created_at=created,
        input_data_hash="struct02",
    )
    j1 = original.to_json()
    restored = ExperimentEvidence.from_json(j1)
    j2 = restored.to_json()
    assert j1 == j2
    assert restored.created_at == created
    assert restored.inference is not None
