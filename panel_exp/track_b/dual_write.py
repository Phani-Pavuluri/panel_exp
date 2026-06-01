"""M2 dual-write: attach Track B views to RunBundle exports."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from panel_exp.track_b.geo_adapter import (
    GeoAdapterResolveInput,
    extract_resolve_input_from_bundle,
    resolve_geo_adapter_input,
    resolve_geo_adapter_output,
)

CONTRACT_STACK_VERSION = "0.1-draft"
ADAPTER_VERSION = "0.1-m2"


def build_track_b_views(
    *,
    spec: Mapping[str, Any],
    run_artifacts_stub: Mapping[str, Any],
    calibration_signal_binding: Optional[Mapping[str, Any]] = None,
    adapter_output: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Build ``track_b_views`` sidecar from spec slice and adapter resolution."""
    resolved = adapter_output or resolve_geo_adapter_output(
        spec=spec,
        run_artifacts_stub=run_artifacts_stub,
        calibration_signal_binding=calibration_signal_binding,
    )
    signal_ref = _calibration_signal_ref(resolved, calibration_signal_binding)
    return {
        "contract_stack_version": CONTRACT_STACK_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "track_b_views_present": True,
        "experiment_spec_view": dict(spec),
        "adapter_output": dict(resolved),
        "experiment_evidence_view": resolved.get("experiment_evidence") or {},
        "diagnostic_summary_view": resolved.get("diagnostic_summary"),
        "alignment_facts_view": resolved.get("alignment_facts"),
        "calibration_signal_ref": signal_ref,
        "export_status": resolved.get("export_status"),
        "block_reason": resolved.get("block_reason"),
        "partial_reason": resolved.get("partial_reason"),
    }


def build_track_b_views_from_bundle(
    bundle: Mapping[str, Any],
) -> dict[str, Any]:
    """Build sidecar from an existing bundle (extract spec from legacy evidence)."""
    from panel_exp.track_b.bundle_extract import (
        extract_resolve_input_from_bundle,
        extraction_to_sidecar_dict,
    )

    extracted = extract_resolve_input_from_bundle(bundle)
    views = build_track_b_views(
        spec=extracted.input.spec,
        run_artifacts_stub=extracted.input.run_artifacts_stub,
        calibration_signal_binding=extracted.input.calibration_signal_binding,
    )
    views["extraction"] = extraction_to_sidecar_dict(extracted)
    return views


def attach_track_b_views(
    bundle_dict: dict[str, Any],
    *,
    spec: Optional[Mapping[str, Any]] = None,
    run_artifacts_stub: Optional[Mapping[str, Any]] = None,
    calibration_signal_binding: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Return a new bundle dict with ``track_b_views`` attached (non-mutating)."""
    out = dict(bundle_dict)
    if spec is not None and run_artifacts_stub is not None:
        views = build_track_b_views(
            spec=spec,
            run_artifacts_stub=run_artifacts_stub,
            calibration_signal_binding=calibration_signal_binding,
        )
    else:
        views = build_track_b_views_from_bundle(out)
    out["track_b_views"] = views
    return out


def _calibration_signal_ref(
    adapter_output: Mapping[str, Any],
    binding: Optional[Mapping[str, Any]],
) -> Optional[dict[str, Any]]:
    evidence = adapter_output.get("experiment_evidence") or {}
    instrument_id = evidence.get("measurement_instrument_id")
    signal_id = evidence.get("calibration_signal_id")
    signal_version = evidence.get("calibration_signal_version")
    if not instrument_id and not signal_id:
        return None
    ref: dict[str, Any] = {
        "measurement_instrument_id": instrument_id,
        "signal_id": signal_id,
        "signal_version": signal_version,
    }
    if binding and binding.get("lookup_key"):
        ref["lookup_key"] = binding["lookup_key"]
    return ref
