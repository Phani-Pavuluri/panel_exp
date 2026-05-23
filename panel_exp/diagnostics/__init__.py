"""Post-fit estimator diagnostics (classification + routing)."""

from panel_exp.diagnostics.estimator_diagnostics import (
    ESTIMATOR_DIAGNOSTIC_PROFILES,
    attach_estimator_diagnostics,
    classify_estimator,
    collect_estimator_diagnostics,
)

__all__ = [
    "ESTIMATOR_DIAGNOSTIC_PROFILES",
    "attach_estimator_diagnostics",
    "classify_estimator",
    "collect_estimator_diagnostics",
]
