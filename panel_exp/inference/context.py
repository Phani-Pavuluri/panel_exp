"""Shared context for inference mode handlers invoked from ImpactAnalyzer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


from panel_exp.panel_data import PanelDataset


@dataclass
class InferenceRunContext:
    """Bindings passed to each registered inference mode ``run`` handler."""

    analyzer: Any
    panel_data: PanelDataset
    inference_kwargs: dict[str, Any] = field(default_factory=dict)

    @property
    def alpha(self) -> float:
        return self.analyzer.alpha
