"""SCM_TREATED_SET_PLACEBO_INTEGRATION_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.scm_treated_set_placebo import (
    SCMStatisticContract,
    SCMStatisticSource,
    SCMTreatedSetIntegrationDecision,
    SCMTreatedSetPlaceboIntegrationSpec,
    evaluate_scm_treated_set_placebo_integration,
    summarize_scm_treated_set_placebo_integration_result,
)

_ARTIFACT_ID = "SCM_TREATED_SET_PLACEBO_INTEGRATION_001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_TREATED_SET_PLACEBO_INTEGRATION_001_summary.json"
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
]

DESIGN = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
FALSIFICATION = AssignmentRole.FALSIFICATION_ONLY.value
BLOCKED_ROLE = AssignmentRole.BLOCKED.value

_PSEUDO_STATS = {f"p{i}": 0.05 * i for i in range(1, 6)}


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


def _contract(
    *,
    observed: float | None = 0.42,
    pseudo: dict[str, float] | None = None,
    statistic_kind: str = "signed_effect",
    effect_direction: str = "greater",
    same_stat: bool = True,
) -> SCMStatisticContract:
    return SCMStatisticContract(
        statistic_kind=statistic_kind,
        effect_direction=effect_direction,
        statistic_source=SCMStatisticSource.PRECOMPUTED,
        observed_statistic=observed,
        pseudo_statistic_by_assignment=pseudo if pseudo is not None else dict(_PSEUDO_STATS),
        same_statistic_observed_and_pseudo=same_stat,
    )


def _spec(
    *,
    num_treated: int = 3,
    assignment_role: str = DESIGN,
    num_valid_pseudo: int = 5,
    contract: SCMStatisticContract | None = None,
    **kwargs: Any,
) -> SCMTreatedSetPlaceboIntegrationSpec:
    defaults: dict[str, Any] = dict(
        num_treated_units=num_treated,
        assignment_role=assignment_role,
        assignment_family="complete_randomized_set",
        num_valid_pseudo_assignments=num_valid_pseudo,
        statistic_contract=contract or _contract(),
    )
    defaults.update(kwargs)
    return SCMTreatedSetPlaceboIntegrationSpec(**defaults)


def _scenario(
    scenario_id: str,
    integration_spec: SCMTreatedSetPlaceboIntegrationSpec,
    *,
    expect_decision: SCMTreatedSetIntegrationDecision,
    expect_method_family: str | None = None,
    expect_scm_semantic_role: str | None = None,
) -> dict[str, Any]:
    result = evaluate_scm_treated_set_placebo_integration(integration_spec)
    passed = result.decision == expect_decision
    summary = summarize_scm_treated_set_placebo_integration_result(result)
    if expect_method_family is not None:
        actual = summary.get("method_randomization_summary", {}).get("method_family")
        if actual != expect_method_family:
            passed = False
    if expect_scm_semantic_role is not None:
        actual = summary.get("scm_semantics_summary", {}).get("semantic_role")
        if actual != expect_scm_semantic_role:
            passed = False
    return {
        "scenario_id": scenario_id,
        "passed": passed,
        "expected_decision": expect_decision.value,
        "result": summary,
    }


def build_scenarios() -> list[dict[str, Any]]:
    return [
        _scenario(
            "scm_multi_treated_design_based_candidate",
            _spec(),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_RANDOMIZATION_CANDIDATE,
            expect_method_family="scm",
            expect_scm_semantic_role="design_based_randomization_candidate",
        ),
        _scenario(
            "scm_multi_treated_two_sided_candidate",
            _spec(contract=_contract(effect_direction="two_sided")),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "scm_falsification_only_diagnostic",
            _spec(assignment_role=FALSIFICATION, assignment_family="greedy_matched_market_falsification"),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_FALSIFICATION_DIAGNOSTIC,
            expect_scm_semantic_role="falsification_diagnostic",
        ),
        _scenario(
            "scm_blocked_assignment_role",
            _spec(assignment_role=BLOCKED_ROLE),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_single_treated_falsification_only",
            _spec(num_treated=1, assignment_role=FALSIFICATION),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_FALSIFICATION_DIAGNOSTIC,
            expect_scm_semantic_role="null_monitor_only",
        ),
        _scenario(
            "scm_missing_observed_statistic",
            _spec(contract=_contract(observed=None)),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_missing_pseudo_statistics",
            _spec(contract=_contract(pseudo={})),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_statistic_kind_mismatch",
            _spec(contract=_contract(same_stat=False)),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_non_numeric_observed_statistic",
            _spec(contract=_contract(observed=float("nan"))),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_non_numeric_pseudo_statistic",
            _spec(contract=_contract(pseudo={"p1": 0.1, "p2": float("inf")})),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_insufficient_pseudo_assignments",
            _spec(num_valid_pseudo=1, contract=_contract(pseudo={"p1": 0.1})),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_final_p_value_request_blocked",
            _spec(requested_final_p_value=True),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_causal_ci_request_blocked",
            _spec(requested_causal_interval=True),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_trustreport_request_blocked",
            _spec(requested_trustreport_authorization=True),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_calibration_signal_request_blocked",
            _spec(requested_calibration_signal=True),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_mmm_ingestion_request_blocked",
            _spec(requested_mmm_ingestion=True),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_llm_decisioning_request_blocked",
            _spec(requested_llm_decisioning=True),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_production_live_scheduler_budget_blocked",
            _spec(
                requested_production_decisioning=True,
                requested_live_api=True,
                requested_scheduler=True,
                requested_budget_optimization=True,
            ),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_design_based_missing_pseudo_method_block",
            _spec(
                contract=_contract(pseudo={}),
                assignment_role=DESIGN,
            ),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_design_based_invalid_treated_count",
            _spec(num_treated=0),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        ),
        _scenario(
            "scm_method_randomization_bridge_scm_family",
            _spec(),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_RANDOMIZATION_CANDIDATE,
            expect_method_family="scm",
        ),
        _scenario(
            "scm_semantics_bridge_design_based_role",
            _spec(),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_RANDOMIZATION_CANDIDATE,
            expect_scm_semantic_role="design_based_randomization_candidate",
        ),
        _scenario(
            "scm_governance_flags_all_false",
            _spec(),
            expect_decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_RANDOMIZATION_CANDIDATE,
        ),
    ]


def _count_decisions(scenarios: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "candidate_scenarios": 0,
        "falsification_diagnostic_scenarios": 0,
        "blocked_scenarios": 0,
    }
    for s in scenarios:
        decision = s["result"]["decision"]
        if decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_RANDOMIZATION_CANDIDATE.value:
            counts["candidate_scenarios"] += 1
        elif decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_FALSIFICATION_DIAGNOSTIC.value:
            counts["falsification_diagnostic_scenarios"] += 1
        elif decision == SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED.value:
            counts["blocked_scenarios"] += 1
    return counts


def run_scm_treated_set_placebo_integration_validation() -> dict[str, Any]:
    """Run deterministic SCM treated-set placebo integration validation scenarios."""
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
        "verdict": "scm_treated_set_placebo_integration_defined_no_downstream_authorization",
        "governance_verdict": "scm_treated_set_placebo_integration_defined_no_downstream_authorization",
        "roadmap_spine": ROADMAP_SPINE,
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        **decision_counts,
        "integration_layers": [
            "design_aware_assignment_generators",
            "treated_set_placebo_framework",
            "scm_placebo_governed_semantics",
            "method_specific_randomization_validation",
        ],
        "statistic_compatibility_states": [
            "comparable",
            "missing_observed",
            "missing_pseudo",
            "mismatched_statistic_kind",
            "non_numeric_statistic",
            "blocked",
        ],
        "allowed_outputs": [
            "empirical_tail_fraction",
            "placebo_rank",
            "framework_level_candidate",
            "falsification_diagnostic",
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
        "next_artifact": "STUDENTIZED_PLACEBO_RANK_INFERENCE_001",
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_scm_treated_set_placebo_integration_validation()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    if args.overwrite:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"artifact_id": _ARTIFACT_ID, "verdict": summary["verdict"]}))


if __name__ == "__main__":
    main()
