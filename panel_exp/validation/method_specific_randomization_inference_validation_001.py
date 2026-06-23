"""METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.method_specific_randomization import (
    MULTICELL_GLOBAL_NOTE,
    DCM_ADAPTER_NOTE,
    LOTO_SENSITIVITY_NOTE,
    MethodFamily,
    MethodGeometry,
    MethodRandomizationValidationSpec,
    MethodSpecificDecision,
    MethodStatisticKind,
    RandomizationValidationRole,
    build_method_randomization_readiness_matrix,
    summarize_method_randomization_result,
    validate_method_randomization_inference,
)

_ARTIFACT_ID = "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001_summary.json"
)

ROADMAP_SPINE = [
    "ROADMAP_REFOCUS_METHOD_VALIDATION_001",
    "INFERENCE_REPLACEMENT_SCOUT_001",
    "DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",
    "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",
    "SCM_PLACEBO_GOVERNED_SEMANTICS_001",
    "METHOD_ROADMAP_ALIGNMENT_AUDIT_001",
    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
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


def _candidate_spec(
    family: MethodFamily,
    *,
    geometry: MethodGeometry = MethodGeometry.MULTI_TREATED_SET,
    statistic: MethodStatisticKind = MethodStatisticKind.SIGNED_EFFECT,
    **kwargs: Any,
) -> MethodRandomizationValidationSpec:
    defaults = dict(
        method_family=family,
        statistic_kind=statistic,
        geometry=geometry,
        assignment_role=DESIGN,
        num_treated_units=3,
        num_valid_pseudo_assignments=10,
        has_observed_statistic=True,
        has_pseudo_statistics=True,
        uses_same_statistic_observed_and_pseudo=True,
    )
    defaults.update(kwargs)
    return MethodRandomizationValidationSpec(**defaults)


def _scenario(
    scenario_id: str,
    spec: MethodRandomizationValidationSpec,
    *,
    expect_decision: MethodSpecificDecision,
    expect_role: RandomizationValidationRole | None = None,
) -> dict[str, Any]:
    result = validate_method_randomization_inference(spec)
    passed = result.decision == expect_decision
    if expect_role is not None and result.role != expect_role:
        passed = False
    return {
        "scenario_id": scenario_id,
        "passed": passed,
        "expected_decision": expect_decision.value,
        "expected_role": expect_role.value if expect_role else None,
        "result": summarize_method_randomization_result(result),
    }


def build_scenarios() -> list[dict[str, Any]]:
    return [
        _scenario(
            "scm_multi_treated_candidate",
            _candidate_spec(MethodFamily.SCM),
            expect_decision=MethodSpecificDecision.METHOD_RANDOMIZATION_CANDIDATE,
            expect_role=RandomizationValidationRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "scm_single_treated_placebo_falsification",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.SCM,
                statistic_kind=MethodStatisticKind.PLACEBO_TAIL_FRACTION,
                geometry=MethodGeometry.SINGLE_TREATED,
                assignment_role=DESIGN,
                num_treated_units=1,
                has_observed_statistic=True,
                has_pseudo_statistics=True,
                uses_same_statistic_observed_and_pseudo=True,
                num_valid_pseudo_assignments=5,
            ),
            expect_decision=MethodSpecificDecision.METHOD_FALSIFICATION_DIAGNOSTIC_ONLY,
        ),
        _scenario(
            "scm_missing_pseudo_statistics",
            _candidate_spec(MethodFamily.SCM, has_pseudo_statistics=False),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "scm_statistic_mismatch",
            _candidate_spec(MethodFamily.SCM, uses_same_statistic_observed_and_pseudo=False),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "did_design_based_candidate",
            _candidate_spec(MethodFamily.DID),
            expect_decision=MethodSpecificDecision.METHOD_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "did_bootstrap_only_diagnostic",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.DID,
                statistic_kind=MethodStatisticKind.BOOTSTRAP_INTERVAL,
                geometry=MethodGeometry.MULTI_TREATED_SET,
                assignment_role=DESIGN,
                has_observed_statistic=True,
                has_pseudo_statistics=False,
                uses_same_statistic_observed_and_pseudo=False,
            ),
            expect_decision=MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY,
        ),
        _scenario(
            "augsynth_point_candidate",
            _candidate_spec(MethodFamily.AUGSYNTH_CVXPY),
            expect_decision=MethodSpecificDecision.METHOD_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "augsynth_jk_diagnostic_only",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.AUGSYNTH_CVXPY,
                statistic_kind=MethodStatisticKind.JACKKNIFE_INTERVAL,
                geometry=MethodGeometry.MULTI_TREATED_SET,
                assignment_role=DESIGN,
                has_observed_statistic=True,
                has_pseudo_statistics=True,
                uses_same_statistic_observed_and_pseudo=True,
                num_valid_pseudo_assignments=5,
            ),
            expect_decision=MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY,
        ),
        _scenario(
            "tbrridge_brb_diagnostic",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.TBRRIDGE,
                statistic_kind=MethodStatisticKind.BOOTSTRAP_INTERVAL,
                geometry=MethodGeometry.MULTI_TREATED_SET,
            ),
            expect_decision=MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY,
        ),
        _scenario(
            "tbrridge_kfold_diagnostic",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.TBRRIDGE,
                statistic_kind=MethodStatisticKind.SIGNED_EFFECT,
                geometry=MethodGeometry.MULTI_TREATED_SET,
            ),
            expect_decision=MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY,
        ),
        _scenario(
            "tbrridge_placebo_diagnostic",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.TBRRIDGE,
                statistic_kind=MethodStatisticKind.PLACEBO_TAIL_FRACTION,
                geometry=MethodGeometry.SINGLE_TREATED,
            ),
            expect_decision=MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY,
        ),
        _scenario(
            "tbrridge_jk_blocked",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.TBRRIDGE,
                statistic_kind=MethodStatisticKind.JACKKNIFE_INTERVAL,
                geometry=MethodGeometry.MULTI_TREATED_SET,
                assignment_role=DESIGN,
                num_valid_pseudo_assignments=10,
                has_observed_statistic=True,
                has_pseudo_statistics=True,
                uses_same_statistic_observed_and_pseudo=True,
            ),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "tbr_aggregate_geometry_blocked",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.TBR,
                statistic_kind=MethodStatisticKind.SIGNED_EFFECT,
                geometry=MethodGeometry.AGGREGATE,
            ),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "bayesian_tbr_research_deferred",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.BAYESIAN_TBR,
                statistic_kind=MethodStatisticKind.POSTERIOR_INTERVAL,
                geometry=MethodGeometry.MULTI_TREATED_SET,
            ),
            expect_decision=MethodSpecificDecision.METHOD_RESEARCH_DEFERRED,
        ),
        _scenario(
            "synthetic_did_research_deferred",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.SYNTHETIC_DID,
                statistic_kind=MethodStatisticKind.UNKNOWN,
                geometry=MethodGeometry.UNKNOWN,
            ),
            expect_decision=MethodSpecificDecision.METHOD_RESEARCH_DEFERRED,
        ),
        _scenario(
            "trop_research_deferred",
            MethodRandomizationValidationSpec(
                method_family=MethodFamily.TROP,
                statistic_kind=MethodStatisticKind.UNKNOWN,
                geometry=MethodGeometry.UNKNOWN,
            ),
            expect_decision=MethodSpecificDecision.METHOD_RESEARCH_DEFERRED,
        ),
        _scenario(
            "falsification_assignment_role",
            _candidate_spec(MethodFamily.SCM, assignment_role=FALSIFICATION),
            expect_decision=MethodSpecificDecision.METHOD_FALSIFICATION_DIAGNOSTIC_ONLY,
        ),
        _scenario(
            "blocked_assignment_role",
            _candidate_spec(MethodFamily.SCM, assignment_role=BLOCKED_ROLE),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "final_p_value_blocked",
            _candidate_spec(MethodFamily.SCM, requested_final_p_value=True),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "causal_ci_blocked",
            _candidate_spec(MethodFamily.SCM, requested_causal_interval=True),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "trustreport_blocked",
            _candidate_spec(MethodFamily.SCM, requested_trustreport_authorization=True),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "calibration_signal_blocked",
            _candidate_spec(MethodFamily.SCM, requested_calibration_signal=True),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "mmm_ingestion_blocked",
            _candidate_spec(MethodFamily.SCM, requested_mmm_ingestion=True),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "llm_decisioning_blocked",
            _candidate_spec(MethodFamily.SCM, requested_llm_decisioning=True),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "production_live_scheduler_budget_blocked",
            _candidate_spec(
                MethodFamily.SCM,
                requested_production_decisioning=True,
                requested_live_api=True,
                requested_scheduler=True,
                requested_budget_optimization=True,
            ),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "multicell_global_blocked",
            _candidate_spec(
                MethodFamily.SCM,
                geometry=MethodGeometry.MULTICELL_SHARED_CONTROL,
                notes=(MULTICELL_GLOBAL_NOTE,),
            ),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
        _scenario(
            "per_cell_marginal_candidate",
            _candidate_spec(
                MethodFamily.SCM,
                geometry=MethodGeometry.MULTICELL_SHARED_CONTROL,
            ),
            expect_decision=MethodSpecificDecision.METHOD_RANDOMIZATION_CANDIDATE,
        ),
        _scenario(
            "scm_loto_sensitivity_only",
            _candidate_spec(
                MethodFamily.SCM,
                notes=(LOTO_SENSITIVITY_NOTE,),
            ),
            expect_decision=MethodSpecificDecision.METHOD_SENSITIVITY_ONLY,
        ),
        _scenario(
            "dcm_adapter_blocked",
            _candidate_spec(MethodFamily.SCM, notes=(DCM_ADAPTER_NOTE,)),
            expect_decision=MethodSpecificDecision.METHOD_BLOCKED,
        ),
    ]


def _readiness_counts(scenarios: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {r.value: 0 for r in RandomizationValidationRole}
    for s in scenarios:
        role = s["result"]["role"]
        counts[role] = counts.get(role, 0) + 1
    return counts


def _method_lists(matrix: list[dict[str, Any]]) -> dict[str, list[str]]:
    candidates: list[str] = []
    diagnostic: list[str] = []
    deferred: list[str] = []
    blocked: list[str] = []
    for row in matrix:
        key = f"{row['method_family']}+{row['statistic_kind']}+{row['geometry']}"
        role = row["default_role"]
        if role == RandomizationValidationRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value:
            candidates.append(key)
        elif role == RandomizationValidationRole.DIAGNOSTIC_ONLY.value:
            diagnostic.append(key)
        elif role == RandomizationValidationRole.RESEARCH_DEFERRED.value:
            deferred.append(key)
        elif role == RandomizationValidationRole.BLOCKED.value:
            blocked.append(key)
    return {
        "candidate_methods": candidates,
        "diagnostic_only_methods": diagnostic,
        "research_deferred_methods": deferred,
        "blocked_methods": blocked,
    }


def run_method_specific_randomization_inference_validation() -> dict[str, Any]:
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    matrix = build_method_randomization_readiness_matrix()
    method_lists = _method_lists(matrix)
    counts = _readiness_counts(scenarios)
    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "verdict": "method_specific_randomization_inference_validated_no_downstream_authorization",
        "governance_verdict": "method_specific_randomization_inference_validated_no_downstream_authorization",
        "roadmap_spine": ROADMAP_SPINE,
        "method_families_classified": [f.value for f in MethodFamily],
        "scenario_results": scenarios,
        "scenario_count": len(scenarios),
        "passed_scenarios": len(scenarios) - len(failed),
        "failed_scenarios": failed,
        "method_readiness_counts": counts,
        "method_readiness_matrix": matrix,
        **method_lists,
        "required_next_evidence": [
            "scm_treated_set_placebo_integration",
            "tbrridge_replacement_inference",
            "multicell_multiplicity_calibration",
            "multicell_shared_control_dependence",
            "augsynth_estimand_scale_bridge",
        ],
        "trustreport_authorized": False,
        "calibration_signal_allowed": False,
        "mmm_ingestion_allowed": False,
        "llm_decisioning_allowed": False,
        "production_decisioning_allowed": False,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "budget_optimization_allowed": False,
        "next_artifact": "SCM_TREATED_SET_PLACEBO_INTEGRATION_001",
    }


def run_validation(*, strict: bool = False) -> dict[str, Any]:
    summary = run_method_specific_randomization_inference_validation()
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
