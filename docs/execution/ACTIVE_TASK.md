<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `changes_requested`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_TIER1_CALLBACK_INJECTION_REPAIR_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `3c2f7ec3dfb196c3308e8fb8f67c68d8ff5dc69e`
- **Authorization provenance:** `9e73059a066cf79c118a389ac4cc2923e0e694c0`
- **Feature branch:** `tests/geox-tier1-callback-injection-repair-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `true`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `78ef230547aff35a79a4a066b6ebd23f97483d29`
- **Reviewed head:** `null`
- **Rejected review head:** `78ef230547aff35a79a4a066b6ebd23f97483d29`
- **Rejected implementation commit:** `78ef230547aff35a79a4a066b6ebd23f97483d29`
- **Approval commit:** `null`
- **Blockers:** `GEOX-TIER1-PIN-RESTORATION-001: restore the preserved GeoX/MIP/MMM coordination pins before rerunning the handoff gate.; GEOX-TIER1-GATE-REENABLE-001: the handoff pin assertion must pass on the corrected exact tree; the three unrelated historical guardrail/BRB failures remain reported and unwaived.`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `changes_requested`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->

## Primary outcome and authority (authorized successor)

Repair the existing validation-owned callback injection surface for the fifteen tests in `tests/validation/test_design_tier1_contract_emission_001.py`. The successor must preserve every assertion and payload expectation, exercise the existing callback seam, and remain tests-only. The three unrelated historical failures (two guardrail cases and one BRB case) must remain visible as limitations; they must not be waived, deselected, or folded into this task. No controller, production, analytical, producer-certification, sibling, or authority change is included. Muse-Spark owns implementation approach; Codex independently reviews.

Upon authorization, create `tests/geox-tier1-callback-injection-repair-001` from synchronized main after mandatory bootstrap, taskctl check, authorization ancestry, metadata-only authoring boundary and branch-absence verification. Affected/modified: GeoX only. Workstream `WS-GEOX-TIER1-CALLBACK-INJECTION-REPAIR-001`; owner `geox_execution_validation_governance`.

## Scope, tests and gate

Owned on authorization: `tests/validation/test_design_tier1_contract_emission_001.py` plus the three stable execution files (generated blocks via native commands; human evidence outside markers). Controller, production, analytical, handoff, context-index, sibling, and authority surfaces are read-only. The task's own evidence must record all fifteen tests and the three unrelated historical failures without waiver or deselection. Frozen branches remain unchanged/unapproved. All protected authority false; unresolved execution-blocking design questions: none.

Tier 1 gate for execution and exact-head review: taskctl check; the repository's focused taskctl and handoff tests; direct execution of all fifteen tier-1 emission tests; combined result; JSON parsing; git diff --check; authorized-baseline changed-path and authority checks. The three historical guardrail/BRB failures must be reported as inherited limitations, never excluded. Full Docker validation is not required for this narrow tests-only milestone and must be recorded as not run.

## Publication and stop (for the authorized task)

Record real gate evidence on the clean implementation tree, including all fifteen direct acceptance tests and the three inherited failures. Human evidence outside report markers must include implementation SHA, gate counts, Git identity/ancestry, limitations, cross-repo impact, and unchanged authority. Freeze and validate the exact tree, publish the declared branch, prove equality, and stop without merge or successor authorization.

## Proposal record

The existing GeoX callback seam is validation-owned and already permitted for tests; the successor covers the complete fifteen-test file rather than an earlier undercount of eleven. The three unrelated historical failures remain separate limitations. No owner policy or producer/finality decision is included; no product, contract, capability or gate authority changes.
