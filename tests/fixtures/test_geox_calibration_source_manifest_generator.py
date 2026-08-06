import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
MAN = ROOT / 'fixtures/geox_calibration_handoff_sources/v1/manifest.json'
SCRIPT = ROOT.parent / 'scripts/build_geox_calibration_source_manifest.py'
SRC = ROOT / 'fixtures/geox_governed_readouts'

def test_manifest_shape_and_safety():
    data = json.loads(MAN.read_text())
    assert data['case_count'] == 12
    assert data['mmm_compatibility_emitted'] is False
    assert data['production_authorized'] is False
    assert len(data['records']) == 12
    expected = set(__import__('runpy').run_path(str(SCRIPT))['FIELDS'])
    for record in data['records']:
        assert set(record) == expected
        assert all(value is False for value in record['authorization_flags'].values())
        assert not {'source_readout','source_replay','calibration_compatibility','method_eligibility_status','compatibility_status','target_model_id','calibration_weight','calibration_signal','trust_report','decision_surface','recommendation','optimization'} & set(record)

def test_paths_checksums_ids_and_timestamps():
    data = json.loads(MAN.read_text())
    for record in data['records']:
        assert record['evidence_artifact_id'] == f"geox-evidence-{record['fixture_id']}-v1"
        for kind in ('governed_readout', 'source_truth', 'replay'):
            path = SRC / record[f'{kind}_path']
            assert path.is_file()
            assert record[f'{kind}_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
        if record['freshness_status'] == 'fresh':
            assert (record['time_window_start'], record['time_window_end'], record['produced_at']) == ('2025-01-06T00:00:00Z','2025-03-30T23:59:59Z','2025-03-31T00:00:00Z')
        else:
            assert (record['time_window_start'], record['time_window_end'], record['produced_at']) == ('2024-01-08T00:00:00Z','2024-03-31T23:59:59Z','2024-04-01T00:00:00Z')

def test_representative_source_values_preserved():
    for record in json.loads(MAN.read_text())['records']:
        readout = json.loads((SRC / record['governed_readout_path']).read_text())
        truth = json.loads((SRC / record['source_truth_path']).read_text())
        for key in ('kpi','kpi_units','estimand','effect_scale','effect_estimate','uncertainty_available','method_family','method_status','instrument_id','design_type','feasibility_status','readout_status','freshness_status','warnings','blocked_reasons','failure_reasons','lineage','provenance','replay_metadata','producer_package_version','producer_commit','authorization_flags'):
            assert record[key] == readout[key]
        for key in ('fixture_class','certification_status','mip_handoff_expectation'):
            assert record[key] == truth[key]

def test_deterministic_and_source_immutable(tmp_path):
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file()}
    first, second = tmp_path / 'a.json', tmp_path / 'b.json'
    env = os.environ.copy()
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    subprocess.run([sys.executable, str(SCRIPT), '--output', str(first)], cwd=tmp_path, env=env, check=True)
    subprocess.run([sys.executable, str(SCRIPT), '--output', str(second)], cwd=tmp_path, env=env, check=True)
    assert first.read_bytes() == second.read_bytes() == MAN.read_bytes()
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file()}

def _isolated_generator(tmp_path):
    copied = tmp_path / 'source'
    shutil.copytree(SRC, copied)
    spec = importlib.util.spec_from_file_location('calibration_generator', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SRC = copied
    return module, copied

@pytest.mark.parametrize('value', [None, '', 42])
def test_invalid_readout_id_rejected(tmp_path, value):
    module, copied = _isolated_generator(tmp_path)
    path = copied / 'geox_truth_scm_candidate_clean_001' / 'governed_readout.json'
    payload = json.loads(path.read_text())
    if value is None:
        payload.pop('readout_id')
    else:
        payload['readout_id'] = value
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        module.build(tmp_path / 'out.json')

def test_manifest_flags_and_paths_rejected(tmp_path):
    module, copied = _isolated_generator(tmp_path)
    manifest = copied / 'manifest.json'
    payload = json.loads(manifest.read_text())
    payload['production_authorized'] = True
    manifest.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        module.build(tmp_path / 'flags.json')

    module, copied = _isolated_generator(tmp_path / 'paths')
    manifest = copied / 'manifest.json'
    payload = json.loads(manifest.read_text())
    payload['cases'][0]['governed_readout'] = '/etc/passwd'
    manifest.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        module.build(tmp_path / 'absolute.json')
