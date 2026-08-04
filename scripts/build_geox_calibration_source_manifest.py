import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).parents[1]; SRC=ROOT/'tests/fixtures/geox_governed_readouts'; DEFAULT=ROOT/'tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json'
CASES={"geox_truth_bayesian_tbr_research_only_001","geox_truth_calibration_incompatible_001","geox_truth_conflicting_evidence_001","geox_truth_did_candidate_warning_001","geox_truth_infeasible_preperiod_001","geox_truth_multicell_shared_control_block_001","geox_truth_safe_blocked_readout_001","geox_truth_scm_candidate_clean_001","geox_truth_stale_incompatible_evidence_001","geox_truth_tbrridge_diagnostic_only_001","geox_truth_unsupported_inference_001","geox_truth_weak_matchability_001"}
FIELDS=('fixture_id','evidence_artifact_id','source_readout_id','experiment_id','dataset_version','truth_version','governed_readout_path','governed_readout_sha256','source_truth_path','source_truth_sha256','replay_path','replay_sha256','fixture_class','certification_status','mip_handoff_expectation','kpi','kpi_units','estimand','effect_scale','channel','tactic','geography_scope','geo_grain','time_window','pre_period','post_period','effect_estimate','absolute_lift','relative_lift','incremental_outcome','uncertainty_available','standard_error','confidence_interval','interval_semantics','method_family','method_status','instrument_id','design_type','feasibility_status','readout_status','freshness_status','handoff_eligibility_status','warnings','blocked_reasons','failure_reasons','lineage','provenance','replay_metadata','producer_package_version','producer_commit','authorization_flags','time_window_start','time_window_end','produced_at','freshness_evaluated_at','synthetic_fixture_time_scope')
def resolve(root, rel):
 p=Path(rel)
 if p.is_absolute() or '..' in p.parts: raise ValueError('unsafe path')
 q=(root/p).resolve()
 if root.resolve() not in q.parents or not q.is_file(): raise ValueError('invalid source path')
 return q
def checksum(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build(output=DEFAULT):
 m=json.loads((SRC/'manifest.json').read_text()); cases=m.get('cases',[]); ids=[c['case_id'] for c in cases]
 if m.get('case_count')!=12 or set(ids)!=CASES or len(ids)!=12: raise ValueError('source manifest cases mismatch')
 records=[]
 for c in sorted(cases,key=lambda x:x['case_id']):
  fid=c['case_id']; paths={k:resolve(SRC,c[k]) for k in ('governed_readout','source_truth','replay')}; r=json.loads(paths['governed_readout'].read_text()); t=json.loads(paths['source_truth'].read_text()); replay=json.loads(paths['replay'].read_text())
  if r['fixture_id']!=fid or t['fixture_id']!=fid or replay['case_id']!=fid: raise ValueError('identity mismatch')
  if r['readout_id'] != r.get('readout_id') or r['experiment_id'] != fid: raise ValueError('readout identity mismatch')
  freshness=r['freshness_status'];
  if freshness not in {'fresh','stale'}: raise ValueError('unsupported freshness')
  fresh=freshness=='fresh'; rec={'fixture_id':fid,'evidence_artifact_id':f'geox-evidence-{fid}-v1','source_readout_id':r['readout_id'],'experiment_id':r['experiment_id'],'dataset_version':r['dataset_version'],'truth_version':r['truth_version'],'governed_readout_path':c['governed_readout'],'governed_readout_sha256':checksum(paths['governed_readout']),'source_truth_path':c['source_truth'],'source_truth_sha256':checksum(paths['source_truth']),'replay_path':c['replay'],'replay_sha256':checksum(paths['replay']),'fixture_class':t['fixture_class'],'certification_status':t['certification_status'],'mip_handoff_expectation':t['mip_handoff_expectation']}
  for k in FIELDS:
   if k not in rec and k not in ('time_window_start','time_window_end','produced_at','freshness_evaluated_at','synthetic_fixture_time_scope'):
    if k not in r: raise ValueError(f'missing required governed field: {k}')
    rec[k]=r[k]
  rec.update(time_window_start='2025-01-06T00:00:00Z' if fresh else '2024-01-08T00:00:00Z',time_window_end='2025-03-30T23:59:59Z' if fresh else '2024-03-31T23:59:59Z',produced_at='2025-03-31T00:00:00Z' if fresh else '2024-04-01T00:00:00Z',freshness_evaluated_at='2025-04-01T00:00:00Z',synthetic_fixture_time_scope=True)
  if set(rec) != set(FIELDS): raise ValueError('record shape mismatch')
  if any(not isinstance(v,bool) or v for v in rec['authorization_flags'].values()): raise ValueError('authorization')
  if any(k in rec for k in ('source_readout','source_replay','calibration_compatibility','method_eligibility_status','compatibility_status','target_model_id','calibration_weight','calibration_signal','trust_report','decision_surface','recommendation','optimization')): raise ValueError('prohibited field')
  records.append(rec)
 out={'schema_version':'geox_calibration_source_manifest_v1','record_version':'1.0.0','case_count':12,'source_repository':'Phani-Pavuluri/panel_exp','source_fixture_checkpoint_sha':'860182386c39f487747de5f43e67a31e9978e57c','source_tree_base_sha':'7f829395bc305550ea1311421a4181dafed795b8','synthetic_fixture_time_scope':True,'mmm_compatibility_emitted':False,'calibration_signal_emitted':False,'production_authorized':False,'records':records}; Path(output).parent.mkdir(parents=True,exist_ok=True); Path(output).write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
if __name__=='__main__': ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=DEFAULT); build(ap.parse_args().output)
