# Lean Repository Delivery Standard

Every executable task has one independently mergeable outcome, explicit
observable behavior, ownership and prohibited paths, failure semantics,
acceptance evidence, risk tier, and deferred successors. Unresolved
execution-blocking design questions must be `none`; otherwise the task remains
proposed or is split.

Inputs, Outputs, compatibility or migration policy, and named acceptance tests
are mandatory. Split when a checkpoint is independently reviewable or changes a
public contract, migration, integration surface, or authority boundary.

Codex prompts are invocation-only: synchronize Git, read the active task,
execute it, publish one durable terminal outcome, push the exact branch, and
stop. Review may mark `changes_requested`; execution publishes only
`ready_for_review` or a genuinely blocked result. The default is one correction cycle; independent outcomes become successor tasks.

Validation is risk-proportional: Tier 1 focused docs/structure/governance tests,
Tier 2 focused package tests, Tier 3 owner and complete applicable gates.
Full gates trigger for the task, analytical/public/package changes, Tier 3, or
repository-authored requirements; unrelated categories are `not_required`.
Never run duplicate validation containers.
Before review, freeze the task tree and record implementation parent, gate,
counts, changed paths, diff check, worktree, evidence source, and authority.
