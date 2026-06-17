"""INFERENCE-BOUNDARY-GUARDRAIL-ENFORCEMENT-001 — DCM row resolution from boundary identity."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from panel_exp.validation.design_combination_guardrail_001 import (
    COMBINATION_REGISTRY,
    COMBINATION_STATUS_NOT_EVALUATED,
)
from panel_exp.validation.inference_boundary_identity_001 import InferenceBoundaryIdentity

RESOLVER_VERSION = "1.0.0"

RESOLUTION_UNKNOWN = "unknown"
RESOLUTION_NOT_EVALUATED = "not_evaluated"
RESOLUTION_ADAPTER_REQUIRED = "adapter_required"
RESOLUTION_BRIDGE_REQUIRED = "bridge_required"


@dataclass(frozen=True)
class DesignCombinationResolution:
    dcm_row_id: str | None
    combination_status: str
    resolution_status: str
    design_id: str | None
    estimator_id: str | None
    inference_id: str | None
    geometry_id: str | None
    readout_semantics: str | None
    pooled: bool
    resolver_version: str = RESOLVER_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _design_id_from_contract(contract: Mapping[str, Any] | None) -> str | None:
    if contract is None:
        return None
    identity = contract.get("design_identity")
    if _is_mapping(identity) and identity.get("design_inventory_id"):
        return str(identity["design_inventory_id"])
    return None


def _geometry_from_contract(contract: Mapping[str, Any] | None) -> str | None:
    if contract is None:
        return None
    geometry = contract.get("geometry")
    if _is_mapping(geometry) and geometry.get("geometry_id"):
        return str(geometry["geometry_id"])
    return None


def _norm(value: str | None) -> str:
    return (value or "").strip().lower().replace("-", "_")


def resolve_design_combination(
    identity: InferenceBoundaryIdentity,
    *,
    design_contract: Mapping[str, Any] | None = None,
) -> DesignCombinationResolution:
    """Map runtime boundary identity to a governed DCM row."""
    design_id = identity.design_id or _design_id_from_contract(design_contract)
    geometry_id = identity.geometry_id or _geometry_from_contract(design_contract)
    est = _norm(identity.estimator_id)
    inf = _norm(identity.inference_id)
    geo = _norm(geometry_id)
    rs = _norm(identity.readout_semantics)

    if not est and not inf and not identity.instrument_id:
        return DesignCombinationResolution(
            dcm_row_id=None,
            combination_status=COMBINATION_STATUS_NOT_EVALUATED,
            resolution_status=RESOLUTION_NOT_EVALUATED,
            design_id=design_id,
            estimator_id=identity.estimator_id,
            inference_id=identity.inference_id,
            geometry_id=geometry_id,
            readout_semantics=identity.readout_semantics,
            pooled=identity.pooled,
        )

    dcm_id: str | None = None

    if identity.pooled or geo == "pooled_multi_cell" or rs in ("pooled_point", "pooled_interval"):
        dcm_id = "DCM-007"
    elif (design_id or "").upper() == "DES-009" or "trimmed" in est:
        dcm_id = "DCM-011"
        status = COMBINATION_REGISTRY["DCM-011"].combination_status
        return DesignCombinationResolution(
            dcm_row_id=dcm_id,
            combination_status=status,
            resolution_status=RESOLUTION_BRIDGE_REQUIRED,
            design_id=design_id,
            estimator_id=identity.estimator_id,
            inference_id=identity.inference_id,
            geometry_id=geometry_id,
            readout_semantics=identity.readout_semantics,
            pooled=identity.pooled,
        )
    elif (design_id or "").upper() == "DES-010" or geo == "supergeo":
        dcm_id = "DCM-013"
        return DesignCombinationResolution(
            dcm_row_id=dcm_id,
            combination_status=COMBINATION_REGISTRY["DCM-013"].combination_status,
            resolution_status=RESOLUTION_BRIDGE_REQUIRED,
            design_id=design_id,
            estimator_id=identity.estimator_id,
            inference_id=identity.inference_id,
            geometry_id=geometry_id,
            readout_semantics=identity.readout_semantics,
            pooled=identity.pooled,
        )
    elif geo == "multi_cell_per_cell" or (
        (design_id or "").upper() == "DES-011" and not identity.pooled
    ):
        if est in ("scm",) or rs in ("per_cell_point", "per_cell_interval"):
            dcm_id = "DCM-006"
    elif (design_id or "").upper() == "DES-004" and est == "scm" and inf == "unit_jackknife":
        dcm_id = "DCM-008"
    elif est == "augsynth":
        dcm_id = "DCM-002"
    elif est == "tbr" and "ridge" not in est:
        dcm_id = "DCM-003"
    elif est == "did":
        dcm_id = "DCM-004"
    elif est == "scm" and inf == "unit_jackknife":
        dcm_id = "DCM-001"
    elif est == "scm" and inf in ("placebo",):
        dcm_id = "DCM-001"
    elif est == "tbrridge":
        dcm_id = "DCM-005"

    if dcm_id is None:
        return DesignCombinationResolution(
            dcm_row_id=None,
            combination_status=COMBINATION_STATUS_NOT_EVALUATED,
            resolution_status=RESOLUTION_UNKNOWN,
            design_id=design_id,
            estimator_id=identity.estimator_id,
            inference_id=identity.inference_id,
            geometry_id=geometry_id,
            readout_semantics=identity.readout_semantics,
            pooled=identity.pooled,
        )

    entry = COMBINATION_REGISTRY.get(dcm_id)
    combination_status = entry.combination_status if entry else RESOLUTION_UNKNOWN
    return DesignCombinationResolution(
        dcm_row_id=dcm_id,
        combination_status=combination_status,
        resolution_status="resolved",
        design_id=design_id,
        estimator_id=identity.estimator_id,
        inference_id=identity.inference_id,
        geometry_id=geometry_id,
        readout_semantics=identity.readout_semantics,
        pooled=identity.pooled,
    )
