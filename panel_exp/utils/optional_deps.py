"""Lightweight optional dependency probes (no heavy imports at package load)."""

from __future__ import annotations

from typing import Optional


def cvxpy_osqp_skip_reason() -> Optional[str]:
    """
    Return a skip reason when cvxpy/OSQP SCM solver deps are missing, else None.

    Used by tests for SyntheticControlCVXPY / AugSynthCVXPY paths only.
    """
    try:
        import cvxpy  # noqa: F401
    except ImportError:
        return "requires cvxpy optional dependency"
    try:
        import osqp  # noqa: F401
    except ImportError:
        return "requires osqp optional dependency (cvxpy OSQP solver path)"
    return None
