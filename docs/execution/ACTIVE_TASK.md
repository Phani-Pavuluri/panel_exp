<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `proposed`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_TASKCTL_TEST_SCAFFOLD_REPAIR_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `0e5abc9ab4f5c87de9a308f0bb8422dd10a01023`
- **Authorization provenance:** `0e5abc9ab4f5c87de9a308f0bb8422dd10a01023`
- **Feature branch:** `feat/geox-taskctl-test-scaffold-repair-001`
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

## Primary outcome and authority (proposed — execution NOT authorized)

Repair the focused-test scaffolds that inherit task authority and evidence from live canonical state, so the live-coupled evidence tests validate green on every live-tree shape: scaffolds establish `task_execution_authorized`, `blockers`, and `completion_evidence` per requested status instead of inheriting them. Identical cases, identical expected codes — the assertions finally exercise the controller instead of the scaffold. Six focused tests are live-coupled on unauthorized and null-evidence trees (four reproduce on closed main; two more surface only where live evidence is null); all resolve to green with self-sufficient scaffolds. No controller, product, sibling, or authority change; no new codes; no weakened assertions. This contract is a proposal only: status `proposed`, task execution authority false. Provenance SHAs anchor the proposal baseline; they do not constitute authorization. Execution requires a future Git commit flipping status and execution authority. Muse-Spark owns implementation approach on authorization; Codex independently reviews.

Upon authorization, create `feat/geox-taskctl-test-scaffold-repair-001` from synchronized post-authoring main after mandatory bootstrap, taskctl check, authorization ancestry, metadata-only authoring boundary and branch-absence verification. Only one writer. Affected/modified: GeoX only. Workstream `WS-GEOX-TASKCTL-SCAFFOLD-REPAIR-001`; owner `geox_execution_validation_governance`.

## Scope, tests and gate

Owned on authorization: `tests/execution/test_taskctl.py` plus the three stable execution files (generated blocks via native commands; human evidence outside markers). Controller, handoff suite, context index, product, sibling, and authority surfaces are read-only. The task's own real gate evidence is recorded via the existing native `record-evidence` route (publication metadata, already authorized as `structured_completion_evidence_authorized` for this purpose); no evidence-feature work, no re-recording, no lifecycle change. Frozen branches remain unchanged/unapproved. All protected authority false; three unrelated defects unresolved. Unresolved execution-blocking design questions: none.

Tier 1 gate for execution, exact-head review and post-fast-forward: taskctl check; full focused, handoff, and combined suites (all green on the exact tree AND re-verified green against a closed main-shaped tree, proving status-agnostic scaffolds, no waiver); JSON parsing; git diff --check; authorized-baseline changed-path and authority checks. Docker/analytical/Ruff/mypy not_required for this narrow milestone.

## Publication and stop (for the authorized task)

Record real gate evidence via the native CLI on the clean implementation tree. Human evidence outside report markers: implementation SHA, gate counts both directions, Git identity/ancestry, limitations, cross-repo impact, authority. Native `transition --to ready_for_review --implementation-sha`. Freeze and validate the exact tree; receipt names implementation parent, gate/results, paths, clean state, evidence source, unchanged authority. Push the declared branch only, prove equality, stop without merge or successor authorization.

## Proposal record

Four focused failures on closed main are harness-live coupling, proven against immutable objects (identical scaffolds fail `E_EXECUTION_EVIDENCE`/`E_BLOCKED_EVIDENCE` with inherited closed authority and validate with authority held); the controller is correct and `taskctl check` passes main. No owner policy outstanding: harness repair under existing process-repair authority, no product/contract/capability change, no gate waiver. Entry carried byte-identical from the merged blob; frozen branches observed read-only unchanged.
