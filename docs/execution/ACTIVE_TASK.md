# Active Task

**Status:** ready_for_review
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_EXECUTION_BRANCH_BINDING_REAUTHORING_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Feature branch:** `feat/geox-execution-branch-binding-reauthoring-001`
- **Authorization head:** `94d512eeffc549cdd98d0dffa166caeb9d75c2c1`
- **Rejected exact review head:** `f7535473a40aeffef5aad21ca404c391bc8fa0d7`
- **Retained implementation candidate:** `b0c56211305bbda9e609ea9d94242b7d61159104`
- **Correction cycle:** one and only permitted correction
- **Capability authorizations changed:** `false`

## Review decision

Exact remote head `f7535473a40aeffef5aad21ca404c391bc8fa0d7` is rejected for direct failures against the frozen contract authored at `94d512eeffc549cdd98d0dffa166caeb9d75c2c1`. Correction execution is authorized on the same branch. This decision adds no new feature, taxonomy, phase, test identity, or publication requirement.

## Required corrections

### 1. Use the exact separate-repository fixture topology

`tests/test_execution_branch_binding.py` currently creates `origin.git` inside the non-bare work repository root. The frozen contract requires a temporary root containing separate siblings:

- `<tmp>/origin.git` — bare repository;
- `<tmp>/work` — non-bare repository initialized on `main`.

Build and execute all scenarios from `<tmp>/work`. Do not stage or nest `origin.git` inside the worktree. Retain the `TemporaryDirectory` owner for the test lifetime. The scenario builder must return named paths and SHAs used by assertions, including the authorization head, synchronized main head, feature head, and remote feature head. Setup Git commands must fail the test immediately when they fail rather than being silently ignored.

### 2. Implement the exact required assertions and mutations

Keep exactly the eight frozen test names.

For `test_preflight_accepts_exact_authorized_branch`, assert all of the following:

- exit `0`;
- empty stderr;
- exactly the seven required JSON keys;
- `status == "ok"`;
- `phase == "preflight"`;
- exact expected task ID and feature branch;
- exact expected `main_head`, `local_head`, and `remote_feature_head` values returned by the scenario builder.

For `test_preflight_rejects_missing_authorization_ancestry`, create a real unrelated orphan commit, update synchronized main state to that exact unrelated SHA, push main, return to the unchanged authorized feature branch, and assert `AUTHORIZATION_ANCESTRY_MISSING`. A forty-zero placeholder SHA does not satisfy the frozen scenario.

Preserve the other six exact scenario mutations and failure assertions. No empty body, `pass`, skip, xfail, xpass, or conditional early return is allowed.

### 3. Correct stable runtime failure mapping

In `scripts/verify_authorized_task_binding.py`, a missing configured upstream currently escapes through generic `GIT_COMMAND_FAILED`. The frozen mapping requires:

- no configured upstream → `REMOTE_DESTINATION_MISMATCH`;
- configured upstream other than `origin/<feature_branch>` → `REMOTE_DESTINATION_MISMATCH`;
- absent remote-tracking feature ref → `REMOTE_FEATURE_BRANCH_MISSING`.

Preserve the exact reason-code set, three phases, seven success keys, read-only behavior, main-first identity resolution, and one-line stderr contract. Capture all Git diagnostics; no raw second stderr line may leak.

### 4. Publish the exact operational sequence in both guidance files

`AGENTS.md` and `docs/execution/TASK_EXECUTION_STANDARD.md` must explicitly state the already-frozen sequence:

1. `git fetch --prune origin`;
2. `git switch main`;
3. `git pull --ff-only origin main`;
4. prove `main == origin/main`;
5. read main execution state and switch to its exact feature branch;
6. run verifier `preflight` before edits;
7. implement and run declared validation;
8. run verifier `prepush` immediately before push;
9. push only `HEAD:refs/heads/<declared-feature-branch>` without force;
10. fetch that exact remote feature branch;
11. run verifier `postpush`;
12. prove exact local/remote feature-head equality.

A nonzero verifier result is fail-closed.

### 5. Publish complete and coherent review evidence

The final `ready_for_review` state and report must satisfy the existing publication contract:

- one implementation SHA;
- exact `8 passed`, `0 failed`, `0 skipped`, no xfail/xpass;
- all validation-category dispositions;
- empty blockers;
- task execution true and correction execution false;
- merge and PR authority false;
- null reviewed and approval SHAs;
- unchanged capability authority;
- current MIP pin `976d3a1daeae9c52c8772e5112574f698951a57c`;
- current MMM pin `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`;
- affected and modified repository GeoX only;
- consumer verification not applicable;
- GitHub-observed evidence separated from locally reported validation;
- limitations and validation debt stated explicitly;
- one current completion narrative;
- `review_decision: ready_for_review` with the current report as its source.

Do not retain stale `authorized` review-decision prose in a successful final state.

## Owned paths

Correction may modify only:

- `AGENTS.md`
- `scripts/verify_authorized_task_binding.py`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `tests/test_execution_branch_binding.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

No package, analytical, contract, fixture, CI, release, sibling-repository, coordination, builder, publication-lifecycle-successor, navigation-index, or capability work is authorized.

## Validation gate

Run on the final task-owned tree:

- parse `docs/execution/EXECUTION_STATE.json` as JSON;
- `python -m py_compile scripts/verify_authorized_task_binding.py tests/test_execution_branch_binding.py`;
- `pytest -q tests/test_execution_branch_binding.py` with exactly `8 passed`, `0 failed`, `0 skipped`, and no xfail/xpass;
- AST inspection proving exactly the eight required test functions exist and none has an empty body or `pass` statement;
- `git diff --check`;
- exact changed-path verification against the seven owned paths;
- verifier `prepush` immediately before push;
- push only the declared branch without force;
- fetch the exact remote branch;
- verifier `postpush`;
- exact local/remote feature-head equality.

Docker, full package tests, analytical tests, Ruff, and mypy remain `not_required` under the frozen contract.

A failing task-owned implementation or test is unfinished work, not a valid blocker. Publish `blocked` only for a genuine external Git, authentication, filesystem, environment, missing-history, or authority obstruction with exact evidence and a live resolution condition.

## Correction limit

This is the single permitted correction cycle. A further failed exact-head review supersedes this task without merge. No additional governance successor is authorized by this correction.

**Unresolved execution-blocking design questions: none.**
