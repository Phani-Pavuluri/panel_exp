# GeoX execution context

Active task: `GEOX_CURRENT_MAIN_HANDOFF_STATUS_PARSER_REPAIR_001`.

The task is authorized from synchronized GeoX main
`14ca3c0beda54737b4a3c5a0b76f5f9f5fd488f9` on branch
`fix/geox-current-main-handoff-status-parser-repair-001`.
Canonical lifecycle state is in `docs/execution/EXECUTION_STATE.json`; generated
views are in `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md`.

This is a test-only repair of
`GEOX-CURRENT-MAIN-HANDOFF-STATUS-PARSER-001`, reproduced by
`tests/test_repo_native_execution_handoff.py::test_v2_state_contract_and_pins`.
The task may repair only the test parser for the canonical backtick-delimited
taskctl status. The repository-authored Docker gate is not required for this
isolated milestone.

No taskctl rendering, package/runtime code, analytical behavior, certification,
product authority, MIP, or MMM changes are authorized. The BRB, callback
injection, and tier-1 contract-emission defects remain outside scope. No
successor is authorized.

Fresh-chat bootstrap: classify the full worktree, fetch and prune, switch to
`main`, pull fast-forward only, prove `main == origin/main`, read root
`AGENTS.md` and all four execution files, verify the authorization and exact
branch baseline, then execute only the contract in `ACTIVE_TASK.md`. Stop at
`ready_for_review`; do not create a PR or merge.
