"""Tests for D5-TRUST-TBRRIDGE-PLACEBO-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import load_registry
from panel_exp.validation.track_d_d5_trust_tbrridge_placebo_001 import (
    DIAGNOSTIC_WORLDS,
    GEOMETRY_VARIANTS,
    POLICY_COMPARISONS,
    _INVESTIGATION_ID,
    PlaceboTrustConfig,
    build_d5_trust_tbrridge_placebo_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/D5_TRUST_TBRRIDGE_PLACEBO_001_summary.json"
REPORT = _REPO / "docs/track_d/D5_TRUST_TBRRIDGE_PLACEBO_001_REPORT.md"

ALLOWED_VERDICTS = frozenset(
    {
        "tbrridge_placebo_null_monitor_only",
        "tbrridge_placebo_falsification_diagnostic_only",
        "tbrridge_placebo_single_treated_restricted",
        "tbrridge_placebo_not_causal_interval_eligible",
        "tbrridge_placebo_production_defect_confirmed",
        "tbrridge_placebo_remediation_inconclusive",
        "tbrridge_placebo_remediation_failed",
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
        "effect_sizes",
        "geometry_variants",
        "run_counts",
        "point_estimate_results",
        "placebo_distribution_results",
        "placebo_rank_calibration",
        "p_value_calibration",
        "type_i_by_world",
        "power_by_effect",
        "results_by_geometry",
        "results_by_control_count",
        "results_by_prefit",
        "results_by_serial_dependence",
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
    return build_d5_trust_tbrridge_placebo_001(PlaceboTrustConfig(fast=True, write_full_results_path=None))


def test_diagnostic_world_count():
    assert len(DIAGNOSTIC_WORLDS) >= 18


def test_geometry_variants_present():
    assert len(GEOMETRY_VARIANTS) >= 4
    ids = {g.geometry_id for g in GEOMETRY_VARIANTS}
    assert "single_treated_unit" in ids
    assert "multiple_treated_units" in ids


def test_policy_comparisons():
    assert len(POLICY_COMPARISONS) == 6


def test_fast_build_schema(fast_payload: dict):
    assert fast_payload["artifact_id"] == "D5-TRUST-TBRRIDGE-PLACEBO-001"
    assert REQUIRED_SUMMARY_KEYS <= set(fast_payload.keys())
    assert fast_payload["verdict"] in ALLOWED_VERDICTS


def test_authorization_blocked(fast_payload: dict):
    auth = fast_payload["authorization_summary"]
    assert auth["trust_report_authorized"] is False
    assert auth["trust_report_ready"] is False


def test_investigation_handoff(fast_payload: dict):
    handoff = fast_payload["investigation_handoff"]
    assert handoff.get("follow_up_issues") == [_INVESTIGATION_ID]
    assert handoff.get("resolved_issues") == []
    assert handoff.get("terminal_dispositions") == []
    assert handoff.get("next_artifact") == "DCM-005-TRUSTREPORT-ELIGIBILITY-REASSESSMENT-001"


def test_placebo_rank_and_pvalue_present(fast_payload: dict):
    assert "placebo_rank_calibration" in fast_payload
    assert "p_value_calibration" in fast_payload
    assert fast_payload["placebo_rank_calibration"].get("uniform_reference") == 0.5


def test_null_non_null_separated(fast_payload: dict):
    assert "0.0" in fast_payload["power_by_effect"]


def test_canonical_scale(fast_payload: dict):
    assert fast_payload["config"]["canonical_scale"] == "level_mean_relative_percent_injection"


def test_production_defect_decision(fast_payload: dict):
    decision = fast_payload["production_defect_assessment"]["decision"]
    assert decision in {
        "production_defect_confirmed",
        "production_defect_not_confirmed",
        "production_defect_indeterminate",
        "method_unsuitable_for_causal_interval",
    }


def test_deterministic_fast_build():
    a = build_d5_trust_tbrridge_placebo_001(PlaceboTrustConfig(fast=True, write_full_results_path=None))
    b = build_d5_trust_tbrridge_placebo_001(PlaceboTrustConfig(fast=True, write_full_results_path=None))
    assert a["run_counts"]["total_runs"] == b["run_counts"]["total_runs"]
    assert a["verdict"] == b["verdict"]


def test_write_summary_atomic(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    write_summary(
        out,
        cfg=PlaceboTrustConfig(fast=True, write_full_results_path=None),
        overwrite=True,
        report_path=rep,
    )
    assert out.exists()
    assert rep.exists()
    text = rep.read_text()
    assert "## Residual Issues and Handoff" in text
    assert "null-reference and falsification path" in text
    payload = json.loads(out.read_text())
    assert payload["authorization_summary"]["trust_report_authorized"] is False


def test_no_large_archive_committed():
    archives = _REPO / "docs/track_d/archives"
    if not archives.exists():
        pytest.skip("no archives dir")
    large = [p for p in archives.glob("D5_TRUST_TBRRIDGE_PLACEBO*") if p.stat().st_size > 90 * 1024 * 1024]
    assert not large


def test_committed_summary_schema_when_present():
    if not SUMMARY.is_file():
        pytest.skip("summary not committed yet")
    payload = json.loads(SUMMARY.read_text())
    assert REQUIRED_SUMMARY_KEYS <= set(payload.keys())
    assert payload["verdict"] in ALLOWED_VERDICTS


def test_registry_placebo_investigation_exists():
    reg = load_registry()
    inv = next(i for i in reg["investigations"] if i["investigation_id"] == _INVESTIGATION_ID)
    assert inv["status"] == "OPEN"
    assert inv["evidence"].get("d5_trust_characterization") == "D5-TRUST-TBRRIDGE-PLACEBO-001"


def test_dcm005_binding_consumes_placebo_investigation():
    reg = load_registry()
    binding = next(b for b in reg["roadmap_lane_bindings"] if b["lane_id"] == "DCM-005-ELIGIBILITY-REASSESSMENT")
    assert binding["must_consume_before_close"] is True
    assert _INVESTIGATION_ID in binding["open_investigations"]


def test_report_handoff_section_when_written(tmp_path: Path):
    rep = tmp_path / "report.md"
    write_summary(
        tmp_path / "s.json",
        cfg=PlaceboTrustConfig(fast=True, write_full_results_path=None),
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


def test_forbidden_trust_authorization_in_summary(fast_payload: dict):
    blob = json.dumps(fast_payload)
    assert not re.search(r'"trust_report_authorized"\s*:\s*true', blob, re.I)


def test_semantic_classification_blocks_causal_interval(fast_payload: dict):
    sem = fast_payload["semantic_classification"]
    assert "restricted_causal_interval" in sem.get("unsupported_roles", [])
    assert "null_monitor" in sem.get("supported_roles", [])


def test_fast_mode():
    payload = build_d5_trust_tbrridge_placebo_001(PlaceboTrustConfig(fast=True, write_full_results_path=None))
    assert payload["config"]["fast"] is True
    assert payload["run_counts"]["total_runs"] < 100


@pytest.mark.parametrize("world_id", ["clean_null", "clean_positive_effect", "clean_negative_effect"])
def test_core_worlds_in_full_registry(world_id: str):
    assert any(w.world_id == world_id for w in DIAGNOSTIC_WORLDS)
