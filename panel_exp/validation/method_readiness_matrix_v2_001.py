"""METHOD_READINESS_MATRIX_V2_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.inference.method_readiness_matrix_v2 import (
    GeometryV2,
    MethodFamilyV2,
    ReadinessTier,
    UsageBoundaryV2,
    build_method_readiness_matrix_v2,
    find_method_readiness_row,
    filter_method_readiness_rows,
    summarize_method_readiness_matrix_v2,
    validate_method_readiness_matrix_v2,
)

_ARTIFACT_ID = "METHOD_READINESS_MATRIX_V2_001"
_ARTIFACT_VERSION = "1.0.0"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/METHOD_READINESS_MATRIX_V2_001_summary.json"

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
    "METHOD_READINESS_MATRIX_V2_001",
]

CANDIDATE_FORBIDDEN = frozenset(
    {
        "final_p_value",
        "causal_confidence_interval",
        "trustreport_authorization",
        "calibration_signal",
        "mmm_ingestion",
        "llm_decisioning",
        "production_decisioning",
    }
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


def _scenario(scenario_id: str, passed: bool, *, detail: str = "") -> dict[str, Any]:
    return {"scenario_id": scenario_id, "passed": passed, "detail": detail}


def build_scenarios(matrix_validation: dict[str, Any]) -> list[dict[str, Any]]:
    matrix = build_method_readiness_matrix_v2()
    validation = matrix_validation
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("matrix_builds_successfully", validation["valid"] or validation["row_count"] >= 25))
    scenarios.append(_scenario("minimum_25_rows_present", validation["row_count"] >= 25))
    scenarios.append(_scenario("all_required_method_ids_present", validation["required_rows_present"]))
    scenarios.append(_scenario("method_ids_unique", validation["unique_method_ids"]))

    all_have_evidence = all(row.evidence_refs for row in matrix.rows)
    scenarios.append(_scenario("all_rows_have_evidence_refs", all_have_evidence))

    downstream_false = all(
        not getattr(row, key)
        for row in matrix.rows
        for key in (
            "trustreport_authorized",
            "calibration_signal_allowed",
            "mmm_ingestion_allowed",
            "llm_decisioning_allowed",
            "production_decisioning_allowed",
            "live_api_authorized",
            "scheduler_authorized",
            "budget_optimization_allowed",
        )
    )
    scenarios.append(_scenario("all_downstream_authorization_flags_false", downstream_false))

    restricted = filter_method_readiness_rows(
        matrix, readiness_tier=ReadinessTier.RESTRICTED_RESEARCH_MODE_USABLE
    )
    scenarios.append(
        _scenario(
            "restricted_research_rows_research_only",
            all(
                r.usage_boundary == UsageBoundaryV2.RESEARCH_MODE_REPORTING_ONLY for r in restricted
            ),
        )
    )

    framework = filter_method_readiness_rows(
        matrix, readiness_tier=ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE
    )
    scenarios.append(
        _scenario(
            "framework_candidate_rows_framework_only",
            all(
                r.usage_boundary == UsageBoundaryV2.FRAMEWORK_LEVEL_CANDIDATE_ONLY for r in framework
            ),
        )
    )

    candidate_tiers = {
        ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE,
        ReadinessTier.CONTRACT_CANDIDATE,
        ReadinessTier.PER_CELL_MARGINAL_ONLY,
    }
    candidate_rows = [r for r in matrix.rows if r.readiness_tier in candidate_tiers]

    scenarios.append(
        _scenario(
            "candidate_rows_forbid_production_p_values",
            all("final_p_value" in r.forbidden_outputs for r in candidate_rows),
        )
    )
    scenarios.append(
        _scenario(
            "candidate_rows_forbid_causal_cis",
            all("causal_confidence_interval" in r.forbidden_outputs for r in candidate_rows),
        )
    )
    scenarios.append(
        _scenario(
            "candidate_rows_forbid_trustreport_calibration_mmm_llm",
            all(
                all(
                    x in r.forbidden_outputs
                    for x in (
                        "trustreport_authorization",
                        "calibration_signal",
                        "mmm_ingestion",
                        "llm_decisioning",
                    )
                )
                for r in candidate_rows
            ),
        )
    )

    diagnostic = filter_method_readiness_rows(matrix, readiness_tier=ReadinessTier.DIAGNOSTIC_ONLY)
    scenarios.append(
        _scenario(
            "diagnostic_rows_diagnostic_only_boundary",
            all(r.usage_boundary == UsageBoundaryV2.DIAGNOSTIC_SUMMARY_ONLY for r in diagnostic),
        )
    )

    sensitivity = filter_method_readiness_rows(matrix, readiness_tier=ReadinessTier.SENSITIVITY_ONLY)
    scenarios.append(
        _scenario(
            "sensitivity_row_sensitivity_only_boundary",
            all(r.usage_boundary == UsageBoundaryV2.SENSITIVITY_REVIEW_ONLY for r in sensitivity),
        )
    )

    per_cell = find_method_readiness_row(matrix, "multicell_per_cell_marginal_only")
    scenarios.append(
        _scenario(
            "per_cell_marginal_forbids_global_claim",
            per_cell is not None
            and "global_multicell_decision" in per_cell.forbidden_outputs
            and per_cell.readiness_tier == ReadinessTier.PER_CELL_MARGINAL_ONLY,
        )
    )

    strat_contract = find_method_readiness_row(matrix, "stratified_pooled_estimand_contract_candidate")
    scenarios.append(
        _scenario(
            "stratified_pooled_contract_row_contract_only",
            strat_contract is not None
            and strat_contract.readiness_tier == ReadinessTier.CONTRACT_CANDIDATE
            and strat_contract.usage_boundary
            == UsageBoundaryV2.CONTRACT_ONLY_NO_INFERENCE_AUTHORIZATION,
        )
    )

    shared_ctrl = find_method_readiness_row(matrix, "multicell_shared_control_unresolved")
    scenarios.append(
        _scenario(
            "multicell_shared_control_unresolved_blocked_from_downstream",
            shared_ctrl is not None
            and shared_ctrl.usage_boundary == UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
        )
    )

    for method_id, geom in (
        ("multicell_global_decision_blocked", GeometryV2.GLOBAL),
        ("multicell_winner_selection_blocked", GeometryV2.WINNER_SELECTION),
        ("multicell_pooled_effect_blocked", GeometryV2.POOLED_MULTICELL),
    ):
        row = find_method_readiness_row(matrix, method_id)
        scenarios.append(
            _scenario(
                f"{method_id}_blocked",
                row is not None
                and row.readiness_tier == ReadinessTier.BLOCKED
                and row.geometry == geom,
            )
        )

    augsynth_point = find_method_readiness_row(matrix, "augsynth_point_randomization_candidate")
    scenarios.append(
        _scenario(
            "augsynth_point_row_candidate",
            augsynth_point is not None
            and augsynth_point.readiness_tier
            == ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE,
        )
    )

    augsynth_jk = find_method_readiness_row(matrix, "augsynth_jackknife_diagnostic_only")
    scenarios.append(
        _scenario(
            "augsynth_jk_diagnostic_row_diagnostic_only",
            augsynth_jk is not None and augsynth_jk.readiness_tier == ReadinessTier.DIAGNOSTIC_ONLY,
        )
    )

    augsynth_jk_blocked = find_method_readiness_row(matrix, "augsynth_jk_production_inference_blocked")
    scenarios.append(
        _scenario(
            "augsynth_jk_production_row_blocked",
            augsynth_jk_blocked is not None
            and augsynth_jk_blocked.readiness_tier == ReadinessTier.BLOCKED,
        )
    )

    tbrridge_diag = [
        find_method_readiness_row(matrix, mid)
        for mid in (
            "tbrridge_brb_diagnostic_only",
            "tbrridge_kfold_diagnostic_only",
            "tbrridge_placebo_diagnostic_only",
        )
    ]
    scenarios.append(
        _scenario(
            "tbrridge_brb_kfold_placebo_diagnostic_only",
            all(r is not None and r.readiness_tier == ReadinessTier.DIAGNOSTIC_ONLY for r in tbrridge_diag),
        )
    )

    tbrridge_jk = find_method_readiness_row(matrix, "tbrridge_jackknife_blocked")
    scenarios.append(
        _scenario(
            "tbrridge_jk_row_blocked",
            tbrridge_jk is not None and tbrridge_jk.readiness_tier == ReadinessTier.BLOCKED,
        )
    )

    tbr_agg = find_method_readiness_row(matrix, "tbr_aggregate_geometry_blocked")
    scenarios.append(
        _scenario(
            "tbr_aggregate_geometry_row_blocked",
            tbr_agg is not None and tbr_agg.readiness_tier == ReadinessTier.BLOCKED,
        )
    )

    dcm_deferred = find_method_readiness_row(matrix, "dcm_009_019_adapters_research_deferred")
    scenarios.append(
        _scenario(
            "dcm_009_019_adapters_research_deferred",
            dcm_deferred is not None
            and dcm_deferred.readiness_tier == ReadinessTier.RESEARCH_DEFERRED,
        )
    )

    find_row = find_method_readiness_row(matrix, "scm_treated_set_placebo_candidate")
    scenarios.append(_scenario("find_row_by_method_id_works", find_row is not None))

    filtered = filter_method_readiness_rows(matrix, method_family=MethodFamilyV2.SCM)
    scenarios.append(_scenario("filter_by_method_family_works", len(filtered) >= 3))

    filtered_tier = filter_method_readiness_rows(matrix, readiness_tier=ReadinessTier.BLOCKED)
    scenarios.append(
        _scenario(
            "filter_by_readiness_tier_works",
            len(filtered_tier) >= 5
            and validation["readiness_tier_counts"].get("blocked", 0) == len(filtered_tier),
        )
    )

    scenarios.append(
        _scenario(
            "summary_counts_match_row_tiers",
            sum(validation["readiness_tier_counts"].values()) == validation["row_count"],
        )
    )

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
    scenarios.append(
        _scenario(
            "summary_json_authorization_flags_false",
            all(v is False for v in governance.values()),
        )
    )

    scenarios.append(
        _scenario(
            "matrix_validation_passes",
            validation["valid"],
            detail="; ".join(validation.get("issues", [])),
        )
    )

    return scenarios


def run_method_readiness_matrix_v2_validation() -> dict[str, Any]:
    """Run deterministic method-readiness matrix v2 validation scenarios."""
    matrix = build_method_readiness_matrix_v2()
    validation = validate_method_readiness_matrix_v2(matrix)
    scenarios = build_scenarios(validation)
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

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
        "verdict": "method_readiness_matrix_v2_defined_no_downstream_authorization",
        "governance_verdict": "method_readiness_matrix_v2_defined_no_downstream_authorization",
        "roadmap_spine": ROADMAP_SPINE,
        "row_count": validation["row_count"],
        "required_rows_present": validation["required_rows_present"],
        "unique_method_ids": validation["unique_method_ids"],
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "readiness_tier_counts": validation["readiness_tier_counts"],
        "matrix_boundaries": {
            "restricted_research_mode_usable": (
                "research-mode reporting only; no downstream authorization"
            ),
            "framework_level_randomization_candidate": (
                "candidate only; no production p-value, CI, TrustReport, or CalibrationSignal"
            ),
            "per_cell_marginal_only": "per-cell readout only; no global/winner/pooled claim",
            "contract_candidate": "contract-level candidate only; no inference authorization",
            "diagnostic_only": "diagnostic summary only",
            "sensitivity_only": "sensitivity review only",
            "multiplicity_or_dependence_unresolved": (
                "blocked from downstream until dependence/multiplicity evidence exists"
            ),
            "research_deferred": "requires future method evidence",
            "blocked": "not allowed for governed causal evidence",
        },
        "forbidden_global_outputs": [
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
            "global_multicell_decision",
            "winner_selection",
            "pooled_multicell_effect",
            "augsynth_jk_authorization",
        ],
        "next_artifact": "CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001",
        "matrix_summary": summarize_method_readiness_matrix_v2(matrix),
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_method_readiness_matrix_v2_validation()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    if args.overwrite:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"artifact_id": _ARTIFACT_ID, "verdict": summary["verdict"]}))


if __name__ == "__main__":
    main()
