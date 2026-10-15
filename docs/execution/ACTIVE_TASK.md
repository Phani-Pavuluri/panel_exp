<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `merged`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_STRUCTURED_COMPLETION_EVIDENCE_RECOVERY_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `9c6c6b2dbd4c106c0c70a5a062c0ea0fd6bb7af9`
- **Authorization provenance:** `7a5c9b90b97704176d4053311de3d0d3746fbea2`
- **Feature branch:** `feat/geox-structured-completion-evidence-recovery-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `2bde13174d208747b4c88283b5e85c23fa3f0915`
- **Reviewed head:** `b810f50b50f0439d79a93ffaf2f5bfe956be2b8c`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `merged`
- **Local feature-branch cleanup:** `observed_deleted`
- **Remote feature-branch cleanup:** `observed_deleted`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->


## Primary outcome and bounded execution authority

Implement schema v6 completion evidence in the GeoX task controller: `completion_evidence` as `null` or the verbatim frozen v4 six-key object, validated on every lifecycle status before rendering, mandatory (non-null and valid) at `ready_for_review`, `changes_requested`, and `merged`. `rejection_history` carried verbatim from the merged lineage, append-only, never mutated by evidence writes. No lifecycle-edge, budget, merge, product, or sibling-authority change. This contract is execution-authorized by the recorded owner direction and canonical state. The original proposal baseline remains historical; the generated provenance identifies the published owner-authoring contract. Muse-Spark owns implementation approach on authorization; Codex independently reviews.

Upon authorization, create `feat/geox-structured-completion-evidence-recovery-001` from synchronized post-authoring main after mandatory bootstrap, taskctl check, authorization ancestry, metadata-only authoring boundary and branch-absence verification. Only one writer. Affected/modified: GeoX only. Workstream `WS-GEOX-STRUCTURED-COMPLETION-EVIDENCE-RECOVERY-001`; owner `geox_execution_validation_governance`.

## Target and dependencies

No historical re-recording is authorized or needed: the canonical disposition for `GEOX_STRUCTURED_COMPLETION_EVIDENCE_001` (`81664df`/`3841c17`, counters 1/1/0, prior pair `61c4e7d`/`0d251c2`) is carried verbatim in live `rejection_history` from merged `9c6c6b2` (dependency `DEP-GEOX-MERGED-REJECTION-HISTORY-001`). Frozen v4 blob `81664df` is the evidence-shape and late-gate reference (dependency `DEP-GEOX-EXHAUSTED-REJECTED-EVIDENCE-001`): exact six keys, late-lifecycle-only validation (the early gap), fully-generated report. Both dependencies are read-only evidence. Frozen branches remain unchanged/unapproved: no branch writes, merges, rebase, cherry-pick, deletion or extra correction.

Read-only live overlay, siblings untouched: MIP `c7215b9c2afe38bbe2191c03cd89a114ea82d9c4`, MMM `6f60cd2896d56f67675c7eb94e23f6e9f6ef36a8`; historical pins preserved; no shared coordination refresh, consumer verification, or product eligibility.

## Resolved interface and compatibility

CLI: `taskctl record-evidence --evidence-file <path>`. Python API mirrors the single named input. No lifecycle edges or unblock commands. On success the command writes the validated evidence object atomically and re-renders views; live status/counters/authority/history stay byte-identical. Malformed file or object fails coded (`E_COMPLETION_EVIDENCE_*`) with no tracked writes.

Compatibility (decided): v3 (no history, no evidence key) and v5 (history required, evidence key forbidden) read/check/render/sync byte-unchanged; v4 live is `E_SCHEMA_VERSION`. v6 requires `rejection_history` (possibly empty) and `completion_evidence` (`null` or valid). Write-time migrations only, never on read: `record-evidence` on v3→v6 (adds `[]` history plus evidence), v5→v6 (adds evidence key, history preserved byte-identical), v6→v6 (replaces evidence after fresh validation); `record-rejection` preserves evidence byte-identical. Authoring wrote this proposal as v5 with history carried verbatim and no evidence key. No downgrades, no general migration command.

History rule: entries are time-bound historical facts; carrying task asserts nothing new and refreshes no carried field. Append-only within and across rotation (never reset, never edited, never dropped); duplicate `(H,I)` refused while retained. New findings about recorded targets belong in task evidence and review prose, not second entries.

## Scope, tests and gate

Owned on authorization: `panel_exp/execution/taskctl.py`, `tests/execution/test_taskctl.py`, `tests/test_repo_native_execution_handoff.py` (schema-set admission only), three stable execution files. Context index unchanged (stable design holds). No new report subsystem, docs contract, analytical/runtime/product/sibling work. All protected authority false; three unrelated defects unresolved. Unresolved execution-blocking design questions: none. One outcome: validated completion-evidence reporting with preserved history; role adoption deferred separately.

Tier 1 gate for execution, exact-head review and post-fast-forward: taskctl check; full focused, handoff, and combined suites (all green, no waiver); JSON parsing; git diff --check; authorized-baseline changed-path and authority checks. Tests prove: null accepted early; malformed non-null rejected coded on every status (string/wrong-keys/missing fields/non-`passed`/prohibited-true, incl. historical crash shapes); null at the three late statuses rejected; v3→v6/v5→v6 migration with preservation both directions; duplicate refusal; v3/v5 reads unchanged; v4 live rejected; invalid input changes no tracked file (byte-asserted); direct render of malformed evidence/history raises coded, never uncaught. Isolated Git fixtures for Git-dependent paths, never actual target writes. Docker/analytical/Ruff/mypy not_required for this narrow milestone.

## Publication and stop (for the authorized task)

Record evidence via the new CLI on the clean implementation tree with real owned paths and executed validations. Human evidence outside report markers: implementation SHA, gate counts, Git identity/ancestry, limitations, cross-repo impact, authority. Native `transition --to ready_for_review --implementation-sha`. Freeze and validate the exact tree; receipt names implementation parent, gate/results, paths, clean state, evidence source, unchanged authority. Push the declared branch only, prove equality, stop without merge or successor authorization.

## Proposal record

Successor to merged `GEOX_EXHAUSTED_REJECTION_RECORD_RECOVERY_001` (closure `9c6c6b2`, reviewed `87d02b6`), per its `planned_followup` (`GEOX_STRUCTURED_COMPLETION_EVIDENCE_RECOVERY_001`, planned-not-authorized). Entry carried byte-identical (verified against the merged blob); frozen v4/v3/v5 semantics reconciled above with no open alternatives. No owner policy outstanding: uniform mandate, verbatim keys, suffix-preserving render, and retention are settled by Git evidence and the merged baseline.


## Recorded owner direction and authoring review

Owner repeatedly directed implementation and independent parallel work across MIP, GeoX and MMM, approved bounded follow-up work within existing goals, directed Git owner-report publication, and requested continuation. This action records that existing scope authority in Git; it does not approve merges or add goals, capabilities, architecture, analytical meaning or sibling authority.

The definition-ready contract above is approved for execution within its named owned paths and validation gate. This authority is materialized in canonical state and native generated views in the metadata finalization. No unresolved execution-blocking design questions remain.
