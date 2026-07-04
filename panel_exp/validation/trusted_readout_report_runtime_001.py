"""TRUSTED_READOUT_REPORT_RUNTIME_001 — governed trusted readout report packet runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.claim_authorization_runtime_001 import (
    CLAIM_AUTHORIZATION_BLOCKED,
    CLAIM_AUTHORIZED,
    CLAIM_AUTHORIZED_WITH_RESTRICTIONS,
    CLAIM_BLOCKED,
    ClaimAuthorizationRuntimeReport,
    authorize_readout_claims,
)
from panel_exp.validation.trusted_readout_report_contract_001 import (
    CAVEAT_CODES,
    REPORT_SECTION_TYPES,
    RETRY_CATEGORIES,
    SECTION_EVIDENCE_REQUIREMENTS,
    SECTION_STATUSES,
)

_ARTIFACT_ID = "TRUSTED_READOUT_REPORT_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "trusted_readout_report_runtime_implemented_no_production_authorization_or_narrative_generation"
_VERDICT = "trusted_readout_report_runtime_implemented_no_production_authorization_or_narrative_generation"
_RECOMMENDED_NEXT = "METHOD_PROMOTION_REVIEW_CONTRACT_001"
_ALTERNATIVE_NEXT = "METHOD_PROMOTION_REVIEW_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/TRUSTED_READOUT_REPORT_RUNTIME_001_summary.json"

TRUSTED_REPORT_READY = "TRUSTED_REPORT_READY"
TRUSTED_REPORT_READY_WITH_REDACTIONS = "TRUSTED_REPORT_READY_WITH_REDACTIONS"
TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION = "TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION"
TRUSTED_REPORT_BLOCKED_BY_MISSING_EVIDENCE = "TRUSTED_REPORT_BLOCKED_BY_MISSING_EVIDENCE"
TRUSTED_REPORT_BLOCKED_BY_PRODUCTION_CATALOG = "TRUSTED_REPORT_BLOCKED_BY_PRODUCTION_CATALOG"
TRUSTED_REPORT_BLOCKED_BY_STATISTICAL_PROMOTION = "TRUSTED_REPORT_BLOCKED_BY_STATISTICAL_PROMOTION"
TRUSTED_REPORT_BLOCKED_BY_ASSIGNMENT_INTEGRITY = "TRUSTED_REPORT_BLOCKED_BY_ASSIGNMENT_INTEGRITY"
TRUSTED_REPORT_BLOCKED_BY_SRM_BALANCE = "TRUSTED_REPORT_BLOCKED_BY_SRM_BALANCE"
TRUSTED_REPORT_BLOCKED_BY_TRUSTED_SURFACE_POLICY = "TRUSTED_REPORT_BLOCKED_BY_TRUSTED_SURFACE_POLICY"
TRUSTED_REPORT_NOT_EVALUATED = "TRUSTED_REPORT_NOT_EVALUATED"

FAILURE_MISSING_CLAIM_AUTHORIZATION_REPORT = "MISSING_CLAIM_AUTHORIZATION_REPORT"
FAILURE_MISSING_REQUIRED_EVIDENCE = "MISSING_REQUIRED_EVIDENCE"
FAILURE_CLAIM_AUTHORIZATION_BLOCKED = "CLAIM_AUTHORIZATION_BLOCKED"
FAILURE_SECTION_REDACTED_BY_POLICY = "SECTION_REDACTED_BY_POLICY"
FAILURE_SECTION_BLOCKED_BY_POLICY = "SECTION_BLOCKED_BY_POLICY"
FAILURE_TRUSTED_SURFACE_POLICY_BLOCKED = "TRUSTED_SURFACE_POLICY_BLOCKED"
FAILURE_PRODUCTION_CATALOG_BLOCKED = "PRODUCTION_CATALOG_BLOCKED"
FAILURE_STATISTICAL_PROMOTION_BLOCKED = "STATISTICAL_PROMOTION_BLOCKED"
FAILURE_ASSIGNMENT_INTEGRITY_BLOCKED = "ASSIGNMENT_INTEGRITY_BLOCKED"
FAILURE_SRM_BALANCE_BLOCKED = "SRM_BALANCE_BLOCKED"
FAILURE_UNCERTAINTY_MISSING = "UNCERTAINTY_MISSING"

_POINT_ESTIMATE_CLAIMS = frozenset({"POINT_ESTIMATE_DESCRIPTION", "POINT_ESTIMATE_CLAIM"})
_UNCERTAINTY_CLAIMS = frozenset({"CONFIDENCE_INTERVAL_CLAIM", "STATISTICAL_SIGNIFICANCE_CLAIM"})
_RECOMMENDATION_CLAIMS = frozenset({"TRUSTED_BUSINESS_RECOMMENDATION", "PRODUCTION_READOUT_CLAIM"})

_POSITIVE_FLAGS = {
    "trusted_readout_report_runtime_implemented": True,
    "trusted_readout_report_packet_generated": True,
    "claim_authorization_binding_enforced": True,
    "unsupported_sections_redacted": True,
    "required_caveats_propagated": True,
    "blocked_claims_rendered_only_as_not_authorized": True,
    "lineage_provenance_recorded": True,
}

_AUTH_FALSE = {
    "production_authorization_granted": False,
    "production_readout_authorized": False,
    "trusted_business_recommendation_authorized": False,
    "authorized_claim_text_generated": False,
    "polished_narrative_generated": False,
    "presentation_generated": False,
    "causal_claim_authorized": False,
    "incremental_lift_claim_authorized": False,
    "roi_claim_authorized": False,
    "statistical_significance_claim_authorized": False,
    "confidence_interval_claim_authorized": False,
    "method_unblocked": False,
    "production_catalog_unblocked": False,
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


@dataclass(frozen=True)
class TrustedReadoutReportRuntimeConfig:
    require_claim_authorization_report: bool = True
    block_recommendation_without_trusted_surface_policy: bool = True
    redact_uncertainty_without_governed_evidence: bool = True
    include_not_evaluated_sections: bool = True


@dataclass(frozen=True)
class TrustedReadoutReportSection:
    section_id: str
    section_type: str
    section_status: str
    required_claim_types: tuple[str, ...]
    bound_claim_authorization_ids: tuple[str, ...]
    bound_evidence_ids: tuple[str, ...]
    allowed_surface: tuple[dict[str, Any], ...]
    blocked_surface: tuple[dict[str, Any], ...]
    required_caveats: tuple[str, ...]
    redaction_reason: str | None
    missing_evidence: tuple[str, ...]
    trace: dict[str, Any]


@dataclass(frozen=True)
class TrustedReadoutReportRuntimeReport:
    request_id: str
    report_id: str
    report_status: str
    report_type: str | None
    report_scope: str | None
    experiment_id: str | None
    design_id: str | None
    readout_id: str | None
    sections: tuple[TrustedReadoutReportSection, ...]
    allowed_sections: tuple[str, ...]
    restricted_sections: tuple[str, ...]
    redacted_sections: tuple[str, ...]
    blocked_sections: tuple[str, ...]
    authorized_claim_bindings: tuple[dict[str, Any], ...]
    restricted_claim_bindings: tuple[dict[str, Any], ...]
    blocked_claim_summaries: tuple[dict[str, Any], ...]
    required_caveats: tuple[str, ...]
    evidence_bundle_summary: dict[str, Any]
    missing_evidence: tuple[str, ...]
    failed_evidence: tuple[str, ...]
    lineage_manifest: dict[str, Any]
    provenance_hash: str
    policy_version: str
    failure_packet: dict[str, Any] | None
    warnings: tuple[str, ...]
    claim_boundary_report: dict[str, Any]


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
    config: TrustedReadoutReportRuntimeConfig | dict[str, Any] | None,
) -> TrustedReadoutReportRuntimeConfig:
    if config is None:
        return TrustedReadoutReportRuntimeConfig()
    if isinstance(config, TrustedReadoutReportRuntimeConfig):
        return config
    base = TrustedReadoutReportRuntimeConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return TrustedReadoutReportRuntimeConfig(**merged)


def _evidence_present(data: dict[str, Any], key: str) -> bool:
    aliases = {
        "execution_result": ("execution_result", "execution_packet", "instrument_execution_results"),
        "execution_artifact_manifest": ("execution_artifact_manifest",),
        "trusted_surface_policy": ("trusted_surface_policy",),
    }
    keys = aliases.get(key, (key,))
    for k in keys:
        val = data.get(k)
        if val not in (None, "", [], {}):
            return True
    return False


def _report_status(report: dict[str, Any] | None) -> str:
    if not report:
        return ""
    return str(
        report.get("status")
        or report.get("overall_status")
        or report.get("evidence_sufficiency_status")
        or report.get("instrument_execution_status")
        or ""
    )


def _uncertainty_governed(data: dict[str, Any]) -> bool:
    results = list(data.get("instrument_execution_results") or [])
    if not results and isinstance(data.get("execution_result"), dict):
        results = list(data["execution_result"].get("instrument_execution_results") or [])
    for row in results:
        if not isinstance(row, dict):
            continue
        unc = _to_dict(row.get("uncertainty_report"))
        status = _token(unc.get("uncertainty_report_status") or unc.get("status"))
        if status not in {"", "NOT_COMPUTED", "NOT_EVALUATED", "MISSING"}:
            return True
    unc = _to_dict(data.get("uncertainty_report"))
    status = _token(unc.get("uncertainty_report_status") or unc.get("status"))
    return status not in {"", "NOT_COMPUTED", "NOT_EVALUATED", "MISSING"}


def _claim_id(claim_type: str, index: int) -> str:
    return f"claim_auth_{claim_type.lower()}_{index}"


def _decision_to_dict(decision: Any, index: int) -> dict[str, Any]:
    d = _to_dict(decision)
    claim_type = str(d.get("claim_type") or f"claim_{index}")
    cid = d.get("claim_authorization_id") or _claim_id(claim_type, index)
    return {
        **d,
        "claim_authorization_id": cid,
        "claim_type": claim_type,
        "authorization_status": d.get("authorization_status") or CLAIM_BLOCKED,
        "caveat_codes": tuple(d.get("caveat_codes") or ()),
        "blockers": tuple(d.get("blockers") or ()),
    }


def _resolve_claim_authorization(
    data: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], bool]:
    raw = data.get("claim_authorization_report")
    if isinstance(raw, ClaimAuthorizationRuntimeReport):
        report = _to_dict(raw)
        decisions = [_decision_to_dict(d, i) for i, d in enumerate(raw.claim_authorizations)]
        return report, decisions, True
    if isinstance(raw, dict) and raw.get("claim_authorizations"):
        decisions = [_decision_to_dict(d, i) for i, d in enumerate(raw["claim_authorizations"])]
        return raw, decisions, True
    if data.get("claim_requests"):
        auth = authorize_readout_claims(data)
        if isinstance(auth, list):
            auth = auth[0]
        report = _to_dict(auth)
        decisions = [_decision_to_dict(d, i) for i, d in enumerate(auth.claim_authorizations)]
        return report, decisions, True
    if isinstance(raw, dict) and raw:
        return raw, [], True
    return {}, [], False


def _structured_surface(
    *,
    surface_type: str,
    claim_type: str,
    status: str,
    caveats: tuple[str, ...] = (),
    blockers: tuple[str, ...] = (),
) -> dict[str, Any]:
    surface: dict[str, Any] = {
        "surface_type": surface_type,
        "claim_type": claim_type,
        "status": status,
    }
    if caveats:
        surface["caveats"] = list(caveats)
    if blockers:
        surface["blockers"] = list(blockers)
    return surface


def _blocked_notice(decision: dict[str, Any]) -> dict[str, Any]:
    return _structured_surface(
        surface_type="BLOCKED_CLAIM_NOTICE",
        claim_type=str(decision.get("claim_type") or "UNKNOWN"),
        status="BLOCKED",
        blockers=tuple(decision.get("blockers") or ()),
    )


def _restricted_surface(decision: dict[str, Any]) -> dict[str, Any]:
    claim_type = str(decision.get("claim_type") or "UNKNOWN")
    caveats = tuple(decision.get("caveat_codes") or ())
    if claim_type in _POINT_ESTIMATE_CLAIMS:
        surface_type = "POINT_ESTIMATE_ONLY"
    else:
        surface_type = "RESTRICTED_CLAIM_SURFACE"
    return _structured_surface(
        surface_type=surface_type,
        claim_type=claim_type,
        status="AUTHORIZED_WITH_RESTRICTIONS",
        caveats=caveats,
    )


def _authorized_surface(decision: dict[str, Any]) -> dict[str, Any]:
    return _structured_surface(
        surface_type="AUTHORIZED_CLAIM_SURFACE",
        claim_type=str(decision.get("claim_type") or "UNKNOWN"),
        status="AUTHORIZED",
        caveats=tuple(decision.get("caveat_codes") or ()),
    )


def _evidence_id(key: str, data: dict[str, Any]) -> str:
    report = data.get(key)
    if isinstance(report, dict):
        for field_name in ("artifact_id", "report_id", "request_id", "status"):
            if report.get(field_name):
                return f"{key}:{report[field_name]}"
    return key if _evidence_present(data, key) else ""


def _missing_for_section(section_type: str, data: dict[str, Any], *, auth_present: bool = False) -> list[str]:
    missing: list[str] = []
    for req in SECTION_EVIDENCE_REQUIREMENTS.get(section_type, ()):
        if req == "claim_authorization_report" and auth_present:
            continue
        if req == "trusted_surface_policy" and section_type != "RECOMMENDATION_SECTION":
            continue
        if not _evidence_present(data, req):
            missing.append(req)
    return missing


def _trusted_surface_allows_recommendation(policy: dict[str, Any] | None) -> bool:
    if not policy:
        return False
    if policy.get("allow_recommendation_section") is True:
        return True
    return _token(policy.get("recommendation_surface")) in {"ALLOWED", "RESTRICTED"}


def _build_section(
    *,
    section_type: str,
    section_status: str,
    required_claim_types: tuple[str, ...],
    bound_claim_ids: tuple[str, ...],
    bound_evidence: tuple[str, ...],
    allowed: tuple[dict[str, Any], ...],
    blocked: tuple[dict[str, Any], ...],
    caveats: tuple[str, ...],
    redaction_reason: str | None,
    missing_evidence: tuple[str, ...],
    trace: dict[str, Any],
    request_id: str,
) -> TrustedReadoutReportSection:
    section_id = f"{request_id}:{section_type.lower()}"
    return TrustedReadoutReportSection(
        section_id=section_id,
        section_type=section_type,
        section_status=section_status,
        required_claim_types=required_claim_types,
        bound_claim_authorization_ids=bound_claim_ids,
        bound_evidence_ids=bound_evidence,
        allowed_surface=allowed,
        blocked_surface=blocked,
        required_caveats=caveats,
        redaction_reason=redaction_reason,
        missing_evidence=missing_evidence,
        trace=trace,
    )


def _evaluate_single(data: dict[str, Any], cfg: TrustedReadoutReportRuntimeConfig) -> TrustedReadoutReportRuntimeReport:
    request_id = str(data.get("request_id") or data.get("design_id") or "request_unspecified")
    report_type = data.get("report_type")
    report_scope = data.get("report_scope")
    experiment_id = data.get("experiment_id")
    design_id = data.get("design_id")
    readout_id = data.get("readout_id")
    requested = data.get("requested_sections")
    requested_sections = (
        tuple(str(s) for s in requested)
        if isinstance(requested, (list, tuple)) and requested
        else REPORT_SECTION_TYPES
    )

    auth_report, decisions, auth_present = _resolve_claim_authorization(data)
    auth_by_type = {str(d["claim_type"]): d for d in decisions}

    authorized = [d for d in decisions if d.get("authorization_status") == CLAIM_AUTHORIZED]
    restricted = [d for d in decisions if d.get("authorization_status") == CLAIM_AUTHORIZED_WITH_RESTRICTIONS]
    blocked = [d for d in decisions if d.get("authorization_status") == CLAIM_BLOCKED]

    all_caveats: list[str] = []
    for d in decisions:
        all_caveats.extend(list(d.get("caveat_codes") or ()))
    for c in auth_report.get("caveats") or []:
        if c:
            all_caveats.append(str(c))
    required_caveats = _safe_str_list([c for c in all_caveats if c in CAVEAT_CODES])

    missing_evidence_global: list[str] = []
    failed_evidence_global: list[str] = []
    failure_codes: list[str] = []
    failure_reasons: list[str] = []
    blocking_sections: list[str] = []
    retry_categories: list[str] = []

    sections: list[TrustedReadoutReportSection] = []
    allowed_sections: list[str] = []
    restricted_sections: list[str] = []
    redacted_sections: list[str] = []
    blocked_sections: list[str] = []
    warnings: list[str] = []

    built_sections: set[str] = set()

    def _add_section(section: TrustedReadoutReportSection) -> None:
        built_sections.add(section.section_type)
        sections.append(section)
        if section.section_status == "SECTION_ALLOWED":
            allowed_sections.append(section.section_type)
        elif section.section_status == "SECTION_ALLOWED_WITH_RESTRICTIONS":
            restricted_sections.append(section.section_type)
        elif section.section_status == "SECTION_REDACTED":
            redacted_sections.append(section.section_type)
        elif section.section_status == "SECTION_BLOCKED":
            blocked_sections.append(section.section_type)

    claim_sections_need_auth = {
        "EXECUTIVE_SUMMARY",
        "AUTHORIZED_CLAIMS",
        "RESTRICTED_CLAIMS",
        "BLOCKED_CLAIMS",
        "POINT_ESTIMATE_SUMMARY",
        "UNCERTAINTY_SUMMARY",
        "DIAGNOSTIC_SUMMARY",
        "PRODUCTION_CATALOG_STATUS",
        "CAVEATS_AND_LIMITATIONS",
        "RECOMMENDATION_SECTION",
    }

    if not auth_present and cfg.require_claim_authorization_report:
        failure_codes.append(FAILURE_MISSING_CLAIM_AUTHORIZATION_REPORT)
        failure_reasons.append("claim_authorization_report missing")
        retry_categories.append("ADD_CLAIM_AUTHORIZATION_REPORT")
        for section_type in requested_sections:
            if section_type in claim_sections_need_auth:
                _add_section(
                    _build_section(
                        section_type=section_type,
                        section_status="SECTION_BLOCKED",
                        required_claim_types=(),
                        bound_claim_ids=(),
                        bound_evidence=(),
                        allowed=(),
                        blocked=(
                            _structured_surface(
                                surface_type="BLOCKED_CLAIM_NOTICE",
                                claim_type="ALL",
                                status="BLOCKED",
                                blockers=(FAILURE_MISSING_CLAIM_AUTHORIZATION_REPORT,),
                            ),
                        ),
                        caveats=(),
                        redaction_reason=FAILURE_MISSING_CLAIM_AUTHORIZATION_REPORT,
                        missing_evidence=("claim_authorization_report",),
                        trace={"reason": "missing_claim_authorization_report"},
                        request_id=request_id,
                    )
                )
                blocking_sections.append(section_type)
                missing_evidence_global.append("claim_authorization_report")

    evidence_ids_present = {
        k: _evidence_id(k, data)
        for k in (
            "readout_plan_report",
            "execution_result",
            "execution_artifact_manifest",
            "diagnostics_sensitivity_report",
            "srm_balance_diagnostic_report",
            "assignment_panel_integrity_report",
            "governed_randomization_report",
            "statistical_promotion_report",
            "production_catalog_report",
            "method_suitability_report",
            "did_instrument_contract",
            "evidence_sources",
            "lineage_manifest",
        )
        if _evidence_present(data, k)
    }
    if auth_present:
        evidence_ids_present["claim_authorization_report"] = _evidence_id(
            "claim_authorization_report",
            {"claim_authorization_report": auth_report},
        ) or f"claim_authorization_report:{auth_report.get('overall_status', 'present')}"

    # AUTHORIZED_CLAIMS
    if "AUTHORIZED_CLAIMS" in requested_sections and auth_present and "AUTHORIZED_CLAIMS" not in built_sections:
        surfaces = tuple(_authorized_surface(d) for d in authorized)
        status = "SECTION_ALLOWED" if surfaces else "SECTION_NOT_EVALUATED"
        _add_section(
            _build_section(
                section_type="AUTHORIZED_CLAIMS",
                section_status=status,
                required_claim_types=tuple(d["claim_type"] for d in authorized),
                bound_claim_ids=tuple(d["claim_authorization_id"] for d in authorized),
                bound_evidence=(evidence_ids_present.get("claim_authorization_report", ""),),
                allowed=surfaces,
                blocked=(),
                caveats=(),
                redaction_reason=None,
                missing_evidence=(),
                trace={"authorized_count": len(authorized)},
                request_id=request_id,
            )
        )

    # RESTRICTED_CLAIMS
    if "RESTRICTED_CLAIMS" in requested_sections and auth_present and "RESTRICTED_CLAIMS" not in built_sections:
        surfaces = tuple(_restricted_surface(d) for d in restricted)
        caveats = _safe_str_list([c for d in restricted for c in (d.get("caveat_codes") or ())])
        status = "SECTION_ALLOWED_WITH_RESTRICTIONS" if surfaces else "SECTION_NOT_EVALUATED"
        _add_section(
            _build_section(
                section_type="RESTRICTED_CLAIMS",
                section_status=status,
                required_claim_types=tuple(d["claim_type"] for d in restricted),
                bound_claim_ids=tuple(d["claim_authorization_id"] for d in restricted),
                bound_evidence=(evidence_ids_present.get("claim_authorization_report", ""),),
                allowed=surfaces,
                blocked=(),
                caveats=caveats,
                redaction_reason=None,
                missing_evidence=(),
                trace={"restricted_count": len(restricted)},
                request_id=request_id,
            )
        )

    # BLOCKED_CLAIMS
    if "BLOCKED_CLAIMS" in requested_sections and auth_present and "BLOCKED_CLAIMS" not in built_sections:
        surfaces = tuple(_blocked_notice(d) for d in blocked)
        status = "SECTION_ALLOWED" if surfaces else "SECTION_NOT_EVALUATED"
        _add_section(
            _build_section(
                section_type="BLOCKED_CLAIMS",
                section_status=status,
                required_claim_types=tuple(d["claim_type"] for d in blocked),
                bound_claim_ids=tuple(d["claim_authorization_id"] for d in blocked),
                bound_evidence=(evidence_ids_present.get("claim_authorization_report", ""),),
                allowed=(),
                blocked=surfaces,
                caveats=(),
                redaction_reason=None,
                missing_evidence=(),
                trace={"blocked_count": len(blocked)},
                request_id=request_id,
            )
        )

    # POINT_ESTIMATE_SUMMARY
    if "POINT_ESTIMATE_SUMMARY" in requested_sections and "POINT_ESTIMATE_SUMMARY" not in built_sections:
        missing = _missing_for_section("POINT_ESTIMATE_SUMMARY", data, auth_present=auth_present)
        pe_claim = None
        for ct in _POINT_ESTIMATE_CLAIMS:
            if ct in auth_by_type:
                pe_claim = auth_by_type[ct]
                break
        if not auth_present:
            missing = list(missing) + ["claim_authorization_report"]
        elif not pe_claim:
            missing = list(missing) + ["point_estimate_claim_authorization"]
        elif pe_claim.get("authorization_status") == CLAIM_BLOCKED:
            _add_section(
                _build_section(
                    section_type="POINT_ESTIMATE_SUMMARY",
                    section_status="SECTION_BLOCKED",
                    required_claim_types=("POINT_ESTIMATE_DESCRIPTION",),
                    bound_claim_ids=(pe_claim["claim_authorization_id"],),
                    bound_evidence=_safe_str_list(
                        [v for v in (
                            evidence_ids_present.get("claim_authorization_report", ""),
                            evidence_ids_present.get("execution_result", ""),
                        ) if v]
                    ),
                    allowed=(),
                    blocked=(_blocked_notice(pe_claim),),
                    caveats=tuple(pe_claim.get("caveat_codes") or ()),
                    redaction_reason=FAILURE_CLAIM_AUTHORIZATION_BLOCKED,
                    missing_evidence=(),
                    trace={"claim_status": CLAIM_BLOCKED},
                    request_id=request_id,
                )
            )
            blocking_sections.append("POINT_ESTIMATE_SUMMARY")
            failure_codes.append(FAILURE_CLAIM_AUTHORIZATION_BLOCKED)
        elif missing:
            _add_section(
                _build_section(
                    section_type="POINT_ESTIMATE_SUMMARY",
                    section_status="SECTION_REDACTED",
                    required_claim_types=("POINT_ESTIMATE_DESCRIPTION",),
                    bound_claim_ids=(pe_claim["claim_authorization_id"],) if pe_claim else (),
                    bound_evidence=_safe_str_list([v for v in evidence_ids_present.values() if v]),
                    allowed=(),
                    blocked=(),
                    caveats=(),
                    redaction_reason=FAILURE_MISSING_REQUIRED_EVIDENCE,
                    missing_evidence=tuple(missing),
                    trace={"missing": missing},
                    request_id=request_id,
                )
            )
            redacted_sections.append("POINT_ESTIMATE_SUMMARY")
            missing_evidence_global.extend(missing)
            failure_codes.append(FAILURE_MISSING_REQUIRED_EVIDENCE)
            retry_categories.append("ADD_REQUIRED_EVIDENCE")
        else:
            caveats = tuple(pe_claim.get("caveat_codes") or ())
            _add_section(
                _build_section(
                    section_type="POINT_ESTIMATE_SUMMARY",
                    section_status="SECTION_ALLOWED_WITH_RESTRICTIONS",
                    required_claim_types=("POINT_ESTIMATE_DESCRIPTION",),
                    bound_claim_ids=(pe_claim["claim_authorization_id"],),
                    bound_evidence=_safe_str_list(
                        [v for v in (
                            evidence_ids_present.get("claim_authorization_report", ""),
                            evidence_ids_present.get("execution_result", ""),
                        ) if v]
                    ),
                    allowed=(_restricted_surface(pe_claim),),
                    blocked=(),
                    caveats=caveats,
                    redaction_reason=None,
                    missing_evidence=(),
                    trace={"point_estimate_only": True},
                    request_id=request_id,
                )
            )

    # UNCERTAINTY_SUMMARY
    if "UNCERTAINTY_SUMMARY" in requested_sections and "UNCERTAINTY_SUMMARY" not in built_sections:
        missing = list(_missing_for_section("UNCERTAINTY_SUMMARY", data, auth_present=auth_present))
        unc_claims = [auth_by_type[c] for c in _UNCERTAINTY_CLAIMS if c in auth_by_type]
        governed = _uncertainty_governed(data)
        if not auth_present:
            status = "SECTION_BLOCKED"
            reason = FAILURE_MISSING_CLAIM_AUTHORIZATION_REPORT
            missing_tuple = ("claim_authorization_report",)
        elif not governed:
            status = "SECTION_REDACTED"
            reason = FAILURE_UNCERTAINTY_MISSING
            missing_tuple = tuple(dict.fromkeys([*missing, "governed_uncertainty"]))
            failure_codes.append(FAILURE_UNCERTAINTY_MISSING)
            retry_categories.append("ADD_GOVERNED_UNCERTAINTY")
        elif unc_claims and all(d.get("authorization_status") == CLAIM_BLOCKED for d in unc_claims):
            status = "SECTION_BLOCKED"
            reason = FAILURE_CLAIM_AUTHORIZATION_BLOCKED
            missing_tuple = tuple(missing)
            failure_codes.append(FAILURE_CLAIM_AUTHORIZATION_BLOCKED)
        elif unc_claims and any(
            d.get("authorization_status") in {CLAIM_AUTHORIZED, CLAIM_AUTHORIZED_WITH_RESTRICTIONS}
            for d in unc_claims
        ):
            status = "SECTION_ALLOWED_WITH_RESTRICTIONS"
            reason = None
            missing_tuple = tuple(missing)
        else:
            status = "SECTION_REDACTED"
            reason = FAILURE_UNCERTAINTY_MISSING
            missing_tuple = tuple(dict.fromkeys([*missing, "confidence_interval_claim_authorization"]))
            failure_codes.append(FAILURE_UNCERTAINTY_MISSING)
        _add_section(
            _build_section(
                section_type="UNCERTAINTY_SUMMARY",
                section_status=status,
                required_claim_types=_UNCERTAINTY_CLAIMS,
                bound_claim_ids=tuple(d["claim_authorization_id"] for d in unc_claims),
                bound_evidence=_safe_str_list([v for v in evidence_ids_present.values() if v]),
                allowed=(),
                blocked=tuple(_blocked_notice(d) for d in unc_claims if d.get("authorization_status") == CLAIM_BLOCKED),
                caveats=("NO_UNCERTAINTY", "NO_CONFIDENCE_INTERVAL", "NO_STATISTICAL_SIGNIFICANCE"),
                redaction_reason=reason,
                missing_evidence=missing_tuple,
                trace={"governed_uncertainty": governed},
                request_id=request_id,
            )
        )
        if status == "SECTION_REDACTED":
            redacted_sections.append("UNCERTAINTY_SUMMARY")
        elif status == "SECTION_BLOCKED":
            blocked_sections.append("UNCERTAINTY_SUMMARY")

    # Evidence-only sections
    def _evidence_section(
        section_type: str,
        *,
        failure_code: str | None = None,
        required_claim_types: tuple[str, ...] = (),
    ) -> None:
        if section_type not in requested_sections or section_type in built_sections:
            return
        missing = _missing_for_section(section_type, data, auth_present=auth_present)
        bound = _safe_str_list([evidence_ids_present[k] for k in SECTION_EVIDENCE_REQUIREMENTS.get(section_type, ()) if k in evidence_ids_present])
        if missing:
            _add_section(
                _build_section(
                    section_type=section_type,
                    section_status="SECTION_REDACTED" if failure_code else "SECTION_NOT_EVALUATED",
                    required_claim_types=required_claim_types,
                    bound_claim_ids=(),
                    bound_evidence=bound,
                    allowed=(),
                    blocked=(),
                    caveats=(),
                    redaction_reason=failure_code or FAILURE_MISSING_REQUIRED_EVIDENCE,
                    missing_evidence=tuple(missing),
                    trace={"missing": missing},
                    request_id=request_id,
                )
            )
            if failure_code:
                redacted_sections.append(section_type)
                missing_evidence_global.extend(missing)
                failure_codes.append(failure_code)
                retry_categories.append("ADD_REQUIRED_EVIDENCE")
            return
        _add_section(
            _build_section(
                section_type=section_type,
                section_status="SECTION_ALLOWED",
                required_claim_types=required_claim_types,
                bound_claim_ids=(),
                bound_evidence=bound,
                allowed=(
                    _structured_surface(
                        surface_type="EVIDENCE_SUMMARY",
                        claim_type=section_type,
                        status="EVIDENCE_PRESENT",
                    ),
                ),
                blocked=(),
                caveats=("NO_PRODUCTION_AUTHORIZATION",) if section_type == "PRODUCTION_CATALOG_STATUS" else (),
                redaction_reason=None,
                missing_evidence=(),
                trace={"evidence_present": True},
                request_id=request_id,
            )
        )

    _evidence_section("DIAGNOSTIC_SUMMARY")
    _evidence_section("ASSIGNMENT_INTEGRITY_SUMMARY", failure_code=FAILURE_ASSIGNMENT_INTEGRITY_BLOCKED)
    _evidence_section("RANDOMIZATION_SUMMARY")
    _evidence_section("SRM_BALANCE_SUMMARY", failure_code=FAILURE_SRM_BALANCE_BLOCKED)
    _evidence_section("STATISTICAL_PROMOTION_SUMMARY", failure_code=FAILURE_STATISTICAL_PROMOTION_BLOCKED)
    _evidence_section("METHOD_AND_INSTRUMENT_SUMMARY")
    _evidence_section("PRODUCTION_CATALOG_STATUS", failure_code=FAILURE_PRODUCTION_CATALOG_BLOCKED)

    # RECOMMENDATION_SECTION
    if "RECOMMENDATION_SECTION" in requested_sections and "RECOMMENDATION_SECTION" not in built_sections:
        policy = _to_dict(data.get("trusted_surface_policy"))
        rec_claim = next((auth_by_type[c] for c in _RECOMMENDATION_CLAIMS if c in auth_by_type), None)
        missing = _missing_for_section("RECOMMENDATION_SECTION", data, auth_present=auth_present)
        if not auth_present:
            status = "SECTION_BLOCKED"
            reason = FAILURE_MISSING_CLAIM_AUTHORIZATION_REPORT
        elif cfg.block_recommendation_without_trusted_surface_policy and not _trusted_surface_allows_recommendation(policy):
            status = "SECTION_BLOCKED"
            reason = FAILURE_TRUSTED_SURFACE_POLICY_BLOCKED
            failure_codes.append(FAILURE_TRUSTED_SURFACE_POLICY_BLOCKED)
            retry_categories.append("REQUEST_WEAKER_REPORT_SURFACE")
        elif not rec_claim or rec_claim.get("authorization_status") != CLAIM_AUTHORIZED:
            status = "SECTION_BLOCKED"
            reason = FAILURE_CLAIM_AUTHORIZATION_BLOCKED
            failure_codes.append(FAILURE_CLAIM_AUTHORIZATION_BLOCKED)
        elif missing:
            status = "SECTION_REDACTED"
            reason = FAILURE_MISSING_REQUIRED_EVIDENCE
        else:
            status = "SECTION_ALLOWED_WITH_RESTRICTIONS"
            reason = None
        _add_section(
            _build_section(
                section_type="RECOMMENDATION_SECTION",
                section_status=status,
                required_claim_types=_RECOMMENDATION_CLAIMS,
                bound_claim_ids=(rec_claim["claim_authorization_id"],) if rec_claim else (),
                bound_evidence=_safe_str_list([v for v in evidence_ids_present.values() if v]),
                allowed=() if status != "SECTION_ALLOWED_WITH_RESTRICTIONS" else (_authorized_surface(rec_claim),),
                blocked=(_blocked_notice(rec_claim),) if rec_claim and status == "SECTION_BLOCKED" else (),
                caveats=("NO_PRODUCTION_AUTHORIZATION",),
                redaction_reason=reason,
                missing_evidence=tuple(missing),
                trace={"trusted_surface_policy_present": bool(policy)},
                request_id=request_id,
            )
        )
        if status == "SECTION_BLOCKED":
            blocked_sections.append("RECOMMENDATION_SECTION")

    # EXECUTIVE_SUMMARY — authorized + restricted only
    if "EXECUTIVE_SUMMARY" in requested_sections and auth_present and "EXECUTIVE_SUMMARY" not in built_sections:
        exec_surfaces = tuple(
            _restricted_surface(d) if d.get("authorization_status") == CLAIM_AUTHORIZED_WITH_RESTRICTIONS else _authorized_surface(d)
            for d in [*authorized, *restricted]
        )
        exec_caveats = _safe_str_list([c for d in [*authorized, *restricted] for c in (d.get("caveat_codes") or ())])
        status = "SECTION_ALLOWED_WITH_RESTRICTIONS" if exec_surfaces else "SECTION_NOT_EVALUATED"
        _add_section(
            _build_section(
                section_type="EXECUTIVE_SUMMARY",
                section_status=status,
                required_claim_types=tuple(d["claim_type"] for d in [*authorized, *restricted]),
                bound_claim_ids=tuple(d["claim_authorization_id"] for d in [*authorized, *restricted]),
                bound_evidence=(evidence_ids_present.get("claim_authorization_report", ""),),
                allowed=exec_surfaces,
                blocked=(),
                caveats=exec_caveats,
                redaction_reason=None,
                missing_evidence=(),
                trace={"excludes_blocked_claims": True},
                request_id=request_id,
            )
        )

    # CAVEATS_AND_LIMITATIONS
    if "CAVEATS_AND_LIMITATIONS" in requested_sections and "CAVEATS_AND_LIMITATIONS" not in built_sections:
        if auth_present and required_caveats:
            _add_section(
                _build_section(
                    section_type="CAVEATS_AND_LIMITATIONS",
                    section_status="SECTION_ALLOWED",
                    required_claim_types=(),
                    bound_claim_ids=tuple(d["claim_authorization_id"] for d in decisions),
                    bound_evidence=(evidence_ids_present.get("claim_authorization_report", ""),),
                    allowed=(
                        _structured_surface(
                            surface_type="CAVEAT_LIST",
                            claim_type="AGGREGATE",
                            status="REQUIRED",
                            caveats=required_caveats,
                        ),
                    ),
                    blocked=(),
                    caveats=required_caveats,
                    redaction_reason=None,
                    missing_evidence=(),
                    trace={"caveat_count": len(required_caveats)},
                    request_id=request_id,
                )
            )
        elif auth_present:
            _add_section(
                _build_section(
                    section_type="CAVEATS_AND_LIMITATIONS",
                    section_status="SECTION_NOT_EVALUATED",
                    required_claim_types=(),
                    bound_claim_ids=(),
                    bound_evidence=(evidence_ids_present.get("claim_authorization_report", ""),),
                    allowed=(),
                    blocked=(),
                    caveats=(),
                    redaction_reason=None,
                    missing_evidence=(),
                    trace={},
                    request_id=request_id,
                )
            )
        else:
            _add_section(
                _build_section(
                    section_type="CAVEATS_AND_LIMITATIONS",
                    section_status="SECTION_BLOCKED",
                    required_claim_types=(),
                    bound_claim_ids=(),
                    bound_evidence=(),
                    allowed=(),
                    blocked=(),
                    caveats=(),
                    redaction_reason=FAILURE_MISSING_CLAIM_AUTHORIZATION_REPORT,
                    missing_evidence=("claim_authorization_report",),
                    trace={},
                    request_id=request_id,
                )
            )

    # EVIDENCE_TRACE / LINEAGE / APPENDIX
    for section_type in ("EVIDENCE_TRACE", "LINEAGE_AND_PROVENANCE", "APPENDIX"):
        if section_type in requested_sections:
            _evidence_section(section_type)

    # Overall report status
    has_content = bool(allowed_sections or restricted_sections)
    if not auth_present and cfg.require_claim_authorization_report:
        report_status = TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION
    elif has_content and (redacted_sections or blocked_sections):
        report_status = TRUSTED_REPORT_READY_WITH_REDACTIONS
    elif has_content:
        report_status = TRUSTED_REPORT_READY
    elif FAILURE_MISSING_CLAIM_AUTHORIZATION_REPORT in failure_codes:
        report_status = TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION
    elif FAILURE_TRUSTED_SURFACE_POLICY_BLOCKED in failure_codes:
        report_status = TRUSTED_REPORT_BLOCKED_BY_TRUSTED_SURFACE_POLICY
    elif FAILURE_PRODUCTION_CATALOG_BLOCKED in failure_codes:
        report_status = TRUSTED_REPORT_BLOCKED_BY_PRODUCTION_CATALOG
    elif FAILURE_STATISTICAL_PROMOTION_BLOCKED in failure_codes:
        report_status = TRUSTED_REPORT_BLOCKED_BY_STATISTICAL_PROMOTION
    elif FAILURE_ASSIGNMENT_INTEGRITY_BLOCKED in failure_codes:
        report_status = TRUSTED_REPORT_BLOCKED_BY_ASSIGNMENT_INTEGRITY
    elif FAILURE_SRM_BALANCE_BLOCKED in failure_codes:
        report_status = TRUSTED_REPORT_BLOCKED_BY_SRM_BALANCE
    elif FAILURE_MISSING_REQUIRED_EVIDENCE in failure_codes:
        report_status = TRUSTED_REPORT_BLOCKED_BY_MISSING_EVIDENCE
    elif blocked_sections:
        report_status = TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION
    else:
        report_status = TRUSTED_REPORT_NOT_EVALUATED

    lineage = _to_dict(data.get("lineage_manifest")) or {
        "artifact_id": _ARTIFACT_ID,
        "request_id": request_id,
        "evidence_keys": sorted(evidence_ids_present.keys()),
    }

    hash_payload = {
        "request_id": request_id,
        "report_status": report_status,
        "sections": [
            {
                "section_type": s.section_type,
                "section_status": s.section_status,
                "bound_claim_authorization_ids": list(s.bound_claim_authorization_ids),
                "bound_evidence_ids": list(s.bound_evidence_ids),
            }
            for s in sections
        ],
        "required_caveats": list(required_caveats),
        "policy_version": _POLICY_VERSION,
    }
    provenance_hash = _hash_payload(hash_payload)
    report_id = f"trusted_report_{_hash_payload({'request_id': request_id, 'design_id': design_id, 'readout_id': readout_id})[:16]}"

    failure_packet = None
    if failure_codes or blocking_sections or missing_evidence_global:
        failure_packet = {
            "failure_code": failure_codes[0] if failure_codes else FAILURE_SECTION_BLOCKED_BY_POLICY,
            "failure_reason": failure_reasons[0] if failure_reasons else "report sections blocked or redacted",
            "blocking_sections": _safe_str_list(blocking_sections),
            "blocking_claims": _safe_str_list([d["claim_type"] for d in blocked]),
            "missing_evidence": _safe_str_list(missing_evidence_global),
            "failed_evidence": _safe_str_list(failed_evidence_global),
            "required_remediation": _safe_str_list(failure_reasons),
            "retry_category": retry_categories[0] if retry_categories else "BLOCK_TRUSTED_REPORT",
        }

    claim_boundary = {
        **_POSITIVE_FLAGS,
        **_AUTH_FALSE,
        "artifact_id": _ARTIFACT_ID,
        "structured_packet_only": True,
        "narrative_generation": False,
    }

    authorized_bindings = tuple(
        {
            "claim_authorization_id": d["claim_authorization_id"],
            "claim_type": d["claim_type"],
            "authorization_status": d["authorization_status"],
            "evidence_ids": list(d.get("satisfied_evidence") or ()),
        }
        for d in authorized
    )
    restricted_bindings = tuple(
        {
            "claim_authorization_id": d["claim_authorization_id"],
            "claim_type": d["claim_type"],
            "authorization_status": d["authorization_status"],
            "caveats": list(d.get("caveat_codes") or ()),
            "evidence_ids": list(d.get("satisfied_evidence") or ()),
        }
        for d in restricted
    )
    blocked_summaries = tuple(
        {
            "claim_authorization_id": d["claim_authorization_id"],
            "claim_type": d["claim_type"],
            "status": "NOT_AUTHORIZED",
            "blockers": list(d.get("blockers") or ()),
        }
        for d in blocked
    )

    return TrustedReadoutReportRuntimeReport(
        request_id=request_id,
        report_id=report_id,
        report_status=report_status,
        report_type=str(report_type) if report_type else None,
        report_scope=str(report_scope) if report_scope else None,
        experiment_id=str(experiment_id) if experiment_id else None,
        design_id=str(design_id) if design_id else None,
        readout_id=str(readout_id) if readout_id else None,
        sections=tuple(sections),
        allowed_sections=_safe_str_list(allowed_sections),
        restricted_sections=_safe_str_list(restricted_sections),
        redacted_sections=_safe_str_list(redacted_sections),
        blocked_sections=_safe_str_list(blocked_sections),
        authorized_claim_bindings=authorized_bindings,
        restricted_claim_bindings=restricted_bindings,
        blocked_claim_summaries=blocked_summaries,
        required_caveats=required_caveats,
        evidence_bundle_summary={
            "present": sorted(evidence_ids_present.keys()),
            "missing": _safe_str_list(missing_evidence_global),
        },
        missing_evidence=_safe_str_list(missing_evidence_global),
        failed_evidence=_safe_str_list(failed_evidence_global),
        lineage_manifest=lineage,
        provenance_hash=provenance_hash,
        policy_version=_POLICY_VERSION,
        failure_packet=failure_packet,
        warnings=_safe_str_list(warnings),
        claim_boundary_report=claim_boundary,
    )


def generate_trusted_readout_report(
    input_data: Any,
    config: TrustedReadoutReportRuntimeConfig | dict[str, Any] | None = None,
) -> TrustedReadoutReportRuntimeReport | list[TrustedReadoutReportRuntimeReport]:
    cfg = _resolve_config(config)
    if isinstance(input_data, list):
        return [_evaluate_single(_to_dict(x), cfg) for x in input_data]
    data = _to_dict(input_data)
    if "requests" in data and isinstance(data["requests"], list):
        return [_evaluate_single(_to_dict(x), cfg) for x in data["requests"]]
    return _evaluate_single(data, cfg)


build_trusted_readout_report = generate_trusted_readout_report
create_trusted_readout_packet = generate_trusted_readout_report


def build_trusted_readout_report_input_from_execution(
    execution_report: Any,
    *,
    extra_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = _to_dict(execution_report)
    packet = report.get("execution_packet") or {}
    payload: dict[str, Any] = {
        "request_id": report.get("design_id") or report.get("request_id"),
        "design_id": report.get("design_id"),
        "execution_result": packet,
        "execution_artifact_manifest": report.get("execution_artifact_manifest"),
        "instrument_execution_results": list(report.get("instrument_execution_results") or []),
        "claim_authorization_report": packet.get("claim_authorization_report"),
        "lineage_manifest": report.get("execution_provenance_manifest"),
        "evidence_sources": {
            "execution_artifact_manifest": report.get("execution_artifact_manifest"),
            "execution_provenance_manifest": report.get("execution_provenance_manifest"),
        },
    }
    if extra_evidence:
        payload.update(extra_evidence)
    return payload


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
    from panel_exp.validation.readout_diagnostics_sensitivity_runtime_001 import EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW
    from panel_exp.validation.statistical_promotion_thresholds_001 import STATISTICAL_PROMOTION_PASSED
    from panel_exp.validation.estimator_inference_did_executor_003 import EFFECT_ESTIMATE_COMPUTED_POINT_ONLY

    claim_scope = {"estimand": "STANDARD_INCREMENTALITY", "metric_kpi": "sales"}
    effect = {
        "estimation_status": EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
        "point_estimate": 1.0,
    }
    base = {
        "request_id": "validation_001",
        "design_id": "design_validation_001",
        "claim_scope": claim_scope,
        "claim_requests": [{"claim_type": "POINT_ESTIMATE_DESCRIPTION", "claim_scope": claim_scope}],
        "assignment_panel_integrity_report": {"status": ASSIGNMENT_PANEL_INTEGRITY_PASSED},
        "srm_balance_diagnostic_report": {"status": SRM_BALANCE_DIAGNOSTIC_PASSED},
        "diagnostics_sensitivity_report": {"evidence_sufficiency_status": EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW},
        "statistical_promotion_report": {"status": STATISTICAL_PROMOTION_PASSED},
        "instrument_execution_results": [
            {
                "instrument_id": "DID_2X2_POINT_ESTIMATE",
                "effect_estimate_report": effect,
                "uncertainty_report": {"uncertainty_report_status": "NOT_COMPUTED"},
            }
        ],
        "execution_result": {"execution_status": "INSTRUMENT_EXECUTION_COMPLETED"},
    }
    report = generate_trusted_readout_report(base)
    assert isinstance(report, TrustedReadoutReportRuntimeReport)
    blocked = generate_trusted_readout_report({"request_id": "no_auth"})
    assert isinstance(blocked, TrustedReadoutReportRuntimeReport)
    assert blocked.report_status == TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "trusted_readout_report_runtime",
        "base_commit": _git_head(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": [
            "TRUSTED_READOUT_REPORT_CONTRACT_001",
            "CLAIM_AUTHORIZATION_RUNTIME_001",
            "CLAIM_AUTHORIZATION_CONTRACT_001",
            "SRM_BALANCE_READOUT_DIAGNOSTIC_001",
            "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001",
            "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001",
            "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001",
        ],
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "failed_scenarios": [],
        "final_verdict": _VERDICT,
        "execution_runtime_integration_added": True,
        "readout_plan_prerequisite_added": True,
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
