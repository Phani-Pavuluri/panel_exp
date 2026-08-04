# Completion report

## Current decision

**CHANGES_REQUESTED**

Exact remote head `feda65c5dbba1529d588d2cb36693a38132ab766` is not approved. The implementation candidate `d2a64376757766c1fd4c009f6e2ea238c85437d7` is retained for one bounded correction against the frozen acceptance contract.

## GitHub-observed evidence

- GeoX `main` is `d17bb81c9dbc67f773fd71068c26b14c92989f42`.
- The feature branch was two commits ahead of main without divergence at the rejected review head.
- The complete task diff remained inside the seven authorized paths.
- The implementation added the read-only verifier, execution guidance, and the named test file.
- The final publication commit claimed JSON parse, Python compilation, `git diff --check`, `8 passed`, successful `prepush`/`postpush`, and exact local/remote equality.
- GitHub exposes no combined commit statuses, pull-request-triggered workflow runs, or PR for the rejected head.

## Findings against the frozen contract

### 1. Six required behavioral tests are placeholders

The required wrong-branch, unsynchronized-main, branch-task-mismatch, missing-ancestry, and diverged-destination tests have empty `pass` bodies. The success and post-push tests execute against the current working repository rather than constructing temporary Git repositories. Therefore the reported `8 passed` count does not establish the eight required behaviors.

### 2. The stable reason-code test does not test the verifier contract

`test_failure_output_uses_stable_reason_code` invokes argparse with an invalid phase and checks only exit code `2`. It does not induce a supported runtime failure and does not assert empty stdout, one stderr line, or a `GEOX_TASK_BINDING_ERROR:<REASON_CODE>:` prefix.

### 3. Some contracted failures do not use their stable reason codes

The verifier maps invalid main-state JSON to `BRANCH_STATE_UNREADABLE`, maps a missing remote feature branch to generic `GIT_COMMAND_FAILED`, and can leave branch-file errors uncaught. Raw `merge-base` subprocesses may also emit diagnostics outside the required single stable stderr line. These behaviors violate the frozen exit/output contract.

### 4. The documented sequence is incomplete

The guidance names the three phases but does not explicitly require the full frozen sequence: preflight before edits, prepush immediately before the declared push, fetch after push, and postpush exact-head verification.

## Validation assessment

The `8 passed` result is retained only as locally reported evidence that pytest collected eight functions. Because six functions are empty and the remaining failure test does not validate the stable error contract, it is not acceptance evidence for the authorized outcome.

No Docker, full package suite, analytical tests, Ruff, or mypy are required under the frozen Tier-2 task contract.

## Required correction

The exact correction is recorded in `docs/execution/ACTIVE_TASK.md` at review-task commit `12d32bb0b0421de144935f8c3a046166da8190d7`:

1. implement all eight tests with isolated temporary Git repositories and real subprocess execution;
2. assert exact success and failure outputs;
3. make every contracted runtime failure exit `2` with one stable reason-code line and no success stdout;
4. complete the documented preflight/prepush/push/fetch/postpush sequence; and
5. rerun the unchanged validation gate on the frozen final tree.

This is the single permitted correction cycle. A further failed review supersedes the task without merge.

## Sibling, consumer, and authority impact

- MIP `main`: `976d3a1daeae9c52c8772e5112574f698951a57c`.
- MMM `main`: `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`.
- Affected repository: GeoX only.
- Consumer verification: not applicable.
- Newly eligible work: correction of this task only.
- Publication-lifecycle successor: proposed and unauthorized.
- Merge authority: false.
- PR authority: false.
- Analytical and capability authority: unchanged and false.

## Validation debt

Eight real isolated behavioral tests and exact stable failure-output validation remain outstanding. No product, analytical, package, fixture, or cross-repository validation debt is introduced by this review.
