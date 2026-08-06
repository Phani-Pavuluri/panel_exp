import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from panel_exp.contracts.geox_calibration_source_manifest import (
    GeoXCalibrationSourceManifestValidationError,
    load_and_validate_geox_calibration_source_manifest,
    validate_geox_calibration_source_manifest,
    validate_geox_calibration_source_manifest_sources,
)

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "fixtures/geox_calibration_handoff_sources/v1/manifest.json"
SOURCE_ROOT = ROOT / "fixtures/geox_governed_readouts"


def payload():
    return json.loads(MANIFEST.read_text())


def test_committed_manifest_intrinsic_and_contextual_valid():
    value = payload()
    assert validate_geox_calibration_source_manifest(value) == ()
    assert (
        validate_geox_calibration_source_manifest_sources(
            value, source_root=SOURCE_ROOT
        )
        == ()
    )


def test_loader_returns_payload_and_typed_errors():
    assert (
        load_and_validate_geox_calibration_source_manifest(
            MANIFEST, source_root=SOURCE_ROOT
        )["case_count"]
        == 12
    )
    bad = payload()
    bad.pop("records")
    with pytest.raises(GeoXCalibrationSourceManifestValidationError) as exc:
        load_and_validate_geox_calibration_source_manifest(
            MANIFEST, source_root=SOURCE_ROOT.parent / "missing"
        )
    assert isinstance(exc.value.errors, tuple)
    assert "manifest:missing_key:records" in validate_geox_calibration_source_manifest(
        bad
    )


def test_top_level_and_record_shape_errors_are_deterministic():
    value = payload()
    value["extra"] = True
    assert "manifest:extra_key:extra" in validate_geox_calibration_source_manifest(
        value
    )
    value = payload()
    value["records"][0].pop("fixture_id")
    assert (
        "record:0:missing_key:fixture_id"
        in validate_geox_calibration_source_manifest(value)
    )


def test_authorization_and_timestamp_rules():
    value = payload()
    value["records"][0]["authorization_flags"]["assignment"] = True
    assert any(
        "unsafe_authorization" in e
        for e in validate_geox_calibration_source_manifest(value)
    )
    value = payload()
    value["records"][0]["freshness_status"] = "unknown"
    assert any(
        "freshness_status" in e
        for e in validate_geox_calibration_source_manifest(value)
    )


def test_source_path_checksum_and_field_mismatch():
    value = payload()
    value["records"][0]["governed_readout_path"] = "../escape.json"
    assert (
        "source:geox_truth_bayesian_tbr_research_only_001:field_mismatch:governed_readout_path"
        in validate_geox_calibration_source_manifest_sources(
            value, source_root=SOURCE_ROOT
        )
    )
    value = payload()
    value["records"][0]["governed_readout_sha256"] = "0" * 64
    assert any(
        "checksum_mismatch:governed_readout" in e
        for e in validate_geox_calibration_source_manifest_sources(
            value, source_root=SOURCE_ROOT
        )
    )


def test_validation_does_not_mutate_payload():
    value = payload()
    before = copy.deepcopy(value)
    validate_geox_calibration_source_manifest_sources(value, source_root=SOURCE_ROOT)
    assert value == before


def test_isolated_installed_package_validator_probe(tmp_path):
    probe = """
import panel_exp
from panel_exp.contracts.geox_calibration_source_manifest import load_and_validate_geox_calibration_source_manifest
from pathlib import Path
root = Path.cwd()
manifest = root / 'tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json'
source = root / 'tests/fixtures/geox_governed_readouts'
loaded = load_and_validate_geox_calibration_source_manifest(manifest, source_root=source)
assert loaded['case_count'] == 12
print(panel_exp.__file__)
"""
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    result = subprocess.run(
        [sys.executable, "-I", "-c", probe],
        cwd=ROOT.parent,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert str(ROOT.parent / "panel_exp") in result.stdout


@pytest.mark.parametrize("freshness", [[], {}, 1, True, None, "unknown"])
def test_invalid_freshness_values_return_reason_tuple(freshness):
    value = payload()
    value["records"][0]["freshness_status"] = freshness
    errors = validate_geox_calibration_source_manifest(value)
    assert isinstance(errors, tuple)
    assert any("freshness_status" in error for error in errors)


def _mutated_case(tmp_path, kind, mutate):
    root = copied_source(tmp_path)
    value = payload()
    record = value["records"][0]
    path = root / record[kind + "_path"]
    data = json.loads(path.read_text())
    mutate(data)
    path.write_text(json.dumps(data))
    record[kind + "_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return value, root, record


def test_loader_malformed_json_and_intrinsic_error(tmp_path):
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{bad")
    with pytest.raises(GeoXCalibrationSourceManifestValidationError) as exc:
        load_and_validate_geox_calibration_source_manifest(
            malformed, source_root=SOURCE_ROOT
        )
    assert exc.value.errors == ("manifest:invalid_json",)
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps({"case_count": 1}))
    with pytest.raises(GeoXCalibrationSourceManifestValidationError) as exc:
        load_and_validate_geox_calibration_source_manifest(
            invalid, source_root=SOURCE_ROOT
        )
    assert "manifest:invalid_value:case_count" in exc.value.errors
    assert "manifest:missing_key:records" in exc.value.errors


def test_source_manifest_duplicate_case_and_malformed_case(tmp_path):
    root = copied_source(tmp_path)
    source_manifest = root / "manifest.json"
    data = json.loads(source_manifest.read_text())
    data["cases"][1]["case_id"] = data["cases"][0]["case_id"]
    source_manifest.write_text(json.dumps(data))
    errors = validate_geox_calibration_source_manifest_sources(
        payload(), source_root=root
    )
    assert "source:manifest:case_set_mismatch" in errors
    root = copied_source(tmp_path / "malformed")
    source_manifest = root / "manifest.json"
    data = json.loads(source_manifest.read_text())
    data["cases"][0] = {}
    source_manifest.write_text(json.dumps(data))
    assert (
        "source:manifest:invalid_case"
        in validate_geox_calibration_source_manifest_sources(
            payload(), source_root=root
        )
    )


def test_unsafe_declared_path_matching_is_rejected(tmp_path):
    root = copied_source(tmp_path)
    source_manifest = root / "manifest.json"
    data = json.loads(source_manifest.read_text())
    data["cases"][0]["replay"] = "../escape.json"
    source_manifest.write_text(json.dumps(data))
    value = payload()
    value["records"][0]["replay_path"] = "../escape.json"
    assert (
        "source:geox_truth_bayesian_tbr_research_only_001:unsafe_path:replay"
        in validate_geox_calibration_source_manifest_sources(value, source_root=root)
    )


@pytest.mark.parametrize(
    "kind,mutate,reason",
    [
        ("governed_readout", lambda d: d.pop("readout_id"), "deserialization_failure"),
        (
            "governed_readout",
            lambda d: d.update(readout_status="not-a-status"),
            "invalid_governed_readout",
        ),
        ("governed_readout", lambda d: d.update(kpi="different"), "field_mismatch:kpi"),
    ],
)
def test_governed_readout_failures(tmp_path, kind, mutate, reason):
    value, root, record = _mutated_case(tmp_path, kind, mutate)
    errors = validate_geox_calibration_source_manifest_sources(value, source_root=root)
    assert f"source:{record['fixture_id']}:{reason}" in errors


@pytest.mark.parametrize(
    "field",
    ["fixture_id", "fixture_class", "certification_status", "mip_handoff_expectation"],
)
def test_source_truth_mismatch(tmp_path, field):
    value, root, record = _mutated_case(
        tmp_path, "source_truth", lambda d: d.update({field: "different"})
    )
    assert (
        f"source:{record['fixture_id']}:source_truth_mismatch:{field}"
        in validate_geox_calibration_source_manifest_sources(value, source_root=root)
    )


@pytest.mark.parametrize(
    "field,value,reason",
    [("case_id", "different", "case_id"), ("deterministic", False, "deterministic")],
)
def test_replay_mismatch(tmp_path, field, value, reason):
    data = payload()
    record = data["records"][0]
    root = copied_source(tmp_path)
    path = root / record["replay_path"]
    replay = json.loads(path.read_text())
    replay[field] = value
    path.write_text(json.dumps(replay))
    record["replay_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert (
        f"source:{record['fixture_id']}:replay_mismatch:{reason}"
        in validate_geox_calibration_source_manifest_sources(data, source_root=root)
    )


def test_invalid_payload_error_order_is_deterministic():
    value = payload()
    value["records"][0]["freshness_status"] = []
    assert validate_geox_calibration_source_manifest(
        value
    ) == validate_geox_calibration_source_manifest(copy.deepcopy(value))


def copied_source(tmp_path):
    target = tmp_path / "source"
    shutil.copytree(SOURCE_ROOT, target)
    return target


def test_path_mismatch_short_circuits_reads(tmp_path, monkeypatch):
    value = payload()
    value["records"][0]["replay_path"] = "wrong/replay.json"
    calls = []
    original = Path.read_bytes

    def fail_if_called(path):
        calls.append(str(path))
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", fail_if_called)
    errors = validate_geox_calibration_source_manifest_sources(
        value, source_root=copied_source(tmp_path)
    )
    assert errors == (
        "source:geox_truth_bayesian_tbr_research_only_001:field_mismatch:replay_path",
    )
    assert not any(
        "geox_truth_bayesian_tbr_research_only_001" in path for path in calls
    )


@pytest.mark.parametrize("kind", ["governed_readout", "source_truth", "replay"])
def test_invalid_json_is_source_specific(tmp_path, kind):
    root = copied_source(tmp_path)
    case = payload()["records"][0]["fixture_id"]
    (root / payload()["records"][0][kind + "_path"]).write_text("{invalid")
    errors = validate_geox_calibration_source_manifest_sources(
        payload(), source_root=root
    )
    assert f"source:{case}:invalid_json:{kind}" in errors


@pytest.mark.parametrize("kind", ["governed_readout", "source_truth", "replay"])
def test_non_object_json_is_source_specific(tmp_path, kind):
    root = copied_source(tmp_path)
    case = payload()["records"][0]["fixture_id"]
    (root / payload()["records"][0][kind + "_path"]).write_text("[]")
    errors = validate_geox_calibration_source_manifest_sources(
        payload(), source_root=root
    )
    assert f"source:{case}:non_object_json:{kind}" in errors


@pytest.mark.parametrize("field", ["dataset_version", "truth_version"])
def test_optional_source_truth_identity_mismatch(tmp_path, field):
    root = copied_source(tmp_path)
    record = payload()["records"][0]
    truth_path = root / record["source_truth_path"]
    truth = json.loads(truth_path.read_text())
    truth[field] = "different"
    truth_path.write_text(json.dumps(truth))
    errors = validate_geox_calibration_source_manifest_sources(
        payload(), source_root=root
    )
    assert f"source:{record['fixture_id']}:source_truth_mismatch:{field}" in errors


@pytest.mark.parametrize(
    "field,value",
    [
        ("case_count", True),
        ("case_count", 12.0),
        ("synthetic_fixture_time_scope", 1),
        ("mmm_compatibility_emitted", 0),
        ("calibration_signal_emitted", 0),
        ("production_authorized", 0),
        ("schema_version", 1),
        ("record_version", False),
    ],
)
def test_top_level_type_rejections(field, value):
    data = payload()
    data[field] = value
    assert any(
        "manifest:invalid_value:" + field in error
        for error in validate_geox_calibration_source_manifest(data)
    )


@pytest.mark.parametrize(
    "field",
    ["time_window_start", "time_window_end", "produced_at", "freshness_evaluated_at"],
)
def test_timestamp_mapping_rejections(field):
    data = payload()
    data["records"][0][field] = "2020-01-01T00:00:00Z"
    assert any(
        "invalid_timestamp:" + field in error
        for error in validate_geox_calibration_source_manifest(data)
    )


@pytest.mark.parametrize(
    "field",
    [
        "effect_estimate",
        "absolute_lift",
        "relative_lift",
        "incremental_outcome",
        "standard_error",
    ],
)
def test_nullable_numeric_bool_rejected(field):
    data = payload()
    data["records"][0][field] = True
    assert any(
        "invalid_type:" + field in error
        for error in validate_geox_calibration_source_manifest(data)
    )


@pytest.mark.parametrize("kind", ["governed_readout", "source_truth", "replay"])
def test_source_path_mismatch_is_reported(kind):
    data = payload()
    data["records"][0][kind + "_path"] = "missing.json"
    errors = validate_geox_calibration_source_manifest_sources(
        data, source_root=SOURCE_ROOT
    )
    assert any("field_mismatch:" + kind + "_path" in error for error in errors)


@pytest.mark.parametrize(
    "field",
    [
        "mip_handoff_expectation",
        "lineage",
        "provenance",
        "replay_metadata",
        "authorization_flags",
    ],
)
def test_nested_schema_rejection(field):
    data = payload()
    data["records"][0][field] = {}
    assert any(
        "invalid_type:" + field in error or "prohibited_key" in error
        for error in validate_geox_calibration_source_manifest(data)
    )
