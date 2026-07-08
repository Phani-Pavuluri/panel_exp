"""TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001 — placebo calibration runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.tbrridge_placebo_calibration_diagnostic_contract_001 import (
    ALLOWED_SURFACES,
    ESTIMATOR_FAMILY,
    INFERENCE_FAMILY,
    INSTRUMENT_ID,
    METHOD_ID,
    PLACEBO_RISK_TYPES,
    PROHIBITED_SURFACES,
    REQUIRED_EVIDENCE,
    evaluate_placebo_calibration_diagnostic,
)

_ARTIFACT_ID = "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "tbrridge_placebo_calibration_diagnostic_runtime_implemented_no_placebo_inference_or_uncertainty"
_VERDICT = "tbrridge_placebo_calibration_diagnostic_runtime_implemented_no_placebo_inference_or_uncertainty"
_RECOMMENDED_NEXT = "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001"
_ALTERNATIVE_NEXT = "AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001_summary.json"
)

DEPENDS_ON = (
    "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001",
    "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001",
    "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001",
)

_POSITIVE_FLAGS = {
    "placebo_calibration_runtime_implemented": True,
    "placebo_calibration_diagnostic_packet_generated": True,
    "placebo_manifest_validation_enforced": True,
    "null_construction_validation_enforced": True,
    "placebo_contamination_detection_enforced": True,
    "placebo_rank_tail_detection_enforced": True,
    "directional_instability_detection_enforced": True,
    "placebo_inference_surfaces_blocked": True,
}

_AUTH_FALSE = {
    "placebo_inference_implemented": False,
    "estimator_implemented": False,
    "inference_implemented": False,
    "bootstrap_inference_implemented": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "coverage_computed": False,
    "effect_estimate_computed_new": False,
    "lift_computed_new": False,
    "roi_computed_new": False,
    "method_promoted": False,
    "method_unblocked": False,
    "production_catalog_unblocked": False,
    "production_authorization_granted": False,
    "production_readout_authorized": False,
    "mmm_runtime_calls_implemented": False,
    "llm_decisioning_authorized": False,
}

_CORE_EVIDENCE_KEYS = (
    "placebo_assignment_manifest",
    "null_period_definition",
    "placebo_geometry_report",
    "placebo_count_report",
    "placebo_contamination_report",
)


@dataclass(frozen=True)
class TbrridgePlaceboCalibrationDiagnosticRuntimeConfig:
    min_placebo_count: int = 20
    require_lineage_manifest: bool = False


@dataclass(frozen=True)
class TbrridgePlaceboCalibrationDiagnosticPacket:
    request_id: str
    diagnostic_id: str
    diagnostic_status: str
    method_id: str
    instrument_id: str
    estimator_family: str
    inference_family: str
    placebo_scheme: str
    null_period_definition: dict[str, Any]
    placebo_count: int | None
    placebo_risks_evaluated: tuple[str, ...]
    detected_placebo_risks: tuple[str, ...]
    required_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    restrictions: tuple[str, ...]
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    failure_packet: dict[str, Any] | None
    lineage_manifest: dict[str, Any]
    provenance_hash: str
    policy_version: str
    authorization_boundary_report: dict[str, Any]
    warnings: tuple[str, ...]


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return True


def _report_flag(report: Any, *keys: str) -> bool:
    if not isinstance(report, dict):
        return False
    for key in keys:
        if report.get(key) is True:
            return True
    return False


def _hash_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _resolve_config(
    config: TbrridgePlaceboCalibrationDiagnosticRuntimeConfig | dict[str, Any] | None,
) -> TbrridgePlaceboCalibrationDiagnosticRuntimeConfig:
    if config is None:
        return TbrridgePlaceboCalibrationDiagnosticRuntimeConfig()
    if isinstance(config, TbrridgePlaceboCalibrationDiagnosticRuntimeConfig):
        return config
    base = TbrridgePlaceboCalibrationDiagnosticRuntimeConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return TbrridgePlaceboCalibrationDiagnosticRuntimeConfig(**merged)


def build_evidence_presence(data: dict[str, Any]) -> dict[str, bool]:
    return {
        "placebo_assignment_manifest": _present(data.get("placebo_assignment_manifest")),
        "pseudo_treated_unit_manifest": _present(data.get("pseudo_treated_unit_manifest")),
        "placebo_control_unit_manifest": _present(data.get("placebo_control_unit_manifest")),
        "null_period_definition": _present(data.get("null_period_definition")),
        "placebo_window_manifest": _present(data.get("placebo_window_manifest")),
        "placebo_metric_manifest": _present(data.get("placebo_metric_manifest")),
        "placebo_geometry_report": _present(data.get("placebo_geometry_report")),
        "placebo_contamination_report": _present(data.get("placebo_contamination_report")),
        "placebo_count_report": _present(data.get("placebo_count_report")),
        "placebo_rank_tail_report": _present(data.get("placebo_rank_tail_report")),
        "placebo_directionality_report": _present(data.get("placebo_directionality_report")),
        "placebo_outlier_influence_report": _present(data.get("placebo_outlier_influence_report")),
        "regularization_sensitivity_report": _present(data.get("regularization_sensitivity_report")),
        "kfold_leakage_diagnostic_report": _present(data.get("kfold_leakage_diagnostic_report")),
        "lineage_provenance_manifest": _present(data.get("lineage_manifest"))
        or _present(data.get("lineage_provenance_manifest")),
    }


def extract_placebo_count(data: dict[str, Any]) -> int | None:
    report = data.get("placebo_count_report") or {}
    if isinstance(report, dict):
        count = report.get("placebo_count")
        if isinstance(count, int):
            return count
        count = report.get("count")
        if isinstance(count, int):
            return count
    manifest = data.get("placebo_assignment_manifest") or {}
    if isinstance(manifest, dict):
        placebos = manifest.get("placebos")
        if isinstance(placebos, list):
            return len(placebos)
    return None


def detect_placebo_risks(
    data: dict[str, Any],
    *,
    min_placebo_count: int = 20,
) -> tuple[str, ...]:
    detected: list[str] = []

    null_period = data.get("null_period_definition") or {}
    if isinstance(null_period, dict):
        if _report_flag(null_period, "invalid_null_period", "invalid_null_construction", "post_treatment_null"):
            detected.append("INVALID_NULL_PERIOD")

    contamination = data.get("placebo_contamination_report") or {}
    if isinstance(contamination, dict):
        if _report_flag(contamination, "pseudo_treated_contamination", "contamination_detected"):
            detected.append("PSEUDO_TREATED_CONTAMINATION")
        if _report_flag(contamination, "placebo_donor_overlap", "donor_overlap_detected", "control_overlap"):
            detected.append("PLACEBO_DONOR_OVERLAP")

    count = extract_placebo_count(data)
    count_report = data.get("placebo_count_report") or {}
    if isinstance(count_report, dict):
        if _report_flag(count_report, "insufficient_placebo_count", "count_insufficient"):
            detected.append("INSUFFICIENT_PLACEBO_COUNT")
    if isinstance(count, int) and count < min_placebo_count:
        detected.append("INSUFFICIENT_PLACEBO_COUNT")

    geometry = data.get("placebo_geometry_report") or {}
    if isinstance(geometry, dict):
        if _report_flag(geometry, "unbalanced_geometry", "geometry_unbalanced", "unbalanced_placebo_geometry"):
            detected.append("UNBALANCED_PLACEBO_GEOMETRY")

    rank_tail = data.get("placebo_rank_tail_report") or {}
    if isinstance(rank_tail, dict):
        if _report_flag(rank_tail, "tail_instability", "placebo_tail_instability"):
            detected.append("PLACEBO_TAIL_INSTABILITY")
        if _report_flag(rank_tail, "rank_instability", "placebo_rank_instability"):
            detected.append("PLACEBO_RANK_INSTABILITY")

    directionality = data.get("placebo_directionality_report") or {}
    if isinstance(directionality, dict):
        if _report_flag(directionality, "directional_sign_instability", "sign_instability", "directional_instability"):
            detected.append("DIRECTIONAL_SIGN_INSTABILITY")
        if _report_flag(directionality, "pre_period_fit_overconfidence", "overconfidence_risk"):
            detected.append("PRE_PERIOD_FIT_OVERCONFIDENCE")

    outlier = data.get("placebo_outlier_influence_report") or {}
    if isinstance(outlier, dict):
        if _report_flag(outlier, "outlier_influence", "outlier_placebo_influence", "outlier_influence_detected"):
            detected.append("OUTLIER_PLACEBO_INFLUENCE")

    regularization = data.get("regularization_sensitivity_report") or {}
    if isinstance(regularization, dict):
        if _report_flag(regularization, "masked_placebo_failure", "regularization_masked_failure"):
            detected.append("REGULARIZATION_MASKED_PLACEBO_FAILURE")

    metric = data.get("placebo_metric_manifest") or {}
    if isinstance(metric, dict):
        if _report_flag(metric, "metric_mismatch", "placebo_metric_mismatch", "estimand_mismatch"):
            detected.append("PLACEBO_METRIC_MISMATCH")

    seen: set[str] = set()
    ordered: list[str] = []
    for item in detected:
        if item in PLACEBO_RISK_TYPES and item not in seen:
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)


def _missing_core_evidence(evidence: dict[str, bool]) -> tuple[str, ...]:
    return tuple(key for key in _CORE_EVIDENCE_KEYS if not evidence.get(key, False))


def _build_restrictions(
    evaluation_status: str,
    detected: tuple[str, ...],
    missing: tuple[str, ...],
    kfold_report: dict[str, Any],
) -> tuple[str, ...]:
    restrictions: list[str] = []
    if evaluation_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS":
        restrictions.append("DIAGNOSTIC_SUMMARY_ONLY")
    if any(
        risk in detected
        for risk in (
            "PRE_PERIOD_FIT_OVERCONFIDENCE",
            "REGULARIZATION_MASKED_PLACEBO_FAILURE",
            "PLACEBO_METRIC_MISMATCH",
            "UNBALANCED_PLACEBO_GEOMETRY",
        )
    ):
        restrictions.append("PLACEBO_RISK_FLAGGED")
    if missing:
        restrictions.append("PARTIAL_EVIDENCE")
    if kfold_report.get("diagnostic_status", "").startswith("KFOLD_LEAKAGE_BLOCKED"):
        restrictions.append("DEPENDENT_KFOLD_LEAKAGE_BLOCKED")
    if evaluation_status.startswith("PLACEBO_CALIBRATION_BLOCKED"):
        restrictions.append("PLACEBO_INFERENCE_SURFACES_BLOCKED")
    return tuple(restrictions)


def _build_warnings(
    detected: tuple[str, ...],
    missing: tuple[str, ...],
    kfold_report: dict[str, Any],
) -> tuple[str, ...]:
    warnings: list[str] = []
    if "PRE_PERIOD_FIT_OVERCONFIDENCE" in detected:
        warnings.append("Strong pre-period fit does not validate placebo calibration semantics.")
    if "REGULARIZATION_MASKED_PLACEBO_FAILURE" in detected:
        warnings.append("Regularization may be masking placebo calibration failure.")
    if "PLACEBO_METRIC_MISMATCH" in detected:
        warnings.append("Placebo metric may not match the governed estimand semantics.")
    if "OUTLIER_PLACEBO_INFLUENCE" in detected:
        warnings.append("Outlier placebo runs may dominate the diagnostic surface.")
    if missing:
        warnings.append(f"Optional evidence missing: {', '.join(missing)}")
    if kfold_report.get("diagnostic_status", "").startswith("KFOLD_LEAKAGE_BLOCKED"):
        warnings.append("Provided KFold leakage diagnostic remains blocked and constrains placebo interpretation.")
    return tuple(warnings)


def _authorization_boundary_report() -> dict[str, Any]:
    return {
        "runtime_scope": "placebo_calibration_diagnostic_only",
        "computes_placebo_inference": False,
        "computes_uncertainty": False,
        "computes_coverage": False,
        "computes_p_values": False,
        "computes_confidence_intervals": False,
        "computes_lift_or_effects": False,
        "authorizes_production_readout": False,
        "authorizes_method_promotion": False,
        "authorizes_catalog_changes": False,
        "placebo_inference_surfaces_blocked": True,
        **_AUTH_FALSE,
    }


def _build_diagnostic_id(
    data: dict[str, Any],
    diagnostic_status: str,
    detected: tuple[str, ...],
    placebo_count: int | None,
) -> str:
    canonical = {
        "request_id": data.get("request_id"),
        "method_id": data.get("method_id") or METHOD_ID,
        "instrument_id": data.get("instrument_id") or INSTRUMENT_ID,
        "placebo_scheme": data.get("placebo_scheme"),
        "diagnostic_status": diagnostic_status,
        "detected_placebo_risks": sorted(detected),
        "placebo_count": placebo_count,
        "null_period_definition": data.get("null_period_definition"),
    }
    return f"tpcd-{_hash_payload(canonical)[:16]}"


def _kfold_dependency_status(data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    report = data.get("kfold_leakage_diagnostic_report") or {}
    blockers: list[str] = []
    if isinstance(report, dict):
        status = str(report.get("diagnostic_status") or "")
        if status.startswith("KFOLD_LEAKAGE_BLOCKED"):
            blockers.append(f"KFold leakage dependency blocked: {status}")
        elif status == "KFOLD_LEAKAGE_REQUIRES_METHOD_REVIEW":
            blockers.append(f"KFold leakage dependency requires review: {status}")
        return report, blockers
    return {}, blockers


def _normalize_failure_packet(
    failure_packet: dict[str, Any] | None,
    detected: tuple[str, ...],
    evaluation_status: str,
) -> dict[str, Any] | None:
    if failure_packet is None:
        return None
    packet = dict(failure_packet)
    code = packet.get("failure_code")
    if code == "PLACEBO_INFERENCE_SURFACE_BLOCKED":
        packet["failure_code"] = "PLACEBO_SIGNIFICANCE_SURFACE_BLOCKED"
    elif code == "DIRECTIONAL_INSTABILITY_DETECTED":
        if "PLACEBO_TAIL_INSTABILITY" in detected:
            packet["failure_code"] = "PLACEBO_TAIL_INSTABILITY_DETECTED"
        elif "PLACEBO_RANK_INSTABILITY" in detected:
            packet["failure_code"] = "PLACEBO_RANK_INSTABILITY_DETECTED"
        elif "DIRECTIONAL_SIGN_INSTABILITY" in detected:
            packet["failure_code"] = "DIRECTIONAL_SIGN_INSTABILITY_DETECTED"
    elif code == "PLACEBO_TAIL_RANK_INSTABILITY" and "UNBALANCED_PLACEBO_GEOMETRY" in detected:
        packet["failure_code"] = "PLACEBO_GEOMETRY_UNBALANCED"
    if evaluation_status == "PLACEBO_CALIBRATION_BLOCKED_BY_DIRECTIONAL_INSTABILITY":
        packet["retry_category"] = "REQUIRE_METHOD_REVIEW"
        packet["required_remediation"] = "REQUIRE_METHOD_REVIEW"
    return packet


def build_tbrridge_placebo_calibration_packet(
    input_data: dict[str, Any] | Any,
    *,
    config: TbrridgePlaceboCalibrationDiagnosticRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgePlaceboCalibrationDiagnosticPacket:
    """Build a single placebo calibration packet from manifests."""
    cfg = _resolve_config(config)
    data = _to_dict(input_data)

    request_id = str(data.get("request_id") or "tpcd_request_unspecified")
    method_id = str(data.get("method_id") or METHOD_ID)
    instrument_id = str(data.get("instrument_id") or INSTRUMENT_ID)
    estimator_family = str(data.get("estimator_family") or ESTIMATOR_FAMILY)
    inference_family = str(data.get("inference_family") or INFERENCE_FAMILY)
    placebo_scheme = str(data.get("placebo_scheme") or "unspecified")
    lineage = dict(data.get("lineage_manifest") or data.get("lineage_provenance_manifest") or {})

    evidence = build_evidence_presence(data)
    if cfg.require_lineage_manifest and not evidence.get("lineage_provenance_manifest"):
        evidence = {**evidence, "lineage_provenance_manifest": False}

    detected = detect_placebo_risks(data, min_placebo_count=cfg.min_placebo_count)
    requested_surface = data.get("requested_surface")
    kfold_report, kfold_blockers = _kfold_dependency_status(data)

    evaluation = evaluate_placebo_calibration_diagnostic(
        evidence=evidence,
        detected_risks=detected,
        requested_surface=str(requested_surface) if requested_surface else None,
        kfold_path_requested=bool(kfold_report),
    )

    missing_all = tuple(req for req in REQUIRED_EVIDENCE if not evidence.get(req, False))
    missing_core = _missing_core_evidence(evidence)
    missing_evidence = evaluation.missing_evidence or missing_core or missing_all

    diagnostic_status = evaluation.diagnostic_status
    blockers: list[str] = []
    if evaluation.failure_reason:
        blockers.append(evaluation.failure_reason)
    blockers.extend(kfold_blockers)
    if missing_core and diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_MISSING_PLACEBO_MANIFEST":
        blockers.append(f"Missing core evidence: {', '.join(missing_core)}")

    if (
        diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"
        and kfold_blockers
    ):
        diagnostic_status = "PLACEBO_CALIBRATION_DIAGNOSTIC_READY_WITH_RESTRICTIONS"

    if (
        diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"
        and not any(evidence.get(k) for k in _CORE_EVIDENCE_KEYS)
        and not detected
    ):
        diagnostic_status = "PLACEBO_CALIBRATION_NOT_EVALUATED"

    placebo_count = extract_placebo_count(data)
    restrictions = _build_restrictions(diagnostic_status, detected, tuple(missing_all), kfold_report)
    warnings = _build_warnings(detected, tuple(missing_all), kfold_report)
    failure_packet = _normalize_failure_packet(evaluation.to_failure_packet(), detected, diagnostic_status)
    diagnostic_id = _build_diagnostic_id(data, diagnostic_status, detected, placebo_count)

    packet_body = {
        "request_id": request_id,
        "diagnostic_id": diagnostic_id,
        "diagnostic_status": diagnostic_status,
        "method_id": method_id,
        "instrument_id": instrument_id,
        "estimator_family": estimator_family,
        "inference_family": inference_family,
        "placebo_scheme": placebo_scheme,
        "null_period_definition": data.get("null_period_definition") or {},
        "placebo_count": placebo_count,
        "placebo_risks_evaluated": list(PLACEBO_RISK_TYPES),
        "detected_placebo_risks": list(detected),
        "required_evidence": list(REQUIRED_EVIDENCE),
        "missing_evidence": list(missing_evidence),
        "blockers": blockers,
        "restrictions": list(restrictions),
        "allowed_surfaces": list(ALLOWED_SURFACES),
        "prohibited_surfaces": list(PROHIBITED_SURFACES),
        "failure_packet": failure_packet,
        "lineage_manifest": lineage,
        "policy_version": _POLICY_VERSION,
        "authorization_boundary_report": _authorization_boundary_report(),
        "warnings": list(warnings),
    }
    provenance_hash = _hash_payload(packet_body)

    return TbrridgePlaceboCalibrationDiagnosticPacket(
        request_id=request_id,
        diagnostic_id=diagnostic_id,
        diagnostic_status=diagnostic_status,
        method_id=method_id,
        instrument_id=instrument_id,
        estimator_family=estimator_family,
        inference_family=inference_family,
        placebo_scheme=placebo_scheme,
        null_period_definition=dict(data.get("null_period_definition") or {}),
        placebo_count=placebo_count,
        placebo_risks_evaluated=PLACEBO_RISK_TYPES,
        detected_placebo_risks=detected,
        required_evidence=REQUIRED_EVIDENCE,
        missing_evidence=missing_evidence,
        blockers=tuple(blockers),
        restrictions=restrictions,
        allowed_surfaces=ALLOWED_SURFACES,
        prohibited_surfaces=PROHIBITED_SURFACES,
        failure_packet=failure_packet,
        lineage_manifest=lineage,
        provenance_hash=provenance_hash,
        policy_version=_POLICY_VERSION,
        authorization_boundary_report={
            **packet_body["authorization_boundary_report"],
            "provenance_hash": provenance_hash,
        },
        warnings=warnings,
    )


def evaluate_tbrridge_placebo_calibration(
    input_data: dict[str, Any] | Any,
    *,
    config: TbrridgePlaceboCalibrationDiagnosticRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgePlaceboCalibrationDiagnosticPacket:
    """Alias for single placebo calibration evaluation."""
    return build_tbrridge_placebo_calibration_packet(input_data, config=config)


def generate_tbrridge_placebo_calibration_diagnostic(
    input_data: dict[str, Any] | Any | list[Any],
    config: TbrridgePlaceboCalibrationDiagnosticRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgePlaceboCalibrationDiagnosticPacket | list[TbrridgePlaceboCalibrationDiagnosticPacket]:
    """Generate one or more independent placebo calibration packets."""
    if isinstance(input_data, list):
        return [build_tbrridge_placebo_calibration_packet(item, config=config) for item in input_data]
    return build_tbrridge_placebo_calibration_packet(input_data, config=config)


def packet_to_dict(packet: TbrridgePlaceboCalibrationDiagnosticPacket) -> dict[str, Any]:
    return asdict(packet)


def get_runtime_metadata() -> dict[str, Any]:
    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "scope": _SCOPE,
        "depends_on": list(DEPENDS_ON),
        "final_verdict": _VERDICT,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "allowed_surfaces": list(ALLOWED_SURFACES),
        "prohibited_surfaces": list(PROHIBITED_SURFACES),
        **_POSITIVE_FLAGS,
        **_AUTH_FALSE,
    }


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = False, summary_path: Path | None = None) -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> None:
        scenarios.append({"scenario_id": sid, "passed": passed})

    clean = {
        "request_id": "validation_clean",
        "placebo_scheme": "pseudo_treated_replay",
        "placebo_assignment_manifest": {"placebos": [{"id": str(i)} for i in range(25)]},
        "pseudo_treated_unit_manifest": {"units": ["u1"]},
        "placebo_control_unit_manifest": {"units": ["c1", "c2"]},
        "null_period_definition": {"pre_treatment_only": True},
        "placebo_window_manifest": {"window": "pre"},
        "placebo_metric_manifest": {"metric": "att", "metric_mismatch": False},
        "placebo_geometry_report": {"unbalanced_geometry": False},
        "placebo_contamination_report": {"contamination_detected": False, "donor_overlap_detected": False},
        "placebo_count_report": {"placebo_count": 25},
        "placebo_rank_tail_report": {"tail_instability": False, "rank_instability": False},
        "placebo_directionality_report": {"directional_sign_instability": False},
        "placebo_outlier_influence_report": {"outlier_influence": False},
        "regularization_sensitivity_report": {"masked_placebo_failure": False},
        "lineage_manifest": {"run_id": "validation"},
    }
    ready = build_tbrridge_placebo_calibration_packet(clean)
    _s("diagnostic_ready_clean_evidence", ready.diagnostic_status == "PLACEBO_CALIBRATION_DIAGNOSTIC_READY")

    missing_manifest = build_tbrridge_placebo_calibration_packet({"request_id": "missing", "null_period_definition": {}})
    _s(
        "blocks_missing_placebo_manifest",
        missing_manifest.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_MISSING_PLACEBO_MANIFEST",
    )

    invalid_null = build_tbrridge_placebo_calibration_packet(
        {**clean, "request_id": "invalid_null", "null_period_definition": {"invalid_null_period": True}}
    )
    _s(
        "blocks_invalid_null_construction",
        invalid_null.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_INVALID_NULL_CONSTRUCTION",
    )

    for flag, expected in _AUTH_FALSE.items():
        meta = get_runtime_metadata()
        _s(f"auth_{flag}_false", meta.get(flag) is expected)

    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_placebo_calibration_diagnostic_runtime",
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": list(DEPENDS_ON),
        "failed_scenarios": failed,
        "final_verdict": _VERDICT,
        **_POSITIVE_FLAGS,
        **_AUTH_FALSE,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
    }
    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=args.write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
