"""ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.inference.estimator_design_inference_suitability import (
    DesignFamily,
    EstimatorFamily,
    FORBIDDEN_OUTPUTS,
    InferenceFamily,
    RECOMMENDED_NEXT_ARTIFACTS,
    SuitabilityStatus,
    build_estimator_design_inference_suitability_matrix,
    filter_suitability_rows,
    summarize_estimator_design_inference_suitability_matrix,
    validate_estimator_design_inference_suitability_matrix,
)

_ARTIFACT_ID = "ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "estimator_design_inference_suitability_matrix_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001_summary.json"
)

ROADMAP_SPINE = [
    "ROADMAP_REFOCUS_METHOD_VALIDATION_001",
    "INFERENCE_REPLACEMENT_SCOUT_001",
    "DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",
    "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",
    "SCM_PLACEBO_GOVERNED_SEMANTICS_001",
    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
    "SCM_TREATED_SET_PLACEBO_INTEGRATION_001",
    "STUDENTIZED_PLACEBO_RANK_INFERENCE_001",
    "SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001",
    "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
    "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",
    "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
    "METHOD_READINESS_MATRIX_V2_001",
    "CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001",
    "METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001",
    "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001",
    "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
    "SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",
    "ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",
]

NEXT_ARTIFACTS = list(RECOMMENDED_NEXT_ARTIFACTS)

_AUTH_FLAGS = {
    "production_p_value_authorized": False,
    "causal_confidence_interval_authorized": False,
    "trustreport_authorized": False,
    "calibration_signal_allowed": False,
    "mmm_ingestion_allowed": False,
    "llm_decisioning_allowed": False,
    "production_decisioning_allowed": False,
    "live_api_authorized": False,
    "scheduler_authorized": False,
    "budget_optimization_allowed": False,
}


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


def _scenario(scenario_id: str, passed: bool, *, detail: str = "") -> dict[str, Any]:
    return {"scenario_id": scenario_id, "passed": passed, "detail": detail}


def _row_ids(rows: tuple[Any, ...]) -> set[str]:
    return {row.row_id for row in rows}


def build_scenarios() -> list[dict[str, Any]]:
    rows = build_estimator_design_inference_suitability_matrix()
    validation = validate_estimator_design_inference_suitability_matrix(rows)
    summary = summarize_estimator_design_inference_suitability_matrix(rows)
    ids = _row_ids(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("matrix_builds_successfully", len(rows) > 0))
    scenarios.append(_scenario("row_count_at_least_35", len(rows) >= 35))
    scenarios.append(_scenario("row_ids_unique", validation["unique_row_ids"]))
    scenarios.append(_scenario("all_estimator_families_present", validation["estimator_families_present"]))
    scenarios.append(_scenario("all_design_families_present", validation["design_families_present"]))
    scenarios.append(_scenario("all_inference_families_present", validation["inference_families_present"]))

    scenarios.append(_scenario("scm_unit_jackknife_row_exists", "scm_single_treated_unit_jackknife" in ids))
    scenarios.append(_scenario("scm_treated_set_placebo_row_exists", "scm_multi_treated_treated_set_placebo" in ids))
    scenarios.append(_scenario("scm_studentized_placebo_row_exists", "scm_multi_treated_studentized_placebo" in ids))
    scenarios.append(
        _scenario("scm_leave_one_treated_out_row_exists", "scm_leave_one_treated_out" in ids)
    )
    scenarios.append(
        _scenario("augsynth_randomization_row_exists", "augsynth_multi_treated_design_randomization" in ids)
    )
    scenarios.append(_scenario("augsynth_jk_retire_row_exists", "augsynth_jackknife_retire" in ids))
    scenarios.append(_scenario("did_bootstrap_row_exists", "did_matched_stratified_bootstrap" in ids))
    scenarios.append(_scenario("did_permutation_row_exists", "did_permutation_randomization" in ids))
    scenarios.append(_scenario("tbrridge_brb_row_exists", "tbrridge_brb" in ids))
    scenarios.append(_scenario("tbrridge_kfold_row_exists", "tbrridge_kfold" in ids))
    scenarios.append(_scenario("tbrridge_jk_blocked_row_exists", "tbrridge_jackknife" in ids))
    scenarios.append(_scenario("tbr_geometry_mismatch_row_exists", "tbr_aggregate_geometry_mismatch" in ids))
    scenarios.append(
        _scenario("bayesian_tbr_posterior_row_exists", "bayesian_tbr_posterior_interval" in ids)
    )
    scenarios.append(
        _scenario(
            "bayesian_tbr_posterior_predictive_row_exists",
            "bayesian_tbr_posterior_predictive" in ids,
        )
    )
    scenarios.append(
        _scenario("synthetic_did_row_exists", "synthetic_did_bootstrap_permutation" in ids)
    )
    scenarios.append(_scenario("trop_row_exists", "trop_permutation_randomization" in ids))
    scenarios.append(
        _scenario("multicell_max_t_row_exists", "multicell_shared_control_max_t" in ids)
    )
    scenarios.append(
        _scenario("multicell_winner_blocked_row_exists", "multicell_global_winner_blocked" in ids)
    )
    scenarios.append(
        _scenario(
            "stratified_pooled_row_exists",
            "stratified_aggregate_no_heterogeneity" in ids or "scm_stratified_pooled_aggregate" in ids,
        )
    )
    scenarios.append(
        _scenario("unknown_assignment_blocked_row_exists", "unknown_assignment_design_inference" in ids)
    )
    scenarios.append(
        _scenario(
            "fixed_deterministic_falsification_row_exists",
            "fixed_deterministic_placebo_falsification" in ids,
        )
    )
    scenarios.append(
        _scenario(
            "greedy_matched_market_falsification_row_exists",
            "greedy_matched_market_placebo_falsification" in ids,
        )
    )
    scenarios.append(
        _scenario(
            "kernel_thinning_falsification_row_exists",
            "kernel_thinning_placebo_falsification" in ids,
        )
    )

    evidence_ok = all(row.required_evidence or row.known_failure_modes for row in rows)
    scenarios.append(_scenario("every_row_has_evidence_or_blocked_reason", evidence_ok))

    forbidden_ok = all(row.forbidden_outputs == FORBIDDEN_OUTPUTS for row in rows)
    scenarios.append(_scenario("every_row_has_forbidden_outputs", forbidden_ok))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"no_row_authorizes_{flag}", summary[flag] is expected))

    scenarios.append(_scenario("summary_counts_by_estimator", bool(summary["estimator_family_counts"])))
    scenarios.append(_scenario("summary_counts_by_design", bool(summary["design_family_counts"])))
    scenarios.append(_scenario("summary_counts_by_inference", bool(summary["inference_family_counts"])))
    scenarios.append(_scenario("summary_counts_by_status", bool(summary["suitability_status_counts"])))
    scenarios.append(
        _scenario("placebo_not_only_inference_layer", summary["placebo_is_only_inference_layer"] is False)
    )
    scenarios.append(_scenario("downstream_work_paused", summary["downstream_work_paused"] is True))

    for artifact in NEXT_ARTIFACTS:
        scenarios.append(
            _scenario(
                f"recommended_next_artifact_{artifact.lower()}",
                artifact in summary["recommended_next_artifacts"],
            )
        )

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_estimator_design_inference_suitability_matrix()
    validation = validate_estimator_design_inference_suitability_matrix(rows)
    summary = summarize_estimator_design_inference_suitability_matrix(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "roadmap_spine": ROADMAP_SPINE,
        "row_count": len(rows),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "estimator_family_counts": summary["estimator_family_counts"],
        "design_family_counts": summary["design_family_counts"],
        "inference_family_counts": summary["inference_family_counts"],
        "suitability_status_counts": summary["suitability_status_counts"],
        "placebo_is_only_inference_layer": False,
        "downstream_work_paused": True,
        "recommended_next_artifacts": NEXT_ARTIFACTS,
        "inference_layer_decisions": summary["inference_layer_decisions"],
        "next_required_evidence": summary["next_required_evidence"],
        "forbidden_outputs": summary["forbidden_outputs"],
        "validation": validation,
        **_AUTH_FLAGS,
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--summary", type=Path, default=_DEFAULT_SUMMARY)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary)
    print(json.dumps({"verdict": result["verdict"], "failed_scenarios": result["failed_scenarios"]}, indent=2))
    if result["failed_scenarios"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
