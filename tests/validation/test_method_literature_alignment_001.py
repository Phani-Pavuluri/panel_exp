"""Smoke tests for METHOD-LITERATURE-ALIGNMENT-001 register."""

from __future__ import annotations

import json

from panel_exp.validation.method_literature_alignment_001 import build_literature_alignment


def test_build_literature_alignment_schema():
    payload = build_literature_alignment()
    assert payload["document_id"] == "METHOD-LITERATURE-ALIGNMENT-001"
    assert payload["counts"]["families_total"] == len(payload["families"])
    assert payload["counts"]["families_total"] >= 20
    allowed = set(payload["alignment_status_values"])
    for fam in payload["families"]:
        assert fam["family_id"]
        assert fam["category"] in ("design", "estimator", "inference", "wrapper")
        assert fam["repo_alignment_status"] in allowed
        assert fam["inventory_canonical_names"]


def test_literature_alignment_json_roundtrip():
    payload = build_literature_alignment()
    loaded = json.loads(json.dumps(payload))
    ids = {f["family_id"] for f in loaded["families"]}
    assert "EST-SCM-001" in ids
    assert "INF-JK-001" in ids
    assert "DES-GMM-001" in ids
