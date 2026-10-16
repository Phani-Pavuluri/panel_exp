# GeoX Producer Provenance and Finality Definition 001

**Status:** Owner-adopted direction, documentation only. This document defines
meanings and boundaries; it selects no version triple, grants no
certification, designates nothing final, and changes no code, fixtures,
schemas, serializers, gateways, or tests. Every factual claim below is
verified against the cited exact source or pin; anything not so verified is
marked as future work.

## 1. Current boundary (verified)

- The native governed pipeline returns only `ReadoutEvidence`:
  `run_governed_analysis` (`panel_exp/validation/estimator_readout_adapter_001.py:515`)
  → `build_estimator_readout` (`:396`, `-> ReadoutEvidence`) →
  `build_guarded_readout` (`panel_exp/validation/readout_boundary_builder_001.py:44`,
  `-> ReadoutEvidence`, `:117`).
- No `GeoXGovernedExperimentReadout(` construction exists outside the contract
  example; nothing in `panel_exp/` or `scripts/` imports
  `contracts.geox_governed_experiment_readout`. The ReadoutEvidence →
  GeoXGovernedExperimentReadout mapping/export boundary is therefore MISSING,
  not merely unstamped: there is no translation layer, only shape-adjacent types.
- `GeoXReadoutProvenance` is exactly four fields — `source_repo`,
  `source_commit`, `producer_package_version`, `created_by`
  (`panel_exp/contracts/geox_governed_experiment_readout.py:15`) — and
  deserialization splats `**payload` (`:32`). Any fifth field breaks
  mixed-version readers and writers in both directions.
- All twelve `tests/fixtures/geox_governed_readouts/*/governed_readout.json`
  carry fixture-generator literals (`readout_version`/`artifact_version`
  `"1.0"`, top-level `producer_package_version` `"1.0"` against provenance
  `"1.0.0"`, `producer_commit` `"fe2e97f"`). They validate shape and
  round-trip only; they are not authority for any version value.

## 2. Version domains (adopted meanings)

| Field(s) | Domain | Source of truth |
|---|---|---|
| `package_version` | Installable distribution identity | `pyproject.toml:3` and `panel_exp/__init__.py:5` (today `0.2.1`), via `evidence_module.__version__` at build time, the pattern `DesignEvidence` paths already use |
| `builder_version` (native) / `created_by` (GeoX) | Which builder logic ran | `BUILDER_VERSION = "1.0.0"` (`readout_boundary_builder_001.py:17`); GeoX side records builder identity in existing free-text `created_by` (fixture precedent: `"fixture_generator"`, `"contract"`) — no schema change, fully compatible both directions |
| `evidence_version` | Names the shape contract whose structure is validated | `EVIDENCE_VERSION = "1.0"` (`panel_exp/evidence.py:48`); the string itself is carried, never compared — structural validation never consults version strings |
| `readout_version` | Opaque lineage string (with `artifact_version` below) | Non-emptiness enforced (`missing_readout_version`, contract validator); carried verbatim, no revision semantics, no conformance check against any shape version |
| `artifact_version` | Opaque lineage string | No source defines revision semantics for it (contract declares the bare field at `:20`; envelope/registry/calibration versions are separate namespaces); carried verbatim, pinned by equality only when designated — no per-artifact-revision meaning is asserted |
| `producer_commit` | Source-tree identity | Git SHA captured at build time; fixture `fe2e97f` is a generator literal, not a pin |
| `replay_version` | Determinism-scheme marker | Existing `"1.0.0"` usage unchanged in meaning |

Rejected alternatives: lockstep single version (conflates schema evolution with releases — a shape fix would force a release bump or vice versa); status quo (proven untestable — shape-only validation can never catch the `1.0`/`1.0.0` split).

## 3. Existing-field export mapping (no new fields)

A future export constructor translates field-by-field, inventing nothing:
native identities and payload (`evidence_version`, builder identity, estimator
result payload, design evidence) → GeoX identity/analytical/kpi/lineage fields;
`package_version` ← distribution `__version__` at build time;
`producer_commit` ← build-tree SHA; `provenance.created_by` ← builder
identity/version convention; `readout_version`/`artifact_version` ← opaque
passthrough carried verbatim. Validation stays shape + marker +
blocked-posture at the gateway (`docs/DOWNSTREAM_READOUT_AUTHORIZATION_GATEWAY_001.md:8`);
equality-to-pin checks activate only after a pin is designated.

## 4. Illustrative future designation record (NON-OPERATIVE)

```json
{
  "designated_triple": {"schema": "<contract schema id>", "artifact": "<artifact id>", "producer_build": "<package>@<commit>"},
  "designated_by": "<owner authority reference>",
  "designated_head": "<exact reviewed head>",
  "status": "final_for_consumers"
}
```

This shape is illustrative only. No designation occurs in this task; no
consumer may treat any existing artifact as final on its basis. Finality also
does not touch calibration eligibility (signal allowlists unchanged;
`final_calibration_compatibility_not_owned_by_geox` stands).

## 5. Compatibility impact

None: no schema, code, fixture, gateway, test, or serialization change. Mixed
-version readers are unaffected (no new fields). Fixture literals remain valid
under shape checks. Certification (`producer_certification_authorized`,
false everywhere), numerical/BRB truth, and MMM ingress (blocked) are
explicitly out of scope and unchanged.

## 6. Independently gated next steps

1. Export implementation + tests (the MISSING constructor above).
2. Gateway pin enforcement (equality checks once a pin is designated).
3. Fixture regeneration with real stamps (transcription only, after 1–2).
4. `producer_certification_authorized` capability decision (owner grant).
5. Calibration pairing (unchanged allowlists).
Each step is separately authorized and gated; none is approved here.
