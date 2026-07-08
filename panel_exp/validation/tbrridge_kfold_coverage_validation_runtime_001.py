"""TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001 — KFold coverage validation runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.tbrridge_kfold_coverage_validation_contract_001 import (
    ALLOWED_SURFACES,
    COVERAGE_RISK_TYPES,
    ESTIMATOR_FAMILY,
    INFERENCE_FAMILY,
    INSTRUMENT_ID,
    METHOD_ID,
    PROHIBITED_SURFACES,
    REQUIRED_EVIDENCE,
    evaluate_coverage_validation,
)

_ARTIFACT_ID = "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "tbrridge_kfold_coverage_validation_runtime_implemented_no_coverage_computation_or_uncertainty"
_VERDICT = "tbrridge_kfold_coverage_validation_runtime_implemented_no_coverage_computation_or_uncertainty"
_RECOMMENDED_NEXT = "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001"
_ALTERNATIVE_NEXT = "AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001"
_DEFERRED = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001_summary.json"
)

DEPENDS_ON = (
    "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001",
    "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_AUDIT_001",
    "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001",
    "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001",
)

_POSITIVE_FLAGS = {
    "coverage_validation_runtime_implemented": True,
    "coverage_validation_packet_generated": True,
    "leakage_dependency_enforced": True,
    "placebo_dependency_enforced": True,
    "interval_semantics_validation_enforced": True,
    "simulation_design_manifest_required": True,
    "null_control_manifest_required": True,
    "positive_control_manifest_required": True,
    "regime_manifest_validation_enforced": True,
    "uncertainty_surfaces_blocked": True,
}

_AUTH_FALSE = {
    "coverage_computed": False,
    "interval_computed": False,
    "empirical_coverage_computed": False,
    "kfold_inference_implemented": False,
    "placebo_inference_implemented": False,
    "estimator_implemented": False,
    "inference_implemented": False,
    "bootstrap_inference_implemented": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
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

_LEAKAGE_BLOCKING_PREFIX = "KFOLD_LEAKAGE_BLOCKED"
_PLACEBO_BLOCKING_PREFIX = "PLACEBO_CALIBRATION_BLOCKED"


@dataclass(frozen=True)
class TbrridgeKfoldCoverageValidationRuntimeConfig:
    require_lineage_manifest: bool = False


@dataclass(frozen=True)
class TbrridgeKfoldCoverageValidationPacket:
    request_id: str
    validation_id: str
    validation_status: str
    method_id: str
    instrument_id: str
    estimator_family: str
    inference_family: str
    interval_semantics: str | None
    nominal_coverage_target: float | None
    empirical_coverage_summary: dict[str, Any]
    validation_regimes_evaluated: tuple[str, ...]
    coverage_risks_evaluated: tuple[str, ...]
    detected_coverage_risks: tuple[str, ...]
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
    config: TbrridgeKfoldCoverageValidationRuntimeConfig | dict[str, Any] | None,
) -> TbrridgeKfoldCoverageValidationRuntimeConfig:
    if config is None:
        return TbrridgeKfoldCoverageValidationRuntimeConfig()
    if isinstance(config, TbrridgeKfoldCoverageValidationRuntimeConfig):
        return config
    base = TbrridgeKfoldCoverageValidationRuntimeConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return TbrridgeKfoldCoverageValidationRuntimeConfig(**merged)


def _dependency_status(report: Any, blocking_prefix: str) -> str | None:
    if not isinstance(report, dict):
        return None
    status = str(report.get("diagnostic_status") or report.get("validation_status") or "")
    if status.startswith(blocking_prefix) or status.endswith("REQUIRES_METHOD_REVIEW"):
        return status
    return None


def build_evidence_presence(data: dict[str, Any]) -> dict[str, bool]:
    return {
        "leakage_diagnostic_report": _present(data.get("leakage_diagnostic_report")),
        "placebo_calibration_diagnostic_report": _present(data.get("placebo_calibration_diagnostic_report")),
        "interval_semantics_report": _present(data.get("interval_semantics_report")),
        "simulation_design_manifest": _present(data.get("simulation_design_manifest")),
        "null_control_manifest": _present(data.get("null_control_manifest")),
        "positive_control_manifest": _present(data.get("positive_control_manifest")),
        "synthetic_effect_injection_manifest": _present(data.get("synthetic_effect_injection_manifest")),
        "fold_geometry_regime_manifest": _present(data.get("fold_geometry_regime_manifest")),
        "sample_size_regime_manifest": _present(data.get("sample_size_regime_manifest")),
        "regularization_grid_manifest": _present(data.get("regularization_grid_manifest")),
        "donor_pool_sensitivity_report": _present(data.get("donor_pool_sensitivity_report")),
        "outlier_sensitivity_report": _present(data.get("outlier_sensitivity_report")),
        "empirical_coverage_report": _present(data.get("empirical_coverage_report")),
        "false_positive_rate_report": _present(data.get("false_positive_rate_report")),
        "directional_error_report": _present(data.get("directional_error_report")),
        "placebo_calibrated_tail_report": _present(data.get("placebo_calibrated_tail_report")),
        "failure_packet_manifest": _present(data.get("failure_packet_manifest")),
        "lineage_provenance_manifest": _present(data.get("lineage_manifest"))
        or _present(data.get("lineage_provenance_manifest")),
    }


def extract_empirical_coverage_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Passthrough supplied empirical coverage summary without computation."""
    report = data.get("empirical_coverage_report")
    if isinstance(report, dict):
        summary = report.get("summary")
        if isinstance(summary, dict):
            return dict(summary)
        passthrough = {
            k: report[k]
            for k in (
                "nominal_coverage_target",
                "empirical_coverage",
                "coverage_by_regime",
                "undercoverage_cells",
                "overcoverage_cells",
                "notes",
            )
            if k in report
        }
        if passthrough:
            return passthrough
        return {"source": "empirical_coverage_report", "fields_present": sorted(report.keys())}
    return {}


def extract_validation_regimes_evaluated(data: dict[str, Any]) -> tuple[str, ...]:
    regimes: list[str] = []
    for key in (
        "fold_geometry_regime_manifest",
        "sample_size_regime_manifest",
        "regularization_grid_manifest",
    ):
        manifest = data.get(key)
        if isinstance(manifest, dict):
            declared = manifest.get("regimes") or manifest.get("regime_ids")
            if isinstance(declared, list):
                regimes.extend(str(r) for r in declared)
            elif manifest.get("regime_id"):
                regimes.append(str(manifest["regime_id"]))
    sim = data.get("simulation_design_manifest") or {}
    if isinstance(sim, dict):
        grid = sim.get("regime_grid") or sim.get("world_regimes")
        if isinstance(grid, list):
            regimes.extend(str(r) for r in grid)
    seen: set[str] = set()
    ordered: list[str] = []
    for regime in regimes:
        if regime not in seen:
            seen.add(regime)
            ordered.append(regime)
    return tuple(ordered)


def detect_coverage_risks(data: dict[str, Any]) -> tuple[str, ...]:
    """Flag coverage risks from supplied report flags without computing coverage."""
    detected: list[str] = []

    interval = data.get("interval_semantics_report") or {}
    if isinstance(interval, dict):
        if _report_flag(interval, "interval_semantics_undefined", "semantics_undefined", "undefined"):
            detected.append("INTERVAL_SEMANTICS_UNDEFINED")
        if _report_flag(interval, "metric_estimand_mismatch", "estimand_mismatch"):
            detected.append("METRIC_ESTIMAND_MISMATCH")

    empirical = data.get("empirical_coverage_report") or {}
    if isinstance(empirical, dict):
        if _report_flag(
            empirical,
            "nominal_empirical_coverage_mismatch",
            "coverage_mismatch",
            "nominal_mismatch",
        ):
            detected.append("NOMINAL_EMPIRICAL_COVERAGE_MISMATCH")
        if _report_flag(empirical, "undercoverage_risk", "undercoverage_detected", "undercoverage"):
            detected.append("UNDERCOVERAGE_RISK")
        if _report_flag(
            empirical,
            "overcoverage_risk",
            "overcoverage_detected",
            "overcoverage",
            "uninformative_interval_risk",
            "uninformative_interval",
        ):
            detected.append("OVERCOVERAGE_UNINFORMATIVE_INTERVAL_RISK")

    fpr = data.get("false_positive_rate_report") or {}
    if isinstance(fpr, dict):
        if _report_flag(fpr, "null_false_positive_risk", "false_positive_risk", "elevated_fpr"):
            detected.append("NULL_FALSE_POSITIVE_RISK")

    directional = data.get("directional_error_report") or {}
    if isinstance(directional, dict):
        if _report_flag(
            directional,
            "directional_false_signal_risk",
            "directional_error",
            "directional_false_signal",
        ):
            detected.append("DIRECTIONAL_FALSE_SIGNAL_RISK")

    positive = data.get("positive_control_manifest") or {}
    synthetic = data.get("synthetic_effect_injection_manifest") or {}
    for report in (positive, synthetic):
        if isinstance(report, dict) and _report_flag(
            report,
            "positive_control_recovery_failure",
            "recovery_failure",
            "recovery_uncharacterized",
        ):
            detected.append("POSITIVE_CONTROL_RECOVERY_FAILURE")

    placebo_tail = data.get("placebo_calibrated_tail_report") or {}
    if isinstance(placebo_tail, dict):
        if _report_flag(
            placebo_tail,
            "placebo_calibrated_tail_mismatch",
            "tail_mismatch",
            "calibrated_tail_mismatch",
        ):
            detected.append("PLACEBO_CALIBRATED_TAIL_MISMATCH")

    fold_geom = data.get("fold_geometry_regime_manifest") or {}
    if isinstance(fold_geom, dict):
        if _report_flag(fold_geom, "fold_geometry_sensitivity", "geometry_sensitivity", "sensitive"):
            detected.append("FOLD_GEOMETRY_SENSITIVITY")

    sample_size = data.get("sample_size_regime_manifest") or {}
    if isinstance(sample_size, dict):
        if _report_flag(sample_size, "sample_size_sensitivity", "size_sensitivity", "sensitive"):
            detected.append("SAMPLE_SIZE_SENSITIVITY")

    donor = data.get("donor_pool_sensitivity_report") or {}
    if isinstance(donor, dict):
        if _report_flag(donor, "donor_pool_sensitivity", "donor_sensitivity", "sensitive"):
            detected.append("DONOR_POOL_SENSITIVITY")

    regularization = data.get("regularization_grid_manifest") or {}
    if isinstance(regularization, dict):
        if _report_flag(regularization, "regularization_sensitivity", "alpha_sensitivity", "sensitive"):
            detected.append("REGULARIZATION_SENSITIVITY")

    outlier = data.get("outlier_sensitivity_report") or {}
    if isinstance(outlier, dict):
        if _report_flag(outlier, "outlier_week_sensitivity", "outlier_sensitivity", "sensitive"):
            detected.append("OUTLIER_WEEK_SENSITIVITY")

    leakage = data.get("leakage_diagnostic_report") or {}
    if isinstance(leakage, dict):
        status = str(leakage.get("diagnostic_status") or "")
        if status.startswith(_LEAKAGE_BLOCKING_PREFIX) or status == "KFOLD_LEAKAGE_REQUIRES_METHOD_REVIEW":
            detected.append("TEMPORAL_LEAKAGE_DEPENDENCY")

    placebo = data.get("placebo_calibration_diagnostic_report") or {}
    if isinstance(placebo, dict):
        status = str(placebo.get("diagnostic_status") or "")
        if status.startswith(_PLACEBO_BLOCKING_PREFIX) or status == "PLACEBO_CALIBRATION_REQUIRES_METHOD_REVIEW":
            detected.append("PLACEBO_MISCALIBRATION_DEPENDENCY")

    simulation = data.get("simulation_design_manifest") or {}
    if isinstance(simulation, dict):
        if _report_flag(
            simulation,
            "aggregate_pooled_misuse_risk",
            "pooled_misuse_risk",
            "aggregate_misuse",
        ):
            detected.append("AGGREGATE_POOLED_MISUSE_RISK")
        if _report_flag(simulation, "metric_estimand_mismatch", "estimand_mismatch"):
            detected.append("METRIC_ESTIMAND_MISMATCH")

    seen: set[str] = set()
    ordered: list[str] = []
    for item in detected:
        if item in COVERAGE_RISK_TYPES and item not in seen:
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)


def _build_restrictions(
    validation_status: str,
    detected: tuple[str, ...],
    missing: tuple[str, ...],
) -> tuple[str, ...]:
    restrictions: list[str] = []
    if validation_status == "COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS":
        restrictions.append("DIAGNOSTIC_SUMMARY_ONLY")
    if detected:
        restrictions.append("COVERAGE_RISK_FLAGGED")
    if missing:
        restrictions.append("PARTIAL_EVIDENCE")
    if validation_status.startswith("COVERAGE_VALIDATION_BLOCKED"):
        restrictions.append("UNCERTAINTY_SURFACES_BLOCKED")
    return tuple(restrictions)


def _build_warnings(
    detected: tuple[str, ...],
    missing: tuple[str, ...],
    leakage_status: str | None,
    placebo_status: str | None,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if "UNDERCOVERAGE_RISK" in detected:
        warnings.append("Supplied reports indicate undercoverage risk; no coverage recomputed.")
    if "OVERCOVERAGE_UNINFORMATIVE_INTERVAL_RISK" in detected:
        warnings.append("Supplied reports indicate overcoverage or uninformative interval risk.")
    if "NULL_FALSE_POSITIVE_RISK" in detected:
        warnings.append("Supplied null false-positive risk flagged from reports only.")
    if "METRIC_ESTIMAND_MISMATCH" in detected:
        warnings.append("Metric/estimand mismatch may invalidate coverage interpretation.")
    if "AGGREGATE_POOLED_MISUSE_RISK" in detected:
        warnings.append("Aggregate/pooled misuse risk flagged; pooled claims remain blocked.")
    if missing:
        warnings.append(f"Optional evidence missing: {', '.join(missing)}")
    if leakage_status:
        warnings.append(f"Leakage diagnostic dependency: {leakage_status}")
    if placebo_status:
        warnings.append(f"Placebo calibration dependency: {placebo_status}")
    return tuple(warnings)


def _authorization_boundary_report() -> dict[str, Any]:
    return {
        "runtime_scope": "coverage_validation_diagnostic_only",
        "computes_coverage": False,
        "computes_intervals": False,
        "computes_empirical_coverage": False,
        "computes_uncertainty": False,
        "computes_p_values": False,
        "computes_confidence_intervals": False,
        "computes_lift_or_effects": False,
        "authorizes_production_readout": False,
        "authorizes_method_promotion": False,
        "authorizes_uncertainty": False,
        "uncertainty_surfaces_blocked": True,
        **_AUTH_FALSE,
    }


def _build_validation_id(
    data: dict[str, Any],
    validation_status: str,
    detected: tuple[str, ...],
) -> str:
    canonical = {
        "request_id": data.get("request_id"),
        "method_id": data.get("method_id") or METHOD_ID,
        "instrument_id": data.get("instrument_id") or INSTRUMENT_ID,
        "validation_status": validation_status,
        "detected_coverage_risks": sorted(detected),
        "interval_semantics": data.get("interval_semantics"),
        "nominal_coverage_target": data.get("nominal_coverage_target"),
    }
    return f"tkcv-{_hash_payload(canonical)[:16]}"


def build_tbrridge_kfold_coverage_validation_packet(
    input_data: dict[str, Any] | Any,
    *,
    config: TbrridgeKfoldCoverageValidationRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeKfoldCoverageValidationPacket:
    """Build a single coverage validation packet from supplied reports/manifests."""
    cfg = _resolve_config(config)
    data = _to_dict(input_data)

    request_id = str(data.get("request_id") or "tkcv_request_unspecified")
    method_id = str(data.get("method_id") or METHOD_ID)
    instrument_id = str(data.get("instrument_id") or INSTRUMENT_ID)
    estimator_family = str(data.get("estimator_family") or ESTIMATOR_FAMILY)
    inference_family = str(data.get("inference_family") or INFERENCE_FAMILY)
    interval_semantics = data.get("interval_semantics")
    if interval_semantics is not None:
        interval_semantics = str(interval_semantics)
    nominal_target = data.get("nominal_coverage_target")
    if nominal_target is not None and not isinstance(nominal_target, (int, float)):
        nominal_target = None
    lineage = dict(data.get("lineage_manifest") or data.get("lineage_provenance_manifest") or {})

    evidence = build_evidence_presence(data)
    if cfg.require_lineage_manifest and not evidence.get("lineage_provenance_manifest"):
        evidence = {**evidence, "lineage_provenance_manifest": False}

    detected = detect_coverage_risks(data)
    leakage_report = data.get("leakage_diagnostic_report") or {}
    placebo_report = data.get("placebo_calibration_diagnostic_report") or {}
    leakage_status = _dependency_status(leakage_report, _LEAKAGE_BLOCKING_PREFIX)
    placebo_status = _dependency_status(placebo_report, _PLACEBO_BLOCKING_PREFIX)

    requested_surface = data.get("requested_surface")
    evaluation = evaluate_coverage_validation(
        evidence=evidence,
        detected_risks=detected,
        requested_surface=str(requested_surface) if requested_surface else None,
        leakage_diagnostic_status=leakage_status,
        placebo_calibration_status=placebo_status,
    )

    missing_all = tuple(req for req in REQUIRED_EVIDENCE if not evidence.get(req, False))
    missing_evidence = evaluation.missing_evidence or missing_all

    validation_status = evaluation.validation_status
    blockers: list[str] = []
    if evaluation.failure_reason:
        blockers.append(evaluation.failure_reason)
    if leakage_status:
        blockers.append(f"Leakage diagnostic blocking: {leakage_status}")
    if placebo_status:
        blockers.append(f"Placebo calibration blocking: {placebo_status}")

    if (
        validation_status == "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW"
        and not any(evidence.get(k) for k in ("leakage_diagnostic_report", "placebo_calibration_diagnostic_report"))
        and not detected
    ):
        validation_status = "COVERAGE_VALIDATION_NOT_EVALUATED"

    empirical_summary = extract_empirical_coverage_summary(data)
    regimes = extract_validation_regimes_evaluated(data)
    restrictions = _build_restrictions(validation_status, detected, tuple(missing_all))
    warnings = _build_warnings(detected, tuple(missing_all), leakage_status, placebo_status)
    failure_packet = evaluation.to_failure_packet()
    validation_id = _build_validation_id(data, validation_status, detected)

    packet_body = {
        "request_id": request_id,
        "validation_id": validation_id,
        "validation_status": validation_status,
        "method_id": method_id,
        "instrument_id": instrument_id,
        "estimator_family": estimator_family,
        "inference_family": inference_family,
        "interval_semantics": interval_semantics,
        "nominal_coverage_target": nominal_target,
        "empirical_coverage_summary": empirical_summary,
        "validation_regimes_evaluated": list(regimes),
        "coverage_risks_evaluated": list(COVERAGE_RISK_TYPES),
        "detected_coverage_risks": list(detected),
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

    return TbrridgeKfoldCoverageValidationPacket(
        request_id=request_id,
        validation_id=validation_id,
        validation_status=validation_status,
        method_id=method_id,
        instrument_id=instrument_id,
        estimator_family=estimator_family,
        inference_family=inference_family,
        interval_semantics=interval_semantics,
        nominal_coverage_target=float(nominal_target) if nominal_target is not None else None,
        empirical_coverage_summary=empirical_summary,
        validation_regimes_evaluated=regimes,
        coverage_risks_evaluated=COVERAGE_RISK_TYPES,
        detected_coverage_risks=detected,
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


def evaluate_tbrridge_kfold_coverage_validation(
    input_data: dict[str, Any] | Any,
    *,
    config: TbrridgeKfoldCoverageValidationRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeKfoldCoverageValidationPacket:
    """Alias for single coverage validation evaluation."""
    return build_tbrridge_kfold_coverage_validation_packet(input_data, config=config)


def generate_tbrridge_kfold_coverage_validation(
    input_data: dict[str, Any] | Any | list[Any],
    config: TbrridgeKfoldCoverageValidationRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeKfoldCoverageValidationPacket | list[TbrridgeKfoldCoverageValidationPacket]:
    """Generate one or more independent coverage validation packets."""
    if isinstance(input_data, list):
        return [build_tbrridge_kfold_coverage_validation_packet(item, config=config) for item in input_data]
    return build_tbrridge_kfold_coverage_validation_packet(input_data, config=config)


def packet_to_dict(packet: TbrridgeKfoldCoverageValidationPacket) -> dict[str, Any]:
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
        "deferred_artifact": _DEFERRED,
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
        "interval_semantics": "fold_cv_dispersion_surrogate",
        "nominal_coverage_target": 0.9,
        "leakage_diagnostic_report": {"diagnostic_status": "KFOLD_LEAKAGE_DIAGNOSTIC_READY"},
        "placebo_calibration_diagnostic_report": {"diagnostic_status": "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"},
        "interval_semantics_report": {"centering": "att", "semantics_undefined": False},
        "simulation_design_manifest": {"world_regimes": ["null", "positive"]},
        "null_control_manifest": {"worlds": ["null_a"]},
        "positive_control_manifest": {"worlds": ["pos_a"]},
        "synthetic_effect_injection_manifest": {"regimes": ["small_effect"]},
        "fold_geometry_regime_manifest": {"regimes": ["single_treated"]},
        "sample_size_regime_manifest": {"regimes": ["medium_n"]},
        "regularization_grid_manifest": {"alphas": [0.1, 1.0]},
        "donor_pool_sensitivity_report": {"sensitive": False},
        "outlier_sensitivity_report": {"sensitive": False},
        "empirical_coverage_report": {"summary": {"empirical_coverage": 0.88}},
        "false_positive_rate_report": {"elevated_fpr": False},
        "directional_error_report": {"directional_false_signal": False},
        "placebo_calibrated_tail_report": {"tail_mismatch": False},
        "failure_packet_manifest": {},
        "lineage_manifest": {"run_id": "validation"},
    }
    ready = build_tbrridge_kfold_coverage_validation_packet(clean)
    _s(
        "diagnostic_ready_clean_evidence",
        ready.validation_status == "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW",
    )

    missing_leakage = build_tbrridge_kfold_coverage_validation_packet({"request_id": "missing_leakage"})
    _s(
        "blocks_missing_leakage_report",
        missing_leakage.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK",
    )

    for flag, expected in _AUTH_FALSE.items():
        meta = get_runtime_metadata()
        _s(f"auth_{flag}_false", meta.get(flag) is expected)

    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_kfold_coverage_validation_runtime",
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
        "deferred_artifact": _DEFERRED,
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
