"""Smoke tests for METHOD-CODE-INVENTORY-001 generator."""

from __future__ import annotations

import json

from panel_exp.validation.method_code_inventory_001 import build_inventory


def test_build_inventory_structure():
    payload = build_inventory()
    assert payload["document_id"] == "METHOD-CODE-INVENTORY-001"
    assert payload["counts"]["total"] == len(payload["items"])
    assert payload["counts"]["total"] >= 30
    names = {item["canonical_name"] for item in payload["items"]}
    assert "greedy_match_markets" in names
    assert "AugSynthCVXPY" in names
    assert "UnitJackKnife" in names
    assert "rerandomization_wrapper" in names


def test_inventory_json_roundtrip():
    payload = build_inventory()
    raw = json.dumps(payload)
    loaded = json.loads(raw)
    assert loaded["counts"]["design"] >= 8
