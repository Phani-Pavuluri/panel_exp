"""D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_inf_augsynth_conformal_failure_001 import (
    COMPARISON_ARMS,
    D5InfAugsynthConformalFailure001Config,
    FAILURE_MECHANISMS,
    PRIMARY_ARM,
    WORLD_REGISTRY_003,
    Ascm003WorldSpec,
    build_d5_inf_augsynth_conformal_failure_001,
    write_artifact,
    write_report,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001_results.json"
)

FAST_WORLDS = (
    Ascm003WorldSpec(
        "W0_baseline_reference",
        "baseline",
        "scm_low_signal",
        effect_grid=(0.0, 0.08),
    ),
    Ascm003WorldSpec(
        "W2_weak_scm_fit_inside_hull",
        "weak inside",
        "scm_trend_mismatch",
        fit_class="weak_fit",
        effect_grid=(0.0, 0.08),
    ),
    Ascm003WorldSpec(
        "W8_post_period_shock",
        "post shock",
        "scm_structural_break",
        fit_class="post_shock",
        effect_grid=(0.0, 0.08),
    ),
)


@pytest.fixture(scope="module")
def cvxpy_available() -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip(cvxpy_osqp_skip_reason())


def _fast_cfg() -> D5InfAugsynthConformalFailure001Config:
    return D5InfAugsynthConformalFailure001Config(n_mc=1, worlds=FAST_WORLDS)


class TestD5InfAugsynthConformalFailure001:
    def test_primary_arm_and_comparison_set(self) -> None:
        assert PRIMARY_ARM == "augsynth_cvxpy_conformal"
        assert PRIMARY_ARM in COMPARISON_ARMS
        assert len(COMPARISON_ARMS) == 4

    def test_build_structure(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_conformal_failure_001(_fast_cfg())
        assert payload["artifact_id"] == "D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001"
        assert payload["governance"]["no_promotion"] is True
        assert payload["governance"]["conformal_remains_diagnostic_restricted"] is True
        assert payload["promotion_audit_eligible"] is False
        assert "conformal_semantics" in payload

    def test_prior_evidence(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_conformal_failure_001(_fast_cfg())
        ids = {p["artifact_id"] for p in payload["prior_evidence"]}
        assert "D5-INST-AUGSYNTH-ASCM-003" in ids
        assert "D5-INF-AUGSYNTH-JK-CALIBRATION-001" in ids

    def test_replicate_has_all_arms(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_conformal_failure_001(_fast_cfg())
        rep = payload["replicates"][0]
        assert set(rep["instruments"].keys()) == set(COMPARISON_ARMS)
        cf = rep["instruments"]["augsynth_cvxpy_conformal"][0.0]
        assert "degenerate_interval" in cf
        assert "null_interval_exclusion_fpr" in cf

    def test_failure_mechanisms_block(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_conformal_failure_001(_fast_cfg())
        mech = payload["failure_mechanisms"]
        assert "likely_mechanisms" in mech
        assert set(mech["mechanism_scores"].keys()) == set(FAILURE_MECHANISMS)

    def test_failure_strata(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_conformal_failure_001(_fast_cfg())
        strata = payload["failure_strata"]["at_null"]
        assert "prefit" in strata
        assert "post_shock" in strata
        assert "method_disagreement" in strata

    def test_arm_comparison(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_conformal_failure_001(_fast_cfg())
        comp = payload["arm_comparison"]
        assert "severe_null_fpr_worlds" in comp
        assert "concerning_null_fpr_worlds" in comp

    def test_verdict_literal(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_conformal_failure_001(_fast_cfg())
        allowed = {
            "conformal_remains_restricted",
            "conformal_research_repair_candidate",
            "conformal_blocked_pending_new_design",
            "conformal_safe_only_under_narrow_diagnostics",
            "conformal_inconclusive_low_mc",
        }
        assert payload["overall_verdict"] in allowed

    def test_world_registry_count(self) -> None:
        assert len(WORLD_REGISTRY_003) >= 19


def test_write_artifact_and_report(tmp_path: Path, cvxpy_available: None) -> None:
    out = write_artifact(tmp_path / "cffail.json", cfg=_fast_cfg())
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["artifact_id"] == "D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001"
    rep = write_report(results_path=out, report_path=tmp_path / "report.md")
    text = rep.read_text(encoding="utf-8")
    assert "## 1. Purpose" in text
    assert "## 15. Next step" in text
    assert "## 11. Likely failure mechanisms" in text


def test_committed_artifact() -> None:
    if not ARTIFACT.is_file():
        pytest.skip("Run D5-INF-AUGSYNTH-CONFORMAL-FAILURE-001 generator")
    loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert loaded["governance"]["no_promotion"] is True
    assert loaded["overall_verdict"] in {
        "conformal_remains_restricted",
        "conformal_research_repair_candidate",
        "conformal_blocked_pending_new_design",
        "conformal_safe_only_under_narrow_diagnostics",
        "conformal_inconclusive_low_mc",
    }
