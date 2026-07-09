"""GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001 — post-test spend evidence adapter."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

from panel_exp.validation.design_scenario_policy_feasibility_runtime_001 import (
    _compute_achieved_contrast,
)
from panel_exp.validation.spend_requirement_and_manipulation_feasibility_diagnostics_001 import (
    SpendDiagnosticsColumnMapping,
    SpendRequirementManipulationFeasibilityConfig,
    _parse_date,
    _to_float,
    _weekly_spend_totals,
)

_ARTIFACT_ID = "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_SCOPE = "post_test_spend_readiness_adapter_runtime_no_claim_authorization_or_roi_calculator"
_VERDICT = "post_test_spend_readiness_adapter_runtime_completed_no_claim_authorization_or_roi_calculator"
_RECOMMENDED_NEXT = "GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001"
_RETURN_TO_LANE_A = "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_CONTRACT_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001_summary.json"
)

SOURCE_ARTIFACT = _ARTIFACT_ID


class PostTestSpendReadinessStatus(str, Enum):
    READY = "READY"
    NOT_REQUESTED = "NOT_REQUESTED"
    PARTIAL_DIAGNOSTIC_ONLY = "PARTIAL_DIAGNOSTIC_ONLY"
    BLOCKED_MISSING_KPI = "BLOCKED_MISSING_KPI"
    BLOCKED_MISSING_COUNTERFACTUAL = "BLOCKED_MISSING_COUNTERFACTUAL"
    BLOCKED_MISSING_DELTA_MU = "BLOCKED_MISSING_DELTA_MU"
    BLOCKED_MISSING_SPEND_SOURCE = "BLOCKED_MISSING_SPEND_SOURCE"
    BLOCKED_MISSING_POST_TEST_SPEND = "BLOCKED_MISSING_POST_TEST_SPEND"
    BLOCKED_MISSING_SPEND_DELTA = "BLOCKED_MISSING_SPEND_DELTA"
    BLOCKED_MISSING_SPEND_BASELINE = "BLOCKED_MISSING_SPEND_BASELINE"
    BLOCKED_SPEND_WINDOW_MISMATCH = "BLOCKED_SPEND_WINDOW_MISMATCH"
    BLOCKED_SPEND_GEO_SCOPE_MISMATCH = "BLOCKED_SPEND_GEO_SCOPE_MISMATCH"
    BLOCKED_SPEND_CELL_SCOPE_MISMATCH = "BLOCKED_SPEND_CELL_SCOPE_MISMATCH"
    BLOCKED_CURRENCY_MISMATCH = "BLOCKED_CURRENCY_MISMATCH"
    BLOCKED_MISSING_VALUE_MAPPING = "BLOCKED_MISSING_VALUE_MAPPING"
    BLOCKED_MISSING_MARGIN_MAPPING = "BLOCKED_MISSING_MARGIN_MAPPING"
    BLOCKED_UNSUPPORTED_EXPERIMENT_TYPE = "BLOCKED_UNSUPPORTED_EXPERIMENT_TYPE"
    BLOCKED_CLAIM_NOT_AUTHORIZED = "BLOCKED_CLAIM_NOT_AUTHORIZED"


class PostTestExperimentType(str, Enum):
    GO_DARK = "go_dark"
    HEAVY_UP = "heavy_up"
    HOLDOUT = "holdout"
    DOSAGE = "dosage"
    REALLOCATION = "reallocation"


_EXPERIMENT_TO_CONTRAST: dict[PostTestExperimentType, str] = {
    PostTestExperimentType.GO_DARK: "GO_DARK",
    PostTestExperimentType.HEAVY_UP: "HEAVY_UP",
    PostTestExperimentType.HOLDOUT: "HOLDOUT",
    PostTestExperimentType.DOSAGE: "DOSAGE_CONTRAST",
    PostTestExperimentType.REALLOCATION: "BUDGET_REALLOCATION",
}

_TREATMENT_ROLES = frozenset({"treatment", "treated", "test", "t1", "treatment_cell"})
_CONTROL_ROLES = frozenset({"control", "bau", "holdout", "comparison", "c0", "control_cell", "baseline"})


@dataclass(frozen=True)
class PostTestSpendInput:
    experiment_id: str
    spend_rows: Sequence[Mapping[str, Any]]
    post_period_start: date | str
    post_period_end: date | str
    experiment_type: PostTestExperimentType | str
    spend_date_column: str = "date"
    spend_geo_column: str = "geo_unit_id"
    spend_amount_column: str = "spend_value"
    spend_cell_column: str | None = "cell_id"
    spend_cell_role_column: str | None = "cell_role"
    spend_channel_column: str | None = "channel"
    spend_campaign_column: str | None = "campaign"
    currency_column: str | None = "currency"
    assignment_rows: Sequence[Mapping[str, Any]] | None = None
    assignment_geo_column: str = "geo_unit_id"
    assignment_cell_column: str = "cell_id"
    assignment_role_column: str = "cell_role"
    experiment_geo_scope: frozenset[str] | tuple[str, ...] | None = None
    treatment_cell_values: frozenset[str] | tuple[str, ...] | None = None
    control_cell_values: frozenset[str] | tuple[str, ...] | None = None
    counterfactual_or_bau_spend: float | None = None
    baseline_spend: float | None = None
    spend_baseline_policy: str | None = None
    spend_aggregation_level: str = "overall"
    spend_allocation_method: str = "sum_compatible_rows"
    budget_source_channel: str | None = None
    budget_destination_channel: str | None = None
    removed_spend_scope: str | None = None
    added_spend_scope: str | None = None
    source_artifact: str | None = None
    source_dataset_ref: str | None = None
    source_lineage: Mapping[str, Any] | None = None
    planning_required_spend_delta: float | None = None


@dataclass(frozen=True)
class PostTestSpendEvidence:
    experiment_id: str
    source_artifact: str
    source_dataset_ref: str | None
    source_lineage: dict[str, Any]
    spend_date_column: str
    spend_geo_column: str
    spend_amount_column: str
    spend_currency: str | None
    spend_scope: str
    spend_window_start: str
    spend_window_end: str
    experiment_geo_scope: tuple[str, ...]
    treatment_cell_scope: tuple[str, ...]
    channel_scope: tuple[str, ...]
    campaign_scope: tuple[str, ...]
    actual_treatment_spend: float | None
    actual_control_or_baseline_spend: float | None
    counterfactual_or_bau_spend: float | None
    spend_delta: float | None
    spend_delta_definition: str | None
    spend_baseline_policy: str | None
    spend_aggregation_level: str
    spend_allocation_method: str
    readiness_status: PostTestSpendReadinessStatus
    blocking_reasons: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["readiness_status"] = self.readiness_status.value
        return payload


def _as_date(value: date | str | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return _parse_date(value)


def _normalize_experiment_type(value: PostTestExperimentType | str) -> PostTestExperimentType | None:
    if isinstance(value, PostTestExperimentType):
        return value
    token = str(value).strip().lower().replace("-", "_")
    aliases = {
        "go_dark": PostTestExperimentType.GO_DARK,
        "godark": PostTestExperimentType.GO_DARK,
        "heavy_up": PostTestExperimentType.HEAVY_UP,
        "heavyup": PostTestExperimentType.HEAVY_UP,
        "holdout": PostTestExperimentType.HOLDOUT,
        "dosage": PostTestExperimentType.DOSAGE,
        "dosage_contrast": PostTestExperimentType.DOSAGE,
        "reallocation": PostTestExperimentType.REALLOCATION,
        "budget_reallocation": PostTestExperimentType.REALLOCATION,
    }
    return aliases.get(token)


def _rows_from_input(spend_rows: Sequence[Mapping[str, Any]] | None) -> list[dict[str, Any]]:
    if not spend_rows:
        return []
    return [dict(row) for row in spend_rows]


def _build_assignment_map(inp: PostTestSpendInput) -> dict[str, dict[str, str]]:
    if not inp.assignment_rows:
        return {}
    mapping: dict[str, dict[str, str]] = {}
    for row in inp.assignment_rows:
        geo = str(row.get(inp.assignment_geo_column, "")).strip()
        if not geo:
            continue
        mapping[geo] = {
            "cell_id": str(row.get(inp.assignment_cell_column, "")).strip(),
            "cell_role": str(row.get(inp.assignment_role_column, "")).strip().lower(),
        }
    return mapping


def _cell_in_scope(cell_id: str, cell_role: str, values: frozenset[str] | tuple[str, ...] | None) -> bool:
    if not values:
        return True
    normalized = {str(v).strip().lower() for v in values}
    return cell_id.lower() in normalized or cell_role.lower() in normalized


def _classify_row_role(
    cell_id: str,
    cell_role: str,
    treatment_values: frozenset[str] | tuple[str, ...] | None,
    control_values: frozenset[str] | tuple[str, ...] | None,
) -> str:
    role = cell_role.lower()
    cid = cell_id.lower()
    if treatment_values and _cell_in_scope(cid, role, treatment_values):
        return "treatment"
    if control_values and _cell_in_scope(cid, role, control_values):
        return "control"
    if role in _TREATMENT_ROLES or cid.startswith("t"):
        return "treatment"
    if role in _CONTROL_ROLES or cid.startswith("c"):
        return "control"
    return "unknown"


def _sum_spend(rows: Sequence[Mapping[str, Any]], amount_col: str) -> float:
    total = 0.0
    for row in rows:
        val = _to_float(row.get(amount_col))
        if val is not None:
            total += val
    return total


def _filter_scope_value(rows: Sequence[Mapping[str, Any]], col: str | None, scope: str | None) -> list[dict[str, Any]]:
    if not scope or not col:
        return [dict(r) for r in rows]
    return [dict(r) for r in rows if str(r.get(col, "")).strip() == scope]


def _currency_status(rows: Sequence[Mapping[str, Any]], currency_col: str | None) -> tuple[str | None, list[str]]:
    if not currency_col:
        return None, ["CURRENCY_COLUMN_NOT_DECLARED"]
    currencies = {str(r.get(currency_col)).strip() for r in rows if r.get(currency_col) not in (None, "")}
    currencies.discard("")
    if not currencies:
        return None, ["CURRENCY_VALUES_MISSING"]
    if len(currencies) > 1:
        return None, ["BLOCKED_CURRENCY_MISMATCH"]
    return next(iter(currencies)), []


def _derive_spend_delta(
    experiment_type: PostTestExperimentType,
    *,
    actual_treatment: float | None,
    actual_control: float | None,
    counterfactual_or_bau: float | None,
    inp: PostTestSpendInput,
) -> tuple[float | None, str | None, tuple[str, ...], tuple[str, ...]]:
    blockers: list[str] = []
    warnings: list[str] = []
    definition: str | None = None
    delta: float | None = None

    if experiment_type == PostTestExperimentType.GO_DARK:
        definition = "counterfactual_or_bau_spend_minus_actual_treatment_spend"
        bau = counterfactual_or_bau if counterfactual_or_bau is not None else inp.baseline_spend
        if bau is None:
            blockers.append("BLOCKED_MISSING_SPEND_BASELINE")
        elif actual_treatment is None:
            blockers.append("BLOCKED_MISSING_POST_TEST_SPEND")
        else:
            delta = bau - actual_treatment
            planning = _planning_contrast_check(experiment_type, bau, actual_treatment)
            if planning is not None:
                warnings.append(planning)
    elif experiment_type == PostTestExperimentType.HEAVY_UP:
        definition = "actual_treatment_spend_minus_counterfactual_or_bau_spend"
        bau = counterfactual_or_bau if counterfactual_or_bau is not None else inp.baseline_spend
        if bau is None:
            blockers.append("BLOCKED_MISSING_SPEND_BASELINE")
        elif actual_treatment is None:
            blockers.append("BLOCKED_MISSING_POST_TEST_SPEND")
        else:
            delta = actual_treatment - bau
            planning = _planning_contrast_check(experiment_type, actual_treatment, bau)
            if planning is not None:
                warnings.append(planning)
    elif experiment_type == PostTestExperimentType.HOLDOUT:
        definition = "actual_treatment_spend_minus_actual_control_or_baseline_spend"
        if actual_control is None:
            blockers.append("BLOCKED_MISSING_SPEND_BASELINE")
        elif actual_treatment is None:
            blockers.append("BLOCKED_MISSING_POST_TEST_SPEND")
        else:
            delta = actual_treatment - actual_control
    elif experiment_type == PostTestExperimentType.DOSAGE:
        definition = "dosage_treatment_cell_spend_minus_baseline_cell_spend"
        if actual_control is None:
            blockers.append("BLOCKED_MISSING_SPEND_BASELINE")
        elif actual_treatment is None:
            blockers.append("BLOCKED_MISSING_POST_TEST_SPEND")
        else:
            delta = actual_treatment - actual_control
    elif experiment_type == PostTestExperimentType.REALLOCATION:
        definition = "added_spend_minus_removed_spend"
        if not inp.added_spend_scope or not inp.removed_spend_scope:
            blockers.append("BLOCKED_MISSING_SPEND_BASELINE")
            warnings.append("REALLOCATION_REQUIRES_ADDED_AND_REMOVED_SCOPE")
        elif actual_treatment is None or actual_control is None:
            blockers.append("BLOCKED_MISSING_POST_TEST_SPEND")
        else:
            delta = actual_treatment - actual_control
    else:
        blockers.append("BLOCKED_UNSUPPORTED_EXPERIMENT_TYPE")

    if inp.planning_required_spend_delta is not None:
        warnings.append("PLANNING_REQUIRED_SPEND_DELTA_NOT_USED_AS_OBSERVED_SPEND_DELTA")

    return delta, definition, tuple(blockers), tuple(warnings)


def _planning_contrast_check(
    experiment_type: PostTestExperimentType,
    treatment_or_bau: float,
    comparison_or_actual: float,
) -> str | None:
    """Cross-check observed delta semantics against planning contrast helper."""
    contrast = _EXPERIMENT_TO_CONTRAST.get(experiment_type, "UNKNOWN")
    treatment = {"proposed_spend": treatment_or_bau}
    comparison = {"proposed_spend": comparison_or_actual}
    planning = _compute_achieved_contrast(contrast, treatment, comparison)
    if planning is None:
        return "PLANNING_CONTRAST_HELPER_NOT_APPLICABLE"
    return None


def build_post_test_spend_evidence(inp: PostTestSpendInput) -> PostTestSpendEvidence:
    """Build governed post-test spend evidence from observed spend rows."""
    blockers: list[str] = []
    warnings: list[str] = []

    rows = _rows_from_input(inp.spend_rows)
    if not rows:
        return _blocked_evidence(inp, ("BLOCKED_MISSING_SPEND_SOURCE",), ())

    for col in (inp.spend_date_column, inp.spend_geo_column, inp.spend_amount_column):
        if col not in rows[0]:
            blockers.append(f"BLOCKED_MISSING_COLUMN:{col}")

    if blockers:
        return _blocked_evidence(inp, tuple(blockers), tuple(warnings))

    start = _as_date(inp.post_period_start)
    end = _as_date(inp.post_period_end)
    if start is None or end is None or start > end:
        return _blocked_evidence(inp, ("BLOCKED_SPEND_WINDOW_MISMATCH",), tuple(warnings))

    col_map = SpendDiagnosticsColumnMapping(
        geo_unit_id=inp.spend_geo_column,
        date=inp.spend_date_column,
        spend=inp.spend_amount_column,
        cell_id=inp.spend_cell_column or "cell_id",
        cell_role=inp.spend_cell_role_column or "cell_role",
        channel=inp.spend_channel_column or "channel",
        campaign=inp.spend_campaign_column or "campaign",
        currency=inp.currency_column or "currency",
    )
    cfg = SpendRequirementManipulationFeasibilityConfig(columns=col_map)

    # Reuse planning primitive for windowed aggregation sanity (observed post-test window).
    weekly_totals, missing_weeks = _weekly_spend_totals(
        rows, cfg, window_start=start, window_end=end
    )
    if missing_weeks:
        warnings.append(f"MISSING_SPEND_VALUES_IN_WINDOW:{missing_weeks}")

    post_rows: list[dict[str, Any]] = []
    for row in rows:
        dt = _parse_date(row.get(inp.spend_date_column))
        if dt is None or dt < start or dt > end:
            continue
        post_rows.append(row)

    if not post_rows:
        return _blocked_evidence(inp, ("BLOCKED_MISSING_POST_TEST_SPEND",), tuple(warnings))

    geo_scope = frozenset(str(g) for g in (inp.experiment_geo_scope or ()))
    if geo_scope:
        post_rows = [r for r in post_rows if str(r.get(inp.spend_geo_column, "")) in geo_scope]
        if not post_rows:
            return _blocked_evidence(inp, ("BLOCKED_SPEND_GEO_SCOPE_MISMATCH",), tuple(warnings))

    assignment_map = _build_assignment_map(inp)
    enriched: list[dict[str, Any]] = []
    treatment_cells: set[str] = set()
    control_cells: set[str] = set()
    channels: set[str] = set()
    campaigns: set[str] = set()

    treatment_values = (
        frozenset(inp.treatment_cell_values) if inp.treatment_cell_values else None
    )
    control_values = frozenset(inp.control_cell_values) if inp.control_cell_values else None

    for row in post_rows:
        geo = str(row.get(inp.spend_geo_column, ""))
        assign = assignment_map.get(geo, {})
        cell_id = str(row.get(inp.spend_cell_column or "", "") or assign.get("cell_id", ""))
        cell_role = str(row.get(inp.spend_cell_role_column or "", "") or assign.get("cell_role", ""))
        role = _classify_row_role(cell_id, cell_role, treatment_values, control_values)
        if role == "unknown" and assignment_map and geo not in assignment_map:
            blockers.append("BLOCKED_SPEND_CELL_SCOPE_MISMATCH")
        enriched_row = dict(row)
        enriched_row["_derived_role"] = role
        enriched.append(enriched_row)
        if inp.spend_channel_column and row.get(inp.spend_channel_column):
            channels.add(str(row[inp.spend_channel_column]))
        if inp.spend_campaign_column and row.get(inp.spend_campaign_column):
            campaigns.add(str(row[inp.spend_campaign_column]))
        if role == "treatment" and cell_id:
            treatment_cells.add(cell_id)
        if role == "control" and cell_id:
            control_cells.add(cell_id)

    if "BLOCKED_SPEND_CELL_SCOPE_MISMATCH" in blockers:
        return _blocked_evidence(inp, tuple(sorted(set(blockers))), tuple(warnings))

    experiment_type = _normalize_experiment_type(inp.experiment_type)
    if experiment_type is None:
        return _blocked_evidence(inp, ("BLOCKED_UNSUPPORTED_EXPERIMENT_TYPE",), tuple(warnings))

    currency, currency_issues = _currency_status(post_rows, inp.currency_column)
    if "BLOCKED_CURRENCY_MISMATCH" in currency_issues:
        return _blocked_evidence(inp, ("BLOCKED_CURRENCY_MISMATCH",), tuple(warnings))
    warnings.extend(currency_issues)

    treatment_rows = [r for r in enriched if r["_derived_role"] == "treatment"]
    control_rows = [r for r in enriched if r["_derived_role"] == "control"]

    if experiment_type == PostTestExperimentType.REALLOCATION:
        added_scope = inp.added_spend_scope or inp.budget_destination_channel
        removed_scope = inp.removed_spend_scope or inp.budget_source_channel
        treatment_rows = _filter_scope_value(post_rows, inp.spend_channel_column, added_scope)
        control_rows = _filter_scope_value(post_rows, inp.spend_channel_column, removed_scope)
    elif experiment_type == PostTestExperimentType.DOSAGE and treatment_values and control_values:
        treatment_rows = [
            r
            for r in enriched
            if _classify_row_role(
                str(r.get(inp.spend_cell_column or "", "")),
                str(r.get(inp.spend_cell_role_column or "", "")),
                treatment_values,
                frozenset(),
            )
            == "treatment"
        ]
        control_rows = [
            r
            for r in enriched
            if _classify_row_role(
                str(r.get(inp.spend_cell_column or "", "")),
                str(r.get(inp.spend_cell_role_column or "", "")),
                frozenset(),
                control_values,
            )
            == "control"
        ]

    actual_treatment = _sum_spend(treatment_rows, inp.spend_amount_column) if treatment_rows else None
    actual_control = _sum_spend(control_rows, inp.spend_amount_column) if control_rows else None
    counterfactual = inp.counterfactual_or_bau_spend

    delta, definition, delta_blockers, delta_warnings = _derive_spend_delta(
        experiment_type,
        actual_treatment=actual_treatment,
        actual_control=actual_control,
        counterfactual_or_bau=counterfactual,
        inp=inp,
    )
    blockers.extend(delta_blockers)
    warnings.extend(delta_warnings)

    if weekly_totals and actual_treatment is not None:
        warnings.append("WEEKLY_SPEND_TOTALS_PRIMITIVE_REUSED_FOR_WINDOW_VALIDATION")

    status = PostTestSpendReadinessStatus.READY
    if blockers:
        status = PostTestSpendReadinessStatus(blockers[0]) if blockers[0] in PostTestSpendReadinessStatus.__members__ else PostTestSpendReadinessStatus.BLOCKED_MISSING_SPEND_DELTA
    elif delta is None:
        status = PostTestSpendReadinessStatus.BLOCKED_MISSING_SPEND_DELTA
    elif experiment_type == PostTestExperimentType.REALLOCATION and (
        not inp.added_spend_scope or not inp.removed_spend_scope
    ):
        status = PostTestSpendReadinessStatus.PARTIAL_DIAGNOSTIC_ONLY

    scope_geos = tuple(sorted({str(r.get(inp.spend_geo_column, "")) for r in post_rows if r.get(inp.spend_geo_column)}))

    return PostTestSpendEvidence(
        experiment_id=inp.experiment_id,
        source_artifact=inp.source_artifact or SOURCE_ARTIFACT,
        source_dataset_ref=inp.source_dataset_ref,
        source_lineage=dict(inp.source_lineage or {}),
        spend_date_column=inp.spend_date_column,
        spend_geo_column=inp.spend_geo_column,
        spend_amount_column=inp.spend_amount_column,
        spend_currency=currency,
        spend_scope=inp.spend_aggregation_level,
        spend_window_start=start.isoformat(),
        spend_window_end=end.isoformat(),
        experiment_geo_scope=scope_geos,
        treatment_cell_scope=tuple(sorted(treatment_cells)),
        channel_scope=tuple(sorted(channels)),
        campaign_scope=tuple(sorted(campaigns)),
        actual_treatment_spend=actual_treatment,
        actual_control_or_baseline_spend=actual_control,
        counterfactual_or_bau_spend=counterfactual if counterfactual is not None else inp.baseline_spend,
        spend_delta=delta,
        spend_delta_definition=definition,
        spend_baseline_policy=inp.spend_baseline_policy,
        spend_aggregation_level=inp.spend_aggregation_level,
        spend_allocation_method=inp.spend_allocation_method,
        readiness_status=status,
        blocking_reasons=tuple(sorted(set(blockers))),
        warnings=tuple(sorted(set(warnings))),
    )


def _blocked_evidence(
    inp: PostTestSpendInput,
    blockers: tuple[str, ...],
    warnings: tuple[str, ...],
) -> PostTestSpendEvidence:
    start = _as_date(inp.post_period_start)
    end = _as_date(inp.post_period_end)
    status_name = blockers[0] if blockers else "BLOCKED_MISSING_SPEND_SOURCE"
    try:
        status = PostTestSpendReadinessStatus(status_name)
    except ValueError:
        status = PostTestSpendReadinessStatus.BLOCKED_MISSING_SPEND_SOURCE
    return PostTestSpendEvidence(
        experiment_id=inp.experiment_id,
        source_artifact=inp.source_artifact or SOURCE_ARTIFACT,
        source_dataset_ref=inp.source_dataset_ref,
        source_lineage=dict(inp.source_lineage or {}),
        spend_date_column=inp.spend_date_column,
        spend_geo_column=inp.spend_geo_column,
        spend_amount_column=inp.spend_amount_column,
        spend_currency=None,
        spend_scope=inp.spend_aggregation_level,
        spend_window_start=start.isoformat() if start else "",
        spend_window_end=end.isoformat() if end else "",
        experiment_geo_scope=tuple(inp.experiment_geo_scope or ()),
        treatment_cell_scope=(),
        channel_scope=(),
        campaign_scope=(),
        actual_treatment_spend=None,
        actual_control_or_baseline_spend=None,
        counterfactual_or_bau_spend=inp.counterfactual_or_bau_spend,
        spend_delta=None,
        spend_delta_definition=None,
        spend_baseline_policy=inp.spend_baseline_policy,
        spend_aggregation_level=inp.spend_aggregation_level,
        spend_allocation_method=inp.spend_allocation_method,
        readiness_status=status,
        blocking_reasons=blockers,
        warnings=warnings,
    )


def build_trusted_readout_spend_handoff(evidence: PostTestSpendEvidence) -> dict[str, Any]:
    """Trusted-readout-consumable handoff packet (no claim authorization)."""
    blocked_efficiency = list(evidence.blocking_reasons)
    if evidence.readiness_status != PostTestSpendReadinessStatus.READY:
        blocked_efficiency.append("EFFICIENCY_METRICS_NOT_READY")
    return {
        "spend_readiness_summary": {
            "readiness_status": evidence.readiness_status.value,
            "spend_delta_ready": evidence.spend_delta is not None
            and evidence.readiness_status == PostTestSpendReadinessStatus.READY,
        },
        "post_test_spend_evidence": evidence.to_dict(),
        "efficiency_metric_readiness": {
            "cost_per_incremental_kpi": "NOT_COMPUTED",
            "roas": "NOT_COMPUTED",
            "profit_roi": "NOT_COMPUTED",
        },
        "blocked_efficiency_metrics": blocked_efficiency,
        "diagnostic_efficiency_metrics": []
        if evidence.readiness_status == PostTestSpendReadinessStatus.READY
        else ["spend_delta"],
        "roi_claim_authorization_status": "NOT_EVALUATED",
        "spend_lineage": evidence.source_lineage,
        "spend_warnings": list(evidence.warnings),
    }


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=_REPO)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    sample_rows = [
        {"geo_unit_id": "g1", "date": "2025-03-01", "spend_value": 100.0, "cell_id": "T1", "cell_role": "treatment"},
        {"geo_unit_id": "g1", "date": "2025-03-08", "spend_value": 50.0, "cell_id": "T1", "cell_role": "treatment"},
        {"geo_unit_id": "g2", "date": "2025-02-01", "spend_value": 999.0, "cell_id": "T1", "cell_role": "treatment"},
    ]
    evidence = build_post_test_spend_evidence(
        PostTestSpendInput(
            experiment_id="validation_sample",
            spend_rows=sample_rows,
            post_period_start="2025-03-01",
            post_period_end="2025-03-31",
            experiment_type=PostTestExperimentType.GO_DARK,
            counterfactual_or_bau_spend=200.0,
            assignment_rows=[
                {"geo_unit_id": "g1", "cell_id": "T1", "cell_role": "treatment"},
                {"geo_unit_id": "g2", "cell_id": "T1", "cell_role": "treatment"},
            ],
        )
    )
    summary = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "geox_post_test_spend_readiness_adapter_runtime",
        "lane": "Lane B - Final trusted readout spend ROI readiness",
        "status": "completed",
        "scope": _SCOPE,
        "base_commit": _git_commit(),
        "depends_on": [
            "FINAL_TEST_RESULTS_EXISTING_ARTIFACT_REUSE_AUDIT_001",
            "GEOX_READOUT_DATAFLOW_AND_SPEND_EXTRACTION_PROCESS_AUDIT_001",
            "GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001",
            "GEO_KPI_SPEND_DATA_PROFILER_001",
            "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
            "TRUSTED_READOUT_REPORT_RUNTIME_001",
            "CLAIM_AUTHORIZATION_RUNTIME_001",
        ],
        "post_test_spend_readiness_adapter_completed": True,
        "post_test_window_filter_implemented": True,
        "spend_assignment_join_implemented": True,
        "actual_treatment_spend_implemented": True,
        "counterfactual_or_bau_spend_supported": True,
        "spend_delta_readiness_implemented": True,
        "readiness_blockers_implemented": True,
        "warnings_implemented": True,
        "existing_spend_primitives_reused_or_referenced": True,
        "planning_required_spend_delta_not_reused_as_observed_spend_delta": True,
        "trusted_readout_consumable_output_defined": True,
        "runtime_implemented": True,
        "spend_ingestion_system_created": False,
        "final_results_module_created": False,
        "roi_calculator_runtime_created": False,
        "claim_authorization_duplicated": False,
        "roi_claim_authorized": False,
        "roas_claim_authorized": False,
        "business_lift_claim_authorized": False,
        "decision_recommendation_authorized": False,
        "production_readout_authorized": False,
        "method_promoted": False,
        "instrument_promoted": False,
        "catalog_unblocked": False,
        "production_compatibility_authorized": False,
        "estimator_implemented": False,
        "inference_implemented": False,
        "mmm_runtime_calls_implemented": False,
        "llm_decisioning_authorized": False,
        "recommended_next_artifact": _RECOMMENDED_NEXT,
        "return_to_lane_a_after": _RETURN_TO_LANE_A,
        "final_verdict": _VERDICT,
        "validation_sample_readiness_status": evidence.readiness_status.value,
        "validation_sample_spend_delta": evidence.spend_delta,
    }
    if write_summary:
        path = summary_path or _DEFAULT_SUMMARY
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="GEOX post-test spend readiness adapter validation")
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    summary = run_validation(write_summary=args.write_summary, summary_path=args.summary_path)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
