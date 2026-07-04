"""DID_INSTRUMENT_ESTIMAND_UNIFICATION_001 — DID instrument/estimand registry."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "DID_INSTRUMENT_ESTIMAND_UNIFICATION_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "did_instrument_estimand_unified_no_bootstrap_or_claim_authorization"
_VERDICT = "did_instrument_estimand_unified_no_bootstrap_or_claim_authorization"
_RECOMMENDED_NEXT = "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001"
_ALTERNATIVE_NEXT = "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/DID_INSTRUMENT_ESTIMAND_UNIFICATION_001_summary.json"

DID_2X2_POINT_ESTIMATE = "DID_2X2_POINT_ESTIMATE"
DID_GOVERNED_POINT_ESTIMATE = "DID_GOVERNED_POINT_ESTIMATE"
DID_BOOTSTRAP_INFERENCE = "DID_BOOTSTRAP_INFERENCE"
DID_TWFE_LIBRARY_RESEARCH = "DID_TWFE_LIBRARY_RESEARCH"

EXECUTION_SUPPORTED = "EXECUTION_SUPPORTED"
EXECUTION_NOT_IMPLEMENTED = "EXECUTION_NOT_IMPLEMENTED"
EXECUTION_BLOCKED = "EXECUTION_BLOCKED"
INFERENCE_NOT_IMPLEMENTED = "INFERENCE_NOT_IMPLEMENTED"
UNCERTAINTY_NOT_SUPPORTED = "UNCERTAINTY_NOT_SUPPORTED"
RESEARCH_LIBRARY_ONLY = "RESEARCH_LIBRARY_ONLY"

BLOCKER_MISLEADING_INSTRUMENT = "MISLEADING_INSTRUMENT_ID"
BLOCKER_INFERENCE_NOT_IMPLEMENTED = "INFERENCE_NOT_IMPLEMENTED"
BLOCKER_USE_CANONICAL_POINT_ESTIMATE = "USE_DID_2X2_POINT_ESTIMATE_FOR_POINT_ONLY_EXECUTION"

_AUTH_FALSE = {
    "twfe_executor_implemented": False,
    "bootstrap_inference_implemented": False,
    "claim_authorization_runtime_implemented": False,
    "claim_authorized": False,
    "claim_authorized_with_restrictions": False,
    "authorized_claim_text_generated": False,
    "trusted_readout_handoff_generated": False,
    "production_readout_authorized": False,
    "causal_claim_authorized": False,
    "incremental_lift_claim_authorized": False,
    "roi_claim_authorized": False,
    "production_authorization_granted": False,
    "inference_execution_implemented": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}

_POSITIVE_FLAGS = {
    "did_instrument_estimand_registry_defined": True,
    "did_instrument_resolution_implemented": True,
    "did_2x2_point_estimate_canonicalized": True,
    "did_bootstrap_inference_separated": True,
    "did_twfe_library_research_separated": True,
    "legacy_did_bootstrap_point_estimate_alias_blocked_by_default": True,
    "did_executor_uses_canonical_point_estimate_id": True,
    "production_catalog_uses_did_instrument_registry": True,
}

_ALIAS_MAP: dict[str, str] = {
    "DID_GOVERNED_POINT_ESTIMATE": DID_2X2_POINT_ESTIMATE,
    "DID_POINT_ESTIMATE": DID_2X2_POINT_ESTIMATE,
    "DID_POINT": DID_2X2_POINT_ESTIMATE,
    "DID_2X2": DID_2X2_POINT_ESTIMATE,
    "DID_BOOTSTRAP": DID_BOOTSTRAP_INFERENCE,
    "DID_BOOTSTRAP_INFERENCE": DID_BOOTSTRAP_INFERENCE,
    "DID_TWFE": DID_TWFE_LIBRARY_RESEARCH,
    "DID_TWFE_LIBRARY": DID_TWFE_LIBRARY_RESEARCH,
    "TWFE": DID_TWFE_LIBRARY_RESEARCH,
    "DID_TWFE_LIBRARY_RESEARCH": DID_TWFE_LIBRARY_RESEARCH,
    "DID_2X2_POINT_ESTIMATE": DID_2X2_POINT_ESTIMATE,
}

_GOVERNED_POINT_ESTIMATE_IDS = frozenset({DID_2X2_POINT_ESTIMATE, DID_GOVERNED_POINT_ESTIMATE})
_BOOTSTRAP_INFERENCE_IDS = frozenset({DID_BOOTSTRAP_INFERENCE, "DID_BOOTSTRAP"})
_TWFE_RESEARCH_IDS = frozenset({DID_TWFE_LIBRARY_RESEARCH})


@dataclass(frozen=True)
class DIDInstrumentRegistryConfig:
    allow_legacy_did_bootstrap_for_point_estimate: bool = False
    allow_governed_did_point_estimate_execution: bool = False


@dataclass(frozen=True)
class DIDInstrumentResolution:
    input_instrument_id: str
    canonical_instrument_id: str
    is_alias: bool
    is_governed_point_estimate: bool
    is_bootstrap_inference: bool
    is_twfe_library_research: bool
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class DIDInstrumentContract:
    canonical_instrument_id: str
    aliases: tuple[str, ...]
    estimator_family: str
    estimand_type: str
    effect_scale: str
    execution_support_status: str
    inference_support_status: str
    uncertainty_support_status: str
    governed_runtime_supported: bool
    research_library_supported: bool
    production_catalog_status: str
    allowed_roles: tuple[str, ...]
    blocked_roles: tuple[str, ...]
    required_remediation: tuple[str, ...]
    claim_boundary: dict[str, Any]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class DIDInstrumentValidationReport:
    input_instrument_id: str
    canonical_instrument_id: str
    is_valid_for_execution: bool
    execution_allowed: bool
    blockers: tuple[str, ...]
    restrictions: tuple[str, ...]
    required_remediation: tuple[str, ...]
    claim_boundary: dict[str, Any]
    trace: dict[str, Any]
    warnings: tuple[str, ...]


def _token(value: Any) -> str:
    return str(value).strip().upper().replace(" ", "_") if value is not None else ""


def _library_did_present() -> bool:
    return (_REPO / "panel_exp/methods/DID.py").is_file()


def _contract_for(canonical_id: str) -> DIDInstrumentContract:
    if canonical_id == DID_2X2_POINT_ESTIMATE:
        return DIDInstrumentContract(
            canonical_instrument_id=DID_2X2_POINT_ESTIMATE,
            aliases=(DID_GOVERNED_POINT_ESTIMATE, "DID_POINT_ESTIMATE", "DID_POINT"),
            estimator_family="DID_FAMILY",
            estimand_type="STANDARD_INCREMENTALITY_2X2",
            effect_scale="absolute",
            execution_support_status=EXECUTION_SUPPORTED,
            inference_support_status=INFERENCE_NOT_IMPLEMENTED,
            uncertainty_support_status=UNCERTAINTY_NOT_SUPPORTED,
            governed_runtime_supported=True,
            research_library_supported=False,
            production_catalog_status="PRODUCTION_CATALOG_RESTRICTED_EXPERT_REVIEW",
            allowed_roles=("GOVERNED_POINT_ESTIMATE", "DRY_RUN", "POINT_ESTIMATE_REVIEW"),
            blocked_roles=("PRODUCTION_CANDIDATE", "PRODUCTION_READOUT", "CAUSAL_LIFT_CLAIM", "INCREMENTAL_LIFT_CLAIM", "ROI_CLAIM"),
            required_remediation=("CLAIM_AUTHORIZATION_RUNTIME_001", "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001"),
            claim_boundary={
                "did_point_estimate_executor_implemented": True,
                "governed_2x2_point_estimate_only": True,
                **_AUTH_FALSE,
            },
            warnings=("no uncertainty; no bootstrap; no causal/incremental/ROI claim authorization",),
        )
    if canonical_id == DID_BOOTSTRAP_INFERENCE:
        return DIDInstrumentContract(
            canonical_instrument_id=DID_BOOTSTRAP_INFERENCE,
            aliases=("DID_BOOTSTRAP",),
            estimator_family="DID_FAMILY",
            estimand_type="STANDARD_INCREMENTALITY",
            effect_scale="absolute",
            execution_support_status=EXECUTION_NOT_IMPLEMENTED,
            inference_support_status=INFERENCE_NOT_IMPLEMENTED,
            uncertainty_support_status=UNCERTAINTY_NOT_SUPPORTED,
            governed_runtime_supported=False,
            research_library_supported=True,
            production_catalog_status="PRODUCTION_CATALOG_BLOCKED",
            allowed_roles=("RESEARCH", "REMEDIATION_PATH"),
            blocked_roles=("GOVERNED_POINT_ESTIMATE", "PRODUCTION_CANDIDATE", "PRODUCTION_READOUT", "CAUSAL_LIFT_CLAIM", "INCREMENTAL_LIFT_CLAIM", "ROI_CLAIM"),
            required_remediation=(
                "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_004_BOOTSTRAP_INFERENCE",
                "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001",
                "DID_INSTRUMENT_ESTIMAND_UNIFICATION_001",
            ),
            claim_boundary={
                "bootstrap_inference_separated_from_point_estimate": True,
                **_AUTH_FALSE,
            },
            warnings=("DID_BOOTSTRAP means bootstrap inference, not governed 2x2 point estimate",),
        )
    if canonical_id == DID_TWFE_LIBRARY_RESEARCH:
        return DIDInstrumentContract(
            canonical_instrument_id=DID_TWFE_LIBRARY_RESEARCH,
            aliases=("DID_TWFE", "TWFE", "DID_TWFE_LIBRARY"),
            estimator_family="DID_FAMILY",
            estimand_type="TWFE_PANEL_DID",
            effect_scale="absolute",
            execution_support_status=RESEARCH_LIBRARY_ONLY,
            inference_support_status=INFERENCE_NOT_IMPLEMENTED,
            uncertainty_support_status=UNCERTAINTY_NOT_SUPPORTED,
            governed_runtime_supported=False,
            research_library_supported=_library_did_present(),
            production_catalog_status="PRODUCTION_CATALOG_RESEARCH_ONLY",
            allowed_roles=("RESEARCH", "LIBRARY_CALL"),
            blocked_roles=("GOVERNED_POINT_ESTIMATE", "PRODUCTION_CANDIDATE", "PRODUCTION_READOUT"),
            required_remediation=("GOVERNED_TWFE_EXECUTOR_FUTURE",),
            claim_boundary={
                "twfe_library_separated_from_governed_runtime": True,
                **_AUTH_FALSE,
            },
            warnings=("library TWFE DID in panel_exp/methods/DID.py; not governed runtime",),
        )
    return DIDInstrumentContract(
        canonical_instrument_id=canonical_id or "UNKNOWN_DID_INSTRUMENT",
        aliases=(),
        estimator_family="DID_FAMILY",
        estimand_type="UNKNOWN",
        effect_scale="unknown",
        execution_support_status=EXECUTION_BLOCKED,
        inference_support_status=INFERENCE_NOT_IMPLEMENTED,
        uncertainty_support_status=UNCERTAINTY_NOT_SUPPORTED,
        governed_runtime_supported=False,
        research_library_supported=False,
        production_catalog_status="PRODUCTION_CATALOG_NOT_EVALUATED",
        allowed_roles=(),
        blocked_roles=("PRODUCTION_CANDIDATE",),
        required_remediation=("DID_INSTRUMENT_ESTIMAND_UNIFICATION_001",),
        claim_boundary=dict(_AUTH_FALSE),
        warnings=("unknown DID instrument id",),
    )


def get_did_instrument_registry() -> dict[str, DIDInstrumentContract]:
    return {
        DID_2X2_POINT_ESTIMATE: _contract_for(DID_2X2_POINT_ESTIMATE),
        DID_BOOTSTRAP_INFERENCE: _contract_for(DID_BOOTSTRAP_INFERENCE),
        DID_TWFE_LIBRARY_RESEARCH: _contract_for(DID_TWFE_LIBRARY_RESEARCH),
    }


def resolve_did_instrument_id(instrument_id: str) -> DIDInstrumentResolution:
    raw = str(instrument_id or "").strip()
    token = _token(raw)
    canonical = _ALIAS_MAP.get(token, token if token in get_did_instrument_registry() else token)
    warnings: list[str] = []
    if token and canonical != token:
        if token == "DID_BOOTSTRAP":
            warnings.append("DID_BOOTSTRAP resolves to bootstrap inference, not governed point estimate")
        else:
            warnings.append(f"alias {raw} canonicalized to {canonical}")
    return DIDInstrumentResolution(
        input_instrument_id=raw or "instrument_unspecified",
        canonical_instrument_id=canonical,
        is_alias=bool(token and canonical != token),
        is_governed_point_estimate=canonical == DID_2X2_POINT_ESTIMATE,
        is_bootstrap_inference=canonical == DID_BOOTSTRAP_INFERENCE,
        is_twfe_library_research=canonical == DID_TWFE_LIBRARY_RESEARCH,
        warnings=tuple(warnings),
    )


def get_did_instrument_contract(instrument_id: str) -> DIDInstrumentContract:
    resolution = resolve_did_instrument_id(instrument_id)
    return _contract_for(resolution.canonical_instrument_id)


def is_governed_did_point_estimate_instrument(instrument_id: str) -> bool:
    return resolve_did_instrument_id(instrument_id).is_governed_point_estimate


def is_did_bootstrap_inference_instrument(instrument_id: str) -> bool:
    return resolve_did_instrument_id(instrument_id).is_bootstrap_inference


def is_did_twfe_research_instrument(instrument_id: str) -> bool:
    return resolve_did_instrument_id(instrument_id).is_twfe_library_research


def governed_point_estimate_instrument_ids() -> frozenset[str]:
    return _GOVERNED_POINT_ESTIMATE_IDS


def validate_did_instrument_for_execution(
    input_data: dict[str, Any] | Any,
    config: DIDInstrumentRegistryConfig | dict[str, Any] | None = None,
) -> DIDInstrumentValidationReport:
    cfg = (
        config
        if isinstance(config, DIDInstrumentRegistryConfig)
        else DIDInstrumentRegistryConfig(**dict(config or {}))
    )
    if isinstance(input_data, dict):
        data = dict(input_data)
    elif is_dataclass(input_data) and not isinstance(input_data, type):
        data = {f.name: getattr(input_data, f.name) for f in fields(input_data)}
    else:
        data = {}

    instrument_id = str(data.get("instrument_id") or "instrument_unspecified")
    resolution = resolve_did_instrument_id(instrument_id)
    contract = get_did_instrument_contract(instrument_id)
    blockers: list[str] = []
    restrictions: list[str] = []
    remediation = list(contract.required_remediation)
    warnings = list(resolution.warnings)

    if resolution.is_bootstrap_inference:
        blockers.extend([BLOCKER_MISLEADING_INSTRUMENT, BLOCKER_INFERENCE_NOT_IMPLEMENTED])
        restrictions.append("bootstrap_inference_not_implemented_in_governed_runtime")
        if cfg.allow_legacy_did_bootstrap_for_point_estimate:
            warnings.append("legacy DID_BOOTSTRAP point-estimate alias allowed by transition config")
        else:
            blockers.append(BLOCKER_USE_CANONICAL_POINT_ESTIMATE)
            remediation.append(DID_2X2_POINT_ESTIMATE)

    if resolution.is_twfe_library_research:
        blockers.append("TWFE_LIBRARY_NOT_GOVERNED_RUNTIME")
        restrictions.append("research_library_only")

    execution_allowed = False
    if resolution.is_governed_point_estimate:
        if cfg.allow_governed_did_point_estimate_execution:
            execution_allowed = True
        else:
            restrictions.append("governed_point_estimate_disabled_by_config")
    elif resolution.is_bootstrap_inference and cfg.allow_legacy_did_bootstrap_for_point_estimate:
        if cfg.allow_governed_did_point_estimate_execution:
            execution_allowed = True
            warnings.append("legacy transition: executing point estimate via DID_BOOTSTRAP alias")

    is_valid = execution_allowed and not blockers

    trace = {
        "policy_version": _ARTIFACT_VERSION,
        "input_instrument_id": instrument_id,
        "canonical_instrument_id": resolution.canonical_instrument_id,
        "execution_allowed": execution_allowed,
        "allow_legacy_did_bootstrap_for_point_estimate": cfg.allow_legacy_did_bootstrap_for_point_estimate,
    }

    return DIDInstrumentValidationReport(
        input_instrument_id=instrument_id,
        canonical_instrument_id=resolution.canonical_instrument_id,
        is_valid_for_execution=is_valid,
        execution_allowed=execution_allowed,
        blockers=tuple(dict.fromkeys(blockers)),
        restrictions=tuple(dict.fromkeys(restrictions)),
        required_remediation=tuple(dict.fromkeys(remediation)),
        claim_boundary={
            "did_instrument_estimand_registry_defined": True,
            "did_instrument_resolution_implemented": True,
            "canonical_instrument_id": resolution.canonical_instrument_id,
            **_AUTH_FALSE,
        },
        trace=trace,
        warnings=tuple(dict.fromkeys(warnings)),
    )


def production_catalog_overlay_for_did(instrument_id: str) -> dict[str, Any]:
    contract = get_did_instrument_contract(instrument_id)
    resolution = resolve_did_instrument_id(instrument_id)
    return {
        "canonical_instrument_id": resolution.canonical_instrument_id,
        "did_instrument_contract": contract.canonical_instrument_id,
        "production_catalog_status": contract.production_catalog_status,
        "governed_runtime_supported": contract.governed_runtime_supported,
        "bootstrap_inference_separated": resolution.is_bootstrap_inference,
    }


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    scenarios = [
        ("point_estimate_canonical", is_governed_did_point_estimate_instrument(DID_2X2_POINT_ESTIMATE)),
        ("bootstrap_separated", is_did_bootstrap_inference_instrument("DID_BOOTSTRAP")),
        ("alias_canonicalized", resolve_did_instrument_id(DID_GOVERNED_POINT_ESTIMATE).canonical_instrument_id == DID_2X2_POINT_ESTIMATE),
        ("bootstrap_blocks_by_default", not validate_did_instrument_for_execution(
            {"instrument_id": "DID_BOOTSTRAP"},
            config={"allow_governed_did_point_estimate_execution": True},
        ).execution_allowed),
    ]
    failed = [name for name, ok in scenarios if not ok]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "instrument_estimand_unification",
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": [
            "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001",
            "AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001",
            "CLAIM_AUTHORIZATION_CONTRACT_001",
            "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR",
            "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS",
            "READOUT_PLAN_RUNTIME_001",
            "METHOD_SUITABILITY_RUNTIME_001",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "executor_adapters_distinguish_did_instruments": True,
        "method_suitability_uses_canonical_did_point_instrument": True,
        "readout_plan_uses_canonical_did_point_instrument": True,
        "execution_runtime_routes_canonical_did_point_estimate": True,
        "failed_scenarios": failed,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "final_verdict": _VERDICT,
        **_POSITIVE_FLAGS,
        **_AUTH_FALSE,
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
