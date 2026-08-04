# Active Task

**Status:** blocked
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_EXECUTION_BRANCH_BINDING_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Task base on main:** `d17bb81c9dbc67f773fd71068c26b14c92989f42`
- **Authorization head:** `dc68853e87a65a494c942b3fe2794e321a22b036`
- **Feature branch:** `feat/geox-execution-branch-binding-001`
- **Rejected exact review head:** `feda65c5dbba1529d588d2cb36693a38132ab766`
- **Retained implementation candidate:** `d2a64376757766c1fd4c009f6e2ea238c85437d7`
- **Risk tier:** Tier 2 — internal executable repository-governance tooling
- **Correction cycle:** one and only permitted correction
- **Capability authorizations changed:** `false`

## Review decision

Exact remote head `feda65c5dbba1529d588d2cb36693a38132ab766` is rejected. Correction execution is authorized on the same feature branch. Merge and PR authority remain false.

The acceptance boundary is frozen to the contract authored before execution at `dc68853e87a65a494c942b3fe2794e321a22b036`. This correction adds no new behavior or preferred design. It addresses only direct failures against that frozen contract.

## Required corrections

### 1. Replace placeholder tests with the required real behavioral tests

`tests/test_execution_branch_binding.py` currently has empty `pass` bodies for six of the eight required tests. The two non-placeholder tests run against the developer's current repository rather than temporary Git repositories. This does not satisfy the frozen requirement that every named test construct isolated temporary Git repositories and execute the real command.

Implement all eight named tests from the frozen contract as independent behavioral tests:

1. `test_preflight_accepts_exact_authorized_branch`
2. `test_preflight_rejects_wrong_current_branch`
3. `test_preflight_rejects_unsynchronized_main`
4. `test_preflight_rejects_branch_task_identity_mismatch`
5. `test_preflight_rejects_missing_authorization_ancestry`
6. `test_prepush_rejects_diverged_remote_destination`
7. `test_postpush_requires_exact_remote_head`
8. `test_failure_output_uses_stable_reason_code`

Create temporary repositories with an isolated bare `origin`, synchronized `main`, the authorized feature branch, branch-local execution state, configured upstream, and the exact divergence or mismatch needed by each test. Execute `scripts/verify_authorized_task_binding.py` as a subprocess inside those repositories.

Each success test must assert exit `0`, empty stderr, `status == "ok"`, the exact seven JSON keys, and expected phase/task/branch/head values. Each failure test must assert exit `2`, empty stdout, exactly one stderr line, and the exact expected `GEOX_TASK_BINDING_ERROR:<REASON_CODE>:` prefix.

The stable-reason-code test must induce a supported runtime failure. It must not pass by invoking argparse with an invalid phase.

### 2. Make every contracted failure fail closed with one stable line

Keep the exact reason-code set already frozen in the task. Do not add or rename codes.

Update `scripts/verify_authorized_task_binding.py` so:

- unreadable or invalid main execution state emits `MAIN_STATE_UNREADABLE`;
- unreadable, missing, or invalid branch-local execution state emits `BRANCH_STATE_UNREADABLE`;
- a missing `origin/<feature_branch>` emits `REMOTE_FEATURE_BRANCH_MISSING`;
- unexpected Git failures emit `GIT_COMMAND_FAILED`;
- authorization ancestry, upstream destination, divergence, and post-push mismatch retain their contracted specific codes;
- every runtime failure exits `2`, writes no stdout success object, and emits exactly one `GEOX_TASK_BINDING_ERROR:` stderr line; and
- Git subprocess diagnostics are captured rather than leaking additional stderr lines.

Preserve all frozen success keys, phase semantics, task/branch/authority checks, ancestry checks, and read-only behavior.

### 3. Complete the exact documented invocation sequence

Update `AGENTS.md` and `docs/execution/TASK_EXECUTION_STANDARD.md` to state the already-frozen sequence explicitly:

1. synchronize and verify `main`;
2. switch to the feature branch named by main execution state;
3. run `--phase preflight` before edits;
4. run `--phase prepush` immediately before push;
5. push only the declared branch;
6. fetch the remote branch after push; and
7. run `--phase postpush` and verify exact local/remote equality.

A nonzero verifier result is fail-closed. Do not publish to another branch or repair missing repository instructions from chat.

## Owned paths

Correction execution may modify only:

- `AGENTS.md`
- `scripts/verify_authorized_task_binding.py`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `tests/test_execution_branch_binding.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify any other path, repository, preserved branch, analytical code, package contract, fixture, coordination file, CI configuration, release configuration, or capability state.

## Validation gate

Run on the final frozen task-owned tree:

- parse `docs/execution/EXECUTION_STATE.json` as JSON;
- `python -m py_compile scripts/verify_authorized_task_binding.py`;
- `pytest -q tests/test_execution_branch_binding.py` with exact pass/fail/skip counts;
- inspect the test file and prove that none of the eight named tests is empty or uses `pass` as its body;
- `git diff --check`;
- exact changed-path verification against the seven owned paths;
- verifier `prepush` immediately before push;
- fetch the exact remote feature branch after push;
- verifier `postpush`; and
- exact local/remote feature-head equality.

Docker, the complete package suite, analytical tests, Ruff, and mypy remain `not_required` under the frozen task contract.

## Publication

On success publish `ready_for_review` with one implementation SHA, empty blockers, task execution true, correction execution false, merge and PR false, null reviewed/approval SHAs, unchanged capability authority, one current completion report, exact test counts, and durable validation evidence.

Publish `blocked` only for a genuine synchronization, Git capability, environment, authority, or required-validation obstruction with exact diagnostics and a live resolution condition.

## Correction limit

This is the single permitted correction cycle. A further failed exact-head review supersedes this task without merge. New preferences or enhancements become separately proposed successors and cannot move this frozen acceptance boundary.

## Deferred successor

`GEOX_PUBLICATION_LIFECYCLE_AND_RECEIPT_001` remains proposed and unauthorized.

**Unresolved execution-blocking design questions: none.**
