"""Tests for TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.tbrridge_method_promotion_review_runtime_001 import (
    TbrridgeMethodPromotionReviewPacket,
    _AUTH_FALSE,
    _POSITIVE_FLAGS,
    build_tbrridge_method_promotion_review_packet,
    detect_tbrridge_method_promotion_risks,
    generate_tbrridge_method_promotion_review,
    get_runtime_metadata,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md"

_PROHIBITED_SURFACES = (
    "METHOD_PROMOTION_NOTICE",
    "CATALOG_UNBLOCK_NOTICE",
    "PRODUCTION_COMPATIBILITY_NOTICE",
    "PRODUCTION_AUTHORIZATION_NOTICE",
    "PRODUCTION_READOUT",
    "UNCERTAINTY_APPROVAL_NOTICE",
    "CONFIDENCE_INTERVAL_CLAIM",
    "P_VALUE_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "ROI_CLAIM",
)


def _clean_input(**extra: object) -> dict:
    payload = {
        "request_id": "runtime_test",
        "method_id": "TBRRidge",
        "instrument_id": "TBRRidge_Kfold",
        "method_promotion_evidence_audit_report": {"summary": {"audit_complete": True}},
        "uncertainty_candidate_review_packet": {
            "review_status": "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW"
        },
        "false_confidence_audit_report": {"summary": {"audit_complete": True}},
        "leakage_diagnostic_report": {"diagnostic_status": "KFOLD_LEAKAGE_DIAGNOSTIC_READY"},
        "placebo_calibration_diagnostic_report": {"diagnostic_status": "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"},
        "coverage_validation_report": {"validation_status": "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW"},
        "interval_semantics_report": {
            "semantics_undefined": False,
            "interval_semantics_incomplete": False,
        },
        "null_control_false_positive_report": {"worlds": ["null_a"], "evidence_incomplete": False},
        "directional_error_report": {"complete": True, "evidence_incomplete": False},
        "positive_control_recovery_report": {"worlds": ["pos_a"], "recovery_failure": False},
        "regime_sensitivity_report": {"regimes": ["r1"], "sensitivity_incomplete": False},
        "donor_pool_sensitivity_report": {"complete": True},
        "regularization_sensitivity_report": {"complete": True},
        "outlier_sensitivity_report": {"complete": True},
        "fold_geometry_sensitivity_report": {"complete": True},
        "metric_estimand_alignment_report": {"metric_estimand_mismatch": False},
        "aggregate_pooled_geometry_blocker_report": {"aggregate_pooled_unsupported": False},
        "claim_authorization_boundary_report": {"complete": True},
        "production_catalog_status_report": {"catalog_blocked": True},
        "production_compatibility_boundary_report": {"production_compatibility_reviewed": True},
        "downstream_readout_safety_report": {"complete": True},
        "lineage_provenance_manifest": {"run_id": "run_clean"},
    }
    payload.update(extra)
    return payload


def test_public_api_exists() -> None:
    packet = generate_tbrridge_method_promotion_review(_clean_input())
    assert isinstance(packet, TbrridgeMethodPromotionReviewPacket)
    alias = build_tbrridge_method_promotion_review_packet(_clean_input(request_id="alias"))
    assert alias.review_id.startswith("tmpr-")


def test_complete_non_blocking_evidence_ready_for_restricted_review() -> None:
    packet = generate_tbrridge_method_promotion_review(_clean_input())
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW"
    assert packet.failure_packet is None


def test_ready_with_restrictions_when_production_compatibility_not_reviewed() -> None:
    packet = generate_tbrridge_method_promotion_review(
        _clean_input(
            production_compatibility_boundary_report={"production_compatibility_not_reviewed": True}
        )
    )
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_READY_WITH_RESTRICTIONS"
    assert "PRODUCTION_COMPATIBILITY_NOT_REVIEWED" in packet.detected_promotion_risks


def test_dict_input_supported() -> None:
    packet = generate_tbrridge_method_promotion_review(_clean_input())
    assert packet.method_id == "TBRRidge"
    assert packet.instrument_id == "TBRRidge_Kfold"


@dataclass
class _InputLike:
    request_id: str
    method_promotion_evidence_audit_report: dict
    uncertainty_candidate_review_packet: dict
    false_confidence_audit_report: dict
    leakage_diagnostic_report: dict
    placebo_calibration_diagnostic_report: dict
    coverage_validation_report: dict
    interval_semantics_report: dict
    null_control_false_positive_report: dict
    directional_error_report: dict
    positive_control_recovery_report: dict
    regime_sensitivity_report: dict
    donor_pool_sensitivity_report: dict
    regularization_sensitivity_report: dict
    outlier_sensitivity_report: dict
    fold_geometry_sensitivity_report: dict
    metric_estimand_alignment_report: dict
    aggregate_pooled_geometry_blocker_report: dict
    claim_authorization_boundary_report: dict
    production_catalog_status_report: dict
    production_compatibility_boundary_report: dict
    downstream_readout_safety_report: dict
    lineage_provenance_manifest: dict


def test_dataclass_like_input_supported() -> None:
    clean = _clean_input(request_id="dc_001")
    obj = _InputLike(**{k: clean[k] for k in _InputLike.__dataclass_fields__})
    packet = generate_tbrridge_method_promotion_review(obj)
    assert packet.review_id.startswith("tmpr-")
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW"


def test_list_input_returns_independent_packets() -> None:
    packets = generate_tbrridge_method_promotion_review(
        [
            _clean_input(request_id="list_a"),
            _clean_input(request_id="list_b"),
        ]
    )
    assert isinstance(packets, list)
    assert len(packets) == 2
    assert packets[0].review_id != packets[1].review_id


def test_missing_evidence_chain_blocks() -> None:
    packet = generate_tbrridge_method_promotion_review({"request_id": "empty"})
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "MISSING_METHOD_PROMOTION_EVIDENCE_AUDIT"


def test_missing_uncertainty_candidate_review_packet_blocks() -> None:
    data = _clean_input()
    del data["uncertainty_candidate_review_packet"]
    packet = generate_tbrridge_method_promotion_review(data)
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN"
    assert packet.failure_packet["failure_code"] == "MISSING_UNCERTAINTY_CANDIDATE_REVIEW_PACKET"


def test_blocking_uncertainty_candidate_review_blocks() -> None:
    packet = generate_tbrridge_method_promotion_review(
        _clean_input(
            uncertainty_candidate_review_packet={
                "review_status": "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC"
            }
        )
    )
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW"
    assert packet.failure_packet["failure_code"] == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING"
    assert "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING" in packet.detected_promotion_risks


def test_missing_interval_semantics_blocks() -> None:
    data = _clean_input()
    del data["interval_semantics_report"]
    packet = generate_tbrridge_method_promotion_review(data)
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS"
    assert packet.failure_packet["failure_code"] == "INTERVAL_SEMANTICS_INCOMPLETE"


def test_incomplete_interval_semantics_blocks() -> None:
    packet = generate_tbrridge_method_promotion_review(
        _clean_input(interval_semantics_report={"interval_semantics_incomplete": True})
    )
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS"
    assert "INTERVAL_SEMANTICS_INCOMPLETE" in packet.detected_promotion_risks


def test_missing_null_control_false_positive_blocks() -> None:
    data = _clean_input()
    del data["null_control_false_positive_report"]
    packet = generate_tbrridge_method_promotion_review(data)
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE"
    assert packet.failure_packet["failure_code"] == "NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE"


def test_missing_directional_error_blocks() -> None:
    data = _clean_input()
    del data["directional_error_report"]
    packet = generate_tbrridge_method_promotion_review(data)
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_DIRECTIONAL_ERROR_EVIDENCE"
    assert packet.failure_packet["failure_code"] == "DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE"


def test_missing_positive_control_recovery_blocks() -> None:
    data = _clean_input()
    del data["positive_control_recovery_report"]
    packet = generate_tbrridge_method_promotion_review(data)
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_POSITIVE_CONTROL_RECOVERY"
    assert packet.failure_packet["failure_code"] == "POSITIVE_CONTROL_RECOVERY_INCOMPLETE"


def test_missing_regime_sensitivity_blocks() -> None:
    data = _clean_input()
    del data["regime_sensitivity_report"]
    packet = generate_tbrridge_method_promotion_review(data)
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_REGIME_SENSITIVITY"
    assert packet.failure_packet["failure_code"] == "REGIME_SENSITIVITY_INCOMPLETE"


def test_metric_estimand_mismatch_blocks() -> None:
    packet = generate_tbrridge_method_promotion_review(
        _clean_input(metric_estimand_alignment_report={"metric_estimand_mismatch": True})
    )
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH"
    assert packet.failure_packet["failure_code"] == "METRIC_ESTIMAND_MISMATCH"
    assert "METRIC_ESTIMAND_MISMATCH" in packet.detected_promotion_risks


def test_aggregate_pooled_unsupported_blocks() -> None:
    packet = generate_tbrridge_method_promotion_review(
        _clean_input(aggregate_pooled_geometry_blocker_report={"aggregate_pooled_unsupported": True})
    )
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_AGGREGATE_POOLED_GEOMETRY"
    assert packet.failure_packet["failure_code"] == "AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED"
    assert "AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED" in packet.detected_promotion_risks


def test_missing_claim_authorization_boundary_blocks() -> None:
    data = _clean_input()
    del data["claim_authorization_boundary_report"]
    packet = generate_tbrridge_method_promotion_review(data)
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY"
    assert packet.failure_packet["failure_code"] == "CLAIM_AUTHORIZATION_BOUNDARY_MISSING"


def test_production_catalog_blocked_flagged() -> None:
    packet = generate_tbrridge_method_promotion_review(_clean_input())
    assert "PRODUCTION_CATALOG_BLOCKED" in packet.detected_promotion_risks
    assert packet.current_catalog_status == "BLOCKED"


def test_production_compatibility_not_reviewed_requires_review_for_production_surface() -> None:
    packet = generate_tbrridge_method_promotion_review(
        _clean_input(
            requested_surface="PRODUCTION_COMPATIBILITY_NOTICE",
            production_compatibility_boundary_report={"production_compatibility_not_reviewed": True},
        )
    )
    assert packet.review_status == "METHOD_PROMOTION_REVIEW_REQUIRES_PRODUCTION_COMPATIBILITY_REVIEW"
    assert packet.failure_packet["failure_code"] == "PRODUCTION_COMPATIBILITY_NOT_REVIEWED"


def test_prohibited_surfaces_blocked() -> None:
    for surface in _PROHIBITED_SURFACES:
        packet = generate_tbrridge_method_promotion_review(_clean_input(requested_surface=surface))
        assert packet.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY"
        assert packet.failure_packet is not None
        assert packet.failure_packet["failure_code"] == "METHOD_PROMOTION_SURFACE_BLOCKED"


def test_failure_packet_fields() -> None:
    packet = generate_tbrridge_method_promotion_review({"request_id": "fail"})
    fp = packet.failure_packet
    assert fp is not None
    assert fp["failure_code"]
    assert fp["failure_reason"]
    assert "detected_promotion_risks" in fp
    assert "missing_evidence" in fp
    assert fp["required_remediation"]
    assert fp["retry_category"]


def test_detect_promotion_risks() -> None:
    risks = detect_tbrridge_method_promotion_risks(
        _clean_input(
            interval_semantics_report={"interval_semantics_incomplete": True},
            production_catalog_status_report={"catalog_blocked": True},
        )
    )
    assert "INTERVAL_SEMANTICS_INCOMPLETE" in risks
    assert "PRODUCTION_CATALOG_BLOCKED" in risks


def test_deterministic_review_id_and_provenance_hash() -> None:
    data = _clean_input(request_id="deterministic")
    first = generate_tbrridge_method_promotion_review(data)
    second = generate_tbrridge_method_promotion_review(data)
    assert first.review_id == second.review_id
    assert first.provenance_hash == second.provenance_hash
    assert first.review_id.startswith("tmpr-")


def test_no_input_mutation() -> None:
    data = _clean_input()
    snapshot = json.dumps(data, sort_keys=True)
    generate_tbrridge_method_promotion_review(data)
    assert json.dumps(data, sort_keys=True) == snapshot


def test_forbidden_flags_false() -> None:
    meta = get_runtime_metadata()
    for flag, expected in _AUTH_FALSE.items():
        assert meta[flag] is expected, flag
    packet = generate_tbrridge_method_promotion_review(_clean_input())
    assert packet.authorization_boundary_report["authorizes_method_promotion"] is False
    assert packet.authorization_boundary_report["authorizes_uncertainty"] is False


def test_positive_runtime_flags() -> None:
    meta = get_runtime_metadata()
    for flag, expected in _POSITIVE_FLAGS.items():
        assert meta[flag] is expected, flag


def test_summary_json_matches_runtime() -> None:
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    meta = get_runtime_metadata()
    assert data["artifact_id"] == meta["artifact_id"]
    assert data["final_verdict"] == meta["final_verdict"]
    assert data["method_promotion_review_runtime_implemented"] is True


def test_report_exists() -> None:
    assert _REPORT.exists()


def test_run_validation_passes() -> None:
    result = run_validation()
    assert result["failed_scenarios"] == []
