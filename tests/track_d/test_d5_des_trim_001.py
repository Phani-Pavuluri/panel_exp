"""D5-DES-TRIM-001 characterization tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.design.registry import get_design_registry
from panel_exp.validation.track_d_d5_des_trim_001 import (
    D5DesTrim001Config,
    build_d5_des_trim_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_DES_TRIM_001_results.json"
)


class TestD5DesTrim001:
    def test_trimmedmatch_registered_not_geo_run(self) -> None:
        reg = get_design_registry()
        spec = reg.resolve("trimmedmatch")
        assert spec.geo_run_supported is False
        assert "trimmedmatch" not in reg.geo_supported_names()

    def test_build_artifact_structure(self) -> None:
        cfg = D5DesTrim001Config(run_full_design=False, panel_sizes=(16,))
        payload = build_d5_des_trim_001(cfg)
        assert payload["artifact_id"] == "D5-DES-TRIM-001"
        assert payload["track_e"]["geo_004_card"] == "characterization_required"
        assert payload["population_semantics"]["target_population"]

    def test_population_shift_documented(self) -> None:
        cfg = D5DesTrim001Config(run_full_design=False, panel_sizes=(20,))
        payload = build_d5_des_trim_001(cfg)
        pop = payload["panel_characterizations"][0]["population"]
        assert pop["n_candidate_markets"] == 20
        assert pop["share_markets_retained"] < 1.0
        assert pop["n_markets_never_paired"] > 0

    def test_readout_blocks_001e(self) -> None:
        payload = build_d5_des_trim_001(D5DesTrim001Config(run_full_design=False, panel_sizes=(16,)))
        excluded = next(
            r for r in payload["readout_compatibility"] if "001e" in r["instrument"]
        )
        assert excluded["compatibility"] == "excluded"

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run D5-DES-TRIM-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-DES-TRIM-001"
        assert loaded["track_e"]["geo_004_card"] == "characterization_required"


def test_write_artifact(tmp_path: Path) -> None:
    cfg = D5DesTrim001Config(run_full_design=False, panel_sizes=(16,))
    out = write_artifact(tmp_path / "trim.json", cfg=cfg)
    assert out.is_file()
