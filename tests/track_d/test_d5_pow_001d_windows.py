"""D5-POW-001d window sensitivity tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_pow_001d import (
    D5Pow001dConfig,
    TRACK_E_SUITABILITY_DIAGNOSTICS,
    WindowSpec,
    run_d5_pow_001d,
    run_one_replicate,
    write_artifact,
)

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_POW_001d_results.json"
)


class TestD5Pow001dWindows:
    def test_track_e_diagnostics_defined(self) -> None:
        assert len(TRACK_E_SUITABILITY_DIAGNOSTICS) >= 5

    def test_one_replicate_multi_window(self) -> None:
        row = run_one_replicate(
            D5Pow001dConfig(
                n_mc=2,
                window_grid=(WindowSpec(24, 8), WindowSpec(28, 8)),
                effect_grid=(0.0, 0.08),
            ),
            seed=20260604,
        )
        assert len(row["windows"]) >= 2
        assert row["windows"][0]["design_context"]["design_method_id"] == "greedy_match_markets"

    def test_characterization_runs(self) -> None:
        payload = run_d5_pow_001d(
            D5Pow001dConfig(
                n_mc=4,
                window_grid=(WindowSpec(24, 6), WindowSpec(28, 8)),
                effect_grid=(0.0, 0.08),
            )
        )
        assert payload["artifact_id"] == "D5-POW-001d"
        assert payload["window_sensitivity_verdict"] in {
            "stable",
            "moderately_sensitive",
            "unstable",
            "fixed_window_preferred",
        }
        assert payload["calibration_eligibility_changed"] is False

    def test_committed_artifact_schema(self) -> None:
        if not ARTIFACT_PATH.is_file():
            pytest.skip("Run D5-POW-001d generator to create committed artifact")
        loaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-POW-001d"
        assert "by_window_summary" in loaded
        assert "track_e_suitability_diagnostics" in loaded
