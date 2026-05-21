"""
Synthetic truth validation infrastructure.

Evaluates whether estimators recover known causal effects under controlled
scenarios. This package does not implement estimators or change inference math.
"""

from panel_exp.validation.metrics import ValidationResult
from panel_exp.validation.recovery_metrics import RecoveryResult, SimulationRecord
from panel_exp.validation.recovery_runner import (
    RecoveryRunner,
    merge_validation_metadata,
    run_recovery_battery,
)
from panel_exp.validation.report import EstimatorValidationReport
from panel_exp.validation.runner import (
    SUPPORTED_ESTIMATORS,
    run_estimator_validation,
    run_scenario_validation,
)
from panel_exp.validation.scenarios import SCENARIO_REGISTRY, get_scenario
from panel_exp.validation.synthetic_scenarios import (
    ESTIMATOR_RECOVERY_SCENARIOS,
    RECOVERY_SCENARIO_REGISTRY,
    get_recovery_scenario,
    scenarios_for_estimator,
)
from panel_exp.validation.synthetic_world import SyntheticScenario, SyntheticWorld

__all__ = [
    "ESTIMATOR_RECOVERY_SCENARIOS",
    "EstimatorValidationReport",
    "RECOVERY_SCENARIO_REGISTRY",
    "RecoveryResult",
    "RecoveryRunner",
    "SCENARIO_REGISTRY",
    "SUPPORTED_ESTIMATORS",
    "SimulationRecord",
    "SyntheticScenario",
    "SyntheticWorld",
    "ValidationResult",
    "get_recovery_scenario",
    "get_scenario",
    "merge_validation_metadata",
    "run_estimator_validation",
    "run_recovery_battery",
    "run_scenario_validation",
    "scenarios_for_estimator",
]
