"""
Synthetic truth validation infrastructure.

Evaluates whether estimators recover known causal effects under controlled
scenarios. Not wired into production design or inference paths.
"""

from panel_exp.validation.metrics import (
    ReplicationOutcome,
    ValidationMetrics,
    aggregate_outcomes,
)
from panel_exp.validation.report import (
    REPORT_VERSION,
    EstimatorValidationReport,
)
from panel_exp.validation.runner import (
    EstimatorConfig,
    EstimatorValidationRunner,
    default_estimator_configs,
    run_estimator_validation,
    run_scenario_validation,
)
from panel_exp.validation.scenarios import SCENARIO_REGISTRY, get_scenario
from panel_exp.validation.synthetic_world import (
    OUTCOME_COL,
    TIME_COL,
    UNIT_COL,
    SyntheticScenario,
    SyntheticWorld,
)

__all__ = [
    "OUTCOME_COL",
    "TIME_COL",
    "UNIT_COL",
    "REPORT_VERSION",
    "EstimatorConfig",
    "EstimatorValidationReport",
    "EstimatorValidationRunner",
    "ReplicationOutcome",
    "SCENARIO_REGISTRY",
    "SyntheticScenario",
    "SyntheticWorld",
    "ValidationMetrics",
    "aggregate_outcomes",
    "default_estimator_configs",
    "get_scenario",
    "run_estimator_validation",
    "run_scenario_validation",
]
