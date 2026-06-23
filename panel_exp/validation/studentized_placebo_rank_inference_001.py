"""STUDENTIZED_PLACEBO_RANK_INFERENCE_001 validation harness."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.studentized_placebo_rank import (
    ScaleSource,
    StudentizedEffectDirection,
    StudentizedPlaceboRankSpec,
    StudentizedRankDecision,
    evaluate_studentized_placebo_rank,
    summarize_studentized_placebo_rank_result,
)

_ARTIFACT_ID = "STUDENTIZED_PLACEBO_RANK_INFERENCE_001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/STUDENTIZED_PLACEBO_RANK_INFERENCE_001_summary.json"
)

ROADMAP_SPINE = [
    "ROADMAP_REFOCUS_METHOD_VALIDATION_001",
    "INFERENCE_REPLACEMENT_SCOUT_001",
    "DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",
    "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",
    "SCM_PLACEBO_GOVERNED_SEMANTICS_001",
    "METHOD_ROADMAP_ALIGNMENT_AUDIT_001",
    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
    "SCM_TREATED_SET_PLACEBO_INTEGRATION_001",
    "STUDENTIZED_PLACEBO_RANK_INFERENCE_001",
]

DESIGN = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
FALSIFICATION = AssignmentRole.FALSIFICATION_ONLY.value
BLOCKED_ROLE = AssignmentRole.BLOCKED.value


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


def _uniform_pseudo(
    n: int = 10,
    *,
    effect_base: float = 0.1,
    scale: float = 1.0,
) -> tuple[dict[str, float], dict[str, float]]:
    effects = {f"p{i}": effect_base * i for i in range(1, n + 1)}
    scales = {k: scale for k in effects}
    return effects, scales


def _spec(
    *,
    observed_effect: float = 1.05,
    observed_scale: float = 1.0,
    direction: StudentizedEffectDirection = StudentizedEffectDirection.GREATER,
    assignment_role: str = DESIGN,
    pseudo_effects: dict[str, float] | None = None,
    pseudo_scales: dict[str, float] | None = None,
    min_placebo_sets: int = 10,
    **kwargs: Any,
) -> StudentizedPlaceboRankSpec:
    effects, scales = _uniform_pseudo()
    if pseudo_effects is not None:
        effects = pseudo_effects
    if pseudo_scales is not None:
        scales = pseudo_scales
    defaults: dict[str, Any] = dict(
        observed_effect=observed_effect,
        pseudo_effect_by_assignment=effects,
        observed_scale=observed_scale,
        pseudo_scale_by_assignment=scales,
        effect_direction=direction,
        scale_source=ScaleSource.PROVIDED_STANDARD_ERROR,
        assignment_role=assignment_role,
        min_placebo_sets=min_placebo_sets,
    )
    defaults.update(kwargs)
    return StudentizedPlaceboRankSpec(**defaults)


def _scenario(
    scenario_id: str,
    rank_spec: StudentizedPlaceboRankSpec,
    *,
    expect_decision: StudentizedRankDecision,
    expect_rank: int | None = None,
    expect_tail: float | None = None,
) -> dict[str, Any]:
    result = evaluate_studentized_placebo_rank(rank_spec)
    passed = result.decision == expect_decision
    if expect_rank is not None and result.placebo_rank != expect_rank:
        passed = False
    if expect_tail is not None and result.empirical_tail_fraction is not None:
        if not math.isclose(result.empirical_tail_fraction, expect_tail, rel_tol=0, abs_tol=1e-9):
            passed = False
    return {
        "scenario_id": scenario_id,
        "passed": passed,
        "expected_decision": expect_decision.value,
        "result": summarize_studentized_placebo_rank_result(result),
    }


def build_scenarios() -> list[dict[str, Any]]:
    greater_effects = {f"p{i}": 0.5 * i for i in range(1, 11)}
    greater_scales = {k: 1.0 for k in greater_effects}

    less_effects = {f"p{i}": -0.5 * i for i in range(1, 11)}
    less_scales = {k: 1.0 for k in less_effects}

    two_sided_effects = {f"p{i}": (-1) ** i * 0.5 * i for i in range(1, 11)}
    two_sided_scales = {k: 1.0 for k in two_sided_effects}

    rank_greater_effects = {f"p{i}": float(i) * 0.5 for i in range(1, 6)}
    rank_greater_scales = {k: 1.0 for k in rank_greater_effects}

    rank_less_effects = {"p1": -0.3, "p2": -0.8, "p3": -1.0, "p4": -1.2, "p5": -1.5}
    rank_less_scales = {k: 1.0 for k in rank_less_effects}

    rank_two_sided_effects = {"p1": -2.0, "p2": 0.5, "p3": 1.0, "p4": 2.0, "p5": 1.8}
    rank_two_sided_scales = {k: 1.0 for k in rank_two_sided_effects}

    return [
        _scenario(
            "design_based_greater_candidate",
            _spec(
                observed_effect=1.05,
                direction=StudentizedEffectDirection.GREATER,
                pseudo_effects=greater_effects,
                pseudo_scales=greater_scales,
            ),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE,
        ),
        _scenario(
            "design_based_less_candidate",
            _spec(
                observed_effect=-1.05,
                direction=StudentizedEffectDirection.LESS,
                pseudo_effects=less_effects,
                pseudo_scales=less_scales,
            ),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE,
        ),
        _scenario(
            "design_based_two_sided_candidate",
            _spec(
                observed_effect=2.0,
                direction=StudentizedEffectDirection.TWO_SIDED,
                pseudo_effects=two_sided_effects,
                pseudo_scales=two_sided_scales,
            ),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE,
        ),
        _scenario(
            "falsification_only_diagnostic",
            _spec(assignment_role=FALSIFICATION),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_DIAGNOSTIC_ONLY,
        ),
        _scenario(
            "blocked_assignment_role",
            _spec(assignment_role=BLOCKED_ROLE),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "missing_observed_scale",
            _spec(observed_scale=None),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "missing_pseudo_scale",
            _spec(pseudo_scales={}),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "pseudo_effect_scale_id_mismatch",
            _spec(
                pseudo_effects={"p1": 0.1, "p2": 0.2},
                pseudo_scales={"p1": 1.0, "p3": 1.0},
                min_placebo_sets=2,
            ),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "zero_observed_scale",
            _spec(observed_scale=0.0),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "negative_pseudo_scale",
            _spec(
                pseudo_effects={"p1": 0.1, "p2": 0.2, "p3": 0.3, "p4": 0.4, "p5": 0.5,
                                "p6": 0.6, "p7": 0.7, "p8": 0.8, "p9": 0.9, "p10": 1.0},
                pseudo_scales={f"p{i}": -1.0 if i == 3 else 1.0 for i in range(1, 11)},
            ),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "nan_observed_effect",
            _spec(observed_effect=float("nan")),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "infinite_pseudo_effect",
            _spec(
                pseudo_effects={f"p{i}": float("inf") if i == 1 else 0.1 * i for i in range(1, 11)},
                pseudo_scales={f"p{i}": 1.0 for i in range(1, 11)},
            ),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "nan_observed_scale",
            _spec(observed_scale=float("nan")),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "insufficient_placebo_sets",
            _spec(
                pseudo_effects={"p1": 0.1, "p2": 0.2},
                pseudo_scales={"p1": 1.0, "p2": 1.0},
                min_placebo_sets=10,
            ),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "final_p_value_request_blocked",
            _spec(requested_final_p_value=True),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "causal_ci_request_blocked",
            _spec(requested_causal_interval=True),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "trustreport_request_blocked",
            _spec(requested_trustreport_authorization=True),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "calibration_signal_request_blocked",
            _spec(requested_calibration_signal=True),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "mmm_ingestion_request_blocked",
            _spec(requested_mmm_ingestion=True),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "llm_decisioning_request_blocked",
            _spec(requested_llm_decisioning=True),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "production_decisioning_request_blocked",
            _spec(requested_production_decisioning=True),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "live_api_request_blocked",
            _spec(requested_live_api=True),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "scheduler_request_blocked",
            _spec(requested_scheduler=True),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "budget_optimization_request_blocked",
            _spec(requested_budget_optimization=True),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        ),
        _scenario(
            "governance_flags_all_false",
            _spec(),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE,
        ),
        _scenario(
            "greater_rank_tail_fraction",
            _spec(
                observed_effect=2.0,
                observed_scale=1.0,
                direction=StudentizedEffectDirection.GREATER,
                pseudo_effects=rank_greater_effects,
                pseudo_scales=rank_greater_scales,
                min_placebo_sets=5,
            ),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE,
            expect_rank=2,
            expect_tail=0.4,
        ),
        _scenario(
            "less_rank_tail_fraction",
            _spec(
                observed_effect=-1.0,
                observed_scale=1.0,
                direction=StudentizedEffectDirection.LESS,
                pseudo_effects=rank_less_effects,
                pseudo_scales=rank_less_scales,
                min_placebo_sets=5,
            ),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE,
            expect_rank=3,
            expect_tail=0.6,
        ),
        _scenario(
            "two_sided_rank_tail_fraction",
            _spec(
                observed_effect=2.0,
                observed_scale=1.0,
                direction=StudentizedEffectDirection.TWO_SIDED,
                pseudo_effects=rank_two_sided_effects,
                pseudo_scales=rank_two_sided_scales,
                min_placebo_sets=5,
            ),
            expect_decision=StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE,
            expect_rank=2,
            expect_tail=0.4,
        ),
    ]


def _count_decisions(scenarios: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "candidate_scenarios": 0,
        "diagnostic_only_scenarios": 0,
        "blocked_scenarios": 0,
    }
    for s in scenarios:
        decision = s["result"]["decision"]
        if decision == StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE.value:
            counts["candidate_scenarios"] += 1
        elif decision == StudentizedRankDecision.STUDENTIZED_RANK_DIAGNOSTIC_ONLY.value:
            counts["diagnostic_only_scenarios"] += 1
        elif decision == StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED.value:
            counts["blocked_scenarios"] += 1
    return counts


def run_studentized_placebo_rank_inference_validation() -> dict[str, Any]:
    """Run deterministic studentized placebo-rank inference validation scenarios."""
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    decision_counts = _count_decisions(scenarios)

    governance = {
        "trustreport_authorized": False,
        "calibration_signal_allowed": False,
        "mmm_ingestion_allowed": False,
        "llm_decisioning_allowed": False,
        "production_decisioning_allowed": False,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "budget_optimization_allowed": False,
    }

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "verdict": "studentized_placebo_rank_inference_defined_no_downstream_authorization",
        "governance_verdict": "studentized_placebo_rank_inference_defined_no_downstream_authorization",
        "roadmap_spine": ROADMAP_SPINE,
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        **decision_counts,
        "studentized_statistic_contract": {
            "formula": "(effect - null_value) / scale",
            "required_inputs": [
                "observed_effect",
                "pseudo_effect_by_assignment",
                "observed_scale",
                "pseudo_scale_by_assignment",
                "effect_direction",
                "assignment_role",
            ],
            "supported_directions": ["greater", "less", "two_sided"],
            "scale_validity_states": [
                "valid",
                "missing_observed_scale",
                "missing_pseudo_scale",
                "non_positive_scale",
                "non_finite_scale",
                "mismatched_scale_source",
                "insufficient_placebo_sets",
                "blocked",
            ],
        },
        "allowed_outputs": [
            "observed_studentized_statistic",
            "pseudo_studentized_statistic_by_assignment",
            "placebo_rank",
            "empirical_tail_fraction",
            "framework_level_candidate",
            "diagnostic_only",
            "blocked",
        ],
        "forbidden_outputs": [
            "final_p_value",
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
        "next_artifact": "SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001",
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_studentized_placebo_rank_inference_validation()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    if args.overwrite:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"artifact_id": _ARTIFACT_ID, "verdict": summary["verdict"]}))


if __name__ == "__main__":
    main()
