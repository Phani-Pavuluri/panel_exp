"""Registry for estimator maturity metadata (read-only catalog)."""

from __future__ import annotations

from typing import Iterator, List

from panel_exp.method_metadata import (
    MATURITY_DOC,
    EstimatorMetadata,
    EstimatorMaturity,
    InferenceModeMaturityMetadata,
    _ESTIMATOR_CATALOG,
    _INFERENCE_MODE_CATALOG,
    _CLASS_TO_KEY,
    _NAME_TO_META,
    get_inference_mode_metadata,
)


class MethodRegistry:
    """
    Read-only registry of estimator maturity metadata.

    Maturity reflects validation and operational readiness, not statistical
    superiority. Ratings do not block execution.
    """

    def list_estimator_names(self) -> List[str]:
        return sorted(_NAME_TO_META.keys())

    def list_inference_mode_names(self) -> List[str]:
        return sorted(m.name for m in _INFERENCE_MODE_CATALOG)

    def metadata(self, name: str) -> EstimatorMetadata:
        """Lookup by registry name (e.g. ``SCM``, ``TBRRidge``)."""
        try:
            return _NAME_TO_META[name]
        except KeyError as exc:
            raise KeyError(
                f"Unknown estimator {name!r}; known estimators: {self.list_estimator_names()}"
            ) from exc

    def metadata_for_class(self, class_name: str) -> EstimatorMetadata:
        """Lookup by ImpactAnalyzer class name (e.g. ``SyntheticControl``)."""
        try:
            return self.metadata(_CLASS_TO_KEY[class_name])
        except KeyError as exc:
            raise KeyError(
                f"Unknown estimator class {class_name!r}; "
                f"known classes: {sorted(_CLASS_TO_KEY)}"
            ) from exc

    def inference_metadata(self, mode_name: str) -> InferenceModeMaturityMetadata:
        return get_inference_mode_metadata(mode_name)

    def iter_estimators(self) -> Iterator[EstimatorMetadata]:
        yield from _ESTIMATOR_CATALOG

    @property
    def maturity_doc(self) -> str:
        return MATURITY_DOC


_REGISTRY: MethodRegistry | None = None


def get_method_registry() -> MethodRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = MethodRegistry()
    return _REGISTRY


__all__ = [
    "MethodRegistry",
    "get_method_registry",
    "EstimatorMaturity",
    "EstimatorMetadata",
]
