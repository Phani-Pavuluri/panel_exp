# EXACT_HEAD_REVIEW_REPORT

## Decision

**CHANGES REQUESTED**

- **Task ID:** `GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Rejected exact remote head:** `49059bf5baae58764c7c80e015c8ddccf590117a`
- **Rejected implementation commit:** `191ddbe918cde06ee30c12b3a3d3998e917b86f5`
- **Authorized branch baseline:** `ef6a57382831210c085b4c1351358c3a0743be5e`
- **Feature branch:** `feat/geox-certified-calibration-handoff-source-fixture-001`
- **Correction cycles used:** 1 of 1
- **Merge, PR, and capability authority:** false

The exact remote head is not approved and must not be merged. One Git-authored correction cycle is authorized on the existing feature branch. A second failed exact-head review supersedes the task without merge.

## GitHub-observed repository evidence

- Live GeoX `main` remains `ef6a57382831210c085b4c1351358c3a0743be5e`.
- The rejected feature head is two commits ahead of that baseline and changes only the ten task-owned paths.
- The rejected publication head records `ready_for_review` and implementation SHA `191ddbe918cde06ee30c12b3a3d3998e917b86f5`.
- The publication report itself states that Docker/full validation is unreported and not claimed.
- Live MIP `main` remains `0b4cd1fca73716e4968c2ceb70c594ad8aadd8ca` with `MIP_P2_GEOX_MMM_COMPATIBILITY_FIXTURE_BRIDGE_001` still blocked.
- Live MMM `main` remains `f2e0eade0ad917c1b28ab5521e6d35a35047d988`; no MMM compatibility fixture for this source identity is merged.
- No PR or merge was observed for this GeoX feature branch.

## Review findings

### Publication and validation

The branch cannot be `ready_for_review` because the frozen Tier-3 contract requires Docker-backed `make validate-docker`, exact focused and adjacent test counts, Ruff, mypy, two deterministic generations, exact-tree receipt evidence, clean worktree evidence, and local/remote equality. The completion report provides none of the required exact counts and expressly admits full validation is unreported.

The publication commit message `Publish calibration handoff source review` is not the required exact-tree receipt. It does not identify the implementation parent, validation gate/results, evidence source, worktree state, or authority impact.

### Generator defect

The source manifest stores paths such as:

`geox_truth_scm_candidate_clean_001/governed_readout.json`

The rejected generator first sets `d = FIX / fixture_id` and then computes checksums using `d / case["governed_readout"]`. That duplicates the fixture directory and cannot regenerate from a clean synchronized tree. Therefore the committed generator and the deterministic-generation claim are inconsistent.

### Contract incompleteness

The rejected contract is a compressed dataclass with blind `cls(**data)` deserialization and a permissive generic `payload`. It omits many required explicit source-envelope fields and does not strictly validate supported versions, field types, unknown keys, path containment, file existence, checksum equality, source identity, analytical equality, terminal vocabularies, contradictory eligibility, strict UTC timestamps, or prohibited downstream fields.

Checksum validation checks only whether a string looks like 64 hexadecimal characters; it does not compare the checksum to the referenced file. Timestamp validation compares strings lexically rather than parsing timezone-aware UTC datetimes.

### Eligibility derivation

The rejected generator derives eligibility from substrings in `method_status` and from readout status alone. It does not use `source_truth.json`, `fixture_class`, `certification_status`, `mip_handoff_expectation.status`, feasibility, handoff eligibility, or failure reasons as required.

The unsupported-inference source readout has `method_status="SCM"`; substring inspection therefore cannot identify it as unsupported. The rejected logic maps it to `blocked`, violating the required unsupported precedence.

### Canonical source validation and lineage

The generator does not deserialize and validate each governed readout through the canonical `GeoXGovernedExperimentReadout` contract. It does not parse source truth or replay content for eligibility and lineage. The generic copied payload does not establish the required explicit field-by-field preservation and source lineage.

### Public package surface

The new import is appended after `__all__` and is omitted from `__all__`, rather than following the repository’s existing deliberate public-export pattern.

### Test coverage

The rejected test file contains only four broad tests. It does not separately prove the named acceptance evidence, including strict schema/version failures, wrong-type or unknown-field failures, exact ID formulas and uniqueness, path traversal, missing file and checksum mismatch failures, field-by-field preservation for all 12 cases, exhaustive eligibility outcomes, contradictory mappings, prohibited-field rejection, two fresh deterministic generations, or source-tree immutability.

The generation test invokes the defective generator once, not twice. No exact focused test count is recorded in the completion report.

### Documentation and reporting

The Track-D document is seven lines and the archive summary is one line. They do not record the required cases, classifications, exact evidence paths, identities, temporal/freshness semantics, lineage, replay behavior, validation evidence, limitations, validation debt, sibling impact, or consumer-verification boundary.

The completion report does not separate GitHub-observed from locally reported evidence and does not provide exact changed paths, exact validation counts, blockers, limitations, validation debt, source checksums, all supported cases, or exact branch-equality evidence.

## Validation disposition

- **GitHub-observed code review:** failed
- **Docker/full validation:** unreported by executor
- **Focused tests:** no exact counts reported; test implementation is insufficient
- **Deterministic generator:** rejected implementation contains a direct path-resolution defect
- **Ruff and mypy:** unreported
- **Exact-tree receipt:** absent
- **Local/remote equality:** claimed in chat but not durably evidenced in the completion report
- **Changed paths:** within the original ten owned paths
- **Capability impact:** none

These are task-owned implementation and validation failures, not external blockers.

## Required correction

The complete correction contract is recorded in `docs/execution/ACTIVE_TASK.md`. It requires:

- a strict typed source contract with complete explicit fields and deterministic failures;
- canonical governed-readout validation and field-by-field preservation;
- correct certified-root path resolution and checksum validation;
- source-truth-driven exhaustive eligibility mapping;
- strict UTC datetime parsing and freshness consistency;
- deliberate package exports;
- complete behavioral acceptance tests over all 12 fixtures;
- complete Track-D and archive evidence;
- full Tier-3 validation including Docker;
- a genuine exact-tree receipt and exact remote-head verification.

## Cross-repository impact

GeoX has not completed the producer-source checkpoint. MIP blocker `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001` remains open. No MMM compatibility work or MIP consumer verification becomes eligible from the rejected head. Producer completion, consumer acceptance, compatibility, planning, recommendation, runtime, real-data, pilot, and production authority remain false.

## Terminal boundary

The correction must publish either:

1. a new fully validated exact remote `ready_for_review` head; or
2. a genuine external `blocked` state with exact diagnostics and a live resolution condition.

No PR or merge is authorized.
