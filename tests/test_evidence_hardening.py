"""Evidence artifact contract: hashing, immutability, JSON serialization."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from panel_exp.evidence import (
    EVIDENCE_VERSION,
    DesignEvidence,
    ExperimentEvidence,
)
from panel_exp.evidence_hash import (
    EvidenceSerializationError,
    assignment_hash,
    canonical_assignment,
    canonical_json,
    canonicalize,
    stable_hash,
)
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spec_from_geo_design


def _spec(**kwargs):
    defaults = dict(
        experiment_id="exp-1",
        outcome_column="y",
        unit_column="u",
        time_column="t",
        pre_period=TimePeriod(0, 10),
        experiment_period=TimePeriod(10, 30),
        design_method="balancedrandomization",
        random_state=7,
    )
    defaults.update(kwargs)
    return spec_from_geo_design(**defaults)


def test_stable_hash_same_spec():
    s1 = _spec()
    s2 = _spec()
    assert s1.content_hash() == s2.content_hash()


def test_assignment_hash_key_order_invariant():
    a1 = {"control": ["u2", "u1"], "test_0": ["u3"]}
    a2 = {"test_0": ["u3"], "control": ["u1", "u2"]}
    assert assignment_hash(a1) == assignment_hash(a2)


def test_assignment_hash_changes_when_units_change():
    base = {"control": ["u0"], "test_0": ["u1"]}
    changed = {"control": ["u0"], "test_0": ["u2"]}
    assert assignment_hash(base) != assignment_hash(changed)


def test_canonical_json_rejects_unserializable():
    with pytest.raises(EvidenceSerializationError):
        canonicalize({"fn": lambda x: x})


def test_canonical_json_normalizes_scalars():
    payload = {"x": np.int64(3), "y": np.float64(1.5)}
    out = canonicalize(payload)
    assert out == {"x": 3, "y": 1.5}


def test_design_evidence_required_fields():
    spec = _spec()
    assignment = {"control": ["a", "b"], "test_0": ["c"]}
    ev = DesignEvidence.from_assignment(
        spec,
        assignment,
        created_at="2026-01-01T00:00:00+00:00",
    )
    d = ev.to_dict()
    assert d["evidence_version"] == EVIDENCE_VERSION
    assert d["experiment_id"] == "exp-1"
    assert d["created_at"] == "2026-01-01T00:00:00+00:00"
    assert d["package_version"]
    assert d["spec_hash"] == spec.content_hash()
    assert d["assignment_hash"] == assignment_hash(assignment)
    assert d["design_name"] == "balanced_randomization"
    assert d["assignment"] == {"control": ["a", "b"], "test_0": ["c"]}
    assert d["validation_summary"] == {}
    assert d["warnings"] == []
    assert d["errors"] == []
    assert d["artifacts"] == {}


def test_design_evidence_json_deterministic():
    spec = _spec()
    assignment = {"test_0": ["c"], "control": ["b", "a"]}
    kw = dict(spec=spec, assignment=assignment, created_at="2026-01-01T00:00:00+00:00")
    j1 = DesignEvidence.from_assignment(**kw).to_json()
    j2 = DesignEvidence.from_assignment(**kw).to_json()
    assert j1 == j2
    json.loads(j1)


def test_design_evidence_frozen_assignment():
    spec = _spec()
    ev = DesignEvidence.from_assignment(spec, {"control": ["u0"], "test_0": ["u1"]})
    with pytest.raises(TypeError):
        ev.assignment["control"] = ("x",)  # type: ignore[index]


def test_experiment_evidence_build_includes_inference_metadata():
    from panel_exp.inference_result import InferenceResult, IntervalType

    spec = _spec()
    assignment = {"control": ["u0"], "test_0": ["u1"]}
    ir = InferenceResult.for_path_intervals(
        method="UnitJackKnife",
        alpha=0.05,
        path_interval_type=IntervalType.CONFIDENCE_INTERVAL,
    )
    exp = ExperimentEvidence.build(
        spec,
        assignment,
        inference_result=ir,
        inference_method="UnitJackKnife",
        created_at="2026-01-01T00:00:00+00:00",
    )
    assert exp.inference is not None
    assert exp.inference_metadata["interval_type"] == "confidence_interval"
    assert exp.to_dict()["inference"] is not None


def test_to_dict_key_order_stable():
    spec = _spec()
    ev = DesignEvidence.from_assignment(spec, {"control": ["a"], "test_0": ["b"]})
    keys = list(ev.to_dict().keys())
    assert keys.index("evidence_version") < keys.index("assignment")
    assert keys.index("experiment_id") < keys.index("spec_hash")


def test_input_data_hash_from_wide():
    from panel_exp.evidence_hash import input_data_hash_from_wide

    wide = pd.DataFrame(
        [[1.0, 2.0], [3.0, 4.0]],
        index=["u1", "u0"],
        columns=[0, 1],
    )
    h1 = input_data_hash_from_wide(wide)
    wide2 = pd.DataFrame(
        [[1.0, 2.0], [3.0, 4.0]],
        index=["u0", "u1"],
        columns=[0, 1],
    )
    h2 = input_data_hash_from_wide(wide2)
    assert h1 == h2
