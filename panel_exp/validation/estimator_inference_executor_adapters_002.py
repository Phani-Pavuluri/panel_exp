"""ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002 governed executor adapter registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from panel_exp.validation.did_instrument_estimand_registry_001 import (
    DID_2X2_POINT_ESTIMATE,
    DID_BOOTSTRAP_INFERENCE,
    DID_TWFE_LIBRARY_RESEARCH,
    is_governed_did_point_estimate_instrument,
    resolve_did_instrument_id,
)
from panel_exp.validation.production_catalog_blocklist_001 import (
    evaluate_production_catalog_status,
    production_catalog_executor_metadata,
)

EXECUTOR_AVAILABLE_FOR_DRY_RUN = "EXECUTOR_AVAILABLE_FOR_DRY_RUN"
EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION = "EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION"
EXECUTOR_NOT_IMPLEMENTED = "EXECUTOR_NOT_IMPLEMENTED"
EXECUTOR_BLOCKED_BY_GOVERNANCE = "EXECUTOR_BLOCKED_BY_GOVERNANCE"
EXECUTOR_BLOCKED_BY_INSTRUMENT_STATUS = "EXECUTOR_BLOCKED_BY_INSTRUMENT_STATUS"
EXECUTOR_BLOCKED_BY_DATA_CONTRACT = "EXECUTOR_BLOCKED_BY_DATA_CONTRACT"
EXECUTOR_BLOCKED_BY_ASSIGNMENT_ARTIFACT = "EXECUTOR_BLOCKED_BY_ASSIGNMENT_ARTIFACT"
EXECUTOR_BLOCKED_BY_ESTIMAND = "EXECUTOR_BLOCKED_BY_ESTIMAND"
EXECUTOR_BLOCKED_BY_UNCERTAINTY_SEMANTICS = "EXECUTOR_BLOCKED_BY_UNCERTAINTY_SEMANTICS"
EXECUTOR_BLOCKED_BY_UNSUPPORTED_INFERENCE = "EXECUTOR_BLOCKED_BY_UNSUPPORTED_INFERENCE"
EXECUTOR_BLOCKED_BY_UNSUPPORTED_ESTIMATOR = "EXECUTOR_BLOCKED_BY_UNSUPPORTED_ESTIMATOR"
EXECUTOR_NOT_EVALUATED = "EXECUTOR_NOT_EVALUATED"

KNOWN_INSTRUMENT_IDS = (
    "DID_2X2_POINT_ESTIMATE",
    "DID_BOOTSTRAP",
    "DID_BOOTSTRAP_INFERENCE",
    "DID_TWFE_LIBRARY_RESEARCH",
    "SCM_PLACEBO",
    "SCM_UNIT_JACKKNIFE",
    "TBR_RIDGE_BRB",
    "TBR_RIDGE_KFOLD",
    "TBR_RIDGE_PLACEBO",
    "AUGSYNTH_JACKKNIFE",
    "MATCHED_PAIR_RANDOMIZATION",
    "AB_STANDARD_INFERENCE",
)


@dataclass(frozen=True)
class GovernedExecutorAdapterSpec:
    instrument_id: str
    estimator_family: str
    inference_family: str
    adapter_name: str
    adapter_version: str
    governance_status: str
    supports_dry_run: bool
    supports_execution: bool
    required_input_fields: tuple[str, ...]
    required_assignment_fields: tuple[str, ...]
    required_estimand_fields: tuple[str, ...]
    required_uncertainty_fields: tuple[str, ...]
    supports_bootstrap_inference: bool = False
    supports_confidence_interval: bool = False
    supports_p_value: bool = False
    blocked_reason_if_not_supported: str | None = None
    notes: str = ""


@dataclass(frozen=True)
class GovernedExecutorRegistry:
    artifact_id: str
    specs: dict[str, GovernedExecutorAdapterSpec]


@dataclass(frozen=True)
class GovernedExecutorTrace:
    instrument_id: str
    adapter_name: str | None
    adapter_version: str | None
    availability_status: str
    deterministic_policy: str


@dataclass(frozen=True)
class GovernedExecutorFailurePacket:
    instrument_id: str
    availability_status: str
    blocking_reason: str
    missing_inputs: tuple[str, ...]
    missing_assignment_fields: tuple[str, ...]
    missing_estimand_fields: tuple[str, ...]
    missing_uncertainty_fields: tuple[str, ...]


@dataclass(frozen=True)
class GovernedExecutorLookupResult:
    instrument_id: str
    availability_status: str
    executor_available: bool
    supports_dry_run: bool
    supports_execution: bool
    adapter_name: str | None = None
    adapter_version: str | None = None
    governance_status: str | None = None
    blocking_reason: str | None = None
    notes: str = ""
    missing_inputs: tuple[str, ...] = ()
    missing_assignment_fields: tuple[str, ...] = ()
    missing_estimand_fields: tuple[str, ...] = ()
    missing_uncertainty_fields: tuple[str, ...] = ()
    production_catalog_status: str | None = None
    production_catalog_blocked: bool = False
    production_claim_blocked: bool = False
    production_catalog_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GovernedExecutorRequest:
    instrument_id: str
    adapter_name: str
    adapter_version: str
    dry_run: bool
    execution_context: dict[str, Any]


@dataclass(frozen=True)
class GovernedExecutorResult:
    instrument_id: str
    availability_status: str
    execution_status: str
    completed: bool
    effect_estimate_report_status: str
    uncertainty_report_status: str
    claim_authorized: bool
    trace: GovernedExecutorTrace
    failure_packet: GovernedExecutorFailurePacket | None = None
    payload: dict[str, Any] = field(default_factory=dict)


def _build_default_specs() -> dict[str, GovernedExecutorAdapterSpec]:
    base = {
        "required_input_fields": ("instrument_id", "metric_name"),
        "required_assignment_fields": ("assignment_artifact_id",),
        "required_estimand_fields": ("estimand_type",),
        "required_uncertainty_fields": ("uncertainty_semantics",),
    }

    return {
        "DID_2X2_POINT_ESTIMATE": GovernedExecutorAdapterSpec(
            instrument_id="DID_2X2_POINT_ESTIMATE",
            estimator_family="DID_FAMILY",
            inference_family="POINT_ESTIMATE_ONLY",
            adapter_name="did_2x2_point_estimate_governed_adapter",
            adapter_version="0.3.0",
            governance_status="RESTRICTED_DIAGNOSTIC",
            supports_dry_run=True,
            supports_execution=True,
            supports_bootstrap_inference=False,
            supports_confidence_interval=False,
            supports_p_value=False,
            blocked_reason_if_not_supported="governed 2x2 point-estimate execution disabled by config",
            notes="Governed DID 2x2 point-estimate executor; no bootstrap, uncertainty, or claims.",
            **base,
        ),
        "DID_BOOTSTRAP": GovernedExecutorAdapterSpec(
            instrument_id="DID_BOOTSTRAP",
            estimator_family="DID_FAMILY",
            inference_family="BOOTSTRAP_INFERENCE_FAMILY",
            adapter_name="did_bootstrap_inference_adapter",
            adapter_version="0.1.0",
            governance_status="RESTRICTED_INFERENCE_NOT_IMPLEMENTED",
            supports_dry_run=True,
            supports_execution=False,
            supports_bootstrap_inference=False,
            supports_confidence_interval=False,
            supports_p_value=False,
            blocked_reason_if_not_supported="bootstrap inference not implemented in governed runtime",
            notes="Alias for DID_BOOTSTRAP_INFERENCE; not governed point estimate.",
            **base,
        ),
        "DID_BOOTSTRAP_INFERENCE": GovernedExecutorAdapterSpec(
            instrument_id="DID_BOOTSTRAP_INFERENCE",
            estimator_family="DID_FAMILY",
            inference_family="BOOTSTRAP_INFERENCE_FAMILY",
            adapter_name="did_bootstrap_inference_adapter",
            adapter_version="0.1.0",
            governance_status="RESTRICTED_INFERENCE_NOT_IMPLEMENTED",
            supports_dry_run=True,
            supports_execution=False,
            supports_bootstrap_inference=False,
            supports_confidence_interval=False,
            supports_p_value=False,
            blocked_reason_if_not_supported="bootstrap inference not implemented in governed runtime",
            notes="Bootstrap inference contract; not implemented.",
            **base,
        ),
        "DID_TWFE_LIBRARY_RESEARCH": GovernedExecutorAdapterSpec(
            instrument_id="DID_TWFE_LIBRARY_RESEARCH",
            estimator_family="DID_FAMILY",
            inference_family="TWFE_LIBRARY",
            adapter_name="did_twfe_library_research_adapter",
            adapter_version="0.1.0",
            governance_status="RESEARCH_ONLY",
            supports_dry_run=False,
            supports_execution=False,
            supports_bootstrap_inference=False,
            blocked_reason_if_not_supported="TWFE library estimator not wired to governed runtime",
            notes="Research-only library TWFE DID in panel_exp/methods/DID.py.",
            **base,
        ),
        "SCM_PLACEBO": GovernedExecutorAdapterSpec(
            instrument_id="SCM_PLACEBO",
            estimator_family="SCM_FAMILY",
            inference_family="PLACEBO_INFERENCE_FAMILY",
            adapter_name="scm_placebo_governed_adapter",
            adapter_version="0.1.0",
            governance_status="DIAGNOSTIC_ONLY",
            supports_dry_run=True,
            supports_execution=False,
            blocked_reason_if_not_supported="diagnostic-only; governed execution not implemented",
            notes="Must remain diagnostic; no production execution.",
            **base,
        ),
        "SCM_UNIT_JACKKNIFE": GovernedExecutorAdapterSpec(
            instrument_id="SCM_UNIT_JACKKNIFE",
            estimator_family="SCM_FAMILY",
            inference_family="UNIT_JACKKNIFE_INFERENCE_FAMILY",
            adapter_name="scm_jackknife_governed_adapter",
            adapter_version="0.1.0",
            governance_status="RESTRICTED_DIAGNOSTIC",
            supports_dry_run=True,
            supports_execution=False,
            blocked_reason_if_not_supported="governed execution not implemented",
            notes="Dry-run only.",
            **base,
        ),
        "TBR_RIDGE_BRB": GovernedExecutorAdapterSpec(
            instrument_id="TBR_RIDGE_BRB",
            estimator_family="TBR_RIDGE_FAMILY",
            inference_family="BRB_INFERENCE_FAMILY",
            adapter_name="tbrridge_brb_governed_adapter",
            adapter_version="0.1.0",
            governance_status="RESTRICTED",
            supports_dry_run=True,
            supports_execution=False,
            blocked_reason_if_not_supported="governed execution not implemented",
            notes="Dry-run only.",
            **base,
        ),
        "TBR_RIDGE_KFOLD": GovernedExecutorAdapterSpec(
            instrument_id="TBR_RIDGE_KFOLD",
            estimator_family="TBR_RIDGE_FAMILY",
            inference_family="KFOLD_INFERENCE_FAMILY",
            adapter_name="tbrridge_kfold_governed_adapter",
            adapter_version="0.1.0",
            governance_status="DIAGNOSTIC_ONLY",
            supports_dry_run=True,
            supports_execution=False,
            blocked_reason_if_not_supported="governed execution not implemented",
            notes="Dry-run only.",
            **base,
        ),
        "TBR_RIDGE_PLACEBO": GovernedExecutorAdapterSpec(
            instrument_id="TBR_RIDGE_PLACEBO",
            estimator_family="TBR_RIDGE_FAMILY",
            inference_family="PLACEBO_INFERENCE_FAMILY",
            adapter_name="tbrridge_placebo_governed_adapter",
            adapter_version="0.1.0",
            governance_status="DIAGNOSTIC_ONLY",
            supports_dry_run=True,
            supports_execution=False,
            blocked_reason_if_not_supported="governed execution not implemented",
            notes="Dry-run only.",
            **base,
        ),
        "AUGSYNTH_JACKKNIFE": GovernedExecutorAdapterSpec(
            instrument_id="AUGSYNTH_JACKKNIFE",
            estimator_family="AUGSYNTH_FAMILY",
            inference_family="JACKKNIFE_INFERENCE_FAMILY",
            adapter_name="augsynth_jackknife_governed_adapter",
            adapter_version="0.1.0",
            governance_status="RESTRICTED_DIAGNOSTIC",
            supports_dry_run=True,
            supports_execution=False,
            blocked_reason_if_not_supported="governed execution not implemented",
            notes="Dry-run only.",
            **base,
        ),
        "MATCHED_PAIR_RANDOMIZATION": GovernedExecutorAdapterSpec(
            instrument_id="MATCHED_PAIR_RANDOMIZATION",
            estimator_family="MATCHED_PAIR_FAMILY",
            inference_family="RANDOMIZATION_INFERENCE_FAMILY",
            adapter_name="matched_pair_randomization_governed_adapter",
            adapter_version="0.1.0",
            governance_status="RESEARCH_ONLY",
            supports_dry_run=True,
            supports_execution=False,
            blocked_reason_if_not_supported="governed execution not implemented",
            notes="Dry-run only.",
            **base,
        ),
        "AB_STANDARD_INFERENCE": GovernedExecutorAdapterSpec(
            instrument_id="AB_STANDARD_INFERENCE",
            estimator_family="AB_FAMILY",
            inference_family="STANDARD_INFERENCE_FAMILY",
            adapter_name="ab_standard_inference_governed_adapter",
            adapter_version="0.1.0",
            governance_status="BLOCKED_FOR_GEO_PANEL",
            supports_dry_run=False,
            supports_execution=False,
            blocked_reason_if_not_supported="unsupported estimator/inference for governed geo-panel runtime",
            notes="Blocked.",
            **base,
        ),
    }


def get_governed_executor_registry() -> GovernedExecutorRegistry:
    return GovernedExecutorRegistry(
        artifact_id="ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS",
        specs=_build_default_specs(),
    )


def _resolve_adapter_config(config: dict[str, Any] | None) -> dict[str, Any]:
    return dict(config or {})


def _did_point_estimate_enabled(config: dict[str, Any] | None) -> bool:
    cfg = _resolve_adapter_config(config)
    return bool(cfg.get("allow_governed_did_point_estimate_execution"))


def _resolve_registry_instrument_id(instrument_id: str) -> str:
    resolution = resolve_did_instrument_id(instrument_id)
    if resolution.canonical_instrument_id == DID_2X2_POINT_ESTIMATE:
        return DID_2X2_POINT_ESTIMATE
    if resolution.canonical_instrument_id == DID_BOOTSTRAP_INFERENCE:
        return "DID_BOOTSTRAP" if instrument_id.upper() == "DID_BOOTSTRAP" else DID_BOOTSTRAP_INFERENCE
    if resolution.canonical_instrument_id == DID_TWFE_LIBRARY_RESEARCH:
        return DID_TWFE_LIBRARY_RESEARCH
    return instrument_id


def _attach_production_catalog(
    result: GovernedExecutorLookupResult,
    *,
    estimator_family: str | None = None,
    inference_family: str | None = None,
    claim_type: str | None = None,
    production_context: str | None = "production",
) -> GovernedExecutorLookupResult:
    report = evaluate_production_catalog_status(
        {
            "instrument_id": result.instrument_id,
            "estimator_family": estimator_family,
            "inference_family": inference_family,
            "claim_type": claim_type,
            "production_context": production_context,
            "requested_role": "PRODUCTION_CANDIDATE",
        }
    )
    meta = production_catalog_executor_metadata(report)
    payload = dict(result.__dict__)
    payload.update(
        {
            "production_catalog_status": meta["production_catalog_status"],
            "production_catalog_blocked": meta["production_catalog_blocked"],
            "production_claim_blocked": meta["production_claim_blocked"],
            "production_catalog_metadata": meta["production_catalog_metadata"],
        }
    )
    return GovernedExecutorLookupResult(**payload)


def lookup_governed_executor(
    instrument_id: str,
    config: dict[str, Any] | None = None,
) -> GovernedExecutorLookupResult:
    cfg = _resolve_adapter_config(config)
    iid = str(instrument_id or "").strip()
    registry = get_governed_executor_registry()
    lookup_id = _resolve_registry_instrument_id(iid)
    spec = registry.specs.get(lookup_id) or registry.specs.get(iid)
    if not spec:
        return _attach_production_catalog(
            GovernedExecutorLookupResult(
                instrument_id=iid or "instrument_unspecified",
                availability_status=EXECUTOR_NOT_EVALUATED,
                executor_available=False,
                supports_dry_run=False,
                supports_execution=False,
                blocking_reason="instrument not found in governed registry",
                notes="No governed adapter spec found.",
            )
        )
    if spec.governance_status.startswith("BLOCKED"):
        return _attach_production_catalog(
            GovernedExecutorLookupResult(
                instrument_id=spec.instrument_id,
                availability_status=EXECUTOR_BLOCKED_BY_GOVERNANCE,
                executor_available=False,
                supports_dry_run=spec.supports_dry_run,
                supports_execution=spec.supports_execution,
                adapter_name=spec.adapter_name,
                adapter_version=spec.adapter_version,
                governance_status=spec.governance_status,
                blocking_reason=spec.blocked_reason_if_not_supported or "blocked by governance",
                notes=spec.notes,
            ),
            estimator_family=spec.estimator_family,
            inference_family=spec.inference_family,
        )

    supports_execution = spec.supports_execution
    if spec.instrument_id == DID_2X2_POINT_ESTIMATE and not _did_point_estimate_enabled(cfg):
        supports_execution = False
    if spec.instrument_id in ("DID_BOOTSTRAP", DID_BOOTSTRAP_INFERENCE):
        supports_execution = False

    if supports_execution:
        status = EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION
    elif spec.supports_dry_run:
        status = EXECUTOR_AVAILABLE_FOR_DRY_RUN
    else:
        status = EXECUTOR_NOT_IMPLEMENTED
    return _attach_production_catalog(
        GovernedExecutorLookupResult(
            instrument_id=spec.instrument_id,
            availability_status=status,
            executor_available=supports_execution or spec.supports_dry_run,
            supports_dry_run=spec.supports_dry_run,
            supports_execution=supports_execution,
            adapter_name=spec.adapter_name,
            adapter_version=spec.adapter_version,
            governance_status=spec.governance_status,
            blocking_reason=spec.blocked_reason_if_not_supported if not supports_execution else None,
            notes=spec.notes,
        ),
        estimator_family=spec.estimator_family,
        inference_family=spec.inference_family,
    )


def evaluate_governed_executor_availability(
    instrument: dict[str, Any],
    execution_context: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> GovernedExecutorLookupResult:
    instrument_id = str(instrument.get("instrument_id") or "instrument_unspecified")
    lookup = lookup_governed_executor(instrument_id, config=config)
    if lookup.availability_status in (EXECUTOR_NOT_EVALUATED, EXECUTOR_BLOCKED_BY_GOVERNANCE):
        return lookup

    role = str(instrument.get("execution_role") or "")
    governance_status = str(instrument.get("governance_status") or "")
    if "BLOCKED" in role or "NOT_EVALUATED" in role:
        payload = dict(lookup.__dict__)
        payload.update(
            {
                "availability_status": EXECUTOR_BLOCKED_BY_INSTRUMENT_STATUS,
                "executor_available": False,
                "blocking_reason": "instrument execution role blocked or not evaluated",
            }
        )
        return GovernedExecutorLookupResult(
            **payload
        )

    assignment_artifact_id = str(execution_context.get("assignment_artifact_id") or "")
    if not assignment_artifact_id or not instrument.get("assignment_artifact_id"):
        payload = dict(lookup.__dict__)
        payload.update(
            {
                "availability_status": EXECUTOR_BLOCKED_BY_ASSIGNMENT_ARTIFACT,
                "executor_available": False,
                "blocking_reason": "assignment artifact reference missing",
            }
        )
        return GovernedExecutorLookupResult(
            **payload
        )

    data_contract = execution_context.get("execution_data_contract") or {}
    required_columns = data_contract.get("required_columns") or []
    available_columns = set(data_contract.get("available_columns") or [])
    missing_columns = tuple(c for c in required_columns if c not in available_columns)
    if missing_columns:
        payload = dict(lookup.__dict__)
        payload.update(
            {
                "availability_status": EXECUTOR_BLOCKED_BY_DATA_CONTRACT,
                "executor_available": False,
                "blocking_reason": "required columns missing for governed adapter",
                "missing_inputs": missing_columns,
            }
        )
        return GovernedExecutorLookupResult(
            **payload
        )

    estimand_scope = execution_context.get("estimand_scope") or {}
    if not estimand_scope.get("estimand_type"):
        payload = dict(lookup.__dict__)
        payload.update(
            {
                "availability_status": EXECUTOR_BLOCKED_BY_ESTIMAND,
                "executor_available": False,
                "blocking_reason": "estimand scope missing for governed adapter",
                "missing_estimand_fields": ("estimand_type",),
            }
        )
        return GovernedExecutorLookupResult(
            **payload
        )

    uncertainty_scope = execution_context.get("uncertainty_scope") or {}
    if not instrument.get("uncertainty_semantics"):
        payload = dict(lookup.__dict__)
        payload.update(
            {
                "availability_status": EXECUTOR_BLOCKED_BY_UNCERTAINTY_SEMANTICS,
                "executor_available": False,
                "blocking_reason": "instrument uncertainty semantics missing",
                "missing_uncertainty_fields": ("uncertainty_semantics",),
            }
        )
        return GovernedExecutorLookupResult(
            **payload
        )
    if uncertainty_scope.get("semantics"):
        if str(uncertainty_scope.get("semantics")).upper() not in str(instrument.get("uncertainty_semantics")).upper():
            payload = dict(lookup.__dict__)
            payload.update(
                {
                    "availability_status": EXECUTOR_BLOCKED_BY_UNCERTAINTY_SEMANTICS,
                    "executor_available": False,
                    "blocking_reason": "uncertainty semantics incompatible with execution context",
                }
            )
            return GovernedExecutorLookupResult(
                **payload
            )

    if "DIAGNOSTIC_ONLY" in governance_status and role == "PRIMARY_EXECUTION_CANDIDATE":
        payload = dict(lookup.__dict__)
        payload.update(
            {
                "availability_status": EXECUTOR_BLOCKED_BY_GOVERNANCE,
                "executor_available": False,
                "blocking_reason": "diagnostic-only instruments cannot run as primary",
            }
        )
        return GovernedExecutorLookupResult(
            **payload
        )

    return lookup


def build_governed_executor_request(
    instrument: dict[str, Any],
    execution_context: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> GovernedExecutorRequest:
    lookup = evaluate_governed_executor_availability(instrument, execution_context, config=config)
    return GovernedExecutorRequest(
        instrument_id=str(instrument.get("instrument_id") or "instrument_unspecified"),
        adapter_name=lookup.adapter_name or "adapter_unavailable",
        adapter_version=lookup.adapter_version or "0.0.0",
        dry_run=True,
        execution_context=dict(execution_context),
    )


def build_governed_executor_result(
    instrument: dict[str, Any],
    execution_context: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> tuple[GovernedExecutorLookupResult, GovernedExecutorRequest, GovernedExecutorResult]:
    registry = get_governed_executor_registry()
    lookup = evaluate_governed_executor_availability(instrument, execution_context, config=config)
    request = build_governed_executor_request(instrument, execution_context, config=config)
    dry_run = lookup.availability_status != EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION
    trace = GovernedExecutorTrace(
        instrument_id=lookup.instrument_id,
        adapter_name=lookup.adapter_name,
        adapter_version=lookup.adapter_version,
        availability_status=lookup.availability_status,
        deterministic_policy=(
            "governed_registry_deterministic_point_estimate_only"
            if lookup.availability_status == EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION
            else "governed_registry_deterministic_no_execution"
        ),
    )
    failure_packet = None
    if lookup.availability_status not in (
        EXECUTOR_AVAILABLE_FOR_DRY_RUN,
        EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION,
    ):
        failure_packet = GovernedExecutorFailurePacket(
            instrument_id=lookup.instrument_id,
            availability_status=lookup.availability_status,
            blocking_reason=lookup.blocking_reason or "adapter unavailable",
            missing_inputs=lookup.missing_inputs,
            missing_assignment_fields=lookup.missing_assignment_fields,
            missing_estimand_fields=lookup.missing_estimand_fields,
            missing_uncertainty_fields=lookup.missing_uncertainty_fields,
        )
    result = GovernedExecutorResult(
        instrument_id=lookup.instrument_id,
        availability_status=lookup.availability_status,
        execution_status="INSTRUMENT_EXECUTION_NOT_RUN" if dry_run else "INSTRUMENT_EXECUTION_READY",
        completed=False,
        effect_estimate_report_status="NOT_COMPUTED",
        uncertainty_report_status="NOT_COMPUTED",
        claim_authorized=False,
        trace=trace,
        failure_packet=failure_packet,
        payload={
            "supports_dry_run": lookup.supports_dry_run,
            "supports_execution": lookup.supports_execution,
            "supports_bootstrap_inference": (
                registry.specs[lookup.instrument_id].supports_bootstrap_inference
                if lookup.instrument_id in registry.specs
                else False
            ),
            "supports_confidence_interval": (
                registry.specs[lookup.instrument_id].supports_confidence_interval
                if lookup.instrument_id in registry.specs
                else False
            ),
            "supports_p_value": (
                registry.specs[lookup.instrument_id].supports_p_value
                if lookup.instrument_id in registry.specs
                else False
            ),
            "adapter_name": lookup.adapter_name,
            "adapter_version": lookup.adapter_version,
        },
    )
    return lookup, request, result
