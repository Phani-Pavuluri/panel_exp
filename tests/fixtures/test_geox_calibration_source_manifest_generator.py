import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).parents[1]; MAN=ROOT/'fixtures/geox_calibration_handoff_sources/v1/manifest.json'; SCRIPT=ROOT.parent/'scripts/build_geox_calibration_source_manifest.py'; SRC=ROOT/'fixtures/geox_governed_readouts'
def test_exact_cases_and_shape():
 d=json.loads(MAN.read_text()); assert set(d)=={'schema_version','record_version','case_count','source_repository','source_fixture_checkpoint_sha','source_tree_base_sha','synthetic_fixture_time_scope','mmm_compatibility_emitted','calibration_signal_emitted','production_authorized','records'}; assert d['case_count']==12; assert len(d['records'])==12; assert all('source_readout' not in r and 'source_replay' not in r for r in d['records'])
def test_paths_checksums_and_ids():
 for r in json.loads(MAN.read_text())['records']:
  assert r['evidence_artifact_id']==f"geox-evidence-{r['fixture_id']}-v1"
  for k in ('governed_readout','source_truth','replay'):
   p=SRC/r[f'{k}_path']; assert p.is_file(); assert r[f'{k}_sha256']==hashlib.sha256(p.read_bytes()).hexdigest()
def test_deterministic_and_source_immutable(tmp_path):
 before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file()}; a=tmp_path/'a'; b=tmp_path/'b'; subprocess.run([sys.executable,str(SCRIPT),'--output',str(a)],check=True); subprocess.run([sys.executable,str(SCRIPT),'--output',str(b)],check=True); assert a.read_bytes()==b.read_bytes()==MAN.read_bytes(); assert before=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file()}
