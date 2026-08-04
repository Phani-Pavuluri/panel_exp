# Active Task

**Status:** ready_for_review
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_EXECUTION_BRANCH_BINDING_REAUTHORING_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Pre-authoring base:** `b6c714ced8a9c6e9c1fcb0f6b4f7f79a542c5a7f`
- **Feature branch:** `feat/geox-execution-branch-binding-reauthoring-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 2 — internal executable repository-governance tooling
- **Canonical MIP execution-standard pin:** `Phani-Pavuluri/marketing_intelligence_platform@369805d923454a51ce98845cea29bdb1ee3c3895`
- **Live MIP main observed:** `976d3a1daeae9c52c8772e5112574f698951a57c`
- **Live MMM main observed:** `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`
- **Superseded predecessor:** `GEOX_EXECUTION_BRANCH_BINDING_001`
- **Preserved predecessor branch head:** `fbb027a3db2c779bf53fcda3165f51fce7a088ae`
- **Capability authorizations changed:** `false`

## Eligibility and authority decision

Connected GitHub establishes that GeoX `main` is synchronized at the pre-authoring base, the predecessor is superseded without merge, and all predecessor task, correction, merge, and PR authority is false. Its preserved branch is historical evidence only and must not be resumed or merged.

MIP and MMM each have separate repository-owned governance tasks at the live pins above. Neither owns or modifies GeoX files. The MIP coordination snapshot is stale for all three repositories; the live overlay controls eligibility and shows no duplicate GeoX owner or overlapping implementation. No coordination blocker or consumer verification is created by this GeoX-only repository-governance task.

## Primary independently mergeable outcome

Implement one deterministic, read-only GeoX command that binds execution to the exact task and feature branch authorized on synchronized `main`, together with eight real isolated temporary-Git behavioral tests and the minimal execution guidance that invokes the command.

This task changes no experiment design, assignment, inference, readout, fixture, contract, numerical truth, MIP/GeoX integration, MMM compatibility, builder, publication-lifecycle, or capability behavior.

## Why this task cannot be split further

The verifier, its isolated Git scenario builder, and the execution sequence are one enforcement unit. A verifier without behavior tests would repeat the predecessor failure; tests without the verifier would not create repository enforcement. Publication lifecycle and receipt semantics remain a separate successor.

## Frozen implementation and acceptance contract

The following decisions are complete before authorization. Codex must not choose a different fixture topology, error taxonomy, phase behavior, or publication rule. Review may reject only against this contract, unauthorized scope, false evidence, or an unsafe defect under this contract. New preferences become successor work.

### 1. Command surface

Create `scripts/verify_authorized_task_binding.py` using only the Python standard library and Git CLI.

Supported invocations are exactly:

- `python scripts/verify_authorized_task_binding.py --phase preflight`
- `python scripts/verify_authorized_task_binding.py --phase prepush`
- `python scripts/verify_authorized_task_binding.py --phase postpush`

The command performs no repository writes.

It reads authorization provenance only from:

`git show main:docs/execution/EXECUTION_STATE.json`

It reads current lifecycle state only from the checked-out branch worktree path:

`docs/execution/EXECUTION_STATE.json`

CLI usage errors outside the three supported phase values are not part of the runtime reason-code contract below. Every runtime failure after a supported phase is accepted must follow the stable failure contract.

### 2. Success contract

Success exits `0`, writes nothing to stderr, and writes exactly one compact JSON object to stdout with exactly these keys:

- `status` equal to `ok`;
- `phase`;
- `task_id`;
- `feature_branch`;
- `main_head`;
- `local_head`; and
- `remote_feature_head`.

### 3. Stable runtime failure contract

Runtime failure exits `2`, writes no stdout, and writes exactly one stderr line:

`GEOX_TASK_BINDING_ERROR:<REASON_CODE>:<detail>`

The reason-code set is exactly:

- `GIT_COMMAND_FAILED`
- `MAIN_NOT_SYNCHRONIZED`
- `MAIN_STATE_UNREADABLE`
- `TASK_NOT_AUTHORIZED`
- `CURRENT_BRANCH_MISMATCH`
- `BRANCH_STATE_UNREADABLE`
- `BRANCH_TASK_MISMATCH`
- `AUTHORIZATION_ANCESTRY_MISSING`
- `REMOTE_FEATURE_BRANCH_MISSING`
- `REMOTE_DESTINATION_MISMATCH`
- `REMOTE_FEATURE_BRANCH_DIVERGED`
- `POSTPUSH_HEAD_MISMATCH`

Git stderr must always be captured. No raw subprocess diagnostic may leak as a second stderr line.

Mapping is fixed:

- unreadable, missing, or invalid main state → `MAIN_STATE_UNREADABLE`;
- missing required main task fields, invalid authorization SHA, or main task authority false → `TASK_NOT_AUTHORIZED`;
- unreadable, missing, or invalid branch-local state → `BRANCH_STATE_UNREADABLE`;
- repository/task/feature-branch identity mismatch → `BRANCH_TASK_MISMATCH`;
- branch execution and correction authority both false → `TASK_NOT_AUTHORIZED`;
- authorization head absent from history or not an ancestor of local `HEAD` → `AUTHORIZATION_ANCESTRY_MISSING`;
- no configured upstream or upstream not exactly `origin/<feature_branch>` → `REMOTE_DESTINATION_MISMATCH`;
- absent `refs/remotes/origin/<feature_branch>` → `REMOTE_FEATURE_BRANCH_MISSING`;
- unexpected Git operation failure not covered above → `GIT_COMMAND_FAILED`.

### 4. Invariants and phase semantics

Every supported phase must prove:

1. local `main` exactly equals `origin/main`;
2. main state contains nonempty repository, task ID, feature branch, and a 40-character authorization-head SHA;
3. main records `task_execution_authorized: true`;
4. the checked-out branch exactly equals main's feature branch;
5. branch-local repository, task ID, and feature branch equal main's values;
6. branch-local task or correction execution authority is true;
7. the authorization head exists and is an ancestor of local `HEAD`;
8. the configured upstream is exactly `origin/<feature_branch>`; and
9. the remote-tracking feature ref exists.

Phase behavior:

- `preflight`: local `HEAD` must exactly equal the remote feature head;
- `prepush`: the remote feature head must be an ancestor of local `HEAD`; rewritten or diverged history fails;
- `postpush`: local `HEAD` must exactly equal the remote feature head.

The command must resolve task identity from synchronized `main` before trusting any branch-local lifecycle state.

### 5. Exact isolated test-repository topology

Create `tests/test_execution_branch_binding.py`. It must execute the real source command as a subprocess with each temporary repository as `cwd`.

A shared fixture/scenario builder must use this exact topology:

1. create a temporary bare repository `origin.git` and a separate non-bare `work` repository initialized with branch `main`;
2. configure deterministic test user identity and add `origin`;
3. create a task-authoring commit on `main` and capture its SHA as `authorization_head_sha`;
4. create an immediate state-only commit on `main` whose execution state names the test task, exact feature branch, captured authorization head, and `task_execution_authorized: true`;
5. push synchronized `main` to the bare origin;
6. create the exact feature branch from that state-only main head, preserve matching branch-local state, commit any fixture marker needed by the test, push it, and configure upstream exactly to `origin/<feature_branch>`; and
7. leave the fixture on the feature branch with local/remote heads equal.

The scenario builder must retain the `TemporaryDirectory` owner for the full test lifetime and must return named SHAs/paths needed by assertions.

The real command may be invoked from the source repository path while the subprocess `cwd` is the temporary work repository. Tests must not depend on the developer repository's current branch, remotes, or state.

### 6. Exact eight tests and scenario mutations

Implement exactly these eight independently collected tests; no empty bodies, `pass`, skip, xfail, or conditional early return is allowed:

1. `test_preflight_accepts_exact_authorized_branch`
   - use the untouched canonical fixture;
   - assert exit `0`, empty stderr, exact seven JSON keys, `status == "ok"`, expected phase/task/branch, and exact named heads.

2. `test_preflight_rejects_wrong_current_branch`
   - create and switch to a local wrong branch from the authorized feature head so the real command remains invokable;
   - assert `CURRENT_BRANCH_MISMATCH`.

3. `test_preflight_rejects_unsynchronized_main`
   - switch to local `main`, create an unpushed empty drift commit, then switch back to the authorized feature branch;
   - assert `MAIN_NOT_SYNCHRONIZED`.

4. `test_preflight_rejects_branch_task_identity_mismatch`
   - modify only the branch worktree execution-state task ID to a different value;
   - assert `BRANCH_TASK_MISMATCH`.

5. `test_preflight_rejects_missing_authorization_ancestry`
   - create an unrelated orphan commit;
   - update main execution state to name that unrelated SHA as the authorization head, commit it, push synchronized main, and return to the unchanged feature branch;
   - assert `AUTHORIZATION_ANCESTRY_MISSING`.

6. `test_prepush_rejects_diverged_remote_destination`
   - create one unpushed local feature commit;
   - use a separate second clone of the bare origin to create and push a different feature-branch commit from the prior common remote head;
   - fetch the updated remote feature ref in the work repository;
   - assert `REMOTE_FEATURE_BRANCH_DIVERGED`.

7. `test_postpush_requires_exact_remote_head`
   - create one unpushed local feature commit;
   - assert `POSTPUSH_HEAD_MISMATCH`.

8. `test_failure_output_uses_stable_reason_code`
   - corrupt the branch-local execution-state JSON in the canonical fixture;
   - assert `BRANCH_STATE_UNREADABLE`.

Every failure test must assert exit `2`, empty stdout, exactly one stderr line, and the exact `GEOX_TASK_BINDING_ERROR:<EXPECTED_CODE>:` prefix.

### 7. Documentation sequence

Update `AGENTS.md` and create `docs/execution/TASK_EXECUTION_STANDARD.md` with this exact operational sequence:

1. fetch/prune, switch to `main`, pull `--ff-only`, and prove `main == origin/main`;
2. read main execution state and switch explicitly to its declared feature branch;
3. run `--phase preflight` before task edits;
4. implement and run the task's declared validation;
5. run `--phase prepush` immediately before pushing;
6. push only `HEAD:refs/heads/<declared-feature-branch>` without force;
7. fetch that exact remote feature branch after push;
8. run `--phase postpush`; and
9. prove exact local/remote feature-head equality.

A nonzero verifier result is fail-closed. Do not publish to another branch or repair missing Git-authored instructions from chat.

## Owned paths

Implementation may modify only:

- `AGENTS.md`
- `scripts/verify_authorized_task_binding.py`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `tests/test_execution_branch_binding.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify any other path.

## Prohibited scope

Do not modify or copy commits from the preserved predecessor branch. Do not modify `REPOSITORY_CONTEXT_INDEX.md`, lean-delivery documents, package or analytical code, contracts, fixtures, design, assignment, inference, CI, release configuration, MIP, MMM, coordination files, or capability state.

Do not create a PR, merge, rebase, squash, force-push, or delete preserved branches.

## Validation gate

Run on the final task-owned tree:

- parse `docs/execution/EXECUTION_STATE.json` as JSON;
- `python -m py_compile scripts/verify_authorized_task_binding.py tests/test_execution_branch_binding.py`;
- `pytest -q tests/test_execution_branch_binding.py` with exactly `8 passed`, `0 failed`, `0 skipped`, and no xfail/xpass;
- AST inspection proving exactly the eight required `test_` functions exist and none has an empty body or `pass` statement;
- `git diff --check`;
- exact changed-path verification against the seven owned paths;
- verifier `prepush` immediately before push;
- push only the declared feature branch without force;
- fetch the exact remote feature branch;
- verifier `postpush`; and
- exact local/remote feature-head equality.

Docker, the complete package suite, analytical tests, Ruff, and mypy are `not_required` because the task changes only standard-library Git governance tooling, isolated temporary repositories, documentation, and execution metadata. Discovery of an unexpected package/runtime dependency is a genuine blocker rather than permission to widen scope.

A failing task-owned test or fixture is unfinished implementation, **not** a valid blocked outcome. Continue correcting and rerunning within the authorized scope until the gate passes. Publish `blocked` only for a genuine external Git capability, remote authentication, filesystem/environment, missing required history, or authority obstruction that task-owned changes cannot resolve; include exact attempted evidence and a live resolution condition.

## Publication contract

On success publish one `ready_for_review` head with:

- one implementation SHA;
- exact `8 passed` evidence and all validation-category dispositions;
- empty blockers;
- task execution true and correction execution false;
- merge and PR authority false;
- null reviewed and approval SHAs;
- unchanged capability authority;
- current MIP/MMM live pins;
- affected repository GeoX only;
- consumer verification not applicable; and
- one current completion report distinguishing GitHub-observed from locally reported evidence.

## Correction limit

One correction cycle is permitted only for failure against this frozen contract. A second failed review supersedes the task without merge. Review must not add independently desirable behavior to this acceptance boundary.

## Deferred successors

- `GEOX_PUBLICATION_LIFECYCLE_AND_RECEIPT_001` remains proposed and unauthorized until this task is approved, merged, and closed.
- Governed-readout builder successors remain unauthorized.
- Navigation-index cleanup remains separate repository-governance work.

**Unresolved execution-blocking design questions: none.**
