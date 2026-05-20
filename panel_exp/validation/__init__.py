"""
Synthetic truth validation infrastructure.

Evaluates whether estimators recover known causal effects under controlled
scenarios. This package does not implement estimators or change inference math.
"""

from panel_exp.validation.metrics import ValidationResult
from panel_exp.validation.report import EstimatorValidationReport
from panel_exp.validation.runner import (
    SUPPORTED_ESTIMATORS,
    run_estimator_validation,
    run_scenario_validation,
)
from panel_exp.validation.scenarios import SCENARIO_REGISTRY, get_scenario
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld

__all__ = [
    "EstimatorValidationReport",
    "SCENARIO_REGISTRY",
    "SUPPORTED_ESTIMATORS",
    "SyntheticScenario",
    "SyntheticWorld",
    "ValidationResult",
    "get_scenario",
    "run_estimator_validation",
    "run_scenario_validation",
]
