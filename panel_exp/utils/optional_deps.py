"""Lightweight optional dependency probes (no heavy imports at package load)."""

from __future__ import annotations

import importlib.util
from importlib.metadata import PackageNotFoundError, version
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


def _package_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def jax_stack_skip_reason() -> str | None:
    """Return a pytest skip reason when the JAX stack is missing or incompatible."""
    if importlib.util.find_spec("jax") is None:
        return "jax not installed"
    if importlib.util.find_spec("jaxlib") is None:
        return "jaxlib not installed"

    jax_version = _package_version("jax")
    jaxlib_version = _package_version("jaxlib")
    if jax_version is None or jaxlib_version is None:
        return "jax or jaxlib not installed"

    mismatch = _jax_jaxlib_version_mismatch_reason(jax_version, jaxlib_version)
    if mismatch is not None:
        return mismatch

    try:
        import jax  # noqa: F401
    except Exception as exc:
        return f"jax import failed: {exc}"
    return None


def _jax_jaxlib_version_mismatch_reason(jax_version: str, jaxlib_version: str) -> str | None:
    """Detect common jax/jaxlib skew before import (e.g. jax 0.4.x + jaxlib 0.6.x)."""
    jax_parts = jax_version.split(".")
    jaxlib_parts = jaxlib_version.split(".")
    if len(jax_parts) < 2 or len(jaxlib_parts) < 2:
        return None
    if jax_parts[:2] != jaxlib_parts[:2]:
        return (
            f"jax {jax_version} and jaxlib {jaxlib_version} are incompatible; "
            "pin matching versions (e.g. jax==0.4.29 and jaxlib==0.4.29)"
        )
    return None
