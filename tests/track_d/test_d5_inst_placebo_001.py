"""D5-INST-PLACEBO-001 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_inst_placebo_001 import (
    D5InstPlacebo001Config,
    build_d5_inst_placebo_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_PLACEBO_001_results.json"
)


class TestD5InstPlacebo001:
    def test_build_structure(self) -> None:
        cfg = D5InstPlacebo001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_placebo_001(cfg)
        assert payload["artifact_id"] == "D5-INST-PLACEBO-001"
        assert payload["governance"]["no_calibration_signal_ingress"] is True
        assert payload["governance"]["no_lift_evidence"] is True

    def test_single_treated_feasible(self) -> None:
        cfg = D5InstPlacebo001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_placebo_001(cfg)
        single = next(
            a for a in payload["geometry_aggregates"] if a["geometry_case"] == "single_treated_forced"
        )
        assert single["feasibility_rate"] >= 0.5

    def test_multi_treated_blocked(self) -> None:
        cfg = D5InstPlacebo001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_placebo_001(cfg)
        multi = next(
            a for a in payload["geometry_aggregates"] if a["geometry_case"] == "multi_treated_natural"
        )
        assert multi["block_rate"] >= 0.5

    def test_track_e_statuses(self) -> None:
        cfg = D5InstPlacebo001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_placebo_001(cfg)
        assert payload["track_e_recommendation"]["INST-006_multi_treated"] == "blocked"
        assert payload["overall_verdict"] == "remain_diagnostic_only_no_promotion"

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-INST-PLACEBO-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["overall_verdict"] == "remain_diagnostic_only_no_promotion"


def test_write_artifact(tmp_path: Path) -> None:
    cfg = D5InstPlacebo001Config(n_mc=2, include_multi_cell_k2=False)
    out = write_artifact(tmp_path / "plac.json", cfg=cfg)
    assert out.is_file()
