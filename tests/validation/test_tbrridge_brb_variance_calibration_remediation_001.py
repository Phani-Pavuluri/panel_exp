"""Tests for TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.validation.tbrridge_brb_variance_calibration_remediation_001 import (
    CANDIDATE_POLICIES,
    INPUT_ARTIFACTS,
    PASS_FAIL_GATES,
    RemediationConfig,
    build_tbrridge_brb_variance_calibration_remediation_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001_summary.json"
REPORT = _REPO / "docs/track_d/TBRRIDGE_BRB_VARIANCE_CALIBRATION_REMEDIATION_001_REPORT.md"

ALLOWED_VERDICTS = frozenset(
    {
        "tbrridge_brb_variance_remediated_restricted",
        "tbrridge_brb_variance_remediation_candidate_only",
        "tbrridge_brb_variance_remediation_failed",
        "tbrridge_brb_diagnostic_only",
        "tbrridge_brb_ineligible",
        "tbrridge_brb_additional_remediation_required",
    }
)

REQUIRED_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_version",
        "generated_at",
        "git_commit",
        "input_artifacts",
        "config",
        "candidate_policies",
        "worlds",
        "run_counts",
        "baseline_results",
        "candidate_results",
        "candidate_comparison",
        "root_cause_analysis",
        "pass_fail_gates",
        "selected_policy",
        "production_changes",
        "coverage_results",
        "type_i_results",
        "power_results",
        "sign_accuracy_results",
        "calibration_ratio_results",
        "interval_width_results",
        "failure_summary",
        "semantic_classification",
        "trustreport_eligibility_implications",
        "authorization_summary",
        "investigation_handoff",
        "limitations",
        "verdict",
        "next_artifact",
    }
)


@pytest.fixture(scope="module")
def fast_payload() -> dict:
    return build_tbrridge_brb_variance_calibration_remediation_001(
        RemediationConfig(fast=True, candidates=("baseline_corrected_brb", "variance_scaled_brb"))
    )


def test_required_input_artifacts_exist():
    for rel in INPUT_ARTIFACTS.values():
        assert (_REPO / rel).is_file()


def test_fast_build_schema(fast_payload: dict):
    assert fast_payload["artifact_id"] == "TBRRIDGE-BRB-VARIANCE-CALIBRATION-REMEDIATION-001"
    assert REQUIRED_KEYS <= set(fast_payload.keys())


def test_authorization_invariant(fast_payload: dict):
    auth = fast_payload["authorization_summary"]
    assert auth["trust_report_authorized"] is False
    assert auth["trust_report_ready"] is False


def test_verdict_taxonomy(fast_payload: dict):
    assert fast_payload["verdict"] in ALLOWED_VERDICTS


def test_baseline_centering_preserved(fast_payload: dict):
    baseline = fast_payload["baseline_results"]
    gap = baseline.get("interval_center_gap")
    assert gap is not None and gap < PASS_FAIL_GATES["interval_center_gap_abs_max"]


def test_candidate_policies_include_baseline_and_variance_scaled():
    assert "baseline_corrected_brb" in CANDIDATE_POLICIES
    assert CANDIDATE_POLICIES["variance_scaled_brb"]["variance_calibration_policy"] == "residual_scaled"


def test_restricted_worlds_not_implemented():
    assert CANDIDATE_POLICIES["restricted_worlds_only_brb"]["implemented"] is False


def test_deterministic_fast_build():
    a = build_tbrridge_brb_variance_calibration_remediation_001(
        RemediationConfig(fast=True, candidates=("baseline_corrected_brb",))
    )
    b = build_tbrridge_brb_variance_calibration_remediation_001(
        RemediationConfig(fast=True, candidates=("baseline_corrected_brb",))
    )
    assert a["verdict"] == b["verdict"]
    assert a["baseline_results"]["n_runs"] == b["baseline_results"]["n_runs"]


def test_write_summary_atomic(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    write_summary(out, overwrite=True, report_path=rep, fast=True, candidates=("baseline_corrected_brb",))
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["authorization_summary"]["trust_report_authorized"] is False


def test_committed_summary_if_present():
    if not SUMMARY.exists():
        pytest.skip("summary not committed")
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert REQUIRED_KEYS <= set(data.keys())
    assert data["authorization_summary"]["trust_report_authorized"] is False


def test_report_required_wording():
    if not REPORT.exists():
        pytest.skip("report not committed")
    text = REPORT.read_text(encoding="utf-8").lower()
    assert "does not authorize trustreport" in text
    assert "does not perform the full trustreport eligibility reassessment" in text


def test_no_trustreport_true_in_summary(fast_payload: dict):
    blob = json.dumps(fast_payload)
    assert not re.search(r'"trust_report_authorized"\s*:\s*true', blob, re.I)


def test_investigation_handoff_has_next_artifact(fast_payload: dict):
    assert fast_payload["investigation_handoff"].get("next_artifact")


def test_gate_evaluation_structure(fast_payload: dict):
    gate = fast_payload["baseline_results"].get("gate_evaluation") or {}
    assert "gates" in gate
    assert "pass_count" in gate
