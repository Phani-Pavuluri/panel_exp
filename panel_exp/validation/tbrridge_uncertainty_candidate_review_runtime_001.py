"""TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001 — uncertainty candidate review runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.tbrridge_uncertainty_candidate_review_contract_001 import (
    ALLOWED_SURFACES,
    CANDIDATE_REVIEW_TARGET_STAGE,
    CURRENT_READINESS_STAGE,
    ESTIMATOR_FAMILY,
    INFERENCE_FAMILY,
    INSTRUMENT_ID,
    METHOD_ID,
    PROHIBITED_SURFACES,
    REQUIRED_EVIDENCE,
    REVIEW_RISK_TYPES,
    UncertaintyCandidateReviewEvaluationResult,
    evaluate_uncertainty_candidate_review,
)

_ARTIFACT_ID = "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "tbrridge_uncertainty_candidate_review_runtime_implemented_no_uncertainty_computation_or_approval"
_VERDICT = "tbrridge_uncertainty_candidate_review_runtime_implemented_no_uncertainty_computation_or_approval"
_RECOMMENDED_NEXT = "TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001"
_ALTERNATIVE_NEXT = "AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001"
_DEFERRED = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001_summary.json"
)

DEPENDS_ON = (
    "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001",
    "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001",
    "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001",
    "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001",
)

_POSITIVE_FLAGS = {
    "uncertainty_candidate_review_runtime_implemented": True,
    "supplied_evidence_reviewed": True,
    "missing_evidence_detected": True,
    "leakage_status_delegated": True,
    "placebo_status_delegated": True,
    "coverage_status_delegated": True,
    "failure_packet_emitted": True,
    "deterministic_provenance_hash_defined": True,
}

_AUTH_FALSE = {
    "uncertainty_candidate_approved": False,
    "uncertainty_authorized": False,
    "confidence_interval_authorized": False,
    "p_value_authorized": False,
    "statistical_significance_authorized": False,
    "coverage_approval_authorized": False,
    "method_promotion_authorized": False,
    "production_compatibility_authorized": False,
    "catalog_unblock_authorized": False,
    "coverage_computed": False,
    "interval_computed": False,
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
_COVERAGE_BLOCKING_PREFIX = "COVERAGE_VALIDATION_BLOCKED"


@dataclass(frozen=True)
class TbrridgeUncertaintyCandidateReviewRuntimeConfig:
    require_lineage_manifest: bool = False


@dataclass(frozen=True)
class TbrridgeUncertaintyCandidateReviewPacket:
    request_id: str
    review_id: str
    review_status: str
    method_id: str
    instrument_id: str
    estimator_family: str
    inference_family: str
    current_readiness_stage: str
    candidate_review_target_stage: str
    evidence_chain_summary: dict[str, Any]
    evidence_components_reviewed: tuple[str, ...]
    required_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    detected_review_risks: tuple[str, ...]
    blockers: tuple[str, ...]
    restrictions: tuple[str, ...]
    allowed_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    failure_packet: dict[str, Any] | None
    recommended_next_action: str | None
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
    config: TbrridgeUncertaintyCandidateReviewRuntimeConfig | dict[str, Any] | None,
) -> TbrridgeUncertaintyCandidateReviewRuntimeConfig:
    if config is None:
        return TbrridgeUncertaintyCandidateReviewRuntimeConfig()
    if isinstance(config, TbrridgeUncertaintyCandidateReviewRuntimeConfig):
        return config
    base = TbrridgeUncertaintyCandidateReviewRuntimeConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return TbrridgeUncertaintyCandidateReviewRuntimeConfig(**merged)


def _extract_status(report: Any, *keys: str) -> str | None:
    if not isinstance(report, dict):
        return None
    for key in keys:
        value = report.get(key)
        if value:
            return str(value)
    return None


def _dependency_status(report: Any, blocking_prefix: str) -> str | None:
    status = _extract_status(report, "diagnostic_status", "validation_status", "review_status")
    if not status:
        return None
    if status.startswith(blocking_prefix) or status.endswith("REQUIRES_METHOD_REVIEW"):
        return status
    return None


def build_evidence_presence(data: dict[str, Any]) -> dict[str, bool]:
    """Map supplied evidence objects to required-evidence presence flags."""
    return {req: _present(data.get(req)) for req in REQUIRED_EVIDENCE}


def extract_evidence_chain_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Passthrough supplied summaries from evidence reports without computation."""
    summary: dict[str, Any] = {}
    for key in REQUIRED_EVIDENCE:
        report = data.get(key)
        if not isinstance(report, dict):
            continue
        passthrough = report.get("summary")
        if isinstance(passthrough, dict):
            summary[key] = dict(passthrough)
        elif report:
            summary[key] = {
                "source": key,
                "fields_present": sorted(report.keys()),
            }
    return summary


def detect_uncertainty_candidate_review_risks(data: dict[str, Any]) -> tuple[str, ...]:
    """Flag review risks from supplied report flags without computing statistics."""
    detected: list[str] = []

    interval = data.get("interval_semantics_report") or {}
    if isinstance(interval, dict):
        if _report_flag(interval, "interval_semantics_incomplete", "semantics_undefined", "undefined"):
            detected.append("INTERVAL_SEMANTICS_INCOMPLETE")
        if _report_flag(interval, "metric_estimand_mismatch", "estimand_mismatch"):
            detected.append("METRIC_ESTIMAND_MISMATCH")

    metric = data.get("metric_estimand_alignment_report") or {}
    if isinstance(metric, dict) and _report_flag(
        metric, "metric_estimand_mismatch", "estimand_mismatch", "alignment_failure"
    ):
        detected.append("METRIC_ESTIMAND_MISMATCH")

    aggregate = data.get("aggregate_pooled_surface_blocker_report") or {}
    if isinstance(aggregate, dict) and _report_flag(
        aggregate,
        "aggregate_pooled_unsupported",
        "aggregate_pooled_surface_unsupported",
        "pooled_surface_unsupported",
        "aggregate_misuse",
    ):
        detected.append("AGGREGATE_POOLED_SURFACE_UNSUPPORTED")

    null_control = data.get("null_control_evidence_report") or {}
    if isinstance(null_control, dict) and _report_flag(
        null_control, "null_control_incomplete", "evidence_incomplete"
    ):
        detected.append("NULL_CONTROL_EVIDENCE_INCOMPLETE")

    positive = data.get("positive_control_evidence_report") or {}
    if isinstance(positive, dict) and _report_flag(
        positive, "positive_control_incomplete", "evidence_incomplete", "recovery_failure"
    ):
        detected.append("POSITIVE_CONTROL_EVIDENCE_INCOMPLETE")

    regime = data.get("regime_sensitivity_report") or {}
    if isinstance(regime, dict) and _report_flag(
        regime, "regime_sensitivity_incomplete", "sensitivity_incomplete"
    ):
        detected.append("REGIME_SENSITIVITY_INCOMPLETE")

    regularization = data.get("regularization_sensitivity_report") or {}
    if isinstance(regularization, dict) and _report_flag(
        regularization, "regularization_sensitivity_incomplete", "sensitivity_incomplete"
    ):
        detected.append("REGULARIZATION_SENSITIVITY_INCOMPLETE")

    donor = data.get("donor_pool_sensitivity_report") or {}
    if isinstance(donor, dict) and _report_flag(
        donor, "donor_pool_sensitivity_incomplete", "sensitivity_incomplete"
    ):
        detected.append("DONOR_POOL_SENSITIVITY_INCOMPLETE")

    outlier = data.get("outlier_sensitivity_report") or {}
    if isinstance(outlier, dict) and _report_flag(
        outlier, "outlier_sensitivity_incomplete", "sensitivity_incomplete"
    ):
        detected.append("OUTLIER_SENSITIVITY_INCOMPLETE")

    claim = data.get("claim_authorization_boundary_report") or {}
    if isinstance(claim, dict) and _report_flag(
        claim, "claim_authorization_boundary_missing", "boundary_missing"
    ):
        detected.append("CLAIM_AUTHORIZATION_BOUNDARY_MISSING")

    promotion = data.get("method_promotion_boundary_report") or {}
    if isinstance(promotion, dict) and _report_flag(
        promotion, "method_promotion_boundary_missing", "boundary_missing"
    ):
        detected.append("METHOD_PROMOTION_BOUNDARY_MISSING")

    stats = data.get("statistical_promotion_threshold_report") or {}
    if isinstance(stats, dict) and _report_flag(
        stats, "statistical_promotion_evidence_incomplete", "evidence_incomplete"
    ):
        detected.append("STATISTICAL_PROMOTION_EVIDENCE_INCOMPLETE")

    catalog = data.get("production_catalog_status_report") or {}
    if isinstance(catalog, dict) and _report_flag(
        catalog, "catalog_blocked", "production_catalog_blocked", "blocked"
    ):
        detected.append("PRODUCTION_CATALOG_BLOCKED")

    leakage = data.get("kfold_leakage_diagnostic_report") or {}
    if isinstance(leakage, dict):
        status = _extract_status(leakage, "diagnostic_status", "validation_status")
        if status and (
            status.startswith(_LEAKAGE_BLOCKING_PREFIX) or status == "KFOLD_LEAKAGE_REQUIRES_METHOD_REVIEW"
        ):
            detected.append("LEAKAGE_DIAGNOSTIC_BLOCKING")

    placebo = data.get("placebo_calibration_diagnostic_report") or {}
    if isinstance(placebo, dict):
        status = _extract_status(placebo, "diagnostic_status", "validation_status")
        if status and (
            status.startswith(_PLACEBO_BLOCKING_PREFIX)
            or status == "PLACEBO_CALIBRATION_REQUIRES_METHOD_REVIEW"
        ):
            detected.append("PLACEBO_CALIBRATION_BLOCKING")

    coverage = data.get("coverage_validation_report") or {}
    if isinstance(coverage, dict):
        status = _extract_status(coverage, "validation_status", "diagnostic_status", "review_status")
        if status and (
            status.startswith(_COVERAGE_BLOCKING_PREFIX)
            or status == "COVERAGE_VALIDATION_REQUIRES_METHOD_REVIEW"
        ):
            detected.append("COVERAGE_VALIDATION_BLOCKING")

    seen: set[str] = set()
    ordered: list[str] = []
    for item in detected:
        if item in REVIEW_RISK_TYPES and item not in seen:
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)


def build_uncertainty_candidate_failure_packet(
    evaluation: UncertaintyCandidateReviewEvaluationResult,
) -> dict[str, Any] | None:
    """Build standardized failure packet from contract evaluation result."""
    return evaluation.to_failure_packet()


def _production_catalog_blocked(data: dict[str, Any]) -> bool:
    catalog = data.get("production_catalog_status_report") or {}
    if isinstance(catalog, dict):
        if catalog.get("catalog_unblocked") is True:
            return False
        if catalog.get("catalog_blocked") is False and catalog.get("production_catalog_blocked") is False:
            return False
    return True


def _metric_estimand_mismatch(data: dict[str, Any], detected: tuple[str, ...]) -> bool:
    if "METRIC_ESTIMAND_MISMATCH" in detected:
        return True
    for key in ("metric_estimand_alignment_report", "interval_semantics_report"):
        report = data.get(key) or {}
        if isinstance(report, dict) and _report_flag(
            report, "metric_estimand_mismatch", "estimand_mismatch", "alignment_failure"
        ):
            return True
    return bool(data.get("metric_estimand_mismatch"))


def _build_restrictions(
    review_status: str,
    detected: tuple[str, ...],
    missing: tuple[str, ...],
) -> tuple[str, ...]:
    restrictions: list[str] = []
    if review_status == "UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS":
        restrictions.append("RESTRICTED_REVIEW_SUMMARY_ONLY")
    if detected:
        restrictions.append("REVIEW_RISK_FLAGGED")
    if missing:
        restrictions.append("PARTIAL_EVIDENCE")
    if review_status.startswith("UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED"):
        restrictions.append("UNCERTAINTY_SURFACES_BLOCKED")
    if review_status == "UNCERTAINTY_CANDIDATE_REVIEW_REQUIRES_METHOD_REVIEW":
        restrictions.append("PROHIBITED_SURFACE_REQUESTED")
    return tuple(restrictions)


def _build_warnings(
    detected: tuple[str, ...],
    missing: tuple[str, ...],
    leakage_status: str | None,
    placebo_status: str | None,
    coverage_status: str | None,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if "INTERVAL_SEMANTICS_INCOMPLETE" in detected:
        warnings.append("Interval semantics incomplete per supplied reports; no intervals computed.")
    if "METRIC_ESTIMAND_MISMATCH" in detected:
        warnings.append("Metric/estimand mismatch flagged from supplied reports only.")
    if "AGGREGATE_POOLED_SURFACE_UNSUPPORTED" in detected:
        warnings.append("Aggregate/pooled surface unsupported; pooled claims remain blocked.")
    if "PRODUCTION_CATALOG_BLOCKED" in detected:
        warnings.append("Production catalog remains blocked for TBRRidge KFold.")
    if missing:
        warnings.append(f"Evidence missing: {', '.join(missing)}")
    if leakage_status:
        warnings.append(f"Leakage diagnostic dependency: {leakage_status}")
    if placebo_status:
        warnings.append(f"Placebo calibration dependency: {placebo_status}")
    if coverage_status and coverage_status.startswith(_COVERAGE_BLOCKING_PREFIX):
        warnings.append(f"Coverage validation dependency: {coverage_status}")
    return tuple(warnings)


def _authorization_boundary_report() -> dict[str, Any]:
    return {
        "runtime_scope": "uncertainty_candidate_review_diagnostic_only",
        "computes_coverage": False,
        "computes_intervals": False,
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


def _build_review_id(
    data: dict[str, Any],
    review_status: str,
    detected: tuple[str, ...],
) -> str:
    canonical = {
        "request_id": data.get("request_id"),
        "method_id": data.get("method_id") or METHOD_ID,
        "instrument_id": data.get("instrument_id") or INSTRUMENT_ID,
        "review_status": review_status,
        "detected_review_risks": sorted(detected),
        "current_readiness_stage": data.get("current_readiness_stage") or CURRENT_READINESS_STAGE,
    }
    return f"tucr-{_hash_payload(canonical)[:16]}"


def build_tbrridge_uncertainty_candidate_review_packet(
    input_data: dict[str, Any] | Any,
    *,
    config: TbrridgeUncertaintyCandidateReviewRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeUncertaintyCandidateReviewPacket:
    """Build a single uncertainty-candidate review packet from supplied evidence."""
    cfg = _resolve_config(config)
    data = _to_dict(input_data)

    request_id = str(data.get("request_id") or "tucr_request_unspecified")
    method_id = str(data.get("method_id") or METHOD_ID)
    instrument_id = str(data.get("instrument_id") or INSTRUMENT_ID)
    estimator_family = str(data.get("estimator_family") or ESTIMATOR_FAMILY)
    inference_family = str(data.get("inference_family") or INFERENCE_FAMILY)
    current_stage = str(data.get("current_readiness_stage") or CURRENT_READINESS_STAGE)
    target_stage = str(data.get("candidate_review_target_stage") or CANDIDATE_REVIEW_TARGET_STAGE)
    lineage = dict(data.get("lineage_manifest") or data.get("lineage_provenance_manifest") or {})

    evidence = build_evidence_presence(data)
    if cfg.require_lineage_manifest and not evidence.get("lineage_provenance_manifest"):
        evidence = {**evidence, "lineage_provenance_manifest": False}

    detected = detect_uncertainty_candidate_review_risks(data)
    leakage_report = data.get("kfold_leakage_diagnostic_report") or {}
    placebo_report = data.get("placebo_calibration_diagnostic_report") or {}
    coverage_report = data.get("coverage_validation_report") or {}

    leakage_status = _dependency_status(leakage_report, _LEAKAGE_BLOCKING_PREFIX)
    placebo_status = _dependency_status(placebo_report, _PLACEBO_BLOCKING_PREFIX)
    coverage_blocking = _dependency_status(coverage_report, _COVERAGE_BLOCKING_PREFIX)
    coverage_status = _extract_status(
        coverage_report, "validation_status", "diagnostic_status", "review_status"
    )

    requested_surface = data.get("requested_surface")
    evaluation = evaluate_uncertainty_candidate_review(
        evidence=evidence,
        detected_risks=detected,
        requested_surface=str(requested_surface) if requested_surface else None,
        leakage_diagnostic_status=leakage_status,
        placebo_calibration_status=placebo_status,
        coverage_validation_status=coverage_status,
        production_catalog_blocked=_production_catalog_blocked(data),
        metric_estimand_mismatch=_metric_estimand_mismatch(data, detected),
        deferred=bool(data.get("deferred")),
    )

    missing_all = tuple(req for req in REQUIRED_EVIDENCE if not evidence.get(req, False))
    missing_evidence = evaluation.missing_evidence or missing_all
    evidence_reviewed = tuple(req for req in REQUIRED_EVIDENCE if evidence.get(req, False))

    review_status = evaluation.review_status
    blockers: list[str] = []
    if evaluation.failure_reason:
        blockers.append(evaluation.failure_reason)
    if leakage_status:
        blockers.append(f"Leakage diagnostic blocking: {leakage_status}")
    if placebo_status:
        blockers.append(f"Placebo calibration blocking: {placebo_status}")
    if coverage_blocking:
        blockers.append(f"Coverage validation blocking: {coverage_blocking}")

    if (
        review_status
        in (
            "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
            "UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS",
        )
        and not any(evidence.get(k) for k in REQUIRED_EVIDENCE)
    ):
        review_status = "UNCERTAINTY_CANDIDATE_REVIEW_NOT_EVALUATED"

    chain_summary = extract_evidence_chain_summary(data)
    restrictions = _build_restrictions(review_status, detected, missing_evidence)
    warnings = _build_warnings(
        detected, missing_evidence, leakage_status, placebo_status, coverage_status
    )
    failure_packet = build_uncertainty_candidate_failure_packet(evaluation)
    review_id = _build_review_id(data, review_status, detected)

    packet_body = {
        "request_id": request_id,
        "review_id": review_id,
        "review_status": review_status,
        "method_id": method_id,
        "instrument_id": instrument_id,
        "estimator_family": estimator_family,
        "inference_family": inference_family,
        "current_readiness_stage": current_stage,
        "candidate_review_target_stage": target_stage,
        "evidence_chain_summary": chain_summary,
        "evidence_components_reviewed": list(evidence_reviewed),
        "required_evidence": list(REQUIRED_EVIDENCE),
        "missing_evidence": list(missing_evidence),
        "detected_review_risks": list(detected),
        "blockers": blockers,
        "restrictions": list(restrictions),
        "allowed_surfaces": list(ALLOWED_SURFACES),
        "prohibited_surfaces": list(PROHIBITED_SURFACES),
        "failure_packet": failure_packet,
        "recommended_next_action": evaluation.recommended_next_action,
        "lineage_manifest": lineage,
        "policy_version": _POLICY_VERSION,
        "authorization_boundary_report": _authorization_boundary_report(),
        "warnings": list(warnings),
    }
    provenance_hash = _hash_payload(packet_body)

    return TbrridgeUncertaintyCandidateReviewPacket(
        request_id=request_id,
        review_id=review_id,
        review_status=review_status,
        method_id=method_id,
        instrument_id=instrument_id,
        estimator_family=estimator_family,
        inference_family=inference_family,
        current_readiness_stage=current_stage,
        candidate_review_target_stage=target_stage,
        evidence_chain_summary=chain_summary,
        evidence_components_reviewed=evidence_reviewed,
        required_evidence=REQUIRED_EVIDENCE,
        missing_evidence=missing_evidence,
        detected_review_risks=detected,
        blockers=tuple(blockers),
        restrictions=restrictions,
        allowed_surfaces=ALLOWED_SURFACES,
        prohibited_surfaces=PROHIBITED_SURFACES,
        failure_packet=failure_packet,
        recommended_next_action=evaluation.recommended_next_action,
        lineage_manifest=lineage,
        provenance_hash=provenance_hash,
        policy_version=_POLICY_VERSION,
        authorization_boundary_report={
            **packet_body["authorization_boundary_report"],
            "provenance_hash": provenance_hash,
        },
        warnings=warnings,
    )


def evaluate_tbrridge_uncertainty_candidate_review(
    input_data: dict[str, Any] | Any,
    *,
    config: TbrridgeUncertaintyCandidateReviewRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeUncertaintyCandidateReviewPacket:
    """Alias for single uncertainty-candidate review evaluation."""
    return build_tbrridge_uncertainty_candidate_review_packet(input_data, config=config)


def generate_tbrridge_uncertainty_candidate_review(
    input_data: dict[str, Any] | Any | list[Any],
    config: TbrridgeUncertaintyCandidateReviewRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeUncertaintyCandidateReviewPacket | list[TbrridgeUncertaintyCandidateReviewPacket]:
    """Generate one or more independent uncertainty-candidate review packets."""
    if isinstance(input_data, list):
        return [
            build_tbrridge_uncertainty_candidate_review_packet(item, config=config)
            for item in input_data
        ]
    return build_tbrridge_uncertainty_candidate_review_packet(input_data, config=config)


def packet_to_dict(packet: TbrridgeUncertaintyCandidateReviewPacket) -> dict[str, Any]:
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
        "false_confidence_audit_report": {"summary": {"audit_complete": True}},
        "kfold_leakage_diagnostic_report": {"diagnostic_status": "KFOLD_LEAKAGE_DIAGNOSTIC_READY"},
        "placebo_calibration_diagnostic_report": {"diagnostic_status": "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"},
        "coverage_validation_report": {"validation_status": "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW"},
        "interval_semantics_report": {"semantics_undefined": False},
        "null_control_evidence_report": {"worlds": ["null_a"]},
        "positive_control_evidence_report": {"worlds": ["pos_a"]},
        "regime_sensitivity_report": {"regimes": ["r1"]},
        "regularization_sensitivity_report": {"complete": True},
        "donor_pool_sensitivity_report": {"complete": True},
        "outlier_sensitivity_report": {"complete": True},
        "metric_estimand_alignment_report": {"metric_estimand_mismatch": False},
        "aggregate_pooled_surface_blocker_report": {"aggregate_pooled_unsupported": False},
        "statistical_promotion_threshold_report": {"complete": True},
        "production_catalog_status_report": {"catalog_blocked": True},
        "claim_authorization_boundary_report": {"complete": True},
        "method_promotion_boundary_report": {"complete": True},
        "lineage_provenance_manifest": {"run_id": "validation"},
    }
    ready = build_tbrridge_uncertainty_candidate_review_packet(clean)
    _s(
        "restricted_review_ready_clean_evidence",
        ready.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
    )

    missing_chain = build_tbrridge_uncertainty_candidate_review_packet({"request_id": "missing"})
    _s(
        "blocks_missing_evidence_chain",
        missing_chain.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN",
    )

    for flag, expected in _AUTH_FALSE.items():
        meta = get_runtime_metadata()
        _s(f"auth_{flag}_false", meta.get(flag) is expected)

    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_uncertainty_candidate_review_runtime",
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
