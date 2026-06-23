"""Tests for METHOD_READINESS_MATRIX_V2_001."""

from __future__ import annotations

from panel_exp.inference.method_readiness_matrix_v2 import (
    GeometryV2,
    MethodFamilyV2,
    ReadinessTier,
    REQUIRED_METHOD_IDS,
    UsageBoundaryV2,
    build_method_readiness_matrix_v2,
    filter_method_readiness_rows,
    find_method_readiness_row,
    validate_method_readiness_matrix_v2,
)

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

DOWNSTREAM_KEYS = (
    "trustreport_authorized",
    "calibration_signal_allowed",
    "mmm_ingestion_allowed",
    "llm_decisioning_allowed",
    "production_decisioning_allowed",
    "live_api_authorized",
    "scheduler_authorized",
    "budget_optimization_allowed",
)


def test_matrix_builds() -> None:
    matrix = build_method_readiness_matrix_v2()
    assert matrix.artifact_id == "METHOD_READINESS_MATRIX_V2_001"
    assert len(matrix.rows) >= 25


def test_required_method_ids_present() -> None:
    matrix = build_method_readiness_matrix_v2()
    ids = {row.method_id for row in matrix.rows}
    assert REQUIRED_METHOD_IDS <= ids


def test_method_ids_unique() -> None:
    matrix = build_method_readiness_matrix_v2()
    ids = [row.method_id for row in matrix.rows]
    assert len(ids) == len(set(ids))


def test_all_rows_have_evidence_refs() -> None:
    matrix = build_method_readiness_matrix_v2()
    assert all(row.evidence_refs for row in matrix.rows)


def test_all_downstream_flags_false() -> None:
    matrix = build_method_readiness_matrix_v2()
    for row in matrix.rows:
        for key in DOWNSTREAM_KEYS:
            assert getattr(row, key) is False
    for key in DOWNSTREAM_KEYS:
        assert matrix.downstream_authorization_flags[key] is False


def test_restricted_research_rows_research_only() -> None:
    matrix = build_method_readiness_matrix_v2()
    rows = filter_method_readiness_rows(
        matrix, readiness_tier=ReadinessTier.RESTRICTED_RESEARCH_MODE_USABLE
    )
    assert rows
    assert all(r.usage_boundary == UsageBoundaryV2.RESEARCH_MODE_REPORTING_ONLY for r in rows)


def test_framework_candidates_framework_only() -> None:
    matrix = build_method_readiness_matrix_v2()
    rows = filter_method_readiness_rows(
        matrix, readiness_tier=ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE
    )
    assert len(rows) == 3
    assert all(r.usage_boundary == UsageBoundaryV2.FRAMEWORK_LEVEL_CANDIDATE_ONLY for r in rows)


def test_candidate_rows_forbid_production_outputs() -> None:
    matrix = build_method_readiness_matrix_v2()
    candidate_tiers = {
        ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE,
        ReadinessTier.CONTRACT_CANDIDATE,
        ReadinessTier.PER_CELL_MARGINAL_ONLY,
    }
    for row in matrix.rows:
        if row.readiness_tier not in candidate_tiers:
            continue
        assert CANDIDATE_FORBIDDEN <= set(row.forbidden_outputs)


def test_diagnostic_rows_diagnostic_only() -> None:
    matrix = build_method_readiness_matrix_v2()
    rows = filter_method_readiness_rows(matrix, readiness_tier=ReadinessTier.DIAGNOSTIC_ONLY)
    assert all(r.usage_boundary == UsageBoundaryV2.DIAGNOSTIC_SUMMARY_ONLY for r in rows)


def test_sensitivity_row_sensitivity_only() -> None:
    matrix = build_method_readiness_matrix_v2()
    row = find_method_readiness_row(matrix, "scm_leave_one_treated_out_sensitivity_only")
    assert row is not None
    assert row.readiness_tier == ReadinessTier.SENSITIVITY_ONLY


def test_per_cell_marginal_forbids_global() -> None:
    matrix = build_method_readiness_matrix_v2()
    row = find_method_readiness_row(matrix, "multicell_per_cell_marginal_only")
    assert row is not None
    assert "global_multicell_decision" in row.forbidden_outputs


def test_stratified_pooled_contract_only() -> None:
    matrix = build_method_readiness_matrix_v2()
    row = find_method_readiness_row(matrix, "stratified_pooled_estimand_contract_candidate")
    assert row is not None
    assert row.readiness_tier == ReadinessTier.CONTRACT_CANDIDATE
    assert "production_pooled_effect" in row.forbidden_outputs


def test_multicell_global_winner_pooled_blocked() -> None:
    matrix = build_method_readiness_matrix_v2()
    for method_id in (
        "multicell_global_decision_blocked",
        "multicell_winner_selection_blocked",
        "multicell_pooled_effect_blocked",
    ):
        row = find_method_readiness_row(matrix, method_id)
        assert row is not None
        assert row.readiness_tier == ReadinessTier.BLOCKED


def test_augsynth_point_candidate_jk_diagnostic() -> None:
    matrix = build_method_readiness_matrix_v2()
    point = find_method_readiness_row(matrix, "augsynth_point_randomization_candidate")
    jk = find_method_readiness_row(matrix, "augsynth_jackknife_diagnostic_only")
    jk_blocked = find_method_readiness_row(matrix, "augsynth_jk_production_inference_blocked")
    assert point is not None and point.readiness_tier == ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE
    assert jk is not None and jk.readiness_tier == ReadinessTier.DIAGNOSTIC_ONLY
    assert jk_blocked is not None and jk_blocked.readiness_tier == ReadinessTier.BLOCKED


def test_tbrridge_paths() -> None:
    matrix = build_method_readiness_matrix_v2()
    for mid in (
        "tbrridge_brb_diagnostic_only",
        "tbrridge_kfold_diagnostic_only",
        "tbrridge_placebo_diagnostic_only",
    ):
        row = find_method_readiness_row(matrix, mid)
        assert row is not None and row.readiness_tier == ReadinessTier.DIAGNOSTIC_ONLY
    jk = find_method_readiness_row(matrix, "tbrridge_jackknife_blocked")
    assert jk is not None and jk.readiness_tier == ReadinessTier.BLOCKED


def test_tbr_aggregate_blocked() -> None:
    matrix = build_method_readiness_matrix_v2()
    row = find_method_readiness_row(matrix, "tbr_aggregate_geometry_blocked")
    assert row is not None and row.readiness_tier == ReadinessTier.BLOCKED


def test_dcm_adapters_research_deferred() -> None:
    matrix = build_method_readiness_matrix_v2()
    row = find_method_readiness_row(matrix, "dcm_009_019_adapters_research_deferred")
    assert row is not None and row.readiness_tier == ReadinessTier.RESEARCH_DEFERRED


def test_find_and_filter_helpers() -> None:
    matrix = build_method_readiness_matrix_v2()
    assert find_method_readiness_row(matrix, "nonexistent") is None
    scm_rows = filter_method_readiness_rows(matrix, method_family=MethodFamilyV2.SCM)
    assert len(scm_rows) >= 3
    blocked = filter_method_readiness_rows(matrix, geometry=GeometryV2.GLOBAL)
    assert len(blocked) == 1


def test_validation_passes() -> None:
    matrix = build_method_readiness_matrix_v2()
    result = validate_method_readiness_matrix_v2(matrix)
    assert result["valid"]
    assert result["required_rows_present"]
    assert sum(result["readiness_tier_counts"].values()) == result["row_count"]
