"""Track B contract views (M2 dual-write)."""

from panel_exp.track_b.dual_write import (
    ADAPTER_VERSION,
    CONTRACT_STACK_VERSION,
    attach_track_b_views,
    build_track_b_views,
)
from panel_exp.track_b.bundle_extract import (
    BundleExtractionResult,
    extract_resolve_input_from_bundle,
)
from panel_exp.track_b.export import build_geo_run_artifact_bundle
from panel_exp.track_b.geo_adapter import (
    resolve_geo_adapter_output,
    resolve_geo_adapter_output_from_bundle,
)
from panel_exp.track_b.trust_report import (
    TRUST_REPORT_VERSION,
    TrackETriangulationAttachment,
    TrustComposeContext,
    attach_trust_report_to_views,
    compose_trust_report,
    trust_report_to_dict,
)
from panel_exp.track_b.triangulation import (
    TriangulationOutcome,
    evaluate_triangulation,
    evaluate_triangulation_fixture,
)

__all__ = [
    "ADAPTER_VERSION",
    "CONTRACT_STACK_VERSION",
    "BundleExtractionResult",
    "attach_track_b_views",
    "build_geo_run_artifact_bundle",
    "build_track_b_views",
    "extract_resolve_input_from_bundle",
    "resolve_geo_adapter_output",
    "resolve_geo_adapter_output_from_bundle",
    "TRUST_REPORT_VERSION",
    "TrackETriangulationAttachment",
    "TriangulationOutcome",
    "TrustComposeContext",
    "attach_trust_report_to_views",
    "compose_trust_report",
    "evaluate_triangulation",
    "evaluate_triangulation_fixture",
    "trust_report_to_dict",
]
