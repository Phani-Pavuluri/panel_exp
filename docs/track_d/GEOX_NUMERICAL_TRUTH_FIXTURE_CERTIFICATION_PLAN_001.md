# GEOX_NUMERICAL_TRUTH_FIXTURE_CERTIFICATION_PLAN_001

## Metadata / Purpose
Docs-only plan for the smallest certified GeoX numerical-truth fixture suite aligned to MIP’s **quarterly planning with experiment-informed budget reallocation** lifecycle.

## Roadmap steering and evidence inventory
GeoX owns analytical truth and governed readout artifacts; MIP consumes them. Existing envelope producer/consumer contracts remain non-production. The method policy-adapter lane pauses unless directly required.

## Minimum fixture suite
Twelve fixture classes are required: (1) governed candidate readout, (2) candidate readout with warning, (3) infeasible design, (4) weak matchability diagnostic, (5) unsupported inference, (6) diagnostic-only method, (7) research-only method, (8) stale/incompatible evidence, (9) conflicting evidence, (10) multicell/shared-control dependence/multiplicity block, (11) calibration-incompatible result, and (12) safe blocked readout packet.

Each class records purpose, input shape, known effect or blocked state, feasibility/design/assignment/readout status, estimate and uncertainty, KPI/estimand/scope/time window, method/instrument, warnings/blockers, calibration compatibility, MIP handoff, tolerances, and provenance/version.

## Analytical truth schema
Required fields: `fixture_id`, `fixture_version`, `dataset_version`, `truth_version`, `design_type`, `method_family`, `instrument_id`, `assignment_seed`, `panel_grain`, `geo_scope`, `time_window`, `pre_period`, `post_period`, `kpi`, `estimand`, `treatment_units`, `control_units`, `known_lift_absolute`, `known_lift_relative`, `known_incremental_outcome`, `expected_point_estimate`, `expected_standard_error`, `expected_confidence_interval`, `expected_uncertainty_semantics`, `expected_feasibility_status`, `expected_design_status`, `expected_assignment_status`, `expected_readout_status`, `expected_blocked_reasons`, `expected_warnings`, `calibration_compatibility_status`, `mip_handoff_status`, `tolerances`, `provenance`, `created_by`, and `certification_status`.

Certification statuses are `certified`, `candidate`, `diagnostic_only`, `research_only`, `blocked`, `unsupported`, `stale`, and `superseded`.

## Feasibility/design/assignment/readout truth
Fixtures distinguish design feasibility from assignment authorization and readout eligibility. Estimates and uncertainty use explicit semantics and tolerances; blocked states never imply zero effect.

## Ownership, provenance, replay, and failure semantics
GeoX owns fixture truth, versions, deterministic replay, and certification. MIP receives only compatible artifacts. Dataset/truth versions, seeds, instrument identity, provenance, and creator are mandatory. Failures preserve blockers, warnings, incompatibility, stale, conflict, and calibration reasons.

## Calibration, MIP handoff, and D6 Gate 1
Calibration compatibility is explicit and separate from readout validity. Handoff requires producer/consumer versions, schema compatibility, required/optional fields, status semantics, and no authorization escalation. D6 Gate 1 remains incomplete: compatibility matrix, ownership, failure semantics, release/rollback order, limitations, owners, authorization flags, and migration/deprecation rules remain required.

## Deferred work / Authorization boundary
No datasets, generators, readout runtime, estimator execution, assignment logic, MIP/MMM changes, exports, TrustReport, DecisionSurface, RecommendationContract, LLM work, agents, real-data pilot, or production authorization are added.

## Final verdict / Recommended next artifact
Plan complete. **PROCEED_TO_GEOX_NUMERICAL_TRUTH_FIXTURE_CONTRACT**. Next: `GEOX_NUMERICAL_TRUTH_FIXTURE_CONTRACT_001`.
