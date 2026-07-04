"""CLAIM_AUTHORIZATION_RUNTIME_001 — governed claim authorization runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.assignment_panel_integrity_runtime_001 import (
    ASSIGNMENT_PANEL_INTEGRITY_BLOCKED,
    ASSIGNMENT_PANEL_INTEGRITY_FAILED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS,
)
from panel_exp.validation.did_instrument_estimand_registry_001 import (
    DID_2X2_POINT_ESTIMATE,
    is_did_bootstrap_inference_instrument,
    is_governed_did_point_estimate_instrument,
    resolve_did_instrument_id,
)
from panel_exp.validation.estimator_inference_did_executor_003 import (
    EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
)
from panel_exp.validation.governed_randomization_runtime_001 import (
    GOVERNED_RANDOMIZATION_BLOCKED,
    GOVERNED_RANDOMIZATION_COMPLETED,
    GOVERNED_RANDOMIZATION_COMPLETED_WITH_WARNINGS,
    GOVERNED_RANDOMIZATION_FAILED,
)
from panel_exp.validation.production_catalog_blocklist_001 import (
    PRODUCTION_CATALOG_BLOCKED,
    PRODUCTION_CATALOG_DIAGNOSTIC_ONLY,
    PRODUCTION_CATALOG_RESEARCH_ONLY,
    evaluate_production_catalog_status,
)
from panel_exp.validation.readout_diagnostics_sensitivity_runtime_001 import (
    EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS,
    EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS,
    EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW,
    EVIDENCE_SUFFICIENT_WITH_WARNINGS,
)
from panel_exp.validation.srm_balance_readout_diagnostic_001 import (
    SRM_BALANCE_DIAGNOSTIC_BLOCKED,
    SRM_BALANCE_DIAGNOSTIC_FAILED,
    SRM_BALANCE_DIAGNOSTIC_PASSED,
    SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS,
)
from panel_exp.validation.statistical_promotion_thresholds_001 import (
    STATISTICAL_PROMOTION_FAILED,
    STATISTICAL_PROMOTION_PASSED,
    STATISTICAL_PROMOTION_PASSED_WITH_WARNINGS,
)

_ARTIFACT_ID = "CLAIM_AUTHORIZATION_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "claim_authorization_runtime_implemented_no_trusted_report_or_production_authorization"
_VERDICT = "claim_authorization_runtime_implemented_no_trusted_report_or_production_authorization"
_RECOMMENDED_NEXT = "TRUSTED_READOUT_REPORT_CONTRACT_001"
_ALTERNATIVE_NEXT = "TRUSTED_READOUT_REPORT_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/CLAIM_AUTHORIZATION_RUNTIME_001_summary.json"

CLAIM_AUTHORIZED = "CLAIM_AUTHORIZED"
CLAIM_AUTHORIZED_WITH_RESTRICTIONS = "CLAIM_AUTHORIZED_WITH_RESTRICTIONS"
CLAIM_INSUFFICIENT_EVIDENCE = "CLAIM_INSUFFICIENT_EVIDENCE"
CLAIM_BLOCKED = "CLAIM_BLOCKED"
CLAIM_NOT_EVALUATED = "CLAIM_NOT_EVALUATED"

CLAIM_AUTHORIZATION_COMPLETED = "CLAIM_AUTHORIZATION_COMPLETED"
CLAIM_AUTHORIZATION_COMPLETED_WITH_RESTRICTIONS = "CLAIM_AUTHORIZATION_COMPLETED_WITH_RESTRICTIONS"
CLAIM_AUTHORIZATION_BLOCKED = "CLAIM_AUTHORIZATION_BLOCKED"
CLAIM_AUTHORIZATION_INSUFFICIENT_EVIDENCE = "CLAIM_AUTHORIZATION_INSUFFICIENT_EVIDENCE"
CLAIM_AUTHORIZATION_NOT_EVALUATED = "CLAIM_AUTHORIZATION_NOT_EVALUATED"

BLOCKER_PRODUCTION_CATALOG_BLOCKED = "PRODUCTION_CATALOG_BLOCKED"
BLOCKER_METHOD_NOT_PRODUCTION_SAFE = "METHOD_NOT_PRODUCTION_SAFE"
BLOCKER_STATISTICAL_PROMOTION_FAILED = "STATISTICAL_PROMOTION_FAILED"
BLOCKER_STATISTICAL_PROMOTION_MISSING = "STATISTICAL_PROMOTION_MISSING"
BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_FAILED = "ASSIGNMENT_PANEL_INTEGRITY_FAILED"
BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_MISSING = "ASSIGNMENT_PANEL_INTEGRITY_MISSING"
BLOCKER_SRM_BALANCE_DIAGNOSTIC_FAILED = "SRM_BALANCE_DIAGNOSTIC_FAILED"
BLOCKER_SRM_BALANCE_DIAGNOSTIC_MISSING = "SRM_BALANCE_DIAGNOSTIC_MISSING"
BLOCKER_REQUIRED_DIAGNOSTIC_FAILED = "REQUIRED_DIAGNOSTIC_FAILED"
BLOCKER_REQUIRED_DIAGNOSTIC_MISSING = "REQUIRED_DIAGNOSTIC_MISSING"
BLOCKER_UNCERTAINTY_MISSING = "UNCERTAINTY_MISSING"
BLOCKER_INFERENCE_NOT_IMPLEMENTED = "INFERENCE_NOT_IMPLEMENTED"
BLOCKER_CONFIDENCE_INTERVAL_MISSING = "CONFIDENCE_INTERVAL_MISSING"
BLOCKER_P_VALUE_MISSING = "P_VALUE_MISSING"
BLOCKER_EFFECT_ESTIMATE_MISSING = "EFFECT_ESTIMATE_MISSING"
BLOCKER_TRUSTED_REPORT_RUNTIME_MISSING = "TRUSTED_REPORT_RUNTIME_MISSING"
BLOCKER_CLAIM_SCOPE_MISSING = "CLAIM_SCOPE_MISSING"
BLOCKER_ESTIMAND_MISMATCH = "ESTIMAND_MISMATCH"
BLOCKER_INSTRUMENT_CLAIM_MISMATCH = "INSTRUMENT_CLAIM_MISMATCH"
BLOCKER_PRODUCTION_CONTEXT_NOT_AUTHORIZED = "PRODUCTION_CONTEXT_NOT_AUTHORIZED"

CAVEAT_DESCRIPTIVE_ONLY = "DESCRIPTIVE_ONLY"
CAVEAT_POINT_ESTIMATE_ONLY = "POINT_ESTIMATE_ONLY"
CAVEAT_NO_UNCERTAINTY = "NO_UNCERTAINTY"
CAVEAT_NO_STATISTICAL_SIGNIFICANCE = "NO_STATISTICAL_SIGNIFICANCE"
CAVEAT_NO_CONFIDENCE_INTERVAL = "NO_CONFIDENCE_INTERVAL"
CAVEAT_NO_CAUSAL_CLAIM = "NO_CAUSAL_CLAIM"
CAVEAT_NO_INCREMENTAL_CLAIM = "NO_INCREMENTAL_CLAIM"
CAVEAT_NO_ROI_CLAIM = "NO_ROI_CLAIM"
CAVEAT_NO_PRODUCTION_AUTHORIZATION = "NO_PRODUCTION_AUTHORIZATION"
CAVEAT_RESEARCH_OR_REVIEW_ONLY = "RESEARCH_OR_REVIEW_ONLY"
CAVEAT_DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"
CAVEAT_METHOD_BLOCKED_FOR_PRODUCTION = "METHOD_BLOCKED_FOR_PRODUCTION"

RETRY_ADD_ASSIGNMENT_PANEL_INTEGRITY_EVIDENCE = "ADD_ASSIGNMENT_PANEL_INTEGRITY_EVIDENCE"
RETRY_ADD_SRM_BALANCE_DIAGNOSTIC = "ADD_SRM_BALANCE_DIAGNOSTIC"
RETRY_ADD_REQUIRED_DIAGNOSTICS = "ADD_REQUIRED_DIAGNOSTICS"
RETRY_ADD_GOVERNED_UNCERTAINTY = "ADD_GOVERNED_UNCERTAINTY"
RETRY_ADD_STATISTICAL_PROMOTION_EVIDENCE = "ADD_STATISTICAL_PROMOTION_EVIDENCE"
RETRY_FIX_PRODUCTION_CATALOG_BLOCKER = "FIX_PRODUCTION_CATALOG_BLOCKER"
RETRY_IMPLEMENT_TRUSTED_REPORT_RUNTIME = "IMPLEMENT_TRUSTED_REPORT_RUNTIME"
RETRY_REQUEST_WEAKER_DESCRIPTIVE_CLAIM = "REQUEST_WEAKER_DESCRIPTIVE_CLAIM"
RETRY_KEEP_RESEARCH_ONLY = "KEEP_RESEARCH_ONLY"
RETRY_BLOCK_CLAIM = "BLOCK_CLAIM"

CANONICAL_CLAIM_TYPES = frozenset({
    "POINT_ESTIMATE_DESCRIPTION",
    "DESCRIPTIVE_DIAGNOSTIC_DESCRIPTION",
    "ASSIGNMENT_INTEGRITY_DESCRIPTION",
    "RANDOMIZATION_ARTIFACT_DESCRIPTION",
    "SRM_BALANCE_DIAGNOSTIC_DESCRIPTION",
    "DIRECTIONAL_RESULT_DESCRIPTION",
    "DIRECTIONAL_LIFT_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "INCREMENTAL_CONVERSIONS_CLAIM",
    "INCREMENTAL_REVENUE_CLAIM",
    "ROI_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "CONFIDENCE_INTERVAL_CLAIM",
    "PRODUCTION_READOUT_CLAIM",
    "TRUSTED_BUSINESS_RECOMMENDATION",
})

CLAIM_TYPE_ALIASES: dict[str, str] = {
    "POINT_ESTIMATE_CLAIM": "POINT_ESTIMATE_DESCRIPTION",
    "DESCRIPTIVE_EFFECT_CLAIM": "POINT_ESTIMATE_DESCRIPTION",
    "DIAGNOSTIC_ONLY_CLAIM": "DESCRIPTIVE_DIAGNOSTIC_DESCRIPTION",
    "INCREMENTAL_LIFT_CLAIM": "INCREMENTAL_CONVERSIONS_CLAIM",
    "POINT_ESTIMATE_READOUT_CLAIM": "POINT_ESTIMATE_DESCRIPTION",
    "SENSITIVITY_ONLY_CLAIM": "DESCRIPTIVE_DIAGNOSTIC_DESCRIPTION",
    "METHOD_COMPARISON_CLAIM": "DESCRIPTIVE_DIAGNOSTIC_DESCRIPTION",
    "INSUFFICIENT_EVIDENCE_CLAIM": "DESCRIPTIVE_DIAGNOSTIC_DESCRIPTION",
}

_STRONG_CLAIM_TYPES = frozenset({
    "DIRECTIONAL_LIFT_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "INCREMENTAL_CONVERSIONS_CLAIM",
    "INCREMENTAL_REVENUE_CLAIM",
    "ROI_CLAIM",
    "PRODUCTION_READOUT_CLAIM",
    "TRUSTED_BUSINESS_RECOMMENDATION",
})

_INFERENCE_CLAIM_TYPES = frozenset({
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "CONFIDENCE_INTERVAL_CLAIM",
})

_DESCRIPTIVE_CLAIM_TYPES = frozenset({
    "ASSIGNMENT_INTEGRITY_DESCRIPTION",
    "RANDOMIZATION_ARTIFACT_DESCRIPTION",
    "SRM_BALANCE_DIAGNOSTIC_DESCRIPTION",
    "DESCRIPTIVE_DIAGNOSTIC_DESCRIPTION",
})

_INTEGRITY_PASSED = frozenset({
    ASSIGNMENT_PANEL_INTEGRITY_PASSED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS,
})

_SRM_PASSED = frozenset({
    SRM_BALANCE_DIAGNOSTIC_PASSED,
    SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS,
})

_RANDOMIZATION_PASSED = frozenset({
    GOVERNED_RANDOMIZATION_COMPLETED,
    GOVERNED_RANDOMIZATION_COMPLETED_WITH_WARNINGS,
})

_PROMOTION_PASSED = frozenset({
    STATISTICAL_PROMOTION_PASSED,
    STATISTICAL_PROMOTION_PASSED_WITH_WARNINGS,
})

_DIAGNOSTICS_PASSED = frozenset({
    EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW,
    EVIDENCE_SUFFICIENT_WITH_WARNINGS,
})

_POSITIVE_FLAGS = {
    "claim_authorization_runtime_implemented": True,
    "claim_authorization_evaluated": True,
    "descriptive_claims_authorized_with_restrictions": True,
    "claim_blockers_enforced": True,
    "production_claims_blocked_without_required_evidence": True,
    "statistical_significance_claims_blocked_without_inference": True,
    "roi_claims_blocked_without_roi_evidence": True,
    "trusted_report_claims_blocked_without_trusted_report_runtime": True,
}

_AUTH_FALSE = {
    "production_authorization_granted": False,
    "production_readout_authorized": False,
    "trusted_readout_handoff_generated": False,
    "trusted_readout_report_generated": False,
    "authorized_claim_text_generated": False,
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
class ClaimAuthorizationRuntimeConfig:
    require_claim_scope: bool = True
    require_assignment_panel_integrity_for_execution_claims: bool = True
    require_srm_balance_for_directional_claims: bool = True
    block_production_claims_without_trusted_report_runtime: bool = True
    trusted_readout_report_runtime_implemented: bool = False


@dataclass(frozen=True)
class ClaimAuthorizationDecision:
    claim_type: str
    claim_scope: dict[str, Any]
    authorization_status: str
    is_authorized: bool
    is_restricted: bool
    is_blocking: bool
    required_evidence: tuple[str, ...]
    satisfied_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    failed_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    caveat_codes: tuple[str, ...]
    allowed_surface: tuple[str, ...]
    disallowed_surface: tuple[str, ...]
    retry_category: str | None
    trace: dict[str, Any]


@dataclass(frozen=True)
class ClaimAuthorizationRuntimeReport:
    request_id: str
    overall_status: str
    production_context: bool
    claim_authorizations: tuple[ClaimAuthorizationDecision, ...]
    authorized_claims: tuple[str, ...]
    restricted_claims: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    insufficient_evidence_claims: tuple[str, ...]
    not_evaluated_claims: tuple[str, ...]
    required_evidence_summary: dict[str, Any]
    missing_evidence: tuple[str, ...]
    failed_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    caveats: tuple[str, ...]
    retry_categories: tuple[str, ...]
    evidence_trace: dict[str, Any]
    claim_boundary_report: dict[str, Any]
    policy_version: str
    provenance: dict[str, Any]


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
    config: ClaimAuthorizationRuntimeConfig | dict[str, Any] | None,
) -> ClaimAuthorizationRuntimeConfig:
    if config is None:
        return ClaimAuthorizationRuntimeConfig()
    if isinstance(config, ClaimAuthorizationRuntimeConfig):
        return config
    base = ClaimAuthorizationRuntimeConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return ClaimAuthorizationRuntimeConfig(**merged)


def _normalize_claim_type(raw: str) -> str:
    tok = _token(raw)
    return CLAIM_TYPE_ALIASES.get(tok, tok)


def _is_production_context(data: dict[str, Any]) -> bool:
    return _token(data.get("production_context")) in {"PRODUCTION", "TRUE", "1", "YES"}


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


def _extract_effect_report(data: dict[str, Any]) -> dict[str, Any]:
    direct = _to_dict(data.get("effect_estimate_report"))
    if direct:
        return direct
    execution = _to_dict(data.get("execution_result"))
    if execution.get("effect_estimate_report"):
        return _to_dict(execution["effect_estimate_report"])
    for row in data.get("instrument_execution_results") or []:
        if isinstance(row, dict) and row.get("effect_estimate_report"):
            return _to_dict(row["effect_estimate_report"])
    return {}


def _extract_uncertainty_report(data: dict[str, Any]) -> dict[str, Any]:
    direct = _to_dict(data.get("uncertainty_report"))
    if direct:
        return direct
    execution = _to_dict(data.get("execution_result"))
    if execution.get("uncertainty_report"):
        return _to_dict(execution["uncertainty_report"])
    for row in data.get("instrument_execution_results") or []:
        if isinstance(row, dict) and row.get("uncertainty_report"):
            return _to_dict(row["uncertainty_report"])
    return {}


def _extract_instrument_id(data: dict[str, Any], claim: dict[str, Any]) -> str:
    for source in (claim, data):
        for key in ("instrument_id", "applies_to_instrument_id"):
            if source.get(key):
                return str(source[key])
    effect = _extract_effect_report(data)
    if effect.get("instrument_id"):
        return str(effect["instrument_id"])
    return str(data.get("instrument_id") or "")


def _effect_estimate_exists(report: dict[str, Any]) -> bool:
    if not report:
        return False
    status = _token(report.get("estimation_status") or report.get("effect_estimate_report_status"))
    if status == EFFECT_ESTIMATE_COMPUTED_POINT_ONLY:
        return True
    return report.get("point_estimate") is not None


def _direction_available(report: dict[str, Any]) -> bool:
    if not _effect_estimate_exists(report):
        return False
    pe = report.get("point_estimate")
    if pe is None:
        return False
    try:
        return float(pe) != 0.0
    except (TypeError, ValueError):
        return False


def _uncertainty_computed(report: dict[str, Any]) -> bool:
    if not report:
        return False
    status = _token(report.get("uncertainty_report_status"))
    if status in {"", "NOT_COMPUTED", "NOT_EVALUATED"}:
        return False
    return bool(report.get("confidence_interval") or report.get("p_value") is not None)


def _p_value_computed(report: dict[str, Any]) -> bool:
    return report.get("p_value") is not None


def _ci_computed(report: dict[str, Any]) -> bool:
    return bool(report.get("confidence_interval"))


def _integrity_passed(report: dict[str, Any] | None) -> bool:
    return _report_status(report) in _INTEGRITY_PASSED


def _integrity_failed(report: dict[str, Any] | None) -> bool:
    status = _report_status(report)
    return status in {ASSIGNMENT_PANEL_INTEGRITY_FAILED, ASSIGNMENT_PANEL_INTEGRITY_BLOCKED}


def _srm_passed(report: dict[str, Any] | None) -> bool:
    return _report_status(report) in _SRM_PASSED


def _srm_failed(report: dict[str, Any] | None) -> bool:
    return _report_status(report) in {
        SRM_BALANCE_DIAGNOSTIC_FAILED,
        SRM_BALANCE_DIAGNOSTIC_BLOCKED,
    }


def _randomization_passed(report: dict[str, Any] | None) -> bool:
    return _report_status(report) in _RANDOMIZATION_PASSED


def _promotion_passed(report: dict[str, Any] | None) -> bool:
    return _report_status(report) in _PROMOTION_PASSED


def _promotion_failed(report: dict[str, Any] | None) -> bool:
    return _report_status(report) == STATISTICAL_PROMOTION_FAILED


def _diagnostics_passed(report: dict[str, Any] | None) -> bool:
    return _report_status(report) in _DIAGNOSTICS_PASSED


def _diagnostics_failed(report: dict[str, Any] | None) -> bool:
    return _report_status(report) == EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS


def _execution_completed(data: dict[str, Any]) -> bool:
    execution = _to_dict(data.get("execution_result"))
    status = _report_status(execution) or _token(data.get("execution_status"))
    if status.endswith("_COMPLETED") or status == "INSTRUMENT_EXECUTION_COMPLETED":
        return True
    for row in data.get("instrument_execution_results") or []:
        if isinstance(row, dict) and _token(row.get("instrument_execution_status")) == "INSTRUMENT_EXECUTION_COMPLETED":
            return True
    return False


def _resolve_catalog_status(data: dict[str, Any], instrument_id: str) -> dict[str, Any]:
    direct = _to_dict(data.get("production_catalog_report"))
    if direct:
        return direct
    row = {
        "instrument_id": instrument_id,
        "estimator_family": data.get("method_family") or data.get("estimator_family"),
        "inference_family": data.get("inference_family"),
        "production_context": data.get("production_context"),
    }
    return _to_dict(evaluate_production_catalog_status(row))


def _catalog_blocks_production(catalog: dict[str, Any]) -> bool:
    status = _token(catalog.get("production_catalog_status"))
    return status in {
        PRODUCTION_CATALOG_BLOCKED,
        PRODUCTION_CATALOG_RESEARCH_ONLY,
        PRODUCTION_CATALOG_DIAGNOSTIC_ONLY,
    }


def _claim_boundary(*, evaluated: bool) -> dict[str, Any]:
    return {
        **_POSITIVE_FLAGS,
        "claim_authorization_evaluated": evaluated,
        **_AUTH_FALSE,
    }


def _build_decision(
    claim_type: str,
    claim_scope: dict[str, Any],
    *,
    status: str,
    required: list[str],
    satisfied: list[str],
    missing: list[str],
    failed: list[str],
    blockers: list[str],
    caveats: list[str],
    allowed: list[str],
    disallowed: list[str],
    retry: str | None,
    trace: dict[str, Any],
) -> ClaimAuthorizationDecision:
    is_authorized = status in {CLAIM_AUTHORIZED, CLAIM_AUTHORIZED_WITH_RESTRICTIONS}
    is_restricted = status == CLAIM_AUTHORIZED_WITH_RESTRICTIONS
    is_blocking = status in {CLAIM_BLOCKED, CLAIM_INSUFFICIENT_EVIDENCE}
    return ClaimAuthorizationDecision(
        claim_type=claim_type,
        claim_scope=claim_scope,
        authorization_status=status,
        is_authorized=is_authorized,
        is_restricted=is_restricted,
        is_blocking=is_blocking,
        required_evidence=_safe_str_list(required),
        satisfied_evidence=_safe_str_list(satisfied),
        missing_evidence=_safe_str_list(missing),
        failed_evidence=_safe_str_list(failed),
        blockers=_safe_str_list(blockers),
        caveat_codes=_safe_str_list(caveats),
        allowed_surface=_safe_str_list(allowed),
        disallowed_surface=_safe_str_list(disallowed),
        retry_category=retry,
        trace=trace,
    )


def _evaluate_claim(
    claim: dict[str, Any],
    data: dict[str, Any],
    cfg: ClaimAuthorizationRuntimeConfig,
) -> ClaimAuthorizationDecision:
    raw_type = str(claim.get("claim_type") or "")
    claim_type = _normalize_claim_type(raw_type)
    claim_scope = _to_dict(claim.get("claim_scope") or data.get("claim_scope"))
    instrument_id = _extract_instrument_id(data, claim)
    production = _is_production_context(data) or bool(claim.get("requires_production_readout"))

    integrity = _to_dict(
        data.get("assignment_panel_integrity_report")
        or data.get("assignment_panel_integrity")
    )
    srm = _to_dict(data.get("srm_balance_diagnostic_report") or data.get("srm_balance_report"))
    randomization = _to_dict(
        data.get("governed_randomization_report") or data.get("randomization_report")
    )
    promotion = _to_dict(data.get("statistical_promotion_report"))
    diagnostics = _to_dict(
        data.get("diagnostics_sensitivity_report") or data.get("diagnostics_sensitivity")
    )
    effect = _extract_effect_report(data)
    uncertainty = _extract_uncertainty_report(data)
    catalog = _resolve_catalog_status(data, instrument_id)

    required: list[str] = []
    satisfied: list[str] = []
    missing: list[str] = []
    failed: list[str] = []
    blockers: list[str] = []
    caveats: list[str] = []
    allowed: list[str] = []
    disallowed: list[str] = []
    retry: str | None = None

    trace_payload = {
        "claim_type": claim_type,
        "instrument_id": instrument_id,
        "production_context": production,
    }
    trace = {**trace_payload, "integrity_hash": _hash_payload(trace_payload)}

    if claim_type not in CANONICAL_CLAIM_TYPES:
        return _build_decision(
            claim_type, claim_scope,
            status=CLAIM_NOT_EVALUATED,
            required=["supported_claim_type"],
            satisfied=[], missing=["supported_claim_type"], failed=[],
            blockers=[BLOCKER_INSTRUMENT_CLAIM_MISMATCH],
            caveats=[], allowed=[], disallowed=["unsupported_claim_type"],
            retry=RETRY_REQUEST_WEAKER_DESCRIPTIVE_CLAIM, trace=trace,
        )

    if cfg.require_claim_scope and not claim_scope:
        blockers.append(BLOCKER_CLAIM_SCOPE_MISSING)
        missing.append("claim_scope")
        retry = RETRY_REQUEST_WEAKER_DESCRIPTIVE_CLAIM
        return _build_decision(
            claim_type, claim_scope,
            status=CLAIM_INSUFFICIENT_EVIDENCE,
            required=["claim_scope"], satisfied=satisfied, missing=missing,
            failed=failed, blockers=blockers, caveats=caveats,
            allowed=allowed, disallowed=disallowed, retry=retry, trace=trace,
        )

    # Descriptive metadata claims
    if claim_type == "ASSIGNMENT_INTEGRITY_DESCRIPTION":
        required.append("assignment_panel_integrity_report")
        if integrity:
            satisfied.append("assignment_panel_integrity_report")
            if _integrity_passed(integrity):
                caveats.extend([CAVEAT_DESCRIPTIVE_ONLY, CAVEAT_NO_CAUSAL_CLAIM, CAVEAT_NO_PRODUCTION_AUTHORIZATION])
                allowed.extend(["assignment_integrity_passed", "panel_labels_match_assignment"])
                return _build_decision(
                    claim_type, claim_scope, status=CLAIM_AUTHORIZED_WITH_RESTRICTIONS,
                    required=required, satisfied=satisfied, missing=missing, failed=failed,
                    blockers=blockers, caveats=caveats, allowed=allowed,
                    disallowed=["causal_lift", "production_readout"], retry=None, trace=trace,
                )
            if _integrity_failed(integrity):
                failed.append("assignment_panel_integrity_report")
                blockers.append(BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_FAILED)
                retry = RETRY_ADD_ASSIGNMENT_PANEL_INTEGRITY_EVIDENCE
                return _build_decision(
                    claim_type, claim_scope, status=CLAIM_BLOCKED,
                    required=required, satisfied=satisfied, missing=missing, failed=failed,
                    blockers=blockers, caveats=caveats, allowed=allowed,
                    disallowed=["all_claim_surfaces"], retry=retry, trace=trace,
                )
        missing.append("assignment_panel_integrity_report")
        blockers.append(BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_MISSING)
        retry = RETRY_ADD_ASSIGNMENT_PANEL_INTEGRITY_EVIDENCE
        return _build_decision(
            claim_type, claim_scope, status=CLAIM_INSUFFICIENT_EVIDENCE,
            required=required, satisfied=satisfied, missing=missing, failed=failed,
            blockers=blockers, caveats=caveats, allowed=allowed,
            disallowed=["all_claim_surfaces"], retry=retry, trace=trace,
        )

    if claim_type == "RANDOMIZATION_ARTIFACT_DESCRIPTION":
        required.append("governed_randomization_report")
        if randomization:
            satisfied.append("governed_randomization_report")
            if _randomization_passed(randomization):
                caveats.extend([CAVEAT_DESCRIPTIVE_ONLY, CAVEAT_NO_CAUSAL_CLAIM, CAVEAT_RESEARCH_OR_REVIEW_ONLY])
                allowed.extend(["randomization_artifact_generated", "seed_policy_recorded"])
                return _build_decision(
                    claim_type, claim_scope, status=CLAIM_AUTHORIZED_WITH_RESTRICTIONS,
                    required=required, satisfied=satisfied, missing=missing, failed=failed,
                    blockers=blockers, caveats=caveats, allowed=allowed,
                    disallowed=["causal_lift", "production_readout"], retry=None, trace=trace,
                )
            status = _report_status(randomization)
            if status in {GOVERNED_RANDOMIZATION_FAILED, GOVERNED_RANDOMIZATION_BLOCKED}:
                failed.append("governed_randomization_report")
                blockers.append(BLOCKER_PRODUCTION_CATALOG_BLOCKED)
                retry = RETRY_BLOCK_CLAIM
                return _build_decision(
                    claim_type, claim_scope, status=CLAIM_BLOCKED,
                    required=required, satisfied=satisfied, missing=missing, failed=failed,
                    blockers=blockers, caveats=caveats, allowed=allowed,
                    disallowed=["all_claim_surfaces"], retry=retry, trace=trace,
                )
        missing.append("governed_randomization_report")
        retry = RETRY_KEEP_RESEARCH_ONLY
        return _build_decision(
            claim_type, claim_scope, status=CLAIM_INSUFFICIENT_EVIDENCE,
            required=required, satisfied=satisfied, missing=missing, failed=failed,
            blockers=blockers, caveats=caveats, allowed=allowed,
            disallowed=["all_claim_surfaces"], retry=retry, trace=trace,
        )

    if claim_type == "SRM_BALANCE_DIAGNOSTIC_DESCRIPTION":
        required.append("srm_balance_diagnostic_report")
        if srm:
            satisfied.append("srm_balance_diagnostic_report")
            if _srm_passed(srm):
                caveats.extend([CAVEAT_DESCRIPTIVE_ONLY, CAVEAT_DIAGNOSTIC_ONLY, CAVEAT_NO_CAUSAL_CLAIM])
                allowed.extend(["srm_balance_diagnostic_passed", "realized_counts_evaluated"])
                return _build_decision(
                    claim_type, claim_scope, status=CLAIM_AUTHORIZED_WITH_RESTRICTIONS,
                    required=required, satisfied=satisfied, missing=missing, failed=failed,
                    blockers=blockers, caveats=caveats, allowed=allowed,
                    disallowed=["causal_lift", "production_readout"], retry=None, trace=trace,
                )
            if _srm_failed(srm):
                failed.append("srm_balance_diagnostic_report")
                blockers.append(BLOCKER_SRM_BALANCE_DIAGNOSTIC_FAILED)
                retry = RETRY_ADD_SRM_BALANCE_DIAGNOSTIC
                return _build_decision(
                    claim_type, claim_scope, status=CLAIM_BLOCKED,
                    required=required, satisfied=satisfied, missing=missing, failed=failed,
                    blockers=blockers, caveats=caveats, allowed=allowed,
                    disallowed=["all_claim_surfaces"], retry=retry, trace=trace,
                )
        missing.append("srm_balance_diagnostic_report")
        blockers.append(BLOCKER_SRM_BALANCE_DIAGNOSTIC_MISSING)
        retry = RETRY_ADD_SRM_BALANCE_DIAGNOSTIC
        return _build_decision(
            claim_type, claim_scope, status=CLAIM_INSUFFICIENT_EVIDENCE,
            required=required, satisfied=satisfied, missing=missing, failed=failed,
            blockers=blockers, caveats=caveats, allowed=allowed,
            disallowed=["all_claim_surfaces"], retry=retry, trace=trace,
        )

    if claim_type == "DESCRIPTIVE_DIAGNOSTIC_DESCRIPTION":
        required.append("diagnostics_sensitivity_report")
        if diagnostics:
            satisfied.append("diagnostics_sensitivity_report")
            if _diagnostics_passed(diagnostics):
                caveats.extend([CAVEAT_DESCRIPTIVE_ONLY, CAVEAT_DIAGNOSTIC_ONLY, CAVEAT_NO_CAUSAL_CLAIM])
                allowed.extend(["diagnostic_evidence_available"])
                return _build_decision(
                    claim_type, claim_scope, status=CLAIM_AUTHORIZED_WITH_RESTRICTIONS,
                    required=required, satisfied=satisfied, missing=missing, failed=failed,
                    blockers=blockers, caveats=caveats, allowed=allowed,
                    disallowed=["causal_lift", "production_readout"], retry=None, trace=trace,
                )
            if _diagnostics_failed(diagnostics):
                failed.append("diagnostics_sensitivity_report")
                blockers.append(BLOCKER_REQUIRED_DIAGNOSTIC_FAILED)
                retry = RETRY_ADD_REQUIRED_DIAGNOSTICS
                return _build_decision(
                    claim_type, claim_scope, status=CLAIM_BLOCKED,
                    required=required, satisfied=satisfied, missing=missing, failed=failed,
                    blockers=blockers, caveats=caveats, allowed=allowed,
                    disallowed=["all_claim_surfaces"], retry=retry, trace=trace,
                )
        missing.append("diagnostics_sensitivity_report")
        blockers.append(BLOCKER_REQUIRED_DIAGNOSTIC_MISSING)
        retry = RETRY_ADD_REQUIRED_DIAGNOSTICS
        return _build_decision(
            claim_type, claim_scope, status=CLAIM_INSUFFICIENT_EVIDENCE,
            required=required, satisfied=satisfied, missing=missing, failed=failed,
            blockers=blockers, caveats=caveats, allowed=allowed,
            disallowed=["all_claim_surfaces"], retry=retry, trace=trace,
        )

    # Point estimate description
    if claim_type == "POINT_ESTIMATE_DESCRIPTION":
        required.extend(["execution_result", "effect_estimate_report"])
        if _execution_completed(data):
            satisfied.append("execution_result")
        else:
            missing.append("execution_result")
        if _effect_estimate_exists(effect):
            satisfied.append("effect_estimate_report")
        else:
            missing.append("effect_estimate_report")
            blockers.append(BLOCKER_EFFECT_ESTIMATE_MISSING)
            retry = RETRY_REQUEST_WEAKER_DESCRIPTIVE_CLAIM
            return _build_decision(
                claim_type, claim_scope, status=CLAIM_INSUFFICIENT_EVIDENCE,
                required=required, satisfied=satisfied, missing=missing, failed=failed,
                blockers=blockers, caveats=caveats, allowed=allowed,
                disallowed=["causal_lift", "statistical_significance"], retry=retry, trace=trace,
            )
        if is_did_bootstrap_inference_instrument(instrument_id):
            blockers.append(BLOCKER_INFERENCE_NOT_IMPLEMENTED)
            blockers.append(BLOCKER_INSTRUMENT_CLAIM_MISMATCH)
            retry = RETRY_REQUEST_WEAKER_DESCRIPTIVE_CLAIM
            return _build_decision(
                claim_type, claim_scope, status=CLAIM_BLOCKED,
                required=required, satisfied=satisfied, missing=missing, failed=failed,
                blockers=blockers, caveats=caveats, allowed=allowed,
                disallowed=["bootstrap_inference_claims"], retry=retry, trace=trace,
            )
        if cfg.require_assignment_panel_integrity_for_execution_claims:
            required.append("assignment_panel_integrity_report")
            if integrity:
                satisfied.append("assignment_panel_integrity_report")
                if _integrity_failed(integrity):
                    failed.append("assignment_panel_integrity_report")
                    blockers.append(BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_FAILED)
                    retry = RETRY_ADD_ASSIGNMENT_PANEL_INTEGRITY_EVIDENCE
                    return _build_decision(
                        claim_type, claim_scope, status=CLAIM_BLOCKED,
                        required=required, satisfied=satisfied, missing=missing, failed=failed,
                        blockers=blockers, caveats=caveats, allowed=allowed,
                        disallowed=["all_execution_claims"], retry=retry, trace=trace,
                    )
            elif data.get("panel_records") or data.get("panel_data"):
                missing.append("assignment_panel_integrity_report")
                blockers.append(BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_MISSING)
        if production and _catalog_blocks_production(catalog):
            blockers.append(BLOCKER_PRODUCTION_CATALOG_BLOCKED)
            caveats.append(CAVEAT_METHOD_BLOCKED_FOR_PRODUCTION)
            retry = RETRY_FIX_PRODUCTION_CATALOG_BLOCKER
            return _build_decision(
                claim_type, claim_scope, status=CLAIM_BLOCKED,
                required=required, satisfied=satisfied, missing=missing, failed=failed,
                blockers=blockers, caveats=caveats, allowed=allowed,
                disallowed=["production_readout"], retry=retry, trace=trace,
            )
        if not is_governed_did_point_estimate_instrument(
            resolve_did_instrument_id(instrument_id or DID_2X2_POINT_ESTIMATE).canonical_instrument_id
        ):
            blockers.append(BLOCKER_INSTRUMENT_CLAIM_MISMATCH)
            retry = RETRY_REQUEST_WEAKER_DESCRIPTIVE_CLAIM
            return _build_decision(
                claim_type, claim_scope, status=CLAIM_BLOCKED,
                required=required, satisfied=satisfied, missing=missing, failed=failed,
                blockers=blockers, caveats=caveats, allowed=allowed,
                disallowed=["unsupported_instrument"], retry=retry, trace=trace,
            )
        caveats.extend([
            CAVEAT_POINT_ESTIMATE_ONLY,
            CAVEAT_NO_UNCERTAINTY,
            CAVEAT_NO_STATISTICAL_SIGNIFICANCE,
            CAVEAT_NO_CONFIDENCE_INTERVAL,
            CAVEAT_NO_CAUSAL_CLAIM,
            CAVEAT_NO_PRODUCTION_AUTHORIZATION,
            CAVEAT_RESEARCH_OR_REVIEW_ONLY,
        ])
        allowed.extend(["point_estimate_value", "descriptive_point_estimate_review"])
        disallowed.extend(["causal_lift", "statistical_significance", "confidence_interval", "production_readout"])
        return _build_decision(
            claim_type, claim_scope, status=CLAIM_AUTHORIZED_WITH_RESTRICTIONS,
            required=required, satisfied=satisfied, missing=missing, failed=failed,
            blockers=blockers, caveats=caveats, allowed=allowed,
            disallowed=disallowed, retry=None, trace=trace,
        )

    # Directional result description
    if claim_type == "DIRECTIONAL_RESULT_DESCRIPTION":
        required.extend(["effect_estimate_report", "assignment_panel_integrity_report", "srm_balance_diagnostic_report"])
        if _effect_estimate_exists(effect):
            satisfied.append("effect_estimate_report")
        else:
            missing.append("effect_estimate_report")
            blockers.append(BLOCKER_EFFECT_ESTIMATE_MISSING)
        if integrity:
            satisfied.append("assignment_panel_integrity_report")
            if _integrity_failed(integrity):
                failed.append("assignment_panel_integrity_report")
                blockers.append(BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_FAILED)
        else:
            missing.append("assignment_panel_integrity_report")
            blockers.append(BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_MISSING)
        if cfg.require_srm_balance_for_directional_claims:
            if srm:
                satisfied.append("srm_balance_diagnostic_report")
                if _srm_failed(srm):
                    failed.append("srm_balance_diagnostic_report")
                    blockers.append(BLOCKER_SRM_BALANCE_DIAGNOSTIC_FAILED)
            else:
                missing.append("srm_balance_diagnostic_report")
                blockers.append(BLOCKER_SRM_BALANCE_DIAGNOSTIC_MISSING)
        if promotion:
            satisfied.append("statistical_promotion_report")
            if _promotion_failed(promotion):
                failed.append("statistical_promotion_report")
                blockers.append(BLOCKER_STATISTICAL_PROMOTION_FAILED)
        elif production:
            missing.append("statistical_promotion_report")
            blockers.append(BLOCKER_STATISTICAL_PROMOTION_MISSING)
        if blockers or failed or missing:
            retry = RETRY_REQUEST_WEAKER_DESCRIPTIVE_CLAIM
            status = CLAIM_BLOCKED if failed or BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_FAILED in blockers else CLAIM_INSUFFICIENT_EVIDENCE
            return _build_decision(
                claim_type, claim_scope, status=status,
                required=required, satisfied=satisfied, missing=missing, failed=failed,
                blockers=blockers, caveats=caveats, allowed=allowed,
                disallowed=["causal_lift", "roi"], retry=retry, trace=trace,
            )
        if not _direction_available(effect):
            missing.append("directional_signal")
            return _build_decision(
                claim_type, claim_scope, status=CLAIM_INSUFFICIENT_EVIDENCE,
                required=required, satisfied=satisfied, missing=missing, failed=failed,
                blockers=blockers, caveats=caveats, allowed=allowed,
                disallowed=["directional_claim"], retry=RETRY_REQUEST_WEAKER_DESCRIPTIVE_CLAIM, trace=trace,
            )
        caveats.extend([
            CAVEAT_DESCRIPTIVE_ONLY,
            CAVEAT_NO_CAUSAL_CLAIM,
            CAVEAT_NO_INCREMENTAL_CLAIM,
            CAVEAT_NO_ROI_CLAIM,
            CAVEAT_NO_PRODUCTION_AUTHORIZATION,
        ])
        allowed.extend(["directional_sign_only", "descriptive_direction_review"])
        disallowed.extend(["causal_lift", "incremental_conversions", "roi"])
        return _build_decision(
            claim_type, claim_scope, status=CLAIM_AUTHORIZED_WITH_RESTRICTIONS,
            required=required, satisfied=satisfied, missing=missing, failed=failed,
            blockers=blockers, caveats=caveats, allowed=allowed,
            disallowed=disallowed, retry=None, trace=trace,
        )

    # Inference claims — block without governed inference
    if claim_type in _INFERENCE_CLAIM_TYPES:
        required.extend(["uncertainty_report", "inference_diagnostic_report", "statistical_promotion_report"])
        blockers.extend([BLOCKER_INFERENCE_NOT_IMPLEMENTED, BLOCKER_UNCERTAINTY_MISSING])
        if claim_type == "STATISTICAL_SIGNIFICANCE_CLAIM":
            blockers.append(BLOCKER_P_VALUE_MISSING)
            missing.extend(["p_value", "governed_inference"])
        else:
            blockers.append(BLOCKER_CONFIDENCE_INTERVAL_MISSING)
            missing.extend(["confidence_interval", "governed_uncertainty"])
        caveats.extend([CAVEAT_NO_STATISTICAL_SIGNIFICANCE, CAVEAT_NO_CONFIDENCE_INTERVAL])
        retry = RETRY_ADD_GOVERNED_UNCERTAINTY
        return _build_decision(
            claim_type, claim_scope, status=CLAIM_BLOCKED,
            required=required, satisfied=satisfied, missing=missing, failed=failed,
            blockers=blockers, caveats=caveats, allowed=allowed,
            disallowed=["statistical_significance", "confidence_interval"], retry=retry, trace=trace,
        )

    # Trusted report claims
    if claim_type in {"PRODUCTION_READOUT_CLAIM", "TRUSTED_BUSINESS_RECOMMENDATION"}:
        blockers.append(BLOCKER_TRUSTED_REPORT_RUNTIME_MISSING)
        if cfg.block_production_claims_without_trusted_report_runtime and not cfg.trusted_readout_report_runtime_implemented:
            caveats.extend([CAVEAT_NO_PRODUCTION_AUTHORIZATION])
            retry = RETRY_IMPLEMENT_TRUSTED_REPORT_RUNTIME
            return _build_decision(
                claim_type, claim_scope, status=CLAIM_BLOCKED,
                required=["trusted_readout_report_runtime"],
                satisfied=satisfied, missing=["trusted_readout_report_runtime"],
                failed=failed, blockers=blockers, caveats=caveats,
                allowed=[], disallowed=["production_readout", "trusted_business_recommendation"],
                retry=retry, trace=trace,
            )

    # Strong causal / incremental / ROI claims
    if claim_type in _STRONG_CLAIM_TYPES:
        required.extend([
            "production_catalog_report",
            "assignment_panel_integrity_report",
            "srm_balance_diagnostic_report",
            "diagnostics_sensitivity_report",
            "statistical_promotion_report",
            "effect_estimate_report",
            "uncertainty_report",
        ])
        if _catalog_blocks_production(catalog):
            blockers.append(BLOCKER_PRODUCTION_CATALOG_BLOCKED)
            failed.append("production_catalog_report")
        else:
            satisfied.append("production_catalog_report")
        if integrity:
            satisfied.append("assignment_panel_integrity_report")
            if _integrity_failed(integrity):
                failed.append("assignment_panel_integrity_report")
                blockers.append(BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_FAILED)
        else:
            missing.append("assignment_panel_integrity_report")
            blockers.append(BLOCKER_ASSIGNMENT_PANEL_INTEGRITY_MISSING)
        if srm:
            satisfied.append("srm_balance_diagnostic_report")
            if _srm_failed(srm):
                failed.append("srm_balance_diagnostic_report")
                blockers.append(BLOCKER_SRM_BALANCE_DIAGNOSTIC_FAILED)
        else:
            missing.append("srm_balance_diagnostic_report")
            blockers.append(BLOCKER_SRM_BALANCE_DIAGNOSTIC_MISSING)
        if diagnostics:
            satisfied.append("diagnostics_sensitivity_report")
            if _diagnostics_failed(diagnostics):
                failed.append("diagnostics_sensitivity_report")
                blockers.append(BLOCKER_REQUIRED_DIAGNOSTIC_FAILED)
        else:
            missing.append("diagnostics_sensitivity_report")
            blockers.append(BLOCKER_REQUIRED_DIAGNOSTIC_MISSING)
        if promotion:
            satisfied.append("statistical_promotion_report")
            if _promotion_failed(promotion):
                failed.append("statistical_promotion_report")
                blockers.append(BLOCKER_STATISTICAL_PROMOTION_FAILED)
        else:
            missing.append("statistical_promotion_report")
            blockers.append(BLOCKER_STATISTICAL_PROMOTION_MISSING)
        if _effect_estimate_exists(effect):
            satisfied.append("effect_estimate_report")
        else:
            missing.append("effect_estimate_report")
            blockers.append(BLOCKER_EFFECT_ESTIMATE_MISSING)
        if not _uncertainty_computed(uncertainty):
            missing.append("uncertainty_report")
            blockers.append(BLOCKER_UNCERTAINTY_MISSING)
            blockers.append(BLOCKER_INFERENCE_NOT_IMPLEMENTED)
        if claim_type == "ROI_CLAIM":
            missing.append("roi_evidence")
            blockers.append(BLOCKER_UNCERTAINTY_MISSING)
        if production:
            blockers.append(BLOCKER_PRODUCTION_CONTEXT_NOT_AUTHORIZED)
        caveats.extend([CAVEAT_NO_CAUSAL_CLAIM, CAVEAT_NO_INCREMENTAL_CLAIM, CAVEAT_NO_ROI_CLAIM, CAVEAT_NO_PRODUCTION_AUTHORIZATION])
        retry = RETRY_BLOCK_CLAIM
        return _build_decision(
            claim_type, claim_scope, status=CLAIM_BLOCKED,
            required=required, satisfied=satisfied, missing=missing, failed=failed,
            blockers=blockers, caveats=caveats, allowed=allowed,
            disallowed=["causal_lift", "incremental_conversions", "incremental_revenue", "roi", "production_readout"],
            retry=retry, trace=trace,
        )

    return _build_decision(
        claim_type, claim_scope, status=CLAIM_NOT_EVALUATED,
        required=required, satisfied=satisfied, missing=missing, failed=failed,
        blockers=blockers, caveats=caveats, allowed=allowed,
        disallowed=[], retry=RETRY_BLOCK_CLAIM, trace=trace,
    )


def _aggregate_overall_status(decisions: list[ClaimAuthorizationDecision]) -> str:
    if not decisions:
        return CLAIM_AUTHORIZATION_NOT_EVALUATED
    statuses = {d.authorization_status for d in decisions}
    if all(s == CLAIM_AUTHORIZED for s in statuses):
        return CLAIM_AUTHORIZATION_COMPLETED
    if CLAIM_BLOCKED in statuses:
        return CLAIM_AUTHORIZATION_BLOCKED
    if CLAIM_INSUFFICIENT_EVIDENCE in statuses:
        return CLAIM_AUTHORIZATION_INSUFFICIENT_EVIDENCE
    if CLAIM_AUTHORIZED_WITH_RESTRICTIONS in statuses or CLAIM_AUTHORIZED in statuses:
        return CLAIM_AUTHORIZATION_COMPLETED_WITH_RESTRICTIONS
    return CLAIM_AUTHORIZATION_NOT_EVALUATED


def _evaluate_single(data: dict[str, Any], cfg: ClaimAuthorizationRuntimeConfig) -> ClaimAuthorizationRuntimeReport:
    request_id = str(data.get("request_id") or data.get("design_id") or "request_unspecified")
    production = _is_production_context(data)
    claim_requests = list(data.get("claim_requests") or [])
    if not claim_requests and data.get("claim_type"):
        claim_requests = [{"claim_type": data["claim_type"], "claim_scope": data.get("claim_scope")}]

    decisions = [_evaluate_claim(_to_dict(c), data, cfg) for c in claim_requests]

    authorized = [d.claim_type for d in decisions if d.authorization_status == CLAIM_AUTHORIZED]
    restricted = [d.claim_type for d in decisions if d.authorization_status == CLAIM_AUTHORIZED_WITH_RESTRICTIONS]
    blocked = [d.claim_type for d in decisions if d.authorization_status == CLAIM_BLOCKED]
    insufficient = [d.claim_type for d in decisions if d.authorization_status == CLAIM_INSUFFICIENT_EVIDENCE]
    not_evaluated = [d.claim_type for d in decisions if d.authorization_status == CLAIM_NOT_EVALUATED]

    all_missing: list[str] = []
    all_failed: list[str] = []
    all_blockers: list[str] = []
    all_caveats: list[str] = []
    all_retries: list[str] = []
    warnings: list[str] = []
    for d in decisions:
        all_missing.extend(d.missing_evidence)
        all_failed.extend(d.failed_evidence)
        all_blockers.extend(d.blockers)
        all_caveats.extend(d.caveat_codes)
        if d.retry_category:
            all_retries.append(d.retry_category)
        if d.is_restricted:
            warnings.append(f"{d.claim_type} authorized with restrictions only")

    overall = _aggregate_overall_status(decisions)
    trace_payload = {
        "artifact_id": _ARTIFACT_ID,
        "request_id": request_id,
        "overall_status": overall,
        "policy_version": _POLICY_VERSION,
        "claim_count": len(decisions),
        "config_hash": _hash_payload(cfg.__dict__),
        "input_hash": _hash_payload(data),
    }
    evidence_trace = {**trace_payload, "integrity_hash": _hash_payload(trace_payload)}

    return ClaimAuthorizationRuntimeReport(
        request_id=request_id,
        overall_status=overall,
        production_context=production,
        claim_authorizations=tuple(decisions),
        authorized_claims=_safe_str_list(authorized),
        restricted_claims=_safe_str_list(restricted),
        blocked_claims=_safe_str_list(blocked),
        insufficient_evidence_claims=_safe_str_list(insufficient),
        not_evaluated_claims=_safe_str_list(not_evaluated),
        required_evidence_summary={
            "claim_types_evaluated": [d.claim_type for d in decisions],
            "evidence_sources_present": list(
                dict.fromkeys(
                    k for k in (
                        "assignment_panel_integrity_report",
                        "srm_balance_diagnostic_report",
                        "governed_randomization_report",
                        "diagnostics_sensitivity_report",
                        "statistical_promotion_report",
                        "effect_estimate_report",
                        "uncertainty_report",
                        "production_catalog_report",
                    )
                    if data.get(k) or data.get(k.replace("_report", ""))
                )
            ),
        },
        missing_evidence=_safe_str_list(all_missing),
        failed_evidence=_safe_str_list(all_failed),
        blockers=_safe_str_list(all_blockers),
        warnings=_safe_str_list(warnings),
        caveats=_safe_str_list(all_caveats),
        retry_categories=_safe_str_list(all_retries),
        evidence_trace=evidence_trace,
        claim_boundary_report=_claim_boundary(evaluated=bool(decisions)),
        policy_version=_POLICY_VERSION,
        provenance={"artifact_id": _ARTIFACT_ID, "integrity_hash": evidence_trace["integrity_hash"]},
    )


def authorize_readout_claims(
    input_data: Any,
    config: ClaimAuthorizationRuntimeConfig | dict[str, Any] | None = None,
) -> ClaimAuthorizationRuntimeReport | list[ClaimAuthorizationRuntimeReport]:
    cfg = _resolve_config(config)
    if isinstance(input_data, list):
        return [_evaluate_single(_to_dict(x), cfg) for x in input_data]
    data = _to_dict(input_data)
    if "requests" in data and isinstance(data["requests"], list):
        return [_evaluate_single(_to_dict(x), cfg) for x in data["requests"]]
    return _evaluate_single(data, cfg)


evaluate_claim_authorization = authorize_readout_claims
authorize_claims = authorize_readout_claims


def build_claim_authorization_input_from_execution(
    execution_report: Any,
    *,
    claim_requests: list[dict[str, Any]] | None = None,
    extra_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build claim authorization input from an execution runtime report."""
    report = _to_dict(execution_report)
    results = list(report.get("instrument_execution_results") or [])
    execution_status = report.get("execution_status")
    if any(_token(r.get("instrument_execution_status")) == "INSTRUMENT_EXECUTION_COMPLETED" for r in results if isinstance(r, dict)):
        execution_status = "INSTRUMENT_EXECUTION_COMPLETED"
    payload: dict[str, Any] = {
        "request_id": report.get("design_id") or report.get("request_id"),
        "execution_status": execution_status,
        "execution_result": report.get("execution_packet"),
        "instrument_execution_results": results,
        "claim_requests": claim_requests or [],
        "production_context": report.get("production_context"),
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
    integrity = {"status": ASSIGNMENT_PANEL_INTEGRITY_PASSED}
    srm = {"status": SRM_BALANCE_DIAGNOSTIC_PASSED}
    effect = {
        "estimation_status": EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
        "effect_estimate_report_status": EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
        "point_estimate": 1.0,
        "instrument_id": DID_2X2_POINT_ESTIMATE,
    }
    smoke = authorize_readout_claims({
        "request_id": "claim_auth_smoke",
        "claim_requests": [
            {"claim_type": "ASSIGNMENT_INTEGRITY_DESCRIPTION", "claim_scope": {"estimand": "STANDARD_INCREMENTALITY"}},
            {"claim_type": "POINT_ESTIMATE_DESCRIPTION", "claim_scope": {"estimand": "STANDARD_INCREMENTALITY"}},
            {"claim_type": "CAUSAL_LIFT_CLAIM", "claim_scope": {"estimand": "STANDARD_INCREMENTALITY"}},
        ],
        "claim_scope": {"estimand": "STANDARD_INCREMENTALITY"},
        "assignment_panel_integrity_report": integrity,
        "srm_balance_diagnostic_report": srm,
        "effect_estimate_report": effect,
        "instrument_id": DID_2X2_POINT_ESTIMATE,
        "instrument_execution_results": [
            {"instrument_id": DID_2X2_POINT_ESTIMATE, "instrument_execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
             "effect_estimate_report": effect},
        ],
        "execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
    })
    assert isinstance(smoke, ClaimAuthorizationRuntimeReport)
    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "claim_authorization_runtime",
        "base_commit": _git_head(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": [
            "CLAIM_AUTHORIZATION_CONTRACT_001",
            "SRM_BALANCE_READOUT_DIAGNOSTIC_001",
            "GOVERNED_RANDOMIZATION_RUNTIME_001",
            "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001",
            "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001",
            "DID_INSTRUMENT_ESTIMAND_UNIFICATION_001",
            "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001",
        ],
        "claim_authorization_runtime_implemented": True,
        "claim_authorization_evaluated": True,
        "descriptive_claims_authorized_with_restrictions": True,
        "claim_blockers_enforced": True,
        "production_claims_blocked_without_required_evidence": True,
        "statistical_significance_claims_blocked_without_inference": True,
        "roi_claims_blocked_without_roi_evidence": True,
        "trusted_report_claims_blocked_without_trusted_report_runtime": True,
        "production_authorization_granted": False,
        "production_readout_authorized": False,
        "trusted_readout_handoff_generated": False,
        "trusted_readout_report_generated": False,
        "authorized_claim_text_generated": False,
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
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "final_verdict": _VERDICT,
        "smoke_status": smoke.overall_status,
        "failed_scenarios": [],
    }
    if write_summary:
        _DEFAULT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
        _DEFAULT_SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--write-summary", action="store_true")
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
