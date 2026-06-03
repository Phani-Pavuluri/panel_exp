"""Track B contract golden fixture loader (B5b).

The JSON fixtures under tests/fixtures/track_b_contracts/ are the oracle.
Tests load and validate structure; adapter comparison uses these expectations
without re-deriving Track B business logic.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

FORBIDDEN_REGRESSION_IDS = frozenset(f"F{i}" for i in range(1, 13))
EXPORT_STATUSES = frozenset({"blocked", "partial", "complete"})
TRUST_VERDICT_FIELDS = frozenset({"trust_outcome", "alignment_verdict"})

# Top-level keys required on every golden JSON document.
DOCUMENT_REQUIRED_KEYS = frozenset(
    {
        "fixture_id",
        "fixture_version",
        "description",
        "expected_test_ids",
        "forbidden_regressions",
    }
)

# Keys required on each executable case (root fixture or variant).
CASE_REQUIRED_KEYS = frozenset(
    {
        "spec",
        "run_artifacts_stub",
        "adapter_expected_output",
        "trust_report_expected_output",
    }
)

MANIFEST_REQUIRED_EXPORT_STATUS: dict[str, str | set[str]] = {
    "GOLD-001": "complete",
    "GOLD-002": "complete",
    "GOLD-003": "complete",
    "GOLD-004": "complete",
    "GOLD-005": "complete",
    "GOLD-006": "blocked",
    "GOLD-007": {"complete", "blocked"},  # mixed variants
    "GOLD-008": "complete",
    "GOLD-009": "complete",
    "GOLD-010": "partial",
}


def fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "track_b_contracts"


def manifest_path() -> Path:
    return fixtures_dir() / "manifest.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_manifest() -> dict[str, Any]:
    return load_json(manifest_path())


def load_fixture_document(filename: str) -> dict[str, Any]:
    return load_json(fixtures_dir() / filename)


@dataclass(frozen=True)
class FixtureCase:
    """One testable slice: a root fixture or a single variant."""

    fixture_id: str
    variant_id: str | None
    filename: str
    document: dict[str, Any]
    spec: dict[str, Any]
    run_artifacts_stub: dict[str, Any]
    adapter_expected_output: dict[str, Any]
    trust_report_expected_output: dict[str, Any]
    expected_test_ids: list[str]
    forbidden_regressions: list[str]
    negative_assertions: list[str]
    calibration_signal_binding: dict[str, Any] | None

    @property
    def case_key(self) -> str:
        if self.variant_id:
            return f"{self.fixture_id}:{self.variant_id}"
        return self.fixture_id

    @property
    def export_status(self) -> str:
        return self.adapter_expected_output["export_status"]


def _case_from_parts(
    *,
    fixture_id: str,
    variant_id: str | None,
    filename: str,
    document: dict[str, Any],
    body: dict[str, Any],
) -> FixtureCase:
    return FixtureCase(
        fixture_id=fixture_id,
        variant_id=variant_id,
        filename=filename,
        document=document,
        spec=body["spec"],
        run_artifacts_stub=body["run_artifacts_stub"],
        adapter_expected_output=body["adapter_expected_output"],
        trust_report_expected_output=body["trust_report_expected_output"],
        expected_test_ids=list(document["expected_test_ids"]),
        forbidden_regressions=list(document["forbidden_regressions"]),
        negative_assertions=list(document.get("negative_assertions", [])),
        calibration_signal_binding=body.get("calibration_signal_binding")
        or document.get("calibration_signal_binding"),
    )


def iter_cases_from_document(
    document: dict[str, Any], *, filename: str
) -> Iterator[FixtureCase]:
    fixture_id = document["fixture_id"]
    variants = document.get("variants")
    if variants:
        for variant in variants:
            yield _case_from_parts(
                fixture_id=fixture_id,
                variant_id=variant.get("variant_id"),
                filename=filename,
                document=document,
                body=variant,
            )
    else:
        yield _case_from_parts(
            fixture_id=fixture_id,
            variant_id=None,
            filename=filename,
            document=document,
            body=document,
        )


def iter_all_fixture_cases() -> Iterator[FixtureCase]:
    manifest = load_manifest()
    for entry in manifest["fixtures"]:
        filename = entry["file"]
        document = load_fixture_document(filename)
        yield from iter_cases_from_document(document, filename=filename)


def iter_manifest_entries() -> Iterator[dict[str, Any]]:
    for entry in load_manifest()["fixtures"]:
        yield entry


def collect_b5_test_ids() -> set[str]:
    ids: set[str] = set()
    for case in iter_all_fixture_cases():
        ids.update(case.expected_test_ids)
    return ids


def compare_adapter_output_to_oracle(
    actual: dict[str, Any],
    oracle: dict[str, Any],
    *,
    path: str = "adapter_expected_output",
) -> list[str]:
    """Deep-compare actual adapter output to fixture oracle.

    Only keys present in ``oracle`` are checked (oracle-driven).
    Returns human-readable mismatch messages; empty list means match.
    """
    mismatches: list[str] = []

    def _walk(expected: Any, received: Any, prefix: str) -> None:
        if isinstance(expected, dict):
            if not isinstance(received, dict):
                mismatches.append(f"{prefix}: expected dict, got {type(received).__name__}")
                return
            for key, exp_val in expected.items():
                if key not in received:
                    mismatches.append(f"{prefix}.{key}: missing in actual")
                    continue
                _walk(exp_val, received[key], f"{prefix}.{key}")
            return
        if isinstance(expected, list):
            if not isinstance(received, list):
                mismatches.append(f"{prefix}: expected list, got {type(received).__name__}")
                return
            if len(expected) != len(received):
                mismatches.append(
                    f"{prefix}: length {len(received)} != oracle {len(expected)}"
                )
                return
            for i, (exp_item, rec_item) in enumerate(zip(expected, received)):
                _walk(exp_item, rec_item, f"{prefix}[{i}]")
            return
        if expected != received:
            mismatches.append(f"{prefix}: {received!r} != oracle {expected!r}")

    _walk(oracle, actual, path)
    return mismatches


def assert_no_trust_verdicts_on_evidence(evidence: dict[str, Any], *, context: str) -> None:
    for field in TRUST_VERDICT_FIELDS:
        if field in evidence:
            raise AssertionError(f"{context}: evidence must not contain {field}")


def assert_trust_report_scenarios_have_verdicts(
    trust_report: dict[str, Any], *, context: str
) -> None:
    scenarios = trust_report.get("scenarios")
    if not scenarios:
        if trust_report.get("composition_permitted") is False:
            return
        raise AssertionError(f"{context}: trust_report missing scenarios")
    for scenario in scenarios:
        sid = scenario.get("scenario_id", "<unknown>")
        for field in TRUST_VERDICT_FIELDS:
            if field not in scenario:
                raise AssertionError(
                    f"{context} scenario {sid}: missing {field}"
                )


def validate_document_structure(document: dict[str, Any], *, filename: str) -> list[str]:
    """Return structural error messages (empty if valid)."""
    errors: list[str] = []

    missing_doc = DOCUMENT_REQUIRED_KEYS - document.keys()
    if missing_doc:
        errors.append(f"{filename}: missing document keys {sorted(missing_doc)}")

    if not document.get("expected_test_ids"):
        errors.append(f"{filename}: expected_test_ids must be non-empty")

    forbidden = document.get("forbidden_regressions", [])
    bad_f = [f for f in forbidden if f not in FORBIDDEN_REGRESSION_IDS]
    if bad_f:
        errors.append(f"{filename}: unknown forbidden_regressions {bad_f}")

    variants = document.get("variants")
    bodies = variants if variants else [document]
    for i, body in enumerate(bodies):
        label = f"{filename} variant[{i}]" if variants else filename
        missing_case = CASE_REQUIRED_KEYS - body.keys()
        if missing_case:
            errors.append(f"{label}: missing case keys {sorted(missing_case)}")
            continue

        adapter = body["adapter_expected_output"]
        status = adapter.get("export_status")
        if status not in EXPORT_STATUSES:
            errors.append(f"{label}: invalid export_status {status!r}")

        evidence = adapter.get("experiment_evidence") or {}
        for field in TRUST_VERDICT_FIELDS:
            if field in evidence:
                errors.append(f"{label}: experiment_evidence contains forbidden {field}")

        for field in adapter.get("must_not_contain_on_evidence", []):
            if field in evidence:
                errors.append(
                    f"{label}: must_not_contain_on_evidence violated: {field}"
                )

        diag = adapter.get("diagnostic_summary")
        if isinstance(diag, dict) and diag.get("must_not_contain_trust_outcome"):
            for field in TRUST_VERDICT_FIELDS:
                if field in diag:
                    errors.append(f"{label}: diagnostic_summary contains {field}")

        try:
            assert_trust_report_scenarios_have_verdicts(
                body["trust_report_expected_output"], context=label
            )
        except AssertionError as exc:
            errors.append(str(exc))

    return errors
