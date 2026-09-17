# GeoX execution context

Active task: `GEOX_CURRENT_MAIN_HANDOFF_STATUS_PARSER_RECOVERY_001`.

The task is authorized from synchronized GeoX main
`0f130f873b472c373cb481574fde25eb5ba62e56` on branch
`fix/geox-current-main-handoff-status-parser-recovery-001`. Canonical lifecycle
state is in `docs/execution/EXECUTION_STATE.json`; generated lifecycle views are
in `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md`.

Preserved cross-repository pins are MIP
`a293ce52a813709ca624332123019139928cc51e` and MMM
`fe8e784923994406a2e4907d28debd872d61fd73`. This GeoX task does not modify or
sequence either repository.

The merged fixture prerequisite closes
`GEOX-TASKCTL-CORRECTION-FIXTURE-BASELINE-001`. The remaining authorized work is
only the one-line handoff status parser recovery in
`tests/test_repo_native_execution_handoff.py`.

The historical branch
`fix/geox-current-main-handoff-status-parser-repair-001` at
`2d262fae8d8a904aa0f8332395588c37f6f74ccd` is immutable evidence. It may not
be merged, rebased, cherry-picked, modified, or used for execution.

No taskctl implementation, generated-document format, package/runtime code,
analytical behavior, certification, product authority, or unrelated defect
change is authorized. `GEOX_STRUCTURED_COMPLETION_EVIDENCE_001` is planned only;
it is not authorized and must be assessed separately after parser recovery.

Fresh-chat bootstrap: classify the full worktree, fetch and prune, switch to
`main`, pull fast-forward only, prove `main == origin/main`, read root
`AGENTS.md` and all four execution files, verify the authorization and exact
branch baseline, then execute only the contract in `ACTIVE_TASK.md`. Stop at
`ready_for_review`; do not create a PR or merge.
