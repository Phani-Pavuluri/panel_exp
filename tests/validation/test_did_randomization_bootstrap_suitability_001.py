"""Tests for DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.did_randomization_bootstrap_suitability_001 import (
    MIN_AUDIT_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    AuditRequiredAction,
    AuditStatus,
    DidPath,
    _AUTH_FLAGS,
    _DID_AUTH_FLAGS,
    build_did_randomization_bootstrap_suitability_audit,
    build_scenarios,
    filter_did_randomization_bootstrap_suitability_audit,
    run_validation,
    summarize_did_randomization_bootstrap_suitability_audit,
    validate_did_randomization_bootstrap_suitability_audit,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001_summary.json"
_REPORT = _REPO / "docs/track_d/DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001_REPORT.md"


def test_audit_rows_build_and_minimum_count() -> None:
    rows = build_did_randomization_bootstrap_suitability_audit()
    assert len(rows) >= MIN_AUDIT_ROW_COUNT
    assert len({r.path_id for r in rows}) == len(rows)


def test_all_paths_statuses_and_actions_represented() -> None:
    rows = build_did_randomization_bootstrap_suitability_audit()
    validation = validate_did_randomization_bootstrap_suitability_audit(rows)
    assert validation["valid"]
    assert validation["all_paths_represented"]
    assert validation["all_statuses_represented"]
    assert validation["all_actions_represented"]


def test_summary_flags() -> None:
    rows = build_did_randomization_bootstrap_suitability_audit()
    summary = summarize_did_randomization_bootstrap_suitability_audit(rows)
    assert summary["did_point_diagnostic_allowed"] is True
    assert summary["did_production_inference_authorized"] is False
    assert summary["did_production_p_value_authorized"] is False
    assert summary["did_causal_ci_authorized"] is False
    assert summary["did_randomization_candidate_requires_known_assignment"] is True
    assert summary["did_permutation_candidate_requires_valid_assignment_support"] is True
    assert summary["did_bootstrap_candidate_requires_dependence_validation"] is True
    assert summary["bootstrap_does_not_fix_invalid_assignment"] is True
    assert summary["parallel_trends_required_before_promotion"] is True
    assert summary["staggered_timing_requires_research_handling"] is True
    assert summary["small_n_and_few_clusters_block_promotion"] is True
    assert summary["sparse_count_binary_outcomes_require_dgp_coverage"] is True
    assert summary["multicell_did_requires_multiplicity_research"] is True
    assert summary["observed_diagnostics_required"] is True
    assert summary["dgp_coverage_required"] is True
    assert summary["failure_registry_consulted"] is True
    assert summary["design_assignment_stress_required"] is True
    assert summary["downstream_work_paused"] is True
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]


def test_no_downstream_authorization() -> None:
    rows = build_did_randomization_bootstrap_suitability_audit()
    summary = summarize_did_randomization_bootstrap_suitability_audit(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    for flag, expected in _DID_AUTH_FLAGS.items():
        if flag in ("did_point_diagnostic_allowed",):
            assert summary[flag] is True
        elif flag.endswith("_authorized") or flag == "did_production_inference_authorized":
            assert summary[flag] is False
        else:
            assert summary[flag] is expected


def test_filter_helpers() -> None:
    rows = build_did_randomization_bootstrap_suitability_audit()
    bootstrap = filter_did_randomization_bootstrap_suitability_audit(rows, did_path=DidPath.BOOTSTRAP)
    assert bootstrap
    blocked = filter_did_randomization_bootstrap_suitability_audit(rows, current_status=AuditStatus.BLOCKED)
    assert len(blocked) >= 5
    rand_candidates = filter_did_randomization_bootstrap_suitability_audit(
        rows, randomization_allowed_as_research_candidate=True
    )
    assert rand_candidates
    boot_candidates = filter_did_randomization_bootstrap_suitability_audit(
        rows, bootstrap_allowed_as_research_candidate=True
    )
    assert boot_candidates
    action = filter_did_randomization_bootstrap_suitability_audit(
        rows, required_action=AuditRequiredAction.BLOCK
    )
    assert action


def test_required_fields_nonempty() -> None:
    rows = build_did_randomization_bootstrap_suitability_audit()
    for row in rows:
        assert row.required_design_conditions
        assert row.observed_diagnostic_triggers
        assert row.dgp_triggers
        assert row.failure_registry_links
        assert row.affected_designs
        assert row.affected_inference_paths


def test_summary_count_consistency() -> None:
    rows = build_did_randomization_bootstrap_suitability_audit()
    summary = summarize_did_randomization_bootstrap_suitability_audit(rows)
    validation = validate_did_randomization_bootstrap_suitability_audit(rows)
    assert summary["audit_row_count"] == len(rows)
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["required_action_counts"] == validation["required_action_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001"
    assert data["failed_scenarios"] == []
    assert data["audit_row_count"] >= MIN_AUDIT_ROW_COUNT
