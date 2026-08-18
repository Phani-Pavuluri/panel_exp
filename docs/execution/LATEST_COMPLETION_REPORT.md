# GEOX_EXECUTION_LIFECYCLE_SINGLE_SOURCE_ADOPTION_001 — Authorized Task Handoff

- **Status:** authorized
- **Task:** `GEOX_EXECUTION_LIFECYCLE_SINGLE_SOURCE_ADOPTION_001`
- **Base main:** `5ab881296c7c8248076bad61292b255aaade11d8`
- **Implementation branch:** `feat/geox-execution-lifecycle-single-source-adoption-001`
- **Authorization provenance:** `5ab881296c7c8248076bad61292b255aaade11d8`
- **Implementation:** not started
- **Merge/PR authority:** false

This authorizes a GeoX-local migration from `geox_repo_execution_state_v2` to
`geox_repo_execution_state_v3`, making `EXECUTION_STATE.json` the sole mutable
lifecycle authority and deterministic generated blocks in the two stable
Markdown execution documents. The canonical correction fields are maximum,
completed, and remaining, with the current D5 lineage represented as `1 / 0 /
1`.

The exact GeoX markers are `BEGIN GEOX TASKCTL EXECUTION VIEW` and
`END GEOX TASKCTL EXECUTION VIEW`; sync may replace only bytes inside one valid
marker pair and must be byte-idempotent. Lifecycle vocabulary, transition
validation, stable reason codes, atomic writes, protected authority fields, and
the MIP-derived rendering order are definition-ready in ACTIVE_TASK.md.

Canonical MIP reference:
`Phani-Pavuluri/marketing_intelligence_platform@b0f57701a55d5cbe1d94692bf378a23d03945646`.
MMM is read-only coordination evidence. No analytical, certification, product,
runtime, sibling, or capability authority changes are authorized.

Future validation requires focused governance tests, Ruff, supported mypy,
JSON/schema migration checks, taskctl check and idempotent sync, diff/scope
checks, and the full repository Docker gate with synchronized-main replay if
baseline debt remains. No implementation or implementation branch was created.
