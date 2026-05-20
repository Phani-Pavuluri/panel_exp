"""
JSON-serializable validation report artifacts.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from panel_exp.evidence_hash import canonical_json
from panel_exp.validation.metrics import ValidationMetrics
from panel_exp.validation.synthetic_world import SyntheticScenario

REPORT_VERSION = "1.0"

RECOVERY_STATEMENT = (
    "Estimators were validated under the tested synthetic scenarios only; "
    "this does not establish general estimator validity."
)


@dataclass(frozen=True)
class EstimatorValidationReport:
    """Summary of synthetic truth recovery experiments."""

    report_version: str
    created_at: str
    scenarios: List[Dict[str, Any]]
    estimator_configs: List[Dict[str, Any]]
    metrics: List[ValidationMetrics]
    failures: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recovery_statement: str = RECOVERY_STATEMENT

    @classmethod
    def build(
        cls,
        *,
        scenarios: Sequence[SyntheticScenario],
        estimator_configs: Sequence[Any],
        metrics: Sequence[ValidationMetrics],
        failures: Optional[Sequence[Dict[str, str]]] = None,
        warnings: Optional[Sequence[str]] = None,
        created_at: Optional[str] = None,
    ) -> "EstimatorValidationReport":
        ts = created_at or datetime.now(timezone.utc).isoformat()
        return cls(
            report_version=REPORT_VERSION,
            created_at=ts,
            scenarios=[_scenario_to_dict(s) for s in scenarios],
            estimator_configs=[_config_to_dict(c) for c in estimator_configs],
            metrics=list(metrics),
            failures=list(failures or []),
            warnings=list(warnings or []),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_version": self.report_version,
            "created_at": self.created_at,
            "scenarios": self.scenarios,
            "estimator_configs": self.estimator_configs,
            "metrics": [m.to_dict() for m in self.metrics],
            "failures": self.failures,
            "warnings": self.warnings,
            "recovery_statement": self.recovery_statement,
        }

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def canonical_payload(self) -> Dict[str, Any]:
        """Deterministic payload excluding ``created_at``."""
        payload = self.to_dict()
        payload.pop("created_at", None)
        return payload

    def canonical_json(self) -> str:
        return canonical_json(self.canonical_payload())


def _scenario_to_dict(scenario: SyntheticScenario) -> Dict[str, Any]:
    return {
        "name": scenario.name,
        "n_geos": scenario.n_geos,
        "n_periods": scenario.n_periods,
        "treatment_start": scenario.treatment_start,
        "treated_units": list(scenario.treated_units),
        "true_effect": scenario.true_effect,
        "effect_type": scenario.effect_type,
        "baseline_level": scenario.baseline_level,
        "seasonality_amplitude": scenario.seasonality_amplitude,
        "heterogeneous_effects": scenario.heterogeneous_effects,
        "random_state": scenario.random_state,
    }


def _config_to_dict(config: Any) -> Dict[str, Any]:
    return {
        "estimator_name": config.estimator_name,
        "inference": config.inference,
        "run_kwargs": dict(config.run_kwargs),
        "supports_significance": config.supports_significance,
    }
