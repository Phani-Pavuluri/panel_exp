"""Tests for JAX optional-dependency guard helpers."""

from __future__ import annotations

import pytest

from panel_exp.utils import optional_deps


def test_jax_jaxlib_version_mismatch_detects_skew():
    reason = optional_deps._jax_jaxlib_version_mismatch_reason("0.4.29", "0.6.2")
    assert reason is not None
    assert "incompatible" in reason
    assert "0.4.29" in reason
    assert "0.6.2" in reason


def test_jax_jaxlib_version_mismatch_none_when_aligned():
    assert optional_deps._jax_jaxlib_version_mismatch_reason("0.4.29", "0.4.29") is None


def test_jax_stack_skip_reason_none_when_compatible():
    reason = optional_deps.jax_stack_skip_reason()
    if reason is not None:
        pytest.skip(f"JAX stack not usable in this environment: {reason}")
    assert reason is None


def test_jax_stack_skip_reason_reports_missing_jax(monkeypatch):
    monkeypatch.setattr(optional_deps.importlib.util, "find_spec", lambda name: None)
    assert optional_deps.jax_stack_skip_reason() == "jax not installed"


@pytest.mark.parametrize(
    "jax_version,jaxlib_version",
    [("0.4.29", "0.6.2"), ("0.4.28", "0.6.1")],
)
def test_jax_stack_skip_reason_reports_incompatible_versions(
    monkeypatch, jax_version: str, jaxlib_version: str
):
    versions = {"jax": jax_version, "jaxlib": jaxlib_version}

    def fake_version(name: str) -> str:
        return versions[name]

    monkeypatch.setattr(optional_deps, "_package_version", fake_version)
    monkeypatch.setattr(
        optional_deps.importlib.util,
        "find_spec",
        lambda name: object() if name in {"jax", "jaxlib"} else None,
    )
    reason = optional_deps.jax_stack_skip_reason()
    assert reason is not None
    assert "incompatible" in reason
