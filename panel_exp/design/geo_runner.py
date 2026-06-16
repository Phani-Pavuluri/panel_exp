"""GeoExperimentDesign assignment + validation + power pipeline (registry handler)."""

from __future__ import annotations

from panel_exp.design.context import DesignRunContext
from panel_exp import evidence as evidence_module
from panel_exp.evidence import ExperimentEvidence, input_data_hash_from_wide
from panel_exp.evidence_hash import assignment_hash
from panel_exp.panel_data import TimePeriod
from panel_exp.spec import spillover_metadata_available, spec_from_geo_design
from panel_exp.validation.design_contract_builder_001 import (
    build_and_validate_tier1_contract,
)


def _build_geo_spec(geo, design_method: str, treatment_probability: float):
    return spec_from_geo_design(
        geo.experiment_id,
        geo.outcome_column,
        geo.unit_column,
        geo.time_column,
        pre_period=TimePeriod(start=0, end=geo.train_length),
        experiment_period=TimePeriod(start=geo.train_length, end=None),
        design_method=design_method,
        random_state=geo.random_state,
        alpha=geo.alpha,
        treatment_probability=treatment_probability,
        n_test_groups=geo.n_test_grps,
        test_whitelist=geo.test_whitelist,
        control_whitelist=geo.control_whitelist,
        test_blacklist=geo.test_blacklist,
        control_blacklist=geo.control_blacklist,
        control_test_blacklist=geo.control_test_blacklist,
        interference=geo.interference,
        spillover_notes=geo.spillover_notes,
        exposure_column=geo.exposure_column,
    )


def run_geo_experiment_design(ctx: DesignRunContext) -> tuple:
    """
    Execute design assignment, optional validation gate, evidence, and MDE sensitivity.

    Pipeline order (must match pre-registry ``GeoExperimentDesign.run_design``):

    1. ``create_design().assign(...)``
    2. ``validate_design`` when ``validate_after_assign``
    3. ``DesignEvidence.from_assignment`` + ``ExperimentEvidence``
    4. ``_calculate_sensitivity_metrics``

    Returns (mde_prc_df, mde_val_df, power_results_df).
    """
    geo = ctx.geo
    if geo.treatment_probability is None:
        tp = geo.n_test_grps / (geo.n_test_grps + 1)
    else:
        tp = geo.treatment_probability

    geo.last_validation = None
    geo.last_evidence = None

    from panel_exp.design.registry import design_class_name

    design_method = design_class_name(geo.base_randomizer_cls)

    pre_treatment_period = None
    if geo.train_length is not None and geo.train_length > 0:
        pre_treatment_period = TimePeriod(start=0, end=geo.train_length)

    # 1. Assignment
    design = geo.create_design()
    rs_dp_grps = design.assign(
        panel_data=geo.panel_data,
        treatment_period=None,
        pre_treatment_period=pre_treatment_period,
        test_whitelist=geo.test_whitelist,
        test_blacklist=geo.test_blacklist,
        control_whitelist=geo.control_whitelist,
        control_blacklist=geo.control_blacklist,
        control_test_blacklist=geo.control_test_blacklist,
        n_test_grps=geo.n_test_grps,
    )

    spec = _build_geo_spec(geo, design_method, tp)

    # 2. Post-assignment validation gate
    if geo.validate_after_assign:
        geo.last_validation = validate_design(
            geo.panel_data.wide_data,
            rs_dp_grps,
            n_test_grps=geo.n_test_grps,
            treatment_probability=tp,
            control_whitelist=geo.control_whitelist,
            test_whitelist=geo.test_whitelist,
            control_blacklist=geo.control_blacklist,
            test_blacklist=geo.test_blacklist,
            control_test_blacklist=geo.control_test_blacklist,
            interference=geo.interference,
            spillover_metadata_available=spillover_metadata_available(spec),
            block_on_fail=geo.block_on_validation_fail,
        )

    validation_summary = (
        geo.last_validation.to_dict() if geo.last_validation else {}
    )
    design_kwargs = dict(geo.design_kwargs or {})
    if getattr(design, "last_multicell_metadata", None):
        design_kwargs["last_multicell_metadata"] = design.last_multicell_metadata
    warnings: list[str] = []
    errors: list[str] = []
    if geo.last_validation is not None:
        errors = list(geo.last_validation.blocking_failures)
        for check in geo.last_validation.checks:
            if check.status.value == "WARN":
                warnings.append(check.message)

    registry_spec = geo._design_spec
    design_contract, contract_validation = build_and_validate_tier1_contract(
        spec=spec,
        assignment=rs_dp_grps,
        registry_key=registry_spec.name,
        base_randomizer_cls=geo.base_randomizer_cls,
        n_test_grps=geo.n_test_grps,
        treatment_probability=tp,
        is_rerandomization_wrapped=True,
        validation_summary=validation_summary,
        wide_data=geo.panel_data.wide_data,
        design_kwargs=design_kwargs,
        spec_hash=spec.content_hash(),
        assignment_hash_value=assignment_hash(rs_dp_grps),
        package_version=evidence_module.__version__,
    )

    geo.last_evidence = ExperimentEvidence.build(
        spec,
        rs_dp_grps,
        validation_summary=validation_summary,
        warnings=warnings,
        errors=errors,
        input_data_hash=input_data_hash_from_wide(geo.panel_data.wide_data),
        design_contract=design_contract,
        contract_validation=contract_validation,
    )

    # 4. Power / MDE sensitivity
    return geo._calculate_sensitivity_metrics(rs_dp_grps, "control")


# Late import avoids circular dependency at module load.
from panel_exp.design.validation import validate_design  # noqa: E402
