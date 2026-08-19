"""
panel_exp — geo-panel experimentation (design, methods, inference).
"""

__version__ = "0.2.1"

from panel_exp.design import GEO_RUN_DESIGN_SUPPORTED, get_design_registry
from panel_exp.evidence import DesignEvidence, ExperimentEvidence, InferenceEvidence
from panel_exp.inference_result import InferenceResult, IntervalType
from panel_exp.panel_data import PanelDataset, TimePeriod, long_df_to_paneldataset
from panel_exp.method_metadata import EstimatorMaturity
from panel_exp.method_registry import get_method_registry
from panel_exp.spec import (
    DesignMethod,
    DesignSpec,
    ExperimentSpec,
    InterferenceAssumption,
    class_name_to_design_method,
    spec_from_geo_design,
)

# Design
from panel_exp.design.assign import (
    CompleteRandomization,
    Rerandomization,
    StratifiedRandomization,
    ThinningDesign,
    greedy_match_markets,
)
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.design.power import PowerAnalysis
from panel_exp.design.validation import DesignValidationResult, ValidationStatus, validate_design

__all__ = [
    "__version__",
    "PanelDataset",
    "TimePeriod",
    "long_df_to_paneldataset",
    "DesignSpec",
    "ExperimentSpec",
    "DesignMethod",
    "InterferenceAssumption",
    "EstimatorMaturity",
    "get_method_registry",
    "class_name_to_design_method",
    "spec_from_geo_design",
    "InferenceResult",
    "IntervalType",
    "DesignEvidence",
    "InferenceEvidence",
    "ExperimentEvidence",
    "build_experiment_card",
    "attach_experiment_card_markdown",
    "get_design_registry",
    "GEO_RUN_DESIGN_SUPPORTED",
    "BalancedRandomization",
    "CompleteRandomization",
    "StratifiedRandomization",
    "ThinningDesign",
    "Rerandomization",
    "greedy_match_markets",
    "GeoExperimentDesign",
    "PowerAnalysis",
    "validate_design",
    "DesignValidationResult",
    "ValidationStatus",
]


def build_experiment_card(*args, **kwargs):
    """Lazily build a human-readable card without importing advisory policy."""
    module = __import__("panel_exp.artifacts.experiment_card", fromlist=["build_experiment_card"])
    return module.build_experiment_card(*args, **kwargs)


def attach_experiment_card_markdown(*args, **kwargs):
    """Lazily attach card markdown without widening production imports."""
    module = __import__("panel_exp.artifacts.experiment_card", fromlist=["attach_experiment_card_markdown"])
    return module.attach_experiment_card_markdown(*args, **kwargs)


def __getattr__(name: str):
    """Lazy imports for heavy method modules."""
    if name == "BalancedRandomization":
        from panel_exp.design.assign import BalancedRandomization

        return BalancedRandomization
    if name == "SyntheticControl":
        from panel_exp.methods.scm import SyntheticControl

        return SyntheticControl
    if name == "TBR":
        from panel_exp.methods.tbr import TBR

        return TBR
    if name == "TBRRidge":
        from panel_exp.methods.tbr import TBRRidge

        return TBRRidge
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Bind the public design class after package initialization so imports from the
# package root remain stable even when Track B is imported first.
from panel_exp.design.assign import BalancedRandomization  # noqa: E402,F401
