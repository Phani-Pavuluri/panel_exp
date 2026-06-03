"""D5-INST-AUGSYNTH-001 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.track_d_d5_inst_augsynth_001 import (
    D5InstAugsynth001Config,
    build_d5_inst_augsynth_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_AUGSYNTH_001_results.json"
)


@pytest.fixture(scope="module")
def cvxpy_available() -> None:
    if cvxpy_osqp_skip_reason():
        pytest.skip(cvxpy_osqp_skip_reason())


class TestD5InstAugsynth001:
    def test_build_structure(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynth001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_001(cfg)
        assert payload["artifact_id"] == "D5-INST-AUGSYNTH-001"
        assert payload["governance"]["no_calibration_signal_ingress"] is True

    def test_cvxpy_point_feasible(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynth001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_001(cfg)
        pt = next(
            s
            for s in payload["instrument_summaries_null_single_cell"]
            if s["instrument"] == "augsynth_cvxpy_point"
        )
        assert pt["feasibility_rate"] >= 0.5

    def test_remain_diagnostic_only(self, cvxpy_available: None) -> None:
        cfg = D5InstAugsynth001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_augsynth_001(cfg)
        assert payload["overall_verdict"] == "remain_diagnostic_only_no_calibration_signal"
        assert payload["instrument_status"]["augsynth_cvxpy_point"]["calibration_signal_ingress"] is False

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-INST-AUGSYNTH-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["overall_verdict"] == "remain_diagnostic_only_no_calibration_signal"


def test_write_artifact(tmp_path: Path, cvxpy_available: None) -> None:
    cfg = D5InstAugsynth001Config(n_mc=2, include_multi_cell_k2=False)
    out = write_artifact(tmp_path / "as.json", cfg=cfg)
    assert out.is_file()
