"""SCM_PLACEBO_GOVERNED_SEMANTICS_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.scm_placebo_semantics import (
    LOTO_AS_PLACEBO_NOTE,
    SCMPlaceboDecision,
    SCMPlaceboSemanticRole,
    SCMPlaceboSemanticsSpec,
    SCMPlaceboUseCase,
    classify_scm_placebo_semantics,
    summarize_scm_placebo_semantics_result,
)

_ARTIFACT_ID = "SCM_PLACEBO_GOVERNED_SEMANTICS_001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/SCM_PLACEBO_GOVERNED_SEMANTICS_001_summary.json"

ROADMAP_SPINE = [
    "ROADMAP_REFOCUS_METHOD_VALIDATION_001",
    "INFERENCE_REPLACEMENT_SCOUT_001",
    "DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",
    "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",
    "SCM_PLACEBO_GOVERNED_SEMANTICS_001",
]

BLOCKED_OVERCLAIMS = [
    "final_p_value",
    "causal_confidence_interval",
    "trustreport_authorization",
    "calibration_signal",
    "production_decisioning",
    "live_api",
    "scheduler",
    "budget_optimization",
]

SCM_PLACEBO_ROLES = [r.value for r in SCMPlaceboSemanticRole]


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


def _scenario(
    scenario_id: str,
    spec: SCMPlaceboSemanticsSpec,
    *,
    expect_decision: SCMPlaceboDecision,
    expect_role: SCMPlaceboSemanticRole | None = None,
) -> dict[str, Any]:
    result = classify_scm_placebo_semantics(spec)
    passed = result.decision == expect_decision
    if expect_role is not None and result.semantic_role != expect_role:
        passed = False
    return {
        "scenario_id": scenario_id,
        "passed": passed,
        "expected_decision": expect_decision.value,
        "expected_role": expect_role.value if expect_role else None,
        "result": summarize_scm_placebo_semantics_result(result),
    }


def build_scenarios() -> list[dict[str, Any]]:
    design_based = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
    falsification = AssignmentRole.FALSIFICATION_ONLY.value
    blocked_role = AssignmentRole.BLOCKED.value
    return [
        _scenario(
            "single_treated_null_monitor",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=1,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_SINGLE_TREATED_FALSIFICATION_ONLY,
            expect_role=SCMPlaceboSemanticRole.NULL_MONITOR_ONLY,
        ),
        _scenario(
            "single_treated_final_p_value_blocked",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=1,
                requested_as_final_p_value=True,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "single_treated_causal_ci_blocked",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=1,
                requested_as_causal_interval=True,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "multi_treated_design_based_candidate",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO,
                num_treated_units=3,
                assignment_role=design_based,
                has_valid_pseudo_assignments=True,
                num_valid_pseudo_assignments=10,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_TREATED_SET_FRAMEWORK_SUPPORTED,
            expect_role=SCMPlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "multi_treated_falsification_only",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO,
                num_treated_units=2,
                assignment_role=falsification,
                has_valid_pseudo_assignments=True,
                num_valid_pseudo_assignments=5,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_FALSIFICATION_ONLY,
            expect_role=SCMPlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC,
        ),
        _scenario(
            "multi_treated_blocked_assignment",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO,
                num_treated_units=2,
                assignment_role=blocked_role,
                has_valid_pseudo_assignments=True,
                num_valid_pseudo_assignments=5,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
            expect_role=SCMPlaceboSemanticRole.BLOCKED,
        ),
        _scenario(
            "multi_treated_no_pseudo_assignments",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO,
                num_treated_units=2,
                assignment_role=design_based,
                has_valid_pseudo_assignments=False,
                num_valid_pseudo_assignments=0,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "leave_one_treated_out_sensitivity_only",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.LEAVE_ONE_TREATED_OUT_SENSITIVITY,
                num_treated_units=3,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_FALSIFICATION_ONLY,
            expect_role=SCMPlaceboSemanticRole.SENSITIVITY_ONLY,
        ),
        _scenario(
            "leave_one_treated_out_as_placebo_rejected",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.LEAVE_ONE_TREATED_OUT_SENSITIVITY,
                num_treated_units=3,
                notes=(LOTO_AS_PLACEBO_NOTE,),
            ),
            expect_decision=SCMPlaceboDecision.SCM_LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO,
        ),
        _scenario(
            "unknown_use_case_blocked",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.UNKNOWN,
                num_treated_units=1,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "zero_treated_count_blocked",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=0,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "trustreport_authorization_blocked",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=1,
                requested_as_trustreport_authorization=True,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "calibration_signal_blocked",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=1,
                requested_as_calibration_signal=True,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "production_decisioning_blocked",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=1,
                requested_as_production_decisioning=True,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "live_api_blocked",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=1,
                requested_as_live_api=True,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "scheduler_blocked",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=1,
                requested_as_scheduler=True,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "budget_optimization_blocked",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO,
                num_treated_units=1,
                requested_as_budget_optimization=True,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
        _scenario(
            "design_aware_pseudo_assignment_design_based",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.DESIGN_AWARE_PSEUDO_ASSIGNMENT_PLACEBO,
                num_treated_units=2,
                assignment_role=design_based,
                has_valid_pseudo_assignments=True,
                num_valid_pseudo_assignments=8,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_DESIGN_BASED_CANDIDATE,
            expect_role=SCMPlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "multi_treated_insufficient_pseudo_assignments",
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO,
                num_treated_units=2,
                assignment_role=design_based,
                has_valid_pseudo_assignments=True,
                num_valid_pseudo_assignments=1,
            ),
            expect_decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        ),
    ]


def run_scm_placebo_governed_semantics_validation() -> dict[str, Any]:
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "verdict": "scm_placebo_governed_semantics_defined_no_authorization",
        "roadmap_spine": ROADMAP_SPINE,
        "scm_placebo_roles": SCM_PLACEBO_ROLES,
        "blocked_overclaims": BLOCKED_OVERCLAIMS,
        "scenario_results": scenarios,
        "scenario_count": len(scenarios),
        "passed_scenarios": len(scenarios) - len(failed),
        "failed_scenarios": failed,
        "trustreport_authorized": False,
        "calibration_signal_allowed": False,
        "production_decisioning_allowed": False,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "budget_optimization_allowed": False,
        "input_artifacts": [
            "docs/track_d/MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001_REPORT.md",
            "docs/track_d/archives/MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001_summary.json",
            "panel_exp/inference/treated_set_placebo.py",
            "panel_exp/design/assignment_generators.py",
        ],
        "next_artifact": "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
    }


def run_validation(*, strict: bool = False) -> dict[str, Any]:
    summary = run_scm_placebo_governed_semantics_validation()
    if strict and summary["failed_scenarios"]:
        raise SystemExit(f"strict mode: failed scenarios {summary['failed_scenarios']}")
    return summary


def write_summary(path: Path, summary: dict[str, Any], *, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"summary exists: {path} (pass --overwrite)")
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--summary-output", type=Path, default=_DEFAULT_SUMMARY)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    summary = run_validation(strict=args.strict)
    write_summary(args.summary_output, summary, overwrite=args.overwrite)
    print(json.dumps({"artifact_id": _ARTIFACT_ID, "verdict": summary["verdict"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
