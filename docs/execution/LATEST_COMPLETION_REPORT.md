# GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001 — Authorized Task Handoff

- **Repository:** `Phani-Pavuluri/panel_exp`
- **Base main:** `b11646bab1f461964644a6526ef4967a8f04624d`
- **Feature branch:** `fix/geox-main-test-isolation-and-checkpoint-context-recovery-001`
- **Status:** `authorized`
- **Execution authorized:** `true`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Capability authority changed:** `false`

## Authorized outcome

Prove normal installed-package import and clean-subprocess deterministic replay
for the existing GeoX calibration-source manifest validator and builder. Correct
only test isolation and publish one validation checkpoint.

This handoff does not certify the producer and does not authorize package,
builder, manifest, fixture, analytical, MMM, MIP, `CalibrationSignal`, runtime,
planning, recommendation, pilot, or production changes.

## Live pins

- GeoX: `b11646bab1f461964644a6526ef4967a8f04624d`
- MIP: `a293ce52a813709ca624332123019139928cc51e`
- MMM: `fe8e784923994406a2e4907d28debd872d61fd73`

## Historical overlap disposition

- `fix/geox-baseline-import-health-001@08d8fe9adeb355b91afb4dc101184bdf199ce84c`
  has no unmerged commits.
- `feat/geox-calibration-source-manifest-validator-b-001@2b6745b9cbcf5a17196796231a39fec4336b5d1f`
  is divergent rejected history and must not be reused.
- Rejected manifest head `c18f56341b50c58505b59fc6cacf2337ca7f9fc4`
  remains historical evidence only.

## Validation

No implementation validation has run yet. The active task contains the complete
acceptance and full Docker gate. Execution must end at a pushed
`ready_for_review` or Git-durable `blocked` branch state.

## Authoring history note

Two transient commits accidentally created empty files below local-only
`docs/tasks/`; each was immediately reversed before branch materialization.
Neither file exists in the final tree, neither path is task evidence, and the
commits must not be represented as implementation work.

No PR, merge, sibling modification, or authority change was created by task
authoring.
