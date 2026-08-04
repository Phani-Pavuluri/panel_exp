import json, subprocess, sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).parents[1]; SCRIPT=ROOT/"scripts/verify_authorized_task_binding.py"
TASK="GEOX_EXECUTION_BRANCH_BINDING_001"; BRANCH="feat/geox-execution-branch-binding-001"

def repo():
    d=TemporaryDirectory(); p=Path(d.name); subprocess.run(["git","init","--bare",str(p/"origin")],check=True,capture_output=True)
    subprocess.run(["git","init",str(p)],check=True,capture_output=True); c={"cwd":p,"capture_output":True,"text":True}
    for k,v in (("user.email","test@example.com"),("user.name","test")): subprocess.run(["git","config",k,v],**c)
    (p/"docs/execution").mkdir(parents=True); state={"repository":"x","task_id":TASK,"feature_branch":BRANCH,"authorization_head_sha":"0"*40,"task_execution_authorized":True}
    (p/"docs/execution/EXECUTION_STATE.json").write_text(json.dumps(state)); subprocess.run(["git","add","."],**c); subprocess.run(["git","commit","-m","base"],**c); auth=subprocess.check_output(["git","rev-parse","HEAD"],cwd=p,text=True).strip(); state["authorization_head_sha"]=auth; (p/"docs/execution/EXECUTION_STATE.json").write_text(json.dumps(state)); subprocess.run(["git","add","."],**c); subprocess.run(["git","commit","-m","auth"],**c); subprocess.run(["git","branch","-M","main"],**c); subprocess.run(["git","remote","add","origin",str(p/"origin")],**c); subprocess.run(["git","push","-u","origin","main"],**c)
    subprocess.run(["git","switch","-c",BRANCH],**c); (p/"scripts").mkdir(); (p/"scripts/verify_authorized_task_binding.py").write_text(SCRIPT.read_text()); subprocess.run(["git","add","."],**c); subprocess.run(["git","commit","-m","task"],**c); subprocess.run(["git","push","-u","origin",BRANCH],**c)
    subprocess.run(["git","switch","main"],**c); subprocess.run(["git","switch",BRANCH],**c); return d,p

def run(p,phase): return subprocess.run([sys.executable,str(p/"scripts/verify_authorized_task_binding.py"),"--phase",phase],cwd=p,text=True,capture_output=True)
def assert_fail(r,code): assert r.returncode==2 and not r.stdout and len(r.stderr.splitlines())==1 and r.stderr.startswith(f"GEOX_TASK_BINDING_ERROR:{code}:")

def test_preflight_accepts_exact_authorized_branch():
    d,p=repo(); r=run(p,"preflight"); assert r.returncode==0 and not r.stderr and set(json.loads(r.stdout))=={"status","phase","task_id","feature_branch","main_head","local_head","remote_feature_head"}; d.cleanup()
def test_preflight_rejects_wrong_current_branch():
    d,p=repo(); subprocess.run(["git","switch","main"],cwd=p,capture_output=True); assert_fail(run(p,"preflight"),"CURRENT_BRANCH_MISMATCH"); d.cleanup()
def test_preflight_rejects_unsynchronized_main():
    d,p=repo(); subprocess.run(["git","commit","--allow-empty","-m","drift"],cwd=p,capture_output=True); assert_fail(run(p,"preflight"),"MAIN_NOT_SYNCHRONIZED"); d.cleanup()
def test_preflight_rejects_branch_task_identity_mismatch():
    d,p=repo(); q=json.loads((p/"docs/execution/EXECUTION_STATE.json").read_text()); q["task_id"]="wrong"; (p/"docs/execution/EXECUTION_STATE.json").write_text(json.dumps(q)); assert_fail(run(p,"preflight"),"BRANCH_TASK_MISMATCH"); d.cleanup()
def test_preflight_rejects_missing_authorization_ancestry():
    d,p=repo(); q=json.loads((p/"docs/execution/EXECUTION_STATE.json").read_text()); q["authorization_head_sha"]="0"*40; (p/"docs/execution/EXECUTION_STATE.json").write_text(json.dumps(q)); assert_fail(run(p,"preflight"),"AUTHORIZATION_ANCESTRY_MISSING"); d.cleanup()
def test_prepush_rejects_diverged_remote_destination():
    d,p=repo(); subprocess.run(["git","switch","main"],cwd=p,capture_output=True); subprocess.run(["git","commit","--allow-empty","-m","remote"],cwd=p,capture_output=True); subprocess.run(["git","push","origin","main:feat/geox-execution-branch-binding-001"],cwd=p,capture_output=True); subprocess.run(["git","switch",BRANCH],cwd=p,capture_output=True); assert_fail(run(p,"prepush"),"REMOTE_FEATURE_BRANCH_DIVERGED"); d.cleanup()
def test_postpush_requires_exact_remote_head():
    d,p=repo(); subprocess.run(["git","commit","--allow-empty","-m","local"],cwd=p,capture_output=True); assert_fail(run(p,"postpush"),"POSTPUSH_HEAD_MISMATCH"); d.cleanup()
def test_failure_output_uses_stable_reason_code():
    d,p=repo(); (p/"docs/execution/EXECUTION_STATE.json").write_text("{"); assert_fail(run(p,"preflight"),"BRANCH_STATE_UNREADABLE"); d.cleanup()
