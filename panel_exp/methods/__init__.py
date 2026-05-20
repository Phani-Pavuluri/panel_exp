"""
Panel causal estimators.

Heavy optional dependencies (JAX, arviz, etc.) are not imported at package load.
Import estimators from their modules directly, e.g. ``from panel_exp.methods.tbr import TBRRidge``.
"""

from panel_exp.methods.scm import SyntheticControl
from panel_exp.methods.tbr import TBR, TBRRidge

__all__ = ["SyntheticControl", "TBR", "TBRRidge"]
