"""METHOD_PROMOTION_REVIEW_RUNTIME_001 — governed method promotion review packet runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.assignment_panel_integrity_runtime_001 import (
    ASSIGNMENT_PANEL_INTEGRITY_BLOCKED,
    ASSIGNMENT_PANEL_INTEGRITY_FAILED,
)
from panel_exp.validation.claim_authorization_runtime_001 import (
    CLAIM_AUTHORIZATION_BLOCKED,
    ClaimAuthorizationRuntimeReport,
)
from panel_exp.validation.method_promotion_review_contract_001 import (
    PROHIBITED_SURFACES,
    SCOPE_EVIDENCE_REQUIREMENTS,
)
from panel_exp.validation.method_suitability_runtime_001 import MethodFamilySuitabilityStatus
from panel_exp.validation.production_catalog_blocklist_001 import PRODUCTION_CATALOG_BLOCKED
from panel_exp.validation.srm_balance_readout_diagnostic_001 import (
    SRM_BALANCE_DIAGNOSTIC_BLOCKED,
    SRM_BALANCE_DIAGNOSTIC_FAILED,
)
from panel_exp.validation.statistical_promotion_thresholds_001 import (
    STATISTICAL_PROMOTION_BLOCKED,
    STATISTICAL_PROMOTION_FAILED,
)
from panel_exp.validation.trusted_readout_report_runtime_001 import (
    TRUSTED_REPORT_READY_WITH_REDACTIONS,
    TrustedReadoutReportRuntimeReport,
)

_ARTIFACT_ID = "METHOD_PROMOTION_REVIEW_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "method_promotion_review_runtime_implemented_no_method_promotion_or_production_authorization"
_VERDICT = "method_promotion_review_runtime_implemented_no_method_promotion_or_production_authorization"
_RECOMMENDED_NEXT = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001"
_ALTERNATIVE_NEXT = "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/METHOD_PROMOTION_REVIEW_RUNTIME_001_summary.json"

FAILURE_MISSING_REQUIRED_EVIDENCE = "MISSING_REQUIRED_EVIDENCE"
FAILURE_METHOD_SUITABILITY_BLOCKED = "METHOD_SUITABILITY_BLOCKED"
FAILURE_PRODUCTION_CATALOG_BLOCKED = "PRODUCTION_CATALOG_BLOCKED"
FAILURE_STATISTICAL_PROMOTION_BLOCKED = "STATISTICAL_PROMOTION_BLOCKED"
FAILURE_ASSIGNMENT_INTEGRITY_BLOCKED = "ASSIGNMENT_INTEGRITY_BLOCKED"
FAILURE_SRM_BALANCE_BLOCKED = "SRM_BALANCE_BLOCKED"
FAILURE_TRUSTED_READOUT_BLOCKED = "TRUSTED_READOUT_BLOCKED"
FAILURE_CLAIM_AUTHORIZATION_BLOCKED = "CLAIM_AUTHORIZATION_BLOCKED"
FAILURE_HUMAN_GOVERNANCE_REQUIRED = "HUMAN_GOVERNANCE_REQUIRED"
FAILURE_PROMOTION_REVIEW_BLOCKED_BY_POLICY = "PROMOTION_REVIEW_BLOCKED_BY_POLICY"

_CLAIM_TO_PROHIBITED_SURFACE = {
    "CAUSAL_CLAIM": "CAUSAL_CERTIFIED",
    "INCREMENTAL_LIFT_CLAIM": "INCREMENTAL_LIFT_CERTIFIED",
    "ROI_CLAIM": "ROI_CERTIFIED",
    "STATISTICAL_SIGNIFICANCE_CLAIM": "STATISTICAL_SIGNIFICANCE_CERTIFIED",
    "CONFIDENCE_INTERVAL_CLAIM": "CONFIDENCE_INTERVAL_CERTIFIED",
    "TRUSTED_BUSINESS_RECOMMENDATION": "TRUSTED_BUSINESS_RECOMMENDATION",
    "PRODUCTION_READOUT_CLAIM": "PRODUCTION_APPROVED",
}

_ELIGIBLE_SURFACES = (
    "RESEARCH_READOUT_SURFACE",
    "RESTRICTED_EXPERT_REVIEW_SURFACE",
    "PROMOTION_REVIEW_PACKET_SURFACE",
    "GOVERNED_EVIDENCE_REVIEW_SURFACE",
)

_POSITIVE_FLAGS = {
    "method_promotion_review_runtime_implemented": True,
    "method_promotion_review_packet_generated": True,
    "promotion_review_evidence_binding_enforced": True,
    "promotion_review_blockers_enforced": True,
    "promotion_review_restrictions_propagated": True,
    "promotion_review_caveats_propagated": True,
    "lineage_provenance_recorded": True,
}

_AUTH_FALSE = {
    "method_promoted": False,
    "method_unblocked": False,
    "production_catalog_unblocked": False,
    "production_authorization_granted": False,
    "production_readout_authorized": False,
    "trusted_business_recommendation_authorized": False,
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
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}

_FORBIDDEN_VERDICTS = frozenset({
    "PROMOTED",
    "PRODUCTION_APPROVED",
    "METHOD_UNBLOCKED",
    "CATALOG_UPDATED",
    "AUTHORIZED_FOR_PRODUCTION",
})


@dataclass(frozen=True)
class MethodPromotionReviewRuntimeConfig:
    require_trusted_readout_report: bool = True
    require_claim_authorization_report: bool = True
    require_human_governance_for_production_scope: bool = True
    propagate_trusted_readout_restrictions: bool = True


@dataclass(frozen=True)
class MethodPromotionReviewSection:
    section_id: str
    section_type: str
    section_status: str
    bound_evidence_ids: tuple[str, ...]
    blockers: tuple[str, ...]
    restrictions: tuple[str, ...]
    required_caveats: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    trace: dict[str, Any]


@dataclass(frozen=True)
class MethodPromotionReviewRuntimeReport:
    request_id: str
    review_id: str
    review_status: str
    candidate_verdict: str
    method_id: str | None
    instrument_id: str | None
    estimator_family: str | None
    inference_family: str | None
    current_catalog_status: str | None
    requested_promotion_scope: str | None
    evidence_bundle_summary: dict[str, Any]
    missing_evidence: tuple[str, ...]
    failed_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    restrictions: tuple[str, ...]
    required_caveats: tuple[str, ...]
    eligible_surfaces: tuple[str, ...]
    prohibited_surfaces: tuple[str, ...]
    review_sections: tuple[MethodPromotionReviewSection, ...]
    lineage_manifest: dict[str, Any]
    provenance_hash: str
    policy_version: str
    failure_packet: dict[str, Any] | None
    warnings: tuple[str, ...]
    authorization_boundary_report: dict[str, Any]


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _token(value: Any) -> str:
    return str(value).strip().upper() if value is not None else ""


def _hash_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _safe_str_list(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(v for v in values if v))


def _resolve_config(
    config: MethodPromotionReviewRuntimeConfig | dict[str, Any] | None,
) -> MethodPromotionReviewRuntimeConfig:
    if config is None:
        return MethodPromotionReviewRuntimeConfig()
    if isinstance(config, MethodPromotionReviewRuntimeConfig):
        return config
    base = MethodPromotionReviewRuntimeConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return MethodPromotionReviewRuntimeConfig(**merged)


def _report_status(report: Any) -> str:
    if report is None:
        return ""
    data = _to_dict(report)
    for key in (
        "status",
        "overall_status",
        "report_status",
        "suitability_status",
        "promotion_status",
        "evidence_sufficiency_status",
    ):
        if data.get(key):
            return _token(data[key])
    return ""


def _report_present(report: Any) -> bool:
    if report is None:
        return False
    if isinstance(report, (dict, list, tuple)):
        return bool(report)
    if is_dataclass(report):
        return True
    return bool(report)


def _evidence_id(key: str, data: dict[str, Any]) -> str:
    report = data.get(key)
    if isinstance(report, dict):
        for field_name in ("artifact_id", "report_id", "review_id", "request_id", "status"):
            if report.get(field_name):
                return f"{key}:{report[field_name]}"
    if isinstance(report, (TrustedReadoutReportRuntimeReport, ClaimAuthorizationRuntimeReport)):
        converted = _to_dict(report)
        for field_name in ("report_id", "request_id", "overall_status"):
            if converted.get(field_name):
                return f"{key}:{converted[field_name]}"
    return key if _report_present(report) else ""


def _scope_token(data: dict[str, Any]) -> str:
    scope = _token(data.get("requested_promotion_scope"))
    if scope in SCOPE_EVIDENCE_REQUIREMENTS:
        return scope
    return "PRODUCTION_REVIEW"


def _required_evidence_for_scope(scope: str) -> tuple[str, ...]:
    return SCOPE_EVIDENCE_REQUIREMENTS.get(scope, SCOPE_EVIDENCE_REQUIREMENTS["PRODUCTION_REVIEW"])


def _evidence_present(data: dict[str, Any], requirement: str) -> bool:
    if requirement == "method_instrument_identity":
        return bool(data.get("method_id")) and bool(data.get("instrument_id"))
    if requirement == "current_production_catalog_status":
        return bool(data.get("current_catalog_status")) or _report_present(data.get("production_catalog_report"))
    if requirement == "method_suitability_report":
        return _report_present(data.get("method_suitability_report"))
    if requirement == "statistical_promotion_report":
        return _report_present(data.get("statistical_promotion_report"))
    if requirement == "trusted_readout_report_packet":
        return _report_present(data.get("trusted_readout_report"))
    if requirement == "claim_authorization_report":
        return _report_present(data.get("claim_authorization_report"))
    if requirement == "diagnostics_sensitivity_report":
        return _report_present(data.get("diagnostics_sensitivity_report"))
    if requirement == "srm_balance_diagnostic_report":
        return _report_present(data.get("srm_balance_diagnostic_report"))
    if requirement == "assignment_panel_integrity_report":
        return _report_present(data.get("assignment_panel_integrity_report"))
    if requirement == "governed_randomization_report":
        return _report_present(data.get("governed_randomization_report"))
    if requirement == "execution_readout_provenance":
        return _report_present(data.get("execution_result")) or _report_present(data.get("readout_plan_report"))
    if requirement == "validation_history_audit_references":
        refs = data.get("audit_registry_refs")
        return bool(refs) if isinstance(refs, (list, dict, tuple)) else _report_present(refs)
    if requirement == "known_limitations_and_blockers":
        limitations = data.get("known_limitations")
        return bool(limitations) if isinstance(limitations, (list, tuple)) else _report_present(limitations)
    if requirement == "lineage_manifest":
        return _report_present(data.get("lineage_manifest"))
    return False


def _catalog_status(data: dict[str, Any]) -> str:
    if data.get("current_catalog_status"):
        return _token(data["current_catalog_status"])
    report = data.get("production_catalog_report")
    status = _report_status(report)
    if status:
        return status
    if isinstance(report, dict):
        return _token(report.get("production_catalog_status"))
    return ""


def _method_suitability_status(data: dict[str, Any]) -> str:
    report = data.get("method_suitability_report")
    if not report:
        return ""
    converted = _to_dict(report)
    if converted.get("suitability_status"):
        return _token(converted["suitability_status"])
    families = converted.get("method_family_suitability_reports") or []
    if isinstance(families, list) and families:
        first = _to_dict(families[0])
        return _token(first.get("suitability_status"))
    return _report_status(report)


def _trusted_readout_status(data: dict[str, Any]) -> str:
    report = data.get("trusted_readout_report")
    if report is None:
        return ""
    if isinstance(report, TrustedReadoutReportRuntimeReport):
        return _token(report.report_status)
    return _token(_to_dict(report).get("report_status"))


def _claim_authorization_status(data: dict[str, Any]) -> str:
    report = data.get("claim_authorization_report")
    if report is None:
        return ""
    if isinstance(report, ClaimAuthorizationRuntimeReport):
        return _token(report.overall_status)
    return _token(_to_dict(report).get("overall_status"))


def _collect_missing_evidence(data: dict[str, Any], scope: str) -> list[str]:
    missing: list[str] = []
    for req in _required_evidence_for_scope(scope):
        if not _evidence_present(data, req):
            missing.append(req)
    return missing


def _build_failure_packet(
    *,
    failure_code: str,
    failure_reason: str,
    missing_evidence: tuple[str, ...],
    failed_evidence: tuple[str, ...],
    blockers: tuple[str, ...],
    retry_category: str,
    required_remediation: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "failure_code": failure_code,
        "failure_reason": failure_reason,
        "missing_evidence": list(missing_evidence),
        "failed_evidence": list(failed_evidence),
        "blockers": list(blockers),
        "required_remediation": list(required_remediation or blockers),
        "retry_category": retry_category,
    }


def _build_section(
    *,
    section_type: str,
    section_status: str,
    request_id: str,
    bound_evidence: tuple[str, ...],
    blockers: tuple[str, ...] = (),
    restrictions: tuple[str, ...] = (),
    caveats: tuple[str, ...] = (),
    missing_evidence: tuple[str, ...] = (),
    trace: dict[str, Any] | None = None,
) -> MethodPromotionReviewSection:
    return MethodPromotionReviewSection(
        section_id=f"{request_id}:{section_type.lower()}",
        section_type=section_type,
        section_status=section_status,
        bound_evidence_ids=bound_evidence,
        blockers=blockers,
        restrictions=restrictions,
        required_caveats=caveats,
        missing_evidence=missing_evidence,
        trace=trace or {},
    )


def _prohibited_from_claims(data: dict[str, Any]) -> list[str]:
    prohibited: list[str] = []
    report = data.get("claim_authorization_report")
    if report is None:
        return prohibited
    blocked: list[str] = []
    if isinstance(report, ClaimAuthorizationRuntimeReport):
        blocked = list(report.blocked_claims)
    elif isinstance(report, dict):
        blocked = list(report.get("blocked_claims") or [])
        for row in report.get("claim_authorizations") or []:
            row_dict = _to_dict(row)
            if _token(row_dict.get("authorization_status")) == "CLAIM_BLOCKED":
                claim_type = _token(row_dict.get("claim_type"))
                if claim_type:
                    blocked.append(claim_type)
    for claim_type in blocked:
        surface = _CLAIM_TO_PROHIBITED_SURFACE.get(_token(claim_type))
        if surface:
            prohibited.append(surface)
    return prohibited


def _restrictions_and_caveats_from_trusted_readout(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    restrictions: list[str] = []
    caveats: list[str] = []
    report = data.get("trusted_readout_report")
    if report is None:
        return restrictions, caveats
    converted = _to_dict(report)
    if converted.get("restricted_sections"):
        restrictions.extend(str(s) for s in converted["restricted_sections"])
    if converted.get("redacted_sections"):
        restrictions.extend(f"REDACTED:{s}" for s in converted["redacted_sections"])
    if converted.get("required_caveats"):
        caveats.extend(str(c) for c in converted["required_caveats"])
    if isinstance(report, TrustedReadoutReportRuntimeReport):
        if report.restricted_sections:
            restrictions.extend(report.restricted_sections)
        if report.redacted_sections:
            restrictions.extend(f"REDACTED:{s}" for s in report.redacted_sections)
        caveats.extend(report.required_caveats)
    return restrictions, caveats


def _authorization_boundary(
    *,
    catalog_status: str | None,
    input_catalog_status: str | None,
    candidate_verdict: str,
) -> dict[str, Any]:
    return {
        **_AUTH_FALSE,
        "forbidden_verdicts_absent": candidate_verdict not in _FORBIDDEN_VERDICTS,
        "catalog_status_preserved": catalog_status == input_catalog_status,
        "promotion_review_collects_evidence_only": True,
        "eligible_verdict_is_not_production_approval": candidate_verdict != "PRODUCTION_APPROVED",
    }


def _deterministic_review_id(data: dict[str, Any], scope: str) -> str:
    payload = {
        "request_id": data.get("request_id"),
        "method_id": data.get("method_id"),
        "instrument_id": data.get("instrument_id"),
        "scope": scope,
        "catalog": _catalog_status(data),
        "evidence_ids": sorted(
            v for k, v in (
                ("method_suitability", _evidence_id("method_suitability_report", data)),
                ("statistical_promotion", _evidence_id("statistical_promotion_report", data)),
                ("trusted_readout", _evidence_id("trusted_readout_report", data)),
                ("claim_authorization", _evidence_id("claim_authorization_report", data)),
            ) if v
        ),
    }
    return f"mpr_{_hash_payload(payload)[:24]}"


def _evaluate_single(
    data: dict[str, Any],
    cfg: MethodPromotionReviewRuntimeConfig,
) -> MethodPromotionReviewRuntimeReport:
    request_id = str(data.get("request_id") or data.get("method_id") or "request_unspecified")
    scope = _scope_token(data)
    input_catalog = _catalog_status(data) or None
    catalog_status = input_catalog

    missing = _collect_missing_evidence(data, scope)
    failed_evidence: list[str] = []
    blockers: list[str] = []
    restrictions: list[str] = []
    caveats: list[str] = []
    warnings: list[str] = []
    sections: list[MethodPromotionReviewSection] = []
    failure_packet: dict[str, Any] | None = None

    evidence_summary: dict[str, Any] = {
        "scope": scope,
        "evidence_ids": {},
        "requirements_checked": list(_required_evidence_for_scope(scope)),
    }
    for key in (
        "method_suitability_report",
        "production_catalog_report",
        "statistical_promotion_report",
        "trusted_readout_report",
        "claim_authorization_report",
        "diagnostics_sensitivity_report",
        "srm_balance_diagnostic_report",
        "assignment_panel_integrity_report",
        "governed_randomization_report",
        "execution_result",
        "readout_plan_report",
        "lineage_manifest",
    ):
        eid = _evidence_id(key, data)
        if eid:
            evidence_summary["evidence_ids"][key] = eid

    review_status = "PROMOTION_REVIEW_NOT_EVALUATED"
    candidate_verdict = "NOT_REVIEWED"

    if missing:
        review_status = "PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE"
        candidate_verdict = "INSUFFICIENT_EVIDENCE"
        blockers.append(FAILURE_MISSING_REQUIRED_EVIDENCE)
        retry = "ADD_METHOD_SUITABILITY_REPORT"
        if "statistical_promotion_report" in missing:
            retry = "ADD_STATISTICAL_PROMOTION_REPORT"
        elif "trusted_readout_report_packet" in missing:
            retry = "ADD_TRUSTED_READOUT_REPORT"
        elif "assignment_panel_integrity_report" in missing:
            retry = "ADD_ASSIGNMENT_INTEGRITY_EVIDENCE"
        elif "srm_balance_diagnostic_report" in missing:
            retry = "ADD_SRM_BALANCE_DIAGNOSTIC"
        failure_packet = _build_failure_packet(
            failure_code=FAILURE_MISSING_REQUIRED_EVIDENCE,
            failure_reason="required promotion review evidence missing",
            missing_evidence=tuple(missing),
            failed_evidence=(),
            blockers=tuple(blockers),
            retry_category=retry,
        )
        sections.append(
            _build_section(
                section_type="EVIDENCE_INVENTORY",
                section_status="SECTION_BLOCKED",
                request_id=request_id,
                bound_evidence=(),
                blockers=(FAILURE_MISSING_REQUIRED_EVIDENCE,),
                missing_evidence=tuple(missing),
                trace={"missing_count": len(missing)},
            )
        )
    else:
        suitability_status = _method_suitability_status(data)
        catalog_gate_status = _catalog_status(data)
        stat_status = _report_status(data.get("statistical_promotion_report"))
        integrity_status = _report_status(data.get("assignment_panel_integrity_report"))
        srm_status = _report_status(data.get("srm_balance_diagnostic_report"))
        trusted_status = _trusted_readout_status(data)
        claim_status = _claim_authorization_status(data)

        sections.extend([
            _build_section(
                section_type="METHOD_SUITABILITY_GATE",
                section_status="SECTION_BLOCKED" if suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED.value else "SECTION_EVALUATED",
                request_id=request_id,
                bound_evidence=(_evidence_id("method_suitability_report", data),),
                blockers=(FAILURE_METHOD_SUITABILITY_BLOCKED,) if suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED.value else (),
                trace={"suitability_status": suitability_status},
            ),
            _build_section(
                section_type="PRODUCTION_CATALOG_GATE",
                section_status="SECTION_BLOCKED" if catalog_gate_status == PRODUCTION_CATALOG_BLOCKED else "SECTION_EVALUATED",
                request_id=request_id,
                bound_evidence=(_evidence_id("production_catalog_report", data) or f"catalog:{catalog_gate_status}",),
                blockers=(FAILURE_PRODUCTION_CATALOG_BLOCKED,) if catalog_gate_status == PRODUCTION_CATALOG_BLOCKED else (),
                trace={"catalog_status": catalog_gate_status},
            ),
            _build_section(
                section_type="STATISTICAL_PROMOTION_GATE",
                section_status="SECTION_BLOCKED" if stat_status in {STATISTICAL_PROMOTION_FAILED, STATISTICAL_PROMOTION_BLOCKED} else "SECTION_EVALUATED",
                request_id=request_id,
                bound_evidence=(_evidence_id("statistical_promotion_report", data),),
                blockers=(FAILURE_STATISTICAL_PROMOTION_BLOCKED,) if stat_status in {STATISTICAL_PROMOTION_FAILED, STATISTICAL_PROMOTION_BLOCKED} else (),
                trace={"promotion_status": stat_status},
            ),
            _build_section(
                section_type="ASSIGNMENT_INTEGRITY_GATE",
                section_status="SECTION_BLOCKED" if integrity_status in {ASSIGNMENT_PANEL_INTEGRITY_FAILED, ASSIGNMENT_PANEL_INTEGRITY_BLOCKED} else "SECTION_EVALUATED",
                request_id=request_id,
                bound_evidence=(_evidence_id("assignment_panel_integrity_report", data),),
                blockers=(FAILURE_ASSIGNMENT_INTEGRITY_BLOCKED,) if integrity_status in {ASSIGNMENT_PANEL_INTEGRITY_FAILED, ASSIGNMENT_PANEL_INTEGRITY_BLOCKED} else (),
                trace={"integrity_status": integrity_status},
            ),
            _build_section(
                section_type="SRM_BALANCE_GATE",
                section_status="SECTION_BLOCKED" if srm_status in {SRM_BALANCE_DIAGNOSTIC_FAILED, SRM_BALANCE_DIAGNOSTIC_BLOCKED} else "SECTION_EVALUATED",
                request_id=request_id,
                bound_evidence=(_evidence_id("srm_balance_diagnostic_report", data),),
                blockers=(FAILURE_SRM_BALANCE_BLOCKED,) if srm_status in {SRM_BALANCE_DIAGNOSTIC_FAILED, SRM_BALANCE_DIAGNOSTIC_BLOCKED} else (),
                trace={"srm_status": srm_status},
            ),
        ])

        if catalog_gate_status == PRODUCTION_CATALOG_BLOCKED:
            review_status = "PROMOTION_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG"
            candidate_verdict = "BLOCKED"
            blockers.append(FAILURE_PRODUCTION_CATALOG_BLOCKED)
            failed_evidence.append("production_catalog_report")
            failure_packet = _build_failure_packet(
                failure_code=FAILURE_PRODUCTION_CATALOG_BLOCKED,
                failure_reason="production catalog blocks promotion review",
                missing_evidence=(),
                failed_evidence=("production_catalog_report",),
                blockers=tuple(blockers),
                retry_category="FIX_PRODUCTION_CATALOG_BLOCKER",
            )
        elif suitability_status == MethodFamilySuitabilityStatus.METHOD_FAMILY_BLOCKED.value:
            review_status = "PROMOTION_REVIEW_BLOCKED_BY_METHOD_SUITABILITY"
            candidate_verdict = "BLOCKED"
            blockers.append(FAILURE_METHOD_SUITABILITY_BLOCKED)
            failed_evidence.append("method_suitability_report")
            failure_packet = _build_failure_packet(
                failure_code=FAILURE_METHOD_SUITABILITY_BLOCKED,
                failure_reason="method suitability blocks promotion review",
                missing_evidence=(),
                failed_evidence=("method_suitability_report",),
                blockers=tuple(blockers),
                retry_category="REQUEST_RESTRICTED_SCOPE",
            )
        elif stat_status in {STATISTICAL_PROMOTION_FAILED, STATISTICAL_PROMOTION_BLOCKED}:
            review_status = "PROMOTION_REVIEW_BLOCKED_BY_STATISTICAL_PROMOTION"
            candidate_verdict = "BLOCKED"
            blockers.append(FAILURE_STATISTICAL_PROMOTION_BLOCKED)
            failed_evidence.append("statistical_promotion_report")
            failure_packet = _build_failure_packet(
                failure_code=FAILURE_STATISTICAL_PROMOTION_BLOCKED,
                failure_reason="statistical promotion thresholds not met",
                missing_evidence=(),
                failed_evidence=("statistical_promotion_report",),
                blockers=tuple(blockers),
                retry_category="ADD_STATISTICAL_PROMOTION_REPORT",
            )
        elif integrity_status in {ASSIGNMENT_PANEL_INTEGRITY_FAILED, ASSIGNMENT_PANEL_INTEGRITY_BLOCKED}:
            review_status = "PROMOTION_REVIEW_BLOCKED_BY_ASSIGNMENT_INTEGRITY"
            candidate_verdict = "BLOCKED"
            blockers.append(FAILURE_ASSIGNMENT_INTEGRITY_BLOCKED)
            failed_evidence.append("assignment_panel_integrity_report")
            failure_packet = _build_failure_packet(
                failure_code=FAILURE_ASSIGNMENT_INTEGRITY_BLOCKED,
                failure_reason="assignment panel integrity blocks promotion review",
                missing_evidence=(),
                failed_evidence=("assignment_panel_integrity_report",),
                blockers=tuple(blockers),
                retry_category="ADD_ASSIGNMENT_INTEGRITY_EVIDENCE",
            )
        elif srm_status in {SRM_BALANCE_DIAGNOSTIC_FAILED, SRM_BALANCE_DIAGNOSTIC_BLOCKED}:
            review_status = "PROMOTION_REVIEW_BLOCKED_BY_SRM_BALANCE"
            candidate_verdict = "BLOCKED"
            blockers.append(FAILURE_SRM_BALANCE_BLOCKED)
            failed_evidence.append("srm_balance_diagnostic_report")
            failure_packet = _build_failure_packet(
                failure_code=FAILURE_SRM_BALANCE_BLOCKED,
                failure_reason="SRM/balance diagnostic blocks promotion review",
                missing_evidence=(),
                failed_evidence=("srm_balance_diagnostic_report",),
                blockers=tuple(blockers),
                retry_category="ADD_SRM_BALANCE_DIAGNOSTIC",
            )
        elif trusted_status.startswith("TRUSTED_REPORT_BLOCKED"):
            review_status = "PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE"
            candidate_verdict = "BLOCKED"
            blockers.append(FAILURE_TRUSTED_READOUT_BLOCKED)
            failed_evidence.append("trusted_readout_report")
            failure_packet = _build_failure_packet(
                failure_code=FAILURE_TRUSTED_READOUT_BLOCKED,
                failure_reason="trusted readout report blocked",
                missing_evidence=(),
                failed_evidence=("trusted_readout_report",),
                blockers=tuple(blockers),
                retry_category="ADD_TRUSTED_READOUT_REPORT",
            )
        elif claim_status == CLAIM_AUTHORIZATION_BLOCKED:
            review_status = "PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE"
            candidate_verdict = "BLOCKED"
            blockers.append(FAILURE_CLAIM_AUTHORIZATION_BLOCKED)
            failed_evidence.append("claim_authorization_report")
            failure_packet = _build_failure_packet(
                failure_code=FAILURE_CLAIM_AUTHORIZATION_BLOCKED,
                failure_reason="claim authorization blocks promotion review surfaces",
                missing_evidence=(),
                failed_evidence=("claim_authorization_report",),
                blockers=tuple(blockers),
                retry_category="BLOCK_METHOD_PROMOTION_REVIEW",
            )
        else:
            tr_restrictions, tr_caveats = _restrictions_and_caveats_from_trusted_readout(data)
            eligibility_restrictions: list[str] = []
            if cfg.propagate_trusted_readout_restrictions:
                eligibility_restrictions.extend(tr_restrictions)
                caveats.extend(tr_caveats)
                restrictions.extend(tr_restrictions)
            if trusted_status == TRUSTED_REPORT_READY_WITH_REDACTIONS:
                warnings.append("trusted readout report contains redactions")
            if suitability_status in {
                MethodFamilySuitabilityStatus.METHOD_FAMILY_RESTRICTED.value,
                MethodFamilySuitabilityStatus.METHOD_FAMILY_DIAGNOSTIC_ONLY.value,
            }:
                eligibility_restrictions.append(f"METHOD_SUITABILITY:{suitability_status}")
                restrictions.append(f"METHOD_SUITABILITY:{suitability_status}")
            limitations = data.get("known_limitations") or []
            if isinstance(limitations, (list, tuple)):
                for item in limitations:
                    restrictions.append(str(item))

            has_eligibility_restrictions = bool(eligibility_restrictions or caveats)
            if scope == "RESTRICTED_USE_REVIEW":
                if has_eligibility_restrictions:
                    review_status = "PROMOTION_REVIEW_READY_WITH_RESTRICTIONS"
                    candidate_verdict = "REVIEW_REQUIRED"
                else:
                    review_status = "PROMOTION_REVIEW_READY"
                    candidate_verdict = "ELIGIBLE_FOR_RESTRICTED_USE_REVIEW"
            else:
                if cfg.require_human_governance_for_production_scope:
                    review_status = (
                        "PROMOTION_REVIEW_READY_WITH_RESTRICTIONS"
                        if has_eligibility_restrictions
                        else "PROMOTION_REVIEW_REQUIRES_HUMAN_GOVERNANCE"
                    )
                    candidate_verdict = (
                        "REVIEW_REQUIRED" if has_eligibility_restrictions else "ELIGIBLE_FOR_PRODUCTION_REVIEW"
                    )
                    if not has_eligibility_restrictions:
                        warnings.append("production scope review eligibility requires human governance")
                else:
                    review_status = (
                        "PROMOTION_REVIEW_READY_WITH_RESTRICTIONS"
                        if has_eligibility_restrictions
                        else "PROMOTION_REVIEW_READY"
                    )
                    candidate_verdict = "ELIGIBLE_FOR_PRODUCTION_REVIEW"

            sections.append(
                _build_section(
                    section_type="PROMOTION_ELIGIBILITY_SUMMARY",
                    section_status="SECTION_ALLOWED_WITH_RESTRICTIONS" if has_eligibility_restrictions else "SECTION_ALLOWED",
                    request_id=request_id,
                    bound_evidence=tuple(evidence_summary["evidence_ids"].values()),
                    restrictions=tuple(restrictions),
                    caveats=tuple(caveats),
                    trace={"scope": scope, "candidate_verdict": candidate_verdict},
                )
            )

    prohibited = _safe_str_list(list(PROHIBITED_SURFACES) + _prohibited_from_claims(data))
    eligible = _safe_str_list(list(_ELIGIBLE_SURFACES))
    lineage = dict(_to_dict(data.get("lineage_manifest")) or {})
    lineage.setdefault("review_artifact_id", _ARTIFACT_ID)
    lineage.setdefault("policy_version", _POLICY_VERSION)

    review_id = _deterministic_review_id(data, scope)
    provenance_payload = {
        "artifact_id": _ARTIFACT_ID,
        "request_id": request_id,
        "review_id": review_id,
        "scope": scope,
        "review_status": review_status,
        "candidate_verdict": candidate_verdict,
        "catalog_status": catalog_status,
        "evidence_summary": evidence_summary,
        "blockers": list(blockers),
        "policy_version": _POLICY_VERSION,
    }
    provenance_hash = _hash_payload(provenance_payload)

    return MethodPromotionReviewRuntimeReport(
        request_id=request_id,
        review_id=review_id,
        review_status=review_status,
        candidate_verdict=candidate_verdict,
        method_id=data.get("method_id"),
        instrument_id=data.get("instrument_id"),
        estimator_family=data.get("estimator_family"),
        inference_family=data.get("inference_family"),
        current_catalog_status=catalog_status,
        requested_promotion_scope=scope,
        evidence_bundle_summary=evidence_summary,
        missing_evidence=tuple(missing),
        failed_evidence=tuple(failed_evidence),
        blockers=tuple(blockers),
        restrictions=tuple(restrictions),
        required_caveats=tuple(caveats),
        eligible_surfaces=eligible,
        prohibited_surfaces=prohibited,
        review_sections=tuple(sections),
        lineage_manifest=lineage,
        provenance_hash=provenance_hash,
        policy_version=_POLICY_VERSION,
        failure_packet=failure_packet,
        warnings=tuple(warnings),
        authorization_boundary_report=_authorization_boundary(
            catalog_status=catalog_status,
            input_catalog_status=input_catalog,
            candidate_verdict=candidate_verdict,
        ),
    )


def generate_method_promotion_review(
    input_data: Any,
    config: MethodPromotionReviewRuntimeConfig | dict[str, Any] | None = None,
) -> MethodPromotionReviewRuntimeReport | list[MethodPromotionReviewRuntimeReport]:
    cfg = _resolve_config(config)
    if isinstance(input_data, list):
        return [_evaluate_single(_to_dict(x), cfg) for x in input_data]
    data = _to_dict(input_data)
    if "requests" in data and isinstance(data["requests"], list):
        return [_evaluate_single(_to_dict(x), cfg) for x in data["requests"]]
    return _evaluate_single(data, cfg)


build_method_promotion_review = generate_method_promotion_review
create_method_promotion_review_packet = generate_method_promotion_review


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def run_validation(*, write_summary: bool = True) -> dict[str, Any]:
    from panel_exp.validation.assignment_panel_integrity_runtime_001 import ASSIGNMENT_PANEL_INTEGRITY_PASSED
    from panel_exp.validation.srm_balance_readout_diagnostic_001 import SRM_BALANCE_DIAGNOSTIC_PASSED
    from panel_exp.validation.statistical_promotion_thresholds_001 import STATISTICAL_PROMOTION_PASSED

    base = {
        "request_id": "validation_001",
        "method_id": "DID_2X2",
        "instrument_id": "DID_2X2_POINT_ESTIMATE",
        "estimator_family": "DID",
        "inference_family": "POINT_ESTIMATE",
        "current_catalog_status": "PRODUCTION_CATALOG_RESEARCH_ONLY",
        "requested_promotion_scope": "RESTRICTED_USE_REVIEW",
        "method_suitability_report": {"suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW"},
        "statistical_promotion_report": {"status": STATISTICAL_PROMOTION_PASSED},
        "trusted_readout_report": {"report_status": "TRUSTED_REPORT_READY"},
        "claim_authorization_report": {"overall_status": "CLAIM_AUTHORIZATION_COMPLETED"},
        "known_limitations": ["point_estimate_only"],
    }
    report = generate_method_promotion_review(base)
    assert isinstance(report, MethodPromotionReviewRuntimeReport)
    blocked = generate_method_promotion_review({"request_id": "missing"})
    assert isinstance(blocked, MethodPromotionReviewRuntimeReport)
    assert blocked.candidate_verdict == "INSUFFICIENT_EVIDENCE"

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "method_promotion_review_runtime",
        "base_commit": _git_head(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": [
            "METHOD_PROMOTION_REVIEW_CONTRACT_001",
            "TRUSTED_READOUT_REPORT_RUNTIME_001",
            "CLAIM_AUTHORIZATION_RUNTIME_001",
            "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001",
            "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001",
            "SRM_BALANCE_READOUT_DIAGNOSTIC_001",
            "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001",
        ],
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "failed_scenarios": [],
        "final_verdict": _VERDICT,
        **_POSITIVE_FLAGS,
        **_AUTH_FALSE,
    }
    if write_summary:
        _DEFAULT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
        _DEFAULT_SUMMARY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"verdict": _VERDICT, "failed_scenarios": [], "validation": {"valid": True}}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
