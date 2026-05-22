"""
Human-readable experiment readout card from design / inference evidence.

Summarizes lineage, validation, inference semantics, and maturity without
changing estimator behavior or claiming causal validity beyond tested assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from panel_exp.evidence import DesignEvidence, ExperimentEvidence

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


def _maturity_evidence_markdown(
    maturity_evidence: Mapping[str, Any],
) -> str:
    """Render optional maturity evidence block for the experiment card."""
    if not maturity_evidence:
        return ""
    lines: List[str] = [
        "## Maturity Evidence",
        "",
        f"- **Estimator:** {_as_str(maturity_evidence.get('estimator_name'))}",
        f"- **Catalog maturity (unchanged):** {_as_str(maturity_evidence.get('maturity'))}",
        f"- **Synthetic validation available:** "
        f"{'yes' if maturity_evidence.get('synthetic_validation_available') else 'no'}",
        f"- **Calibration report attached:** "
        f"{'yes' if maturity_evidence.get('calibration_available') else 'no'}",
    ]
    scenarios = maturity_evidence.get("scenarios_run") or ()
    if scenarios:
        lines.append("- **Recovery scenarios run:**")
        for sc in _as_list(scenarios):
            lines.append(f"  - {sc}")
    else:
        lines.append("- **Recovery scenarios run:** *none attached*")
    for label, key in (
        ("False positive rate", "false_positive_rate"),
        ("Coverage under null", "coverage_under_null"),
        ("Power", "power"),
        ("Recovery success rate", "recovery_success_rate"),
    ):
        val = maturity_evidence.get(key)
        if val is None:
            text = "n/a"
        elif isinstance(val, (int, float)) and val == val:
            text = f"{float(val):.3f}"
        else:
            text = _as_str(val, "n/a")
        lines.append(f"- **{label}:** {text}")
    summary = maturity_evidence.get("evidence_summary")
    if summary:
        lines.extend(["", f"> {summary}"])
    me_warnings = maturity_evidence.get("warnings") or ()
    if me_warnings:
        lines.append("")
        lines.append("**Maturity evidence warnings:**")
        for w in _as_list(me_warnings):
            lines.append(f"- {w}")
    return "\n".join(lines)


def _readiness_assessment_markdown(
    readiness_assessment: Mapping[str, Any],
) -> str:
    """Render optional decision-readiness block (advisory, non-blocking)."""
    if not readiness_assessment:
        return ""
    from panel_exp.policy.readiness import ReadinessAssessment, ReadinessStatus

    try:
        status = ReadinessStatus(str(readiness_assessment.get("status", "")))
    except ValueError:
        status = ReadinessStatus.READY_WITH_REVIEW
    thresholds_raw = readiness_assessment.get("thresholds_used") or {}
    if isinstance(thresholds_raw, Mapping):
        thresholds_used = tuple(thresholds_raw.items())
    else:
        thresholds_used = ()
    assessment = ReadinessAssessment(
        status=status,
        reasons=tuple(readiness_assessment.get("reasons") or ()),
        warnings=tuple(readiness_assessment.get("warnings") or ()),
        recommended_actions=tuple(
            readiness_assessment.get("recommended_actions") or ()
        ),
        inputs_used=tuple(readiness_assessment.get("inputs_used") or ()),
        profile_name=str(readiness_assessment.get("profile_name") or "standard"),
        thresholds_used=thresholds_used,
    )
    return assessment.to_markdown()


def _interference_review_from_containers(
    inference_metadata: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> Dict[str, Any]:
    for container in (artifacts, inference_metadata):
        if not isinstance(container, Mapping):
            continue
        raw = container.get("interference_review")
        if isinstance(raw, Mapping):
            return dict(raw)
    return {}


def _format_geo_list(geos: Any) -> str:
    items = _as_list(geos)
    return ", ".join(items) if items else ""


def _power_run_payload_from_containers(
    inference_metadata: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> tuple[bool, Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Detect whether simulation power results were attached (not just interpretation rules).

    Returns ``(results_available, mde_semantics, aa_calibration)``.
    """
    from panel_exp.design.power import power_analysis_was_run

    for container in (artifacts, inference_metadata):
        if not isinstance(container, Mapping):
            continue
        semantics = container.get("mde_semantics")
        if isinstance(semantics, Mapping) and power_analysis_was_run(semantics):
            cal = container.get("aa_calibration")
            return (
                True,
                dict(semantics),
                dict(cal) if isinstance(cal, Mapping) else None,
            )
        contract = container.get("power_contract")
        if isinstance(contract, Mapping) and contract.get("power_analysis_run"):
            sem = (
                dict(semantics)
                if isinstance(semantics, Mapping)
                else dict(contract)
            )
            cal = container.get("aa_calibration")
            return (
                True,
                sem,
                dict(cal) if isinstance(cal, Mapping) else None,
            )
    return False, {}, None


def _generic_power_interpretation_contract() -> Dict[str, Any]:
    """Package-default interpretation rules; does not imply a power study was run."""
    from panel_exp.design.power import MDE_SEMANTICS, build_power_contract

    return build_power_contract(MDE_SEMANTICS, power_analysis_run=False)


def _analysis_contract_from_metadata(
    inference_metadata: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> Dict[str, Any]:
    for container in (inference_metadata, artifacts):
        if not isinstance(container, Mapping):
            continue
        raw = container.get("analysis_contract")
        if isinstance(raw, Mapping):
            return dict(raw)
    return {}


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
    interference_review_assumption: str = _UNKNOWN
    interference_review_buffer_geos: str = ""
    interference_review_shared_market_risk: str = _UNKNOWN
    interference_review_contamination_risk: str = _UNKNOWN
    interference_review_spillover_direction: str = _UNKNOWN
    interference_review_warnings: Tuple[str, ...] = _EMPTY_LIST
    estimator_name: str = _UNKNOWN
    estimator_maturity: str = _UNKNOWN
    inference_mode: str = _UNKNOWN
    inference_mode_maturity: str = _UNKNOWN
    interval_type: str = _UNKNOWN
    intervals_available: Optional[bool] = None
    validation_metadata_summary: Dict[str, Any] = field(default_factory=dict)
    calibration_summary: str = ""
    maturity_evidence_summary: str = ""
    readiness_assessment_summary: str = ""
    target_estimand_label: str = _UNKNOWN
    uncertainty_contract_label: str = _UNKNOWN
    analysis_contract_warnings: Tuple[str, ...] = _EMPTY_LIST
    power_results_available: bool = False
    power_mde_type: str = _UNKNOWN
    power_simulation_based: Optional[bool] = None
    power_recommended_use: Tuple[str, ...] = _EMPTY_LIST
    power_not_recommended_for: Tuple[str, ...] = _EMPTY_LIST
    power_interpretation_warnings: Tuple[str, ...] = _EMPTY_LIST
    power_results_mde_percent: Optional[str] = None
    power_results_mde_kpi: Optional[str] = None
    power_results_aa_fpr: Optional[str] = None
    power_run_warnings: Tuple[str, ...] = _EMPTY_LIST
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
            "interference_review_assumption": self.interference_review_assumption,
            "interference_review_buffer_geos": self.interference_review_buffer_geos,
            "interference_review_shared_market_risk": self.interference_review_shared_market_risk,
            "interference_review_contamination_risk": self.interference_review_contamination_risk,
            "interference_review_spillover_direction": self.interference_review_spillover_direction,
            "interference_review_warnings": list(self.interference_review_warnings),
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
            "maturity_evidence_summary": self.maturity_evidence_summary,
            "readiness_assessment_summary": self.readiness_assessment_summary,
            "target_estimand_label": self.target_estimand_label,
            "uncertainty_contract_label": self.uncertainty_contract_label,
            "analysis_contract_warnings": list(self.analysis_contract_warnings),
            "power_results_available": self.power_results_available,
            "power_mde_type": self.power_mde_type,
            "power_simulation_based": self.power_simulation_based,
            "power_recommended_use": list(self.power_recommended_use),
            "power_not_recommended_for": list(self.power_not_recommended_for),
            "power_interpretation_warnings": list(self.power_interpretation_warnings),
            "power_results_mde_percent": self.power_results_mde_percent,
            "power_results_mde_kpi": self.power_results_mde_kpi,
            "power_results_aa_fpr": self.power_results_aa_fpr,
            "power_run_warnings": list(self.power_run_warnings),
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
        lines.extend(["", "## Estimand and Uncertainty Contract", ""])
        lines.append("")
        lines.append("Target estimand:")
        lines.append(self.target_estimand_label)
        lines.append("")
        lines.append("Uncertainty:")
        lines.append(self.uncertainty_contract_label)
        if self.analysis_contract_warnings:
            lines.append("")
            lines.append("Warning:")
            for w in self.analysis_contract_warnings:
                lines.append(w)
        lines.extend(["", "## Interference Review", ""])
        lines.append(f"- **Assumption:** {self.interference_review_assumption}")
        buffers = self.interference_review_buffer_geos or "*none documented*"
        lines.append(f"- **Buffer geos:** {buffers}")
        lines.append(
            f"- **Shared market risk:** {self.interference_review_shared_market_risk}"
        )
        lines.append(
            f"- **Contamination risk:** {self.interference_review_contamination_risk}"
        )
        lines.append(
            f"- **Expected spillover direction:** {self.interference_review_spillover_direction}"
        )
        if self.interference_review_warnings:
            lines.append("- **Warnings:**")
            for w in self.interference_review_warnings:
                lines.append(f"  - {w}")
        lines.append("")
        lines.append(
            "_This package records interference assumptions but does not estimate "
            "spillover effects._"
        )
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
        lines.extend(["", "## Power and MDE Contract", ""])
        lines.append("")
        lines.append(
            "> Interpretation rules below apply when using ``PowerAnalysis``; "
            "they do **not** mean a power study was run for this evidence record."
        )
        lines.extend(["", "### Interpretation rules", ""])
        lines.append(f"- **MDE type (if used):** {self.power_mde_type}")
        if self.power_simulation_based is None:
            lines.append("- **Simulation-based planning:** unknown")
        else:
            lines.append(
                "- **Simulation-based planning:** "
                f"{'yes' if self.power_simulation_based else 'no'}"
            )
        if self.power_simulation_based is None:
            lines.append("- **Classical analytic power:** unknown")
        else:
            lines.append(
                f"- **Classical analytic power:** "
                f"{'no' if self.power_simulation_based else 'yes'}"
            )
        if self.power_recommended_use:
            lines.append("- **Recommended uses:**")
            for use in self.power_recommended_use:
                lines.append(f"  - {use}")
        if self.power_not_recommended_for:
            lines.append("- **Not recommended for:**")
            for item in self.power_not_recommended_for:
                lines.append(f"  - {item}")
        if self.power_interpretation_warnings:
            lines.append("- **Interpretation warnings:**")
            for w in self.power_interpretation_warnings:
                lines.append(f"  - {w}")
        lines.extend(["", "### Power analysis status", ""])
        if self.power_results_available:
            lines.append("- **Power results attached:** yes")
            lines.extend(["", "### Power results (this run)", ""])
            if self.power_results_mde_percent is not None:
                lines.append(
                    f"- **MDE percent (simulation):** {self.power_results_mde_percent}"
                )
            if self.power_results_mde_kpi is not None:
                lines.append(
                    f"- **MDE KPI cumulative (simulation):** {self.power_results_mde_kpi}"
                )
            if self.power_results_aa_fpr is not None:
                lines.append(
                    f"- **Null-effect FPR (A/A calibration):** {self.power_results_aa_fpr}"
                )
            if self.power_run_warnings:
                lines.append("- **Run-specific warnings:**")
                for w in self.power_run_warnings:
                    lines.append(f"  - {w}")
        else:
            lines.append("- **Power results attached:** no")
            lines.append(
                "- *No simulation-based power analysis results are attached to "
                "this evidence record.*"
            )
        lines.append("")
        lines.append(
            "_When results are attached, they are planning diagnostics only—not "
            "guaranteed detection probabilities._"
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
        if self.maturity_evidence_summary:
            lines.extend(["", self.maturity_evidence_summary.strip()])
        if self.readiness_assessment_summary:
            lines.extend(["", self.readiness_assessment_summary.strip()])
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

    from panel_exp.validation.calibration_report import (
        calibration_markdown_from_mapping,
    )

    maturity_evidence = artifacts.get("maturity_evidence")
    maturity_md = ""
    if isinstance(maturity_evidence, Mapping):
        maturity_md = _maturity_evidence_markdown(maturity_evidence)
    elif isinstance(inference_metadata.get("maturity_evidence"), Mapping):
        maturity_md = _maturity_evidence_markdown(
            inference_metadata["maturity_evidence"]
        )

    readiness_raw = artifacts.get("readiness_assessment")
    if not isinstance(readiness_raw, Mapping):
        readiness_raw = inference_metadata.get("readiness_assessment")
    readiness_md = ""
    if isinstance(readiness_raw, Mapping):
        readiness_md = _readiness_assessment_markdown(readiness_raw)

    contract = _analysis_contract_from_metadata(meta, artifacts)
    if not contract:
        from panel_exp.evidence import build_analysis_contract

        contract = build_analysis_contract(
            inference_metadata=meta,
            estimator_name=estimator_name if estimator_name != _UNKNOWN else None,
        )
    target_label = _as_str(
        contract.get("target_estimand_label") or contract.get("target_estimand")
    )
    uncertainty_label = _as_str(
        contract.get("uncertainty_contract_label")
        or contract.get("uncertainty_contract")
    )
    contract_warnings = tuple(_as_list(contract.get("notes")))

    review = _interference_review_from_containers(meta, artifacts)
    if review:
        ir_assumption = _as_str(review.get("assumption"))
        ir_buffers = _format_geo_list(review.get("buffer_geos"))
        ir_shared = _as_str(review.get("shared_market_risk"))
        ir_contam = _as_str(review.get("contamination_risk"))
        ir_direction = _as_str(review.get("expected_spillover_direction"))
        ir_warnings = tuple(_as_list(review.get("review_warnings")))
    else:
        ir_assumption = _as_str(meta.get("interference_assumption"))
        ir_buffers = ""
        ir_shared = _UNKNOWN
        ir_contam = _UNKNOWN
        ir_direction = _UNKNOWN
        ir_warnings = _EMPTY_LIST
        if ir_assumption in (_UNKNOWN, "unknown"):
            ir_warnings = (
                "Unknown interference assumption limits causal interpretation",
            )

    interpretation = _generic_power_interpretation_contract()
    power_results_available, run_semantics, aa_cal = _power_run_payload_from_containers(
        meta, artifacts
    )
    pc_mde_type = _as_str(interpretation.get("mde_type"))
    pc_sim = interpretation.get("simulation_based")
    power_simulation_based: Optional[bool]
    if pc_sim is None:
        power_simulation_based = None
    else:
        power_simulation_based = bool(pc_sim)
    pc_recommended = tuple(_as_list(interpretation.get("recommended_use")))
    pc_not_recommended = tuple(_as_list(interpretation.get("not_recommended_for")))
    pc_interp_warnings = tuple(_as_list(interpretation.get("warnings")))

    power_results_mde_percent: Optional[str] = None
    power_results_mde_kpi: Optional[str] = None
    power_results_aa_fpr: Optional[str] = None
    power_run_warnings: Tuple[str, ...] = _EMPTY_LIST
    if power_results_available:
        if run_semantics.get("mde_percent") is not None:
            power_results_mde_percent = str(run_semantics.get("mde_percent"))
        if run_semantics.get("mde_kpi_cumulative") is not None:
            power_results_mde_kpi = str(run_semantics.get("mde_kpi_cumulative"))
        if aa_cal and aa_cal.get("false_positive_rate") is not None:
            power_results_aa_fpr = f"{float(aa_cal['false_positive_rate']):.4f}"
        run_warns: List[str] = []
        if aa_cal:
            run_warns.extend(_as_list(aa_cal.get("warnings")))
        attached_pc = artifacts.get("power_contract")
        if not isinstance(attached_pc, Mapping):
            attached_pc = meta.get("power_contract")
        if isinstance(attached_pc, Mapping) and attached_pc.get("power_analysis_run"):
            generic_set = set(pc_interp_warnings)
            for w in _as_list(attached_pc.get("warnings")):
                if w not in generic_set and w not in run_warns:
                    run_warns.append(w)
        power_run_warnings = tuple(run_warns)

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
        maturity_evidence_summary=maturity_md,
        readiness_assessment_summary=readiness_md,
        target_estimand_label=target_label,
        uncertainty_contract_label=uncertainty_label,
        analysis_contract_warnings=contract_warnings,
        interference_review_assumption=ir_assumption,
        interference_review_buffer_geos=ir_buffers,
        interference_review_shared_market_risk=ir_shared,
        interference_review_contamination_risk=ir_contam,
        interference_review_spillover_direction=ir_direction,
        interference_review_warnings=ir_warnings,
        power_results_available=power_results_available,
        power_mde_type=pc_mde_type,
        power_simulation_based=power_simulation_based,
        power_recommended_use=pc_recommended,
        power_not_recommended_for=pc_not_recommended,
        power_interpretation_warnings=pc_interp_warnings,
        power_results_mde_percent=power_results_mde_percent,
        power_results_mde_kpi=power_results_mde_kpi,
        power_results_aa_fpr=power_results_aa_fpr,
        power_run_warnings=power_run_warnings,
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
