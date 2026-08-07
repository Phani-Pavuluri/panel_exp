# GEOX_EXECUTION_HANDOFF_PIN_SCHEMA_REFRESH_001 — Authorized Task Handoff

- **Repository:** `Phani-Pavuluri/panel_exp`
- **Base main:** `b3f6b9acf81ff268c21d96d1014f8780fba5644f`
- **Task-authoring branch:** `docs/geox-execution-handoff-pin-schema-refresh-001`
- **Future implementation branch:** `fix/geox-execution-handoff-pin-schema-refresh-001-authorized`
- **Status:** `authorized`
- **Execution authorized:** `true` after task-branch creation
- **Merge authorized:** `false`
- **PR creation authorized:** `false`

## Authorization

This authorizes only a governance-test update from the synchronized main
ancestry. The obsolete pin names `canonical_mip_standard_commit` and
`canonical_mmm_workflow_commit` must be replaced by current
`mip_main_pin` and `mmm_main_pin`. Historical implementation commit
`c7835e586925fe4e7b04505ad18e6563289bbb8b` is evidence only and must not be
reused. No implementation or validation has been performed in this authoring
step.

## Dependency and authority

The isolation milestone remains parked and blocked by synchronized-main
validation debt at `0c16766f47cae903c9a085043dfa51949e61ea68`; its implementation
is `a625a9dac6b97b05c4044dc5af5ae7875a63e889`. This task resolves one known
baseline failure and does not authorize its merge. D5, TBR, production/
validation-boundary, BlockResidualBootstrap, and D5 artifact repairs remain
separate. Analytical, runtime, producer-certification, capability, MIP, and MMM
authority are unchanged.

## Required validation

JSON parse, focused handoff tests, complete handoff test file, Ruff, and
`git diff --check`; no full Docker suite is required. No PR or merge is
authorized.

Current repository pins: MIP `a293ce52a813709ca624332123019139928cc51e`;
MMM `fe8e784923994406a2e4907d28debd872d61fd73`.
