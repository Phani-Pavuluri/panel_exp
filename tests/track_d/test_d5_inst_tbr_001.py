"""D5-INST-TBR-001 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_inst_tbr_001 import (
    D5InstTbr001Config,
    build_d5_inst_tbr_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_TBR_001_results.json"
)


class TestD5InstTbr001:
    def test_build_structure(self) -> None:
        cfg = D5InstTbr001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_tbr_001(cfg)
        assert payload["artifact_id"] == "D5-INST-TBR-001"
        assert payload["governance"]["not_tbrridge"] is True
        assert payload["governance"]["geometry"] == "aggregate_two_series_only"

    def test_point_feasible_on_agg2(self) -> None:
        cfg = D5InstTbr001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_tbr_001(cfg)
        pt = next(
            s
            for s in payload["instrument_summaries_null_single_cell_agg2"]
            if s["instrument"] == "tbr_point"
        )
        assert pt["feasibility_rate"] >= 0.5

    def test_jk_blocked_on_agg2(self) -> None:
        cfg = D5InstTbr001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_tbr_001(cfg)
        jk = next(
            s
            for s in payload["instrument_summaries_null_single_cell_agg2"]
            if s["instrument"] == "tbr_jk"
        )
        assert jk["feasibility_rate"] == 0.0
        modes = payload["instrument_status"]["callable_inference_modes"]
        assert modes["UnitJackKnife"] == "blocked_on_agg2"

    def test_no_mmm_or_calibration(self) -> None:
        cfg = D5InstTbr001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_tbr_001(cfg)
        assert payload["instrument_status"]["calibration_signal_ingress"] is False
        assert payload["instrument_status"]["mmm_ingress"] is False
        assert payload["instrument_status"]["audit_010_prerequisites_met"] is False

    def test_unit_panel_blocked_probe(self) -> None:
        cfg = D5InstTbr001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_tbr_001(cfg)
        probe = payload["blocked_geometry_probes_sample"]["unit_panel_class_tbr"]
        assert probe["status"] == "blocked"

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-INST-TBR-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["overall_verdict"] in (
            "remain_restricted_aggregate_diagnostic",
            "restricted_with_caveats",
            "blocked_low_feasibility",
        )


@pytest.mark.skipif(bool(cvxpy_osqp_skip_reason()), reason=cvxpy_osqp_skip_reason() or "")
def test_augsynth_context_optional() -> None:
    cfg = D5InstTbr001Config(n_mc=2, include_multi_cell_k2=False, include_augsynth_context=True)
    payload = build_d5_inst_tbr_001(cfg)
    assert "context_comparison" in payload


def test_write_artifact(tmp_path: Path) -> None:
    cfg = D5InstTbr001Config(n_mc=2, include_multi_cell_k2=False)
    out = write_artifact(tmp_path / "tbr.json", cfg=cfg)
    assert out.is_file()
