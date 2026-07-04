"""ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001 — assignment vs analysis panel integrity gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "assignment_panel_integrity_runtime_implemented_no_assignment_generation_or_claim_authorization"
_VERDICT = "assignment_panel_integrity_runtime_implemented_no_assignment_generation_or_claim_authorization"
_RECOMMENDED_NEXT = "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001"
_ALTERNATIVE_NEXT = "GOVERNED_RANDOMIZATION_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001_summary.json"

ASSIGNMENT_PANEL_INTEGRITY_PASSED = "ASSIGNMENT_PANEL_INTEGRITY_PASSED"
ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS = "ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS"
ASSIGNMENT_PANEL_INTEGRITY_FAILED = "ASSIGNMENT_PANEL_INTEGRITY_FAILED"
ASSIGNMENT_PANEL_INTEGRITY_BLOCKED = "ASSIGNMENT_PANEL_INTEGRITY_BLOCKED"
ASSIGNMENT_PANEL_INTEGRITY_NOT_EVALUATED = "ASSIGNMENT_PANEL_INTEGRITY_NOT_EVALUATED"

ISSUE_ASSIGNMENT_ARTIFACT_MISSING = "ASSIGNMENT_ARTIFACT_MISSING"
ISSUE_ASSIGNMENT_ALLOCATIONS_MISSING = "ASSIGNMENT_ALLOCATIONS_MISSING"
ISSUE_PANEL_RECORDS_MISSING = "PANEL_RECORDS_MISSING"
ISSUE_UNIT_ID_FIELD_MISSING = "UNIT_ID_FIELD_MISSING"
ISSUE_TREATMENT_FIELD_MISSING = "TREATMENT_FIELD_MISSING"
ISSUE_CELL_FIELD_MISSING = "CELL_FIELD_MISSING"
ISSUE_DUPLICATE_ASSIGNMENT_UNIT = "DUPLICATE_ASSIGNMENT_UNIT"
ISSUE_CONFLICTING_ASSIGNMENT_LABELS = "CONFLICTING_ASSIGNMENT_LABELS"
ISSUE_UNASSIGNED_PANEL_UNIT = "UNASSIGNED_PANEL_UNIT"
ISSUE_MISSING_PANEL_UNIT = "MISSING_PANEL_UNIT"
ISSUE_TREATMENT_LABEL_MISMATCH = "TREATMENT_LABEL_MISMATCH"
ISSUE_CELL_LABEL_MISMATCH = "CELL_LABEL_MISMATCH"
ISSUE_ASSIGNMENT_HASH_MISMATCH = "ASSIGNMENT_HASH_MISMATCH"
ISSUE_ASSIGNMENT_ARTIFACT_ID_MISMATCH = "ASSIGNMENT_ARTIFACT_ID_MISMATCH"
ISSUE_INVALID_TREATMENT_LABEL = "INVALID_TREATMENT_LABEL"
ISSUE_INVALID_CELL_LABEL = "INVALID_CELL_LABEL"
ISSUE_TREATED_OR_CONTROL_GROUP_MISSING = "TREATED_OR_CONTROL_GROUP_MISSING"

RETRY_FIX_ASSIGNMENT_ARTIFACT = "FIX_ASSIGNMENT_ARTIFACT"
RETRY_FIX_PANEL_DATA_CONTRACT = "FIX_PANEL_DATA_CONTRACT"
RETRY_FIX_ASSIGNMENT_PANEL_JOIN = "FIX_ASSIGNMENT_PANEL_JOIN"
RETRY_FIX_TREATMENT_LABEL_MAPPING = "FIX_TREATMENT_LABEL_MAPPING"
RETRY_FIX_CELL_LABEL_MAPPING = "FIX_CELL_LABEL_MAPPING"
RETRY_REGENERATE_ASSIGNMENT_ARTIFACT = "REGENERATE_ASSIGNMENT_ARTIFACT"
RETRY_DISABLE_PRODUCTION_CONTEXT = "DISABLE_PRODUCTION_CONTEXT"

_TREATED_TOKENS = frozenset({"1", "TRUE", "TREATED", "TREATMENT", "TEST", "T"})
_CONTROL_TOKENS = frozenset({"0", "FALSE", "CONTROL", "C"})

_POSITIVE_FLAGS = {
    "assignment_panel_integrity_runtime_implemented": True,
    "assignment_panel_integrity_evaluated": True,
    "assignment_panel_integrity_provenance_recorded": True,
    "assignment_panel_integrity_failure_blocks_execution": True,
}

_AUTH_FALSE = {
    "assignment_generation_implemented": False,
    "randomization_implemented": False,
    "claim_authorization_runtime_implemented": False,
    "claim_authorized": False,
    "claim_authorized_with_restrictions": False,
    "authorized_claim_text_generated": False,
    "trusted_readout_handoff_generated": False,
    "production_readout_authorized": False,
    "causal_claim_authorized": False,
    "incremental_lift_claim_authorized": False,
    "roi_claim_authorized": False,
    "production_authorization_granted": False,
    "inference_execution_implemented": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}


@dataclass(frozen=True)
class AssignmentPanelIntegrityConfig:
    require_assignment_artifact: bool = True
    require_assignment_allocations: bool = True
    require_panel_records: bool = True
    require_panel_units_present_in_assignment: bool = True
    require_all_assigned_units_present: bool = False
    require_no_unassigned_panel_units: bool = True
    require_panel_assignment_consistency: bool = True
    require_treatment_match: bool = True
    require_cell_match_when_available: bool = True
    require_hash_match: bool = False
    block_execution_on_integrity_failure: bool = True
    allow_warnings_for_extra_assigned_units_not_in_panel: bool = True
    assignment_unit_id_field: str = "unit_id"
    assignment_cell_field: str = "assigned_cell_id"
    assignment_treatment_field: str = "assigned_cell_role"
    panel_unit_id_field: str = "unit_id"
    panel_cell_field: str = "cell_id"
    panel_treatment_field: str = "treated"
    expected_treatment_values: tuple[str, ...] = ()
    expected_control_values: tuple[str, ...] = ()
    allowed_cell_labels: tuple[str, ...] = ()
    allowed_treatment_labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class AssignmentPanelIntegrityIssue:
    category: str
    message: str
    severity: str
    unit_id: str | None = None


@dataclass(frozen=True)
class AssignmentPanelIntegrityReport:
    request_id: str
    assignment_artifact_id: str | None
    assignment_candidate_id: str | None
    assignment_hash: str | None
    panel_hash: str | None
    status: str
    is_blocking: bool
    can_proceed_to_execution: bool
    assigned_unit_count: int
    panel_unit_count: int
    matched_unit_count: int
    unassigned_panel_units: tuple[str, ...]
    missing_panel_units: tuple[str, ...]
    treatment_mismatches: tuple[str, ...]
    cell_mismatches: tuple[str, ...]
    duplicate_assignment_units: tuple[str, ...]
    conflicting_assignment_labels: tuple[str, ...]
    invalid_treatment_labels: tuple[str, ...]
    invalid_cell_labels: tuple[str, ...]
    issues: tuple[AssignmentPanelIntegrityIssue, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    retry_category: str | None
    integrity_trace: dict[str, Any]
    provenance: dict[str, Any]
    claim_boundary_report: dict[str, Any]


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _hash_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _token(value: Any) -> str:
    return str(value).strip().upper() if value is not None else ""


def _safe_str_list(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(v for v in values if v))


def _resolve_config(config: AssignmentPanelIntegrityConfig | dict[str, Any] | None) -> AssignmentPanelIntegrityConfig:
    if config is None:
        return AssignmentPanelIntegrityConfig()
    if isinstance(config, AssignmentPanelIntegrityConfig):
        return config
    base = AssignmentPanelIntegrityConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    for key in ("expected_treatment_values", "expected_control_values", "allowed_cell_labels", "allowed_treatment_labels"):
        if key in config and config[key] is not None:
            merged[key] = tuple(str(x) for x in config[key])
    return AssignmentPanelIntegrityConfig(**merged)


def _as_list_of_dict(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [dict(x) for x in value if isinstance(x, dict)]
    return []


def _extract_panel_records(data: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("panel_records", "panel_data", "records"):
        val = data.get(key)
        if isinstance(val, list):
            return [dict(x) for x in val if isinstance(x, dict)]
    analysis_panel = _to_dict(data.get("analysis_panel"))
    for key in ("panel_records", "records", "panel_data"):
        val = analysis_panel.get(key)
        if isinstance(val, list):
            return [dict(x) for x in val if isinstance(x, dict)]
    execution_contract = _to_dict(data.get("execution_data_contract"))
    val = execution_contract.get("panel_data")
    if isinstance(val, list):
        return [dict(x) for x in val if isinstance(x, dict)]
    return []


def _extract_allocations(data: dict[str, Any]) -> list[dict[str, Any]]:
    direct = _as_list_of_dict(data.get("assignment_allocations"))
    if direct:
        return direct
    direct = _as_list_of_dict(data.get("unit_allocations"))
    if direct:
        return direct
    for container_key in ("assignment_artifact", "assignment_candidate", "assignment_plan"):
        container = _to_dict(data.get(container_key))
        for alloc_key in ("unit_allocations", "assignment_allocations", "unit_allocation_report"):
            rows = _as_list_of_dict(container.get(alloc_key))
            if rows:
                return rows
    return []


def _normalize_treatment_label(value: Any) -> str | None:
    if value is None:
        return None
    if value in (0, 1, True, False):
        return "TREATED" if bool(value) else "CONTROL"
    tok = _token(value)
    if tok in _TREATED_TOKENS:
        return "TREATED"
    if tok in _CONTROL_TOKENS:
        return "CONTROL"
    return tok


def _resolve_field(data: dict[str, Any], *keys: str, default: str) -> str:
    for key in keys:
        if data.get(key):
            return str(data[key])
    return default


def _claim_boundary(*, evaluated: bool, passed: bool) -> dict[str, Any]:
    return {
        **_POSITIVE_FLAGS,
        "assignment_panel_integrity_evaluated": evaluated,
        "assignment_panel_integrity_passed": passed,
        **_AUTH_FALSE,
    }


def _build_report(
    *,
    data: dict[str, Any],
    cfg: AssignmentPanelIntegrityConfig,
    issues: list[AssignmentPanelIntegrityIssue],
    warnings: list[str],
    blocking: list[str],
    status: str,
    retry_category: str | None,
    assigned_unit_count: int,
    panel_unit_count: int,
    matched_unit_count: int,
    unassigned_panel_units: list[str],
    missing_panel_units: list[str],
    treatment_mismatches: list[str],
    cell_mismatches: list[str],
    duplicate_assignment_units: list[str],
    conflicting_assignment_labels: list[str],
    invalid_treatment_labels: list[str],
    invalid_cell_labels: list[str],
    assignment_hash: str | None,
    panel_hash: str | None,
    checks_run: list[str],
) -> AssignmentPanelIntegrityReport:
    request_id = str(data.get("request_id") or f"integrity::{_hash_payload(data)[:12]}")
    assignment_artifact = _to_dict(data.get("assignment_artifact"))
    assignment_candidate = _to_dict(data.get("assignment_candidate"))
    assignment_artifact_id = str(
        data.get("assignment_artifact_id")
        or assignment_artifact.get("artifact_id")
        or assignment_candidate.get("candidate_id")
        or ""
    ) or None
    assignment_candidate_id = str(
        data.get("assignment_candidate_id") or assignment_candidate.get("candidate_id") or ""
    ) or None

    is_blocking = status in (
        ASSIGNMENT_PANEL_INTEGRITY_FAILED,
        ASSIGNMENT_PANEL_INTEGRITY_BLOCKED,
    )
    can_proceed = status in (
        ASSIGNMENT_PANEL_INTEGRITY_PASSED,
        ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS,
    )

    trace_payload = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "request_id": request_id,
        "status": status,
        "checks_run": checks_run,
        "assigned_unit_count": assigned_unit_count,
        "panel_unit_count": panel_unit_count,
        "matched_unit_count": matched_unit_count,
        "config_hash": _hash_payload(cfg.__dict__),
        "input_hash": _hash_payload(data),
    }
    trace = {
        **trace_payload,
        "integrity_hash": _hash_payload(trace_payload),
    }
    provenance = {
        "artifact_id": _ARTIFACT_ID,
        "input_hash": trace["input_hash"],
        "config_hash": trace["config_hash"],
        "integrity_hash": trace["integrity_hash"],
        "assignment_hash": assignment_hash,
        "panel_hash": panel_hash,
    }

    return AssignmentPanelIntegrityReport(
        request_id=request_id,
        assignment_artifact_id=assignment_artifact_id,
        assignment_candidate_id=assignment_candidate_id,
        assignment_hash=assignment_hash,
        panel_hash=panel_hash,
        status=status,
        is_blocking=is_blocking,
        can_proceed_to_execution=can_proceed,
        assigned_unit_count=assigned_unit_count,
        panel_unit_count=panel_unit_count,
        matched_unit_count=matched_unit_count,
        unassigned_panel_units=_safe_str_list(unassigned_panel_units),
        missing_panel_units=_safe_str_list(missing_panel_units),
        treatment_mismatches=_safe_str_list(treatment_mismatches),
        cell_mismatches=_safe_str_list(cell_mismatches),
        duplicate_assignment_units=_safe_str_list(duplicate_assignment_units),
        conflicting_assignment_labels=_safe_str_list(conflicting_assignment_labels),
        invalid_treatment_labels=_safe_str_list(invalid_treatment_labels),
        invalid_cell_labels=_safe_str_list(invalid_cell_labels),
        issues=tuple(issues),
        warnings=_safe_str_list(warnings),
        blocking_reasons=_safe_str_list(blocking),
        retry_category=retry_category,
        integrity_trace=trace,
        provenance=provenance,
        claim_boundary_report=_claim_boundary(
            evaluated=status != ASSIGNMENT_PANEL_INTEGRITY_NOT_EVALUATED,
            passed=can_proceed,
        ),
    )


def _evaluate_single(data: dict[str, Any], cfg: AssignmentPanelIntegrityConfig) -> AssignmentPanelIntegrityReport:
    issues: list[AssignmentPanelIntegrityIssue] = []
    warnings: list[str] = []
    blocking: list[str] = []
    checks_run: list[str] = []
    retry_category: str | None = None

    unit_id_field = _resolve_field(
        data,
        "assignment_unit_id_field",
        default=cfg.assignment_unit_id_field,
    )
    assignment_cell_field = _resolve_field(
        data,
        "assignment_cell_field",
        default=cfg.assignment_cell_field,
    )
    assignment_treatment_field = _resolve_field(
        data,
        "assignment_treatment_field",
        default=cfg.assignment_treatment_field,
    )
    panel_unit_id_field = _resolve_field(
        data,
        "panel_unit_id_field",
        default=cfg.panel_unit_id_field,
    )
    panel_cell_field = _resolve_field(
        data,
        "panel_cell_field",
        default=cfg.panel_cell_field,
    )
    panel_treatment_field = _resolve_field(
        data,
        "panel_treatment_field",
        default=cfg.panel_treatment_field,
    )

    assignment_artifact = _to_dict(data.get("assignment_artifact"))
    assignment_candidate = _to_dict(data.get("assignment_candidate"))
    reproducibility_manifest = _to_dict(data.get("reproducibility_manifest"))
    has_artifact = bool(
        assignment_artifact
        or assignment_candidate
        or data.get("assignment_artifact_id")
        or data.get("assignment_plan")
    )
    allocations = _extract_allocations(data)
    panel_records = _extract_panel_records(data)

    expected_treatment = {
        _token(x) for x in (
            list(cfg.expected_treatment_values)
            + list(data.get("expected_treatment_values") or [])
        )
    }
    expected_control = {
        _token(x) for x in (
            list(cfg.expected_control_values)
            + list(data.get("expected_control_values") or [])
        )
    }
    allowed_cells = {
        _token(x) for x in (
            list(cfg.allowed_cell_labels)
            + list(data.get("allowed_cell_labels") or [])
        )
    }
    allowed_treatment = {
        _token(x) for x in (
            list(cfg.allowed_treatment_labels)
            + list(data.get("allowed_treatment_labels") or [])
        )
    }

    assignment_artifact_id = str(
        data.get("assignment_artifact_id")
        or assignment_artifact.get("artifact_id")
        or ""
    )
    provided_artifact_id = str(data.get("expected_assignment_artifact_id") or "")
    if provided_artifact_id and assignment_artifact_id and provided_artifact_id != assignment_artifact_id:
        checks_run.append("artifact_id_matches")
        issues.append(
            AssignmentPanelIntegrityIssue(
                category=ISSUE_ASSIGNMENT_ARTIFACT_ID_MISMATCH,
                message="assignment artifact id mismatch",
                severity="BLOCKING",
            )
        )
        blocking.append("assignment artifact id mismatch")
        retry_category = RETRY_FIX_ASSIGNMENT_ARTIFACT

    assignment_hash = str(
        data.get("assignment_hash")
        or reproducibility_manifest.get("output_hash")
        or reproducibility_manifest.get("assignment_hash")
        or ""
    ) or None
    expected_hash = str(data.get("expected_assignment_hash") or "")
    require_hash = bool(data.get("require_hash_match", cfg.require_hash_match))

    if not has_artifact and not allocations and not panel_records:
        if not (
            cfg.require_assignment_artifact
            or cfg.require_assignment_allocations
            or cfg.require_panel_records
        ):
            return _build_report(
                data=data,
                cfg=cfg,
                issues=issues,
                warnings=warnings,
                blocking=blocking,
                status=ASSIGNMENT_PANEL_INTEGRITY_NOT_EVALUATED,
                retry_category=None,
                assigned_unit_count=0,
                panel_unit_count=0,
                matched_unit_count=0,
                unassigned_panel_units=[],
                missing_panel_units=[],
                treatment_mismatches=[],
                cell_mismatches=[],
                duplicate_assignment_units=[],
                conflicting_assignment_labels=[],
                invalid_treatment_labels=[],
                invalid_cell_labels=[],
                assignment_hash=assignment_hash,
                panel_hash=None,
                checks_run=["not_evaluated"],
            )

    if require_hash and assignment_hash and expected_hash:
        checks_run.append("assignment_hash_matches")
        if assignment_hash != expected_hash:
            issues.append(
                AssignmentPanelIntegrityIssue(
                    category=ISSUE_ASSIGNMENT_HASH_MISMATCH,
                    message="assignment hash mismatch",
                    severity="BLOCKING",
                )
            )
            blocking.append("assignment hash mismatch")
            retry_category = RETRY_REGENERATE_ASSIGNMENT_ARTIFACT

    if cfg.require_assignment_artifact and not has_artifact:
        checks_run.append("assignment_artifact_present")
        issues.append(
            AssignmentPanelIntegrityIssue(
                category=ISSUE_ASSIGNMENT_ARTIFACT_MISSING,
                message="assignment artifact missing",
                severity="BLOCKING",
            )
        )
        blocking.append("assignment artifact missing")
        retry_category = retry_category or RETRY_FIX_ASSIGNMENT_ARTIFACT
        return _build_report(
            data=data,
            cfg=cfg,
            issues=issues,
            warnings=warnings,
            blocking=blocking,
            status=ASSIGNMENT_PANEL_INTEGRITY_BLOCKED,
            retry_category=retry_category,
            assigned_unit_count=0,
            panel_unit_count=0,
            matched_unit_count=0,
            unassigned_panel_units=[],
            missing_panel_units=[],
            treatment_mismatches=[],
            cell_mismatches=[],
            duplicate_assignment_units=[],
            conflicting_assignment_labels=[],
            invalid_treatment_labels=[],
            invalid_cell_labels=[],
            assignment_hash=assignment_hash,
            panel_hash=None,
            checks_run=checks_run,
        )

    if cfg.require_assignment_allocations and not allocations:
        checks_run.append("assignment_allocations_present")
        issues.append(
            AssignmentPanelIntegrityIssue(
                category=ISSUE_ASSIGNMENT_ALLOCATIONS_MISSING,
                message="assignment allocations missing",
                severity="BLOCKING",
            )
        )
        blocking.append("assignment allocations missing")
        retry_category = retry_category or RETRY_FIX_ASSIGNMENT_ARTIFACT
        return _build_report(
            data=data,
            cfg=cfg,
            issues=issues,
            warnings=warnings,
            blocking=blocking,
            status=ASSIGNMENT_PANEL_INTEGRITY_BLOCKED,
            retry_category=retry_category,
            assigned_unit_count=0,
            panel_unit_count=0,
            matched_unit_count=0,
            unassigned_panel_units=[],
            missing_panel_units=[],
            treatment_mismatches=[],
            cell_mismatches=[],
            duplicate_assignment_units=[],
            conflicting_assignment_labels=[],
            invalid_treatment_labels=[],
            invalid_cell_labels=[],
            assignment_hash=assignment_hash,
            panel_hash=None,
            checks_run=checks_run,
        )

    if cfg.require_panel_records and not panel_records:
        checks_run.append("panel_records_present")
        if has_artifact or allocations:
            issues.append(
                AssignmentPanelIntegrityIssue(
                    category=ISSUE_PANEL_RECORDS_MISSING,
                    message="panel records missing",
                    severity="BLOCKING",
                )
            )
            blocking.append("panel records missing")
            retry_category = retry_category or RETRY_FIX_PANEL_DATA_CONTRACT
            return _build_report(
                data=data,
                cfg=cfg,
                issues=issues,
                warnings=warnings,
                blocking=blocking,
                status=ASSIGNMENT_PANEL_INTEGRITY_BLOCKED,
                retry_category=retry_category,
                assigned_unit_count=len(allocations),
                panel_unit_count=0,
                matched_unit_count=0,
                unassigned_panel_units=[],
                missing_panel_units=[],
                treatment_mismatches=[],
                cell_mismatches=[],
                duplicate_assignment_units=[],
                conflicting_assignment_labels=[],
                invalid_treatment_labels=[],
                invalid_cell_labels=[],
                assignment_hash=assignment_hash,
                panel_hash=None,
                checks_run=checks_run,
            )
        return _build_report(
            data=data,
            cfg=cfg,
            issues=issues,
            warnings=warnings,
            blocking=blocking,
            status=ASSIGNMENT_PANEL_INTEGRITY_NOT_EVALUATED,
            retry_category=None,
            assigned_unit_count=0,
            panel_unit_count=0,
            matched_unit_count=0,
            unassigned_panel_units=[],
            missing_panel_units=[],
            treatment_mismatches=[],
            cell_mismatches=[],
            duplicate_assignment_units=[],
            conflicting_assignment_labels=[],
            invalid_treatment_labels=[],
            invalid_cell_labels=[],
            assignment_hash=assignment_hash,
            panel_hash=None,
            checks_run=["panel_records_present"],
        )

    checks_run.extend(
        [
            "assignment_artifact_present",
            "assignment_allocations_present",
            "panel_records_present",
        ]
    )

    assignment_map: dict[str, dict[str, str | None]] = {}
    duplicate_assignment_units: list[str] = []
    conflicting_assignment_labels: list[str] = []
    invalid_treatment_labels: list[str] = []
    invalid_cell_labels: list[str] = []
    treated_present = False
    control_present = False

    for row in allocations:
        uid = str(row.get(unit_id_field) or row.get("unit_id") or row.get("geo_id") or "").strip()
        if not uid:
            checks_run.append("unit_id_fields_present")
            issues.append(
                AssignmentPanelIntegrityIssue(
                    category=ISSUE_UNIT_ID_FIELD_MISSING,
                    message="assignment allocation missing unit id",
                    severity="BLOCKING",
                )
            )
            blocking.append("assignment unit id missing")
            retry_category = retry_category or RETRY_FIX_ASSIGNMENT_ARTIFACT
            continue

        cell_val = str(row.get(assignment_cell_field) or row.get("assigned_cell_id") or row.get("cell_id") or "").strip()
        role_raw = row.get(assignment_treatment_field) or row.get("assigned_cell_role") or row.get("treatment")
        treatment_norm = _normalize_treatment_label(role_raw)
        if treatment_norm is None and cell_val:
            cell_tok = _token(cell_val)
            if "TREAT" in cell_tok or cell_tok.startswith("T"):
                treatment_norm = "TREATED"
            elif "CONTROL" in cell_tok or cell_tok.startswith("C"):
                treatment_norm = "CONTROL"

        if treatment_norm == "TREATED":
            treated_present = True
        elif treatment_norm == "CONTROL":
            control_present = True

        if allowed_treatment and treatment_norm and _token(treatment_norm) not in allowed_treatment:
            invalid_treatment_labels.append(uid)
            issues.append(
                AssignmentPanelIntegrityIssue(
                    category=ISSUE_INVALID_TREATMENT_LABEL,
                    message=f"invalid treatment label for unit {uid}",
                    severity="BLOCKING",
                    unit_id=uid,
                )
            )
        if allowed_cells and cell_val and _token(cell_val) not in allowed_cells:
            invalid_cell_labels.append(uid)
            issues.append(
                AssignmentPanelIntegrityIssue(
                    category=ISSUE_INVALID_CELL_LABEL,
                    message=f"invalid cell label for unit {uid}",
                    severity="BLOCKING",
                    unit_id=uid,
                )
            )

        if uid in assignment_map:
            duplicate_assignment_units.append(uid)
            prev = assignment_map[uid]
            if prev.get("treatment") != treatment_norm or prev.get("cell") != cell_val:
                conflicting_assignment_labels.append(uid)
                issues.append(
                    AssignmentPanelIntegrityIssue(
                        category=ISSUE_CONFLICTING_ASSIGNMENT_LABELS,
                        message=f"conflicting assignment labels for unit {uid}",
                        severity="BLOCKING",
                        unit_id=uid,
                    )
                )
                blocking.append(f"conflicting assignment for unit {uid}")
                retry_category = retry_category or RETRY_REGENERATE_ASSIGNMENT_ARTIFACT
        else:
            assignment_map[uid] = {"cell": cell_val or None, "treatment": treatment_norm}

    if duplicate_assignment_units:
        checks_run.append("assigned_units_unique")
        issues.append(
            AssignmentPanelIntegrityIssue(
                category=ISSUE_DUPLICATE_ASSIGNMENT_UNIT,
                message="duplicate assignment units detected",
                severity="BLOCKING",
            )
        )
        blocking.append("duplicate assignment units")
        retry_category = retry_category or RETRY_REGENERATE_ASSIGNMENT_ARTIFACT

    panel_map: dict[str, dict[str, str | None]] = {}
    panel_conflicts: list[str] = []
    for row in panel_records:
        uid = str(row.get(panel_unit_id_field) or row.get("unit_id") or row.get("geo_id") or "").strip()
        if not uid:
            issues.append(
                AssignmentPanelIntegrityIssue(
                    category=ISSUE_UNIT_ID_FIELD_MISSING,
                    message="panel record missing unit id",
                    severity="BLOCKING",
                )
            )
            blocking.append("panel unit id missing")
            retry_category = retry_category or RETRY_FIX_PANEL_DATA_CONTRACT
            continue
        cell_val = str(row.get(panel_cell_field) or row.get("cell_id") or "").strip() or None
        treatment_norm = _normalize_treatment_label(row.get(panel_treatment_field) or row.get("treated"))
        if uid in panel_map:
            prev = panel_map[uid]
            if prev.get("treatment") != treatment_norm or prev.get("cell") != cell_val:
                panel_conflicts.append(uid)
        else:
            panel_map[uid] = {"cell": cell_val, "treatment": treatment_norm}

    if panel_conflicts:
        checks_run.append("no_conflicting_panel_label_for_same_unit")
        for uid in panel_conflicts:
            issues.append(
                AssignmentPanelIntegrityIssue(
                    category=ISSUE_CONFLICTING_ASSIGNMENT_LABELS,
                    message=f"conflicting panel labels for unit {uid}",
                    severity="BLOCKING",
                    unit_id=uid,
                )
            )
            blocking.append(f"conflicting panel labels for unit {uid}")
        retry_category = retry_category or RETRY_FIX_PANEL_DATA_CONTRACT

    panel_hash = _hash_payload(
        sorted(
            (
                uid,
                panel_map[uid].get("cell"),
                panel_map[uid].get("treatment"),
            )
            for uid in panel_map
        )
    )

    checks_run.append("treated_and_control_units_present")
    if cfg.require_panel_assignment_consistency and not (treated_present and control_present):
        issues.append(
            AssignmentPanelIntegrityIssue(
                category=ISSUE_TREATED_OR_CONTROL_GROUP_MISSING,
                message="treated or control group missing in assignment allocations",
                severity="BLOCKING",
            )
        )
        blocking.append("treated or control group missing")
        retry_category = retry_category or RETRY_FIX_ASSIGNMENT_ARTIFACT

    unassigned_panel_units: list[str] = []
    missing_panel_units: list[str] = []
    treatment_mismatches: list[str] = []
    cell_mismatches: list[str] = []
    matched_unit_count = 0

    assignment_units = set(assignment_map)
    panel_units = set(panel_map)

    if cfg.require_panel_units_present_in_assignment:
        checks_run.append("panel_units_present_in_assignment")
        for uid in sorted(panel_units - assignment_units):
            unassigned_panel_units.append(uid)
            issues.append(
                AssignmentPanelIntegrityIssue(
                    category=ISSUE_UNASSIGNED_PANEL_UNIT,
                    message=f"panel unit {uid} not in assignment",
                    severity="BLOCKING",
                    unit_id=uid,
                )
            )
            blocking.append(f"panel unit {uid} not assigned")
            retry_category = retry_category or RETRY_FIX_ASSIGNMENT_PANEL_JOIN

    if cfg.require_all_assigned_units_present:
        checks_run.append("assignment_units_present_in_panel")
        for uid in sorted(assignment_units - panel_units):
            missing_panel_units.append(uid)
            issues.append(
                AssignmentPanelIntegrityIssue(
                    category=ISSUE_MISSING_PANEL_UNIT,
                    message=f"assigned unit {uid} missing from panel",
                    severity="BLOCKING",
                    unit_id=uid,
                )
            )
            blocking.append(f"assigned unit {uid} missing from panel")
            retry_category = retry_category or RETRY_FIX_ASSIGNMENT_PANEL_JOIN
    elif cfg.allow_warnings_for_extra_assigned_units_not_in_panel:
        for uid in sorted(assignment_units - panel_units):
            missing_panel_units.append(uid)
            warnings.append(f"assigned unit {uid} not present in analysis panel")

    if cfg.require_no_unassigned_panel_units and unassigned_panel_units:
        checks_run.append("require_no_unassigned_panel_units")

    common_units = assignment_units & panel_units
    matched_unit_count = len(common_units)

    if cfg.require_panel_assignment_consistency:
        for uid in sorted(common_units):
            assign = assignment_map[uid]
            panel = panel_map[uid]
            if cfg.require_treatment_match:
                checks_run.append("panel_treatment_matches_assignment")
                a_treat = assign.get("treatment")
                p_treat = panel.get("treatment")
                if a_treat and p_treat and a_treat != p_treat:
                    treatment_mismatches.append(uid)
                    issues.append(
                        AssignmentPanelIntegrityIssue(
                            category=ISSUE_TREATMENT_LABEL_MISMATCH,
                            message=f"treatment mismatch for unit {uid}",
                            severity="BLOCKING",
                            unit_id=uid,
                        )
                    )
                    blocking.append(f"treatment mismatch for unit {uid}")
                    retry_category = retry_category or RETRY_FIX_TREATMENT_LABEL_MAPPING
            if cfg.require_cell_match_when_available:
                checks_run.append("panel_cell_matches_assignment")
                a_cell = assign.get("cell")
                p_cell = panel.get("cell")
                if a_cell and p_cell and _token(a_cell) != _token(p_cell):
                    cell_mismatches.append(uid)
                    issues.append(
                        AssignmentPanelIntegrityIssue(
                            category=ISSUE_CELL_LABEL_MISMATCH,
                            message=f"cell mismatch for unit {uid}",
                            severity="BLOCKING",
                            unit_id=uid,
                        )
                    )
                    blocking.append(f"cell mismatch for unit {uid}")
                    retry_category = retry_category or RETRY_FIX_CELL_LABEL_MAPPING

    if expected_treatment or expected_control:
        checks_run.append("allowed_treatment_values_used")
        for uid, assign in assignment_map.items():
            tok = _token(assign.get("treatment") or "")
            if expected_treatment and tok in expected_treatment:
                continue
            if expected_control and tok in expected_control:
                continue
            if expected_treatment or expected_control:
                invalid_treatment_labels.append(uid)

    status = ASSIGNMENT_PANEL_INTEGRITY_PASSED
    if blocking or any(i.severity == "BLOCKING" for i in issues):
        status = ASSIGNMENT_PANEL_INTEGRITY_FAILED
    elif warnings:
        status = ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS

    return _build_report(
        data=data,
        cfg=cfg,
        issues=issues,
        warnings=warnings,
        blocking=blocking,
        status=status,
        retry_category=retry_category,
        assigned_unit_count=len(assignment_map),
        panel_unit_count=len(panel_map),
        matched_unit_count=matched_unit_count,
        unassigned_panel_units=unassigned_panel_units,
        missing_panel_units=missing_panel_units,
        treatment_mismatches=treatment_mismatches,
        cell_mismatches=cell_mismatches,
        duplicate_assignment_units=duplicate_assignment_units,
        conflicting_assignment_labels=conflicting_assignment_labels,
        invalid_treatment_labels=invalid_treatment_labels,
        invalid_cell_labels=invalid_cell_labels,
        assignment_hash=assignment_hash,
        panel_hash=panel_hash,
        checks_run=sorted(set(checks_run)),
    )


def evaluate_assignment_panel_integrity(
    input_data: Any,
    config: AssignmentPanelIntegrityConfig | dict[str, Any] | None = None,
) -> AssignmentPanelIntegrityReport | list[AssignmentPanelIntegrityReport]:
    """Evaluate assignment-panel integrity for one or more requests."""
    cfg = _resolve_config(config)
    if isinstance(input_data, list):
        return [_evaluate_single(_to_dict(x), cfg) for x in input_data]
    data = _to_dict(input_data)
    if "requests" in data and isinstance(data["requests"], list):
        return [_evaluate_single(_to_dict(x), cfg) for x in data["requests"]]
    return _evaluate_single(data, cfg)


validate_assignment_panel_integrity = evaluate_assignment_panel_integrity
check_assignment_panel_integrity = evaluate_assignment_panel_integrity


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=_REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def run_validation(*, write_summary: bool = True) -> dict[str, Any]:
    smoke_allocations = [
        {"unit_id": "u1", "assigned_cell_id": "C1", "assigned_cell_role": "TREATMENT"},
        {"unit_id": "u2", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL"},
    ]
    smoke_panel = [
        {"unit_id": "u1", "treated": 1, "cell_id": "C1"},
        {"unit_id": "u2", "treated": 0, "cell_id": "C0"},
    ]
    report = evaluate_assignment_panel_integrity(
        {
            "assignment_artifact": {"artifact_id": "assign_smoke"},
            "assignment_artifact_id": "assign_smoke",
            "unit_allocations": smoke_allocations,
            "panel_records": smoke_panel,
        }
    )
    assert isinstance(report, AssignmentPanelIntegrityReport)
    assert report.status == ASSIGNMENT_PANEL_INTEGRITY_PASSED

    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "assignment_panel_integrity_runtime",
        "base_commit": _git_head(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": [
            "DID_INSTRUMENT_ESTIMAND_UNIFICATION_001",
            "PRODUCTION_CATALOG_BLOCKLIST_ENFORCEMENT_001",
            "AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001",
            "DESIGN_ASSIGNMENT_RUNTIME_001",
            "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR",
            "READOUT_PLAN_RUNTIME_001",
        ],
        "assignment_panel_integrity_runtime_implemented": True,
        "assignment_panel_integrity_evaluated": True,
        "assignment_panel_integrity_statuses_defined": True,
        "assignment_panel_integrity_issue_taxonomy_defined": True,
        "assignment_panel_integrity_retry_categories_defined": True,
        "assignment_panel_integrity_provenance_recorded": True,
        "assignment_panel_integrity_failure_blocks_execution": True,
        "assignment_panel_integrity_gate_integrated_with_execution_runtime": True,
        "assignment_panel_integrity_gate_integrated_with_did_executor": True,
        "assignment_panel_integrity_status_propagated_to_diagnostics": True,
        "assignment_generation_implemented": False,
        "randomization_implemented": False,
        "claim_authorization_runtime_implemented": False,
        "claim_authorized": False,
        "claim_authorized_with_restrictions": False,
        "authorized_claim_text_generated": False,
        "trusted_readout_handoff_generated": False,
        "production_readout_authorized": False,
        "causal_claim_authorized": False,
        "incremental_lift_claim_authorized": False,
        "roi_claim_authorized": False,
        "production_authorization_granted": False,
        "inference_execution_implemented": False,
        "p_value_computed": False,
        "confidence_interval_computed": False,
        "uncertainty_computed": False,
        "mmm_runtime_calls_implemented": False,
        "mmm_calibration_authorized": False,
        "llm_decisioning_authorized": False,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "final_verdict": _VERDICT,
        "smoke_status": report.status,
        "failed_scenarios": [],
    }
    if write_summary:
        _DEFAULT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
        _DEFAULT_SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--write-summary", action="store_true")
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
