"""Context objects for design registry dispatch."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from panel_exp.design.geo_experiment_design import GeoExperimentDesign


@dataclass
class DesignRunContext:
    """Bindings for a single GeoExperimentDesign execution."""

    geo: GeoExperimentDesign
    design_kwargs: dict[str, Any] = field(default_factory=dict)
    # Validation-owned callbacks are injected by validation workflows; the
    # production registry never resolves validation modules itself.
    validate_design: Any = None
    build_contract: Any = None
