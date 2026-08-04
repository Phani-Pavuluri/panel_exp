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
- **Preserved final branch head:** `a84d85277f9bbc35c08a40308d65858adbd36713`
- **Disposition:** superseded without merge
- **Capability authorizations changed:** `false`

## Final decision

The task is superseded without merge after its only correction cycle failed exact-head review. No further correction is authorized.

The correction did not implement the frozen contract. It modified only `panel_exp/contracts/geox_calibration_handoff_source.py` and `panel_exp/contracts/__init__.py`, leaving the rejected generator, manifest, tests, Track-D evidence, archive summary, source-truth eligibility logic, canonical readout validation, path/checksum verification, and named acceptance coverage materially unchanged.

The published blocked condition is not accepted as a genuine external obstruction. The repository-authored Docker gate builds a fresh image, installs Poetry, runs `poetry install --with dev`, and executes pytest. The repository declares both `seaborn` and dev `pytest`. The executor reported an unhydrated host and a direct/stale image missing pytest, but did not evidence failure of the mandated `make validate-docker` path.

The feature branch is preserved as failed-attempt evidence only. Do not resume, merge, rebase, force-update, delete, or open a pull request from it.

## Authority and next work

Task execution, correction execution, merge, pull-request creation, sibling implementation, MMM compatibility, `CalibrationSignal`, analytical recomputation, runtime integration, planning, recommendation, real-data, and capability authority are false.

MIP blocker `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001` remains unresolved. No MMM compatibility or MIP consumer work becomes eligible from this task.

A future producer task, if justified by synchronized live consumer evidence, must be freshly scoped and authorized from current `main`; this failed implementation must not be represented as approved or validated.
