# GeoX Main Test Isolation and Checkpoint Context Recovery

## Checkpoint

- GeoX main: `b11646bab1f461964644a6526ef4967a8f04624d`
- MIP main: `a293ce52a813709ca624332123019139928cc51e`
- MMM main: `fe8e784923994406a2e4907d28debd872d61fd73`
- Validator: `panel_exp/contracts/geox_calibration_source_manifest.py`
- Builder: `scripts/build_geox_calibration_source_manifest.py`
- Manifest: `tests/fixtures/geox_calibration_handoff_sources/v1/manifest.json`
- Source root: `tests/fixtures/geox_governed_readouts/`

The validator test now uses normal package imports; synthetic `ModuleType`,
manual package paths, and `sys.modules` injection were removed. Isolated probes
use `python -I`, sanitized `PYTHONPATH`/`PYTHONHOME`, and temporary working
directories. Builder replay uses two sanitized subprocesses and proves byte
identity with the committed manifest and source-tree immutability.

This is validation evidence only. `producer_certified: false`,
`mmm_compatibility_emitted: false`, and `calibration_signal_emitted: false`.
The remaining certification gap is the combined producer gate. The successor
`GEOX_CALIBRATION_SOURCE_MANIFEST_CERTIFICATION_RECOVERY_001` remains
unauthorized. No MIP/MMM or downstream authority is changed.

## Validation evidence

Focused and adjacent test counts, Ruff, Docker, deterministic replay, source
immutability, and exact-tree publication evidence are recorded in the execution
completion report after the frozen task-owned gate.
