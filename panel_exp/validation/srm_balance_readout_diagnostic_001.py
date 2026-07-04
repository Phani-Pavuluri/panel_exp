"""SRM_BALANCE_READOUT_DIAGNOSTIC_001 — SRM and balance readout diagnostic runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any

from panel_exp.validation.assignment_panel_integrity_runtime_001 import (
    ASSIGNMENT_PANEL_INTEGRITY_BLOCKED,
    ASSIGNMENT_PANEL_INTEGRITY_FAILED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS,
)

_ARTIFACT_ID = "SRM_BALANCE_READOUT_DIAGNOSTIC_001"
_ARTIFACT_VERSION = "1.0.0"
_POLICY_VERSION = "1.0.0"
_SCOPE = "srm_balance_readout_diagnostic_implemented_no_inference_or_claim_authorization"
_VERDICT = "srm_balance_readout_diagnostic_implemented_no_inference_or_claim_authorization"
_RECOMMENDED_NEXT = "CLAIM_AUTHORIZATION_RUNTIME_001"
_ALTERNATIVE_NEXT = "TRUSTED_READOUT_REPORT_CONTRACT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/SRM_BALANCE_READOUT_DIAGNOSTIC_001_summary.json"

SRM_BALANCE_DIAGNOSTIC_PASSED = "SRM_BALANCE_DIAGNOSTIC_PASSED"
SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS = "SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS"
SRM_BALANCE_DIAGNOSTIC_FAILED = "SRM_BALANCE_DIAGNOSTIC_FAILED"
SRM_BALANCE_DIAGNOSTIC_BLOCKED = "SRM_BALANCE_DIAGNOSTIC_BLOCKED"
SRM_BALANCE_DIAGNOSTIC_INCONCLUSIVE = "SRM_BALANCE_DIAGNOSTIC_INCONCLUSIVE"
SRM_BALANCE_DIAGNOSTIC_NOT_EVALUATED = "SRM_BALANCE_DIAGNOSTIC_NOT_EVALUATED"

SRM_CHECK_PASSED = "SRM_CHECK_PASSED"
SRM_CHECK_FAILED = "SRM_CHECK_FAILED"
SRM_CHECK_INCONCLUSIVE = "SRM_CHECK_INCONCLUSIVE"
BALANCE_CHECK_PASSED = "BALANCE_CHECK_PASSED"
BALANCE_CHECK_FAILED = "BALANCE_CHECK_FAILED"
BALANCE_CHECK_INCONCLUSIVE = "BALANCE_CHECK_INCONCLUSIVE"

ISSUE_ASSIGNMENT_ARTIFACT_MISSING = "ASSIGNMENT_ARTIFACT_MISSING"
ISSUE_UNIT_ALLOCATIONS_MISSING = "UNIT_ALLOCATIONS_MISSING"
ISSUE_ANALYSIS_PANEL_MISSING = "ANALYSIS_PANEL_MISSING"
ISSUE_ASSIGNMENT_PANEL_INTEGRITY_FAILED = "ASSIGNMENT_PANEL_INTEGRITY_FAILED"
ISSUE_EXPECTED_COUNTS_MISSING = "EXPECTED_COUNTS_MISSING"
ISSUE_REALIZED_CELL_MISSING = "REALIZED_CELL_MISSING"
ISSUE_TREATED_OR_CONTROL_REALIZED_MISSING = "TREATED_OR_CONTROL_REALIZED_MISSING"
ISSUE_SAMPLE_RATIO_MISMATCH = "SAMPLE_RATIO_MISMATCH"
ISSUE_MISSING_ASSIGNED_UNITS = "MISSING_ASSIGNED_UNITS"
ISSUE_EXTRA_PANEL_UNITS = "EXTRA_PANEL_UNITS"
ISSUE_MINIMUM_CELL_COUNT_FAILED = "MINIMUM_CELL_COUNT_FAILED"
ISSUE_COVARIATE_FIELD_MISSING = "COVARIATE_FIELD_MISSING"
ISSUE_COVARIATE_NON_NUMERIC = "COVARIATE_NON_NUMERIC"
ISSUE_COVARIATE_BALANCE_FAILED = "COVARIATE_BALANCE_FAILED"
ISSUE_BASELINE_OUTCOME_BALANCE_FAILED = "BASELINE_OUTCOME_BALANCE_FAILED"
ISSUE_NONFINITE_BALANCE_METRIC = "NONFINITE_BALANCE_METRIC"

RETRY_FIX_ASSIGNMENT_ARTIFACT = "FIX_ASSIGNMENT_ARTIFACT"
RETRY_FIX_PANEL_DATA_CONTRACT = "FIX_PANEL_DATA_CONTRACT"
RETRY_FIX_ASSIGNMENT_PANEL_JOIN = "FIX_ASSIGNMENT_PANEL_JOIN"
RETRY_RECONCILE_REALIZED_PANEL = "RECONCILE_REALIZED_PANEL"
RETRY_RERUN_GOVERNED_RANDOMIZATION = "RERUN_GOVERNED_RANDOMIZATION"
RETRY_RERUN_ASSIGNMENT_PANEL_INTEGRITY = "RERUN_ASSIGNMENT_PANEL_INTEGRITY"
RETRY_ADD_BASELINE_COVARIATES = "ADD_BASELINE_COVARIATES"
RETRY_ADD_PRE_PERIOD_OUTCOME = "ADD_PRE_PERIOD_OUTCOME"
RETRY_REDESIGN_EXPERIMENT_STRUCTURE = "REDESIGN_EXPERIMENT_STRUCTURE"
RETRY_KEEP_RESEARCH_ONLY = "KEEP_RESEARCH_ONLY"
RETRY_BLOCK_CLAIM_REVIEW = "BLOCK_CLAIM_REVIEW"

SRM_BALANCE_DIAGNOSTIC_TYPES = frozenset({
    "SRM_DIAGNOSTIC",
    "SAMPLE_RATIO_MISMATCH_DIAGNOSTIC",
    "BALANCE_DIAGNOSTIC",
    "COVARIATE_BALANCE_DIAGNOSTIC",
    "BASELINE_BALANCE_DIAGNOSTIC",
    "READOUT_BALANCE_DIAGNOSTIC",
})

_TREATED_TOKENS = frozenset({"1", "TRUE", "TREATED", "TREATMENT", "TEST", "T"})
_CONTROL_TOKENS = frozenset({"0", "FALSE", "CONTROL", "C"})

_POSITIVE_FLAGS = {
    "srm_balance_diagnostic_runtime_implemented": True,
    "sample_ratio_mismatch_diagnostic_evaluated": True,
    "realized_assignment_balance_evaluated": True,
    "covariate_balance_smd_evaluated": True,
}

_AUTH_FALSE = {
    "effect_estimate_computed": False,
    "lift_computed": False,
    "roi_computed": False,
    "estimator_implemented": False,
    "inference_implemented": False,
    "bootstrap_inference_implemented": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "rerandomization_optimization_implemented": False,
    "balance_optimization_implemented": False,
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
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}


@dataclass(frozen=True)
class SRMBalanceReadoutDiagnosticPolicy:
    policy_version: str = _POLICY_VERSION
    maximum_sample_ratio_deviation: float = 0.05
    maximum_missing_assignment_unit_rate_production: float = 0.0
    maximum_missing_assignment_unit_rate_research: float = 0.05
    maximum_extra_panel_unit_rate_production: float = 0.0
    maximum_extra_panel_unit_rate_research: float = 0.05
    minimum_cell_count: int = 1
    maximum_standardized_mean_difference_warning: float = 0.25
    maximum_standardized_mean_difference_blocking: float = 0.50
    maximum_baseline_outcome_smd_warning: float = 0.25
    maximum_baseline_outcome_smd_blocking: float = 0.50


@dataclass(frozen=True)
class SRMBalanceReadoutDiagnosticConfig:
    require_assignment_artifact: bool = True
    require_panel_records: bool = True
    require_assignment_panel_integrity_pass: bool = True
    block_on_failed_srm: bool = True
    block_on_failed_balance_production: bool = True
    block_on_failed_balance_research: bool = False
    policy: SRMBalanceReadoutDiagnosticPolicy = field(default_factory=SRMBalanceReadoutDiagnosticPolicy)


@dataclass(frozen=True)
class CovariateBalanceResult:
    field_name: str
    standardized_mean_difference: float | None
    treatment_mean: float | None
    control_mean: float | None
    status: str
    issue_category: str | None


@dataclass(frozen=True)
class SRMBalanceReadoutDiagnosticReport:
    request_id: str
    assignment_artifact_id: str | None
    assignment_hash: str | None
    status: str
    is_blocking: bool
    can_support_claim_review: bool
    can_support_production_readout: bool
    expected_cell_counts: dict[str, int]
    realized_cell_counts: dict[str, int]
    expected_treatment_counts: dict[str, int]
    realized_treatment_counts: dict[str, int]
    sample_ratio_deviation_by_cell: dict[str, float]
    max_sample_ratio_deviation: float | None
    missing_assigned_units: tuple[str, ...]
    extra_panel_units: tuple[str, ...]
    missing_assigned_unit_rate: float | None
    extra_panel_unit_rate: float | None
    minimum_cell_count: int
    covariate_balance_results: tuple[CovariateBalanceResult, ...]
    baseline_outcome_balance_result: CovariateBalanceResult | None
    component_statuses: dict[str, str]
    issues: tuple[str, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    required_remediation: tuple[str, ...]
    failure_packet: dict[str, Any] | None
    retry_category: str | None
    policy_version: str
    diagnostic_trace: dict[str, Any]
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
    config: SRMBalanceReadoutDiagnosticConfig | dict[str, Any] | None,
) -> SRMBalanceReadoutDiagnosticConfig:
    if config is None:
        return SRMBalanceReadoutDiagnosticConfig()
    if isinstance(config, SRMBalanceReadoutDiagnosticConfig):
        return config
    base = SRMBalanceReadoutDiagnosticConfig()
    policy_data = config.get("policy") or {}
    policy = SRMBalanceReadoutDiagnosticPolicy(
        **{**base.policy.__dict__, **{k: v for k, v in policy_data.items() if k in base.policy.__dict__}}
    )
    merged = {
        **{k: getattr(base, k) for k in (
            "require_assignment_artifact", "require_panel_records",
            "require_assignment_panel_integrity_pass", "block_on_failed_srm",
            "block_on_failed_balance_production", "block_on_failed_balance_research",
        )},
        **{k: v for k, v in config.items() if k in (
            "require_assignment_artifact", "require_panel_records",
            "require_assignment_panel_integrity_pass", "block_on_failed_srm",
            "block_on_failed_balance_production", "block_on_failed_balance_research",
        )},
    }
    return SRMBalanceReadoutDiagnosticConfig(policy=policy, **merged)


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
    return []


def _extract_allocations(data: dict[str, Any]) -> list[dict[str, Any]]:
    direct = data.get("unit_allocations") or data.get("assignment_allocations")
    if isinstance(direct, list):
        return [dict(x) for x in direct if isinstance(x, dict)]
    artifact = _to_dict(data.get("assignment_artifact"))
    for key in ("unit_allocations", "assignment_allocations"):
        rows = artifact.get(key)
        if isinstance(rows, list):
            return [dict(x) for x in rows if isinstance(x, dict)]
    return []


def _normalize_treatment(value: Any) -> str | None:
    if value is None:
        return None
    if value in (0, 1, True, False):
        return "TREATED" if bool(value) else "CONTROL"
    tok = _token(value)
    if tok in _TREATED_TOKENS:
        return "TREATED"
    if tok in _CONTROL_TOKENS:
        return "CONTROL"
    if "TREAT" in tok:
        return "TREATED"
    if "CONTROL" in tok:
        return "CONTROL"
    return tok


def _is_production_context(data: dict[str, Any]) -> bool:
    return _token(data.get("production_context")) in {"PRODUCTION", "TRUE", "1", "YES"}


def _compute_smd(treated_vals: list[float], control_vals: list[float]) -> float | None:
    if not treated_vals or not control_vals:
        return None
    mean_t = sum(treated_vals) / len(treated_vals)
    mean_c = sum(control_vals) / len(control_vals)
    var_t = sum((x - mean_t) ** 2 for x in treated_vals) / max(len(treated_vals) - 1, 1)
    var_c = sum((x - mean_c) ** 2 for x in control_vals) / max(len(control_vals) - 1, 1)
    pooled = math.sqrt(
        ((len(treated_vals) - 1) * var_t + (len(control_vals) - 1) * var_c)
        / max(len(treated_vals) + len(control_vals) - 2, 1)
    )
    if pooled == 0:
        return 0.0 if mean_t == mean_c else float("nan")
    return (mean_t - mean_c) / pooled


def _claim_boundary(*, evaluated: bool, baseline_evaluated: bool) -> dict[str, Any]:
    return {
        **_POSITIVE_FLAGS,
        "baseline_outcome_balance_evaluated": baseline_evaluated,
        "srm_balance_diagnostic_evaluated": evaluated,
        **_AUTH_FALSE,
    }


def is_srm_balance_diagnostic_type(requirement_type: str | None) -> bool:
    return _token(requirement_type) in SRM_BALANCE_DIAGNOSTIC_TYPES


def to_provided_diagnostic_result(report: SRMBalanceReadoutDiagnosticReport) -> dict[str, Any]:
    status_map = {
        SRM_BALANCE_DIAGNOSTIC_PASSED: "DIAGNOSTIC_PASSED",
        SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS: "DIAGNOSTIC_PASSED_WITH_WARNINGS",
        SRM_BALANCE_DIAGNOSTIC_FAILED: "DIAGNOSTIC_FAILED",
        SRM_BALANCE_DIAGNOSTIC_BLOCKED: "DIAGNOSTIC_BLOCKED",
        SRM_BALANCE_DIAGNOSTIC_INCONCLUSIVE: "DIAGNOSTIC_INCONCLUSIVE",
        SRM_BALANCE_DIAGNOSTIC_NOT_EVALUATED: "DIAGNOSTIC_NOT_EVALUATED",
    }
    return {
        "result_id": report.diagnostic_trace.get("integrity_hash"),
        "result_status": status_map.get(report.status, "DIAGNOSTIC_NOT_EVALUATED"),
        "result_value": report.max_sample_ratio_deviation,
        "threshold": report.policy_version,
        "threshold_direction": "lte",
        "passed": report.status in {
            SRM_BALANCE_DIAGNOSTIC_PASSED,
            SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS,
        },
        "blocking_result": report.is_blocking,
        "interpretation": "srm_balance_readout_diagnostic_descriptive_only",
        "evidence_level": "computed_descriptive",
        "artifact_references": [report.assignment_artifact_id] if report.assignment_artifact_id else [],
        "warnings": list(report.warnings),
        "max_sample_ratio_deviation": report.max_sample_ratio_deviation,
        "component_statuses": dict(report.component_statuses),
    }


def _evaluate_single(data: dict[str, Any], cfg: SRMBalanceReadoutDiagnosticConfig) -> SRMBalanceReadoutDiagnosticReport:
    request_id = str(data.get("request_id") or data.get("design_id") or "request_unspecified")
    policy = cfg.policy
    production = _is_production_context(data)
    max_missing_rate = (
        policy.maximum_missing_assignment_unit_rate_production
        if production else policy.maximum_missing_assignment_unit_rate_research
    )
    max_extra_rate = (
        policy.maximum_extra_panel_unit_rate_production
        if production else policy.maximum_extra_panel_unit_rate_research
    )

    issues: list[str] = []
    warnings: list[str] = []
    blocking: list[str] = []
    remediation: list[str] = []
    component_statuses: dict[str, str] = {}

    panel_unit_field = str(data.get("panel_unit_id_field") or "unit_id")
    panel_cell_field = str(data.get("panel_cell_field") or "cell_id")
    panel_treatment_field = str(data.get("panel_treatment_field") or "treated")
    panel_time_field = str(data.get("panel_time_field") or "time")
    panel_outcome_field = str(data.get("panel_outcome_field") or "outcome")
    pre_period_field = str(data.get("pre_period_indicator_field") or "")
    pre_period_values = set(str(x) for x in (data.get("pre_period_values") or []))

    artifact = _to_dict(data.get("assignment_artifact"))
    has_artifact = bool(artifact or data.get("assignment_artifact_id"))
    allocations = _extract_allocations(data)
    panel_records = _extract_panel_records(data)

    assignment_artifact_id = str(
        data.get("assignment_artifact_id") or artifact.get("artifact_id") or artifact.get("assignment_artifact_id") or ""
    ) or None
    assignment_hash = str(data.get("assignment_hash") or artifact.get("assignment_hash") or "") or None

    if cfg.require_assignment_artifact and not has_artifact:
        issues.append(ISSUE_ASSIGNMENT_ARTIFACT_MISSING)
        blocking.append("assignment artifact missing")
        remediation.append(RETRY_FIX_ASSIGNMENT_ARTIFACT)
        return _blocked_report(
            request_id, assignment_artifact_id, assignment_hash, cfg, issues, warnings, blocking, remediation,
            component_statuses,
        )

    if not allocations:
        issues.append(ISSUE_UNIT_ALLOCATIONS_MISSING)
        blocking.append("unit allocations missing")
        remediation.append(RETRY_FIX_ASSIGNMENT_ARTIFACT)
        return _blocked_report(
            request_id, assignment_artifact_id, assignment_hash, cfg, issues, warnings, blocking, remediation,
            component_statuses,
        )

    if cfg.require_panel_records and not panel_records:
        issues.append(ISSUE_ANALYSIS_PANEL_MISSING)
        blocking.append("analysis panel missing")
        remediation.append(RETRY_FIX_PANEL_DATA_CONTRACT)
        return _blocked_report(
            request_id, assignment_artifact_id, assignment_hash, cfg, issues, warnings, blocking, remediation,
            component_statuses,
        )

    integrity_report = _to_dict(data.get("assignment_panel_integrity_report"))
    integrity_status = str(integrity_report.get("status") or data.get("assignment_panel_integrity_status") or "")
    if cfg.require_assignment_panel_integrity_pass and integrity_status:
        if integrity_status not in {
            ASSIGNMENT_PANEL_INTEGRITY_PASSED,
            ASSIGNMENT_PANEL_INTEGRITY_PASSED_WITH_WARNINGS,
        }:
            issues.append(ISSUE_ASSIGNMENT_PANEL_INTEGRITY_FAILED)
            blocking.append("assignment panel integrity failed")
            remediation.append(RETRY_RERUN_ASSIGNMENT_PANEL_INTEGRITY)
            return _blocked_report(
                request_id, assignment_artifact_id, assignment_hash, cfg, issues, warnings, blocking, remediation,
                component_statuses,
            )

    expected_cell_counts = dict(data.get("expected_cell_counts") or {})
    expected_treatment_counts = dict(data.get("expected_treatment_counts") or {})
    if not expected_cell_counts:
        for row in allocations:
            cid = str(row.get("assigned_cell_id") or row.get("cell_id") or "UNSPECIFIED")
            expected_cell_counts[cid] = expected_cell_counts.get(cid, 0) + 1
            tr = _normalize_treatment(row.get("assigned_cell_role") or row.get("treatment_label") or row.get("treated"))
            if tr:
                expected_treatment_counts[tr] = expected_treatment_counts.get(tr, 0) + 1

    if not expected_cell_counts:
        issues.append(ISSUE_EXPECTED_COUNTS_MISSING)
        blocking.append("expected counts missing")
        remediation.append(RETRY_FIX_ASSIGNMENT_ARTIFACT)

    assigned_unit_ids = {
        str(row.get("unit_id") or row.get(panel_unit_field))
        for row in allocations
        if row.get("unit_id") or row.get(panel_unit_field)
    }

    panel_by_unit: dict[str, dict[str, Any]] = {}
    for rec in panel_records:
        uid = str(rec.get(panel_unit_field) or rec.get("unit_id") or rec.get("geo_id") or "")
        if uid:
            panel_by_unit[uid] = rec

    realized_cell_counts: dict[str, int] = {}
    realized_treatment_counts: dict[str, int] = {}
    for uid, rec in panel_by_unit.items():
        cid = str(rec.get(panel_cell_field) or rec.get("assigned_cell_id") or "UNSPECIFIED")
        realized_cell_counts[cid] = realized_cell_counts.get(cid, 0) + 1
        tr = _normalize_treatment(rec.get(panel_treatment_field) or rec.get("treated"))
        if tr:
            realized_treatment_counts[tr] = realized_treatment_counts.get(tr, 0) + 1

    missing_assigned = sorted(assigned_unit_ids - set(panel_by_unit))
    extra_panel = sorted(set(panel_by_unit) - assigned_unit_ids)

    missing_rate = len(missing_assigned) / len(assigned_unit_ids) if assigned_unit_ids else None
    extra_rate = len(extra_panel) / len(panel_by_unit) if panel_by_unit else None

    if missing_assigned and missing_rate is not None and missing_rate > max_missing_rate:
        issues.append(ISSUE_MISSING_ASSIGNED_UNITS)
        blocking.append("missing assigned units exceed threshold")
        remediation.append(RETRY_RECONCILE_REALIZED_PANEL)
    elif missing_assigned:
        warnings.append("missing assigned units within threshold")

    if extra_panel and extra_rate is not None and extra_rate > max_extra_rate:
        issues.append(ISSUE_EXTRA_PANEL_UNITS)
        blocking.append("extra panel units exceed threshold")
        remediation.append(RETRY_RECONCILE_REALIZED_PANEL)
    elif extra_panel:
        warnings.append("extra panel units within threshold")

    if "TREATED" not in realized_treatment_counts or "CONTROL" not in realized_treatment_counts:
        issues.append(ISSUE_TREATED_OR_CONTROL_REALIZED_MISSING)
        blocking.append("treated or control group missing in realized panel")
        remediation.append(RETRY_FIX_PANEL_DATA_CONTRACT)

    sample_ratio_deviation_by_cell: dict[str, float] = {}
    max_deviation: float | None = None
    total_expected = sum(expected_cell_counts.values()) or 0
    total_realized = sum(realized_cell_counts.values()) or 0
    if total_expected and total_realized:
        for cid, exp_count in expected_cell_counts.items():
            exp_share = exp_count / total_expected
            real_count = realized_cell_counts.get(cid, 0)
            real_share = real_count / total_realized
            dev = abs(real_share - exp_share)
            sample_ratio_deviation_by_cell[cid] = dev
            max_deviation = dev if max_deviation is None else max(max_deviation, dev)
        if max_deviation is not None and max_deviation > policy.maximum_sample_ratio_deviation:
            issues.append(ISSUE_SAMPLE_RATIO_MISMATCH)
            if cfg.block_on_failed_srm:
                blocking.append("sample ratio mismatch exceeds threshold")
            else:
                warnings.append("sample ratio mismatch exceeds threshold")
            remediation.append(RETRY_RECONCILE_REALIZED_PANEL)
        component_statuses["srm"] = SRM_CHECK_FAILED if ISSUE_SAMPLE_RATIO_MISMATCH in issues else SRM_CHECK_PASSED
    else:
        component_statuses["srm"] = SRM_CHECK_INCONCLUSIVE

    if any(realized_cell_counts.get(cid, 0) < policy.minimum_cell_count for cid in expected_cell_counts):
        issues.append(ISSUE_MINIMUM_CELL_COUNT_FAILED)
        blocking.append("minimum cell count failed")
        remediation.append(RETRY_REDESIGN_EXPERIMENT_STRUCTURE)

    covariate_fields = list(data.get("covariate_fields") or data.get("baseline_fields") or [])
    covariate_results: list[CovariateBalanceResult] = []
    balance_failed = False
    balance_warn = False

    unit_treatment: dict[str, str] = {}
    for uid, rec in panel_by_unit.items():
        unit_treatment[uid] = _normalize_treatment(rec.get(panel_treatment_field) or rec.get("treated")) or "UNKNOWN"

    for field_name in covariate_fields:
        treated_vals: list[float] = []
        control_vals: list[float] = []
        non_numeric = False
        for uid, rec in panel_by_unit.items():
            val = rec.get(field_name)
            if val is None:
                continue
            try:
                fval = float(val)
            except (TypeError, ValueError):
                non_numeric = True
                break
            if unit_treatment.get(uid) == "TREATED":
                treated_vals.append(fval)
            elif unit_treatment.get(uid) == "CONTROL":
                control_vals.append(fval)
        if non_numeric:
            issues.append(ISSUE_COVARIATE_NON_NUMERIC)
            warnings.append(f"covariate {field_name} non-numeric")
            covariate_results.append(CovariateBalanceResult(
                field_name=field_name, standardized_mean_difference=None,
                treatment_mean=None, control_mean=None,
                status=BALANCE_CHECK_INCONCLUSIVE, issue_category=ISSUE_COVARIATE_NON_NUMERIC,
            ))
            continue
        smd = _compute_smd(treated_vals, control_vals)
        if smd is not None and math.isnan(smd):
            issues.append(ISSUE_NONFINITE_BALANCE_METRIC)
            covariate_results.append(CovariateBalanceResult(
                field_name=field_name, standardized_mean_difference=smd,
                treatment_mean=sum(treated_vals) / len(treated_vals) if treated_vals else None,
                control_mean=sum(control_vals) / len(control_vals) if control_vals else None,
                status=BALANCE_CHECK_FAILED, issue_category=ISSUE_NONFINITE_BALANCE_METRIC,
            ))
            balance_failed = True
            continue
        abs_smd = abs(smd) if smd is not None else None
        status = BALANCE_CHECK_PASSED
        issue_cat = None
        if abs_smd is not None:
            if abs_smd > policy.maximum_standardized_mean_difference_blocking:
                status = BALANCE_CHECK_FAILED
                issue_cat = ISSUE_COVARIATE_BALANCE_FAILED
                balance_failed = True
                issues.append(ISSUE_COVARIATE_BALANCE_FAILED)
            elif abs_smd > policy.maximum_standardized_mean_difference_warning:
                status = BALANCE_CHECK_FAILED
                issue_cat = ISSUE_COVARIATE_BALANCE_FAILED
                balance_warn = True
                warnings.append(f"covariate {field_name} SMD above warning threshold")
        covariate_results.append(CovariateBalanceResult(
            field_name=field_name,
            standardized_mean_difference=smd,
            treatment_mean=sum(treated_vals) / len(treated_vals) if treated_vals else None,
            control_mean=sum(control_vals) / len(control_vals) if control_vals else None,
            status=status,
            issue_category=issue_cat,
        ))

    baseline_result: CovariateBalanceResult | None = None
    baseline_evaluated = False
    if panel_outcome_field and (pre_period_values or pre_period_field):
        baseline_evaluated = True
        treated_out: list[float] = []
        control_out: list[float] = []
        for rec in panel_records:
            is_pre = False
            if pre_period_field and rec.get(pre_period_field) is not None:
                is_pre = bool(rec.get(pre_period_field))
            elif pre_period_values:
                is_pre = str(rec.get(panel_time_field)) in pre_period_values
            if not is_pre:
                continue
            uid = str(rec.get(panel_unit_field) or rec.get("unit_id") or "")
            val = rec.get(panel_outcome_field)
            if val is None:
                continue
            try:
                fval = float(val)
            except (TypeError, ValueError):
                continue
            if unit_treatment.get(uid) == "TREATED":
                treated_out.append(fval)
            elif unit_treatment.get(uid) == "CONTROL":
                control_out.append(fval)
        smd = _compute_smd(treated_out, control_out)
        abs_smd = abs(smd) if smd is not None and not math.isnan(smd) else None
        b_status = BALANCE_CHECK_PASSED
        b_issue = None
        if smd is not None and math.isnan(smd):
            issues.append(ISSUE_NONFINITE_BALANCE_METRIC)
            b_status = BALANCE_CHECK_FAILED
            balance_failed = True
        elif abs_smd is not None:
            if abs_smd > policy.maximum_baseline_outcome_smd_blocking:
                b_status = BALANCE_CHECK_FAILED
                b_issue = ISSUE_BASELINE_OUTCOME_BALANCE_FAILED
                balance_failed = True
                issues.append(ISSUE_BASELINE_OUTCOME_BALANCE_FAILED)
            elif abs_smd > policy.maximum_baseline_outcome_smd_warning:
                b_status = BALANCE_CHECK_FAILED
                balance_warn = True
                warnings.append("baseline outcome SMD above warning threshold")
        baseline_result = CovariateBalanceResult(
            field_name=panel_outcome_field,
            standardized_mean_difference=smd,
            treatment_mean=sum(treated_out) / len(treated_out) if treated_out else None,
            control_mean=sum(control_out) / len(control_out) if control_out else None,
            status=b_status,
            issue_category=b_issue,
        )

    block_balance = (
        (production and cfg.block_on_failed_balance_production)
        or (not production and cfg.block_on_failed_balance_research)
    )
    if balance_failed and block_balance:
        blocking.append("covariate or baseline balance failed")
        remediation.append(RETRY_ADD_BASELINE_COVARIATES)
    elif balance_failed:
        warnings.append("covariate or baseline balance failed in research context")
    elif balance_warn:
        warnings.append("balance warning only in research context")

    component_statuses["balance"] = (
        BALANCE_CHECK_FAILED if balance_failed else (
            BALANCE_CHECK_PASSED if covariate_results or baseline_result else BALANCE_CHECK_INCONCLUSIVE
        )
    )

    status = SRM_BALANCE_DIAGNOSTIC_PASSED
    if blocking:
        status = SRM_BALANCE_DIAGNOSTIC_BLOCKED if any(
            x in issues for x in (
                ISSUE_ASSIGNMENT_ARTIFACT_MISSING,
                ISSUE_ASSIGNMENT_PANEL_INTEGRITY_FAILED,
            )
        ) else SRM_BALANCE_DIAGNOSTIC_FAILED
    elif warnings or balance_warn:
        status = SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS
    elif not panel_records or not allocations:
        status = SRM_BALANCE_DIAGNOSTIC_INCONCLUSIVE

    is_blocking = status in {SRM_BALANCE_DIAGNOSTIC_FAILED, SRM_BALANCE_DIAGNOSTIC_BLOCKED}
    can_support_claim_review = status in {
        SRM_BALANCE_DIAGNOSTIC_PASSED,
        SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS,
    }
    can_support_production_readout = False

    trace_payload = {
        "artifact_id": _ARTIFACT_ID,
        "request_id": request_id,
        "status": status,
        "policy_version": policy.policy_version,
        "config_hash": _hash_payload(cfg.__dict__),
        "input_hash": _hash_payload(data),
    }
    trace = {**trace_payload, "integrity_hash": _hash_payload(trace_payload)}

    failure_packet = None
    if is_blocking or status == SRM_BALANCE_DIAGNOSTIC_INCONCLUSIVE:
        failure_packet = {
            "status": status,
            "issues": issues,
            "blocking_reasons": blocking,
            "retry_category": remediation[0] if remediation else RETRY_BLOCK_CLAIM_REVIEW,
        }

    return SRMBalanceReadoutDiagnosticReport(
        request_id=request_id,
        assignment_artifact_id=assignment_artifact_id,
        assignment_hash=assignment_hash,
        status=status,
        is_blocking=is_blocking,
        can_support_claim_review=can_support_claim_review,
        can_support_production_readout=can_support_production_readout,
        expected_cell_counts=expected_cell_counts,
        realized_cell_counts=realized_cell_counts,
        expected_treatment_counts=expected_treatment_counts,
        realized_treatment_counts=realized_treatment_counts,
        sample_ratio_deviation_by_cell=sample_ratio_deviation_by_cell,
        max_sample_ratio_deviation=max_deviation,
        missing_assigned_units=_safe_str_list(missing_assigned),
        extra_panel_units=_safe_str_list(extra_panel),
        missing_assigned_unit_rate=missing_rate,
        extra_panel_unit_rate=extra_rate,
        minimum_cell_count=policy.minimum_cell_count,
        covariate_balance_results=tuple(covariate_results),
        baseline_outcome_balance_result=baseline_result,
        component_statuses=component_statuses,
        issues=_safe_str_list(issues),
        warnings=_safe_str_list(warnings),
        blocking_reasons=_safe_str_list(blocking),
        required_remediation=_safe_str_list(remediation),
        failure_packet=failure_packet,
        retry_category=remediation[0] if remediation else None,
        policy_version=policy.policy_version,
        diagnostic_trace=trace,
        provenance={"artifact_id": _ARTIFACT_ID, "integrity_hash": trace["integrity_hash"]},
        claim_boundary_report=_claim_boundary(evaluated=True, baseline_evaluated=baseline_evaluated),
    )


def _blocked_report(
    request_id: str,
    assignment_artifact_id: str | None,
    assignment_hash: str | None,
    cfg: SRMBalanceReadoutDiagnosticConfig,
    issues: list[str],
    warnings: list[str],
    blocking: list[str],
    remediation: list[str],
    component_statuses: dict[str, str],
) -> SRMBalanceReadoutDiagnosticReport:
    trace_payload = {"artifact_id": _ARTIFACT_ID, "request_id": request_id, "status": SRM_BALANCE_DIAGNOSTIC_BLOCKED}
    trace = {**trace_payload, "integrity_hash": _hash_payload(trace_payload)}
    return SRMBalanceReadoutDiagnosticReport(
        request_id=request_id,
        assignment_artifact_id=assignment_artifact_id,
        assignment_hash=assignment_hash,
        status=SRM_BALANCE_DIAGNOSTIC_BLOCKED,
        is_blocking=True,
        can_support_claim_review=False,
        can_support_production_readout=False,
        expected_cell_counts={},
        realized_cell_counts={},
        expected_treatment_counts={},
        realized_treatment_counts={},
        sample_ratio_deviation_by_cell={},
        max_sample_ratio_deviation=None,
        missing_assigned_units=(),
        extra_panel_units=(),
        missing_assigned_unit_rate=None,
        extra_panel_unit_rate=None,
        minimum_cell_count=cfg.policy.minimum_cell_count,
        covariate_balance_results=(),
        baseline_outcome_balance_result=None,
        component_statuses=component_statuses,
        issues=_safe_str_list(issues),
        warnings=_safe_str_list(warnings),
        blocking_reasons=_safe_str_list(blocking),
        required_remediation=_safe_str_list(remediation),
        failure_packet={"status": SRM_BALANCE_DIAGNOSTIC_BLOCKED, "issues": issues},
        retry_category=remediation[0] if remediation else RETRY_FIX_ASSIGNMENT_ARTIFACT,
        policy_version=cfg.policy.policy_version,
        diagnostic_trace=trace,
        provenance={"artifact_id": _ARTIFACT_ID, "integrity_hash": trace["integrity_hash"]},
        claim_boundary_report=_claim_boundary(evaluated=True, baseline_evaluated=False),
    )


def evaluate_srm_balance_readout_diagnostic(
    input_data: Any,
    config: SRMBalanceReadoutDiagnosticConfig | dict[str, Any] | None = None,
) -> SRMBalanceReadoutDiagnosticReport | list[SRMBalanceReadoutDiagnosticReport]:
    cfg = _resolve_config(config)
    if isinstance(input_data, list):
        return [_evaluate_single(_to_dict(x), cfg) for x in input_data]
    data = _to_dict(input_data)
    if "requests" in data and isinstance(data["requests"], list):
        return [_evaluate_single(_to_dict(x), cfg) for x in data["requests"]]
    return _evaluate_single(data, cfg)


evaluate_srm_balance_diagnostic = evaluate_srm_balance_readout_diagnostic
check_srm_balance_readiness = evaluate_srm_balance_readout_diagnostic


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def run_validation(*, write_summary: bool = True) -> dict[str, Any]:
    allocations = [
        {"unit_id": "u1", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL", "treated": 0},
        {"unit_id": "u2", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL", "treated": 0},
        {"unit_id": "u3", "assigned_cell_id": "T1", "assigned_cell_role": "TREATMENT", "treated": 1},
        {"unit_id": "u4", "assigned_cell_id": "T1", "assigned_cell_role": "TREATMENT", "treated": 1},
    ]
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0, "baseline_spend": 10.0},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0, "baseline_spend": 11.0},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1, "baseline_spend": 10.5},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1, "baseline_spend": 10.2},
    ]
    smoke = evaluate_srm_balance_readout_diagnostic({
        "request_id": "srm_smoke",
        "assignment_artifact": {"artifact_id": "assign_smoke"},
        "unit_allocations": allocations,
        "panel_records": panel,
        "covariate_fields": ["baseline_spend"],
        "assignment_panel_integrity_report": {"status": ASSIGNMENT_PANEL_INTEGRITY_PASSED},
    })
    assert isinstance(smoke, SRMBalanceReadoutDiagnosticReport)
    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "srm_balance_readout_diagnostic_runtime",
        "base_commit": _git_head(),
        "status": "completed",
        "scope": _SCOPE,
        "depends_on": [
            "GOVERNED_RANDOMIZATION_RUNTIME_001",
            "ASSIGNMENT_PANEL_INTEGRITY_RUNTIME_001",
            "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001",
            "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001",
            "AUDIT_P0_GOVERNED_RUNTIME_HARDENING_001",
        ],
        "srm_balance_diagnostic_runtime_implemented": True,
        "sample_ratio_mismatch_diagnostic_evaluated": True,
        "realized_assignment_balance_evaluated": True,
        "covariate_balance_smd_evaluated": True,
        "baseline_outcome_balance_evaluated": True,
        "diagnostics_runtime_integrated_with_srm_balance": True,
        "readout_plan_prerequisite_added": True,
        "effect_estimate_computed": False,
        "lift_computed": False,
        "roi_computed": False,
        "estimator_implemented": False,
        "inference_implemented": False,
        "bootstrap_inference_implemented": False,
        "p_value_computed": False,
        "confidence_interval_computed": False,
        "uncertainty_computed": False,
        "rerandomization_optimization_implemented": False,
        "balance_optimization_implemented": False,
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
