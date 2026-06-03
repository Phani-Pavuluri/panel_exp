"""D5-DES-SUPERGEO-001 characterization tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.design.registry import get_design_registry
from panel_exp.validation.track_d_d5_des_supergeo_001 import (
    build_d5_des_supergeo_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_DES_SUPERGEO_001_results.json"
)


class TestD5DesSupergeo001:
    def test_supergeos_registered_not_geo_run(self) -> None:
        reg = get_design_registry()
        spec = reg.resolve("supergeos")
        assert spec.geo_run_supported is False
        assert "supergeos" not in reg.geo_supported_names()

    def test_build_artifact_structure(self) -> None:
        payload = build_d5_des_supergeo_001(
            run_milp=False,
        )
        assert payload["artifact_id"] == "D5-DES-SUPERGEO-001"
        assert payload["registry"]["registry_name"] == "supergeos"
        assert len(payload["panel_characterizations"]) >= 3
        assert payload["track_e"]["geo_003_card"] == "characterization_required"
        assert payload["excluded_from"]

    def test_milp_coverage_mismatch_documented(self) -> None:
        payload = build_d5_des_supergeo_001(run_milp=False)
        for panel in payload["panel_characterizations"]:
            mismatch = panel["milp_coverage_mismatch"]
            if mismatch["n_markets_total"] > mismatch["n_markets_in_combo_scope"]:
                assert mismatch["n_markets_outside_combo_scope"] > 0

    def test_readout_blocks_flat_scm_jk(self) -> None:
        payload = build_d5_des_supergeo_001(run_milp=False)
        flat = next(
            r
            for r in payload["readout_compatibility"]
            if "original market level" in r["instrument"]
        )
        assert flat["compatibility"] == "blocked"

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-DES-SUPERGEO-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-DES-SUPERGEO-001"
        assert loaded["track_e"]["geo_003_card"] == "characterization_required"


def test_write_artifact(tmp_path: Path) -> None:
    out = write_artifact(tmp_path / "supergeo.json", run_milp=False)
    assert out.is_file()
