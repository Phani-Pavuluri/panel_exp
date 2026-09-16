<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `merged`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_REASSESSMENT_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `d819fb17ccb2be90bb296d528ca7e0b05548f766`
- **Authorization provenance:** `b003d7915d635413fd45fcb98e4ee36ccbc0c7b8`
- **Feature branch:** `audit/geox-main-test-isolation-and-checkpoint-context-reassessment-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `7cef5d0b0d7b854d1dd6b9ab1f5b326606da9ca5`
- **Reviewed head:** `0f79d277afac4a8675bc3a1365ae89c6da8dcbf9`
- **Rejected review head:** `e146620e2d1b4b3c5d87e14a5b6e9c01d18a303a`
- **Rejected implementation commit:** `746f7082a5cd727461a076867f1dd17bc25d23b6`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `1`
- **Correction cycles remaining:** `0`
- **Review decision:** `merged`
- **Local feature-branch cleanup:** `observed_deleted`
- **Remote feature-branch cleanup:** `observed_deleted`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->
## Repository and branch

- Repository: `Phani-Pavuluri/panel_exp`
- Local path: `/Users/phani/Desktop/panel_exp`
- Authorized implementation branch:
  `audit/geox-main-test-isolation-and-checkpoint-context-reassessment-001`
- Fresh-main base: `d819fb17ccb2be90bb296d528ca7e0b05548f766`

Create the authorized branch only after verifying that local `main` and
`origin/main` are identical, task-authoring commit
`b003d7915d635413fd45fcb98e4ee36ccbc0c7b8` is its ancestor, and intervening
commits are task-authoring metadata only. The branch must not already exist
locally or remotely. Do not execute from another branch.

## Objective

Determine whether the historical synchronized-main validation debt recorded by
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` still exists on
the exact authorized current-main baseline. Publish one evidence-backed result:

1. retire the parked dependency because the current repository-authored gate
   no longer reproduces the historical debt; or
2. identify a concrete remaining current-main defect with exact failing test,
   command, and clean-baseline comparison evidence.

This is a validation-only checkpoint reassessment. Do not repair any defect and
do not change analytical, package, runtime, test, builder, validator, manifest,
or fixture behavior.

## Prerequisites and evidence

- Synchronized GeoX main and lifecycle authority:
  `d819fb17ccb2be90bb296d528ca7e0b05548f766`.
- Parked historical branch:
  `fix/geox-main-test-isolation-and-checkpoint-context-recovery-001` at
  `0c16766f47cae903c9a085043dfa51949e61ea68`.
- Historical implementation commit:
  `a625a9dac6b97b05c4044dc5af5ae7875a63e889`.
- Merge base with authorized main:
  `b3f6b9acf81ff268c21d96d1014f8780fba5644f`.
- Observed divergence at authorization: authorized main is 79 commits ahead
  and the parked branch is 13 commits ahead of the merge base.
- Historical result: focused and adjacent tests reported `71 passed`; the full
  Docker gate reported `23 failed, 6151 passed, 28 skipped`; clean-main replay
  reproduced 22 failures, leaving one branch-specific lifecycle failure that
  was repaired before the parked task remained blocked.
- Current relevant surfaces:
  `tests/contracts/test_geox_calibration_source_manifest.py`,
  `tests/fixtures/test_geox_calibration_source_manifest_generator.py`,
  `panel_exp/contracts/geox_calibration_source_manifest.py`,
  `scripts/build_geox_calibration_source_manifest.py`,
  `tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json`, and
  `tests/fixtures/geox_governed_readouts/`.
- Preserved cross-repository pins are MIP
  `a293ce52a813709ca624332123019139928cc51e` and MMM
  `fe8e784923994406a2e4907d28debd872d61fd73`; neither repository is modified
  or sequenced by this task.

Treat the parked branch and all of its commits as immutable read-only evidence.
Do not cherry-pick, merge, rebase, copy, or revive them.

## Owned paths

Only these paths may change during execution:

- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/ACTIVE_TASK.md` through the generated lifecycle view only
- `docs/execution/LATEST_COMPLETION_REPORT.md`
- `docs/track_d/GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_REASSESSMENT_001.md`

Do not modify `docs/execution/REPOSITORY_CONTEXT_INDEX.md` during task
execution. All other paths are read-only for this milestone.

## Required behavior

1. Perform the root `AGENTS.md` bootstrap exactly and prove the authorized base
   and branch ancestry before validation.
2. Record the parked branch head, implementation commit, merge base, divergence
   counts, changed paths, and the semantic differences between the parked test
   changes and current main. Do not treat patch non-equivalence alone as a
   defect.
3. Run the current-main focused validator and generator tests and the directly
   adjacent governed-readout tests. Record exact commands and results.
4. Run the complete repository-authored Docker gate with
   `make validate-docker`. A local environment issue is not sufficient evidence
   of product debt: attempt the repository-supported repair or Docker path and
   record exact diagnostics if execution still cannot complete.
5. If the full gate fails, reproduce each relevant failure against an untouched
   worktree at exact base
   `d819fb17ccb2be90bb296d528ca7e0b05548f766`. Classify failures as current-main
   defects, reassessment-branch lifecycle regressions, or environment failures.
   Name concrete current-main defects; do not make or propose code fixes in the
   implementation commit.
6. Publish the reassessment report with exact tree SHA, commands, counts,
   failures, comparison to the historical 22-failure debt, conclusion, and
   limitations. The conclusion must be exactly one of
   `retired_no_longer_reproduced` or `concrete_current_main_defect_identified`.
7. Update canonical state consistently. When retired, set the parked dependency
   state to `retired_no_longer_reproduced`. When a concrete defect remains, set
   it to `concrete_current_main_defect_identified` and record the exact defect
   identifier in the report and the canonical `parked_isolation_dependency`
   evidence. Preserve every protected authority as `false`; do not place a
   completed reassessment in top-level `blocked` state merely because it found
   a baseline defect.
8. Use the repository task control to synchronize and verify generated views,
   then stop at `ready_for_review` if the reassessment evidence is complete.

## Acceptance and validation

Run and report these commands, resolving the focused adjacent test paths from
the current repository rather than inventing absent files:

```text
.venv/bin/python -m panel_exp.execution.taskctl check
.venv/bin/python -m pytest -q tests/contracts/test_geox_calibration_source_manifest.py tests/fixtures/test_geox_calibration_source_manifest_generator.py
make validate-docker
git diff --check
git diff --name-only <authorized-baseline>...HEAD
.venv/bin/python -m panel_exp.execution.taskctl check
```

Acceptance requires exact authorized ancestry, an evidence-complete report, a
single unambiguous conclusion, no behavioral file changes, only owned changed
paths, consistent canonical/generated lifecycle state, and no changed protected
authority. The full gate need not pass only when a concrete current-main defect
is reproduced and named; an unclassified failure is not an acceptable result.

## Commit and push

Create one independently reviewable implementation commit on the authorized
branch, then update the lifecycle evidence to `ready_for_review` with the exact
implementation SHA as repository rules require. Commit the resulting review
receipt if needed, push only
`audit/geox-main-test-isolation-and-checkpoint-context-reassessment-001`, prove
the exact remote head, and stop for external review.

Do not create a PR, merge, squash, rebase, force-push, create a merge commit,
delete the parked branch, authorize a successor, or change capability,
certification, CalibrationSignal, MMM, simulation, planning, recommendation,
real-data, runtime, pilot, or production authority.
