"""SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.inference.scm_augsynth_statistic_adapter import (
    AdaptedStatisticSet,
    AdapterCompatibilityStatus,
    AdapterStatisticKind,
    AdapterUsageBoundary,
    StatisticAdapterFamily,
    build_adapted_statistic_set_from_dict,
    build_statistic_adapter_readiness_matrix,
    compare_observed_and_pseudo_statistic_contract,
    summarize_statistic_adapter_compatibility_result,
)

_ARTIFACT_ID = "SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_augsynth_statistic_adapter_contract_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001_summary.json"
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
]

NEXT_ARTIFACT = "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"

_PSEUDO = {f"a{i}": 0.03 * (i % 7) - 0.05 for i in range(1, 26)}


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


def _set_dict(
    *,
    family: str,
    kind: str,
    observed: float | None = 0.12,
    pseudo: dict[str, float] | None = None,
    effect_direction: str = "two_sided",
    studentization_scale_id: str | None = None,
    source: str = "TEST",
    **config_overrides: Any,
) -> AdaptedStatisticSet:
    config = {
        "estimand_id": "treated_set_att",
        "outcome_scale": "absolute_level",
        "pre_period_id": "pre_main",
        "post_period_id": "post_main",
        "donor_eligibility_rule_id": "eligible_donors_v1",
        "estimator_config_id": "default_v1",
        "treated_set_aggregation_rule_id": "mean_across_treated",
        "effect_direction": effect_direction,
        "missing_data_policy_id": "complete_case_v1",
        "statistic_kind": kind,
        "studentization_scale_id": studentization_scale_id,
    }
    config.update(config_overrides)
    return build_adapted_statistic_set_from_dict(
        {
            "observed_statistic": observed,
            "pseudo_statistic_by_assignment": pseudo if pseudo is not None else dict(_PSEUDO),
            "config": config,
            "provenance": {
                "estimator_family": family,
                "estimator_version": "contract_v1",
                "adapter_version": "1.0.0",
                "config_hash": "sha256:test",
                "source_artifact_id": source,
                "computation_mode": "statistic_first",
            },
        }
    )


def _scenario(scenario_id: str, passed: bool, *, detail: str = "") -> dict[str, Any]:
    return {"scenario_id": scenario_id, "passed": passed, "detail": detail}


def _compare(set_a: AdaptedStatisticSet, set_b: AdaptedStatisticSet | None = None) -> Any:
    return compare_observed_and_pseudo_statistic_contract(set_a, set_b)


def build_scenarios() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []

    scm_cal = _set_dict(
        family="scm_style_calibration",
        kind="scm_style_effect",
        source="SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
    )
    r = _compare(scm_cal)
    scenarios.append(
        _scenario(
            "valid_scm_style_calibration_harness_only",
            r.is_calibration_harness_only and not r.is_blocked,
        )
    )

    scm = _set_dict(family="scm", kind="point_effect", source="SCM_TREATED_SET_PLACEBO_INTEGRATION_001")
    r = _compare(scm)
    scenarios.append(
        _scenario(
            "valid_scm_randomization_candidate_only",
            r.is_randomization_candidate_compatible and not r.is_blocked,
        )
    )

    for sid, kind in (
        ("valid_augsynth_point", "point_effect"),
        ("valid_augsynth_relative", "relative_effect"),
        ("valid_augsynth_studentized", "studentized_effect"),
    ):
        stud = "pre_period_residual_scale" if kind == "studentized_effect" else None
        aug = _set_dict(
            family="augsynth_cvxpy",
            kind=kind,
            observed=0.42,
            studentization_scale_id=stud,
            source="AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
        )
        r = _compare(aug)
        scenarios.append(
            _scenario(
                sid,
                r.is_randomization_candidate_compatible and not r.is_blocked,
            )
        )

    base = _set_dict(family="scm", kind="point_effect")
    pseudo_match = _set_dict(family="scm", kind="point_effect")
    scenarios.append(
        _scenario(
            "observed_pseudo_config_match",
            not _compare(base, pseudo_match).is_blocked,
        )
    )

    scm_side = _set_dict(family="scm", kind="point_effect")
    aug_side = _set_dict(family="augsynth_cvxpy", kind="point_effect", observed=0.42)
    cross = _compare(scm_side, aug_side)
    scenarios.append(
        _scenario(
            "scm_augsynth_side_by_side_shared_config",
            cross.status == AdapterCompatibilityStatus.COMPATIBLE
            and cross.is_diagnostic_only,
        )
    )

    scenarios.append(
        _scenario(
            "missing_observed_statistic_blocked",
            _compare(_set_dict(family="scm", kind="point_effect", observed=None)).status
            == AdapterCompatibilityStatus.MISSING_OBSERVED_STATISTIC,
        )
    )
    scenarios.append(
        _scenario(
            "missing_pseudo_statistics_blocked",
            _compare(_set_dict(family="scm", kind="point_effect", pseudo={})).status
            in {
                AdapterCompatibilityStatus.MISSING_PSEUDO_STATISTICS,
                AdapterCompatibilityStatus.INSUFFICIENT_PSEUDO_STATISTICS,
            },
        )
    )
    scenarios.append(
        _scenario(
            "non_finite_observed_statistic_blocked",
            _compare(_set_dict(family="scm", kind="point_effect", observed=float("nan"))).status
            == AdapterCompatibilityStatus.NON_NUMERIC_STATISTIC,
        )
    )
    bad_pseudo = dict(_PSEUDO)
    bad_pseudo["a1"] = float("inf")
    scenarios.append(
        _scenario(
            "non_finite_pseudo_statistic_blocked",
            _compare(_set_dict(family="scm", kind="point_effect", pseudo=bad_pseudo)).is_blocked,
        )
    )
    scenarios.append(
        _scenario(
            "too_few_pseudo_statistics_blocked",
            _compare(_set_dict(family="scm", kind="point_effect", pseudo={"a1": 0.1})).status
            == AdapterCompatibilityStatus.INSUFFICIENT_PSEUDO_STATISTICS,
        )
    )
    scenarios.append(
        _scenario(
            "unsupported_family_blocked",
            _compare(_set_dict(family="unknown", kind="point_effect")).status
            == AdapterCompatibilityStatus.UNSUPPORTED_FAMILY,
        )
    )
    scenarios.append(
        _scenario(
            "unknown_statistic_kind_blocked",
            _compare(_set_dict(family="scm", kind="unknown")).is_blocked,
        )
    )
    scenarios.append(
        _scenario(
            "missing_provenance_blocked",
            _compare(
                build_adapted_statistic_set_from_dict(
                    {
                        "observed_statistic": 0.1,
                        "pseudo_statistic_by_assignment": dict(_PSEUDO),
                        "config": {
                            "estimand_id": "treated_set_att",
                            "outcome_scale": "absolute_level",
                            "pre_period_id": "pre_main",
                            "post_period_id": "post_main",
                            "donor_eligibility_rule_id": "eligible_donors_v1",
                            "estimator_config_id": "default_v1",
                            "treated_set_aggregation_rule_id": "mean_across_treated",
                            "effect_direction": "two_sided",
                            "missing_data_policy_id": "complete_case_v1",
                            "statistic_kind": "point_effect",
                        },
                        "provenance": {
                            "estimator_family": "scm",
                            "estimator_version": "",
                            "adapter_version": "",
                            "config_hash": "",
                            "source_artifact_id": "",
                            "computation_mode": "",
                        },
                    }
                )
            ).status
            == AdapterCompatibilityStatus.PROVENANCE_MISSING,
        )
    )

    def _mismatch(field: str, value: str, expect: AdapterCompatibilityStatus) -> None:
        overrides = {field: value}
        left = _set_dict(family="scm", kind="point_effect")
        right = _set_dict(family="scm", kind="point_effect", **overrides)
        scenarios.append(
            _scenario(
                f"{field}_mismatch_blocked",
                _compare(left, right).status == expect,
            )
        )

    _mismatch("estimand_id", "other_estimand", AdapterCompatibilityStatus.ESTIMAND_MISMATCH)
    _mismatch("outcome_scale", "relative", AdapterCompatibilityStatus.OUTCOME_SCALE_MISMATCH)
    _mismatch("pre_period_id", "pre_alt", AdapterCompatibilityStatus.TIME_WINDOW_MISMATCH)
    _mismatch("post_period_id", "post_alt", AdapterCompatibilityStatus.TIME_WINDOW_MISMATCH)
    _mismatch(
        "donor_eligibility_rule_id",
        "other_rule",
        AdapterCompatibilityStatus.DONOR_ELIGIBILITY_MISMATCH,
    )
    _mismatch(
        "estimator_config_id",
        "other_config",
        AdapterCompatibilityStatus.ESTIMATOR_CONFIG_MISMATCH,
    )
    _mismatch(
        "treated_set_aggregation_rule_id",
        "median",
        AdapterCompatibilityStatus.TREATED_SET_AGGREGATION_MISMATCH,
    )
    _mismatch(
        "effect_direction",
        "greater",
        AdapterCompatibilityStatus.EFFECT_DIRECTION_MISMATCH,
    )
    _mismatch(
        "missing_data_policy_id",
        "impute_v1",
        AdapterCompatibilityStatus.MISSING_DATA_POLICY_MISMATCH,
    )
    _mismatch("statistic_kind", "relative_effect", AdapterCompatibilityStatus.STATISTIC_KIND_MISMATCH)

    stud_left = _set_dict(
        family="augsynth_cvxpy",
        kind="studentized_effect",
        studentization_scale_id="pre_period_residual_scale",
    )
    stud_right = _set_dict(
        family="augsynth_cvxpy",
        kind="studentized_effect",
        studentization_scale_id="other_scale",
    )
    scenarios.append(
        _scenario(
            "studentization_scale_mismatch_blocked",
            _compare(stud_left, stud_right).status
            == AdapterCompatibilityStatus.STATISTIC_KIND_MISMATCH,
        )
    )

    scenarios.append(
        _scenario(
            "invalid_effect_direction_blocked",
            _compare(_set_dict(family="scm", kind="point_effect", effect_direction="invalid")).is_blocked,
        )
    )

    sample = _compare(_set_dict(family="scm", kind="point_effect"))
    scenarios.append(
        _scenario(
            "summary_includes_usage_boundary",
            summarize_statistic_adapter_compatibility_result(sample).get("usage_boundary")
            == AdapterUsageBoundary.RANDOMIZATION_CANDIDATE_ONLY.value,
        )
    )

    matrix = build_statistic_adapter_readiness_matrix()
    row_ids = {r["row_id"] for r in matrix}
    scenarios.append(
        _scenario("readiness_matrix_scm_style_calibration_row", "scm_style_calibration_harness" in row_ids)
    )
    scenarios.append(
        _scenario(
            "readiness_matrix_scm_randomization_candidate_row",
            "scm_treated_set_randomization_candidate" in row_ids,
        )
    )
    scenarios.append(
        _scenario(
            "readiness_matrix_augsynth_point_row",
            "augsynth_point_randomization" in row_ids,
        )
    )

    auth_flags = (
        "production_p_value_authorized",
        "causal_confidence_interval_authorized",
        "trustreport_authorized",
        "calibration_signal_allowed",
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
    )
    for flag in auth_flags:
        scenarios.append(
            _scenario(
                f"no_result_authorizes_{flag}",
                sample.governance_flags.get(flag) is False,
            )
        )

    scenarios.append(
        _scenario(
            "recommended_next_artifact_valid",
            NEXT_ARTIFACT in {
                "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
                "MULTICELL_MAX_T_RESEARCH_SCOUT_001",
            },
        )
    )

    return scenarios


def run_scm_augsynth_statistic_adapter_contract_harness() -> dict[str, Any]:
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    matrix = build_statistic_adapter_readiness_matrix()

    compatible = 0
    cal_only = 0
    rand_only = 0
    blocked = 0
    for s in scenarios:
        sid = s["scenario_id"]
        if "blocked" in sid and s["passed"]:
            blocked += 1
        if sid.startswith("valid_scm_style_calibration"):
            cal_only += 1
        if sid.startswith("valid_scm_randomization") or sid.startswith("valid_augsynth"):
            rand_only += 1
        if sid in {"observed_pseudo_config_match", "scm_augsynth_side_by_side_shared_config"}:
            compatible += 1

    governance = {
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

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "verdict": _VERDICT,
        "governance_verdict": _VERDICT,
        "roadmap_spine": ROADMAP_SPINE,
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "compatible_scenarios": compatible,
        "calibration_harness_only_scenarios": cal_only,
        "randomization_candidate_only_scenarios": rand_only,
        "blocked_scenarios": blocked,
        "readiness_matrix_rows": len(matrix),
        "readiness_matrix": matrix,
        "recommended_next_artifact": NEXT_ARTIFACT,
        "adapter_contract": {
            "required_config_fields": [
                "estimand_id",
                "outcome_scale",
                "pre_period_id",
                "post_period_id",
                "donor_eligibility_rule_id",
                "estimator_config_id",
                "treated_set_aggregation_rule_id",
                "effect_direction",
                "missing_data_policy_id",
                "statistic_kind",
            ],
            "required_provenance_fields": [
                "estimator_family",
                "estimator_version",
                "adapter_version",
                "config_hash",
                "source_artifact_id",
                "computation_mode",
            ],
            "supported_families": [
                "scm",
                "scm_style_calibration",
                "augsynth_cvxpy",
            ],
            "usage_boundaries": [
                "calibration_harness_only",
                "randomization_candidate_only",
                "diagnostic_only",
                "blocked",
            ],
        },
        "next_required_evidence": [
            "production estimator-backed adapter implementation",
            "larger null calibration grids",
            "assignment-generator stress tests",
            "SCM vs AugSynth disagreement diagnostics",
            "method-specific promotion audit",
        ],
        "forbidden_outputs": [
            "production_p_value",
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
        "next_artifact": NEXT_ARTIFACT,
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--summary", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_scm_augsynth_statistic_adapter_contract_harness()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    print(json.dumps({"artifact_id": summary["artifact_id"], "verdict": summary["verdict"]}))

    if args.overwrite or args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
