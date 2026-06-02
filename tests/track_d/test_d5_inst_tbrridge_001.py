"""D5-INST-TBRRIDGE-001 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_inst_tbrridge_001 import (
    D5InstTbrridge001Config,
    build_d5_inst_tbrridge_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_TBRRIDGE_001_results.json"
)


class TestD5InstTbrridge001:
    def test_build_structure(self) -> None:
        cfg = D5InstTbrridge001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_tbrridge_001(cfg)
        assert payload["artifact_id"] == "D5-INST-TBRRIDGE-001"
        assert payload["governance"]["no_calibration_signal_ingress"] is True
        assert payload["instrument_status"]["calibration_signal_ingress"] is False

    def test_remain_restricted(self) -> None:
        cfg = D5InstTbrridge001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_tbrridge_001(cfg)
        assert payload["track_e_recommendation"]["INST-002"] in {
            "restricted",
            "remain_restricted",
            "restricted_diagnostic_only",
            "restricted_narrower_wording",
        }

    def test_scm_and_tbr_summaries_present(self) -> None:
        cfg = D5InstTbrridge001Config(n_mc=2, include_multi_cell_k2=False)
        payload = build_d5_inst_tbrridge_001(cfg)
        keys = {s["instrument"] for s in payload["instrument_summaries_null"]}
        assert "scm_jk_unit" in keys
        assert "tbr_kfold_unit" in keys

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-INST-TBRRIDGE-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["overall_verdict"] == "remain_restricted_no_promotion"


def test_write_artifact(tmp_path: Path) -> None:
    cfg = D5InstTbrridge001Config(n_mc=2, include_multi_cell_k2=False)
    out = write_artifact(tmp_path / "tbr.json", cfg=cfg)
    assert out.is_file()
