"""Track B contract views (M2 dual-write)."""

from panel_exp.track_b.dual_write import (
    ADAPTER_VERSION,
    CONTRACT_STACK_VERSION,
    attach_track_b_views,
    build_track_b_views,
)
from panel_exp.track_b.geo_adapter import (
    resolve_geo_adapter_output,
    resolve_geo_adapter_output_from_bundle,
)

__all__ = [
    "ADAPTER_VERSION",
    "CONTRACT_STACK_VERSION",
    "attach_track_b_views",
    "build_track_b_views",
    "resolve_geo_adapter_output",
    "resolve_geo_adapter_output_from_bundle",
]
