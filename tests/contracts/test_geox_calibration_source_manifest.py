import copy
import json
import shutil
import sys
import types
from pathlib import Path

import pytest

package = types.ModuleType('panel_exp')
package.__path__ = [str(Path(__file__).parents[2] / 'panel_exp')]
contracts = types.ModuleType('panel_exp.contracts')
contracts.__path__ = [str(Path(__file__).parents[2] / 'panel_exp/contracts')]
sys.modules.setdefault('panel_exp', package)
sys.modules.setdefault('panel_exp.contracts', contracts)

from panel_exp.contracts.geox_calibration_source_manifest import (
    GeoXCalibrationSourceManifestValidationError,
    load_and_validate_geox_calibration_source_manifest,
    validate_geox_calibration_source_manifest,
    validate_geox_calibration_source_manifest_sources,
)

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / 'fixtures/geox_calibration_handoff_sources/v1/manifest.json'
SOURCE_ROOT = ROOT / 'fixtures/geox_governed_readouts'

def payload():
    return json.loads(MANIFEST.read_text())

def test_committed_manifest_intrinsic_and_contextual_valid():
    value = payload()
    assert validate_geox_calibration_source_manifest(value) == ()
    assert validate_geox_calibration_source_manifest_sources(value, source_root=SOURCE_ROOT) == ()

def test_loader_returns_payload_and_typed_errors():
    assert load_and_validate_geox_calibration_source_manifest(MANIFEST, source_root=SOURCE_ROOT)['case_count'] == 12
    bad = payload(); bad.pop('records')
    with pytest.raises(GeoXCalibrationSourceManifestValidationError) as exc:
        load_and_validate_geox_calibration_source_manifest(MANIFEST, source_root=SOURCE_ROOT.parent / 'missing')
    assert isinstance(exc.value.errors, tuple)
    assert 'manifest:missing_key:records' in validate_geox_calibration_source_manifest(bad)

def test_top_level_and_record_shape_errors_are_deterministic():
    value = payload(); value['extra'] = True
    assert 'manifest:extra_key:extra' in validate_geox_calibration_source_manifest(value)
    value = payload(); value['records'][0].pop('fixture_id')
    assert 'record:0:missing_key:fixture_id' in validate_geox_calibration_source_manifest(value)

def test_authorization_and_timestamp_rules():
    value = payload(); value['records'][0]['authorization_flags']['assignment'] = True
    assert any('unsafe_authorization' in e for e in validate_geox_calibration_source_manifest(value))
    value = payload(); value['records'][0]['freshness_status'] = 'unknown'
    assert any('freshness_status' in e for e in validate_geox_calibration_source_manifest(value))

def test_source_path_checksum_and_field_mismatch():
    value = payload(); value['records'][0]['governed_readout_path'] = '../escape.json'
    assert 'source:geox_truth_bayesian_tbr_research_only_001:field_mismatch:governed_readout_path' in validate_geox_calibration_source_manifest_sources(value, source_root=SOURCE_ROOT)
    value = payload(); value['records'][0]['governed_readout_sha256'] = '0' * 64
    assert any('checksum_mismatch:governed_readout' in e for e in validate_geox_calibration_source_manifest_sources(value, source_root=SOURCE_ROOT))

def test_validation_does_not_mutate_payload():
    value = payload(); before = copy.deepcopy(value)
    validate_geox_calibration_source_manifest_sources(value, source_root=SOURCE_ROOT)
    assert value == before

@pytest.mark.parametrize('freshness', [[], {}, 1, True, None, 'unknown'])
def test_invalid_freshness_values_return_reason_tuple(freshness):
    value = payload()
    value['records'][0]['freshness_status'] = freshness
    errors = validate_geox_calibration_source_manifest(value)
    assert isinstance(errors, tuple)
    assert any('freshness_status' in error for error in errors)

def copied_source(tmp_path):
    target = tmp_path / 'source'
    shutil.copytree(SOURCE_ROOT, target)
    return target

def test_path_mismatch_short_circuits_reads(tmp_path, monkeypatch):
    value = payload(); value['records'][0]['replay_path'] = 'wrong/replay.json'
    calls = []
    original = Path.read_bytes
    def fail_if_called(path):
        calls.append(str(path))
        return original(path)
    monkeypatch.setattr(Path, 'read_bytes', fail_if_called)
    errors = validate_geox_calibration_source_manifest_sources(value, source_root=copied_source(tmp_path))
    assert errors == ('source:geox_truth_bayesian_tbr_research_only_001:field_mismatch:replay_path',)
    assert not any('geox_truth_bayesian_tbr_research_only_001' in path for path in calls)

@pytest.mark.parametrize('kind', ['governed_readout', 'source_truth', 'replay'])
def test_invalid_json_is_source_specific(tmp_path, kind):
    root = copied_source(tmp_path)
    case = payload()['records'][0]['fixture_id']
    (root / payload()['records'][0][kind + '_path']).write_text('{invalid')
    errors = validate_geox_calibration_source_manifest_sources(payload(), source_root=root)
    assert f'source:{case}:invalid_json:{kind}' in errors

@pytest.mark.parametrize('kind', ['governed_readout', 'source_truth', 'replay'])
def test_non_object_json_is_source_specific(tmp_path, kind):
    root = copied_source(tmp_path)
    case = payload()['records'][0]['fixture_id']
    (root / payload()['records'][0][kind + '_path']).write_text('[]')
    errors = validate_geox_calibration_source_manifest_sources(payload(), source_root=root)
    assert f'source:{case}:non_object_json:{kind}' in errors

@pytest.mark.parametrize('field', ['dataset_version', 'truth_version'])
def test_optional_source_truth_identity_mismatch(tmp_path, field):
    root = copied_source(tmp_path)
    record = payload()['records'][0]
    truth_path = root / record['source_truth_path']
    truth = json.loads(truth_path.read_text()); truth[field] = 'different'
    truth_path.write_text(json.dumps(truth))
    errors = validate_geox_calibration_source_manifest_sources(payload(), source_root=root)
    assert f"source:{record['fixture_id']}:source_truth_mismatch:{field}" in errors

@pytest.mark.parametrize('field,value', [
    ('case_count', True), ('case_count', 12.0),
    ('synthetic_fixture_time_scope', 1), ('mmm_compatibility_emitted', 0),
    ('calibration_signal_emitted', 0), ('production_authorized', 0),
    ('schema_version', 1), ('record_version', False),
])
def test_top_level_type_rejections(field, value):
    data = payload(); data[field] = value
    assert any('manifest:invalid_value:' + field in error for error in validate_geox_calibration_source_manifest(data))

@pytest.mark.parametrize('field', ['time_window_start', 'time_window_end', 'produced_at', 'freshness_evaluated_at'])
def test_timestamp_mapping_rejections(field):
    data = payload(); data['records'][0][field] = '2020-01-01T00:00:00Z'
    assert any('invalid_timestamp:' + field in error for error in validate_geox_calibration_source_manifest(data))

@pytest.mark.parametrize('field', ['effect_estimate', 'absolute_lift', 'relative_lift', 'incremental_outcome', 'standard_error'])
def test_nullable_numeric_bool_rejected(field):
    data = payload(); data['records'][0][field] = True
    assert any('invalid_type:' + field in error for error in validate_geox_calibration_source_manifest(data))

@pytest.mark.parametrize('kind', ['governed_readout', 'source_truth', 'replay'])
def test_source_path_mismatch_is_reported(kind):
    data = payload(); data['records'][0][kind + '_path'] = 'missing.json'
    errors = validate_geox_calibration_source_manifest_sources(data, source_root=SOURCE_ROOT)
    assert any('field_mismatch:' + kind + '_path' in error for error in errors)

@pytest.mark.parametrize('field', ['mip_handoff_expectation', 'lineage', 'provenance', 'replay_metadata', 'authorization_flags'])
def test_nested_schema_rejection(field):
    data = payload(); data['records'][0][field] = {}
    assert any('invalid_type:' + field in error or 'prohibited_key' in error for error in validate_geox_calibration_source_manifest(data))
