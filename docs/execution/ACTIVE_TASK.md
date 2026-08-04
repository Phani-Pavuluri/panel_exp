# Active Task

**Status:** authorized
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_EXECUTION_BRANCH_BINDING_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Pre-authoring base:** `f15b0ee1713eaa46b7dc55e597e713443f5a8d32`
- **Feature branch:** `feat/geox-execution-branch-binding-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 2 — internal executable repository-governance tooling
- **Canonical MIP standard:** `Phani-Pavuluri/marketing_intelligence_platform@369805d923454a51ce98845cea29bdb1ee3c3895`
- **MIP live main observed:** `976d3a1daeae9c52c8772e5112574f698951a57c`
- **MMM live main observed:** `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`
- **Superseded predecessor:** `GEOX_LEAN_REPOSITORY_DELIVERY_STANDARD_ADOPTION_001`
- **Preserved predecessor branch head:** `bb1ac8d5ce29e2cab33eb680b3b7db76110f35f1`
- **Capability authorizations changed:** `false`

## Primary mergeable outcome

Add one deterministic, read-only GeoX command that binds task execution to the
exact task and feature branch authorized on synchronized `main`, validates
authorization ancestry and the intended remote destination, and fails closed on
stale, wrong, or diverged branch state.

This task does not adopt the broader lean-delivery standard, define publication
lifecycle/report schemas, redesign exact-tree receipts, or resume any builder
work.

## Why this task cannot be split further

The command and its behavioral tests are one enforcement unit. Documentation
without the command would not prevent wrong-branch publication; the command
without executable tests would not establish its failure behavior. Publication
lifecycle and receipt semantics are independently reviewable and remain a later
successor.

## Frozen acceptance contract

The following contract is complete at authorization. Review may reject only for
failure to satisfy this contract, unauthorized scope, incorrect evidence, or an
unsafe defect under this contract. A newly preferred enhancement that is not
required below becomes a successor and does not move this task's acceptance
boundary.

### Command

Create:

`scripts/verify_authorized_task_binding.py`

The command uses only the Python standard library and Git CLI, performs no
writes, and supports exactly:

- `--phase preflight`
- `--phase prepush`
- `--phase postpush`

It reads authorization provenance from:

`git show main:docs/execution/EXECUTION_STATE.json`

It reads current lifecycle state from the checked-out branch's:

`docs/execution/EXECUTION_STATE.json`

### Success output

On success, exit `0` and emit one JSON object to stdout containing exactly these
keys:

- `status` with value `ok`;
- `phase`;
- `task_id`;
- `feature_branch`;
- `main_head`;
- `local_head`; and
- `remote_feature_head`.

No success text is written to stderr.

### Failure output

On failure, exit `2`, write no JSON success object, and emit one stderr line:

`GEOX_TASK_BINDING_ERROR:<REASON_CODE>:<detail>`

Supported reason codes are exactly:

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

### Invariants in every phase

The command must prove:

1. local `main` equals `origin/main`;
2. main execution state provides a nonempty `task_id`, `feature_branch`, and
   40-character `authorization_head_sha`;
3. main records `task_execution_authorized: true`;
4. the current branch exactly equals main's `feature_branch`;
5. branch-local repository, task ID, and feature branch equal main's values;
6. branch-local task or correction execution authority is true;
7. the authorization head is an ancestor of local `HEAD`;
8. the current branch upstream is exactly
   `refs/remotes/origin/<feature_branch>`; and
9. `origin/<feature_branch>` exists.

### Phase semantics

- `preflight`: local `HEAD` must exactly equal `origin/<feature_branch>`.
- `prepush`: `origin/<feature_branch>` must be an ancestor of local `HEAD`; a
  diverged or rewritten destination fails.
- `postpush`: local `HEAD` must exactly equal `origin/<feature_branch>`.

The command must never resolve task identity from the previously checked-out
branch before reading synchronized main provenance.

## Documentation behavior

Update `AGENTS.md` and create
`docs/execution/TASK_EXECUTION_STANDARD.md` so an executor must:

1. synchronize and verify `main`;
2. switch explicitly to the feature branch named by main state;
3. run the command in `preflight` before task edits;
4. run it in `prepush` immediately before pushing; and
5. fetch and run it in `postpush` after pushing.

A nonzero command result is fail-closed. Do not continue, publish to another
branch, or repair the missing contract from chat.

## Named acceptance tests

Create `tests/test_execution_branch_binding.py`. Tests must construct temporary
Git repositories and execute the real command. Required independent tests are:

1. `test_preflight_accepts_exact_authorized_branch`
2. `test_preflight_rejects_wrong_current_branch`
3. `test_preflight_rejects_unsynchronized_main`
4. `test_preflight_rejects_branch_task_identity_mismatch`
5. `test_preflight_rejects_missing_authorization_ancestry`
6. `test_prepush_rejects_diverged_remote_destination`
7. `test_postpush_requires_exact_remote_head`
8. `test_failure_output_uses_stable_reason_code`

The tests must assert exit codes, JSON success keys, and exact reason-code
prefixes. Keyword-presence-only documentation tests do not satisfy this task.

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

Do not modify the superseded predecessor branch, the preserved builder branch,
`REPOSITORY_CONTEXT_INDEX.md`, a lean-delivery standard, analytical/package
code, contracts, fixtures, design, assignment, inference, MIP, MMM, coordination
files, CI, release configuration, or capability state.

Do not create a PR, merge, rebase, squash, force-push, or delete preserved
branches.

## Validation gate

Run on the frozen task-owned tree:

- parse `docs/execution/EXECUTION_STATE.json` as JSON;
- `python -m py_compile scripts/verify_authorized_task_binding.py`;
- `pytest -q tests/test_execution_branch_binding.py` with exact pass/fail/skip
  counts;
- `git diff --check`;
- exact changed-path verification against the seven owned paths;
- command `prepush` verification before push;
- command `postpush` verification after fetch; and
- exact local/remote feature-head equality.

Docker, the complete package suite, analytical tests, Ruff, and mypy are
`not_required` because this task changes a standard-library repository-governance
command and isolated temporary-Git tests only; it does not import or alter the
GeoX package, public API, numerical truth, or analytical runtime. Discovery of an
unexpected package/runtime dependency is a genuine blocker rather than
permission to widen scope.

## Publication

On success publish `ready_for_review` with:

- one implementation SHA;
- exact command and test counts;
- empty blockers;
- task execution true and correction execution false;
- merge and PR authority false;
- null reviewed and approval SHAs;
- unchanged capability authority; and
- one current completion report.

Publish `blocked` only for a genuine synchronization, Git capability,
environment, authority, or required-validation obstruction with exact diagnostics
and a live resolution condition.

## Correction limit

One correction cycle is permitted only for failure against the frozen acceptance
contract. A second failed review supersedes this task without merge. New design
preferences become separately proposed successors.

## Deferred successor

`GEOX_PUBLICATION_LIFECYCLE_AND_RECEIPT_001` remains proposed and unauthorized
until this task is approved, merged, and closed.

**Unresolved execution-blocking design questions: none.**
