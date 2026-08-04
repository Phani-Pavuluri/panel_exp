# Active Task

**Status:** superseded
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_EXECUTION_BRANCH_BINDING_REAUTHORING_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Feature branch:** `feat/geox-execution-branch-binding-reauthoring-001`
- **Authorization head:** `94d512eeffc549cdd98d0dffa166caeb9d75c2c1`
- **First rejected review head:** `f7535473a40aeffef5aad21ca404c391bc8fa0d7`
- **Original implementation candidate:** `b0c56211305bbda9e609ea9d94242b7d61159104`
- **Failed correction implementation:** `bd73ee767c1737e22ec65f40280073aaa2768b16`
- **Disposition:** superseded without merge
- **Capability authorizations changed:** `false`

## Final decision

The task is superseded without merge. Its single permitted correction cycle published a `ready_for_review` branch state, but the live remote tree still fails the frozen acceptance contract. No further correction is authorized.

The preserved branch is historical failed-attempt evidence only. Do not resume, merge, rebase, force-update, delete, or open a pull request from it. No execution-governance successor is authorized by this decision.

## Contract failures at final review

1. The required sibling repository topology is still violated. The test fixture creates `<tmp>/origin.git` and `<tmp>/work`, but also creates and stages a `work/origin.git` symlink. The frozen correction explicitly prohibited nesting or staging `origin.git` inside the worktree.
2. The scenario builder still returns only the temporary-directory owner, work path, state mapping, and authorization SHA. It does not return the named synchronized-main, feature, and remote-feature heads required by the correction.
3. The success test still checks only exit status, stderr, and the JSON key set. It does not assert `status`, phase, task ID, feature branch, or exact head values.
4. The divergence scenario still clones through `work/origin.git`, not the separate sibling bare repository path, and its setup Git commands still omit fail-fast `check=True` behavior.
5. `scripts/verify_authorized_task_binding.py` is unchanged from the rejected implementation. A missing configured upstream still escapes through the generic Git helper and maps to `GIT_COMMAND_FAILED`, not the required `REMOTE_DESTINATION_MISMATCH`.
6. `AGENTS.md` and `TASK_EXECUTION_STANDARD.md` summarize the sequence but do not publish the exact command/refspec contract required by the frozen correction.
7. The branch execution state claims `ready_for_review` while retaining `correction_execution_authorized: true` and stale `review_decision: changes_requested`; the publication contract required correction authority false and a coherent `ready_for_review` decision.
8. The completion report does not separate GitHub-observed evidence from locally reported validation and omits required current sibling pins, consumer-verification disposition, limitations, and validation debt.
9. Live sibling evidence changed after the correction report: MIP main is `9bed0f30879e68473a37b0e65d449ea0b6a6e3f3` with `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_001` authorized, and MMM main is `ac546548784385baab67d7c935e5a4fcdfc9e1af` with `MMM_REPOSITORY_EXECUTION_PROTOCOL_ADOPTION_001` merged. The correction report retained older pins.

The reported focused result of `8 passed` is locally reported evidence only. It does not establish acceptance because the implemented fixtures and assertions do not match the frozen behavioral contract.

## Authority and next work

Task execution, correction execution, merge, pull-request creation, sibling authority, analytical authority, and capability authority are false.

`GEOX_PUBLICATION_LIFECYCLE_AND_RECEIPT_001`, builder successors, navigation cleanup, and additional branch-binding or launcher governance are not authorized. The next GeoX task must be selected from synchronized live Git and should advance actual experiment, readout, integration, validation, or user-facing capability rather than another execution-governance abstraction.

**Unresolved execution-blocking design questions for this superseded task:** not applicable.
