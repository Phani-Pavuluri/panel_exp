"""B5b — manifest and golden fixture structural validation.

Fixtures are the oracle; these tests validate the oracle is internally consistent
before any adapter implementation is wired.
"""

from __future__ import annotations

import json

import pytest

from tests.track_b.contract_fixtures import (
    DOCUMENT_REQUIRED_KEYS,
    EXPORT_STATUSES,
    FORBIDDEN_REGRESSION_IDS,
    MANIFEST_REQUIRED_EXPORT_STATUS,
    collect_b5_test_ids,
    fixtures_dir,
    iter_all_fixture_cases,
    iter_manifest_entries,
    load_fixture_document,
    load_manifest,
    manifest_path,
    validate_document_structure,
)


class TestManifestLoader:
    def test_manifest_file_exists_and_parses(self) -> None:
        manifest = load_manifest()
        assert manifest["manifest_version"]
        assert len(manifest["fixtures"]) == 10

    @pytest.mark.parametrize("entry", list(iter_manifest_entries()), ids=lambda e: e["fixture_id"])
    def test_manifest_entry_points_to_valid_json(self, entry: dict) -> None:
        path = fixtures_dir() / entry["file"]
        assert path.is_file(), f"missing fixture file {path}"
        doc = json.loads(path.read_text(encoding="utf-8"))
        assert doc["fixture_id"] == entry["fixture_id"]

    def test_manifest_lists_gold_001_through_010(self) -> None:
        ids = {e["fixture_id"] for e in iter_manifest_entries()}
        expected = {f"GOLD-{i:03d}" for i in range(1, 11)}
        assert ids == expected


class TestFixtureDocumentStructure:
    @pytest.mark.parametrize("entry", list(iter_manifest_entries()), ids=lambda e: e["file"])
    def test_fixture_has_required_document_keys(self, entry: dict) -> None:
        doc = load_fixture_document(entry["file"])
        assert DOCUMENT_REQUIRED_KEYS <= doc.keys()

    @pytest.mark.parametrize("entry", list(iter_manifest_entries()), ids=lambda e: e["file"])
    def test_fixture_structural_validation_passes(self, entry: dict) -> None:
        doc = load_fixture_document(entry["file"])
        errors = validate_document_structure(doc, filename=entry["file"])
        assert not errors, "\n".join(errors)

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_export_status_is_allowed_enum(self, case) -> None:
        assert case.export_status in EXPORT_STATUSES

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_evidence_never_contains_trust_verdicts(self, case) -> None:
        evidence = case.adapter_expected_output.get("experiment_evidence") or {}
        for field in ("trust_outcome", "alignment_verdict"):
            assert field not in evidence, f"{case.case_key}: evidence has {field}"

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_expected_test_ids_non_empty(self, case) -> None:
        assert case.expected_test_ids

    @pytest.mark.parametrize("case", list(iter_all_fixture_cases()), ids=lambda c: c.case_key)
    def test_forbidden_regressions_are_f1_through_f12(self, case) -> None:
        for ref in case.forbidden_regressions:
            assert ref in FORBIDDEN_REGRESSION_IDS, f"{case.case_key}: bad ref {ref}"


class TestManifestExportStatusExpectations:
    @pytest.mark.parametrize(
        "fixture_id,expected",
        [
            ("GOLD-006", "blocked"),
            ("GOLD-010", "partial"),
        ],
    )
    def test_blocked_and_partial_goldens(self, fixture_id: str, expected: str) -> None:
        statuses = [
            c.export_status
            for c in iter_all_fixture_cases()
            if c.fixture_id == fixture_id
        ]
        assert statuses
        assert all(s == expected for s in statuses)

    @pytest.mark.parametrize(
        "fixture_id",
        ["GOLD-001", "GOLD-002", "GOLD-003", "GOLD-004", "GOLD-005", "GOLD-008", "GOLD-009"],
    )
    def test_complete_export_goldens(self, fixture_id: str) -> None:
        for case in iter_all_fixture_cases():
            if case.fixture_id == fixture_id:
                assert case.export_status == "complete"

    def test_gold_007_mixed_variant_statuses(self) -> None:
        by_variant = {
            c.variant_id: c.export_status
            for c in iter_all_fixture_cases()
            if c.fixture_id == "GOLD-007"
        }
        assert by_variant["relative_att_post_pooled_policy_maps"] == "complete"
        assert by_variant["unknown_legacy_blocks"] == "blocked"


class TestB5TestIdCoverage:
    def test_collected_test_ids_use_known_prefixes(self) -> None:
        prefixes = ("SPEC-", "EV-", "INST-", "ALIGN-", "TR-", "CS-", "DIAG-")
        for tid in collect_b5_test_ids():
            assert tid.startswith(prefixes) or tid.startswith("GOLD-"), tid

    def test_at_least_one_spec_and_tr_id_linked(self) -> None:
        ids = collect_b5_test_ids()
        assert any(i.startswith("SPEC-") for i in ids)
        assert any(i.startswith("TR-") for i in ids)


class TestNegativeAssertionsPresent:
    @pytest.mark.parametrize("entry", list(iter_manifest_entries()), ids=lambda e: e["fixture_id"])
    def test_document_has_negative_assertions(self, entry: dict) -> None:
        doc = load_fixture_document(entry["file"])
        assert doc.get("negative_assertions"), f"{entry['fixture_id']} needs negative_assertions"
