"""M2.1 — representative real RunBundle adapter wire-up (AUDIT-002 follow-up)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from panel_exp.artifacts.run_bundle import build_run_artifact_bundle
from panel_exp.track_b.bundle_extract import extract_resolve_input_from_bundle
from panel_exp.track_b.export import build_geo_run_artifact_bundle
from panel_exp.track_b.geo_adapter import resolve_geo_adapter_output_from_bundle

REP_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "representative_run_bundles"


def _load_rep_cases():
    manifest = json.loads((REP_DIR / "manifest.json").read_text(encoding="utf-8"))
    cases = []
    for entry in manifest["cases"]:
        doc = json.loads((REP_DIR / entry["file"]).read_text(encoding="utf-8"))
        cases.append(doc)
    return cases


_REP_CASES = _load_rep_cases()


@pytest.mark.parametrize("rep", _REP_CASES, ids=lambda r: r["case_id"])
class TestRepresentativeBundleExtraction:
    def test_extraction_completeness_matches_expectation(self, rep: dict) -> None:
        extracted = extract_resolve_input_from_bundle(rep["bundle"])
        expected = rep["expected_export_status"]
        if expected == "blocked":
            assert extracted.completeness == "blocked"
            assert "config_alias" in extracted.missing_fields or not extracted.input.run_artifacts_stub.get(
                "config_alias"
            )
        elif expected == "partial":
            assert extracted.completeness == "partial"
        else:
            assert extracted.completeness == "complete"
            assert extracted.input.run_artifacts_stub.get("config_alias")

    def test_adapter_output_export_status(self, rep: dict) -> None:
        adapter = resolve_geo_adapter_output_from_bundle(rep["bundle"])
        assert adapter["export_status"] == rep["expected_export_status"]
        if rep.get("expected_block_reason_prefix"):
            assert adapter.get("block_reason", "").startswith(
                rep["expected_block_reason_prefix"]
            )
        if rep.get("expected_partial_reason"):
            assert adapter.get("partial_reason") == rep["expected_partial_reason"]
        if rep.get("expected_legacy_mapping_applied"):
            assert adapter.get("legacy_mapping_applied") is True

    def test_no_trust_verdicts_on_adapter_output(self, rep: dict) -> None:
        adapter = resolve_geo_adapter_output_from_bundle(rep["bundle"])
        evidence = adapter.get("experiment_evidence") or {}
        for field in ("trust_outcome", "alignment_verdict"):
            assert field not in evidence
            assert field not in adapter


class TestGeoRunBundleExportPath:
    def test_build_geo_run_artifact_bundle_includes_track_b_views(self) -> None:
        rep = next(r for r in _REP_CASES if r["case_id"] == "REP-001")
        bundle = build_geo_run_artifact_bundle(
            evidence=rep["bundle"]["evidence"],
            include_track_b_views=True,
        )
        payload = bundle.to_dict()
        assert "track_b_views" in payload
        views = payload["track_b_views"]
        assert views["export_status"] == "complete"
        assert views["extraction"]["completeness"] == "complete"
        assert views["adapter_output"]["export_status"] == "complete"

    def test_legacy_default_unchanged_without_opt_in(self) -> None:
        rep = _REP_CASES[0]
        bundle = build_run_artifact_bundle(evidence=rep["bundle"]["evidence"])
        assert "track_b_views" not in bundle.to_dict()

    def test_at_least_three_representative_cases_succeed_or_explicit(self) -> None:
        statuses = {
            resolve_geo_adapter_output_from_bundle(r["bundle"])["export_status"]
            for r in _REP_CASES
        }
        assert "complete" in statuses
        assert "blocked" in statuses
        assert "partial" in statuses
        assert len(_REP_CASES) >= 3
