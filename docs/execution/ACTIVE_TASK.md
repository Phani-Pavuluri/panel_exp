<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `ready_for_review`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_ROUTINE_MERGE_ADOPTION_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `b3a52ac34edca35e83c143c59eb37665a2e3ad2d`
- **Authorization provenance:** `029f3039a92eec36e4401255331e8b8bfec8b74e`
- **Feature branch:** `docs/geox-routine-merge-adoption-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `936ccf451dfef5486dc9302403fd51782b367204`
- **Reviewed head:** `null`
- **Rejected review head:** `7775700e36d353016db689752a281999f9299043`
- **Rejected implementation commit:** `936ccf451dfef5486dc9302403fd51782b367204`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `1`
- **Correction cycles remaining:** `0`
- **Review decision:** `ready_for_review`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->

## Primary outcome and authority (authorized — execution authorized, not started)

Adopt standing GeoX routine-merge authority for already-authorized, already-reviewed routine work: fail-closed eligibility, independent Codex exact-head review, required tests, durable external approval receipt, ff-only mechanical closure — with no per-head owner prompt for eligible heads. Major goals, architecture, contracts, capabilities, and authority decisions stay with the owner. This contract is a proposal only: status `proposed`, task execution authority false. Provenance SHAs anchor the proposal baseline; they do not constitute authorization. Execution requires a future Git commit flipping status and execution authority. Muse-Spark owns implementation approach on authorization; Codex independently reviews.

Upon authorization, create `docs/geox-routine-merge-adoption-001` from synchronized post-authoring main after mandatory bootstrap, taskctl check, authorization ancestry, metadata-only authoring boundary and branch-absence verification. Only one writer. Affected/modified: GeoX only. Workstream `WS-GEOX-ROUTINE-MERGE-ADOPTION-001`; owner `geox_execution_validation_governance`.

## Eligibility, receipt, and closure (decided)

Eligible head: `ready_for_review` on its declared branch; merge/PR/capability/next-task authority all false; approval null; independent Codex exact-head review passed with findings resolved and re-reviewed; Tier 1 gate green on the exact head (taskctl check, focused + handoff + combined suites, `json.tool`, `git diff --check`, ancestry/ff-eligibility, owned-paths); branch diff limited to owned paths; no scope, contract, product, sibling, or authority change. Anything else stays owner-prompted.

Approval evidence: Git note under the supervised namespace (`refs/notes/codex-supervised-reviews`) recording exact reviewed head, decision, gate results, reviewer thread/session, and timestamp — the proven `8bcbba2`/`87d02b6` pattern. No new service, no hardcoded verifier. Task-state flags are never flipped for merging; authority flows from standing approval plus the per-head receipt.

Mechanical closure (foreground, private clone): verify eligibility, `git merge --ff-only` (non-ff aborts to owner), one closure commit citing reviewed head, receipt note, gate summary, and unchanged authority; push; prove `main == origin/main`; observe branch cleanup; post-fast-forward re-validation. The `9c6c6b2`/`b3a52ac` closures are the template.

## Retained, revocation, and alignment

Owner-retained: goals, architecture, contracts, capabilities, authority grants, product eligibility, any ineligible head, any non-ff situation, revocation, and the parked producer-version contract choice (preserved for its own follow-up; no version pinned here). Standing authority is revocable/narrowable by authoring commit at any time.

Clauses to align on adoption: `AGENTS.md` merge paragraph and context-index merge protocol (receipt-for-exact-head satisfies exact-head approval for eligible heads only); task-contract boilerplate unchanged (routine merge stays outside execution authority); `approval_provenance.mode` generalized from one-off exception to standing authority with eligibility pointer, receipt format, and revocation — itself an owner decision, not self-adopted by this proposal.

## Proposal record

Successor context: merged `GEOX_STRUCTURED_COMPLETION_EVIDENCE_RECOVERY_001` (closure `b3a52ac`, reviewed `b810f50`); owner-directed routine-approval repair is the active coordination step. Entry carried byte-identical from the merged blob; frozen branches observed read-only unchanged. No owner policy outstanding beyond adoption itself.

## Execution authorization recorded — October 15, 2026

Owner direction for bounded routine-merge adoption is recorded in canonical state (status `authorized`, task execution authority true) and native generated views. This action grants execution within the named owned paths and validation gate only; it does not approve merges, activate routine merging, or add goals, capabilities, architecture, analytical meaning, or sibling authority. The definition-ready contract above is unchanged except for the authorized status heading. Muse-Spark implements on this authority; Codex independently reviews. No unresolved execution-blocking design questions remain.


## Independent bounded correction authorization

Rejected exact head 7775700e36d353016db689752a281999f9299043, implementation 936ccf451dfef5486dc9302403fd51782b367204. The remaining existing correction cycle is authorized in canonical state. Preserve owned implementation paths (AGENTS.md and context-index approval alignment) plus the stable three files; no controller/tests/product/sibling changes.

Current scope/authority comes from canonical state and the dated execution authorization, not stale proposal sentences carried in human prose. This correction must make the human task/report evidence consistent with that actual authority and current implementation; prior-task provenance is explicitly historical, never Current outcome. Keep the owner's process decision and all eligibility/major-decision boundaries.

Using the already-merged native completion-evidence recording API to publish this task's own truthful evidence in its owned stable files is authorized publication work, not authorization to implement a new evidence feature. The workflow flag is explicitly enabled for that existing route. Do not change controller or test code, weaken a check, or relabel a required failure as optional. Full controller, handoff and combined suites must all pass on the final exact tree. If a real unowned fixture/controller defect remains after normal task-owned publication, record the exact reproduction and blocked dependency; do not widen this task.

The authoritative remote feature state is changes_requested; synchronized main remains the older authorization snapshot. Resume the declared branch and use actual rejection provenance/counter state. Implement the bounded correction, publish fresh consistent human evidence with actual current implementation SHA, run every required gate, use native ready transition with complete-correction, and stop at a new frozen ready_for_review receipt head. No merge or activation.
