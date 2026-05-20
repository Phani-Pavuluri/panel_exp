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

from panel_exp import __version__
from panel_exp.evidence_hash import (
    assignment_hash,
    assignment_to_json_dict,
    canonical_json,
    canonicalize,
    input_data_hash_from_wide,
    stable_hash,
)
from panel_exp.inference_result import InferenceResult
from panel_exp.spec import DesignSpec, spec_canonical_payload

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


def _freeze_mapping(data: Optional[Dict[str, Any]]) -> Mapping[str, Any]:
    return MappingProxyType(dict(canonicalize(data or {})))


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
            "design_name": self.design_name,
            "design_method": self.design_name,
            "assignment": assignment_json,
            "validation_summary": dict(self.validation_summary),
            "inference_metadata": dict(self.inference_metadata),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "artifacts": dict(self.artifacts),
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
        from panel_exp.evidence_hash import canonical_assignment

        canonical = canonical_assignment(assignment)
        merged_warnings = list(warnings or [])
        for w in spec.assumptions.get("warnings", []):
            if w not in merged_warnings:
                merged_warnings.append(str(w))
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
            validation_summary=_freeze_mapping(validation_summary),
            inference_metadata=_freeze_mapping(inference_metadata),
            warnings=tuple(merged_warnings),
            errors=tuple(errors or []),
            artifacts=_freeze_mapping(artifacts),
            diagnostics=_freeze_mapping(diagnostics),
        )


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
            "design_name": self.design_name,
            "design_method": self.design_name,
            "method": self.method,
            "inference_metadata": dict(self.inference_metadata),
            "validation_summary": dict(self.validation_summary),
            "assignment": assignment_to_json_dict(self.assignment)
            if self.assignment
            else {},
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "artifacts": dict(self.artifacts),
            "diagnostics": dict(self.diagnostics),
        }
        return _ordered_dict(payload, _EXPERIMENT_EVIDENCE_KEY_ORDER)

    def to_json(self, **kwargs: Any) -> str:
        kwargs.pop("sort_keys", None)
        indent = kwargs.pop("indent", None)
        if indent is not None:
            return json.dumps(self.to_dict(), indent=indent, **kwargs)
        return canonical_json(self.to_dict())


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
            "design_name": self.design_name,
            "design_method": self.design_name,
            "assignment": assignment_to_json_dict(self.assignment),
            "validation_summary": dict(self.validation_summary),
            "inference_metadata": dict(self.inference_metadata),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "artifacts": dict(self.artifacts),
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

        design_ev = DesignEvidence.from_assignment(
            spec,
            assignment,
            validation_summary=validation_summary,
            inference_metadata=inference_meta,
            warnings=warnings,
            errors=errors,
            artifacts=artifacts,
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
                inference_metadata=_freeze_mapping(inference_meta),
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


__all__ = [
    "EVIDENCE_VERSION",
    "DesignEvidence",
    "InferenceEvidence",
    "ExperimentEvidence",
    "input_data_hash_from_wide",
    "stable_hash",
]
