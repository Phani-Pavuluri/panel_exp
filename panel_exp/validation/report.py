"""
JSON-serializable validation report artifacts.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from panel_exp.evidence import EVIDENCE_VERSION
from panel_exp.evidence_hash import canonical_json
from panel_exp.validation.metrics import ValidationResult


@dataclass(frozen=True)
class EstimatorValidationReport:
    """
    Summary of synthetic truth recovery experiments.

    Language policy: report recovery under tested scenarios, not estimator correctness.
    """

    evidence_version: str
    scenario_names: List[str]
    results: List[ValidationResult]
    warnings: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    scenario_metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    recovery_statement: str = (
        "Estimators were evaluated for recovery of known synthetic effects "
        "under the listed scenarios only."
    )

    @classmethod
    def build(
        cls,
        *,
        scenario_names: Sequence[str],
        results: Sequence[ValidationResult],
        warnings: Optional[Sequence[str]] = None,
        assumptions: Optional[Sequence[str]] = None,
        scenario_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> "EstimatorValidationReport":
        from panel_exp.validation.scenarios import get_scenario

        meta: Dict[str, Dict[str, Any]] = dict(scenario_metadata or {})
        for name in scenario_names:
            if name in meta:
                continue
            sc = get_scenario(name)
            meta[name] = {
                "scenario_name": sc.scenario_name,
                "n_geos": sc.n_geos,
                "n_periods": sc.n_periods,
                "treatment_start": sc.treatment_start,
                "true_effect": sc.true_effect,
                "effect_type": sc.effect_type,
                "seasonality": sc.seasonality,
                "heterogeneous_effects": sc.heterogeneous_effects,
                "random_state": sc.random_state,
            }

        return cls(
            evidence_version=EVIDENCE_VERSION,
            scenario_names=list(scenario_names),
            results=list(results),
            warnings=list(warnings or []),
            assumptions=list(assumptions or []),
            scenario_metadata=meta,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_version": self.evidence_version,
            "scenario_names": self.scenario_names,
            "scenario_metadata": self.scenario_metadata,
            "results": [r.to_dict() for r in self.results],
            "warnings": self.warnings,
            "assumptions": self.assumptions,
            "recovery_statement": self.recovery_statement,
        }

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def canonical_json(self) -> str:
        return canonical_json(self.to_dict())
