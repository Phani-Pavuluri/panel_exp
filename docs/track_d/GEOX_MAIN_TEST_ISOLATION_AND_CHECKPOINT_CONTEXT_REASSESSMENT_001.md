# GeoX Main Test Isolation and Checkpoint Context Reassessment

## Decision

`concrete_current_main_defect_identified`

The historical synchronized-main validation debt cannot be retired. All 15
failures from the completed Docker gate reproduce against an untouched archive
of authorized base `d819fb17ccb2be90bb296d528ca7e0b05548f766`. No defect was
repaired and no analytical, package, runtime, test, builder, validator,
manifest, fixture, certification, or downstream authority changed.

## Exact lineage and historical evidence

- Authorized current-main base:
  `d819fb17ccb2be90bb296d528ca7e0b05548f766`
- Rejected review head and tested committed head:
  `e146620e2d1b4b3c5d87e14a5b6e9c01d18a303a`
- Original implementation commit:
  `746f7082a5cd727461a076867f1dd17bc25d23b6`
- Parked branch:
  `fix/geox-main-test-isolation-and-checkpoint-context-recovery-001`
- Parked head: `0c16766f47cae903c9a085043dfa51949e61ea68`
- Parked implementation:
  `a625a9dac6b97b05c4044dc5af5ae7875a63e889`
- Merge base: `b3f6b9acf81ff268c21d96d1014f8780fba5644f`
- Divergence at authorization: current main ahead 79; parked branch ahead 13.

The parked branch was inspected only as immutable evidence. It was not merged,
rebased, cherry-picked, copied, or revived.

## Focused and adjacent validation

Focused validator/generator command:

```text
.venv/bin/python -m pytest -q tests/contracts/test_geox_calibration_source_manifest.py tests/fixtures/test_geox_calibration_source_manifest_generator.py
```

Result: `68 passed in 8.17s`.

The literal review-specified adjacent command named
`tests/contracts/test_geox_governed_experiment_readout.py`, which does not exist
on the authorized repository tree. That command failed at path resolution and
is not represented as a product-test failure.

The repository-resolved adjacent command was:

```text
.venv/bin/python -m pytest -q tests/contracts/test_geox_governed_experiment_readout_contract.py tests/fixtures/test_geox_certified_governed_readout_fixtures.py
```

Result: `3 passed in 0.03s`.

## Complete Docker gate

Command: `make validate-docker`

- Exit code: `1`
- Result: `15 failed, 6174 passed, 28 skipped`
- Warnings: `2162592`
- Runtime: `3618.89s` (`1:00:18`)
- Complete durable host log:
  `/private/tmp/geox-reassessment-validate-docker.XXXXXX.log`

The filename contains literal `XXXXXX`; it is the actual preserved filename,
not an unresolved template. The final pytest summary and all 15 failing node
IDs are present in the durable log.

The 15 failures were:

1. `tests/test_inference_registry_equivalence.py::test_numeric_outputs_match_golden_fixture[BlockResidualBootstrap]`
2. `tests/test_repo_native_execution_handoff.py::test_v2_state_contract_and_pins`
3. `tests/validation/test_design_guardrail_enforcement_001.py::TestGeoRunnerIntegration::test_geo_runner_emits_guardrail_enforcement`
4. `tests/validation/test_design_tier1_contract_emission_001.py::test_tier1_output_contains_design_contract`
5. `tests/validation/test_design_tier1_contract_emission_001.py::test_emitted_contract_validates_with_standalone_validator`
6. `tests/validation/test_design_tier1_contract_emission_001.py::test_contract_validation_summary_exists`
7. `tests/validation/test_design_tier1_contract_emission_001.py::test_emitted_status_is_validator_derived`
8. `tests/validation/test_design_tier1_contract_emission_001.py::test_no_contract_complete_allowed`
9. `tests/validation/test_design_tier1_contract_emission_001.py::test_no_downstream_authorization_allowed`
10. `tests/validation/test_design_tier1_contract_emission_001.py::test_forbidden_downstream_claims_nonempty`
11. `tests/validation/test_design_tier1_contract_emission_001.py::test_stratified_emits_structure_metadata`
12. `tests/validation/test_design_tier1_contract_emission_001.py::test_rerandomization_wrapper_identity_emitted`
13. `tests/validation/test_design_tier1_contract_emission_001.py::test_multicell_emits_cell_and_shared_control_metadata`
14. `tests/validation/test_design_tier1_contract_emission_001.py::test_never_emits_contract_complete_status`
15. `tests/validation/test_inference_boundary_guardrail_enforcement_001.py::TestIntegration::test_geo_runner_design_then_boundary`

## Untouched authorized-base replay

The failing node IDs were extracted from the durable Docker summary. An archive
produced directly by
`git archive d819fb17ccb2be90bb296d528ca7e0b05548f766` was extracted outside the
repository, and all 15 tests were executed there in one focused replay.

Result: `15 failed, 2 warnings in 10.70s`.

Every Docker failure therefore reproduces on the untouched authorized base.
None is a correction-branch regression. They group into four concrete defects:

- `GEOX-CURRENT-MAIN-BRB-GOLDEN-EQUIVALENCE-001`: one
  BlockResidualBootstrap golden-equivalence failure;
- `GEOX-CURRENT-MAIN-HANDOFF-STATUS-PARSER-001`: one lifecycle generated-status
  parser failure;
- `GEOX-CURRENT-MAIN-DESIGN-VALIDATION-CALLBACK-INJECTION-001`: two integration
  failures caused by the absent validation-owned callback;
- `GEOX-CURRENT-MAIN-DESIGN-TIER1-CONTRACT-EMISSION-001`: eleven failures from
  missing or unknown tier-1 design-contract emission and validation evidence.

The BlockResidualBootstrap failure mismatched 8 of 30 `y_lower` elements, with
maximum absolute difference `10.09483532` and maximum relative difference
`0.00899396`.

## Scope and authority

The complete gate and exact-base replay establish concrete current-main debt,
so the parked dependency is not retired. This reassessment does not authorize
or include fixes for any identified defect.

No code or test file changed. No successor task is authorized. No protected
capability, certification, CalibrationSignal, MMM, simulation, planning,
recommendation, real-data, runtime, pilot, or production authority changed. No
PR, merge, squash, rebase, force-push, or merge commit was created.
