# GeoX execution context

Active task: `GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_002`.

The authorized implementation branch is
`fix/geox-d5-power-control-geometry-repair-002`; the task-authoring branch is
`docs/geox-d5-power-control-geometry-repair-002`. This GeoX-local D5
validation-harness repair does not alter MIP sequencing or capability authority.
The merged pin-schema repair is closed historical evidence, not the active task.

The historical pin-schema implementation
`c7835e586925fe4e7b04505ad18e6563289bbb8b` remains evidence only and must not
be reused.

Current verified pins:

- GeoX: `Phani-Pavuluri/panel_exp@7bee4f7f24ff909b6b60cc067ca2da8cab1077c1`
- MIP: `Phani-Pavuluri/marketing_intelligence_platform@a293ce52a813709ca624332123019139928cc51e`
- MMM: `Phani-Pavuluri/MMM@fe8e784923994406a2e4907d28debd872d61fd73`

The active milestone repairs the shared D5 power-characterization harnesses so
they consume `assignment["test_0"]` and `assignment["control"]` from the
production `greedy_match_markets(...).assign` dictionary and enforce
the configured treated/control geometry. It does not change production
assignment, SCM, analytical/runtime behavior, artifacts, producer
certification, MMM compatibility, MIP consumer mapping, or `CalibrationSignal`.

The MIP P2 capability ledger remains the current cross-repository sequence
source and still points to the parked
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` milestone. This
active D5 repair is GeoX-local and does not alter MIP's product or capability
sequence. After D5 and the other baseline families are repaired, work returns
to the parked isolation milestone.

Historical branches are not executable evidence. In particular,
`feat/geox-calibration-source-manifest-validator-b-001@2b6745b9cbcf5a17196796231a39fec4336b5d1f`
is divergent rejected work and must not be copied or cherry-picked.

The parked isolation milestone remains at
`fix/geox-main-test-isolation-and-checkpoint-context-recovery-001@0c16766f47cae903c9a085043dfa51949e61ea68`
with implementation `a625a9dac6b97b05c4044dc5af5ae7875a63e889`; its blocker is
synchronized-main validation debt. The pin-schema repair is merged and closed;
the D5 harness repair is the active authorized baseline-repair milestone and
does not authorize isolation-branch merge or any capability authority. The
prior closure correction-cycle mismatch remains historical lifecycle debt for
a future single-source pilot.

## Fresh Chat Bootstrap

Connected GitHub and synchronized Git are authoritative. Perform the mandatory
bootstrap from root `AGENTS.md`, then read `EXECUTION_STATE.json`,
`ACTIVE_TASK.md`, this index, `LATEST_COMPLETION_REPORT.md`, the existing
validator/builder/tests, and the current MIP ledger. Stop on any synchronization,
ownership, branch, prerequisite, or authority conflict.
