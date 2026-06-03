"""
Track F P0 instrument contract hygiene (AUDIT-010 follow-on).

Guards naming/taxonomy issues that block reliable interpretation. Not promotion,
CalibrationSignal expansion, or MMM ingress.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Type

# F-P0-001 — SCM / AugSynth full_model post-period fit risk (INV-D2-001).
FULL_MODEL_GOVERNED_CLASS_NAMES = frozenset(
    {
        "SyntheticControl",
        "AugSynth",
        "AugSynthCVXPY",
        "SyntheticControlCVXPY",
    }
)
FULL_MODEL_BLOCKED_REASON = "full_model_true_blocked_for_governed_export"

# F-P0-003 — registry Bayesian ≠ BayesianTBR NUTS MCMC (INV-015).
INV_015_REGISTRY_BAYESIAN_NOT_MCMC = (
    "registry_inference_bayesian_is_not_bayesian_tbr_mcmc"
)

# F-P0-005 — Placebo is inference / falsification, not an estimator readout.
PLACEBO_INFERENCE_MODES = frozenset({"Placebo", "placebo"})

# F-P0-006 — multi-cell pooling without governed rule.
MULTI_CELL_POOLED_WITHOUT_RULE = "multi_cell_pooled_without_pooling_rule_id"


def full_model_export_block_reason(
    estimator_class_name: str,
    full_model: bool,
    *,
    governed_export: bool = True,
) -> Optional[str]:
    """Return block reason when ``full_model=True`` on governed SCM/AugSynth paths."""
    if not governed_export or not full_model:
        return None
    if estimator_class_name in FULL_MODEL_GOVERNED_CLASS_NAMES:
        return FULL_MODEL_BLOCKED_REASON
    return None


def assert_full_model_allowed_for_export(
    estimator_class_name: str,
    full_model: bool,
    *,
    governed_export: bool = True,
) -> None:
    reason = full_model_export_block_reason(
        estimator_class_name, full_model, governed_export=governed_export
    )
    if reason:
        raise ValueError(
            f"{estimator_class_name}: full_model=True is blocked for governed export "
            f"({reason}; INV-D2-001)."
        )


def is_placebo_inference_mode(inference: Optional[str]) -> bool:
    return inference in PLACEBO_INFERENCE_MODES


def assert_not_placebo_as_estimator(estimator_name: str) -> None:
    """Placebo must appear only as inference/falsification layer (AUDIT-010 taxonomy)."""
    if estimator_name in PLACEBO_INFERENCE_MODES:
        raise ValueError(
            f"Placebo is inference/falsification, not an estimator readout "
            f"(got estimator_name={estimator_name!r})."
        )


def is_registry_bayesian_inference(inference: Optional[str]) -> bool:
    return str(inference or "") == "Bayesian"


def registry_bayesian_production_block_reason(
    estimator_name: str,
    inference: Optional[str],
    *,
    governed_production: bool = True,
) -> Optional[str]:
    """INV-015: registry ``Bayesian`` must not be read as BayesianTBR MCMC."""
    if not governed_production or not is_registry_bayesian_inference(inference):
        return None
    if estimator_name in ("BayesianTBR", "BayesianTBRHorseShoe"):
        return INV_015_REGISTRY_BAYESIAN_NOT_MCMC
    if estimator_name == "TBRRidge":
        return INV_015_REGISTRY_BAYESIAN_NOT_MCMC
    return INV_015_REGISTRY_BAYESIAN_NOT_MCMC


def multi_cell_pooling_block_reason(
    n_test_grps: int,
    pooling_rule_id: Optional[str],
    *,
    pooled_aggregation_requested: bool = False,
) -> Optional[str]:
    """
    Global multi-cell rule (AUDIT-010): per-cell only unless ``pooling_rule_id`` set.

    When ``pooled_aggregation_requested`` is True and ``n_test_grps > 1``, require a
    governed pooling rule id.
    """
    if n_test_grps <= 1:
        return None
    if pooled_aggregation_requested and not pooling_rule_id:
        return MULTI_CELL_POOLED_WITHOUT_RULE
    return None


def assert_multi_cell_not_pooled_without_rule(
    n_test_grps: int,
    pooling_rule_id: Optional[str],
    *,
    pooled_aggregation_requested: bool = False,
) -> None:
    reason = multi_cell_pooling_block_reason(
        n_test_grps,
        pooling_rule_id,
        pooled_aggregation_requested=pooled_aggregation_requested,
    )
    if reason:
        raise ValueError(
            f"multi-cell evidence requires per-cell analysis or a governed "
            f"pooling_rule_id (n_test_grps={n_test_grps}, reason={reason})."
        )


def assert_class_tbr_recovery_factory(factory: Callable[[], Any]) -> None:
    """F-P0-002: recovery config ``TBR`` must instantiate class ``TBR``, not ``TBRRidge``."""
    instance = factory()
    cls = type(instance)
    if cls.__name__ == "TBRRidge":
        raise ValueError(
            "recovery_runner TBR config must use class TBR, not TBRRidge (F-P0-002)."
        )
    if cls.__name__ != "TBR":
        raise ValueError(
            f"recovery_runner TBR config expected class TBR, got {cls.__name__}."
        )


def class_tbr_recovery_factory(
    *,
    inference: Optional[str] = None,
    alpha: float = 0.05,
) -> Callable[[], Any]:
    """Canonical factory for validation recovery config key ``TBR``."""
    from panel_exp.methods.tbr import TBR

    def _factory() -> TBR:
        return TBR(inference=inference, alpha=alpha, full_model=False)

    return _factory


__all__ = [
    "FULL_MODEL_GOVERNED_CLASS_NAMES",
    "FULL_MODEL_BLOCKED_REASON",
    "INV_015_REGISTRY_BAYESIAN_NOT_MCMC",
    "MULTI_CELL_POOLED_WITHOUT_RULE",
    "PLACEBO_INFERENCE_MODES",
    "assert_class_tbr_recovery_factory",
    "assert_full_model_allowed_for_export",
    "assert_multi_cell_not_pooled_without_rule",
    "assert_not_placebo_as_estimator",
    "class_tbr_recovery_factory",
    "full_model_export_block_reason",
    "is_placebo_inference_mode",
    "is_registry_bayesian_inference",
    "multi_cell_pooling_block_reason",
    "registry_bayesian_production_block_reason",
]
