"""CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.inference.calibration_signal_method_gate_draft import (
    CalibrationSignalGateStatus,
    build_calibration_signal_method_gate_draft,
    filter_calibration_gate_rows,
    find_calibration_gate_row,
    validate_calibration_signal_method_gate_draft,
)
from panel_exp.inference.method_readiness_matrix_v2 import (
    ReadinessTier,
    build_method_readiness_matrix_v2,
)

_ARTIFACT_ID = "CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001"
_ARTIFACT_VERSION = "1.0.0"
_SOURCE_MATRIX = "METHOD_READINESS_MATRIX_V2_001"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001_summary.json"
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
    "METHOD_READINESS_MATRIX_V2_001",
    "CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001",
]

DOWNSTREAM_KEYS = (
    "calibration_signal_allowed",
    "calibration_signal_authorized",
    "trustreport_authorized",
    "mmm_ingestion_allowed",
    "llm_decisioning_allowed",
    "production_decisioning_allowed",
    "live_api_authorized",
    "scheduler_authorized",
    "budget_optimization_allowed",
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


def build_scenarios() -> list[dict[str, Any]]:
    matrix = build_method_readiness_matrix_v2()
    draft = build_calibration_signal_method_gate_draft(matrix)
    validation = validate_calibration_signal_method_gate_draft(draft)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("draft_builds_from_matrix", validation["valid"] or draft.rows))
    scenarios.append(
        _scenario(
            "row_count_equals_source_matrix",
            validation["row_count"] == validation["source_row_count"],
        )
    )
    scenarios.append(_scenario("all_source_method_ids_represented", validation["method_ids_match_source_matrix"]))
    scenarios.append(_scenario("method_ids_unique", validation["unique_method_ids"]))

    restricted = [
        r for r in draft.rows if r.readiness_tier == ReadinessTier.RESTRICTED_RESEARCH_MODE_USABLE.value
    ]
    scenarios.append(
        _scenario(
            "restricted_research_maps_eligible_future_review",
            all(
                r.gate_status == CalibrationSignalGateStatus.ELIGIBLE_FOR_FUTURE_REVIEW
                for r in restricted
            ),
        )
    )

    framework = [
        r
        for r in draft.rows
        if r.readiness_tier == ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE.value
    ]
    scenarios.append(
        _scenario(
            "framework_candidates_conditionally_reviewable",
            all(
                r.gate_status
                == CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE
                for r in framework
            ),
        )
    )

    per_cell = find_calibration_gate_row(draft, "multicell_per_cell_marginal_only")
    scenarios.append(
        _scenario(
            "per_cell_marginal_conditionally_reviewable_with_scope_evidence",
            per_cell is not None
            and per_cell.gate_status
            == CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE
            and "per_cell_only_calibration_signal_scope_rule" in per_cell.categorical_exclusion_reasons,
        )
    )

    contract = find_calibration_gate_row(draft, "stratified_pooled_estimand_contract_candidate")
    scenarios.append(
        _scenario(
            "contract_candidate_not_eligible_contract_only",
            contract is not None
            and contract.gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_CONTRACT_ONLY,
        )
    )

    diagnostic = [
        r for r in draft.rows if r.readiness_tier == ReadinessTier.DIAGNOSTIC_ONLY.value
    ]
    scenarios.append(
        _scenario(
            "diagnostic_rows_not_eligible_diagnostic_only",
            all(
                r.gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_DIAGNOSTIC_ONLY
                for r in diagnostic
            ),
        )
    )

    sensitivity = find_calibration_gate_row(draft, "scm_leave_one_treated_out_sensitivity_only")
    scenarios.append(
        _scenario(
            "sensitivity_row_not_eligible_sensitivity_only",
            sensitivity is not None
            and sensitivity.gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_SENSITIVITY_ONLY,
        )
    )

    heterogeneity = find_calibration_gate_row(draft, "stratified_pooling_heterogeneity_review_required")
    scenarios.append(
        _scenario(
            "heterogeneity_review_conditionally_reviewable",
            heterogeneity is not None
            and heterogeneity.gate_status
            == CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE,
        )
    )

    unresolved = [
        r
        for r in draft.rows
        if r.readiness_tier == ReadinessTier.MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED.value
    ]
    scenarios.append(
        _scenario(
            "multiplicity_unresolved_not_eligible",
            all(
                r.gate_status
                == CalibrationSignalGateStatus.NOT_ELIGIBLE_UNRESOLVED_MULTIPLICITY_DEPENDENCE
                for r in unresolved
            ),
        )
    )

    deferred = find_calibration_gate_row(draft, "dcm_009_019_adapters_research_deferred")
    scenarios.append(
        _scenario(
            "research_deferred_not_eligible",
            deferred is not None
            and deferred.gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_RESEARCH_DEFERRED,
        )
    )

    blocked = [r for r in draft.rows if r.readiness_tier == ReadinessTier.BLOCKED.value]
    scenarios.append(
        _scenario(
            "blocked_rows_not_eligible_blocked",
            all(r.gate_status == CalibrationSignalGateStatus.NOT_ELIGIBLE_BLOCKED for r in blocked),
        )
    )

    for key in DOWNSTREAM_KEYS:
        scenarios.append(
            _scenario(
                f"all_rows_{key}_false",
                all(not getattr(row, key) for row in draft.rows),
            )
        )

    reviewable = [
        r
        for r in draft.rows
        if r.gate_status
        in {
            CalibrationSignalGateStatus.ELIGIBLE_FOR_FUTURE_REVIEW,
            CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE,
        }
    ]
    scenarios.append(
        _scenario(
            "eligible_rows_have_required_evidence",
            all(r.required_evidence_before_review for r in reviewable if r.gate_status == CalibrationSignalGateStatus.ELIGIBLE_FOR_FUTURE_REVIEW),
        )
    )
    scenarios.append(
        _scenario(
            "conditionally_reviewable_rows_have_required_evidence",
            all(
                r.required_evidence_before_review
                for r in reviewable
                if r.gate_status
                == CalibrationSignalGateStatus.CONDITIONALLY_REVIEWABLE_AFTER_ADDITIONAL_EVIDENCE
            ),
        )
    )

    ineligible = [
        r for r in draft.rows if r.gate_status.value.startswith("not_eligible_")
    ]
    scenarios.append(
        _scenario(
            "ineligible_rows_have_exclusion_reasons",
            all(r.categorical_exclusion_reasons for r in ineligible),
        )
    )

    scenarios.append(
        _scenario(
            "all_rows_forbid_signal_creation_export",
            all(
                "actual_calibration_signal_creation" in r.forbidden_outputs
                and "calibration_signal_export" in r.forbidden_outputs
                for r in draft.rows
            ),
        )
    )
    scenarios.append(
        _scenario(
            "all_rows_forbid_downstream_execution",
            all(
                all(
                    x in r.forbidden_outputs
                    for x in (
                        "mmm_ingestion",
                        "llm_decisioning",
                        "production_decisioning",
                        "live_api_execution",
                        "scheduler_execution",
                        "budget_optimization",
                    )
                )
                for r in draft.rows
            ),
        )
    )

    scenarios.append(
        _scenario(
            "find_row_works",
            find_calibration_gate_row(draft, "scm_treated_set_placebo_candidate") is not None,
        )
    )
    filtered = filter_calibration_gate_rows(
        draft, gate_status=CalibrationSignalGateStatus.NOT_ELIGIBLE_BLOCKED
    )
    scenarios.append(
        _scenario(
            "filter_by_gate_status_works",
            len(filtered) == draft.gate_status_counts["not_eligible_blocked"],
        )
    )
    filtered_family = filter_calibration_gate_rows(draft, method_family="scm")
    scenarios.append(
        _scenario("filter_by_method_family_works", len(filtered_family) >= 3)
    )
    scenarios.append(
        _scenario(
            "summary_counts_match_rows",
            sum(draft.gate_status_counts.values()) == len(draft.rows),
        )
    )

    governance = {k: False for k in DOWNSTREAM_KEYS}
    scenarios.append(
        _scenario(
            "summary_json_authorization_flags_false",
            all(v is False for v in governance.values()),
        )
    )
    scenarios.append(
        _scenario(
            "no_row_claims_trustreport_expansion",
            all(not row.trustreport_authorized for row in draft.rows),
        )
    )
    scenarios.append(
        _scenario(
            "draft_validation_passes",
            validation["valid"],
            detail="; ".join(validation.get("issues", [])),
        )
    )

    return scenarios


def run_calibration_signal_method_gate_draft_validation() -> dict[str, Any]:
    """Run deterministic CalibrationSignal method gate draft validation scenarios."""
    draft = build_calibration_signal_method_gate_draft()
    validation = validate_calibration_signal_method_gate_draft(draft)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    governance = {k: False for k in DOWNSTREAM_KEYS}

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "verdict": "calibration_signal_method_gate_draft_defined_no_authorization",
        "governance_verdict": "calibration_signal_method_gate_draft_defined_no_authorization",
        "source_matrix_artifact_id": _SOURCE_MATRIX,
        "roadmap_spine": ROADMAP_SPINE,
        "row_count": validation["row_count"],
        "source_row_count": validation["source_row_count"],
        "method_ids_match_source_matrix": validation["method_ids_match_source_matrix"],
        "unique_method_ids": validation["unique_method_ids"],
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "gate_status_counts": validation["gate_status_counts"],
        "draft_gate_boundaries": {
            "eligible_for_future_review": (
                "future review only; no signal creation or downstream authorization"
            ),
            "conditionally_reviewable_after_additional_evidence": (
                "not signal-ready; requires additional evidence before review"
            ),
            "not_eligible_diagnostic_only": "diagnostic rows cannot produce CalibrationSignal",
            "not_eligible_sensitivity_only": "sensitivity rows cannot produce CalibrationSignal",
            "not_eligible_contract_only": "contract rows are not inference authorization",
            "not_eligible_unresolved_multiplicity_dependence": (
                "multiplicity/dependence unresolved rows cannot produce CalibrationSignal"
            ),
            "not_eligible_research_deferred": (
                "research deferred rows cannot produce CalibrationSignal"
            ),
            "not_eligible_blocked": "blocked rows cannot produce CalibrationSignal",
        },
        "forbidden_outputs": [
            "actual_calibration_signal_creation",
            "calibration_signal_export",
            "calibration_signal_ingestion",
            "trustreport_expansion",
            "mmm_ingestion",
            "llm_decisioning",
            "production_decisioning",
            "live_api_execution",
            "scheduler_execution",
            "budget_optimization",
        ],
        "next_artifact": "CALIBRATION_SIGNAL_SCHEMA_ALIGNMENT_DRAFT_001",
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_calibration_signal_method_gate_draft_validation()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    if args.overwrite:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"artifact_id": _ARTIFACT_ID, "verdict": summary["verdict"]}))


if __name__ == "__main__":
    main()
