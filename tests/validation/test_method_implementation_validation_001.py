"""Smoke tests for METHOD-IMPLEMENTATION-VALIDATION-001 register."""

from __future__ import annotations

import json

from panel_exp.validation.method_implementation_validation_001 import (
    KNOWN_GAP_REGISTER,
    build_implementation_validation,
    load_layer2,
)
from panel_exp.validation.method_literature_alignment_001 import literature_families


def _strip_timestamp(payload: dict) -> dict:
    out = json.loads(json.dumps(payload))
    out.pop("generated_at", None)
    return out


def test_build_deterministic_excluding_timestamp():
    a = _strip_timestamp(build_implementation_validation())
    b = _strip_timestamp(build_implementation_validation())
    assert a == b


def test_every_layer2_family_has_layer3_row():
    payload = build_implementation_validation()
    assert payload["coverage"]["missing_layer2_family_ids"] == []
    assert payload["counts"]["layer2_families_covered"] == payload["counts"][
        "layer2_families"
    ]


def test_known_issues_in_gap_register():
    payload = build_implementation_validation()
    register = set(payload["known_gap_register"])
    assert register == set(KNOWN_GAP_REGISTER)
    blob = json.dumps(payload["rows"])
    for gap in ("INV-D1-001", "G1", "G4", "G7", "G8", "IMPL-CONF-001", "F-GEO-003"):
        assert gap in blob or gap.replace("-", "") in blob


def test_promotion_and_trust_role_always_false():
    payload = build_implementation_validation()
    for row in payload["rows"]:
        assert row["promotion_allowed"] is False
        assert row["trust_role_allowed"] is False


def test_status_values_allowed():
    payload = build_implementation_validation()
    allowed = set(payload["implementation_validation_status_values"])
    for row in payload["rows"]:
        assert row["implementation_validation_status"] in allowed


def test_layer2_family_count_matches_literature_module():
    lit = {f.family_id for f in literature_families()}
    l2 = {f["family_id"] for f in load_layer2()["families"]}
    assert lit == l2
