"""Pytest helpers for Bayesian / JAX tests."""

from __future__ import annotations

import pytest

from panel_exp.utils.optional_deps import jax_stack_skip_reason


def require_compatible_jax() -> None:
    """Skip with a clear reason when JAX is missing or jax/jaxlib versions mismatch."""
    reason = jax_stack_skip_reason()
    if reason is not None:
        pytest.skip(reason)
