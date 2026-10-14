<!-- BEGIN GEOX TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** `authorized`

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `GEOX_EXHAUSTED_REVIEW_ROUTE_CONTRACT_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `496c317bc44c31a89aff805896863bd7eb637b7e`
- **Authorization provenance:** `41972b488ad1af418c6c3275584cc595e7824a92`
- **Feature branch:** `docs/geox-exhausted-review-route-contract-001`
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

Authoring owns only the three stable execution files on main. Create `docs/geox-exhausted-review-route-contract-001` from synchronized post-authoring main after verifying authorization ancestry and metadata-only authoring boundary. Preserve the historical branch unchanged: no merge, rebase, cherry-pick, deletion, extra correction or execution from it.

## Evidence and impact

Historical target: `GEOX_STRUCTURED_COMPLETION_EVIDENCE_001`, branch `feat/geox-structured-completion-evidence-001`, exact remote review head `81664df0d687746a8ee990eada702a2a54cc23c0`, implementation `3841c1790d82d94ebdb99dc6a4022b3c4097c86d`, authorization `55c4c6c237642195732d949d034e98763c5d8cac`. One correction completed, none remaining. Independently reproduced: malformed non-null completion evidence passes early-lifecycle validation and can crash rendering; existing 25 focused tests pass. Current controller rejects both exhausted rejection routes. Verify immutable Git evidence; the old head remains unapproved.

Live overlay verified 2026-10-14: GeoX main `496c317bc44c31a89aff805896863bd7eb637b7e`; MIP main `c7215b9c2afe38bbe2191c03cd89a114ea82d9c4`, validator recovery merged; MMM main `6f60cd2896d56f67675c7eb94e23f6e9f6ef36a8`, worker/reviewer roles merged. Affected/modified repository: GeoX only. Siblings read-only context. Preserve historical pins and coordination snapshot. Workstream `WS-GEOX-EXHAUSTED-REVIEW-ROUTE-CONTRACT-001`, owner `geox_execution_validation_governance`. Dependency `DEP-GEOX-EXHAUSTED-REJECTED-EVIDENCE-001` is immutable evidence, not a merged prerequisite. No consumer verification or product eligibility follows. No overlapping writer is authorized.

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
