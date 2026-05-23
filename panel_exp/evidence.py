"""
Local experiment evidence artifacts (auditable, JSON-serializable).

Immutable, deterministic hashes and canonical JSON for offline audit trails.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Tuple

try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("panel_exp")
except PackageNotFoundError:
    __version__ = "0.2.1"
from panel_exp.evidence_hash import (
    assignment_hash,
    assignment_to_json_dict,
    canonical_assignment,
    canonical_json,
    canonicalize,
    deep_freeze,
    input_data_hash_from_wide,
    input_structure_hash_from_wide,
)
from panel_exp.inference_result import InferenceResult, IntervalType
from panel_exp.spec import (
    DesignSpec,
    TargetEstimand,
    UncertaintyContract,
    build_interference_review,
    interference_evidence_metadata,
    target_estimand_label,
    uncertainty_contract_label,
)

# Evidence schema version.
# Version policy:
# - Patch: bugfix / serialization-only, backward compatible.
# - Minor: additive fields only, backward compatible.
# - Major: breaking schema change. Bump only when incompatible.
EVIDENCE_VERSION = "1.0"

# Top-level key order for deterministic JSON exports.
_EXPERIMENT_EVIDENCE_KEY_ORDER = (
    "evidence_version",
    "experiment_id",
    "created_at",
    "package_version",
    "code_version",
    "spec_hash",
    "assignment_hash",
    "input_data_hash",
    "input_structure_hash",
    "design_name",
    "assignment",
    "validation_summary",
    "inference_metadata",
    "warnings",
    "errors",
    "artifacts",
    "design",
    "inference",
    # Legacy aliases (backward-compatible metadata)
    "timestamp",
    "design_method",
    "diagnostics",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _code_version() -> Optional[str]:
    for key in ("PANEL_EXP_CODE_VERSION", "GIT_COMMIT", "GITHUB_SHA"):
        val = os.environ.get(key)
        if val and str(val).strip():
            return str(val).strip()
    return None


def _freeze_payload(data: Optional[Dict[str, Any]]) -> Mapping[str, Any]:
    """Canonicalize then recursively freeze nested dict/list structures."""
    frozen = deep_freeze(canonicalize(data or {}))
    if isinstance(frozen, Mapping):
        return frozen
    return MappingProxyType({})


_INTERVAL_TO_CONTRACT: Dict[IntervalType, UncertaintyContract] = {
    IntervalType.CONFIDENCE_INTERVAL: UncertaintyContract.CONFIDENCE_INTERVAL,
    IntervalType.CREDIBLE_INTERVAL: UncertaintyContract.CREDIBLE_INTERVAL,
    IntervalType.CONFORMAL_INTERVAL: UncertaintyContract.CONFORMAL_INTERVAL,
    IntervalType.PLACEBO_BAND: UncertaintyContract.PLACEBO_BAND,
    IntervalType.UNAVAILABLE: UncertaintyContract.NONE,
}


def _coerce_target_estimand(value: Any) -> TargetEstimand:
    if isinstance(value, TargetEstimand):
        return value
    if value is None or str(value).strip() == "":
        return TargetEstimand.UNKNOWN
    try:
        return TargetEstimand(str(value))
    except ValueError:
        return TargetEstimand.UNKNOWN


def _coerce_uncertainty_contract(value: Any) -> UncertaintyContract:
    if isinstance(value, UncertaintyContract):
        return value
    if value is None or str(value).strip() == "":
        return UncertaintyContract.UNKNOWN
    try:
        return UncertaintyContract(str(value))
    except ValueError:
        return UncertaintyContract.UNKNOWN


def _interval_type_from_metadata(meta: Mapping[str, Any]) -> Optional[IntervalType]:
    for key in ("path_interval_type", "interval_type", "effect_interval_type"):
        raw = meta.get(key)
        if raw is None:
            continue
        try:
            return IntervalType(str(raw))
        except ValueError:
            continue
    return None


def _infer_target_estimand(
    *,
    spec: Optional[DesignSpec],
    estimator_name: Optional[str],
    inference_metadata: Optional[Mapping[str, Any]],
    run_kwargs: Optional[Mapping[str, Any]],
) -> TargetEstimand:
    if spec is not None and spec.target_estimand != TargetEstimand.UNKNOWN:
        return spec.target_estimand

    meta = inference_metadata or {}
    declared = meta.get("target_estimand")
    if declared is not None:
        coerced = _coerce_target_estimand(declared)
        if coerced != TargetEstimand.UNKNOWN:
            return coerced

    assumptions = dict(spec.assumptions) if spec is not None else {}
    if str(assumptions.get("effect_type", "")).lower() == "relative":
        return TargetEstimand.RELATIVE_ATT_POST
    if str(assumptions.get("effect_type", "")).lower() == "absolute":
        return TargetEstimand.ABSOLUTE_ATT_POST

    est = (estimator_name or meta.get("estimator_name") or meta.get("estimator") or "").strip()
    run = run_kwargs or meta.get("run_kwargs") or {}
    if isinstance(run, Mapping):
        if str(run.get("multiple_treated", "")).lower() == "pooled":
            return TargetEstimand.POOLED_ATT
    if est in ("DID",):
        return TargetEstimand.POOLED_ATT

    return TargetEstimand.UNKNOWN


def _infer_uncertainty_contract(
    *,
    spec: Optional[DesignSpec],
    inference_result: Optional[InferenceResult],
    inference_metadata: Optional[Mapping[str, Any]],
) -> UncertaintyContract:
    if spec is not None and spec.uncertainty_contract != UncertaintyContract.UNKNOWN:
        return spec.uncertainty_contract

    meta = inference_metadata or {}
    declared = meta.get("uncertainty_contract")
    if declared is not None:
        coerced = _coerce_uncertainty_contract(declared)
        if coerced != UncertaintyContract.UNKNOWN:
            return coerced

    if inference_result is not None:
        path_type = inference_result.effective_path_interval_type()
        return _INTERVAL_TO_CONTRACT.get(path_type, UncertaintyContract.UNKNOWN)

    interval_type = _interval_type_from_metadata(meta)
    if interval_type is not None:
        return _INTERVAL_TO_CONTRACT.get(interval_type, UncertaintyContract.UNKNOWN)

    if meta.get("intervals_available") is False:
        return UncertaintyContract.NONE

    return UncertaintyContract.UNKNOWN


def build_analysis_contract(
    *,
    spec: Optional[DesignSpec] = None,
    inference_result: Optional[InferenceResult] = None,
    inference_metadata: Optional[Mapping[str, Any]] = None,
    estimator_name: Optional[str] = None,
    run_kwargs: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build prespecified estimand and uncertainty contract for evidence / cards.

    Conservative inference: explicit ``DesignSpec`` fields win; otherwise only
    obvious cases (e.g. pooled DID) are inferred; remaining fields stay
    ``unknown``.
    """
    meta = dict(inference_metadata) if inference_metadata else {}
    estimand = _infer_target_estimand(
        spec=spec,
        estimator_name=estimator_name,
        inference_metadata=meta,
        run_kwargs=run_kwargs,
    )
    uncertainty = _infer_uncertainty_contract(
        spec=spec,
        inference_result=inference_result,
        inference_metadata=meta,
    )
    notes: List[str] = []

    if estimand == TargetEstimand.UNKNOWN:
        notes.append("Effect interpretation not explicitly declared.")
    elif spec is not None and spec.target_estimand == TargetEstimand.UNKNOWN:
        notes.append(
            "Target estimand inferred from analysis context; "
            "set DesignSpec.target_estimand to prespecify."
        )

    if uncertainty == UncertaintyContract.UNKNOWN:
        notes.append("Uncertainty interpretation not explicitly declared.")
    elif spec is not None and spec.uncertainty_contract == UncertaintyContract.UNKNOWN:
        notes.append(
            "Uncertainty contract inferred from inference metadata; "
            "set DesignSpec.uncertainty_contract to prespecify."
        )

    if (
        spec is not None
        and spec.target_estimand != TargetEstimand.UNKNOWN
        and estimand != spec.target_estimand
    ):
        notes.append(
            f"Resolved estimand {estimand.value} differs from spec "
            f"prespecification {spec.target_estimand.value}."
        )
    if (
        spec is not None
        and spec.uncertainty_contract != UncertaintyContract.UNKNOWN
        and uncertainty != spec.uncertainty_contract
    ):
        notes.append(
            f"Resolved uncertainty {uncertainty.value} differs from spec "
            f"prespecification {spec.uncertainty_contract.value}."
        )

    return {
        "target_estimand": estimand.value,
        "uncertainty_contract": uncertainty.value,
        "target_estimand_label": target_estimand_label(estimand),
        "uncertainty_contract_label": uncertainty_contract_label(uncertainty),
        "notes": notes,
    }


def attach_power_contract_to_artifacts(
    artifacts: Dict[str, Any],
    contract: Optional[Mapping[str, Any]] = None,
    *,
    power_analysis: Optional[Any] = None,
    mde_semantics: Optional[Mapping[str, Any]] = None,
    aa_calibration: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Attach :data:`power_contract` to evidence artifacts (lazy import; additive only).
    """
    from panel_exp.design.power import attach_power_contract, build_power_contract

    if contract is not None:
        payload = dict(contract)
    elif power_analysis is not None:
        payload = dict(
            getattr(power_analysis, "power_contract", None)
            or build_power_contract(
                getattr(power_analysis, "mde_semantics", None),
                aa_calibration=getattr(power_analysis, "aa_calibration", None),
            )
        )
    else:
        payload = build_power_contract(mde_semantics, aa_calibration=aa_calibration)
    return attach_power_contract(artifacts, payload)


def attach_did_pretrend_contract(
    results_or_artifacts: Dict[str, Any],
    contract: Mapping[str, Any],
) -> Dict[str, Any]:
    """
    Attach DID parallel-trends contract metadata (additive; does not block runs).
    """
    payload = dict(contract)
    results_or_artifacts["did_pretrend_contract"] = payload
    meta = results_or_artifacts.get("inference_metadata")
    if isinstance(meta, dict):
        meta["did_pretrend_contract"] = payload
    else:
        results_or_artifacts["inference_metadata"] = {"did_pretrend_contract": payload}
    return results_or_artifacts


def attach_interference_review(
    results_or_artifacts: Dict[str, Any],
    review: Mapping[str, Any],
) -> Dict[str, Any]:
    """
    Attach an interference review packet to a mutable results or artifacts dict.

    Additive only; does not block execution or alter estimates.
    """
    payload = dict(review)
    results_or_artifacts["interference_review"] = payload
    return payload


def _merge_interference_review_artifact(
    artifacts: Optional[Dict[str, Any]],
    *,
    spec: DesignSpec,
    inference_metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    merged = dict(artifacts or {})
    review = build_interference_review(
        spec,
        existing_metadata=inference_metadata,
    )
    attach_interference_review(merged, review)
    return merged


def _merge_analysis_contract(
    inference_metadata: Dict[str, Any],
    *,
    spec: DesignSpec,
    inference_result: Optional[InferenceResult] = None,
    estimator_name: Optional[str] = None,
) -> Dict[str, Any]:
    merged = dict(inference_metadata)
    contract = build_analysis_contract(
        spec=spec,
        inference_result=inference_result,
        inference_metadata=merged,
        estimator_name=estimator_name,
    )
    merged["analysis_contract"] = contract
    return merged


def _ordered_dict(payload: Dict[str, Any], key_order: Tuple[str, ...]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    seen = set()
    for key in key_order:
        if key in payload:
            out[key] = payload[key]
            seen.add(key)
    for key in sorted(payload.keys()):
        if key not in seen:
            out[key] = payload[key]
    return out


@dataclass(frozen=True)
class DesignEvidence:
    """Design-phase evidence (assignment + validation)."""

    evidence_version: str
    experiment_id: str
    created_at: str
    package_version: str
    code_version: Optional[str]
    spec_hash: str
    assignment_hash: str
    input_data_hash: Optional[str]
    design_name: str
    assignment: Mapping[str, Tuple[str, ...]]
    validation_summary: Mapping[str, Any] = field(default_factory=dict)
    inference_metadata: Mapping[str, Any] = field(default_factory=dict)
    warnings: Tuple[str, ...] = ()
    errors: Tuple[str, ...] = ()
    artifacts: Mapping[str, Any] = field(default_factory=dict)
    diagnostics: Mapping[str, Any] = field(default_factory=dict)

    @property
    def design_method(self) -> str:
        """Legacy alias for ``design_name``."""
        return self.design_name

    @property
    def timestamp(self) -> str:
        """Legacy alias for ``created_at``."""
        return self.created_at

    @property
    def input_structure_hash(self) -> Optional[str]:
        """
        Structural panel fingerprint (index, columns, shape).

        Same value as ``input_data_hash``; the latter name is retained for
        backward compatibility but does not hash full data values.
        """
        return self.input_data_hash

    def to_dict(self) -> Dict[str, Any]:
        assignment_json = assignment_to_json_dict(self.assignment)
        payload = {
            "evidence_version": self.evidence_version,
            "experiment_id": self.experiment_id,
            "created_at": self.created_at,
            "timestamp": self.created_at,
            "package_version": self.package_version,
            "code_version": self.code_version,
            "spec_hash": self.spec_hash,
            "assignment_hash": self.assignment_hash,
            "input_data_hash": self.input_data_hash,
            "input_structure_hash": self.input_structure_hash,
            "design_name": self.design_name,
            "design_method": self.design_name,
            "assignment": assignment_json,
            "validation_summary": dict(self.validation_summary),
            "inference_metadata": canonicalize(self.inference_metadata),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "artifacts": canonicalize(self.artifacts),
            "diagnostics": dict(self.diagnostics),
        }
        return _ordered_dict(payload, _EXPERIMENT_EVIDENCE_KEY_ORDER)

    def to_json(self, **kwargs: Any) -> str:
        kwargs.pop("sort_keys", None)
        indent = kwargs.pop("indent", None)
        if indent is not None:
            return json.dumps(self.to_dict(), indent=indent, **kwargs)
        return canonical_json(self.to_dict())

    @classmethod
    def from_assignment(
        cls,
        spec: DesignSpec,
        assignment: Dict[str, List],
        *,
        validation_summary: Optional[Dict[str, Any]] = None,
        inference_metadata: Optional[Dict[str, Any]] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
        artifacts: Optional[Dict[str, Any]] = None,
        input_data_hash: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> "DesignEvidence":
        canonical = canonical_assignment(assignment)
        merged_warnings = list(warnings or [])
        for w in spec.assumptions.get("warnings", []):
            if w not in merged_warnings:
                merged_warnings.append(str(w))
        infer_meta = dict(inference_metadata or {})
        infer_meta.update(
            interference_evidence_metadata(
                spec,
                validation_warnings=[
                    w for w in merged_warnings if "interference" in w.lower()
                ],
            )
        )
        infer_meta = _merge_analysis_contract(infer_meta, spec=spec)
        frozen_artifacts = _merge_interference_review_artifact(
            dict(artifacts) if artifacts else {},
            spec=spec,
            inference_metadata=infer_meta,
        )
        return cls(
            evidence_version=EVIDENCE_VERSION,
            experiment_id=spec.experiment_id,
            created_at=created_at or _utc_now_iso(),
            package_version=__version__,
            code_version=_code_version(),
            spec_hash=spec.content_hash(),
            assignment_hash=assignment_hash(assignment),
            input_data_hash=input_data_hash,
            design_name=spec.design_method.value,
            assignment=MappingProxyType(dict(canonical)),
            validation_summary=_freeze_payload(validation_summary),
            inference_metadata=_freeze_payload(infer_meta),
            warnings=tuple(merged_warnings),
            errors=tuple(errors or []),
            artifacts=_freeze_payload(frozen_artifacts),
            diagnostics=_freeze_payload(diagnostics),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DesignEvidence":
        """Reconstruct from ``to_dict()`` / JSON without recomputing hashes or timestamps."""
        assignment_raw = data["assignment"]
        canonical = canonical_assignment(
            {k: list(v) for k, v in assignment_raw.items()}
        )
        input_hash = data.get("input_data_hash")
        if input_hash is None:
            input_hash = data.get("input_structure_hash")
        return cls(
            evidence_version=data["evidence_version"],
            experiment_id=data["experiment_id"],
            created_at=data["created_at"],
            package_version=data["package_version"],
            code_version=data.get("code_version"),
            spec_hash=data["spec_hash"],
            assignment_hash=data["assignment_hash"],
            input_data_hash=input_hash,
            design_name=data.get("design_name") or data.get("design_method"),
            assignment=MappingProxyType(dict(canonical)),
            validation_summary=_freeze_payload(data.get("validation_summary")),
            inference_metadata=_freeze_payload(data.get("inference_metadata")),
            warnings=tuple(data.get("warnings") or ()),
            errors=tuple(data.get("errors") or ()),
            artifacts=_freeze_payload(data.get("artifacts")),
            diagnostics=_freeze_payload(data.get("diagnostics")),
        )

    @classmethod
    def from_json(cls, payload: str) -> "DesignEvidence":
        return cls.from_dict(json.loads(payload))


@dataclass(frozen=True)
class InferenceEvidence:
    """Inference-phase evidence (typed interval metadata, no raw arrays)."""

    evidence_version: str
    experiment_id: str
    created_at: str
    package_version: str
    code_version: Optional[str]
    spec_hash: str
    assignment_hash: str
    input_data_hash: Optional[str]
    design_name: str
    method: str
    inference_metadata: Mapping[str, Any]
    validation_summary: Mapping[str, Any] = field(default_factory=dict)
    assignment: Mapping[str, Tuple[str, ...]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    warnings: Tuple[str, ...] = ()
    errors: Tuple[str, ...] = ()
    artifacts: Mapping[str, Any] = field(default_factory=dict)
    diagnostics: Mapping[str, Any] = field(default_factory=dict)

    @property
    def input_structure_hash(self) -> Optional[str]:
        return self.input_data_hash

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "evidence_version": self.evidence_version,
            "experiment_id": self.experiment_id,
            "created_at": self.created_at,
            "timestamp": self.created_at,
            "package_version": self.package_version,
            "code_version": self.code_version,
            "spec_hash": self.spec_hash,
            "assignment_hash": self.assignment_hash,
            "input_data_hash": self.input_data_hash,
            "input_structure_hash": self.input_structure_hash,
            "design_name": self.design_name,
            "design_method": self.design_name,
            "method": self.method,
            "inference_metadata": canonicalize(self.inference_metadata),
            "validation_summary": dict(self.validation_summary),
            "assignment": assignment_to_json_dict(self.assignment)
            if self.assignment
            else {},
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "artifacts": canonicalize(self.artifacts),
            "diagnostics": dict(self.diagnostics),
        }
        return _ordered_dict(payload, _EXPERIMENT_EVIDENCE_KEY_ORDER)

    def to_json(self, **kwargs: Any) -> str:
        kwargs.pop("sort_keys", None)
        indent = kwargs.pop("indent", None)
        if indent is not None:
            return json.dumps(self.to_dict(), indent=indent, **kwargs)
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InferenceEvidence":
        assignment_raw = data.get("assignment") or {}
        canonical = canonical_assignment(
            {k: list(v) for k, v in assignment_raw.items()}
        ) if assignment_raw else {}
        input_hash = data.get("input_data_hash")
        if input_hash is None:
            input_hash = data.get("input_structure_hash")
        return cls(
            evidence_version=data["evidence_version"],
            experiment_id=data["experiment_id"],
            created_at=data["created_at"],
            package_version=data["package_version"],
            code_version=data.get("code_version"),
            spec_hash=data["spec_hash"],
            assignment_hash=data["assignment_hash"],
            input_data_hash=input_hash,
            design_name=data.get("design_name") or data.get("design_method"),
            method=data["method"],
            inference_metadata=_freeze_payload(data.get("inference_metadata")),
            validation_summary=_freeze_payload(data.get("validation_summary")),
            assignment=MappingProxyType(dict(canonical)),
            warnings=tuple(data.get("warnings") or ()),
            errors=tuple(data.get("errors") or ()),
            artifacts=_freeze_payload(data.get("artifacts")),
            diagnostics=_freeze_payload(data.get("diagnostics")),
        )

    @classmethod
    def from_json(cls, payload: str) -> "InferenceEvidence":
        return cls.from_dict(json.loads(payload))


@dataclass(frozen=True)
class ExperimentEvidence:
    """Combined design (+ optional inference) experiment readout."""

    evidence_version: str
    experiment_id: str
    created_at: str
    package_version: str
    code_version: Optional[str]
    spec_hash: str
    assignment_hash: str
    input_data_hash: Optional[str]
    design_name: str
    assignment: Mapping[str, Tuple[str, ...]]
    validation_summary: Mapping[str, Any]
    inference_metadata: Mapping[str, Any]
    warnings: Tuple[str, ...]
    errors: Tuple[str, ...]
    artifacts: Mapping[str, Any]
    design: DesignEvidence
    inference: Optional[InferenceEvidence] = None

    @property
    def input_structure_hash(self) -> Optional[str]:
        return self.input_data_hash

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "evidence_version": self.evidence_version,
            "experiment_id": self.experiment_id,
            "created_at": self.created_at,
            "timestamp": self.created_at,
            "package_version": self.package_version,
            "code_version": self.code_version,
            "spec_hash": self.spec_hash,
            "assignment_hash": self.assignment_hash,
            "input_data_hash": self.input_data_hash,
            "input_structure_hash": self.input_structure_hash,
            "design_name": self.design_name,
            "design_method": self.design_name,
            "assignment": assignment_to_json_dict(self.assignment),
            "validation_summary": dict(self.validation_summary),
            "inference_metadata": canonicalize(self.inference_metadata),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "artifacts": canonicalize(self.artifacts),
            "design": self.design.to_dict(),
            "inference": self.inference.to_dict() if self.inference is not None else None,
        }
        return _ordered_dict(payload, _EXPERIMENT_EVIDENCE_KEY_ORDER)

    def to_json(self, **kwargs: Any) -> str:
        kwargs.pop("sort_keys", None)
        indent = kwargs.pop("indent", None)
        if indent is not None:
            return json.dumps(self.to_dict(), indent=indent, **kwargs)
        return canonical_json(self.to_dict())

    @classmethod
    def build(
        cls,
        spec: DesignSpec,
        assignment: Dict[str, List],
        *,
        validation_summary: Optional[Dict[str, Any]] = None,
        inference_result: Optional[InferenceResult] = None,
        inference_method: Optional[str] = None,
        assignment_hash_override: Optional[str] = None,
        input_data_hash: Optional[str] = None,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
        artifacts: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None,
    ) -> "ExperimentEvidence":
        created = created_at or _utc_now_iso()
        inference_meta: Dict[str, Any] = {}
        if inference_result is not None:
            inference_meta = dict(canonicalize(inference_result.to_dict()))

        inference_meta = _merge_analysis_contract(
            inference_meta,
            spec=spec,
            inference_result=inference_result,
            estimator_name=inference_method,
        )

        merged_artifacts = _merge_interference_review_artifact(
            dict(artifacts) if artifacts else {},
            spec=spec,
            inference_metadata=inference_meta,
        )
        design_ev = DesignEvidence.from_assignment(
            spec,
            assignment,
            validation_summary=validation_summary,
            inference_metadata=inference_meta,
            warnings=warnings,
            errors=errors,
            artifacts=merged_artifacts,
            input_data_hash=input_data_hash,
            created_at=created,
        )
        a_hash = assignment_hash_override or design_ev.assignment_hash

        inf_ev = None
        if inference_result is not None:
            inf_ev = InferenceEvidence(
                evidence_version=EVIDENCE_VERSION,
                experiment_id=spec.experiment_id,
                created_at=created,
                package_version=__version__,
                code_version=_code_version(),
                spec_hash=spec.content_hash(),
                assignment_hash=a_hash,
                input_data_hash=input_data_hash,
                design_name=spec.design_method.value,
                method=inference_method or inference_result.method or "unknown",
                inference_metadata=_freeze_payload(inference_meta),
                assignment=design_ev.assignment,
                warnings=tuple(inference_result.warnings),
            )

        return cls(
            evidence_version=EVIDENCE_VERSION,
            experiment_id=spec.experiment_id,
            created_at=created,
            package_version=__version__,
            code_version=_code_version(),
            spec_hash=design_ev.spec_hash,
            assignment_hash=a_hash,
            input_data_hash=input_data_hash,
            design_name=design_ev.design_name,
            assignment=design_ev.assignment,
            validation_summary=design_ev.validation_summary,
            inference_metadata=design_ev.inference_metadata,
            warnings=design_ev.warnings,
            errors=design_ev.errors,
            artifacts=design_ev.artifacts,
            design=design_ev,
            inference=inf_ev,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentEvidence":
        design = DesignEvidence.from_dict(data["design"])
        inference = None
        if data.get("inference") is not None:
            inference = InferenceEvidence.from_dict(data["inference"])
        input_hash = data.get("input_data_hash")
        if input_hash is None:
            input_hash = data.get("input_structure_hash")
        return cls(
            evidence_version=data["evidence_version"],
            experiment_id=data["experiment_id"],
            created_at=data["created_at"],
            package_version=data["package_version"],
            code_version=data.get("code_version"),
            spec_hash=data["spec_hash"],
            assignment_hash=data["assignment_hash"],
            input_data_hash=input_hash,
            design_name=data.get("design_name") or data.get("design_method"),
            assignment=design.assignment,
            validation_summary=design.validation_summary,
            inference_metadata=design.inference_metadata,
            warnings=design.warnings,
            errors=design.errors,
            artifacts=design.artifacts,
            design=design,
            inference=inference,
        )

    @classmethod
    def from_json(cls, payload: str) -> "ExperimentEvidence":
        return cls.from_dict(json.loads(payload))


__all__ = [
    "EVIDENCE_VERSION",
    "DesignEvidence",
    "InferenceEvidence",
    "ExperimentEvidence",
    "attach_did_pretrend_contract",
    "attach_interference_review",
    "attach_power_contract_to_artifacts",
    "build_analysis_contract",
    "input_data_hash_from_wide",
    "input_structure_hash_from_wide",
]
