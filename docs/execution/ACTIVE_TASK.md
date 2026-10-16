<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `proposed`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_VALIDATION_ENTRYPOINT_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `a360c4cfcfa48eeaaf215beec6f44c47a462d9b5`
- **Authorization provenance:** `null`
- **Feature branch:** `feat/geox-validation-entrypoint-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `null`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `proposed`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->

## Primary outcome and owner direction

Materialize the owner-approved separate validation entrypoint while preserving ordinary `run_design()` behavior and the existing validation-owned guardrail boundary. Muse owns implementation; Codex independently reviews. This is a bounded validation orchestration task, not a production-default, statistical, certification, export, sibling, or analytical authority change.

## Proposed contract and scope

Add `panel_exp/validation/validated_design_runner_001.py` with validation-owned `run_validated_design(...)` that injects callbacks into the existing unmodified design runner, evaluates the existing contract-to-combination-to-enforcement bundle, attaches frozen evidence copies, preserves error propagation and `validate_after_assign` semantics, and returns the existing triple. `build_contract` is required to prevent wrong-builder emission. The ordinary `run_design()` path remains unchanged and receives a dedicated regression guard.

## Scope, failure semantics and named acceptance

Owned paths are the new validation module, two focused guardrail test files with invocation-line changes only, and the three stable execution files. Existing production modules, default orchestration, evidence vocabulary, statistical truth, export/certification behavior, sibling repositories, and authority flags are read-only. No implementation execution is authorized by this proposal.

Acceptance evidence must preserve payload identity, existing error behavior, and default-path output equality. Existing `NOT_EVALUATED` semantics are reported as observed; no guardrail or statistical assertion may be weakened.

## Gate and publication boundary

Tier 1 acceptance requires both guardrail tests, assert-identical payload proof, the default-path regression, focused/native/handoff/combined checks, JSON parsing, `git diff --check`, exact owned-path and ancestry checks, and a durable receipt on the frozen exact tree. Full production or analytical validation is outside this task.

The preceding native provenance audit is the merged prerequisite. Preserve rejection history and historical cross-repository pins byte-for-byte. This task is GeoX-only under `WS-GEOX-VALIDATION-ENTRYPOINT-001`; MIP and MMM remain independent.

The task is proposed only. Authorization, feature-branch creation, implementation, review, merge, PR creation, certification, and production designation remain false until the repository records them through its native lifecycle.
