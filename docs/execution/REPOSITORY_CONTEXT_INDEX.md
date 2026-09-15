# GeoX execution context

Active task:
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_REASSESSMENT_001`.

The task is authorized from synchronized GeoX main
`d819fb17ccb2be90bb296d528ca7e0b05548f766` on branch
`audit/geox-main-test-isolation-and-checkpoint-context-reassessment-001`.
Canonical lifecycle state is in `docs/execution/EXECUTION_STATE.json`; generated
views are in `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md`.

This is a validation-only reassessment of the historical parked
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` branch at
`0c16766f47cae903c9a085043dfa51949e61ea68`. That branch is divergent,
immutable evidence only and may not be merged, rebased, cherry-picked, copied,
or revived. The task must use current-main tests and the full
repository-authored Docker gate to either retire the historical synchronized-
main validation debt or identify a concrete current-main defect.

No tests, package/runtime code, analytical behavior, certification, product
authority, MIP, or MMM changes are authorized. No successor is authorized.

Fresh-chat bootstrap: classify the full worktree, fetch and prune, switch to
`main`, pull fast-forward only, prove `main == origin/main`, read root
`AGENTS.md` and all four execution files, verify the authorization and exact
branch baseline, then execute only the contract in `ACTIVE_TASK.md`. Stop at
`ready_for_review`; do not create a PR or merge.
