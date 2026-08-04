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

Branch-bound tasks read identity from synchronized main, switch explicitly,
run binding preflight before edits, prepush before pushing only the declared
branch, fetch the remote branch, and run postpush to prove exact equality.
