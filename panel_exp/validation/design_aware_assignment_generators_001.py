"""DESIGN-AWARE-ASSIGNMENT-GENERATORS-001 validation harness."""

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
    AssignmentRole,
    AssignmentUnit,
    ValidityStatus,
    generate_pseudo_assignments,
    summarize_assignment_generation,
    validate_pseudo_assignment,
)

_ARTIFACT_ID = "DESIGN-AWARE-ASSIGNMENT-GENERATORS-001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/DESIGN_AWARE_ASSIGNMENT_GENERATORS_001_summary.json"
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


def _scenario(
    scenario_id: str,
    *,
    family: AssignmentFamily,
    units: list[AssignmentUnit],
    observed: tuple[str, ...],
    constraints: dict[str, Any] | None = None,
    seed: int = 0,
    min_assignments: int = 2,
    max_assignments: int = 10,
    expect_non_empty: bool = True,
    expect_role: AssignmentRole | None = None,
) -> dict[str, Any]:
    spec = AssignmentDesignSpec(
        family=family,
        units=units,
        observed_treated_unit_ids=observed,
        constraints=constraints,
        seed=seed,
        min_assignments=min_assignments,
        max_assignments=max_assignments,
    )
    assignments = generate_pseudo_assignments(spec)
    summary = summarize_assignment_generation(spec, assignments)
    ok = True
    reasons: list[str] = []
    if expect_non_empty and not assignments:
        ok = False
        reasons.append("expected non-empty assignments")
    if not expect_non_empty and assignments:
        ok = False
        reasons.append("expected blocked/empty assignments")
    if expect_role is not None and assignments:
        if not all(a.role == expect_role for a in assignments):
            ok = False
            reasons.append(f"expected role {expect_role.value}")
    for a in assignments:
        validated = validate_pseudo_assignment(spec, a)
        if validated.validity_status == ValidityStatus.ASSIGNMENT_GENERATION_INVALID.value:
            ok = False
            reasons.append(f"invalid assignment {a.assignment_id}")
    return {
        "scenario_id": scenario_id,
        "family": family.value,
        "passed": ok,
        "reasons": reasons,
        "assignment_count": len(assignments),
        "summary": summary,
        "sample_assignment_ids": [a.assignment_id for a in assignments[:3]],
    }


def build_scenarios() -> list[dict[str, Any]]:
    complete_units = [
        AssignmentUnit(unit_id=f"u{i}") for i in range(10)
    ]
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
    return [
        _scenario(
            "complete_randomized_positive",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=complete_units,
            observed=("u0", "u1"),
            seed=11,
            min_assignments=5,
            expect_role=AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "complete_randomized_blocked_too_few",
            family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
            units=[AssignmentUnit(unit_id=f"u{i}") for i in range(4)],
            observed=("u0", "u1", "u2"),
            seed=1,
            min_assignments=10,
            expect_non_empty=False,
        ),
        _scenario(
            "matched_pair_positive",
            family=AssignmentFamily.MATCHED_PAIR_RANDOMIZED,
            units=pair_units,
            observed=("p1a", "p2b", "p3a"),
            seed=3,
            min_assignments=4,
            expect_role=AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "matched_pair_malformed_blocked",
            family=AssignmentFamily.MATCHED_PAIR_RANDOMIZED,
            units=[
                AssignmentUnit(unit_id="a1", pair_id="p1"),
                AssignmentUnit(unit_id="a2", pair_id="p1"),
                AssignmentUnit(unit_id="a3", pair_id="p1"),
            ],
            observed=("a1",),
            expect_non_empty=False,
        ),
        _scenario(
            "matched_block_positive",
            family=AssignmentFamily.MATCHED_BLOCK_RANDOMIZED,
            units=block_units,
            observed=("b1a", "b1b", "b2a"),
            seed=5,
            min_assignments=2,
            expect_role=AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "stratified_positive",
            family=AssignmentFamily.STRATIFIED_RANDOMIZED,
            units=strata_units,
            observed=("s1a", "s2a", "s2b"),
            seed=7,
            min_assignments=2,
            expect_role=AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "rerandomized_downgrade_without_rule",
            family=AssignmentFamily.RERANDOMIZED_DESIGN_CANDIDATE,
            units=complete_units[:8],
            observed=("u0", "u1"),
            seed=2,
            min_assignments=3,
            expect_role=AssignmentRole.FALSIFICATION_ONLY,
        ),
        _scenario(
            "rerandomized_balance_filtered",
            family=AssignmentFamily.RERANDOMIZED_DESIGN_CANDIDATE,
            units=rerand_units,
            observed=("u0", "u4"),
            constraints={"balance_key": "x", "max_imbalance": 3.5},
            seed=4,
            min_assignments=2,
            expect_role=AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "greedy_falsification_only",
            family=AssignmentFamily.GREEDY_MATCHED_MARKET_FALSIFICATION,
            units=complete_units[:7],
            observed=("u0", "u1"),
            seed=1,
            min_assignments=3,
            expect_role=AssignmentRole.FALSIFICATION_ONLY,
        ),
        _scenario(
            "kernel_thinning_falsification_only",
            family=AssignmentFamily.KERNEL_THINNING_FALSIFICATION,
            units=complete_units[:7],
            observed=("u0",),
            seed=1,
            min_assignments=3,
            expect_role=AssignmentRole.FALSIFICATION_ONLY,
        ),
        _scenario(
            "fixed_deterministic_falsification_only",
            family=AssignmentFamily.FIXED_DETERMINISTIC_FALSIFICATION,
            units=complete_units[:6],
            observed=("u2",),
            seed=1,
            min_assignments=2,
            expect_role=AssignmentRole.FALSIFICATION_ONLY,
        ),
        _scenario(
            "unknown_assignment_blocked",
            family=AssignmentFamily.UNKNOWN_ASSIGNMENT_BLOCKED,
            units=complete_units[:5],
            observed=("u0",),
            expect_non_empty=False,
        ),
    ]


def run_determinism_checks() -> dict[str, Any]:
    spec = AssignmentDesignSpec(
        family=AssignmentFamily.COMPLETE_RANDOMIZED_SET,
        units=[AssignmentUnit(unit_id=f"u{i}") for i in range(12)],
        observed_treated_unit_ids=("u0", "u1"),
        seed=99,
        min_assignments=5,
        max_assignments=8,
    )
    a = generate_pseudo_assignments(spec)
    b = generate_pseudo_assignments(spec)
    return {
        "passed": [x.pseudo_treated_unit_ids for x in a] == [x.pseudo_treated_unit_ids for x in b],
        "assignment_count": len(a),
    }


def build_summary() -> dict[str, Any]:
    scenarios = build_scenarios()
    positive = [s for s in scenarios if s["passed"] and s["assignment_count"] > 0]
    negative = [s for s in scenarios if s["passed"] and s["assignment_count"] == 0]
    failed = [s for s in scenarios if not s["passed"]]

    role_counts: dict[str, int] = {}
    decision_counts: dict[str, int] = {}
    for s in scenarios:
        for role, count in s["summary"].get("role_counts", {}).items():
            role_counts[role] = role_counts.get(role, 0) + count
        for status, count in s["summary"].get("decision_counts", {}).items():
            decision_counts[status] = decision_counts.get(status, 0) + count

    design_based = [
        AssignmentFamily.COMPLETE_RANDOMIZED_SET.value,
        AssignmentFamily.MATCHED_PAIR_RANDOMIZED.value,
        AssignmentFamily.MATCHED_BLOCK_RANDOMIZED.value,
        AssignmentFamily.STRATIFIED_RANDOMIZED.value,
    ]
    falsification_only = [
        AssignmentFamily.GREEDY_MATCHED_MARKET_FALSIFICATION.value,
        AssignmentFamily.KERNEL_THINNING_FALSIFICATION.value,
        AssignmentFamily.FIXED_DETERMINISTIC_FALSIFICATION.value,
    ]
    blocked = [AssignmentFamily.UNKNOWN_ASSIGNMENT_BLOCKED.value]

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "input_artifacts": [
            "docs/audits/INFERENCE_REPLACEMENT_SCOUT_001.md",
            "panel_exp/design/assignment_generators.py",
        ],
        "assignment_families_evaluated": [f.value for f in AssignmentFamily],
        "generator_contract": {
            "module": "panel_exp.design.assignment_generators",
            "functions": [
                "generate_pseudo_assignments",
                "validate_pseudo_assignment",
                "summarize_assignment_generation",
            ],
        },
        "scenario_results": scenarios,
        "positive_scenarios": [s["scenario_id"] for s in positive],
        "negative_scenarios": [s["scenario_id"] for s in negative],
        "failed_scenarios": [s["scenario_id"] for s in failed],
        "role_counts": role_counts,
        "decision_counts": decision_counts,
        "determinism_checks": run_determinism_checks(),
        "constraint_preservation_checks": {
            "pair_level": "matched_pair_positive",
            "block_level": "matched_block_positive",
            "stratum_level": "stratified_positive",
            "all_passed": all(s["passed"] for s in scenarios),
        },
        "blocked_designs": blocked,
        "falsification_only_designs": falsification_only,
        "design_based_candidate_designs": design_based,
        "known_limitations": [
            "No placebo p-values or randomization inference implemented.",
            "Rerandomization without explicit acceptance rule downgrades to falsification only.",
            "Greedy/thinning/fixed designs never marked design-based randomization candidates.",
        ],
        "trustreport_authorized": False,
        "calibration_signal_allowed": False,
        "production_decisioning_allowed": False,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "budget_optimization_allowed": False,
        "governance_verdict": "design_aware_assignment_generators_defined_no_inference_authorization",
        "next_artifact": "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",
    }


def run_validation(*, strict: bool = False) -> dict[str, Any]:
    summary = build_summary()
    if strict and summary["failed_scenarios"]:
        raise SystemExit(f"strict mode: failed scenarios {summary['failed_scenarios']}")
    if strict and not summary["determinism_checks"]["passed"]:
        raise SystemExit("strict mode: determinism check failed")
    return summary


def write_summary(path: Path, summary: dict[str, Any], *, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"summary exists: {path} (pass --overwrite)")
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=_DEFAULT_SUMMARY,
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    summary = run_validation(strict=args.strict)
    write_summary(args.summary_output, summary, overwrite=args.overwrite)
    print(json.dumps({"artifact_id": _ARTIFACT_ID, "governance_verdict": summary["governance_verdict"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
