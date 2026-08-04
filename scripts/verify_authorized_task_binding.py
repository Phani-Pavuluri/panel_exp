import argparse,json,re,subprocess,sys
SHA=re.compile(r'^[0-9a-f]{40}$')
def g(*a):
 p=subprocess.run(['git',*a],capture_output=True,text=True)
 if p.returncode: raise RuntimeError(p.stderr.strip() or 'git failure')
 return p.stdout.strip()
def bad(c,d): print(f'GEOX_TASK_BINDING_ERROR:{c}:{d}',file=sys.stderr); raise SystemExit(2)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--phase',choices=['preflight','prepush','postpush'],required=True); ph=ap.parse_args().phase
 try:
  if g('rev-parse','main')!=g('rev-parse','origin/main'): bad('MAIN_NOT_SYNCHRONIZED','main differs')
  try: ms=json.loads(g('show','main:docs/execution/EXECUTION_STATE.json'))
  except Exception as e: bad('MAIN_STATE_UNREADABLE',str(e))
  task,br,auth=ms.get('task_id'),ms.get('feature_branch'),ms.get('authorization_head_sha')
  if not ms.get('repository') or not task or not br or not isinstance(auth,str) or not SHA.fullmatch(auth) or not ms.get('task_execution_authorized'): bad('TASK_NOT_AUTHORIZED','main authority')
  if g('branch','--show-current')!=br: bad('CURRENT_BRANCH_MISMATCH',br)
  try: bs=json.load(open('docs/execution/EXECUTION_STATE.json'))
  except Exception as e: bad('BRANCH_STATE_UNREADABLE',str(e))
  if any(bs.get(k)!=ms.get(k) for k in ('repository','task_id','feature_branch')): bad('BRANCH_TASK_MISMATCH','identity')
  if not (bs.get('task_execution_authorized') or bs.get('correction_execution_authorized')): bad('TASK_NOT_AUTHORIZED','branch authority')
  if subprocess.run(['git','merge-base','--is-ancestor',auth,'HEAD'],capture_output=True).returncode: bad('AUTHORIZATION_ANCESTRY_MISSING',auth)
  up=g('rev-parse','--abbrev-ref','--symbolic-full-name','@{upstream}')
  if up!=f'origin/{br}': bad('REMOTE_DESTINATION_MISMATCH',up)
  try: remote=g('rev-parse',f'refs/remotes/origin/{br}')
  except RuntimeError: bad('REMOTE_FEATURE_BRANCH_MISSING',br)
  local=g('rev-parse','HEAD'); mainh=g('rev-parse','main')
  if ph=='preflight' and local!=remote: bad('REMOTE_FEATURE_BRANCH_DIVERGED','local differs')
  if ph=='prepush' and subprocess.run(['git','merge-base','--is-ancestor',remote,'HEAD'],capture_output=True).returncode: bad('REMOTE_FEATURE_BRANCH_DIVERGED','remote diverged')
  if ph=='postpush' and local!=remote: bad('POSTPUSH_HEAD_MISMATCH','local differs')
  print(json.dumps({'status':'ok','phase':ph,'task_id':task,'feature_branch':br,'main_head':mainh,'local_head':local,'remote_feature_head':remote},separators=(',',':')))
 except SystemExit: raise
 except Exception as e: bad('GIT_COMMAND_FAILED',str(e))
if __name__=='__main__': main()
