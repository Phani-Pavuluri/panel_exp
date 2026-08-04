# TASK_AUTHORIZATION_REPORT

## Current decision

- **Task ID:** `GEOX_EXECUTION_BRANCH_BINDING_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Status:** `authorized`
- **Pre-authoring base:** `f15b0ee1713eaa46b7dc55e597e713443f5a8d32`
- **Feature branch:** `feat/geox-execution-branch-binding-001`
- **Risk tier:** Tier 2 internal executable repository governance
- **Implementation SHA:** not yet created
- **Capability authority:** unchanged

## Eligibility and overlap evidence

GeoX `main` first superseded
`GEOX_LEAN_REPOSITORY_DELIVERY_STANDARD_ADOPTION_001` without merge. Its
preserved branch remains at `bb1ac8d5ce29e2cab33eb680b3b7db76110f35f1`
and has no remaining task, correction, merge, or PR authority.

Live sibling evidence observed:

- MIP `976d3a1daeae9c52c8772e5112574f698951a57c`, with a MIP-only
  cross-repository roadmap/coordination reconciliation task authorized;
- MMM `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`, with an MMM-only execution
  protocol task authorized.

Neither sibling task owns GeoX files. Their cached GeoX observations become
stale when GeoX main moves and must be evaluated through each task's declared
live-overlay behavior. No duplicate GeoX owner or overlapping implementation
blocks this task.

## Primary outcome

Implement one deterministic read-only command that enforces exact main-derived
task and feature-branch binding across `preflight`, `prepush`, and `postpush`
phases. The task includes real temporary-Git behavioral tests and minimal
repository guidance invoking the command.

Publication lifecycle, completion-report schema, exact-tree receipt redesign,
lean task authoring, navigation changes, builder work, and analytical behavior
are outside scope.

## Frozen acceptance matrix

The exact command inputs, success JSON keys, failure format, reason-code set,
phase invariants, phase semantics, documentation calls, and eight required
behavioral tests are fixed in `docs/execution/ACTIVE_TASK.md` before execution.
Review may reject only against that matrix, unauthorized scope, false evidence,
or an unsafe defect under the fixed behavior. New preferences become successor
work and do not expand this task.

The task permits at most one correction cycle. A second failed review requires
supersession without merge.

## Owned paths

Only these paths may change:

- `AGENTS.md`
- `scripts/verify_authorized_task_binding.py`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `tests/test_execution_branch_binding.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

## Validation requirement

Run JSON parsing, Python compilation, the isolated branch-binding tests with exact
counts, `git diff --check`, exact changed-path verification, and the command's
prepush/postpush phases on the final branch. Docker, the complete package suite,
analytical tests, Ruff, and mypy are explicitly `not_required` because this task
uses only standard-library Git tooling and isolated temporary repositories and
does not import or change the GeoX package or analytical runtime.

## Task-authoring boundary

The authoring range starts at
`f15b0ee1713eaa46b7dc55e597e713443f5a8d32` and changes only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The commit containing this report is the task-authoring head. The immediate next
commit must change only `docs/execution/EXECUTION_STATE.json` to record that
exact head and executable authorization. Create the feature branch from the
resulting synchronized state-only GeoX main.

## Cross-repository and authority impact

- **Affected repository:** GeoX only.
- **MIP/GeoX/MMM blocker transitions:** none.
- **Consumer verification:** not applicable.
- **Newly eligible work:** implementation of this branch-binding task only.
- **Deferred work:** publication lifecycle/receipt task remains proposed and
  unauthorized.
- **Merge and PR authority:** false.
- **Analytical and capability authority:** unchanged and false.

No implementation occurred during task authoring.
