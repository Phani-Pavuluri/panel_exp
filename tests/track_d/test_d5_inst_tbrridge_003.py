"""D5-INST-TBRRIDGE-003 — post F-INF-002 targeted OC (A16, A18, A21)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_inst_tbrridge_003 import (
    D5InstTbrridge003Config,
    build_d5_inst_tbrridge_003,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_INST_TBRRIDGE_003_results.json"
)


class TestD5InstTbrridge003:
    def test_build_structure(self) -> None:
        cfg = D5InstTbrridge003Config(n_mc=2, single_treated_n_mc=2)
        payload = build_d5_inst_tbrridge_003(cfg)
        assert payload["artifact_id"] == "D5-INST-TBRRIDGE-003"
        assert payload["prerequisite"] == "F-INF-002"
        assert set(payload["tuples"]) == {"A16", "A18", "A21"}

    def test_post_fix_not_blocked_interface(self) -> None:
        cfg = D5InstTbrridge003Config(n_mc=2, single_treated_n_mc=2)
        payload = build_d5_inst_tbrridge_003(cfg)
        for row in ("A16", "A18", "A21"):
            disp = payload["tuples"][row]["tbrridge_003_disposition"]
            assert disp != "blocked_interface", row
            post = payload["tuples"][row]["post_fix"]["single_cell_multi_treated"]
            assert post["feasibility_rate"] > 0.0, row

    def test_no_governed_uncertainty_or_promotion(self) -> None:
        cfg = D5InstTbrridge003Config(n_mc=2, single_treated_n_mc=2)
        payload = build_d5_inst_tbrridge_003(cfg)
        assert payload["governance"]["no_governed_uncertainty_claim"] is True
        assert payload["governance"]["no_promotion"] is True
        for row in ("A16", "A18", "A21"):
            assert payload["tuples"][row]["governed_uncertainty"] is False
            assert payload["tuples"][row]["promotion"] is False
            finf = payload["tuples"][row]["f_inf_classification"]
            assert finf["is_governed_uncertainty"] is False

    def test_interface_failure_resolved_vs_tbrridge_002(self) -> None:
        cfg = D5InstTbrridge003Config(n_mc=2, single_treated_n_mc=2)
        payload = build_d5_inst_tbrridge_003(cfg)
        for row in ("A16", "A18", "A21"):
            assert payload["tuples"][row]["interface_failure_resolved"] is True

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-INST-TBRRIDGE-003 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["overall_verdict"] == "remain_restricted_no_promotion"
        assert loaded["governance"]["audit_010_verdict"] == "not_ready_continue_track_f"
