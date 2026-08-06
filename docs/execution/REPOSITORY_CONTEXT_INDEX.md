# GeoX execution context

Active task: `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001`.

Current verified pins:

- GeoX: `Phani-Pavuluri/panel_exp@b11646bab1f461964644a6526ef4967a8f04624d`
- MIP: `Phani-Pavuluri/marketing_intelligence_platform@a293ce52a813709ca624332123019139928cc51e`
- MMM: `Phani-Pavuluri/MMM@fe8e784923994406a2e4907d28debd872d61fd73`

The active milestone is a test-isolation checkpoint for the existing
calibration-source manifest validator and builder. It may modify only the two
declared test files, one Track D checkpoint document, and lifecycle execution
files. It does not own package/runtime code, the builder, manifests, source
fixtures, producer certification, MMM compatibility, MIP consumer mapping, or
`CalibrationSignal`.

The MIP P2 capability ledger is the current cross-repository sequence source.
It records this task as the sole next-eligible GeoX milestone and keeps the
producer-certification successor unauthorized.

Historical branches are not executable evidence. In particular,
`feat/geox-calibration-source-manifest-validator-b-001@2b6745b9cbcf5a17196796231a39fec4336b5d1f`
is divergent rejected work and must not be copied or cherry-picked.

## Fresh Chat Bootstrap

Connected GitHub and synchronized Git are authoritative. Perform the mandatory
bootstrap from root `AGENTS.md`, then read `EXECUTION_STATE.json`,
`ACTIVE_TASK.md`, this index, `LATEST_COMPLETION_REPORT.md`, the existing
validator/builder/tests, and the current MIP ledger. Stop on any synchronization,
ownership, branch, prerequisite, or authority conflict.
