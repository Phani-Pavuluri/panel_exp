# GeoX repository-native execution

Mandatory bootstrap order:

1. Classify the full worktree; only `.codex/` and `docs/tasks/` may be local-only untracked.
2. Run `git fetch --prune origin` and hydrate missing history.
3. Run `git switch main`.
4. Run `git pull --ff-only origin main`.
5. Prove `main == origin/main`.
6. Only then read execution state, active task, context index, GeoX evidence, and pinned MIP/MMM standards.

Execution is fail-closed: verify authorization, exact base and ancestry,
prerequisites, branch, owned scope, validation, commit, and push; stop at
`ready_for_review`. Approval is external. `approved_for_merge` is not a state,
and no pre-merge approval metadata commit is allowed. Merge only after exact-head
approval with `git merge --ff-only`, one closure commit, push, synchronization,
and cleanup. Never create a PR or guess.

For lifecycle-state work, the repository-authored validation invocation is
`python -m panel_exp.execution.taskctl check`.

# GeoX routine-merge standing authority (proposed; activates only on owner adoption and merge)

A durable external approval receipt for an exact head satisfies exact-head
approval for eligible routine heads only, without a per-head owner prompt.
Eligible head: `ready_for_review` on its declared branch; merge, PR,
capability, and next-task authority all false; approval null; independent
exact-head review passed with findings resolved and re-reviewed; Tier 1 gate
green on the exact head (`taskctl check`, focused plus handoff plus combined
suites, `json.tool`, `git diff --check`, ancestry and fast-forward
eligibility, owned-paths check); branch diff limited to owned paths; no scope,
contract, product, sibling, or authority change. Anything else stays
owner-prompted, including any non-fast-forward situation.

The receipt is a Git note under the supervised namespace
(`refs/notes/codex-supervised-reviews`) recording exact reviewed head,
decision, gate results, reviewer thread and session references, and timestamp.
Task-state flags are never flipped for merging; merge authority flows from
this standing authority plus the per-head receipt, never from task flags.

Mechanical closure stays foreground-owned in private clones: verify
eligibility, `git merge --ff-only`, push the merged branch and main, observe
local and remote branch deletion, then write one closure commit citing
reviewed head, receipt note, gate summary, observed cleanup, and unchanged
authority; prove `main == origin/main` and re-validate the merged tree.
Deletion must be observed before the closure is valid (merged state requires
both cleanups observed); a non-fast-forward situation aborts to the owner.
This standing authority is revocable and narrowable by authoring commit
at any time. Goals, architecture, contracts, capabilities, authority grants,
product eligibility, and revocation itself stay with the owner.
