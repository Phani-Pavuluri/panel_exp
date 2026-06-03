"""D5-INST-AUGSYNTH-ASCM-003 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.scm_augsynth_diagnostics import (
    CONFLICT_DIAGNOSTIC_FIELDS,
    INSTRUMENT_DIAGNOSTIC_FIELDS,
    PANEL_DIAGNOSTIC_FIELDS,
)
from panel_exp.validation.track_d_d5_inst_augsynth_ascm_003 import (
    D5InstAugsynthAscm003Config,
    INSTRUMENT_ARMS,
    PRIMARY_INSTRUMENT_ARMS,
    WORLD_REGISTRY_003,
    Ascm003WorldSpec,
    build_d5_inst_augsynth_ascm_003,
    write_artifact,
    write_report,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_AUGSYNTH_ASCM_003_results.json"
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


def _fast_cfg() -> D5InstAugsynthAscm003Config:
    return D5InstAugsynthAscm003Config(
        n_mc=1,
        worlds=FAST_WORLDS,
        weak_fit_world_ids=(
            "W2_weak_scm_fit_inside_hull",
            "W3_weak_scm_fit_outside_hull",
        ),
    )


class TestD5InstAugsynthAscm003:
    def test_world_registry_includes_severity_extensions(self) -> None:
        ids = {w.world_id for w in WORLD_REGISTRY_003}
        assert "W2m_mild_weak_fit" in ids
        assert "W2s_severe_weak_fit" in ids
        assert "W2r_lambda_reg_moderate" in ids
        assert len(WORLD_REGISTRY_003) >= 19

    def test_build_structure(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_003(_fast_cfg())
        assert payload["artifact_id"] == "D5-INST-AUGSYNTH-ASCM-003"
        assert payload["governance"]["no_promotion"] is True
        assert payload["governance"]["no_threshold_finalization"] is True
        assert payload["governance"]["no_eligibility_change"] is True
        assert payload["promotion_audit_eligible"] is False
        assert payload["promotion_audit_opened"] is False

    def test_primary_arms_subset(self) -> None:
        assert set(PRIMARY_INSTRUMENT_ARMS).issubset(set(INSTRUMENT_ARMS))

    def test_fidelity_audit_metadata(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_003(_fast_cfg())
        fid = payload["fidelity_audit"]
        assert fid["audit_id"] == "AUGSYNTH-ASCM-IMPLEMENTATION-FIDELITY-AUDIT-001"
        assert fid["verdict"] == "fidelity_confirmed_with_caveats"
        assert any(c["id"] == "G4" for c in fid["caveats"])

    def test_diagnostics_present(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_003(_fast_cfg())
        diag = payload["replicates"][0]["diagnostics"]
        for key in PANEL_DIAGNOSTIC_FIELDS:
            assert key in diag
        rep = payload["replicates"][0]
        inst = rep["instruments"]["augsynth_cvxpy_unit_jackknife"][0.0]
        for key in INSTRUMENT_DIAGNOSTIC_FIELDS:
            assert key in inst
        for key in CONFLICT_DIAGNOSTIC_FIELDS:
            assert key in rep["conflict_vs_a26"]

    def test_lambda_reg_tracked_on_world(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynthAscm003Config(
            n_mc=1,
            worlds=(
                Ascm003WorldSpec(
                    "W2r_lambda_reg_moderate",
                    "ridge test",
                    "scm_trend_mismatch",
                    fit_class="weak_fit",
                    augsynth_lambda_reg=0.01,
                    effect_grid=(0.0, 0.08),
                ),
            ),
        )
        payload = build_d5_inst_augsynth_ascm_003(cfg)
        rep = payload["replicates"][0]
        assert rep["augsynth_lambda_reg"] == 0.01
        pt = rep["instruments"]["augsynth_cvxpy_point"][0.0]
        assert pt.get("augsynth_lambda_reg_used") == 0.01

    def test_extended_summaries(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_003(_fast_cfg())
        assert payload["hull_strata_summary"]
        assert payload["weak_fit_severity_summary"]
        assert payload["diagnostic_usefulness"]
        assert payload["null_interval_summary"]
        assert payload["panel_diagnostics_by_world"]

    def test_verdict_literal(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_003(_fast_cfg())
        allowed = {
            "continue_diagnostic_comparator",
            "promising_needs_inference_calibration",
            "implementation_fix_required",
            "stop_augsynth_lane",
            "promotion_audit_candidate_future_only",
        }
        assert payload["overall_verdict"] in allowed

    def test_default_n_mc_target(self) -> None:
        cfg = D5InstAugsynthAscm003Config()
        assert cfg.n_mc == 14


def test_write_artifact_and_report(tmp_path: Path, cvxpy_available: None) -> None:
    out = write_artifact(tmp_path / "ascm3.json", cfg=_fast_cfg())
    assert out.is_file()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["artifact_id"] == "D5-INST-AUGSYNTH-ASCM-003"
    rep = write_report(results_path=out, report_path=tmp_path / "report.md")
    text = rep.read_text(encoding="utf-8")
    assert "## 1. Purpose" in text
    assert "## 14. Next step" in text
    assert "Fidelity-audit caveats" in text


def test_committed_artifact() -> None:
    if not ARTIFACT.is_file():
        pytest.skip("Run D5-INST-AUGSYNTH-ASCM-003 generator")
    loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert loaded["governance"]["no_promotion"] is True
    assert loaded["config"]["n_mc"] >= 1
    assert len(loaded.get("world_registry", [])) >= 19
