"""Validation-owned orchestrated design runs with guardrail evidence.

This module wires existing reviewed pieces and changes no production
behavior: ordinary ``GeoExperimentDesign.run_design()`` is untouched.
Callers that need guardrail-bearing evidence invoke :func:`run_validated_design`
explicitly with a builder; nothing is emitted by default.
"""

from __future__ import annotations

import dataclasses
from typing import Any

from panel_exp.design.context import DesignRunContext
from panel_exp.design.geo_experiment_design import GeoExperimentDesign
from panel_exp.validation.design_guardrail_enforcement_001 import (
    build_producer_guardrail_bundle,
)


def run_validated_design(
    geo: GeoExperimentDesign,
    *,
    validate_design: Any = None,
    build_contract: Any,
    estimator_id: str | None = None,
    inference_id: str | None = None,
    geometry_id: str | None = None,
    readout_semantics: str | None = None,
) -> tuple:
    """Run a validated design and leave guardrail-enriched evidence.

    Builds a :class:`DesignRunContext` with the injected callbacks, executes
    the unmodified registry pipeline, evaluates the existing guardrail bundle
    from the produced contract, and attaches the evaluated guardrail fields
    via frozen-dataclass copies. Sets ``geo.last_evidence`` to the enriched
    evidence (the pipeline's own side-effect convention) and returns the same
    ``(mde_prc_df, mde_val_df, power_results_df)`` triple as ``run_design``.

    ``build_contract`` is required with no default so no builder is ever
    selected silently. ``validate_design`` follows pipeline gate semantics
    unchanged. All errors propagate from the underlying builders, validators,
    and pipeline with no new error vocabulary.
    """
    from panel_exp.design.geo_runner import run_geo_experiment_design

    context = DesignRunContext(
        geo=geo,
        validate_design=validate_design,
        build_contract=build_contract,
    )
    outputs = run_geo_experiment_design(context)
    evidence = geo.last_evidence
    if evidence is None:  # pragma: no cover - pipeline always sets evidence
        raise RuntimeError("validated design run produced no evidence")
    contract = evidence.design.to_dict().get("design_contract")
    validation = evidence.design.to_dict().get("contract_validation")
    bundle = build_producer_guardrail_bundle(
        design_contract=contract,
        contract_validation=validation,
        estimator_id=estimator_id,
        inference_id=inference_id,
        geometry_id=geometry_id,
        readout_semantics=readout_semantics,
    )
    enriched_design = dataclasses.replace(
        evidence.design,
        design_guardrail=bundle["design_guardrail"],
        combination_guardrail=bundle["combination_guardrail"],
        guardrail_enforcement=bundle["guardrail_enforcement"],
    )
    geo.last_evidence = dataclasses.replace(evidence, design=enriched_design)
    return outputs
