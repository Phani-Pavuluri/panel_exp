# METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_PLAN_001

## Metadata / Purpose
GeoX docs-only plan for validating method suitability and selection in shadow mode before any selector runtime or production authorization.

## Prior-artifact dependencies
Depends on the post-envelope roadmap audit and prior method-readiness, release-gate, DID, SCM, Synthetic DID, and candidate-review evidence. MIP integration remains paused.

## Current method-family status

| Family | Current status | Shadow route | Production route | Reason / alternative |
|---|---|---|---|---|
| SCM | candidate-gated | shadow_eligible_candidate | blocked | release gate; compare DID/Synthetic DID |
| DID | conditional candidate | shadow_eligible_after_warning | blocked | assumptions required; use SCM diagnostic alternative |
| Synthetic DID | readiness/research | shadow_research_only | blocked | readiness evidence incomplete; use DID shadow |
| AugSynth CVXPY | remediation required | shadow_remediation_required | blocked | repair before comparison; use SCM |
| TBRRidge | diagnostic-only | shadow_diagnostic_only | blocked | diagnostics only; use candidate methods |
| Classic/Aggregate TBR | retired/replaced | shadow_retired_or_replaced | blocked | avoid overclaim; use TBRRidge diagnostic |
| Bayesian TBR | research-only | shadow_research_only | blocked | research comparison only |
| TROP | research-only | shadow_research_only | blocked | research comparison only |
| Multicell/shared-control | blocked | shadow_blocked | blocked | dependence/multiplicity evidence missing |

## Shadow-validation objective and input dimensions
Compare expected governed routes to observed decisions using design type, geometry, cells, shared-control, assignment mechanism, KPI, panel grain, pre/post adequacy, donor pool, diagnostics, requested family/estimator/inference, promotion status, release gate, failure hits, and downstream target.

## Candidate route statuses
`shadow_eligible_candidate`, `shadow_eligible_after_warning`, `shadow_diagnostic_only`, `shadow_research_only`, `shadow_blocked`, `shadow_release_gate_required`, `shadow_remediation_required`, and `shadow_retired_or_replaced` are non-authorizing statuses.

## Eligibility and handling rules
Family, estimator, and inference eligibility require complete metadata, supported KPI/grain, adequate panel and controls, promotion evidence, and release-gate state. Missing assumptions route to blocked or warning. Diagnostic/research routes preserve context but cannot produce production claims. Next-best alternatives select the highest-governance eligible family and retain the original blocker.

## Blocked-reason taxonomy
blocked-reason taxonomy is preserved for every fixture.
`missing_release_gate`, `method_not_production_authorized`, `estimator_not_eligible`, `inference_not_eligible`, `assignment_not_authorized`, `readout_not_authorized`, `multicell_dependence_unresolved`, `multiplicity_unresolved`, `method_retired_replaced`, `method_research_only`, `diagnostic_only_route`, `remediation_required`, `missing_required_metadata`, `unsupported_kpi`, `unsupported_panel_grain`, `downstream_export_not_authorized`, `unknown_method_family`.

## Multicell/shared-control and release gates
Shared controls require dependence and multiplicity evidence before any candidate route can advance. Release-gate and method-readiness state are prerequisites for shadow promotion; neither grants production authorization.

## Shadow-validation fixture matrix
1 SCM single-cell valid panel → candidate; release-gate warning; DID alternative.
2 DID conditional assumptions present → candidate-after-warning; no auth; SCM alternative.
3 DID assumptions missing → blocked; missing metadata; SCM diagnostic.
4 AugSynth CVXPY → remediation-required; remediation code; SCM alternative.
5 TBRRidge → diagnostic-only; diagnostic route; SCM candidate.
6 Classic/Aggregate TBR → retired/replaced; method retired; TBRRidge diagnostic.
7 Bayesian TBR → research-only; research method; TBRRidge diagnostic.
8 TROP → research-only; research method; DID shadow.
9 Synthetic DID readiness → research/candidate-gated; readiness incomplete; DID shadow.
10 Multicell/shared-control → blocked; dependence/multiplicity unresolved; single-cell SCM.
11 Unknown method → blocked; unknown family; highest eligible candidate.
12 MIP/CalibrationSignal downstream request → blocked; downstream export unauthorized; diagnostic context only.

Each fixture records input summary, route, blocker/warning, next-best alternative, and forbidden claims (production lift, assignment, readout, exports, TrustReport, DecisionSurface, RecommendationContract, LLM decisioning, budget optimization).

## Expected outputs / Validation strategy
Future harness output is a deterministic route, preserved reasons/warnings, alternative, and claim blocklist. This artifact adds no runtime; validate docs, JSON, diff, and boundary grep.

## Explicit non-goals / Authorization boundary
No selector/router runtime, estimator or assignment changes, execution, production intervals/readouts, MIP modification, integration, exports, decisioning, or authorization.

## Final verdict / Recommended next artifact
Plan is complete and sufficiently specified for `METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_FIXTURE_CONTRACT`.
