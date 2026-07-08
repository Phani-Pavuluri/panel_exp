"""Tests for TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.tbrridge_uncertainty_candidate_review_runtime_001 import (
    TbrridgeUncertaintyCandidateReviewPacket,
    _AUTH_FALSE,
    _POSITIVE_FLAGS,
    build_tbrridge_uncertainty_candidate_review_packet,
    evaluate_tbrridge_uncertainty_candidate_review,
    generate_tbrridge_uncertainty_candidate_review,
    get_runtime_metadata,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001_REPORT.md"

_PROHIBITED_SURFACES = (
    "UNCERTAINTY_APPROVAL_NOTICE",
    "CONFIDENCE_INTERVAL_CLAIM",
    "P_VALUE_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "COVERAGE_APPROVAL_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "ROI_CLAIM",
    "PRODUCTION_READOUT",
    "METHOD_PROMOTION_NOTICE",
    "PRODUCTION_COMPATIBILITY_NOTICE",
    "CATALOG_UNBLOCK_NOTICE",
)


def _clean_input(**extra: object) -> dict:
    payload = {
        "request_id": "runtime_test",
        "method_id": "TBRRidge",
        "instrument_id": "TBRRidge_Kfold",
        "estimator_family": "TBRRidge",
        "inference_family": "KFold",
        "false_confidence_audit_report": {"summary": {"audit_complete": True}},
        "kfold_leakage_diagnostic_report": {"diagnostic_status": "KFOLD_LEAKAGE_DIAGNOSTIC_READY"},
        "placebo_calibration_diagnostic_report": {"diagnostic_status": "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"},
        "coverage_validation_report": {"validation_status": "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW"},
        "interval_semantics_report": {
            "centering": "att",
            "semantics_undefined": False,
            "metric_estimand_mismatch": False,
        },
        "null_control_evidence_report": {"worlds": ["null_a", "null_b"]},
        "positive_control_evidence_report": {"worlds": ["pos_a"]},
        "regime_sensitivity_report": {"regimes": ["fold_geometry", "sample_size"]},
        "regularization_sensitivity_report": {"complete": True},
        "donor_pool_sensitivity_report": {"complete": True},
        "outlier_sensitivity_report": {"complete": True},
        "metric_estimand_alignment_report": {"metric_estimand_mismatch": False},
        "aggregate_pooled_surface_blocker_report": {"aggregate_pooled_unsupported": False},
        "statistical_promotion_threshold_report": {"complete": True},
        "production_catalog_status_report": {"catalog_blocked": True},
        "claim_authorization_boundary_report": {"complete": True},
        "method_promotion_boundary_report": {"complete": True},
        "lineage_provenance_manifest": {"run_id": "run_clean"},
    }
    payload.update(extra)
    return payload


def test_public_api_exists() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review(_clean_input())
    assert isinstance(packet, TbrridgeUncertaintyCandidateReviewPacket)
    alias = evaluate_tbrridge_uncertainty_candidate_review(_clean_input(request_id="alias"))
    assert alias.review_id == build_tbrridge_uncertainty_candidate_review_packet(
        _clean_input(request_id="alias")
    ).review_id


def test_complete_non_blocking_evidence_ready_for_restricted_review() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review(_clean_input())
    assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW"
    assert packet.failure_packet is None


def test_ready_with_restrictions_when_coverage_restricted() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review(
        _clean_input(
            coverage_validation_report={"validation_status": "COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS"}
        )
    )
    assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS"


def test_dict_input_supported() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review(_clean_input())
    assert packet.request_id == "runtime_test"


@dataclass
class _InputLike:
    request_id: str
    false_confidence_audit_report: dict
    kfold_leakage_diagnostic_report: dict
    placebo_calibration_diagnostic_report: dict
    coverage_validation_report: dict
    interval_semantics_report: dict
    null_control_evidence_report: dict
    positive_control_evidence_report: dict
    regime_sensitivity_report: dict
    regularization_sensitivity_report: dict
    donor_pool_sensitivity_report: dict
    outlier_sensitivity_report: dict
    metric_estimand_alignment_report: dict
    aggregate_pooled_surface_blocker_report: dict
    statistical_promotion_threshold_report: dict
    production_catalog_status_report: dict
    claim_authorization_boundary_report: dict
    method_promotion_boundary_report: dict
    lineage_provenance_manifest: dict


def test_dataclass_like_input_supported() -> None:
    clean = _clean_input(request_id="dc_001")
    obj = _InputLike(**{k: clean[k] for k in _InputLike.__dataclass_fields__})
    packet = generate_tbrridge_uncertainty_candidate_review(obj)
    assert packet.request_id == "dc_001"
    assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW"


def test_list_input_returns_independent_packets() -> None:
    packets = generate_tbrridge_uncertainty_candidate_review(
        [
            _clean_input(request_id="list_a"),
            _clean_input(request_id="list_b"),
        ]
    )
    assert isinstance(packets, list)
    assert len(packets) == 2
    assert packets[0].request_id == "list_a"
    assert packets[1].request_id == "list_b"
    assert packets[0].review_id != packets[1].review_id


def test_missing_evidence_chain_blocks() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review({"request_id": "empty"})
    assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "MISSING_FALSE_CONFIDENCE_AUDIT"


def test_missing_interval_semantics_blocks() -> None:
    data = _clean_input()
    del data["interval_semantics_report"]
    packet = generate_tbrridge_uncertainty_candidate_review(data)
    assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS"
    assert packet.failure_packet["failure_code"] == "INTERVAL_SEMANTICS_INCOMPLETE"


def test_leakage_blocking_status_blocks() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review(
        _clean_input(
            kfold_leakage_diagnostic_report={
                "diagnostic_status": "KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE"
            }
        )
    )
    assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC"
    assert packet.failure_packet["failure_code"] == "LEAKAGE_DIAGNOSTIC_BLOCKING"
    assert "LEAKAGE_DIAGNOSTIC_BLOCKING" in packet.detected_review_risks


def test_placebo_blocking_status_blocks() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review(
        _clean_input(
            placebo_calibration_diagnostic_report={
                "diagnostic_status": "PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION"
            }
        )
    )
    assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PLACEBO_CALIBRATION"
    assert packet.failure_packet["failure_code"] == "PLACEBO_CALIBRATION_BLOCKING"
    assert "PLACEBO_CALIBRATION_BLOCKING" in packet.detected_review_risks


def test_coverage_blocking_status_blocks() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review(
        _clean_input(
            coverage_validation_report={
                "validation_status": "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS"
            }
        )
    )
    assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_COVERAGE_VALIDATION"
    assert packet.failure_packet["failure_code"] == "COVERAGE_VALIDATION_BLOCKING"
    assert "COVERAGE_VALIDATION_BLOCKING" in packet.detected_review_risks


def test_metric_estimand_mismatch_blocks() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review(
        _clean_input(metric_estimand_alignment_report={"metric_estimand_mismatch": True})
    )
    assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH"
    assert packet.failure_packet["failure_code"] == "METRIC_ESTIMAND_MISMATCH"
    assert "METRIC_ESTIMAND_MISMATCH" in packet.detected_review_risks


def test_aggregate_pooled_unsupported_flagged() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review(
        _clean_input(aggregate_pooled_surface_blocker_report={"aggregate_pooled_unsupported": True})
    )
    assert "AGGREGATE_POOLED_SURFACE_UNSUPPORTED" in packet.detected_review_risks


def test_prohibited_surfaces_blocked() -> None:
    for surface in _PROHIBITED_SURFACES:
        packet = generate_tbrridge_uncertainty_candidate_review(_clean_input(requested_surface=surface))
        assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_REQUIRES_METHOD_REVIEW"
        assert packet.failure_packet is not None
        assert packet.failure_packet["failure_code"] == "UNCERTAINTY_APPROVAL_SURFACE_BLOCKED"


def test_production_readout_blocked_when_catalog_blocked() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review(
        _clean_input(requested_surface="PRODUCTION_READOUT")
    )
    assert packet.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_REQUIRES_METHOD_REVIEW"


def test_failure_packet_fields() -> None:
    packet = generate_tbrridge_uncertainty_candidate_review({"request_id": "fail"})
    fp = packet.failure_packet
    assert fp is not None
    assert fp["failure_code"]
    assert fp["failure_reason"]
    assert "detected_review_risks" in fp
    assert "missing_evidence" in fp
    assert fp["required_remediation"]
    assert fp["retry_category"]


def test_deterministic_review_id_and_provenance_hash() -> None:
    data = _clean_input(request_id="deterministic")
    first = generate_tbrridge_uncertainty_candidate_review(data)
    second = generate_tbrridge_uncertainty_candidate_review(data)
    assert first.review_id == second.review_id
    assert first.provenance_hash == second.provenance_hash
    assert first.review_id.startswith("tucr-")


def test_no_input_mutation() -> None:
    data = _clean_input()
    snapshot = json.dumps(data, sort_keys=True)
    generate_tbrridge_uncertainty_candidate_review(data)
    assert json.dumps(data, sort_keys=True) == snapshot


def test_forbidden_flags_false() -> None:
    meta = get_runtime_metadata()
    for flag, expected in _AUTH_FALSE.items():
        assert meta[flag] is expected, flag
    packet = generate_tbrridge_uncertainty_candidate_review(_clean_input())
    assert packet.authorization_boundary_report["computes_uncertainty"] is False
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
    assert data["uncertainty_candidate_review_runtime_implemented"] is True


def test_report_exists() -> None:
    assert _REPORT.exists()


def test_run_validation_passes() -> None:
    result = run_validation()
    assert result["failed_scenarios"] == []
