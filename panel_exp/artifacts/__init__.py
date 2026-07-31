"""Human-readable experiment artifacts derived from evidence objects."""

from panel_exp.artifacts.experiment_card import (
    CARD_VERSION,
    ExperimentCard,
    attach_experiment_card_markdown,
    build_experiment_card,
)
from panel_exp.artifacts.geox_governed_readout_builder import build_geox_governed_readout_package_entrypoint
from panel_exp.artifacts.run_bundle import (
    BUNDLE_VERSION,
    RunArtifactBundle,
    build_run_artifact_bundle,
    write_run_artifact_bundle_json,
    write_run_artifact_bundle_markdown,
)

__all__ = [
    "BUNDLE_VERSION",
    "CARD_VERSION",
    "ExperimentCard",
    "RunArtifactBundle",
    "attach_experiment_card_markdown",
    "build_geox_governed_readout_package_entrypoint",
    "build_experiment_card",
    "build_run_artifact_bundle",
    "export_geo_run_bundle",
    "write_run_artifact_bundle_json",
    "write_run_artifact_bundle_markdown",
]


def export_geo_run_bundle(*args, **kwargs):
    """Lazily dispatch to the canonical GeoX export entrypoint.

    Keeping this package-root re-export lazy avoids importing Track B while
    ``panel_exp.track_b._registry`` is still being initialized.
    """
    from panel_exp.artifacts.geo_run_export import export_geo_run_bundle as _export

    return _export(*args, **kwargs)
