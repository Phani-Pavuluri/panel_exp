# Active Task

**Status:** ready_for_review
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_LEAN_REPOSITORY_DELIVERY_STANDARD_ADOPTION_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Task base on main:** `a4bf6bfaa4311dacd3642d289dca3917543e0309`
- **Authorization head:** `686c3505151ee7073d52a9e70a8ea1b3f942ced4`
- **Feature branch:** `docs/geox-lean-repository-delivery-standard-adoption-001`
- **Accepted substantive correction candidate:** `9e5a8473157c0562dce4a870563d7e9d21ca7445`
- **Latest rejected review head:** `d3543179ce93e5f1563d96554e8a490702735a15`
- **Prior rejected review head:** `811ff9802cc41a46a7b4186e0eb026358becd337`
- **Risk tier:** Tier 1 governance
- **Canonical MIP standard:** `369805d923454a51ce98845cea29bdb1ee3c3895`
- **Canonical MMM workflow pin:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`

## Review decision

The substantive governance correction at `9e5a8473157c0562dce4a870563d7e9d21ca7445`
is retained. Exact remote head `d3543179ce93e5f1563d96554e8a490702735a15`
is rejected only as a final publication head because its lifecycle metadata and
receipt field are inconsistent. No implementation redesign or additional scope
is authorized.

## Required correction

Correct only these two issues:

1. Successful `ready_for_review` publication must set
   `correction_execution_authorized` to `false`, set `review_decision` to
   `ready_for_review`, and set `review_decision_source` to the single current
   completion report. Keep blockers empty, implementation SHA equal to
   `9e5a8473157c0562dce4a870563d7e9d21ca7445`, reviewed and approval SHAs null,
   merge and PR authority false, and capability authority unchanged.
2. Replace the ambiguous receipt value
   `Implementation-Parent: a4bf6bfaa4311dacd3642d289dca3917543e0309`.
   The corrected receipt must distinguish the task base from the substantive
   implementation by recording:
   - `Task-Base-Main: a4bf6bfaa4311dacd3642d289dca3917543e0309`; and
   - `Implementation-SHA: 9e5a8473157c0562dce4a870563d7e9d21ca7445`.
   Do not use `Implementation-Parent` in the replacement receipt.

Replace `LATEST_COMPLETION_REPORT.md` with one current `ready_for_review`
narrative carrying the same identities and exact validation evidence.

## Owned paths

This correction may modify only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify the adopted standards, tests, navigation index, analytical code,
contracts, fixtures, superseded builder branch, MIP, MMM, or coordination files.

## Validation gate

Run the Tier-1 gate on the final task-owned tree:

- JSON parse for `docs/execution/EXECUTION_STATE.json`;
- Markdown/current-state consistency;
- exact changed-path verification;
- `git diff --check`;
- `pytest -q tests/test_repo_native_execution_handoff.py` with exact counts;
- receipt-trailer inspection; and
- exact local/remote feature-head equality after push.

Docker, Ruff, mypy, and the full suite are `not_required`.

## Publication

Publish one new `ready_for_review` head with a durable receipt containing
`Task-Base-Main`, `Implementation-SHA`, validation gate/result, exact focused-test
count, changed paths, diff check, worktree state, evidence source, full-suite
disposition, and unchanged authority. Push the exact feature branch and stop
without PR or merge.

**Unresolved execution-blocking design questions: none.**
