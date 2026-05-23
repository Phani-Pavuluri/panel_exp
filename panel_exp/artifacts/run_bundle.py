"""
Portable JSON/markdown export for experiment run readout artifacts.

Additive export only; does not change estimators, validation, or readiness rules.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from panel_exp.artifacts.experiment_card import ExperimentCard
from panel_exp.evidence import DesignEvidence, ExperimentEvidence
from panel_exp.evidence_hash import canonicalize

BUNDLE_VERSION = "1.0"

_BUNDLE_KEY_ORDER: Tuple[str, ...] = (
    "bundle_version",
    "created_at",
    "experiment_id",
    "lineage",
    "warnings",
    "errors",
    "evidence",
    "experiment_card",
    "experiment_card_markdown",
    "calibration_report",
    "maturity_evidence",
    "readiness_assessment",
    "interference_review",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _ordered_dict(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    seen: set[str] = set()
    for key in _BUNDLE_KEY_ORDER:
        if key in payload:
            out[key] = payload[key]
            seen.add(key)
    for key in sorted(payload.keys()):
        if key not in seen:
            out[key] = payload[key]
    return out


def _plain_copy(value: Any) -> Any:
    """Deep copy to plain JSON-friendly structures without mutating inputs."""
    if value is None:
        return None
    if isinstance(value, Mapping):
        return {str(k): _plain_copy(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain_copy(v) for v in value]
    return value


def _serialize_component(value: Any) -> Optional[Dict[str, Any]]:
    if value is None:
        return None
    if hasattr(value, "to_dict"):
        copied = value.to_dict()
        return _plain_copy(copied) if isinstance(copied, dict) else None
    if isinstance(value, Mapping):
        return _plain_copy(dict(value))
    return None


def _merge_unique_strings(
    *sources: Optional[Sequence[str]],
) -> Tuple[str, ...]:
    seen: List[str] = []
    for source in sources:
        if not source:
            continue
        for item in source:
            text = str(item).strip()
            if text and text not in seen:
                seen.append(text)
    return tuple(seen)


def _lineage_from_evidence(
    evidence: Optional[Union[DesignEvidence, ExperimentEvidence, Mapping[str, Any]]],
) -> Dict[str, Any]:
    if evidence is None:
        return {}
    if isinstance(evidence, (DesignEvidence, ExperimentEvidence)):
        return {
            "evidence_version": evidence.evidence_version,
            "spec_hash": evidence.spec_hash,
            "assignment_hash": evidence.assignment_hash,
            "input_structure_hash": evidence.input_structure_hash,
            "package_version": evidence.package_version,
            "code_version": evidence.code_version,
        }
    if isinstance(evidence, Mapping):
        data = dict(evidence)
        return {
            k: data[k]
            for k in (
                "evidence_version",
                "spec_hash",
                "assignment_hash",
                "input_structure_hash",
                "input_data_hash",
                "package_version",
                "code_version",
            )
            if k in data and data[k] is not None
        }
    return {}


def _experiment_id_from_inputs(
    evidence: Optional[Any],
    experiment_card: Optional[Any],
) -> str:
    if evidence is not None:
        if isinstance(evidence, (DesignEvidence, ExperimentEvidence)):
            return evidence.experiment_id
        if isinstance(evidence, Mapping) and evidence.get("experiment_id"):
            return str(evidence["experiment_id"])
    if experiment_card is not None and hasattr(experiment_card, "experiment_id"):
        exp_id = getattr(experiment_card, "experiment_id", None)
        if exp_id and str(exp_id) != "unknown":
            return str(exp_id)
    if isinstance(experiment_card, Mapping) and experiment_card.get("experiment_id"):
        return str(experiment_card["experiment_id"])
    return ""


@dataclass(frozen=True)
class RunArtifactBundle:
    """Single portable export of decision/readout artifacts for one run."""

    bundle_version: str = BUNDLE_VERSION
    created_at: str = ""
    experiment_id: str = ""
    evidence: Optional[Dict[str, Any]] = None
    experiment_card: Optional[Dict[str, Any]] = None
    experiment_card_markdown: str = ""
    calibration_report: Optional[Dict[str, Any]] = None
    maturity_evidence: Optional[Dict[str, Any]] = None
    readiness_assessment: Optional[Dict[str, Any]] = None
    interference_review: Optional[Dict[str, Any]] = None
    warnings: Tuple[str, ...] = ()
    errors: Tuple[str, ...] = ()
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "bundle_version": self.bundle_version,
            "created_at": self.created_at,
            "experiment_id": self.experiment_id,
            "lineage": _plain_copy(dict(self.lineage)),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "evidence": self.evidence,
            "experiment_card": self.experiment_card,
            "experiment_card_markdown": self.experiment_card_markdown,
            "calibration_report": self.calibration_report,
            "maturity_evidence": self.maturity_evidence,
            "readiness_assessment": self.readiness_assessment,
            "interference_review": self.interference_review,
        }
        return _ordered_dict(payload)

    def to_json(self, *, indent: int = 2) -> str:
        canonical = canonicalize(self.to_dict())
        return json.dumps(canonical, indent=indent, sort_keys=True)

    def to_markdown(self) -> str:
        sections: List[str] = [
            "# Run Artifact Bundle",
            "",
            f"- **Bundle version:** {self.bundle_version}",
            f"- **Experiment ID:** {self.experiment_id or 'unknown'}",
            f"- **Created at:** {self.created_at or 'unknown'}",
            "",
        ]
        if self.lineage:
            sections.extend(["## Lineage", ""])
            for key in sorted(self.lineage.keys()):
                sections.append(f"- **{key}:** `{self.lineage[key]}`")
            sections.append("")
        if self.warnings:
            sections.extend(["## Warnings", ""])
            for w in self.warnings:
                sections.append(f"- {w}")
            sections.append("")
        if self.errors:
            sections.extend(["## Errors", ""])
            for e in self.errors:
                sections.append(f"- {e}")
            sections.append("")
        if self.experiment_card_markdown:
            sections.append(self.experiment_card_markdown.strip())
            sections.append("")
        else:
            sections.extend(["## Experiment Card", "", "*No experiment card markdown attached.*", ""])
        if self.interference_review:
            sections.extend(["## Interference Review", ""])
            ir = self.interference_review
            sections.append(f"- **Assumption:** {ir.get('assumption', 'unknown')}")
            buffers = ir.get("buffer_geos") or []
            if buffers:
                sections.append(f"- **Buffer geos:** {', '.join(map(str, buffers))}")
            else:
                sections.append("- **Buffer geos:** *none documented*")
            sections.append(
                f"- **Shared market risk:** {ir.get('shared_market_risk', 'unknown')}"
            )
            sections.append(
                f"- **Contamination risk:** {ir.get('contamination_risk', 'unknown')}"
            )
            sections.append(
                "- **Expected spillover direction:** "
                f"{ir.get('expected_spillover_direction', 'unknown')}"
            )
            ir_warnings = ir.get("review_warnings") or []
            if ir_warnings:
                sections.append("- **Warnings:**")
                for w in ir_warnings:
                    sections.append(f"  - {w}")
            sections.append("")
            sections.append(
                "_This package records interference assumptions but does not "
                "estimate spillover effects._"
            )
            sections.append("")
        for title, block in (
            ("Calibration Report", self.calibration_report),
            ("Maturity Evidence", self.maturity_evidence),
            ("Readiness Assessment", self.readiness_assessment),
        ):
            if not block:
                continue
            sections.extend([f"## {title}", ""])
            if title == "Calibration Report" and isinstance(block, Mapping):
                from panel_exp.validation.calibration_report import (
                    calibration_markdown_from_mapping,
                )

                text = calibration_markdown_from_mapping(block)
                if text:
                    sections.append(text.strip())
                    sections.append("")
                    continue
            if title == "Readiness Assessment" and isinstance(block, Mapping):
                from panel_exp.policy.readiness import ReadinessAssessment, ReadinessStatus

                try:
                    status = ReadinessStatus(str(block.get("status", "")))
                except ValueError:
                    status = ReadinessStatus.READY_WITH_REVIEW
                thresholds_raw = block.get("thresholds_used") or {}
                thresholds_used = (
                    tuple(thresholds_raw.items())
                    if isinstance(thresholds_raw, Mapping)
                    else ()
                )
                assessment = ReadinessAssessment(
                    status=status,
                    reasons=tuple(block.get("reasons") or ()),
                    warnings=tuple(block.get("warnings") or ()),
                    recommended_actions=tuple(block.get("recommended_actions") or ()),
                    inputs_used=tuple(block.get("inputs_used") or ()),
                    profile_name=str(block.get("profile_name") or "standard"),
                    thresholds_used=thresholds_used,
                )
                sections.append(assessment.to_markdown().strip())
                sections.append("")
                continue
            if title == "Maturity Evidence" and isinstance(block, Mapping):
                summary = block.get("evidence_summary")
                if summary:
                    sections.append(f"> {summary}")
                    sections.append("")
                for key in (
                    "estimator_name",
                    "maturity",
                    "false_positive_rate",
                    "coverage_under_null",
                    "power",
                    "recovery_success_rate",
                ):
                    if key in block:
                        sections.append(f"- **{key}:** {block[key]}")
                sections.append("")
                continue
            sections.append("```json")
            sections.append(json.dumps(_plain_copy(block), indent=2, sort_keys=True))
            sections.append("```")
            sections.append("")
        return "\n".join(sections).rstrip() + "\n"


def _interference_review_from_evidence(
    evidence: Optional[Any],
) -> Optional[Dict[str, Any]]:
    if evidence is None:
        return None
    if isinstance(evidence, (DesignEvidence, ExperimentEvidence)):
        artifacts = dict(evidence.artifacts)
        raw = artifacts.get("interference_review")
        if isinstance(raw, Mapping):
            return _plain_copy(dict(raw))
        meta = dict(evidence.inference_metadata)
        raw = meta.get("interference_review")
        if isinstance(raw, Mapping):
            return _plain_copy(dict(raw))
        return None
    if isinstance(evidence, Mapping):
        artifacts = evidence.get("artifacts") or {}
        if isinstance(artifacts, Mapping):
            raw = artifacts.get("interference_review")
            if isinstance(raw, Mapping):
                return _plain_copy(dict(raw))
        meta = evidence.get("inference_metadata") or {}
        if isinstance(meta, Mapping):
            raw = meta.get("interference_review")
            if isinstance(raw, Mapping):
                return _plain_copy(dict(raw))
    return None


def build_run_artifact_bundle(
    *,
    evidence: Optional[
        Union[DesignEvidence, ExperimentEvidence, Mapping[str, Any]]
    ] = None,
    experiment_card: Optional[Union[ExperimentCard, Mapping[str, Any]]] = None,
    calibration_report: Optional[Any] = None,
    maturity_evidence: Optional[Any] = None,
    readiness_assessment: Optional[Any] = None,
    interference_review: Optional[Union[Mapping[str, Any], Any]] = None,
    warnings: Optional[Sequence[str]] = None,
    errors: Optional[Sequence[str]] = None,
    created_at: Optional[str] = None,
) -> RunArtifactBundle:
    """
    Assemble a portable run bundle from optional readout components.

    Does not mutate input objects. Uses each component's ``to_dict()`` when available.
    """
    evidence_dict = _serialize_component(evidence)
    card_dict = _serialize_component(experiment_card)

    card_md = ""
    if isinstance(experiment_card, ExperimentCard):
        card_md = experiment_card.to_markdown()
    elif isinstance(experiment_card, Mapping):
        card_md = str(experiment_card.get("experiment_card_markdown") or "")

    evidence_warnings: Tuple[str, ...] = ()
    evidence_errors: Tuple[str, ...] = ()
    if isinstance(evidence, (DesignEvidence, ExperimentEvidence)):
        evidence_warnings = evidence.warnings
        evidence_errors = evidence.errors
    elif isinstance(evidence, Mapping):
        evidence_warnings = tuple(evidence.get("warnings") or ())
        evidence_errors = tuple(evidence.get("errors") or ())

    merged_warnings = _merge_unique_strings(evidence_warnings, warnings)
    merged_errors = _merge_unique_strings(evidence_errors, errors)

    lineage = _lineage_from_evidence(evidence)
    if evidence_dict and not lineage.get("spec_hash"):
        lineage = {**lineage, **_lineage_from_evidence(evidence_dict)}

    timestamp = created_at
    if not timestamp:
        if isinstance(evidence, (DesignEvidence, ExperimentEvidence)):
            timestamp = evidence.created_at
        elif isinstance(evidence, Mapping):
            timestamp = str(evidence.get("created_at") or "") or None
    if not timestamp:
        timestamp = _utc_now_iso()

    ir_dict = _serialize_component(interference_review)
    if ir_dict is None:
        ir_dict = _interference_review_from_evidence(evidence)

    return RunArtifactBundle(
        bundle_version=BUNDLE_VERSION,
        created_at=timestamp,
        experiment_id=_experiment_id_from_inputs(evidence, experiment_card),
        evidence=evidence_dict,
        experiment_card=card_dict,
        experiment_card_markdown=card_md,
        calibration_report=_serialize_component(calibration_report),
        maturity_evidence=_serialize_component(maturity_evidence),
        readiness_assessment=_serialize_component(readiness_assessment),
        interference_review=ir_dict,
        warnings=merged_warnings,
        errors=merged_errors,
        lineage=lineage,
    )


def write_run_artifact_bundle_json(
    bundle: RunArtifactBundle,
    path: Union[str, Path],
) -> Path:
    """Write bundle JSON to ``path`` (creates parent directories, UTF-8)."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(bundle.to_json(indent=2), encoding="utf-8")
    return out


def write_run_artifact_bundle_markdown(
    bundle: RunArtifactBundle,
    path: Union[str, Path],
) -> Path:
    """Write bundle markdown summary to ``path`` (creates parent directories, UTF-8)."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(bundle.to_markdown(), encoding="utf-8")
    return out


__all__ = [
    "BUNDLE_VERSION",
    "RunArtifactBundle",
    "build_run_artifact_bundle",
    "write_run_artifact_bundle_json",
    "write_run_artifact_bundle_markdown",
]
