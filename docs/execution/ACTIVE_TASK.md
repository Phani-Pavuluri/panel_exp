<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** blocked

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_EXECUTION_LIFECYCLE_SINGLE_SOURCE_ADOPTION_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `5ab881296c7c8248076bad61292b255aaade11d8`
- **Authorization provenance:** `5ab881296c7c8248076bad61292b255aaade11d8`
- **Feature branch:** `feat/geox-execution-lifecycle-single-source-adoption-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `8731beeb8fb41bf90c8b1fd1ba8db9fbad6e497d`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `DOCKER_GATE_BASELINE_VALIDATION_DEBT`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `blocked`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->

## Objective

Adopt GeoX-local single-source lifecycle semantics equivalent to the merged MIP
reference at `Phani-Pavuluri/marketing_intelligence_platform@b0f57701a55d5cbe1d94692bf378a23d03945646`.
`docs/execution/EXECUTION_STATE.json` becomes the sole mutable authority;
`ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md` receive deterministic
generated lifecycle views.

## Canonical schema and migration

Migrate `geox_repo_execution_state_v2` in place to
`geox_repo_execution_state_v3`. Use exactly
`maximum_correction_cycles`, `correction_cycles_completed`, and
`correction_cycles_remaining`, with completed plus remaining equal to maximum.
The current closed D5 lineage migrates as `1 / 0 / 1` (maximum/completed/
remaining), changing representation only.

Generated views use exactly one pair of markers per document. The marker names
are documented without HTML comment delimiters so this contract body cannot be
parsed as a live generated view: `BEGIN GEOX TASKCTL EXECUTION VIEW` and
`END GEOX TASKCTL EXECUTION VIEW`.

Only bytes between markers may be replaced. Missing, duplicated, reversed or
nested markers fail closed. Generated blocks contain the MIP-derived deterministic
field order, lowercase booleans, literal `null`, `none` for empty blockers, and
`_Generated from \`EXECUTION_STATE.json\`; do not edit._`.

The deterministic field order is: status/current decision, Task ID, Repository,
Execution mode, Base SHA, Authorization provenance, Feature branch, Feature
branch created, Task execution authorized, Correction execution authorized,
Merge authorized, PR creation authorized, Implementation commit, Reviewed head,
Rejected review head, Rejected implementation commit, Approval commit, Blockers,
Maximum correction cycles, Correction cycles completed, Correction cycles
remaining, Review decision, Local feature-branch cleanup, Remote feature-branch
cleanup, and Capability authorizations changed. The ACTIVE_TASK status line is
`**Status:** <status>` and the completion-report decision line is
`**Current decision:** \`<status>\``.

Lifecycle states are `idle`, `proposed`, `authorized`, `in_progress`, `blocked`,
`ready_for_review`, `changes_requested`, `merged`, and `superseded`;
`approved_for_merge` is forbidden. External exact-head approval remains outside
the tree and `merge_authorized` remains false.

## Future implementation boundary

Owned paths are `AGENTS.md`, `panel_exp/execution/`, `tests/execution/`, the
three stable execution files, and an existing GeoX execution-standard file only
if present. No analytical, assignment, inference, TBR, SCM, UnitJackKnife,
calibration-source, artifact, P2, runtime, MIP, MMM, or capability behavior may
change. No cross-repository runtime dependency is permitted.

Future API surface:

`python -m panel_exp.execution.taskctl check`
`python -m panel_exp.execution.taskctl sync`
`python -m panel_exp.execution.taskctl transition --to <status>`

Require table-driven transitions, stable reason codes, canonical validation
before writes, atomic candidate validation, divergence detection, byte-preserving
and byte-idempotent sync, correction-counter invariants, protected-authority
preservation, and migrated live-tree `taskctl check`.

## Validation and sequencing

Require focused execution-governance tests, Ruff, mypy when supported, JSON
validation, `git diff --check`, changed-path checks, taskctl check/idempotent
sync, and the repository-authored full Docker gate. Replay synchronized main if
baseline debt remains. MMM lifecycle adoption is separate; TBR remains
unauthorized and no successor authority changes occur.

No implementation branch has been created. No PR or merge is authorized.
