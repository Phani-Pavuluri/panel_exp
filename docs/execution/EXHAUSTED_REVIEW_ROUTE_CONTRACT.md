# Exhausted Review Route Contract

**Task:** `GEOX_EXHAUSTED_REVIEW_ROUTE_CONTRACT_001`
**Status:** Recommended definition-ready governance contract. Not implemented.
**Scope:** Documentation only. No controller implementation, rejection execution,
additional correction, or successor execution is authorized by this document.
Muse-Spark owns the recommendation and supporting investigation; Codex
independently reviews it.

**Reading rule:** Sections marked **Approved principle** restate owner-approved
process constraints from `docs/execution/ACTIVE_TASK.md` and
`docs/execution/EXECUTION_STATE.json`. Sections marked **Recommendation**
are the coherent route proposed for independent review. Reviewers may accept,
amend, or reject any recommendation; they must not be mistaken for approved
behavior.

**Historical target (immutable evidence, not a merged prerequisite):**
task `GEOX_STRUCTURED_COMPLETION_EVIDENCE_001`, branch
`feat/geox-structured-completion-evidence-001`, exact remote review head
`81664df0d687746a8ee990eada702a2a54cc23c0`, implementation
`3841c1790d82d94ebdb99dc6a4022b3c4097c86d`, authorization
`55c4c6c237642195732d949d034e98763c5d8cac`, base
`a78c4017e06c6f0bfb4329e749972b516dfbc7e9`, counters 1 maximum / 1 completed /
0 remaining, schema `geox_repo_execution_state_v4`, status `ready_for_review`.
Verified 2026-10-14: `git ls-remote origin
refs/heads/feat/geox-structured-completion-evidence-001` returns exactly
`81664df0d687746a8ee990eada702a2a54cc23c0`; the old head remains unapproved.

**Current-task provenance (Git-observed):** base
`496c317bc44c31a89aff805896863bd7eb637b7e`, task-authoring and authorization
head `41972b488ad1af418c6c3275584cc595e7824a92`, post-authoring main
`3dc762d1a7937c3b1872591cc380f3aa0edeb68c`, feature branch
`docs/geox-exhausted-review-route-contract-001`. Live overlay 2026-10-14:
GeoX main `496c317bc44c31a89aff805896863bd7eb637b7e`; MIP main
`c7215b9c2afe38bbe2191c03cd89a114ea82d9c4` (validator recovery merged); MMM
main `6f60cd2896d56f67675c7eb94e23f6e9f6ef36a8` (worker/reviewer roles merged).
Preserved historical pins: GeoX `a78c4017e06c6f0bfb4329e749972b516dfbc7e9`,
MIP `a293ce52a813709ca624332123019139928cc51e`, MMM
`fe8e784923994406a2e4907d28debd872d61fd73`.

**Recommendation summary:** Add exactly one canonical route — direct
`ready_for_review` (exhausted) to `blocked` via independent rejection — to a
successor controller. Do not route exhausted rejection through
`changes_requested` (it requires correction budget that is zero by definition).

---

## 1. Interface — signatures, fields, codes, permissions, Git checks

### 1.1 Approved principle

- Execution mode is `branch_and_fast_forward` on base branch `main`
  (`panel_exp/execution/taskctl.py:129-131`).
- Only review-ready completion is available to the current (`v3`) task
  controller: `transition()` raises `E_TRANSITION_EVIDENCE` for any target
  other than `ready_for_review` (`taskctl.py:274-275`).
- Current transitions allow `authorized/in_progress/changes_requested` to
  `blocked`, but **not** `ready_for_review` to `blocked`
  (`taskctl.py:34-44`; `TRANSITIONS["ready_for_review"] ==
  {"changes_requested", "merged"}`).
- `blocked` requires execution authority and explicit blockers
  (`taskctl.py:165-166`, `E_BLOCKED_EVIDENCE`); `ready_for_review` requires
  implementation, no blockers, and closed correction authority
  (`taskctl.py:172-174`, `E_REVIEW_EVIDENCE`); correction counters must satisfy
  completed plus remaining equals maximum (`taskctl.py:148-152`,
  `E_CORRECTION_COUNTERS`); rejected review and implementation evidence must be
  paired (`taskctl.py:159-161`, `E_REJECTED_PROVENANCE`).
- Merge and PR authority must remain false (`taskctl.py:155-156`,
  `E_AUTHORITY`); all protected authority must remain false
  (`taskctl.py:157-158`, `E_PROTECTED_AUTHORITY`).

### 1.2 Recommendation — CLI signature

Add one subcommand path to the successor controller (exact flag spelling is
part of this recommendation and is reviewable):

```text
python -m panel_exp.execution.taskctl transition --to blocked \
  --rejected-head <40-lowercase-hex> \
  --rejected-implementation <40-lowercase-hex> \
  --blocker <nonempty-string> \
  [--live-main <40-lowercase-hex>]
```

- `--to blocked` selects the new edge. All other `--to` values keep existing
  behavior, including the current-task gate that only `ready_for_review` is
  available to this documentation task.
- `--rejected-head`: the exact remote review-ready head being rejected.
- `--rejected-implementation`: the implementation commit recorded in that
  review-ready state.
- `--blocker`: one durable human-readable blocker string (nonempty after
  strip). Repeatable (`--blocker` may be given more than once); each entry
  becomes one element of `blockers`.
- `--live-main`: optional observed `origin/main` SHA at rejection time. When
  omitted, the controller observes it via Git and records the observation in
  the rejection finding. When given, it must equal the observed value or the
  call fails stale (see 1.6, 4.10).

Python API recommendation (mirrors CLI, reviewable):

```python
transition(
    "blocked",
    *,
    rejected_head_sha: str,
    rejected_implementation_sha: str,
    blockers: list[str],
    live_main_sha: str | None = None,
) -> None
```

No other signature change is recommended. In particular, no `--complete-correction`,
`--implementation-sha`, approval, merge, or successor flags are added on this
path.

### 1.3 Recommendation — field, type, and invariant table

| Field | Type | Invariant |
|---|---|---|
| `repository` | `str` | Must equal `Phani-Pavuluri/panel_exp`, else `E_REJECTION_IDENTITY`. |
| `task_id` | `str` | Must equal the rejected task's canonical ID (historical: `GEOX_STRUCTURED_COMPLETION_EVIDENCE_001`), else `E_REJECTION_IDENTITY`. |
| `feature_branch` | `str` | Must equal the rejected task's branch (historical: `feat/geox-structured-completion-evidence-001`), valid per `BRANCH_RE`, never `main`, else `E_REJECTION_IDENTITY`. |
| pre-state `status` | `str` | Must be exactly `ready_for_review`, else `E_TRANSITION`. |
| pre-state `correction_cycles_remaining` | `int` | Must be exactly `0`, and `completed == maximum`, else `E_REJECTION_BUDGET`. Non-exhausted tasks must not use this route. |
| pre-state `correction_execution_authorized` | `bool` | Must be `false`, else `E_REJECTION_BUDGET`. |
| pre-state `blockers` | `list[str]` | Must be `[]` (review-ready invariant), else `E_REVIEW_EVIDENCE`. |
| pre-state `implementation_commit_sha` | `str \\| null` | Must be non-null valid SHA and must equal `--rejected-implementation`, else `E_REJECTION_IMPLEMENTATION`. |
| `--rejected-head` | `str` | Valid lowercase 40-hex (`SHA_RE`), else `E_SHA`. Must equal the independently observed exact remote head (1.6), else `E_REJECTION_HEAD`. |
| `--rejected-implementation` | `str` | Valid lowercase 40-hex, else `E_SHA`. Must equal recorded implementation and be an ancestor of `--rejected-head` (1.6), else `E_REJECTION_IMPLEMENTATION`. |
| `--blocker` entries | `list[str]` | Each nonempty after strip, at least one required, else `E_BLOCKERS`. |
| protected authority (all 13 keys) | `bool` | All `false` before and after; any `true` is `E_PROTECTED_AUTHORITY`. `merge_authorized` / `pr_creation_authorized` `false`, else `E_AUTHORITY`. |
| `review_decision` | `str` | Must equal `status` before and after (`blocked` after), else `E_REVIEW_DECISION`. |

### 1.4 Recommendation — stable error codes

Keep every existing `E_*` code byte-stable. Add exactly these new codes for
this route (reviewable spelling, stable once merged):

- `E_REJECTION_IDENTITY`: wrong repository, task, or branch triple.
- `E_REJECTION_HEAD`: rejected head is malformed, stale, or not the exact
  observed remote head.
- `E_REJECTION_IMPLEMENTATION`: implementation mismatch or not an ancestor of
  the rejected head.
- `E_REJECTION_BUDGET`: task is not exhausted (`remaining != 0`,
  `completed != maximum`, or correction authority still open).
- `E_REJECTION_EVIDENCE`: missing independent finding / resolution condition
  (see 2.4), or malformed `--blocker`.
- `E_STALE_MAIN`: live `origin/main` observation disagrees with `--live-main`
  or local `main != origin/main` at check time.
- `E_WRITE_ATOMICITY`: a multi-file write was interrupted or left divergent
  views; recovery is re-run of `check`/`sync` with no state advance (see 4.12).

`E_TRANSITION`, `E_TRANSITION_EVIDENCE`, `E_BLOCKED_EVIDENCE`,
`E_CORRECTION_COUNTERS`, `E_REJECTED_PROVENANCE`, `E_VIEW_DIVERGENCE`, and
`E_SHA` keep their current meanings and are reused where they already apply
(pre-state not `ready_for_review`, non-`blocked` targets on old controllers,
missing blockers, counter mutation, unpaired rejection provenance, divergent
views, malformed SHAs).

### 1.5 Recommendation — reviewer permissions

- Rejection is an **independent review act**, not an implementation act. The
  reviewer must be independent of the implementation author (current-task
  analogue: Muse-Spark implements, Codex reviews).
- The controller does not encode human identity beyond Git-observed evidence:
  the rejecting commit's author/committer, its parent (the exact rejected
  tree), and the recorded `--rejected-head` / `--rejected-implementation`
  pair constitute the permission evidence. No new capability flag is granted.
- `merge_authorized`, `pr_creation_authorized`, and all 13 protected-authority
  flags remain `false`. Rejection confers no merge, PR, correction, product,
  calibration, simulation, planning, recommendation, real-data, runtime,
  pilot, production, or next-task authority.
- Exact-head approval remains external: the blocked state is reviewable at its
  exact tree, but only a separately authorized successor may advance it. This
  contract authorizes no successor.

### 1.6 Recommendation — Git identity, ancestry, and head checks

All checks run **before any write**, in this order, failing closed on the
first mismatch with no state or view mutation (see section 4):

1. `repository`, `task_id`, `feature_branch` exact-match against canonical
   state; mismatch is `E_REJECTION_IDENTITY`.
2. Pre-state is `ready_for_review`, exhausted (`remaining == 0`,
   `completed == maximum`), correction authority closed, blockers empty;
   otherwise `E_TRANSITION` / `E_REJECTION_BUDGET` / `E_REVIEW_EVIDENCE`.
3. `--rejected-head` and `--rejected-implementation` match `SHA_RE`;
   otherwise `E_SHA`.
4. `--rejected-implementation` equals the state's recorded
   `implementation_commit_sha`; otherwise `E_REJECTION_IMPLEMENTATION`.
5. Observe the remote head: `git ls-remote origin
   refs/heads/<feature_branch>` must return exactly one line whose SHA equals
   `--rejected-head`; `git cat-file -t <rejected-head>` must succeed as
   `commit`. Any disagreement is `E_REJECTION_HEAD`. The historical branch is
   read-only: no fetch-mutation, merge, rebase, cherry-pick, deletion, or
   push is performed against it.
6. Ancestry: `git merge-base --is-ancestor <rejected-implementation>
   <rejected-head>` must succeed; otherwise `E_REJECTION_IMPLEMENTATION`.
7. Liveness: `git rev-parse main` and `git rev-parse origin/main` must agree
   (after `git fetch --prune origin`); if `--live-main` was supplied it must
   equal that value. Disagreement is `E_STALE_MAIN`. The observed live main is
   recorded as evidence; it is not required to equal any historical base.
8. Protected authority re-verified false; otherwise `E_PROTECTED_AUTHORITY` /
   `E_AUTHORITY`.

Rejection applies **only** to an exhausted review-ready exact remote head.
Any other head — including a newer push to the same branch, a local-only
commit, or a prefix abbreviation — is `E_REJECTION_HEAD`.

---

## 2. Canonical blocked outcome

### 2.1 Approved principle

`blocked` means execution authority held plus at least one durable explicit
blocker (`taskctl.py:165-166`). `ready_for_review` means implementation
present, no blockers, correction closed (`taskctl.py:172-174`).

### 2.2 Recommendation — deterministic post-state

On success the successor controller writes exactly this transition
(`ready_for_review` to `blocked`), changing only these fields:

- `status`: `ready_for_review` to `blocked`.
- `review_decision`: `ready_for_review` to `blocked` (must match `status`).
- `blockers`: `[]` to the ordered `--blocker` list (duplicates removed,
  order preserved; at least one remains).
- `rejected_review_head_sha`: `null` to `--rejected-head` (historical:
  `81664df0d687746a8ee990eada702a2a54cc23c0`).
- `rejected_implementation_commit_sha`: `null` to `--rejected-implementation`
  (historical: `3841c1790d82d94ebdb99dc6a4022b3c4097c86d`).
- Review metadata (timestamps, observed live main, reviewer commit
  reference) recorded in existing free-form evidence fields only; no new
  persisted-schema field beyond the already-defined rejected pair.

Everything else is byte-identical, specifically:

- `correction_cycles_completed`, `correction_cycles_remaining`
  (`1`/`0` historical), and `maximum_correction_cycles` are **unchanged**.
  No extra correction is consumed, granted, or refunded.
- `implementation_commit_sha` is unchanged (historical:
  `3841c1790d82d94ebdb99dc6a4022b3c4097c86d`).
- `task_execution_authorized` stays `true`; `correction_execution_authorized`
  stays `false`; `merge_authorized`, `pr_creation_authorized`, and all 13
  protected-authority flags stay `false`.
- `completion_evidence` (v4 states) is preserved byte-for-byte; it is neither
  regenerated nor revalidated beyond the existing late-lifecycle gate.
- `reviewed_head_sha`, `approval_commit_sha` stay `null`; cleanup markers stay
  `null`.

### 2.3 Recommendation — lineage preservation

- The rejected pair (`rejected_review_head_sha`,
  `rejected_implementation_commit_sha`) is the sole lineage record of the
  independent rejection. It must satisfy the existing pairing invariant (both
  null or both SHAs; after rejection both SHAs).
- The pre-rejection review-ready head is never rewritten: the historical
  branch `feat/geox-structured-completion-evidence-001` at
  `81664df0d687746a8ee990eada702a2a54cc23c0` remains immutable and unapproved.
- The rejecting commit's parent chain proves ancestry from the synchronized
  authorizing main; the receipt records implementation parent, exact-tree
  gate, and evidence source (see current-task publication protocol in
  `ACTIVE_TASK.md`).

### 2.4 Recommendation — durable blocker, findings, resolution condition

The first `--blocker` entry must be durable (still true on re-check), of the
form:

```text
Independent rejection of exhausted review-ready <remote-head>: <reason>;
implementation <impl-sha>; no correction budget remains (completed <n> of <m>);
re-review requires separately authorized recovery; no merge or successor authorized.
```

Historical recommendation:

```text
Independent rejection of exhausted review-ready
81664df0d687746a8ee990eada702a2a54cc23c0: malformed non-null completion
evidence passes early-lifecycle validation and can crash rendering (25 focused
tests pass; controller rejects both exhausted routes); implementation
3841c1790d82d94ebdb99dc6a4022b3c4097c86d; no correction budget remains
(completed 1 of 1); re-review requires separately authorized recovery; no
merge or successor authorized.
```

Independent findings preserved (not fixed by this route): (a) malformed
non-null completion evidence passes early-lifecycle v4 validation and can
crash `render()` with uncaught `KeyError`/`TypeError` instead of
`E_COMPLETION_EVIDENCE_*`; (b) 25 focused tests pass on the exhausted head
(`tests/execution/test_taskctl.py` 22 plus
`tests/test_repo_native_execution_handoff.py` 3); (c) the v3 and v4
controllers reject both exhausted rejection paths (`E_TRANSITION` direct,
`E_TRANSITION_EVIDENCE` via correction).

Live resolution condition (recorded alongside, not auto-evaluated): "Design
the approved exhausted-review rejection route first; old branch remains
immutable and unapproved. Separate implementation and completion recovery
require fresh Git authorization." — the dependency resolution condition
already recorded in the current-task state
(`EXECUTION_STATE.json: dependencies[0]`).

No extra correction, merge, or product authority follows from the blocked
outcome.

---

## 3. Compatibility and migration from schema v3 and unmerged v4

### 3.1 Approved principle

- Current main persists schema `geox_repo_execution_state_v3` with no
  `completion_evidence` key (`taskctl.py:20`,
  `docs/execution/EXECUTION_STATE.json:2`).
- The unmerged historical branch persists schema
  `geox_repo_execution_state_v4` with required `completion_evidence` for
  `ready_for_review` / `changes_requested` / `merged`, fully generated
  completion reports, and identical `TRANSITIONS` (no `ready_for_review` to
  `blocked` edge).
- This documentation task performs no runtime or persisted-schema migration;
  migration design is the deliverable (`ACTIVE_TASK.md`).

### 3.2 Recommendation — version and acceptance

- The successor controller introduces schema `geox_repo_execution_state_v5`
  (exact version label reviewable; `v4.1` is an acceptable alternative if the
  owner prefers patch lineage). `v5` equals `v4` plus exactly: (a) the new
  `ready_for_review` to `blocked` edge, (b) the section-1 exhausted-rejection
  validation, (c) atomic blocked-view rendering. No other semantic change.
- `v5` `validate_state()` must accept both `v3`-shaped states (no
  `completion_evidence` key, for pre-evidence tasks) and `v4`-shaped states
  (evidence required for late lifecycle) during a read-only migration window,
  then persist `v5` on first authorized write. It must never silently drop,
  default, or regenerate `completion_evidence`.
- The known v4 early-lifecycle evidence gap (malformed non-null evidence
  passing `authorized`/`in_progress`/`blocked` validation, crashing
  `render()`) is **not** fixed by this route; it is owned by the separate
  completion-evidence recovery successor (section 5). The v5 controller must
  preserve that finding byte-for-byte and must not widen `render()` to accept
  malformed evidence.

### 3.3 Recommendation — how historical rejection is recorded without editing history or bypassing controls

- The immutable historical branch
  (`feat/geox-structured-completion-evidence-001` at `81664df…`) is **never**
  written: no merge, rebase, cherry-pick, deletion, extra correction, or
  execution from it (`ACTIVE_TASK.md`).
- **Authoritative write target:** the live canonical
  `docs/execution/EXECUTION_STATE.json` of the task being rejected, as carried
  forward on a **freshly Git-authorized recovery branch** taken from
  synchronized post-v5 main — not the historical branch, not main directly.
  Until such a recovery task is separately authorized, the rejection exists
  only as external review evidence (this contract plus the reviewer's blocked
  finding); no controller writes it anywhere.
- **Historic-task identity** pinned on every write: `(repository
  Phani-Pavuluri/panel_exp, task_id
  GEOX_STRUCTURED_COMPLETION_EVIDENCE_001, feature_branch
  feat/geox-structured-completion-evidence-001, remote_head
  81664df0d687746a8ee990eada702a2a54cc23c0, implementation
  3841c1790d82d94ebdb99dc6a4022b3c4097c86d)`. The v5 controller refuses the
  transition when the live state's triple disagrees (`E_REJECTION_IDENTITY`),
  when the recorded implementation disagrees
  (`E_REJECTION_IMPLEMENTATION`), or when the observed remote head has moved
  (`E_REJECTION_HEAD`).
- Rejected alternatives (not recommended): an append-only
  `HISTORICAL_REJECTIONS.json` log (bypasses lifecycle controls and view
  determinism); rewriting main's `EXECUTION_STATE.json` in place for a
  different `task_id` (confuses task identity); force-pushing or
  cherry-picking onto the historical branch (violates immutability).
- No implicit successor execution: recording the blocked outcome does not
  authorize implementation, completion-evidence recovery, role adoption, or
  any next task (`next_task_authorized` remains `false`; all protected
  authority remains `false`).

---

## 4. Failure semantics, consistency, recovery, and acceptance cases

### 4.1 Approved principle

- `transition()` calls `check()` first; divergent views fail with
  `E_VIEW_DIVERGENCE` before any mutation (`taskctl.py:269`).
- Candidate states are validated before any atomic write
  (`taskctl.py:292`); writes are atomic via temporary file plus
  `os.replace` (`taskctl.py:226-239`).

### 4.2 Recommendation — no writes on invalid or stale input

The successor `transition --to blocked` path must: (1) `load_state()` and
`check()`; (2) run every section-1.6 check against Git-observed values; (3)
build the candidate in memory and `validate_state()` it; (4) only then
atomically write `EXECUTION_STATE.json`, `ACTIVE_TASK.md`, and
`LATEST_COMPLETION_REPORT.md`. Any failure in steps 1–3 leaves all three
files byte-identical. Partial writes are never left behind; an interrupted
step-4 write is detected as `E_VIEW_DIVERGENCE` / `E_WRITE_ATOMICITY` on the
next `check()` and recovered by re-running the same command after verifying
Git state (no auto-repair, no state advance on recovery).

### 4.3 Recommendation — multi-file consistency and deterministic views

- The three files advance together or not at all. Generated marker blocks are
  the sole controller-owned regions; human-authored sections outside markers
  are preserved byte-for-byte via `replace_view()` (v3 behavior) or the v4
  fully-generated report path, as applicable to the state's schema.
- `render(state, "active_task")` and `render(state, "completion_report")` are
  pure functions of canonical state plus preserved human sections; the same
  blocked state always renders the same blocks, including the rejected pair,
  unchanged counters, and ordered blockers.

### 4.4 Named acceptance cases

Each case names the expected stable code and the no-write guarantee. Cases
AC-1–AC-9 are negative (no file may change); AC-10 is positive; AC-11 covers
interruption; AC-12 covers determinism.

- **AC-1 wrong repository:** state `repository` is not
  `Phani-Pavuluri/panel_exp` (or a tampered copy claims another repo).
  Expect `E_STATE_REPOSITORY` (load) or `E_REJECTION_IDENTITY` (transition).
  No writes.
- **AC-2 wrong task:** `task_id` mismatch between state and
  `--rejected-head` provenance (e.g. presenting the contract task's ID for
  the historical head). Expect `E_REJECTION_IDENTITY`. No writes.
- **AC-3 wrong branch:** `feature_branch` mismatch (e.g. the contract-task
  branch `docs/geox-exhausted-review-route-contract-001` presented for the
  historical head). Expect `E_REJECTION_IDENTITY`. No writes.
- **AC-4 wrong head:** `--rejected-head` is well-formed but unequal to `git
  ls-remote origin refs/heads/<branch>`, or names a non-commit, or is a
  prefix. Expect `E_REJECTION_HEAD`. No writes. Includes the moved-branch
  sub-case: remote advanced past `81664df…` after observation.
- **AC-5 wrong implementation:** `--rejected-implementation` unequal to the
  recorded `implementation_commit_sha`, or not an ancestor of
  `--rejected-head` per `git merge-base --is-ancestor`. Expect
  `E_REJECTION_IMPLEMENTATION`. No writes. Historical positive control:
  `3841c17…` is an ancestor of `81664df…`.
- **AC-6 remaining budget:** pre-state has `correction_cycles_remaining > 0`
  or `correction_execution_authorized == true` (non-exhausted). Expect
  `E_REJECTION_BUDGET`. No writes. Rationale: non-exhausted rejection must
  use the existing correction path, not this route.
- **AC-7 missing evidence:** no `--blocker` given, any `--blocker` blank, or
  (v4 states) `completion_evidence` failing the existing
  `_validate_completion_evidence` gate. Expect `E_REJECTION_EVIDENCE` (blocker
  case) or the existing `E_COMPLETION_EVIDENCE_*` code (evidence case). No
  writes.
- **AC-8 protected flags:** any protected-authority flag, `merge_authorized`,
  or `pr_creation_authorized` true before the call, or any attempt to flip one
  in the candidate. Expect `E_PROTECTED_AUTHORITY` / `E_AUTHORITY`. No writes.
- **AC-9 stale main:** `git rev-parse main != git rev-parse origin/main` at
  check time, or `--live-main` disagrees with observed `origin/main`. Expect
  `E_STALE_MAIN`. No writes.
- **AC-10 success:** exhausted `ready_for_review` (`1/1/0`),
  `--rejected-head 81664df0d687746a8ee990eada702a2a54cc23c0`,
  `--rejected-implementation 3841c1790d82d94ebdb99dc6a4022b3c4097c86d`,
  one durable `--blocker`, synchronized main. Expect exit 0; post-state is
  exactly section 2.2; `taskctl check`, `json.tool`, and `git diff --check`
  pass; counters unchanged; protected authority all false.
- **AC-11 interrupted write:** kill or crash between the state write and view
  writes (simulated by truncating one view). Next `taskctl check` must report
  `E_VIEW_DIVERGENCE` (or `E_WRITE_ATOMICITY`), change nothing, and succeed
  after the operator re-runs the identical rejected command on verified Git
  state. No state advance on the failed attempt.
- **AC-12 deterministic views:** rendering the AC-10 post-state twice yields
  byte-identical `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md` blocks;
  `sync()` is idempotent.

---

## 5. Successors, resolved recommendations, and owner-reserved ambiguity

### 5.1 Approved principle

Controller implementation, completion-evidence recovery, and role adoption are
separate successors. This task does not execute rejection or authorize a
successor (`ACTIVE_TASK.md`). All protected authority remains false; the three
unrelated defect IDs (`GEOX-CURRENT-MAIN-BRB-GOLDEN-EQUIVALENCE-001`,
`GEOX-CURRENT-MAIN-DESIGN-VALIDATION-CALLBACK-INJECTION-001`,
`GEOX-CURRENT-MAIN-DESIGN-TIER1-CONTRACT-EMISSION-001`) remain unresolved.
Affected/modified repository is GeoX only; MIP and MMM are read-only context.

### 5.2 Recommendation — three separate successors (no implicit execution)

1. **Controller implementation successor:** implements sections 1–4 in a new
   `taskctl.py` plus focused `transition --to blocked` tests (negative cases
   AC-1–AC-9, positive AC-10, interruption AC-11, determinism AC-12). Must not
   bundle evidence recovery or role changes. Merges only via exact-head
   external approval and fast-forward.
2. **Completion-evidence recovery successor:** owns the v4 early-lifecycle
   `_validate_completion_evidence` gap and `render()` crash hardening
   (fail-closed `E_COMPLETION_EVIDENCE_*` on every lifecycle state, or
   total `render()` validation — owner's choice). Must not smuggle in the
   blocked route or new authority.
3. **Role-adoption successor:** owns reviewer/worker role wiring (cf. MMM
   worker/reviewer merge at `6f60cd2896d56f67675c7eb94e23f6e9f6ef36a8`),
   independent-reviewer permission plumbing, and any identity evidencing
   beyond Git-observed SHAs. Must not change lifecycle semantics.

Technical recommendations resolved here (reviewable): direct
`ready_for_review → blocked` edge (not via `changes_requested`); exhausted-only
guard (`remaining == 0`, `completed == maximum`, correction closed);
unchanged counters; paired rejected lineage; remote-head + ancestry checks;
`E_REJECTION_*` / `E_STALE_MAIN` / `E_WRITE_ATOMICITY` codes; v5-equals-v4-plus-route
migration; fresh-recovery-branch write target; durable-blocker wording.

### 5.3 Owner-reserved ambiguity (explicitly not decided here)

- Exact successor schema label (`geox_repo_execution_state_v5` vs `v4.1`) and
  migration-window duration.
- Exact CLI flag spelling (`--rejected-head` / `--blocker` / `--live-main`)
  and whether `--blocker` repeatability or a `--blockers-file` is preferred.
- Whether the recovery branch for the historical task reuses
  `feat/geox-structured-completion-evidence-001` naming lineage (new suffix)
  or takes a fresh `feat/` name, and who authorizes it.
- Whether observed live-main becomes a required persisted field or stays
  finding evidence.
- Whether reviewer independence is evidenced purely by Git commit identity or
  additionally by forge (GitHub) identity.
- Whether any append-only historical-rejection index is ever permitted
  alongside (not instead of) canonical state.
- Any new capability, policy, product eligibility, or consumer-verification
  commitment: none is chosen here; all require explicit owner authorization.

No new capability or policy is silently adopted by this document.

---

## Appendix A — Evidence pins and references

- Current controller: `panel_exp/execution/taskctl.py` (v3, 323 lines);
  `STATES`/`TRANSITIONS` lines 21–44; `transition()` lines 262–296;
  `validate_state()` lines 110–179; `render()`/`replace_view()`/
  `_candidate_views()`/`sync()`/`check()` lines 182–259.
- Historical controller: `81664df:panel_exp/execution/taskctl.py`
  (`SCHEMA_VERSION = "geox_repo_execution_state_v4"`,
  `COMPLETION_EVIDENCE_KEYS`, `_validate_completion_evidence`,
  late-lifecycle-only evidence gate, evidence `render()` block,
  fully-generated report); identical `TRANSITIONS` and identical
  `only review-ready completion` gate.
- Historical state: `81664df:docs/execution/EXECUTION_STATE.json`
  (`GEOX_STRUCTURED_COMPLETION_EVIDENCE_001`, `ready_for_review`, `1/1/0`,
  implementation `3841c17…`, rejected pair from `61c4e7d`/`0d251c2` lineage,
  25-entry validation evidence).
- Current state: `docs/execution/EXECUTION_STATE.json`
  (`GEOX_EXHAUSTED_REVIEW_ROUTE_CONTRACT_001`, `authorized`, base
  `496c317…`, authorization `41972b…`, dependency
  `DEP-GEOX-EXHAUSTED-REJECTED-EVIDENCE-001`, source defect
  `GEOX-EXHAUSTED-REVIEW-ROUTE-GAP-001`, recurrence evidence for
  `GEOX_TASKCTL_CORRECTION_FIXTURE_BASELINE_REPAIR_001` at `1c3a2b0…` and
  `GEOX_CURRENT_MAIN_HANDOFF_STATUS_PARSER_RECOVERY_001` at `b97d75a…`).
- Failing invariant: "An exhausted independently rejected review has no
  supported canonical blocked transition."
  (`EXECUTION_STATE.json: source_defect.failing_invariant`).
- Focused tests: `tests/execution/test_taskctl.py` (10 tests on main, 14
  function-level / 22 with parametrization on the historical branch) and
  `tests/test_repo_native_execution_handoff.py` (3 tests); historical combined
  evidence 25 passed.
- This task's gate (documentation scope): `taskctl check`, `json.tool` on
  `EXECUTION_STATE.json`, `git diff --check`, authorization-baseline diff
  limited to the four owned paths, and section references for all five
  acceptance items. Docker, analytical tests, Ruff, and mypy are
  not-required; no tests mirroring document text are added.
