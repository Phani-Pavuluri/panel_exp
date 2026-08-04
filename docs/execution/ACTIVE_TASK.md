# Active Task

**Status:** changes_requested
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_LEAN_REPOSITORY_DELIVERY_STANDARD_ADOPTION_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Task base on main:** `a4bf6bfaa4311dacd3642d289dca3917543e0309`
- **Authorization head:** `686c3505151ee7073d52a9e70a8ea1b3f942ced4`
- **Feature branch:** `docs/geox-lean-repository-delivery-standard-adoption-001`
- **Retained substantive implementation:** `9e5a8473157c0562dce4a870563d7e9d21ca7445`
- **Rejected review head:** `6cf6c2584af78c6c288cd572cf4d9e31416b2cc6`
- **Prior rejected review heads:** `d3543179ce93e5f1563d96554e8a490702735a15`, `811ff9802cc41a46a7b4186e0eb026358becd337`
- **Risk tier:** Tier 1 governance
- **Canonical MIP standard:** `369805d923454a51ce98845cea29bdb1ee3c3895`
- **Live MIP main observed:** `976d3a1daeae9c52c8772e5112574f698951a57c`
- **Canonical MMM workflow pin:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Live MMM main observed:** `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`

## Review decision

Exact remote head `6cf6c2584af78c6c288cd572cf4d9e31416b2cc6` is not approved. The two previously requested metadata corrections were completed, but exact-head review found four remaining task-compliance defects. The substantive implementation at `9e5a8473157c0562dce4a870563d7e9d21ca7445` remains the implementation candidate; no analytical, builder, fixture, MIP, or MMM scope is authorized.

## Required final correction

1. **Make the receipt contract internally consistent.**
   `LEAN_REPOSITORY_DELIVERY_STANDARD.md` and `TASK_EXECUTION_STANDARD.md` still require an `implementation parent`, while the corrected publication deliberately replaced that ambiguous field with `Task-Base-Main` and `Implementation-SHA`. Update both standards to require the exact durable fields `Task-Base-Main`, `Implementation-SHA`, validation gate/result, exact test counts, full authorized task-diff paths, final-correction paths when applicable, diff check, worktree state, evidence source, full-suite disposition, and authority impact. Do not require or publish `Implementation-Parent`.

2. **Enforce behavior rather than phrase presence.**
   Strengthen `tests/test_repo_native_execution_handoff.py` so it independently verifies:
   - branch/task binding from synchronized `main`, explicit feature-branch switch, branch-local task/branch/ancestry verification, pre-push destination verification, stale/wrong-branch failure, and local/remote equality language in `AGENTS.md`;
   - `ready_for_review` requires `correction_execution_authorized == false`, `review_decision == ready_for_review`, `review_decision_source == docs/execution/LATEST_COMPLETION_REPORT.md`, empty blockers, and null reviewed/approval SHAs;
   - the standards require the exact receipt fields above and do not require `Implementation-Parent`;
   - the navigation index contains no current task identity, branch, status, or 40-character sibling pins.

3. **Publish a complete final report.**
   Replace `LATEST_COMPLETION_REPORT.md` with one current report containing the implementation SHA; exact validation commands and counts; GitHub-observed versus locally reported evidence; blockers; limitations; validation debt; complete authorized task-diff paths; final-correction paths; sibling impact; consumer verification; newly eligible work; and authority impact. State explicitly that no PR or merge exists, the superseded builder branch is untouched, and no successor or capability is authorized.

4. **Remove stale current-state prose.**
   On successful publication, update `EXECUTION_STATE.json` so its task note describes the new review candidate rather than instructing execution of an already completed prior correction. Keep the retained implementation SHA exact and preserve all rejected-head history.

## Owned paths

This final correction may modify only:

- `docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `tests/test_repo_native_execution_handoff.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify `AGENTS.md`, the navigation index, analytical code, contracts, fixtures, the superseded builder branch, MIP, MMM, or coordination files.

## Validation gate

Run on the frozen final tree:

- JSON parse for `docs/execution/EXECUTION_STATE.json`;
- Markdown/current-state consistency;
- exact full-task and final-correction changed-path verification;
- `git diff --check`;
- `pytest -q tests/test_repo_native_execution_handoff.py` with exact passed/failed/skipped counts;
- receipt-trailer inspection; and
- exact local/remote feature-head equality after push.

Docker, Ruff, mypy, and the full suite are `not_required` for this Tier-1 governance task.

## Publication and stop rule

On success publish one `ready_for_review` head with correction authority false, one current complete report, and a durable exact-tree receipt. Push the exact branch and stop without PR or merge.

This is the final bounded correction cycle. If the same task still cannot satisfy these exact requirements, publish accurate evidence and supersede it without merge rather than adding another correction cycle.

**Unresolved execution-blocking design questions: none.**
