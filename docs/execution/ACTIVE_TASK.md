# Active Task

**Status:** superseded
**Owner:** GeoX governed-readout producer contract and certified-fixture owner
**Last updated:** 2026-08-04
**Last verified:** 2026-08-04

## Identity

- **Task ID:** `GEOX_CERTIFIED_CALIBRATION_HANDOFF_SOURCE_FIXTURE_001`
- **Repository:** `Phani-Pavuluri/panel_exp`
- **Feature branch:** `feat/geox-certified-calibration-handoff-source-fixture-001`
- **Authorized branch baseline:** `ef6a57382831210c085b4c1351358c3a0743be5e`
- **First rejected review head:** `49059bf5baae58764c7c80e015c8ddccf590117a`
- **First rejected implementation:** `191ddbe918cde06ee30c12b3a3d3998e917b86f5`
- **Correction implementation:** `1c08554dc4d50b1a73c33af49ff7b9f6e2756889`
- **Correction blocked-publication head:** `8986036c0c114b7ff75ac675e69cfbb69223b3ff`
- **Disposition:** superseded without merge
- **Capability authorizations changed:** `false`

## Final decision

The task is superseded without merge after its only correction cycle failed exact-head review. No further correction is authorized.

The correction did not implement the frozen contract. It modified only `panel_exp/contracts/geox_calibration_handoff_source.py` and `panel_exp/contracts/__init__.py`, leaving the rejected generator, manifest, tests, Track-D evidence, archive summary, source-truth eligibility logic, canonical readout validation, path/checksum verification, and named acceptance coverage materially unchanged.

The published blocked condition is not accepted as a genuine external obstruction. The repository-authored Docker gate builds a fresh image, installs Poetry, runs `poetry install --with dev`, and then executes pytest. The repository declares both `seaborn` and dev `pytest` dependencies. The reported host missing `seaborn` and direct `panel-exp-validation:local` image missing `pytest` show an unhydrated host or stale/direct image invocation, not completion of the mandated `make validate-docker` path.

## Remaining direct contract failures

1. The source contract remains compressed and incomplete, with most required source-envelope fields hidden inside a generic payload.
2. Strict type, nested-shape, identity, terminal-vocabulary, prohibited-field, path-containment, file-existence, checksum-equality, and field-preservation validation remain absent.
3. The generator path-duplication defect remains unchanged.
4. The generator still derives method eligibility from method-status substrings/readout status instead of certified `source_truth.json` evidence.
5. The unsupported-inference case remains incorrectly classifiable because its source method status is `SCM`.
6. Canonical `GeoXGovernedExperimentReadout` validation is still not integrated into generation.
7. The focused tests, deterministic two-run proof, source-tree immutability proof, and full named acceptance matrix remain unimplemented.
8. The Track-D document, archive summary, and completion report remain below the frozen reporting contract.
9. Docker/full validation, exact counts, Ruff, mypy, and an exact-tree receipt remain absent.
10. The package export correction replaces the repository's existing `__all__` list rather than extending it, risking removal of prior public exports.

## Authority and preservation

Task execution, correction execution, merge, pull-request creation, sibling implementation, MMM compatibility, `CalibrationSignal`, analytical recomputation, runtime integration, planning, recommendation, real-data, and capability authority are false.

Do not resume, merge, rebase, force-update, or open a pull request from this branch. Preserve it as failed-attempt evidence. A future producer task, if ever justified by live consumer need, must be freshly scoped and authorized from synchronized `main`; it must not represent this implementation as approved or validated.

MIP blocker `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001` remains unresolved. No MMM compatibility or MIP consumer work becomes eligible from this task.
