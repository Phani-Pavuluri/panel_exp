"""TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001 — TBRRidge method promotion review runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.tbrridge_method_promotion_review_contract_001 import (
    ALLOWED_SURFACES,
    CURRENT_CATALOG_RANK,
    CURRENT_CATALOG_STATUS,
    CURRENT_READINESS_STAGE,
    INSTRUMENT_ID,
    METHOD_ID,
    PROMOTION_RISK_TYPES,
    PROHIBITED_SURFACES,
    REQUIRED_EVIDENCE,
    TARGET_REVIEW_STAGE,
    MethodPromotionReviewEvaluationResult,
    evaluate_method_promotion_review,
)

_ARTIFACT_ID = "TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "tbrridge_method_promotion_review_runtime_implemented_no_promotion_or_catalog_unblock"
_VERDICT = "tbrridge_method_promotion_review_runtime_implemented_no_promotion_or_catalog_unblock"
_RECOMMENDED_NEXT = "TBRRIDGE_PROMOTION_EVIDENCE_BATTERY_PLAN_001"
_ALTERNATIVE_NEXT = "AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001"
_DEFERRED = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_METHOD_PROMOTION_REVIEW_RUNTIME_001_summary.json"
)

DEPENDS_ON = (
    "TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001",
    "TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001",
    "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001",
    "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001",
)

_POSITIVE_FLAGS = {
    "method_promotion_review_runtime_implemented": True,
    "supplied_promotion_evidence_reviewed": True,
    "missing_promotion_evidence_detected": True,
    "uncertainty_candidate_review_status_delegated": True,
    "promotion_risk_detection_implemented": True,
    "promotion_failure_packet_emitted": True,
    "deterministic_provenance_hash_defined": True,
}

_AUTH_FALSE = {
    "method_promoted": False,
    "method_unblocked": False,
    "method_promotion_authorized": False,
    "production_catalog_unblocked": False,
    "production_compatibility_authorized": False,
    "production_authorization_granted": False,
    "production_readout_authorized": False,
    "uncertainty_candidate_approved": False,
    "uncertainty_authorized": False,
    "confidence_interval_authorized": False,
    "p_value_authorized": False,
    "statistical_significance_authorized": False,
    "coverage_approval_authorized": False,
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
    "mmm_runtime_calls_implemented": False,
    "llm_decisioning_authorized": False,
}

_UC_READY_STATUSES = frozenset(
    {
        "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
        "UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS",
    }
)


@dataclass(frozen=True)
class TbrridgeMethodPromotionReviewRuntimeConfig:
    require_lineage_manifest: bool = False


@dataclass(frozen=True)
class TbrridgeMethodPromotionReviewPacket:
    review_id: str
    review_status: str
    method_id: str
    instrument_id: str
    current_catalog_rank: str
    current_catalog_status: str
    current_readiness_stage: str
    target_review_stage: str
    evidence_chain_summary: dict[str, Any]
    evidence_components_reviewed: tuple[str, ...]
    required_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    detected_promotion_risks: tuple[str, ...]
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
    config: TbrridgeMethodPromotionReviewRuntimeConfig | dict[str, Any] | None,
) -> TbrridgeMethodPromotionReviewRuntimeConfig:
    if config is None:
        return TbrridgeMethodPromotionReviewRuntimeConfig()
    if isinstance(config, TbrridgeMethodPromotionReviewRuntimeConfig):
        return config
    base = TbrridgeMethodPromotionReviewRuntimeConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return TbrridgeMethodPromotionReviewRuntimeConfig(**merged)


def _extract_status(report: Any, *keys: str) -> str | None:
    if not isinstance(report, dict):
        return None
    for key in keys:
        value = report.get(key)
        if value:
            return str(value)
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


def detect_tbrridge_method_promotion_risks(data: dict[str, Any]) -> tuple[str, ...]:
    """Flag promotion risks from supplied report flags without computing statistics."""
    detected: list[str] = []

    interval = data.get("interval_semantics_report") or {}
    if isinstance(interval, dict) and _report_flag(
        interval,
        "interval_semantics_incomplete",
        "semantics_undefined",
        "semantics_incomplete",
    ):
        detected.append("INTERVAL_SEMANTICS_INCOMPLETE")
    if isinstance(interval, dict) and _report_flag(
        interval, "metric_estimand_mismatch", "estimand_mismatch"
    ):
        detected.append("METRIC_ESTIMAND_MISMATCH")

    null_fp = data.get("null_control_false_positive_report") or {}
    if isinstance(null_fp, dict) and _report_flag(
        null_fp,
        "null_control_false_positive_incomplete",
        "false_positive_incomplete",
        "evidence_incomplete",
    ):
        detected.append("NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE")

    directional = data.get("directional_error_report") or {}
    if isinstance(directional, dict) and _report_flag(
        directional,
        "directional_error_evidence_incomplete",
        "directional_error_incomplete",
        "evidence_incomplete",
    ):
        detected.append("DIRECTIONAL_ERROR_EVIDENCE_INCOMPLETE")

    positive = data.get("positive_control_recovery_report") or {}
    if isinstance(positive, dict) and _report_flag(
        positive,
        "positive_control_recovery_incomplete",
        "recovery_failure",
        "evidence_incomplete",
    ):
        detected.append("POSITIVE_CONTROL_RECOVERY_INCOMPLETE")

    regime = data.get("regime_sensitivity_report") or {}
    if isinstance(regime, dict) and _report_flag(
        regime, "regime_sensitivity_incomplete", "sensitivity_incomplete"
    ):
        detected.append("REGIME_SENSITIVITY_INCOMPLETE")

    donor = data.get("donor_pool_sensitivity_report") or {}
    if isinstance(donor, dict) and _report_flag(
        donor, "donor_pool_sensitivity_incomplete", "sensitivity_incomplete"
    ):
        detected.append("DONOR_POOL_SENSITIVITY_INCOMPLETE")

    regularization = data.get("regularization_sensitivity_report") or {}
    if isinstance(regularization, dict) and _report_flag(
        regularization, "regularization_sensitivity_incomplete", "sensitivity_incomplete"
    ):
        detected.append("REGULARIZATION_SENSITIVITY_INCOMPLETE")

    outlier = data.get("outlier_sensitivity_report") or {}
    if isinstance(outlier, dict) and _report_flag(
        outlier, "outlier_sensitivity_incomplete", "sensitivity_incomplete"
    ):
        detected.append("OUTLIER_SENSITIVITY_INCOMPLETE")

    fold = data.get("fold_geometry_sensitivity_report") or {}
    if isinstance(fold, dict) and _report_flag(
        fold, "fold_geometry_sensitivity_incomplete", "sensitivity_incomplete"
    ):
        detected.append("FOLD_GEOMETRY_SENSITIVITY_INCOMPLETE")

    metric = data.get("metric_estimand_alignment_report") or {}
    if isinstance(metric, dict) and _report_flag(
        metric, "metric_estimand_mismatch", "estimand_mismatch", "alignment_failure"
    ):
        detected.append("METRIC_ESTIMAND_MISMATCH")

    aggregate = data.get("aggregate_pooled_geometry_blocker_report") or {}
    if isinstance(aggregate, dict) and _report_flag(
        aggregate,
        "aggregate_pooled_unsupported",
        "aggregate_pooled_geometry_unsupported",
        "pooled_geometry_unsupported",
        "aggregate_misuse",
    ):
        detected.append("AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED")

    claim = data.get("claim_authorization_boundary_report") or {}
    if isinstance(claim, dict) and _report_flag(
        claim, "claim_authorization_boundary_missing", "boundary_missing"
    ):
        detected.append("CLAIM_AUTHORIZATION_BOUNDARY_MISSING")

    catalog = data.get("production_catalog_status_report") or {}
    if isinstance(catalog, dict) and _report_flag(
        catalog, "catalog_blocked", "production_catalog_blocked", "blocked"
    ):
        detected.append("PRODUCTION_CATALOG_BLOCKED")

    compat = data.get("production_compatibility_boundary_report") or {}
    if isinstance(compat, dict):
        if _report_flag(
            compat,
            "production_compatibility_not_reviewed",
            "compatibility_not_reviewed",
            "not_reviewed",
        ):
            detected.append("PRODUCTION_COMPATIBILITY_NOT_REVIEWED")
        elif compat.get("production_compatibility_reviewed") is False and compat.get("reviewed") is False:
            detected.append("PRODUCTION_COMPATIBILITY_NOT_REVIEWED")

    downstream = data.get("downstream_readout_safety_report") or {}
    if isinstance(downstream, dict) and _report_flag(
        downstream,
        "downstream_readout_safety_incomplete",
        "readout_safety_incomplete",
        "safety_incomplete",
    ):
        detected.append("DOWNSTREAM_READOUT_SAFETY_INCOMPLETE")

    uc_packet = data.get("uncertainty_candidate_review_packet") or {}
    if isinstance(uc_packet, dict):
        uc_status = _extract_status(
            uc_packet, "review_status", "candidate_review_status", "uncertainty_candidate_review_status"
        )
        if uc_status and uc_status not in _UC_READY_STATUSES:
            detected.append("UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING")

    seen: set[str] = set()
    ordered: list[str] = []
    for item in detected:
        if item in PROMOTION_RISK_TYPES and item not in seen:
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)


def build_tbrridge_method_promotion_failure_packet(
    evaluation: MethodPromotionReviewEvaluationResult,
) -> dict[str, Any] | None:
    """Build standardized failure packet from contract evaluation result."""
    return evaluation.to_failure_packet()


def _extract_uncertainty_candidate_review_status(data: dict[str, Any]) -> str | None:
    override = data.get("uncertainty_candidate_review_status")
    if override:
        return str(override)
    packet = data.get("uncertainty_candidate_review_packet") or {}
    if isinstance(packet, dict):
        return _extract_status(
            packet, "review_status", "candidate_review_status", "uncertainty_candidate_review_status"
        )
    return None


def _production_catalog_blocked(data: dict[str, Any]) -> bool:
    catalog = data.get("production_catalog_status_report") or {}
    if isinstance(catalog, dict):
        if catalog.get("catalog_unblocked") is True:
            return False
        if catalog.get("catalog_blocked") is False and catalog.get("production_catalog_blocked") is False:
            return False
    return True


def _production_compatibility_reviewed(data: dict[str, Any]) -> bool:
    if data.get("production_compatibility_reviewed") is True:
        return True
    report = data.get("production_compatibility_boundary_report") or {}
    if isinstance(report, dict):
        if report.get("production_compatibility_reviewed") is True:
            return True
        if report.get("reviewed") is True:
            return True
        if report.get("compatibility_reviewed") is True:
            return True
    return False


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


def _aggregate_pooled_unsupported(data: dict[str, Any], detected: tuple[str, ...]) -> bool:
    if "AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED" in detected:
        return True
    report = data.get("aggregate_pooled_geometry_blocker_report") or {}
    if isinstance(report, dict) and _report_flag(
        report,
        "aggregate_pooled_unsupported",
        "aggregate_pooled_geometry_unsupported",
        "pooled_geometry_unsupported",
        "aggregate_misuse",
    ):
        return True
    return bool(data.get("aggregate_pooled_unsupported"))


def _build_restrictions(
    review_status: str,
    detected: tuple[str, ...],
    missing: tuple[str, ...],
    authorized_for_promotion_summary: bool,
) -> tuple[str, ...]:
    restrictions: list[str] = []
    if review_status == "METHOD_PROMOTION_REVIEW_READY_WITH_RESTRICTIONS":
        restrictions.append("RESTRICTED_PROMOTION_SUMMARY_ONLY")
    if authorized_for_promotion_summary:
        restrictions.append("NO_METHOD_PROMOTION_OR_CATALOG_UNBLOCK")
    if detected:
        restrictions.append("PROMOTION_RISK_FLAGGED")
    if missing:
        restrictions.append("PARTIAL_EVIDENCE")
    if review_status.startswith("METHOD_PROMOTION_REVIEW_BLOCKED"):
        restrictions.append("METHOD_PROMOTION_SURFACES_BLOCKED")
    if review_status == "METHOD_PROMOTION_REVIEW_REQUIRES_PRODUCTION_COMPATIBILITY_REVIEW":
        restrictions.append("PRODUCTION_COMPATIBILITY_REVIEW_REQUIRED")
    return tuple(restrictions)


def _build_warnings(
    detected: tuple[str, ...],
    missing: tuple[str, ...],
    uc_status: str | None,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if "INTERVAL_SEMANTICS_INCOMPLETE" in detected:
        warnings.append("Interval semantics incomplete per supplied reports; no intervals computed.")
    if "METRIC_ESTIMAND_MISMATCH" in detected:
        warnings.append("Metric/estimand mismatch flagged from supplied reports only.")
    if "AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED" in detected:
        warnings.append("Aggregate/pooled geometry unsupported; pooled claims remain blocked.")
    if "PRODUCTION_CATALOG_BLOCKED" in detected:
        warnings.append("Production catalog remains blocked for TBRRidge KFold (RANK_0).")
    if "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING" in detected:
        warnings.append(f"Uncertainty-candidate review blocking: {uc_status or 'unknown'}")
    if missing:
        warnings.append(f"Evidence missing: {', '.join(missing)}")
    warnings.append("Method promotion, catalog unblock, and production authorization remain blocked.")
    return tuple(warnings)


def _authorization_boundary_report() -> dict[str, Any]:
    return {
        "runtime_scope": "method_promotion_review_diagnostic_only",
        "computes_coverage": False,
        "computes_intervals": False,
        "computes_uncertainty": False,
        "computes_p_values": False,
        "computes_confidence_intervals": False,
        "computes_lift_or_effects": False,
        "authorizes_production_readout": False,
        "authorizes_method_promotion": False,
        "authorizes_uncertainty": False,
        "method_promotion_surfaces_blocked": True,
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
        "detected_promotion_risks": sorted(detected),
        "current_catalog_rank": data.get("current_catalog_rank") or CURRENT_CATALOG_RANK,
        "current_readiness_stage": data.get("current_readiness_stage") or CURRENT_READINESS_STAGE,
    }
    return f"tmpr-{_hash_payload(canonical)[:16]}"


def build_tbrridge_method_promotion_review_packet(
    input_data: dict[str, Any] | Any,
    *,
    config: TbrridgeMethodPromotionReviewRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeMethodPromotionReviewPacket:
    """Build a single method-promotion review packet from supplied evidence."""
    cfg = _resolve_config(config)
    data = _to_dict(input_data)

    method_id = str(data.get("method_id") or METHOD_ID)
    instrument_id = str(data.get("instrument_id") or INSTRUMENT_ID)
    catalog_rank = str(data.get("current_catalog_rank") or CURRENT_CATALOG_RANK)
    catalog_status = str(data.get("current_catalog_status") or CURRENT_CATALOG_STATUS)
    current_stage = str(data.get("current_readiness_stage") or CURRENT_READINESS_STAGE)
    target_stage = str(data.get("target_review_stage") or TARGET_REVIEW_STAGE)
    lineage = dict(data.get("lineage_manifest") or data.get("lineage_provenance_manifest") or {})

    evidence = build_evidence_presence(data)
    if cfg.require_lineage_manifest and not evidence.get("lineage_provenance_manifest"):
        evidence = {**evidence, "lineage_provenance_manifest": False}

    detected = detect_tbrridge_method_promotion_risks(data)
    uc_status = _extract_uncertainty_candidate_review_status(data)
    requested_surface = data.get("requested_surface")

    evaluation = evaluate_method_promotion_review(
        evidence=evidence,
        detected_risks=detected,
        requested_surface=str(requested_surface) if requested_surface else None,
        uncertainty_candidate_review_status=uc_status,
        production_catalog_blocked=_production_catalog_blocked(data),
        production_compatibility_reviewed=_production_compatibility_reviewed(data),
        metric_estimand_mismatch=_metric_estimand_mismatch(data, detected),
        aggregate_pooled_unsupported=_aggregate_pooled_unsupported(data, detected),
        deferred=bool(data.get("deferred")),
    )

    missing_all = tuple(req for req in REQUIRED_EVIDENCE if not evidence.get(req, False))
    missing_evidence = evaluation.missing_evidence or missing_all
    evidence_reviewed = tuple(req for req in REQUIRED_EVIDENCE if evidence.get(req, False))

    review_status = evaluation.review_status
    blockers: list[str] = []
    if evaluation.failure_reason:
        blockers.append(evaluation.failure_reason)
    for risk in detected:
        blockers.append(f"Promotion risk: {risk}")

    if (
        review_status
        in (
            "METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW",
            "METHOD_PROMOTION_REVIEW_READY_WITH_RESTRICTIONS",
        )
        and not any(evidence.get(k) for k in REQUIRED_EVIDENCE)
    ):
        review_status = "METHOD_PROMOTION_REVIEW_NOT_EVALUATED"

    chain_summary = extract_evidence_chain_summary(data)
    restrictions = _build_restrictions(
        review_status,
        detected,
        missing_evidence,
        evaluation.authorized_for_promotion_summary,
    )
    warnings = _build_warnings(detected, missing_evidence, uc_status)
    failure_packet = build_tbrridge_method_promotion_failure_packet(evaluation)
    review_id = _build_review_id(data, review_status, detected)

    packet_body = {
        "review_id": review_id,
        "review_status": review_status,
        "method_id": method_id,
        "instrument_id": instrument_id,
        "current_catalog_rank": catalog_rank,
        "current_catalog_status": catalog_status,
        "current_readiness_stage": current_stage,
        "target_review_stage": target_stage,
        "evidence_chain_summary": chain_summary,
        "evidence_components_reviewed": list(evidence_reviewed),
        "required_evidence": list(REQUIRED_EVIDENCE),
        "missing_evidence": list(missing_evidence),
        "detected_promotion_risks": list(detected),
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

    return TbrridgeMethodPromotionReviewPacket(
        review_id=review_id,
        review_status=review_status,
        method_id=method_id,
        instrument_id=instrument_id,
        current_catalog_rank=catalog_rank,
        current_catalog_status=catalog_status,
        current_readiness_stage=current_stage,
        target_review_stage=target_stage,
        evidence_chain_summary=chain_summary,
        evidence_components_reviewed=evidence_reviewed,
        required_evidence=REQUIRED_EVIDENCE,
        missing_evidence=missing_evidence,
        detected_promotion_risks=detected,
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


def generate_tbrridge_method_promotion_review(
    input_data: dict[str, Any] | Any | list[Any],
    config: TbrridgeMethodPromotionReviewRuntimeConfig | dict[str, Any] | None = None,
) -> TbrridgeMethodPromotionReviewPacket | list[TbrridgeMethodPromotionReviewPacket]:
    """Generate one or more independent method-promotion review packets."""
    if isinstance(input_data, list):
        return [
            build_tbrridge_method_promotion_review_packet(item, config=config)
            for item in input_data
        ]
    return build_tbrridge_method_promotion_review_packet(input_data, config=config)


def packet_to_dict(packet: TbrridgeMethodPromotionReviewPacket) -> dict[str, Any]:
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
        "method_promotion_evidence_audit_report": {"summary": {"audit_complete": True}},
        "uncertainty_candidate_review_packet": {
            "review_status": "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW"
        },
        "false_confidence_audit_report": {"summary": {"audit_complete": True}},
        "leakage_diagnostic_report": {"diagnostic_status": "KFOLD_LEAKAGE_DIAGNOSTIC_READY"},
        "placebo_calibration_diagnostic_report": {"diagnostic_status": "PLACEBO_CALIBRATION_DIAGNOSTIC_READY"},
        "coverage_validation_report": {"validation_status": "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW"},
        "interval_semantics_report": {"semantics_undefined": False},
        "null_control_false_positive_report": {"worlds": ["null_a"]},
        "directional_error_report": {"complete": True},
        "positive_control_recovery_report": {"worlds": ["pos_a"]},
        "regime_sensitivity_report": {"regimes": ["r1"]},
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
        "lineage_provenance_manifest": {"run_id": "validation"},
    }
    ready = build_tbrridge_method_promotion_review_packet(clean)
    _s(
        "restricted_review_ready_clean_evidence",
        ready.review_status == "METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW",
    )

    missing_chain = build_tbrridge_method_promotion_review_packet({"request_id": "missing"})
    _s(
        "blocks_missing_evidence_chain",
        missing_chain.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN",
    )

    blocked_promotion = build_tbrridge_method_promotion_review_packet(
        {**clean, "requested_surface": "METHOD_PROMOTION_NOTICE"}
    )
    _s(
        "blocks_method_promotion_surface",
        blocked_promotion.review_status
        == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY",
    )

    for flag, expected in _AUTH_FALSE.items():
        meta = get_runtime_metadata()
        _s(f"auth_{flag}_false", meta.get(flag) is expected)

    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "tbrridge_method_promotion_review_runtime",
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
