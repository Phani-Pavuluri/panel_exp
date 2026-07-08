"""Tests for TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.tbrridge_kfold_coverage_validation_runtime_001 import (
    TbrridgeKfoldCoverageValidationPacket,
    _AUTH_FALSE,
    _POSITIVE_FLAGS,
    build_tbrridge_kfold_coverage_validation_packet,
    evaluate_tbrridge_kfold_coverage_validation,
    generate_tbrridge_kfold_coverage_validation,
    get_runtime_metadata,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001_REPORT.md"

_PROHIBITED_SURFACES = (
    "COVERAGE_APPROVAL_CLAIM",
    "CONFIDENCE_INTERVAL_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "P_VALUE_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "ROI_CLAIM",
    "PRODUCTION_READOUT",
    "METHOD_PROMOTION_NOTICE",
    "UNCERTAINTY_AUTHORIZATION_NOTICE",
)


def _clean_input(**extra: object) -> dict:
    payload = {
        "request_id": "runtime_test",
        "method_id": "TBRRidge",
        "instrument_id": "TBRRidge_Kfold",
        "estimator_family": "TBRRidge",
        "inference_family": "KFold",
        "interval_semantics": "fold_cv_dispersion_surrogate",
        "nominal_coverage_target": 0.9,
        "leakage_diagnostic_report": {"diagnostic_status": "KFOLD_LEAKAGE_DIAGNOSTIC_READY"},
        "placebo_calibration_diagnostic_report": {"diagnostic_status": "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"},
        "interval_semantics_report": {
            "centering": "att",
            "width_construction": "fold_cv",
            "semantics_undefined": False,
            "metric_estimand_mismatch": False,
        },
        "simulation_design_manifest": {
            "world_regimes": ["null_world", "positive_world"],
            "aggregate_pooled_misuse_risk": False,
            "estimand_mismatch": False,
        },
        "null_control_manifest": {"worlds": ["null_a", "null_b"]},
        "positive_control_manifest": {"worlds": ["pos_a"], "recovery_failure": False},
        "synthetic_effect_injection_manifest": {"regimes": ["small_effect"], "recovery_failure": False},
        "fold_geometry_regime_manifest": {"regimes": ["single_treated"], "geometry_sensitivity": False},
        "sample_size_regime_manifest": {"regimes": ["medium_n"], "size_sensitivity": False},
        "regularization_grid_manifest": {"alphas": [0.1, 1.0], "alpha_sensitivity": False},
        "donor_pool_sensitivity_report": {"donor_sensitivity": False},
        "outlier_sensitivity_report": {"outlier_sensitivity": False},
        "empirical_coverage_report": {
            "summary": {"empirical_coverage": 0.88, "nominal_coverage_target": 0.9},
            "undercoverage_risk": False,
            "overcoverage": False,
            "coverage_mismatch": False,
        },
        "false_positive_rate_report": {"elevated_fpr": False, "false_positive_risk": False},
        "directional_error_report": {"directional_false_signal": False},
        "placebo_calibrated_tail_report": {"tail_mismatch": False},
        "failure_packet_manifest": {"schema_version": "1"},
        "lineage_manifest": {"run_id": "run_clean"},
    }
    payload.update(extra)
    return payload


def test_public_api_exists() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(_clean_input())
    assert isinstance(packet, TbrridgeKfoldCoverageValidationPacket)
    alias = evaluate_tbrridge_kfold_coverage_validation(_clean_input(request_id="alias"))
    assert alias.validation_id == build_tbrridge_kfold_coverage_validation_packet(
        _clean_input(request_id="alias")
    ).validation_id


def test_dict_input_supported() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(_clean_input())
    assert packet.request_id == "runtime_test"
    assert packet.validation_status == "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW"


@dataclass
class _InputLike:
    request_id: str
    interval_semantics: str
    nominal_coverage_target: float
    leakage_diagnostic_report: dict
    placebo_calibration_diagnostic_report: dict
    interval_semantics_report: dict
    simulation_design_manifest: dict
    null_control_manifest: dict
    positive_control_manifest: dict
    synthetic_effect_injection_manifest: dict
    fold_geometry_regime_manifest: dict
    sample_size_regime_manifest: dict
    regularization_grid_manifest: dict
    donor_pool_sensitivity_report: dict
    outlier_sensitivity_report: dict
    empirical_coverage_report: dict
    false_positive_rate_report: dict
    directional_error_report: dict
    placebo_calibrated_tail_report: dict
    failure_packet_manifest: dict
    lineage_manifest: dict


def test_dataclass_like_input_supported() -> None:
    clean = _clean_input(request_id="dc_001")
    obj = _InputLike(**{k: clean[k] for k in _InputLike.__dataclass_fields__})
    packet = generate_tbrridge_kfold_coverage_validation(obj)
    assert packet.request_id == "dc_001"
    assert packet.validation_status == "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW"


def test_list_input_returns_multiple_packets_without_ranking() -> None:
    packets = generate_tbrridge_kfold_coverage_validation(
        [
            _clean_input(request_id="list_a"),
            _clean_input(request_id="list_b"),
        ]
    )
    assert isinstance(packets, list)
    assert len(packets) == 2
    assert packets[0].request_id == "list_a"
    assert packets[1].request_id == "list_b"
    assert packets[0].validation_id != packets[1].validation_id


def test_missing_leakage_diagnostic_blocks() -> None:
    data = _clean_input()
    del data["leakage_diagnostic_report"]
    packet = generate_tbrridge_kfold_coverage_validation(data)
    assert packet.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "MISSING_LEAKAGE_DIAGNOSTIC_REPORT"


def test_blocking_leakage_diagnostic_blocks() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(
            leakage_diagnostic_report={
                "diagnostic_status": "KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE"
            }
        )
    )
    assert packet.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "LEAKAGE_DIAGNOSTIC_BLOCKING"
    assert "TEMPORAL_LEAKAGE_DEPENDENCY" in packet.detected_coverage_risks


def test_missing_placebo_calibration_diagnostic_blocks() -> None:
    data = _clean_input()
    del data["placebo_calibration_diagnostic_report"]
    packet = generate_tbrridge_kfold_coverage_validation(data)
    assert packet.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION"
    assert packet.failure_packet["failure_code"] == "MISSING_PLACEBO_CALIBRATION_DIAGNOSTIC_REPORT"


def test_blocking_placebo_calibration_diagnostic_blocks() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(
            placebo_calibration_diagnostic_report={
                "diagnostic_status": "PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION"
            }
        )
    )
    assert packet.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_PLACEBO_MISCALIBRATION"
    assert packet.failure_packet["failure_code"] == "PLACEBO_CALIBRATION_BLOCKING"
    assert "PLACEBO_MISCALIBRATION_DEPENDENCY" in packet.detected_coverage_risks


def test_missing_interval_semantics_blocks() -> None:
    data = _clean_input()
    del data["interval_semantics_report"]
    packet = generate_tbrridge_kfold_coverage_validation(data)
    assert packet.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS"
    assert packet.failure_packet["failure_code"] == "MISSING_INTERVAL_SEMANTICS_REPORT"


def test_undefined_interval_semantics_blocks() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(interval_semantics_report={"semantics_undefined": True})
    )
    assert packet.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS"
    assert "INTERVAL_SEMANTICS_UNDEFINED" in packet.detected_coverage_risks


def test_missing_simulation_design_blocks() -> None:
    data = _clean_input()
    del data["simulation_design_manifest"]
    packet = generate_tbrridge_kfold_coverage_validation(data)
    assert packet.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_SIMULATION_DESIGN"
    assert packet.failure_packet["failure_code"] == "MISSING_SIMULATION_DESIGN_MANIFEST"


def test_missing_null_control_manifest_blocks() -> None:
    data = _clean_input()
    del data["null_control_manifest"]
    packet = generate_tbrridge_kfold_coverage_validation(data)
    assert packet.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_NULL_CONTROL"
    assert packet.failure_packet["failure_code"] == "MISSING_NULL_CONTROL_MANIFEST"


def test_missing_positive_control_manifest_blocks() -> None:
    data = _clean_input()
    del data["positive_control_manifest"]
    packet = generate_tbrridge_kfold_coverage_validation(data)
    assert packet.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_POSITIVE_CONTROL"
    assert packet.failure_packet["failure_code"] == "MISSING_POSITIVE_CONTROL_MANIFEST"


def test_missing_regime_manifests_block() -> None:
    data = _clean_input()
    del data["fold_geometry_regime_manifest"]
    packet = generate_tbrridge_kfold_coverage_validation(data)
    assert packet.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_REGIME_COVERAGE"
    assert packet.failure_packet["failure_code"] == "MISSING_REGIME_MANIFEST"


def test_clean_supplied_reports_produce_diagnostic_review_ready() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(_clean_input())
    assert packet.validation_status == "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW"
    assert packet.empirical_coverage_summary.get("empirical_coverage") == 0.88


def test_supplied_undercoverage_risk_flagged_without_computing_coverage() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(empirical_coverage_report={"undercoverage_risk": True, "summary": {"empirical_coverage": 0.5}})
    )
    assert "UNDERCOVERAGE_RISK" in packet.detected_coverage_risks
    assert packet.validation_status == "COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS"
    assert packet.authorization_boundary_report["computes_coverage"] is False


def test_supplied_overcoverage_risk_flagged() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(empirical_coverage_report={"uninformative_interval_risk": True})
    )
    assert "OVERCOVERAGE_UNINFORMATIVE_INTERVAL_RISK" in packet.detected_coverage_risks


def test_supplied_false_positive_risk_flagged() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(false_positive_rate_report={"null_false_positive_risk": True})
    )
    assert "NULL_FALSE_POSITIVE_RISK" in packet.detected_coverage_risks


def test_supplied_directional_false_signal_risk_flagged() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(directional_error_report={"directional_false_signal_risk": True})
    )
    assert "DIRECTIONAL_FALSE_SIGNAL_RISK" in packet.detected_coverage_risks


def test_supplied_positive_control_recovery_failure_flagged() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(positive_control_manifest={"recovery_failure": True, "worlds": ["pos_a"]})
    )
    assert "POSITIVE_CONTROL_RECOVERY_FAILURE" in packet.detected_coverage_risks
    assert packet.validation_status == "COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS"


def test_supplied_placebo_calibrated_tail_mismatch_flagged() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(placebo_calibrated_tail_report={"placebo_calibrated_tail_mismatch": True})
    )
    assert "PLACEBO_CALIBRATED_TAIL_MISMATCH" in packet.detected_coverage_risks


def test_supplied_sensitivity_risks_flagged() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(
            fold_geometry_regime_manifest={"regimes": ["a"], "geometry_sensitivity": True},
            sample_size_regime_manifest={"regimes": ["b"], "size_sensitivity": True},
            donor_pool_sensitivity_report={"donor_pool_sensitivity": True},
            regularization_grid_manifest={"alphas": [1.0], "regularization_sensitivity": True},
            outlier_sensitivity_report={"outlier_week_sensitivity": True},
        )
    )
    risks = set(packet.detected_coverage_risks)
    assert "FOLD_GEOMETRY_SENSITIVITY" in risks
    assert "SAMPLE_SIZE_SENSITIVITY" in risks
    assert "DONOR_POOL_SENSITIVITY" in risks
    assert "REGULARIZATION_SENSITIVITY" in risks
    assert "OUTLIER_WEEK_SENSITIVITY" in risks


def test_aggregate_pooled_misuse_risk_flagged() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(simulation_design_manifest={"aggregate_pooled_misuse_risk": True})
    )
    assert "AGGREGATE_POOLED_MISUSE_RISK" in packet.detected_coverage_risks


def test_metric_estimand_mismatch_flagged() -> None:
    packet = generate_tbrridge_kfold_coverage_validation(
        _clean_input(interval_semantics_report={"semantics_undefined": False, "metric_estimand_mismatch": True})
    )
    assert "METRIC_ESTIMAND_MISMATCH" in packet.detected_coverage_risks


def test_prohibited_surfaces_blocked() -> None:
    for surface in _PROHIBITED_SURFACES:
        packet = generate_tbrridge_kfold_coverage_validation(_clean_input(requested_surface=surface))
        assert packet.validation_status == "COVERAGE_VALIDATION_REQUIRES_METHOD_REVIEW"
        assert packet.failure_packet is not None
        assert packet.failure_packet["failure_code"] == "COVERAGE_APPROVAL_SURFACE_BLOCKED"
        assert surface in packet.prohibited_surfaces


def test_deterministic_validation_id_and_provenance_hash() -> None:
    data = _clean_input(request_id="deterministic")
    first = generate_tbrridge_kfold_coverage_validation(data)
    second = generate_tbrridge_kfold_coverage_validation(data)
    assert first.validation_id == second.validation_id
    assert first.provenance_hash == second.provenance_hash
    assert first.validation_id.startswith("tkcv-")


def test_forbidden_flags_false() -> None:
    meta = get_runtime_metadata()
    for flag, expected in _AUTH_FALSE.items():
        assert meta[flag] is expected, flag
    packet = generate_tbrridge_kfold_coverage_validation(_clean_input())
    assert packet.authorization_boundary_report["computes_coverage"] is False
    assert packet.authorization_boundary_report["computes_intervals"] is False
    assert packet.authorization_boundary_report["empirical_coverage_computed"] is False


def test_positive_runtime_flags() -> None:
    meta = get_runtime_metadata()
    for flag, expected in _POSITIVE_FLAGS.items():
        assert meta[flag] is expected, flag


def test_summary_json_matches_runtime() -> None:
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    meta = get_runtime_metadata()
    assert data["artifact_id"] == meta["artifact_id"]
    assert data["final_verdict"] == meta["final_verdict"]
    assert data["coverage_validation_runtime_implemented"] is True


def test_report_exists() -> None:
    assert _REPORT.exists()


def test_run_validation_passes() -> None:
    result = run_validation()
    assert result["failed_scenarios"] == []


def test_no_fixture_specific_branching_in_runtime_source() -> None:
    source = (_REPO / "panel_exp/validation/tbrridge_kfold_coverage_validation_runtime_001.py").read_text()
    assert "fixture_id" not in source
    assert "case_id" not in source
    assert "Scenario A" not in source
    assert "Scenario B" not in source
    assert "Scenario C" not in source
