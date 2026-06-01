# Track B contract golden fixtures (B5a)

**Status:** normative truth table for B5b adapter tests, B5c TrustReport composer tests, and B5d validators.

**Binding architecture:** `docs/TRACK_B_CONTRACT_TEST_PLAN_001.md`, `docs/TRACK_B_ADAPTER_ID_RESOLUTION_001.md`, `docs/TRACK_B_CONTRACT_SCHEMA_DRAFT_001.md`, `docs/TRACK_B_ESTIMAND_REGISTRY_001.md`, `docs/TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001.md`.

These fixtures are **governance artifacts**. They are intentionally explicit and redundant. They define expected behavior; implementations must conform to fixtures, not the reverse.

## Files

| File | Golden ID | Scenario |
|------|-----------|----------|
| `gold_001_scm_jk_null_monitor.json` | GOLD-001 | SCM + UnitJackKnife null monitor |
| `gold_002_tbrridge_kfold_restricted.json` | GOLD-002 | TBRRidge + KFold restricted |
| `gold_003_augsynth_point_no_ci.json` | GOLD-003 | AugSynth point, no fake CI |
| `gold_004_mmm_intake_transform_required.json` | GOLD-004 | MMM intake requires transform |
| `gold_005_placebo_semantics.json` | GOLD-005 | Placebo band semantics |
| `gold_006_missing_declared_estimand_blocked.json` | GOLD-006 | Missing declared estimand blocks export |
| `gold_007_legacy_mapping.json` | GOLD-007 | Legacy TargetEstimand mapping |
| `gold_008_did_cumulative_not_relative.json` | GOLD-008 | DID cumulative interval ≠ relative ATT |
| `gold_009_ab_drift.json` | GOLD-009 | Cell-mean vs pooled-path drift (A vs B) |
| `gold_010_placebo_geometry.json` | GOLD-010 | SCM Placebo multi-treated geometry failure |

## Fixture shape

Each JSON file contains:

- `spec` — input ExperimentSpec slice
- `run_artifacts_stub` — minimal run/config stub (not a full RunBundle)
- `adapter_expected_output` — export tier, evidence identity, alignment facts, DiagnosticSummary
- `calibration_signal_binding` — expected signal lookup (where applicable)
- `trust_report_expected_output` — verdict scenarios by `intended_use` / `claim_type`
- `expected_test_ids` — linked B5 test IDs
- `forbidden_regressions` — linked B2 F* IDs

## Discipline

- Adapter tests assert `adapter_expected_output` only — **no** `trust_outcome` on evidence.
- TrustReport tests (`tests/track_b/test_trust_report_composer.py`, B5c) assert `trust_report_expected_output` via the contract composer in `trust_report_composer.py` — **only** that layer emits `alignment_verdict` / `trust_outcome`.
- Do not shorten IDs or collapse aggregation segments for elegance.

## Regeneration

No auto-regeneration script yet. Update fixtures only when architecture docs change via governed doc revision.
