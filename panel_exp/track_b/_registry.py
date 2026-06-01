"""Static registry tables for geo Track B adapter (M2).

Derived from B3a instrument catalog and B5a golden fixtures — not runtime inference.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

POOLED_RELATIVE_ATT_ID = "geo.relative_att_post.pooled_path.relative"
PLACEBO_NULL_ENVELOPE_ID = "geo.placebo_null_envelope.pooled_path.relative"

_BLOCK = object()

LEGACY_ESTIMAND_MAP: dict[tuple[str, str], Any] = {
    ("relative_att_post", "pooled_path"): POOLED_RELATIVE_ATT_ID,
    ("relative_att_post", "cell_mean"): "geo.relative_att_post.cell_mean.relative",
    ("cumulative_att", ""): "geo.cumulative_att.full_post.absolute",
    ("cumulative_att", "pooled_path"): "geo.cumulative_att.full_post.absolute",
    ("absolute_att_post", "pooled_path"): "geo.mean_post_period_att.post_window.absolute",
    ("unknown", ""): _BLOCK,
    ("unknown", "pooled_path"): _BLOCK,
}


@dataclass(frozen=True)
class ConfigResolution:
    config_alias: str
    instrument_family: str
    inference_method: str
    interval_semantics: str
    instrument_id_template: str
    instrument_geometry_scope: str = "multi_treated_default"


CONFIG_RESOLUTION: dict[str, ConfigResolution] = {
    "SCM_UnitJackKnife": ConfigResolution(
        config_alias="SCM_UnitJackKnife",
        instrument_family="synthetic_control",
        inference_method="unit_jackknife",
        interval_semantics="confidence_interval",
        instrument_id_template=(
            "geo.synthetic_control.unit_jackknife.relative_att_post.{geometry}.confidence_interval"
        ),
    ),
    "TBRRidge_Kfold": ConfigResolution(
        config_alias="TBRRidge_Kfold",
        instrument_family="tbrridge",
        inference_method="kfold",
        interval_semantics="confidence_interval",
        instrument_id_template=(
            "geo.tbrridge.kfold.relative_att_post.{geometry}.confidence_interval"
        ),
    ),
    "AugSynthCVXPY_Point": ConfigResolution(
        config_alias="AugSynthCVXPY_Point",
        instrument_family="augsynth_cvxpy",
        inference_method="point_only",
        interval_semantics="none",
        instrument_id_template=(
            "geo.augsynth_cvxpy.point_only.relative_att_post.{geometry}.none"
        ),
    ),
    "SCM_Placebo": ConfigResolution(
        config_alias="SCM_Placebo",
        instrument_family="synthetic_control",
        inference_method="placebo",
        interval_semantics="placebo_band",
        instrument_id_template=(
            "geo.synthetic_control.placebo.relative_att_post.{geometry}.placebo_band"
        ),
        instrument_geometry_scope="single_treated_only",
    ),
    "DID_Bootstrap": ConfigResolution(
        config_alias="DID_Bootstrap",
        instrument_family="did",
        inference_method="bootstrap",
        interval_semantics="cumulative_att_interval",
        instrument_id_template=(
            "geo.did.bootstrap.relative_att_post.{geometry}.cumulative_att_interval"
        ),
    ),
    "TBRRidge_BlockResidualBootstrap": ConfigResolution(
        config_alias="TBRRidge_BlockResidualBootstrap",
        instrument_family="tbrridge",
        inference_method="block_residual_bootstrap",
        interval_semantics="confidence_interval",
        instrument_id_template=(
            "geo.tbrridge.block_residual_bootstrap.relative_att_post.{geometry}.confidence_interval"
        ),
    ),
}

CALIBRATION_SIGNAL_BY_CONFIG: dict[str, dict[str, Optional[str]]] = {
    "SCM_UnitJackKnife": {"signal_id": "cs-geo-scm-jk-001", "signal_version": "1"},
    "TBRRidge_Kfold": {"signal_id": "cs-geo-tbr-kf-001", "signal_version": "1"},
    "AugSynthCVXPY_Point": {"signal_id": "cs-geo-as-point-001", "signal_version": "1"},
    "SCM_Placebo": {"signal_id": "cs-geo-scm-plac-001", "signal_version": "1"},
    "DID_Bootstrap": {"signal_id": "cs-geo-did-boot-001", "signal_version": "1"},
    "TBRRidge_BlockResidualBootstrap": {
        "signal_id": "cs-geo-tbr-brb-002",
        "signal_version": "2",
    },
}
