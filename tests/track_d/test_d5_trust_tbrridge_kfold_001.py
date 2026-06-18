"""Tests for D5-TRUST-TBRRIDGE-KFOLD-001."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from panel_exp.governance.investigation_lifecycle_contract import load_registry
from panel_exp.validation.track_d_d5_trust_tbrridge_kfold_001 import (
    DIAGNOSTIC_WORLDS,
    FOLD_VARIANTS,
    KfoldTrustConfig,
    POLICY_COMPARISONS,
    build_d5_trust_tbrridge_kfold_001,
    write_summary,
)

_REPO = Path(__file__).resolve().parents[2]
SUMMARY = _REPO / "docs/track_d/archives/D5_TRUST_TBRRIDGE_KFOLD_001_summary.json"
REPORT = _REPO / "docs/track_d/D5_TRUST_TBRRIDGE_KFOLD_001_REPORT.md"

ALLOWED_VERDICTS = frozenset(
    {
        "tbrridge_kfold_directional_diagnostic_only",
        "tbrridge_kfold_time_ordered_restricted",
        "tbrridge_kfold_null_fpr_defect_confirmed",
        "tbrridge_kfold_not_causal_interval_eligible",
        "tbrridge_kfold_remediation_inconclusive",
        "tbrridge_kfold_remediation_failed",
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
        "fold_variants",
        "run_counts",
        "point_estimate_results",
        "fold_diagnostics",
        "coverage_by_effect",
        "coverage_by_world",
        "type_i_by_world",
        "type_i_by_fold_variant",
        "sign_accuracy",
        "leakage_diagnostics",
        "variance_decomposition",
        "prefit_relationships",
        "ridge_relationships",
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
    return build_d5_trust_tbrridge_kfold_001(KfoldTrustConfig(fast=True, write_full_results_path=None))


def test_diagnostic_world_count():
    assert len(DIAGNOSTIC_WORLDS) >= 18


def test_fold_variants_present():
    assert len(FOLD_VARIANTS) >= 3
    ids = {v.fold_type for v in FOLD_VARIANTS}
    assert "random_kfold" in ids
    assert "forward_chaining_time_series_kfold" in ids


def test_policy_comparisons():
    assert len(POLICY_COMPARISONS) == 6


def test_fast_build_schema(fast_payload: dict):
    assert fast_payload["artifact_id"] == "D5-TRUST-TBRRIDGE-KFOLD-001"
    assert REQUIRED_SUMMARY_KEYS <= set(fast_payload.keys())
    assert fast_payload["verdict"] in ALLOWED_VERDICTS


def test_authorization_blocked(fast_payload: dict):
    auth = fast_payload["authorization_summary"]
    assert auth["trust_report_authorized"] is False
    assert auth["trust_report_ready"] is False


def test_investigation_handoff(fast_payload: dict):
    handoff = fast_payload["investigation_handoff"]
    assert handoff.get("follow_up_issues") == ["INV-TBRRIDGE-KFOLD-NULL-FPR-001"]
    assert handoff.get("resolved_issues") == []
    assert handoff.get("terminal_dispositions") == []
    assert handoff.get("next_artifact") == "D5-TRUST-TBRRIDGE-PLACEBO-001"


def test_type_i_by_fold_variant(fast_payload: dict):
    by_fold = fast_payload["type_i_by_fold_variant"]
    assert "random_kfold" in by_fold or len(by_fold) >= 1


def test_null_non_null_separated(fast_payload: dict):
    cov = fast_payload["coverage_by_effect"]
    assert "0.0" in cov


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
    a = build_d5_trust_tbrridge_kfold_001(KfoldTrustConfig(fast=True, write_full_results_path=None))
    b = build_d5_trust_tbrridge_kfold_001(KfoldTrustConfig(fast=True, write_full_results_path=None))
    assert a["run_counts"]["total_runs"] == b["run_counts"]["total_runs"]
    assert a["verdict"] == b["verdict"]


def test_write_summary_atomic(tmp_path: Path):
    out = tmp_path / "summary.json"
    rep = tmp_path / "report.md"
    write_summary(
        out,
        cfg=KfoldTrustConfig(fast=True, write_full_results_path=None),
        overwrite=True,
        report_path=rep,
    )
    assert out.exists()
    assert rep.exists()
    assert "## Residual Issues and Handoff" in rep.read_text()
    payload = json.loads(out.read_text())
    assert payload["authorization_summary"]["trust_report_authorized"] is False


def test_no_large_archive_committed():
    archives = _REPO / "docs/track_d/archives"
    if not archives.exists():
        pytest.skip("no archives dir")
    large = [p for p in archives.glob("D5_TRUST_TBRRIDGE_KFOLD*") if p.stat().st_size > 90 * 1024 * 1024]
    assert not large


def test_registry_kfold_investigation_exists():
    reg = load_registry()
    inv = next(i for i in reg["investigations"] if i["investigation_id"] == "INV-TBRRIDGE-KFOLD-NULL-FPR-001")
    assert inv["status"] == "RESOLVED"
    assert inv["evidence"].get("d5_trust_characterization") == "D5-TRUST-TBRRIDGE-KFOLD-001"


def test_report_handoff_section_when_written(tmp_path: Path):
    rep = tmp_path / "report.md"
    write_summary(
        tmp_path / "s.json",
        cfg=KfoldTrustConfig(fast=True, write_full_results_path=None),
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


@pytest.mark.parametrize("world_id", ["clean_null", "clean_positive_effect", "clean_negative_effect"])
def test_core_worlds_in_full_registry(world_id: str):
    assert any(w.world_id == world_id for w in DIAGNOSTIC_WORLDS)
