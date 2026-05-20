"""Registry for ImpactAnalyzer inference dispatch."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Sequence, Union

from panel_exp.inference.context import InferenceRunContext
from panel_exp.inference_result import IntervalType


class FailureBehavior(str, Enum):
    """How an inference mode reports unsupported or invalid inputs."""

    RAISE = "raise"
    RAISE_IF_STRICT = "raise_if_strict"
    SILENT = "silent"


EstimatorCheck = Callable[[Any], Optional[str]]


@dataclass(frozen=True)
class InferenceModeSpec:
    """Declarative metadata and handler for one inference mode."""

    name: str
    run: Callable[[InferenceRunContext], None]
    aliases: tuple[str, ...] = ()
    output_keys: tuple[str, ...] = ("times", "y", "y_hat")
    default_kwargs: dict[str, Any] = field(default_factory=dict)
    estimator_check: Optional[EstimatorCheck] = None
    failure_behavior: FailureBehavior = FailureBehavior.RAISE
    interval_keys: tuple[str, ...] = ()
    path_interval_type: Optional[IntervalType] = None


class InferenceRegistry:
    def __init__(self) -> None:
        self._by_key: dict[Optional[str], InferenceModeSpec] = {}
        self._alias_to_key: dict[str, Optional[str]] = {}

    def register(self, spec: InferenceModeSpec) -> None:
        key: Optional[str] = spec.name if spec.name != "point_estimate" else None
        if key in self._by_key:
            raise ValueError(f"Inference mode already registered: {spec.name!r}")
        self._by_key[key] = spec
        for alias in spec.aliases:
            if alias in self._alias_to_key:
                raise ValueError(f"Inference alias already registered: {alias!r}")
            self._alias_to_key[alias] = key

    def list_mode_keys(self) -> list[Optional[str]]:
        """Registered inference keys in stable registration order."""
        return list(self._by_key.keys())

    def list_mode_names(self) -> list[str]:
        """Human-readable mode names in stable registration order."""
        return [self._by_key[k].name for k in self.list_mode_keys()]

    def resolve(self, inference: Optional[Union[str, Any]]) -> InferenceModeSpec:
        if inference is None:
            spec = self._by_key.get(None)
            if spec is None:
                raise KeyError("point_estimate (None) is not registered")
            return spec
        if isinstance(inference, str) and inference in self._alias_to_key:
            return self._by_key[self._alias_to_key[inference]]
        if inference in self._by_key:
            return self._by_key[inference]
        raise NotImplementedError(f"{inference} is not a supported inference method")

    def run(
        self,
        inference: Optional[Union[str, Any]],
        analyzer: Any,
        panel_data: Any,
        inference_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        spec = self.resolve(inference)
        if spec.estimator_check is not None:
            reason = spec.estimator_check(analyzer)
            if reason is not None:
                if spec.failure_behavior == FailureBehavior.RAISE:
                    raise ValueError(reason)
                if spec.failure_behavior == FailureBehavior.RAISE_IF_STRICT:
                    strict = (inference_kwargs or {}).get("placebo_strict", True)
                    if strict:
                        raise ValueError(reason)

        ctx = InferenceRunContext(
            analyzer=analyzer,
            panel_data=panel_data,
            inference_kwargs=inference_kwargs if inference_kwargs is not None else {},
        )
        spec.run(ctx)
        from panel_exp.inference._metadata import sync_inference_metadata

        sync_inference_metadata(analyzer, spec)


_REGISTRY: Optional[InferenceRegistry] = None


def get_inference_registry() -> InferenceRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        from panel_exp.inference.modes import register_builtin_inference_modes

        _REGISTRY = InferenceRegistry()
        register_builtin_inference_modes(_REGISTRY)
    return _REGISTRY
