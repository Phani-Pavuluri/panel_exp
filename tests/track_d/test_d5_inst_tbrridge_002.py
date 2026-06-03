"""D5-INST-TBRRIDGE-002 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_inst_tbrridge_002 import (
    D5InstTbrridge002Config,
    build_d5_inst_tbrridge_002,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_TBRRIDGE_002_results.json"
)


class TestD5InstTbrridge002:
    def test_build_structure(self) -> None:
        cfg = D5InstTbrridge002Config(n_mc=2, include_combo_scale_probe=False)
        payload = build_d5_inst_tbrridge_002(cfg)
        assert payload["artifact_id"] == "D5-INST-TBRRIDGE-002"
        assert payload["governance"]["not_class_TBR"] is True
        assert payload["governance"]["tbr_label_audit"]["p0_002_satisfied"] is True

    def test_jk_jkp_conformal_blocked(self) -> None:
        cfg = D5InstTbrridge002Config(n_mc=2, include_combo_scale_probe=False)
        payload = build_d5_inst_tbrridge_002(cfg)
        for inf in ("UnitJackKnife", "JKP", "Conformal"):
            assert payload["mode_dispositions"][inf]["disposition"] == "blocked_interface"

    def test_bayesian_blocked_policy(self) -> None:
        cfg = D5InstTbrridge002Config(n_mc=2, include_combo_scale_probe=False)
        payload = build_d5_inst_tbrridge_002(cfg)
        assert payload["mode_dispositions"]["Bayesian"]["disposition"] == "blocked_production_policy"

    def test_kfold_context_already_characterized(self) -> None:
        cfg = D5InstTbrridge002Config(n_mc=2, include_combo_scale_probe=False)
        payload = build_d5_inst_tbrridge_002(cfg)
        assert (
            payload["mode_dispositions"]["Kfold"]["disposition"]
            == "already_characterized_restricted"
        )

    def test_no_mmm_calibration_promotion(self) -> None:
        cfg = D5InstTbrridge002Config(n_mc=2, include_combo_scale_probe=False)
        payload = build_d5_inst_tbrridge_002(cfg)
        assert payload["governance"]["calibration_signal_ingress"] is False
        assert payload["governance"]["mmm_ingress"] is False
        assert payload["governance"]["promotion"] is False

    def test_timeseries_kfold_not_governed_intervals(self) -> None:
        cfg = D5InstTbrridge002Config(n_mc=2, include_combo_scale_probe=False)
        payload = build_d5_inst_tbrridge_002(cfg)
        tskf = payload["mode_dispositions"]["TimeSeriesKfold"]["disposition"]
        assert tskf in (
            "callable_unverified_interval_semantics",
            "characterized_restricted",
        )

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-INST-TBRRIDGE-002 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["overall_verdict"] == "remain_restricted_no_promotion"
        assert loaded["governance"]["audit_010_verdict"] == "not_ready_continue_track_f"
