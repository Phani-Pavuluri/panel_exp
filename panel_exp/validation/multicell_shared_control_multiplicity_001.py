"""MULTICELL_SHARED_CONTROL_MULTIPLICITY_001 validation harness."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.inference.multicell_multiplicity import (
    MultiCellDecisionUseCase,
    MultiCellDependenceStructure,
    MultiCellMultiplicityDecision,
    MultiCellMultiplicityRole,
    MultiCellMultiplicitySpec,
    MultiplicityAdjustmentKind,
    compute_bonferroni_alpha,
    compute_independent_familywise_false_positive_risk,
    summarize_multicell_multiplicity_result,
    validate_multicell_multiplicity,
)

_ARTIFACT_ID = "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_summary.json"
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
]


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


def _spec(**kwargs: Any) -> MultiCellMultiplicitySpec:
    defaults: dict[str, Any] = dict(
        use_case=MultiCellDecisionUseCase.PER_CELL_MARGINAL,
        num_cells=3,
        nominal_alpha=0.10,
        dependence_structure=MultiCellDependenceStructure.INDEPENDENT_APPROXIMATION,
    )
    defaults.update(kwargs)
    return MultiCellMultiplicitySpec(**defaults)


def _scenario(
    scenario_id: str,
    multiplicity_spec: MultiCellMultiplicitySpec,
    *,
    expect_decision: MultiCellMultiplicityDecision,
    expect_role: MultiCellMultiplicityRole | None = None,
    expect_fwer: float | None = None,
    expect_bonferroni: float | None = None,
) -> dict[str, Any]:
    result = validate_multicell_multiplicity(multiplicity_spec)
    passed = result.decision == expect_decision
    if expect_role is not None and result.role != expect_role:
        passed = False
    if expect_fwer is not None and result.independent_familywise_false_positive_risk is not None:
        if not math.isclose(
            result.independent_familywise_false_positive_risk,
            expect_fwer,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            passed = False
    if expect_bonferroni is not None and result.adjusted_alpha_bonferroni is not None:
        if not math.isclose(
            result.adjusted_alpha_bonferroni,
            expect_bonferroni,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            passed = False
    return {
        "scenario_id": scenario_id,
        "passed": passed,
        "expected_decision": expect_decision.value,
        "expected_role": expect_role.value if expect_role else None,
        "result": summarize_multicell_multiplicity_result(result),
    }


def build_scenarios() -> list[dict[str, Any]]:
    fwer_3 = compute_independent_familywise_false_positive_risk(0.10, 3)
    bonf_3 = compute_bonferroni_alpha(0.10, 3)

    return [
        _scenario(
            "per_cell_marginal_with_estimands",
            _spec(
                use_case=MultiCellDecisionUseCase.PER_CELL_MARGINAL,
                has_cell_level_estimand_contracts=True,
            ),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_PER_CELL_MARGINAL_ALLOWED_AS_SEPARATE_READOUT,
            expect_role=MultiCellMultiplicityRole.PER_CELL_MARGINAL_ONLY,
        ),
        _scenario(
            "per_cell_marginal_missing_estimands",
            _spec(
                use_case=MultiCellDecisionUseCase.PER_CELL_MARGINAL,
                has_cell_level_estimand_contracts=False,
            ),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "multiple_cell_family_no_adjustment",
            _spec(use_case=MultiCellDecisionUseCase.MULTIPLE_CELL_FAMILY),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_FAMILY_REQUIRES_MULTIPLICITY_ADJUSTMENT,
            expect_role=MultiCellMultiplicityRole.MULTIPLICITY_ADJUSTMENT_REQUIRED,
            expect_fwer=fwer_3,
            expect_bonferroni=bonf_3,
        ),
        _scenario(
            "multiple_cell_family_bonferroni",
            _spec(
                use_case=MultiCellDecisionUseCase.MULTIPLE_CELL_FAMILY,
                adjustment_kind=MultiplicityAdjustmentKind.BONFERRONI,
            ),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_FAMILY_REQUIRES_MULTIPLICITY_ADJUSTMENT,
            expect_role=MultiCellMultiplicityRole.MULTIPLICITY_ADJUSTMENT_REQUIRED,
        ),
        _scenario(
            "multiple_cell_family_holm",
            _spec(
                use_case=MultiCellDecisionUseCase.MULTIPLE_CELL_FAMILY,
                adjustment_kind=MultiplicityAdjustmentKind.HOLM,
            ),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_FAMILY_REQUIRES_MULTIPLICITY_ADJUSTMENT,
            expect_role=MultiCellMultiplicityRole.MULTIPLICITY_ADJUSTMENT_REQUIRED,
        ),
        _scenario(
            "shared_control_no_dependence_model",
            _spec(
                use_case=MultiCellDecisionUseCase.SHARED_CONTROL_FAMILY,
                dependence_structure=MultiCellDependenceStructure.SHARED_CONTROL,
            ),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_SHARED_CONTROL_REQUIRES_DEPENDENCE_MODEL,
            expect_role=MultiCellMultiplicityRole.SHARED_CONTROL_DEPENDENCE_UNRESOLVED,
        ),
        _scenario(
            "shared_control_dependence_no_joint_null",
            _spec(
                use_case=MultiCellDecisionUseCase.SHARED_CONTROL_FAMILY,
                dependence_structure=MultiCellDependenceStructure.SHARED_CONTROL,
                has_shared_control_dependence_model=True,
                has_valid_joint_null_distribution=False,
            ),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_RESEARCH_DEFERRED,
            expect_role=MultiCellMultiplicityRole.RESEARCH_DEFERRED,
        ),
        _scenario(
            "global_decision_blocked",
            _spec(use_case=MultiCellDecisionUseCase.GLOBAL_DECISION),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_GLOBAL_DECISION_BLOCKED,
        ),
        _scenario(
            "winner_selection_blocked",
            _spec(use_case=MultiCellDecisionUseCase.WINNER_SELECTION),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_WINNER_SELECTION_BLOCKED,
        ),
        _scenario(
            "pooled_effect_blocked",
            _spec(
                use_case=MultiCellDecisionUseCase.POOLED_EFFECT,
                has_pooled_estimand_contract=True,
            ),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_POOLED_EFFECT_BLOCKED,
        ),
        _scenario(
            "pooled_effect_missing_estimand",
            _spec(
                use_case=MultiCellDecisionUseCase.POOLED_EFFECT,
                has_pooled_estimand_contract=False,
            ),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_POOLED_EFFECT_BLOCKED,
        ),
        _scenario(
            "unknown_dependence_research_deferred",
            _spec(dependence_structure=MultiCellDependenceStructure.UNKNOWN),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_RESEARCH_DEFERRED,
            expect_role=MultiCellMultiplicityRole.RESEARCH_DEFERRED,
        ),
        _scenario(
            "invalid_num_cells_zero",
            _spec(num_cells=0),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "invalid_negative_alpha",
            _spec(nominal_alpha=-0.1),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "invalid_alpha_ge_one",
            _spec(nominal_alpha=1.0),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "fwer_formula_alpha_010_m_3",
            _spec(use_case=MultiCellDecisionUseCase.MULTIPLE_CELL_FAMILY),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_FAMILY_REQUIRES_MULTIPLICITY_ADJUSTMENT,
            expect_fwer=fwer_3,
        ),
        _scenario(
            "bonferroni_formula_alpha_010_m_3",
            _spec(use_case=MultiCellDecisionUseCase.MULTIPLE_CELL_FAMILY),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_FAMILY_REQUIRES_MULTIPLICITY_ADJUSTMENT,
            expect_bonferroni=bonf_3,
        ),
        _scenario(
            "trustreport_blocked",
            _spec(requested_trustreport_authorization=True),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "calibration_signal_blocked",
            _spec(requested_calibration_signal=True),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "mmm_ingestion_blocked",
            _spec(requested_mmm_ingestion=True),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "llm_decisioning_blocked",
            _spec(requested_llm_decisioning=True),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "production_decisioning_blocked",
            _spec(requested_production_decisioning=True),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "live_api_blocked",
            _spec(requested_live_api=True),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "scheduler_blocked",
            _spec(requested_scheduler=True),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "budget_optimization_blocked",
            _spec(requested_budget_optimization=True),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
        ),
        _scenario(
            "governance_flags_all_false",
            _spec(
                use_case=MultiCellDecisionUseCase.PER_CELL_MARGINAL,
                has_cell_level_estimand_contracts=True,
            ),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_PER_CELL_MARGINAL_ALLOWED_AS_SEPARATE_READOUT,
        ),
        _scenario(
            "no_downstream_promotion_authorized",
            _spec(use_case=MultiCellDecisionUseCase.MULTIPLE_CELL_FAMILY),
            expect_decision=MultiCellMultiplicityDecision.MULTICELL_FAMILY_REQUIRES_MULTIPLICITY_ADJUSTMENT,
        ),
    ]


def _count_scenarios(scenarios: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "per_cell_marginal_only_scenarios": 0,
        "adjustment_required_scenarios": 0,
        "shared_control_unresolved_scenarios": 0,
        "blocked_scenarios": 0,
    }
    for s in scenarios:
        role = s["result"]["role"]
        if role == MultiCellMultiplicityRole.PER_CELL_MARGINAL_ONLY.value:
            counts["per_cell_marginal_only_scenarios"] += 1
        elif role == MultiCellMultiplicityRole.MULTIPLICITY_ADJUSTMENT_REQUIRED.value:
            counts["adjustment_required_scenarios"] += 1
        elif role == MultiCellMultiplicityRole.SHARED_CONTROL_DEPENDENCE_UNRESOLVED.value:
            counts["shared_control_unresolved_scenarios"] += 1
        elif s["result"]["is_blocked"]:
            counts["blocked_scenarios"] += 1
    return counts


def run_multicell_shared_control_multiplicity_validation() -> dict[str, Any]:
    """Run deterministic multi-cell shared-control multiplicity validation scenarios."""
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
        "global_multicell_decision_allowed": False,
        "winner_selection_allowed": False,
        "pooled_multicell_effect_allowed": False,
    }

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "verdict": "multicell_shared_control_multiplicity_defined_no_downstream_authorization",
        "governance_verdict": (
            "multicell_shared_control_multiplicity_defined_no_downstream_authorization"
        ),
        "roadmap_spine": ROADMAP_SPINE,
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        **scenario_counts,
        "multiplicity_contract": {
            "independent_fwer_formula": "1 - (1 - alpha)^m",
            "bonferroni_alpha_formula": "alpha / m",
            "shared_control_warning": (
                "independent FWER is a proxy only and does not authorize "
                "shared-control global/winner/pooled inference"
            ),
        },
        "allowed_outputs": [
            "per_cell_marginal_only",
            "familywise_false_positive_risk_proxy",
            "bonferroni_alpha",
            "multiplicity_adjustment_required",
            "shared_control_dependence_unresolved",
            "blocked",
        ],
        "forbidden_outputs": [
            "global_multicell_decision",
            "winner_selection",
            "pooled_multicell_effect",
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
        "next_artifact": "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_multicell_shared_control_multiplicity_validation()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    if args.overwrite:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"artifact_id": _ARTIFACT_ID, "verdict": summary["verdict"]}))


if __name__ == "__main__":
    main()
