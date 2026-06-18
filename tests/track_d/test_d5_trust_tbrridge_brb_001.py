"""Tests for D5-TRUST-TBRRIDGE-BRB-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_trust_tbrridge_brb_001 import (
    DIAGNOSTIC_WORLDS,
    BrbTrustConfig,
    POLICY_COMPARISONS,
    build_d5_trust_tbrridge_brb_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/D5_TRUST_TBRRIDGE_BRB_001_summary.json"
REPORT = _REPO / "docs/track_d/D5_TRUST_TBRRIDGE_BRB_001_REPORT.md"

ALLOWED_VERDICTS = frozenset(
    {
        "tbrridge_brb_restricted_causal_interval_candidate",
        "tbrridge_brb_prefit_gated_restricted",
        "tbrridge_brb_serial_dependence_restricted",
        "tbrridge_brb_diagnostic_only",
        "tbrridge_brb_not_interval_eligible",
        "tbrridge_brb_production_defect_confirmed",
        "tbrridge_brb_remediation_inconclusive",
        "tbrridge_brb_remediation_failed",
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
        "block_lengths",
        "run_counts",
        "point_estimate_results",
        "interval_results",
        "coverage_by_effect",
        "coverage_by_world",
        "coverage_by_block_length",
        "coverage_by_serial_dependence",
        "bias_decomposition",
        "variance_decomposition",
        "bootstrap_centering_diagnostics",
        "prefit_relationships",
        "ridge_relationships",
        "failure_summary",
        "policy_comparisons",
        "production_defect_assessment",
        "semantic_classification",
        "trustreport_eligibility_implications",
        "authorization_summary",
        "limitations",
        "verdict",
    }
)

FORBIDDEN_REPORT = [
    r"\bis production-ready\b",
    r"\btrust_report_authorized.*true\b",
    r"\beligible_for_promotion\b",
]


@pytest.fixture(scope="module")
def fast_payload() -> dict:
    return build_d5_trust_tbrridge_brb_001(BrbTrustConfig(fast=True, write_full_results_path=None))


def test_diagnostic_world_count():
    assert len(DIAGNOSTIC_WORLDS) >= 18


def test_policy_comparisons_present():
    assert len(POLICY_COMPARISONS) == 7
    assert {p["policy_id"] for p in POLICY_COMPARISONS} == {"A", "B", "C", "D", "E", "F", "G"}


def test_fast_build_schema(fast_payload: dict):
    assert fast_payload["artifact_id"] == "D5-TRUST-TBRRIDGE-BRB-001"
    assert REQUIRED_SUMMARY_KEYS <= set(fast_payload.keys())
    assert fast_payload["verdict"] in ALLOWED_VERDICTS


def test_authorization_blocked(fast_payload: dict):
    auth = fast_payload["authorization_summary"]
    assert auth["trust_report_authorized"] is False
    assert auth["trust_report_ready"] is False
    assert auth.get("trust_report_authorized_count", 0) == 0


def test_null_positive_coverage_separated(fast_payload: dict):
    cov = fast_payload["coverage_by_effect"]
    assert "0.0" in cov
    null = cov["0.0"]
    assert "null_coverage" in null
    assert "positive_coverage" in null


def test_block_length_sweep_recorded(fast_payload: dict):
    assert len(fast_payload["coverage_by_block_length"]) >= 1


def test_production_defect_decision(fast_payload: dict):
    decision = fast_payload["production_defect_assessment"]["decision"]
    assert decision in {
        "production_defect_confirmed",
        "production_defect_not_confirmed",
        "production_defect_indeterminate",
    }


def test_bootstrap_center_recorded(fast_payload: dict):
    diag = fast_payload["bootstrap_centering_diagnostics"]
    assert "mean_bootstrap_center_minus_point" in diag


def test_canonical_scale_level(fast_payload: dict):
    assert fast_payload["config"]["canonical_scale"] == "level_mean_relative_percent_injection"


def test_write_summary_atomic(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    write_summary(
        out,
        cfg=BrbTrustConfig(fast=True, write_full_results_path=None),
        overwrite=True,
        report_path=rep,
    )
    assert out.exists()
    assert rep.exists()
    payload = json.loads(out.read_text())
    assert payload["authorization_summary"]["trust_report_authorized"] is False


def test_committed_summary_if_present():
    if not SUMMARY.exists():
        pytest.skip("committed summary not generated yet")
    payload = json.loads(SUMMARY.read_text())
    assert REQUIRED_SUMMARY_KEYS <= set(payload.keys())
    assert payload["verdict"] in ALLOWED_VERDICTS
    assert payload["authorization_summary"]["trust_report_authorized"] is False


def test_committed_report_wording():
    if not REPORT.exists():
        pytest.skip("committed report not generated yet")
    text = REPORT.read_text()
    assert "does not authorize TrustReport" in text
    for pat in FORBIDDEN_REPORT:
        assert not re.search(pat, text, re.I)
