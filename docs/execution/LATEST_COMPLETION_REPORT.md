# TASK_AUTHORIZATION_REPORT

## Current decision

- **Current decision:** `authorized`
- **Task ID:** `GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Pre-authoring base:** `e9b7d311ecaf5a90e227d8299f745a0e8f332368`
- **Feature branch:** `feat/geox-certified-calibration-handoff-source-fixture-001`
- **Risk tier:** Tier 3 producer contract and certified cross-repository source fixture
- **Implementation SHA:** not yet created
- **Capability authority:** unchanged

## GitHub-observed orientation evidence

- GeoX `main` was synchronized at `e9b7d311ecaf5a90e227d8299f745a0e8f332368` before authoring.
- The prior GeoX execution-governance task is superseded without merge and has no remaining execution, correction, merge, PR, analytical, or capability authority.
- Certified governed-readout fixtures were introduced at merged commit `860182386c39f487747de5f43e67a31e9978e57c`, which remains an ancestor of live GeoX `main`.
- The canonical source contract is `panel_exp/contracts/geox_governed_experiment_readout.py`.
- The canonical source fixture root is `tests/fixtures/geox_governed_readouts/`; its manifest contains 12 cases and records `mmm_compatibility_emitted: false` and `production_authorized: false`.
- The existing fixtures preserve readout, experiment, KPI/unit/estimand/effect-scale, channel, geography/grain, uncertainty, method/instrument, freshness-status, handoff, lineage, provenance, replay, and authorization data, but do not provide exact fixture datetimes, freshness timestamps, a canonical cross-producer evidence-artifact identity, exact source paths/checksums, or a closed method-eligibility taxonomy.
- MIP `main` was observed at `0b4cd1fca73716e4968c2ceb70c594ad8aadd8ca`.
- MIP task `MIP_P2_GEOX_MMM_COMPATIBILITY_FIXTURE_BRIDGE_001` is blocked on its remote feature branch at `480b32040ce185b8ff091435121c4bea6fc6c453` by `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`.
- MMM `main` was observed at `f2e0eade0ad917c1b28ab5521e6d35a35047d988`; its current proposed task is non-executable and does not overlap this GeoX producer surface.
- No existing active, authorized, review-ready, blocked, or recently completed GeoX task owns this exact calibration-handoff source fixture.

## Authorized outcome

Publish one provenance-complete, deterministic, non-authorizing GeoX source manifest over all 12 existing certified governed-readout fixtures.

The task adds a strict `GeoXCalibrationHandoffSourceRecord`, a deterministic fixture builder, one committed 12-record manifest, tests, and producer documentation. It provides stable source identities, exact synthetic fixture time scope, freshness provenance, governed method eligibility, exact source paths, and SHA-256 checksums.

Existing governed-readout payloads are immutable inputs. Their experiment estimates, uncertainty, statuses, handoff decisions, lineage, replay metadata, and authorization flags must remain unchanged.

## Ownership and non-actions

GeoX owns experiment/readout identity, temporal scope, method/instrument status, handoff eligibility, and producer lineage.

MMM retains exclusive ownership of normalization and final calibration-compatibility truth. MIP retains exclusive ownership of canonical `CalibrationSignal` construction, consumer reconciliation, orchestration, trust, and reporting.

This authorization does not permit:

- MMM compatibility evaluation or compatibility fixtures;
- `CalibrationSignal`, target-model, calibration-weight, or MIP evidence construction;
- changes to experiment design, assignment, inference, estimates, or uncertainty;
- runtime integration with MIP or MMM;
- TrustReport, DecisionSurface, simulation, optimization, planning, recommendation, LLM, real-data, pilot, or production behavior;
- modifications to MIP or MMM repositories.

## Blocker and consumer-verification impact

The task advances only the GeoX producer side of `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`.

Producer completion does not resolve that blocker. Resolution still requires a separately merged MMM compatibility fixture linked to this exact GeoX evidence identity, followed by MIP consumer verification and a MIP-owned blocker transition.

No MMM or MIP successor is authorized here.

## Validation requirement

The frozen task requires:

- changed JSON parsing;
- Python compilation;
- exact owned-path verification;
- `git diff --check`;
- focused and adjacent governed-readout tests with exact counts;
- configured Ruff and mypy;
- two byte-identical deterministic fixture generations matching the committed manifest;
- Docker-backed full repository validation through `make validate-docker` with exact counts and warnings;
- an exact-tree publication receipt;
- clean task-owned worktree;
- exact local/remote feature-branch equality.

Focused success cannot hide Docker/full-suite validation debt. Required validation failure must produce an accurate Git-durable `blocked` state.

## Task-authoring boundary

The authoring range starts at `e9b7d311ecaf5a90e227d8299f745a0e8f332368` and may change only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The commit containing this report is the final task-authoring head. The immediate next commit must change only `docs/execution/EXECUTION_STATE.json`, record this exact authoring head as `authorization_head_sha`, and authorize the declared feature branch.

## Publication and review boundary

Successful execution must publish one exact remote `ready_for_review` head and stop without PR or merge. The report must distinguish GitHub-observed evidence from locally reported validation, identify one implementation SHA, record exact counts, list blockers and limitations, preserve consumer-verification debt, and state unchanged capability authority.

At most one externally directed correction cycle is permitted. A second failed exact-head review supersedes the task without merge.
