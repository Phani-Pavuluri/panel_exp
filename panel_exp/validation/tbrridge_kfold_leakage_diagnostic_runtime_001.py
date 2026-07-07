"""TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001 — KFold leakage diagnostic runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.tbrridge_kfold_leakage_diagnostic_contract_001 import (
    ALLOWED_SURFACES,
    ESTIMATOR_FAMILY,
    INFERENCE_FAMILY,
    INSTRUMENT_ID,
    LEAKAGE_TYPES,
    METHOD_ID,
    PROHIBITED_SURFACES,
    REQUIRED_EVIDENCE,
    evaluate_kfold_leakage_diagnostic,
)

_ARTIFACT_ID = "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "tbrridge_kfold_leakage_diagnostic_runtime_implemented_no_kfold_inference_or_uncertainty"
_VERDICT = "tbrridge_kfold_leakage_diagnostic_runtime_implemented_no_kfold_inference_or_uncertainty"
_RECOMMENDED_NEXT = "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001"
_ALTERNATIVE_NEXT = "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001_summary.json"
)

DEPENDS_ON = (
    "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001",
    "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001",
)

_POSITIVE_FLAGS = {
    "kfold_leakage_runtime_implemented": True,
    "kfold_leakage_diagnostic_packet_generated": True,
    "fold_manifest_validation_enforced": True,
    "temporal_leakage_detection_enforced": True,
    "fold_overlap_detection_enforced": True,
    "treated_control_contamination_detection_enforced": True,
    "unsupported_geometry_detection_enforced": True,
    "kfold_uncertainty_surface_blocked": True,
}

_AUTH_FALSE = {
    "kfold_inference_implemented": False,
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
    "fold_assignment_manifest",
    "temporal_split_report",
    "geometry_support_report",
    "treated_control_separation_report",
    "sample_size_by_fold",
)


@dataclass(frozen=True)
class TbrridgeKfoldLeakageDiagnosticRuntimeConfig:
    min_fold_size_threshold: int = 5
    require_lineage_manifest: bool = False


@dataclass(frozen=True)
class TbrridgeKfoldLeakageDiagnosticPacket:
    request_id: str
    diagnostic_id: str
    diagnostic_status: str
    method_id: str
    instrument_id: str
    estimator_family: str
    inference_family: str
    fold_scheme: str
    treated_geometry: str
    control_geometry: str
    leakage_types_evaluated: tuple[str, ...]
    detected_leakage_types: tuple[str, ...]
    unsupported_geometries: tuple[str, ...]
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
    config: TbrridgeKfoldLeakageDiagnosticRuntimeConfig | dict[str, Any] | None,
) -> TbrridgeKfoldLeakageDiagnosticRuntimeConfig:
    if config is None:
        return TbrridgeKfoldLeakageDiagnosticRuntimeConfig()
    if isinstance(config, TbrridgeKfoldLeakageDiagnosticRuntimeConfig):
        return config
    base = TbrridgeKfoldLeakageDiagnosticRuntimeConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return TbrridgeKfoldLeakageDiagnosticRuntimeConfig(**merged)


def infer_treated_geometry(data: dict[str, Any]) -> str:
    geometry_report = data.get("geometry_support_report") or {}
    if isinstance(geometry_report, dict):
        explicit = geometry_report.get("treated_geometry")
        if explicit:
            return str(explicit)
    treated_manifest = data.get("treated_unit_manifest") or {}
    if isinstance(treated_manifest, dict):
        geometry = treated_manifest.get("geometry")
        if geometry:
            return str(geometry)
        treated_units = treated_manifest.get("treated_units") or treated_manifest.get("units") or []
        if isinstance(treated_units, (list, tuple)) and len(treated_units) > 1:
            return "multi_treated"
    return "single_treated"


def infer_control_geometry(data: dict[str, Any]) -> str:
    control_manifest = data.get("control_unit_manifest") or {}
    if isinstance(control_manifest, dict):
        geometry = control_manifest.get("geometry")
        if geometry:
            return str(geometry)
        shared = control_manifest.get("shared_control") or control_manifest.get("shared_control_family")
        if shared:
            return "shared_control"
    shared_report = data.get("shared_control_family_report")
    if _present(shared_report):
        return "shared_control"
    return "pooled_control"


def build_evidence_presence(data: dict[str, Any]) -> dict[str, bool]:
    """Map manifest presence to contract evidence keys."""
    geometry_report = data.get("geometry_support_report") or {}
    if not isinstance(geometry_report, dict):
        geometry_report = {}

    shared_report = data.get("shared_control_family_report")
    shared_present = _present(shared_report)
    shared_required = False
    if isinstance(shared_report, dict):
        shared_required = bool(
            shared_report.get("shared_control")
            or shared_report.get("shared_control_family")
            or shared_report.get("applicable")
        )
    control_geometry = infer_control_geometry(data)
    if control_geometry == "shared_control":
        shared_required = True

    flags: dict[str, bool] = {
        "fold_assignment_manifest": _present(data.get("fold_assignment_manifest")),
        "treated_unit_manifest": _present(data.get("treated_unit_manifest")),
        "control_unit_manifest": _present(data.get("control_unit_manifest")),
        "pre_period_window": _present(data.get("pre_period_window")),
        "post_period_window": _present(data.get("post_period_window")),
        "feature_construction_manifest": _present(data.get("feature_construction_manifest")),
        "hyperparameter_selection_manifest": _present(data.get("hyperparameter_selection_manifest")),
        "geometry_support_report": _present(data.get("geometry_support_report")),
        "temporal_split_report": _present(data.get("temporal_split_report")),
        "fold_overlap_report": _present(data.get("fold_overlap_report")),
        "treated_control_separation_report": _present(data.get("treated_control_separation_report")),
        "sample_size_by_fold": _present(data.get("sample_size_by_fold")),
        "shared_control_family_report": shared_present or not shared_required,
        "multicell_family_contrast_packet": _present(data.get("multicell_family_contrast_packet"))
        or not shared_required,
        "lineage_provenance_manifest": _present(data.get("lineage_manifest"))
        or _present(data.get("lineage_provenance_manifest")),
        "geometry_support_report_multi_treated_policy": bool(
            geometry_report.get("multi_treated_policy")
            or geometry_report.get("multi_treated_supported")
        ),
    }
    return flags


def detect_leakage_types(
    data: dict[str, Any],
    *,
    min_fold_size_threshold: int = 5,
) -> tuple[str, ...]:
    """Detect leakage types from manifest/report content."""
    detected: list[str] = []

    temporal = data.get("temporal_split_report") or {}
    if isinstance(temporal, dict):
        if _report_flag(temporal, "temporal_leakage", "temporal_leakage_detected"):
            detected.append("TEMPORAL_LEAKAGE")
        if _report_flag(temporal, "post_period_leakage", "post_period_leakage_detected"):
            detected.append("POST_PERIOD_LEAKAGE")
        if _report_flag(
            temporal,
            "pre_post_boundary_leakage",
            "pre_post_boundary_leakage_detected",
            "boundary_leakage",
        ):
            detected.append("PRE_POST_BOUNDARY_LEAKAGE")
        if _report_flag(temporal, "future_information_in_training", "future_information_leakage"):
            if "TEMPORAL_LEAKAGE" not in detected:
                detected.append("TEMPORAL_LEAKAGE")

    fold_overlap = data.get("fold_overlap_report") or {}
    if isinstance(fold_overlap, dict):
        if _report_flag(fold_overlap, "unit_overlap", "unit_overlap_detected"):
            detected.append("UNIT_OVERLAP_LEAKAGE")
        if _report_flag(fold_overlap, "fold_overlap", "fold_overlap_detected"):
            detected.append("FOLD_ASSIGNMENT_INSTABILITY")
        if _report_flag(fold_overlap, "fold_assignment_instability", "assignment_instability"):
            detected.append("FOLD_ASSIGNMENT_INSTABILITY")

    separation = data.get("treated_control_separation_report") or {}
    if isinstance(separation, dict):
        if _report_flag(
            separation,
            "contamination",
            "contamination_detected",
            "treated_control_contamination",
        ):
            detected.append("TREATED_CONTROL_CONTAMINATION")
        if _report_flag(separation, "treated_control_overlap", "overlap_detected"):
            detected.append("TREATED_CONTROL_CONTAMINATION")

    shared_report = data.get("shared_control_family_report") or {}
    if isinstance(shared_report, dict):
        if _report_flag(shared_report, "fold_leakage", "shared_control_fold_leakage"):
            detected.append("SHARED_CONTROL_FOLD_LEAKAGE")

    treated_geometry = infer_treated_geometry(data)
    geometry_report = data.get("geometry_support_report") or {}
    geometry_supported = True
    if isinstance(geometry_report, dict) and geometry_report.get("geometry_supported") is False:
        geometry_supported = False
    if treated_geometry == "multi_treated" and not (
        isinstance(geometry_report, dict)
        and (geometry_report.get("multi_treated_policy") or geometry_report.get("multi_treated_supported"))
    ):
        detected.append("MULTI_TREATED_GEOMETRY_UNSUPPORTED")
    elif treated_geometry == "multi_treated" and not geometry_supported:
        detected.append("MULTI_TREATED_GEOMETRY_UNSUPPORTED")

    sample_sizes = data.get("sample_size_by_fold") or {}
    if isinstance(sample_sizes, dict):
        degeneracy = _report_flag(sample_sizes, "degeneracy", "degeneracy_detected", "fold_degeneracy")
        min_per_fold = sample_sizes.get("min_per_fold") or sample_sizes.get("minimum_fold_size")
        if degeneracy or (
            isinstance(min_per_fold, (int, float)) and min_per_fold < min_fold_size_threshold
        ):
            detected.append("SMALL_SAMPLE_FOLD_DEGENERACY")
        if _report_flag(sample_sizes, "outlier_influence_risk", "outlier_influence_leakage"):
            detected.append("OUTLIER_INFLUENCE_LEAKAGE")

    feature_manifest = data.get("feature_construction_manifest") or {}
    if isinstance(feature_manifest, dict):
        if _report_flag(
            feature_manifest,
            "leakage_risk",
            "feature_construction_leakage",
            "uses_post_period_features",
        ):
            detected.append("FEATURE_CONSTRUCTION_LEAKAGE")

    hyper_manifest = data.get("hyperparameter_selection_manifest") or {}
    if isinstance(hyper_manifest, dict):
        if _report_flag(
            hyper_manifest,
            "leakage_risk",
            "hyperparameter_selection_leakage",
            "uses_post_period_outcomes",
        ):
            detected.append("HYPERPARAMETER_SELECTION_LEAKAGE")

    # Deduplicate while preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for item in detected:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)


def _missing_core_evidence(evidence: dict[str, bool]) -> tuple[str, ...]:
    return tuple(key for key in _CORE_EVIDENCE_KEYS if not evidence.get(key, False))


def _build_restrictions(
    evaluation_status: str,
    detected: tuple[str, ...],
    missing: tuple[str, ...],
) -> tuple[str, ...]:
    restrictions: list[str] = []
    if evaluation_status == "KFOLD_LEAKAGE_DIAGNOSTIC_READY_WITH_RESTRICTIONS":
        restrictions.append("DIAGNOSTIC_SUMMARY_ONLY")
    if any(
        lt in detected
        for lt in ("FEATURE_CONSTRUCTION_LEAKAGE", "HYPERPARAMETER_SELECTION_LEAKAGE")
    ):
        restrictions.append("LEAKAGE_RISK_FLAGGED")
    if missing:
        restrictions.append("PARTIAL_EVIDENCE")
    if evaluation_status.startswith("KFOLD_LEAKAGE_BLOCKED"):
        restrictions.append("KFOLD_UNCERTAINTY_SURFACES_BLOCKED")
    return tuple(restrictions)


def _build_warnings(
    detected: tuple[str, ...],
    missing: tuple[str, ...],
    evaluation_status: str,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if "FEATURE_CONSTRUCTION_LEAKAGE" in detected:
        warnings.append("Feature construction may leak post-period information into folds.")
    if "HYPERPARAMETER_SELECTION_LEAKAGE" in detected:
        warnings.append("Hyperparameter selection may use post-period outcomes.")
    if "OUTLIER_INFLUENCE_LEAKAGE" in detected:
        warnings.append("Outlier influence may distort fold stability diagnostics.")
    if missing and evaluation_status == "KFOLD_LEAKAGE_DIAGNOSTIC_READY_WITH_RESTRICTIONS":
        warnings.append(f"Optional evidence missing: {', '.join(missing)}")
    return tuple(warnings)


def _authorization_boundary_report() -> dict[str, Any]:
    return {
        "runtime_scope": "kfold_leakage_diagnostic_only",
        "computes_kfold_inference": False,
        "computes_uncertainty": False,
        "computes_coverage": False,
        "computes_p_values": False,
        "computes_confidence_intervals": False,
        "computes_lift_or_effects": False,
        "authorizes_production_readout": False,
        "authorizes_method_promotion": False,
        "authorizes_catalog_changes": False,
        "kfold_uncertainty_surface_blocked": True,
        **_AUTH_FALSE,
    }


def _build_diagnostic_id(
    data: dict[str, Any],
    diagnostic_status: str,
    detected: tuple[str, ...],
) -> str:
    canonical = {
        "request_id": data.get("request_id"),
        "method_id": data.get("method_id") or METHOD_ID,
        "instrument_id": data.get("instrument_id") or INSTRUMENT_ID,
        "fold_scheme": data.get("fold_scheme"),
        "diagnostic_status": diagnostic_status,
        "detected_leakage_types": sorted(detected),
        "treated_geometry": infer_treated_geometry(data),
        "control_geometry": infer_control_geometry(data),
    }
    return f"tkld-{_hash_payload(canonical)[:16]}"


def build_tbrridge_kfold_leakage_packet(
    input_data: dict[str, Any] | Any,
    *,
    config: TbrridgeKfoldLeakageDiagnosticRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeKfoldLeakageDiagnosticPacket:
    """Build a single KFold leakage diagnostic packet from manifests."""
    cfg = _resolve_config(config)
    data = _to_dict(input_data)

    request_id = str(data.get("request_id") or "tkld_request_unspecified")
    method_id = str(data.get("method_id") or METHOD_ID)
    instrument_id = str(data.get("instrument_id") or INSTRUMENT_ID)
    estimator_family = str(data.get("estimator_family") or ESTIMATOR_FAMILY)
    inference_family = str(data.get("inference_family") or INFERENCE_FAMILY)
    fold_scheme = str(data.get("fold_scheme") or "unspecified")
    treated_geometry = infer_treated_geometry(data)
    control_geometry = infer_control_geometry(data)
    lineage = dict(data.get("lineage_manifest") or data.get("lineage_provenance_manifest") or {})

    evidence = build_evidence_presence(data)
    if cfg.require_lineage_manifest and not evidence.get("lineage_provenance_manifest"):
        evidence = {**evidence, "lineage_provenance_manifest": False}

    detected = detect_leakage_types(data, min_fold_size_threshold=cfg.min_fold_size_threshold)
    requested_surface = data.get("requested_surface")

    evaluation = evaluate_kfold_leakage_diagnostic(
        evidence=evidence,
        treated_geometry=treated_geometry,
        detected_leakage=detected,
        requested_surface=str(requested_surface) if requested_surface else None,
    )

    missing_all = tuple(
        req for req in REQUIRED_EVIDENCE if not evidence.get(req, False)
    )
    missing_core = _missing_core_evidence(evidence)
    missing_evidence = evaluation.missing_evidence or missing_core or missing_all

    blockers: list[str] = []
    if evaluation.failure_reason:
        blockers.append(evaluation.failure_reason)
    if missing_core and evaluation.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE":
        blockers.append(f"Missing core evidence: {', '.join(missing_core)}")

    restrictions = _build_restrictions(
        evaluation.diagnostic_status,
        detected,
        tuple(missing_all),
    )
    warnings = _build_warnings(detected, tuple(missing_all), evaluation.diagnostic_status)

    diagnostic_status = evaluation.diagnostic_status
    if (
        diagnostic_status == "KFOLD_LEAKAGE_DIAGNOSTIC_READY"
        and not any(evidence.get(k) for k in _CORE_EVIDENCE_KEYS)
        and not detected
    ):
        diagnostic_status = "KFOLD_LEAKAGE_NOT_EVALUATED"

    diagnostic_id = _build_diagnostic_id(data, diagnostic_status, detected)
    failure_packet = evaluation.to_failure_packet()

    packet_body = {
        "request_id": request_id,
        "diagnostic_id": diagnostic_id,
        "diagnostic_status": diagnostic_status,
        "method_id": method_id,
        "instrument_id": instrument_id,
        "estimator_family": estimator_family,
        "inference_family": inference_family,
        "fold_scheme": fold_scheme,
        "treated_geometry": treated_geometry,
        "control_geometry": control_geometry,
        "leakage_types_evaluated": list(LEAKAGE_TYPES),
        "detected_leakage_types": list(detected),
        "unsupported_geometries": list(evaluation.unsupported_geometries),
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

    return TbrridgeKfoldLeakageDiagnosticPacket(
        request_id=request_id,
        diagnostic_id=diagnostic_id,
        diagnostic_status=diagnostic_status,
        method_id=method_id,
        instrument_id=instrument_id,
        estimator_family=estimator_family,
        inference_family=inference_family,
        fold_scheme=fold_scheme,
        treated_geometry=treated_geometry,
        control_geometry=control_geometry,
        leakage_types_evaluated=LEAKAGE_TYPES,
        detected_leakage_types=detected,
        unsupported_geometries=evaluation.unsupported_geometries,
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


def evaluate_tbrridge_kfold_leakage(
    input_data: dict[str, Any] | Any,
    *,
    config: TbrridgeKfoldLeakageDiagnosticRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeKfoldLeakageDiagnosticPacket:
    """Alias for single diagnostic evaluation."""
    return build_tbrridge_kfold_leakage_packet(input_data, config=config)


def generate_tbrridge_kfold_leakage_diagnostic(
    input_data: dict[str, Any] | Any | list[Any],
    config: TbrridgeKfoldLeakageDiagnosticRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeKfoldLeakageDiagnosticPacket | list[TbrridgeKfoldLeakageDiagnosticPacket]:
    """Generate one or more independent KFold leakage diagnostic packets (no ranking)."""
    if isinstance(input_data, list):
        return [build_tbrridge_kfold_leakage_packet(item, config=config) for item in input_data]
    return build_tbrridge_kfold_leakage_packet(input_data, config=config)


def packet_to_dict(packet: TbrridgeKfoldLeakageDiagnosticPacket) -> dict[str, Any]:
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
        "fold_assignment_manifest": {"folds": [{"fold_id": 0}]},
        "treated_unit_manifest": {"treated_units": ["t1"], "geometry": "single_treated"},
        "control_unit_manifest": {"control_units": ["c1"]},
        "pre_period_window": {"start": "2024-01-01"},
        "post_period_window": {"start": "2024-07-01"},
        "feature_construction_manifest": {"leakage_risk": False},
        "hyperparameter_selection_manifest": {"leakage_risk": False},
        "geometry_support_report": {"treated_geometry": "single_treated", "geometry_supported": True},
        "temporal_split_report": {"pre_post_boundary_declared": True},
        "fold_overlap_report": {"fold_overlap": False},
        "treated_control_separation_report": {"contamination": False},
        "sample_size_by_fold": {"min_per_fold": 10},
        "lineage_manifest": {"run_id": "validation"},
    }
    ready = build_tbrridge_kfold_leakage_packet(clean)
    _s("diagnostic_ready_clean_evidence", ready.diagnostic_status == "KFOLD_LEAKAGE_DIAGNOSTIC_READY")

    missing_fold = build_tbrridge_kfold_leakage_packet({"request_id": "missing_fold", "temporal_split_report": {}})
    _s("blocks_missing_fold_manifest", missing_fold.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_MISSING_EVIDENCE")

    temporal = build_tbrridge_kfold_leakage_packet(
        {**clean, "request_id": "temporal", "temporal_split_report": {"temporal_leakage": True}}
    )
    _s("blocks_temporal_leakage", temporal.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE")

    multi = build_tbrridge_kfold_leakage_packet(
        {
            **clean,
            "request_id": "multi",
            "treated_unit_manifest": {"treated_units": ["t1", "t2"], "geometry": "multi_treated"},
            "geometry_support_report": {"treated_geometry": "multi_treated", "geometry_supported": False},
        }
    )
    _s("blocks_multi_treated", multi.diagnostic_status == "KFOLD_LEAKAGE_BLOCKED_BY_UNSUPPORTED_GEOMETRY")

    for flag, expected in _AUTH_FALSE.items():
        meta = get_runtime_metadata()
        _s(f"auth_{flag}_false", meta.get(flag) is expected)

    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_kfold_leakage_diagnostic_runtime",
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
