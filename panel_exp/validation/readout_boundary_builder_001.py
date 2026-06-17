"""INFERENCE-BOUNDARY-GUARDRAIL-ENFORCEMENT-001 — guarded readout evidence builder."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from panel_exp.evidence import ReadoutEvidence
from panel_exp.validation.design_guardrail_runtime_001 import GUARDRAIL_BLOCK
from panel_exp.validation.inference_boundary_guardrail_001 import (
    InferenceBoundaryViolation,
    evaluate_inference_boundary_guardrail,
    enforce_inference_boundary,
)
from panel_exp.validation.inference_boundary_identity_001 import InferenceBoundaryIdentity

BUILDER_VERSION = "1.0.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _compact_result_payload(
    *,
    point_estimate: float | None,
    interval: tuple[float, float] | None,
    p_value: float | None,
    metadata: Mapping[str, Any] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if point_estimate is not None:
        payload["point_estimate"] = float(point_estimate)
    if interval is not None:
        payload["interval_lower"] = float(interval[0])
        payload["interval_upper"] = float(interval[1])
    if p_value is not None:
        payload["p_value"] = float(p_value)
    if metadata:
        payload["metadata"] = dict(metadata)
    return payload


def build_guarded_readout(
    *,
    design_evidence: Mapping[str, Any] | Any,
    estimator_id: str | None = None,
    inference_id: str | None = None,
    instrument_id: str | None = None,
    readout_semantics: str | None = None,
    interval_type: str | None = None,
    estimand: str | None = None,
    requested_role: str | None = "research",
    point_estimate: float | None = None,
    interval: tuple[float, float] | None = None,
    p_value: float | None = None,
    cell_id: str | None = None,
    pooled: bool = False,
    geometry_id: str | None = None,
    design_id: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    enforce: bool = True,
    created_at: str | None = None,
) -> ReadoutEvidence:
    """Construct governed readout evidence after boundary guardrail evaluation."""
    if interval is not None and readout_semantics is None:
        readout_semantics = "causal_interval"
    if interval is not None and interval_type is None:
        interval_type = "jackknife_interval"
    if point_estimate is not None and readout_semantics is None and interval is None:
        readout_semantics = "point_estimate"
        interval_type = interval_type or "none"

    identity = InferenceBoundaryIdentity.build(
        design_id=design_id,
        estimator_id=estimator_id,
        inference_id=inference_id,
        instrument_id=instrument_id,
        geometry_id=geometry_id,
        readout_semantics=readout_semantics,
        interval_type=interval_type,
        estimand=estimand,
        cell_id=cell_id,
        pooled=pooled,
        requested_role=requested_role,
        source="readout_boundary_builder",
    )

    if enforce and requested_role:
        boundary = enforce_inference_boundary(
            design_evidence=design_evidence,
            identity=identity,
        )
    else:
        boundary = evaluate_inference_boundary_guardrail(
            design_evidence=design_evidence,
            identity=identity,
        )

    if enforce and boundary.status == GUARDRAIL_BLOCK and requested_role:
        raise InferenceBoundaryViolation(
            "Guarded readout build blocked at inference boundary.",
            result=boundary,
        )

    design_payload: dict[str, Any] = {}
    if hasattr(design_evidence, "to_dict"):
        design_payload = design_evidence.to_dict()
    elif isinstance(design_evidence, Mapping):
        design_payload = dict(design_evidence)

    from panel_exp.validation.design_combination_resolver_001 import resolve_design_combination

    contract = design_payload.get("design_contract")
    resolution = resolve_design_combination(identity, design_contract=contract)

    return ReadoutEvidence(
        evidence_version="1.0",
        created_at=created_at or _utc_now_iso(),
        builder_version=BUILDER_VERSION,
        estimator_identity={
            "estimator_id": identity.estimator_id,
            "instrument_id": identity.instrument_id,
        },
        inference_identity={
            "inference_id": identity.inference_id,
            "interval_type": identity.interval_type,
        },
        readout_identity=identity.to_dict(),
        combination_resolution=resolution.to_dict(),
        inference_boundary_guardrail=boundary.to_dict(),
        guardrail_enforcement=boundary.enforcement,
        result_payload=_compact_result_payload(
            point_estimate=point_estimate,
            interval=interval,
            p_value=p_value,
            metadata=metadata,
        ),
    )
