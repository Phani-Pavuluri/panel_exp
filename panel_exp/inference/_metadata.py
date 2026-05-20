"""Attach standardized interval semantics after inference runs (no math changes)."""

from __future__ import annotations

from typing import Any, Optional

import numpy as np

from panel_exp.inference.registry import InferenceModeSpec
from panel_exp.inference_result import InferenceResult, IntervalType


def treatment_window_point_effect(analyzer: Any) -> Optional[float]:
    """Mean treated-minus-counterfactual over the post-treatment window."""
    results = getattr(analyzer, "results", None)
    panel = getattr(analyzer, "panel_data", None)
    if not results or panel is None:
        return None
    if "y" not in results or "y_hat" not in results:
        return None
    pre = panel.treated_start_idxs[0]
    diff = np.asarray(results["y"], dtype=float)[pre:] - np.asarray(results["y_hat"], dtype=float)[pre:]
    if diff.size == 0:
        return None
    return float(np.nanmean(diff))


def sync_inference_metadata(analyzer: Any, spec: InferenceModeSpec) -> None:
    """
    Ensure ``analyzer.inference_result`` and ``results`` interval keys are set.

    Handlers may set ``inference_result`` explicitly (e.g. placebo). Otherwise
    infer from ``spec.path_interval_type`` without altering ``y_lower``/``y_upper``.
    """
    if not hasattr(analyzer, "results") or analyzer.results is None:
        return

    alpha = float(getattr(analyzer, "alpha", 0.05))
    existing = getattr(analyzer, "inference_result", None)

    if isinstance(existing, InferenceResult):
        if existing.path_interval_type is None and spec.path_interval_type is not None:
            existing.path_interval_type = spec.path_interval_type
        existing.attach_to_results(analyzer.results)
        return

    path_type = spec.path_interval_type
    has_path_bounds = bool(
        spec.interval_keys
        and all(k in analyzer.results for k in spec.interval_keys)
    )

    if path_type is None or path_type == IntervalType.UNAVAILABLE:
        if spec.name == "point_estimate":
            reason = "Point estimate only; no uncertainty intervals."
            analyzer.inference_result = InferenceResult.unavailable(
                method=spec.name, alpha=alpha, reason=reason
            )
            return
        if analyzer.results.get("placebo_unsupported"):
            reason = str(analyzer.results["placebo_unsupported"])
        else:
            reason = "Uncertainty intervals not produced for this mode."
        ir = InferenceResult.unavailable(method=spec.name, alpha=alpha, reason=reason)
    elif has_path_bounds:
        ir = InferenceResult.for_path_intervals(
            method=spec.name,
            alpha=alpha,
            path_interval_type=path_type,
            point_estimate=treatment_window_point_effect(analyzer),
        )
    else:
        ir = InferenceResult.unavailable(
            method=spec.name,
            alpha=alpha,
            reason="Expected path bounds missing after inference run.",
        )

    analyzer.inference_result = ir
    ir.attach_to_results(analyzer.results)
