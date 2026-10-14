<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `authorized`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_EXHAUSTED_REVIEW_ROUTE_CONTRACT_RECOVERY_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `3dc762d1a7937c3b1872591cc380f3aa0edeb68c`
- **Authorization provenance:** `3dc762d1a7937c3b1872591cc380f3aa0edeb68c`
- **Feature branch:** `docs/geox-exhausted-review-route-contract-recovery-001`
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


## Owner-approved bounded prerequisite

Primary outcome: one recommended definition-ready governance contract in `docs/execution/EXHAUSTED_REVIEW_ROUTE_CONTRACT.md`. Documentation only. Muse-Spark owns the recommendation and supporting investigation; Codex independently reviews it. Controller implementation, completion-evidence recovery and role adoption are separate successors. This task does not execute rejection or authorize a successor.

Authoring owns only the three stable execution files on main. Create `docs/geox-exhausted-review-route-contract-recovery-001` from synchronized post-authoring main after verifying authorization ancestry and metadata-only authoring boundary. Preserve the historical branch unchanged: no merge, rebase, cherry-pick, deletion, extra correction or execution from it.

## Evidence and impact

Historical target: `GEOX_STRUCTURED_COMPLETION_EVIDENCE_001`, branch `feat/geox-structured-completion-evidence-001`, exact remote review head `81664df0d687746a8ee990eada702a2a54cc23c0`, implementation `3841c1790d82d94ebdb99dc6a4022b3c4097c86d`, authorization `55c4c6c237642195732d949d034e98763c5d8cac`. One correction completed, none remaining. Independently reproduced: malformed non-null completion evidence passes early-lifecycle validation and can crash rendering; existing 25 focused tests pass. Current controller rejects both exhausted rejection routes. Verify immutable Git evidence; the old head remains unapproved.

Live overlay verified 2026-10-14: GeoX main `496c317bc44c31a89aff805896863bd7eb637b7e`; MIP main `c7215b9c2afe38bbe2191c03cd89a114ea82d9c4`, validator recovery merged; MMM main `6f60cd2896d56f67675c7eb94e23f6e9f6ef36a8`, worker/reviewer roles merged. Affected/modified repository: GeoX only. Siblings read-only context. Preserve historical pins and coordination snapshot. Workstream `WS-GEOX-EXHAUSTED-REVIEW-ROUTE-CONTRACT-RECOVERY-001`, owner `geox_execution_validation_governance`. Dependency `DEP-GEOX-EXHAUSTED-REJECTED-EVIDENCE-001` is immutable evidence, not a merged prerequisite. No consumer verification or product eligibility follows. No overlapping writer is authorized.

## Contract acceptance

Recommend one coherent route. Distinguish approved process principles from recommended implementation details. The document must cover all five items:

1. Exact CLI/API signatures, fields/types/invariants, stable error codes, reviewer permissions, and Git identity/ancestry/head checks. Rejection applies only to an exhausted review-ready exact remote head.
2. Deterministic canonical blocked outcome, unchanged exhausted counters, protected authority and implementation/rejection lineage. Durable blocker, independent findings and live resolution condition. No extra correction, merge or product authority.
3. Explicit compatibility/migration from current main schema v3 and unmerged schema v4. Explain how a newly merged controller records historical-task rejection without editing its immutable branch or bypassing lifecycle controls. Specify the authoritative write target and historic-task identity. No implicit successor execution.
4. Failure semantics, no writes on invalid/stale input, multi-file consistency and recovery, deterministic views, and named acceptance cases: wrong repository/task/branch/head/implementation, remaining budget, missing evidence, protected flags, stale main, success and interrupted writes.
5. Separate implementation, completion-evidence recovery and role-adoption successors. Resolve technical recommendations. Identify any owner-reserved ambiguity without silently choosing a new capability or policy.

Unresolved execution-blocking design questions for this documentation outcome: none. Compatibility for this task: no runtime or persisted-schema migration; migration design is the deliverable.

## Owned paths and gate

Owned: new `docs/execution/EXHAUSTED_REVIEW_ROUTE_CONTRACT.md`; `docs/execution/EXECUTION_STATE.json`; generated block only in `docs/execution/ACTIVE_TASK.md`; `docs/execution/LATEST_COMPLETION_REPORT.md`. Other files read-only, including context index. All protected authority remains false; the three unrelated defect IDs remain unresolved.

Tier 1 documentation gate, repeated for execution, exact-head review and post-fast-forward: `.venv/bin/python -B -m panel_exp.execution.taskctl check`; `.venv/bin/python -m json.tool docs/execution/EXECUTION_STATE.json`; `git diff --check`; verify the authorization-baseline diff is limited to these four owned paths; manually verify all five acceptance items with section references. Docker, analytical tests, Ruff and mypy are not_required for this documentation scope. Do not add tests mirroring document text.

## Publication and stop

Commit the document implementation independently. Write human-authored evidence outside generated report markers: five acceptance section references, local gate results, implementation SHA, Git-observed identity/ancestry and paths, limitations, cross-repository impact and authority. Use native `taskctl transition --to ready_for_review --implementation-sha <implementation SHA>`. Freeze task-owned files, run the declared gate on the exact tree, then publish a receipt commit naming implementation parent, exact-tree gate/results, evidence source, tracked worktree state and authority impact. Push only the declared branch, prove local/remote equality and stop without merging or authorizing successors.

## Independent review findings and agreed discussion

Prior draft `cf743b8a0ac858a56997b41b1362f5be6d480a92` is immutable rejected evidence, not an implementation baseline or approved contract. Read its pushed `refs/notes/codex-supervised-reviews` finding receipt. Muse agreed all six findings and proposed live-task versus historical-target identity separation, structured rejection history, view-only sync recovery, explicit finding/resolution inputs, a main-v3-based compatibility route, and technical decisions owned by Muse/Codex.

This successor must produce a replacement document resolving all six findings, not merely add sections: define one feasible target input/read/write model; preserve earlier target rejection lineage without overwriting live task identity or unrelated top-level rejection fields; distinguish target exhausted budget from the live recording task's budget and lifecycle; fully specify canonical record fields, actual review evidence and limits of independence checks; define feasible per-file atomic state-first writes and view-only recovery with no double record; keep unmerged completion-evidence code out of the route-only baseline; choose routine schema/API/naming details as technical recommendations rather than owner approval questions.

Remaining discussion concerns: `approval_commit_sha` must stay null under the existing external-approval contract; a shared Git identity does not evidence independent agents; target identity must be read and checked from the exact remote Git blob, not compared tautologically to itself; findings and resolution cannot be inferred from an arbitrary blocker; new structured records must define all fields and validation, including prior rejected lineage. Do not promise a three-file transaction if only individual atomic replacement is provided. Avoid alternatives left for implementation to choose. Preserve every approved process boundary; recommendations are documentation only. Record any substantive disagreement as a limitation for owner review, not implied authority.
