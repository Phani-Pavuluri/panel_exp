"""Pytest markers for cvxpy/OSQP optional SCM solver dependencies."""

from __future__ import annotations

import pytest

from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason

_skip_reason = cvxpy_osqp_skip_reason() or "requires cvxpy/osqp optional dependencies"

skip_without_cvxpy_osqp = pytest.mark.skipif(
    cvxpy_osqp_skip_reason() is not None,
    reason=_skip_reason,
)
