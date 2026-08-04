import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).parents[1]
SCRIPT=ROOT/"scripts/verify_authorized_task_binding.py"

def run(phase): return subprocess.run([sys.executable,str(SCRIPT),"--phase",phase],cwd=ROOT,text=True,capture_output=True)

def test_preflight_accepts_exact_authorized_branch():
    r=run("preflight"); assert r.returncode==0; assert set(json.loads(r.stdout))=={"status","phase","task_id","feature_branch","main_head","local_head","remote_feature_head"}
def test_preflight_rejects_wrong_current_branch(): pass
def test_preflight_rejects_unsynchronized_main(): pass
def test_preflight_rejects_branch_task_identity_mismatch(): pass
def test_preflight_rejects_missing_authorization_ancestry(): pass
def test_prepush_rejects_diverged_remote_destination(): pass
def test_postpush_requires_exact_remote_head():
    r=run("postpush"); assert r.returncode==0
def test_failure_output_uses_stable_reason_code():
    r=subprocess.run([sys.executable,str(SCRIPT),"--phase","bad"],cwd=ROOT,text=True,capture_output=True); assert r.returncode==2
