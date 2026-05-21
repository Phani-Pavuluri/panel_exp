"""
Synthetic truth validation infrastructure.

Evaluates whether estimators recover known causal effects under controlled
scenarios. Not wired into production design or inference paths.
"""

from panel_exp.validation.calibration_report import (
    CalibrationReport,
    attach_calibration_report,
    build_calibration_report,
    calibration_markdown_from_mapping,
    compute_calibration_warnings,
)
from panel_exp.validation.metrics import (
    ReplicationOutcome,
    ValidationMetrics,
    aggregate_outcomes,
)
from panel_exp.validation.recovery_metrics import RecoveryResult, SimulationRecord
from panel_exp.validation.recovery_runner import (
    RecoveryRunner,
    merge_validation_metadata,
    run_recovery_battery,
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
from panel_exp.validation.synthetic_scenarios import (
    ESTIMATOR_RECOVERY_SCENARIOS,
    RECOVERY_SCENARIO_REGISTRY,
    get_recovery_scenario,
    scenarios_for_estimator,
)
from panel_exp.validation.synthetic_world import (
    OUTCOME_COL,
    TIME_COL,
    UNIT_COL,
    SyntheticScenario,
    SyntheticWorld,
)

__all__ = [
    "CalibrationReport",
    "ESTIMATOR_RECOVERY_SCENARIOS",
    "EstimatorConfig",
    "EstimatorValidationReport",
    "EstimatorValidationRunner",
    "OUTCOME_COL",
    "RECOVERY_SCENARIO_REGISTRY",
    "REPORT_VERSION",
    "RecoveryResult",
    "RecoveryRunner",
    "ReplicationOutcome",
    "SCENARIO_REGISTRY",
    "SimulationRecord",
    "TIME_COL",
    "UNIT_COL",
    "SyntheticScenario",
    "SyntheticWorld",
    "ValidationMetrics",
    "aggregate_outcomes",
    "attach_calibration_report",
    "build_calibration_report",
    "calibration_markdown_from_mapping",
    "compute_calibration_warnings",
    "default_estimator_configs",
    "get_recovery_scenario",
    "get_scenario",
    "merge_validation_metadata",
    "run_estimator_validation",
    "run_recovery_battery",
    "run_scenario_validation",
    "scenarios_for_estimator",
]
