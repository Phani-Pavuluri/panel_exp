"""Smoke tests for DESIGN-ESTIMATOR-INFERENCE-SUITABILITY-FRAMEWORK-001."""

from __future__ import annotations

import json

from panel_exp.validation.design_estimator_inference_suitability_framework_001 import (
    FORBIDDEN_CLASS_SUBSTRINGS,
    RECOMMENDED_NEXT_ARTIFACT,
    build_suitability_framework,
    load_layer5_matrix,
)


def _strip_timestamp(payload: dict) -> dict:
    out = json.loads(json.dumps(payload))
    out.pop("generated_at", None)
    return out


def test_build_deterministic_excluding_timestamp():
    a = _strip_timestamp(build_suitability_framework())
    b = _strip_timestamp(build_suitability_framework())
    assert a == b


def test_every_layer5_row_maps_exactly_once():
    l5 = load_layer5_matrix()
    payload = build_suitability_framework()
    matrix_ids = {r["combination_id"] for r in l5["rows"]}
    framework_ids = {r["combination_id"] for r in payload["rows"]}
    assert framework_ids == matrix_ids
    assert payload["counts"]["rows_total"] == len(matrix_ids)


def test_forbidden_flags_always_false():
    payload = build_suitability_framework()
    for row in payload["rows"]:
        assert row["promotion_allowed"] is False
        assert row["trust_role_allowed"] is False
        assert row["calibration_signal_allowed"] is False
        assert row["mmm_allowed"] is False
        assert row["llm_recommendation_allowed"] is False


def test_no_forbidden_authorization_in_suitability_class():
    payload = build_suitability_framework()
    allowed = set(payload["suitability_class_values"])
    for row in payload["rows"]:
        cls = row["suitability_class"]
        assert cls in allowed
        normalized = cls.replace("_", " ")
        for word in FORBIDDEN_CLASS_SUBSTRINGS:
            assert word.replace("_", " ") not in normalized, (
                f"{word} in suitability_class for {row['combination_id']}"
            )


def test_ready_for_oc_not_suitable_without_evidence():
    l5 = load_layer5_matrix()
    payload = build_suitability_framework()
    by_id = {r["combination_id"]: r for r in payload["rows"]}
    ready_matrix_ids = {
        r["combination_id"]
        for r in l5["rows"]
        if r["validation_matrix_status"]
        in ("ready_for_oc_execution", "ready_for_oc_with_caveats")
    }
    non_promoted_classes = {
        "oc_ready_not_suitable_yet",
        "diagnostic_candidate_pending_oc",
        "suitability_candidate_pending_oc",
        "not_yet_assessed",
    }
    for cid in ready_matrix_ids:
        assert by_id[cid]["suitability_class"] in non_promoted_classes
        suit_ev = by_id[cid]["minimum_evidence_before_suitability_claim"].lower()
        assert (
            "d5-stat" in suit_ev
            and (
                "not satisfied" in suit_ev
                or "blocked" in suit_ev
                or "requires" in suit_ev
            )
        )


def test_known_blocked_combos_stay_blocked():
    payload = build_suitability_framework()
    by_id = {r["combination_id"]: r for r in payload["rows"]}
    blocked_classes = {
        "blocked_before_suitability",
        "bridge_required_before_suitability",
        "implementation_fix_required",
    }
    for combo_id in payload["known_blocked_combos"]:
        assert by_id[combo_id]["suitability_class"] in blocked_classes


def test_augsynth_conformal_blocked():
    payload = build_suitability_framework()
    row = next(r for r in payload["rows"] if r["combination_id"] == "AUGSYNTH-CONFORMAL")
    assert row["suitability_class"] == "blocked_before_suitability"


def test_augsynth_jk_implementation_fix():
    payload = build_suitability_framework()
    row = next(r for r in payload["rows"] if r["combination_id"] == "AUGSYNTH-JK")
    assert row["suitability_class"] == "implementation_fix_required"


def test_pooled_multicell_bridge_required():
    payload = build_suitability_framework()
    for cid in ("MCELL-POOLED-AUGSYNTH", "MCELL-POOLED-SCM-JK"):
        row = next(r for r in payload["rows"] if r["combination_id"] == cid)
        assert row["suitability_class"] == "bridge_required_before_suitability"


def test_supergeo_trim_bridge_required():
    payload = build_suitability_framework()
    for cid in ("SUPERGEO-SCM-JK", "TRIM-SCM-JK", "SUPERGEO-AUGSYNTH-POINT", "TRIM-AUGSYNTH-POINT"):
        row = next(r for r in payload["rows"] if r["combination_id"] == cid)
        assert row["suitability_class"] == "bridge_required_before_suitability"


def test_tbr_unit_panel_blocked():
    payload = build_suitability_framework()
    row = next(r for r in payload["rows"] if r["combination_id"] == "TBR-UNIT-JK")
    assert row["suitability_class"] == "blocked_before_suitability"


def test_registry_bayesian_blocked():
    payload = build_suitability_framework()
    row = next(r for r in payload["rows"] if r["combination_id"] == "TBRRIDGE-BAYESIAN-REG")
    assert row["suitability_class"] == "blocked_before_suitability"


def test_next_concrete_artifact_is_smoke():
    payload = build_suitability_framework()
    assert payload["recommended_next_concrete_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert RECOMMENDED_NEXT_ARTIFACT == "D5-STAT-SMOKE-CALLABLE-001"
