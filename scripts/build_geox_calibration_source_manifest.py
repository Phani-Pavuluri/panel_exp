import argparse, hashlib, json
from pathlib import Path

ROOT=Path(__file__).parents[1]; SRC=ROOT/'tests/fixtures/geox_governed_readouts'; DEFAULT=ROOT/'tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json'
CASES={"geox_truth_bayesian_tbr_research_only_001","geox_truth_calibration_incompatible_001","geox_truth_conflicting_evidence_001","geox_truth_did_candidate_warning_001","geox_truth_infeasible_preperiod_001","geox_truth_multicell_shared_control_block_001","geox_truth_safe_blocked_readout_001","geox_truth_scm_candidate_clean_001","geox_truth_stale_incompatible_evidence_001","geox_truth_tbrridge_diagnostic_only_001","geox_truth_unsupported_inference_001","geox_truth_weak_matchability_001"}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(root, rel):
 p=Path(rel)
 if p.is_absolute() or '..' in p.parts: raise ValueError('unsafe path')
 q=(root/p).resolve()
 if root.resolve() not in q.parents or not q.is_file(): raise ValueError('invalid source path')
 return q
def build(output=DEFAULT):
 m=json.loads((SRC/'manifest.json').read_text()); cases=[c['case_id'] for c in m['cases']]
 if set(cases)!=CASES or len(cases)!=12: raise ValueError('source cases mismatch')
 records=[]
 for c in sorted(m['cases'],key=lambda x:x['case_id']):
  fid=c['case_id']; d=SRC/fid; r=json.loads((d/'governed_readout.json').read_text()); truth=json.loads((d/'source_truth.json').read_text()); replay=json.loads((d/'replay.json').read_text())
  paths={k:resolve(SRC,c[k]) for k in ('governed_readout','source_truth','replay')}
  rec={'fixture_id':fid,'evidence_artifact_id':f'geox-evidence-{fid}-v1','source_readout_id':r['readout_id'],'experiment_id':r['experiment_id'],'dataset_version':r['dataset_version'],'truth_version':r['truth_version'],'governed_readout_path':c['governed_readout'],'source_truth_path':c['source_truth'],'replay_path':c['replay'],'governed_readout_sha256':sha(paths['governed_readout']),'source_truth_sha256':sha(paths['source_truth']),'replay_sha256':sha(paths['replay']),'fixture_class':truth['fixture_class'],'certification_status':truth['certification_status'],'mip_handoff_expectation':truth['mip_handoff_expectation'],'source_readout':r,'source_replay':replay,'time_window_start':'2025-01-06T00:00:00Z' if r['freshness_status']=='fresh' else '2024-01-08T00:00:00Z','time_window_end':'2025-03-30T23:59:59Z' if r['freshness_status']=='fresh' else '2024-03-31T23:59:59Z','produced_at':'2025-03-31T00:00:00Z' if r['freshness_status']=='fresh' else '2024-04-01T00:00:00Z','freshness_evaluated_at':'2025-04-01T00:00:00Z','synthetic_fixture_time_scope':True}
  records.append(rec)
 out={'schema_version':'geox_calibration_source_manifest_v1','record_version':'1.0.0','case_count':12,'source_repository':'Phani-Pavuluri/panel_exp','source_fixture_checkpoint_sha':'860182386c39f487747de5f43e67a31e9978e57c','source_tree_base_sha':'7f829395bc305550ea1311421a4181dafed795b8','synthetic_fixture_time_scope':True,'mmm_compatibility_emitted':False,'calibration_signal_emitted':False,'production_authorized':False,'records':records}
 Path(output).parent.mkdir(parents=True,exist_ok=True); Path(output).write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=DEFAULT); build(ap.parse_args().output)
