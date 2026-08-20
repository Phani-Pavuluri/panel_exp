# Active Task

**Status:** changes_requested
**Task ID:** `GEOX_EXECUTION_LIFECYCLE_SINGLE_SOURCE_ADOPTION_001`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `d44e114df27b276966d4c78266a8b451e5c05b37`
**Implementation branch:** `feat/geox-execution-lifecycle-single-source-adoption-001-correction`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 3 — execution-governance state migration
**Task execution authorized:** `true`
**Correction execution authorized:** `true`
**Merge authorized:** `false`
**PR creation authorized:** `false`
**Unresolved execution-blocking design questions:** none


## Objective

Adopt GeoX-local single-source execution lifecycle semantics equivalent to the
merged MIP reference at
`Phani-Pavuluri/marketing_intelligence_platform@b0f57701a55d5cbe1d94692bf378a23d03945646`.
`docs/execution/EXECUTION_STATE.json` becomes the sole mutable lifecycle
authority; `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md` contain
deterministic generated views.

## Contract

Migrate `geox_repo_execution_state_v2` in place to
`geox_repo_execution_state_v3`. Use exactly
`maximum_correction_cycles`, `correction_cycles_completed`, and
`correction_cycles_remaining`, with completed plus remaining equal to maximum.
Preserve historical D5 closure meaning without changing analytical or product
meaning.

Use exactly one pair of generated-view markers per stable execution document:
`BEGIN GEOX TASKCTL EXECUTION VIEW` and `END GEOX TASKCTL EXECUTION VIEW`.
Only bytes inside the generated block may change; missing, duplicate, nested,
reversed, or malformed markers fail closed. Marker examples in this contract
must not be represented as live HTML marker pairs.

Generated fields render deterministically from canonical state: status/current
decision, task identity, repository and execution mode, base and authorization
provenance, branch state, execution/merge/PR authority, implementation and
review evidence, blockers, correction counters, review decision, cleanup
evidence, and capability-authority status. Use lowercase booleans, literal
`null`, `none` for empty blockers, and the generated-view warning.

Adopt the lifecycle states `idle`, `proposed`, `authorized`, `in_progress`,
`blocked`, `ready_for_review`, `changes_requested`, `merged`, and `superseded`.
`approved_for_merge` is forbidden. Transitions must be table-driven,
evidence-driven, fail closed, validate canonical state and both current views
before any write, validate complete candidate state/views before replacement,
and preserve protected GeoX analytical, product, runtime, certification,
capability, CalibrationSignal, simulation, planning, recommendation, real-data,
pilot, production, and successor-task authorities.

## Implementation boundary

Own only `AGENTS.md`, `panel_exp/execution/`, `tests/execution/`, the three
stable execution files, and an existing GeoX execution-standard file only if
present on synchronized Git. Do not modify analytical methods, assignment,
inference, TBR, SCM, UnitJackKnife, calibration-source behavior, artifacts, P2
semantics, MIP, MMM, CI, or runtime dependencies.

The prior blocked implementation branch/head
`feat/geox-execution-lifecycle-single-source-adoption-001@cf816fcb781b4dc5df6173e68a5a37c2b766c480`
is preserved as historical evidence only. Do not cherry-pick, merge, rebase, or
reuse its executable ancestry; implementation must be recreated on the fresh
branch identity from this authorization.

## Revised focused validation

Require JSON/schema migration checks, focused execution-governance and
transition/reason-code tests, generated-view divergence and malformed-marker
tests, byte-preserving/idempotent sync tests, correction-counter and closure
invariant tests, protected-authority tests, migrated-tree `taskctl check`, Ruff,
mypy when supported, compile validation, `git diff --check`, and exact
changed-path verification. Under the revised focused-validation policy, the
full Docker gate is not required for this authorization; any separately
observed baseline debt must not be misclassified as an adoption regression.

No successor task is authorized. MMM lifecycle adoption remains separately
owned. Stop at `ready_for_review`; do not create a PR or merge.

The rejected implementation head
`46e598babf8377b0334d9b66c0223e829fce8197` is under correction review. The
historical and rejected branches remain untouched; correction work must use the
new correction branch from current main and preserve all protected authorities.
