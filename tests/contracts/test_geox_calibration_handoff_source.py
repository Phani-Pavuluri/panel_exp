import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).parents[2]; MAN=ROOT/'tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json'
def test_manifest_exactly_twelve_and_deterministic():
 before=MAN.read_bytes(); data=json.loads(before); assert len(data['records'])==12; subprocess.run([sys.executable,str(ROOT/'scripts/build_geox_calibration_handoff_source_manifest.py')],cwd=ROOT,check=True); assert MAN.read_bytes()==before
def test_identity_and_provenance():
 for r in json.loads(MAN.read_text())['records']:
  assert r['handoff_source_id']==f"geox-calibration-source-{r['fixture_id']}-v1"; assert r['evidence_artifact_id']==f"geox-evidence-{r['fixture_id']}-v1"; assert len(r['source_fixture_checkpoint_sha'])==40; assert all(not v for v in r['authorization_flags'].values())
def test_temporal_scope_and_paths():
 for r in json.loads(MAN.read_text())['records']:
  assert r['synthetic_fixture_time_scope']; assert r['time_window_start']<r['time_window_end']<=r['produced_at']<=r['freshness_evaluated_at']; assert not Path(r['governed_readout_path']).is_absolute()
