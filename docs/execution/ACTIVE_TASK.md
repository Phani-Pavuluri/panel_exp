<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `merged`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_TASKCTL_TEST_SCAFFOLD_REPAIR_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `0e5abc9ab4f5c87de9a308f0bb8422dd10a01023`
- **Authorization provenance:** `a05cf0c0092e55cd2ca659b8469eae2fc4b873b3`
- **Feature branch:** `feat/geox-taskctl-test-scaffold-repair-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `eab24592e6d7d590693c7b28788751de473514c5`
- **Reviewed head:** `5fca67a23ad92d8256e90ebe623e41063bfc442c`
- **Rejected review head:** `bc4ba647f3627eeb623faf165fb28adfada71269`
- **Rejected implementation commit:** `eab24592e6d7d590693c7b28788751de473514c5`
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

## Primary outcome and authority (authorized — implementation pending)

Repair the focused-test scaffolds that inherit task authority and evidence from live canonical state, so the live-coupled evidence tests validate green on every live-tree shape: scaffolds establish `task_execution_authorized`, `blockers`, and `completion_evidence` per requested status instead of inheriting them. Identical cases, identical expected codes — the assertions finally exercise the controller instead of the scaffold. Six focused tests are live-coupled on unauthorized and null-evidence trees (four reproduce on closed main; two more surface only where live evidence is null); all resolve to green with self-sufficient scaffolds. No controller, product, sibling, or authority change; no new codes; no weakened assertions. This definition-ready tests-only contract is authorized under the owner's existing bounded process-repair instruction; canonical state and the authorization record below carry execution authority. No merge, policy, product or sibling authority is granted. Muse-Spark owns implementation approach on authorization; Codex independently reviews.

Upon authorization, create `feat/geox-taskctl-test-scaffold-repair-001` from synchronized post-authoring main after mandatory bootstrap, taskctl check, authorization ancestry, metadata-only authoring boundary and branch-absence verification. Only one writer. Affected/modified: GeoX only. Workstream `WS-GEOX-TASKCTL-SCAFFOLD-REPAIR-001`; owner `geox_execution_validation_governance`.

## Scope, tests and gate

Owned on authorization: `tests/execution/test_taskctl.py` plus the three stable execution files (generated blocks via native commands; human evidence outside markers). Controller, handoff suite, context index, product, sibling, and authority surfaces are read-only. The task's own real gate evidence is recorded via the existing native `record-evidence` route (publication metadata, already authorized as `structured_completion_evidence_authorized` for this purpose); no evidence-feature work, no re-recording, no lifecycle change. Frozen branches remain unchanged/unapproved. All protected authority false; three unrelated defects unresolved. Unresolved execution-blocking design questions: none.

Tier 1 gate for execution, exact-head review and post-fast-forward: taskctl check; full focused, handoff, and combined suites (all green on the exact tree AND re-verified green against a closed main-shaped tree, proving status-agnostic scaffolds, no waiver); JSON parsing; git diff --check; authorized-baseline changed-path and authority checks. Docker/analytical/Ruff/mypy not_required for this narrow milestone.

## Publication and stop (for the authorized task)

Record real gate evidence via the native CLI on the clean implementation tree. Human evidence outside report markers: implementation SHA, gate counts both directions, Git identity/ancestry, limitations, cross-repo impact, authority. Native `transition --to ready_for_review --implementation-sha`. Freeze and validate the exact tree; receipt names implementation parent, gate/results, paths, clean state, evidence source, unchanged authority. Push the declared branch only, prove equality, stop without merge or successor authorization.

## Proposal record

Four focused failures on closed main are harness-live coupling, proven against immutable objects (identical scaffolds fail `E_EXECUTION_EVIDENCE`/`E_BLOCKED_EVIDENCE` with inherited closed authority and validate with authority held); the controller is correct and `taskctl check` passes main. No owner policy outstanding: harness repair under existing process-repair authority, no product/contract/capability change, no gate waiver. Entry carried byte-identical from the merged blob; frozen branches observed read-only unchanged.


## Task-specific execution authorization — October 15, 2026

Codex records execution authorization for GEOX_TASKCTL_TEST_SCAFFOLD_REPAIR_001 under the owner's existing explicit bounded process-repair direction: “approved, also fix the process so we dont need these kind of approvals”. The owner also requested continuing coordination and keeping agents working. This authoring action materializes that existing scope for the identified tests-only defect; it does not claim the owner supplied this task ID or a new approval SHA. Standing merge policy alone is not task authorization.

Owned implementation remains tests/execution/test_taskctl.py plus the stable three execution files. Observable behavior, assertions/codes, all declared final gates, closed-state evidence, correction budget and protected boundaries above are unchanged. Muse-Spark owns implementation; Codex independently reviews the exact published head. Execution stops at published ready_for_review or a genuine Git-durable blocked state. No policy/controller/product/analytical/sibling work, no test waiver and no new capability.
