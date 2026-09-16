<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `ready_for_review`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_TASKCTL_CORRECTION_FIXTURE_BASELINE_REPAIR_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `7c3799af5e406fe65161daf7d474cb363fa766b0`
- **Authorization provenance:** `25d26dec07659150ec4d23eae012b6f4fc3d50d8`
- **Feature branch:** `fix/geox-taskctl-correction-fixture-baseline-repair-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `d713480f5c520efeab06d7a3b3f15eeb68b80d8f`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `ready_for_review`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->
## Repository and branch

- Repository: `Phani-Pavuluri/panel_exp`
- Local path: `/Users/phani/Desktop/panel_exp`
- Authorized implementation branch:
  `fix/geox-taskctl-correction-fixture-baseline-repair-001`
- Fresh-main base: `7c3799af5e406fe65161daf7d474cb363fa766b0`

Create the authorized branch only after verifying that local `main` and
`origin/main` are identical, task-authoring commit
`25d26dec07659150ec4d23eae012b6f4fc3d50d8` is its ancestor, and intervening
commits are task-authoring metadata only. The branch must not already exist
locally or remotely. Do not execute from another branch.

## Objective

Repair `GEOX-TASKCTL-CORRECTION-FIXTURE-BASELINE-001` by aligning the synthetic
`changes_requested` fixture in `tests/execution/test_taskctl.py` with the
current lifecycle evidence required by `taskctl.validate_state`.

This is a test-fixture-only lifecycle repair. Preserve the fail-closed taskctl
invariants. Do not change taskctl implementation, generated views, the handoff
status parser, package/runtime behavior, analytical behavior, or another defect.

## Prerequisites and evidence

- Synchronized GeoX main: `7c3799af5e406fe65161daf7d474cb363fa766b0`.
- Blocked parser-repair branch:
  `fix/geox-current-main-handoff-status-parser-repair-001`.
- Exact blocked remote head:
  `2d262fae8d8a904aa0f8332395588c37f6f74ccd`.
- Valid parser implementation evidence:
  `ddb8d3e9cdaaf253e8b2f93a8ecc0dc54a8effed`.
- Concrete prerequisite defect:
  `GEOX-TASKCTL-CORRECTION-FIXTURE-BASELINE-001`.
- Failing node:
  `tests/execution/test_taskctl.py::test_correction_closure_requires_explicit_evidence_and_updates_counters`.
- Fresh-main reproduction: `1 failed in 1.40s`.
- Observed cause: `prepare_changes_requested()` sets `changes_requested` and
  correction authority but omits the non-null implementation SHA and paired
  rejected review/implementation SHAs required before `taskctl.sync()`.
- Preserved cross-repository pins are MIP
  `a293ce52a813709ca624332123019139928cc51e` and MMM
  `fe8e784923994406a2e4907d28debd872d61fd73`; neither repository is modified
  or sequenced by this task.

## Owned paths

Only these paths may change during execution:

- `tests/execution/test_taskctl.py`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/ACTIVE_TASK.md` through the generated lifecycle view only
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify `docs/execution/REPOSITORY_CONTEXT_INDEX.md` during task
execution. All other paths are read-only for this milestone.

## Required behavior

1. Perform the root `AGENTS.md` bootstrap exactly and prove the authorized base
   and branch ancestry before editing.
2. Reproduce the named fixture failure on the authorized baseline and record
   the exact result.
3. Change only `prepare_changes_requested()` in
   `tests/execution/test_taskctl.py` so its synthetic state includes a valid
   non-null `implementation_commit_sha` and paired valid
   `rejected_review_head_sha` / `rejected_implementation_commit_sha` before
   `taskctl.sync()`.
4. Preserve `changes_requested`, correction authority, correction counters,
   null reviewed/approval evidence, protected authorities, and the test's
   explicit-correction closure assertions. Use deterministic test-only SHAs;
   do not read or invent repository history.
5. Do not modify `panel_exp/execution/taskctl.py`,
   `tests/test_repo_native_execution_handoff.py`, generated Markdown format,
   runtime/package code, analytical code, other fixtures, or unrelated tests.
6. Record focused validation and changed paths in the completion report. Keep
   every protected authority `false` and all four current-main defect IDs
   unresolved.
7. Use task control to synchronize and verify generated views, then stop at
   `ready_for_review` when the repair evidence is complete.

## Acceptance and validation

Run and report these commands:

```text
.venv/bin/python -m panel_exp.execution.taskctl check
.venv/bin/python -m pytest -q tests/execution/test_taskctl.py::test_correction_closure_requires_explicit_evidence_and_updates_counters
.venv/bin/python -m pytest -q tests/execution/test_taskctl.py
.venv/bin/python -m pytest -q tests/execution/test_taskctl.py tests/test_repo_native_execution_handoff.py::test_status_invariants_are_closure_safe
git diff --check
git diff --name-only <authorized-baseline>...HEAD
.venv/bin/python -m panel_exp.execution.taskctl check
```

Acceptance requires exact authorized ancestry, all three pytest commands
passing, only owned changed paths, consistent canonical/generated lifecycle
state, no runtime or analytical change, and no changed protected authority.

Do not run `make validate-docker` for this test-only repair. It is not an
acceptance command for this isolated fixture milestone. The known handoff
status-parser failure is also outside this task and remains parked at exact
remote head `2d262fae8d8a904aa0f8332395588c37f6f74ccd`.

## Commit and push

Create one independently reviewable implementation commit on the authorized
branch, then update the lifecycle evidence to `ready_for_review` with the exact
implementation SHA as repository rules require. Commit the resulting review
receipt if needed, push only
`fix/geox-taskctl-correction-fixture-baseline-repair-001`, prove
the exact remote head, and stop for external review.

Do not create a PR, merge, squash, rebase, force-push, create a merge commit,
authorize a successor, modify or merge the blocked parser branch, repair
another defect class, or change capability,
certification, CalibrationSignal, MMM, simulation, planning, recommendation,
real-data, runtime, pilot, or production authority.
