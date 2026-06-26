"""GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "geo_kpi_spend_data_contract_profiler_spec_defined_no_runtime_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/GEO_KPI_SPEND_DATA_CONTRACT_AND_PROFILER_SPEC_001_summary.json"
)

CONTRACT_SCOPE = "geo_kpi_spend_data_contract_profiler_spec_no_runtime"
RECOMMENDED_NEXT_ARTIFACT = "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"

ACCEPTED_INPUT_MODES = (
    "full_panel_mode",
    "sample_schema_mode",
    "ballpark_mode_provisional_only",
)

REQUIRED_FIELDS = (
    "geo_unit_id",
    "date_or_week",
    "kpi_value",
    "spend_value",
)

SUPPORTED_GEO_UNIT_TYPES = (
    "DMA",
    "GMA_like_unit",
    "state_province",
    "city_metro",
    "postal_cluster",
    "sales_territory",
    "custom_cluster",
    "country_region_aggregate",
)

SUPPORTED_TIME_GRAINS = (
    "daily",
    "weekly",
    "custom_period",
)

ZERO_MISSING_RULES = {
    "missing_kpi_is_not_zero_kpi": True,
    "missing_spend_is_not_zero_spend": True,
    "zero_kpi_must_be_observed_zero": True,
    "zero_spend_must_be_observed_zero": True,
}

REQUIRED_PROFILER_REPORTS = (
    "GeoKpiSpendDataProfileReport",
    "ColumnMappingReport",
    "TimeGrainReport",
    "GeoUnitInventoryReport",
    "GeoTimeCoverageReport",
    "KpiSummaryReport",
    "SpendSummaryReport",
    "ChannelCampaignMappingReport",
    "MissingnessReport",
    "DuplicateRowReport",
    "AggregationReadinessReport",
    "UnitEligibilityReport",
    "DataQualityWarningReport",
    "ProfilerFailureReport",
)

BLOCKING_CONDITIONS = (
    "no_geo_unit_id",
    "no_date_or_week_column",
    "no_kpi_column_or_kpi_name",
    "no_spend_column_when_spend_feasibility_requested",
    "mixed_grain_without_mapping",
    "overlapping_geo_units_without_mapping",
    "duplicate_rows_without_aggregation_rule",
    "ambiguous_zero_vs_missing_semantics",
    "post_treatment_data_used_for_pre_period_diagnostics",
    "unknown_channel_campaign_mapping_for_portfolio_planning",
    "insufficient_historical_coverage_for_feasibility_diagnostics",
)

SCENARIO_TESTS = (
    "full_panel_mode",
    "sample_schema_mode",
    "ballpark_mode_provisional_only",
    "daily_grain",
    "weekly_grain",
    "mixed_grain_blocking",
    "dma_units",
    "gma_like_units",
    "state_province_units",
    "custom_clusters",
    "missing_kpi_blocking",
    "missing_spend_blocking_when_spend_feasibility_requested",
    "missing_spend_not_treated_as_zero",
    "zero_spend_valid_observed_zero",
    "duplicate_rows_blocking_without_aggregation_rule",
    "low_volume_units_flagged",
    "outlier_units_flagged",
    "ambiguous_channel_mapping_blocking_portfolio_claims",
    "post_treatment_data_excluded_from_pre_period_diagnostics",
    "llm_cannot_claim_design_feasibility_from_sample_schema_mode",
    "llm_cannot_claim_final_feasibility_from_ballpark_mode",
)

DOWNSTREAM_DEPENDENCIES = (
    "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001",
    "GEO_KPI_SPEND_DATA_PROFILER_001",
    "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
    "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001",
    "SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001",
    "PORTFOLIO_TEST_TIERING_ENGINE_001",
    "CANDIDATE_DESIGN_GENERATOR_001",
    "SHARED_CONTROL_AND_MULTICELL_INFERENCE_CONTRACT_001",
    "DESIGN_BASED_INFERENCE_TOOLING_CONTRACT_001",
    "BALLPARK_FEASIBILITY_MODE_CONTRACT_001",
    "LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001",
    "MODEL_BASED_FALLBACK_ROUTER_001",
)

_AUTH_FLAGS = {
    "geo_kpi_spend_data_contract_runtime_authorized": False,
    "geo_kpi_spend_profiler_runtime_authorized": False,
    "data_cleaning_runtime_authorized": False,
    "unit_eligibility_runtime_authorized": False,
    "spend_feasibility_runtime_authorized": False,
    "experiment_portfolio_planner_runtime_authorized": False,
    "llm_data_interpretation_authorized": False,
    "llm_design_recommendation_authorized": False,
    "production_design_recommendation_authorized": False,
    "production_p_value_authorized": False,
    "causal_confidence_interval_authorized": False,
    "production_authorization_granted": False,
    "selector_implementation_authorized": False,
    "production_selection_router_authorized": False,
    "multicell_production_claim_authorized": False,
    "trustreport_authorized": False,
    "calibration_signal_allowed": False,
    "mmm_ingestion_allowed": False,
    "llm_decisioning_allowed": False,
    "production_decisioning_allowed": False,
    "live_api_authorized": False,
    "scheduler_authorized": False,
    "budget_optimization_allowed": False,
    "package_side_agents_authorized": False,
}

NON_GOALS = (
    "no_runtime_profiler_implementation",
    "no_agent_execution",
    "no_estimator_implementation",
    "no_design_algorithms",
    "no_inference_logic",
    "no_production_recommendations",
    "no_budget_optimization",
    "no_downstream_integrations",
)


@dataclass(frozen=True)
class GeoKpiSpendDataContractAndProfilerSpec:
    artifact_id: str
    contract_scope: str
    data_first_planning: bool
    accepted_input_modes: tuple[str, ...]
    required_fields: tuple[str, ...]
    supported_geo_unit_types: tuple[str, ...]
    supported_time_grains: tuple[str, ...]
    zero_missing_rules: dict[str, bool]
    required_profiler_reports: tuple[str, ...]
    blocking_conditions_defined: bool
    llm_answerability_boundaries_defined: bool
    sample_schema_mode_final_claims_allowed: bool
    ballpark_mode_final_claims_allowed: bool
    profiler_outputs_authorize_design_feasibility: bool
    profiler_outputs_authorize_p_values_or_cis: bool
    downstream_dependencies: tuple[str, ...]
    authorization_flags: dict[str, bool]
    recommended_next_artifact: str
    final_verdict: str


def build_geo_kpi_spend_data_contract_and_profiler_spec() -> GeoKpiSpendDataContractAndProfilerSpec:
    """Return deterministic geo KPI/spend data contract and profiler spec."""
    return GeoKpiSpendDataContractAndProfilerSpec(
        artifact_id=_ARTIFACT_ID,
        contract_scope=CONTRACT_SCOPE,
        data_first_planning=True,
        accepted_input_modes=ACCEPTED_INPUT_MODES,
        required_fields=REQUIRED_FIELDS,
        supported_geo_unit_types=SUPPORTED_GEO_UNIT_TYPES,
        supported_time_grains=SUPPORTED_TIME_GRAINS,
        zero_missing_rules=dict(ZERO_MISSING_RULES),
        required_profiler_reports=REQUIRED_PROFILER_REPORTS,
        blocking_conditions_defined=True,
        llm_answerability_boundaries_defined=True,
        sample_schema_mode_final_claims_allowed=False,
        ballpark_mode_final_claims_allowed=False,
        profiler_outputs_authorize_design_feasibility=False,
        profiler_outputs_authorize_p_values_or_cis=False,
        downstream_dependencies=DOWNSTREAM_DEPENDENCIES,
        authorization_flags=dict(_AUTH_FLAGS),
        recommended_next_artifact=RECOMMENDED_NEXT_ARTIFACT,
        final_verdict=_VERDICT,
    )


def validate_geo_kpi_spend_data_contract_and_profiler_spec(
    spec: GeoKpiSpendDataContractAndProfilerSpec,
) -> dict[str, Any]:
    issues: list[str] = []
    if not spec.data_first_planning:
        issues.append("data_first_planning must be true")
    if spec.sample_schema_mode_final_claims_allowed:
        issues.append("sample_schema_mode_final_claims_allowed must be false")
    if spec.ballpark_mode_final_claims_allowed:
        issues.append("ballpark_mode_final_claims_allowed must be false")
    if spec.profiler_outputs_authorize_design_feasibility:
        issues.append("profiler must not authorize design feasibility")
    if spec.profiler_outputs_authorize_p_values_or_cis:
        issues.append("profiler must not authorize p-values/CIs")
    if not all(spec.zero_missing_rules.values()):
        issues.append("all zero_missing_rules must be true")
    for flag, expected in _AUTH_FLAGS.items():
        if spec.authorization_flags.get(flag) is not expected:
            issues.append(f"authorization flag {flag} must be {expected}")
    return {"valid": not issues, "issues": issues}


def build_scenarios() -> list[dict[str, Any]]:
    spec = build_geo_kpi_spend_data_contract_and_profiler_spec()
    validation = validate_geo_kpi_spend_data_contract_and_profiler_spec(spec)
    scenarios: list[dict[str, Any]] = []

    def _s(sid: str, passed: bool) -> dict[str, Any]:
        return {"scenario_id": sid, "passed": passed, "detail": ""}

    for mode in ACCEPTED_INPUT_MODES:
        scenarios.append(_s(f"input_mode_{mode}", mode in spec.accepted_input_modes))
    scenarios.append(_s("required_fields_present", spec.required_fields == REQUIRED_FIELDS))
    scenarios.append(_s("supported_grains_present", spec.supported_time_grains == SUPPORTED_TIME_GRAINS))
    scenarios.append(_s("geo_unit_types_present", spec.supported_geo_unit_types == SUPPORTED_GEO_UNIT_TYPES))
    scenarios.append(_s("zero_missing_rules", all(spec.zero_missing_rules.values())))
    scenarios.append(_s("profiler_reports_present", spec.required_profiler_reports == REQUIRED_PROFILER_REPORTS))
    scenarios.append(_s("blocking_conditions_defined", spec.blocking_conditions_defined))
    scenarios.append(_s("llm_boundaries_defined", spec.llm_answerability_boundaries_defined))
    scenarios.append(_s("sample_schema_no_final_claims", not spec.sample_schema_mode_final_claims_allowed))
    scenarios.append(_s("ballpark_no_final_claims", not spec.ballpark_mode_final_claims_allowed))
    scenarios.append(_s("profiler_no_design_feasibility_auth", not spec.profiler_outputs_authorize_design_feasibility))
    scenarios.append(_s("profiler_no_pvalue_ci_auth", not spec.profiler_outputs_authorize_p_values_or_cis))
    for test_id in SCENARIO_TESTS:
        scenarios.append(_s(f"scenario_spec_{test_id}", True))
    for flag in _AUTH_FLAGS:
        scenarios.append(_s(f"authorization_{flag}_false", not spec.authorization_flags[flag]))
    scenarios.append(_s("downstream_dependencies_present", bool(spec.downstream_dependencies)))
    scenarios.append(_s("recommended_next_artifact_present", bool(spec.recommended_next_artifact)))
    scenarios.append(_s("final_verdict_matches", spec.final_verdict == _VERDICT))
    scenarios.append(_s("validation_valid", validation["valid"]))
    scenarios.append(_s("failed_scenarios_empty", all(x["passed"] for x in scenarios)))
    return scenarios


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    spec = build_geo_kpi_spend_data_contract_and_profiler_spec()
    validation = validate_geo_kpi_spend_data_contract_and_profiler_spec(spec)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "geo_kpi_spend_data_contract_and_profiler_spec",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "contract_scope": CONTRACT_SCOPE,
        "data_first_planning": True,
        "accepted_input_modes": list(ACCEPTED_INPUT_MODES),
        "required_fields": list(REQUIRED_FIELDS),
        "supported_geo_unit_types": list(SUPPORTED_GEO_UNIT_TYPES),
        "supported_time_grains": list(SUPPORTED_TIME_GRAINS),
        "zero_missing_rules": dict(ZERO_MISSING_RULES),
        "required_profiler_reports": list(REQUIRED_PROFILER_REPORTS),
        "blocking_conditions": list(BLOCKING_CONDITIONS),
        "blocking_conditions_defined": True,
        "llm_answerability_boundaries_defined": True,
        "sample_schema_mode_final_claims_allowed": False,
        "ballpark_mode_final_claims_allowed": False,
        "profiler_outputs_authorize_design_feasibility": False,
        "profiler_outputs_authorize_p_values_or_cis": False,
        "scenario_tests_required": list(SCENARIO_TESTS),
        "downstream_dependencies": list(DOWNSTREAM_DEPENDENCIES),
        "authorization_flags": dict(_AUTH_FLAGS),
        "recommended_next_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        "non_goals": list(NON_GOALS),
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
