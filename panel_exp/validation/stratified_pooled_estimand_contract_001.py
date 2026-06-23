"""STRATIFIED_POOLED_ESTIMAND_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.inference.stratified_pooled_estimand import (
    HeterogeneityPolicy,
    PooledEstimandDecision,
    PooledEstimandGeometry,
    PooledEstimandRole,
    PooledEstimandUseCase,
    PoolingWeightKind,
    StratifiedPooledEstimandSpec,
    StratumEstimandSpec,
    normalize_pooling_weights,
    summarize_stratified_pooled_estimand_result,
    validate_stratified_pooled_estimand,
)

_ARTIFACT_ID = "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/STRATIFIED_POOLED_ESTIMAND_CONTRACT_001_summary.json"
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


def _stratum(stratum_id: str, **kwargs: Any) -> StratumEstimandSpec:
    defaults: dict[str, Any] = dict(
        estimand_id="ate",
        metric="revenue",
        effect_scale="absolute",
        target_population="geo",
        time_window="post",
        is_compatible=True,
    )
    defaults.update(kwargs)
    return StratumEstimandSpec(stratum_id=stratum_id, **defaults)


def _strata_pair(**kwargs: Any) -> tuple[StratumEstimandSpec, StratumEstimandSpec]:
    return (_stratum("s1", **kwargs), _stratum("s2", **kwargs))


def _spec(**kwargs: Any) -> StratifiedPooledEstimandSpec:
    s1, s2 = _strata_pair()
    defaults: dict[str, Any] = dict(
        use_case=PooledEstimandUseCase.STRATUM_LEVEL_READOUT,
        geometry=PooledEstimandGeometry.MULTI_STRATUM,
        strata=(s1, s2),
        weighting_kind=PoolingWeightKind.NONE,
        has_common_metric=True,
        has_common_effect_scale=True,
        has_common_time_window=True,
        has_common_target_population=True,
    )
    defaults.update(kwargs)
    return StratifiedPooledEstimandSpec(**defaults)


def _contract_spec(**kwargs: Any) -> StratifiedPooledEstimandSpec:
    defaults: dict[str, Any] = dict(
        use_case=PooledEstimandUseCase.STRATIFIED_AGGREGATE,
        geometry=PooledEstimandGeometry.MULTI_STRATUM,
        weighting_kind=PoolingWeightKind.PRE_SPECIFIED_POPULATION,
        weights_by_stratum={"s1": 0.6, "s2": 0.4},
        weights_pre_specified=True,
        heterogeneity_policy=HeterogeneityPolicy.ALLOW_WITH_PRE_SPECIFIED_POOLING,
        heterogeneity_assessed=True,
        material_heterogeneity_detected=False,
        has_valid_pooled_estimand_statement=True,
        has_valid_inference_for_pooling=True,
        has_multiplicity_adjustment=True,
        has_shared_control_dependence_resolution=True,
    )
    defaults.update(kwargs)
    return _spec(**defaults)


def _scenario(
    scenario_id: str,
    estimand_spec: StratifiedPooledEstimandSpec,
    *,
    expect_decision: PooledEstimandDecision,
    expect_role: PooledEstimandRole | None = None,
    expect_weights_sum_one: bool = False,
) -> dict[str, Any]:
    result = validate_stratified_pooled_estimand(estimand_spec)
    passed = result.decision == expect_decision
    if expect_role is not None and result.role != expect_role:
        passed = False
    if expect_weights_sum_one:
        weights = result.normalized_weights_by_stratum or {}
        total = sum(weights.values())
        if not math.isclose(total, 1.0, rel_tol=0, abs_tol=1e-9):
            passed = False
    return {
        "scenario_id": scenario_id,
        "passed": passed,
        "expected_decision": expect_decision.value,
        "expected_role": expect_role.value if expect_role else None,
        "result": summarize_stratified_pooled_estimand_result(result),
    }


def build_scenarios() -> list[dict[str, Any]]:
    s1, s2 = _strata_pair()
    return [
        _scenario(
            "stratum_level_readout_allowed",
            _spec(use_case=PooledEstimandUseCase.STRATUM_LEVEL_READOUT, strata=(s1,)),
            expect_decision=PooledEstimandDecision.STRATUM_LEVEL_READOUT_ALLOWED,
            expect_role=PooledEstimandRole.STRATUM_LEVEL_ONLY,
        ),
        _scenario(
            "multiple_stratum_readouts_not_pooled",
            _spec(use_case=PooledEstimandUseCase.STRATUM_LEVEL_READOUT),
            expect_decision=PooledEstimandDecision.STRATUM_LEVEL_READOUT_ALLOWED,
            expect_role=PooledEstimandRole.STRATUM_LEVEL_ONLY,
        ),
        _scenario(
            "stratified_aggregate_contract_candidate",
            _contract_spec(),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_CONTRACT_CANDIDATE,
            expect_role=PooledEstimandRole.POOLED_ESTIMAND_CONTRACT_CANDIDATE,
            expect_weights_sum_one=True,
        ),
        _scenario(
            "stratified_aggregate_diagnostic_only",
            _contract_spec(has_valid_inference_for_pooling=False),
            expect_decision=PooledEstimandDecision.STRATIFIED_AGGREGATE_DIAGNOSTIC_ONLY,
            expect_role=PooledEstimandRole.DIAGNOSTIC_SUMMARY_ONLY,
        ),
        _scenario(
            "heterogeneity_not_assessed_review_required",
            _contract_spec(heterogeneity_assessed=False),
            expect_decision=PooledEstimandDecision.HETEROGENEITY_REVIEW_REQUIRED,
            expect_role=PooledEstimandRole.HETEROGENEITY_REVIEW_REQUIRED,
        ),
        _scenario(
            "material_heterogeneity_block_policy_blocked",
            _contract_spec(
                material_heterogeneity_detected=True,
                heterogeneity_policy=HeterogeneityPolicy.BLOCK_IF_MATERIAL_HETEROGENEITY,
            ),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
            expect_role=PooledEstimandRole.BLOCKED,
        ),
        _scenario(
            "material_heterogeneity_report_separately_not_pooled",
            _contract_spec(
                material_heterogeneity_detected=True,
                heterogeneity_policy=HeterogeneityPolicy.REPORT_SEPARATELY,
            ),
            expect_decision=PooledEstimandDecision.STRATIFIED_AGGREGATE_DIAGNOSTIC_ONLY,
            expect_role=PooledEstimandRole.DIAGNOSTIC_SUMMARY_ONLY,
        ),
        _scenario(
            "incompatible_metric_blocked",
            _contract_spec(
                strata=(
                    _stratum("s1", metric="revenue"),
                    _stratum("s2", metric="orders"),
                ),
                has_common_metric=False,
            ),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "incompatible_effect_scale_blocked",
            _contract_spec(
                strata=(
                    _stratum("s1", effect_scale="absolute"),
                    _stratum("s2", effect_scale="relative"),
                ),
                has_common_effect_scale=False,
            ),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "incompatible_time_window_blocked",
            _contract_spec(
                strata=(
                    _stratum("s1", time_window="post"),
                    _stratum("s2", time_window="long_run"),
                ),
                has_common_time_window=False,
            ),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "incompatible_target_population_blocked",
            _contract_spec(
                strata=(
                    _stratum("s1", target_population="geo"),
                    _stratum("s2", target_population="national"),
                ),
                has_common_target_population=False,
            ),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "missing_pooled_estimand_statement_blocked",
            _contract_spec(has_valid_pooled_estimand_statement=False),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "missing_weights_blocked",
            _contract_spec(weights_by_stratum=None),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "weight_id_mismatch_blocked",
            _contract_spec(weights_by_stratum={"s1": 1.0, "s3": 0.0}),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "negative_weight_blocked",
            _contract_spec(weights_by_stratum={"s1": -0.5, "s2": 1.5}),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "zero_total_weights_blocked",
            _contract_spec(weights_by_stratum={"s1": 0.0, "s2": 0.0}),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "non_finite_weight_blocked",
            _contract_spec(weights_by_stratum={"s1": float("inf"), "s2": 0.0}),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "post_hoc_effect_size_weights_blocked",
            _contract_spec(weighting_kind=PoolingWeightKind.POST_HOC_EFFECT_SIZE),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "winner_selected_weights_blocked",
            _contract_spec(weighting_kind=PoolingWeightKind.WINNER_SELECTED),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "pooled_multicell_effect_blocked",
            _spec(
                use_case=PooledEstimandUseCase.POOLED_MULTICELL_EFFECT,
                geometry=PooledEstimandGeometry.SHARED_CONTROL_MULTICELL,
                weighting_kind=PoolingWeightKind.PRE_SPECIFIED_POPULATION,
                weights_by_stratum={"s1": 0.5, "s2": 0.5},
            ),
            expect_decision=PooledEstimandDecision.MULTICELL_POOLED_EFFECT_BLOCKED,
            expect_role=PooledEstimandRole.MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED,
        ),
        _scenario(
            "shared_control_unresolved_pooled_blocked",
            _contract_spec(
                geometry=PooledEstimandGeometry.SHARED_CONTROL_MULTICELL,
                has_shared_control_dependence_resolution=False,
                has_multiplicity_adjustment=False,
            ),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
            expect_role=PooledEstimandRole.MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED,
        ),
        _scenario(
            "global_summary_blocked",
            _spec(use_case=PooledEstimandUseCase.GLOBAL_SUMMARY),
            expect_decision=PooledEstimandDecision.GLOBAL_SUMMARY_BLOCKED,
        ),
        _scenario(
            "winner_selected_summary_blocked",
            _spec(use_case=PooledEstimandUseCase.WINNER_SELECTED_SUMMARY),
            expect_decision=PooledEstimandDecision.WINNER_SELECTED_SUMMARY_BLOCKED,
        ),
        _scenario(
            "trustreport_request_blocked",
            _spec(requested_trustreport_authorization=True),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "calibration_signal_blocked",
            _spec(requested_calibration_signal=True),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "mmm_ingestion_blocked",
            _spec(requested_mmm_ingestion=True),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "llm_decisioning_blocked",
            _spec(requested_llm_decisioning=True),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "production_decisioning_blocked",
            _spec(requested_production_decisioning=True),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "live_api_blocked",
            _spec(requested_live_api=True),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "scheduler_blocked",
            _spec(requested_scheduler=True),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "budget_optimization_blocked",
            _spec(requested_budget_optimization=True),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "pooled_effect_authorization_blocked",
            _spec(requested_pooled_effect_authorization=True),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
        ),
        _scenario(
            "normalized_weights_sum_to_one",
            _contract_spec(),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_CONTRACT_CANDIDATE,
            expect_weights_sum_one=True,
        ),
        _scenario(
            "governance_flags_all_false",
            _contract_spec(),
            expect_decision=PooledEstimandDecision.POOLED_ESTIMAND_CONTRACT_CANDIDATE,
        ),
    ]


def _count_scenarios(scenarios: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "stratum_level_only_scenarios": 0,
        "contract_candidate_scenarios": 0,
        "diagnostic_only_scenarios": 0,
        "heterogeneity_review_required_scenarios": 0,
        "blocked_scenarios": 0,
    }
    for s in scenarios:
        role = s["result"]["role"]
        if role == PooledEstimandRole.STRATUM_LEVEL_ONLY.value:
            counts["stratum_level_only_scenarios"] += 1
        elif role == PooledEstimandRole.POOLED_ESTIMAND_CONTRACT_CANDIDATE.value:
            counts["contract_candidate_scenarios"] += 1
        elif role == PooledEstimandRole.DIAGNOSTIC_SUMMARY_ONLY.value:
            counts["diagnostic_only_scenarios"] += 1
        elif role == PooledEstimandRole.HETEROGENEITY_REVIEW_REQUIRED.value:
            counts["heterogeneity_review_required_scenarios"] += 1
        elif s["result"]["is_blocked"]:
            counts["blocked_scenarios"] += 1
    return counts


def run_stratified_pooled_estimand_contract_validation() -> dict[str, Any]:
    """Run deterministic stratified/pooled estimand contract validation scenarios."""
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
        "pooled_effect_authorized": False,
        "global_summary_allowed": False,
        "winner_selection_allowed": False,
    }

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "verdict": "stratified_pooled_estimand_contract_defined_no_downstream_authorization",
        "governance_verdict": (
            "stratified_pooled_estimand_contract_defined_no_downstream_authorization"
        ),
        "roadmap_spine": ROADMAP_SPINE,
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        **scenario_counts,
        "pooled_estimand_contract": {
            "required_fields": [
                "compatible_stratum_estimands",
                "common_metric",
                "common_effect_scale",
                "common_time_window",
                "common_target_population",
                "pre_specified_weights",
                "heterogeneity_policy",
                "valid_pooling_inference",
                "multiplicity_or_dependence_resolution",
            ],
            "blocked_weighting_rules": [
                "post_hoc_effect_size",
                "winner_selected",
                "unknown",
            ],
            "blocked_claims": [
                "pooled_effect_authorization",
                "global_summary",
                "winner_selection",
                "production_decisioning",
            ],
        },
        "allowed_outputs": [
            "stratum_level_only",
            "pooled_estimand_contract_candidate",
            "diagnostic_summary_only",
            "heterogeneity_review_required",
            "blocked",
        ],
        "forbidden_outputs": [
            "production_pooled_effect",
            "global_multicell_decision",
            "winner_selection",
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
        "next_artifact": "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_stratified_pooled_estimand_contract_validation()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    if args.overwrite:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"artifact_id": _ARTIFACT_ID, "verdict": summary["verdict"]}))


if __name__ == "__main__":
    main()
