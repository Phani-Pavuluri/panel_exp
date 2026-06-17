"""ESTIMATOR-READOUT-GUARDRAIL-INTEGRATION-001 — governed readout from native estimator results.

Routes native ImpactAnalyzer / results-dict outputs through ``build_guarded_readout()``
without duplicating DCM resolution or inference-boundary enforcement logic.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

import numpy as np

from panel_exp.evidence import ReadoutEvidence
from panel_exp.inference._metadata import treatment_window_point_effect
from panel_exp.inference_result import IntervalType
from panel_exp.method_metadata import _CLASS_TO_KEY
from panel_exp.validation.inference_boundary_identity_001 import (
    normalize_estimator_id,
    normalize_estimand,
    normalize_inference_id,
    normalize_interval_type,
    normalize_readout_semantics,
)
from panel_exp.validation.inference_boundary_guardrail_001 import InferenceBoundaryViolation
from panel_exp.validation.readout_boundary_builder_001 import build_guarded_readout

ADAPTER_VERSION = "1.0.0"
GOVERNED_READOUT_MARKER = "governed_readout_evidence"


def _require_identity_for_enforcement(
    *,
    estimator_id: str | None,
    inference_id: str | None,
    readout_semantics: str | None,
    enforce: bool,
    requested_role: str | None,
) -> None:
    """Fail closed at adapter boundary when required identity is absent."""
    if not enforce or not requested_role:
        return
    if not normalize_estimator_id(estimator_id):
        raise InferenceBoundaryViolation(
            "Estimator identity is required for governed readout construction.",
            result=None,
        )
    rs = normalize_readout_semantics(readout_semantics or "")
    est = normalize_estimator_id(estimator_id)
    inf = normalize_inference_id(inference_id)
    if est == "scm" and rs in ("causal_interval", "per_cell_interval") and not inf:
        raise InferenceBoundaryViolation(
            "Inference identity is required for SCM interval readouts.",
            result=None,
        )

_CLASS_TO_ESTIMATOR: dict[str, str] = {
    cls: normalize_estimator_id(key) or key.lower()
    for cls, key in _CLASS_TO_KEY.items()
}

_INFERENCE_MODE_TO_GOVERNED: dict[str, str] = {
    "unitjackknife": "unit_jackknife",
    "unit_jackknife": "unit_jackknife",
    "placebo": "placebo",
    "kfold": "kfold",
    "timeserieskfold": "kfold",
    "time_series_kfold": "kfold",
    "blockresidualbootstrap": "brb",
    "block_residual_bootstrap": "brb",
    "brb": "brb",
    "bootstrap": "bootstrap",
    "point_estimate": "point_only",
    "point_only": "point_only",
    "none": "none",
}

_INTERVAL_TYPE_BY_INFERENCE: dict[str, str] = {
    "unit_jackknife": "jackknife_interval",
    "placebo": "placebo_interval",
    "bootstrap": "bootstrap_interval",
    "brb": "brb_interval",
    "kfold": "kfold_interval",
    "point_only": "none",
    "none": "none",
}

_PATH_INTERVAL_TO_GOVERNED: dict[IntervalType, str] = {
    IntervalType.CONFIDENCE_INTERVAL: "jackknife_interval",
    IntervalType.PLACEBO_BAND: "placebo_interval",
    IntervalType.CONFORMAL_INTERVAL: "credible_interval",
    IntervalType.CREDIBLE_INTERVAL: "credible_interval",
    IntervalType.UNAVAILABLE: "none",
}


@dataclass(frozen=True)
class AdaptedNativeResult:
    """Governed scalar readout fields extracted from a native estimator payload."""

    point_estimate: float | None = None
    interval: tuple[float, float] | None = None
    p_value: float | None = None
    readout_semantics: str | None = None
    interval_type: str | None = None
    estimand: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GovernedAnalysisResult:
    """Native estimator output plus governed ``ReadoutEvidence``."""

    native_results: dict[str, Any]
    readout_evidence: ReadoutEvidence
    adapted: AdaptedNativeResult
    adapter_version: str = ADAPTER_VERSION


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _design_payload(design_evidence: Any) -> dict[str, Any]:
    if hasattr(design_evidence, "to_dict"):
        return design_evidence.to_dict()
    if _is_mapping(design_evidence):
        if "design" in design_evidence and _is_mapping(design_evidence["design"]):
            return dict(design_evidence["design"])
        return dict(design_evidence)
    return {}


def extract_geometry_context(
    design_evidence: Any,
) -> dict[str, Any]:
    """Propagate design geometry metadata from ``DesignEvidence`` (not estimator identity)."""
    payload = _design_payload(design_evidence)
    contract = payload.get("design_contract") or {}
    identity = contract.get("design_identity") or {}
    geometry = contract.get("geometry") or {}
    multi_cell = contract.get("multi_cell") or {}

    design_id = identity.get("design_inventory_id")
    geometry_id = geometry.get("geometry_id")
    is_multi_cell = bool(multi_cell.get("is_multi_cell"))
    cell_ids = list(multi_cell.get("cell_ids") or [])
    shared_control_policy = multi_cell.get("shared_control_policy")
    control_reuse_policy = multi_cell.get("control_reuse_policy")
    pooled_claims_allowed = multi_cell.get("pooled_claims_allowed")

    return {
        "design_id": design_id,
        "geometry_id": geometry_id,
        "is_multi_cell": is_multi_cell,
        "cell_ids": cell_ids,
        "shared_control_policy": shared_control_policy,
        "control_reuse_policy": control_reuse_policy,
        "pooled_claims_allowed": pooled_claims_allowed,
    }


def infer_estimator_id_from_analyzer(analyzer: Any) -> str | None:
    """Map ImpactAnalyzer class to governed estimator identity (never ``multicell``)."""
    cls_name = type(analyzer).__name__
    registry_key = _CLASS_TO_KEY.get(cls_name)
    if registry_key:
        return normalize_estimator_id(registry_key)
    return normalize_estimator_id(cls_name)


def infer_inference_id_from_analyzer(analyzer: Any) -> str | None:
    raw = getattr(analyzer, "inference", None)
    if raw is None:
        return "point_only"
    key = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
    governed = _INFERENCE_MODE_TO_GOVERNED.get(key, normalize_inference_id(str(raw)))
    return governed


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        out = float(value)
        return out if np.isfinite(out) else None
    except (TypeError, ValueError):
        return None


def _point_from_results(results: Mapping[str, Any], analyzer: Any | None = None) -> float | None:
    for key in (
        "point_estimate",
        "cumulative_att",
        "att_post",
        "effect_post_test",
        "lift_point",
        "relative_att_post",
    ):
        val = _float_or_none(results.get(key))
        if val is not None:
            return val
    if analyzer is not None:
        return treatment_window_point_effect(analyzer)
    y = results.get("y")
    y_hat = results.get("y_hat")
    if y is not None and y_hat is not None:
        diff = np.asarray(y, dtype=float) - np.asarray(y_hat, dtype=float)
        if diff.size:
            return _float_or_none(np.nanmean(diff))
    return None


def _interval_from_path_bounds(
    results: Mapping[str, Any],
    *,
    test_length: int | None = None,
) -> tuple[float, float] | None:
    lo = _float_or_none(results.get("interval_lower"))
    hi = _float_or_none(results.get("interval_upper"))
    if lo is not None and hi is not None:
        return (lo, hi)

    ci = results.get("treatment_ci")
    if isinstance(ci, (list, tuple)) and len(ci) == 2:
        lo = _float_or_none(ci[0])
        hi = _float_or_none(ci[1])
        if lo is not None and hi is not None:
            return (lo, hi)

    if results.get("y") is None or results.get("y_hat") is None:
        return None

    y = np.asarray(results.get("y"), dtype=float).reshape(-1)
    y_lo = np.asarray(results.get("y_lower"), dtype=float).reshape(-1)
    y_hi = np.asarray(results.get("y_upper"), dtype=float).reshape(-1)
    if y.size == 0 or y_lo.size == 0 or y_hi.size == 0:
        return None

    sl = slice(-test_length, None) if test_length and test_length < y.size else slice(None)
    eff_lo = y[sl] - y_hi[sl]
    eff_hi = y[sl] - y_lo[sl]
    lo = _float_or_none(np.nanmean(eff_lo))
    hi = _float_or_none(np.nanmean(eff_hi))
    if lo is None or hi is None:
        return None
    return (lo, hi)


def _interval_type_from_analyzer(analyzer: Any, inference_id: str | None) -> str:
    ir = getattr(analyzer, "inference_result", None)
    if ir is not None and hasattr(ir, "effective_path_interval_type"):
        path = ir.effective_path_interval_type()
        mapped = _PATH_INTERVAL_TO_GOVERNED.get(path)
        if mapped and mapped != "none":
            if inference_id == "brb":
                return "brb_interval"
            if inference_id == "kfold":
                return "kfold_interval"
            if inference_id == "placebo":
                return "placebo_interval"
            if inference_id == "bootstrap":
                return "bootstrap_interval"
            return mapped
    if inference_id:
        return _INTERVAL_TYPE_BY_INFERENCE.get(inference_id, "unknown")
    return "none"


def _default_readout_semantics(
    *,
    estimator_id: str | None,
    inference_id: str | None,
    interval: tuple[float, float] | None,
    readout_semantics: str | None,
    pooled: bool,
    cell_id: str | None,
    is_multi_cell: bool,
) -> str:
    if readout_semantics:
        return normalize_readout_semantics(readout_semantics)
    if pooled:
        return "pooled_point" if interval is None else "pooled_interval"
    if is_multi_cell or cell_id:
        return "per_cell_point" if interval is None else "per_cell_interval"
    if interval is not None:
        if inference_id == "placebo":
            return "null_monitor_interval"
        return "causal_interval"
    if estimator_id == "augsynth" or inference_id == "point_only":
        return "point_estimate"
    return "point_estimate"


def adapt_native_result_payload(
    *,
    estimator_id: str,
    inference_id: str | None,
    native: Mapping[str, Any],
    analyzer: Any | None = None,
    readout_semantics: str | None = None,
    interval_type: str | None = None,
    estimand: str | None = None,
    test_length: int | None = None,
    allow_interval_from_native: bool = True,
    metadata: Mapping[str, Any] | None = None,
) -> AdaptedNativeResult:
    """Map governed scalar fields from a native results mapping."""
    est = normalize_estimator_id(estimator_id) or "unknown"
    inf = normalize_inference_id(inference_id)

    point = _point_from_results(native, analyzer)
    interval: tuple[float, float] | None = None

    if allow_interval_from_native and est != "augsynth":
        interval = _interval_from_path_bounds(native, test_length=test_length)
    elif allow_interval_from_native and est == "augsynth" and inf not in (None, "point_only", "none"):
        interval = _interval_from_path_bounds(native, test_length=test_length)

    if est == "augsynth" and inf in (None, "point_only", "none"):
        interval = None

    p_value = _float_or_none(native.get("p_value") or native.get("treatment_pvalue"))

    if interval_type is None and analyzer is not None:
        interval_type = _interval_type_from_analyzer(analyzer, inf)
    elif interval_type is None and inf:
        interval_type = _INTERVAL_TYPE_BY_INFERENCE.get(inf, "none")
    else:
        interval_type = normalize_interval_type(interval_type)

    rs = _default_readout_semantics(
        estimator_id=est,
        inference_id=inf,
        interval=interval,
        readout_semantics=readout_semantics,
        pooled=False,
        cell_id=None,
        is_multi_cell=False,
    )

    meta: dict[str, Any] = {
        "adapter_version": ADAPTER_VERSION,
        "native_keys": sorted(str(k) for k in native.keys()),
    }
    if metadata:
        meta.update(dict(metadata))
    if native.get("inference_metadata"):
        meta["inference_metadata"] = dict(native["inference_metadata"])

    return AdaptedNativeResult(
        point_estimate=point,
        interval=interval,
        p_value=p_value,
        readout_semantics=rs,
        interval_type=interval_type,
        estimand=normalize_estimand(estimand) if estimand else None,
        metadata=meta,
    )


def adapt_impact_analyzer_results(
    analyzer: Any,
    *,
    estimator_id: str | None = None,
    inference_id: str | None = None,
    readout_semantics: str | None = None,
    interval_type: str | None = None,
    estimand: str | None = None,
    test_length: int | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AdaptedNativeResult:
    """Extract governed readout fields from an ImpactAnalyzer after ``run_analysis``."""
    results = getattr(analyzer, "results", None) or {}
    if not _is_mapping(results):
        results = {}
    est = estimator_id or infer_estimator_id_from_analyzer(analyzer)
    inf = inference_id or infer_inference_id_from_analyzer(analyzer)
    return adapt_native_result_payload(
        estimator_id=est or "unknown",
        inference_id=inf,
        native=results,
        analyzer=analyzer,
        readout_semantics=readout_semantics,
        interval_type=interval_type,
        estimand=estimand,
        test_length=test_length,
        allow_interval_from_native=True,
        metadata=metadata,
    )


def build_estimator_readout(
    *,
    design_evidence: Any,
    estimator_id: str | None = None,
    inference_id: str | None = None,
    result_payload: Mapping[str, Any] | Any | None = None,
    analyzer: Any | None = None,
    requested_role: str = "research",
    readout_semantics: str | None = None,
    interval_type: str | None = None,
    estimand: str | None = None,
    cell_id: str | None = None,
    pooled: bool = False,
    metadata: Mapping[str, Any] | None = None,
    test_length: int | None = None,
    enforce: bool = True,
) -> ReadoutEvidence:
    """Build governed ``ReadoutEvidence`` from design evidence and native estimator output."""
    geo_ctx = extract_geometry_context(design_evidence)
    design_id = geo_ctx.get("design_id")
    geometry_id = geo_ctx.get("geometry_id")
    is_multi_cell = bool(geo_ctx.get("is_multi_cell"))

    if result_payload is not None and hasattr(result_payload, "results"):
        analyzer = result_payload
        result_payload = None

    if analyzer is not None and (estimator_id is None or inference_id is None):
        estimator_id = estimator_id or infer_estimator_id_from_analyzer(analyzer)
        inference_id = inference_id or infer_inference_id_from_analyzer(analyzer)

    native: Mapping[str, Any]
    if analyzer is not None:
        adapted = adapt_impact_analyzer_results(
            analyzer,
            estimator_id=estimator_id,
            inference_id=inference_id,
            readout_semantics=readout_semantics,
            interval_type=interval_type,
            estimand=estimand,
            test_length=test_length,
            metadata=metadata,
        )
    elif result_payload is not None and _is_mapping(result_payload):
        adapted = adapt_native_result_payload(
            estimator_id=estimator_id or "unknown",
            inference_id=inference_id,
            native=result_payload,
            readout_semantics=readout_semantics,
            interval_type=interval_type,
            estimand=estimand,
            test_length=test_length,
            allow_interval_from_native=estimator_id != "augsynth"
            or inference_id not in (None, "point_only", "none"),
            metadata=metadata,
        )
    else:
        adapted = AdaptedNativeResult(
            readout_semantics=normalize_readout_semantics(readout_semantics or "unknown"),
            interval_type=normalize_interval_type(interval_type),
            estimand=normalize_estimand(estimand) if estimand else None,
            metadata=dict(metadata or {}),
        )

    rs = readout_semantics or adapted.readout_semantics
    if pooled:
        rs = "pooled_point" if adapted.interval is None else "pooled_interval"
    elif is_multi_cell or cell_id:
        if rs in (None, "point_estimate", "causal_interval"):
            rs = "per_cell_point" if adapted.interval is None else "per_cell_interval"

    if estimand is None and is_multi_cell and cell_id:
        estimand = "per_cell_effect"
    elif estimand is None and pooled:
        estimand = "pooled_multicell_effect"

    meta = dict(adapted.metadata)
    meta.update(
        {
            "geometry_context": geo_ctx,
            "adapter_version": ADAPTER_VERSION,
            GOVERNED_READOUT_MARKER: True,
        }
    )
    if cell_id:
        meta["cell_id"] = cell_id
    if geo_ctx.get("shared_control_policy"):
        meta["shared_control_policy"] = geo_ctx["shared_control_policy"]
    if geo_ctx.get("control_reuse_policy"):
        meta["control_reuse_policy"] = geo_ctx["control_reuse_policy"]

    _require_identity_for_enforcement(
        estimator_id=estimator_id,
        inference_id=inference_id,
        readout_semantics=rs,
        enforce=enforce,
        requested_role=requested_role,
    )

    return build_guarded_readout(
        design_evidence=design_evidence,
        estimator_id=estimator_id,
        inference_id=inference_id,
        readout_semantics=rs,
        interval_type=interval_type or adapted.interval_type,
        estimand=estimand or adapted.estimand,
        requested_role=requested_role,
        point_estimate=adapted.point_estimate,
        interval=adapted.interval,
        p_value=adapted.p_value,
        cell_id=cell_id,
        pooled=pooled,
        geometry_id=geometry_id,
        design_id=design_id,
        metadata=meta,
        enforce=enforce,
    )


def run_governed_analysis(
    analyzer: Any,
    panel_data: Any,
    design_evidence: Any,
    *,
    estimator_id: str | None = None,
    inference_id: str | None = None,
    requested_role: str = "research",
    readout_semantics: str | None = None,
    interval_type: str | None = None,
    estimand: str | None = None,
    cell_id: str | None = None,
    pooled: bool = False,
    metadata: Mapping[str, Any] | None = None,
    test_length: int | None = None,
    enforce: bool = True,
    **inference_kwargs: Any,
) -> GovernedAnalysisResult:
    """Run ``run_analysis`` then automatically attach governed ``ReadoutEvidence``."""
    native_results = analyzer.run_analysis(panel_data, **inference_kwargs)
    if not _is_mapping(native_results):
        native_results = getattr(analyzer, "results", {}) or {}

    adapted = adapt_impact_analyzer_results(
        analyzer,
        estimator_id=estimator_id,
        inference_id=inference_id,
        readout_semantics=readout_semantics,
        interval_type=interval_type,
        estimand=estimand,
        test_length=test_length,
        metadata=metadata,
    )
    readout = build_estimator_readout(
        design_evidence=design_evidence,
        estimator_id=estimator_id,
        inference_id=inference_id,
        analyzer=analyzer,
        requested_role=requested_role,
        readout_semantics=readout_semantics,
        interval_type=interval_type,
        estimand=estimand,
        cell_id=cell_id,
        pooled=pooled,
        metadata=metadata,
        test_length=test_length,
        enforce=enforce,
    )
    return GovernedAnalysisResult(
        native_results=dict(native_results),
        readout_evidence=readout,
        adapted=adapted,
    )


__all__ = [
    "ADAPTER_VERSION",
    "AdaptedNativeResult",
    "GovernedAnalysisResult",
    "adapt_impact_analyzer_results",
    "adapt_native_result_payload",
    "build_estimator_readout",
    "extract_geometry_context",
    "GOVERNED_READOUT_MARKER",
    "infer_estimator_id_from_analyzer",
    "infer_inference_id_from_analyzer",
    "run_governed_analysis",
]
