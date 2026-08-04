import json, importlib.util
from pathlib import Path
ROOT=Path(__file__).parents[1]
_spec=importlib.util.spec_from_file_location('geox_source',ROOT/'panel_exp/contracts/geox_calibration_handoff_source.py'); _mod=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
GeoXCalibrationHandoffSourceRecord=_mod.GeoXCalibrationHandoffSourceRecord; SOURCE_COMMIT=_mod.SOURCE_COMMIT; checksum=_mod.checksum
FIX=ROOT/'tests/fixtures/geox_governed_readouts'; OUT=ROOT/'tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json'
def build():
 manifest=json.loads((FIX/'manifest.json').read_text()); records=[]
 for case in manifest['cases']:
  fid=case['case_id']; d=FIX/fid; read=json.loads((d/'governed_readout.json').read_text());
  payload=read.copy(); status=read.get('readout_status','blocked'); method=read.get('method_status',''); elig='unsupported' if 'unsupported' in method else ('research_only' if 'research' in method else ('diagnostic_only' if 'diagnostic' in method else ('blocked' if status in {'blocked','failed'} else 'candidate')))
  rec=GeoXCalibrationHandoffSourceRecord('1.0','1.0',f'geox-calibration-handoff-{fid}-v1',f'geox-evidence-{fid}-v1',fid,read['readout_id'],read['experiment_id'],read['dataset_version'],read['truth_version'],SOURCE_COMMIT,'Phani-Pavuluri/panel_exp','ef6a57382831210c085b4c1351358c3a0743be5e',case['governed_readout'],case['source_truth'],case['replay'],checksum(d/'governed_readout.json'),checksum(d/'source_truth.json'),checksum(d/'replay.json'),read['method_family'],method,read['instrument_id'],read['design_type'],read['feasibility_status'],elig,status,read['handoff_eligibility_status'],read['freshness_status'],'2024-01-01T00:00:00Z','2024-01-31T00:00:00Z','2024-02-01T00:00:00Z','2024-02-01T00:00:00Z',True,payload)
  if rec.validate(): raise ValueError(rec.validate())
  records.append(rec.to_dict())
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps({'schema_version':'1.0','source_commit':SOURCE_COMMIT,'records':records},sort_keys=True,indent=2)+'\n')
if __name__=='__main__': build()
