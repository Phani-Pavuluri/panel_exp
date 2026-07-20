# METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_POLICY_ADAPTER_PLAN_001

## Metadata / Purpose
Plan for deterministic fixture-only policy logic deriving observed shadow outcomes from input metadata and governance state, not expected outcomes.

## Prior-artifact dependencies / Current harness limitation
Depends on the fixture contract, harness plan/contract/runtime, and runtime validation. Current harness derives observations from expectations; the future adapter removes that shortcut.

## Policy-adapter objective and non-goals
Derive route, blockers, warnings, alternatives, forbidden claims, safety flags, diagnostics, and failure codes without selector runtime, estimator execution, MIP integration, or authorization.

## Input metadata and governance state
Consume design geometry, cells/shared-control, assignment mechanism, KPI/grain, adequacy, diagnostics, requested family/estimator/inference, promotion/readiness, release gate, failure hits, downstream target, and authorization state.

## Method-family / release-gate / downstream rules
SCM adequate single-cell → `shadow_eligible_candidate` or `shadow_release_gate_required`; DID assumptions present → candidate or gate-required, missing → `shadow_blocked`; AugSynth → `shadow_remediation_required`; TBRRidge → `shadow_diagnostic_only`; Classic/Aggregate → `shadow_retired_or_replaced`; Bayesian/TROP → `shadow_research_only`; Synthetic DID → warning/research; multicell unresolved → blocked; unknown → blocked; downstream export → blocked. Missing release gate yields `missing_release_gate`; no rule authorizes production.

## Blocked-reason / Warning rules
Blocked codes include `method_not_production_authorized`, `assignment_not_authorized`, `readout_not_authorized`, `calibration_signal_export_not_authorized`, `mip_experiment_evidence_export_not_authorized`, `trust_report_production_assembly_not_authorized`, `decision_surface_not_authorized`, `recommendation_contract_not_authorized`, `llm_decisioning_not_authorized`, `budget_optimization_not_authorized`, `multicell_dependence_unresolved`, `multiplicity_unresolved`, `method_research_only`, `method_diagnostic_only`, `method_retired_or_replaced`, `method_remediation_required`, `missing_required_metadata`, `unsupported_kpi_outcome`, `unsupported_panel_grain`, and `unknown_method_family`.

Warnings include `shadow_validation_only`, `no_production_authorization`, `release_gate_required_before_production`, `method_candidate_gated`, `diagnostic_only_route`, `research_only_route`, `downstream_export_blocked`, `multicell_validation_required`, and `method_readiness_review_required`.

## Next-best alternatives
next-best alternatives are explicitly mapped for each fixture.
Use SCM/DID shadow candidates when eligible, TBRRidge diagnostics, AugSynth remediation, method-family remediation/validation when readiness blocks, multicell dependence/multiplicity evidence when shared-control blocks, MIP-owned integration only after its lane is ready, and roadmap reconciliation on conflicts. Never suggest production authorization.

## Policy diagnostics / failure-code taxonomy
Diagnostics contain `fixture_id`, `rule_ids_applied`, `method_family_status`, `release_gate_state`, `downstream_target`, `metadata_completeness`, `failure_registry_hits`, `blocked_reason_codes`, `warning_codes`, `next_best_alternative_codes`, `unsafe_claims`, and `notes`.
Failure codes include `policy_unknown_method_family`, `policy_missing_required_metadata`, `policy_release_gate_missing`, `policy_downstream_export_requested`, `policy_multicell_dependence_unresolved`, `policy_method_research_only`, `policy_method_diagnostic_only`, `policy_method_retired_or_replaced`, `policy_method_remediation_required`, `policy_assignment_not_authorized`, `policy_readout_not_authorized`, and `policy_unsafe_production_claim`.

## Default fixture mapping
Downstream MIP/CalibrationSignal requests are blocked from GeoX.
1 SCM candidate; 2 DID assumptions; 3 DID missing assumptions; 4 AugSynth remediation; 5 TBRRidge diagnostic; 6 Classic/Aggregate retired; 7 Bayesian research; 8 TROP research; 9 Synthetic DID readiness; 10 multicell dependence/multiplicity; 11 unknown method; 12 downstream MIP/CalibrationSignal. Each maps route, blockers, warnings, alternative, and forbidden claims.

## Integration / Validation / Authorization boundary
Future adapter output feeds the existing harness as observed outcomes; harness compares against expected and emits packets/summary. This plan changes no runtime. Production inference, assignment, readout, exports, TrustReport, DecisionSurface, RecommendationContract, LLM decisioning, budget optimization, multicell claims, and agent work remain false.

## Final verdict / Recommended next artifact
**PROCEED_TO_METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_POLICY_ADAPTER_CONTRACT**. Next: `METHOD_SUITABILITY_SELECTION_SHADOW_VALIDATION_POLICY_ADAPTER_CONTRACT_001`.
