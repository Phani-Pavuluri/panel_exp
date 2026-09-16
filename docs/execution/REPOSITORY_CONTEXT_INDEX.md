# GeoX execution context

Active task: `GEOX_TASKCTL_CORRECTION_FIXTURE_BASELINE_REPAIR_001`.

The task is authorized from synchronized GeoX main
`7c3799af5e406fe65161daf7d474cb363fa766b0` on branch
`fix/geox-taskctl-correction-fixture-baseline-repair-001`.
Canonical lifecycle state is in `docs/execution/EXECUTION_STATE.json`; generated
views are in `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md`.

Preserved cross-repository pins are MIP
`a293ce52a813709ca624332123019139928cc51e` and MMM
`fe8e784923994406a2e4907d28debd872d61fd73`. This GeoX task does not modify or
sequence either repository.

This is a test-fixture-only repair of
`GEOX-TASKCTL-CORRECTION-FIXTURE-BASELINE-001`, reproduced by
`tests/execution/test_taskctl.py::test_correction_closure_requires_explicit_evidence_and_updates_counters`.
The task may align only the synthetic `changes_requested` fixture with current
taskctl evidence invariants. The repository-authored Docker gate is not required
for this isolated milestone.

No taskctl implementation, parser test, package/runtime code, analytical
behavior, certification, product authority, MIP, or MMM changes are authorized.
The blocked parser branch at `2d262fae8d8a904aa0f8332395588c37f6f74ccd`
is immutable evidence and may not be merged or modified. No successor is
authorized.

Fresh-chat bootstrap: classify the full worktree, fetch and prune, switch to
`main`, pull fast-forward only, prove `main == origin/main`, read root
`AGENTS.md` and all four execution files, verify the authorization and exact
branch baseline, then execute only the contract in `ACTIVE_TASK.md`. Stop at
`ready_for_review`; do not create a PR or merge.
