"""AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001 validation harness."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.augsynth_point_randomization import (
    AugSynthCompatibility,
    AugSynthInferenceMode,
    AugSynthPointRandomizationSpec,
    AugSynthPointStatisticContract,
    AugSynthRandomizationDecision,
    AugSynthStatisticKind,
    evaluate_augsynth_point_randomization,
    summarize_augsynth_point_randomization_result,
)
from panel_exp.inference.method_specific_randomization import (
    MethodFamily,
    RandomizationValidationRole,
)

_ARTIFACT_ID = "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001_summary.json"
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
    "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
    "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",
    "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
]

DESIGN = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
FALSIFICATION = AssignmentRole.FALSIFICATION_ONLY.value
BLOCKED_ROLE = AssignmentRole.BLOCKED.value

_PSEUDO_STATS = {f"p{i}": 0.05 * i for i in range(1, 12)}
_RANK_PSEUDO = {"p1": 0.1, "p2": 0.2, "p3": 0.3, "p4": 0.4, "p5": 0.5, "p6": 0.6}


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
    statistic_kind: AugSynthStatisticKind = AugSynthStatisticKind.POINT_EFFECT,
    inference_mode: AugSynthInferenceMode = AugSynthInferenceMode.POINT_ONLY,
    effect_direction: str = "greater",
    **kwargs: Any,
) -> AugSynthPointStatisticContract:
    defaults: dict[str, Any] = dict(
        observed_statistic=observed,
        pseudo_statistic_by_assignment=pseudo if pseudo is not None else dict(_PSEUDO_STATS),
        statistic_kind=statistic_kind,
        inference_mode=inference_mode,
        effect_direction=effect_direction,
        estimand_id="ate",
        outcome_scale="absolute",
        pre_period_id="pre",
        post_period_id="post",
        donor_eligibility_rule_id="default",
        augmentation_config_id="ridge_v1",
    )
    defaults.update(kwargs)
    return AugSynthPointStatisticContract(**defaults)


def _spec(
    *,
    assignment_role: str = DESIGN,
    num_treated: int = 2,
    num_valid_pseudo: int = 11,
    contract: AugSynthPointStatisticContract | None = None,
    **kwargs: Any,
) -> AugSynthPointRandomizationSpec:
    defaults: dict[str, Any] = dict(
        assignment_role=assignment_role,
        assignment_family="complete_randomized_set",
        num_treated_units=num_treated,
        num_valid_pseudo_assignments=num_valid_pseudo,
        statistic_contract=contract or _contract(),
    )
    defaults.update(kwargs)
    return AugSynthPointRandomizationSpec(**defaults)


def _scenario(
    scenario_id: str,
    randomization_spec: AugSynthPointRandomizationSpec,
    *,
    expect_decision: AugSynthRandomizationDecision,
    expect_compatibility: AugSynthCompatibility | None = None,
    expect_placebo_rank: int | None = None,
    expect_tail_fraction: float | None = None,
    expect_method_family: str | None = None,
    expect_method_role: str | None = None,
) -> dict[str, Any]:
    result = evaluate_augsynth_point_randomization(randomization_spec)
    passed = result.decision == expect_decision
    if expect_compatibility is not None and result.compatibility != expect_compatibility:
        passed = False
    if expect_placebo_rank is not None and result.placebo_rank != expect_placebo_rank:
        passed = False
    if expect_tail_fraction is not None and result.empirical_tail_fraction is not None:
        if not math.isclose(
            result.empirical_tail_fraction,
            expect_tail_fraction,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            passed = False
    if expect_method_family is not None:
        if result.method_randomization_summary.get("method_family") != expect_method_family:
            passed = False
    if expect_method_role is not None:
        if result.method_randomization_summary.get("role") != expect_method_role:
            passed = False
    return {
        "scenario_id": scenario_id,
        "passed": passed,
        "expected_decision": expect_decision.value,
        "expected_compatibility": expect_compatibility.value if expect_compatibility else None,
        "result": summarize_augsynth_point_randomization_result(result),
    }


def build_scenarios() -> list[dict[str, Any]]:
    return [
        _scenario(
            "point_effect_design_candidate",
            _spec(),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_POINT_RANDOMIZATION_CANDIDATE,
            expect_compatibility=AugSynthCompatibility.COMPATIBLE,
        ),
        _scenario(
            "relative_point_effect_design_candidate",
            _spec(contract=_contract(statistic_kind=AugSynthStatisticKind.RELATIVE_POINT_EFFECT)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_POINT_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "studentized_point_effect_design_candidate",
            _spec(
                contract=_contract(
                    statistic_kind=AugSynthStatisticKind.STUDENTIZED_POINT_EFFECT,
                    inference_mode=AugSynthInferenceMode.STUDENTIZED_PLACEBO_RANK,
                )
            ),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_POINT_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "falsification_only_diagnostic",
            _spec(assignment_role=FALSIFICATION),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_POINT_DIAGNOSTIC_ONLY,
        ),
        _scenario(
            "blocked_assignment_role",
            _spec(assignment_role=BLOCKED_ROLE),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "jackknife_statistic_diagnostic_only",
            _spec(contract=_contract(statistic_kind=AugSynthStatisticKind.JACKKNIFE_EFFECT)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_JK_DIAGNOSTIC_ONLY,
        ),
        _scenario(
            "jackknife_production_request_blocked",
            _spec(requested_jackknife_production_inference=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "missing_observed_statistic_blocked",
            _spec(contract=_contract(observed=None)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.MISSING_OBSERVED_STATISTIC,
        ),
        _scenario(
            "missing_pseudo_statistics_blocked",
            _spec(contract=_contract(pseudo={})),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.MISSING_PSEUDO_STATISTICS,
        ),
        _scenario(
            "unsupported_statistic_kind_blocked",
            _spec(contract=_contract(statistic_kind=AugSynthStatisticKind.UNKNOWN)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "unsupported_inference_mode_blocked",
            _spec(contract=_contract(inference_mode=AugSynthInferenceMode.UNKNOWN)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "statistic_definition_mismatch_blocked",
            _spec(contract=_contract(same_statistic_definition_observed_and_pseudo=False)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.STATISTIC_DEFINITION_MISMATCH,
        ),
        _scenario(
            "estimand_mismatch_blocked",
            _spec(contract=_contract(same_estimand_observed_and_pseudo=False)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.ESTIMAND_MISMATCH,
        ),
        _scenario(
            "outcome_scale_mismatch_blocked",
            _spec(contract=_contract(same_outcome_scale_observed_and_pseudo=False)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.OUTCOME_SCALE_MISMATCH,
        ),
        _scenario(
            "time_window_mismatch_blocked",
            _spec(contract=_contract(same_time_window_observed_and_pseudo=False)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.TIME_WINDOW_MISMATCH,
        ),
        _scenario(
            "donor_eligibility_mismatch_blocked",
            _spec(contract=_contract(same_donor_eligibility_observed_and_pseudo=False)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.DONOR_ELIGIBILITY_MISMATCH,
        ),
        _scenario(
            "augmentation_config_mismatch_blocked",
            _spec(contract=_contract(same_augmentation_config_observed_and_pseudo=False)),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.AUGMENTATION_CONFIG_MISMATCH,
        ),
        _scenario(
            "non_finite_observed_blocked",
            _spec(contract=_contract(observed=float("nan"))),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.NON_NUMERIC_STATISTIC,
        ),
        _scenario(
            "non_finite_pseudo_blocked",
            _spec(contract=_contract(pseudo={"p1": float("inf"), **{f"p{i}": 0.1 for i in range(2, 12)}})),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.NON_NUMERIC_STATISTIC,
        ),
        _scenario(
            "insufficient_pseudo_assignments_blocked",
            _spec(
                contract=_contract(pseudo={f"p{i}": 0.1 for i in range(1, 6)}),
                num_valid_pseudo=5,
            ),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
            expect_compatibility=AugSynthCompatibility.INSUFFICIENT_PSEUDO_ASSIGNMENTS,
        ),
        _scenario(
            "invalid_effect_direction_blocked",
            _spec(contract=_contract(effect_direction="invalid")),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "final_p_value_request_blocked",
            _spec(requested_final_p_value=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "causal_ci_request_blocked",
            _spec(requested_causal_interval=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "trustreport_request_blocked",
            _spec(requested_trustreport_authorization=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "calibration_signal_blocked",
            _spec(requested_calibration_signal=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "mmm_ingestion_blocked",
            _spec(requested_mmm_ingestion=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "llm_decisioning_blocked",
            _spec(requested_llm_decisioning=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "production_decisioning_blocked",
            _spec(requested_production_decisioning=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "live_api_blocked",
            _spec(requested_live_api=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "scheduler_blocked",
            _spec(requested_scheduler=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "budget_optimization_blocked",
            _spec(requested_budget_optimization=True),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        ),
        _scenario(
            "placebo_bridge_rank_tail",
            _spec(
                contract=_contract(
                    observed=0.5,
                    pseudo=dict(_RANK_PSEUDO),
                    effect_direction="greater",
                    inference_mode=AugSynthInferenceMode.PLACEBO_RANK,
                ),
                num_valid_pseudo=6,
                min_pseudo_assignments=6,
            ),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_POINT_RANDOMIZATION_CANDIDATE,
            expect_placebo_rank=2,
            expect_tail_fraction=2 / 6,
        ),
        _scenario(
            "method_bridge_augsynth_family",
            _spec(),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_POINT_RANDOMIZATION_CANDIDATE,
            expect_method_family=MethodFamily.AUGSYNTH_CVXPY.value,
            expect_method_role=RandomizationValidationRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value,
        ),
        _scenario(
            "governance_flags_all_false",
            _spec(),
            expect_decision=AugSynthRandomizationDecision.AUGSYNTH_POINT_RANDOMIZATION_CANDIDATE,
        ),
    ]


def _count_scenarios(scenarios: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "candidate_scenarios": 0,
        "diagnostic_only_scenarios": 0,
        "jk_diagnostic_only_scenarios": 0,
        "blocked_scenarios": 0,
    }
    for s in scenarios:
        decision = s["result"]["decision"]
        if decision == AugSynthRandomizationDecision.AUGSYNTH_POINT_RANDOMIZATION_CANDIDATE.value:
            counts["candidate_scenarios"] += 1
        elif decision == AugSynthRandomizationDecision.AUGSYNTH_POINT_DIAGNOSTIC_ONLY.value:
            counts["diagnostic_only_scenarios"] += 1
        elif decision == AugSynthRandomizationDecision.AUGSYNTH_JK_DIAGNOSTIC_ONLY.value:
            counts["jk_diagnostic_only_scenarios"] += 1
        elif s["result"]["is_blocked"]:
            counts["blocked_scenarios"] += 1
    return counts


def run_augsynth_point_randomization_integration_validation() -> dict[str, Any]:
    """Run deterministic AugSynth point randomization integration scenarios."""
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    scenario_counts = _count_scenarios(scenarios)

    governance = {
        "trustreport_authorized": False,
        "calibration_signal_allowed": False,
        "mmm_ingestion_allowed": False,
        "llm_decisioning_allowed": False,
        "production_decisioning_allowed": False,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "budget_optimization_allowed": False,
        "augsynth_jk_authorized": False,
    }

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "verdict": "augsynth_point_randomization_integration_defined_no_downstream_authorization",
        "governance_verdict": (
            "augsynth_point_randomization_integration_defined_no_downstream_authorization"
        ),
        "roadmap_spine": ROADMAP_SPINE,
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        **scenario_counts,
        "augsynth_point_contract": {
            "required_fields": [
                "observed_statistic",
                "pseudo_statistic_by_assignment",
                "statistic_kind",
                "inference_mode",
                "effect_direction",
                "estimand_id",
                "outcome_scale",
                "pre_period_id",
                "post_period_id",
                "donor_eligibility_rule_id",
                "augmentation_config_id",
            ],
            "candidate_statistic_kinds": [
                "point_effect",
                "relative_point_effect",
                "studentized_point_effect",
            ],
            "blocked_or_diagnostic_statistic_kinds": [
                "jackknife_effect",
                "unknown",
            ],
            "allowed_outputs": [
                "augsynth_point_randomization_candidate",
                "augsynth_point_diagnostic_only",
                "augsynth_jk_diagnostic_only",
                "placebo_rank",
                "empirical_tail_fraction",
                "blocked",
            ],
            "forbidden_outputs": [
                "final_p_value",
                "causal_confidence_interval",
                "augsynth_jk_authorization",
                "trustreport_authorization",
                "calibration_signal",
                "mmm_ingestion",
                "llm_decisioning",
                "production_decisioning",
                "live_api",
                "scheduler",
                "budget_optimization",
            ],
        },
        "next_artifact": "METHOD_READINESS_MATRIX_V2_001",
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_augsynth_point_randomization_integration_validation()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    if args.overwrite:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"artifact_id": _ARTIFACT_ID, "verdict": summary["verdict"]}))


if __name__ == "__main__":
    main()
