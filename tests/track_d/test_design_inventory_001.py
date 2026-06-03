"""DESIGN-INVENTORY-001 tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.design.registry import get_design_registry
from panel_exp.validation.track_d_design_inventory_001 import (
    build_design_inventory_001,
    write_artifact,
)

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "track_d"
    / "archives"
    / "DESIGN_INVENTORY_001_results.json"
)


class TestDesignInventory001:
    def test_registry_alignment(self) -> None:
        inv = build_design_inventory_001()
        reg = set(get_design_registry().geo_supported_names())
        legacy = set(inv["legacy_geo_run_allowlist"])
        assert reg == legacy

    def test_confirmed_001e_methods(self) -> None:
        inv = build_design_inventory_001()
        confirmed = set(inv["confirmed_for_d5_pow_001e"])
        assert "greedy_match_markets" in confirmed
        assert "rerandomization_wrapper" in confirmed
        assert "completerandomization" in confirmed
        assert "supergeos" not in confirmed
        assert "trimmedmatch" not in confirmed

    def test_no_phantom_multi_cell_class(self) -> None:
        inv = build_design_inventory_001()
        ids = {m["method_id"] for m in inv["methods"]}
        assert "multi_cell_multi_treated" not in ids

    def test_committed_artifact(self) -> None:
        if not ARTIFACT.is_file():
            pytest.skip("Run DESIGN-INVENTORY-001 generator")
        loaded = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        assert loaded["artifact_id"] == "DESIGN-INVENTORY-001"
        assert len(loaded["confirmed_for_d5_pow_001e"]) >= 6
