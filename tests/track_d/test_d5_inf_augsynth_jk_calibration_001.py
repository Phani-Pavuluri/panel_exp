"""D5-INF-AUGSYNTH-JK-CALIBRATION-001 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_inf_augsynth_jk_calibration_001 import (
    D5InfAugsynthJkCalibration001Config,
    JK_ARMS,
    WORLD_REGISTRY_003,
    Ascm003WorldSpec,
    build_d5_inf_augsynth_jk_calibration_001,
    write_artifact,
    write_report,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INF_AUGSYNTH_JK_CALIBRATION_001_results.json"
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
        weak_fit_severity="moderate",
        effect_grid=(0.0, 0.08),
    ),
    Ascm003WorldSpec(
        "W3_weak_scm_fit_outside_hull",
        "weak outside",
        "scm_low_signal",
        scenario_overrides={"cross_geo_correlation": 0.05, "noise_scale": 3.2},
        fit_class="weak_fit_outside_hull",
        weak_fit_severity="moderate",
        effect_grid=(0.0, 0.08),
    ),
)


@pytest.fixture(scope="module")
def cvxpy_available() -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip(cvxpy_osqp_skip_reason())


def _fast_cfg() -> D5InfAugsynthJkCalibration001Config:
    return D5InfAugsynthJkCalibration001Config(n_mc=1, worlds=FAST_WORLDS)


class TestD5InfAugsynthJkCalibration001:
    def test_jk_arms_only(self) -> None:
        assert JK_ARMS == (
            "a26_scm_unit_jackknife",
            "augsynth_cvxpy_unit_jackknife",
        )

    def test_build_structure(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_jk_calibration_001(_fast_cfg())
        assert payload["artifact_id"] == "D5-INF-AUGSYNTH-JK-CALIBRATION-001"
        assert payload["governance"]["no_promotion"] is True
        assert payload["governance"]["no_governed_uncertainty_allowlist_change"] is True
        assert payload["governance"]["augsynth_jk_not_governed_uncertainty"] is True
        assert payload["promotion_audit_eligible"] is False

    def test_prior_evidence_from_ascm003(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_jk_calibration_001(_fast_cfg())
        assert payload["prior_evidence"]["artifact_id"] == "D5-INST-AUGSYNTH-ASCM-003"
        assert payload["prior_evidence"]["verdict"] == "promising_needs_inference_calibration"

    def test_replicate_jk_fields(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_jk_calibration_001(_fast_cfg())
        rep = payload["replicates"][0]
        assert set(rep["instruments"].keys()) == set(JK_ARMS)
        aug = rep["instruments"]["augsynth_cvxpy_unit_jackknife"][0.0]
        assert "null_interval_exclusion_fpr" in aug
        assert "covers_injected_effect" in aug
        assert "false_conf_narrow_poor_prefit" in aug

    def test_null_and_effect_summaries(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_jk_calibration_001(_fast_cfg())
        assert "null_fpr_summary" in payload
        assert "effect_coverage_summary" in payload
        assert "interval_width_summary" in payload
        assert "false_confidence_summary" in payload

    def test_diagnostic_strata(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_jk_calibration_001(_fast_cfg())
        strata = payload["diagnostic_strata"]
        assert "at_null" in strata
        assert "prefit" in strata["at_null"]
        assert "hull" in strata["at_null"]

    def test_a26_comparison_block(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_jk_calibration_001(_fast_cfg())
        comp = payload["a26_vs_aug_jk_comparison"]
        assert "comparisons" in comp
        assert "unsafe_aug_null_fpr_worlds" in comp

    def test_verdict_literal(self, cvxpy_available: None) -> None:
        payload = build_d5_inf_augsynth_jk_calibration_001(_fast_cfg())
        allowed = {
            "jk_not_ready",
            "jk_safe_but_conservative",
            "jk_promising_needs_more_oc",
            "jk_unsafe_under_diagnostics",
            "jk_calibration_candidate_future_only",
        }
        assert payload["overall_verdict"] in allowed

    def test_world_registry_matches_ascm003_count(self) -> None:
        assert len(WORLD_REGISTRY_003) >= 19


def test_write_artifact_and_report(tmp_path: Path, cvxpy_available: None) -> None:
    out = write_artifact(tmp_path / "jkcal.json", cfg=_fast_cfg())
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["artifact_id"] == "D5-INF-AUGSYNTH-JK-CALIBRATION-001"
    rep = write_report(results_path=out, report_path=tmp_path / "report.md")
    text = rep.read_text(encoding="utf-8")
    assert "## 1. Purpose" in text
    assert "## 15. Next step" in text
    assert "## 13. Verdict" in text


def test_committed_artifact() -> None:
    if not ARTIFACT.is_file():
        pytest.skip("Run D5-INF-AUGSYNTH-JK-CALIBRATION-001 generator")
    loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert loaded["governance"]["no_promotion"] is True
    assert loaded["overall_verdict"] in {
        "jk_not_ready",
        "jk_safe_but_conservative",
        "jk_promising_needs_more_oc",
        "jk_unsafe_under_diagnostics",
        "jk_calibration_candidate_future_only",
    }
