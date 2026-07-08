"""Tests for TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.tbrridge_placebo_calibration_diagnostic_runtime_001 import (
    TbrridgePlaceboCalibrationDiagnosticPacket,
    _AUTH_FALSE,
    _POSITIVE_FLAGS,
    build_tbrridge_placebo_calibration_packet,
    evaluate_tbrridge_placebo_calibration,
    generate_tbrridge_placebo_calibration_diagnostic,
    get_runtime_metadata,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001_REPORT.md"


def _clean_input(**extra: object) -> dict:
    payload = {
        "request_id": "runtime_test",
        "method_id": "TBRRidge",
        "instrument_id": "TBRRidge_Placebo",
        "estimator_family": "TBRRidge",
        "inference_family": "Placebo",
        "placebo_scheme": "pseudo_treated_replay",
        "placebo_assignment_manifest": {"placebos": [{"id": str(i)} for i in range(25)]},
        "pseudo_treated_unit_manifest": {"units": ["u1"], "geometry": "single_treated"},
        "placebo_control_unit_manifest": {"units": ["c1", "c2"], "geometry": "pooled_control"},
        "null_period_definition": {"pre_treatment_only": True, "invalid_null_period": False},
        "placebo_window_manifest": {"window_start": "2024-01-01", "window_end": "2024-06-30"},
        "placebo_metric_manifest": {"metric": "att", "metric_mismatch": False},
        "placebo_geometry_report": {"unbalanced_geometry": False},
        "placebo_contamination_report": {
            "contamination_detected": False,
            "pseudo_treated_contamination": False,
            "donor_overlap_detected": False,
        },
        "placebo_count_report": {"placebo_count": 25, "insufficient_placebo_count": False},
        "placebo_rank_tail_report": {"tail_instability": False, "rank_instability": False},
        "placebo_directionality_report": {
            "directional_sign_instability": False,
            "pre_period_fit_overconfidence": False,
        },
        "placebo_outlier_influence_report": {"outlier_influence": False},
        "regularization_sensitivity_report": {"masked_placebo_failure": False},
        "lineage_manifest": {"run_id": "run_clean"},
    }
    payload.update(extra)
    return payload


def test_public_api_exists() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(_clean_input())
    assert isinstance(packet, TbrridgePlaceboCalibrationDiagnosticPacket)
    alias = evaluate_tbrridge_placebo_calibration(_clean_input(request_id="alias"))
    assert alias.diagnostic_id == build_tbrridge_placebo_calibration_packet(
        _clean_input(request_id="alias")
    ).diagnostic_id


def test_dict_input_supported() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(_clean_input())
    assert packet.request_id == "runtime_test"
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"


@dataclass
class _InputLike:
    request_id: str
    placebo_scheme: str
    placebo_assignment_manifest: dict
    pseudo_treated_unit_manifest: dict
    placebo_control_unit_manifest: dict
    null_period_definition: dict
    placebo_window_manifest: dict
    placebo_metric_manifest: dict
    placebo_geometry_report: dict
    placebo_contamination_report: dict
    placebo_count_report: dict
    placebo_rank_tail_report: dict
    placebo_directionality_report: dict
    placebo_outlier_influence_report: dict
    regularization_sensitivity_report: dict
    lineage_manifest: dict


def test_dataclass_like_input_supported() -> None:
    clean = _clean_input(request_id="dc_001")
    obj = _InputLike(**{k: clean[k] for k in _InputLike.__dataclass_fields__})
    packet = generate_tbrridge_placebo_calibration_diagnostic(obj)
    assert packet.request_id == "dc_001"
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"


def test_list_input_returns_multiple_diagnostics_without_ranking() -> None:
    packets = generate_tbrridge_placebo_calibration_diagnostic(
        [
            _clean_input(request_id="list_a"),
            _clean_input(request_id="list_b"),
        ]
    )
    assert isinstance(packets, list)
    assert len(packets) == 2
    assert packets[0].request_id == "list_a"
    assert packets[1].request_id == "list_b"
    assert packets[0].diagnostic_id != packets[1].diagnostic_id


def test_missing_placebo_assignment_manifest_blocks() -> None:
    data = _clean_input()
    del data["placebo_assignment_manifest"]
    packet = generate_tbrridge_placebo_calibration_diagnostic(data)
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_MISSING_PLACEBO_MANIFEST"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "MISSING_PLACEBO_ASSIGNMENT_MANIFEST"


def test_missing_null_period_definition_blocks() -> None:
    data = _clean_input()
    del data["null_period_definition"]
    packet = generate_tbrridge_placebo_calibration_diagnostic(data)
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_MISSING_PLACEBO_MANIFEST"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "MISSING_NULL_PERIOD_DEFINITION"


def test_invalid_null_construction_blocks() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(null_period_definition={"invalid_null_period": True})
    )
    assert "INVALID_NULL_PERIOD" in packet.detected_placebo_risks
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_INVALID_NULL_CONSTRUCTION"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "INVALID_NULL_CONSTRUCTION"


def test_insufficient_placebo_count_blocks() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(placebo_count_report={"placebo_count": 5})
    )
    assert "INSUFFICIENT_PLACEBO_COUNT" in packet.detected_placebo_risks
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_INSUFFICIENT_PLACEBOS"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "INSUFFICIENT_PLACEBO_COUNT"


def test_placebo_contamination_detected() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(placebo_contamination_report={"pseudo_treated_contamination": True})
    )
    assert "PSEUDO_TREATED_CONTAMINATION" in packet.detected_placebo_risks
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "PLACEBO_CONTAMINATION_DETECTED"


def test_placebo_donor_control_overlap_detected() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(placebo_contamination_report={"placebo_donor_overlap": True})
    )
    assert "PLACEBO_DONOR_OVERLAP" in packet.detected_placebo_risks
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION"


def test_unbalanced_placebo_geometry_detected() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(placebo_geometry_report={"unbalanced_geometry": True})
    )
    assert "UNBALANCED_PLACEBO_GEOMETRY" in packet.detected_placebo_risks
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "PLACEBO_GEOMETRY_UNBALANCED"


def test_rank_tail_instability_flagged() -> None:
    tail_packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(placebo_rank_tail_report={"tail_instability": True})
    )
    assert "PLACEBO_TAIL_INSTABILITY" in tail_packet.detected_placebo_risks
    assert tail_packet.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_DIRECTIONAL_INSTABILITY"
    assert tail_packet.failure_packet is not None
    assert tail_packet.failure_packet["failure_code"] == "PLACEBO_TAIL_INSTABILITY_DETECTED"

    rank_packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(placebo_rank_tail_report={"rank_instability": True})
    )
    assert "PLACEBO_RANK_INSTABILITY" in rank_packet.detected_placebo_risks
    assert rank_packet.failure_packet is not None
    assert rank_packet.failure_packet["failure_code"] == "PLACEBO_RANK_INSTABILITY_DETECTED"


def test_directional_sign_instability_flagged() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(placebo_directionality_report={"directional_sign_instability": True})
    )
    assert "DIRECTIONAL_SIGN_INSTABILITY" in packet.detected_placebo_risks
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_DIRECTIONAL_INSTABILITY"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "DIRECTIONAL_SIGN_INSTABILITY_DETECTED"


def test_outlier_placebo_influence_flagged() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(placebo_outlier_influence_report={"outlier_influence": True})
    )
    assert "OUTLIER_PLACEBO_INFLUENCE" in packet.detected_placebo_risks
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_OUTLIER_INFLUENCE"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "OUTLIER_PLACEBO_INFLUENCE_DETECTED"


def test_pre_period_fit_overconfidence_flagged() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(placebo_directionality_report={"pre_period_fit_overconfidence": True})
    )
    assert "PRE_PERIOD_FIT_OVERCONFIDENCE" in packet.detected_placebo_risks
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "PRE_PERIOD_FIT_OVERCONFIDENCE_RISK"


def test_regularization_masked_placebo_failure_flagged() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(regularization_sensitivity_report={"masked_placebo_failure": True})
    )
    assert "REGULARIZATION_MASKED_PLACEBO_FAILURE" in packet.detected_placebo_risks
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "REGULARIZATION_MASKED_PLACEBO_FAILURE_RISK"


def test_metric_mismatch_flagged() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(placebo_metric_manifest={"metric_mismatch": True})
    )
    assert "PLACEBO_METRIC_MISMATCH" in packet.detected_placebo_risks
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "PLACEBO_TAIL_RANK_INSTABILITY"


def test_failed_kfold_leakage_dependency_propagates_restriction_blocker() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(
        _clean_input(
            kfold_leakage_diagnostic_report={
                "diagnostic_status": "KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE"
            }
        )
    )
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS"
    assert "DEPENDENT_KFOLD_LEAKAGE_BLOCKED" in packet.restrictions
    assert any("KFold leakage dependency blocked" in blocker for blocker in packet.blockers)


def test_diagnostic_ready_packet_emitted_when_required_evidence_clean() -> None:
    packet = generate_tbrridge_placebo_calibration_diagnostic(_clean_input())
    assert packet.diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"
    assert packet.detected_placebo_risks == ()
    assert packet.failure_packet is None
    assert "DIAGNOSTIC_ONLY" in packet.allowed_surfaces
    assert "PLACEBO_P_VALUE_CLAIM" in packet.prohibited_surfaces


def test_placebo_inference_surfaces_blocked() -> None:
    for surface in (
        "PLACEBO_P_VALUE_CLAIM",
        "STATISTICAL_SIGNIFICANCE_CLAIM",
        "CONFIDENCE_INTERVAL_CLAIM",
        "COVERAGE_CLAIM",
        "CAUSAL_LIFT_CLAIM",
        "ROI_CLAIM",
    ):
        packet = generate_tbrridge_placebo_calibration_diagnostic(_clean_input(requested_surface=surface))
        assert packet.diagnostic_status == "PLACEBO_CALIBRATION_REQUIRES_METHOD_REVIEW"
        assert packet.failure_packet is not None
        assert packet.failure_packet["failure_code"] == "PLACEBO_SIGNIFICANCE_SURFACE_BLOCKED"
        assert packet.authorization_boundary_report["placebo_inference_surfaces_blocked"] is True


def test_deterministic_diagnostic_id_and_provenance_hash() -> None:
    data = _clean_input(request_id="deterministic")
    first = generate_tbrridge_placebo_calibration_diagnostic(data)
    second = generate_tbrridge_placebo_calibration_diagnostic(data)
    assert first.diagnostic_id == second.diagnostic_id
    assert first.provenance_hash == second.provenance_hash
    assert first.diagnostic_id.startswith("tpcd-")


def test_forbidden_flags_false() -> None:
    meta = get_runtime_metadata()
    for flag, expected in _AUTH_FALSE.items():
        assert meta[flag] is expected, flag
    assert meta["placebo_inference_implemented"] is False
    assert meta["coverage_computed"] is False


def test_positive_flags_true() -> None:
    meta = get_runtime_metadata()
    for flag, expected in _POSITIVE_FLAGS.items():
        assert meta[flag] is expected, flag


def test_summary_json_matches_runtime() -> None:
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    meta = get_runtime_metadata()
    assert data["artifact_id"] == meta["artifact_id"]
    assert data["final_verdict"] == meta["final_verdict"]
    assert data["placebo_calibration_runtime_implemented"] is True


def test_report_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert "no_placebo_inference_or_uncertainty" in text


def test_run_validation_passes() -> None:
    result = run_validation(write_summary=False)
    assert result["failed_scenarios"] == []
