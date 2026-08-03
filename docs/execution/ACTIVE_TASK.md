# Active Task

**Status:** authorized
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_LEAN_REPOSITORY_DELIVERY_STANDARD_ADOPTION_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Pre-authoring base:** `b433879138e7bca303a1095acf50054619aa76a0`
- **Feature branch:** `docs/geox-lean-repository-delivery-standard-adoption-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 1 — documentation, execution governance, and one focused governance test
- **Canonical MIP execution-standard pin:** `Phani-Pavuluri/marketing_intelligence_platform@369805d923454a51ce98845cea29bdb1ee3c3895`
- **MMM main observed:** `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Superseded GeoX task:** `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`
- **Preserved superseded branch head:** `216c53f13919ec5ee7fa060a9c052e8a074fb9cc`
- **Capability authorizations changed:** `false`

## Primary mergeable outcome

Adopt the merged MIP lean repository-delivery and Codex-execution rules as
GeoX-owned execution governance so future GeoX tasks are definition-ready,
independently mergeable, risk-proportionately validated, invoked with minimal
Codex prompts, and required to publish one durable terminal outcome.

This is one governance outcome. It does not implement, recover, split, or merge
the superseded governed-readout builder work.

## Why this task cannot be split further

The lean task-definition rule, invocation-only prompt rule, terminal-outcome
rule, risk-tier validation, and durable exact-tree receipt jointly define one
GeoX execution contract. Adopting only part would leave contradictory task
authoring and execution behavior. The implementation remains bounded to
execution guidance and one focused semantic test.

## Exact observable behavior

### 1. Lean task definition

GeoX execution guidance must require every executable task to declare:

- one primary independently mergeable outcome;
- why it cannot be split further;
- exact observable behavior and preserved boundaries;
- resolved design and authority decisions;
- inputs, outputs, and failure semantics appropriate to the changed surface;
- compatibility or migration policy when applicable, otherwise
  `not_applicable`;
- named acceptance tests or deterministic evidence;
- owned and prohibited paths;
- focused validation and risk tier;
- deferred successor tasks; and
- `unresolved execution-blocking design questions: none`.

A task remains `proposed`, design-blocked, or is split when Codex would otherwise
need to choose among materially different contract meanings.

### 2. Small merge units and bounded corrections

One authorized task has one primary mergeable outcome. A meaningful checkpoint
becomes a successor task when it can be reviewed and merged independently or
changes a public contract, migration, integration surface, or authority
boundary.

One correction cycle is the default. When review reveals a new independent
outcome, contract, migration, or integration surface, supersede or close the
current task and author a successor rather than repeatedly widening the branch.

### 3. Risk-proportional validation

Adopt the MIP three-tier model:

- Tier 1: focused documentation, structure, changed-path, and named governance
  tests;
- Tier 2: focused tests plus validation required by the changed public/package
  surface;
- Tier 3: owner-repository evidence, cross-repository review, and the complete
  applicable validation gate.

Docker-backed full validation remains required when Tier 3, the active task, a
changed analytical/public/package surface, or another repository-authored gate
requires it. A category outside the applicable gate is `not_required`, not a
failure. Never start duplicate GeoX validation containers.

### 4. Invocation-only Codex prompts

Durable implementation instructions live in Git. A Codex invocation must contain
only the execution command: synchronize from Git, resolve and read the exact
active task, execute only it, publish the required durable terminal outcome,
push the exact branch head, and stop without PR or merge.

Chat prompts must not restate architecture, acceptance criteria, checkpoints, or
correction detail already recorded in Git.

### 5. Terminal outcome enforcement

After successful orientation, an executable authorized task must continue to one
of these durable outcomes:

- `ready_for_review` after completing the task and applicable validation; or
- `blocked` only for a genuine external, dependency, environment, authority, or
  required-validation obstruction with exact diagnostics.

The executor must not stop after an orientation summary, report unfinished
implementation as `blocked`, or publish multiple current narratives. External
review alone sets `changes_requested`.

### 6. Durable exact-tree receipt

Before `ready_for_review`, freeze the task-owned tree and run the applicable gate
on that exact tree. The final publication commit message must durably record the
implementation parent, validation gate and result, focused-test count,
changed-path and diff checks, worktree state, evidence source, full-suite
disposition, and unchanged authority. Any later task-owned change requires a new
validated publication head.

### 7. Stable navigation

`REPOSITORY_CONTEXT_INDEX.md` must navigate to canonical execution and evidence
paths without mirroring mutable task identity, status, branch, or sibling pins.
Current task selection comes from `EXECUTION_STATE.json` and `ACTIVE_TASK.md`.

## Owned paths

Execution may modify only:

- `AGENTS.md`
- `docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `tests/test_repo_native_execution_handoff.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The two standard files may be created if absent. Do not modify any other file.

## Named acceptance evidence

Add or strengthen focused semantic tests that prove:

1. `test_lean_repository_delivery_standard_is_adopted` — one outcome,
   definition-ready fields, no unresolved execution-blocking design questions,
   split triggers, and one-correction-cycle rule are present;
2. `test_codex_invocation_and_terminal_outcome_rules_are_adopted` — minimal
   invocation-only prompt, continued execution after orientation, valid terminal
   outcomes, and reviewer-only `changes_requested` are present;
3. `test_risk_tier_and_durable_receipt_rules_are_adopted` — Tier 1/2/3,
   full-gate triggers, duplicate-container prohibition, and exact-tree receipt
   requirements are present; and
4. `test_repository_context_index_is_navigation_only` — the context index does
   not mirror current task ID, status, feature branch, or mutable sibling pins.

Equivalent test names are acceptable only when the same four semantic groups are
explicitly and independently asserted.

## Focused validation gate

Run on the exact task-owned tree:

- JSON parse for `docs/execution/EXECUTION_STATE.json`;
- Markdown/current-state consistency checks;
- exact changed-path verification;
- `git diff --check`;
- `pytest -q tests/test_repo_native_execution_handoff.py`;
- inspection of the final publication receipt trailers; and
- local/remote exact branch-head equality after push.

Docker, Ruff, mypy, and the complete suite are `not_required` for this Tier 1
documentation/governance task unless an unexpected executable dependency or
repository-authored gate is discovered. In that case publish accurate `blocked`
state rather than widening scope.

## Deferred successors

After this adoption is approved, merged, and closed, author builder work as
separate definition-ready tasks in this order:

1. GeoX governed-readout temporal lifecycle contract;
2. typed producer builder;
3. certified fixture generation, hashes, and replay semantics;
4. optional envelope and final repository handoff/integration validation.

No successor is authorized by this task.

## Non-goals and authority

Do not modify or merge the preserved builder branch. Do not implement contracts,
builders, fixtures, replay, envelopes, estimators, design, assignment, inference,
MMM compatibility, MIP consumer behavior, or coordination-ledger changes.

Task execution is authorized. Merge and PR creation remain false. MMM adoption,
product capabilities, analytical authority, live integration, real data, pilot,
production, and package-side agents remain unauthorized.

**Unresolved execution-blocking design questions: none.**

## Publication

On success publish `ready_for_review` with one real implementation SHA, empty
blockers, execution authorization true, correction authorization false, merge
and PR false, null reviewed/approval SHAs, unchanged capability authority, and a
durable exact-tree receipt commit. Push the exact branch head and stop.

Publish `blocked` only for a genuine external, authority, dependency,
environment, or required-validation obstruction with exact diagnostics. Do not
publish unfinished implementation as blocked. Do not create a PR or merge.
