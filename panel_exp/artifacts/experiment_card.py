"""
Human-readable experiment readout card from design / inference evidence.

Summarizes lineage, validation, inference semantics, and maturity without
changing estimator behavior or claiming causal validity beyond tested assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from panel_exp.evidence import DesignEvidence, ExperimentEvidence
from panel_exp.validation.calibration_report import calibration_markdown_from_mapping

CARD_VERSION = "1.0"

_UNKNOWN = "unknown"
_EMPTY_LIST: Tuple[str, ...] = ()


def _as_str(value: Any, default: str = _UNKNOWN) -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if v is not None and str(v).strip()]
    return []


def _assignment_summary(assignment: Mapping[str, Tuple[str, ...]]) -> Dict[str, int]:
    if not assignment:
        return {}
    return {arm: len(units) for arm, units in sorted(assignment.items())}


def _plain_value(value: Any) -> Any:
    """Recursively copy mappings to plain dicts (evidence may use MappingProxyType)."""
    if isinstance(value, Mapping):
        return {str(k): _plain_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain_value(v) for v in value]
    return value


def _interference_from_validation(validation_summary: Mapping[str, Any]) -> str:
    checks = validation_summary.get("checks")
    if isinstance(checks, (list, tuple)):
        for check in checks:
            if not isinstance(check, Mapping):
                continue
            if check.get("metric") == "interference_assumption":
                return _as_str(check.get("message"), _UNKNOWN)
    for key in ("interference", "interference_assumption"):
        if key in validation_summary:
            return _as_str(validation_summary[key])
    return _UNKNOWN


def _spillover_available(
    validation_summary: Mapping[str, Any],
    inference_metadata: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> bool:
    keys = ("spillover", "spillover_metadata", "spillover_detected")
    for container in (validation_summary, inference_metadata, artifacts):
        if not isinstance(container, Mapping):
            continue
        for key in keys:
            if key in container:
                return True
        for subkey in container:
            if "spillover" in str(subkey).lower():
                return True
    return False


def _validation_metadata_summary(
    inference_metadata: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> Dict[str, Any]:
    vm = inference_metadata.get("validation_metadata")
    if isinstance(vm, Mapping) and vm:
        return dict(vm)
    card_vm = artifacts.get("validation_metadata")
    if isinstance(card_vm, Mapping):
        return dict(card_vm)
    return {}


@dataclass(frozen=True)
class ExperimentCard:
    """
    Human-readable experiment summary card (version ``CARD_VERSION``).

    Missing optional fields use ``unknown`` or empty collections; builders never
    require inference-phase evidence.
    """

    card_version: str = CARD_VERSION
    experiment_id: str = _UNKNOWN
    created_at: str = _UNKNOWN
    design_name: str = _UNKNOWN
    assignment_summary: Dict[str, int] = field(default_factory=dict)
    validation_summary: Dict[str, Any] = field(default_factory=dict)
    warnings: Tuple[str, ...] = _EMPTY_LIST
    errors: Tuple[str, ...] = _EMPTY_LIST
    interference_assumption: str = _UNKNOWN
    spillover_metadata_available: bool = False
    estimator_name: str = _UNKNOWN
    estimator_maturity: str = _UNKNOWN
    inference_mode: str = _UNKNOWN
    inference_mode_maturity: str = _UNKNOWN
    interval_type: str = _UNKNOWN
    intervals_available: Optional[bool] = None
    validation_metadata_summary: Dict[str, Any] = field(default_factory=dict)
    calibration_summary: str = ""
    spec_hash: str = _UNKNOWN
    assignment_hash: str = _UNKNOWN
    input_structure_hash: str = _UNKNOWN
    evidence_version: str = _UNKNOWN

    def to_dict(self) -> Dict[str, Any]:
        return {
            "card_version": self.card_version,
            "experiment_id": self.experiment_id,
            "created_at": self.created_at,
            "design_name": self.design_name,
            "assignment_summary": dict(self.assignment_summary),
            "validation_summary": _plain_value(self.validation_summary),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "interference_assumption": self.interference_assumption,
            "spillover_metadata_available": self.spillover_metadata_available,
            "estimator_name": self.estimator_name,
            "estimator_maturity": self.estimator_maturity,
            "inference_mode": self.inference_mode,
            "inference_mode_maturity": self.inference_mode_maturity,
            "interval_type": self.interval_type,
            "intervals_available": self.intervals_available,
            "validation_metadata_summary": _plain_value(
                self.validation_metadata_summary
            ),
            "calibration_summary": self.calibration_summary,
            "spec_hash": self.spec_hash,
            "assignment_hash": self.assignment_hash,
            "input_structure_hash": self.input_structure_hash,
            "evidence_version": self.evidence_version,
        }

    def to_markdown(self) -> str:
        lines: List[str] = [
            "# Experiment Card",
            "",
            "> This card summarizes recorded evidence and assumptions. It does "
            "not establish causal validity beyond the design and analysis "
            "artifacts listed below.",
            "",
            "## Summary",
            "",
            f"- **Experiment ID:** {self.experiment_id}",
            f"- **Created at:** {self.created_at}",
            f"- **Design:** {self.design_name}",
            f"- **Evidence schema:** {self.evidence_version}",
            f"- **Card version:** {self.card_version}",
            "",
            "## Design",
            "",
            f"- **Design method:** {self.design_name}",
            "",
            "## Assignment",
            "",
        ]
        if self.assignment_summary:
            for arm, count in sorted(self.assignment_summary.items()):
                lines.append(f"- **{arm}:** {count} unit(s)")
        else:
            lines.append("- *No assignment summary recorded.*")
        lines.extend(["", "## Validation", ""])
        if self.validation_summary:
            status = _as_str(self.validation_summary.get("status"), _UNKNOWN)
            lines.append(f"- **Validation status:** {status}")
            blocking = self.validation_summary.get("blocking_failures")
            if blocking:
                lines.append("- **Blocking failures:**")
                for item in _as_list(blocking):
                    lines.append(f"  - {item}")
        else:
            lines.append("- *No validation summary recorded.*")
        lines.extend(["", "## Interference Assumptions", ""])
        lines.append(f"- **Declared / checked assumption:** {self.interference_assumption}")
        spill = "yes" if self.spillover_metadata_available else "no"
        lines.append(f"- **Spillover metadata present:** {spill}")
        lines.extend(["", "## Inference", ""])
        lines.append(f"- **Inference mode:** {self.inference_mode}")
        lines.append(f"- **Interval type:** {self.interval_type}")
        if self.intervals_available is None:
            lines.append("- **Intervals available:** unknown")
        else:
            lines.append(
                f"- **Intervals available:** {'yes' if self.intervals_available else 'no'}"
            )
        lines.extend(
            [
                "",
                "## Estimator / Inference Maturity",
                "",
                f"- **Estimator:** {self.estimator_name}",
                f"- **Estimator maturity:** {self.estimator_maturity}",
                f"- **Inference mode maturity:** {self.inference_mode_maturity}",
                "",
                "## Validation Evidence",
                "",
            ]
        )
        if self.validation_metadata_summary:
            scenarios = self.validation_metadata_summary.get("validation_scenarios_run")
            if scenarios:
                lines.append("- **Recovery scenarios run:**")
                for sc in _as_list(scenarios):
                    lines.append(f"  - {sc}")
            for label, key in (
                ("Bias", "validation_bias"),
                ("Coverage", "validation_coverage"),
                ("FPR", "validation_fpr"),
                ("Power", "validation_power"),
            ):
                block = self.validation_metadata_summary.get(key)
                if isinstance(block, Mapping) and block:
                    lines.append(f"- **{label} (by scenario):**")
                    for sc_name in sorted(block.keys()):
                        lines.append(f"  - `{sc_name}`: {block[sc_name]}")
        else:
            lines.append(
                "- *No synthetic recovery validation metadata attached to this run.*"
            )
        if self.calibration_summary:
            lines.append("")
            lines.append(self.calibration_summary.strip())
        lines.extend(
            [
                "",
                "## Warnings and Limitations",
                "",
            ]
        )
        if self.warnings:
            lines.append("### Warnings")
            for w in self.warnings:
                lines.append(f"- **WARNING:** {w}")
            lines.append("")
        else:
            lines.append("- *No warnings recorded.*")
            lines.append("")
        if self.errors:
            lines.append("### Errors / blocking issues")
            for e in self.errors:
                lines.append(f"- **ERROR:** {e}")
            lines.append("")
        else:
            lines.append("- *No errors recorded.*")
            lines.append("")
        lines.append(
            "_Limitation: Maturity ratings reflect operational readiness under "
            "documented tests, not proof of correct causal inference for this dataset._"
        )
        lines.extend(
            [
                "",
                "## Lineage",
                "",
                f"- **spec_hash:** `{self.spec_hash}`",
                f"- **assignment_hash:** `{self.assignment_hash}`",
                f"- **input_structure_hash:** `{self.input_structure_hash}`",
                "",
            ]
        )
        return "\n".join(lines)


def _card_from_common(
    *,
    evidence_version: str,
    experiment_id: str,
    created_at: str,
    design_name: str,
    assignment: Mapping[str, Tuple[str, ...]],
    validation_summary: Mapping[str, Any],
    inference_metadata: Mapping[str, Any],
    warnings: Tuple[str, ...],
    errors: Tuple[str, ...],
    artifacts: Mapping[str, Any],
    spec_hash: str,
    assignment_hash: str,
    input_structure_hash: Optional[str],
    inference_mode: Optional[str] = None,
) -> ExperimentCard:
    meta = dict(inference_metadata) if inference_metadata else {}
    interval_type = _as_str(meta.get("path_interval_type") or meta.get("interval_type"))
    intervals_raw = meta.get("intervals_available")
    intervals_available: Optional[bool]
    if intervals_raw is None:
        intervals_available = None
    else:
        intervals_available = bool(intervals_raw)

    estimator_name = _UNKNOWN
    for key in ("estimator_name", "estimator", "method"):
        if key in meta and meta[key]:
            estimator_name = _as_str(meta[key])
            break

    return ExperimentCard(
        experiment_id=_as_str(experiment_id),
        created_at=_as_str(created_at),
        design_name=_as_str(design_name),
        assignment_summary=_assignment_summary(assignment),
        validation_summary=_plain_value(validation_summary) if validation_summary else {},
        warnings=warnings,
        errors=errors,
        interference_assumption=_interference_from_validation(validation_summary),
        spillover_metadata_available=_spillover_available(
            validation_summary, meta, artifacts
        ),
        estimator_name=estimator_name,
        estimator_maturity=_as_str(meta.get("estimator_maturity")),
        inference_mode=_as_str(inference_mode or meta.get("method")),
        inference_mode_maturity=_as_str(meta.get("inference_mode_maturity")),
        interval_type=interval_type,
        intervals_available=intervals_available,
        validation_metadata_summary=_plain_value(
            _validation_metadata_summary(meta, artifacts)
        ),
        calibration_summary=calibration_markdown_from_mapping(
            artifacts.get("calibration_report")
        ),
        spec_hash=_as_str(spec_hash),
        assignment_hash=_as_str(assignment_hash),
        input_structure_hash=_as_str(input_structure_hash or _UNKNOWN),
        evidence_version=_as_str(evidence_version),
    )


def build_experiment_card(
    evidence: Union[ExperimentEvidence, DesignEvidence],
) -> ExperimentCard:
    """
    Build a readout card from frozen evidence without mutating ``evidence``.

    Accepts combined :class:`~panel_exp.evidence.ExperimentEvidence` or
    design-only :class:`~panel_exp.evidence.DesignEvidence`.
    """
    if isinstance(evidence, ExperimentEvidence):
        inf_mode = evidence.inference.method if evidence.inference is not None else None
        inf_meta = dict(evidence.inference_metadata)
        if evidence.inference is not None:
            inf_meta = {**inf_meta, **dict(evidence.inference.inference_metadata)}
        return _card_from_common(
            evidence_version=evidence.evidence_version,
            experiment_id=evidence.experiment_id,
            created_at=evidence.created_at,
            design_name=evidence.design_name,
            assignment=evidence.assignment,
            validation_summary=evidence.validation_summary,
            inference_metadata=inf_meta,
            warnings=evidence.warnings,
            errors=evidence.errors,
            artifacts=evidence.artifacts,
            spec_hash=evidence.spec_hash,
            assignment_hash=evidence.assignment_hash,
            input_structure_hash=evidence.input_structure_hash,
            inference_mode=inf_mode,
        )

    return _card_from_common(
        evidence_version=evidence.evidence_version,
        experiment_id=evidence.experiment_id,
        created_at=evidence.created_at,
        design_name=evidence.design_name,
        assignment=evidence.assignment,
        validation_summary=evidence.validation_summary,
        inference_metadata=evidence.inference_metadata,
        warnings=evidence.warnings,
        errors=evidence.errors,
        artifacts=evidence.artifacts,
        spec_hash=evidence.spec_hash,
        assignment_hash=evidence.assignment_hash,
        input_structure_hash=evidence.input_structure_hash,
        inference_mode=None,
    )


def attach_experiment_card_markdown(
    artifacts: Dict[str, Any],
    evidence: Union[ExperimentEvidence, DesignEvidence],
) -> str:
    """
    Add ``experiment_card_markdown`` to a mutable artifacts dict (additive only).

    Returns the markdown string. Does not modify ``evidence``.
    """
    markdown = build_experiment_card(evidence).to_markdown()
    artifacts["experiment_card_markdown"] = markdown
    return markdown


__all__ = [
    "CARD_VERSION",
    "ExperimentCard",
    "attach_experiment_card_markdown",
    "build_experiment_card",
]
