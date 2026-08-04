# Active Task

**Status:** changes_requested
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_LEAN_REPOSITORY_DELIVERY_STANDARD_ADOPTION_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Pre-authoring base:** `b433879138e7bca303a1095acf50054619aa76a0`
- **Authorization head:** `686c3505151ee7073d52a9e70a8ea1b3f942ced4`
- **Feature branch:** `docs/geox-lean-repository-delivery-standard-adoption-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 1 — documentation, execution governance, and focused governance tests
- **Canonical MIP execution-standard pin:** `Phani-Pavuluri/marketing_intelligence_platform@369805d923454a51ce98845cea29bdb1ee3c3895`
- **MMM main observed during review:** `Phani-Pavuluri/MMM@b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`
- **Canonical MMM workflow pin:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Rejected review head:** `811ff9802cc41a46a7b4186e0eb026358becd337`
- **Rejected implementation commit:** `78e4145415b1530c4ca9795f81cd82480f33942b`
- **Superseded builder branch:** `feat/geox-governed-readout-builder-package-entrypoint-001`
- **Capability authorizations changed:** `false`

## Primary mergeable outcome

Adopt the merged MIP lean repository-delivery and Codex-execution rules as one
GeoX-owned execution-governance contract. Future GeoX tasks must be
branch-bound, definition-ready, independently mergeable, risk-proportionately
validated, invoked with minimal Codex prompts, and required to publish one
durable terminal outcome.

This task does not implement, recover, split, resume, or merge governed-readout
builder work.

## Review decision

Exact remote head `811ff9802cc41a46a7b4186e0eb026358becd337` is rejected as a
completion or merge candidate. Correction execution is authorized on the same
feature branch. Merge and PR authority remain false.

## Required corrections

### 1. Bind every execution to the exact authorized branch and task

Repository guidance must require this fail-closed sequence:

1. synchronize and read task identity from `main`;
2. obtain the exact authorized `feature_branch`, `task_id`, and authorization
   boundary from `main` execution state;
3. explicitly switch to that feature branch;
4. verify the checked-out branch name, branch-local `task_id`, branch-local
   `feature_branch`, and authorization ancestry before modifying anything;
5. stop when branch-local state names another task, when the branch is stale, or
   when the authorization boundary cannot be proven;
6. repeat branch, task-ID, destination-ref, and owned-path checks immediately
   before publication and push; and
7. verify local and remote feature-branch heads match after push.

Task identity must never be resolved from whatever branch happens to be checked
out. The superseded builder branch must not be modified, resumed, rebased,
merged, or used as the publication destination.

Update `AGENTS.md` and/or `docs/execution/TASK_EXECUTION_STANDARD.md` so this is
an executable rule, not an implication.

### 2. Complete the lean execution contract

The two standard documents must explicitly require:

- one primary independently mergeable outcome and why it cannot be split;
- exact observable behavior, resolved design and authority decisions, inputs,
  outputs, failure semantics, compatibility/migration policy, named acceptance
  evidence, owned/prohibited paths, risk tier, focused validation, deferred
  successors, and `unresolved execution-blocking design questions: none`;
- split triggers for independently reviewable checkpoints, public contracts,
  migrations, integration surfaces, and authority boundaries;
- one correction cycle by default;
- Tier 1, Tier 2, and Tier 3 validation;
- full-gate triggers when the task, changed analytical/public/package surface,
  Tier 3 boundary, or another repository-authored gate requires it;
- explicit `not_required` handling outside the applicable gate;
- prohibition on duplicate GeoX validation containers;
- invocation-only Codex prompts with durable detail in Git;
- continued execution after successful orientation;
- executor terminal outcomes limited to `ready_for_review` or genuine `blocked`;
- external-review-only `changes_requested`; and
- an exact-tree receipt containing implementation parent, gate, result, exact
  test counts, changed-path check, diff check, worktree state, evidence source,
  full-suite disposition, and authority impact.

The six-line execution standard and keyword summary are insufficient.

### 3. Make the context index truly navigation-only

Remove all mirrored mutable task identity, task status, feature-branch identity,
and mutable MIP/MMM commit pins from
`docs/execution/REPOSITORY_CONTEXT_INDEX.md`.

The rejected implementation added a navigation disclaimer but retained the stale
`GEOX_REPO_NATIVE_EXECUTION_HANDOFF_V2_ADOPTION_RECOVERY_001` task and old
canonical pins. The final index must contain only stable navigation and ownership
information, directing readers to the execution files for current state.

### 4. Replace keyword-presence tests with semantic enforcement

Strengthen `tests/test_repo_native_execution_handoff.py` so the four named test
groups independently prove the required behavior. Tests must not pass merely
because selected words occur in a document.

At minimum, tests must verify:

- definition-ready fields, split triggers, and the one-correction-cycle rule;
- exact main-to-feature-branch binding, task/branch/head verification,
  pre-push destination verification, and fail-closed handling of stale or wrong
  branch-local state;
- invocation-only prompts, continued execution after orientation, valid executor
  terminal outcomes, and reviewer-only `changes_requested`;
- Tier 1/2/3, full-gate triggers, `not_required`, duplicate-container
  prohibition, and every exact-tree receipt field; and
- absence of active task IDs, statuses, feature branches, and mutable sibling
  SHAs from the context index.

### 5. Publish one current report and a real exact-tree receipt

Replace `LATEST_COMPLETION_REPORT.md` with one current evidence narrative. Do
not append a completion section beneath an older `AUTHORIZED FOR EXECUTION`
decision.

The final report must record the exact implementation SHA, commands, pass/fail/
skip counts, evidence source, blockers, limitations, validation debt, sibling
impact, consumer verification, newly eligible work, and authority impact.

The final publication commit message must contain the declared receipt fields.
The rejected publication commit `811ff980...` had no receipt trailers. Its claim
that focused Docker tests passed also omitted the exact command and counts, and
Docker was not required for this Tier-1 gate.

## Owned paths

Correction execution may modify only:

- `AGENTS.md`
- `docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `tests/test_repo_native_execution_handoff.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify any analytical, contract, builder, fixture, estimator, design,
assignment, inference, MIP, MMM, coordination-ledger, or product/runtime path.

## Validation gate

Run on the frozen task-owned tree:

- JSON parse for `docs/execution/EXECUTION_STATE.json`;
- Markdown/current-state consistency checks;
- exact changed-path verification;
- `git diff --check`;
- `pytest -q tests/test_repo_native_execution_handoff.py` with exact counts;
- inspection of the final publication receipt trailers; and
- local/remote exact branch-head equality after push.

Docker, Ruff, mypy, and the complete suite are `not_required` for this Tier-1
governance task unless an unexpected executable dependency or repository gate
is discovered. Such a discovery is a genuine blocker; do not widen scope.

## Deferred successors

Only after this task is approved, merged, and closed may GeoX separately
authorize:

1. governed-readout temporal lifecycle contract;
2. typed producer builder;
3. certified fixture generation, hashes, and replay semantics; and
4. optional envelope plus final handoff/integration validation.

No successor is authorized here.

## Publication

On success, publish `ready_for_review` with one implementation SHA, empty
blockers, execution authorization true, correction authorization false, merge
and PR false, null reviewed/approval SHAs, unchanged capability authority, one
current completion report, and a durable exact-tree receipt commit.

Publish `blocked` only for a genuine external, authority, dependency,
environment, or required-validation obstruction with exact diagnostics. Do not
publish unfinished implementation as blocked. Do not create a PR or merge.

**Unresolved execution-blocking design questions: none.**
