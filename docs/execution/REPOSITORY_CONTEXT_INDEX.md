# GeoX execution context

Active task: `GEOX_EXECUTION_HANDOFF_STATE_SCHEMA_REFRESH_001`.

The authorized implementation branch is
`fix/geox-execution-handoff-state-schema-refresh-001`; it has not yet been
created. This GeoX-local governance-test repair updates one stale v2 schema
assertion to the live v3 execution-state schema and does not alter MIP
sequencing or capability authority. The merged import-isolation and pin-schema
repairs are closed historical evidence, not the active task.

The historical pin-schema implementation
`c7835e586925fe4e7b04505ad18e6563289bbb8b` remains evidence only and must not
be reused.

Current verified pins:

- GeoX: `Phani-Pavuluri/panel_exp@687e4063ca9d43bcc0ea4527cac3fc9dab3fa8fd`
- MIP: `Phani-Pavuluri/marketing_intelligence_platform@a293ce52a813709ca624332123019139928cc51e`
- MMM: `Phani-Pavuluri/MMM@fe8e784923994406a2e4907d28debd872d61fd73`

The active milestone repairs one stale repository-native execution-handoff test
so it validates the live `geox_repo_execution_state_v3` schema. It does not
change production assignment, SCM, analytical/runtime behavior, artifacts,
producer certification, MMM compatibility, MIP consumer mapping, or
`CalibrationSignal`.

The MIP P2 capability ledger remains the current cross-repository sequence
source and still points to the parked
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` milestone. This
active schema-test repair is GeoX-local and does not alter MIP's product or
capability sequence. Remaining baseline families remain separately owned.

Historical branches are not executable evidence. In particular,
`feat/geox-calibration-source-manifest-validator-b-001@2b6745b9cbcf5a17196796231a39fec4336b5d1f`
is divergent rejected work and must not be copied or cherry-picked.

The parked isolation milestone remains at
`fix/geox-main-test-isolation-and-checkpoint-context-recovery-001@0c16766f47cae903c9a085043dfa51949e61ea68`
with implementation `a625a9dac6b97b05c4044dc5af5ae7875a63e889`; its blocker is
 synchronized-main validation debt. The pin-schema and import-isolation repairs
are merged and closed; the current schema-test task does not authorize
isolation-branch merge or any capability authority. The
prior closure correction-cycle mismatch remains historical lifecycle debt for
a future single-source pilot.

## Fresh Chat Bootstrap

Connected GitHub and synchronized Git are authoritative. Perform the mandatory
bootstrap from root `AGENTS.md`, then read `EXECUTION_STATE.json`,
`ACTIVE_TASK.md`, this index, `LATEST_COMPLETION_REPORT.md`, the existing
validator/builder/tests, and the current MIP ledger. Stop on any synchronization,
ownership, branch, prerequisite, or authority conflict.
