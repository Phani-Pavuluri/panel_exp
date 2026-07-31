# Active Task

**Status:** authorized adoption
**Owner:** GeoX repository governance
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** GeoX `main` / `373b2fb34f4e5f93b43fd2009de529acb0ccc8ed`
**Update trigger:** execution-state transition, review decision, or task closure.

## Identity

- **Task ID:** `GEOX_REPO_NATIVE_EXECUTION_HANDOFF_V2_ADOPTION_001`
- **Base branch/SHA:** `main` / `373b2fb34f4e5f93b43fd2009de529acb0ccc8ed`
- **Feature branch:** `feat/geox-repo-native-execution-handoff-v2-adoption-001`
- **Execution mode:** `branch_and_fast_forward`
- **Canonical MIP V2 pin:** `Phani-Pavuluri/marketing_intelligence_platform@38f88467f55d5bc4cc64e5a58b0f08f1639a40d0`
- **Canonical MMM workflow pin:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Superseded task:** `GEOX_REPO_NATIVE_EXECUTION_HANDOFF_ADOPTION_001`
- **Capability authorizations changed:** `false`

## Why a new task is required

The V1 GeoX adoption task was authorized on `main` but never executed: no
feature branch, implementation commit, completion report, review head, merge, or
closure exists. It pins obsolete MIP commit `5eebba6` and uses the legacy
`approved_for_merge` lifecycle.

This V2 task supersedes that unstarted task. It does not claim the V1 task was
implemented, reviewed, merged, or closed.

## Objective

Adopt the final MIP V2 repository-native workflow in GeoX and establish durable
Git-backed task discovery, execution, review, exact-head approval, fast-forward
merge, closure, and fresh-chat handoff. This is workflow governance only.

No GeoX analytical behavior or authority is owned or authorized.

## Owned files

Execution may create or modify only:

- `AGENTS.md`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `tests/test_repo_native_execution_handoff.py`
- one existing documentation index only when strictly required for discovery

Do not modify estimators, designs, assignment, inference, contracts, fixtures,
numerical truth, governed-readout semantics, roadmaps, validation registries,
MIP, or MMM.

## Task-authoring boundary

The pre-authoring base is `373b2fb34f4e5f93b43fd2009de529acb0ccc8ed`.
Verify `base_sha..authorization_head_sha` changes only the stable task and report
files. Because a commit cannot contain its own SHA, one state-only commit may
exist immediately after `authorization_head_sha` solely to record that boundary.
No other intervening path or commit is permitted.

Create the feature branch from exact synchronized post-authoring `main`.

## Prerequisites

1. Before task discovery, classify the full worktree and fail closed on unrelated
   tracked changes or unexpected untracked paths. Permit untracked content only
   below `.codex/` and `docs/tasks/`; never stage or commit it.
2. Run `git fetch --prune origin`; hydrate shallow or missing history; switch to
   `main`; run `git pull --ff-only origin main`; prove local `main` equals
   `origin/main`.
3. Verify MIP pin `38f88467f55d5bc4cc64e5a58b0f08f1639a40d0`
   exists on MIP `main`, contains `docs/execution/TASK_EXECUTION_STANDARD.md`,
   and records closed V2 recovery.
4. Verify MMM pin `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
   exists on MMM `main` and records closed V2 workflow reconciliation.
5. Verify the superseded GeoX V1 task was never implemented: no corresponding
   feature branch, implementation commit, completion report, or merge exists.
6. Verify the task-authoring boundary and current GeoX checkpoint exactly.

## Required implementation

1. Create and switch to
   `feat/geox-repo-native-execution-handoff-v2-adoption-001` from synchronized
   post-authoring `main`.
2. Create `AGENTS.md` requiring, before task discovery:
   - full worktree classification;
   - only `.codex/` and `docs/tasks/` as permitted local-only untracked paths;
   - `git fetch --prune origin` and history hydration;
   - `git switch main` and `git pull --ff-only origin main`;
   - exact local/remote `main` equality;
   - then state, task, context index, relevant GeoX evidence, and pinned MIP
     standard/program files.
3. Implement V2 execution semantics:
   - `Execute the active task` verifies authorization, boundary, prerequisites,
     branch, scope, validation, commit, push, and stops at `ready_for_review`;
   - exact remote-head approval is external;
   - no `approved_for_merge` state and no pre-merge approval metadata commit;
   - persisted `merge_authorized` remains false until closure;
   - merge uses `git merge --ff-only`, with no PR, squash, rebase, merge commit,
     force update, or history rewrite;
   - exactly one post-merge closure commit records approval, validation,
     synchronization, authority, and cleanup.
4. Create `REPOSITORY_CONTEXT_INDEX.md` as a concise navigation index covering:
   - pinned MIP standard and canonical MIP program files;
   - GeoX method-family status, instrument identity, and selection-gate state;
   - governed experiment-readout contract and certified fixtures;
   - numerical-truth fixtures and validation evidence;
   - active roadmaps, open investigations, D6/release evidence, and deferred
     package-side agent roadmap;
   - MMM as compatibility owner and MIP as consumer/orchestrator;
   - exact cross-repository checkpoint verification.
5. Add a Fresh Chat Bootstrap requiring Git synchronization before reading
   execution state and forbidding modification or authorization without explicit
   user direction.
6. Upgrade state to `geox_repo_execution_state_v2`. Allowed statuses are only:
   `idle`, `proposed`, `authorized`, `in_progress`, `blocked`,
   `ready_for_review`, `changes_requested`, `merged`, and `superseded`.
7. Add `tests/test_repo_native_execution_handoff.py` to enforce:
   - V2 schema/status vocabulary and canonical MIP pin;
   - mandatory bootstrap order and local-only path policy;
   - task/state/report/context agreement;
   - external exact-head approval, no pre-merge approval commit,
     fast-forward-only merge, and one closure commit;
   - state-specific invariants for `authorized`, `ready_for_review`, and
     `merged`;
   - `capability_authorizations_changed: false`.
8. Write `TASK_COMPLETION_REPORT_V2` with exact lineage, changed files,
   prerequisites, validation, local versus GitHub-observed evidence, limitations,
   branch state, and authority impact.
9. Run focused execution-handoff and relevant documentation/governance tests,
   JSON and Markdown/path checks, Ruff, mypy, `git diff --check`, and
   Docker-backed `make validate`.
10. On any failed prerequisite or validation, publish an accurate `blocked`
    branch state and stop.
11. On success, publish `ready_for_review` with execution authorization true,
    merge authorization false, null reviewed/approval SHAs, populated
    implementation SHA, no blockers, and unchanged capability authority.
12. Push and verify the exact remote branch head, then stop. Do not create a PR,
    merge, or delete branches during execution.

## Completion and authority requirements

The report must explicitly confirm whether the task changed or authorized:

design eligibility; assignment; estimator or inference status; instrument
identity; governed-readout semantics; numerical truth; multicell/shared-control
status; production inference; package-side agents; CalibrationSignal;
ExperimentEvidence; TrustReport; DecisionSurface; recommendations; LLM
decisioning; or budget authority.

Every item must remain unchanged and unauthorized.

## Later approved merge and closure

Only after explicit approval of the exact remote V2 branch head may Codex merge.
It must repeat synchronization and validation, fast-forward the approved SHA,
push and verify `main`, delete the V2 branch, and create exactly one closure
commit. The closure commit becomes the canonical GeoX workflow pin.

## Prohibited scope

Do not authorize or change production p-values or confidence intervals,
TrustReport operations, CalibrationSignal/MMM ingestion, LLM decisioning,
production decisioning, live APIs, schedulers, budget optimization, selector or
router runtime, method-family production inference, multicell production claims,
or package-side agents.
