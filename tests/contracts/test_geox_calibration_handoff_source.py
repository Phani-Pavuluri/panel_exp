import hashlib, json, subprocess, sys
from pathlib import Path
from panel_exp.contracts.geox_calibration_handoff_source import GeoXCalibrationHandoffSourceRecord, SOURCE_COMMIT
ROOT=Path(__file__).parents[2]; MAN=ROOT/'tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json'
def test_manifest_has_all_cases_and_strict_records():
 data=json.loads(MAN.read_text()); assert len(data['records'])==12
 for raw in data['records']:
  r=GeoXCalibrationHandoffSourceRecord.from_dict(raw); assert not r.validate(); assert r.source_commit==SOURCE_COMMIT; assert r.handoff_source_id.endswith('-v1'); assert not any(r.payload.get('authorization_flags',{}).values())
def test_checksums_and_paths_are_exact():
 data=json.loads(MAN.read_text())
 for raw in data['records']:
  base=ROOT/'tests/fixtures/geox_governed_readouts'/raw['fixture_id']
  for key,path in [('governed_readout_sha256',raw['governed_readout_path']),('source_truth_sha256',raw['source_truth_path']),('replay_sha256',raw['replay_path'])]: assert raw[key]==hashlib.sha256((ROOT/'tests/fixtures/geox_governed_readouts'/path).read_bytes()).hexdigest()
def test_generation_is_byte_identical():
 before=MAN.read_bytes(); subprocess.run([sys.executable,str(ROOT/'scripts/build_geox_calibration_handoff_source_fixtures.py')],cwd=ROOT,check=True); assert MAN.read_bytes()==before
def test_temporal_and_eligibility_are_closed():
 for raw in json.loads(MAN.read_text())['records']:
  assert raw['synthetic_fixture_time_scope']; assert raw['time_window_start']<raw['time_window_end']<=raw['produced_at']<=raw['freshness_evaluated_at']; assert raw['method_eligibility_status'] in {'candidate','diagnostic_only','research_only','blocked','unsupported'}
