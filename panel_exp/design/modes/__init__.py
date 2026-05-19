"""Built-in design registrations for GeoExperimentDesign.

Registered designs include geo-supported randomizers and geo-unsupported designs
(QuickBlock, MatchedPair, etc.). Registration does not imply ``GeoExperimentDesign``
support — see ``geo_run_supported`` on each ``DesignSpec``.
"""

from __future__ import annotations

from panel_exp.design.assign import (
    BalancedRandomization,
    CompleteRandomization,
    StratifiedRandomization,
    ThinningDesign,
    greedy_match_markets,
)
from panel_exp.design.geo_runner import run_geo_experiment_design
from panel_exp.design.registry import DesignSpec, DesignRegistry

try:
    from panel_exp.design.quickblock import QuickBlock
except ImportError:  # pragma: no cover
    QuickBlock = None  # type: ignore[misc, assignment]

try:
    from panel_exp.design.matched_pair import MatchedPair
except ImportError:  # pragma: no cover
    MatchedPair = None  # type: ignore[misc, assignment]

try:
    from panel_exp.design.trimmed_match import TrimmedMatchDesign
except ImportError:  # pragma: no cover
    TrimmedMatchDesign = None  # type: ignore[misc, assignment]

try:
    from panel_exp.design.supergeos import SupergeoModel
except ImportError:  # pragma: no cover
    SupergeoModel = None  # type: ignore[misc, assignment]


def _geo_spec(
    name: str,
    randomizer_cls: type,
    *,
    aliases: tuple[str, ...] = (),
    geo_run_supported: bool = False,
    supports_rerandomization: bool = True,
    supports_whitelist: bool = True,
    supports_blacklist: bool = True,
    priority: int = 100,
) -> DesignSpec:
    return DesignSpec(
        name=name,
        randomizer_cls=randomizer_cls,
        aliases=aliases,
        run=run_geo_experiment_design,
        output_type="geo_run_design_tuple",
        supports_rerandomization=supports_rerandomization,
        supports_whitelist=supports_whitelist,
        supports_blacklist=supports_blacklist,
        geo_run_supported=geo_run_supported,
        priority=priority,
    )


def register_builtin_designs(registry: DesignRegistry) -> None:
    registry.register(
        _geo_spec(
            "greedy_match_markets",
            greedy_match_markets,
            aliases=("gmm", "greedymatchmarkets"),
            geo_run_supported=True,
            priority=10,
        )
    )
    registry.register(
        _geo_spec(
            "thinningdesign",
            ThinningDesign,
            aliases=("thinning_design", "thinning"),
            geo_run_supported=True,
            priority=20,
        )
    )
    registry.register(
        _geo_spec(
            "balancedrandomization",
            BalancedRandomization,
            aliases=("balanced_randomization", "balanced"),
            geo_run_supported=True,
            priority=30,
        )
    )
    registry.register(
        _geo_spec(
            "completerandomization",
            CompleteRandomization,
            aliases=("complete_randomization", "complete"),
            geo_run_supported=True,
            priority=40,
        )
    )
    registry.register(
        _geo_spec(
            "stratifiedrandomization",
            StratifiedRandomization,
            aliases=("stratified_randomization", "stratified"),
            geo_run_supported=True,
            priority=50,
        )
    )

    if QuickBlock is not None:
        registry.register(
            DesignSpec(
                name="quickblock",
                randomizer_cls=QuickBlock,
                aliases=("quick_block",),
                run=run_geo_experiment_design,
                supports_rerandomization=False,
                supports_whitelist=False,
                supports_blacklist=False,
                geo_run_supported=False,
                priority=200,
            )
        )
    if MatchedPair is not None:
        registry.register(
            DesignSpec(
                name="matchedpair",
                randomizer_cls=MatchedPair,
                aliases=("matched_pair",),
                run=run_geo_experiment_design,
                supports_rerandomization=False,
                supports_whitelist=False,
                supports_blacklist=False,
                geo_run_supported=False,
                priority=210,
            )
        )
    if TrimmedMatchDesign is not None:
        registry.register(
            DesignSpec(
                name="trimmedmatch",
                randomizer_cls=TrimmedMatchDesign,
                aliases=("trimmed_match",),
                run=run_geo_experiment_design,
                supports_rerandomization=False,
                supports_whitelist=False,
                supports_blacklist=False,
                geo_run_supported=False,
                priority=220,
            )
        )
    if SupergeoModel is not None:
        registry.register(
            DesignSpec(
                name="supergeos",
                randomizer_cls=SupergeoModel,
                aliases=("supergeo", "supergeo_model"),
                run=run_geo_experiment_design,
                supports_rerandomization=False,
                supports_whitelist=False,
                supports_blacklist=False,
                geo_run_supported=False,
                priority=230,
            )
        )
