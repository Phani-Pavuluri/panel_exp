# GeoX Main Test Isolation and Checkpoint Context Reassessment

## Decision

`concrete_current_main_defect_identified`

The historical synchronized-main validation debt cannot be retired. Two
concrete failures reproduce against an untouched archive of authorized base
`d819fb17ccb2be90bb296d528ca7e0b05548f766`. No defect was repaired and no
analytical, package, runtime, test, builder, validator, manifest, fixture,
certification, or downstream authority changed.

## Exact lineage and historical evidence

- Authorized current-main base:
  `d819fb17ccb2be90bb296d528ca7e0b05548f766`
- Tested audit-branch tree before evidence publication:
  `2111cfb2197ea62531919791a1e794a5f601ee6e`
- Parked branch:
  `fix/geox-main-test-isolation-and-checkpoint-context-recovery-001`
- Parked head: `0c16766f47cae903c9a085043dfa51949e61ea68`
- Parked implementation:
  `a625a9dac6b97b05c4044dc5af5ae7875a63e889`
- Merge base: `b3f6b9acf81ff268c21d96d1014f8780fba5644f`
- Divergence at authorization: current main ahead 79; parked branch ahead 13.

The parked branch was inspected only as immutable evidence. It was not merged,
rebased, cherry-picked, copied, or revived.

## Full Docker gate

Command: `make validate-docker`

- Container:
  `a2e9572bdceff1a9a9c491e84b3a189855948f239953cbed9acc717ea7268400`
- Container start: `2026-09-14T17:38:06-07:00`
- Runtime: `20486` seconds (`5:41:26`)
- Docker-recorded exit code: `1`
- Captured progress: 3168 test outcomes through 50 percent
- Captured failure markers: 3
- Preserved partial log:
  `/private/tmp/geox-reassessment-validate-docker.log`

The run was detached from a visible Codex terminal and used `docker run --rm`.
The container was destroyed after exit, so the final pytest count and traceback
summary were not preserved. This prevents an exhaustive full-suite count, but
does not erase the failed exit or the three captured failure markers. The
markers were mapped to pytest collection order and rerun individually below.

## Focused validation

Command:

```text
.venv/bin/python -m pytest -q tests/contracts/test_geox_calibration_source_manifest.py tests/fixtures/test_geox_calibration_source_manifest_generator.py
```

Result: `68 passed in 8.17s`.

Command:

```text
.venv/bin/python -m pytest -q tests/execution/test_taskctl.py tests/test_repo_native_execution_handoff.py
```

Result: `14 passed, 2 failed in 0.99s`.

The three Docker failure-marker indices mapped to:

1. index 129:
   `tests/execution/test_taskctl.py::test_correction_closure_requires_explicit_evidence_and_updates_counters`
2. index 2255:
   `tests/test_inference_registry_equivalence.py::test_numeric_outputs_match_golden_fixture[BlockResidualBootstrap]`
3. index 2494:
   `tests/test_repo_native_execution_handoff.py::test_v2_state_contract_and_pins`

The BlockResidualBootstrap failure was reproduced directly on the audit tree:
`BlockResidualBootstrap.y_lower` mismatched 8 of 30 elements, maximum absolute
difference `10.09483532`, maximum relative difference `0.00899396`.

## Untouched authorized-base replay

An archive produced directly by
`git archive d819fb17ccb2be90bb296d528ca7e0b05548f766` was extracted outside the
repository and the three identified tests were run there. Result:
`1 passed, 2 failed in 8.53s`.

Classification:

- `test_correction_closure_requires_explicit_evidence_and_updates_counters`
  passed on the untouched base. Its audit-tree failure is caused by the test
  helper assuming the active canonical state already has a non-null
  implementation SHA when it synthesizes `changes_requested`. This is an
  authorization-state lifecycle-test assumption, not a reproduced base defect.
- `test_v2_state_contract_and_pins` failed on the untouched base because its
  status regular expression does not accept the backtick-delimited generated
  status that `taskctl` emits. Defect ID:
  `GEOX-CURRENT-MAIN-HANDOFF-STATUS-PARSER-001`.
- The BlockResidualBootstrap golden-equivalence test failed identically on the
  untouched base. Defect ID:
  `GEOX-CURRENT-MAIN-BRB-GOLDEN-EQUIVALENCE-001`.

## Scope, limitations, and authority

The reassessment establishes concrete current-main validation debt and
therefore does not retire the parked dependency. Because the detached Docker
run lost its post-50-percent output, this report does not claim an exhaustive
failure count or that no additional failures exist. Repeating the six-hour gate
is not required to prove the binary conclusion after two exact-base defects
were reproduced.

No code or test fix is authorized or included. No successor task is authorized.
No PR, merge, squash, rebase, force-push, or merge commit was created.
