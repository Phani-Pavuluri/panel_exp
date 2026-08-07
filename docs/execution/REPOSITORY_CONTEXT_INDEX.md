# GeoX execution context

Active task: `GEOX_EXECUTION_HANDOFF_PIN_SCHEMA_REFRESH_001`.

The authorized implementation branch is
`fix/geox-execution-handoff-pin-schema-refresh-001-authorized`; its
task-authoring branch is `docs/geox-execution-handoff-pin-schema-refresh-001`.
The historical unmerged implementation
`c7835e586925fe4e7b04505ad18e6563289bbb8b` is evidence only and must not be
reused.

Current verified pins:

- GeoX: `Phani-Pavuluri/panel_exp@b11646bab1f461964644a6526ef4967a8f04624d`
- MIP: `Phani-Pavuluri/marketing_intelligence_platform@a293ce52a813709ca624332123019139928cc51e`
- MMM: `Phani-Pavuluri/MMM@fe8e784923994406a2e4907d28debd872d61fd73`

The active milestone only repairs the stale repository-execution pin-schema
test. It changes no analytical or runtime behavior and does not own the
validator, builder, manifests, source fixtures, D5 harnesses, producer
certification, MMM compatibility, MIP consumer mapping, or `CalibrationSignal`.

The MIP P2 capability ledger is the current cross-repository sequence source.
It records this task as the sole next-eligible GeoX milestone and keeps the
producer-certification successor unauthorized.

Historical branches are not executable evidence. In particular,
`feat/geox-calibration-source-manifest-validator-b-001@2b6745b9cbcf5a17196796231a39fec4336b5d1f`
is divergent rejected work and must not be copied or cherry-picked.

The parked isolation milestone remains at
`fix/geox-main-test-isolation-and-checkpoint-context-recovery-001@0c16766f47cae903c9a085043dfa51949e61ea68`
with implementation `a625a9dac6b97b05c4044dc5af5ae7875a63e889`; its blocker is
synchronized-main validation debt. The pin-schema repair removes one known
baseline validation debt and does not authorize isolation-branch merge or any
capability authority. After this pin-schema repair, the intended next
baseline-repair milestone is `GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_001`, which
remains unauthorized.

## Fresh Chat Bootstrap

Connected GitHub and synchronized Git are authoritative. Perform the mandatory
bootstrap from root `AGENTS.md`, then read `EXECUTION_STATE.json`,
`ACTIVE_TASK.md`, this index, `LATEST_COMPLETION_REPORT.md`, the existing
validator/builder/tests, and the current MIP ledger. Stop on any synchronization,
ownership, branch, prerequisite, or authority conflict.
