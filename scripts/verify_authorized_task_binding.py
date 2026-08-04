#!/usr/bin/env python3
import argparse, json, subprocess, sys, re

SHA = re.compile(r"^[0-9a-f]{40}$")

def git(*args):
    p = subprocess.run(["git", *args], text=True, capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.strip() or "git failed")
    return p.stdout.strip()

def fail(code, detail):
    print(f"GEOX_TASK_BINDING_ERROR:{code}:{detail}", file=sys.stderr); raise SystemExit(2)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--phase", choices=("preflight","prepush","postpush"), required=True); a=ap.parse_args()
    try:
        if git("rev-parse","main") != git("rev-parse","origin/main"): fail("MAIN_NOT_SYNCHRONIZED","main differs from origin/main")
        state=json.loads(git("show","main:docs/execution/EXECUTION_STATE.json"))
        task=state.get("task_id"); branch=state.get("feature_branch"); auth=state.get("authorization_head_sha")
        if not task or not branch or not SHA.fullmatch(str(auth)) or not state.get("task_execution_authorized"): fail("TASK_NOT_AUTHORIZED","main state is not executable")
        current=git("branch","--show-current")
        if current != branch: fail("CURRENT_BRANCH_MISMATCH", f"expected {branch}, got {current}")
        local=json.loads(open("docs/execution/EXECUTION_STATE.json").read())
        if local.get("repository") != state.get("repository") or local.get("task_id") != task or local.get("feature_branch") != branch: fail("BRANCH_TASK_MISMATCH","branch state does not match main")
        if not (local.get("task_execution_authorized") or local.get("correction_execution_authorized")): fail("TASK_NOT_AUTHORIZED","branch execution is not authorized")
        if subprocess.run(["git","merge-base","--is-ancestor",auth,"HEAD"]).returncode: fail("AUTHORIZATION_ANCESTRY_MISSING",auth)
        upstream=git("rev-parse","--abbrev-ref","--symbolic-full-name","@{upstream}")
        expected=f"origin/{branch}"
        if upstream != expected: fail("REMOTE_DESTINATION_MISMATCH",f"expected {expected}, got {upstream}")
        remote=git("rev-parse",expected)
        head=git("rev-parse","HEAD"); mainhead=git("rev-parse","main")
        if a.phase in ("preflight","postpush") and head != remote: fail("POSTPUSH_HEAD_MISMATCH" if a.phase=="postpush" else "REMOTE_FEATURE_BRANCH_DIVERGED","local and remote differ")
        if a.phase=="prepush" and subprocess.run(["git","merge-base","--is-ancestor",remote,"HEAD"]).returncode: fail("REMOTE_FEATURE_BRANCH_DIVERGED","remote is not ancestor")
        print(json.dumps({"status":"ok","phase":a.phase,"task_id":task,"feature_branch":branch,"main_head":mainhead,"local_head":head,"remote_feature_head":remote},separators=(",",":")))
    except SystemExit: raise
    except json.JSONDecodeError as e: fail("BRANCH_STATE_UNREADABLE",str(e))
    except RuntimeError as e: fail("GIT_COMMAND_FAILED",str(e))
if __name__ == "__main__": main()
