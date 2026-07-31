# GeoX governed readout builder package entrypoint

This artifact defines a deterministic package entrypoint that validates an
already-certified `GeoXGovernedExperimentReadout` and emits a blocked,
non-production `GeoXMIPArtifactEnvelope`. It consumes supplied values only;
it does not run estimators, infer truth, or determine MMM compatibility.

Freshness uses an explicit UTC reference time and valid-through boundary; no
wall clock is read. Unknown timestamps remain unknown and stale evidence is
never refreshed silently. Existing governed-readout fixtures remain the
certified inputs. Focused validation and full-suite limitations are recorded in
the execution report.
