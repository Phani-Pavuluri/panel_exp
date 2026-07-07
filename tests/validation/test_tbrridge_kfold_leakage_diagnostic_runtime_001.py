"""Tests for TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.tbrridge_kfold_leakage_diagnostic_runtime_001 import (
    TbrridgeKfoldLeakageDiagnosticPacket,
    _AUTH_FALSE,
    _POSITIVE_FLAGS,
    build_tbrridge_kfold_leakage_packet,
    evaluate_tbrridge_kfold_leakage,
    generate_tbrridge_kfold_leakage_diagnostic,
    get_runtime_metadata,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001_REPORT.md"


def _clean_input(**extra: object) -> dict:
    payload = {
        "request_id": "runtime_test",
        "method_id": "TBRRidge",
        "instrument_id": "TBRRidge_Kfold",
        "estimator_family": "TBRRidge",
        "inference_family": "KFold",
        "fold_scheme": "rolling_tskfold",
        "fold_assignment_manifest": {"folds": [{"fold_id": 0, "units": ["u1", "u2"]}]},
        "treated_unit_manifest": {"treated_units": ["t1"], "geometry": "single_treated"},
        "control_unit_manifest": {"control_units": ["c1", "c2"]},
        "pre_period_window": {"start": "2024-01-01", "end": "2024-06-30"},
        "post_period_window": {"start": "2024-07-01", "end": "2024-12-31"},
        "feature_construction_manifest": {"leakage_risk": False, "uses_post_period_features": False},
        "hyperparameter_selection_manifest": {"leakage_risk": False, "uses_post_period_outcomes": False},
        "geometry_support_report": {
            "treated_geometry": "single_treated",
            "geometry_supported": True,
        },
        "temporal_split_report": {
            "pre_post_boundary_declared": True,
            "temporal_leakage": False,
            "post_period_leakage": False,
            "pre_post_boundary_leakage": False,
        },
        "fold_overlap_report": {
            "fold_overlap": False,
            "unit_overlap": False,
            "fold_assignment_instability": False,
        },
        "treated_control_separation_report": {"contamination": False, "separation_verified": True},
        "sample_size_by_fold": {"min_per_fold": 12, "degeneracy": False},
        "lineage_manifest": {"run_id": "run_clean"},
    }
    payload.update(extra)
    return payload


def test_public_api_exists() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(_clean_input())
    assert isinstance(packet, TbrridgeKfoldLeakageDiagnosticPacket)
    alias = evaluate_tbrridge_kfold_leakage(_clean_input(request_id="alias"))
    assert alias.diagnostic_id == build_tbrridge_kfold_leakage_packet(
        _clean_input(request_id="alias")
    ).diagnostic_id


def test_dict_input_supported() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(_clean_input())
    assert packet.request_id == "runtime_test"
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_DIAGNOSTIC_READY"


@dataclass
class _InputLike:
    request_id: str
    fold_assignment_manifest: dict
    treated_unit_manifest: dict
    control_unit_manifest: dict
    pre_period_window: dict
    post_period_window: dict
    feature_construction_manifest: dict
    hyperparameter_selection_manifest: dict
    geometry_support_report: dict
    temporal_split_report: dict
    fold_overlap_report: dict
    treated_control_separation_report: dict
    sample_size_by_fold: dict
    lineage_manifest: dict


def test_dataclass_like_input_supported() -> None:
    clean = _clean_input(request_id="dc_001")
    obj = _InputLike(**{k: clean[k] for k in _InputLike.__dataclass_fields__})
    packet = generate_tbrridge_kfold_leakage_diagnostic(obj)
    assert packet.request_id == "dc_001"
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_DIAGNOSTIC_READY"


def test_list_input_returns_multiple_diagnostics_without_ranking() -> None:
    packets = generate_tbrridge_kfold_leakage_diagnostic(
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


def test_missing_fold_assignment_manifest_blocks() -> None:
    data = _clean_input()
    del data["fold_assignment_manifest"]
    packet = generate_tbrridge_kfold_leakage_diagnostic(data)
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "MISSING_FOLD_ASSIGNMENT_MANIFEST"


def test_missing_temporal_split_report_blocks() -> None:
    data = _clean_input()
    del data["temporal_split_report"]
    packet = generate_tbrridge_kfold_leakage_diagnostic(data)
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "MISSING_TEMPORAL_SPLIT_REPORT"


def test_missing_geometry_support_report_blocks() -> None:
    data = _clean_input()
    del data["geometry_support_report"]
    packet = generate_tbrridge_kfold_leakage_diagnostic(data)
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "MISSING_GEOMETRY_SUPPORT_REPORT"


def test_temporal_leakage_detected() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(
        _clean_input(temporal_split_report={"temporal_leakage": True})
    )
    assert "TEMPORAL_LEAKAGE" in packet.detected_leakage_types
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "TEMPORAL_LEAKAGE_DETECTED"


def test_pre_post_boundary_leakage_detected() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(
        _clean_input(temporal_split_report={"pre_post_boundary_leakage": True})
    )
    assert "PRE_POST_BOUNDARY_LEAKAGE" in packet.detected_leakage_types
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE"


def test_treated_control_contamination_detected() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(
        _clean_input(treated_control_separation_report={"contamination": True})
    )
    assert "TREATED_CONTROL_CONTAMINATION" in packet.detected_leakage_types
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_TREATED_CONTROL_CONTAMINATION"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "TREATED_CONTROL_CONTAMINATION_DETECTED"


def test_fold_overlap_detected() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(
        _clean_input(fold_overlap_report={"fold_overlap": True})
    )
    assert "FOLD_ASSIGNMENT_INSTABILITY" in packet.detected_leakage_types
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_FOLD_OVERLAP"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "FOLD_OVERLAP_DETECTED"


def test_unsupported_multi_treated_geometry_blocked() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(
        _clean_input(
            treated_unit_manifest={"treated_units": ["t1", "t2"], "geometry": "multi_treated"},
            geometry_support_report={"treated_geometry": "multi_treated", "geometry_supported": False},
        )
    )
    assert "MULTI_TREATED_GEOMETRY_UNSUPPORTED" in packet.detected_leakage_types
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "MULTI_TREATED_GEOMETRY_UNSUPPORTED"


def test_small_sample_fold_degeneracy_blocked() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(
        _clean_input(sample_size_by_fold={"min_per_fold": 2, "degeneracy": True})
    )
    assert "SMALL_SAMPLE_FOLD_DEGENERACY" in packet.detected_leakage_types
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_SMALL_SAMPLE_GEOMETRY"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "SMALL_SAMPLE_FOLD_DEGENERACY"


def test_feature_construction_leakage_risk_flagged() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(
        _clean_input(feature_construction_manifest={"leakage_risk": True})
    )
    assert "FEATURE_CONSTRUCTION_LEAKAGE" in packet.detected_leakage_types
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_DIAGNOSTIC_READY_WITH_RESTRICTIONS"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "FEATURE_CONSTRUCTION_LEAKAGE_RISK"


def test_hyperparameter_selection_leakage_risk_flagged() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(
        _clean_input(hyperparameter_selection_manifest={"leakage_risk": True})
    )
    assert "HYPERPARAMETER_SELECTION_LEAKAGE" in packet.detected_leakage_types
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_DIAGNOSTIC_READY_WITH_RESTRICTIONS"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "HYPERPARAMETER_SELECTION_LEAKAGE_RISK"


def test_diagnostic_ready_packet_emitted_when_evidence_clean() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(_clean_input())
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_DIAGNOSTIC_READY"
    assert packet.detected_leakage_types == ()
    assert packet.failure_packet is None
    assert "DIAGNOSTIC_ONLY" in packet.allowed_surfaces
    assert "KFOLD_UNCERTAINTY_CLAIM" in packet.prohibited_surfaces


def test_kfold_uncertainty_surfaces_blocked() -> None:
    packet = generate_tbrridge_kfold_leakage_diagnostic(
        _clean_input(requested_surface="CONFIDENCE_INTERVAL_CLAIM")
    )
    assert packet.diagnostic_status == "KFOLD_LEAKAGE_REQUIRES_METHOD_REVIEW"
    assert packet.failure_packet is not None
    assert packet.failure_packet["failure_code"] == "KFOLD_UNCERTAINTY_SURFACE_BLOCKED"
    assert "CONFIDENCE_INTERVAL_CLAIM" in packet.prohibited_surfaces
    assert packet.authorization_boundary_report["kfold_uncertainty_surface_blocked"] is True


def test_deterministic_diagnostic_id_and_provenance_hash() -> None:
    data = _clean_input(request_id="deterministic")
    first = generate_tbrridge_kfold_leakage_diagnostic(data)
    second = generate_tbrridge_kfold_leakage_diagnostic(data)
    assert first.diagnostic_id == second.diagnostic_id
    assert first.provenance_hash == second.provenance_hash
    assert first.diagnostic_id.startswith("tkld-")


def test_forbidden_flags_false() -> None:
    meta = get_runtime_metadata()
    for flag, expected in _AUTH_FALSE.items():
        assert meta[flag] is expected, flag
    assert meta["kfold_inference_implemented"] is False
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
    assert data["kfold_leakage_runtime_implemented"] is True


def test_report_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert "no_kfold_inference_or_uncertainty" in text


def test_run_validation_passes() -> None:
    result = run_validation(write_summary=False)
    assert result["failed_scenarios"] == []
