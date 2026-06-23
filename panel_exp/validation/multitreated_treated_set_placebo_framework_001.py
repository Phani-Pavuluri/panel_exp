"""MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.design.assignment_generators import (
    AssignmentDesignSpec,
    AssignmentFamily,
    AssignmentUnit,
    generate_pseudo_assignments,
)
from panel_exp.inference.treated_set_placebo import (
    PlaceboDecision,
    TestStatisticKind,
    TreatedSetPlaceboSpec,
    evaluate_treated_set_placebo,
    summarize_treated_set_placebo_result,
)

_ARTIFACT_ID = "MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001_summary.json"
)


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


def _complete_units(n: int = 10) -> list[AssignmentUnit]:
    return [AssignmentUnit(unit_id=f"u{i}") for i in range(n)]


def _stats_for_design(design: AssignmentDesignSpec, base: float = 0.1) -> dict[str, float]:
    assignments = generate_pseudo_assignments(design)
    return {a.assignment_id: base + i * 0.02 for i, a in enumerate(assignments)}


def _run_scenario(
    scenario_id: str,
    *,
    family: AssignmentFamily,
    units: list[AssignmentUnit],
    observed: tuple[str, ...],
    constraints: dict[str, Any] | None = None,
    seed: int = 0,
    min_placebo: int = 5,
    observed_stat: float = 0.55,
    metadata: dict[str, Any] | None = None,
    stats: dict[str, float] | None = None,
    expect_decision: PlaceboDecision | None = None,
) -> dict[str, Any]:
    design = AssignmentDesignSpec(
        family=family,
        units=units,
        observed_treated_unit_ids=observed,
        constraints=constraints,
        seed=seed,
        min_assignments=min_placebo,
        max_assignments=min_placebo + 5,
    )
    if stats is None:
        stats = _stats_for_design(design)
    spec = TreatedSetPlaceboSpec(
        design_spec=design,
        observed_statistic=observed_stat,
        pseudo_statistic_by_assignment=stats,
        minimum_valid_placebo_sets=min_placebo,
        metadata=metadata,
    )
    result = evaluate_treated_set_placebo(spec)
    passed = expect_decision is None or result.decision == expect_decision
    return {
        "scenario_id": scenario_id,
        "passed": passed,
        "expected_decision": expect_decision.value if expect_decision else None,
        "result": summarize_treated_set_placebo_result(result),
    }


def build_scenarios() -> list[dict[str, Any]]:
    pair_units = [
        AssignmentUnit(unit_id="p1a", pair_id="p1"),
        AssignmentUnit(unit_id="p1b", pair_id="p1"),
        AssignmentUnit(unit_id="p2a", pair_id="p2"),
        AssignmentUnit(unit_id="p2b", pair_id="p2"),
        AssignmentUnit(unit_id="p3a", pair_id="p3"),
        AssignmentUnit(unit_id="p3b", pair_id="p3"),
    ]
    block_units = [
        AssignmentUnit(unit_id="b1a", block_id="b1"),
        AssignmentUnit(unit_id="b1b", block_id="b1"),
        AssignmentUnit(unit_id="b1c", block_id="b1"),
        AssignmentUnit(unit_id="b2a", block_id="b2"),
        AssignmentUnit(unit_id="b2b", block_id="b2"),
        AssignmentUnit(unit_id="b2c", block_id="b2"),
    ]
    strata_units = [
        AssignmentUnit(unit_id="s1a", stratum_id="s1"),
        AssignmentUnit(unit_id="s1b", stratum_id="s1"),
        AssignmentUnit(unit_id="s2a", stratum_id="s2"),
        AssignmentUnit(unit_id="s2b", stratum_id="s2"),
        AssignmentUnit(unit_id="s2c", stratum_id="s2"),
    ]
    rerand_units = [
        AssignmentUnit(unit_id="u0", covariates={"x": 1.0}),
        AssignmentUnit(unit_id="u1", covariates={"x": 1.0}),
        AssignmentUnit(unit_id="u2", covariates={"x": 9.0}),
        AssignmentUnit(unit_id="u3", covariates={"x": 9.0}),
        AssignmentUnit(unit_id="u4", covariates={"x": 3.0}),
        AssignmentUnit(unit_id="u5", covariates={"x": 3.0}),
    ]
    complete = _complete_units()
    return [
        _run_scenario(
            "complete_randomized_positive",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=complete,
            observed=("u0", "u1"),
            seed=11,
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED,
        ),
        _run_scenario(
            "stratified_positive",
            family=AssignmentFamily.STRATIFIED_RANDOMIZED,
            units=strata_units,
            observed=("s1a", "s2a"),
            seed=7,
            min_placebo=4,
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED,
        ),
        _run_scenario(
            "matched_pair_positive",
            family=AssignmentFamily.MATCHED_PAIR_RANDOMIZED,
            units=pair_units,
            observed=("p1a", "p2b", "p3a"),
            seed=3,
            min_placebo=4,
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED,
        ),
        _run_scenario(
            "matched_block_positive",
            family=AssignmentFamily.MATCHED_BLOCK_RANDOMIZED,
            units=block_units,
            observed=("b1a", "b1b", "b2a"),
            seed=5,
            min_placebo=2,
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED,
        ),
        _run_scenario(
            "rerandomized_with_acceptance_rule",
            family=AssignmentFamily.RERANDOMIZED_DESIGN_CANDIDATE,
            units=rerand_units,
            observed=("u0", "u4"),
            constraints={"balance_key": "x", "max_imbalance": 3.5},
            seed=4,
            min_placebo=2,
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED,
        ),
        _run_scenario(
            "greedy_falsification_only",
            family=AssignmentFamily.GREEDY_MATCHED_MARKET_FALSIFICATION,
            units=complete[:7],
            observed=("u0", "u1"),
            seed=1,
            min_placebo=3,
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_FALSIFICATION_ONLY,
        ),
        _run_scenario(
            "kernel_thinning_falsification_only",
            family=AssignmentFamily.KERNEL_THINNING_FALSIFICATION,
            units=complete[:7],
            observed=("u0",),
            seed=1,
            min_placebo=3,
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_FALSIFICATION_ONLY,
        ),
        _run_scenario(
            "fixed_deterministic_falsification_only",
            family=AssignmentFamily.FIXED_DETERMINISTIC_FALSIFICATION,
            units=complete[:6],
            observed=("u2",),
            seed=1,
            min_placebo=2,
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_FALSIFICATION_ONLY,
        ),
        _run_scenario(
            "rerandomized_without_acceptance_rule",
            family=AssignmentFamily.RERANDOMIZED_DESIGN_CANDIDATE,
            units=complete[:8],
            observed=("u0", "u1"),
            seed=2,
            min_placebo=3,
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_FALSIFICATION_ONLY,
        ),
        _run_scenario(
            "unknown_assignment_blocked",
            family=AssignmentFamily.UNKNOWN_ASSIGNMENT_BLOCKED,
            units=complete[:5],
            observed=("u0",),
            min_placebo=2,
            stats={},
            expect_decision=PlaceboDecision.UNKNOWN_ASSIGNMENT_DESIGN_BLOCKED,
        ),
        _run_scenario(
            "too_few_valid_assignments",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=[AssignmentUnit(unit_id=f"u{i}") for i in range(5)],
            observed=("u0", "u1", "u2", "u3"),
            seed=1,
            min_placebo=20,
            stats={},
            expect_decision=PlaceboDecision.TOO_FEW_VALID_PSEUDO_ASSIGNMENTS,
        ),
        _run_scenario(
            "leave_one_treated_out_blocked",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=complete,
            observed=("u0", "u1"),
            metadata={"leave_one_treated_out_requested": True},
            stats={},
            expect_decision=PlaceboDecision.LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO,
        ),
        _run_scenario(
            "missing_pseudo_statistics_blocked",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=complete,
            observed=("u0", "u1"),
            stats={},
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
        ),
        _run_scenario(
            "assignment_id_mismatch_blocked",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=complete,
            observed=("u0", "u1"),
            stats={
                **_stats_for_design(
                    AssignmentDesignSpec(
                        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
                        units=complete,
                        observed_treated_unit_ids=("u0", "u1"),
                        seed=11,
                        min_assignments=5,
                        max_assignments=10,
                    )
                ),
                "bogus:assignment:id": 1.0,
            },
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
        ),
        _run_scenario(
            "multicell_global_claim_blocked",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=complete,
            observed=("u0", "u1"),
            metadata={"multicell_global_claim_requested": True},
            stats={},
            expect_decision=PlaceboDecision.MULTICELL_GLOBAL_CLAIM_BLOCKED,
        ),
        _run_scenario(
            "trustreport_authorization_blocked",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=complete,
            observed=("u0", "u1"),
            metadata={"trustreport_authorization_requested": True},
            stats={},
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
        ),
        _run_scenario(
            "calibration_signal_blocked",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=complete,
            observed=("u0", "u1"),
            metadata={"calibration_signal_requested": True},
            stats={},
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
        ),
        _run_scenario(
            "production_decisioning_blocked",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=complete,
            observed=("u0", "u1"),
            metadata={"production_decisioning_requested": True},
            stats={},
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
        ),
        _run_scenario(
            "budget_optimization_blocked",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=complete,
            observed=("u0", "u1"),
            metadata={"budget_optimization_requested": True},
            stats={},
            expect_decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
        ),
    ]


def build_summary() -> dict[str, Any]:
    scenarios = build_scenarios()
    positive_ids = {
        "complete_randomized_positive",
        "stratified_positive",
        "matched_pair_positive",
        "matched_block_positive",
        "rerandomized_with_acceptance_rule",
    }
    falsification_ids = {
        "greedy_falsification_only",
        "kernel_thinning_falsification_only",
        "fixed_deterministic_falsification_only",
        "rerandomized_without_acceptance_rule",
    }
    blocked_ids = {
        s["scenario_id"]
        for s in scenarios
        if s["scenario_id"] not in positive_ids | falsification_ids
    }

    decision_counts: dict[str, int] = {}
    semantic_role_counts: dict[str, int] = {}
    for s in scenarios:
        dec = s["result"]["decision"]
        role = s["result"]["semantic_role"]
        decision_counts[dec] = decision_counts.get(dec, 0) + 1
        semantic_role_counts[role] = semantic_role_counts.get(role, 0) + 1

    loto = next(s for s in scenarios if s["scenario_id"] == "leave_one_treated_out_blocked")
    multicell = next(s for s in scenarios if s["scenario_id"] == "multicell_global_claim_blocked")
    supported = next(s for s in scenarios if s["scenario_id"] == "complete_randomized_positive")

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": [
            "docs/track_d/DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_REPORT.md",
            "docs/track_d/archives/DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_summary.json",
            "docs/audits/INFERENCE_REPLACEMENT_SCOUT_001.md",
        ],
        "dependency_artifacts": [
            "DESIGN-AWARE-ASSIGNMENT-GENERATORS-001",
        ],
        "assignment_generator_dependency": {
            "module": "panel_exp.design.assignment_generators",
            "functions": ["generate_pseudo_assignments"],
        },
        "treated_set_placebo_contract": {
            "module": "panel_exp.inference.treated_set_placebo",
            "functions": [
                "evaluate_treated_set_placebo",
                "classify_placebo_semantics",
                "compute_placebo_rank",
                "reject_leave_one_treated_out_as_placebo",
                "summarize_treated_set_placebo_result",
            ],
        },
        "statistic_contract": {
            "kinds": [k.value for k in TestStatisticKind],
            "effect_directions": ["greater", "less", "two_sided"],
            "tail_fraction_label": "framework_only_not_production_p_value",
        },
        "scenario_results": scenarios,
        "positive_scenarios": sorted(positive_ids),
        "falsification_only_scenarios": sorted(falsification_ids),
        "blocked_scenarios": sorted(blocked_ids),
        "decision_counts": decision_counts,
        "semantic_role_counts": semantic_role_counts,
        "tail_fraction_examples": {
            "complete_randomized_positive": {
                "observed_statistic": supported["result"]["observed_statistic"],
                "placebo_rank": supported["result"]["placebo_rank"],
                "empirical_tail_fraction": supported["result"]["empirical_tail_fraction"],
                "label": "not_production_p_value",
            },
        },
        "leave_one_treated_out_decision": loto["result"]["decision"],
        "multicell_global_claim_decision": multicell["result"]["decision"],
        "trustreport_authorized": False,
        "calibration_signal_allowed": False,
        "production_decisioning_allowed": False,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "budget_optimization_allowed": False,
        "governance_verdict": (
            "multitreated_treated_set_placebo_framework_defined_no_inference_authorization"
        ),
        "known_limitations": [
            "No estimator-specific SCM/TBRRidge/DID placebo integration yet.",
            "Empirical tail fraction is framework-only; not a production p-value.",
            "Leave-one-treated-out remains sensitivity analysis only.",
            "Multicell global/winner/pooled claims blocked.",
        ],
        "next_artifact": "SCM_PLACEBO_GOVERNED_SEMANTICS_001",
    }


def run_validation(*, strict: bool = False) -> dict[str, Any]:
    summary = build_summary()
    failed = [s["scenario_id"] for s in summary["scenario_results"] if not s["passed"]]
    if strict and failed:
        raise SystemExit(f"strict mode: failed scenarios {failed}")
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
    print(json.dumps({"artifact_id": _ARTIFACT_ID, "governance_verdict": summary["governance_verdict"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
