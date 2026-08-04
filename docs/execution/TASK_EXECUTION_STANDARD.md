# GeoX Task Execution Standard

This repository adopts the lean delivery standard. Task selection comes from
`EXECUTION_STATE.json` and `ACTIVE_TASK.md`; the context index is navigation
only. Executions must finish with one durable `ready_for_review` or genuine
`blocked` outcome and must not create PRs or merges.

Prompts are invocation-only and execution continues after orientation. Before
publication, record implementation parent, exact gate and counts, changed
paths, diff check, worktree, evidence source, full-suite disposition, and
authority impact in a durable exact-tree receipt.
