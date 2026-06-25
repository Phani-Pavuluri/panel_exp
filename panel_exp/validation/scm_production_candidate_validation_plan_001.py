"""SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_production_candidate_validation_plan_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
    "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
)

MIN_VALIDATION_ROW_COUNT = 60

_AUTH_FLAGS = {
    "production_p_value_authorized": False,
    "causal_confidence_interval_authorized": False,
    "trustreport_authorized": False,
    "calibration_signal_allowed": False,
    "mmm_ingestion_allowed": False,
    "llm_decisioning_allowed": False,
    "production_decisioning_allowed": False,
    "live_api_authorized": False,
    "scheduler_authorized": False,
    "budget_optimization_allowed": False,
}

_BOUNDARY_FLAGS = {
    "scm_first_production_candidate_lane": True,
    "scm_point_estimate_not_sufficient_for_production_inference": True,
    "scm_production_inference_authorized": False,
    "scm_production_p_value_authorized": False,
    "scm_causal_ci_authorized": False,
    "donor_support_required": True,
    "convex_hull_required": True,
    "pre_period_fit_required": True,
    "pre_period_trend_stability_required": True,
    "assignment_design_validity_required": True,
    "assignment_generator_stress_required": True,
    "treated_set_placebo_requires_adapter": True,
    "studentized_statistic_requires_adapter": True,
    "null_calibration_required": True,
    "dgp_coverage_required": True,
    "failure_registry_consulted": True,
    "multi_treated_scm_requires_research_handling": True,
    "multicell_shared_control_blocked_without_dependence_handling": True,
    "release_gate_required_before_any_authorization": True,
    "downstream_work_paused": True,
}

_FORBID = (
    "production_p_value",
    "causal_ci",
    "trustreport",
    "production_inference",
    "calibration_signal",
    "mmm_ingestion",
    "llm_decisioning",
    "live_api",
    "scheduler",
    "budget_optimization",
)
_NEXT = "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001"


class ValidationArea(str, Enum):
    POINT_ESTIMATE_VALIDITY = "scm_point_estimate_validity"
    DONOR_POOL_ELIGIBILITY = "donor_pool_eligibility"
    DONOR_SUPPORT_CONVEX_HULL = "donor_support_convex_hull"
    PREPERIOD_FIT_QUALITY = "preperiod_fit_quality"
    PREPERIOD_TREND_STABILITY = "preperiod_trend_stability"
    OUTCOME_SCALE_COMPATIBILITY = "outcome_scale_compatibility"
    SPARSE_COUNT_RATE_OUTCOME = "sparse_count_rate_outcome_handling"
    ASSIGNMENT_DESIGN_VALIDITY = "assignment_design_validity"
    ASSIGNMENT_GENERATOR_STRESS = "assignment_generator_stress_compatibility"
    SINGLE_TREATED_SCM = "single_treated_scm"
    MULTI_TREATED_SCM = "multi_treated_scm"
    TREATED_SET_PLACEBO = "treated_set_placebo"
    UNIT_JACKKNIFE = "unit_jackknife"
    PLACEBO_RANK_INFERENCE = "placebo_rank_inference"
    STUDENTIZED_PLACEBO = "studentized_placebo_statistic"
    NULL_CALIBRATION = "null_calibration"
    DGP_SIMULATION_COVERAGE = "dgp_simulation_coverage"
    FAILURE_REGISTRY_BLOCKERS = "failure_registry_blockers"
    METHOD_DISAGREEMENT = "method_disagreement_checks"
    MULTICELL_SHARED_CONTROL = "multicell_shared_control_boundary"
    RELEASE_GATE = "release_gate_boundary"


class ValidationStatus(str, Enum):
    REQUIRED_BLOCKER = "required_blocker"
    REQUIRED_WARNING = "required_warning"
    CANDIDATE_AFTER_VALIDATION = "candidate_after_validation"
    CANDIDATE_AFTER_ADAPTER = "candidate_after_adapter"
    CANDIDATE_AFTER_NULL_CALIBRATION = "candidate_after_null_calibration"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    BLOCKED = "blocked"
    RESEARCH_REQUIRED = "research_required"


REQUIRED_VALIDATION_AREAS = frozenset(ValidationArea)
REQUIRED_STATUSES = frozenset(ValidationStatus)


@dataclass(frozen=True)
class ScmValidationRow:
    validation_id: str
    name: str
    validation_area: ValidationArea
    current_status: ValidationStatus
    required_inputs: tuple[str, ...]
    required_diagnostics: tuple[str, ...]
    required_dgp_coverage: tuple[str, ...]
    required_assignment_stress: tuple[str, ...]
    required_failure_registry_checks: tuple[str, ...]
    required_statistic_adapter: tuple[str, ...]
    required_null_calibration: tuple[str, ...]
    blocking_conditions: tuple[str, ...]
    passing_evidence_required: tuple[str, ...]
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    promotion_dependency: tuple[str, ...]
    recommended_next_artifact: str | None
    notes: str


def _row(
    validation_id: str,
    name: str,
    validation_area: ValidationArea,
    current_status: ValidationStatus,
    notes: str,
    *,
    required_inputs: tuple[str, ...],
    required_diagnostics: tuple[str, ...],
    required_dgp_coverage: tuple[str, ...],
    required_assignment_stress: tuple[str, ...],
    required_failure_registry_checks: tuple[str, ...],
    required_statistic_adapter: tuple[str, ...] = (),
    required_null_calibration: tuple[str, ...] = (),
    blocking_conditions: tuple[str, ...],
    passing_evidence_required: tuple[str, ...],
    allowed_current_use: tuple[str, ...],
    forbidden_current_use: tuple[str, ...],
    promotion_dependency: tuple[str, ...],
    recommended_next_artifact: str | None = None,
) -> ScmValidationRow:
    return ScmValidationRow(
        validation_id=validation_id,
        name=name,
        validation_area=validation_area,
        current_status=current_status,
        required_inputs=required_inputs,
        required_diagnostics=required_diagnostics,
        required_dgp_coverage=required_dgp_coverage,
        required_assignment_stress=required_assignment_stress,
        required_failure_registry_checks=required_failure_registry_checks,
        required_statistic_adapter=required_statistic_adapter,
        required_null_calibration=required_null_calibration,
        blocking_conditions=blocking_conditions,
        passing_evidence_required=passing_evidence_required,
        allowed_current_use=allowed_current_use,
        forbidden_current_use=forbidden_current_use,
        promotion_dependency=promotion_dependency,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


def _area_primary_status(area: ValidationArea) -> ValidationStatus:
    mapping: dict[ValidationArea, ValidationStatus] = {
        ValidationArea.POINT_ESTIMATE_VALIDITY: ValidationStatus.DIAGNOSTIC_ONLY,
        ValidationArea.DONOR_POOL_ELIGIBILITY: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.DONOR_SUPPORT_CONVEX_HULL: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.PREPERIOD_FIT_QUALITY: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.PREPERIOD_TREND_STABILITY: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.OUTCOME_SCALE_COMPATIBILITY: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.SPARSE_COUNT_RATE_OUTCOME: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.ASSIGNMENT_DESIGN_VALIDITY: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.ASSIGNMENT_GENERATOR_STRESS: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.SINGLE_TREATED_SCM: ValidationStatus.CANDIDATE_AFTER_VALIDATION,
        ValidationArea.MULTI_TREATED_SCM: ValidationStatus.RESEARCH_REQUIRED,
        ValidationArea.TREATED_SET_PLACEBO: ValidationStatus.CANDIDATE_AFTER_ADAPTER,
        ValidationArea.UNIT_JACKKNIFE: ValidationStatus.CANDIDATE_AFTER_ADAPTER,
        ValidationArea.PLACEBO_RANK_INFERENCE: ValidationStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
        ValidationArea.STUDENTIZED_PLACEBO: ValidationStatus.CANDIDATE_AFTER_ADAPTER,
        ValidationArea.NULL_CALIBRATION: ValidationStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
        ValidationArea.DGP_SIMULATION_COVERAGE: ValidationStatus.CANDIDATE_AFTER_SIMULATION,
        ValidationArea.FAILURE_REGISTRY_BLOCKERS: ValidationStatus.REQUIRED_BLOCKER,
        ValidationArea.METHOD_DISAGREEMENT: ValidationStatus.REQUIRED_WARNING,
        ValidationArea.MULTICELL_SHARED_CONTROL: ValidationStatus.BLOCKED,
        ValidationArea.RELEASE_GATE: ValidationStatus.BLOCKED,
    }
    return mapping[area]


def _area_variants(area: ValidationArea) -> tuple[tuple[str, ValidationStatus, str], ...]:
    """Return (name_suffix, status, note_suffix) variants per area."""
    primary = _area_primary_status(area)
    return (
        ("gate", primary, "Primary promotion gate for this validation area."),
        ("diagnostic", ValidationStatus.DIAGNOSTIC_ONLY, "Diagnostic-only path; not sufficient for production."),
        ("blocked_production", ValidationStatus.BLOCKED, "Production inference blocked until evidence passes."),
    )


def _area_defaults(area: ValidationArea) -> dict[str, Any]:
    diag = ("OPD-PF-001", "OPD-DS-005")
    dgp = ("DGP-SCM-001", "DGP-ES-007")
    stress = ("ST-AD-001", "ST-AD-009")
    fm = ("FM-ES-001", "FM-CP-003")
    promo = ("observed_diagnostics", "dgp_coverage", "failure_registry_consult")

    base: dict[str, Any] = {
        "required_inputs": ("panel_data", "treated_unit", "donor_pool"),
        "required_diagnostics": diag,
        "required_dgp_coverage": dgp,
        "required_assignment_stress": stress,
        "required_failure_registry_checks": fm,
        "required_statistic_adapter": (),
        "required_null_calibration": (),
        "blocking_conditions": ("production_inference_unauthorized",),
        "passing_evidence_required": promo,
        "allowed_current_use": ("diagnostic_readout",),
        "forbidden_current_use": _FORBID,
        "promotion_dependency": promo,
        "recommended_next_artifact": None,
    }

    if area == ValidationArea.DONOR_SUPPORT_CONVEX_HULL:
        base["required_diagnostics"] = ("OPD-DS-005", "OPD-DONOR-001")
        base["blocking_conditions"] = ("donor_support_failure", "convex_hull_violation")
    elif area == ValidationArea.PREPERIOD_FIT_QUALITY:
        base["required_diagnostics"] = ("OPD-PF-001", "OPD-PF-003")
        base["blocking_conditions"] = ("preperiod_fit_poor",)
    elif area == ValidationArea.PREPERIOD_TREND_STABILITY:
        base["required_diagnostics"] = ("OPD-PF-002", "OPD-PF-003")
        base["blocking_conditions"] = ("trend_instability",)
    elif area in (ValidationArea.TREATED_SET_PLACEBO, ValidationArea.STUDENTIZED_PLACEBO):
        base["required_statistic_adapter"] = ("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",)
        base["required_null_calibration"] = ("null_fpr_gate",)
        base["blocking_conditions"] = ("adapter_not_ready", "null_calibration_missing")
    elif area == ValidationArea.NULL_CALIBRATION:
        base["required_null_calibration"] = ("null_fpr_gate", "coverage_replay")
        base["blocking_conditions"] = ("null_calibration_incomplete",)
    elif area == ValidationArea.MULTI_TREATED_SCM:
        base["blocking_conditions"] = ("multi_treated_dependence_unhandled",)
        base["promotion_dependency"] = promo + ("multi_treated_research_handling",)
    elif area == ValidationArea.MULTICELL_SHARED_CONTROL:
        base["blocking_conditions"] = ("multicell_dependence_unhandled", "multiplicity_unhandled")
        base["required_failure_registry_checks"] = ("FM-CP-004", "FM-INF-009")
        base["recommended_next_artifact"] = _NEXT
    elif area == ValidationArea.RELEASE_GATE:
        base["blocking_conditions"] = ("release_gate_not_passed",)
        base["promotion_dependency"] = ("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",)
    elif area == ValidationArea.DGP_SIMULATION_COVERAGE:
        base["required_dgp_coverage"] = ("DGP-SCM-001", "DGP-ES-007", "DGP-CP-002")
    elif area == ValidationArea.ASSIGNMENT_GENERATOR_STRESS:
        base["required_assignment_stress"] = ("ST-AD-001", "ST-AD-009", "ST-AD-010")

    return base


def build_scm_production_candidate_validation_plan() -> tuple[ScmValidationRow, ...]:
    """Return metadata-only SCM production-candidate validation plan rows."""
    rows: list[ScmValidationRow] = []
    row_num = 1
    for area in ValidationArea:
        defaults = _area_defaults(area)
        for suffix, status, note_suffix in _area_variants(area):
            rows.append(
                _row(
                    f"SCM-VAL-{row_num:03d}",
                    f"scm_{area.value}_{suffix}",
                    area,
                    status,
                    f"{area.value}: {note_suffix}",
                    required_inputs=defaults["required_inputs"],
                    required_diagnostics=defaults["required_diagnostics"],
                    required_dgp_coverage=defaults["required_dgp_coverage"],
                    required_assignment_stress=defaults["required_assignment_stress"],
                    required_failure_registry_checks=defaults["required_failure_registry_checks"],
                    required_statistic_adapter=defaults.get("required_statistic_adapter", ()),
                    required_null_calibration=defaults.get("required_null_calibration", ()),
                    blocking_conditions=defaults["blocking_conditions"],
                    passing_evidence_required=defaults["passing_evidence_required"],
                    allowed_current_use=defaults["allowed_current_use"],
                    forbidden_current_use=defaults["forbidden_current_use"],
                    promotion_dependency=defaults["promotion_dependency"],
                    recommended_next_artifact=defaults["recommended_next_artifact"],
                )
            )
            row_num += 1
    return tuple(rows)


def filter_scm_production_candidate_validation_plan(
    rows: tuple[ScmValidationRow, ...],
    *,
    validation_area: ValidationArea | None = None,
    current_status: ValidationStatus | None = None,
    requires_adapter: bool | None = None,
    requires_null_calibration: bool | None = None,
) -> tuple[ScmValidationRow, ...]:
    """Filter SCM validation plan rows by optional criteria."""
    result: list[ScmValidationRow] = []
    for row in rows:
        if validation_area is not None and row.validation_area != validation_area:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if requires_adapter is not None:
            has_adapter = bool(row.required_statistic_adapter)
            if requires_adapter != has_adapter:
                continue
        if requires_null_calibration is not None:
            has_null = bool(row.required_null_calibration)
            if requires_null_calibration != has_null:
                continue
        result.append(row)
    return tuple(result)


def validate_scm_production_candidate_validation_plan(
    rows: tuple[ScmValidationRow, ...],
) -> dict[str, Any]:
    """Validate SCM validation plan registry thresholds and coverage."""
    issues: list[str] = []
    validation_ids = [r.validation_id for r in rows]

    if len(rows) < MIN_VALIDATION_ROW_COUNT:
        issues.append(f"validation_row_count {len(rows)} < {MIN_VALIDATION_ROW_COUNT}")
    if len(validation_ids) != len(set(validation_ids)):
        issues.append("duplicate validation_id values")

    status_counts = Counter(r.current_status for r in rows)
    area_counts = Counter(r.validation_area.value for r in rows)

    for area in REQUIRED_VALIDATION_AREAS:
        if not any(r.validation_area == area for r in rows):
            issues.append(f"missing validation_area: {area.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    donor_blocked = any(
        r.validation_area == ValidationArea.DONOR_SUPPORT_CONVEX_HULL
        and r.current_status == ValidationStatus.REQUIRED_BLOCKER
        for r in rows
    )
    if not donor_blocked:
        issues.append("donor support/convex hull required_blocker missing")

    multicell_blocked = any(
        r.validation_area == ValidationArea.MULTICELL_SHARED_CONTROL
        and r.current_status == ValidationStatus.BLOCKED
        for r in rows
    )
    if not multicell_blocked:
        issues.append("multicell blocked row missing")

    adapter_rows = [r for r in rows if r.required_statistic_adapter]
    if not adapter_rows:
        issues.append("no statistic adapter rows")

    unlinked = [r.validation_id for r in rows if not r.required_failure_registry_checks]
    if unlinked:
        issues.append(f"rows missing required_failure_registry_checks: {unlinked}")

    return {
        "valid": not issues,
        "validation_row_count": len(rows),
        "unique_validation_ids": len(validation_ids) == len(set(validation_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in ValidationStatus},
        "validation_area_counts": dict(area_counts),
        "all_required_validation_areas_covered": all(
            any(r.validation_area == a for r in rows) for a in REQUIRED_VALIDATION_AREAS
        ),
        "all_statuses_represented": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "issues": issues,
    }


def summarize_scm_production_candidate_validation_plan(
    rows: tuple[ScmValidationRow, ...],
) -> dict[str, Any]:
    """Serialize SCM validation plan summary for archives."""
    validation = validate_scm_production_candidate_validation_plan(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "validation_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "validation_area_counts": validation["validation_area_counts"],
        "all_required_validation_areas_covered": validation["all_required_validation_areas_covered"],
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_BOUNDARY_FLAGS,
        **_AUTH_FLAGS,
        "valid": validation["valid"],
    }


def _git_commit() -> str | None:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=_REPO,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _scenario(scenario_id: str, passed: bool, *, detail: str = "") -> dict[str, Any]:
    return {"scenario_id": scenario_id, "passed": passed, "detail": detail}


def build_scenarios() -> list[dict[str, Any]]:
    rows = build_scm_production_candidate_validation_plan()
    validation = validate_scm_production_candidate_validation_plan(rows)
    summary = summarize_scm_production_candidate_validation_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("validation_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("validation_row_count_at_least_60", len(rows) >= MIN_VALIDATION_ROW_COUNT))
    scenarios.append(_scenario("validation_ids_unique", validation["unique_validation_ids"]))

    for area in REQUIRED_VALIDATION_AREAS:
        present = any(r.validation_area == area for r in rows)
        scenarios.append(_scenario(f"validation_area_{area.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] is expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_multicell_dependence_plan",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_scm_production_candidate_validation_plan()
    validation = validate_scm_production_candidate_validation_plan(rows)
    summary = summarize_scm_production_candidate_validation_plan(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "validation_row_count": len(rows),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        **{k: summary[k] for k in summary if k not in ("failed_scenarios", "valid")},
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
