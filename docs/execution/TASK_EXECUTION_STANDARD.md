# GeoX Task Execution Standard

This repository adopts the lean delivery standard. Task selection comes from
`EXECUTION_STATE.json` and `ACTIVE_TASK.md`; the context index is navigation
only. Executions must finish with one durable `ready_for_review` or genuine
`blocked` outcome and must not create PRs or merges.
