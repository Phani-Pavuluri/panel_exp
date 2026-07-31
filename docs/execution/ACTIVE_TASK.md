# Active Task

**Status:** merged
**Owner:** GeoX repository governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `GEOX_REPO_NATIVE_EXECUTION_HANDOFF_V2_ADOPTION_RECOVERY_001`
- **Pre-authoring base:** `main` / `b0c00228629dcc6231b85115d2448d8d7c20ee47`
- **Feature branch:** `feat/geox-repo-native-execution-handoff-v2-adoption-recovery-001`
- **Execution mode:** `branch_and_fast_forward`
- **Canonical MIP V2 pin:** `Phani-Pavuluri/marketing_intelligence_platform@38f88467f55d5bc4cc64e5a58b0f08f1639a40d0`
- **Canonical MMM workflow pin:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Superseded task:** `GEOX_REPO_NATIVE_EXECUTION_HANDOFF_V2_ADOPTION_001`
- **Superseded branch/head:** `feat/geox-repo-native-execution-handoff-v2-adoption-001` / `315ae7c996551c0f1fdb2414791be7e63586222d`
- **Superseded implementation:** `6dc5fe455c49d764932ee9abf05c5ab2f55f609c`
- **Capability authorizations changed:** `false`

## Purpose

Adopt the repository-native execution handoff V2 on the repaired GeoX `main`.
The prior V2 branch was created from obsolete history and is now diverged. It is
evidence only: do not merge, cherry-pick, rebase, reset, or copy its execution
metadata. Re-create the intended stable workflow artifacts on the current line,
correcting any state-coupled assumptions found in the old implementation.

This is a governance and execution-handoff task only. It must not alter GeoX
analytical behavior, method eligibility, assignment, estimation, inference,
instrument identity, governed readouts, numerical truth, MIP/MMM integration,
or package-side-agent authority.

## Owned files

Execution may modify only:

- `AGENTS.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `tests/test_repo_native_execution_handoff.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

No other file is authorized.

## Required implementation

1. Fetch/prune and hydrate history. Synchronize `main` and prove local
   `main == origin/main` before task discovery or branching.
2. Verify the task-authoring boundary recorded in
   `docs/execution/EXECUTION_STATE.json`: the pre-authoring base through the
   authorization head may change only the active task and completion report;
   synchronized `main` may then contain exactly one state-only recording commit.
3. Verify the superseded branch still equals
   `315ae7c996551c0f1fdb2414791be7e63586222d`. Do not modify or delete it during
   execution.
4. Create the exact feature branch from synchronized repaired `main`. Do not
   reuse the superseded branch.
5. Add root `AGENTS.md` defining the mandatory bootstrap order:
   - classify the full worktree;
   - allow only `.codex/` and `docs/tasks/` as local-only untracked paths;
   - `git fetch --prune origin` and hydrate missing history;
   - `git switch main`;
   - `git pull --ff-only origin main`;
   - prove `main == origin/main`;
   - only then read execution state, active task, repository context, relevant
     GeoX evidence, and pinned MIP/MMM standards.
6. Define fail-closed execution semantics in `AGENTS.md`: verify authorization,
   exact base/ancestry, prerequisites, exact branch, owned scope, validation,
   commit and push; stop at `ready_for_review`; approval is external; there is no
   `approved_for_merge` state or pre-merge approval metadata commit; merge only
   after exact-head approval by `git merge --ff-only`, followed by exactly one
   closure commit, push, synchronization, and cleanup; never create a PR or guess.
7. Add `docs/execution/REPOSITORY_CONTEXT_INDEX.md` with:
   - exact MIP and MMM pins;
   - canonical MIP execution/program documents;
   - GeoX method-family, instrument-identity, governed-readout, numerical-truth,
     roadmap, investigation, release, and deferred-agent evidence locations;
   - ownership boundaries among GeoX, MMM, and MIP;
   - a `Fresh Chat Bootstrap` section requiring connected GitHub as source of
     truth and a read-only orientation before modification or authorization.
8. Add `tests/test_repo_native_execution_handoff.py` validating:
   - schema version and allowed statuses;
   - exact canonical pins and task/state/report/context agreement;
   - full 40-character SHA or null rules;
   - task status agreement with state;
   - bootstrap ordering and local-only policy;
   - absence of an `approved_for_merge` state;
   - merge protocol language;
   - status-dependent invariants for `authorized`, `blocked`,
     `ready_for_review`, and `merged`.
9. The invariant test must remain valid after closure. Do not unconditionally
   require `reviewed_head_sha` to be null: it is null before review/merge and a
   full SHA in `merged`. `approval_commit_sha` remains null under this workflow.
10. Preserve current execution-state schema V2 and exact MIP/MMM pins. Do not
    introduce analytical or capability authority.
11. Preserve the completed import-health recovery and its explicit full-suite
    validation debt. Do not claim the entire GeoX suite passes.

## Validation gate

This docs-and-workflow task uses a scoped, isolated-Docker gate defined at task
authoring; it is not the prior recovery exception and does not waive validation
for product or method changes.

Required checks:

- `tests/test_repo_native_execution_handoff.py`;
- `tests/test_import_surface_health.py`;
- `tests/contracts/test_geox_mip_artifact_envelope_dry_run.py`;
- `tests/test_audit_fixes.py`;
- JSON parsing and required-field checks for `EXECUTION_STATE.json`;
- Markdown/path existence and exact-pin agreement checks;
- Ruff on the new Python test;
- `git diff --check`;
- exact changed-path verification against the owned-file list.

Run the focused tests in an isolated Docker/Poetry environment. Record exact
passed/skipped/warning counts. The unresolved full GeoX suite remains separate
repository-validation debt and is not a gate for this governance-only adoption.

## State transitions

- On success, publish `ready_for_review` with a full implementation SHA, empty
  blockers, `task_execution_authorized: true`, `merge_authorized: false`, null
  reviewed/approval SHAs, and unchanged capability authority.
- On failure, publish an accurate `blocked` state with specific blockers.
- Push and prove the exact remote branch head, then stop. Do not create a PR,
  merge, rebase, squash, force-push, or delete branches during execution.

## Acceptance criteria

- The three stable workflow artifacts exist on the repaired history and satisfy
  the focused validation gate.
- The invariant test is closure-safe and status-dependent.
- The diff is restricted to the six owned files.
- Exact MIP/MMM pins and authority boundaries are preserved.
- The old V2 branch remains unchanged during execution and is explicitly
  superseded, not merged.
- No PR or merge occurs before exact-head review and external approval.

## Post-merge sequence

Merged by `git merge --ff-only` at approved exact head
`ce7ae512bfe952853924b78cae22db87e092e4cf`; both completed branch cleanups
are recorded after closure.

After exact-head approval, fast-forward merge the fresh branch and create exactly
one closure commit. Delete the completed fresh branch locally and remotely. At
that closure step, also delete the old superseded V2 branch locally and remotely
after verifying it still equals `315ae7c996551c0f1fdb2414791be7e63586222d`.

## Prohibited authority

No design eligibility, assignment behavior, estimator or inference status,
instrument identity, governed-readout semantics, numerical truth,
multicell/shared-control claim, production inference, CalibrationSignal,
ExperimentEvidence, TrustReport, DecisionSurface, recommendation, LLM, budget,
or package-side-agent authority is changed or authorized.
