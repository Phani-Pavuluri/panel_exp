# GeoX execution context (stable source index)

Canonical lifecycle state: `docs/execution/EXECUTION_STATE.json`. It is the
sole authority for task identity (`task_id`, `feature_branch`), lifecycle
status and review decision, base and authorization SHAs, correction counters,
authority flags, preserved pins, and (on schema v5) `rejection_history`. No
per-task identity value is duplicated here; resolve task identity, status, and
SHAs from canonical state.

Generated lifecycle views: `docs/execution/ACTIVE_TASK.md` and
`docs/execution/LATEST_COMPLETION_REPORT.md`, controller-rendered between
`<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->` and
`<!-- END GEOX TASKCTL EXECUTION VIEW -->` markers. Human-authored sections
outside the markers are evidence and prose, preserved byte-for-byte by view
replacement. Validation entry point:
`python -m panel_exp.execution.taskctl check` (generated views must match
canonical state).

Preserved cross-repository pins (historical coordination baseline, stable):
GeoX `a78c4017e06c6f0bfb4329e749972b516dfbc7e9`, MIP
`a293ce52a813709ca624332123019139928cc51e`, MMM
`fe8e784923994406a2e4907d28debd872d61fd73`. This GeoX task does not modify or
sequence sibling repositories. Live main observations are recorded per task in
the active contract and completion evidence, never refreshed here.

Bootstrap and merge protocol: root `AGENTS.md` — classify the full worktree,
fetch and prune, switch to `main`, pull fast-forward only, prove
`main == origin/main`; merge only after exact-head approval with
`git merge --ff-only`, one closure commit, push, synchronization, and cleanup.
No `approved_for_merge` state exists; execution never creates a PR.
