<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `ready_for_review`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_STRUCTURED_COMPLETION_EVIDENCE_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `a78c4017e06c6f0bfb4329e749972b516dfbc7e9`
- **Authorization provenance:** `55c4c6c237642195732d949d034e98763c5d8cac`
- **Feature branch:** `feat/geox-structured-completion-evidence-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `0d251c22bbfb41ab57c830b89f291464de2e1fa5`
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
  `feat/geox-structured-completion-evidence-001`
- Fresh-main base: `a78c4017e06c6f0bfb4329e749972b516dfbc7e9`

Create the authorized branch only after verifying that local `main` and
`origin/main` are identical, task-authoring commit
`55c4c6c237642195732d949d034e98763c5d8cac` is its ancestor, and intervening
commits are task-authoring metadata only. The branch must not already exist
locally or remotely. Do not execute from any other branch.

## Objective

Implement canonical structured completion evidence so a fresh reviewer can
recover the complete execution handoff from Git without relying on mutable
completion-report prose or a pasted Work-session summary.

Extend the existing single-source lifecycle; do not introduce a parallel task
or reporting subsystem. This is execution-governance work only.

## Prerequisites and evidence

- Synchronized GeoX main:
  `a78c4017e06c6f0bfb4329e749972b516dfbc7e9`.
- Merged parser-recovery prerequisite: reviewed head
  `d001891238b7124cdaa5d27d05a563b3386a5715`, closure
  `a78c4017e06c6f0bfb4329e749972b516dfbc7e9`.
- Current focused lifecycle/handoff baseline: `16 passed`.
- Recurrence evidence: fixture task head
  `1c3a2b01c5d85469c984c2139d5e16a8790a5537` and parser task head
  `b97d75a2a622441b4c063e1835caa93f6a0c9305` each reached canonical
  `ready_for_review` while retaining contradictory pre-implementation prose.
- Current cause: `taskctl.replace_view()` preserves completion-report content
  outside the generated markers, while schema v3 has no structured completion
  evidence for review handoff facts.
- Preserved cross-repository pins are MIP
  `a293ce52a813709ca624332123019139928cc51e` and MMM
  `fe8e784923994406a2e4907d28debd872d61fd73`; neither repository is modified
  or sequenced by this task.

Git remains authoritative for code, diffs, commits, and live remote branch
state. The execution session must not try to persist its own final remote branch
head inside that same branch; external review resolves that head, and merge
closure records it as `reviewed_head_sha`.

## Owned paths

Only these paths may change during execution:

- `panel_exp/execution/taskctl.py`
- `tests/execution/test_taskctl.py`
- `tests/test_repo_native_execution_handoff.py`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/ACTIVE_TASK.md` through the generated lifecycle view only
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify `docs/execution/REPOSITORY_CONTEXT_INDEX.md` during task
execution. All other paths are read-only for this milestone.

## Required behavior

1. Perform the root `AGENTS.md` bootstrap exactly and prove synchronized main,
   authorization provenance, branch absence, and authorized ancestry before
   creating the feature branch.
2. Migrate the canonical schema from `geox_repo_execution_state_v3` to
   `geox_repo_execution_state_v4` and add required top-level
   `completion_evidence`, which may be `null` before completion but must be a
   validated object for `ready_for_review`, `changes_requested`, and `merged`.
3. Define the evidence object exactly with:
   - nonempty, unique, repository-relative `changed_paths`;
   - nonempty `behavior_summary`;
   - nonempty `validation_results`, each containing nonempty `command`, exact
     nonempty `result`, and `outcome: "passed"`;
   - `validation_not_run`, each containing nonempty `command` and `reason`;
   - `blockers_and_limitations` as a list of nonempty strings, which may be
     empty; and
   - `prohibited_operations` with boolean occurrence fields for PR creation,
     merge, squash, rebase, and force-push, all required to remain `false` at
     review readiness.
4. Reject missing keys, wrong types, empty required values, duplicate/absolute
   or parent-traversing paths, non-passing validation results, and any prohibited
   operation with stable reason-coded errors.
5. Require complete evidence before transition to `ready_for_review`; preserve
   it through correction and merged lifecycle states. Do not require or store
   the execution branch's final remote head in this object.
6. Render `LATEST_COMPLETION_REPORT.md` completely from canonical state,
   including task/branch/implementation identity, GeoX/MIP/MMM pins, changed
   paths, behavior, validations, omitted validations, limitations, and
   prohibited-operation confirmation. Remove the legacy mutable suffix.
7. Keep `ACTIVE_TASK.md` as the generated lifecycle block plus the Git-authored
   task contract. Do not make the active task fully generated.
8. Make `taskctl check` reject any appended or edited completion-report prose;
   `taskctl sync` must deterministically migrate/remove the legacy suffix and be
   byte-preserving after the first synchronization.
9. Update transition and handoff tests so missing or malformed evidence cannot
   reach review readiness, valid evidence renders deterministically, pins remain
   present, corrections remain closure-safe, and exact remote-head resolution
   remains external.
10. Migrate this task's canonical state and use the new evidence path for its
    own completion handoff. Keep every protected authority `false`, keep the
    three unrelated defect IDs unresolved, and stop at `ready_for_review`.

## Acceptance and validation

Run and report:

```text
.venv/bin/python -m panel_exp.execution.taskctl check
.venv/bin/python -m pytest -q tests/execution/test_taskctl.py::test_ready_for_review_requires_structured_completion_evidence
.venv/bin/python -m pytest -q tests/execution/test_taskctl.py::test_completion_evidence_schema_fails_closed
.venv/bin/python -m pytest -q tests/execution/test_taskctl.py::test_completion_report_is_fully_generated
.venv/bin/python -m pytest -q tests/execution/test_taskctl.py::test_transition_renders_structured_completion_evidence
.venv/bin/python -m pytest -q tests/execution/test_taskctl.py
.venv/bin/python -m pytest -q tests/test_repo_native_execution_handoff.py
.venv/bin/python -m pytest -q tests/test_repo_native_execution_handoff.py tests/execution/test_taskctl.py
.venv/bin/python -m json.tool docs/execution/EXECUTION_STATE.json
git diff --check
git diff --name-only <authorized-baseline>...HEAD
.venv/bin/python -m panel_exp.execution.taskctl check
```

Acceptance requires exact authorized ancestry; all four named evidence nodes,
the complete taskctl file, complete handoff file, and combined adjacent suite
passing; schema v4 and generated-report determinism; only owned paths changed;
and no protected-authority, runtime, analytical, or unrelated-defect change.

Do not run `make validate-docker`. It is not proportionate or required for this
isolated execution-governance milestone.

## Commit and push

Create one independently reviewable implementation commit on the authorized
branch. Update the completion evidence, transition through task control to
`ready_for_review` using the exact implementation SHA, commit the review receipt
if needed, push only
`feat/geox-structured-completion-evidence-001`, prove exact
local/remote head equality, and stop for external review.

Do not create a PR, merge, squash, rebase, force-push, create a merge commit,
authorize a successor, add a parallel evidence file/subsystem, repair another
defect class, or change certification, CalibrationSignal, MMM compatibility,
simulation, planning, recommendation, real-data, runtime, pilot, or production
authority.
