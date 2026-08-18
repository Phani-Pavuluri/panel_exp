# Active Task

**Status:** ready_for_review
**Task ID:** `GEOX_EXECUTION_HANDOFF_STATE_SCHEMA_REFRESH_001`
**Repository:** `Phani-Pavuluri/panel_exp`
**Base SHA:** `843fa3d9196b68cf205a88addae83ec890b48366`
**Implementation branch:** `fix/geox-execution-handoff-state-schema-refresh-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 1 — repository governance test repair
**Task execution authorized:** `true`
**Correction execution authorized:** `false`
**Merge authorized:** `false`
**PR creation authorized:** `false`
**Implementation commit:** `159a7c4c54cdbb7c39f387c949728610e7c4c8a6`
**Review decision:** `ready_for_review`
**Unresolved execution-blocking design questions:** none

Verified repository pins: GeoX `843fa3d9196b68cf205a88addae83ec890b48366`,
MIP `a293ce52a813709ca624332123019139928cc51e`, MMM
`fe8e784923994406a2e4907d28debd872d61fd73`.

## Objective

Update `tests/test_repo_native_execution_handoff.py::test_v2_state_contract_and_pins`
to validate the current GeoX repository execution-state schema
`geox_repo_execution_state_v3` rather than the obsolete `v2` literal.

Preserve all existing checks for valid Git SHAs, lifecycle status vocabulary,
task identity, MIP/MMM pin consistency across execution evidence, required
repository surfaces, merge authority, and capability authority. The repair may
change only the stale schema expectation and any directly necessary assertions
proven by the live v3 state. Do not add compatibility aliases or weaken
invariants.

## Scope

Owned implementation path:

`tests/test_repo_native_execution_handoff.py`

Lifecycle publication may update the three stable execution files. No
production, analytical, validation, D5, calibration-source, artifact, MIP,
MMM, dependency, Docker, CI, or capability-authority changes are authorized.
The prior import-isolation repair is merged and closed; its implementation is
not to be reused as ancestry.

## Validation contract

Run JSON parsing, the focused stale-schema and closure-invariant tests, the
complete handoff test module, Ruff on the changed test, compile validation, and
`git diff --check`. Verify exact changed paths and local/remote feature-head
equality. The full Docker gate is not required for this isolated governance
test repair; the known remaining baseline families stay separate and must not
be repaired here.

## Sequencing and authority

The task does not authorize TBR, production/validation-boundary, D5 artifact,
analytical, producer-certification, lifecycle-adoption, MIP, MMM, or any
downstream capability work. All product, runtime, certification, sibling, and
capability authority remains false. Stop at `ready_for_review` for external
exact-head review; do not create a PR or merge.
