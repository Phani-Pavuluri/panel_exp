"""Smoke tests for METHOD-COMBINATION-VALIDATION-MATRIX-001 register."""

from __future__ import annotations

import json

from panel_exp.validation.method_combination_validation_matrix_001 import (
    FORBIDDEN_AUTHORIZATION_SUBSTRINGS,
    build_combination_validation_matrix,
    load_layer4,
)


def _strip_timestamp(payload: dict) -> dict:
    out = json.loads(json.dumps(payload))
    out.pop("generated_at", None)
    return out


def test_build_deterministic_excluding_timestamp():
    a = _strip_timestamp(build_combination_validation_matrix())
    b = _strip_timestamp(build_combination_validation_matrix())
    assert a == b


def test_every_layer4_combo_maps_to_matrix_row():
    l4 = load_layer4()
    payload = build_combination_validation_matrix()
    matrix_ids = {r["combination_id"] for r in payload["rows"]}
    for row in l4["rows"]:
        cid = row.get("combination_id")
        if cid:
            assert cid in matrix_ids, f"missing matrix row for Layer 4 combo {cid}"


def test_forbidden_flags_always_false():
    payload = build_combination_validation_matrix()
    for row in payload["rows"]:
        assert row["promotion_allowed"] is False
        assert row["trust_role_allowed"] is False
        assert row["calibration_signal_allowed"] is False
        assert row["mmm_allowed"] is False


def test_validation_matrix_status_allowed_enum():
    payload = build_combination_validation_matrix()
    allowed = set(payload["validation_matrix_status_values"])
    for row in payload["rows"]:
        assert row["validation_matrix_status"] in allowed


def test_allowed_next_action_allowed_enum():
    payload = build_combination_validation_matrix()
    allowed = set(payload["allowed_next_action_values"])
    for row in payload["rows"]:
        assert row["allowed_next_action"] in allowed


def test_no_forbidden_authorization_labels_in_status_fields():
    payload = build_combination_validation_matrix()
    for row in payload["rows"]:
        for field in ("validation_matrix_status", "allowed_next_action"):
            value = row[field].lower().replace("_", "-")
            for word in FORBIDDEN_AUTHORIZATION_SUBSTRINGS:
                assert word not in value, f"{word} in {field} for {row['combination_id']}"


def test_known_blocked_combos_remain_blocked():
    payload = build_combination_validation_matrix()
    by_id = {r["combination_id"]: r for r in payload["rows"]}
    for combo_id in payload["known_blocked_combos"]:
        row = by_id[combo_id]
        assert row["validation_matrix_status"] in (
            "blocked_before_oc",
            "blocked_needs_bridge",
        )


def test_required_ready_for_oc_candidates_present():
    payload = build_combination_validation_matrix()
    by_id = {r["combination_id"]: r for r in payload["rows"]}
    for combo_id in payload["known_ready_for_oc_combos"]:
        assert combo_id in by_id
        row = by_id[combo_id]
        assert row["validation_matrix_status"] in (
            "ready_for_oc_execution",
            "ready_for_oc_with_caveats",
        )


def test_augsynth_conformal_blocked():
    payload = build_combination_validation_matrix()
    row = next(r for r in payload["rows"] if r["combination_id"] == "AUGSYNTH-CONFORMAL")
    assert row["validation_matrix_status"] == "blocked_before_oc"


def test_pooled_multicell_blocked():
    payload = build_combination_validation_matrix()
    for cid in ("MCELL-POOLED-AUGSYNTH", "MCELL-POOLED-SCM-JK"):
        row = next(r for r in payload["rows"] if r["combination_id"] == cid)
        assert row["validation_matrix_status"] == "blocked_needs_bridge"


def test_supergeo_trim_blocked():
    payload = build_combination_validation_matrix()
    for cid in ("SUPERGEO-SCM-JK", "TRIM-SCM-JK", "SUPERGEO-AUGSYNTH-POINT", "TRIM-AUGSYNTH-POINT"):
        row = next(r for r in payload["rows"] if r["combination_id"] == cid)
        assert row["validation_matrix_status"] == "blocked_needs_bridge"


def test_tbr_unit_panel_blocked():
    payload = build_combination_validation_matrix()
    row = next(r for r in payload["rows"] if r["combination_id"] == "TBR-UNIT-JK")
    assert row["validation_matrix_status"] == "blocked_needs_bridge"


def test_registry_bayesian_blocked():
    payload = build_combination_validation_matrix()
    row = next(r for r in payload["rows"] if r["combination_id"] == "TBRRIDGE-BAYESIAN-REG")
    assert row["validation_matrix_status"] == "blocked_before_oc"


def test_d5_stat_execution_queue_present():
    payload = build_combination_validation_matrix()
    assert "D5-STAT-SMOKE-CALLABLE-001" in payload["d5_stat_execution_queue"]
    assert "D5-STAT-SCM-JK-001" in payload["d5_stat_execution_queue"]
