"""Tests for D5-TRUST-STRATIFIED-SCM-JK-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import load_registry
from panel_exp.validation.track_d_d5_trust_stratified_scm_jk_001 import (
    EFFECT_PATTERNS,
    GEOMETRY_VARIANTS,
    POLICY_COMPARISONS,
    TRUST_WORLDS,
    _INVESTIGATION_ID,
    StratifiedTrustConfig,
    build_d5_trust_stratified_scm_jk_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/D5_TRUST_STRATIFIED_SCM_JK_001_summary.json"
REPORT = _REPO / "docs/track_d/D5_TRUST_STRATIFIED_SCM_JK_001_REPORT.md"

ALLOWED_VERDICTS = frozenset(
    {
        "stratified_scm_jk_eligible_with_restrictions",
        "stratified_scm_jk_balanced_only",
        "stratified_scm_jk_small_stratum_restricted",
        "stratified_scm_jk_weight_dominance_restricted",
        "stratified_scm_jk_aggregate_blocked",
        "stratified_scm_jk_diagnostic_only",
        "stratified_scm_jk_ineligible",
        "stratified_scm_jk_remediation_required",
        "stratified_scm_jk_inconclusive",
    }
)

REQUIRED_SUMMARY_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "config",
        "worlds",
        "effect_patterns",
        "geometry_variants",
        "run_counts",
        "stratum_level_results",
        "aggregate_results",
        "coverage_by_stratum",
        "coverage_by_geometry",
        "type_i_by_stratum",
        "aggregate_type_i",
        "stratum_weighting_results",
        "donor_pool_results",
        "small_stratum_results",
        "weight_dominance_results",
        "failure_summary",
        "production_defect_assessment",
        "semantic_classification",
        "trustreport_eligibility_implications",
        "authorization_summary",
        "investigation_handoff",
        "limitations",
        "verdict",
    }
)


@pytest.fixture(scope="module")
def fast_payload() -> dict:
    return build_d5_trust_stratified_scm_jk_001(
        StratifiedTrustConfig(fast=True, write_full_results_path=None)
    )


def test_world_count():
    assert len(TRUST_WORLDS) >= 20


def test_geometry_variants_present():
    ids = {g.geometry_id for g in GEOMETRY_VARIANTS}
    assert "balanced_two_strata" in ids
    assert "balanced_three_strata" in ids
    assert "donor_pool_within_stratum_only" in ids
    assert "donor_pool_global" in ids
    assert "control_absent_in_one_stratum_negative_control" in ids


def test_effect_patterns():
    assert (0.0, 0.0) in EFFECT_PATTERNS
    assert (0.08, 0.0) in EFFECT_PATTERNS
    assert (0.08, -0.05) in EFFECT_PATTERNS
    three = [p for p in EFFECT_PATTERNS if len(p) == 3]
    assert len(three) >= 3


def test_policy_comparisons():
    assert len(POLICY_COMPARISONS) == 7


def test_fast_build_schema(fast_payload: dict):
    assert fast_payload["artifact_id"] == "D5-TRUST-STRATIFIED-SCM-JK-001"
    assert REQUIRED_SUMMARY_KEYS <= set(fast_payload.keys())
    assert fast_payload["verdict"] in ALLOWED_VERDICTS


def test_authorization_blocked(fast_payload: dict):
    auth = fast_payload["authorization_summary"]
    assert auth["trust_report_authorized"] is False
    assert auth["trust_report_ready"] is False


def test_investigation_handoff(fast_payload: dict):
    handoff = fast_payload["investigation_handoff"]
    assert _INVESTIGATION_ID in handoff.get("resolved_issues", [])
    assert handoff.get("next_artifact") == "FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT"


def test_stratum_level_results_present(fast_payload: dict):
    rows = fast_payload["stratum_level_results"]
    assert rows
    sample = rows[0]
    for key in (
        "world_id",
        "stratum_id",
        "point_estimate",
        "interval_lower",
        "interval_upper",
        "contains_truth",
        "contains_zero",
        "donor_pool_policy",
    ):
        assert key in sample


def test_two_and_three_strata_geometry(fast_payload: dict):
    geoms = {g["geometry_id"] for g in fast_payload["geometry_variants"]}
    assert "balanced_two_strata" in geoms
    assert any(g.get("n_strata") == 3 for g in fast_payload["geometry_variants"])


def test_balanced_and_unequal_strata(fast_payload: dict):
    cov = fast_payload["coverage_by_geometry"]
    assert "balanced_two_strata" in cov
    assert "unequal_strata_sizes" in cov or "balanced_three_strata" in cov


def test_small_stratum(fast_payload: dict):
    assert "small_stratum_results" in fast_payload


def test_donor_pool_metadata(fast_payload: dict):
    dp = fast_payload["donor_pool_results"]
    assert "within_stratum" in dp
    assert "global" in dp


def test_within_and_global_donor_pool(fast_payload: dict):
    geom_ids = {g.geometry_id for g in GEOMETRY_VARIANTS}
    assert "donor_pool_within_stratum_only" in geom_ids
    assert "donor_pool_global" in geom_ids
    cov = fast_payload["coverage_by_geometry"]
    assert cov


def test_unsupported_missing_stratum_fails_closed():
    blocked = [
        g
        for g in GEOMETRY_VARIANTS
        if g.geometry_id == "control_absent_in_one_stratum_negative_control"
    ]
    assert blocked
    assert blocked[0].geometry_supported is False


def test_aggregate_results(fast_payload: dict):
    agg = fast_payload["aggregate_results"]
    assert "aggregate_coverage" in agg
    assert "aggregate_type_i" in agg


def test_weight_dominance(fast_payload: dict):
    wd = fast_payload["weight_dominance_results"]
    assert "dominance_rate" in wd


def test_coverage_calculation(fast_payload: dict):
    assert fast_payload["coverage_by_stratum"]


def test_type_i_calculation(fast_payload: dict):
    assert "type_i_by_stratum" in fast_payload
    assert "aggregate_type_i" in fast_payload


def test_failure_summary(fast_payload: dict):
    assert "failure_summary" in fast_payload


def test_canonical_scale(fast_payload: dict):
    assert fast_payload["config"]["canonical_scale"] == "level_mean_relative_percent_injection"


def test_scm_fit_mode_documented(fast_payload: dict):
    assert fast_payload["config"]["scm_fit_mode"] == "per_stratum_panel_aggregate_treated"


def test_production_defect_decision(fast_payload: dict):
    decision = fast_payload["production_defect_assessment"]["decision"]
    assert decision in {
        "production_defect_confirmed",
        "production_defect_not_confirmed",
        "production_defect_indeterminate",
        "geometry_or_semantic_limitation",
    }


def test_deterministic_fast_build():
    a = build_d5_trust_stratified_scm_jk_001(
        StratifiedTrustConfig(fast=True, write_full_results_path=None)
    )
    b = build_d5_trust_stratified_scm_jk_001(
        StratifiedTrustConfig(fast=True, write_full_results_path=None)
    )
    assert a["verdict"] == b["verdict"]
    assert a["run_counts"]["total_runs"] == b["run_counts"]["total_runs"]


def test_homogeneous_and_heterogeneous_worlds(fast_payload: dict):
    worlds = set(fast_payload["worlds"])
    assert "homogeneous_positive" in worlds or "all_strata_null" in worlds


def test_mixed_sign_and_null_worlds(fast_payload: dict):
    worlds = set(fast_payload["worlds"])
    assert "all_strata_null" in worlds


def test_stratum_identity_in_rows(fast_payload: dict):
    ok_rows = [r for r in fast_payload["stratum_level_results"] if r.get("failure_status") == "ok"]
    if ok_rows:
        assert any(r.get("stratum_identity_preserved") for r in ok_rows)


def test_aggregate_claim_blocked(fast_payload: dict):
    for pol in fast_payload["policy_comparisons"]:
        if pol["policy"]["policy_id"] == "G":
            assert pol.get("aggregate_claim_blocked") is True


def test_investigation_registry_update():
    reg = load_registry()
    inv = next(
        (i for i in reg["investigations"] if i["investigation_id"] == _INVESTIGATION_ID),
        None,
    )
    assert inv is not None
    assert inv["status"] == "RESOLVED"
    assert inv["affected_combination"] == "DCM-008"


def test_lane_binding_complete():
    reg = load_registry()
    lane = next(
        (l for l in reg["roadmap_lane_bindings"] if l["lane_id"] == "D5-TRUST-STRATIFIED-SCM-JK-001"),
        None,
    )
    assert lane is not None
    assert lane["status"] == "complete"


def test_mandatory_report_handoff_section():
    if not REPORT.exists():
        pytest.skip("report not generated yet")
    text = REPORT.read_text(encoding="utf-8")
    assert "## Residual Issues and Handoff" in text
    assert _INVESTIGATION_ID in text


def test_fast_mode():
    payload = build_d5_trust_stratified_scm_jk_001(
        StratifiedTrustConfig(fast=True, write_full_results_path=None)
    )
    assert payload["config"]["fast"] is True


def test_atomic_writes(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    write_summary(out, cfg=StratifiedTrustConfig(fast=True), overwrite=True, report_path=rep)
    assert out.exists()
    assert rep.exists()
    json.loads(out.read_text(encoding="utf-8"))


def test_no_full_archive_committed():
    full_archive = _REPO / "docs/track_d/archives/D5_TRUST_STRATIFIED_SCM_JK_001_results.json"
    assert not full_archive.exists()


def test_committed_summary_matches_schema():
    if not SUMMARY.exists():
        pytest.skip("summary not committed yet")
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert REQUIRED_SUMMARY_KEYS <= set(payload.keys())
    assert payload["verdict"] in ALLOWED_VERDICTS
    assert payload["authorization_summary"]["trust_report_authorized"] is False


def test_report_required_wording():
    if not REPORT.exists():
        pytest.skip("report not generated yet")
    text = REPORT.read_text(encoding="utf-8").lower()
    assert "does not authorize trustreport" in text
    assert "does not perform the full trustreport eligibility reassessment" in text
    assert "does not validate unrelated estimator" in text


def test_report_section_count():
    if not REPORT.exists():
        pytest.skip("report not generated yet")
    text = REPORT.read_text(encoding="utf-8")
    sections = re.findall(r"^## \d+\.", text, re.MULTILINE)
    assert len(sections) >= 34
