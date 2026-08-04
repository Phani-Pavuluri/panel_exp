import json, subprocess, sys, os
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).parents[1]; SCRIPT=ROOT/'scripts/verify_authorized_task_binding.py'; TASK='GEOX_EXECUTION_BRANCH_BINDING_REAUTHORING_001'; BR='feat/geox-execution-branch-binding-reauthoring-001'
_check_output=subprocess.check_output
def _clean_output(*args, **kwargs):
 value=_check_output(*args, **kwargs)
 return value.strip() if isinstance(value,str) else value.strip()
subprocess.check_output=_clean_output
def scenario():
 d=TemporaryDirectory(); root=Path(d.name); p=root/'work'; origin=root/'origin.git'; c={'cwd':p,'capture_output':True,'text':True,'check':True}; subprocess.run(['git','init','--bare',str(origin)],check=True,capture_output=True); p.mkdir(); os.symlink(origin,p/'origin.git'); subprocess.run(['git','init','-b','main',str(p)],check=True,capture_output=True)
 for k,v in [('user.email','t@e'),('user.name','t')]: subprocess.run(['git','config',k,v],**c)
 (p/'docs/execution').mkdir(parents=True); (p/'docs/execution/EXECUTION_STATE.json').write_text('{}'); subprocess.run(['git','add','.'],**c); subprocess.run(['git','commit','-m','author'],**c); auth=subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip(); s={'repository':'x','task_id':TASK,'feature_branch':BR,'authorization_head_sha':auth,'task_execution_authorized':True}; (p/'docs/execution/EXECUTION_STATE.json').write_text(json.dumps(s)); subprocess.run(['git','add','.'],**c); subprocess.run(['git','commit','-m','state'],**c); subprocess.run(['git','remote','add','origin',str(origin)],**c); subprocess.run(['git','push','-u','origin','main'],**c); subprocess.run(['git','switch','-c',BR],**c); subprocess.run(['git','push','-u','origin',BR],**c); return d,p,s,auth
def run(p,ph): return subprocess.run([sys.executable,str(SCRIPT),'--phase',ph],cwd=p,text=True,capture_output=True)
def fail(r,c): assert r.returncode==2 and not r.stdout and len(r.stderr.splitlines())==1 and r.stderr.startswith('GEOX_TASK_BINDING_ERROR:'+c+':')
def test_preflight_accepts_exact_authorized_branch():
 d,p,s,a=scenario(); r=run(p,'preflight'); assert r.returncode==0 and not r.stderr and set(json.loads(r.stdout))=={'status','phase','task_id','feature_branch','main_head','local_head','remote_feature_head'}; d.cleanup()
def test_preflight_rejects_wrong_current_branch():
 d,p,s,a=scenario(); subprocess.run(['git','switch','-c','wrong'],cwd=p,capture_output=True); fail(run(p,'preflight'),'CURRENT_BRANCH_MISMATCH'); d.cleanup()
def test_preflight_rejects_unsynchronized_main():
 d,p,s,a=scenario(); subprocess.run(['git','switch','main'],cwd=p,capture_output=True); subprocess.run(['git','commit','--allow-empty','-m','drift'],cwd=p,capture_output=True); subprocess.run(['git','switch',BR],cwd=p,capture_output=True); fail(run(p,'preflight'),'MAIN_NOT_SYNCHRONIZED'); d.cleanup()
def test_preflight_rejects_branch_task_identity_mismatch():
 d,p,s,a=scenario(); s['task_id']='wrong'; (p/'docs/execution/EXECUTION_STATE.json').write_text(json.dumps(s)); fail(run(p,'preflight'),'BRANCH_TASK_MISMATCH'); d.cleanup()
def test_preflight_rejects_missing_authorization_ancestry():
 tree_fix = True
 d,p,s,a=scenario(); tree=subprocess.check_output(['git','mktree'],input='',cwd=p,text=True); orphan=subprocess.check_output(['git','commit-tree',tree,'-m','unrelated orphan'],cwd=p,text=True).strip(); s['authorization_head_sha']=orphan; subprocess.run(['git','switch','main'],cwd=p,capture_output=True,check=True); (p/'docs/execution/EXECUTION_STATE.json').write_text(json.dumps(s)); subprocess.run(['git','add','.'],cwd=p,capture_output=True,check=True); subprocess.run(['git','commit','-m','bad auth'],cwd=p,capture_output=True,check=True); subprocess.run(['git','push','origin','main'],cwd=p,capture_output=True,check=True); subprocess.run(['git','switch','-f',BR],cwd=p,capture_output=True,check=True); fail(run(p,'preflight'),'AUTHORIZATION_ANCESTRY_MISSING'); d.cleanup()
def test_prepush_rejects_diverged_remote_destination():
 d,p,s,a=scenario(); subprocess.run(['git','commit','--allow-empty','-m','local'],cwd=p,capture_output=True); q=Path(d.name)/'other'; subprocess.run(['git','clone',str(p/'origin.git'),str(q)],capture_output=True); subprocess.run(['git','switch',BR],cwd=q,capture_output=True); subprocess.run(['git','config','user.email','t@e'],cwd=q,capture_output=True); subprocess.run(['git','config','user.name','t'],cwd=q,capture_output=True); subprocess.run(['git','commit','--allow-empty','-m','remote'],cwd=q,capture_output=True); subprocess.run(['git','push'],cwd=q,capture_output=True); subprocess.run(['git','fetch','origin'],cwd=p,capture_output=True); fail(run(p,'prepush'),'REMOTE_FEATURE_BRANCH_DIVERGED'); d.cleanup()
def test_postpush_requires_exact_remote_head():
 d,p,s,a=scenario(); subprocess.run(['git','commit','--allow-empty','-m','local'],cwd=p,capture_output=True); fail(run(p,'postpush'),'POSTPUSH_HEAD_MISMATCH'); d.cleanup()
def test_failure_output_uses_stable_reason_code():
 d,p,s,a=scenario(); (p/'docs/execution/EXECUTION_STATE.json').write_text('{'); fail(run(p,'preflight'),'BRANCH_STATE_UNREADABLE'); d.cleanup()
