"""Smoke tests for METHOD-STATISTICAL-VALIDATION-PROTOCOL-001 register."""

from __future__ import annotations

import json

from panel_exp.validation.method_statistical_validation_protocol_001 import (
    BATTERY_LEVELS,
    DGP_WORLD_CATALOG,
    METRIC_CATALOG,
    build_statistical_validation_protocol,
    load_layer3,
)


def _strip_timestamp(payload: dict) -> dict:
    out = json.loads(json.dumps(payload))
    out.pop("generated_at", None)
    return out


def test_build_deterministic_excluding_timestamp():
    a = _strip_timestamp(build_statistical_validation_protocol())
    b = _strip_timestamp(build_statistical_validation_protocol())
    assert a == b


def test_every_layer3_row_mapped():
    l3 = load_layer3()
    payload = build_statistical_validation_protocol()
    blob = json.dumps(payload["rows"])
    for row in l3["rows"]:
        fam = row["method_family"]
        impl = row["implementation_name"]
        key = f"{fam}:{impl}"
        assert key in blob or fam in blob, f"missing Layer 3 mapping for {key}"


def test_forbidden_flags_always_false():
    payload = build_statistical_validation_protocol()
    for row in payload["rows"]:
        assert row["promotion_allowed"] is False
        assert row["trust_role_allowed"] is False
        assert row["calibration_signal_allowed"] is False
        assert row["mmm_allowed"] is False


def test_battery_levels_valid():
    payload = build_statistical_validation_protocol()
    allowed = set(BATTERY_LEVELS)
    for row in payload["rows"]:
        assert row["battery_level"] in allowed


def test_metric_catalog_includes_required_metrics():
    required = {
        "null_false_positive_rate",
        "empirical_coverage",
        "bias",
        "mae",
        "interval_width",
        "interval_orientation_validity",
        "degenerate_interval_rate",
        "shock_sensitivity",
        "donor_count_sensitivity",
        "outside_hull_sensitivity",
    }
    assert required.issubset(set(METRIC_CATALOG))
    payload = build_statistical_validation_protocol()
    used = set()
    for row in payload["rows"]:
        used.update(row["required_metrics"])
    assert required.issubset(used)


def test_known_blocked_combos_remain_blocked():
    payload = build_statistical_validation_protocol()
    by_id = {r["combination_id"]: r for r in payload["rows"] if r["combination_id"]}
    blocked_ids = payload["known_blocked_combos"]
    for combo_id in blocked_ids:
        row = by_id[combo_id]
        assert row["eligible_for_layer4"] is False
        assert row["eligibility_status"] in (
            "blocked_by_implementation_gap",
            "blocked_by_architecture_gap",
            "blocked_by_geometry",
        )


def test_dgp_world_catalog_present():
    payload = build_statistical_validation_protocol()
    assert set(payload["dgp_world_catalog"]) == set(DGP_WORLD_CATALOG)


def test_augsynth_conformal_blocked():
    payload = build_statistical_validation_protocol()
    row = next(r for r in payload["rows"] if r["combination_id"] == "AUGSYNTH-CONFORMAL")
    assert row["eligible_for_layer4"] is False
    assert "IMPL-CONF-001" in json.dumps(row["blocked_by"])


def test_pooled_multicell_blocked():
    payload = build_statistical_validation_protocol()
    row = next(r for r in payload["rows"] if r["combination_id"] == "MCELL-POOLED-AUGSYNTH")
    assert row["eligible_for_layer4"] is False
    assert row["eligibility_status"] == "blocked_by_geometry"


def test_supergeo_trim_blocked_without_bridge():
    payload = build_statistical_validation_protocol()
    for combo_id in ("SUPERGEO-SCM-JK", "TRIM-SCM-JK"):
        row = next(r for r in payload["rows"] if r["combination_id"] == combo_id)
        assert row["eligible_for_layer4"] is False
        assert row["eligibility_status"] == "blocked_by_geometry"


def test_tbr_unit_panel_jk_blocked():
    payload = build_statistical_validation_protocol()
    row = next(r for r in payload["rows"] if r["combination_id"] == "TBR-UNIT-JK")
    assert row["eligible_for_layer4"] is False
    assert row["eligibility_status"] == "blocked_by_geometry"


def test_registry_bayesian_production_blocked():
    payload = build_statistical_validation_protocol()
    row = next(r for r in payload["rows"] if r["combination_id"] == "TBRRIDGE-BAYESIAN-REG")
    assert row["eligible_for_layer4"] is False
    assert row["eligibility_status"] == "blocked_by_architecture_gap"
