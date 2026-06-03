"""D5-INST-AUGSYNTH-ASCM-002 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_inst_augsynth_ascm_002 import (
    D5InstAugsynthAscm002Config,
    INSTRUMENT_ARMS,
    WORLD_REGISTRY,
    AscmWorldSpec,
    build_d5_inst_augsynth_ascm_002,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_AUGSYNTH_ASCM_002_results.json"
)

FAST_WORLDS = (
    AscmWorldSpec(
        "W0_baseline_reference",
        "baseline",
        "scm_low_signal",
        effect_grid=(0.0, 0.08),
    ),
    AscmWorldSpec(
        "W2_weak_scm_fit_inside_hull",
        "weak inside",
        "scm_trend_mismatch",
        fit_class="weak_fit",
        effect_grid=(0.0, 0.08),
    ),
    AscmWorldSpec(
        "W3_weak_scm_fit_outside_hull",
        "weak outside",
        "scm_low_signal",
        scenario_overrides={"cross_geo_correlation": 0.05, "noise_scale": 3.2},
        fit_class="weak_fit_outside_hull",
        effect_grid=(0.0, 0.08),
    ),
)


@pytest.fixture(scope="module")
def cvxpy_available() -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip(cvxpy_osqp_skip_reason())


def _fast_cfg() -> D5InstAugsynthAscm002Config:
    return D5InstAugsynthAscm002Config(n_mc=1, worlds=FAST_WORLDS)


class TestD5InstAugsynthAscm002:
    def test_all_charter_worlds_registered(self) -> None:
        ids = {w.world_id for w in WORLD_REGISTRY}
        assert "W1_strong_scm_fit_inside_hull" in ids
        assert "W11_multi_treated_unit_panel" in ids
        assert len(WORLD_REGISTRY) >= 11

    def test_build_structure(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_002(_fast_cfg())
        assert payload["artifact_id"] == "D5-INST-AUGSYNTH-ASCM-002"
        assert payload["governance"]["no_promotion"] is True
        assert payload["governance"]["no_calibration_signal_ingress"] is True
        assert payload["governance"]["no_mmm"] is True
        assert payload["governance"]["augsynth_not_primary"] is True
        assert payload["promotion_audit_eligible"] is False

    def test_worlds_emitted(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_002(_fast_cfg())
        rep_worlds = {r["world_id"] for r in payload["replicates"]}
        for w in FAST_WORLDS:
            assert w.world_id in rep_worlds

    def test_a26_and_augsynth_arms_present(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_002(_fast_cfg())
        rep = payload["replicates"][0]
        assert set(rep["instruments"].keys()) == set(INSTRUMENT_ARMS)
        assert "a26_scm_unit_jackknife" in rep["instruments"]
        assert "augsynth_cvxpy_point" in rep["instruments"]

    def test_null_and_effect_worlds_distinguished(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_002(_fast_cfg())
        reg = {w["world_id"]: w["effect_grid"] for w in payload["world_registry"]}
        assert reg["W0_baseline_reference"] == [0.0, 0.08]
        w6 = next(w for w in WORLD_REGISTRY if w.world_id == "W6_null_treatment")
        assert w6.effect_grid == (0.0,)

    def test_diagnostics_present(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_002(_fast_cfg())
        diag = payload["replicates"][0]["diagnostics"]
        assert "scm_pre_rmse" in diag
        assert "augsynth_pre_rmse" in diag
        assert "hull_min_donor_z_distance" in diag

    def test_summaries_schema(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_002(_fast_cfg())
        assert payload["summaries_by_world_arm_effect"]
        row = payload["summaries_by_world_arm_effect"][0]
        for key in ("world_id", "instrument", "effect", "feasibility_rate"):
            assert key in row

    def test_weak_fit_comparison_block(self, cvxpy_available: None) -> None:
        payload = build_d5_inst_augsynth_ascm_002(_fast_cfg())
        assert "weak_fit_vs_a26" in payload
        assert "weak_fit_comparisons" in payload["weak_fit_vs_a26"]


def test_write_artifact(tmp_path: Path, cvxpy_available: None) -> None:
    out = write_artifact(tmp_path / "ascm2.json", cfg=_fast_cfg())
    assert out.is_file()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["artifact_id"] == "D5-INST-AUGSYNTH-ASCM-002"


def test_committed_artifact() -> None:
    if not ARTIFACT.is_file():
        pytest.skip("Run D5-INST-AUGSYNTH-ASCM-002 generator")
    loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert loaded["governance"]["no_promotion"] is True
    assert len(loaded.get("world_registry", [])) >= 11
