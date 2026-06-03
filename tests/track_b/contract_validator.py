"""Track B contract bundle validator (B5d).

Validates golden fixture bundles and composed TrustReport outputs against
B2/B4/B5 structural expectations. Does not implement adapter resolution or
redefine trust business logic — fixtures remain the oracle for outcomes.

CLI::

    poetry run python -m tests.track_b.contract_validator
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any, Callable, Iterator

from tests.track_b import contract_fixtures as _cf
from tests.track_b.contract_fixtures import (
    EXPORT_STATUSES,
    FORBIDDEN_REGRESSION_IDS,
    MANIFEST_REQUIRED_EXPORT_STATUS,
    TRUST_VERDICT_FIELDS,
    FixtureCase,
    validate_document_structure,
)
from tests.track_b.trust_report_composer import compose_trust_report, trust_report_to_dict

ALIGNMENT_VERDICTS = frozenset(
    {"aligned", "divergent", "incompatible", "not_assessable"}
)
TRUST_OUTCOMES = frozenset(
    {
        "supported",
        "supported_with_limitations",
        "inconclusive",
        "unsupported",
        "not_assessable",
    }
)

SPEC_REQUIRED_FIELDS = frozenset({"study_id", "spec_version", "modality"})
EVIDENCE_IDENTITY_FIELDS = frozenset(
    {
        "declared_estimand_id",
        "exported_estimand_id",
        "measurement_instrument_id",
    }
)
CALIBRATION_BINDING_FIELDS = frozenset(
    {
        "lookup_key",
        "expected_signal_id",
        "expected_signal_version",
        "expected_calibration_estimand_id",
        "expected_usage_boundary",
    }
)
TRUST_SCENARIO_REQUIRED_FIELDS = frozenset(
    {
        "scenario_id",
        "intended_use",
        "claim_type",
        "alignment_verdict",
        "trust_outcome",
    }
)


@dataclass(frozen=True)
class ValidationIssue:
    """Single validation failure with a stable location path."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass
class ValidationResult:
    issues: list[ValidationIssue]

    @property
    def ok(self) -> bool:
        return not self.issues

    def format_messages(self) -> str:
        return "\n".join(str(i) for i in self.issues)


def _issue(path: str, message: str) -> ValidationIssue:
    return ValidationIssue(path=path, message=message)


def _prefix(case: FixtureCase) -> str:
    return case.case_key


def _walk_forbidden_verdict_fields(
    obj: Any, *, path: str, issues: list[ValidationIssue]
) -> None:
    if isinstance(obj, dict):
        for key, val in obj.items():
            child = f"{path}.{key}" if path else key
            if key in TRUST_VERDICT_FIELDS:
                issues.append(
                    _issue(child, f"layer must not contain trust field {key!r}")
                )
            _walk_forbidden_verdict_fields(val, path=child, issues=issues)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _walk_forbidden_verdict_fields(item, path=f"{path}[{i}]", issues=issues)


def validate_manifest() -> list[ValidationIssue]:
    """Manifest index: GOLD-001–010 coverage and file presence."""
    issues: list[ValidationIssue] = []
    try:
        manifest = _cf.load_manifest()
    except (OSError, json.JSONDecodeError) as exc:
        return [_issue("manifest", str(exc))]

    entries = manifest.get("fixtures")
    if not isinstance(entries, list):
        return [_issue("manifest.fixtures", "must be a list")]

    if len(entries) != 10:
        issues.append(
            _issue("manifest.fixtures", f"expected 10 entries, got {len(entries)}")
        )

    seen_ids: set[str] = set()
    for i, entry in enumerate(entries):
        base = f"manifest.fixtures[{i}]"
        fixture_id = entry.get("fixture_id")
        if not fixture_id:
            issues.append(_issue(base, "missing fixture_id"))
            continue
        if fixture_id in seen_ids:
            issues.append(_issue(base, f"duplicate fixture_id {fixture_id!r}"))
        seen_ids.add(fixture_id)

        filename = entry.get("file")
        if not filename:
            issues.append(_issue(base, "missing file"))
            continue
        path = _cf.fixtures_dir() / filename
        if not path.is_file():
            issues.append(_issue(base, f"fixture file not found: {path}"))
            continue
        try:
            doc = _cf.load_fixture_document(filename)
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(_issue(base, f"cannot load {filename}: {exc}"))
            continue
        if doc.get("fixture_id") != fixture_id:
            issues.append(
                _issue(
                    base,
                    f"fixture_id mismatch: manifest {fixture_id!r} "
                    f"vs file {doc.get('fixture_id')!r}",
                )
            )

        expected_status = MANIFEST_REQUIRED_EXPORT_STATUS.get(fixture_id)
        if expected_status is not None:
            actual_statuses = {
                c.export_status
                for c in _cf.iter_all_fixture_cases()
                if c.fixture_id == fixture_id
            }
            if isinstance(expected_status, str):
                if actual_statuses != {expected_status}:
                    issues.append(
                        _issue(
                            base,
                            f"export_status expected all {expected_status!r}, "
                            f"got {sorted(actual_statuses)}",
                        )
                    )
            else:
                if not actual_statuses <= expected_status:
                    issues.append(
                        _issue(
                            base,
                            f"export_status {sorted(actual_statuses)} "
                            f"not in allowed {sorted(expected_status)}",
                        )
                    )

    expected = {f"GOLD-{n:03d}" for n in range(1, 11)}
    if seen_ids != expected:
        missing = expected - seen_ids
        extra = seen_ids - expected
        if missing:
            issues.append(_issue("manifest", f"missing fixture_ids: {sorted(missing)}"))
        if extra:
            issues.append(_issue("manifest", f"unexpected fixture_ids: {sorted(extra)}"))

    return issues


def validate_fixture_document(filename: str) -> list[ValidationIssue]:
    """Structural validation for one golden JSON file."""
    issues: list[ValidationIssue] = []
    try:
        doc = _cf.load_fixture_document(filename)
    except (OSError, json.JSONDecodeError) as exc:
        return [_issue(filename, str(exc))]

    for msg in validate_document_structure(doc, filename=filename):
        issues.append(_issue(filename, msg))
    return issues


def validate_contract_case(case: FixtureCase) -> list[ValidationIssue]:
    """Full Track B contract bundle validation for one executable case."""
    issues: list[ValidationIssue] = []
    p = _prefix(case)

    issues.extend(_validate_spec(case, p))
    issues.extend(_validate_adapter_layer(case, p))
    issues.extend(_validate_calibration_binding(case, p))
    issues.extend(_validate_trust_report_oracle(case, p))
    issues.extend(_validate_trust_composition(case, p))
    issues.extend(_validate_forbidden_regressions(case, p))

    return issues


def _validate_spec(case: FixtureCase, prefix: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    spec = case.spec
    for field in SPEC_REQUIRED_FIELDS:
        if not spec.get(field):
            issues.append(_issue(f"{prefix}.spec", f"missing required {field!r}"))
    modality = spec.get("modality")
    if modality and not isinstance(modality, str):
        issues.append(_issue(f"{prefix}.spec.modality", "must be a string"))
    return issues


def _validate_adapter_layer(case: FixtureCase, prefix: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    adapter = case.adapter_expected_output
    base = f"{prefix}.adapter_expected_output"

    status = adapter.get("export_status")
    if status not in EXPORT_STATUSES:
        issues.append(_issue(base, f"invalid export_status {status!r}"))

    _walk_forbidden_verdict_fields(adapter, path=base, issues=issues)

    evidence = adapter.get("experiment_evidence")
    if evidence is None and status != "blocked":
        issues.append(_issue(base, "missing experiment_evidence"))
    elif isinstance(evidence, dict):
        ev_path = f"{base}.experiment_evidence"
        for field in adapter.get("must_not_contain_on_evidence", []):
            if field in evidence:
                issues.append(
                    _issue(ev_path, f"must_not_contain_on_evidence violated: {field!r}")
                )
        if status in ("complete", "partial"):
            for field in EVIDENCE_IDENTITY_FIELDS:
                if field not in evidence:
                    issues.append(_issue(ev_path, f"missing identity field {field!r}"))
            inst = evidence.get("measurement_instrument_id")
            if inst and isinstance(inst, str) and status == "complete":
                if inst.count(".") < 3:
                    issues.append(
                        _issue(
                            ev_path,
                            "measurement_instrument_id must be registry-canonical "
                            "(F12: alias alone is insufficient)",
                        )
                    )

    facts = adapter.get("alignment_facts")
    if facts is not None and not isinstance(facts, dict):
        issues.append(_issue(f"{base}.alignment_facts", "must be dict or null"))
    elif isinstance(facts, dict):
        _walk_forbidden_verdict_fields(facts, path=f"{base}.alignment_facts", issues=issues)

    diag = adapter.get("diagnostic_summary")
    if isinstance(diag, dict):
        _walk_forbidden_verdict_fields(
            diag, path=f"{base}.diagnostic_summary", issues=issues
        )
        if diag.get("must_not_contain_trust_outcome"):
            for field in TRUST_VERDICT_FIELDS:
                if field in diag:
                    issues.append(
                        _issue(
                            f"{base}.diagnostic_summary",
                            f"F7: diagnostic must not contain {field!r}",
                        )
                    )

    return issues


def _validate_calibration_binding(
    case: FixtureCase, prefix: str
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    binding = case.calibration_signal_binding
    if not binding:
        return issues

    base = f"{prefix}.calibration_signal_binding"
    _walk_forbidden_verdict_fields(binding, path=base, issues=issues)

    if binding.get("lookup_attempted") is False:
        return issues

    if binding.get("lookup_key"):
        required_binding = set(CALIBRATION_BINDING_FIELDS)
        if binding.get("expected_usage_boundary") in (
            "null_reference_diagnostic",
            "null_monitor_only",
        ):
            required_binding.discard("expected_calibration_estimand_id")
        for field in required_binding:
            if field not in binding:
                issues.append(_issue(base, f"missing calibration binding field {field!r}"))

        evidence = case.adapter_expected_output.get("experiment_evidence") or {}
        if case.export_status in ("complete", "partial"):
            exp_id = binding.get("expected_signal_id")
            exp_ver = binding.get("expected_signal_version")
            if exp_id and evidence.get("calibration_signal_id") != exp_id:
                issues.append(
                    _issue(
                        f"{prefix}.adapter_expected_output.experiment_evidence",
                        f"calibration_signal_id {evidence.get('calibration_signal_id')!r} "
                        f"!= binding expected {exp_id!r}",
                    )
                )
            if exp_ver and evidence.get("calibration_signal_version") != exp_ver:
                issues.append(
                    _issue(
                        f"{prefix}.adapter_expected_output.experiment_evidence",
                        f"calibration_signal_version mismatch vs binding",
                    )
                )
            lookup = binding.get("lookup_key")
            inst = evidence.get("measurement_instrument_id")
            if lookup and inst and lookup != inst:
                issues.append(
                    _issue(
                        base,
                        f"lookup_key must match evidence measurement_instrument_id "
                        f"({lookup!r} vs {inst!r})",
                    )
                )

        if binding.get("signal_must_not_contain_trust_outcome"):
            for field in TRUST_VERDICT_FIELDS:
                if field in binding:
                    issues.append(
                        _issue(base, f"signal binding must not contain {field!r}")
                    )

    return issues


def _validate_trust_report_oracle(
    case: FixtureCase, prefix: str
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    tr = case.trust_report_expected_output
    base = f"{prefix}.trust_report_expected_output"

    _walk_forbidden_verdict_fields(
        {k: v for k, v in tr.items() if k != "scenarios"},
        path=base,
        issues=issues,
    )

    scenarios = tr.get("scenarios")
    if tr.get("composition_permitted") is False and not scenarios:
        return issues

    if not scenarios:
        issues.append(_issue(base, "missing scenarios"))
        return issues

    seen_ids: set[str] = set()
    for i, scenario in enumerate(scenarios):
        sp = f"{base}.scenarios[{i}]"
        sid = scenario.get("scenario_id")
        if not sid:
            issues.append(_issue(sp, "missing scenario_id"))
            continue
        if sid in seen_ids:
            issues.append(_issue(sp, f"duplicate scenario_id {sid!r}"))
        seen_ids.add(sid)

        for field in TRUST_SCENARIO_REQUIRED_FIELDS:
            if field not in scenario:
                issues.append(_issue(sp, f"missing required field {field!r}"))

        av = scenario.get("alignment_verdict")
        to = scenario.get("trust_outcome")
        if av not in ALIGNMENT_VERDICTS:
            issues.append(_issue(sp, f"invalid alignment_verdict {av!r}"))
        if to not in TRUST_OUTCOMES:
            issues.append(_issue(sp, f"invalid trust_outcome {to!r}"))

    return issues


def _validate_trust_composition(case: FixtureCase, prefix: str) -> list[ValidationIssue]:
    """Composed TrustReport must match fixture oracle; root has no verdict fields."""
    issues: list[ValidationIssue] = []
    tr_oracle = case.trust_report_expected_output
    if tr_oracle.get("composition_permitted") is False and not tr_oracle.get("scenarios"):
        return issues

    composed = trust_report_to_dict(compose_trust_report(case))
    base = f"{prefix}.trust_composition"

    for field in TRUST_VERDICT_FIELDS:
        if field in composed:
            issues.append(
                _issue(base, f"composition root must not contain {field!r} (scenarios only)")
            )

    oracle_by_id = {
        s["scenario_id"]: s for s in tr_oracle.get("scenarios") or []
    }
    for scenario in composed["scenarios"]:
        sid = scenario["scenario_id"]
        if sid not in oracle_by_id:
            issues.append(_issue(f"{base}.{sid}", "unexpected composed scenario"))
            continue
        oracle = oracle_by_id[sid]
        oracle_av = oracle.get("alignment_verdict")
        oracle_to = oracle.get("trust_outcome")
        if oracle_av is None:
            issues.append(_issue(f"{base}.{sid}", "oracle missing alignment_verdict"))
        elif scenario["alignment_verdict"] != oracle_av:
            issues.append(
                _issue(
                    f"{base}.{sid}",
                    f"alignment_verdict {scenario['alignment_verdict']!r} "
                    f"!= oracle {oracle_av!r}",
                )
            )
        if oracle_to is None:
            issues.append(_issue(f"{base}.{sid}", "oracle missing trust_outcome"))
        elif scenario["trust_outcome"] != oracle_to:
            issues.append(
                _issue(
                    f"{base}.{sid}",
                    f"trust_outcome {scenario['trust_outcome']!r} != oracle {oracle_to!r}",
                )
            )

    ref = tr_oracle.get("alignment_reference_estimand_id")
    if ref and composed.get("alignment_reference_estimand_id") != ref:
        issues.append(
            _issue(
                base,
                f"alignment_reference_estimand_id "
                f"{composed.get('alignment_reference_estimand_id')!r} != oracle {ref!r}",
            )
        )

    return issues


ForbiddenGuard = Callable[[FixtureCase], list[ValidationIssue]]


def _guard_f1(case: FixtureCase) -> list[ValidationIssue]:
    """F1: no estimator-name inference — complete export needs declared identity."""
    if case.export_status != "complete":
        return []
    adapter = case.adapter_expected_output
    if adapter.get("legacy_mapping_applied"):
        return []
    spec_decl = case.spec.get("declared_estimand_id")
    evidence = adapter.get("experiment_evidence") or {}
    ev_decl = evidence.get("declared_estimand_id")
    if not spec_decl and not ev_decl:
        return [
            _issue(
                _prefix(case),
                "F1: complete export without declared_estimand_id "
                "(estimator must not infer estimand)",
            )
        ]
    return []


def _guard_f2(case: FixtureCase) -> list[ValidationIssue]:
    """F2: instrument resolved via catalog, not estimator class name."""
    if case.export_status != "complete":
        return []
    evidence = case.adapter_expected_output.get("experiment_evidence") or {}
    if not evidence.get("measurement_instrument_id"):
        return [
            _issue(
                _prefix(case),
                "F2: complete export missing measurement_instrument_id",
            )
        ]
    return []


def _guard_f3(case: FixtureCase) -> list[ValidationIssue]:
    """F3: placebo band must not be treated as confidence interval."""
    evidence = case.adapter_expected_output.get("experiment_evidence") or {}
    if evidence.get("interval_semantics") != "placebo_band":
        return []
    if evidence.get("interval_semantics_compatible") is True:
        return [
            _issue(
                _prefix(case),
                "F3: placebo_band cannot have interval_semantics_compatible=true",
            )
        ]
    return []


def _guard_f4(case: FixtureCase) -> list[ValidationIssue]:
    """F4: cumulative vs relative scale — incompatible facts must be recorded."""
    facts = case.adapter_expected_output.get("alignment_facts") or {}
    if facts.get("scale_compatible") is False:
        return []
    evidence = case.adapter_expected_output.get("experiment_evidence") or {}
    point = evidence.get("exported_estimand_id") or ""
    interval = evidence.get("interval_estimand_id") or ""
    if "cumulative" in interval and "relative" in point and case.export_status == "complete":
        return [
            _issue(
                _prefix(case),
                "F4: cumulative interval with relative point export requires "
                "scale_compatible=false",
            )
        ]
    return []


def _guard_f5(case: FixtureCase) -> list[ValidationIssue]:
    """F5: recovery/null-monitor signal must not license business lift as supported."""
    binding = case.calibration_signal_binding or {}
    if binding.get("expected_lift_detection_calibrated") is not False:
        return []
    for scenario in case.trust_report_expected_output.get("scenarios") or []:
        if scenario.get("claim_type") == "positive_lift_detection":
            if scenario.get("trust_outcome") == "supported":
                return [
                    _issue(
                        f"{_prefix(case)}.trust_report",
                        "F5: lift claim cannot be supported when "
                        "expected_lift_detection_calibrated is false",
                    )
                ]
    return []


def _guard_f6(case: FixtureCase) -> list[ValidationIssue]:
    """F6: MMM intake requires transform ref when intent is set."""
    if not case.spec.get("mmm_calibration_intent"):
        return []
    if case.spec.get("estimand_transform_ref"):
        return []
    evidence = case.adapter_expected_output.get("experiment_evidence") or {}
    if not evidence.get("mmm_intake_blocked"):
        return [
            _issue(
                _prefix(case),
                "F6: mmm_calibration_intent without transform_ref requires "
                "mmm_intake_blocked on evidence",
            )
        ]
    return []


def _guard_f7(case: FixtureCase) -> list[ValidationIssue]:
    """F7: diagnostics must not emit trust outcomes."""
    diag = case.adapter_expected_output.get("diagnostic_summary")
    if not isinstance(diag, dict):
        return []
    for field in TRUST_VERDICT_FIELDS:
        if field in diag:
            return [
                _issue(
                    f"{_prefix(case)}.diagnostic_summary",
                    f"F7: diagnostic must not contain {field!r}",
                )
            ]
    return []


def _guard_f8(case: FixtureCase) -> list[ValidationIssue]:
    """F8: calibration signal must not override declared estimand on evidence."""
    spec_decl = case.spec.get("declared_estimand_id")
    if not spec_decl:
        return []
    evidence = case.adapter_expected_output.get("experiment_evidence") or {}
    ev_decl = evidence.get("declared_estimand_id")
    if ev_decl is not None and ev_decl != spec_decl:
        binding = case.calibration_signal_binding or {}
        cal_id = binding.get("expected_calibration_estimand_id")
        if cal_id and ev_decl == cal_id and ev_decl != spec_decl:
            return []
        return [
            _issue(
                _prefix(case),
                f"F8: evidence declared_estimand_id {ev_decl!r} "
                f"!= spec {spec_decl!r}",
            )
        ]
    return []


def _guard_f9(case: FixtureCase) -> list[ValidationIssue]:
    """F9: trust verdicts only on TrustReport scenarios, not adapter/evidence."""
    issues: list[ValidationIssue] = []
    _walk_forbidden_verdict_fields(
        case.adapter_expected_output,
        path=f"{_prefix(case)}.adapter_expected_output",
        issues=issues,
    )
    return [
        _issue(i.path, f"F9: {i.message}") if not i.message.startswith("F9:") else i
        for i in issues
    ]


def _guard_f10(case: FixtureCase) -> list[ValidationIssue]:
    """F10: A/B aggregation drift must not hide identical declared/exported IDs."""
    facts = case.adapter_expected_output.get("alignment_facts") or {}
    if not facts.get("aggregation_divergence_detected"):
        return []
    evidence = case.adapter_expected_output.get("experiment_evidence") or {}
    declared = evidence.get("declared_estimand_id")
    exported = evidence.get("exported_estimand_id")
    if declared and exported and declared == exported:
        return [
            _issue(
                _prefix(case),
                "F10: aggregation_divergence_detected but "
                "declared_estimand_id == exported_estimand_id",
            )
        ]
    return []


def _guard_f11(case: FixtureCase) -> list[ValidationIssue]:
    """F11: cross-modality OC — geo fixtures must stay in geo namespace."""
    modality = case.spec.get("modality")
    evidence = case.adapter_expected_output.get("experiment_evidence") or {}
    for field in ("declared_estimand_id", "exported_estimand_id", "measurement_instrument_id"):
        val = evidence.get(field)
        if isinstance(val, str) and val and not val.startswith(f"{modality}."):
            return [
                _issue(
                    _prefix(case),
                    f"F11: {field} {val!r} outside modality namespace {modality!r}",
                )
            ]
    return []


def _guard_f12(case: FixtureCase) -> list[ValidationIssue]:
    """F12: config alias alone is not a canonical instrument ID."""
    if case.export_status != "complete":
        return []
    evidence = case.adapter_expected_output.get("experiment_evidence") or {}
    inst = evidence.get("measurement_instrument_id")
    alias = evidence.get("config_alias") or case.run_artifacts_stub.get("config_alias")
    if inst and alias and inst == alias:
        return [
            _issue(
                _prefix(case),
                "F12: measurement_instrument_id must not equal config_alias",
            )
        ]
    return []


FORBIDDEN_GUARDS: dict[str, ForbiddenGuard] = {
    "F1": _guard_f1,
    "F2": _guard_f2,
    "F3": _guard_f3,
    "F4": _guard_f4,
    "F5": _guard_f5,
    "F6": _guard_f6,
    "F7": _guard_f7,
    "F8": _guard_f8,
    "F9": _guard_f9,
    "F10": _guard_f10,
    "F11": _guard_f11,
    "F12": _guard_f12,
}


def _validate_forbidden_regressions(
    case: FixtureCase, prefix: str
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for ref in case.forbidden_regressions:
        if ref not in FORBIDDEN_REGRESSION_IDS:
            issues.append(_issue(prefix, f"unknown forbidden regression {ref!r}"))
            continue
        guard = FORBIDDEN_GUARDS.get(ref)
        if guard:
            issues.extend(guard(case))
    return issues


def validate_all_track_b_contracts() -> ValidationResult:
    """Validate manifest, all fixture documents, and every executable case."""
    issues: list[ValidationIssue] = []
    issues.extend(validate_manifest())

    seen_files: set[str] = set()
    for entry in _cf.iter_manifest_entries():
        filename = entry["file"]
        if filename not in seen_files:
            seen_files.add(filename)
            issues.extend(validate_fixture_document(filename))

    for case in _cf.iter_all_fixture_cases():
        issues.extend(validate_contract_case(case))

    return ValidationResult(issues=issues)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Track B contract golden fixtures (B5d)."
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Validate manifest index only (skip per-case bundle checks).",
    )
    args = parser.parse_args(argv)

    if args.manifest_only:
        issues = validate_manifest()
        result = ValidationResult(issues=issues)
    else:
        result = validate_all_track_b_contracts()

    if result.ok:
        print("Track B contract validation: OK")
        return 0

    print("Track B contract validation: FAILED", file=sys.stderr)
    print(result.format_messages(), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
