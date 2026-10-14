# Exhausted Review Route Contract (recovery)

**Task:** `GEOX_EXHAUSTED_REVIEW_ROUTE_CONTRACT_RECOVERY_001`
**Status:** Recommended definition-ready governance contract. Not implemented.
**Scope:** Documentation only. No controller implementation, rejection execution,
correction, merge, or successor is authorized by this document. Muse-Spark owns
the recommendation and supporting investigation; Codex independently reviews it.
This is a replacement document: it resolves the six independent-review findings
against the prior draft rather than amending that draft's text.

**Reading rule:** Paragraphs marked **Approved principle** restate owner-approved
process constraints from `docs/execution/ACTIVE_TASK.md`,
`docs/execution/EXECUTION_STATE.json`, and the repository-native controller
`panel_exp/execution/taskctl.py`. Paragraphs marked **Recommendation** are
definite technical decisions proposed for review. This document leaves no
alternatives open for implementation to choose; where a choice exists it is made
here, and any substantive disagreement is recorded as a limitation (§5.5).

**Historical target (immutable evidence):** task
`GEOX_STRUCTURED_COMPLETION_EVIDENCE_001`, branch
`feat/geox-structured-completion-evidence-001`, exact remote review head
`81664df0d687746a8ee990eada702a2a54cc23c0`, implementation
`3841c1790d82d94ebdb99dc6a4022b3c4097c86d`, authorization
`55c4c6c237642195732d949d034e98763c5d8cac`, base
`a78c4017e06c6f0bfb4329e749972b516dfbc7e9`. Blob read 2026-10-14 via
`git show 81664df…:docs/execution/EXECUTION_STATE.json`: status
`ready_for_review`, schema `geox_repo_execution_state_v4`, counters 1 maximum /
1 completed / 0 remaining, correction authority closed, blockers empty, prior
rejected pair `61c4e7d2100cdf79bd1687598e5e410bbc450e62` /
`0d251c22bbfb41ab57c830b89f291464de2e1fa5`, `completion_evidence` present.
`git ls-remote` still returns exactly `81664df…` for the branch;
`git merge-base --is-ancestor 3841c17… 81664df…` holds. The head remains
unapproved and the branch is never written.

**Prior draft (immutable rejected evidence):** branch
`docs/geox-exhausted-review-route-contract-001`, remote head
`cf743b8a0ac858a56997b41b1362f5be6d480a92` (verified unchanged via
`git ls-remote`), implementation `6217e0686041b7c3fa154ccab6ae5bcb36e57946`,
review decision `reject_for_contract_inconsistency` recorded in pushed
`refs/notes/codex-supervised-reviews`. It is evidence only: not a baseline, not
an approved contract, not to be merged, rebased, cherry-picked, or executed
from.

**Current-task provenance (Git-observed):** base
`3dc762d1a7937c3b1872591cc380f3aa0edeb68c`, task-authoring and authorization
head `a9677d5bf1c699434fc6d6536209718f988eb876`, post-authoring main
`3eda8e5057a1162989bd1020c12e335476b73669`, feature branch
`docs/geox-exhausted-review-route-contract-recovery-001`. Live overlay
2026-10-14: GeoX main `496c317bc44c31a89aff805896863bd7eb637b7e`; MIP main
`c7215b9c2afe38bbe2191c03cd89a114ea82d9c4`; MMM main
`6f60cd2896d56f67675c7eb94e23f6e9f6ef36a8`. Preserved historical pins: GeoX
`a78c4017e06c6f0bfb4329e749972b516dfbc7e9`, MIP
`a293ce52a813709ca624332123019139928cc51e`, MMM
`fe8e784923994406a2e4907d28debd872d61fd73`.

**Recommendation summary:** The successor controller records an exhausted
historical rejection as one appended `rejection_history` entry on a freshly
authorized live recording task, read from the exact remote target blob under a
three-way agreement (CLI inputs, blob contents, observed remote), with the live
task's own identity, budget, and lifecycle fields untouched. The route is direct
recording-to-`blocked`; exhausted rejection is never routed through
`changes_requested`.

---

## 1. Interface — signatures, model, fields, codes, permissions, Git checks

### 1.1 Approved principle

- Execution mode is `branch_and_fast_forward` on base branch `main`
  (`panel_exp/execution/taskctl.py:129-131`).
- The v3 controller's `transition()` executes only `--to ready_for_review`
  (`taskctl.py:274-275`, `E_TRANSITION_EVIDENCE`); its `TRANSITIONS` table
  (`taskctl.py:34-44`) permits `authorized/in_progress/changes_requested` to
  `blocked` but has no `ready_for_review` to `blocked` edge, and no CLI path
  executes those `blocked` edges at all.
- `blocked` requires execution authority plus explicit blockers
  (`taskctl.py:165-166`); `ready_for_review` requires implementation, no
  blockers, closed correction authority (`taskctl.py:172-174`); counters must
  satisfy completed plus remaining equals maximum (`taskctl.py:148-152`); the
  rejected pair must be jointly null or jointly SHAs (`taskctl.py:159-161`).
- Merge/PR authority must stay false (`taskctl.py:155-156`); all protected
  authority must stay false (`taskctl.py:157-158`); `review_decision` must equal
  `status` (`taskctl.py:133-134`).
- Writes are per-file atomic via temporary file plus `os.replace`
  (`taskctl.py:226-239`); `transition()` runs `check()` before any mutation and
  validates the in-memory candidate before writing (`taskctl.py:269,292).

### 1.2 Recommendation — CLI signature (decided)

```text
python -m panel_exp.execution.taskctl transition --to blocked \
  --rejected-head <40-lowercase-hex> \
  --rejected-implementation <40-lowercase-hex> \
  --blocker <nonempty-string> [--blocker <nonempty-string> ...] \
  --finding <nonempty-string> \
  --resolution-condition <nonempty-string> \
  [--live-main <40-lowercase-hex>]
```

- `--rejected-head`: the exact remote review-ready head being recorded as
  rejected. `--rejected-implementation`: the implementation it records, cross-checked
  against the blob (not trusted on its own).
- `--blocker`: one durable blocker string per flag; at least one required; the
  ordered deduplicated list becomes live `blockers`.
- `--finding`: the independent technical finding (required; §2.4). A blocker
  alone is not evidence — finding and resolution are separate inputs because
  neither can be inferred from an arbitrary blocker string.
- `--resolution-condition`: the live resolution condition (required; §2.4).
- `--live-main`: optional observed `origin/main`; when given it must equal the
  controller's own observation or the call fails stale (§4.10); the observed
  value is always persisted in the record (§1.5).

Python API mirror (decided): `transition("blocked", *,
rejected_head_sha: str, rejected_implementation_sha: str, blockers: list[str],
finding: str, resolution_condition: str, live_main_sha: str | None = None)`.
No other flags exist on this path: no correction, approval, merge, or successor
inputs.

### 1.3 Recommendation — the one input/read/write model (decided)

There is exactly one model. Inputs are CLI args. Reads come from three mutually
independent sources plus the recording task's own authorization. Writes go to
exactly one authoritative file plus its two derived views.

- **Inputs:** the six CLI values in §1.2.
- **Read 1 — target blob:** `git show <rejected-head>:docs/execution/EXECUTION_STATE.json`,
  parsed as JSON. This read is authoritative for the *target's* identity and
  budget: `task_id`, `feature_branch`, `implementation_commit_sha`,
  `maximum/correction_cycles_completed/remaining`, `correction_execution_authorized`,
  `task_execution_authorized`, `blockers`, and the blob's own rejected pair
  (carried as prior lineage, §2.3). Target facts are never taken from the live
  state's fields — comparing the live state to itself would be tautological.
- **Read 2 — observed remote:** `git ls-remote origin
  refs/heads/<blob feature_branch>` must return exactly one line equal to
  `--rejected-head`; `git cat-file -t <rejected-head>` must be `commit`;
  `git merge-base --is-ancestor <blob implementation> <rejected-head>` must
  hold.
- **Read 3 — live observation:** after `git fetch --prune origin`,
  `git rev-parse main` must equal `git rev-parse origin/main`; that value is the
  observed live main.
- **Read 4 — recording-task authorization:** the live state's own
  `repository/task_id/feature_branch`, its dependency pin naming the expected
  historical triple (pattern: `DEP-…` entries as in the current-task state),
  and its pre-status/authority/counters.
- **Agreement rule:** `--rejected-implementation` must equal the blob's
  `implementation_commit_sha`; `--rejected-head` must equal the observed remote
  head for the blob's branch; the blob's `(task_id, feature_branch)` must equal
  the dependency-pinned expectation. Four sources, pairwise agreement, no
  self-comparison.
- **Write target:** the live recording task's own
  `docs/execution/EXECUTION_STATE.json` on its freshly authorized branch — never
  the historical branch, never main directly, never another task's file. Then
  the two views re-render from the new state (§4.2).

### 1.4 Recommendation — canonical record fields (decided, complete)

Top-level addition, required on every v5 state, possibly empty:

- `rejection_history`: `list[RejectionRecord]`, `[]` when nothing has been
  recorded. Migration from v3 persists `[]`; the key is required, never null.

`RejectionRecord` — every field required, no extras:

| Field | Type | Value rule |
|---|---|---|
| `target_task_id` | `str` | Equals blob `task_id` and the dependency-pinned expectation (historical: `GEOX_STRUCTURED_COMPLETION_EVIDENCE_001`), else `E_REJECTION_IDENTITY`. |
| `target_branch` | `str` | Equals blob `feature_branch` and the pinned expectation (historical: `feat/geox-structured-completion-evidence-001`), else `E_REJECTION_IDENTITY`. |
| `target_head_sha` | `str` | Lowercase 40-hex equal to CLI, blob commit, and observed remote head (historical: `81664df…`), else `E_SHA` / `E_REJECTION_HEAD`. |
| `target_implementation_sha` | `str` | Lowercase 40-hex equal to CLI and blob `implementation_commit_sha`, ancestor of head (historical: `3841c17…`), else `E_SHA` / `E_REJECTION_IMPLEMENTATION`. |
| `target_counters` | `{maximum: int, completed: int, remaining: int}` | Equal to blob counters with `remaining == 0` and `completed == maximum` (historical: `1/1/0`), else `E_REJECTION_BUDGET`. Non-negative integers summing correctly, else `E_CORRECTION_COUNTERS`. |
| `prior_rejected_review_head_sha` | `SHA \\| null` | Equals blob `rejected_review_head_sha` (historical: `61c4e7d…`), null iff blob pair null. Pairing with the next field enforced, else `E_REJECTED_PROVENANCE`. |
| `prior_rejected_implementation_commit_sha` | `SHA \\| null` | Equals blob `rejected_implementation_commit_sha` (historical: `0d251c2…`), null iff blob pair null. |
| `finding` | `str` | Nonempty after strip, names both rejected SHAs, else `E_REJECTION_EVIDENCE`. |
| `resolution_condition` | `str` | Nonempty after strip, else `E_REJECTION_EVIDENCE`. |
| `live_main_sha` | `str` | Lowercase 40-hex equal to observed `origin/main`, else `E_SHA` / `E_STALE_MAIN`. Persisted field (decided), not evidence-only prose. |
| `blockers` | `list[str]` | Ordered deduplicated `--blocker` list, at least one nonempty entry, equal to live post `blockers`, else `E_BLOCKERS`. |

Live-field invariants on this path: pre-status is one of `in_progress`,
`changes_requested` (existing edges, newly CLI-executable) or `ready_for_review`
(new edge); `task_execution_authorized` true; live `blockers == []`;
`correction_execution_authorized` false; protected authority, merge, and PR flags
false before and after. Live counters are byte-identical after (this path
consumes no budget on either side). Live top-level `rejected_review_head_sha` /
`rejected_implementation_commit_sha` are untouched — they track the live task's
own rejection events, a different fact from the recorded historical one, and
reusing them would overwrite unrelated lifecycle fields. `approval_commit_sha`
stays null: this path never approves, and no approval metadata commit is
permitted before external exact-head approval.

### 1.5 Recommendation — stable error codes (decided)

All existing `E_*` codes keep byte-stable meanings. Deterministic mapping rule:
**lexical/shape failures use existing codes; semantic/identity failures use new
codes.** `E_SHA` for non-hex SHAs; `E_BLOCKERS` for empty or blank blocker
lists. `E_REJECTION_HEAD` only for well-formed-but-wrong heads (remote
disagreement, non-commit, prefix); `E_REJECTION_EVIDENCE` only for missing
finding/resolution or a finding that does not name both SHAs. Remaining codes:
`E_REJECTION_IDENTITY` (repository/target-triple vs blob/pin mismatch),
`E_REJECTION_IMPLEMENTATION` (implementation vs blob/ancestry mismatch),
`E_REJECTION_BUDGET` (target blob not exhausted or correction still open),
`E_STALE_MAIN` (local/remote main disagreement or `--live-main` mismatch),
`E_WRITE_ATOMICITY` (torn single-file state only, §4.3). Existing
`E_TRANSITION`, `E_BLOCKED_EVIDENCE`, `E_CORRECTION_COUNTERS`,
`E_REJECTED_PROVENANCE`, `E_VIEW_DIVERGENCE`, `E_PROTECTED_AUTHORITY`,
`E_AUTHORITY`, `E_REVIEW_DECISION` are reused where they already apply.

### 1.6 Recommendation — reviewer permissions and independence limits

- Recording is a review act, not an implementation act; the reviewer must be
  independent of the implementation author (current-task analogue: Muse-Spark
  implements, Codex reviews; no overlapping writer is authorized).
- Stated limitation: shared Git identity does not evidence independent agents.
  Both prior-draft commits carry the same owner identity, and any successor
  commits will too. Independence rests on role-separated sessions with separate
  evidence chains, the no-overlapping-writer discipline, the structured
  finding/resolution record, and external exact-head owner approval — never on
  commit author/committer strings, which the controller does not interpret.
- This path confers no merge, PR, correction, product, calibration, simulation,
  planning, recommendation, real-data, runtime, pilot, production, or next-task
  authority. All such flags remain false.

### 1.7 Recommendation — ordered Git checks (all before any write)

1. Load live state; `check()` views — divergence is `E_VIEW_DIVERGENCE`, no
   writes. 2. Live triple exact-match plus pre-status/authority/emptiness —
   else identity/transition/evidence codes. 3. SHAs match `SHA_RE` — else
   `E_SHA`. 4. Read target blob; blob triple equals pinned expectation — else
   `E_REJECTION_IDENTITY`. 5. CLI implementation equals blob implementation —
   else `E_REJECTION_IMPLEMENTATION`. 6. Remote head equals CLI head,
   commit-typed, ancestry holds — else `E_REJECTION_HEAD` /
   `E_REJECTION_IMPLEMENTATION`. 7. Blob counters exhausted and correction
   closed — else `E_REJECTION_BUDGET`. 8. Finding/resolution/blockers valid —
   else `E_REJECTION_EVIDENCE` / `E_BLOCKERS`. 9. Liveness observation (and
   `--live-main` agreement) — else `E_STALE_MAIN`. 10. History membership: the
   `(head, implementation)` pair already recorded is `E_TRANSITION` (already
   applied — recover via `sync`, never re-append). Only then build, validate,
   and write the candidate.

---

## 2. Canonical blocked outcome

### 2.1 Approved principle

`blocked` means execution authority held plus durable explicit blockers
(`taskctl.py:165-166`); the live recording task's own lifecycle rules continue
to apply to its own fields throughout.

### 2.2 Recommendation — deterministic post-state (decided)

From an eligible pre-status the successor controller writes exactly:

- `status` and `review_decision`: to `blocked` (equal to each other).
- `blockers`: `[]` to the ordered deduplicated `--blocker` list.
- `rejection_history`: plus exactly one entry built per §1.4.

Every other persisted value is byte-identical: live counters (this recovery-task
pattern: 1/0/1 stays 1/0/1), live top-level rejected pair (null/null stays
null/null), `implementation_commit_sha`, `approval_commit_sha` (null),
protected/merge/PR/next-task flags (false), `completion_evidence` absence (v5
has no such key), and all provenance SHAs.

### 2.3 Recommendation — lineage without overwriting (decided)

The blob's prior rejected pair (`61c4e7d…` / `0d251c2…`) is carried into the new
entry's `prior_*` fields — the first correction cycle's lineage is preserved
inside the record, and the new rejection is appended after it. History is
append-only by construction (`post.history == pre.history + [entry]`, enforced
in the transition function; procedural diff review covers out-of-band edits).
The live top-level rejected fields are not projections, aliases, or copies of
historical data and are never assigned on this path.

### 2.4 Recommendation — durable blocker, finding, resolution (decided)

Historical entry content:

- Blocker: `Independent rejection of exhausted review-ready
  81664df0d687746a8ee990eada702a2a54cc23c0 (implementation
  3841c1790d82d94ebdb99dc6a4022b3c4097c86d): no canonical blocked transition
  exists; no correction budget remains (completed 1 of 1); re-review requires
  separately authorized recovery; no merge or successor authorized.`
- Finding: names both SHAs and states the reproduced defect — malformed
  non-null completion evidence passes early-lifecycle v4 validation and can
  crash `render()` with uncaught errors instead of fail-closed codes; the v3
  and v4 controllers reject both exhausted rejection paths; 25 focused tests
  pass on the exhausted head.
- Resolution condition: `Design the approved exhausted-review rejection route
  first; old branch remains immutable and unapproved. Separate implementation
  and completion recovery require fresh Git authorization.`

### 2.5 Target budget versus live budget (decided)

The exhausted guard reads only the target blob (`remaining == 0`,
`completed == maximum`, blob correction closed). The live recording task's own
budget is a separate fact in its own counters and is never incremented,
decremented, refunded, or gated by this path. Concretely: target `1/1/0` and
live `1/0/1` coexist — one inside the new history entry's `target_counters`,
one in top-level counters — with neither derived from the other.

### 2.6 No authority follows

Recording confers no extra correction, merge, or product authority (§1.6). The
three unrelated defect IDs remain unresolved; no consumer verification or
product eligibility follows.

---

## 3. Compatibility and migration from schema v3 and unmerged v4

### 3.1 Approved principle

- Current main persists `geox_repo_execution_state_v3` with no
  `completion_evidence` key (`taskctl.py:20`,
  `docs/execution/EXECUTION_STATE.json:2`).
- The unmerged historical branch persists `geox_repo_execution_state_v4` with
  required `completion_evidence` for late lifecycle, fully generated reports,
  and the same `TRANSITIONS` gap (no `ready_for_review` to `blocked`).
- This task performs no runtime or persisted-schema migration; migration design
  is the deliverable.

### 3.2 Recommendation — version and boundary (decided)

- Successor schema is `geox_repo_execution_state_v5`, defined as **v3 plus the
  route**: the `rejection_history` key, the `--to blocked` payload path, the
  `ready_for_review` to `blocked` edge, and the §1.7 target-blob rules. No
  other semantic change.
- v5 states must not contain a `completion_evidence` key: its presence fails
  `E_STATE_KEYS` as an unknown key. A v4 live state presented to a v5
  controller fails `E_SCHEMA_VERSION`. The unmerged completion-evidence
  contract and its renderer behavior stay entirely on their own track with
  their owned recovery successor; this route-only baseline imports none of it.
- Migration: v3 states gain `"rejection_history": []` on first authorized v5
  write; every entry validates fully on every load (shape, SHAs, nonempty
  finding/resolution naming both SHAs, exhausted target counters, paired prior
  fields), and any malformed entry fails `E_REJECTION_EVIDENCE` / companions —
  `render()` validates shape before dereference and never raises uncaught
  errors on history data.
- The v4 historical blob is referenced by SHA inside history entries; it is
  never loaded as live state.

### 3.3 Recommendation — write target and historic identity (decided)

- **Authoritative write target:** the live recording task's own
  `docs/execution/EXECUTION_STATE.json` on its freshly Git-authorized branch
  (pattern of this task family: authorized recovery branch from synchronized
  post-v5 main). Until such a task is authorized, a rejection exists only as
  external review evidence; no controller writes it anywhere.
- **Historic-task identity** pinned per entry: `(Phani-Pavuluri/panel_exp,
  GEOX_STRUCTURED_COMPLETION_EVIDENCE_001,
  feat/geox-structured-completion-evidence-001,
  81664df0d687746a8ee990eada702a2a54cc23c0,
  3841c1790d82d94ebdb99dc6a4022b3c4097c86d)`, each element checked against the
  blob and the remote per §1.3, never against the live fields.
- Rejected designs: substituting the live task's identity into historical
  fields (destroys authorization/evidence separation); an append-only sidecar
  log outside canonical state (bypasses lifecycle controls and view
  determinism); writing the historical branch (violates immutability).
- No implicit successor execution: recording never authorizes implementation,
  evidence recovery, role adoption, or any next task.

---

## 4. Failure semantics, consistency, recovery, and acceptance cases

### 4.1 Approved principle

Candidate states validate before any write; each file write is individually
atomic; `check()` precedes mutation (§1.1).

### 4.2 Recommendation — honest per-file atomicity (decided)

No three-file transaction is promised because none is provided. Guaranteed
order and windows: (1) all §1.7 checks pass on Git-observed values; (2)
candidate validated in memory; (3) state file replaced atomically
(temp-file plus rename); (4) each view replaced atomically in turn. Crash
windows: before (3) — nothing changed, safe retry of the identical command;
between (3) and (4) — state advanced, views stale; during (4) — one view
stale. The latter two converge on the same recovery (§4.3). At no point is a
partial JSON state left behind: the state replacement is itself all-or-nothing.

### 4.3 Recommendation — view-only sync recovery with no double record (decided)

- Any stale-view window surfaces as `E_VIEW_DIVERGENCE` on the next `check()`,
  changing nothing. Recovery is `sync`, which re-renders views from canonical
  state and mutates no state field, counter, or history entry. State repair
  outside `sync` is forbidden.
- The transition is non-reentrant by history membership: re-issuing the
  identical command after the state advanced fails `E_TRANSITION` (already
  recorded) instead of appending a duplicate. Operators must run `sync`, not
  re-transition.
- `E_WRITE_ATOMICITY` is narrowed to a torn state file (JSON parse failure
  with a leftover temp file): recovery is restoring the last committed state
  via Git and re-applying, never hand-editing canonical JSON.

### 4.4 Recommendation — deterministic views (decided)

`render()` is a pure function of canonical state plus preserved human sections
outside markers. The active-task block shape is unchanged (live lifecycle
fields as today; live top-level rejected fields render the live task's own
facts). The completion-report block gains one deterministic section —
`Rejection history` listing each entry's target triple, target counters, prior
pair, finding, resolution condition, live main, and blockers, or `none` when
empty. Shape validation precedes any dereference.

### 4.5 Named acceptance cases (decided)

Negative cases change no tracked file; each names its code:

- **AC-1 wrong repository:** live `repository` mismatch — `E_STATE_REPOSITORY`
  at load or `E_REJECTION_IDENTITY` at agreement.
- **AC-2 wrong target task:** blob `task_id` differs from the pinned
  expectation — `E_REJECTION_IDENTITY`.
- **AC-3 wrong target branch:** blob `feature_branch` differs from pinned
  expectation, or `ls-remote` queried for the wrong ref — `E_REJECTION_IDENTITY`.
- **AC-4 wrong head:** well-formed head unequal to observed remote head,
  non-commit object, or prefix abbreviation — `E_REJECTION_HEAD`; malformed
  hex — `E_SHA`.
- **AC-5 wrong implementation:** CLI value unequal to blob implementation, or
  not an ancestor of the head — `E_REJECTION_IMPLEMENTATION`; malformed hex —
  `E_SHA`. Positive control: `3841c17…` is an ancestor of `81664df…`.
- **AC-6 target budget remains:** blob `remaining > 0`, `completed != maximum`,
  or blob correction open — `E_REJECTION_BUDGET`. Non-exhausted recording must
  use the plain self-block path, never this route.
- **AC-7 missing evidence:** absent/blank finding or resolution —
  `E_REJECTION_EVIDENCE`; finding not naming both SHAs —
  `E_REJECTION_EVIDENCE`; absent/blank blockers — `E_BLOCKERS`.
- **AC-8 protected flags:** any protected/merge/PR/next-task flag set, or any
  candidate flip — `E_PROTECTED_AUTHORITY` / `E_AUTHORITY`; approval field set —
  rejected (stays null).
- **AC-9 stale main:** local `main != origin/main`, or `--live-main`
  disagreement — `E_STALE_MAIN`.
- **AC-10 success:** exhausted blob `1/1/0` with prior pair `61c4e7d…` /
  `0d251c2…`, exact head/implementation, durable blocker, full finding and
  resolution, synchronized main — exit 0; post-state exactly §2.2;
  `taskctl check`, `json.tool`, `git diff --check` pass; live counters and
  top-level rejected pair unchanged; protected authority all false.
- **AC-11 interrupted write:** crash between state and view writes — next
  `check` reports `E_VIEW_DIVERGENCE`; re-issued transition fails
  `E_TRANSITION` with history length unchanged (no double record); `sync`
  repairs; `check` passes.
- **AC-12 determinism:** rendering the AC-10 post-state twice is
  byte-identical; `sync` is idempotent.

---

## 5. Successors, resolved decisions, reserved policy, limitations

### 5.1 Approved principle

Controller implementation, completion-evidence recovery, and role adoption are
separate successors; this task executes no rejection and authorizes no
successor. GeoX only; MIP/MMM read-only; the three unrelated defect IDs stay
unresolved; no tests mirroring document text are added.

### 5.2 Recommendation — three separate successors (decided)

1. **Controller implementation:** builds §1–§4 in `taskctl.py` with focused
   tests for every AC case plus history append-only, prior-lineage carry,
   non-reentrancy (history length unchanged on replay), code-mapping
   (`E_SHA`/`E_BLOCKERS` vs `E_REJECTION_HEAD`/`E_REJECTION_EVIDENCE`), and
   `sync`-only recovery. Merges only via external exact-head approval,
   fast-forward.
2. **Completion-evidence recovery:** owns the v4 early-lifecycle validation gap
   and renderer hardening on its own track. Imports nothing from, and changes
   nothing in, this route.
3. **Role adoption:** owns reviewer/worker wiring and any identity evidencing
   beyond Git-observed SHAs. Changes no lifecycle semantics.

### 5.3 Technical decisions resolved here (not reserved)

Schema label `geox_repo_execution_state_v5`; CLI/API spelling in §1.2;
persisted (not prose-only) `live_main_sha`, `target_counters`, and `prior_*`
fields; `rejection_history` top-level key with `[]` default; new edge
`ready_for_review` to `blocked` alongside CLI-executable existing blocked
edges; state-then-views write order with `sync`-only recovery; lexical-vs-semantic
code mapping in §1.5; controller places no constraint on recovery-branch name
patterns beyond exact-match authorization. All are Muse recommendations open to
Codex review, requiring no separate owner permission.

### 5.4 Owner-reserved substantive policy (only these)

New authority or capability of any kind; product eligibility or consumer
verification; any exception to historical-branch immutability; correction-budget
policy (exhausted defined as `remaining == 0` with `completed == maximum`;
budget sizes remain per-task authorizations); any successor authorization. None
is chosen or implied by this document.

### 5.5 Disagreement and limitations

No substantive disagreement with the six findings: all are agreed and addressed
(§6 traces each). Known limitations: Git identity cannot evidence agent
independence (§1.6); the v4 renderer gap is preserved as a finding for its owned
successor, not fixed here; the combined v3+v4 controller
reconciliation is owned by a later merge design, not this route; review quality
of finding/resolution prose is human responsibility beyond shape checks.

---

## 6. Finding traceability

- Finding 1 (write target / identity coexistence) → §1.3 model, §1.4 live-vs-target
  separation, §3.3 authoritative target and rejected designs.
- Finding 2 (prior rejected pair overwrite) → §1.4 `prior_*` fields, §2.3
  append-only history, §2.2 live rejected fields untouched.
- Finding 3 (impossible retry) → §4.2 honest windows, §4.3 `sync`-only recovery
  and non-reentrancy, AC-11.
- Finding 4 (no finding input / Git identity) → §1.2 `--finding` /
  `--resolution-condition`, §1.4 exact paths, §1.6 independence limits.
- Finding 5 (v5 imports v4) → §3.2 v5-equals-v3 boundary, key forbidding,
  SHA-only reference.
- Finding 6 (over-reservation / code conflicts) → §5.3 resolved list, §5.4
  narrowed reservation, §1.5 mapping rule with AC-4/AC-7 alignment.
- Remaining concerns: approval null (§1.4, §2.2, AC-8); shared identity (§1.6,
  §5.5); blob-not-self reads (§1.3, §1.7 steps 4–6); finding not inferred (§1.2,
  AC-7); all record fields defined (§1.4, §4.4); no three-file transaction
  promise (§4.2); no open alternatives (§5.3).

---

## Appendix A — Evidence pins and references

- Current controller: `panel_exp/execution/taskctl.py` (v3, 323 lines):
  `SCHEMA_VERSION` line 20; `STATES`/`TRANSITIONS` lines 21–44; `validate_state`
  lines 110–179; `render`/`replace_view`/`_candidate_views`/`sync`/`check` lines
  182–259; `transition` lines 262–296; atomic writer lines 226–239.
- Target blob: `81664df:docs/execution/EXECUTION_STATE.json` (fields in header).
- Prior draft: branch `docs/geox-exhausted-review-route-contract-001` at
  `cf743b8…`, finding receipt in pushed `refs/notes/codex-supervised-reviews`
  (`reject_for_contract_inconsistency`, six findings, no merge/correction
  granted).
- Current authorization: base `3dc762d…`, authoring/authorization
  `a9677d5…`, post-authoring main `3eda8e5…`, dependencies
  `DEP-GEOX-EXHAUSTED-REJECTED-EVIDENCE-001` and
  `DEP-GEOX-REJECTED-CONTRACT-EVIDENCE-001`.
- Failing invariant: "An exhausted independently rejected review has no
  supported canonical blocked transition."
- Focused tests: `tests/execution/test_taskctl.py` (10 on main) and
  `tests/test_repo_native_execution_handoff.py` (3); historical combined
  evidence 25 passed on the frozen head.
- This task's gate (documentation scope): `taskctl check`, `json.tool` on
  `EXECUTION_STATE.json`, `git diff --check`, authorization-baseline diff
  limited to the four owned paths, section references for all five acceptance
  items (1→§1, 2→§2, 3→§3, 4→§4, 5→§5). Docker, analytical tests, Ruff, mypy
  not required; no tests mirroring document text.
