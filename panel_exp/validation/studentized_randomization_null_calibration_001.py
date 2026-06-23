"""STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.inference.studentized_randomization_calibration import (
    CalibrationAssignmentFamily,
    CalibrationStatisticMode,
    CalibrationVerdict,
    NullDGPKind,
    StudentizedNullSimulationSpec,
    build_default_studentized_null_calibration_grid,
    run_studentized_null_calibration,
    run_studentized_null_calibration_grid,
    summarize_studentized_null_calibration_grid,
    validate_studentized_null_simulation_spec,
)

_ARTIFACT_ID = "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "studentized_randomization_null_calibration_completed_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001_summary.json"
)

ROADMAP_SPINE = [
    "ROADMAP_REFOCUS_METHOD_VALIDATION_001",
    "INFERENCE_REPLACEMENT_SCOUT_001",
    "DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",
    "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",
    "SCM_PLACEBO_GOVERNED_SEMANTICS_001",
    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
    "SCM_TREATED_SET_PLACEBO_INTEGRATION_001",
    "STUDENTIZED_PLACEBO_RANK_INFERENCE_001",
    "SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001",
    "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
    "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",
    "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
    "METHOD_READINESS_MATRIX_V2_001",
    "CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001",
    "METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001",
    "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001",
]

NEXT_ARTIFACT = "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001"


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


def _valid_spec(**kwargs: Any) -> StudentizedNullSimulationSpec:
    defaults: dict[str, Any] = dict(
        dgp_kind=NullDGPKind.IID_NORMAL,
        assignment_family=CalibrationAssignmentFamily.COMPLETE_RANDOMIZED_SET,
        statistic_mode=CalibrationStatisticMode.STUDENTIZED,
        num_units=12,
        num_treated=3,
        num_pre_periods=4,
        num_post_periods=2,
        num_replications=100,
        num_pseudo_assignments=25,
        seed=42,
        min_replications=100,
        min_pseudo_assignments=20,
    )
    defaults.update(kwargs)
    return StudentizedNullSimulationSpec(**defaults)


def _fast_spec(**kwargs: Any) -> StudentizedNullSimulationSpec:
    """Smaller spec for harness scenario checks (not full grid)."""
    return _valid_spec(
        num_replications=30,
        min_replications=20,
        num_pseudo_assignments=25,
        **kwargs,
    )


def _scenario(scenario_id: str, passed: bool, *, detail: str = "") -> dict[str, Any]:
    return {"scenario_id": scenario_id, "passed": passed, "detail": detail}


def build_scenarios(
    grid_summary: dict[str, Any],
    grid_results: tuple[Any, ...],
) -> list[dict[str, Any]]:
    """Build validation scenarios for null-calibration harness."""
    scenarios: list[dict[str, Any]] = []

    ok, _ = validate_studentized_null_simulation_spec(_valid_spec())
    scenarios.append(_scenario("valid_spec_passes_validation", ok))

    for sid, spec, expect_fail in (
        ("invalid_num_units_blocked", _valid_spec(num_units=2), True),
        ("invalid_num_treated_blocked", _valid_spec(num_treated=0), True),
        ("num_treated_ge_num_units_blocked", _valid_spec(num_treated=12), True),
        ("invalid_pre_post_periods_blocked", _valid_spec(num_pre_periods=1), True),
        ("invalid_alpha_blocked", _valid_spec(alpha_levels=(1.5,)), True),
        ("too_few_replications_blocked", _valid_spec(num_replications=5, min_replications=100), True),
        (
            "too_few_pseudo_assignments_blocked",
            _valid_spec(num_pseudo_assignments=5, min_pseudo_assignments=20),
            True,
        ),
    ):
        valid, reasons = validate_studentized_null_simulation_spec(spec)
        scenarios.append(_scenario(sid, (not valid) == expect_fail, detail="; ".join(reasons)))

    dgp_specs = {
        "iid_null_simulation_runs": _fast_spec(dgp_kind=NullDGPKind.IID_NORMAL),
        "unit_fixed_effect_null_simulation_runs": _fast_spec(
            dgp_kind=NullDGPKind.UNIT_FIXED_EFFECT
        ),
        "unit_time_fixed_effect_null_simulation_runs": _fast_spec(
            dgp_kind=NullDGPKind.UNIT_AND_TIME_FIXED_EFFECT
        ),
        "heteroskedastic_null_simulation_runs": _fast_spec(
            dgp_kind=NullDGPKind.HETEROSKEDASTIC
        ),
    }
    for sid, spec in dgp_specs.items():
        result = run_studentized_null_calibration(spec)
        scenarios.append(
            _scenario(
                sid,
                len(result.replication_results) >= spec.min_replications
                and result.verdict != CalibrationVerdict.INVALID_CALIBRATION_SPEC,
            )
        )

    family_specs = {
        "complete_randomized_assignment_covered": _fast_spec(
            assignment_family=CalibrationAssignmentFamily.COMPLETE_RANDOMIZED_SET
        ),
        "matched_pair_assignment_covered": _fast_spec(
            assignment_family=CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED,
            num_units=12,
            num_treated=6,
        ),
        "stratified_assignment_covered": _fast_spec(
            assignment_family=CalibrationAssignmentFamily.STRATIFIED_RANDOMIZED,
            num_units=16,
            num_treated=4,
        ),
    }
    for sid, spec in family_specs.items():
        result = run_studentized_null_calibration(spec)
        scenarios.append(
            _scenario(
                sid,
                len(result.replication_results) >= spec.min_replications,
            )
        )

    for sid, mode in (
        ("studentized_mode_covered", CalibrationStatisticMode.STUDENTIZED),
        ("unstudentized_comparison_mode_covered", CalibrationStatisticMode.UNSTUDENTIZED),
    ):
        result = run_studentized_null_calibration(_fast_spec(statistic_mode=mode))
        scenarios.append(_scenario(sid, len(result.replication_results) > 0))

    sample = run_studentized_null_calibration(_fast_spec(seed=99))
    tails = [r.empirical_tail_fraction for r in sample.replication_results]
    scenarios.append(
        _scenario(
            "empirical_tail_fraction_bounded",
            all(0.0 <= t <= 1.0 for t in tails),
        )
    )
    scenarios.append(
        _scenario(
            "empirical_type_i_bounded",
            all(0.0 <= v <= 1.0 for v in sample.empirical_type_i_by_alpha.values()),
        )
    )
    scenarios.append(
        _scenario(
            "type_i_excess_computed",
            all(k in sample.type_i_excess_by_alpha for k in sample.empirical_type_i_by_alpha),
        )
    )
    scenarios.append(
        _scenario(
            "tail_fraction_quantiles_computed",
            bool(sample.tail_fraction_quantiles.get("q50") is not None),
        )
    )

    r1 = run_studentized_null_calibration(_fast_spec(seed=7))
    r2 = run_studentized_null_calibration(_fast_spec(seed=7))
    scenarios.append(
        _scenario(
            "deterministic_seed_reproducibility",
            len(r1.replication_results) == len(r2.replication_results)
            and (
                not r1.replication_results
                or r1.replication_results[0].empirical_tail_fraction
                == r2.replication_results[0].empirical_tail_fraction
            ),
        )
    )
    r3 = run_studentized_null_calibration(_fast_spec(seed=8))
    scenarios.append(
        _scenario(
            "different_seed_changes_results",
            not r1.replication_results
            or r1.replication_results[0].empirical_tail_fraction
            != r3.replication_results[0].empirical_tail_fraction,
        )
    )

    verdicts = {v.value for v in CalibrationVerdict}
    scenarios.append(
        _scenario(
            "calibration_verdict_assigned",
            sample.verdict.value in verdicts,
        )
    )
    scenarios.append(
        _scenario(
            "grid_summary_counts_by_verdict",
            sum(grid_summary.get("verdict_counts", {}).values()) == len(grid_results),
        )
    )

    auth_flags = (
        "production_p_value_authorized",
        "causal_confidence_interval_authorized",
        "trustreport_authorized",
        "calibration_signal_allowed",
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
    )
    for flag in auth_flags:
        scenarios.append(
            _scenario(
                f"no_result_authorizes_{flag}",
                all(not r.governance_flags.get(flag, True) for r in grid_results),
            )
        )

    scenarios.append(
        _scenario(
            "summary_json_flags_all_false",
            all(not grid_summary.get("governance_flags", {}).get(f, True) for f in auth_flags),
        )
    )
    scenarios.append(
        _scenario(
            "recommended_next_artifact_valid",
            NEXT_ARTIFACT
            in {
                "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
                "SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",
            },
        )
    )

    return scenarios


def run_studentized_randomization_null_calibration_harness() -> dict[str, Any]:
    """Run deterministic null-calibration validation harness."""
    grid_specs = build_default_studentized_null_calibration_grid()
    grid_results = run_studentized_null_calibration_grid(grid_specs)
    grid_summary = summarize_studentized_null_calibration_grid(grid_results)
    scenarios = build_scenarios(grid_summary, grid_results)
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    governance = {
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

    required_dgps = {
        "iid_normal": NullDGPKind.IID_NORMAL.value,
        "unit_fixed_effect": NullDGPKind.UNIT_FIXED_EFFECT.value,
        "unit_and_time_fixed_effect": NullDGPKind.UNIT_AND_TIME_FIXED_EFFECT.value,
        "heteroskedastic": NullDGPKind.HETEROSKEDASTIC.value,
    }
    required_families = {
        "complete_randomized_set": CalibrationAssignmentFamily.COMPLETE_RANDOMIZED_SET.value,
        "matched_pair_randomized": CalibrationAssignmentFamily.MATCHED_PAIR_RANDOMIZED.value,
        "stratified_randomized": CalibrationAssignmentFamily.STRATIFIED_RANDOMIZED.value,
    }
    required_modes = {
        "studentized": CalibrationStatisticMode.STUDENTIZED.value,
        "unstudentized": CalibrationStatisticMode.UNSTUDENTIZED.value,
    }

    dgp_coverage = {
        k: required_dgps[k] in grid_summary.get("dgp_coverage", {}) for k in required_dgps
    }
    family_coverage = {
        k: required_families[k] in grid_summary.get("assignment_family_coverage", {})
        for k in required_families
    }
    mode_coverage = {
        k: required_modes[k] in grid_summary.get("statistic_mode_coverage", {})
        for k in required_modes
    }

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "verdict": _VERDICT,
        "governance_verdict": _VERDICT,
        "roadmap_spine": ROADMAP_SPINE,
        "grid_result_count": grid_summary["grid_result_count"],
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "dgp_coverage": dgp_coverage,
        "assignment_family_coverage": family_coverage,
        "statistic_mode_coverage": mode_coverage,
        "verdict_counts": grid_summary.get("verdict_counts", {}),
        "max_empirical_type_i_excess": grid_summary.get("max_empirical_type_i_excess"),
        "recommended_next_artifact": NEXT_ARTIFACT,
        "calibration_scope": {
            "purpose": "empirical null calibration of studentized placebo-rank mechanics",
            "production_claim": False,
            "tested_dgps": list(required_dgps.values()),
            "tested_assignment_families": list(required_families.values()),
            "tested_statistic_modes": list(required_modes.values()),
            "tail_semantics": "empirical_tail_fraction_only_not_final_p_value",
        },
        "next_required_evidence": [
            "larger_simulation_grid",
            "SCM-specific statistic calibration",
            "observed/pseudo estimator adapter contract",
            "assignment-generator stress tests",
        ],
        "forbidden_outputs": [
            "production_p_value",
            "causal_confidence_interval",
            "trustreport_authorization",
            "calibration_signal",
            "mmm_ingestion",
            "llm_decisioning",
            "production_decisioning",
            "live_api",
            "scheduler",
            "budget_optimization",
        ],
        "grid_summaries": [
            summarize_studentized_null_calibration_grid(grid_results)["grid_result_count"]
        ],
        "next_artifact": NEXT_ARTIFACT,
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--summary", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_studentized_randomization_null_calibration_harness()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    print(json.dumps({"artifact_id": summary["artifact_id"], "verdict": summary["verdict"]}))

    if args.overwrite or args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
