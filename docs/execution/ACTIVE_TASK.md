<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `ready_for_review`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_EXHAUSTED_REJECTION_RECORD_RECOVERY_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `7a83bc0af5dd293512d17a7ce42bc3b4afb8f038`
- **Authorization provenance:** `a2efa242d27043307fe6b3a8cee89fbbc81d6c73`
- **Feature branch:** `feat/geox-exhausted-rejection-record-recovery-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `5dc0fa0f11809618412cacf78859a5932305e6be`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `ready_for_review`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END GEOX TASKCTL EXECUTION VIEW -->


## Primary outcome and authority

Implement one evidence-only `record-rejection` command in the existing GeoX task controller, then use it for the pinned exhausted historical task. The canonical record conveys a blocked review disposition; it does not mutate the target branch or the live recording task's lifecycle. Muse-Spark owns implementation approach; Codex independently reviews. Prior contract drafts are rejected evidence, not executable requirements. This task supersedes their recommendations with the resolved contract below.

Create `feat/geox-exhausted-rejection-record-recovery-001` from synchronized post-authoring main after mandatory bootstrap, taskctl check, authorization ancestry, metadata-only three-file task-authoring boundary and branch-absence verification. Only one writer. Affected/modified: GeoX only. Workstream `WS-GEOX-EXHAUSTED-REJECTION-RECORD-RECOVERY-001`; owner `geox_execution_validation_governance`.

## Target and dependencies

Only permitted live recording target is dependency `DEP-GEOX-EXHAUSTED-REJECTED-EVIDENCE-001`: task `GEOX_STRUCTURED_COMPLETION_EVIDENCE_001`, branch `feat/geox-structured-completion-evidence-001`, head `81664df0d687746a8ee990eada702a2a54cc23c0`, implementation `3841c1790d82d94ebdb99dc6a4022b3c4097c86d`, authorization `55c4c6c237642195732d949d034e98763c5d8cac`, counters 1/1/0. Prior rejected pair is retained from its exact blob, not guessed. Git independently confirms authorization and implementation are ancestors of the target head. Historical target and both rejected draft branches remain unchanged/unapproved: no branch writes, merges, rebase, cherry-pick, deletion or extra correction.

Read MIP coordination protocol/state, apply read-only live overlay and verify sibling main evidence. Last verified MIP `c7215b9c2afe38bbe2191c03cd89a114ea82d9c4` and MMM `6f60cd2896d56f67675c7eb94e23f6e9f6ef36a8`, both merged and independent. Reverify live observations, retain historical pins, do not refresh shared coordination state. Draft dependencies are immutable evidence, not merged prerequisites. No consumer verification or product eligibility follows.

## Resolved interface and canonical meaning

CLI: `taskctl record-rejection --dependency-id ID --rejected-head H --rejected-implementation I --blocker B [--blocker B ...] --finding F --resolution-condition R [--live-main M]`. Python API mirrors these named inputs. No new lifecycle edges or unblock commands.

Allowed live status: authorized or in_progress, with task execution authorized, correction authority closed, no blockers and all protected/merge/PR flags false. Actual checked-out branch must equal live feature_branch; live authorization and branch-baseline SHAs must be commit ancestors of HEAD. Verify live repository origin identity, clean tracked worktree before recording, main==origin/main after fetch, and supplied live-main equals the observed SHA. Named dependency must exactly pin target repository/task/branch/head/implementation. Missing/mismatched permission or pin fails before writes. This active task permits the actual append on its own branch; unit fixtures may simulate other valid targets.

Read target canonical JSON from exact H, supporting target schema v3 or v4 only. It must be an object with correctly typed identity/provenance/status/counters/authority/rejection fields: same GeoX repository, branch_and_fast_forward/main, ready_for_review, correction closed, task execution authorized, blockers empty, all protected flags false, valid nonnegative integer counters (not booleans), completed+remaining==maximum, remaining==0. Auth and branch-baseline commits and I must be ancestors of H. Verify remote target ref still equals H. Historical Git evidence must not be loaded as live state or bring unmerged completion code into main.

Live compatibility: continue reading/checking/rendering v3 unchanged when rejection_history absent. Successful first record on v3 atomically migrates schema to `geox_repo_execution_state_v5` and adds history containing the new entry, preserving every other state value. V5 requires rejection_history as a list (possibly empty); v4 is not supported live. No migration on read/check/sync, no general migration command. Live completion_evidence is not introduced or permitted on this route-only v5 baseline. The separate completion-evidence recovery must reconcile its contract with this merged schema; it must not replace this history.

Each history entry is an exact-key object with: target_repository (constant GeoX), target_task_id, target_branch, target_head_sha, target_implementation_sha, target_authorization_head_sha, target_branch_baseline_sha, target_schema_version (v3/v4), target_disposition (constant blocked), target_counters ({maximum,completed,remaining}), prior_rejected_review_head_sha and prior_rejected_implementation_commit_sha (paired SHA/null from blob), finding, resolution_condition, live_main_sha, blockers (ordered deduplicated nonempty strings). SHAs lowercase 40 hex; required strings nonempty after strip. Finding must name H and I. Entry blockers are historical snapshots, never compared to current live blockers on later loads. Validate entries in every v5 lifecycle before rendering; no uncaught dereference errors. Existing history entries are preserved exactly and one entry appended; duplicate target H/I fails. Existing live top-level rejected fields remain about the live task and are untouched.

Record command changes only schema/history and generated views. Live status/review_decision/blockers/counters/implementation/provenance/authority/approval_commit_sha remain unchanged, with approval_commit_sha null. The target's immutable branch remains ready_for_review; the canonical history explicitly represents independent rejected disposition, not target lifecycle mutation or approval. Later recovery cites the exact merged recording head and target H/I in its dependency and reads this history. It cannot regain budget or merge the rejected branch. Reviewer independence is procedural and evidenced externally by separate sessions/receipts; shared Git author names cannot prove it.

Stable failures: E_SHA for lexical SHA failures including prefixes; E_BLOCKERS for missing/blank blockers; E_REJECTION_EVIDENCE for record shape/finding/resolution; E_REJECTION_IDENTITY for identity, permission, pin or auth ancestry mismatch; E_REJECTION_IMPLEMENTATION for I mismatch/ancestry; E_REJECTION_HEAD for observed target ref disagreement or non-commit H; E_REJECTION_BUDGET for target not exhausted/correction open; E_REJECTION_BLOB_MISSING for unavailable commit/path/transport; E_REJECTION_BLOB_CORRUPT for unreadable JSON/object/required-field shape; E_REJECTION_SCHEMA for unsupported target schema; E_STALE_MAIN for live main mismatch; E_TRANSITION for disallowed live/target lifecycle or duplicate H/I; existing E_PROTECTED_AUTHORITY/E_AUTHORITY/E_VIEW_DIVERGENCE retain meanings. Deterministic check-first order: load/check live views; lexical inputs/live eligibility and branch/authority/pin; fetch/observe main and target; read/validate target and ancestry; findings/duplicate; build and validate candidate; write. Invalid input changes no tracked file. Git fetch may update refs, never task files or target branch.

Per-file atomic state-first replacement then two view replacements; no three-file transaction claim. A crash after state advance is detected as E_VIEW_DIVERGENCE; immediate retry also reports divergence. `sync` repairs views only, preserving state/history/counters, then duplicate record fails E_TRANSITION. Crash before state replacement leaves original tree retryable. No torn-state recovery scheme or automatic Git restoration. Active lifecycle block remains unchanged; completion generated block adds deterministic history details/none for v5, preserving native v3 human suffix behavior. Sync is idempotent.

## Scope, tests and gate

Owned: `panel_exp/execution/taskctl.py`, `tests/execution/test_taskctl.py`, `tests/test_repo_native_execution_handoff.py`, three stable execution files, and `docs/execution/REPOSITORY_CONTEXT_INDEX.md`. ACTIVE_TASK changes generated block only. No new parallel report subsystem, docs contract, analytical/runtime/product/sibling work. Context-index synchronization is explicitly owned as part of this migration handoff. All protected authority false; three unrelated defects unresolved. Unresolved execution-blocking design questions: none. One outcome: verified canonical historical rejection recording; completion evidence repair and role adoption are deferred separately.

Tier 1 isolated execution-governance gate for execution, exact-head review and post-fast-forward: taskctl check; full tests/execution/test_taskctl.py; full tests/test_repo_native_execution_handoff.py; combined both files; JSON parsing; git diff --check; authorized-baseline changed-path and authority checks. Add meaningful named rejection tests covering success with prior lineage/live invariance, wrong repo/task/branch/head/I/auth ancestry, target non-review-ready/remaining budget/protected flags, live permission/branch/pin/stale-main, malformed input/target/history, target schema compatibility, v3 unchanged read and first-write migration, duplicate, invalid no-write, interrupted state/view recovery, all-lifecycle rendering and sync determinism. Use isolated Git fixtures, never actual target writes. Native Docker/analytical suite/Ruff/mypy not_required for this declared narrow milestone. Existing controller/handoff suites must pass without weakening them.

Use the command once on this task's clean implementation tree with the pinned dependency, actual independent finding (malformed completion evidence accepted before rendering, exhausted review; 25 historical focused tests passed) and resolution (fresh completion-evidence recovery after merged record; old branch remains immutable/unapproved). Commit the implementation and canonical record; completion report records actual local validation results/counts, Git identity/provenance, limitations and cross-repository impact outside generated block. Use native transition to ready_for_review with implementation SHA. Freeze and validate exact task-owned tree; final publication receipt identifies implementation parent, exact-tree gate/results, changed paths, clean tracked state, evidence source, unchanged authority. Publish exact branch and stop without merge or successor authorization.

## Verified recovery evidence and migration handoff

Read pushed independent review notes on exact rejected head `8bcbba2ed4390e56e607fcd2e391d8b01a898e62`. Verified: required handoff gate 1 failed/2 passed (hardcoded v3 rejects v5); actual Git fixture accepts unsupported target execution_mode, non-main base_branch and non-boolean authority fields; malformed history target_schema_version list raises uncaught TypeError. The receipt's claim that the handoff file is outside scope is false. A baseline failure does not waive this gate.

You may use only the controller and focused-test content from immutable `8bcbba2` as starting material, not validation evidence. Restore those selected owned files into the fresh branch if useful; do not merge/rebase/cherry-pick or execute from the rejected branch and do not import its canonical state/report/record. Re-record the target through the corrected CLI on a new clean tree and independently validate the complete new outcome.

Acceptance additionally requires strict typed target validation for every required identity/provenance/lifecycle/authority/counter/rejection field before Git arguments or renderer dereference. Reject unsupported execution_mode/base_branch and non-boolean authorities with the already defined coded shape/identity failures. Exercise list/dict/null/wrong-scalar values for schema, status, branch, provenance and history fields; no uncaught exceptions, no writes on invalid input. Preserve prior typed semantics, lineage and all required negative tests.

Migration handoff includes an explicitly owned context index. Make it a stable source index referencing canonical EXECUTION_STATE.json and generated task/report views, rather than duplicating mutable task identity and pins that become stale at every task rotation. Meaningful native handoff checks must verify these source references resolve to the actual canonical identity, valid preserved pins, schema validation and task/report lifecycle/provenance consistency. Update the old v3-only test to test the authorized v3/v5 compatibility meaning; do not disable or skip the test, remove authority assertions, or count a failing baseline as passed. The seven-file owned boundary includes the context index, controller, both test files and three stable execution files.

Preserved canonical historical pins (readable in this task contract and completion evidence): GeoX `a78c4017e06c6f0bfb4329e749972b516dfbc7e9`, MIP `a293ce52a813709ca624332123019139928cc51e`, MMM `fe8e784923994406a2e4907d28debd872d61fd73`. These are distinct from current live main observations. Preserve the pinned values; do not refresh shared coordination state.

The full taskctl file, full handoff file and combined suite must each pass on execution, exact-head review and post-fast-forward. A failed required gate is not ready_for_review. Do not publish a successful readiness claim with a failed gate; no unsupported lifecycle hand-edit. If a real blocker prevents a legal terminal transition, preserve evidence on the safe authorized branch and clearly identify the missing controller path rather than claiming success.
