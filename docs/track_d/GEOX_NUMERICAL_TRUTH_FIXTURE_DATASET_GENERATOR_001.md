# GEOX_NUMERICAL_TRUTH_FIXTURE_DATASET_GENERATOR_001

## Metadata / Purpose
Deterministic local-only generator for the 12 planned numerical-truth fixture artifacts.

## Generated artifact layout / API
`tests/fixtures/geox_numerical_truth/manifest.json/<case_id>/` contains `input_panel.csv`, `truth.json`, `expected_readout.json` or `expected_packet.json`, and `replay.json`. API: `build_geox_numerical_truth_fixture_artifacts`, `build_all_geox_numerical_truth_fixture_artifacts`, and `validate_generated_geox_truth_fixture_artifacts`.

## Cases / Behavior
All twelve planned case IDs are generated with stable seeds, panel shape, treatment/control labels, truth metadata, blocked/warning states, replay metadata, and manifest indexing. Generation is local, deterministic, idempotent, network-free, and validation-backed.

## Readout / MIP / D6 alignment
Successful and warning cases produce candidate shapes; blocked cases packets; diagnostic/research cases remain constrained. Calibration-incompatible and multicell cases remain non-production. MIP consumes but does not certify GeoX truth. D6 Gate 1 still requires versions, compatibility, ownership, failure/release/rollback, limitations, owners, flags, and migration rules.

## Validation / Limitations
Validation checks manifest, all 12 directories, required files, stable replay metadata, and non-production flags. The generator does not execute estimators or create certified production readouts.

## Authorization boundary / Final verdict
No MIP/MMM changes, exports, selector/router, assignment, readout authorization, reporting, decisioning, or production claims are enabled. **PROCEED_TO_GEOX_NUMERICAL_TRUTH_FIXTURE_VALIDATION_CHECKPOINT**.

## Recommended next artifact
`GEOX_NUMERICAL_TRUTH_FIXTURE_VALIDATION_CHECKPOINT_001`.
