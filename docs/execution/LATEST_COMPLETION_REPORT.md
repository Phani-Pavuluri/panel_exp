# GEOX_EXECUTION_HANDOFF_STATE_SCHEMA_REFRESH_001 — Authorization Report

- **Task:** `GEOX_EXECUTION_HANDOFF_STATE_SCHEMA_REFRESH_001`
- **Status:** authorized
- **Base main:** `843fa3d9196b68cf205a88addae83ec890b48366`
- **Implementation branch:** `fix/geox-execution-handoff-state-schema-refresh-001`
- **Authorization provenance:** `843fa3d9196b68cf205a88addae83ec890b48366`
- **Implementation:** not started
- **Correction budget:** `0 completed / 1 remaining`
- **Merge/PR authority:** false

## Reason for authorization

The current repository-native handoff test still asserts the obsolete literal
`geox_repo_execution_state_v2`, while synchronized main persists
`geox_repo_execution_state_v3`. The live state and all other execution
evidence use the v3 schema. This task repairs that stale governance assertion
only and preserves the test’s SHA, task-identity, pin-consistency, lifecycle,
required-surface, merge-authority, and capability-authority checks.

## Validation required during implementation

JSON parsing, the focused stale-schema and closure-invariant tests, the full
`tests/test_repo_native_execution_handoff.py` module, Ruff, compile validation,
`git diff --check`, exact changed-path verification, and local/remote feature
head equality. No full Docker run is required for this isolated test repair;
TBR, production/validation-boundary, D5 artifact, analytical, calibration,
lifecycle-adoption, MIP, MMM, and downstream capability work remains separate
and unauthorized.

No implementation branch, implementation commit, PR, merge, or sibling change
was created in this authoring pass.
