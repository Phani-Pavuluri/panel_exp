"""Deterministic local-only GeoX numerical-truth fixture generator."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
CASE_IDS=("geox_truth_scm_candidate_clean_001","geox_truth_did_candidate_warning_001","geox_truth_infeasible_preperiod_001","geox_truth_weak_matchability_001","geox_truth_unsupported_inference_001","geox_truth_tbrridge_diagnostic_only_001","geox_truth_bayesian_tbr_research_only_001","geox_truth_stale_incompatible_evidence_001","geox_truth_conflicting_evidence_001","geox_truth_multicell_shared_control_block_001","geox_truth_calibration_incompatible_001","geox_truth_safe_blocked_readout_001")
BLOCKED=set(CASE_IDS[2:5]+CASE_IDS[7:12]); READOUT=set(CASE_IDS[:2]+(CASE_IDS[5],CASE_IDS[6]))
def _truth(case_id):
    blocked=case_id in BLOCKED; status='blocked' if blocked else ('diagnostic_only' if case_id==CASE_IDS[5] else 'research_only' if case_id==CASE_IDS[6] else 'candidate')
    return {'fixture_id':case_id,'fixture_version':'1.0.0','dataset_version':'dataset-1','truth_version':'truth-1','fixture_class':case_id.replace('geox_truth_','').replace('_001',''),'certification_status':status,'design_type':'geo_experiment','method_family':'SCM','instrument_id':'SCM_UNIT_JACKKNIFE','assignment_seed':1,'panel_grain':'geo_time','geo_scope':'fixture_geos','time_window':{'pre_period':'pre','post_period':'post'},'kpi':'revenue','estimand':'ATT','treatment_units':['treated'],'control_units':['control'],'known_lift_absolute':None if blocked else 0.1,'known_lift_relative':None if blocked else 0.01,'known_incremental_outcome':None if blocked else 10.0,'expected_point_estimate':None if blocked else 0.1,'expected_standard_error':None if blocked else 0.02,'expected_confidence_interval':None if blocked else [0.05,0.15],'expected_uncertainty_semantics':'blocked' if blocked else 'standard_error','expected_feasibility_status':'blocked' if blocked else 'feasible','expected_design_status':'blocked' if blocked else 'ready','expected_assignment_status':'not_authorized','expected_readout_status':'blocked' if blocked else 'diagnostic','expected_blocked_reasons':['fixture_blocked'] if blocked else [],'expected_warnings':['shadow_validation_only'],'calibration_compatibility':{'status':'incompatible' if blocked else 'compatible','reasons':[]},'mip_handoff_expectation':{'status':'blocked' if blocked else 'diagnostic_only','artifact_kind':'readout_packet'},'tolerances':{'estimate_abs':0.01,'standard_error_abs':0.01,'interval_abs':0.02},'provenance':{'source_repo':'panel_exp','source_commit':'929a6ce','created_by':'fixture_generator','schema_version':'1.0.0'}}
def _write(path,obj): path.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
def build_geox_numerical_truth_fixture_artifacts(case_id,root):
    if case_id not in CASE_IDS: raise ValueError('unknown_case_id')
    root=Path(root); d=root/case_id; d.mkdir(parents=True,exist_ok=True); truth=_truth(case_id)
    with (d/'input_panel.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['unit_id','geo','period','is_treatment','is_post','kpi_value']); w.writeheader(); w.writerows([{'unit_id':'treated','geo':'treated','period':'pre','is_treatment':1,'is_post':0,'kpi_value':100},{'unit_id':'control','geo':'control','period':'pre','is_treatment':0,'is_post':0,'kpi_value':100},{'unit_id':'treated','geo':'treated','period':'post','is_treatment':1,'is_post':1,'kpi_value':110},{'unit_id':'control','geo':'control','period':'post','is_treatment':0,'is_post':1,'kpi_value':100}])
    _write(d/'truth.json',truth); _write(d/('expected_readout.json' if case_id in READOUT else 'expected_packet.json'),{'fixture_id':case_id,'status':truth['expected_readout_status'],'production_authorized':False,'blocked_reasons':truth['expected_blocked_reasons'],'warnings':truth['expected_warnings']}); _write(d/'replay.json',{'case_id':case_id,'generator_version':'1.0.0','seed':1,'assignment_seed':1,'generated_files':['input_panel.csv','truth.json','replay.json'],'generation_mode':'local_deterministic','external_dependency':False})
    return {'case_id':case_id,'path':case_id,'files':sorted(p.name for p in d.iterdir())}
def build_all_geox_numerical_truth_fixture_artifacts(root):
    root=Path(root); root.mkdir(parents=True,exist_ok=True); items=tuple(build_geox_numerical_truth_fixture_artifacts(c,root) for c in CASE_IDS); _write(root/'manifest.json',{'generator_version':'1.0.0','case_count':12,'cases':items,'external_dependency':False}); return items
def validate_generated_geox_truth_fixture_artifacts(root):
    root=Path(root); errors=[]
    if not (root/'manifest.json').exists(): return ('missing_manifest',)
    try: manifest=json.loads((root/'manifest.json').read_text())
    except Exception: return ('invalid_manifest',)
    if manifest.get('case_count')!=12: errors.append('invalid_case_count')
    for c in CASE_IDS:
        d=root/c
        if not d.is_dir(): errors.append('missing_case_directory:'+c); continue
        for f in ('input_panel.csv','truth.json','replay.json'):
            if not (d/f).exists(): errors.append('missing_file:'+c+':'+f)
    return tuple(errors)
