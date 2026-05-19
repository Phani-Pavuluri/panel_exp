"""Registry for geo experiment design dispatch.

A design may be **registered** in the registry without being **geo-run supported**.
Only specs with ``geo_run_supported=True`` may be used via
``GeoExperimentDesign`` / ``run_design``. Use ``list_names()`` for all registered
designs and ``geo_supported_names()`` (or ``GEO_RUN_DESIGN_SUPPORTED``) for the
geo orchestrator allowlist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Union

from panel_exp.design.context import DesignRunContext


class FailureBehavior(str, Enum):
    RAISE = "raise"
    SILENT = "silent"


def design_class_name(cls: type) -> str:
    """Normalized design class name (legacy GeoExperimentDesign convention)."""
    return cls.__name__.lower()


def _normalize_lookup_key(value: str) -> str:
    return value.lower().replace("_", "").replace(" ", "")


# Exact legacy allowlist (substring keys used by GeoExperimentDesign pre-registry).
LEGACY_GEO_RUN_DESIGN_SUPPORTED: frozenset[str] = frozenset(
    {
        "greedy_match_markets",
        "thinningdesign",
        "balancedrandomization",
        "completerandomization",
        "stratifiedrandomization",
    }
)


@dataclass(frozen=True)
class DesignSpec:
    """Declarative metadata and handler for one design implementation."""

    name: str
    randomizer_cls: type
    run: Callable[[DesignRunContext], Any]
    aliases: tuple[str, ...] = ()
    output_type: Optional[str] = "assignment_dict"
    default_kwargs: dict[str, Any] = field(default_factory=dict)
    supports_rerandomization: bool = False
    supports_whitelist: bool = False
    supports_blacklist: bool = False
    geo_run_supported: bool = False
    estimator_requirements: tuple[str, ...] = ()
    failure_behavior: FailureBehavior = FailureBehavior.RAISE
    priority: int = 100


class DesignRegistry:
    def __init__(self) -> None:
        self._by_name: dict[str, DesignSpec] = {}
        self._alias_to_name: dict[str, str] = {}
        self._class_to_name: dict[type, str] = {}

    def _sorted_specs(self) -> list[DesignSpec]:
        return sorted(self._by_name.values(), key=lambda s: (s.priority, s.name))

    def register(self, spec: DesignSpec) -> None:
        if spec.name in self._by_name:
            raise ValueError(f"Design already registered: {spec.name!r}")
        self._by_name[spec.name] = spec
        self._class_to_name[spec.randomizer_cls] = spec.name
        for alias in spec.aliases:
            key = _normalize_lookup_key(alias)
            if key in self._alias_to_name:
                raise ValueError(f"Design alias already registered: {alias!r}")
            self._alias_to_name[key] = spec.name

    def list_names(self) -> list[str]:
        return [s.name for s in self._sorted_specs()]

    def list_keys(self) -> list[str]:
        """Canonical registry keys (includes geo-unsupported designs)."""
        return self.list_names()

    def geo_supported_names(self) -> list[str]:
        """Canonical names supported via GeoExperimentDesign (subset of registered)."""
        return [s.name for s in self._sorted_specs() if s.geo_run_supported]

    def list_registered_names(self) -> list[str]:
        """All registered design names (includes geo-unsupported designs)."""
        return self.list_names()

    def resolve(self, design: Union[str, type]) -> DesignSpec:
        if isinstance(design, type):
            if design in self._class_to_name:
                return self._by_name[self._class_to_name[design]]
            normalized = _normalize_lookup_key(design.__name__)
            for spec in self._sorted_specs():
                spec_key = _normalize_lookup_key(spec.name)
                if spec_key in normalized or normalized in spec_key:
                    return spec
                if spec.randomizer_cls.__name__.lower() == design.__name__.lower():
                    return spec
            supported = ", ".join(self.geo_supported_names())
            raise ValueError(
                f"Unsupported design: {design.__name__!r}. Supported designs: [{supported}]"
            )

        key = _normalize_lookup_key(design)
        if key in self._alias_to_name:
            return self._by_name[self._alias_to_name[key]]
        if key in {_normalize_lookup_key(n) for n in self._by_name}:
            for name, spec in self._by_name.items():
                if _normalize_lookup_key(name) == key:
                    return spec
        if design in self._by_name:
            return spec
        supported = ", ".join(self.list_names())
        raise ValueError(
            f"Unsupported design: {design!r}. Supported designs: [{supported}]"
        )

    def validate_geo_capabilities(self, spec: DesignSpec, geo: Any) -> None:
        """Raise when GeoExperimentDesign requests unsupported capabilities."""
        if not spec.geo_run_supported:
            supported = ", ".join(self.geo_supported_names())
            raise ValueError(
                f"{spec.randomizer_cls.__name__} is not supported via GeoExperimentDesign.run_design. "
                f"Use the design class directly or select one of: {supported}."
            )
        if geo.design_kwargs.get("use_rerandomization") is False:
            if not spec.supports_rerandomization:
                raise ValueError(f"{spec.name} does not support rerandomization")
        has_whitelist = bool(
            geo.test_whitelist or geo.control_whitelist
        )
        has_blacklist = bool(
            geo.test_blacklist
            or geo.control_blacklist
            or geo.control_test_blacklist
        )
        if has_whitelist and not spec.supports_whitelist:
            raise ValueError(f"{spec.name} does not support whitelist constraints")
        if has_blacklist and not spec.supports_blacklist:
            raise ValueError(f"{spec.name} does not support blacklist constraints")

    def run(
        self,
        design: Union[str, type],
        geo: Any,
        design_kwargs: Optional[dict[str, Any]] = None,
    ) -> Any:
        spec = self.resolve(design)
        self.validate_geo_capabilities(spec, geo)
        ctx = DesignRunContext(
            geo=geo,
            design_kwargs=design_kwargs if design_kwargs is not None else {},
        )
        result = spec.run(ctx)
        if result is None:
            raise ValueError(
                f"Design {spec.name!r} returned None; assignment pipeline must return outputs."
            )
        return result


_REGISTRY: Optional[DesignRegistry] = None


def get_design_registry() -> DesignRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        from panel_exp.design.modes import register_builtin_designs

        _REGISTRY = DesignRegistry()
        register_builtin_designs(_REGISTRY)
        assert_legacy_geo_registry_alignment()
    return _REGISTRY


def geo_run_design_supported() -> frozenset[str]:
    """Legacy ``GEO_RUN_DESIGN_SUPPORTED`` export (exact pre-refactor allowlist)."""
    return LEGACY_GEO_RUN_DESIGN_SUPPORTED


def assert_legacy_geo_registry_alignment() -> None:
    """Ensure geo_run_supported registry entries match the legacy allowlist."""
    reg = get_design_registry()
    supported = {_normalize_lookup_key(n) for n in reg.geo_supported_names()}
    legacy = {_normalize_lookup_key(n) for n in LEGACY_GEO_RUN_DESIGN_SUPPORTED}
    if supported != legacy:
        raise RuntimeError(
            f"Registry geo-supported names {sorted(supported)} "
            f"!= legacy {sorted(legacy)}"
        )
