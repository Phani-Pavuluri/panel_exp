"""
Standardized inference output metadata.

Every interval-like output is labeled explicitly (confidence, credible, conformal,
placebo band, or unavailable). Numeric ``y_lower`` / ``y_upper`` are unchanged;
only reporting semantics are standardized.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class IntervalType(str, Enum):
    CONFIDENCE_INTERVAL = "confidence_interval"
    CREDIBLE_INTERVAL = "credible_interval"
    CONFORMAL_INTERVAL = "conformal_interval"
    PLACEBO_BAND = "placebo_band"
    UNAVAILABLE = "unavailable"


_INTERVAL_LABELS: Dict[IntervalType, str] = {
    IntervalType.CONFIDENCE_INTERVAL: "confidence interval",
    IntervalType.CREDIBLE_INTERVAL: "credible interval",
    IntervalType.CONFORMAL_INTERVAL: "conformal prediction interval",
    IntervalType.PLACEBO_BAND: "placebo null band",
    IntervalType.UNAVAILABLE: "unavailable",
}


@dataclass
class InferenceResult:
    """
    Typed uncertainty summary attached to ImpactAnalyzer results.

  ``interval_type`` describes the primary inferential summary (often a scalar
    effect). ``path_interval_type`` describes ``results['y_lower']`` /
    ``results['y_upper']`` when they differ (e.g. placebo path band vs inversion CI).
    """

    point_estimate: Optional[float] = None
    interval_lower: Optional[float] = None
    interval_upper: Optional[float] = None
    interval_type: IntervalType = IntervalType.UNAVAILABLE
    path_interval_type: Optional[IntervalType] = None
    effect_interval_type: Optional[IntervalType] = None
    alpha: float = 0.05
    method: Optional[str] = None
    assumptions: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    @property
    def confidence_level(self) -> float:
        return 1.0 - self.alpha

    def effective_path_interval_type(self) -> IntervalType:
        """Semantics of ``y_lower`` / ``y_upper`` in ``results``."""
        if self.path_interval_type is not None:
            return self.path_interval_type
        return self.interval_type

    @property
    def intervals_available(self) -> bool:
        return self.effective_path_interval_type() != IntervalType.UNAVAILABLE

    @property
    def interval_label(self) -> str:
        return _INTERVAL_LABELS[self.effective_path_interval_type()]

    @property
    def effect_interval_label(self) -> Optional[str]:
        if self.effect_interval_type is None:
            if self.interval_type != self.effective_path_interval_type():
                return _INTERVAL_LABELS.get(self.interval_type)
            return None
        return _INTERVAL_LABELS.get(self.effect_interval_type)

    def attach_to_results(self, results: Dict[str, Any]) -> None:
        """Mirror typed semantics into legacy ``results`` keys (no numeric changes)."""
        path_type = self.effective_path_interval_type()
        results["interval_type"] = path_type.value
        results["intervals_available"] = self.intervals_available
        results["inference_metadata"] = self.to_dict()
        effect_type = self.effect_interval_type
        if effect_type is None and self.interval_type != path_type:
            effect_type = self.interval_type
        if effect_type is not None and effect_type != IntervalType.UNAVAILABLE:
            results["effect_interval_type"] = effect_type.value

    def to_dict(self) -> Dict[str, Any]:
        path_type = self.effective_path_interval_type()
        out: Dict[str, Any] = {
            "point_estimate": self.point_estimate,
            "interval_lower": self.interval_lower,
            "interval_upper": self.interval_upper,
            "interval_type": self.interval_type.value,
            "path_interval_type": path_type.value,
            "alpha": self.alpha,
            "confidence_level": self.confidence_level,
            "method": self.method,
            "assumptions": self.assumptions,
            "warnings": self.warnings,
            "intervals_available": self.intervals_available,
            "interval_label": self.interval_label,
        }
        if self.effect_interval_type is not None:
            out["effect_interval_type"] = self.effect_interval_type.value
            out["effect_interval_label"] = self.effect_interval_label
        elif self.interval_type != path_type:
            out["effect_interval_type"] = self.interval_type.value
            out["effect_interval_label"] = _INTERVAL_LABELS.get(self.interval_type)
        return out

    @classmethod
    def unavailable(
        cls,
        *,
        method: Optional[str],
        alpha: float,
        reason: str,
        assumptions: Optional[Dict[str, Any]] = None,
    ) -> "InferenceResult":
        return cls(
            interval_type=IntervalType.UNAVAILABLE,
            path_interval_type=IntervalType.UNAVAILABLE,
            alpha=alpha,
            method=method,
            assumptions=assumptions or {},
            warnings=[reason],
        )

    @classmethod
    def for_path_intervals(
        cls,
        *,
        method: str,
        alpha: float,
        path_interval_type: IntervalType,
        point_estimate: Optional[float] = None,
        assumptions: Optional[Dict[str, Any]] = None,
    ) -> "InferenceResult":
        """Path ``y_lower``/``y_upper`` share one interval semantics."""
        return cls(
            point_estimate=point_estimate,
            interval_type=path_interval_type,
            path_interval_type=path_interval_type,
            alpha=alpha,
            method=method,
            assumptions=assumptions or {},
        )
