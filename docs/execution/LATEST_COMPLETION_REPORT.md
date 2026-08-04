# Completion report

## Current decision

**CHANGES_REQUESTED**

- **Task:** `GEOX_EXECUTION_BRANCH_BINDING_REAUTHORING_001`
- **Rejected exact remote head:** `f7535473a40aeffef5aad21ca404c391bc8fa0d7`
- **Retained implementation candidate:** `b0c56211305bbda9e609ea9d94242b7d61159104`
- **Review-task commit:** `c15797d7af81fa4fb974d7c0715cf15df2e61aee`
- **Merge/PR/capability authority:** false

## GitHub-observed evidence

- GeoX `main` is `0a463ad96cda31dc2bdc962fd24f5481bb7aede9`.
- The rejected branch head is two commits ahead of main and not diverged.
- The complete diff changes only the seven authorized paths.
- Implementation commit `b0c56211305bbda9e609ea9d94242b7d61159104` adds the verifier, tests, and execution-standard file.
- Publication head `f7535473a40aeffef5aad21ca404c391bc8fa0d7` records `ready_for_review` and claims the focused validation gate passed.
- GitHub exposes no combined status checks, pull-request workflow runs, or PR for the rejected head.
- Live MIP main is `976d3a1daeae9c52c8772e5112574f698951a57c`.
- Live MMM main is `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`.

## Locally reported validation

The submitted report claims:

- Python compilation passed;
- AST/no-pass inspection passed;
- `git diff --check` passed;
- `pytest -q tests/test_execution_branch_binding.py` returned `8 passed, 0 failed, 0 skipped`;
- verifier prepush and postpush passed;
- local and remote branch heads were equal.

These are retained as locally reported results. There is no GitHub CI evidence for this head.

## Findings against the frozen contract

### 1. The isolated repository topology is incorrect

The shared scenario creates the bare `origin.git` inside the non-bare work repository root and initializes the work repository at that same root. The frozen contract requires separate sibling paths `<tmp>/origin.git` and `<tmp>/work`. The submitted layout can stage an embedded repository during `git add .` and is not the authorized topology.

### 2. Required test assertions and ancestry mutation are missing

The successful preflight test checks the key set but does not assert `status == "ok"`, the expected phase, task ID, feature branch, or exact main/local/remote head values. The scenario builder does not return the named heads required for those assertions.

The missing-authorization-ancestry test assigns forty zeroes instead of creating the required unrelated orphan commit and using that real SHA in synchronized main state.

Therefore the reported eight passing tests do not establish the eight exact authorized scenarios.

### 3. Missing upstream is mapped to the wrong reason code

The verifier resolves `@{upstream}` through the generic Git helper. With no upstream configured, that helper raises and the outer handler emits `GIT_COMMAND_FAILED`. The frozen mapping requires `REMOTE_DESTINATION_MISMATCH` for both a missing upstream and an upstream that is not exactly `origin/<feature_branch>`.

### 4. The documented execution sequence is incomplete

`AGENTS.md` and `TASK_EXECUTION_STANDARD.md` summarize the phases but omit the exact required commands and controls: fetch/prune, pull `--ff-only`, explicit main equality, exact non-force push refspec, exact remote fetch, and final local/remote equality proof.

### 5. The publication evidence is incomplete and internally stale

The completion report does not distinguish GitHub-observed from locally reported evidence, does not record the live MIP/MMM pins, affected repository, consumer-verification disposition, limitations, or validation debt. The execution state says `ready_for_review` while retaining `review_decision: authorized` and stale authoring-note prose.

## Required correction

The complete bounded correction is recorded in `docs/execution/ACTIVE_TASK.md` at `c15797d7af81fa4fb974d7c0715cf15df2e61aee`. It preserves the original frozen contract and requires only:

1. separate bare-origin and non-bare-work fixture paths with checked setup commands and named SHAs;
2. the exact successful assertions and real unrelated-commit ancestry scenario;
3. correct missing-upstream reason mapping;
4. the exact documented execution sequence; and
5. complete, coherent ready-for-review evidence.

## Scope and authority impact

- **Affected repository:** GeoX only
- **Modified repository:** GeoX only
- **Consumer verification:** not applicable
- **Sibling blocker transitions:** none
- **Analytical/package capability impact:** none
- **Merge authority:** false
- **PR authority:** false
- **Capability authority:** unchanged and false
- **Publication-lifecycle successor:** unauthorized
- **Builder successors:** unauthorized

## Validation debt and next outcome

The focused gate must be rerun after correcting the exact fixture, assertions, verifier mapping, documentation, and publication metadata. Docker, the full package suite, analytical tests, Ruff, and mypy remain not required.

This is the one permitted correction cycle. The next exact-head review must either approve the task or supersede it without merge.
