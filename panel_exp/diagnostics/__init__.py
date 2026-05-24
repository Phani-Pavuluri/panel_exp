"""Post-fit estimator diagnostics (classification + routing), separate from core results."""

from panel_exp.diagnostics.estimator_diagnostics import (
    ESTIMATOR_DIAGNOSTIC_PROFILES,
    attach_estimator_diagnostics,
    classify_estimator,
    collect_estimator_diagnostics,
)
from panel_exp.diagnostics.review import DIAGNOSTICS_VERSION, build_estimator_review
from panel_exp.diagnostics.review_flags import (
    attach_review_flags,
    classify_review_flag_support,
    collect_review_flags,
)

__all__ = [
    "DIAGNOSTICS_VERSION",
    "ESTIMATOR_DIAGNOSTIC_PROFILES",
    "attach_estimator_diagnostics",
    "attach_review_flags",
    "build_estimator_review",
    "classify_estimator",
    "classify_review_flag_support",
    "collect_estimator_diagnostics",
    "collect_review_flags",
]
