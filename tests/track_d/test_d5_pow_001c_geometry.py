"""D5-POW-001c unit vs 2-row aggregation geometry tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.validation.track_d_d5_pow_001c import (
    D5Pow001cConfig,
    DESIGN_METHODS_FOR_001E,
    run_d5_pow_001c,
    run_one_replicate,
    write_artifact,
)

ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "D5_POW_001c_results.json"
)


class TestD5Pow001cGeometry:
    def test_design_methods_table_present(self) -> None:
        assert any(m["design_method_id"] == "greedy_match_markets" for m in DESIGN_METHODS_FOR_001E)
        greedy = next(m for m in DESIGN_METHODS_FOR_001E if m["design_method_id"] == "greedy_match_markets")
        assert greedy["in_d5_pow_001c"] is True

    def test_one_replicate_design_aware(self) -> None:
        row = run_one_replicate(
            D5Pow001cConfig(n_mc=2, effect_grid=(0.0, 0.08)),
            seed=20260603,
        )
        assert row["design_context"]["design_method_id"] == "greedy_match_markets"
        assert row["geometry_loss"]["n_markets_collapsed"] >= 1
        assert "unit_scm_jk" in row
        assert "agg2_tbr_kfold" in row

    def test_characterization_runs(self) -> None:
        payload = run_d5_pow_001c(D5Pow001cConfig(n_mc=4, effect_grid=(0.0, 0.08)))
        assert payload["artifact_id"] == "D5-POW-001c"
        assert payload["aggregation_proxy_verdict"] in {
            "acceptable",
            "optimistic",
            "conservative",
            "invalid",
            "narrow_diagnostics_only",
        }
        assert payload["calibration_eligibility_changed"] is False
        assert len(payload["design_methods_for_001e"]) >= 3

    def test_committed_artifact_schema(self) -> None:
        if not ARTIFACT_PATH.is_file():
            pytest.skip("Run D5-POW-001c generator to create committed artifact")
        loaded = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "D5-POW-001c"
        assert "design_context_reference" in loaded
        assert "design_methods_for_001e" in loaded
