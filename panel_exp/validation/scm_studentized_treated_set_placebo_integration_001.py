"""SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001 validation harness."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.scm_studentized_treated_set_placebo import (
    SCMStudentizedIntegrationDecision,
    SCMStudentizedStatisticContract,
    SCMStudentizedStatisticSource,
    SCMStudentizedTreatedSetPlaceboSpec,
    evaluate_scm_studentized_treated_set_placebo,
    summarize_scm_studentized_treated_set_placebo_result,
)

_ARTIFACT_ID = "SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001_summary.json"
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
    "SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001",
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


def _uniform_pseudo(n: int = 10) -> tuple[dict[str, float], dict[str, float]]:
    effects = {f"p{i}": 0.1 * i for i in range(1, n + 1)}
    scales = {k: 1.0 for k in effects}
    return effects, scales


def _contract(**kwargs: Any) -> SCMStudentizedStatisticContract:
    effects, scales = _uniform_pseudo()
    defaults: dict[str, Any] = dict(
        observed_effect=1.05,
        pseudo_effect_by_assignment=effects,
        observed_scale=1.0,
        pseudo_scale_by_assignment=scales,
        effect_direction="greater",
        scale_source="provided_standard_error",
        statistic_source=SCMStudentizedStatisticSource.PRECOMPUTED,
    )
    defaults.update(kwargs)
    return SCMStudentizedStatisticContract(**defaults)


def _spec(**kwargs: Any) -> SCMStudentizedTreatedSetPlaceboSpec:
    defaults: dict[str, Any] = dict(
        num_treated_units=3,
        assignment_role=DESIGN,
        assignment_family="complete_randomized_set",
        num_valid_pseudo_assignments=10,
        statistic_contract=_contract(),
        min_placebo_sets=10,
    )
    defaults.update(kwargs)
    return SCMStudentizedTreatedSetPlaceboSpec(**defaults)


def _scenario(
    scenario_id: str,
    integration_spec: SCMStudentizedTreatedSetPlaceboSpec,
    *,
    expect_decision: SCMStudentizedIntegrationDecision,
    expect_method_family: str | None = None,
    expect_scm_semantic_role: str | None = None,
    expect_scm_treated_set_decision: str | None = None,
    expect_rank: int | None = None,
    expect_tail: float | None = None,
) -> dict[str, Any]:
    result = evaluate_scm_studentized_treated_set_placebo(integration_spec)
    passed = result.decision == expect_decision
    summary = summarize_scm_studentized_treated_set_placebo_result(result)
    if expect_method_family is not None:
        actual = summary.get("method_randomization_summary", {}).get("method_family")
        if actual != expect_method_family:
            passed = False
    if expect_scm_semantic_role is not None:
        actual = summary.get("scm_semantics_summary", {}).get("semantic_role")
        if actual != expect_scm_semantic_role:
            passed = False
    if expect_scm_treated_set_decision is not None:
        actual = summary.get("scm_treated_set_summary", {}).get("decision")
        if actual != expect_scm_treated_set_decision:
            passed = False
    if expect_rank is not None and result.placebo_rank != expect_rank:
        passed = False
    if expect_tail is not None and result.empirical_tail_fraction is not None:
        if not math.isclose(result.empirical_tail_fraction, expect_tail, rel_tol=0, abs_tol=1e-9):
            passed = False
    return {
        "scenario_id": scenario_id,
        "passed": passed,
        "expected_decision": expect_decision.value,
        "result": summary,
    }


def build_scenarios() -> list[dict[str, Any]]:
    less_effects = {f"p{i}": -0.1 * i for i in range(1, 11)}
    less_scales = {k: 1.0 for k in less_effects}
    two_sided_effects = {f"p{i}": (-1) ** i * 0.1 * i for i in range(1, 11)}
    two_sided_scales = {k: 1.0 for k in two_sided_effects}

    rank_effects = {f"p{i}": float(i) * 0.5 for i in range(1, 6)}
    rank_scales = {k: 1.0 for k in rank_effects}

    return [
        _scenario(
            "scm_design_based_greater_candidate",
            _spec(),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE,
            expect_method_family="scm",
            expect_scm_semantic_role="design_based_randomization_candidate",
            expect_scm_treated_set_decision="scm_treated_set_randomization_candidate",
        ),
        _scenario(
            "scm_design_based_less_candidate",
            _spec(
                statistic_contract=_contract(
                    observed_effect=-1.05,
                    effect_direction="less",
                    pseudo_effect_by_assignment=less_effects,
                    pseudo_scale_by_assignment=less_scales,
                )
            ),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE,
        ),
        _scenario(
            "scm_design_based_two_sided_candidate",
            _spec(
                statistic_contract=_contract(
                    observed_effect=2.0,
                    effect_direction="two_sided",
                    pseudo_effect_by_assignment=two_sided_effects,
                    pseudo_scale_by_assignment=two_sided_scales,
                )
            ),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE,
        ),
        _scenario(
            "scm_falsification_diagnostic",
            _spec(assignment_role=FALSIFICATION, assignment_family="greedy_matched_market_falsification"),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_DIAGNOSTIC_ONLY,
            expect_scm_semantic_role="falsification_diagnostic",
        ),
        _scenario(
            "scm_blocked_assignment_role",
            _spec(assignment_role=BLOCKED_ROLE),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_single_treated_diagnostic_only",
            _spec(num_treated_units=1, assignment_role=FALSIFICATION),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_DIAGNOSTIC_ONLY,
            expect_scm_semantic_role="null_monitor_only",
        ),
        _scenario(
            "scm_missing_observed_effect",
            _spec(statistic_contract=_contract(observed_effect=None)),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_missing_observed_scale",
            _spec(statistic_contract=_contract(observed_scale=None)),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_missing_pseudo_effects",
            _spec(statistic_contract=_contract(pseudo_effect_by_assignment={})),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_missing_pseudo_scales",
            _spec(statistic_contract=_contract(pseudo_scale_by_assignment={})),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_effect_scale_assignment_mismatch",
            _spec(
                statistic_contract=_contract(
                    pseudo_effect_by_assignment={"p1": 0.1, "p2": 0.2},
                    pseudo_scale_by_assignment={"p1": 1.0, "p3": 1.0},
                ),
                min_placebo_sets=2,
                num_valid_pseudo_assignments=2,
            ),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_non_finite_observed_effect",
            _spec(statistic_contract=_contract(observed_effect=float("nan"))),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_non_finite_pseudo_effect",
            _spec(
                statistic_contract=_contract(
                    pseudo_effect_by_assignment={
                        f"p{i}": float("inf") if i == 1 else 0.1 * i for i in range(1, 11)
                    },
                )
            ),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_non_finite_observed_scale",
            _spec(statistic_contract=_contract(observed_scale=float("nan"))),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_non_positive_pseudo_scale",
            _spec(
                statistic_contract=_contract(
                    pseudo_scale_by_assignment={
                        f"p{i}": -1.0 if i == 3 else 1.0 for i in range(1, 11)
                    },
                )
            ),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_effect_definition_mismatch",
            _spec(statistic_contract=_contract(same_effect_definition_observed_and_pseudo=False)),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_scale_definition_mismatch",
            _spec(statistic_contract=_contract(same_scale_definition_observed_and_pseudo=False)),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_insufficient_placebo_sets",
            _spec(
                statistic_contract=_contract(
                    pseudo_effect_by_assignment={"p1": 0.1, "p2": 0.2},
                    pseudo_scale_by_assignment={"p1": 1.0, "p2": 1.0},
                ),
                num_valid_pseudo_assignments=2,
                min_placebo_sets=10,
            ),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_invalid_effect_direction",
            _spec(statistic_contract=_contract(effect_direction="invalid_direction")),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_final_p_value_blocked",
            _spec(requested_final_p_value=True),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_causal_ci_blocked",
            _spec(requested_causal_interval=True),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_trustreport_blocked",
            _spec(requested_trustreport_authorization=True),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_calibration_signal_blocked",
            _spec(requested_calibration_signal=True),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_mmm_ingestion_blocked",
            _spec(requested_mmm_ingestion=True),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_llm_decisioning_blocked",
            _spec(requested_llm_decisioning=True),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_production_decisioning_blocked",
            _spec(requested_production_decisioning=True),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_live_api_blocked",
            _spec(requested_live_api=True),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_scheduler_blocked",
            _spec(requested_scheduler=True),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_budget_optimization_blocked",
            _spec(requested_budget_optimization=True),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "studentized_primitive_bridge_rank_tail",
            _spec(
                statistic_contract=_contract(
                    observed_effect=2.0,
                    pseudo_effect_by_assignment=rank_effects,
                    pseudo_scale_by_assignment=rank_scales,
                ),
                min_placebo_sets=5,
                num_valid_pseudo_assignments=5,
            ),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE,
            expect_rank=2,
            expect_tail=0.4,
        ),
        _scenario(
            "scm_treated_set_bridge_candidate",
            _spec(),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE,
            expect_scm_treated_set_decision="scm_treated_set_randomization_candidate",
        ),
        _scenario(
            "scm_semantics_bridge_design_based",
            _spec(),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE,
            expect_scm_semantic_role="design_based_randomization_candidate",
        ),
        _scenario(
            "method_randomization_bridge_scm_candidate",
            _spec(),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE,
            expect_method_family="scm",
        ),
        _scenario(
            "governance_flags_all_false",
            _spec(),
            expect_decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE,
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
        if decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE.value:
            counts["candidate_scenarios"] += 1
        elif decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_DIAGNOSTIC_ONLY.value:
            counts["diagnostic_only_scenarios"] += 1
        elif decision == SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED.value:
            counts["blocked_scenarios"] += 1
    return counts


def run_scm_studentized_treated_set_placebo_integration_validation() -> dict[str, Any]:
    """Run deterministic SCM studentized treated-set placebo integration scenarios."""
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
        "verdict": "scm_studentized_treated_set_placebo_integration_defined_no_downstream_authorization",
        "governance_verdict": (
            "scm_studentized_treated_set_placebo_integration_defined_no_downstream_authorization"
        ),
        "roadmap_spine": ROADMAP_SPINE,
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        **decision_counts,
        "integration_layers": [
            "studentized_placebo_rank",
            "scm_treated_set_placebo",
            "scm_placebo_governed_semantics",
            "method_specific_randomization_validation",
        ],
        "studentized_scm_contract": {
            "formula": "(effect - null_value) / scale",
            "required_inputs": [
                "observed_effect",
                "pseudo_effect_by_assignment",
                "observed_scale",
                "pseudo_scale_by_assignment",
                "assignment_role",
                "effect_direction",
            ],
            "supported_directions": ["greater", "less", "two_sided"],
        },
        "allowed_outputs": [
            "observed_studentized_statistic",
            "pseudo_studentized_statistic_by_assignment",
            "studentized_placebo_rank",
            "studentized_empirical_tail_fraction",
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
        "next_artifact": "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_scm_studentized_treated_set_placebo_integration_validation()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    if args.overwrite:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"artifact_id": _ARTIFACT_ID, "verdict": summary["verdict"]}))


if __name__ == "__main__":
    main()
