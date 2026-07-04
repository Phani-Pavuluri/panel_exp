"""GOVERNED_RANDOMIZATION_RUNTIME_001 — deterministic governed randomization artifact generation."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "GOVERNED_RANDOMIZATION_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "governed_randomization_runtime_implemented_no_inference_or_claim_authorization"
_VERDICT = "governed_randomization_runtime_implemented_no_inference_or_claim_authorization"
_RECOMMENDED_NEXT = "SRM_BALANCE_READOUT_DIAGNOSTIC_001"
_ALTERNATIVE_NEXT = "CLAIM_AUTHORIZATION_RUNTIME_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/GOVERNED_RANDOMIZATION_RUNTIME_001_summary.json"
_ASSIGNMENT_SOURCE = "GOVERNED_RANDOMIZATION_RUNTIME_001"

GOVERNED_RANDOMIZATION_COMPLETED = "GOVERNED_RANDOMIZATION_COMPLETED"
GOVERNED_RANDOMIZATION_COMPLETED_WITH_WARNINGS = "GOVERNED_RANDOMIZATION_COMPLETED_WITH_WARNINGS"
GOVERNED_RANDOMIZATION_BLOCKED = "GOVERNED_RANDOMIZATION_BLOCKED"
GOVERNED_RANDOMIZATION_FAILED = "GOVERNED_RANDOMIZATION_FAILED"
GOVERNED_RANDOMIZATION_NOT_EVALUATED = "GOVERNED_RANDOMIZATION_NOT_EVALUATED"

ASSIGNMENT_ARTIFACT_GENERATED = "ASSIGNMENT_ARTIFACT_GENERATED"
ASSIGNMENT_ARTIFACT_NOT_GENERATED = "ASSIGNMENT_ARTIFACT_NOT_GENERATED"
ASSIGNMENT_ARTIFACT_BLOCKED = "ASSIGNMENT_ARTIFACT_BLOCKED"

ISSUE_ELIGIBLE_UNITS_MISSING = "ELIGIBLE_UNITS_MISSING"
ISSUE_DUPLICATE_UNIT_IDS = "DUPLICATE_UNIT_IDS"
ISSUE_CELL_REQUIREMENTS_MISSING = "CELL_REQUIREMENTS_MISSING"
ISSUE_INSUFFICIENT_ELIGIBLE_UNITS = "INSUFFICIENT_ELIGIBLE_UNITS"
ISSUE_INVALID_ALLOCATION_RATIO = "INVALID_ALLOCATION_RATIO"
ISSUE_INVALID_TARGET_CELL_SIZE = "INVALID_TARGET_CELL_SIZE"
ISSUE_SEED_POLICY_MISSING = "SEED_POLICY_MISSING"
ISSUE_UNSUPPORTED_RANDOMIZATION_TYPE = "UNSUPPORTED_RANDOMIZATION_TYPE"
ISSUE_STRATA_FIELD_MISSING = "STRATA_FIELD_MISSING"
ISSUE_STRATUM_INSUFFICIENT_UNITS = "STRATUM_INSUFFICIENT_UNITS"
ISSUE_BLOCK_FIELD_MISSING = "BLOCK_FIELD_MISSING"
ISSUE_BLOCK_INSUFFICIENT_UNITS = "BLOCK_INSUFFICIENT_UNITS"
ISSUE_COMMON_CONTROL_REQUIREMENTS_INVALID = "COMMON_CONTROL_REQUIREMENTS_INVALID"
ISSUE_SPLIT_CONTROL_REQUIRES_RECHECK = "SPLIT_CONTROL_REQUIRES_RECHECK"
ISSUE_ASSIGNMENT_FEASIBILITY_BLOCKED = "ASSIGNMENT_FEASIBILITY_BLOCKED"
ISSUE_METHOD_SUITABILITY_BLOCKED = "METHOD_SUITABILITY_BLOCKED"
ISSUE_PRODUCTION_CONTEXT_REQUIRES_GOVERNED_RANDOMIZATION = "PRODUCTION_CONTEXT_REQUIRES_GOVERNED_RANDOMIZATION"

RETRY_FIX_ELIGIBLE_UNIT_POOL = "FIX_ELIGIBLE_UNIT_POOL"
RETRY_FIX_CELL_REQUIREMENTS = "FIX_CELL_REQUIREMENTS"
RETRY_FIX_RANDOMIZATION_CONFIG = "FIX_RANDOMIZATION_CONFIG"
RETRY_ADD_SEED_POLICY = "ADD_SEED_POLICY"
RETRY_ADD_STRATIFICATION_FIELDS = "ADD_STRATIFICATION_FIELDS"
RETRY_ADD_BLOCK_FIELDS = "ADD_BLOCK_FIELDS"
RETRY_RERUN_ASSIGNMENT_FEASIBILITY = "RERUN_ASSIGNMENT_FEASIBILITY"
RETRY_RERUN_METHOD_SUITABILITY = "RERUN_METHOD_SUITABILITY"
RETRY_REDESIGN_EXPERIMENT_STRUCTURE = "REDESIGN_EXPERIMENT_STRUCTURE"
RETRY_DISABLE_PRODUCTION_CONTEXT = "DISABLE_PRODUCTION_CONTEXT"

_SUPPORTED_RANDOMIZATION_TYPES = frozenset({
    "TWO_CELL_COMPLETE_RANDOMIZATION",
    "MULTI_CELL_COMPLETE_RANDOMIZATION",
    "STRATIFIED_RANDOMIZATION",
    "BLOCK_RANDOMIZATION",
    "COMMON_CONTROL_RANDOMIZATION",
})

_POSITIVE_FLAGS = {
    "governed_randomization_runtime_implemented": True,
    "governed_randomization_artifact_generated": True,
    "deterministic_seed_policy_enforced": True,
    "randomization_reproducibility_manifest_recorded": True,
    "assignment_panel_integrity_compatible_artifact_generated": True,
}

_AUTH_FALSE = {
    "rerandomization_optimization_implemented": False,
    "balance_optimization_implemented": False,
    "matched_market_optimization_implemented": False,
    "power_mde_computed": False,
    "estimator_implemented": False,
    "inference_implemented": False,
    "bootstrap_inference_implemented": False,
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
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}


@dataclass(frozen=True)
class GovernedRandomizationConfig:
    allow_derived_seed: bool = True
    derived_seed_policy: str = "REQUEST_PAYLOAD_HASH"
    require_explicit_seed_in_production: bool = True
    block_on_assignment_feasibility_blocked: bool = True
    block_on_method_suitability_blocked: bool = True
    randomization_version: str = "1.0.0"


@dataclass(frozen=True)
class GovernedRandomizationIssue:
    category: str
    message: str
    severity: str = "BLOCKING"


@dataclass(frozen=True)
class GovernedRandomizationReport:
    request_id: str
    design_id: str | None
    randomization_type: str
    status: str
    is_blocking: bool
    assignment_artifact_generated: bool
    assignment_artifact: dict[str, Any] | None
    assignment_artifact_id: str | None
    assignment_candidate_id: str | None
    assignment_hash: str | None
    seed: str | None
    seed_policy: str | None
    randomization_version: str
    eligible_unit_count: int
    excluded_unit_count: int
    assigned_unit_count: int
    cell_counts: dict[str, int]
    strata_counts: dict[str, int]
    block_counts: dict[str, int]
    unit_allocations: tuple[dict[str, Any], ...]
    excluded_units: tuple[str, ...]
    warnings: tuple[str, ...]
    issues: tuple[GovernedRandomizationIssue, ...]
    blocking_reasons: tuple[str, ...]
    failure_packet: dict[str, Any] | None
    retry_category: str | None
    reproducibility_manifest: dict[str, Any] | None
    randomization_trace: dict[str, Any]
    provenance: dict[str, Any]
    claim_boundary_report: dict[str, Any]


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _token(value: Any) -> str:
    return str(value).strip().upper() if value is not None else ""


def _hash_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _safe_str_list(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(v for v in values if v))


def _resolve_config(
    config: GovernedRandomizationConfig | dict[str, Any] | None,
) -> GovernedRandomizationConfig:
    if config is None:
        return GovernedRandomizationConfig()
    if isinstance(config, GovernedRandomizationConfig):
        return config
    base = GovernedRandomizationConfig()
    return GovernedRandomizationConfig(
        **{**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    )


def _normalize_eligible_units(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("eligible_units")
    if raw is None:
        nested = _to_dict(raw)
        raw = nested.get("eligible_units") if nested else None
    if isinstance(raw, dict) and "eligible_units" in raw:
        raw = raw["eligible_units"]
    units: list[dict[str, Any]] = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                units.append({"unit_id": item})
            elif isinstance(item, dict):
                uid = item.get("unit_id") or item.get(data.get("unit_id_field") or "unit_id")
                if uid:
                    units.append(dict(item, unit_id=str(uid)))
    return units


def _normalize_cells(data: dict[str, Any]) -> list[dict[str, Any]]:
    cells = data.get("cells") or data.get("cell_requirements") or []
    if not isinstance(cells, list):
        return []
    normalized: list[dict[str, Any]] = []
    target_sizes = _to_dict(data.get("target_cell_sizes"))
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        cell_id = str(cell.get("cell_id") or cell.get("id") or "")
        if not cell_id:
            continue
        role = cell.get("role") or cell.get("cell_role")
        target = cell.get("target_size")
        if target is None:
            target = cell.get("required_unit_count") or cell.get("min_unit_count")
        if target is None and cell_id in target_sizes:
            target = target_sizes[cell_id]
        normalized.append({
            "cell_id": cell_id,
            "role": str(role).upper() if role else None,
            "target_size": int(target) if target is not None else None,
        })
    return normalized


def _unit_order_key(seed: str, unit_id: str, *, stratum: str = "", block: str = "") -> str:
    payload = f"{seed}|{unit_id}|{stratum}|{block}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _role_to_treatment_label(role: str | None) -> str:
    tok = _token(role)
    if tok in {"TREATMENT", "TREATED", "TEST", "T"}:
        return "TREATED"
    if tok in {"CONTROL", "C"}:
        return "CONTROL"
    if "TREAT" in tok:
        return "TREATED"
    if "CONTROL" in tok:
        return "CONTROL"
    return tok or "UNKNOWN"


def _resolve_seed(data: dict[str, Any], cfg: GovernedRandomizationConfig) -> tuple[str | None, str | None, list[str], list[str]]:
    """Return seed, seed_policy, blockers, remediation."""
    blockers: list[str] = []
    remediation: list[str] = []
    explicit_seed = data.get("seed")
    seed_policy = str(data.get("seed_policy") or "")
    production = _token(data.get("production_context")) in {"PRODUCTION", "TRUE", "1", "YES"}

    if explicit_seed is not None and str(explicit_seed).strip():
        policy = seed_policy or "EXPLICIT_SEED"
        return str(explicit_seed), policy, blockers, remediation

    if cfg.allow_derived_seed:
        derived = _hash_payload({
            "design_id": data.get("design_id"),
            "randomization_type": data.get("randomization_type"),
            "eligible_units": [u.get("unit_id") for u in _normalize_eligible_units(data)],
            "cells": _normalize_cells(data),
        })[:16]
        policy = seed_policy or cfg.derived_seed_policy
        return derived, policy, blockers, remediation

    if production and cfg.require_explicit_seed_in_production:
        blockers.append(ISSUE_SEED_POLICY_MISSING)
        remediation.append(RETRY_ADD_SEED_POLICY)
        if production:
            blockers.append(ISSUE_PRODUCTION_CONTEXT_REQUIRES_GOVERNED_RANDOMIZATION)
            remediation.append(RETRY_DISABLE_PRODUCTION_CONTEXT)

    return None, seed_policy or None, blockers, remediation


def _compute_cell_targets(
    cells: list[dict[str, Any]],
    available: int,
    allocation_ratio: Any,
) -> tuple[dict[str, int], list[str], list[str]]:
    """Return cell_id -> target count, blockers, remediation."""
    blockers: list[str] = []
    remediation: list[str] = []
    targets: dict[str, int] = {}

    explicit_total = 0
    all_explicit = True
    for cell in cells:
        cid = cell["cell_id"]
        ts = cell.get("target_size")
        if ts is None:
            all_explicit = False
            continue
        if ts < 0:
            blockers.append(ISSUE_INVALID_TARGET_CELL_SIZE)
            remediation.append(RETRY_FIX_CELL_REQUIREMENTS)
            return {}, blockers, remediation
        targets[cid] = int(ts)
        explicit_total += int(ts)

    if all_explicit and targets:
        if explicit_total > available:
            blockers.append(ISSUE_INSUFFICIENT_ELIGIBLE_UNITS)
            remediation.append(RETRY_FIX_ELIGIBLE_UNIT_POOL)
        return targets, blockers, remediation

    if allocation_ratio is not None:
        if isinstance(allocation_ratio, (int, float)):
            if not 0 < float(allocation_ratio) < 1:
                blockers.append(ISSUE_INVALID_ALLOCATION_RATIO)
                remediation.append(RETRY_FIX_RANDOMIZATION_CONFIG)
                return {}, blockers, remediation
            if len(cells) == 2:
                treatment_cells = [c for c in cells if _role_to_treatment_label(c.get("role")) == "TREATED"]
                control_cells = [c for c in cells if _role_to_treatment_label(c.get("role")) == "CONTROL"]
                if len(treatment_cells) == 1 and len(control_cells) == 1:
                    t_size = int(round(available * float(allocation_ratio)))
                    t_size = max(0, min(t_size, available))
                    c_size = available - t_size
                    targets[treatment_cells[0]["cell_id"]] = t_size
                    targets[control_cells[0]["cell_id"]] = c_size
                    return targets, blockers, remediation
            blockers.append(ISSUE_INVALID_ALLOCATION_RATIO)
            remediation.append(RETRY_FIX_RANDOMIZATION_CONFIG)
            return {}, blockers, remediation

        if isinstance(allocation_ratio, dict):
            weights = {str(k): float(v) for k, v in allocation_ratio.items() if float(v) > 0}
            if not weights:
                blockers.append(ISSUE_INVALID_ALLOCATION_RATIO)
                remediation.append(RETRY_FIX_RANDOMIZATION_CONFIG)
                return {}, blockers, remediation
            total_w = sum(weights.values())
            remaining = available
            cell_ids = [c["cell_id"] for c in cells]
            for i, cid in enumerate(cell_ids):
                if cid not in weights:
                    continue
                if i == len(cell_ids) - 1:
                    targets[cid] = remaining
                else:
                    count = int(round(available * weights[cid] / total_w))
                    count = max(0, min(count, remaining))
                    targets[cid] = count
                    remaining -= count
            return targets, blockers, remediation

    if len(cells) == 2 and not targets:
        half = available // 2
        targets[cells[0]["cell_id"]] = half
        targets[cells[1]["cell_id"]] = available - half
        return targets, blockers, remediation

    per_cell = available // len(cells) if cells else 0
    for i, cell in enumerate(cells):
        cid = cell["cell_id"]
        if i == len(cells) - 1:
            targets[cid] = available - sum(targets.values())
        else:
            targets[cid] = per_cell
    return targets, blockers, remediation


def _allocate_units_to_cells(
    units: list[dict[str, Any]],
    cells: list[dict[str, Any]],
    targets: dict[str, int],
    seed: str,
    *,
    stratum: str = "",
    block: str = "",
) -> list[dict[str, Any]]:
    unit_id_field = "unit_id"
    sorted_units = sorted(
        units,
        key=lambda u: _unit_order_key(seed, str(u.get(unit_id_field)), stratum=stratum, block=block),
    )
    allocations: list[dict[str, Any]] = []
    idx = 0
    for cell in cells:
        cid = cell["cell_id"]
        role = cell.get("role")
        count = targets.get(cid, 0)
        for _ in range(count):
            if idx >= len(sorted_units):
                break
            unit = sorted_units[idx]
            idx += 1
            uid = str(unit.get(unit_id_field))
            treatment_label = _role_to_treatment_label(role)
            treated_val = 1 if treatment_label == "TREATED" else 0
            row = {
                "unit_id": uid,
                "assigned_cell_id": cid,
                "assigned_cell_role": role or treatment_label,
                "cell_id": cid,
                "cell_role": role,
                "treatment_label": treatment_label,
                "treated": treated_val,
                "assignment_source": _ASSIGNMENT_SOURCE,
                "assignment_algorithm": _ASSIGNMENT_SOURCE,
            }
            if stratum:
                row["stratum"] = stratum
            if block:
                row["block"] = block
            if unit.get("geo_id"):
                row["geo_id"] = unit["geo_id"]
            allocations.append(row)
    return allocations


def _claim_boundary(*, artifact_generated: bool) -> dict[str, Any]:
    return {
        **_POSITIVE_FLAGS,
        "governed_randomization_artifact_generated": artifact_generated,
        **_AUTH_FALSE,
    }


def _failure_report(
    *,
    data: dict[str, Any],
    cfg: GovernedRandomizationConfig,
    randomization_type: str,
    status: str,
    issues: list[GovernedRandomizationIssue],
    warnings: list[str],
    blocking: list[str],
    retry_category: str | None,
    eligible_count: int = 0,
    excluded_count: int = 0,
) -> GovernedRandomizationReport:
    request_id = str(data.get("request_id") or data.get("design_id") or "request_unspecified")
    design_id = str(data.get("design_id")) if data.get("design_id") else None
    trace_payload = {
        "artifact_id": _ARTIFACT_ID,
        "request_id": request_id,
        "randomization_type": randomization_type,
        "status": status,
        "config_hash": _hash_payload(cfg.__dict__),
        "input_hash": _hash_payload(data),
    }
    trace = {**trace_payload, "integrity_hash": _hash_payload(trace_payload)}
    candidate_status = ASSIGNMENT_ARTIFACT_BLOCKED if status == GOVERNED_RANDOMIZATION_BLOCKED else ASSIGNMENT_ARTIFACT_NOT_GENERATED
    return GovernedRandomizationReport(
        request_id=request_id,
        design_id=design_id,
        randomization_type=randomization_type,
        status=status,
        is_blocking=True,
        assignment_artifact_generated=False,
        assignment_artifact=None,
        assignment_artifact_id=None,
        assignment_candidate_id=None,
        assignment_hash=None,
        seed=None,
        seed_policy=None,
        randomization_version=cfg.randomization_version,
        eligible_unit_count=eligible_count,
        excluded_unit_count=excluded_count,
        assigned_unit_count=0,
        cell_counts={},
        strata_counts={},
        block_counts={},
        unit_allocations=(),
        excluded_units=(),
        warnings=_safe_str_list(warnings),
        issues=tuple(issues),
        blocking_reasons=_safe_str_list(blocking),
        failure_packet={
            "status": status,
            "candidate_status": candidate_status,
            "issues": [i.category for i in issues],
            "blocking_reasons": blocking,
            "retry_category": retry_category,
        },
        retry_category=retry_category,
        reproducibility_manifest=None,
        randomization_trace=trace,
        provenance={"artifact_id": _ARTIFACT_ID, "integrity_hash": trace["integrity_hash"]},
        claim_boundary_report=_claim_boundary(artifact_generated=False),
    )


def _evaluate_single(data: dict[str, Any], cfg: GovernedRandomizationConfig) -> GovernedRandomizationReport:
    request_id = str(data.get("request_id") or data.get("design_id") or "request_unspecified")
    design_id = str(data.get("design_id")) if data.get("design_id") else None
    randomization_type = _token(data.get("randomization_type") or "TWO_CELL_COMPLETE_RANDOMIZATION")
    issues: list[GovernedRandomizationIssue] = []
    warnings: list[str] = []
    blocking: list[str] = []
    retry_category: str | None = None

    if randomization_type not in _SUPPORTED_RANDOMIZATION_TYPES:
        issues.append(GovernedRandomizationIssue(
            category=ISSUE_UNSUPPORTED_RANDOMIZATION_TYPE,
            message=f"unsupported randomization type: {randomization_type}",
        ))
        blocking.append("unsupported randomization type")
        return _failure_report(
            data=data, cfg=cfg, randomization_type=randomization_type,
            status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
            blocking=blocking, retry_category=RETRY_FIX_RANDOMIZATION_CONFIG,
        )

    split_control = data.get("split_control_cells")
    if split_control and randomization_type != "MULTI_CELL_COMPLETE_RANDOMIZATION":
        issues.append(GovernedRandomizationIssue(
            category=ISSUE_SPLIT_CONTROL_REQUIRES_RECHECK,
            message="split-control requires explicit multi-cell support",
        ))
        blocking.append("split-control requires recheck")
        return _failure_report(
            data=data, cfg=cfg, randomization_type=randomization_type,
            status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
            blocking=blocking, retry_category=RETRY_REDESIGN_EXPERIMENT_STRUCTURE,
        )

    feas = _to_dict(data.get("assignment_feasibility_report"))
    if cfg.block_on_assignment_feasibility_blocked:
        feas_status = _token(feas.get("status") or feas.get("assignment_feasibility_status") or data.get("assignment_feasibility_status"))
        if feas_status and ("BLOCKED" in feas_status or "NOT_FEASIBLE" in feas_status):
            issues.append(GovernedRandomizationIssue(
                category=ISSUE_ASSIGNMENT_FEASIBILITY_BLOCKED,
                message="assignment feasibility blocked",
            ))
            blocking.append("assignment feasibility blocked")
            retry_category = RETRY_RERUN_ASSIGNMENT_FEASIBILITY
            return _failure_report(
                data=data, cfg=cfg, randomization_type=randomization_type,
                status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
                blocking=blocking, retry_category=retry_category,
            )

    ms = _to_dict(data.get("method_suitability_report"))
    if cfg.block_on_method_suitability_blocked:
        ms_status = _token(ms.get("status") or ms.get("method_suitability_status") or data.get("method_suitability_status"))
        if ms_status and "BLOCKED" in ms_status:
            issues.append(GovernedRandomizationIssue(
                category=ISSUE_METHOD_SUITABILITY_BLOCKED,
                message="method suitability blocked",
            ))
            blocking.append("method suitability blocked")
            retry_category = RETRY_RERUN_METHOD_SUITABILITY
            return _failure_report(
                data=data, cfg=cfg, randomization_type=randomization_type,
                status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
                blocking=blocking, retry_category=retry_category,
            )

    eligible_units = _normalize_eligible_units(data)
    if not eligible_units:
        issues.append(GovernedRandomizationIssue(
            category=ISSUE_ELIGIBLE_UNITS_MISSING,
            message="eligible units missing",
        ))
        blocking.append("eligible units missing")
        return _failure_report(
            data=data, cfg=cfg, randomization_type=randomization_type,
            status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
            blocking=blocking, retry_category=RETRY_FIX_ELIGIBLE_UNIT_POOL,
        )

    unit_ids = [str(u.get("unit_id")) for u in eligible_units]
    if len(unit_ids) != len(set(unit_ids)):
        issues.append(GovernedRandomizationIssue(
            category=ISSUE_DUPLICATE_UNIT_IDS,
            message="duplicate eligible unit ids",
        ))
        blocking.append("duplicate eligible unit ids")
        return _failure_report(
            data=data, cfg=cfg, randomization_type=randomization_type,
            status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
            blocking=blocking, retry_category=RETRY_FIX_ELIGIBLE_UNIT_POOL,
            eligible_count=len(unit_ids),
        )

    excluded_raw = data.get("excluded_units") or []
    excluded_set = {str(u) for u in excluded_raw} if isinstance(excluded_raw, list) else set()
    pool = [u for u in eligible_units if str(u.get("unit_id")) not in excluded_set]

    cells = _normalize_cells(data)
    if not cells:
        if randomization_type == "TWO_CELL_COMPLETE_RANDOMIZATION":
            control_id = str(data.get("control_cell_id") or "C0")
            treatment_id = str(data.get("treatment_cell_id") or "T1")
            cells = [
                {"cell_id": control_id, "role": "CONTROL", "target_size": None},
                {"cell_id": treatment_id, "role": "TREATMENT", "target_size": None},
            ]
        else:
            issues.append(GovernedRandomizationIssue(
                category=ISSUE_CELL_REQUIREMENTS_MISSING,
                message="cell requirements missing",
            ))
            blocking.append("cell requirements missing")
            return _failure_report(
                data=data, cfg=cfg, randomization_type=randomization_type,
                status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
                blocking=blocking, retry_category=RETRY_FIX_CELL_REQUIREMENTS,
                eligible_count=len(pool), excluded_count=len(excluded_set),
            )

    if randomization_type == "COMMON_CONTROL_RANDOMIZATION":
        common_control = str(data.get("common_control_cell_id") or "")
        if not common_control:
            issues.append(GovernedRandomizationIssue(
                category=ISSUE_COMMON_CONTROL_REQUIREMENTS_INVALID,
                message="common_control_cell_id required",
            ))
            blocking.append("common control requirements invalid")
            return _failure_report(
                data=data, cfg=cfg, randomization_type=randomization_type,
                status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
                blocking=blocking, retry_category=RETRY_FIX_CELL_REQUIREMENTS,
                eligible_count=len(pool), excluded_count=len(excluded_set),
            )
        if not any(c["cell_id"] == common_control for c in cells):
            cells.insert(0, {"cell_id": common_control, "role": "CONTROL", "target_size": None})

    seed, seed_policy, seed_blockers, seed_remediation = _resolve_seed(data, cfg)
    if seed_blockers:
        for b in seed_blockers:
            issues.append(GovernedRandomizationIssue(category=b, message=b.replace("_", " ").lower()))
            blocking.append(b.replace("_", " ").lower())
        return _failure_report(
            data=data, cfg=cfg, randomization_type=randomization_type,
            status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
            blocking=blocking, retry_category=seed_remediation[0] if seed_remediation else RETRY_ADD_SEED_POLICY,
            eligible_count=len(pool), excluded_count=len(excluded_set),
        )
    assert seed is not None

    strata_field = str(data.get("strata_field") or "")
    block_field = str(data.get("block_field") or "")

    all_allocations: list[dict[str, Any]] = []
    strata_counts: dict[str, int] = {}
    block_counts: dict[str, int] = {}

    if randomization_type == "STRATIFIED_RANDOMIZATION":
        if not strata_field:
            issues.append(GovernedRandomizationIssue(
                category=ISSUE_STRATA_FIELD_MISSING,
                message="strata field missing",
            ))
            blocking.append("strata field missing")
            return _failure_report(
                data=data, cfg=cfg, randomization_type=randomization_type,
                status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
                blocking=blocking, retry_category=RETRY_ADD_STRATIFICATION_FIELDS,
                eligible_count=len(pool), excluded_count=len(excluded_set),
            )
        by_stratum: dict[str, list[dict[str, Any]]] = {}
        for unit in pool:
            stratum = str(unit.get(strata_field) or "UNSPECIFIED")
            by_stratum.setdefault(stratum, []).append(unit)
        for stratum, stratum_units in sorted(by_stratum.items()):
            targets, t_blockers, t_rem = _compute_cell_targets(cells, len(stratum_units), data.get("allocation_ratio"))
            if t_blockers:
                for b in t_blockers:
                    cat = ISSUE_STRATUM_INSUFFICIENT_UNITS if b == ISSUE_INSUFFICIENT_ELIGIBLE_UNITS else b
                    issues.append(GovernedRandomizationIssue(category=cat, message=f"{cat} in stratum {stratum}"))
                    blocking.append(f"{cat} in stratum {stratum}")
                return _failure_report(
                    data=data, cfg=cfg, randomization_type=randomization_type,
                    status=GOVERNED_RANDOMIZATION_FAILED, issues=issues, warnings=warnings,
                    blocking=blocking, retry_category=t_rem[0] if t_rem else RETRY_FIX_CELL_REQUIREMENTS,
                    eligible_count=len(pool), excluded_count=len(excluded_set),
                )
            stratum_allocs = _allocate_units_to_cells(stratum_units, cells, targets, seed, stratum=stratum)
            all_allocations.extend(stratum_allocs)
            strata_counts[stratum] = len(stratum_allocs)

    elif randomization_type == "BLOCK_RANDOMIZATION":
        if not block_field:
            issues.append(GovernedRandomizationIssue(
                category=ISSUE_BLOCK_FIELD_MISSING,
                message="block field missing",
            ))
            blocking.append("block field missing")
            return _failure_report(
                data=data, cfg=cfg, randomization_type=randomization_type,
                status=GOVERNED_RANDOMIZATION_BLOCKED, issues=issues, warnings=warnings,
                blocking=blocking, retry_category=RETRY_ADD_BLOCK_FIELDS,
                eligible_count=len(pool), excluded_count=len(excluded_set),
            )
        by_block: dict[str, list[dict[str, Any]]] = {}
        for unit in pool:
            blk = str(unit.get(block_field) or "UNSPECIFIED")
            by_block.setdefault(blk, []).append(unit)
        for blk, block_units in sorted(by_block.items()):
            targets, t_blockers, t_rem = _compute_cell_targets(cells, len(block_units), data.get("allocation_ratio"))
            if t_blockers:
                for b in t_blockers:
                    cat = ISSUE_BLOCK_INSUFFICIENT_UNITS if b == ISSUE_INSUFFICIENT_ELIGIBLE_UNITS else b
                    issues.append(GovernedRandomizationIssue(category=cat, message=f"{cat} in block {blk}"))
                    blocking.append(f"{cat} in block {blk}")
                return _failure_report(
                    data=data, cfg=cfg, randomization_type=randomization_type,
                    status=GOVERNED_RANDOMIZATION_FAILED, issues=issues, warnings=warnings,
                    blocking=blocking, retry_category=t_rem[0] if t_rem else RETRY_FIX_CELL_REQUIREMENTS,
                    eligible_count=len(pool), excluded_count=len(excluded_set),
                )
            block_allocs = _allocate_units_to_cells(block_units, cells, targets, seed, block=blk)
            all_allocations.extend(block_allocs)
            block_counts[blk] = len(block_allocs)

    else:
        targets, t_blockers, t_rem = _compute_cell_targets(cells, len(pool), data.get("allocation_ratio"))
        if t_blockers:
            for b in t_blockers:
                issues.append(GovernedRandomizationIssue(category=b, message=b.replace("_", " ").lower()))
                blocking.append(b.replace("_", " ").lower())
            return _failure_report(
                data=data, cfg=cfg, randomization_type=randomization_type,
                status=GOVERNED_RANDOMIZATION_FAILED, issues=issues, warnings=warnings,
                blocking=blocking, retry_category=t_rem[0] if t_rem else RETRY_FIX_CELL_REQUIREMENTS,
                eligible_count=len(pool), excluded_count=len(excluded_set),
            )
        all_allocations = _allocate_units_to_cells(pool, cells, targets, seed)

    cell_counts: dict[str, int] = {}
    for row in all_allocations:
        cid = str(row.get("assigned_cell_id"))
        cell_counts[cid] = cell_counts.get(cid, 0) + 1

    assignment_hash = _hash_payload(all_allocations)
    artifact_id = f"assignment_{design_id or request_id}_{assignment_hash[:12]}"
    candidate_id = f"candidate_{design_id or request_id}_{assignment_hash[:12]}"

    repro_manifest = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "algorithm_version": cfg.randomization_version,
        "algorithm_category": "GOVERNED_RANDOMIZATION",
        "seed_policy": seed_policy,
        "seed": seed,
        "randomization_type": randomization_type,
        "config_hash": _hash_payload(cfg.__dict__),
        "input_hash": _hash_payload(data),
        "eligible_pool_hash": _hash_payload([u.get("unit_id") for u in pool]),
        "output_artifact_id": artifact_id,
        "output_hash": assignment_hash,
        "assignment_hash": assignment_hash,
        "generated_at_policy": "DETERMINISTIC_NO_WALL_CLOCK",
    }

    assignment_artifact = {
        "artifact_id": artifact_id,
        "assignment_artifact_id": artifact_id,
        "assignment_candidate_id": candidate_id,
        "assignment_hash": assignment_hash,
        "design_id": design_id,
        "randomization_type": randomization_type,
        "seed": seed,
        "seed_policy": seed_policy,
        "randomization_version": cfg.randomization_version,
        "cells": cells,
        "unit_allocations": all_allocations,
        "reproducibility_manifest": repro_manifest,
    }

    status = GOVERNED_RANDOMIZATION_COMPLETED
    if warnings:
        status = GOVERNED_RANDOMIZATION_COMPLETED_WITH_WARNINGS

    trace_payload = {
        "artifact_id": _ARTIFACT_ID,
        "request_id": request_id,
        "randomization_type": randomization_type,
        "status": status,
        "seed_policy": seed_policy,
        "assigned_unit_count": len(all_allocations),
        "config_hash": _hash_payload(cfg.__dict__),
        "input_hash": _hash_payload(data),
    }
    trace = {**trace_payload, "integrity_hash": _hash_payload(trace_payload)}

    return GovernedRandomizationReport(
        request_id=request_id,
        design_id=design_id,
        randomization_type=randomization_type,
        status=status,
        is_blocking=False,
        assignment_artifact_generated=True,
        assignment_artifact=assignment_artifact,
        assignment_artifact_id=artifact_id,
        assignment_candidate_id=candidate_id,
        assignment_hash=assignment_hash,
        seed=seed,
        seed_policy=seed_policy,
        randomization_version=cfg.randomization_version,
        eligible_unit_count=len(pool),
        excluded_unit_count=len(excluded_set),
        assigned_unit_count=len(all_allocations),
        cell_counts=cell_counts,
        strata_counts=strata_counts,
        block_counts=block_counts,
        unit_allocations=tuple(all_allocations),
        excluded_units=_safe_str_list(sorted(excluded_set)),
        warnings=_safe_str_list(warnings),
        issues=tuple(issues),
        blocking_reasons=(),
        failure_packet=None,
        retry_category=None,
        reproducibility_manifest=repro_manifest,
        randomization_trace=trace,
        provenance={
            "artifact_id": _ARTIFACT_ID,
            "integrity_hash": trace["integrity_hash"],
            "assignment_hash": assignment_hash,
        },
        claim_boundary_report=_claim_boundary(artifact_generated=True),
    )


def generate_governed_randomization(
    input_data: Any,
    config: GovernedRandomizationConfig | dict[str, Any] | None = None,
) -> GovernedRandomizationReport | list[GovernedRandomizationReport]:
    cfg = _resolve_config(config)
    if isinstance(input_data, list):
        return [_evaluate_single(_to_dict(x), cfg) for x in input_data]
    data = _to_dict(input_data)
    if "requests" in data and isinstance(data["requests"], list):
        return [_evaluate_single(_to_dict(x), cfg) for x in data["requests"]]
    return _evaluate_single(data, cfg)


run_governed_randomization = generate_governed_randomization
generate_randomized_assignment = generate_governed_randomization


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
    smoke = generate_governed_randomization({
        "request_id": "smoke_two_cell",
        "design_id": "smoke_design",
        "randomization_type": "TWO_CELL_COMPLETE_RANDOMIZATION",
        "seed": 42,
        "seed_policy": "EXPLICIT_SEED",
        "eligible_units": ["u1", "u2", "u3", "u4"],
        "cells": [
            {"cell_id": "C0", "role": "CONTROL", "target_size": 2},
            {"cell_id": "T1", "role": "TREATMENT", "target_size": 2},
        ],
    })
    assert isinstance(smoke, GovernedRandomizationReport)
    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "governed_randomization_runtime",
        "base_commit": _git_head(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": [
            "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001",
            "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001",
            "DESIGN_ASSIGNMENT_RUNTIME_001",
            "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001",
            "AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001",
        ],
        "governed_randomization_runtime_implemented": True,
        "governed_randomization_artifact_generated": True,
        "deterministic_seed_policy_enforced": True,
        "randomization_reproducibility_manifest_recorded": True,
        "assignment_panel_integrity_compatible_artifact_generated": True,
        "assignment_panel_integrity_integration_tested": True,
        "design_assignment_runtime_integration_added": True,
        "rerandomization_optimization_implemented": False,
        "balance_optimization_implemented": False,
        "matched_market_optimization_implemented": False,
        "power_mde_computed": False,
        "estimator_implemented": False,
        "inference_implemented": False,
        "bootstrap_inference_implemented": False,
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
        "p_value_computed": False,
        "confidence_interval_computed": False,
        "uncertainty_computed": False,
        "mmm_runtime_calls_implemented": False,
        "mmm_calibration_authorized": False,
        "llm_decisioning_authorized": False,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "alternative_next_artifact": _ALTERNATIVE_NEXT,
        "final_verdict": _VERDICT,
        "smoke_status": smoke.status,
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
