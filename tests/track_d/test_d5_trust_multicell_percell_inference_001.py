"""Tests for D5-TRUST-MULTICELL-PERCELL-INFERENCE-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import load_registry
from panel_exp.validation.track_d_d5_trust_multicell_percell_inference_001 import (
    EFFECT_PATTERNS,
    GEOMETRY_VARIANTS,
    POLICY_COMPARISONS,
    TRUST_WORLDS,
    _INVESTIGATION_ID,
    MulticellTrustConfig,
    build_d5_trust_multicell_percell_inference_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/D5_TRUST_MULTICELL_PERCELL_INFERENCE_001_summary.json"
REPORT = _REPO / "docs/track_d/D5_TRUST_MULTICELL_PERCELL_INFERENCE_001_REPORT.md"

ALLOWED_VERDICTS = frozenset(
    {
        "multicell_percell_eligible_with_restrictions",
        "multicell_percell_disjoint_controls_only",
        "multicell_percell_shared_control_restricted",
        "multicell_percell_multiplicity_unresolved",
        "multicell_percell_diagnostic_only",
        "multicell_percell_ineligible",
        "multicell_percell_remediation_inconclusive",
        "multicell_percell_remediation_failed",
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
        "cell_level_results",
        "cross_cell_dependence",
        "coverage_by_cell",
        "coverage_by_geometry",
        "type_i_by_cell",
        "familywise_type_i",
        "simultaneous_coverage",
        "multiplicity_comparisons",
        "shared_control_results",
        "pooled_block_verification",
        "failure_summary",
        "policy_comparisons",
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
    return build_d5_trust_multicell_percell_inference_001(
        MulticellTrustConfig(fast=True, write_full_results_path=None)
    )


def test_world_count():
    assert len(TRUST_WORLDS) >= 18


def test_geometry_variants_present():
    ids = {g.geometry_id for g in GEOMETRY_VARIANTS}
    assert "two_cells_disjoint_controls" in ids
    assert "two_cells_shared_controls" in ids
    assert "three_cells_shared_controls" in ids
    assert "partially_overlapping_controls" in ids
    assert "pooled_multi_cell_negative_control" in ids


def test_effect_patterns():
    assert (0.0, 0.0) in EFFECT_PATTERNS
    assert (0.08, 0.0) in EFFECT_PATTERNS
    assert (0.08, -0.05) in EFFECT_PATTERNS
    three_cell = [p for p in EFFECT_PATTERNS if len(p) == 3]
    assert len(three_cell) >= 3


def test_policy_comparisons():
    assert len(POLICY_COMPARISONS) == 7


def test_fast_build_schema(fast_payload: dict):
    assert fast_payload["artifact_id"] == "D5-TRUST-MULTICELL-PERCELL-INFERENCE-001"
    assert REQUIRED_SUMMARY_KEYS <= set(fast_payload.keys())
    assert fast_payload["verdict"] in ALLOWED_VERDICTS


def test_authorization_blocked(fast_payload: dict):
    auth = fast_payload["authorization_summary"]
    assert auth["trust_report_authorized"] is False
    assert auth["trust_report_ready"] is False


def test_investigation_handoff(fast_payload: dict):
    handoff = fast_payload["investigation_handoff"]
    assert _INVESTIGATION_ID in handoff.get("resolved_issues", [])
    assert handoff.get("next_artifact") == "D5-TRUST-STRATIFIED-SCM-JK-001"
    assert handoff.get("terminal_dispositions") == [_INVESTIGATION_ID]


def test_cell_level_results_present(fast_payload: dict):
    rows = fast_payload["cell_level_results"]
    assert rows
    sample = rows[0]
    for key in (
        "world_id",
        "cell_id",
        "point_estimate",
        "interval_lower",
        "interval_upper",
        "contains_truth",
        "contains_zero",
    ):
        assert key in sample


def test_two_and_three_cell_geometry(fast_payload: dict):
    geoms = {g["geometry_id"] for g in fast_payload["geometry_variants"]}
    assert "two_cells_shared_controls" in geoms
    assert any(g.get("n_cells") == 3 for g in fast_payload["geometry_variants"])


def test_disjoint_and_shared_controls(fast_payload: dict):
    cov = fast_payload["coverage_by_geometry"]
    assert "two_cells_disjoint_controls" in cov
    assert "two_cells_shared_controls" in cov


def test_pooled_block_verification(fast_payload: dict):
    pool = fast_payload["pooled_block_verification"]
    assert pool.get("all_blocked") is True
    assert pool.get("effect_emitted", 1) == 0


def test_multiplicity_comparisons(fast_payload: dict):
    mc = fast_payload["multiplicity_comparisons"]
    assert mc.get("proxy_comparison_valid") is False
    assert mc.get("bonferroni_proxy") is None
    assert mc.get("holm_proxy") is None
    assert "unadjusted_familywise_type_i" in mc
    audit = mc.get("calibration_audit") or {}
    assert audit.get("per_cell_p_values_available") is False
    assert audit.get("adjusted_intervals_reconstructed") is False
    assert "does not expose compatible per-cell p-values" in mc.get("disclaimer", "")


def test_multiplicity_proxy_disclaimer_in_limitations(fast_payload: dict):
    lim = " ".join(fast_payload.get("limitations", [])).lower()
    assert "bonferroni/holm proxy" in lim or "not a valid calibration test" in lim


def test_shared_control_results(fast_payload: dict):
    sc = fast_payload["shared_control_results"]
    assert "shared_geometry" in sc
    assert "disjoint_geometry" in sc


def test_canonical_scale(fast_payload: dict):
    assert fast_payload["config"]["canonical_scale"] == "level_mean_relative_percent_injection"


def test_production_defect_decision(fast_payload: dict):
    decision = fast_payload["production_defect_assessment"]["decision"]
    assert decision in {
        "production_defect_confirmed",
        "production_defect_not_confirmed",
        "production_defect_indeterminate",
        "geometry_or_semantic_limitation",
    }


def test_deterministic_fast_build():
    a = build_d5_trust_multicell_percell_inference_001(
        MulticellTrustConfig(fast=True, write_full_results_path=None)
    )
    b = build_d5_trust_multicell_percell_inference_001(
        MulticellTrustConfig(fast=True, write_full_results_path=None)
    )
    assert a["run_counts"]["total_runs"] == b["run_counts"]["total_runs"]
    assert a["verdict"] == b["verdict"]


def test_null_and_non_null_cells(fast_payload: dict):
    worlds = set(fast_payload["worlds"])
    assert "all_cell_null" in worlds
    assert "one_cell_positive_others_null" in worlds


def test_mixed_sign_effects(fast_payload: dict):
    assert any(list(p) == [0.08, -0.05] for p in fast_payload["effect_patterns"])


def test_familywise_type_i_present(fast_payload: dict):
    assert "familywise_type_i" in fast_payload
    assert "simultaneous_coverage" in fast_payload


def test_write_summary_atomic(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    write_summary(
        out,
        cfg=MulticellTrustConfig(fast=True, write_full_results_path=None),
        overwrite=True,
        report_path=rep,
    )
    assert out.exists()
    assert rep.exists()
    text = rep.read_text()
    assert "## Residual Issues and Handoff" in text
    assert "per-cell inference for multi-cell designs" in text
    payload = json.loads(out.read_text())
    assert payload["authorization_summary"]["trust_report_authorized"] is False


def test_no_large_archive_committed():
    archives = _REPO / "docs/track_d/archives"
    if not archives.exists():
        pytest.skip("no archives dir")
    large = [
        p
        for p in archives.glob("D5_TRUST_MULTICELL_PERCELL*")
        if p.stat().st_size > 90 * 1024 * 1024
    ]
    assert not large


def test_committed_summary_schema_when_present():
    if not SUMMARY.is_file():
        pytest.skip("summary not committed yet")
    payload = json.loads(SUMMARY.read_text())
    assert REQUIRED_SUMMARY_KEYS <= set(payload.keys())
    assert payload["verdict"] in ALLOWED_VERDICTS


def test_registry_multicell_investigation_when_updated():
    reg = load_registry()
    inv = next(
        (i for i in reg["investigations"] if i["investigation_id"] == _INVESTIGATION_ID),
        None,
    )
    if inv is None:
        pytest.skip("investigation not in registry")
    if SUMMARY.is_file():
        assert inv["status"] == "RESOLVED"
        assert inv.get("resolution_artifact") == "D5-TRUST-MULTICELL-PERCELL-INFERENCE-001"


def test_report_handoff_section_when_written(tmp_path: Path):
    rep = tmp_path / "report.md"
    write_summary(
        tmp_path / "s.json",
        cfg=MulticellTrustConfig(fast=True, write_full_results_path=None),
        overwrite=True,
        report_path=rep,
    )
    text = rep.read_text()
    for subsection in (
        "Resolved in this artifact",
        "New investigations opened",
        "Next artifact",
    ):
        assert subsection in text


def test_no_trust_report_true_in_artifact():
    text = (_REPO / "panel_exp/validation/track_d_d5_trust_multicell_percell_inference_001.py").read_text()
    assert "trust_report_authorized'] = True" not in text
    assert "trust_report_ready'] = True" not in text


def test_limitations_wording(fast_payload: dict):
    lim = " ".join(fast_payload.get("limitations", [])).lower()
    assert "does not authorize trustreport" in lim
    assert "pooled multi-cell" in lim


def test_control_overlap_metadata(fast_payload: dict):
    rows = fast_payload["cell_level_results"]
    assert any("control_overlap_fraction" in r for r in rows)


def test_small_cell_geometry(fast_payload: dict):
    assert "small_cell" in fast_payload["coverage_by_geometry"]


def test_fast_mode(fast_payload: dict):
    assert fast_payload["config"]["fast"] is True


def test_verdict_taxonomy(fast_payload: dict):
    assert fast_payload["verdict"] in ALLOWED_VERDICTS
