<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `authorized`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_TIER1_CALLBACK_INJECTION_REPAIR_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `bc1458610fec48a90d25cedf7c13b5d2d58f8e78`
- **Authorization provenance:** `b44f2d8b8169fee931d3bdcf575b817c577620dd`
- **Feature branch:** `tests/geox-tier1-callback-injection-repair-003`
- **Feature branch created:** `false`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `null`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `authorized`
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


## Authoring amendment — historical pin restoration and fresh branch

This preserves the authorized task's single tests-only outcome, owned paths, all fifteen unchanged acceptance assertions, mandatory gates and existing correction budget. Task authoring incorrectly put live observations into the three preserved historical pin fields; restore the exact committed historical values already recorded by the stable index. This is no context-index or coordination refresh and no producer-version/finality decision.

Canonical declared branch is now `tests/geox-tier1-callback-injection-repair-003`, created from synchronized amended main. The initial task authorization and authoring commits remain ancestors and are recorded in canonical authoring_amendments. Prior unpublished implementation `78ef230547aff35a79a4a066b6ebd23f97483d29` on tests/geox-tier1-callback-injection-repair-001 remains frozen local evidence, not a reviewed or approved head. Preserve it; do not merge, rebase, cherry-pick, force-push, reset or delete that line. The fresh branch avoids divergence between authoring metadata repair and the unpublished implementation. Muse owns implementation approach within the same original scope. New lifecycle evidence must be actual; all gates, owned paths and authority boundaries above remain unchanged. No new task, test waiver, product or policy meaning is introduced.
