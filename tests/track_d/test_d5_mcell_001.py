"""D5-MCELL-001 optimal cell-count characterization tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_mcell_001 import (
    D5Mcell001Config,
    build_d5_mcell_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_MCELL_001_results.json"
)


class TestD5Mcell001:
    def test_build_structure(self) -> None:
        cfg = D5Mcell001Config(n_mc=3, requested_cell_counts=(1, 2))
        payload = build_d5_mcell_001(cfg)
        assert payload["artifact_id"] == "D5-MCELL-001"
        assert payload["governance"]["no_pooled_multi_cell_claim"] is True
        assert payload["recommendations"]["conservative_recommended_max_cells"] >= 1

    def test_no_pooled_fpr_in_aggregates(self) -> None:
        cfg = D5Mcell001Config(n_mc=2, requested_cell_counts=(1, 2))
        payload = build_d5_mcell_001(cfg)
        for row in payload["cell_count_aggregates"]:
            assert row.get("null_interval_exclusion_fpr_pooled_across_cells") is None

    def test_per_method_table(self) -> None:
        cfg = D5Mcell001Config(n_mc=2, requested_cell_counts=(1, 2, 3))
        payload = build_d5_mcell_001(cfg)
        assert len(payload["recommendations"]["per_method"]) == 6

    def test_track_e_mcell_012_characterized(self) -> None:
        cfg = D5Mcell001Config(n_mc=2, requested_cell_counts=(1, 2))
        payload = build_d5_mcell_001(cfg)
        assert payload["track_e"]["e_des_mcell_012"] == "characterized"

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-MCELL-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-MCELL-001"
        assert loaded["track_e"]["recommended_max_concurrent_cells"] >= 1


def test_write_artifact(tmp_path: Path) -> None:
    cfg = D5Mcell001Config(n_mc=2, requested_cell_counts=(1, 2))
    out = write_artifact(tmp_path / "mcell.json", cfg=cfg)
    assert out.is_file()
