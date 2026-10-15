<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `proposed`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_ROUTINE_MERGE_ADOPTION_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `b3a52ac34edca35e83c143c59eb37665a2e3ad2d`
- **Authorization provenance:** `b3a52ac34edca35e83c143c59eb37665a2e3ad2d`
- **Feature branch:** `docs/geox-routine-merge-adoption-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
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
- **Review decision:** `proposed`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->

## Primary outcome and authority (proposed — execution NOT authorized)

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
