"""
Local experiment evidence artifacts (auditable, JSON-serializable).

Does not replace external APIs; provides an offline audit trail.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from panel_exp import __version__
from panel_exp.inference_result import InferenceResult
from panel_exp.spec import DesignSpec


def _hash_assignment(assignment: Dict[str, List]) -> str:
    normalized = {k: sorted(str(u) for u in v) for k, v in sorted(assignment.items())}
    blob = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


@dataclass
class DesignEvidence:
    spec_hash: str
    assignment_hash: str
    package_version: str
    design_method: str
    assignment: Dict[str, List]
    validation_summary: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_assignment(
        cls,
        spec: DesignSpec,
        assignment: Dict[str, List],
        *,
        validation_summary: Optional[Dict[str, Any]] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
    ) -> "DesignEvidence":
        return cls(
            spec_hash=spec.content_hash(),
            assignment_hash=_hash_assignment(assignment),
            package_version=__version__,
            design_method=spec.design_method.value,
            assignment=assignment,
            validation_summary=validation_summary or {},
            diagnostics=diagnostics or {},
            warnings=warnings or [],
        )


@dataclass
class InferenceEvidence:
    spec_hash: str
    assignment_hash: str
    package_version: str
    method: str
    inference: Dict[str, Any]
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), **kwargs)


@dataclass
class ExperimentEvidence:
    design: DesignEvidence
    inference: Optional[InferenceEvidence] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"design": self.design.to_dict()}
        if self.inference is not None:
            out["inference"] = self.inference.to_dict()
        return out

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def build(
        cls,
        spec: DesignSpec,
        assignment: Dict[str, List],
        *,
        validation_summary: Optional[Dict[str, Any]] = None,
        inference_result: Optional[InferenceResult] = None,
        inference_method: Optional[str] = None,
        assignment_hash: Optional[str] = None,
    ) -> "ExperimentEvidence":
        design_ev = DesignEvidence.from_assignment(
            spec,
            assignment,
            validation_summary=validation_summary,
            warnings=list(spec.assumptions.get("warnings", [])),
        )
        inf_ev = None
        if inference_result is not None:
            inf_ev = InferenceEvidence(
                spec_hash=spec.content_hash(),
                assignment_hash=assignment_hash or design_ev.assignment_hash,
                package_version=__version__,
                method=inference_method or inference_result.method or "unknown",
                inference=inference_result.to_dict(),
                warnings=inference_result.warnings,
            )
        return cls(design=design_ev, inference=inf_ev)
