"""Assignment and input fingerprint hash semantics."""

from __future__ import annotations

import tempfile

import pandas as pd
import pytest

from panel_exp.evidence_hash import (
    EvidenceSerializationError,
    assignment_hash,
    canonical_json,
    canonicalize,
    input_data_hash_from_wide,
    input_structure_hash_from_wide,
    stable_hash,
)


def test_assignment_hash_unit_order_within_arm_invariant():
    a = {"control": ["u2", "u1"], "test_0": ["u3"]}
    b = {"control": ["u1", "u2"], "test_0": ["u3"]}
    assert assignment_hash(a) == assignment_hash(b)


def test_assignment_hash_arm_dict_key_order_invariant():
    a = {"control": ["u1"], "test_0": ["u2"]}
    b = {"test_0": ["u2"], "control": ["u1"]}
    assert assignment_hash(a) == assignment_hash(b)


def test_assignment_hash_unit_moved_between_arms_changes():
    a = {"control": ["u0", "u1"], "test_0": []}
    b = {"control": ["u0"], "test_0": ["u1"]}
    assert assignment_hash(a) != assignment_hash(b)


def test_assignment_hash_multi_arm_label_semantics():
    a = {"test_0": ["A"], "test_1": ["B"]}
    b = {"test_0": ["B"], "test_1": ["A"]}
    assert assignment_hash(a) != assignment_hash(b)


def test_input_structure_hash_ignores_value_changes():
    wide1 = pd.DataFrame([[1.0, 2.0], [3.0, 4.0]], index=["u0", "u1"], columns=[0, 1])
    wide2 = pd.DataFrame([[9.0, 9.0], [9.0, 9.0]], index=["u0", "u1"], columns=[0, 1])
    assert input_structure_hash_from_wide(wide1) == input_structure_hash_from_wide(wide2)


def test_input_data_hash_alias_matches_structure_hash():
    wide = pd.DataFrame([[1.0]], index=["u0"], columns=[0])
    assert input_data_hash_from_wide(wide) == input_structure_hash_from_wide(wide)


def test_stable_hash_rejects_callable():
    with pytest.raises(EvidenceSerializationError, match="Cannot canonicalize"):
        stable_hash({"fn": lambda x: x})


def test_stable_hash_rejects_plain_object():
    with pytest.raises(EvidenceSerializationError, match="Cannot canonicalize"):
        canonicalize(object())


def test_stable_hash_rejects_open_file_handle():
    with tempfile.NamedTemporaryFile(mode="w") as tmp:
        with pytest.raises(EvidenceSerializationError, match="Cannot canonicalize"):
            canonical_json({"f": tmp})
