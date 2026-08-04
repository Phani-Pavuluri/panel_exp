import hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).parents[1]; MAN=ROOT/'fixtures/geox_calibration_handoff_sources/v1/manifest.json'; SCRIPT=ROOT.parent/'scripts/build_geox_calibration_source_manifest.py'; SRC=ROOT/'fixtures/geox_governed_readouts'
def test_manifest_has_exact_cases_and_sorted_identity():
 d=json.loads(MAN.read_text()); assert d['case_count']==12; ids=[x['fixture_id'] for x in d['records']]; assert ids==sorted(ids); assert len(set(ids))==12
def test_paths_checksums_and_provenance():
 d=json.loads(MAN.read_text());
 for r in d['records']:
  assert r['evidence_artifact_id']==f"geox-evidence-{r['fixture_id']}-v1"; assert r['source_readout_id']==r['source_readout']['readout_id']; assert r['source_fixture_checkpoint_sha'] if 'source_fixture_checkpoint_sha' in r else True
  for p,k in ((r['governed_readout_path'],'governed_readout_sha256'),(r['source_truth_path'],'source_truth_sha256'),(r['replay_path'],'replay_sha256')): assert hashlib.sha256((SRC/p).read_bytes()).hexdigest()==r[k]
def test_generation_is_byte_identical_and_source_unchanged(tmp_path):
 before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file()}; a=tmp_path/'a.json'; b=tmp_path/'b.json'; subprocess.run([sys.executable,str(SCRIPT),'--output',str(a)],check=True); subprocess.run([sys.executable,str(SCRIPT),'--output',str(b)],check=True); assert a.read_bytes()==b.read_bytes()==MAN.read_bytes(); assert before=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.rglob('*') if p.is_file()}
