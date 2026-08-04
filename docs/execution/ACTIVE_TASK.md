# Active Task

**Status:** superseded
**Owner:** GeoX repository governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `GEOX_LEAN_REPOSITORY_DELIVERY_STANDARD_ADOPTION_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Main authorization head:** `a4bf6bfaa4311dacd3642d289dca3917543e0309`
- **Preserved feature branch:** `docs/geox-lean-repository-delivery-standard-adoption-001`
- **Preserved final branch head:** `bb1ac8d5ce29e2cab33eb680b3b7db76110f35f1`
- **Retained substantive candidate:** `9e5a8473157c0562dce4a870563d7e9d21ca7445`
- **Earlier rejected heads:** `811ff9802cc41a46a7b4186e0eb026358becd337`, `d3543179ce93e5f1563d96554e8a490702735a15`, `6cf6c2584af78c6c288cd572cf4d9e31416b2cc6`
- **Disposition:** superseded without merge
- **Capability authorizations changed:** `false`

## Supersession decision

This task is no longer an acceptable merge unit. It combined branch/task
binding, lean task authoring, terminal-state rules, validation tiers, publication
receipts, stable navigation, and lifecycle reporting. The acceptance contract was
not frozen before execution, review introduced requirements that should have
been known earlier, and the branch exceeded the one-correction-cycle default.

The branch and commits remain historical partial evidence only. Do not resume,
merge, rebase, force-update, open a PR from, or reuse the branch wholesale.
Future work may reuse a specifically reviewed hunk only inside a separately
authorized successor with independent validation.

## Preserved evidence

The preserved branch contains useful but unmerged evidence for:

- main-to-feature-branch task binding guidance;
- navigation-only context guidance;
- candidate lean-delivery wording;
- candidate focused governance tests; and
- locally reported Tier-1 validation receipts.

None of that evidence is merged GeoX governance, satisfies a producer or
consumer dependency, or changes capability authority.

## Successor decomposition

Only the following first successor is eligible for separate authorization:

1. `GEOX_EXECUTION_BRANCH_BINDING_001` — deterministic enforcement that resolves
   authorization from synchronized `main`, binds execution to the exact declared
   feature branch and task identity, verifies ancestry and destination, and
   fails closed on stale or wrong branch state.

A second successor for publication lifecycle, report schema, and exact-tree
receipt semantics remains proposed and unauthorized until the branch-binding
task is approved, merged, and closed.

No governed-readout builder successor, analytical capability, live integration,
real data, pilot, production, or package-side agent is authorized by this
supersession.

## Authority

Task execution, correction execution, merge, PR creation, sibling work, and
capability authority are false. No implementation branch is active under this
task.
